# -*- coding: utf-8 -*-

import model_type as mt
import model_data as md
import cal_index

@mt.geo_model(
	mt.model('NDWI', 'Normalized Difference Water Index',
			refs=['Gao, B. (1996). NDWI-a normalized difference water index for remote sensing of vegetation liquid water from space. Remote sensing of environment, 266(April 1995), 257-266'],
			urls=['http://www.sciencedirect.com/science/article/pii/S0034425796000673'],
				contact=[mt.contact_info('Min Feng', email='feng.tank@gmail.com', affiliation=mt.affiliation_info('中国科学院地理科学与资源研究所', '朝阳区大屯路甲11号', '北京', '中国', 100101))]
		  ),
		[
			mt.parameter(md.d_band, 1, 'RED', 'Red band'),
			mt.parameter(md.d_band, 1, 'SWIR', 'SWIR band')
		],
		[
			mt.output_parameter('ndwi', md.data_band(md.d_float), title='NDWI')
		]
		)
def ndwi(b_red, b_swir):
	return {'ndwi': cal_index.index_cal(b_red.value, b_swir.value)}

@mt.geo_model(
	mt.model('MNDWI', 'Modified Normalized Difference Water Index',
			refs=['Xu, H. (2006). Modification of normalised difference water index (NDWI) to enhance open water features in remotely sensed imagery. International Journal of Remote Sensing, 27(14), 3025-3033'],
			dois=['10.1080/01431160600589179']
		  ),
		[
			mt.parameter(md.d_band, 1, 'GREEN', 'GREEN band'),
			mt.parameter(md.d_band, 1, 'SWIR', 'SWIR band')
		],
		[
			mt.output_parameter('ndwi', md.data_band(md.d_float), title='MNDWI')
		]
		)
def mndwi(b_green, b_swir):
	return {'mndwi': cal_index.index_cal(b_green.value, b_swir.value)}

