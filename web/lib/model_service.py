
import serv_base
import model_process
import logging
import config

_models = model_process.geo_models(config.get_at('general', 'mod_path'))

class service_handler(serv_base.service_base):

	def task(self):
		_ms = {}
		for _m in _models.models:
			_mod = _models.models[_m]
			_met = _models.metadata[_m]
			_ms[_m] = {'model': _mod.model, 'inputs': _mod.inputs, 'outputs': _mod.outputs, 'pic': len(_met.pic), 'doc': len(_met.doc)}

		_o = {'model_service': {'provider': 'geodata.cn'}, 'models': _ms}
		self.output_json(_o)

class metedata_handler(serv_base.service_base):

	def task(self, model_id):
		logging.info('model id:' + model_id)

		_ks = _models.models.keys()
		_ks.sort()

		_ms = []
		for _m in _ks:
			if model_id == '*' or model_id == _m:
				_mod = _models.models[_m]
				_met = _models.metadata[_m]

				_ms.append({'id': _m, 'model': _mod.model, 'inputs': _mod.inputs, 'outputs': _mod.outputs, 'pic': len(_met.pic), 'doc': len(_met.doc)})

		self.output_json(_ms)

class resource_handler(serv_base.service_base):

	def task(self, model_id):
		logging.info('load resource %s' % model_id)

		import re
		_m = re.match('(.+)/(\w+)/(\d+)', model_id)
		if not _m:
			raise Exception('Unsupported request %s' % model_id)

		_mod = _m.group(1)
		_res = _m.group(2)
		_val = _m.group(3)

		if _res == 'pic':
			return self.load_pic(_mod, int(_val))

		if _res == 'doc':
			return self.load_doc(_mod, int(_val))

		raise Exception('Unsupported resource type %s' % _res)

	def load_pic(self, model_id, idx):
		logging.info('load pic %s-%s' % (model_id, idx))

		_met = _models.metadata[model_id]

		if len(_met.pic) == 0 and idx == 0:
			import config
			self.output_file(config.cfg.get('general', 'pic_default'))
			return

		if idx >= len(_met.pic):
			raise Exception('no preview image for index (%s)' % idx)

		self.output_file(_met.pic[idx])

	def load_doc(self, model_id, idx):
		logging.info('load doc %s-%s' % (model_id, idx))

		_met = _models.metadata[model_id]
		if idx >= len(_met.doc):
			raise Exception('no document for index (%s)' % idx)

		self.output_file(_met.doc[idx])

class model_handler(serv_base.service_base):

	def task(self, model_id):
		print 'parameter list'
		for _k in self.request.arguments():
			print ' -', _k

		_args = {}
		for _k in self.request.arguments():
			_args[_k] = self.request.get(_k)

		_pid = _models.run_model(model_id, _args)

		_o = {'process_id': _pid, 'done': _models.proc_mag.is_done(_pid)}
		self.output_json(_o)

class status_handler(serv_base.service_base):

	def task(self, proc_id):
		_o = _models.get_status(proc_id)
		self.output_json(_o)

class output_handler(serv_base.service_base):

	def task(self, proc_id):
		_o = _models.get_outputs(proc_id)
		self.output_json(_o)

class admin_handler(serv_base.service_base):

	def task(self, path):
		if path == 'ps':
			return self.list_processes()
		else:
			raise Exception('unsupported request (%s)' % path)

	def list_processes(self):
		logging.info('list processes')

		_ps = []
		for _p in _models.proc_mag.processes:
			_ps.append(_models.get_status(_p))

		logging.info('found %s processes' % len(_ps))

		return self.output_json(_ps)

class data_cache_handler(serv_base.service_base):

	def __init__(self, *args):
		import model_data_cache
		self.mag = model_data_cache.data_cache_mag()
		serv_base.service_base.__init__(self, *args)

	def task(self, oid, dtype=None):
		import file_unzip
		import config

		print 'request data cache: %s, %s' % (oid, dtype)
		with file_unzip.file_unzip(config.get_at('general', 'tmp_path')) as _zip:
			_f = self.mag.load(oid, dtype.lower() if dtype else dtype, _zip)
			self.output_file(_f)

