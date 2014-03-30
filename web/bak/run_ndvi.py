

def load_band(f, fzip):
	import geo_raster_c as ge

	_img = ge.geo_raster.open(fzip.unzip(f))
	_bnd = _img.get_band().cache()
	_bnd.nodata = 0

	return _bnd

def cal_ndvi(host, port, proc, b_nir, b_red, f_out):
	import model_client
	import file_unzip

	with file_unzip.file_unzip() as _zip:
		_vars = {'b_nir': load_band(b_nir, _zip), 'b_red': load_band(b_red, _zip)}

		_serv = model_client.service(host, port)
		_proc = _serv.run_process(proc, _vars)
		_vars = _proc.run()
		_ndvi = _vars[_vars.keys()[0]]

		print 'write NDVI', f_out
		_ndvi.save(f_out)

def main():
	_opts = init_env()
	cal_ndvi(_opts.host, _opts.port, _opts.process, _opts.band_nir, _opts.band_red, _opts.output)

def usage():
	import argparse

	_p = argparse.ArgumentParser()
	_p.add_argument('--logging', dest='logging')

	_p.add_argument('--host', dest='host', default='159.226.111.26')
	_p.add_argument('--port', dest='port', default=38080)
	_p.add_argument('--process', dest='process', default='mod_ndvi.ndvi')

	_p.add_argument('-b1', '--band-nir', dest='band_nir', required=True)
	_p.add_argument('-b2', '--band-red', dest='band_red', required=True)
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

