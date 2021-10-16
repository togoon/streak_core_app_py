var js_parsing_tree = null;
var state = 1;
var equity_added = {};
var cursor_loc = 0;
var pref_data = null;
var lastest_item = [];
var default_preferences = {'drag_container1':['at_price'],
							'drag_container2_ti':['sma','ema','rsi','macd','macd_signal','obv','atr','aroon_up','aroon_down','number'],
							'drag_container2_ohlcv':['open','high','low','close'],
							'drag_container3':['higher_than','lower_than']
							};

function show_tooltip(event,title,description,pos='up'){
	tooltip='<div class="tooltip_top" id="tooltip"><div class="tt_container"><div class="tt_header"><p>'+title+'</p></div><div class="tt_body"><div class="tt_content"><p>'+description+'</p></div></div></div></div>';
	if(pos!='up')
		{
			// $(event.target).before(tooltip);
		}
	else
		{
			// $(event.target).after(tooltip);
		}
	// return tooltip;
}
// document.addEventListener('contextmenu', function(e) {
//   e.preventDefault();
// });
function remove_tooltip(event,title,description,pos='up'){
	// tooltip='<div class="tooltip_top" id="tooltip"><div class="tt_container"><div class="tt_header"><p>'+title+'</p></div><div class="tt_body"><div class="tt_content"><p>'+description+'</p></div></div></div></div>';
	// $(event.target).before(tooltip);
	// if(pos!='up')
	// 	$(event.target).before(tooltip);
	// else
	// 	$(event.target).after(tooltip);
	setTimeout(function(){
		$('.tooltip_top').remove();
	},200);
	// return tooltip;
}
function pref_loader(data){
	if(data['status']){
		pref_data = data;

		drag_container1 = []; 
		drag_container2_ti = [];
		drag_container2_ohlcv = [];
		drag_container3 = [];

		if (data['ti_indicators'] != null)
			drag_container2_ti = data['ti_indicators'];

		if (data['ohlcv_indicators'] != null)
			drag_container2_ohlcv = data['ohlcv_indicators'];

		if (data['comparators'] != null)
			drag_container3 = data['comparators'];

	  	default_preferences.drag_container2_ti = arrayUnique(drag_container2_ti.concat(default_preferences.drag_container2_ti));

	  	default_preferences.drag_container2_ohlcv = arrayUnique(drag_container2_ohlcv.concat(default_preferences.drag_container2_ohlcv));
	  	
	  	default_preferences.drag_container3 = arrayUnique(drag_container3.concat(default_preferences.drag_container3));
	  	
	  	if(default_preferences.drag_container2_ti.length>=20){
	  		default_preferences.drag_container2_ti = default_preferences.drag_container2_ti.slice(0,20);
	  	}
	  	if(default_preferences.drag_container2_ohlcv.length>=20){
	  		default_preferences.drag_container2_ohlcv = default_preferences.drag_container2_ohlcv.slice(0,20);
	  	}
	  	if(default_preferences.drag_container3.length>=20){
	  		default_preferences.drag_container3 = default_preferences.drag_container3.slice(0,20);
	  	}
	  	$('#drag_container1 #drag_tech_elements').html('');
	  	$('#drag_container2 #drag_tech_elements').html('');
	  	$('#drag_container3 #drag_comp_elements').html('');

	  	for(var i=0;i<default_preferences.drag_container1.length;i++){
	  		key = default_preferences.drag_container1[i];
	  		item = js_parsing_tree.main.indicator[key];
	  		
	  		if(lastest_item)
	  			latest_indicator = lastest_item[0]
	  		if(i==1)
	  			$('#drag_container1 #drag_tech_elements').append('<br>');

	  		if(cursor_loc%3==1) // if first indiactor has been dropped
		  	{
		  		$('#drag_container1 #drag_tech_elements').append('<span class="ti disabled_'+item.html_tags+'" id="'+key+'">&nbsp;'+item.name+'</span>');	
		  	}
	  		else if(cursor_loc%3==2 && !latest_indicator['allowed_comparision'].includes(item['function_group']))
	  		{
	  			$('#drag_container1 #drag_tech_elements').append('<span class="ti disabled_'+item.html_tags+'" id="'+key+'">&nbsp;'+item.name+'</span>');
	  		}
	  		else{
	  			$('#drag_container1 #drag_tech_elements').append('<span draggable="true" onclick="custom_click(event)" ondragstart="drag(event);" class="ti '+item.html_tags+'" id="'+key+'" data-tooltip-bottom="'+item.tooltip+'" onmouseover="show_tooltip(event,\''+item.tooltip+'\',\''+item.description+'\')" onmouseout="remove_tooltip(event,\''+item.tooltip+'\',\''+item.description+'\')">&nbsp;'+item.name+'</span>');
	  		}
	  	}

	  	for(var i=0;i<default_preferences.drag_container2_ti.length;i++){
	  		key = default_preferences.drag_container2_ti[i];
	  		item = js_parsing_tree.main.indicator[key];
	  		
	  		if(lastest_item)
	  			latest_indicator = lastest_item[0]

	  		if(cursor_loc%3==1) // if first indiactor has been dropped
		  	{
		  		$('#drag_container2 #drag_tech_elements').append('<span class="ti disabled_'+item.html_tags+'" id="'+key+'">&nbsp;'+item.name+'</span>');	
		  	}
	  		else if(cursor_loc%3==2 && !latest_indicator['allowed_comparision'].includes(item['function_group']))
	  		{
	  			$('#drag_container2 #drag_tech_elements').append('<span class="ti disabled_'+item.html_tags+'" id="'+key+'">&nbsp;'+item.name+'</span>');
	  		}
	  		else{
	  			$('#drag_container2 #drag_tech_elements').append('<span draggable="true" onclick="custom_click(event)" ondragstart="drag(event);" class="ti '+item.html_tags+'" id="'+key+'"  data-tooltip-top="'+item.tooltip+'" onmouseover="show_tooltip(event,\''+item.tooltip+'\',\''+item.description+'\')" onmouseout="remove_tooltip(event,\''+item.tooltip+'\',\''+item.description+'\')">&nbsp;'+item.name+'</span>');
	  		}
	  		// $('#drag_container2 #drag_tech_elements').append(attach_tooltip(item.tooltip,item.description));
	  	}

	  	// $('#drag_container2 #drag_tech_elements').append('<br><br>');

	  	for(var i=0;i<default_preferences.drag_container2_ohlcv.length;i++){ // ohlcv loader
	  		key = default_preferences.drag_container2_ohlcv[i];
	  		item = js_parsing_tree.main.indicator[key];

	  		if(lastest_item)
	  			latest_indicator = lastest_item[0]

	  		if(cursor_loc%3==1) // if first indiactor has been dropped
		  	{
		  		$('#drag_container2 #drag_tech_elements').append('<span class="ti disabled_'+item.html_tags+'" id="'+key+'">&nbsp;'+item.name+'</span>');
		  	}
		  	else if(cursor_loc%3==2 && !latest_indicator['allowed_comparision'].includes(item['function_group']))
		  	{
		  		$('#drag_container2 #drag_tech_elements').append('<span class="ti disabled_'+item.html_tags+'" id="'+key+'">&nbsp;'+item.name+'</span>');
		  	}
		  	else
	  			$('#drag_container2 #drag_tech_elements').append('<span draggable="true" onclick="custom_click(event)" ondragstart="drag(event);" class="ti '+item.html_tags+'" id="'+key+'" onmouseover="show_tooltip(event,\''+item.tooltip+'\',\''+item.description+'\')" onmouseout="remove_tooltip(event,\''+item.tooltip+'\',\''+item.description+'\')">&nbsp;'+item.name+'</span>');
	  	}

	  	for(var i=0;i<default_preferences.drag_container3.length;i++){
	  		key = default_preferences.drag_container3[i];
	  		item = js_parsing_tree.main.comparator[key];

	  		if(cursor_loc%3==0 || cursor_loc%3==2){
	  			$('#drag_container3 #drag_comp_elements').append('<span draggable="true" class="co disabled_'+item.html_tags+'" id="'+key+'">&nbsp;'+item.name+'</span>');
			}
			else{
	  			$('#drag_container3 #drag_comp_elements').append('<span draggable="true" onclick="custom_click(event)" ondragstart="drag(event);" class="co '+item.html_tags+'" id="'+key+'" onmouseover="show_tooltip(event,\''+item.tooltip+'\',\''+item.description+'\')" onmouseout="remove_tooltip(event,\''+item.tooltip+'\',\''+item.description+'\')">&nbsp;'+item.name+'</span>');

			}
	  	}
	  	console.log('preference loaded');
	}
	else{

	}$(".loader_parent").fadeOut();
};

function update_pref(key){
	var form = new FormData();
	form.append("indicator", key);
	var settings = {
	  "async": true,
	  "crossDomain": true,
	  "url": "/update_preference/",
	  "method": "POST",
	  "headers": {
	    "cache-control": "no-cache",
	    "postman-token": "77a10891-d9c6-30bf-2c5a-8fcf20b41b09"
	  },
	  "processData": false,
	  "contentType": false,
	  "mimeType": "multipart/form-data",
	  "data": form
	}
	$.ajax(settings).done(function (response) {
	  console.log('pref updated');
	  load_toolbar();

	});
};
// loading preferences
function load_toolbar(){
	var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
	params = {
	  'csrfmiddlewaretoken':csrfmiddlewaretoken
	};
	$.get('/load_preference/', params,function(data) {
	// alert(data);
		pref_loader(data);
	});

};

function section_complete(params){ // ids list
	section_done = true;
	for(var i=0;i<params.length;i++){
		if($('#'+params[i]).val()=='')
			section_done = false;

		if($('#'+params[i]).val()==null)
			section_done = false;
	}
	return section_done;
};

