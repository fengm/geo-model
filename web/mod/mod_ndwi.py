# -*- encoding: utf-8 -*-

import model_type as mt
import model_data as md

@mt.geo_model(
	mt.model('NDWI', 'Normalized Difference Water Index',
			refs=['McFeeters, S.K., 1996. The use of Normalized Difference Water Index (NDWI) in the delineation of open water features, International Journal of Remote Sensing, 17(7):1425-1432'],
			urls=['http://www.tandfonline.com/doi/abs/10.1080/01431169608948714'],
			dois=['10.1080/01431169608948714']
		  ),
		[
			mt.parameter(md.d_band, title='GREEN', desc='GREEN band'),
			mt.parameter(md.d_band, title='NIR', desc='NIR band')
		],
		[
			mt.output_parameter('ndwi', md.data_band(md.d_float), title='NDWI')
		]
		)
def ndwi(b_green, b_nir):
	import cal_index
	return {'ndwi': cal_index.index_cal(b_green.value, b_nir.value)}

