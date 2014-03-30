
function add_table_value(ns, vs, tag, val){
	ns.push('<td class="status_tag"><div class="status_tag_text">' + tag + '</div></td>');
	vs.push('<td class="status_val"><div class="status_val_text">' + val + '</div></td>');
}

function list_process_status(status){
	var _tags = [];
	var _vals = [];

	add_table_value(_tags, _vals, 'Done', status.done);
	add_table_value(_tags, _vals, 'Success', status.success);
	add_table_value(_tags, _vals, 'Progress', status.progress + '%');
	add_table_value(_tags, _vals, 'Status', status.status);
	add_table_value(_tags, _vals, 'Error', status.error);
	
	var _txt = '<table class="status_text">';

	_txt += '<tr>' + _tags.join('') + '</tr>';
	_txt += '<tr>' + _vals.join('') + '</tr>';

	_txt += '</table>';

	return _txt
}

function create_func(title, func){
	return '<a href="#" onclick="' + func + ';">' + title + '</a>';
}

function create_link(title, link){
	return '<a target="_blank" href="' + link + '">' + title + '</a>';
}

function load_process_list(){
	$('#c_right').empty();

	$.getJSON('/admin/ps', function(data){
			$('#c_right').append($('<div class="tip_panel">运行模型实例数量:' + count_attrs(data) + '</div>'));

			var _nu = 0;
			$.each(data, function(idx, val){
				var _status = list_process_status(val);
				var _links = '<div>' + [create_func('模型', 'load_model_mete(\'' + val.model_id + '\')'), create_link('元数据', '/d/' + val.model_id), create_link('状态', '/s/' + val.process_id), create_link('结果', '/o/' + val.process_id)].join('&nbsp;') + '</div>';
				var _item = $('<div class="model_item"><div class="model_title"><div style="padding-left: 5px;">' + (++_nu) + ': ' + val.process_id + '&nbsp;(<a style="display:inline-block; font-size: 13px;" href="#" model_id="' + val.model_id + '" onclick="load_model_mete(\'' + val.model_id + '\');">' + val.model_id + '</a>)</div></div>' + _status + _links + '</div>');

				$('#c_right').append(_item);

				// $.each($('a'), function(idx, val){
				// 	if(typeof($.attr(val, 'model_id')) == 'undefined'){
				// 		return;
				// 	}

				// 	$(val).click(function(){
				// 		load_model_mete($(this).attr('model_id'));
				// 	});
				// });
			});
		});
}

function list_model_params(tag, inputs){
	var _vs = [];
	$.each(inputs, function(key, value){
		_name = value.name;
		if($(value).attr('title') != 'undefined'){
			_name = value.title;
		}

		_vs.push('<div class="param_value"><b>' + value.name + '</b>&nbsp;(' + value.d_type.type + ', ' + value.nargs + ')</div>');
	});

	return '<div class="model_input"><div class="param_title">' + tag + ': </div>' + _vs.join('<div style="float:left; margin-right: 10px;">, </div>') + '</div>';
}

function count_attrs(obj){
	var _num = 0;
	$.each(obj, function(key, val){
		_num += 1;
		});

	return _num;
}

function add_info(tag, vs, url){
	if(vs == null || vs.length == 0){
		return '';
	}

	if(vs.length == 1 && typeof(vs[0]) == 'undefined'){
		return '';
	}

	var _txt = '<div class="model_input"><div class="param_title">' + tag + '</div><div clss="param_values">';
	$.each(vs, function(idx, val){
		var _val = val;
		if(typeof(_val) == 'undefined')
			_val = '';

		if(_val.length > 0 && url){
			_url = _val;
			if(_url.substring(0, 3) == '10.'){
				_url = 'http://dx.doi.org/' + _val;
			}
			_txt += '<a target="_blank" href="' + _url + '">' + _val + '</a><pr/>';
		}
		else{
			_txt += _val + '<pr/>';
		}
	});

	_txt += '</div></div>';

	return _txt;
}

function load_model_mete(m_id) {
	$.getJSON('/d/' + m_id, function(data){
			if( data.length == 0){
				alert('No model found with id ' + m_id);
				return;
			}

			var _val = data[0];

			var _inputs = list_model_params('Inputs', _val.inputs);
			var _outputs = list_model_params('Outputs', _val.outputs);

			var _txt = '<div class="model_item" style="font-size: 10px;"><div class="model_title"><div style="padding-left: 5px;">' + _val.model.title + ' &nbsp;<div style="display:inline-block; font-size: 13px;">(' + _val.id + ': <a href="test.html?model_id=' + _val.id + '" target="_blank">测试</a>)' + '</div></div></div>';

			_txt += add_info('Description', [_val.model.desc], false);
			_txt += add_info('Keywords', _val.model.tags, false);
			_txt += _inputs;
			_txt += _outputs;
			_txt += add_info('URLs', _val.model.urls, true);
			_txt += add_info('DOIs', _val.model.dois, true);
			_txt += add_info('References', _val.model.refs, false);

			_txt += '</div>';

			var _item = $(_txt);
			_item.dialog({width: 800, title: _val.model.title, show: function() {$(this).fadeIn(500);}});
		});
}

function load_model_list() {
	$('#c_right').empty();

	$.getJSON('/d/*', function(data){
			$('#c_right').append($('<div class="tip_panel">已共享模型数量:' + count_attrs(data) + '</div>'));

			var _nu = 0;
			$.each(data, function(idx, val){
				var _inputs = list_model_params('Inputs', val.inputs);
				var _outputs = list_model_params('Outputs', val.outputs);

				var _txt = '<div class="model_item"><div class="model_title"><div style="padding-left: 5px;">' + (++_nu) + ': ' + val.model.title + ' &nbsp;<div style="display:inline-block; font-size: 13px;">(' + val.id + ': <a href="test.html?model_id=' + val.id + '" target="_blank">测试</a>)' + '</div></div></div>';

				var _pic = '';
				_txt += '<table><tr><td style="width:120px;"><img style="width:100%;" src="/d/' + val.id + '/pic/0" /></td><td style="vertical-align:top;">';
				_txt += add_info('Description', [val.model.desc], false);
				_txt += add_info('Keywords', val.model.tags, false);
				_txt += _inputs;
				_txt += _outputs;
				_txt += add_info('URLs', val.model.urls, true);
				_txt += add_info('DOIs', val.model.dois, true);
				_txt += add_info('References', val.model.refs, false);
				_txt += '</td></tr></table>'

				_txt += '</div>';

				var _item = $(_txt);
				$('#c_right').append(_item);
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
			if(_tag == 'list_model'){
				load_model_list();
			}
			else if(_tag == 'list_process'){
				load_process_list();
			}
			else{
				alert('Unsupport operation <' + _tag + '>');
			}
			}
		});
}

$(document).ready(function(){
	init_menu();
}); 
