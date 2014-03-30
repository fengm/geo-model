
def main():
	_opts = _init_env()

	import model_data_cache
	_mag = model_data_cache.data_cache_mag()

	# _id = _mag.insert('/home/mfeng/local/test/fcc_1975/p224r078/test/test1.img', 'band', 'mfeng')
	_id = _mag.insert('/home/mfeng/local/test/model_sharing/footprint/monthly/test2005_6_purefp.csv', 'foot', 'csv', 'mfeng')
	print _id

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
