'''
File: model_datacache.py
Author: Min Feng
Version: 0.1
Create: 2013-12-22 01:36:09
Description: provide the functions for managing data caches
'''

import logging

class data_type:

	def __init__(self, ctype, data_types):
		self.ctype = ctype
		self.data_types = data_types

	def _convert(self, f_in, f_ot, d_from, d_to, rec):
		raise Exception('unimplemented function')

class data_type_band(data_type):

	def __init__(self):
		# GDAL format code, single file, suffix
		_data_types = {
			'img': ('HFA', True, '.img'),
			'png': ('PNG', True, '.png'),
			'jpg': ('JPEG', True, '.jpg'),
			'tif': ('GTIFF', True, '.tif'),
			'grid': ('AAIGrid', False, ''),
			'xyz': ('XYZ', True, '.txt'),
			'envi': ('ENVI', False, '.bin')
		}

		data_type.__init__(self, 'band', _data_types)

	def _convert(self, f_in, f_ot, d_from, d_to, rec):
		_cmd = 'gdal_translate -of %s %s %s' % (d_to, f_in, f_ot)
		logging.info('run gdal %s' % _cmd)

		import run_commands
		_ps = run_commands.run(_cmd)
		if _ps[0] != 0:
			raise Exception('failed to process the data')

class data_type_foot(data_type):

	def __init__(self):
		_data_types = {
			'csv': ('csv', True, '.csv'),
			'png': ('png', True, '.png')
		}

		data_type.__init__(self, 'foot', _data_types)

	def _convert(self, f_in, f_ot, d_from, d_to, rec):
		if d_to == 'csv':
			import shutil
			shutil.copyfile(f_in, f_ot)
		elif d_to == 'png':
			self._export_map(f_in, f_ot, rec.get('note', 'Untitle'))
		else:
			raise Exception('unsupported data format')

	def _export_map(self, f_in, f_ot, title):
		import numpy as np
		_dat = np.loadtxt(f_in, delimiter=',')

		import matplotlib
		import matplotlib.figure
		from matplotlib.backends.backend_agg import FigureCanvasAgg

		_fig = matplotlib.figure.Figure(figsize=(4,4))

		_axprops = dict(xticks=[], yticks=[])
		_t = _fig.add_axes((0, 0.92, 1.0, 0.08), frameon=False, **_axprops)
		_t.text(0.2, 0.2, title)
		_p = _fig.add_axes((0, 0, 1.0, 0.92), frameon=False)

		_img = _p.imshow(_dat)

		_fig.colorbar(_img, shrink=0.6, aspect=15)

		_cav = FigureCanvasAgg(_fig)
		_cav.print_png(f_ot)

class data_cache_mag:

	def __init__(self):
		import config
		import pymongo

		self.con = pymongo.MongoClient(config.get_at('general', 'db_connect'))
		self.db = self.con.data_cache
		self.data_caches = self.db.data_caches
		self.cache_path = config.get_at('general', 'data_cache_path')

		self.types = {
			'band': data_type_band(),
			'foot': data_type_foot()
		}

	def generate_url(self, oid):
		import config
		_url = 'http://%s:%s/data/%s' % (config.get_at('general', 'host'), config.get_at('general', 'port'), str(oid))
		return {'type': 'cache', 'url': _url}

	def _save_file(self, f, oid):
		import os
		_ff, _et = os.path.splitext(os.path.basename(f))

		import os
		_f = os.path.join(self.cache_path, '%s_%s%s' % (_ff, str(oid), _et))
		logging.info('save file %s to %s' % (f, _f))

		import shutil
		shutil.copyfile(f, _f)

		return _f

	def insert(self, filepath, ctype, dtype, username, note=''):
		if ctype not in self.types:
			raise Exception('supported type %s' % ctype)

		from bson.objectid import ObjectId
		_id = ObjectId()
		_fp = self._save_file(filepath, _id)

		import datetime
		import os
		_rec = {'_id': _id, 'filename': os.path.basename(filepath), 'filepath': _fp,
		  'ctype': ctype, 'dtype': dtype, 'note': note,
		  'username': username, 'create_date': datetime.datetime.utcnow()}

		return str(self.data_caches.insert(_rec))

	def insert_band(self, bnd, username, note=''):
		import file_unzip
		import config

		with file_unzip.file_unzip(config.get_at('general', 'tmp_path')) as _zip:
			_f = _zip.generate_file('', '.tif')
			bnd.save(_f)

			return self.insert_file(_f, 'band', 'tif', username, note)

	def _find(self, oid):
		from bson.objectid import ObjectId
		return self.data_caches.find_one(ObjectId(oid))

	def _output_file_name(self, filepath, filename, suffix, fzip):
		logging.info('generate output file name %s, %s %s' % (filepath, filename, suffix))

		import os
		_dir = fzip.generate_file('', '')

		os.makedirs(_dir)
		_ff = os.path.join(_dir, '%s%s' % (os.path.splitext(filename)[0], suffix))
		logging.info('generated file %s' % _ff)

		return _ff

	def _pack_folder(self, d_in, f_ot, fzip):
		import zipfile
		import os

		_d_ot = fzip.generate_file('', '')
		os.makedirs(_d_ot)

		_f_ot = os.path.join(_d_ot, os.path.splitext(f_ot)[0] + '.zip')
		print 'pack', d_in, 'into', _f_ot
		with zipfile.ZipFile(_f_ot, 'w') as _zip:
			for _root, _dirs, _files in os.walk(d_in):
				for _file in _files:
					_fn = os.path.join(_root, _file)
					_fo = _fn.replace(d_in + '/', '')
					_zip.write(_fn, _fo)

		return _f_ot

	def load(self, oid, dtype, fzip):
		from bson.objectid import ObjectId
		_id = oid
		if not isinstance(_id, ObjectId):
			_id = ObjectId(_id)

		_rec = self._find(_id)
		if _rec == None:
			raise Exception('no resource found with id (%s)' % str(_id))

		_c_type = _rec['ctype']
		if _c_type not in self.types:
			raise Exception('unsupported data type')

		_handle = self.types[_c_type]

		_d_type = _rec['dtype']
		_s_type = _handle.data_types[_d_type]
		_t_type = _handle.data_types[dtype if dtype else _d_type]

		_f_out = self._output_file_name(_rec['filepath'], _rec['filename'], _t_type[2], fzip)
		_handle._convert(_rec['filepath'], _f_out, _s_type[0], _t_type[0], _rec)

		if _t_type[1] == False:
			import os
			return self._pack_folder(os.path.dirname(_f_out), _rec['filename'], fzip)

		return _f_out

