
import logging
import numpy as np
import geo_raster_c as ge

def index_cal(b1, b2):
	logging.info('calculate index')

	if b1.nodata != None and b2.nodata != None:
		return index_cal_ma(b1, b2)

	_dat1 = b1.data.astype(np.float32)
	_dat2 = b2.data.astype(np.float32)

	_dat = (_dat1 - _dat2) / (_dat1 + _dat2)

	_dat[_dat > 1] = 1
	_dat[_dat < -1] = -1

	import copy
	_bnd = copy.copy(b1)
	_bnd.data = _dat
	_bnd.pixel_type = ge.pixel_type('float')

	return _bnd

def index_cal_ma(b1, b2):
	logging.info('calculate index with masked array')

	_dat1 = np.ma.masked_equal(b1.data.astype(np.float32), b1.nodata)
	_dat2 = np.ma.masked_equal(b2.data.astype(np.float32), b2.nodata)

	_dat = (_dat1 - _dat2) / (_dat1 + _dat2)

	_dat[_dat > 1] = 1
	_dat[_dat < -1] = -1

	import copy
	_bnd = copy.copy(b1)
	_bnd.data = _dat.filled(-9999)
	_bnd.pixel_type = ge.pixel_type('float')
	_bnd.nodata = -9999

	return _bnd

