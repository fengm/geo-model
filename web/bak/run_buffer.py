
def save_polygon(f_out, poly):
	from shapely.geometry import mapping
	import fiona

	_schema = {
		'geometry': 'Polygon',
		'properties': {'id': 'int'},
	}

	with fiona.open(f_out, 'w', 'ESRI Shapefile', _schema) as _fo:
		_fo.write({
			'geometry': mapping(poly),
			'properties': {'id': 123},
		})

def cal_buffer(host, port, proc, pt, dis, f_out):
	import model_client
	import shapely.geometry

	_vars = {'geo': shapely.geometry.Point(pt[0], pt[1]), 'dis': dis}

	_serv = model_client.service(host, port)
	_proc = _serv.run_process(proc, _vars)
	_vars = _proc.run()
	_poly = _vars[_vars.keys()[0]]

	print 'write buffered polygon', f_out
	save_polygon(f_out, _poly)

def main():
	_opts = init_env()
	cal_buffer(_opts.host, _opts.port, _opts.process, _opts.point, _opts.distance, _opts.output)

def usage():
	import argparse

	_p = argparse.ArgumentParser()
	_p.add_argument('--logging', dest='logging')

	_p.add_argument('--host', dest='host', default='159.226.111.26')
	_p.add_argument('--port', dest='port', default=38080)
	_p.add_argument('--process', dest='process', default='mod_buffer.buffer')

	_p.add_argument('-p', '--point', dest='point', required=True, nargs=2, type=float)
	_p.add_argument('-d', '--distance', dest='distance', required=True, type=float)
	_p.add_argument('-o', '--output', dest='output', required=True)

	return _p.parse_args()

def init_env():
	import os, sys
	_d_in = os.path.join(sys.path[0], 'lib')
	if os.path.exists(_d_in):
		sys.path.append(_d_in)

	_opts = usage()

	import logging_util
	logging_util.init(_opts.logging)

	return _opts

if __name__ == '__main__':
	main()
