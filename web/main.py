# -*- coding: utf-8 -*-

import webapp2

def handle_error(request, response, exception):
	import json

	response.headers.add_header('Content-Type', 'application/json')
	result = {
			'status': 'error',
			'status_code': exception.code,
			'error_message': exception.explanation,
		}

	response.write(json.dumps(result))
	response.set_status(exception.code)

def main():
	_opts = _init_env()
	del _opts

	_routes = [
		(r'/', 'model_service.service_handler'),
		(r'/web/(.+)', 'serv_web.web_handler'),
		(r'/admin/(.+)', 'model_service.admin_handler'),
		(r'/d/([^/]+)', 'model_service.metedata_handler'),
		(r'/d/([^/]+/\w+/.+)', 'model_service.resource_handler'),
		(r'/m/([^/]+)', 'model_service.model_handler'),
		(r'/s/([^/]+)', 'model_service.status_handler'),
		(r'/o/([^/]+)', 'model_service.output_handler'),
		(r'/data/([^/]+)/([^/]+)', 'model_service.data_cache_handler'),
		(r'/data/([^/]+)', 'model_service.data_cache_handler')
	]

	_config = {}
	_config['webapp2_extras.sessions'] = {
		'secret_key': 'something-very-secret'
	}

	_app = webapp2.WSGIApplication(routes=_routes, debug=True, config=_config)
	_app.error_handlers[400] = handle_error
	_app.error_handlers[404] = handle_error

	from paste import httpserver
	import config
	httpserver.serve(_app, host=config.get_at('general', 'host'), port=config.get_at('general', 'port'))

def _usage():
	import argparse

	_p = argparse.ArgumentParser()
	_p.add_argument('--logging', dest='logging')
	_p.add_argument('--config', dest='config', required=True)

	return _p.parse_args()

def _init_env():
	import os, sys

	_d_in = os.path.join(sys.path[0], 'lib')
	if os.path.exists(_d_in):
		sys.path.append(_d_in)

	_d_in = os.path.join(sys.path[0], 'var')
	if os.path.exists(_d_in):
		sys.path.append(_d_in)

	_d_in = os.path.join(sys.path[0], 'mod')
	if os.path.exists(_d_in):
		sys.path.append(_d_in)

	_opts = _usage()

	import logging_util
	logging_util.init(_opts.logging)

	import config
	config.load(_opts.config)

	return _opts

if __name__ == '__main__':
	main()

