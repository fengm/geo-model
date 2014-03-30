# -*- coding: utf-8 -*-

import model_type as mt
import model_data as md
import logging

@mt.geo_model(
	mt.model('Foot Print',
		refs=['Chen, B., Black, A., Coops, N. C., Hilker, T., Trofymow, T., Nesic, Z., & Morgenstern, K. (2009). Assessing tower ﬂux footprint climatology and scaling between remotely sensed and eddy covariance measurements. Boundary-Layer Meteorology, 130, 137–167.'],
		dois=['10.1007/s10546-008-9339-1'],
	),
	[
		mt.parameter(md.d_float, title='Canopy Height', unit='m', desc='Height of canopy'),
		mt.parameter(md.d_float, title='Height of EC', unit='m', desc='Height of EC (eddy-covariance) sensor'),
		mt.parameter(md.d_float, title='Pixel Size', unit='m', desc='Pixel size of footprint'),
		mt.parameter(md.d_float, title='Year', unit='m', desc='Year for calculating'),
	],
	[mt.output_parameter('c_pdf', md.data_band(md.d_float), nargs='+', title='Cumulative footprint PDF')]
)
def foot_print(h_c, z_m, pixel, year, env):
	_fig = env.metadata.cfg

	# use parameters from the config file
	f_foot_print = _fig.get('path', 'foot_print')
	f_matlab = _fig.get('path', 'matlab')
	d_input = _fig.get('path', 'sample_input')
	c_hhr_save = _fig.getint('param', 'save_hhr')

	# f_foot_print = '/data/mfeng/lib/footprint/code/run_SAFEmain.sh'
	# f_matlab = '/usr/local/matlab'
	# d_out='/data/mfeng/lib/footprint/test/test'
	# d_input='/data/mfeng/lib/footprint/code/sample.csv'
	# c_hhr_save=0

	c_h_c=h_c.value #3
	c_z_m=z_m.value #9
	c_pix=pixel.value #30
	c_site_id='test_'

	year = 2005 #use year 2005
	c_start_year=year
	c_end_year=year

	d_out = env.fzip.generate_file()
	logging.info('output dir: %s' % d_out)
	import os
	os.makedirs(d_out)

	import subprocess_ex
	import datetime
	import re

	_cmd = [f_foot_print, f_matlab, d_out, c_h_c, c_z_m, c_pix, c_site_id, c_start_year, c_end_year, d_input, c_hhr_save]
	logging.info('cmd: %s' % ' '.join([str(_v) for _v in _cmd]))
	_p = subprocess_ex.Popen([str(_v) for _v in _cmd], stdout=subprocess_ex.PIPE)

	_ts = []
	while True:
		_txt = _p.asyncread()
		if _txt:
			_m = re.search('(\d+-\w+-\d{4})', _txt)
			if _m:
				_d = datetime.datetime.strptime(_m.group(1), '%d-%b-%Y')
				env.status = _format_status_txt(_txt.strip()) #_m.group(1)

				_prg = min((int(_d.strftime('%j')) * 100) / 365, 100)
				if _prg != env.progress:
					logging.info('progress: %s%%, %s' % (_prg, env.status))
					_ingest_outputs(d_out, env.data_cache, _ts, env.outputs['c_pdf'])
				env.progress= _prg

		if _p.poll() != None:
			break

	_ingest_outputs(d_out, env.data_cache, _ts, env.outputs['c_pdf'])

def _format_status_txt(txt):
	import re
	_m = re.search('(\d+-\w+-\d{4}).+(\d+)/(\d+)', txt)

	import datetime
	_d = datetime.datetime.strptime(_m.group(1), '%d-%b-%Y')

	_t = '%s: %02d/%02d' % (_d.strftime('%Y-%m-%d'), int(_m.group(2)), int(_m.group(3)))
	return _t

def _ingest_outputs(d_in, mag, ts, out):
	import os
	import re

	_ids = []
	for _root, _dirs, _files in os.walk(d_in):
		for _file in _files:
			if 'monthly' not in _root:
				continue

			_m = re.search('\D(\d+)_(\d+)_cumu.*\.csv', _file)
			if _m:
				_tt = '%s-%02d' % (_m.group(1), int(_m.group(2)))
				if _tt in ts:
					continue
				ts.append(_tt)

				_id = mag.insert(os.path.join(_root, _file), 'foot', 'csv', 'mfeng', note=_tt)
				_ids.append(_id)

				logging.info('adding cached file %s' % str(_id))
				out.value.append(md.data(mag.generate_url(_id), {'date': _tt}))
	return _ids
