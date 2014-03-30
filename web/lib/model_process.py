'''
File: model_process.py
Author: Min Feng
Version: 0.1
Create: 2013-12-20 12:46:55
Description: manage the model instance and convert the model inputs and outputs back and forth between transfering format and objects
'''
# updated (2013-12-20 12:47:39): updated all inputs and outputs parameters from
# value to model_data.data objects, which consist of metadata and values
# updated (2013-12-23 15:25:11): updated the outputs to support async outputs

import logging
import threading

class model_env:

	def __init__(self, metadata, outputs={}):
		self._status = ''
		self._progress = 0
		self._metadata = metadata
		self._fzip = self.make_tmp_dir()
		self._outputs = outputs

		import model_data_cache
		self.data_cache = model_data_cache.data_cache_mag()

	def make_tmp_dir(self):
		import file_unzip
		import config

		return file_unzip.file_unzip(config.cfg.get('general', 'tmp_path'))

	@property
	def status(self):
		return self._status

	@status.setter
	def status(self, value):
		self._status = value

	@property
	def progress(self):
		return self._progress

	@progress.setter
	def progress(self, value):
		self._progress = value

		if self._progress < 0:
			self._progress = 0
		if self._progress > 100:
			self._progress = 100

	@property
	def outputs(self):
		return self._outputs

	@property
	def metadata(self):
		return self._metadata

	@property
	def fzip(self):
		return self._fzip

class geo_processing(threading.Thread):

	def __init__(self, model_id, func, args, env):
		threading.Thread.__init__(self)

		self.func = func
		self.model_id = model_id
		self.args = args
		self.error = None
		self.env = env

	def run(self):
		self.name = threading.currentThread().getName()
		try:
			_res = self.func(*[], **self.args)

			if _res == None:
				return

			for _k in _res:
				self.env.outputs[_k] = _res[_k]

		except Exception, _err:
			import traceback
			logging.error(traceback.format_exc())

			self.error = _err
			self.outputs = None
		finally:
			if ('env' in self.args) and (self.args['env'].fzip != None):
				self.args['env'].fzip.clean()

class geo_processing_mag:

	def __init__(self):
		self.processes = {}

	def create_task(self, model_id, env, func, args):
		_p = geo_processing(model_id, func, args, env)
		_p.start()

		_id = '%s.%s' % (model_id, _p.name.split('-')[-1])
		self.processes[_id] = _p

		return _id

	def get_process(self, pid):
		if pid not in self.processes:
			logging.error('no process with ID (%s)' % pid)
			raise Exception('no process with ID (%s)' % pid)

		return self.processes[pid]

	def check_status(self):
		for _id in self.processes:
			print _id, self.processes[_id].is_alive()

	def is_alive(self, pid):
		return self.processes[pid].is_alive()

	def is_done(self, pid):
		return not self.processes[pid].is_alive()

class res_info:

	def __init__(self, cfg, pic, doc):
		self.cfg = cfg
		self.pic = pic
		self.doc = doc

	@staticmethod
	def load(d_res, model_id):
		import os

		_d_res = os.path.join(d_res, model_id)
		logging.info('searching resource folder: ' + _d_res)

		_d_cfg = os.path.join(_d_res, 'cfg')
		_d_pic = os.path.join(_d_res, 'pic')
		_d_doc = os.path.join(_d_res, 'doc')

		_f_conf = res_info.list_files(_d_cfg)
		_f_pics = res_info.list_files(_d_pic)
		_f_docs = res_info.list_files(_d_doc)

		logging.info('found %s cfg, %s pic, %s doc' % (len(_f_conf), len(_f_pics), len(_f_docs)))

		import ConfigParser
		_cfg = ConfigParser.ConfigParser()

		if len(_f_conf) > 0:
			_cfg.read(_f_conf)
		return res_info(_cfg, _f_pics, _f_docs)

	@staticmethod
	def list_files(d):
		import os
		if not os.path.exists(d):
			return []

		_ls = [os.path.join(d, _f) for _f in os.listdir(d)]
		_ls.sort()

		return _ls