function footer_updater(){
	// strategy details updater
	if($('#ip_strategy_name').val()=='' || $('#ip_strategy_name').val().length<3)
		$('.strategy_name p').html('Algorithm name');
	else{
		$('.strategy_name p').html($('#ip_strategy_name').val())
	}
	$('.strategy_desc p').html('');
	// if($('#ip_strategy_desc').val()=='' || $('#ip_strategy_desc').val().length<3)
	// 	$('.strategy_desc p').html('Algorithm description');
	// else{
	// 	$('.strategy_desc p').html($('#ip_strategy_desc').val())
	// }
	// entry summary
	txt = ''
	if ($("#ip_position_type").val()=='Buy')
		txt += 'Buy ';
	else
		txt += 'Sell ';

	if ($("#ip_position_qty").val()!=undefined)
		txt += $("#ip_position_qty").val()+' shares ';
			
	txt += 'when ';
  	$("#display_condition1").find('span').each(function(e){ 
  		if($(this).text()!='Clear')
  			txt = txt + ' ' + $(this).text();
  	});
  	if(cursor_loc%3==0)
  	$(".and_or").each(function(e){ 
		andor1 = $(this).find("#andor option:selected").val();

		// injecting hidden <p> which will be used later select and/or during page revisit
		$(this).find("#andor_save").each(function(e,obj){$(obj).remove();});

		$(this).append("<p id='andor_save' style='display:none'>"+andor1+"</p>");
		  andor1_input = '';

		$(this).find("span").each(function(e,obj){
			if($(this).text()!='Clear' && andor1_input!='Indicator' && andor1_input!=' Indicator' && andor1_input!=' Comparator')
		  		andor1_input = andor1_input + ' ' +$(obj).text();
		  });
		  if (andor1_input != '' && andor1_input!= 'Indicator Comparator Indicator' && andor1_input!='Indicator' && andor1_input!=' Indicator' && andor1_input!=' Comparator'){
			txt = txt + ' ' + andor1 + ' ' + andor1_input;
		  	}
		// });
	});
	txt = txt.replace(/\s+/g,' ').trim();
	if(txt!='' || txt !=' '){
		$('.entry p').html(txt);
	}
	if(cursor_loc==0){
		$('.entry p').html('When something interesting happens !');	
	}

	// exit summary
	exit_str = 'Sell 50 shares at a Stop Loss of 5% or Take Profit of 10%' // this servers as an template	
	exit_str = '';

	// at a';

	if($("#ip_position_qty").val())
		// exit_qty = $("#ip_position_type").val();
	{
		if ($("#ip_position_type").val()=='Sell')
			exit_str += 'Buy ';
		else
			exit_str += 'Sell ';

		exit_str += $("#ip_position_qty").val()+' shares'
	}

	exit_str += ' at ';

	if($("#ip_stop_loss").val()!='')
		exit_str += 'Stop loss of '+$('#ip_stop_loss').val()+'%';
	else
		exit_str += 'Stop loss';

	if($("#ip_take_profit").val()!='')
		exit_str += ' or Take profit of '+$('#ip_take_profit').val()+'%';
	else
		exit_str += ' or Take profit';


	// if($("#ip_position_qty").val())
	// 	// exit_qty = $("#ip_position_type").val();
	// {
	// 	exit_str += $("#ip_position_qty").val()+' shares'

	// 	exit_str += ' at a ';

	// 	if($("#ip_stop_loss").val()!='')
	// 		exit_str += 'Stop loss of '+$('#ip_stop_loss').val()+'%';
	// 	if($("#ip_take_profit").val()!='')
	// 		exit_str += ' or Take profit of '+$('#ip_take_profit').val()+'%';
	// }

	$(".exit p").html(exit_str);

	if(section_complete(['ip_strategy_name','ip_strategy_desc']) &&section_complete(['ip_position_type','ip_position_qty']) &&  section_complete(['ip_take_profit','ip_stop_loss']) && section_complete(['ip_position_type','ip_position_qty']) && cursor_loc/3>=1 && cursor_loc%3==0 && Object.keys(equity_added).length>0 && $('.indicator_popup').length<1){
		// $('.save_backtest').unbind('click');
		$('#algo_submit').html("<button class=\"save_backtest\" type=\"submit\" onclick=\"save_algorithm_new();ga('send', 'event', 'Submit Strategy', 'Button Clicked');\">Save & Run Backtest&nbsp;<img src=\"/static/imgs/icon-forward.png\"></button>");
		$($('.finish_section div span')[0]).css("background-color", "#029cff");
		$($('.finish_section div span')[0]).css("border-color", "#b1ddf9");
	}
	else{
		// save_backtest_disabled
		// $('.save_backtest').unbind('click');
		$('#algo_submit').html("<button class=\"save_backtest save_backtest_disabled\" type=\"submit\" onclick=\"show_snackbar(event,'Please complete all the fields');ga('send', 'event', 'Submit Strategy', 'Button Clicked');\">Save & Run Backtest&nbsp;<img src=\"/static/imgs/icon-forward.png\"></button>");
		$($('.finish_section div span')[0]).css("background-color", "#ADADAD");
		$($('.finish_section div span')[0]).css("border-color", "#F3F3F3");
	}
	if (cursor_loc/3<1){
		$($('.enter_strategy_section div span')[0]).css("background-color", "#ADADAD");
		$($('.enter_strategy_section div span')[0]).css("border-color", "#F3F3F3");
	}
};
function show_prompter_text(){
	if(cursor_loc%3==1){
		$('.prompter_text p').empty();
		$('.prompter_text').html("<p>Add a Comparator<span>(Hint)</span></p>");
		// $('.prompter_text').show();
	}
	else{
		$('.prompter_text p').empty();
		$('.prompter_text').html("Add an Indicator<span>(Hint)</span></p>");
		// $('.prompter_text').show();
	}
}
// function show_snackbar(e,msg){

