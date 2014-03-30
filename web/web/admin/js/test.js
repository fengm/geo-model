
function add_input_param(block, val){
	var _name = val.name;
	var _type = val.d_type.type;

	if($.inArray(_type, ['int', 'float', 'double']) >= 0){
		_txt = '<div><span class="text_label">' + _name + ':</span><input style="width: 500px;float:left;" id="val_input_' + _name + '"></input></div>';
		$(_txt).appendTo(block);
	}
	if($.inArray(_type, ['geometry', 'point', 'line', 'polygon']) >= 0){
		_txt = '<div style="vertical-align: text-top;"><span class="text_label">' + _name + ':</span><textarea style="float:left;width: 550px;font-size: 13px; height: 100px;" id="val_input_' + _name + '"></textarea><div style="float: left;" id="btn_sel_input_' + _name + '">地图</div></div>';
		$(_txt).appendTo(block);
		$('#btn_sel_input_' + _name).button();
		$('#btn_sel_input_' + _name).click(function(){
			init_map_panel();
		});
	}
}

function add_output_param(block, val){
	var _name = val.name;
	var _type = val.d_type.type;

	if($.inArray(_type, ['int', 'float', 'double']) >= 0){
		_txt = '<div><span class="text_label">' + _name + ':</span><input style="width: 500px;float:left;" id="val_output_' + _name + '"></input></div>';
		$(_txt).appendTo(block);
	}
	if($.inArray(_type, ['geometry', 'point', 'line', 'polygon']) >= 0){
		_txt = '<div style="vertical-align: text-top;"><span class="text_label">' + _name + ':</span><textarea style="float:left;font-size: 13px;width: 550px; height: 100px;" id="val_output_' + _name + '"></textarea><div style="float: left;" id="btn_sel_output_' + _name + '">地图</div></div>';
		$(_txt).appendTo(block);
		$('#btn_sel_output_' + _name).button();
		$('#btn_sel_output_' + _name).click(function(){
			init_map_panel();
		});
	}
}

_data = null;
_p_id = null;
_t_id = -1;

function run_model(){
	$('#mod_progress').progressbar({"value": 0});

	if(_data == null)
		return;

	var _vs = {};
	var _error = false;
	$.each(_data.inputs, function(key, val){
		var _name = val.name;
		var _text = $('#val_input_' + _name).prop('value');
		if(_text == ''){
			_error = true;
			alert('No input for ' + val.name);
			return;
		}

		_vs[_name] = _text;
	});

	if (_error)
		return;

	$.post('/m/' + _data.id, _vs, function(data, textStatus){
		var _id = data.process_id;
		_p_id = _id;
		_t_id = setInterval(check_status, 500);
	}, 'json');
}

function check_status(){
	$.getJSON('/s/' + _p_id, function(data){
		$('#mod_progress').progressbar({"value": parseInt(data.progress)});
		$('#mod_progress_label').html(data.status);

		if(data.error != '' || data.progress >= 100){
			clearInterval(_t_id);
		}

		if(data.done){
			load_outputs();
		}
	});
}

function load_outputs() {
	$.getJSON('/o/' + _p_id, function(data){
		$.each(data.outputs, function(key, val){
			var _text = $('#val_output_' + key).prop('value', JSON.stringify(val));
		});
	});
}

function load_model_mete(m_id) {
	$.getJSON('/d/' + m_id, function(data){
			if( data.length == 0){
				alert('No model found with id ' + m_id);
				return;
			}

			var _val = data[0];
			_data = _val;

			var _box = $('#c_right');
			_box.append($('<div style="float:left; margin-top: 15px;">&nbsp;</div>'));

			$.each(_val.inputs, function(idx, val){
				add_input_param(_box, val);
			});

			_box.append($('<div style="clear: both; float:left; margin-top: 5px;">&nbsp;</div>'));

			var _btn_run = $('<div style="clear: both; float: left;">运行模型<div>').button();
			_box.append(_btn_run);

			_btn_run.click(function(){
				run_model();
			});

			var _prg = $('<div style="float:left; width: 500; margin-left: 30px;" id="mod_progress"></div>').progressbar();
			_box.append(_prg);

			var _prg_label = $('<div style="float:left; margin-left: 5px; width: 150; clear: right; overflow: hidden;" id="mod_progress_label"></div>');
			_box.append(_prg_label);

			_box.append($('<div style="clear: both; float:left; margin-top: 5px;">&nbsp;</div>'));

			$.each(_val.outputs, function(idx, val){
				add_output_param(_box, val);
			});
		});
}

function init_menu() {
	var _items = [
		['管理用户列表', 'list_user'],
		['共享模型列表', 'list_model'],
		['运行模型列表', 'list_process']
	];

	var _div = $('#menu');
	$.each(_items, function(idx, val){
		var _item = $('<li><a href="#" tag="' + val[1] + '">' + val[0] + '</a></li>');
		_div.append(_item);
	});

	_div.menu({
		select: function(event, ui){
			var _tag = $(ui.item.children()[0]).attr('tag');
		}});
}

$(document).ready(function(){
	init_menu();

	var _model_id = $.url().param('model_id');
	console.log('model_id:' + _model_id);

	// init_map_panel();

	$('#btn_test').button().click(function(){
		init_map_panel();
	});

	load_model_mete(_model_id);
}); 
