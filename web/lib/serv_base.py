
import logging
import webapp2

class service_base(webapp2.RequestHandler):

	def get(self, *arg):
		logging.info('GET request')
		return self.__task(*arg)

	def post(self, *arg):
		logging.info('POST request')
		return self.__task(*arg)

	def __task(self, *arg):
		self.task(*arg)

	def task(self, *arg):
		raise NotImplementedError()

	def output_json(self, obj):
		import json
		import model_data

		self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
		# _txt = json.dumps(obj, default=model_data.convert_to_builtin_type, indent=2, ensure_ascii=False, sort_keys=True)
		# self.response.out.write(_txt)
		json.dump(obj, self.response.out, default=model_data.convert_to_builtin_type, indent=2, ensure_ascii=False, sort_keys=True)

	def output_file(self, f):
		import mimetypes
		import os

		_context = mimetypes.guess_type(f)[0]
		self.response.headers['Content-Type'] = _context
		_type = 'inline' if 'image' in _context else 'attachment'
		self.response.headers['Content-Disposition'] = '%s; filename=%s' % (_type, os.path.basename(f))

		logging.info('context-type:' + _context)
		logging.info('loading web file: ' + f)

		with open(f) as _fi:
			self.response.out.write(_fi.read())

	def handle_exception(self, exception, debug):
		import traceback

		logging.error(traceback.format_exc())
		logging.error(str(exception))
		print '\n\n* Error:', traceback.format_exc()

		_json = {'message': str(exception.message)}
		if isinstance(exception, webapp2.HTTPException):
			self.response.set_status(exception.code)
			_json['code'] = exception.code
		else:
			self.response.set_status(500)
			_json['code'] = 500

		self.output_json({'error': _json})