class geo_models:

	def __init__(self, model_dir):
		self.metadata = {}
		self.models = self.load_models(model_dir)
		self.proc_mag = geo_processing_mag()

	def load_model(self, name, ms):
		import imp
		import config

		_d_etc = config.cfg.get('general', 'res_path')
		_fp, _path, _desc = imp.find_module(name)
		try:
			_mod = imp.load_module(name, _fp, _path, _desc)
			import inspect

			for _n, _v in inspect.getmembers(_mod):
				if not inspect.isfunction(_v):
					continue

				if hasattr(_v, 'model') and hasattr(_v, 'inputs'):
					logging.info('found function %s.%s' % (name, _n))
					_id = '%s.%s' % (name, _n)
					ms[_id] = _v

					_res = res_info.load(_d_etc, _id)
					self.metadata[_id] = _res
		finally:
			if _fp:
				_fp.close()

	def load_models(self, d_in):
		import os

		_fs = [_f[:-3] for _f in os.listdir(d_in) if _f.endswith('.py')]
		_ms = {}

		for _f in _fs:
			logging.info('loading models in %s' % _f)
			self.load_model(_f, _ms)

		return _ms

	def format_data(self, val):
		if isinstance(val, dict) and ('attrs' in val.keys() or 'value' in val.keys()):
			_val = val
			return _val.get('attrs', {}), _val.get('value', None)
		else:
			return {}, val

	def run_model(self, model_id, args):
		import model_data

		if model_id not in self.models:
			raise Exception('[%s] does not exist' % model_id)

		_mod = self.models[model_id]

		_m_inputs = _mod.inputs
		logging.info('inputs %d' % len(_m_inputs.keys()))

		# _m_model = _mod.m_model
		# _m_outputs = _mod.m_outputs

		import model_utility
		_vs = {}
		for _k in _m_inputs:
			logging.info('input parameter: %s' % _k)
			if _k not in args:
				raise Exception('parameter %s is missing' % _k)

			# if _m_inputs[_k].nargs not in [1, '?']: or (not isinstance(_d_type, model_data.data_simple)):
			_val = model_utility.decode_json(args.get(_k))

			# wrap all the input parameters into data object
			_met, _val = self.format_data(_val)

			_d_type =_m_inputs[_k].d_type

			if _m_inputs[_k].nargs in [1, '?']:
				_obj = _d_type.decode(_val)
			else:
				if not isinstance(_val, list):
					_val = [_val]
					# raise TypeError('parameter [%s] is required to be list')
				_obj = [_m_inputs[_k].d_type.decode(_v) for _v in _val]

			_vs[_k] = model_data.data(_obj, self.decode_attrs(_met))

		# init environment variables
		_env = model_env(self.metadata[model_id], outputs=self._init_outputs(_mod.outputs))

		if _mod.need_env:
			_vs['env'] = _env

		return self.proc_mag.create_task(model_id, _env, _mod, _vs)

	def _init_outputs(self, outputs):
		import model_data

		_vs = {}
		for _k in outputs:
			_vs[_k] = model_data.data(None if outputs[_k].nargs == 1 else [], {})

		return _vs

	def get_status(self, proc_id):
		if proc_id not in self.proc_mag.processes:
			raise Exception('process [%s] does not exist' % proc_id)

		_proc = self.proc_mag.get_process(proc_id)

		_done = self.proc_mag.is_done(proc_id)
		_prog = _proc.env.progress
		_status = _proc.env.status

		if _done and _proc.error == None:
			_prog = 100
			_status = ''

		return {'process_id': proc_id,
		  'model_id': _proc.model_id,
		  'done': _done,
		  'success': _proc.error == None,
		  'status': _status,
		  'progress': '%d' % int(_prog),
		  'error': str(_proc.error) if _proc.error != None else ''}

	def decode_attrs(self, attrs):
		# convert the reserved attrs to their corrosponding types
		import copy
		_attrs = copy.copy(attrs)

		if _attrs.get('proj', None):
			from osgeo import osr

			if isinstance(_attrs['proj'], osr.SpatialReference):
				pass
			else:
				import model_utility
				_attrs['proj'] = model_utility.proj_from_proj4(_attrs['proj'])

		return _attrs

	def encode_attrs(self, attrs):
		# convert the corrosponding types to text
		import copy
		_attrs = copy.copy(attrs)

		if _attrs.get('proj', None):
			from osgeo import osr

			if isinstance(_attrs['proj'], osr.SpatialReference):
				import model_utility
				_attrs['proj'] = model_utility.proj_to_proj4(_attrs['proj'])

		return _attrs

	def get_outputs(self, proc_id):
		_json = self.get_status(proc_id)

		_proc = self.proc_mag.processes[proc_id]

		# In order to support assyncnous outputs, outputs can be retrieved even the processing is
		# still going and error occured.
		# if not self.proc_mag.is_done(proc_id) or _proc.error != None:
		# 	return _json

		_model_id = _proc.model_id

		if _model_id not in self.models:
			raise Exception('[%s] does not exist' % _model_id)

		_mod = self.models[_model_id]

		# _m_model = _mod.m_model
		# _m_inputs = _mod.inputs

		_m_outputs = _mod.outputs
		_v_outputs = _proc.env.outputs

		import model_data

		for _v in _v_outputs:
			if not isinstance(_v_outputs[_v], model_data.data):
				_v_outputs[_v] = model_data.data(_v_outputs[_v], {})

		logging.info('outputs %d' % len(_m_outputs.keys()))

		_vs = {}
		for _k in _m_outputs:
			_obj = {'attrs': self.encode_attrs(_v_outputs[_k].attrs)}
			if _m_outputs[_k].nargs == 1:
				_obj['value'] = _m_outputs[_k].d_type.encode(_v_outputs[_k].value)
			else:
				_vv = _v_outputs[_k].value
				if not (isinstance(_v_outputs[_k].value, list) or isinstance(_v_outputs[_k].value, tuple)):
					_vv = [_vv]
					# raise TypeError('output parameter [%s] is required to be list')
				_obj['value'] = [_m_outputs[_k].d_type.encode(_v) for _v in _vv]
			_vs[_k] = _obj

		_json['outputs'] = _vs
		return _json


