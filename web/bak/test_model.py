

def main():
	init_env()

	import geo_raster_c as ge
	_bnd = ge.geo_raster.open('/home/mfeng/work/test/raster/lucc_ansai.tif').get_band().cache()
	_bnd.pixel_type = 2

	import model_data
	_txt = model_data.d_band.encode(_bnd)

	import json
	_txt = json.dumps(_txt, default=model_data.convert_to_builtin_type, indent=2, sort_keys=True)

	_obj = json.loads(_txt)
	_bnd = model_data.d_band.decode(_obj)

def usage():
	import argparse

	_p = argparse.ArgumentParser()
	_p.add_argument('--logging', dest='logging')

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
