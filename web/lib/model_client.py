'''
File: model_client.py
Author: Min Feng
Version: 0.1
Create: 2013-09-29 23:25:14
Description: library for calling the model service
'''
import logging

class process:
	'''warping the remote process'''

	def __init__(self, serv, p_name, p_mete, pid):
		self.service = serv
		self.pid = pid
		self.name = p_name
		self.mete = p_mete
		self.status = None

	def check(self):
		_url = '/s/%s' % self.pid
		_obj = self.service.call_service(_url)

		self.status = _obj

	def is_done(self):
		if self.status:
			return self.status['done']
		return False

	def is_success(self):
		if self.status:
			return self.status['success']
		return False

	def get_error(self):
		if self.status:
			return self.status['error']
		return None

	def get_status(self):
		if self.status:
			return self.status['status']
		return ''

	def get_progress(self):
		if self.status:
			return int(self.status['progress'])
		return 0

	def get_outputs(self):
		_url = '/o/%s' % self.pid
		_obj = self.service.call_service(_url)

		if _obj['done'] == False:
			raise Exception('process (%s) is still running' % (self.pid, _obj['error']))

		if _obj['error']:
			raise Exception('process (%s) failed: %s' % (self.pid, _obj['error']))

		_vs = self.format_outputs(self.mete['outputs'], _obj['outputs'])
		return _vs

	def run(self):
		import time
		import sys

		print 'waiting process running', self.pid
		while(True):
			self.check()

			print '\r %3d%%: %s' % (self.get_progress(), self.get_status()),
			sys.stdout.flush()

			if self.is_done():
				break

			# check the status of the process every 0.5 second
			time.sleep(1)
		print ''

		return self.get_outputs()

	def format_outputs(self, o_mete, args):
		import model_data

		# add this line just to disable the gramma checking error
		model_data.d_int

		_vs = {}

		for _k in args:
			if _k not in o_mete:
				raise Exception('param (%s) not defined by the process' % _k)

			_mete = o_mete[_k]

			_nargs = _mete['nargs']
			_dtype = _mete['d_type']

			_otype = eval('model_data.data_%s()' % _dtype['type'])
			_vv = None

			if _nargs in ['?', 1]:
				if args[_k] != None:
					_vv = _otype.decode(args[_k])
			else:
				_vv = []

				if args[_k] == None:
					continue

				for _v in args[_k]:
					_vv.append(_otype.decode(_v))

			if _vv == None:
				continue

			_vs[_k] = _vv

		return _vs

class service:
	'''wrap the model service'''

	def __init__(self, host, port):
		self.host = host
		self.port = port

		_obj = self.call_service('/')

		_pro = {}
		for _k in _obj['models']:
			_pro[_k] = _obj['models'][_k]

		self.process = _pro
		self.info = _obj['model_service']

	def format_inputs(self, i_mete, args):
		import json
		import model_data

		# add this line just to disable the gramma checking error
		model_data.d_int

		_vs = {}

		for _k in args:
			if _k not in i_mete:
				raise Exception('param (%s) not defined by the process' % _k)

			_mete = i_mete[_k]

			_nargs = _mete['nargs']
			_dtype = _mete['d_type']

			_otype = eval('model_data.data_%s()' % _dtype['type'])
			_vv = None

			if _nargs in ['?', 1]:
				if args[_k] != None:
					_vv = _otype.encode(args[_k])
			else:
				_vv = []

				if args[_k] == None:
					continue

				for _v in args[_k]:
					_vv.append(_otype.encode(_v))

			if _vv == None:
				continue

			_vs[_k] = json.dumps(_vv, default=model_data.convert_to_builtin_type)

		return _vs

	def run_process(self, p_name, args):
		'''run the remote process and return a wrap of it'''

		if p_name not in self.process:
			raise Exception('process %s not found' % p_name)

		_url = '/m/%s' % p_name
		_obj = self.call_service(_url, self.format_inputs(self.process[p_name]['inputs'], args))

		_pid = _obj['process_id']
		return process(self, p_name, self.process[p_name], _pid)

	def call_service(self, url='/', params=None, method='GET', headers={}):
		import urllib
		import urllib2

		try:
			_url = 'http://%s:%s%s' % (self.host, self.port, url)
			_req = urllib2.Request(_url)

			if params != None:
				_data = urllib.urlencode(params)
				_req.add_data(_data)

			_res = urllib2.urlopen(_req)

			_txt = _res.read()
			_obj = None

			import json
			try:
				_obj = json.loads(_txt)
			except Exception:
				logging.error('failed to load the response')
				pass

			if _res.code != 200:
				_status = _res.code
				_reason = _res.msg

				if _obj != None and 'error' in _obj:
					_err = _obj['error']

					_status = _err['code']
					_reason = _err['message']

				logging.error('request error (%s) %s' % (_status, _reason))
				raise Exception('failed to connect the service (%s): %s' % (_status, _reason))

			return _obj
		finally:
			pass
			# _con.close()

if __name__ == '__main__':
	_serv = service('159.226.111.26', 38080)
	for _k in _serv.process:
		print '>', _k

	import shapely.geometry
	_params = {'dis': 3, 'geo': shapely.geometry.Point(100, 40)}
	_proc = _serv.run_process('mod_buffer.buffer', _params)
	print _proc.pid

	for i in xrange(10):
		import time
		time.sleep(0.5)

		_proc.check()
		if _proc.is_done():
			print _proc.get_outputs()