// }
function and_or_select_change(e){
	footer_updater();
}
function drop_animation(e){
	var drop_location = $('.conditions');
    var drop_location_height = (drop_location.height())/3.5;
    var drop_location_width = (drop_location.width())/3.5;
    // var imgtodrag = $(this).parent('.item').find("img").eq(0);
    var imgtodrag = $(e.target).find('img');
    // var imgtodrag = $(this);
    if (imgtodrag) {
        var imgclone = imgtodrag.clone()
            .offset({
            top: imgtodrag.offset().top,
            left: imgtodrag.offset().left
        })
            .css({
            	'display' : 'block',
            	'opacity': '0.5',
                'position': 'absolute',
                'height': '75px',
                'width': '75px',
                'z-index': '100'
        })
            .appendTo($('body'))
            .animate({
            'top': drop_location.offset().top + drop_location_height,
                'left': drop_location.offset().left + drop_location_width,
                'width': 75,
                'height': 75
        }, 1000, 'easeInOutExpo');

        // setTimeout(function () {
        //     drop_location.effect("", {
        //         times: 2
        //     }, 200);
        // }, 1500);

        imgclone.animate({
            'width': 0,
                'height': 0
        }, function () {
            $(e.target).detach()
        });
    }
}
$(document).ready( function() {
	// $("#tooltip").hide();
	footer_updater();

	$('input').focusout(function(){
		footer_updater();
	});
	$('select').focusout(function(){
		footer_updater();
	});
	$('.done').on('click', function () {
        
    });

    $("#ip_position_type").focusout(function(){
    	v = $("#ip_position_type").val();
    	if(v==undefined||v==''){
    		$("#ip_position_type").addClass('empty_input_field');
    		show_snackbar(null,'Please select trade type.');
    	}else{
    		$("#ip_position_type").removeClass('empty_input_field');
    	}
    });
    $("#ip_position_qty").focusout(function(){
    	v = $("#ip_position_qty").val();
    	if(v==undefined||v==''){
    		$("#ip_position_qty").addClass('empty_input_field');
    		show_snackbar(null,'Please enter trade quantity.');
    	}else{
    		$("#ip_position_qty").removeClass('empty_input_field');
    	}
    });
    $("#ip_strategy_name").focusout(function(){
    	v = $("#ip_strategy_name").val();
    	if(v==undefined||v==''){
    		$("#ip_strategy_name").addClass('empty_input_field');
    		show_snackbar(null,'Please enter algorithm name.');
    	}else{
    		$("#ip_strategy_name").removeClass('empty_input_field');
    	}
    });
    $("#ip_strategy_desc").focusout(function(){
    	v = $("#ip_strategy_desc").val();
    	if(v==undefined||v==''){
    		$("#ip_strategy_desc").addClass('empty_input_field');
    		show_snackbar(null,'Please enter algorithm description.');
    	}else{
    		$("#ip_strategy_desc").removeClass('empty_input_field');
    	}
    });
    $("#ip_stop_loss").focusout(function(){
    	v = $("#ip_stop_loss").val();
    	if(v==undefined||v==''){
    		$("#ip_stop_loss").addClass('empty_input_field');
    		show_snackbar(null,'Please enter a stop loss');
    	}else{
    		$("#ip_stop_loss").removeClass('empty_input_field');
    	}
    });
    $("#ip_take_profit").focusout(function(){
    	v = $("#ip_take_profit").val();
    	if(v==undefined||v==''){
    		$("#ip_take_profit").addClass('empty_input_field');
    		show_snackbar(null,'Please enter a take profit');
    	}else{
    		$("#ip_take_profit").removeClass('empty_input_field');
    	}
    });
    $("#equities_input").focusout(function(){
    	show_inline_error_for_blank_equity();
    });
    function show_inline_error_for_blank_equity(){
    	if(Object.keys(equity_added).length==0){
    		$("#equities_input").addClass('empty_input_field');
    		show_snackbar(null,'Please select an instrument');
    	}else{
    		$("#equities_input").removeClass('empty_input_field');
    	}
    }

	$(".drag_tech_elements span").click(function(){
 		$(".indicator_popup").remove();
 		$("<div class='indicator_popup' id='indicator_popup'><div class='close_indicator_popup'><img src='/static/imgs/icon-deploy-close.png'></div><div class='indicator_popup_body'><p id='ti_name'>Middle Bollinger Band</p><div id='ti_populate'><div class='field'><p>Period</p><input type='number' name=''></div><div class='field'><p>Frequency</p><input type='number' name=''></div></div></div><div class='indicator_popup_buttons'><button type='submit' class='ti_cancel'>Cancel</button><button type='submit' class='done'>Done <img class='fly' src='/static/imgs/fly.png'></button></div></div>").insertAfter(this);
		$(".close_indicator_popup img, .ti_cancel, .done").click(function(){
    		$(".indicator_popup").remove();
  		});
	  	setTimeout(function(){
	  		if($(".left_main").find(".indicator_popup").length==1){
	  		$("body").click(function(e){
	        	var subject = $("#indicator_popup"); 
	        	if(e.target.id != subject.attr('id') && !subject.has(e.target).length)
       			{
	            	subject.remove();
	            	$("body").unbind("click");
	            	if(e.target.classList[0] == "ti"){
            		$(".indicator_popup").remove();
					$("<div class='indicator_popup' id='indicator_popup'><div class='close_indicator_popup'><img src='/static/imgs/icon-deploy-close.png'></div><div class='indicator_popup_body'><p id='ti_name'>Middle Bollinger Band</p><div id='ti_populate'><div class='field'><p>Period</p><input type='number' name=''></div><div class='field'><p>Frequency</p><input type='number' name=''></div></div></div><div class='indicator_popup_buttons'><button type='submit' class='ti_cancel'>Cancel</button><button type='submit' class='done'>Done <img class='fly' src='/static/imgs/fly.png'></button></div></div>").insertAfter(e.target);
					$(".close_indicator_popup img, .ti_cancel, .done").click(function(){
  						$(".indicator_popup").remove();
						});
            	}
        	}
    	});
  		}
	  	},100);
	});
	$("#search_ti").focusin(function(){
		$("#add_indicators_text").hide();
		$(".search_ti").css({"width" : "100%"});
	});
	$("#search_ti").focusout(function(){
		$("#add_indicators_text").fadeIn();
		$(".search_ti").css({"width" : "auto"});
	});
	$("#search_ti").keydown(function(){
		// TODO perform search and append in front of the queue the latest indicator
	});
	
	if(section_complete(['ip_position_type','ip_position_qty'])){
    		$($('.write_strategy_section div span')[0]).css("background-color", "#029cff");
			$($('.write_strategy_section div span')[0]).css("border-color", "#b1ddf9");
    	}
    	else{
			$($('.write_strategy_section div span')[0]).css("background-color", "#ADADAD");
			$($('.write_strategy_section div span')[0]).css("border-color", "#F3F3F3");
		}
	if(section_complete(['ip_strategy_name','ip_strategy_desc'])){
    		$($('.naming_strategy_section div span')[0]).css("background-color", "#029cff");
			$($('.naming_strategy_section div span')[0]).css("border-color", "#b1ddf9");
    	}
    	else{
			$($('.naming_strategy_section div span')[0]).css("background-color", "#ADADAD");
			$($('.naming_strategy_section div span')[0]).css("border-color", "#F3F3F3");
		}

	if(section_complete(['ip_take_profit','ip_stop_loss'])){
    		$($('.exit_strategy_section div span')[0]).css("background-color", "#029cff");
			$($('.exit_strategy_section div span')[0]).css("border-color", "#b1ddf9");
    	}
    	else{
			$($('.exit_strategy_section div span')[0]).css("background-color", "#ADADAD");
			$($('.exit_strategy_section div span')[0]).css("border-color", "#F3F3F3");
		}

	$("#ip_position_qty").on('focus change input',function(){
    // console.log('out');
    	if(section_complete(['ip_position_type','ip_position_qty'])){
    		$($('.write_strategy_section div span')[0]).css("background-color", "#029cff");
			$($('.write_strategy_section div span')[0]).css("border-color", "#b1ddf9");
			footer_updater();
    	}
    	else{
			$($('.write_strategy_section div span')[0]).css("background-color", "#ADADAD");
			$($('.write_strategy_section div span')[0]).css("border-color", "#F3F3F3");
		}
	});
	$("#ip_position_type").on('focus change input',function() {
    // console.log('out');
    	if(section_complete(['ip_position_type','ip_position_qty'])){
    		$($('.write_strategy_section div span')[0]).css("background-color", "#029cff");
			$($('.write_strategy_section div span')[0]).css("border-color", "#b1ddf9");
			footer_updater();
    	}
    	else{
			$($('.write_strategy_section div span')[0]).css("background-color", "#ADADAD");
			$($('.write_strategy_section div span')[0]).css("border-color", "#F3F3F3");
		}
	});
	
	$("#ip_strategy_name").on('focus change input',function(){
    // console.log('out');
    	if(section_complete(['ip_strategy_name','ip_strategy_desc'])){
    		$($('.naming_strategy_section div span')[0]).css("background-color", "#029cff");
			$($('.naming_strategy_section div span')[0]).css("border-color", "#b1ddf9");
			footer_updater();
    	}
    	else{
			$($('.naming_strategy_section div span')[0]).css("background-color", "#ADADAD");
			$($('.naming_strategy_section div span')[0]).css("border-color", "#F3F3F3");
		}
	});
	$("#ip_strategy_desc").on('focus change input',function() {
    // console.log('out');
    	if(section_complete(['ip_strategy_name','ip_strategy_desc'])){
    		$($('.naming_strategy_section div span')[0]).css("background-color", "#029cff");
			$($('.naming_strategy_section div span')[0]).css("border-color", "#b1ddf9");
			footer_updater();
    	}
    	else{
			$($('.naming_strategy_section div span')[0]).css("background-color", "#ADADAD");
			$($('.naming_strategy_section div span')[0]).css("border-color", "#F3F3F3");
		}
	});

	$("#ip_stop_loss").on('focus change input',function(){
    // console.log('out');
    	if(section_complete(['ip_take_profit','ip_stop_loss'])){
    		$($('.exit_strategy_section div span')[0]).css("background-color", "#029cff");
			$($('.exit_strategy_section div span')[0]).css("border-color", "#b1ddf9");
			footer_updater();
    	}
    	else{
			$($('.exit_strategy_section div span')[0]).css("background-color", "#ADADAD");
			$($('.exit_strategy_section div span')[0]).css("border-color", "#F3F3F3");
		}
	});
	$("#ip_take_profit").on('focus change input',function(){
    // console.log('out');
    	if(section_complete(['ip_take_profit','ip_stop_loss'])){
    		$($('.exit_strategy_section div span')[0]).css("background-color", "#029cff");
			$($('.exit_strategy_section div span')[0]).css("border-color", "#b1ddf9");
			footer_updater();
    	}
		else{
			$($('.exit_strategy_section div span')[0]).css("background-color", "#ADADAD");
			$($('.exit_strategy_section div span')[0]).css("border-color", "#F3F3F3");
		}
	});

	$("#equities_input").autocomplete({
	  source: function(request,response){
		params = {'query':request['term'].toLowerCase()}
		$.get('/autocomplete/', params,function(data) {
			// alert(data);
			if(data['status']=='success'){

				response($.map(data['results'], function (el) {
					 return {
						 label: el[0]+' '+el[3],
						 value: el[1]+' '+el[3] //assumption, symbols and segment name does not have space in between
					 };
				 }));
			}
		});
	  },
	  delay: 0,
	  minLength: 2,
	  change: function(event,ui)
		{
		if (ui.item==null)
			{
			$("#equities_input").val('');
			$("#equities_input").focus();
			}
	   $("#equities_input").val('');
	   $("#equities_input").focus();
	   // ui.item.value = "";
		},
	   select:function(event, ui){
	   	// console.log('selected');
	   	// console.log(ui['item'])
	   	val = ui.item.value.split(' ');
	   	if(equity_added[val[0]]==null)
	   	{
	   		// $('.added_equities').append('<span><span data-syms="'+val[0]+'_'+val[1]+'">'+ui.item.value+'</span><span><img src="/static/imgs/close.png"></span></span>');
	   		$('.added_equities').append('<span><span data-syms="'+val[0]+'_'+val[1]+'">'+ui.item.value+'</span><span><img src="/static/imgs/icon-strategy-remove_equity.png"></span></span>');
		   	// symbols.push(ui.item.value.split(' ').reverse());
		   	// ui.item.value = "";
		   	$(".added_equities img").click(function(){
				// $(this).parentsUntil('.added_equities').hide();
				x = $($($(this).parentsUntil('.added_equities')).find('span')[0]).data('syms');
				if(x!=null){
					[sym,seg] = x.split('_');
					delete equity_added[sym];
				}
				$(this).parentsUntil('.added_equities').remove();
				
				if(Object.keys(equity_added).length==0){
					$($('.adding_equities_section div span')[0]).css("background-color", "#ADADAD");
					$($('.adding_equities_section div span')[0]).css("border-color", "#F3F3F3");
				}
				footer_updater();
				show_inline_error_for_blank_equity();
			});
			
			equity_added[val[0]]=val[1];
			$($('.adding_equities_section div span')[0]).css("background-color", "#029cff");
			$($('.adding_equities_section div span')[0]).css("border-color", "#b1ddf9");
			footer_updater();
	    	show_inline_error_for_blank_equity();
	   	}
		$("#equities_input").val('');
	    $("#equities_input").focus();
	   	return false
	   }
	});

	$("#search_ti").autocomplete({
	  source: function(request,response){
		params = {'query':request['term'].toLowerCase()}
		$.get('/autocomplete_indicators/', params,function(data) {
			// alert(data);
			if(data['status']=='success'){

				response($.map(data['results'], function (el) {
					 return {
						 label: el.toUpperCase(),
						 value: el.toLowerCase()//assumption, symbols and segment name does not have space in between
					 };
				 }));
			}
		});
	  },
	  delay: 0,
	  minLength: 2,
	  change: function(event,ui)
		{
		if (ui.item==null)
			{
			$("#search_ti").val('');
			$("#search_ti").focus();
			}
	   $("#search_ti").val('');
	   $("#search_ti").focus();
	   // ui.item.value = "";
		},
	   select:function(event, ui){
	   	// console.log('selected');
	   	// console.log(ui['item'])
	   	val = ui.item.value;
	   	item = js_parsing_tree.main.indicator[val];
	   	if(lastest_item.length<1)
	  	{
	  		ev = {};
	   		ev['currentTarget']={'className':'ti ti_tags','classList':['ti','ti_tags'],'id':val};
	   		custom_click(ev);
			// update_pref(val);
	   	}
	   	else
	   	{
	 		// condition_div = $('.input_condition');
			// right_div = null;
			// right_span = null;
			// if(condition_div.length==parseInt(cursor_loc/3))

	   		latest_indicator = lastest_item[0]
	   		if(latest_indicator['allowed_comparision'].includes(item['function_group']) || (cursor_loc/3>=1 && cursor_loc%3==0))
		   	{
		   		ev = {};
		   		ev['currentTarget']={'className':'ti ti_tags','classList':['ti','ti_tags'],'id':val};
		   		custom_click(ev);
	   			// update_pref(val);
		   	}
		   	else{
		   		alert('Not applicable here');
		   	}
	   	}
		$("#search_ti").val('');
	    $("#search_ti").focus();
	   	return false
	   }
	});

	// $(".added_equities img").click(function(){
	// 	$(this).parentsUntil('.added_equities').hide();
	// });

	load_toolbar();

	$("#drag_tech_elements span, #drag_comp_elements span").mouseenter(function(e,d){
		var ele_id = e.target.id;
		try {
				if(drag_dict[ele_id]['content']!=undefined && drag_dict[ele_id]['content']!='')
				{
					$("#tooltip").show();
					$(".tt_content").find("p").html(drag_dict[ele_id]['content']);
					$(".tt_header").find("p").text(drag_dict[ele_id]['title']);
				}
				else{
					$("#tooltip").hide();
					$(".tt_content").find("p").html('');
					$(".tt_header").find("p").text('');
				}
		}
		catch(err) {
			// document.getElementById("demo").innerHTML = err.message;
			$("#tooltip").hide();
			$(".tt_content").find("p").html('');
			$(".tt_header").find("p").text('');
		}
	});
	$("#tooltip").mouseleave(function(){
		$("#tooltip").hide();
		$(".tt_content").find("p").html('');
		$(".tt_header").find("p").text('');
	});
	$(".right_main, .header").mouseenter(function(){
		$("#tooltip").hide();
		$(".tt_content").find("p").html('');
		$(".tt_header").find("p").text('');
	});
	
	$(".close_position_div").hide();
	// $("#create_title").click(function(){
	//	 $(this).parent().find("#create_algo").slideToggle(1000);
	// });
	// $("#exchanges_input").val('NSE');

	// $('.clear').on('click',function(e){
	// 	$(e.target.previousSibling).html("<span>Indicator</span><span>Comparator</span><span>Indicator</span>");
	// 	$(e.target.previousSibling).find('span').each(function(e,obj)
	// 		{
	// 			if($(obj).html()!='Indicator' && $(obj).html()!='Comparator'){
	// 				if($(obj).html().indexOf('range')!=-1)
	// 					cursor_loc -= 3;
	// 				else
	// 					cursor_loc -= 1;
	// 			}
	// 		});
	// 	});

	if(cursor_loc<0){
		cursor_loc = 0
	}
  	});


