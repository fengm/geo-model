
import model_type as mt
import model_data as md

@mt.geo_model(
	mt.model('Buffer'),
		[
			mt.parameter(md.d_geometry),
			mt.parameter(md.d_float, unit=['m', 'km'])
		],
		[
			mt.output_parameter('buffered', md.d_polygon)
		])
def buffer(geo, dis):
	return {'buffered': geo.value.buffer(dis.value)}

@mt.geo_model(
	mt.model('Buffer geometries'),
		[
			mt.parameter(md.d_geometry, nargs='+'),
			mt.parameter(md.d_float)
		],
		[
			mt.output_parameter('buffered', md.d_polygon, nargs='+')
		])
def buffers(geos, dis):
	_geos = [_g.buffer(dis.value) for _g in geos.value]
	return {'buffered': _geos}

