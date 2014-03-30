
import model_type as mt
import model_data as md

@mt.geo_model(
	mt.model('Reproject geometries'),
		[
			mt.parameter(md.d_point, nargs='+'),
			mt.parameter(md.d_proj)
		],
		[
			mt.output_parameter('geom', md.d_point, nargs='+')
		])
def reproject(geoms, proj_t):
	import geo_raster_ex_c as gx
	import shapely.geometry

	_geoms = []
	for _geom in geoms.value:
		_pt = gx.geo_point(_geom.x, _geom.y, geoms.attrs['proj'])
		_pp = _pt.project_to(proj_t.value)

		_geoms.append(shapely.geometry.Point(_pp.x, _pp.y))

	return {'geom': _geoms}