$.getJSON('/static/js_parsing_tree.json', function(data) {
		//data is the JSON string
	console.log("tree loaded");
	js_parsing_tree = data;
});

$(document).load(function () {
	
});

function update_state(){

}

var logical_operators_dict = {
  'OR':{
	'desc':''
  },
  'AND':{
	'desc':''
  }
}
function select_color(){
  // alert("Here");
  close_position();
  var eSelect = document.getElementById("buysell_select");
		// var optOtherReason = document.getElementById('otherdetail');
		// eSelect.onchange = function() {
			if(eSelect.selectedIndex === 1) {
				$("#buysell_select").css({"background-color" : "#d20e0e"});
			} else {
				 $("#buysell_select").css({"background-color" : "#00897b"});
			}
		// }
}
function clear_condition_first(e){
	// $(e.target.previousSibling.parentElement.parentElement.previousSibling).find('.another_condition').show();
	// $(e.target.previousSibling.parentElement.parentElement).remove();
	$(e.target.previousSibling).find('span').each(function(e,obj)
	{
		if($(obj).html()!='Indicator' && $(obj).html()!='Comparator'){
			if($(obj).html().indexOf('range')!=-1)
				cursor_loc -= 3;
			else
				cursor_loc -= 1;
		}
	});
	if(cursor_loc<0){
		cursor_loc = 0
	}
	// if($('.display_condition').length<1)
		// $('.another_condition').show();
	if($('.display_condition').length>1){
		prev_div = $('#display_condition1');
		all_displays = $('.display_condition');
		for(var i=1;i<all_displays.length;i++){
			prev_div.find('.input_condition').html($(all_displays[i]).find('.input_condition').html());
			prev_div = $(all_displays[i]);
		}
		
		if($('.display_condition').length==1)
			{
				$('.another_condition').show();
				$('.another_condition p').show();
			}
		// else if($('.display_condition').length==2)
		// 	$('.another_condition').show();
		else{
			// prev_div.find('.and_or').remove();
			prev_div.remove();
			if($('.display_condition').length==1)
				{$('.another_condition').show();
				$('.another_condition p').show();
				}
			else
				{
				$($('.display_condition').last()).find('.another_condition').show();
				$($('.display_condition').last()).find('.another_condition p').show();
				}	
			// prev_div.find('.another_condition').show();
		}
	}
	else{
		$(e.target.previousSibling).html("<span>Indicator</span><span>Comparator</span><span>Indicator</span>");
	}
	footer_updater();
	refresh_toolbar();
}
function clear_condition(e){
	// $(e.target.previousSibling).html("<span>Indicator</span><span>Comparator</span><span>Indicator</span>");
	console.log('clear addition click');
	$(e.target.previousSibling).find('span').each(function(e,obj)
	{
		if($(obj).html()!='Indicator' && $(obj).html()!='Comparator'){
			if($(obj).html().indexOf('range')!=-1)
				cursor_loc -= 3;
			else
				cursor_loc -= 1;
		}
	});

	if(cursor_loc/3>1)
		{	$(e.target.previousSibling.previousElementSibling.parentElement.parentElement.previousSibling).find('.another_condition').show();
			$(e.target.previousSibling.previousElementSibling.parentElement.parentElement).remove();
			if($('.display_condition').length==1)
				{$('.another_condition').show();
				$('.another_condition p').show();
				}
			else
				{
					$($('.display_condition').last()).find('.another_condition').show();
					$($('.display_condition').last()).find('.another_condition p').show();
				}
		}
	else if (cursor_loc/3==1)
		try
			{
			$(e.target.previousSibling.previousElementSibling.parentElement.parentElement).remove();
			// $('.another_condition').show()
			if($('.display_condition').length==1)
				{$('.another_condition').show();
				$('.another_condition p').show();
				}
			else
				{
					$($('.display_condition').last()).find('.another_condition').show();
					$($('.display_condition').last()).find('.another_condition p').show();
				}
			}
		catch(e){

		}
	else{
		
	}
	if(cursor_loc<0){
		cursor_loc = 0
	}
	footer_updater();
	refresh_toolbar();
}

function insert_condition2(){
  // $(".conditions").append("<div class='display_condition'><div class='and_or'><select id='andor'><option>and</option><option>or</option></select><span>&nbsp;&nbsp;Indicator&nbsp;&nbsp;</span><span>&nbsp;&nbsp;Comparator&nbsp;&nbsp;</span><span>&nbsp;&nbsp;Indicator&nbsp;&nbsp;</span></div><div class='another_condition'><p onclick='insert_condition2();$(this).hide();'>+ Add another condition</p></div></div>");
  // ga('send', 'event', 'Add condition', 'Take Position');
  $(".conditions").append("<div class='display_condition'><div class='and_or' onchange='and_or_select_change(event)'><select id='andor'><option>and</option><option>or</option></select><p class='input_condition'><span>Indicator</span><span>Comparator</span><span>Indicator</span></p><span class='clear clear_additional' onclick='clear_condition(event)'>Clear</span></div><div class='another_condition'><p onclick='insert_condition2();$(this).hide();'>+ Add another condition</p></div></div>");
  show_prompter_text()
}

function insert_condition(){
  // $(".conditions").append("<div class='display_condition'><div class='and_or'><select><option>and</option><option>or</option></select><input readonly type='text' name='' placeholder='Indicator &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Comparator &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Indicator' ondrop='drop(event);' ondragover='allowDrop(event);'></div><div class='another_condition'><p onclick='insert_condition();$(this).hide();'>+ Add another condition</p></div></div>");
  // $(".conditions").append("<div class='display_condition'><div class='and_or'><select><option>and</option><option>or</option></select><p class='input_condition'><span>Indicator</span><span>Comparator</span><span>Indicator</span></p></div><div class='another_condition'><p onclick='insert_condition();$(this).hide();'>+ Add another condition</p></div></div>");
  $(".conditions").append("<div class='display_condition'><div class='and_or'><select><option>and</option><option>or</option></select><p class='input_condition'><span>Indicator</span><span>Comparator</span><span>Indicator</span></p><span class='clear'>Clear</span></div><div class='another_condition'><p onclick='insert_condition();$(this).hide();'>+ Add another condition</p></div></div>");
  ga('send', 'event', 'Add condition', 'Take Position');
}
function insert_close_condition(){	
  $(".close_position_div").append("<div class='andordiv'><table><tr><th class='left_th'><p><select class='andor' id='andor1' name='andor'><option id='and' value=' AND '>and</option><option id='or' value=' OR '>or</option></select></p></th><th class='right_th'><span id='and'><p id='andor1_input' ondrop='drop(event);' ondragover='allowDrop(event);'></p></span></th></tr><tr><th></th><th><p id='close_condition_button' onclick='insert_close_condition();$(this).hide();'>Add another Condition</p></th><th></th></tr></table></div>");	 
  ga('send', 'event', 'Add condition', 'Close Position');
}   
function close_position() {   
  var close_exc = $('#exchanges_input').val();	
  var close_eq = $('#equities_input').val();	
  var close_qty = $('#qty_input').val();	
  var eSelect = document.getElementById("buysell_select");	
  var buysell = $('#buy').val().toString();   
  // alert(close_exc+close_eq+close_qty+eSelect.selectedIndex);   
  $('#close_exc').text(close_exc);	
  $('#close_eq').text(close_eq);	
  $('#close_qty').text(close_qty);	
  if(eSelect.selectedIndex === 0) {   
	$('#close_pos').text('Sell');   
	$("#buysell_sel").css({"background-color" : "#d20e0e"});	
	// $("#buysell_select").css({"background-color" : "#d20e0e"});	
			} else {	
	$('#close_pos').text('Buy');	
	$("#buysell_sel").css({"background-color" : "#00897b"});	
	// $("#buysell_select").css({"background-color" : "#00897b"});	
			}   
  // if(buysell == 'BUY'){	
  //   $('#close_pos').text('Sell');	
  //   $("#buysell_sel").css({"background-color" : "#d20e0e"});   
  // }	
  // else{	
  //   $('#close_pos').text('Buy');   
  //   $("#buysell_sel").css({"background-color" : "#00897b"});   
  // }	
}   
function close_position_toggle(){   
  var position = $("#close_position_toggle").text();	
  // alert(position);   
  if (position == 'Add a Close Position'){	
	$('.close_position_div').show();	
	close_position();   
	$("#close_position_toggle").text('Remove Close Position');	
	$("#close_position_toggle").css({"color" : "#D20E0E", "border" : "none", "text-decoration" : "underline", "margin-bottom" : "30px"});   
	ga('send', 'event', 'Add/Remove Close Position', 'Add');
  }   
  else{   
	$("#close_position_toggle").text('Add a Close Position');   
	$("#close_position_toggle").css({"color" : "orange", "border" : "1px solid orange", "text-decoration" : "none", "margin-bottom" : "0px"});
	$("#close_position_div").hide();  
	ga('send', 'event', 'Add/Remove Close Position', 'Remove');
  }   
}

function algo_input_valid(){
  return true;
}

