# -*- coding: utf-8 -*-

import model_type as mt
import model_data as md
import cal_index

@mt.geo_model(
	mt.model('NDVI', 'Normalized Difference Vegetation Index'),
		[
			mt.parameter(md.data_band(md.d_float), title='NIR', desc='NIR band'),
			mt.parameter(md.data_band(md.d_float), title='RED', desc='Red band')
		],
		[
			mt.output_parameter('ndvi', md.data_band(md.d_float), title='NDVI')
		])
def ndvi(b_nir, b_red):
	return {'ndvi': cal_index.index_cal(b_nir.value, b_red.value)}

@mt.geo_model(
	mt.model('NDVI series', 'Provide NDVI series at a given location'),
	[
		mt.parameter(md.d_point, '+', 'Location', 'Location for retrieving the NDVI values'),
		mt.parameter(md.d_proj, '?', 'Projection', 'CRS of the location'),
		mt.parameter(md.d_int, '+', 'Year', 'Years of the NDVI')
	],
	[
		mt.output_parameter('ndvi', md.data_feature([md.data_item('date', md.data_time('%Y-%j')), md.data_item('ndvi', md.d_float)]), nargs='+')
	]
)
def ndvi_series(pts, proj, years):
	_vs = []
	_vs.append({'date': '2000-010', 'ndvi': 322})

	return {'ndvi': _vs}

