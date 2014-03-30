# -*- coding: utf-8 -*-

import model_type as mt
import model_data as md

@mt.geo_model(
	mt.model('Test'),
		[
			mt.parameter(md.d_int),
			mt.parameter(md.d_float)
		],
		[
			mt.output_parameter('val', md.d_int, nargs='+')
		])
def test(pt, dist, env):
	import time

	for i in range(pt.value):
		time.sleep(1)
		env.progress = i * 100 / pt.value
		env.status = '完成了%d%%' % (i * 100 / pt.value)
		env.outputs['val'].value.append(i)

	# return {'val': 100}