function save_algorithm(){
  $(".loader_parent").fadeIn();
  if(parser_error_all()){
   $(".loader_parent").fadeOut();
	return;
  }
  // alert('In here');
  var action_name = $("#algo_name").val();
  var action_uuid = $("#action_id").val();
  var action_desc = $("#algo_description").val();
  var transaction_type = $("#buysell_select option:selected").val();
  var exchanges_input = $("#exchanges_input").val();
  var equities_input = $("#equities_input").val();
  var qty_input = $("#qty_input").val();
  var when_input = $("#when_input").val();
  var stop_loss = $("#stop_loss").val();
  var take_profit = $("#take_profit").val();

  var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();

  $("#when_input").find('span').each(function(e){ when_input = when_input + ' ' + $(this).text();
  });

  $(".andordiv").each(function(e){ 
	andor1 = $(this).find("#andor1 option:selected").val();
	// andor1_input = $(this).find("#andor1_input").val()

	// injecting hidden <p> which will be used later select and/or during page revisit
	$(this).find("#andor_save").each(function(e,obj){$(obj).remove();});

	$(this).append("<p id='andor_save' style='display:none'>"+andor1+"</p>");

	$(this).find("#andor1_input").each(function(e,obj){
	  andor1_input = '';
	  $(obj).find('span').each(function(e){ andor1_input = andor1_input + ' ' +$(this).text();
	  });
	  if (andor1_input != ''){
		when_input = when_input + ' ' + andor1 + ' ' + andor1_input;
	  }
	});
	
  });

  var create_segment = $(".right_main").html();

  if (algo_input_valid(action_name,
				action_desc,
				transaction_type,
				exchanges_input,
				equities_input,
				qty_input,
				exchanges_input,
				when_input
	)==true)
  {
  	if (action_name.length>50){
  		close_popup();
  		// $('.ti_msg_popup').show();
	// 	$('.ti_msg_popup> div').show(); 
	   //  // $('.ti_msg').html('Parse error !!!<br>'+msg);
	   //  $('.ti_msg').html('The name is too long. It needs to be under 50 characters.');
		$('#error_message').text('Algorithm Name is too long, max character limit 50.');
		$("#error_box").show();
	  	$(".body").css({"margin-top": "5px"});
	  	$(".loader_parent").fadeOut();
  		return;
  	}
  	else if(action_name.length<=0){
		$('#error_message').text('Enter an Algorithm name.');
		$("#error_box").show();
	  	$(".body").css({"margin-top": "5px"});
	  	$(".loader_parent").fadeOut();
  		return;
  	}
  	if (action_desc.length>200){
  		// close_popup();
  		$('#error_message').text('Description Name is too long, max character limit 50.');
		$("#error_box").show();
	  	$(".body").css({"margin-top": "5px"});
	  	$(".loader_parent").fadeOut();
  		return;
  	}
	// perform a post call to the view , passing the params
	params = {
	  'action_uuid':action_uuid,
	  'action_name':action_name,
	  'action_desc':action_desc,
	  'transaction_type' : transaction_type,
	  'exchange': exchanges_input,
	  'symbol':equities_input,
	  'qty':qty_input,
	  'when_text':when_input,
	  'stop_loss':stop_loss,
	  'take_profit':take_profit,
	  'create_segment_html':create_segment,
	  'csrfmiddlewaretoken':csrfmiddlewaretoken,
	};

	// $(".loader_parent").fadeOut();
	close_popup();
	
	$.post('/submit_algorithm/', params,function(data) {
		// alert(data);
		if(data['status']){
		  window.location = '/test';
		  }
		else{
		  if(data['msg']){
			// alert(data['error']);
	  //	   $('.ti_msg_popup').show();
			// $('.ti_msg_popup> div').show(); 
			// $('.ti_msg').html('Parse error !!!<br>'+msg);
			$('#error_message').text(data['msg']);
			for (var e in data['error'])
			{	
				$('#error_message').append('<br>');
				$('#error_message').append(data['error'][e]);
			}
	  		$("#error_box").show();
	  		$(".body").css({"margin-top": "5px"});
		  }
			window.scrollTo(0,0);

		}
		$(".loader_parent").fadeOut();
		});
  }
  else{
	close_popup();
	// alert('Input error');
	$(".loader_parent").fadeOut();

  }
}

function ti_popup_show4(data,ev,id,searched){
 		$(".indicator_popup").remove();

 		r = parseInt(Math.random()*100); // for being able to modify and remove individual elements

		condition_div = $('.display_condition');
		right_div = null;
		right_span = null;

		// if(cursor_loc==0){
		right_div = condition_div[parseInt(cursor_loc/3)];
		right_span = $(right_div).find("span")[cursor_loc%3];

		var ti_name = data['name'];
		$('.ti_popup').show();
		$('.ti_popup div').show();
		$('#ti_populate').empty();
		$('#ti_name').empty();
		$('#ti_name').html(ti_name);

		if (data['params'].length==0){
			$('.ti_popup div').fadeOut();
			$('.ti_popup').fadeOut();
			// $(".indicator_popup").remove();
			if(condition_div.length==parseInt(cursor_loc/3))
			{
				$('.another_condition').hide()
				insert_condition2();
				condition_div = $('.display_condition');
				right_div = condition_div[parseInt(cursor_loc/3)];
				right_span = $(right_div).find("span")[cursor_loc%3];
			}
			right_span.id = id+'__'+r;
			$(right_span).addClass(data['class']);
					// $(right_span).html('&nbsp;'+js_parsing_tree.main.comparator[data.id]['name']+'<img width=10px height=10px src="/static/imgs/close.png" onclick="remove_id(\''+data.id+'__'+r+'\')">');	
			$(right_span).html('&nbsp;'+data['syntax']);	
			$(right_span).attr('style',"color: #192024 !important; font-weight: 400 !important;");
			$(right_span).attr('data-params',id);

			if(data['function_group']=='Condition')
				cursor_loc += 3;
			else
				cursor_loc += 1;

			refresh_toolbar()
			if (cursor_loc/3>=1 && cursor_loc%3==0){
				$($('.enter_strategy_section div span')[0]).css("background-color", "#029cff");
				$($('.enter_strategy_section div span')[0]).css("border-color", "#b1ddf9");
				footer_updater();
			}
			lastest_item.shift();
			lastest_item.push(data);
		}
		else{
			// if(searched==true){
			// 	$('#drag_tech_elements').prepend("<div class='indicator_popup' id='indicator_popup'><div class='close_indicator_popup'><img src='/static/imgs/icon-deploy-close.png'></div><div class='indicator_popup_body'></div></div>");
			// }
			// else{
			// 	$("<div class='indicator_popup' id='indicator_popup'><div class='close_indicator_popup'><img src='/static/imgs/icon-deploy-close.png'></div><div class='indicator_popup_body'></div></div>").insertAfter(ev.target);
			// }
			// $('.indicator_popup_body').append("<p id='ti_name'>"+ti_name+"</p>");
			// $('.indicator_popup_body').append("<div id='ti_populate'></div>");

			for(var i=0;i<data['params'].length;i++){
				row = '<tr>';
				if(data['params'][i][0]=='offset')
					row += '<th style="text-transform:capitalize;">'+data['params'][i][3].replace('_',' ')+'</th>';
				else
					row += '<th style="text-transform:capitalize;">'+data['params'][i][0].replace('_',' ')+'</th>';
				if(data['params'][i][0]=='range_percentage')
					row += '<th><input id="'+data['params'][i][0]+r+'" type="number" name="" step="'+data['params'][i][4]+'" min="0" value='+ data['params'][i][1]+'></th>';
				else if(data['params'][i][0]=='interval')
					row += '<th><input list="intervals" id="'+data['params'][i][0]+r+'"type="text" name="myText" value="'+data['params'][i][1]+'"><datalist id="intervals"><option value="min"><option value="5min"><option value="15min"><option value="30min"><option value="hour"><option value="day"></datalist></th>' 
				else
					row += '<th><input id="' + data['params'][i][0]+r+'" type="number" name="" step="1" min="0" value='+ data['params'][i][1]+'></th>';

				row += '</tr>';
				$("#ti_populate").append(row);
			}
			$('.indicator_popup_body').append("<div class='indicator_popup_buttons'><button type='submit' class='ti_cancel'>Cancel</button><button type='submit' class='done'>Done <img class='fly' src='/static/imgs/fly.png'></button></div>");
			$('.done').unbind('click');
			if(searched==true)
				$('.done').click(function(event){ti_done2(data,r,ev,id);update_pref(data.name.toLowerCase());});
			else
				$('.done').click(function(event){ti_done2(data,r,ev,id);});

		}
		// $(".indicator_popup").remove();
 	// 	$("<div class='indicator_popup' id='indicator_popup'><div class='close_indicator_popup'><img src='/static/imgs/icon-deploy-close.png'></div><div class='indicator_popup_body'><p id='ti_name'>Middle Bollinger Band</p><div id='ti_populate'><div class='field'><p>Period</p><input type='number' name=''></div><div class='field'><p>Frequency</p><input type='number' name=''></div></div></div><div class='indicator_popup_buttons'><button type='submit' class='ti_cancel'>Cancel</button><button type='submit' class='done'>Done</button></div></div>").insertAfter(ev.target);
		$(".ti_cancel").click(function(){
    			// $(".indicator_popup").remove();
    			$('.ti_popup div').fadeOut();
				$('.ti_popup').fadeOut();
  		});
  		// setTimeout(function(){
	  	// 	if($(".left_main").find(".indicator_popup").length==1){
	  	// 	$("body").click(function(e){
	   //      	var subject = $("#indicator_popup"); 
	   //      	if(e.target.id != subject.attr('id') && !subject.has(e.target).length)
    //    			{
	            	
	   //          	$("body").unbind("click");
	   //          	if(e.target.classList[0] == "ti"){
    //         			$(".indicator_popup").remove();
    //         			custom_click(e);
				// 	// $("<div class='indicator_popup' id='indicator_popup'><div class='close_indicator_popup'><img src='/static/imgs/icon-deploy-close.png'></div><div class='indicator_popup_body'><p id='ti_name'>Middle Bollinger Band</p><div id='ti_populate'><div class='field'><p>Period</p><input type='number' name=''></div><div class='field'><p>Frequency</p><input type='number' name=''></div></div></div><div class='indicator_popup_buttons'><button type='submit' class='ti_cancel'>Cancel</button><button type='submit' class='done'>Done</button></div></div>").insertAfter(e.target);
				// 	// $(".close_indicator_popup img, .ti_cancel, .done").click(function(){
  		// 	// 			$(".indicator_popup").remove();
				// 	// 	});
    //         	}
    //         	else{
    //         		subject.remove();
    //         	}
    //     	}
    // 	});
  		// }
	  	// },100);
	  	// setTimeout(function(){
	  	// 	if($(".left_main").find(".indicator_popup").length==1){
	  	// 	$("body").click(function(e){
	   //      	var subject = $("#indicator_popup"); 
	   //      	if(e.target.id != subject.attr('id') && !subject.has(e.target).length)
    //    				{
	   //          	subject.remove();
	   //          	$("body").unbind("click");
	   //          	if(e.target.classList[0] == "ti"){
    //         		$(".indicator_popup").remove();
				// 	$("<div class='indicator_popup' id='indicator_popup'><div class='close_indicator_popup'><img src='/static/imgs/icon-deploy-close.png'></div><div class='indicator_popup_body'><p id='ti_name'>Middle Bollinger Band</p><div id='ti_populate'><div class='field'><p>Period</p><input type='number' name=''></div><div class='field'><p>Frequency</p><input type='number' name=''></div></div></div><div class='indicator_popup_buttons'><button type='submit' class='ti_cancel'>Cancel</button><button type='submit' class='done'>Done</button></div></div>").insertAfter(e.target);
				// 	$(".close_indicator_popup img, .ti_cancel, .done").click(function(){
  		// 				$(".indicator_popup").remove();
				// 		});
    //         		}
    //     		}
    // 		});
  		// }
	  	// },100);
}

