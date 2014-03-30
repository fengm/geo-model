
import logging
import model_base

system_vars = ['env']

class affiliation_info:

	def __init__(self, name, address, state, country, zip_code):
		self.name = name
		self.address = address
		self.state = state
		self.country = country
		self.zip_code = zip_code

class contact_info:

	def __init__(self, name, email, first_name=None, last_name=None, title=None, phone=None, affiliation=None):
		self.name = name
		self.email = email
		self.first_name = first_name
		self.last_name = last_name
		self.title = title
		self.phone = phone
		self.affiliation = affiliation

class parameter(model_base.base_info):

	def __init__(self, d_type, nargs=1, title=None, desc=None, unit=None, tags=[], urls=[], refs=[], dois=[]):
		model_base.base_info.__init__(self, None, title, desc, tags, urls, refs, dois)
		self.unit = unit
		self.nargs= nargs
		self.d_type = d_type

class output_parameter(parameter):

	def __init__(self, name, d_type, nargs=1, title=None, desc=None, unit=None, tags=[], urls=[], refs=[], dois=[]):
		parameter.__init__(self, d_type, nargs, title, desc, unit, tags, urls, refs, dois)
		self.name = name

class model(model_base.base_info):

	def __init__(self, title, desc=None, contact=[], tags=[], urls=[], refs=[], dois=[]):
		self.contact = contact
		model_base.base_info.__init__(self, None, title, desc, tags, urls, refs, dois)

class geo_model:

	def __init__(self, m_model, m_inputs, m_outputs):
		self.m_model = m_model
		self.m_inputs = m_inputs
		self.m_outputs = m_outputs

	def __call__(self, f):

		def geo_process(*arg, **kwargs):
			# check the model info
			# check the parameters

			if len(arg) > 0:
				logging.error('the model inputs cannot be array')
				raise Exception('the model inputs cannot be array')

			_keys = kwargs.keys()
			if len([_key for _key in _keys if (_key not in system_vars)]) != len(self.m_inputs):
				logging.error('the model inputs do not match the requirement')
				raise Exception('the model inputs do not match the requirement')

			_vs = []
			for _m in self.m_inputs:
				if _m.name not in _keys:
					logging.error('parameter [%s] is missing' % _m.name)
					raise Exception('parameter [%s] is missing' % _m.name)

				_o = kwargs[_m.name]

				# check the inputs
				if _m.nargs != 1 and _m.nargs != '?':
					_v = _o.value
					if not (isinstance(_v, list) or isinstance(_v, tuple)):
						raise TypeError('the input parameter [%s] needs to be list' % _m.name)

					if _m.nargs not in ['+', '*']:
						if len(_v) != int(_m.nargs):
							raise TypeError('the input parameter [%s] require %s values, but %s provided' % (_m.nargs, len(_v)))

				_vs.append(_o)

			if self.need_env:
				_vs.append(kwargs['env'])

			_res = f(*_vs)

			# if type(_res) != dict:
			# 	raise Exception('output has to be a dict')

			# for _o in self.m_outputs:
			# 	if _o.name not in _res:
			# 		raise Exception('output parameter [%s] is missing' % _o.name)

			# 	_s = _res[_o.name]
			# 	# check the outputs
			# 	if _o.nargs != 1 and _o.nargs != '?':
			# 		import model_data
			# 		print _s
			# 		_v = _s.value if isinstance(_s, model_data.data) else _s
			# 		if not (isinstance(_v, list) or isinstance(_v, tuple)):
			# 			raise TypeError('the output parameter [%s] needs to be list' % _o.name)

			# 		if _o.nargs not in ['+', '*']:
			# 			if len(_v) != int(_o.nargs):
			# 				raise TypeError('the output parameter [%s] require %s values, but %s provided' % (_o.nargs, len(_v)))

			# 	_vs.append(_s)

			# process the outputs
			return _res

		self.m_model.name = f.__name__

		import inspect
		_args = inspect.getargspec(f)[0]
		_args_val = [_arg for _arg in _args if (_arg not in system_vars)]

		if len(_args_val) != len(self.m_inputs):
			logging.error('the model inputs do not match the requirement')
			raise Exception('the model inputs do not match the requirement')

		_inputs = {}
		for i in xrange(len(_args_val)):
			_inputs[_args_val[i]] = self.m_inputs[i]
			self.m_inputs[i].name = _args_val[i]

		_outputs = {}
		for _o in self.m_outputs:
			if not _o.name:
				raise Exception('name is required for each output variable')
			if _o.name in _outputs:
				raise Exception('output [%s] cannot be duplicated' % _o.name)
			_outputs[_o.name] = _o

		geo_process.model = self.m_model
		geo_process.inputs = _inputs
		geo_process.outputs = _outputs
		geo_process.need_env = 'env' in _args
		self.need_env = geo_process.need_env

		return geo_process


