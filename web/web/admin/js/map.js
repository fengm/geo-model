
function init_map_panel(){
	var _panel = $('#p_map');
	if(_panel.length == 0){
		var _txt = ''; 
		_txt += '<div id="p_map" style="clear: both; padding: 0px; margin: 0px;text-align: left;">';

		_txt += '<div id="controlToggle" style="text-align:left;">';
		var _tools = ['pan', 'point', 'line', 'polygon']
		$.each(_tools, function(idx, val){
			var _checked = '';
			if(idx == 0)
				_checked = ' checked="checked"';
			_txt += '<input type="radio" name="type" tag="' + val + '" id="rad_' + val + '"' + _checked + '/><label for="rad_' + val + '">' + val + '</label>';
		});
		_txt += '</div>';

		_txt += '<div id="c_map" style="height: 400px;"></div>';

		_txt += '<div style="text-align: left;"><div id="btn_map_select">选择</div></div>';
		_txt += '</div>';

		_panel = $(_txt);
		_panel.dialog({width: 800, height: 490});

		init_map();
		$( "#controlToggle" ).buttonset().change(function(){
				var _sel = $('#controlToggle :radio:checked');
				if(_sel.length == 0){
					return;
				}
				toggleControl(_sel.attr('tag'));
			});

		$('#btn_map_select').button();
	}
	else{
		_panel.dialog();
	}
}

var map, drawControls;
function init_map(){
	map = new OpenLayers.Map('c_map', {
        projection: 'EPSG:3857',
		layers: [new OpenLayers.Layer.Google(
			"Google Physical",
			{type: google.maps.MapTypeId.TERRAIN, numZoomLevels: 20}
		)],
        center: new OpenLayers.LonLat(10.2, 48.9)
            .transform('EPSG:4326', 'EPSG:3857'),
        numZoomLevels: 20});

	var pointLayer = new OpenLayers.Layer.Vector("Point Layer");
	var lineLayer = new OpenLayers.Layer.Vector("Line Layer");
	var polygonLayer = new OpenLayers.Layer.Vector("Polygon Layer");
	var boxLayer = new OpenLayers.Layer.Vector("Box layer");

	map.addLayers([pointLayer, lineLayer, polygonLayer, boxLayer]);
	// map.addControl(new OpenLayers.Control.LayerSwitcher());
	map.addControl(new OpenLayers.Control.MousePosition({displayProjection: 'EPSG:4326'}));

	drawControls = {
		point: new OpenLayers.Control.DrawFeature(pointLayer,
			OpenLayers.Handler.Point),
		line: new OpenLayers.Control.DrawFeature(lineLayer,
			OpenLayers.Handler.Path),
		polygon: new OpenLayers.Control.DrawFeature(polygonLayer,
			OpenLayers.Handler.Polygon)
	};

	for(var key in drawControls) {
		map.addControl(drawControls[key]);
	}

	map.setCenter(new OpenLayers.LonLat(0, 0), 3);
}

function toggleControl(tag) {
	for(key in drawControls) {
		var control = drawControls[key];
		if(key == tag) {
			control.activate();
		} else {
			control.deactivate();
		}
	}
}

function allowPan(element) {
	var stop = !element.checked;
	for(var key in drawControls) {
		drawControls[key].handler.stopDown = stop;
		drawControls[key].handler.stopUp = stop;
	}
}