function ti_popup_show3(data,ev,id,searched){
 		$(".indicator_popup").remove();

 		r = parseInt(Math.random()*100); // for being able to modify and remove individual elements

		condition_div = $('.display_condition');
		right_div = null;
		right_span = null;

		// if(cursor_loc==0){
		right_div = condition_div[parseInt(cursor_loc/3)];
		right_span = $(right_div).find("span")[cursor_loc%3];

		var ti_name = data['name'];

		if (data['params'].length==0){
			$('.ti_popup div').fadeOut();
			$('.ti_popup').fadeOut();
			$(".indicator_popup").remove();
			if(condition_div.length==parseInt(cursor_loc/3))
			{
				$('.another_condition').hide()
				insert_condition2();
				condition_div = $('.display_condition');
				right_div = condition_div[parseInt(cursor_loc/3)];
				right_span = $(right_div).find("span")[cursor_loc%3];
			}
			right_span.id = id+'__'+r;
			$(right_span).addClass(data['class']);
					// $(right_span).html('&nbsp;'+js_parsing_tree.main.comparator[data.id]['name']+'<img width=10px height=10px src="/static/imgs/close.png" onclick="remove_id(\''+data.id+'__'+r+'\')">');	
			$(right_span).html('&nbsp;'+data['syntax']);	
			$(right_span).attr('style',"color: #192024 !important; font-weight: 400 !important;");
			$(right_span).attr('data-params',id);

			if(data['function_group']=='Condition')
				cursor_loc += 3;
			else
				cursor_loc += 1;

			refresh_toolbar()
			if (cursor_loc/3>=1 && cursor_loc%3==0){
				$($('.enter_strategy_section div span')[0]).css("background-color", "#029cff");
				$($('.enter_strategy_section div span')[0]).css("border-color", "#b1ddf9");
				footer_updater();
			}
			lastest_item.shift();
			lastest_item.push(data);
		}
		else{
			if(searched==true){
				$('#drag_tech_elements').prepend("<div class='indicator_popup' id='indicator_popup'><div class='close_indicator_popup'><img src='/static/imgs/icon-deploy-close.png'></div><div class='indicator_popup_body'></div></div>");
			}
			else{
				$("<div class='indicator_popup' id='indicator_popup'><div class='close_indicator_popup'><img src='/static/imgs/icon-deploy-close.png'></div><div class='indicator_popup_body'></div></div>").insertAfter(ev.target);
			}
			$('.indicator_popup_body').append("<p id='ti_name'>"+ti_name+"</p>");
			$('.indicator_popup_body').append("<div id='ti_populate'></div>");

			for(var i=0;i<data['params'].length;i++){
				row = "<div class='field'>";

				if(data['params'][i][0]=='offset')
					row += "<p style=\"text-transform:capitalize;\">"+data['params'][i][3].replace('_',' ')+"</p>";
				else
					row += "<p style=\"text-transform:capitalize;\">"+data['params'][i][0].replace('_',' ')+"</p>";

				if(data['params'][i][0]=='range_percentage')
					row += '<input id="'+data['params'][i][0]+r+'" type="number" name="" step="'+data['params'][i][4]+'" min="0" value='+ data['params'][i][1]+'>';
				else if(data['params'][i][0]=='interval')
					row += '<input list="intervals" id="'+data['params'][i][0]+r+'"type="text" name="myText" value="'+data['params'][i][1]+'"><datalist id="intervals"><option value="min"><option value="5min"><option value="15min"><option value="30min"><option value="hour"><option value="day"></datalist>' 
				else
					row += '<input id="' + data['params'][i][0]+r+'" type="number" name="" step="1" min="0" value='+ data['params'][i][1]+'>';

				row += '</div>';
				$("#ti_populate").append(row);
			}
			$('.indicator_popup_body').append("<div class='indicator_popup_buttons'><button type='submit' class='ti_cancel'>Cancel</button><button type='submit' class='done'>Done <img class='fly' src='/static/imgs/fly.png'></button></div>");
			$('.done').unbind('click');
			if(searched==true)
				$('.done').click(function(event){drop_animation(event);ti_done2(data,r,ev,id);update_pref(data.name.toLowerCase());});
			else
				$('.done').click(function(event){drop_animation(event);ti_done2(data,r,ev,id);});

		}
		// $(".indicator_popup").remove();
 	// 	$("<div class='indicator_popup' id='indicator_popup'><div class='close_indicator_popup'><img src='/static/imgs/icon-deploy-close.png'></div><div class='indicator_popup_body'><p id='ti_name'>Middle Bollinger Band</p><div id='ti_populate'><div class='field'><p>Period</p><input type='number' name=''></div><div class='field'><p>Frequency</p><input type='number' name=''></div></div></div><div class='indicator_popup_buttons'><button type='submit' class='ti_cancel'>Cancel</button><button type='submit' class='done'>Done</button></div></div>").insertAfter(ev.target);
		$(".close_indicator_popup img, .ti_cancel, .done").click(function(){
    			$(".indicator_popup").remove();
  		});
  		setTimeout(function(){
	  		if($(".left_main").find(".indicator_popup").length==1){
	  		$("body").click(function(e){
	        	var subject = $("#indicator_popup"); 
	        	if(e.target.id != subject.attr('id') && !subject.has(e.target).length)
       			{
	            	
	            	$("body").unbind("click");
	            	if(e.target.classList[0] == "ti"){
            			$(".indicator_popup").remove();
            			custom_click(e);
					// $("<div class='indicator_popup' id='indicator_popup'><div class='close_indicator_popup'><img src='/static/imgs/icon-deploy-close.png'></div><div class='indicator_popup_body'><p id='ti_name'>Middle Bollinger Band</p><div id='ti_populate'><div class='field'><p>Period</p><input type='number' name=''></div><div class='field'><p>Frequency</p><input type='number' name=''></div></div></div><div class='indicator_popup_buttons'><button type='submit' class='ti_cancel'>Cancel</button><button type='submit' class='done'>Done</button></div></div>").insertAfter(e.target);
					// $(".close_indicator_popup img, .ti_cancel, .done").click(function(){
  			// 			$(".indicator_popup").remove();
					// 	});
            	}
            	else{
            		subject.remove();
            	}
        	}
    	});
  		}
	  	},100);
	  	// setTimeout(function(){
	  	// 	if($(".left_main").find(".indicator_popup").length==1){
	  	// 	$("body").click(function(e){
	   //      	var subject = $("#indicator_popup"); 
	   //      	if(e.target.id != subject.attr('id') && !subject.has(e.target).length)
    //    				{
	   //          	subject.remove();
	   //          	$("body").unbind("click");
	   //          	if(e.target.classList[0] == "ti"){
    //         		$(".indicator_popup").remove();
				// 	$("<div class='indicator_popup' id='indicator_popup'><div class='close_indicator_popup'><img src='/static/imgs/icon-deploy-close.png'></div><div class='indicator_popup_body'><p id='ti_name'>Middle Bollinger Band</p><div id='ti_populate'><div class='field'><p>Period</p><input type='number' name=''></div><div class='field'><p>Frequency</p><input type='number' name=''></div></div></div><div class='indicator_popup_buttons'><button type='submit' class='ti_cancel'>Cancel</button><button type='submit' class='done'>Done</button></div></div>").insertAfter(e.target);
				// 	$(".close_indicator_popup img, .ti_cancel, .done").click(function(){
  		// 				$(".indicator_popup").remove();
				// 		});
    //         		}
    //     		}
    // 		});
  		// }
	  	// },100);
}
function ti_popup_show2(data,ev,id){
	$('#ti_name').empty();
    $('#ti_name').html(data['name']);

	r = parseInt(Math.random()*100); // for being able to modify and remove individual elements

	condition_div = $('.display_condition');
	right_div = null;
	right_span = null;

	// if(cursor_loc==0){
	right_div = condition_div[parseInt(cursor_loc/3)];
	right_span = $(right_div).find("span")[cursor_loc%3];
	// }
	
	if (data['params'].length==0){
		$('.ti_popup div').fadeOut();
		$('.ti_popup').fadeOut();

		right_span.id = id+'__'+r;
		$(right_span).text(data['name']);
		$(right_span).addClass(data['class']);
		$(right_span).append('&nbsp;<img width=10px height=10px src="/static/imgs/close.png" onclick="remove_id(\''+id+'__'+r+'\')">');
		cursor_loc += 1;
	}
	else{
		$('.ti_popup').show();
		$('.ti_popup div').show();

		$("#ti_populate").find("tr").remove();
		for(var i=0;i<data['params'].length;i++){
			row = '<tr>';
			if(data['params'][i][0]=='offset')
				row += '<th style="text-transform:capitalize;">'+data['params'][i][3].replace('_',' ')+'</th>';
			else
				row += '<th style="text-transform:capitalize;">'+data['params'][i][0].replace('_',' ')+'</th>';
			if(data['params'][i][0]=='range_percentage')
				row += '<th><input id="'+data['params'][i][0]+r+'" type="number" name="" step="'+data['params'][i][4]+'" min="0" value='+ data['params'][i][1]+'></th>';
			else if(data['params'][i][0]=='interval')
				row += '<th><input list="intervals" id="'+data['params'][i][0]+r+'"type="text" name="myText" value="'+data['params'][i][1]+'"><datalist id="intervals"><option value="min"><option value="5min"><option value="15min"><option value="30min"><option value="hour"><option value="day"></datalist></th>' 
			else
				row += '<th><input id="' + data['params'][i][0]+r+'" type="number" name="" step="1" min="0" value='+ data['params'][i][1]+'></th>';

			row += '</tr>';
			$("#ti_populate").append(row);
		}
		$('.done').unbind('click');
		$('.done').click(function(){ti_done2(data,r,ev,id);});
	}
}
function ti_done2(data,r,ev,id){
	txt = '';

	syntax = data['syntax'];
	// syntax = syntax.split(' ');

	var default_value = false;
	params = [];
	// probably more effective approach is to loop though params of the item and replace them in syntax 
	for(var i=0;i<data['params'].length;i++){
		if(data['params'][i][0]=='offset'&&data['params'][i][1] == parseInt($('#'+data['params'][i][0]+r).val()))
		{
			syntax = syntax.replace('<offset> <interval> ago','');
			syntax = syntax.replace('<interval> back','');
			syntax = syntax.replace('back','');
		}
		else{
			replace_str = '<'+data['params'][i][0]+'>';
			var re = new RegExp(replace_str,"g");
			if($('#'+data['params'][i][0]+r).val()!=""){
				syntax = syntax.replace(re,$('#'+data['params'][i][0]+r).val());
				params.push($('#'+data['params'][i][0]+r).val());
				}
			else
				syntax = syntax.replace(re,data['params'][i][1]);
		}
	}
	txt = syntax;
	// txt trimming
	// if(txt.endsWith('with ')){
	// 	txt.replace('with ','');
	// }

	$('.ti_popup').hide();
	$('.ti_popup div').hide();
	$('#tim_name').empty();
	$('#ti_populate').find("tr").remove();

	if(txt!='' && txt!=' '){
		condition_div = $('.input_condition');
		right_div = null;
		right_span = null;

		if(condition_div.length==parseInt(cursor_loc/3))
		{
			$('.another_condition').hide()
			insert_condition2();
			condition_div = $('.display_condition');
		}
			// $(this).hide();

		right_div = condition_div[parseInt(cursor_loc/3)];
		right_span = $(right_div).find("span")[cursor_loc%3];
		
		$('.ti_popup div').fadeOut();
		$('.ti_popup').fadeOut();

		right_span.id = id+'__'+r;
		// $(right_span).text(data['name']);
		$(right_span).addClass(data['class']);
		$(right_span).html('&nbsp;'+txt);
		$(right_span).attr('style',"color: #192024 !important; font-weight: 400 !important;");
		$(right_span).attr('data-params',params.join());
		// $(right_span).html('&nbsp;'+txt+'<img width=10px height=10px src="/static/imgs/close.png" onclick="remove_id(\''+id+'__'+r+'\')">');
		
		// $($(right_span).find('span')).click(custom_click_inplace);
		// $(right_span).click(custom_click_inplace);
		$(right_span).attr('onclick', 'custom_click_inplace(event)');

		if(data['function_group']=='Condition')
			{
				$($(right_div).find("span")[cursor_loc%3+1]).remove();
				$($(right_div).find("span")[cursor_loc%3+1]).remove();
				cursor_loc += 3;
			}
		else
			{
				cursor_loc += 1;
			}

		lastest_item.shift();
		lastest_item.push(data);
		refresh_toolbar()
		if (cursor_loc/3>=1 && cursor_loc%3==0){
			$($('.enter_strategy_section div span')[0]).css("background-color", "#029cff");
			$($('.enter_strategy_section div span')[0]).css("border-color", "#b1ddf9");
			footer_updater();
		}
		if(cursor_loc==0 || cursor_loc%3!=0){
			show_prompter_text();	
		}else{
			$('.prompter_text').hide()
		}
	}
}

