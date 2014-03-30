
def main():
	_opts = _init_env()

	import model_data_cache
	_mag = model_data_cache.data_cache_mag()

	# _id = _mag.insert('/home/mfeng/local/test/fcc_1975/p224r078/test/test1.img', 'band', 'mfeng')
	_d_in = '/data/mfeng/lib/footprint/test/test/test/monthly'

	import os
	import re

	for _root, _dirs, _files in os.walk(_d_in):
		for _file in _files:
			_m = re.search('\w(\d+)_(\d+)_cumu.*\.csv', _file)
			if _m:
				_t = '%s_%02d' % (_m.group(1), int(_m.group(2)))
				_id = _mag.insert(os.path.join(_root, _file), 'foot', 'csv', 'mfeng', note=_t)
				print _id

	# import file_unzip
	# with file_unzip.file_unzip() as _zip:
	# 	_id = '52b75473e13823059255faea'
	# 	_ff = _mag.load(_id, 'png', _zip)

	# 	print _ff

def _usage():
	import argparse

	_p = argparse.ArgumentParser()
	_p.add_argument('--logging', dest='logging')
	_p.add_argument('--config', dest='config')

	return _p.parse_args()

def _init_env():
	import os, sys
	_d_in = os.path.join(sys.path[0], 'lib')
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