function ti_popup_show_inplace2(data,ev,id){

	$(".indicator_popup").remove();

	condition_div = $(ev.currentTarget);
	right_div = null;
	right_span = null;

	[key,r] = ev.currentTarget.id.split('__');

	// if(cursor_loc==0){
	right_div = $(ev.currentTarget);
	right_span = $(ev.currentTarget);
	// }
	
	var ti_name = data['name'];

	if (data['params'].length==0){
		$('.ti_popup div').fadeOut();
		$('.ti_popup').fadeOut();

		// right_span.id = id+'__'+r;
		$(right_span).text(data['name']);
		$(right_span).addClass(data['class']);
		$(right_span).append('&nbsp;<img width=10px height=10px src="/static/imgs/close.png" onclick="remove_id(\''+key+'__'+r+'\')">');
		cursor_loc += 1;
	}
	else{
		$("<div class='indicator_popup' id='indicator_popup'><div class='close_indicator_popup'><img src='/static/imgs/icon-deploy-close.png'></div><div class='indicator_popup_body'></div></div>").insertAfter(ev.target);
			$('.indicator_popup_body').append("<p id='ti_name'>"+ti_name+"</p>");
			$('.indicator_popup_body').append("<div id='ti_populate'></div>");

		$(".close_indicator_popup img, .ti_cancel, .done").click(function(){
    			$(".indicator_popup").remove();
  		});

		for(var i=0;i<data['params'].length;i++){
			row = "<div class='field'>";
			if(data['params'][i][0]=='offset')
				row += "<p style=\"text-transform:capitalize;\">"+data['params'][i][3].replace('_',' ')+"</p>";
			else
				row += "<p style=\"text-transform:capitalize;\">"+data['params'][i][0].replace('_',' ')+"</p>";
			if(data['params'][i][0]=='range_percentage')
				row += '<input id="'+data['params'][i][0]+r+'" type="number" name="" step="'+data['params'][i][4]+'" min="0" value='+ data['params'][i][1]+'>';
			else if(data['params'][i][0]=='interval')
				row += '<input list="intervals" id="'+data['params'][i][0]+r+'"type="text" name="myText" value="'+data['params'][i][1]+'"><datalist id="intervals"><option value="min"><option value="5min"><option value="15min"><option value="30min"><option value="hour"><option value="day"></datalist>'  
			else
				row += '<input id="' + data['params'][i][0]+r+'" type="number" name="" step="1" min="0" value='+ data['params'][i][1]+'>';

			row += '</div>';
			$("#ti_populate").append(row);
		}
		$('.indicator_popup_body').append("<div class='indicator_popup_buttons'><button type='submit' class='ti_cancel'>Cancel</button><button type='submit' class='done'>Done <img class='fly' src='/static/imgs/fly.png'></button></div>");
		$('.done').unbind('click');
		$('.done').click(function(event){drop_animation(event);ti_done_inplace3(data,ev,id);});
	}
}

function ti_popup_show_inplace(data,ev,id){
	$('#ti_name').empty();
    $('#ti_name').html(data['name']);

	condition_div = $(ev.currentTarget);
	right_div = null;
	right_span = null;

	[key,r] = ev.currentTarget.id.split('__');

	// if(cursor_loc==0){
	right_div = $(ev.currentTarget);
	right_span = $(ev.currentTarget);
	// }
	
	if (data['params'].length==0){
		$('.ti_popup div').fadeOut();
		$('.ti_popup').fadeOut();

		// right_span.id = id+'__'+r;
		$(right_span).text(data['name']);
		$(right_span).addClass(data['class']);
		$(right_span).append('&nbsp;<img width=10px height=10px src="/static/imgs/close.png" onclick="remove_id(\''+key+'__'+r+'\')">');
		cursor_loc += 1;
	}
	else{
		$('.ti_popup').show();
		$('.ti_popup div').show();

		$("#ti_populate").find("tr").remove();
		for(var i=0;i<data['params'].length;i++){
			row = '<tr>';
			if(data['params'][i][0]=='offset')
				row += '<th style="text-transform:capitalize;">'+data['params'][i][3].replace('_',' ')+'</th>';
			else
				row += '<th style="text-transform:capitalize;">'+data['params'][i][0].replace('_',' ')+'</th>';
			if(data['params'][i][0]=='range_percentage')
				row += '<th><input id="'+data['params'][i][0]+r+'" type="number" name="" step="'+data['params'][i][4]+'" min="0" value='+ data['params'][i][1]+'></th>';
			else if(data['params'][i][0]=='interval')
				row += '<th><input list="intervals" id="'+data['params'][i][0]+r+'"type="text" name="myText" value="'+data['params'][i][1]+'"><datalist id="intervals"><option value="min"><option value="5min"><option value="15min"><option value="30min"><option value="hour"><option value="day"></datalist></th>' 
			else
				row += '<th><input id="' + data['params'][i][0]+r+'" type="number" name="" step="1" min="0" value='+ data['params'][i][1]+'></th>';

			row += '</tr>';
			$("#ti_populate").append(row);
		}
		$('.done').unbind('click');
		$('.done').click(function(event){drop_animation(event);ti_done_inplace(data,ev,id);});
	}
}

function ti_done_inplace2(data,ev,id){
	txt = '';

	syntax = data['syntax'];
	// syntax = syntax.split(' ');
	[key,r] = ev.currentTarget.id.split('__');
	var default_value = false;
	var params = [];
	// probably more effective approach is to loop though params of the item and replace them in syntax 
	for(var i=0;i<data['params'].length;i++){
		if(data['params'][i][0]=='offset'&&data['params'][i][1] == parseInt($('#'+data['params'][i][0]+r).val()))
		{
			syntax = syntax.replace('<offset> <interval> ago','');
			syntax = syntax.replace('<interval> back','');
			syntax = syntax.replace('back','');
		}
		else{
			replace_str = '<'+data['params'][i][0]+'>';
			var re = new RegExp(replace_str,"g");
			if($('#'+data['params'][i][0]+r).val()!="")
			{
				syntax = syntax.replace(re,$('#'+data['params'][i][0]+r).val());
				params.push($('#'+data['params'][i][0]+r).val());
			}
			else
				syntax = syntax.replace(re,data['params'][i][1]);
		}
	}
	txt = syntax;
	// txt trimming
	// if(txt.endsWith('with ')){
	// 	txt.replace('with ','');
	// }

	$('.indicator_popup').remove();

	if(txt!='' && txt!=' '){
		condition_div = $(ev.currentTarget);
		right_div = null;
		right_span = $(ev.currentTarget);

		// if(condition_div.length==parseInt(cursor_loc/3))
		// {
		// 	$('.another_condition').hide()
		// 	insert_condition2();
		// 	condition_div = $('.display_condition');
		// }
			// $(this).hide();

		// right_div = condition_div[parseInt(cursor_loc/3)];
		// right_span = $(right_div).find("span")[cursor_loc%3];
		
		$('.ti_popup div').fadeOut();
		$('.ti_popup').fadeOut();

		// right_span.id = id+'__'+r;
		// $(right_span).text(data['name']);
		// $(right_span).addClass(data['class']);
		$(right_span).html('&nbsp;'+txt);
		$(right_span).attr('style',"color: #192024 !important; font-weight: 400 !important;");
		$(right_span).attr('data-params',params.join());
		
		// $(right_span).click(custom_click_inplace);
		$(right_span).attr('onclick', 'custom_click_inplace(event)');
		footer_updater();
	}
}

function ti_done_inplace3(data,ev,id){
	txt = '';

	syntax = data['syntax'];
	// syntax = syntax.split(' ');
	[key,r] = ev.target.id.split('__');
	var default_value = false;
	var params = [];
	// probably more effective approach is to loop though params of the item and replace them in syntax 
	for(var i=0;i<data['params'].length;i++){
		if(data['params'][i][0]=='offset'&&data['params'][i][1] == parseInt($('#'+data['params'][i][0]+r).val()))
		{
			syntax = syntax.replace('<offset> <interval> ago','');
			syntax = syntax.replace('<interval> back','');
			syntax = syntax.replace('back','');
		}
		else{
			replace_str = '<'+data['params'][i][0]+'>';
			var re = new RegExp(replace_str,"g");
			if($('#'+data['params'][i][0]+r).val()!="")
			{
				syntax = syntax.replace(re,$('#'+data['params'][i][0]+r).val());
				params.push($('#'+data['params'][i][0]+r).val());
			}
			else
				syntax = syntax.replace(re,data['params'][i][1]);
		}
	}
	txt = syntax;
	// txt trimming
	// if(txt.endsWith('with ')){
	// 	txt.replace('with ','');
	// }

	$('.indicator_popup').remove();

	if(txt!='' && txt!=' '){
		condition_div = $(ev.target);
		right_div = null;
		right_span = $(ev.target);

		// if(condition_div.length==parseInt(cursor_loc/3))
		// {
		// 	$('.another_condition').hide()
		// 	insert_condition2();
		// 	condition_div = $('.display_condition');
		// }
			// $(this).hide();

		// right_div = condition_div[parseInt(cursor_loc/3)];
		// right_span = $(right_div).find("span")[cursor_loc%3];
		
		$('.ti_popup div').fadeOut();
		$('.ti_popup').fadeOut();

		// right_span.id = id+'__'+r;
		// $(right_span).text(data['name']);
		// $(right_span).addClass(data['class']);
		$(right_span).html('&nbsp;'+txt);
		$(right_span).attr('style',"color: #192024 !important; font-weight: 400 !important;");
		$(right_span).attr('data-params',params.join());
		
		// $(right_span).click(custom_click_inplace);
		$(right_span).attr('onclick', 'custom_click_inplace(event)');
		footer_updater();
	}
}

function ti_done_inplace(data,ev,id){
	txt = '';

	syntax = data['syntax'];
	// syntax = syntax.split(' ');
	[key,r] = ev.currentTarget.id.split('__');
	var default_value = false;
	// probably more effective approach is to loop though params of the item and replace them in syntax 
	for(var i=0;i<data['params'].length;i++){
		if(data['params'][i][0]=='offset'&&data['params'][i][1] == parseInt($('#'+data['params'][i][0]+r).val()))
		{
			syntax = syntax.replace('<offset> <interval> ago','');
			syntax = syntax.replace('<interval> back','');
			syntax = syntax.replace('back','');
		}
		else{
			replace_str = '<'+data['params'][i][0]+'>';
			var re = new RegExp(replace_str,"g");
			if($('#'+data['params'][i][0]+r).val()!="")
				syntax = syntax.replace(re,$('#'+data['params'][i][0]+r).val());
			else
				syntax = syntax.replace(re,data['params'][i][1]);
		}
	}
	txt = syntax;
	// txt trimming
	// if(txt.endsWith('with ')){
	// 	txt.replace('with ','');
	// }

	$('.ti_popup').hide();
	$('.ti_popup div').hide();
	$('#tim_name').empty();
	$('#ti_populate').find("tr").remove();

	if(txt!='' && txt!=' '){
		condition_div = $(ev.currentTarget);
		right_div = null;
		right_span = $(ev.currentTarget);

		// if(condition_div.length==parseInt(cursor_loc/3))
		// {
		// 	$('.another_condition').hide()
		// 	insert_condition2();
		// 	condition_div = $('.display_condition');
		// }
			// $(this).hide();

		// right_div = condition_div[parseInt(cursor_loc/3)];
		// right_span = $(right_div).find("span")[cursor_loc%3];
		
		$('.ti_popup div').fadeOut();
		$('.ti_popup').fadeOut();

		// right_span.id = id+'__'+r;
		// $(right_span).text(data['name']);
		// $(right_span).addClass(data['class']);
		$(right_span).html('&nbsp;'+txt);
		
		// $(right_span).click(custom_click_inplace);
		$(right_span).attr('onclick', 'custom_click_inplace(event)');

		// if(data['function_group']=='Condition')
		// 	{
		// 		$($(right_div).find("span")[cursor_loc%3+1]).remove();
		// 		$($(right_div).find("span")[cursor_loc%3+1]).remove();
		// 		cursor_loc += 3;
		// 	}
		// else
		// 	{
		// 		cursor_loc += 1;
		// 	}

		// lastest_item.shift();
		// lastest_item.push(data);
		// refresh_toolbar()
		// if (cursor_loc/3>=1 && cursor_loc%3==0){
		// 	$($('.enter_strategy_section div span')[0]).css("background-color", "#029cff");
		// 	$($('.enter_strategy_section div span')[0]).css("border-color", "#b1ddf9");
		// 	footer_updater();
		// }
	}
}

function custom_click_inplace(ev){
	// TODO for editing varaible on click
	var ele_class = ev.currentTarget.className;
	var ele_class_list = ev.currentTarget.classList; // ['ti','ti_tags']
	var data = ev.currentTarget; // 'sma'
	var bool_ti = true;

	// if (ele_class_list.contains == null)
	// 	bool_ti = ele_class_list.includes('ti')
	// else
	// 	bool_ti = ele_class_list.contains('ti')

	if(bool_ti){
		// ti_popup_show_inplace2(js_parsing_tree.main.indicator[data.className],ev,data.id);
		// footer_updater();
	}
}

function save_algorithm_new(){
	$(".loader_parent").fadeIn();

	var error = 'Please complete all the sections, following things you have missed:<br>'

	var algo_name = $('#ip_strategy_name').val();
	var algo_desc = $('#ip_strategy_desc').val();
	var algo_uuid = $('#algo_uuid').val();
	var position_type = $('#ip_position_type').val();
	var position_qty = $('#ip_position_qty').val();

	if(algo_uuid==null)
		algo_uuid = ''
	// entry summary
	txt = '';
  	$("#display_condition1").find('span').each(function(e){ 
  		if($(this).text()!='Clear')
  			txt = txt + ' ' + $(this).text();
  	});
  	$(".and_or").each(function(e){ 
		andor1 = $(this).find("#andor option:selected").val();

		// injecting hidden <p> which will be used later select and/or during page revisit
		$(this).find("#andor_save").each(function(e,obj){$(obj).remove();});

		$(this).append("<p id='andor_save' style='display:none'>"+andor1+"</p>");
		  andor1_input = '';

		$(this).find("span").each(function(e,obj){
			if($(this).text()!='Clear')
		  		andor1_input = andor1_input + ' ' +$(obj).text();
		  });
		  if (andor1_input != ''){
			txt = txt + ' ' + andor1 + ' ' + andor1_input;
		  	}
		// });
	});
	txt = txt.replace(/\s+/g,' ').trim();

	var entry_logic = txt;

	// exit summary
	var exit_logic = '';

	var take_profit = $('#ip_take_profit').val();
	var stop_loss = $('#ip_stop_loss').val();

	var html_block = $(".right_main").html();

	var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();

	// validate input
	if(algo_name==''){
		error += 'Stratergy name<br>';
	}
	if(position_qty==''){
		error += 'Quantity<br>';
	}
	if(take_profit=='' || take_profit=='0'){
		error += 'Take profit<br>';
	}
	if(stop_loss=='' || stop_loss=='0'){
		error += 'Take profit<br>';
	}
	if(Object.keys(equity_added).length==0){
		error += 'Equities to run trade with<br>';	
	}

	if(error!='Please complete all the sections, following things you have missed:<br>'){

	}
	else{
		params={
			'algo_uuid':algo_uuid,//.hexEncode(),
			'algo_name':algo_name,//.hexEncode(),
			'algo_desc':algo_desc,//.hexEncode(),
			'position_type':position_type,
			'position_qty':position_qty,
			'equities':JSON.stringify(equity_added).hexEncode(), // SYM:SEG
			'entry_logic':entry_logic,//.hexEncode(),
			'exit_logic':exit_logic,//hexEncode(),
			'take_profit':take_profit,
			'stop_loss':stop_loss,
			'html_block':html_block,
			'csrfmiddlewaretoken':csrfmiddlewaretoken
		};
		$.post('/submit_algorithm/',params,function(data){
			if(data['status']){
				// window.location = '/test';
				var redirect = '/backtest/';
				delete params["html_block"];
				if(data['algo_uuid']!=undefined && data['algo_uuid']!='')
					params['algo_uuid']=data['algo_uuid'];
				$.redirectPost(redirect, params);
			}
			else{
				// handle any error from save algorithm
				show_snackbar(null,'Error while saving algorithm'+data['error']);
				// console.log('error saving algorithm!',data['error'])
				$(".loader_parent").fadeOut();
			}
		});
		close_popup();
		// $(".loader_parent").fadeOut();
	}
}

function refresh_toolbar(){
		pref_loader(pref_data);
}

function custom_click(ev){
	console.log('custom_click');
	var searched = false;
	if (ev.target == null)
		{
			ev.target = ev.currentTarget;
			searched = true;
		}
	var ele_class = ev.target.className;
	var ele_class_list = ev.target.classList; // ['ti','ti_tags']
	var data = ev.target; // 'sma'
	var bool_ti = false

	if (ele_class_list.contains == null)
		bool_ti = ele_class_list.includes('ti')
	else
		bool_ti = ele_class_list.contains('ti')

	if(bool_ti){
		ti_popup_show4(js_parsing_tree.main.indicator[data.id],ev,data.id,searched);
	}
	else{
		condition_div = $('.display_condition');
		right_div = null;
		right_span = null;

		r = parseInt(Math.random()*100);

		right_div = condition_div[parseInt(cursor_loc/3)];
		right_span = $(right_div).find("span")[cursor_loc%3];
		
		$('.ti_popup div').fadeOut();
		$('.ti_popup').fadeOut();

		r = parseInt(Math.random()*100);

		right_span.id = data.id+'__'+r;
		// $(right_span).text(data['name']);
		$(right_span).addClass(data['class']);
		// $(right_span).html('&nbsp;'+js_parsing_tree.main.comparator[data.id]['name']+'<img width=10px height=10px src="/static/imgs/close.png" onclick="remove_id(\''+data.id+'__'+r+'\')">');	
		$(right_span).html('&nbsp;'+js_parsing_tree.main.comparator[data.id]['syntax']);	
		$(right_span).attr('style',"color: #192024 !important; font-weight: 400 !important;");
		$(right_span).attr('data-params',data.id);

		if(data['function_group']=='Condition')
			cursor_loc += 3;
		else
			cursor_loc += 1;

		// lastest_item.shift();
		// lastest_item.push(js_parsing_tree.main.comparator[data.id]);
		refresh_toolbar();
		if(cursor_loc==0 || cursor_loc%3!=0){
			show_prompter_text();	
		}else{
			$('.prompter_text').hide()
		}
	}
	// if(condition_div.length==parseInt(cursor_loc/3))
	// 	{
	// 		$('.another_condition').hide()
	// 		insert_condition2();
	// 		condition_div = $('.display_condition');
	// 	}
}

$.extend(
{
    redirectPost: function(location, args)
    {
        var form = '';
        $.each( args, function( key, value ) {
            form += '<input type="hidden" name="'+key+'" value="'+value+'">';
        });
        form = $('<form action="'+location+'" method="POST">'+form+'</form>');
        $(document.body).append(form);
        form.submit();
    }
});

function remove_id(id){
  // $('#'+id).hide();
  // $("#"+id).remove();
  $("#"+id).empty();
  $("#"+id).html('&nbsp;&nbsp;Indicator&nbsp;&nbsp;');
  cursor_loc -= 1;
  if(cursor_loc<0){
		cursor_loc = 0
	}
  refresh_toolbar();
}
function replace_indicator(content, id, ele_class){
  var content = content;
  var id = id;
  var ele_class = ele_class;
  // alert("I'm here"+content+ele_class);
  if(ele_class.split(' ').includes('ti')){
	$("#drag_tech_elements").append("<span draggable='true' ondragstart='drag(event);' class='ti' id='"+id+"'> "+content+"</span>");
  }
  else{
	$("#drag_comp_elements").append("<span draggable='true' ondragstart='drag(event);' class='co' id='"+id+"'> "+content+"</span>");
  }
  
}
