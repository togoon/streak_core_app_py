var equity_added = {}

var url_selector = 1;
var bt_loading_time = 90;
var run_backtest_flag = true;

// var holding_type_latest = $("#ip_holding_type").val();//'CNC';

var backtest_result_response = {};

var backtest_multi = true;

var candle_freq_map = {'min':10,
                        '3min':9,
                        '5min':8,
                        '10min':7,
                        '15min':6,
                        '30min':5,
                        '45min':4,
                        'hour':3,
                        'day':2,
                        };
var freq_candle_map = {10:'min',
                        9:'3min',
                        8:'5min',
                        7:'10min',
                        6:'15min',
                        5:'30min',
                        4:'45min',
                        3:'hour',
                        2:'day',
                        };

// advnaced variables
var c_chart_type = 'Candlestick';
var c_trading_start_time = '00:00';
var c_trading_stop_time = '23:59';

// populating advanced fields
adv_holding_type = 'MIS';
adv_chart_type = "candlestick";
adv_trading_start_time = "09:00";
adv_trading_stop_time = "23:30";
adv_variety = "REGULAR";

var interval_mapping = {'1 Minute':"min",'3 Minutes':"3min",'5 Minutes':"5min",'10 Minutes':"10min",'15 Minutes':"15min",'30 Minutes':"30min",'1 Hour':"hour",'1 Day':"day"};
var chart_type_maping = {'Candlestick':"candlestick",'Heikin-Ashi':"heikinAshi"};
var holding_type_mapping = {'MIS':"MIS",'CNC/NRML':"CNC"};

var interval_mapping_rev = {"min":'1 Minute',"3min":'3 Minutes',"5min":'5 Minutes',"10min":'10 Minutes',"15min":'15 Minutes',"30min":'30 Minutes',"hour":'1 Hour',"day":'1 Day'};
var chart_type_maping_rev = {"candlestick":'Candlestick',"heikinAshi":'Heikin-Ashi'};
var holding_type_mapping_rev = {'MIS':"MIS","CNC":'CNC/NRML'};

$(window).load(function() {
    // Animate loader off screen
    $(".loader_parent").fadeOut();
});

function lmda_vs_ec2_select(){
	var interval = interval_mapping[$("#ip_interval").val()];
	// [from_datepicker,to_datepicker] = $('#date_range').val().split(' – ');
	[from_datepicker,to_datepicker] = [elements.start_input.value,elements.stop_input.value]
	var day_range = Math.abs(new moment(to_datepicker,'DD/MM/YYYY')-new moment(from_datepicker,'DD/MM/YYYY'))/(1000*3600*24);
	var equity_added_len = Object.keys(equity_added).length;

	if(interval=='min' && day_range>10 && equity_added_len>3)
		url_selector = 2;
	else if(interval=='3min' && day_range>52 && equity_added_len>3)
		url_selector = 2;
	else if(interval=='5min' && day_range>52 && equity_added_len>3)
		url_selector = 2;
	else if(interval=='10min' && day_range>52 && equity_added_len>3)
		url_selector = 2;
	else if(interval=='15min' && day_range>157 && equity_added_len>3)
		url_selector = 2;
	else if(interval=='30min' && day_range>314 && equity_added_len>3)
		url_selector = 2;
	else if(interval=='hour' && day_range>730 && equity_added_len>3)
		url_selector = 2;
	else if(interval=='day' && day_range>3650 && equity_added_len>3)
		url_selector = 2;
	else
		url_selector = 1;

	switch(interval){
		case 'min':
			bt_loading_time = 180;
			break;
		case '3min':
			bt_loading_time = 165;
			break;
		case '5min':
			bt_loading_time = 165;
			break;
		case '10min':
			bt_loading_time = 165;
			break;
		case '15min':
			bt_loading_time = 155;
			break;
		case '30min':
			bt_loading_time = 145;
			break;
		case 'hour':
			bt_loading_time = 105;
			break;
		case 'day':
			bt_loading_time = 100;
			break;
		default:
			bt_loading_time = 95;
	}
}
// $(window).scroll(function(){
// 		var margin = $(".test_headers").height();
// 		if($(window).scrollTop() > 70){
// 			$(".header").hide();
// 			$(".test_headers").css({"top" : "0px"},{"margin-top" : "0px"});
// 			$(".backtest_results").css({"margin-top" : "0px"});
// 			$(".test_headers").css({"box-shadow" : "0 2px 4px 0 rgba(0, 0, 0, 0.03)"});
// 		}
// 		else{
// 			$(".header").show();
// 			$(".test_headers").css({"top" : "70px"},{"margin-top" : "0px"});
// 			$(".backtest_results").css({"margin-top" : margin+"px"});
// 			$(".test_headers").css({"box-shadow" : "none"});
// 		}
// 	});
function chart_type_click(event){
  $("#ip_chart_type").attr('data-val-text','Renko('+$("#chart_type_renko").val()+')');
  $("#ip_chart_type").removeAttr('readonly');
  $("#ip_chart_type").val('Renko('+$("#chart_type_renko").val()+')');
  $("#ip_chart_type").attr('readonly',"");
  $("#ip_chart_type").attr('value','Renko('+$("#chart_type_renko").val()+')');
  adv_chart_type = 'Renko('+$("#chart_type_renko").val()+')';
  $(".indicator_popup").remove();
}
 $(document).ready(function(){

  // $('#ip_interval').on('change',function(){
  //     date_updater();
  // });
  	Chart.defaults.global.defaultFontColor = '#9ea1a4';
	Chart.defaults.global.defaultFontFamily = "'Roboto', sans-serif";
	Chart.defaults.global.defaultFontSize = 10;
	Chart.defaults.global.defaultFontStyle = 'normal';
    $("#from_datepicker").datepicker();
    $("#to_datepicker").datepicker();
    $(".charts").each(function(){$(this).hide()});
    $(".transactions_table").hide();
    $(".condition_not_met").hide();
    $(".low_capital").hide();
    // var margin = $(".test_headers").height();
    // $(".backtest_results").css({"margin-top" : margin+"px"});
    $(".added_equities img").click(function(){
		$(this).parentsUntil('.added_equities').hide();
	});
	disable_edit();
	$("#ip_live_period").change(function(){
        live_period_mapping = {'Intraday (MIS)':1,'Overnight (CNC/NRML)':30}
        if(live_period_mapping[$('#ip_live_period').val()]== 1){
            $("#mis_disclaimer_deploy").html("All Intraday (MIS) strategies will expire at 3:20 PM (currency futures at 4:30 PM)");
        }
        else{
            $("#mis_disclaimer_deploy").html("Note: All SL-M orders for CNC strategies is valid only for today till 3:15 PM and will not be placed on the consecutive day.");
            $("#ip_variety").val("REGULAR");
            $("#ip_variety").attr('readonly',"");
            $("#ip_variety").attr('value',"REGULAR");
        }
    });
    // $(".multiple_backtest_row_first>div:nth-child(1),.multiple_backtest_row_first>div:nth-child(2),.multiple_backtest_row_first>div:nth-child(3),.multiple_backtest_row_first>div:nth-child(4),.multiple_backtest_row_first>div:nth-child(5),.multiple_backtest_row_first>div:nth-child(6),.multiple_backtest_row_first>div:nth-child(7)").click(function(){
    // 	// alert($(this).parents(".multiple_backtest_row").find(".multiple_backtest_row_second").attr('class'));
    // 	$(this).parents(".multiple_backtest_row").find(".multiple_backtest_row_second").slideToggle();
    // });
   //   $('#ip_chart_type').on('change',function(){
   //  	adv_chart_type = $('#ip_chart_type').val();   
	  // });
	  // $('#ip_holding_type').on('change',function(){
	  //   adv_holding_type = $('#ip_holding_type').val();   
	  // });
	   $('#trading_start_time').on('change',function(){
	    adv_trading_start_time = $('#trading_start_time').val();   
	  });
	  $('#trading_stop_time').on('change',function(){
	    adv_trading_stop_time = $('#trading_stop_time').val();   
	  });

    $('#ip_interval').autocomplete({
      source: function(request,response){
        results = ['1 Minute','3 Minutes','5 Minutes','10 Minutes','15 Minutes','30 Minutes','1 Hour','1 Day'];

        x = $.map(results, function (el) {
        // console.log(el)
         return {
           label: el,//+'<p>'+el[1]+'</p>',
           value: el//assumption, symbols and segment name does not have space in between
            };
          });
        response(x);
      },
      delay: 0,
      minLength: 0,
      focus: function(event,ui){
            // if($(this).val()=='' && is_the_correct_input(this))
            //   cursor_loc +=1 ;
          },
      select:function(event, ui){
          if(candle_freq_map[interval_mapping[ui.item.value]]<min_candle_freq && !(min_candle_freq==10||min_candle_freq==1000)){
          
            ui.item.value = interval_mapping_rev[freq_candle_map[min_candle_freq+1]];
            show_snackbar(null,'Choose a smaller candle interval');
          }
          $(this).attr('data-val-text',ui.item.value);
          $(this).removeAttr('readonly');
          $(this).val(ui.item.value);
          $(this).attr('readonly',"");
          $(this).attr('value',ui.item.value);
          $(this).focusout();
          $(this).blur();

          // fetch_open_orders();
          // console.log(ui.item.value);
          date_updater();
        }
      }).focus(function() {
        $(this).autocomplete('search', '');
    });

  $('#ip_chart_type').autocomplete({
      source: function(request,response){
        try{
          if(subscription_status.subscription_plan=='free')
            results = ['Candlestick'];
          else if(subscription_status.subscription_plan=='ultimate')
            results = ['Candlestick','Heikin-Ashi','Renko'];
          else
            results = ['Candlestick','Heikin-Ashi'];
        }
        catch(e){
          results = ['Candlestick','Heikin-Ashi'];
        }

        x = $.map(results, function (el) {
        // console.log(el)
         return {
           label: el,//+'<p>'+el[1]+'</p>',
           value: el//assumption, symbols and segment name does not have space in between
            };
          });
        response(x);
      },
      delay: 0,
      minLength: 0,
      focus: function(event,ui){
            // if($(this).val()=='' && is_the_correct_input(this))
            //   cursor_loc +=1 ;
          },
      select:function(event, ui){
        if(ui.item.value=='Renko'){
          $("#ip_chart_type").after("<div class='indicator_popup' id='indicator_popup'><div class='close_indicator_popup'><img src='/static/imgs/new/close.svg'></div><div class='indicator_popup_body'><p id='popup_title_chart'>Renko chart</p><div class='field'><p style='text-transform:capitalize;'>Brick Size</p><input id='chart_type_renko' type='number' name='' step='1' min='0' value='1' onfocus=''></div><div class='indicator_popup_buttons'><button type='submit' class='done' onclick='chart_type_click(event)'>Done</button><button type='submit' class='ti_cancel'>Cancel</button></div></div></div></div>");

          $(".close_indicator_popup img, .ti_cancel, .done").click(function(){
            $(".indicator_popup").remove();
            adv_chart_type = 'Renko(1)';
            $("#ip_chart_type").attr('data-val-text','Renko(1)');
            $("#ip_chart_type").removeAttr('readonly');
            $("#ip_chart_type").val('Renko(1)');
            $("#ip_chart_type").attr('readonly',"");
            $("#ip_chart_type").attr('value','Renko(1)');
          });
        }
        else
        {
          $(this).attr('data-val-text',chart_type_maping[ui.item.value]);
          $(this).removeAttr('readonly');
          $(this).val(ui.item.value);
          $(this).attr('readonly',"");
          $(this).attr('value',ui.item.value);
          adv_chart_type = chart_type_maping[ui.item.value];
        }
          $(this).focusout();
          $(this).blur();

          // fetch_open_orders();
          // console.log(ui.item.value);
        }
      }).focus(function() {
        $(this).autocomplete('search', '');
  });

  $('#ip_holding_type').autocomplete({
      source: function(request,response){
        results = ['MIS','CNC/NRML'];
        x = $.map(results, function (el) {
        // console.log(el)
         return {
           label: el,//+'<p>'+el[1]+'</p>',
           value: el//assumption, symbols and segment name does not have space in between
            };
          });
        response(x);
      },
      delay: 0,
      minLength: 0,
      focus: function(event,ui){
            // if($(this).val()=='' && is_the_correct_input(this))
            //   cursor_loc +=1 ;
          },
      select:function(event, ui){
          $(this).attr('data-val-text',holding_type_mapping[ui.item.value]);
          $(this).removeAttr('readonly');
          $(this).val(ui.item.value);
          $(this).attr('readonly',"");
          $(this).attr('value',ui.item.value);
          adv_holding_type = holding_type_mapping[ui.item.value];
          $(this).focusout();
          $(this).blur();

          // fetch_open_orders();
          // console.log(ui.item.value);
        }
      }).focus(function() {
        $(this).autocomplete('search', '');
    });

    $('#ip_variety').autocomplete({
      source: function(request,response){
        results = ['REGULAR','BO'];
        live_period_mapping = {'Intraday (MIS)':1,'Overnight (CNC/NRML)':30}
        if((live_period_mapping[$('#ip_live_period').val()]!= 1)){
          results = ['REGULAR'];
          adv_variety = 'REGULAR';
        }
        x = $.map(results, function (el) {
        // console.log(el)
         return {
           label: el,//+'<p>'+el[1]+'</p>',
           value: el//assumption, symbols and segment name does not have space in between
            };
          });
        response(x);
      },
      delay: 0,
      minLength: 0,
      focus: function(event,ui){
            // if($(this).val()=='' && is_the_correct_input(this))
            //   cursor_loc +=1 ;
          },
      select:function(event, ui){
          $(this).attr('data-val-text',ui.item.value);
          $(this).removeAttr('readonly');
          $(this).val(ui.item.value);
          $(this).attr('readonly',"");
          $(this).attr('value',ui.item.value);
          adv_variety = ui.item.value;
          $(this).focusout();
          $(this).blur();

          // fetch_open_orders();
          // console.log(ui.item.value);
        }
      }).focus(function() {
        $(this).autocomplete('search', '');
    });

	  $('#ip_frequency').autocomplete({
      source: function(request,response){
        results = ['1','2','3','4','5'];
        x = $.map(results, function (el) {
        // console.log(el)
         return {
           label: el,//+'<p>'+el[1]+'</p>',
           value: el//assumption, symbols and segment name does not have space in between
            };
          });
        response(x);
      },
      delay: 0,
      minLength: 0,
      focus: function(event,ui){
            // if($(this).val()=='' && is_the_correct_input(this))
            //   cursor_loc +=1 ;
          },
      select:function(event, ui){
          $(this).attr('data-val-text',ui.item.value);
          $(this).removeAttr('readonly');
          $(this).val(ui.item.value);
          $(this).attr('readonly',"");
          $(this).attr('value',ui.item.value);
          $(this).focusout();
          $(this).blur();

          // fetch_open_orders();
          // console.log(ui.item.value);
        }
      }).focus(function() {
        $(this).autocomplete('search', '');
    });

    $('#ip_live_period').autocomplete({
      source: function(request,response){
        results = ['Notification Only','Paper trading','Auto trading'];
        x = $.map(results, function (el) {
        // console.log(el)
         return {
           label: el,//+'<p>'+el[1]+'</p>',
           value: el//assumption, symbols and segment name does not have space in between
            };
          });
        response(x);
      },
      delay: 0,
      minLength: 0,
      focus: function(event,ui){
            // if($(this).val()=='' && is_the_correct_input(this))
            //   cursor_loc +=1 ;
          },
      select:function(event, ui){
          $(this).attr('data-val-text',ui.item.value);
          $(this).removeAttr('readonly');
          $(this).val(ui.item.value);
          $(this).attr('readonly',"");
          $(this).attr('value',ui.item.value);
          $(this).focusout();
          $(this).blur();

          live_period_mapping = {'Intraday (MIS)':1,'Overnight (CNC/NRML)':30}
          if(live_period_mapping[$('#ip_live_period').val()]== 1){
              $("#mis_disclaimer_deploy").html("All Intraday (MIS) strategies will expire at 3:20 PM (currency futures at 4:30 PM)");
          }
          else{
              $("#mis_disclaimer_deploy").html("Note: All SL-M orders for CNC strategies is valid only for today till 3:15 PM and will not be placed on the consecutive day.");
              $("#ip_variety").val("REGULAR");
              $("#ip_variety").attr('readonly',"");
              $("#ip_variety").attr('value',"REGULAR");
          }
          // fetch_open_orders();
          // console.log(ui.item.value);
        }
      }).focus(function() {
        $(this).autocomplete('search', '');
    });

  });

function toggle_multi_backtest_row(event,k){
    	// alert($(this).parents(".multiple_backtest_row").find(".multiple_backtest_row_second").attr('class'));
    	if($(event.target).parents(".multiple_backtest_row").find(".multiple_backtest_row_second").data('toggle')==false)
    	{
    		$(event.target).parents(".multiple_backtest_row").find(".multiple_backtest_row_second").data('toggle',true);
    		$(event.target).parents(".multiple_backtest_row").find(".expand_row_detail img").attr('src',"/static/imgs/bt_up.svg");
    	}
    	else{
    		$(event.target).parents(".multiple_backtest_row").find(".multiple_backtest_row_second").data('toggle',false);
    		$(event.target).parents(".multiple_backtest_row").find(".expand_row_detail img").attr('src',"/static/imgs/bt_down.svg") 
    	}

    	$(event.target).parents(".multiple_backtest_row").find(".multiple_backtest_row_second").slideToggle();
    	// multiple_backtest_row_second
    	// $(event.target).parents(".multiple_backtest_row").find(".multiple_backtest_row_second")[0].is(':visible')
    	// $("#NSE_SBINpnl_chartContainer_new").is(':visible')
    	// setTimeout(function(){ 
    		load_backtest(k,$(event.target).parents(".multiple_backtest_row").find(".multiple_backtest_row_second").data('toggle'));
        // $('.force_stop_popup').removeClass('take_position_popup');
        // }, 1000);

}
function attach_toggle_multi_backtest_row(k){
	$(".multiple_backtest_row_first>div:nth-child(1),.multiple_backtest_row_first>div:nth-child(2),.multiple_backtest_row_first>div:nth-child(3),.multiple_backtest_row_first>div:nth-child(4),.multiple_backtest_row_first>div:nth-child(5),.multiple_backtest_row_first>div:nth-child(6),.multiple_backtest_row_first>div:nth-child(7)").attr('onclick',"toggle_multi_backtest_row(event,'"+k+"')");
}
function select_all(e, t) {
	var c = 0;
    if (t.is(':checked')) {
      // $(e).find('input').attr('disabled', true);
      // $($(t[0].parentElement.parentElement).find('div[class^="token__"]')[0]).find('.deploy_checkbox input')[0].checked = true
      $('.backtest_results_body').find(".deploy_checkbox").each(function(i,obj){
      	 if(!obj.disabled){
      	 	obj.checked = true	
      	 	c += 1;
      	 }
      });
    } else {
      // $(e).find('input').removeAttr('disabled');
      $('.backtest_results_body').find(".deploy_checkbox").each(function(i,obj){
      	 if(!obj.disabled){
      	 	obj.checked = false	
      	 }
      });
    }
    if(c>0){
      $('.deploy_holder .deploy').removeClass('deploy_disabled');
      $('.deploy_holder .deploy').removeAttr('data-tooltip-top');
      // $('.deploy_appear').slideDown();
    }else{
      $('.deploy_holder .deploy').addClass('deploy_disabled');
      $('.deploy_holder .deploy').attr('data-tooltip-top','Select strategies to deploy');
    	// $('.deploy_appear').slideUp();
    }
}

function select_any(e, t) {
    var deploy_instrument_list = []

    var deploy_instrument_list = [];
	$('.backtest_results_body').find(".deploy_checkbox").each(function(i,obj){
      	 if(!obj.disabled && obj.checked){
      	 	id = obj.id;
      	 	id = id.split('__')[1].split('_');
          if(id[0]=='MCX' && subscription_status.subscription_plan!=undefined &&subscription_status.subscription_plan!='ultimate'){
            show_snackbar(null,'MCX is only available in ultimate plan'); 
            obj.checked = false;
            return;
          }
      	 	deploy_instrument_list.push(id);	
      	 }
      });

	if(deploy_instrument_list.length>0){
		$('.deploy_holder .deploy').removeClass('deploy_disabled');
    $('.deploy_holder .deploy').removeAttr('data-tooltip-top');

    // $('.deploy_appear').slideDown();
  }else{
    $('.deploy_holder .deploy').addClass('deploy_disabled');
    $('.deploy_holder .deploy').attr('data-tooltip-top','Select strategies to deploy');
		// $('.deploy_appear').slideUp();
        $(".deploy_all_checkbox")[0].checked = false
	}

    if(deploy_instrument_list.length==$('.backtest_results_body').find(".deploy_checkbox").length-deployed_seg_sym.length){
        $(".deploy_all_checkbox")[0].checked = true
        // $('.deploy_appear').slideDown();
    }
    else{
        $(".deploy_all_checkbox")[0].checked = false
        // $('.deploy_appear').slideUp();
    }
}

 function date_updater_(){
 	  var interval = $('#ip_interval').val();
  		if(interval=='min'){
  			$("#date_range").remove()
  			$("#td_datepicker").html('<input type="" name="" id="date_range">');
			$("#date_range").daterangepicker({
		  		  timeZone: 'Asia/Kolkata',
		  		  dateLimit:moment(days=29),
  		  		  daterangepickerFormat: 'DD/MM/YYYY',
  		  		  expanded: true,
				  // minDate: moment().subtract(89, 'days'),
				  callback: function (startDate, endDate, period) {
				  	if(startDate<moment().subtract(29, 'days')){
						endDate = startDate.clone();
						endDate.add(29, 'd');
						// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.add(89, 'd').format('DD/MM/YYYY'));
					}
				  	
				  	if(endDate-startDate>(30-1)*24*3600000){
				  		show_snackbar(null,'Max date range limit for 1min candle is 1 month.');
				  	}
				    $(this).val(startDate.format('DD/MM/YYYY') + ' – ' + endDate.format('DD/MM/YYYY'));
				  }
				});
			$('#date_range').val(moment().subtract(29, 'days').format('DD/MM/YYYY')+' – '+moment().format('DD/MM/YYYY'));
  		}else if(interval=='3min'){
			$("#date_range").remove()
  			$("#td_datepicker").html('<input type="" name="" id="date_range">');
			$("#date_range").daterangepicker({
		  		  timeZone: 'Asia/Kolkata',
		  		  dateLimit:moment(days=89),
  		  		  daterangepickerFormat: 'DD/MM/YYYY',
  		  		  expanded: true,
				  // minDate: moment().subtract(89, 'days'),
				  callback: function (startDate, endDate, period) {
				  	if(startDate<moment().subtract(89, 'days')){
						endDate = startDate.clone();
						endDate.add(89, 'd');
						// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.add(89, 'd').format('DD/MM/YYYY'));
					}

				  	if(endDate-startDate>(90-1)*24*3600000){
				  		show_snackbar(null,'Max date range limit for 3min candle is 1 month.');
				  	}
				    $(this).val(startDate.format('DD/MM/YYYY') + ' – ' + endDate.format('DD/MM/YYYY'));
				  }
				});
			$('#date_range').val(moment().subtract(89, 'days').format('DD/MM/YYYY')+' – '+moment().format('DD/MM/YYYY'));
  		}else if(interval=='5min'){
			$("#date_range").remove()
  			$("#td_datepicker").html('<input type="" name="" id="date_range">');
			$("#date_range").daterangepicker({
		  		  timeZone: 'Asia/Kolkata',
		  		  dateLimit:moment(days=89),
  		  		  daterangepickerFormat: 'DD/MM/YYYY',
  		  		  expanded: true,
				  // minDate: moment().subtract(89, 'days'),
				  callback: function (startDate, endDate, period) {
				  	if(startDate<moment().subtract(89, 'days')){
						endDate = startDate.clone();
						endDate.add(89, 'd');
						// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.add(89, 'd').format('DD/MM/YYYY'));
					}

				  	if(endDate-startDate>(90-1)*24*3600000){
				  		show_snackbar(null,'Max date range limit for 1min candle is 1 month.');
				  	}
				    $(this).val(startDate.format('DD/MM/YYYY') + ' – ' + endDate.format('DD/MM/YYYY'));
				  }
				});
			$('#date_range').val(moment().subtract(89, 'days').format('DD/MM/YYYY')+' – '+moment().format('DD/MM/YYYY'));
  		}else if(interval=='10min'){
			$("#date_range").remove()
  			$("#td_datepicker").html('<input type="" name="" id="date_range">');
			$("#date_range").daterangepicker({
		  		  timeZone: 'Asia/Kolkata',
		  		  dateLimit:moment(days=89),
  		  		  daterangepickerFormat: 'DD/MM/YYYY',
  		  		  expanded: true,
				  // minDate: moment().subtract(89, 'days'),
				  callback: function (startDate, endDate, period) {
				  	if(startDate<moment().subtract(89, 'days')){
				  		endDate = startDate.clone();
						endDate.add(89, 'd');
						// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.add(89, 'd').format('DD/MM/YYYY'));
					}

				  	if(endDate-startDate>(90-1)*24*3600000){
				  		show_snackbar(null,'Max date range limit for 10min candle is 1 month.');
				  	}
				    $(this).val(startDate.format('DD/MM/YYYY') + ' – ' + endDate.format('DD/MM/YYYY'));
				  }
				});
			$('#date_range').val(moment().subtract(89, 'days').format('DD/MM/YYYY')+' – '+moment().format('DD/MM/YYYY'));
  		}else if(interval=='15min'){
			$("#date_range").remove()
  			$("#td_datepicker").html('<input type="" name="" id="date_range">');
			$("#date_range").daterangepicker({
		  		  timeZone: 'Asia/Kolkata',
		  		  dateLimit:moment(days=89),
  		  		  daterangepickerFormat: 'DD/MM/YYYY',
  		  		  expanded: true,
				  // minDate: moment().subtract(89, 'days'),
				  callback: function (startDate, endDate, period) {
				  	if(startDate<moment().subtract(89, 'days')){
				  		endDate = startDate.clone();
						endDate.add(89, 'd');
						// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.add(89, 'd').format('DD/MM/YYYY'));
					}

				  	if(endDate-startDate>(90-1)*24*3600000){
				  		show_snackbar(null,'Max date range limit for 15min candle is 1 month.');
				  	}
				    $(this).val(startDate.format('DD/MM/YYYY') + ' – ' + endDate.format('DD/MM/YYYY'));
				  }
				});
			$('#date_range').val(moment().subtract(89, 'days').format('DD/MM/YYYY')+' – '+moment().format('DD/MM/YYYY'));
  		}else if(interval=='30min'){
			$("#date_range").remove()
  			$("#td_datepicker").html('<input type="" name="" id="date_range">');
			$("#date_range").daterangepicker({
		  		  timeZone: 'Asia/Kolkata',
		  		  dateLimit:moment(days=89),
  		  		  daterangepickerFormat: 'DD/MM/YYYY',
  		  		  expanded: true,
				  // minDate: moment().subtract(89, 'days'),
				  callback: function (startDate, endDate, period) {
				  	if(startDate<moment().subtract(89, 'days')){
				  		endDate = startDate.clone();
						endDate.add(89, 'd');
						// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.add(89, 'd').format('DD/MM/YYYY'));
					}

				  	if(endDate-startDate>(89-1)*24*3600000){
				  		show_snackbar(null,'Max date range limit for 1min candle is 1 month.');
				  	}
				    $(this).val(startDate.format('DD/MM/YYYY') + ' – ' + endDate.format('DD/MM/YYYY'));
				  }
				});
			$('#date_range').val(moment().subtract(89, 'days').format('DD/MM/YYYY')+' – '+moment().format('DD/MM/YYYY'));
  		}else if(interval=='hour'){
  			$("#date_range").remove()
  			$("#td_datepicker").html('<input type="" name="" id="date_range">');
			$("#date_range").daterangepicker({
		  		  timeZone: 'Asia/Kolkata',
		  		  dateLimit:moment(days=364),
  		  		  daterangepickerFormat: 'DD/MM/YYYY',
  		  		  expanded: true,
				  // minDate: moment().subtract(364, 'days'),
				  callback: function (startDate, endDate, period) {
				  	if(startDate<moment().subtract(364, 'days')){
				  		endDate = startDate.clone();
						endDate.add(364, 'd');
						// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.add(364, 'd').format('DD/MM/YYYY'));
					}

				  	if(endDate-startDate>(365-1)*24*3600000){
				  		show_snackbar(null,'Max date range limit for hour candle is 1 year.');
				  	}
				    $(this).val(startDate.format('DD/MM/YYYY') + ' – ' + endDate.format('DD/MM/YYYY'));
				  }
				});
			$('#date_range').val(moment().subtract(364, 'days').format('DD/MM/YYYY')+' – '+moment().format('DD/MM/YYYY'));
  		}else if(interval=='day'){
  			$("#date_range").remove()
  			$("#td_datepicker").html('<input type="" name="" id="date_range">');
			$("#date_range").daterangepicker({
		  		  timeZone: 'Asia/Kolkata',
  		  		  daterangepickerFormat: 'DD/MM/YYYY',
  		  		  expanded: true,
		  		  dateLimit:moment(years=5),
				  // minDate: moment().subtract(5, 'years'),
				  callback: function (startDate, endDate, period) {
				  	if(startDate<moment().subtract(5, 'years')){
				  		endDate = startDate.clone();
						endDate.add(5, 'years');
						// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.subtract(5, 'years').format('DD/MM/YYYY'));
					}

				  	// if(endDate-startDate>(365*10-1)*24*3600000){
				  	// 	show_snackbar(null,'Max date range limit for day candle is 10 years.');
				  	// }
				    $(this).val(startDate.format('DD/MM/YYYY') + ' – ' + endDate.format('DD/MM/YYYY'));
				  }
				});
			$('#date_range').val(moment().subtract(5, 'years').format('DD/MM/YYYY')+' – '+moment().format('DD/MM/YYYY'));
  		}
 }

function date_updater(){
	var interval = interval_mapping[$("#ip_interval").val()];
		if(interval=='min'){
	
		start_calendar.set(moment().subtract(6, 'days').format('DD/MM/YYYY'));
		stop_calendar.set(moment().format('DD/MM/YYYY'));

		elements.start_input.value = moment().subtract(6, 'days').format('DD/MM/YYYY');
		elements.stop_input.value = moment().format('DD/MM/YYYY');

		}else if(interval=='3min'){
		
		start_calendar.set(moment().subtract(6, 'days').format('DD/MM/YYYY'));
		stop_calendar.set(moment().format('DD/MM/YYYY'));

		elements.start_input.value = moment().subtract(6, 'days').format('DD/MM/YYYY');
		elements.stop_input.value = moment().format('DD/MM/YYYY');

		}else if(interval=='5min'){
		
		start_calendar.set(moment().subtract(6, 'days').format('DD/MM/YYYY'));
		stop_calendar.set(moment().format('DD/MM/YYYY'));

		elements.start_input.value = moment().subtract(6, 'days').format('DD/MM/YYYY');
		elements.stop_input.value = moment().format('DD/MM/YYYY');

		}else if(interval=='10min'){
		
		start_calendar.set(moment().subtract(6, 'days').format('DD/MM/YYYY'));
		stop_calendar.set(moment().format('DD/MM/YYYY'));

		elements.start_input.value = moment().subtract(6, 'days').format('DD/MM/YYYY');
		elements.stop_input.value = moment().format('DD/MM/YYYY');

		}else if(interval=='15min'){
		
		start_calendar.set(moment().subtract(6, 'days').format('DD/MM/YYYY'));
		stop_calendar.set(moment().format('DD/MM/YYYY'));

		elements.start_input.value = moment().subtract(6, 'days').format('DD/MM/YYYY');
		elements.stop_input.value = moment().format('DD/MM/YYYY');

		}else if(interval=='30min'){
		
		start_calendar.set(moment().subtract(6, 'days').format('DD/MM/YYYY'));
		stop_calendar.set(moment().format('DD/MM/YYYY'));

		elements.start_input.value = moment().subtract(6, 'days').format('DD/MM/YYYY');
		elements.stop_input.value = moment().format('DD/MM/YYYY');

		}else if(interval=='hour'){
	
		start_calendar.set(moment().subtract(364, 'days').format('DD/MM/YYYY'));
		stop_calendar.set(moment().format('DD/MM/YYYY'));

		elements.start_input.value = moment().subtract(364, 'days').format('DD/MM/YYYY');
		elements.stop_input.value = moment().format('DD/MM/YYYY');

		}else if(interval=='day'){
	
		start_calendar.set(moment().subtract(5, 'years').format('DD/MM/YYYY'));
		stop_calendar.set(moment().format('DD/MM/YYYY'));

		elements.start_input.value = moment().subtract(5, 'years').format('DD/MM/YYYY');
		elements.stop_input.value = moment().format('DD/MM/YYYY');

		}
}

function date_updated_start(date){
	var interval = interval_mapping[$("#ip_interval").val()];
		if(interval=='min'){
	
			if(Math.abs(moment(elements.stop_input.value,'DD/MM/YYYY')-moment(date,'DD/MM/YYYY'))>(7-1)*24*3600000 || moment(date,'DD/MM/YYYY')>moment(elements.stop_input.value,'DD/MM/YYYY')){
				stop_calendar.set(moment(date,'DD/MM/YYYY').add(6, 'days').format('DD/MM/YYYY'));
				elements.stop_input.value = moment(date,'DD/MM/YYYY').add(6, 'days').format('DD/MM/YYYY');
				// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.subtract(5, 'years').format('DD/MM/YYYY'));
			}

		}else if(interval=='3min'){
		
			if(Math.abs(moment(elements.stop_input.value,'DD/MM/YYYY'))-moment(date,'DD/MM/YYYY')>(7-1)*24*3600000 || moment(date,'DD/MM/YYYY')>moment(elements.stop_input.value,'DD/MM/YYYY')){
				stop_calendar.set(moment(date,'DD/MM/YYYY').add(6, 'days').format('DD/MM/YYYY'));
				elements.stop_input.value = moment(date,'DD/MM/YYYY').add(6, 'days').format('DD/MM/YYYY');
				// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.subtract(5, 'years').format('DD/MM/YYYY'));
			}

		}else if(interval=='5min'){
		
			if(Math.abs(moment(elements.stop_input.value,'DD/MM/YYYY')-moment(date,'DD/MM/YYYY'))>(7-1)*24*3600000 || moment(date,'DD/MM/YYYY')>moment(elements.stop_input.value,'DD/MM/YYYY')){
				stop_calendar.set(moment(date,'DD/MM/YYYY').add(6, 'days').format('DD/MM/YYYY'));
				elements.stop_input.value = moment(date,'DD/MM/YYYY').add(6, 'days').format('DD/MM/YYYY');
				// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.subtract(5, 'years').format('DD/MM/YYYY'));
			}

		}else if(interval=='10min'){
		
			if(Math.abs(moment(elements.stop_input.value,'DD/MM/YYYY')-moment(date,'DD/MM/YYYY'))>(7-1)*24*3600000 || moment(date,'DD/MM/YYYY')>moment(elements.stop_input.value,'DD/MM/YYYY')){
				stop_calendar.set(moment(date,'DD/MM/YYYY').add(6, 'days').format('DD/MM/YYYY'));
				elements.stop_input.value = moment(date,'DD/MM/YYYY').add(6, 'days').format('DD/MM/YYYY');
				// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.subtract(5, 'years').format('DD/MM/YYYY'));
			}

		}else if(interval=='15min'){
		
			if(Math.abs(moment(elements.stop_input.value,'DD/MM/YYYY')-moment(date,'DD/MM/YYYY'))>(7-1)*24*3600000 || moment(date,'DD/MM/YYYY')>moment(elements.stop_input.value,'DD/MM/YYYY')){
				stop_calendar.set(moment(date,'DD/MM/YYYY').add(6, 'days').format('DD/MM/YYYY'));
				elements.stop_input.value = moment(date,'DD/MM/YYYY').add(6, 'days').format('DD/MM/YYYY');
				// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.subtract(5, 'years').format('DD/MM/YYYY'));
			}

		}else if(interval=='30min'){
		
			if(Math.abs(moment(elements.stop_input.value,'DD/MM/YYYY')-moment(date,'DD/MM/YYYY'))>(7-1)*24*3600000 || moment(date,'DD/MM/YYYY')>moment(elements.stop_input.value,'DD/MM/YYYY')){
				stop_calendar.set(moment(date,'DD/MM/YYYY').add(6, 'days').format('DD/MM/YYYY'));
				elements.stop_input.value = moment(date,'DD/MM/YYYY').add(6, 'days').format('DD/MM/YYYY');
				// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.subtract(5, 'years').format('DD/MM/YYYY'));
			}

		}else if(interval=='hour'){
	
			if(Math.abs(moment(elements.stop_input.value,'DD/MM/YYYY')-moment(date,'DD/MM/YYYY'))>(365-1)*24*3600000 || moment(date,'DD/MM/YYYY')>moment(elements.stop_input.value,'DD/MM/YYYY')){
				stop_calendar.set(moment(date,'DD/MM/YYYY').add(364, 'days').format('DD/MM/YYYY'));
				elements.stop_input.value = moment(date,'DD/MM/YYYY').add(364, 'days').format('DD/MM/YYYY');
				// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.subtract(5, 'years').format('DD/MM/YYYY'));
			}

		}else if(interval=='day'){
	
			if(Math.abs(moment(elements.stop_input.value,'DD/MM/YYYY')-moment(date,'DD/MM/YYYY'))>365*5*24*3600000 || moment(date,'DD/MM/YYYY')>moment(elements.stop_input.value,'DD/MM/YYYY')){
				stop_calendar.set(moment(date,'DD/MM/YYYY').add(5, 'years').format('DD/MM/YYYY'));
				elements.stop_input.value = moment(date,'DD/MM/YYYY').add(5, 'years').format('DD/MM/YYYY');
				// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.subtract(5, 'years').format('DD/MM/YYYY'));
			}

		}
}

function date_updated_stop(date){
	var interval = interval_mapping[$("#ip_interval").val()];
		if(interval=='min'){
	
			if(Math.abs(moment(date,'DD/MM/YYYY')-moment(elements.start_input.value,'DD/MM/YYYY'))>(7-1)*24*3600000 || moment(date,'DD/MM/YYYY')<moment(elements.start_input.value,'DD/MM/YYYY')){
				start_calendar.set(moment(date,'DD/MM/YYYY').subtract(6, 'days').format('DD/MM/YYYY'));
				elements.start_input.value = moment(date,'DD/MM/YYYY').subtract(29, 'days').format('DD/MM/YYYY');
				// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.subtract(5, 'years').format('DD/MM/YYYY'));
			}

		}else if(interval=='3min'){
		
			if(Math.abs(moment(date,'DD/MM/YYYY')-moment(elements.start_input.value,'DD/MM/YYYY'))>(7-1)*24*3600000 || moment(date,'DD/MM/YYYY')<moment(elements.start_input.value,'DD/MM/YYYY')){
				start_calendar.set(moment(date,'DD/MM/YYYY').subtract(6, 'days').format('DD/MM/YYYY'));
				elements.start_input.value = moment(date,'DD/MM/YYYY').subtract(89, 'days').format('DD/MM/YYYY');
				// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.subtract(5, 'years').format('DD/MM/YYYY'));
			}

		}else if(interval=='5min'){
		
			if(Math.abs(moment(date,'DD/MM/YYYY')-moment(elements.start_input.value,'DD/MM/YYYY'))>(7-1)*24*3600000 || moment(date,'DD/MM/YYYY')<moment(elements.start_input.value,'DD/MM/YYYY')){
				start_calendar.set(moment(date,'DD/MM/YYYY').subtract(6, 'days').format('DD/MM/YYYY'));
				elements.start_input.value = moment(date,'DD/MM/YYYY').subtract(89, 'days').format('DD/MM/YYYY');
				// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.subtract(5, 'years').format('DD/MM/YYYY'));
			}

		}else if(interval=='10min'){
		
			if(Math.abs(moment(date,'DD/MM/YYYY')-moment(elements.start_input.value,'DD/MM/YYYY'))>(7-1)*24*3600000 || moment(date,'DD/MM/YYYY')<moment(elements.start_input.value,'DD/MM/YYYY')){
				start_calendar.set(moment(date,'DD/MM/YYYY').subtract(6, 'days').format('DD/MM/YYYY'));
				elements.start_input.value = moment(date,'DD/MM/YYYY').subtract(89, 'days').format('DD/MM/YYYY');
				// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.subtract(5, 'years').format('DD/MM/YYYY'));
			}

		}else if(interval=='15min'){
		
			if(Math.abs(moment(date,'DD/MM/YYYY')-moment(elements.start_input.value,'DD/MM/YYYY'))>(7-1)*24*3600000 || moment(date,'DD/MM/YYYY')<moment(elements.start_input.value,'DD/MM/YYYY')){
				start_calendar.set(moment(date,'DD/MM/YYYY').subtract(6, 'days').format('DD/MM/YYYY'));
				elements.start_input.value = moment(date,'DD/MM/YYYY').subtract(89, 'days').format('DD/MM/YYYY');
				// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.subtract(5, 'years').format('DD/MM/YYYY'));
			}

		}else if(interval=='30min'){
		
			if(Math.abs(moment(date,'DD/MM/YYYY')-moment(elements.start_input.value,'DD/MM/YYYY'))>(7-1)*24*3600000 || moment(date,'DD/MM/YYYY')<moment(elements.start_input.value,'DD/MM/YYYY')){
				start_calendar.set(moment(date,'DD/MM/YYYY').subtract(6, 'days').format('DD/MM/YYYY'));
				elements.start_input.value = moment(date,'DD/MM/YYYY').subtract(89, 'days').format('DD/MM/YYYY');
				// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.subtract(5, 'years').format('DD/MM/YYYY'));
			}

		}else if(interval=='hour'){
	
			if(Math.abs(moment(date,'DD/MM/YYYY')-moment(elements.start_input.value,'DD/MM/YYYY'))>(365-1)*24*3600000 || moment(date,'DD/MM/YYYY')<moment(elements.start_input.value,'DD/MM/YYYY')){
				start_calendar.set(moment(date,'DD/MM/YYYY').subtract(364, 'days').format('DD/MM/YYYY'));
				elements.start_input.value = moment(date,'DD/MM/YYYY').subtract(364, 'days').format('DD/MM/YYYY');
				// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.subtract(5, 'years').format('DD/MM/YYYY'));
			}

		}else if(interval=='day'){
	
			if(Math.abs(moment(date,'DD/MM/YYYY')-moment(elements.start_input.value,'DD/MM/YYYY'))>365*5*24*3600000 || moment(date,'DD/MM/YYYY')<moment(elements.start_input.value,'DD/MM/YYYY')){
				start_calendar.set(moment(date,'DD/MM/YYYY').subtract(5, 'years').format('DD/MM/YYYY'));
				elements.start_input.value = moment(date,'DD/MM/YYYY').subtract(5, 'years').format('DD/MM/YYYY');
				// $(this).val(startDate.format('DD/MM/YYYY')+' – '+startDate.subtract(5, 'years').format('DD/MM/YYYY'));
			}

		}
}
// function load_basket(basket_name){
//  	if(Object.keys(equity_added).length>=20)
//    	{
//    		show_snackbar(null,'Cannot add more than 5 instruments');
//    		return false;
//    	}

//  	params_admin = {
//             'basket_name':basket_name
//             };
//     var settings = {
//       "async": true,
//       "crossDomain": true,
//       "url": '/user_baskets/',
//       "method": "GET",
//       "headers": {
//       },
//       "data":params_admin,
//       "timeout": 10000,//40 sec timeout
//     }
    
//     $.ajax(settings).done(function (data){
// 		if(data['status']=="success"){
// 			var val = null;
// 			data['basket_instruments'] = JSON.parse(data['basket_instruments']);
// 			for(var i=0;i<data['basket_instruments'].length;i++){
// 				val = data['basket_instruments'][i].split('_'); 
// 				if(equity_added[val[0]]==null)
// 			   	{
// 			   		$('.added_equities').append('<span><span data-syms="'+val[0]+'_'+val[1]+'">'+val[0]+' '+val[1]+'</span><span><img src="/static/imgs/new/close.svg"></span></span>');
// 				   	// symbols.push(ui.item.value.split(' ').reverse());
// 				   	// ui.item.value = "";
// 				   	$(".added_equities img").click(function(){

// 						x = $($($(this).parentsUntil('.added_equities')).find('span')[0]).data('syms');
// 						if(x!=null){
// 							[sym,seg] = x.split('_');
// 							delete equity_added[sym];
// 						}
// 						$(this).parentsUntil('.added_equities').remove();

// 						if(Object.keys(equity_added).length==0){
// 							$($('.adding_equities_section div span')[0]).css("background-color", "#ADADAD");
// 							$($('.adding_equities_section div span')[0]).css("border-color", "#F3F3F3");
// 						}
// 					});
					
// 					equity_added[val[0]]=val[1];
// 					$($('.adding_equities_section div span')[0]).css("background-color", "#06D092");
// 					$($('.adding_equities_section div span')[0]).css("border-color", "#B1FDE6");

// 			   	}
// 			}
// 		}
// 	});
//  }
$(document).ready(function(){
  	date_updater();
  	// $('#ip_interval').on('change',function(){
  	// 	if(candle_freq_map[interval_mapping[$("#ip_interval").val()]]<min_candle_freq && !(min_candle_freq==10||min_candle_freq==1000)){
   //      $("#ip_interval").val(interval_mapping_rev[freq_candle_map[min_candle_freq+1]]);
   //      show_snackbar(null,'Choose a smaller candle interval');
   //    }
  	// 	date_updater();
  	// });
  	$("#open_parameters").click(function(){
  		$(".test_headers").slideDown();
  		$("#open_parameters span").html("<img src='/static/imgs/new/filter.svg'>Parameters");
  		$("#open_parameters").css("color", "#6e6e6e");
  	});
  	$("#close_parameters").click(function(){
  		$(".test_headers").slideUp();
  		$("#open_parameters span").html("<img src='/static/imgs/new/filter_blue.svg'>Parameters");
  		$("#open_parameters").css("color", "#0088ff");
  		try{
			elements.start_calendar.style.display = "none";
			elements.stop_calendar.style.display = "none";
  		}catch(e){
  			console.log(e);
  		}
  	});
	  // $(".transactions_section").click(function(){
	  // 	// alert($(this).attr("class"));
	  // 	$(this).toggleClass("expandable-color");
	  // 	$(this).parentsUntil(".backtest_results_row").find(".transactions_table").slideToggle();
	  // 	if($(this).find("img").attr("src") == "/static/imgs/icon-down-arrow.png"){
	  // 	$(this).find("img").attr("src", "/static/imgs/icon-up-arrow.png");	
	  // 	}
	  // 	else{
	  // 	$(this).find("img").attr("src", "/static/imgs/icon-down-arrow.png");
	  // 	}
	  // });
	$("#myProgress").click(function(){
 		var elem = document.getElementById("myBar");   
 		var width = 1;
 		var id = setInterval(frame, 10);
 		function frame() {
 	  if (width >= 100) {
 	    clearInterval(id);
 	  } else {
 	    width++; 
 	    elem.style.width = width + '%'; 
 	  }
 		}
 	});
	// $(".share").click(function(){
    	// $(this).parents(".actions_section").find(".social_buttons").fadeToggle();
    	// $(this).parents(".actions_section").find(".share_window").fadeToggle();
  	// });
  	// $(".share").click(function(){
   //  	$(this).parents(".actions_section").find(".share_window").fadeOut();
  	// });
  	// $(".social_buttons button").click(function(){
   //  	$(this).parents(".actions_section").find(".share_window").fadeIn();
  	// });
 	$('.added_equities span').each(function(e){
 		if($(this).data('syms')!=null){
 			[sym,seg]=$(this).data('syms').split('_');
 			equity_added[sym+'_'+seg]=seg;
 		}
 	});
 	$(".added_equities img").click(function(){
		x = $($($(this).parentsUntil('.added_equities')).find('span')[0]).data('syms');
		if(x!=null){
			[sym,seg] = x.split('_');
			delete equity_added[x];
		}
		$(this).parentsUntil('.added_equities').remove();
	});

 	$( "#equities_input" ).autocomplete({
	  source: function(request,response){
		// params = {'query':request['term'].toLowerCase()}
    params = JSON.stringify({"limit":40,"search":request['term'].toLowerCase(),"search_fields": ["name", "symbol","segment"]});
    $.ajax({
      type: "POST",
      dataType: "json",
      data: params,
      url: 'https://s.streak.world/instruments/basic_search',
      headers: { 'Content-Type': 'application/json' },
      // async: false,
      success: function(data) {
        //data is the JSON string
        response($.map(data['data'], function (el) {
         return {
           label: el['symbol']+' '+el['segment'],
           name: el['name'],
           value: el['symbol']+' '+el['segment'], //assumption, symbols and segment name does not have space in between
         };
       }));
      }
    });
    // $.post('https://s.streak.world/instruments/basic_search', params,function(data) {
    //   // alert(data);
    //   // if(data['status']=='success'){

    //     response($.map(data['data'], function (el) {
    //        return {
    //          label: el['symbol']+' '+el['segment'],
    //          name: el['name'],
    //          value: el['symbol']+' '+el['segment'], //assumption, symbols and segment name does not have space in between
    //        };
    //      }));
    //   // }
    // });
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
	   	if(val.length>2){
	   		// var temp = val[1];
        val[0]=val[0]+' '+val[1];
	   		val[1]=val[2];
        if(val[0]=="NIFTY FIN"){ 
          val[0]="NIFTY FIN SERVICE"; 
          val[1]="INDICES"; 
        } 
        if(val[0]=="NIFTY PSU"){ 
          val[0]="NIFTY PSU BANK"; 
          val[1]="INDICES"; 
        } 
	   	}
	   	if(Object.keys(equity_added).length>=20)
		   	{
		   		show_snackbar(null,'Cannot add more than 20 instruments');
		   		return false;
		   	}
		if(val[val.length-1]!='NSE' && val[val.length-1]!='NFO-FUT' && val[val.length-1]!='INDICES' && val[val.length-1]!='CDS-FUT' &&  val[0].indexOf('/')==-1){
        	var basket_name = ui.item.value.split(' ').slice(0,val.length-1).join(' ');
        	load_basket(basket_name);
        	$("#equities_input").val('');
        	$("#equities_input").focus();
        	return false;
      	}
	   	if(equity_added[val[0]+'_'+val[1]]==null)// || equity_added[val[0]]!=val[1])
	   	{
	   		$('.added_equities').append('<span><span data-syms="'+val[0]+'_'+val[1]+'">'+ui.item.value+'</span><span><img src="/static/imgs/new/close.svg"></span></span>');
		   	// symbols.push(ui.item.value.split(' ').reverse());
		   	// ui.item.value = "";
		   	$(".added_equities img").click(function(){

				x = $($($(this).parentsUntil('.added_equities')).find('span')[0]).data('syms');
				if(x!=null){
					[sym,seg] = x.split('_');
					delete equity_added[x];
				}
				$(this).parentsUntil('.added_equities').remove();

				if(Object.keys(equity_added).length==0){
					$($('.adding_equities_section div span')[0]).css("background-color", "#ADADAD");
					$($('.adding_equities_section div span')[0]).css("border-color", "#F3F3F3");
				}
			});
			
			equity_added[val[0]+'_'+val[1]]=val[1];
			$($('.adding_equities_section div span')[0]).css("background-color", "#06D092");
			$($('.adding_equities_section div span')[0]).css("border-color", "#B1FDE6");

	   	}
		$("#equities_input").val('');
	    $("#equities_input").focus();
	   	return false
	   }
	}).data( "ui-autocomplete" )._renderItem = function( ul, item ) {
      // console.log(item)
      return $( "<li></li>" )
        .data( "item.autocomplete", item )
        .append( "<a><img src='/static/imgs/new/currencies/"+item.label.split('/')[0]+".png'/>" + item.label +"</a>" )
        .appendTo( ul );
    };


	$( "#algos_search_input" ).autocomplete({
	  source: function(request,response){
		// params = {'query':request['term'].toLowerCase()}
		var params = {
				"limit": 10,
				"user_uuid": $("#ui_cc").val(),
				"search": request['term'].toLowerCase(),
				"search_fields": ["algo_name", "action_str", "symbols"],
				"return_fields": ["algo_name", "algo_uuid"]
				}

	  	var settings = {
	      "async": true,
	      "crossDomain": true,
	      "url": 'https://s.streak.tech/algorithms/basic_search',
	      "method": "POST",
	      "headers": {
	      	"Content-Type": "application/json"
	      },
	      "data":JSON.stringify(params),
	      "timeout": 10000,//40 sec timeout
	    };

  		$.ajax(settings).done(function(data) {
			// alert(data);
			if(data['data']!=undefined){

				response($.map(data['data'], function (el) {
					 return {
						 label: el['algo_name'],
						 value: el['algo_name'],
						 u_id: el['algo_uuid'], //assumption, symbols and segment name does not have space in between
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
			$("#algos_search_input").val('');
			$("#algos_search_input").focus();
			}
	   $("#algos_search_input").val('');
	   $("#algos_search_input").focus();
	   // ui.item.value = "";
		},
	   select:function(event, ui){
	   	// console.log('selected');
	   	// console.log(ui['item'])
	 //   	val = ui.item.value.split(' ');
	 //   	if(val.length>2){
	 //   		// var temp = val[1];
	 //   		val[0]=val[0]+' '+val[1];
	 //   		val[1]=val[2];
	 //   	}
	 //   	if(Object.keys(equity_added).length>=20)
		//    	{
		//    		show_snackbar(null,'Cannot add more than 20 instruments');
		//    		return false;
		//    	}
		// if(val[val.length-1]!='NSE' && val[val.length-1]!='NFO-FUT' && val[val.length-1]!='INDICES' && val[val.length-1]!='CDS-FUT'){
  //       	var basket_name = ui.item.value.split(' ').slice(0,val.length-1).join(' ');
  //       	load_basket(basket_name);
  //       	$("#algos_search_input").val('');
  //       	$("#algos_search_input").focus();
  //       	return false;
  //     	}
	 //   	if(equity_added[val[0]]==null)
	 //   	{
	 //   		$('.added_equities').append('<span><span data-syms="'+val[0]+'_'+val[1]+'">'+ui.item.value+'</span><span><img src="/static/imgs/new/close.svg"></span></span>');
		//    	// symbols.push(ui.item.value.split(' ').reverse());
		//    	// ui.item.value = "";
		//    	$(".added_equities img").click(function(){

		// 		x = $($($(this).parentsUntil('.added_equities')).find('span')[0]).data('syms');
		// 		if(x!=null){
		// 			[sym,seg] = x.split('_');
		// 			delete equity_added[sym];
		// 		}
		// 		$(this).parentsUntil('.added_equities').remove();

		// 		if(Object.keys(equity_added).length==0){
		// 			$($('.adding_equities_section div span')[0]).css("background-color", "#ADADAD");
		// 			$($('.adding_equities_section div span')[0]).css("border-color", "#F3F3F3");
		// 		}
		// 	});
			
		// 	equity_added[val[0]]=val[1];
		// 	$($('.adding_equities_section div span')[0]).css("background-color", "#06D092");
		// 	$($('.adding_equities_section div span')[0]).css("border-color", "#B1FDE6");

	 //   	}
	 	window.location.href='/backtests/?algo_uuid='+ui.item.u_id;
		$("#algos_search_input").val('');
	    $("#algos_search_input").focus();
	   	return false
	   }
	});

 	// if (run_backtest_flag == true)
		// run_backtest_sequential();


	// $('#'+k+' .brokerage_toggle:checkbox').on('change',function(e){
	// 	broker_toggle(e);
	// });
});

function broker_toggle_(e){
	backtest_results_row = $(e.target).closest('.backtest_results_row')[0];
	k = backtest_results_row.id;
	if($(e.target).is(':checked')){
		if (k!=undefined && backtest_result_response[k]!=null && backtest_result_response[k]!=undefined)
		{
			[adj_pnl,max_cap_used] = processListToXYList_brokerage(k,backtest_result_response[k].trade_log,backtest_result_response[k].pnl);
			adj_final_pnl = adj_pnl[adj_pnl.length-1].y;
			pnl_div = $(backtest_results_row).find('.pnl');
			if (adj_final_pnl>=0)
				{
					color = '#06d092';
					img_url = "/static/imgs/icon-arrow-up-green.png";	
					adj_return = adj_final_pnl/max_cap_used*100;
					pnl_div.html('<p>P&amp;L&nbsp;<span><img src='+img_url+'>&nbsp;</span><span style="color:'+color+'">'+adj_final_pnl+'&nbsp;</span><span style="color:'+color+'" "="">( +'+adj_return.toFixed(2)+'%)&nbsp;</span></p>');
				}
			else
				{
					color = '#ff4343';
					img_url = "/static/imgs/icon-arrow-down-red.png";
					adj_return = adj_final_pnl/max_cap_used*100;
					pnl_div.html('<p>P&amp;L&nbsp;<span><img src='+img_url+'>&nbsp;</span><span style="color:'+color+'">'+adj_final_pnl+'&nbsp;</span><span style="color:'+color+'" "="">( '+adj_return.toFixed(2)+'%)&nbsp;</span></p>');
				}
			// var ctx = document.getElementById(k.replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").getContext('2d');
			// var ctx = $('#'+k+"pnl_chartContainer_new");

			$('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").replaceWith('<canvas id="'+k.replace('/','_--_').replace(/ /g,'_-_')+'pnl_chartContainer_new"></canvas>');
			// var ctx = $('#'+k+"pnl_chartContainer_new")[0].getContext('2d');

			var ctx = document.getElementById(k.replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").getContext('2d');

			var pnl_chartContainer_new = new Chart(ctx,{
				type: 'line',
				scaleSteps : 4,
		    	data: {
		    		// labels: ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
					datasets: [{
					    label: 'P&L',
					    data: adj_pnl,
					    backgroundColor:'rgba(255,255,255,0)',
					    borderColor: '#2288ff',
					    borderWidth: 2,
					    lineTension: 0,
					    // pointStyle: 'star',
					    // point: { radius: 0 },
					    hoverRadius: 5
					}]
		    	},
		    	options: {
		    		scales: {
		            yAxes: [{
		            	gridLines: {
							color: '#ecf0f1',
							zeroLineBorderDash: [5, 5],
							zeroLineColor: '#ecf0f1'
								},
		                ticks: {
		                	fontColor: '#9ea1a4',
		                    beginAtZero:true,
		                    // maxTicksLimit:1
		                    // ticks: {min: 0, max:4}
		                }
		            }],
		            	xAxes: [{
				        type: 'time',
				        position: 'bottom',
				         gridLines: {
								display: false,
								color: '#ecf0f1',
								zeroLineBorderDash: [5, 5],
								zeroLineColor: '#ecf0f1'
						},
						ticks: {
							fontColor: '#9ea1a4'
						},
				        time: {
				          displayFormats: {
				          	// 'millisecond': 'MMM DD',
				           //  'second': 'MMM DD',
				           //  'minute': 'MMM DD',
				           //  'hour': 'MMM DD',
				           //  'day': 'MMM DD',
				           //  'week': 'MMM DD',
				           //  'month': 'MMM DD',
				           //  'quarter': 'MMM DD',
				            'year': 'YY MMM DD',
				          }
				        }
				      }],
					},
					legend: {
					    display: false,
					},
					// title: {
					//     display: true,
					//     text: 'P&L Performance',
					//     fontColor: '#333333',
					//     fontFamily: '"open_sansregular","AvenirNextLTPro",Arial,Helvetica,sans-serif',
					//     fontStyle:'bold',
					//     position: 'top',
					//     fontSize: 16
					// },
					// legend: {
					//     display: true,
					//     labels: {
					//         fontColor: '#666666'
					//     }
					// },
					elements: { point: { radius: 0 } },	
				}
			});


			var transactions_table = $('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')).find(".transactions_table");
			transactions_table.empty();

			var trade_log = $("<table>",{}).append('<tr><th>Trigger date</th><th>Equity</th><th>Buy/Sell</th><th>Qty</th><th>Price</th><th>Cumulative P&L</th><th>Trigger type</th></tr>');
			var prev_pnl = 0;
			var total_brokerage_till_now = 0.0
			data = backtest_result_response[k];
			for(var i = 0; i <= data.trade_log.length - 1; i++){
				if(data.trade_log[i][3]!=0)
					{
					trade_row = '<tr>';
					date = new Date(data.trade_log[i][0]);
					// trade_row += '<td>'+dateFormat(date, "dS - mmmm - yyyy, h:MM:ss TT")+'</td>';
					// trade_row += '<td>'+dateFormat(date, "dd - mmm - yyyy, hh:MM:ss A")+'</td>';
					trade_row += '<td>'+moment(date).format("DD - MMM - YYYY, hh:mm:ss A")+'</td>';
					// trade_row += '<td>'+data.trade_log[i][1]+'</td>';
					trade_row += '<td>'+sym+' '+seg+'</td>';
					
					if (data.trade_log[i][2]=='BUY')
						trade_row += '<td class="buy_tag">'+data.trade_log[i][2]+'</td>'
					else
						trade_row += '<td class="sell_tag">'+data.trade_log[i][2]+'</td>'

					trade_row += '<td>'+data.trade_log[i][3]+'</td>'
					trade_row += '<td>'+parseFloat(data.trade_log[i][4]).toFixed(2)+'</td>'
					t_pnl = parseFloat(data.trade_log[i][5])
					total_brokerage_till_now += broker_cal(seg,sym,parseFloat(data.trade_log[i][3]),parseFloat(data.trade_log[i][4]));
					t_pnl -= total_brokerage_till_now;
					if ( prev_pnl<=t_pnl)
						trade_row += '<td class="profit">'+t_pnl.toFixed(2)+'</td>'
					else
						trade_row += '<td class="loss">'+t_pnl.toFixed(2)+'</td>'
					prev_pnl = t_pnl;

					portfolio_val = parseFloat(data.trade_log[i][6]) - total_brokerage_till_now;

					trade_row += '<td>'+parseFloat(portfolio_val).toFixed(2)+'</td>'

					trade_row += '</tr>';
					trade_log.append(trade_row);
				}
			}

			transactions_table.append(trade_log);
		}
	}else{
		if (k!=undefined && backtest_result_response[k]!=null && backtest_result_response[k]!=undefined)
		{
		// var ctx = document.getElementById(k.replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").getContext('2d');
			$('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").replaceWith('<canvas id="'+k.replace('/','_--_').replace(/ /g,'_-_')+'pnl_chartContainer_new"></canvas>');
			var ctx = document.getElementById(k.replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").getContext('2d');
			max_cap_used = backtest_result_response[k].max_cap_used;
			abs_pnl = processListToXYList(backtest_result_response[k].pnl);
			abs_final_pnl = backtest_result_response[k].final_pnl;//abs_pnl[abs_pnl.length-1].y;
			pnl_div = $(backtest_results_row).find('.pnl');
			if (abs_final_pnl>=0)
				{
					color = '#06d092';
					img_url = "/static/imgs/icon-arrow-up-green.png";	
					adj_return = abs_final_pnl/max_cap_used*100;//abs_final_pnl/max_cap_used*100;
					pnl_div.html('<p>P&amp;L&nbsp;<span><img src='+img_url+'>&nbsp;</span><span style="color:'+color+'">'+abs_final_pnl.toFixed(2)+'&nbsp;</span><span style="color:'+color+'" "="">( +'+adj_return.toFixed(2)+'%)&nbsp;</span></p>');
				}
			else
				{
					color = '#ff4343';
					img_url = "/static/imgs/icon-arrow-down-red.png";
					adj_return = abs_final_pnl/max_cap_used*100;//abs_final_pnl/max_cap_used*100;
					pnl_div.html('<p>P&amp;L&nbsp;<span><img src='+img_url+'>&nbsp;</span><span style="color:'+color+'">'+abs_final_pnl.toFixed(2)+'&nbsp;</span><span style="color:'+color+'" "="">( '+adj_return.toFixed(2)+'%)&nbsp;</span></p>');
				}
			var pnl_chartContainer_new = new Chart(ctx,{
				type: 'line',
				scaleSteps : 4,
		    	data: {
		    		// labels: ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
					datasets: [{
					    label: 'P&L',
					    data: abs_pnl,
					    backgroundColor:'rgba(255,255,255,0)',
					    borderColor: '#2288ff',
					    borderWidth: 2,
					    lineTension: 0,
					    // pointStyle: 'star',
					    // point: { radius: 0 },
					    hoverRadius: 5
					}]
		    	},
		    	options: {
		    		scales: {
		            yAxes: [{
		            	gridLines: {
							color: '#ecf0f1',
							zeroLineBorderDash: [5, 5],
							zeroLineColor: '#ecf0f1'
								},
		                ticks: {
		                	fontColor: '#9ea1a4',
		                    beginAtZero:true,
		                    // maxTicksLimit:1
		                    // ticks: {min: 0, max:4}
		                }
		            }],
		            	xAxes: [{
				        type: 'time',
				        position: 'bottom',
				         gridLines: {
								display: false,
								color: '#ecf0f1',
								zeroLineBorderDash: [5, 5],
								zeroLineColor: '#ecf0f1'
						},
						ticks: {
							fontColor: '#9ea1a4'
						},
				        time: {
				          displayFormats: {
				          	// 'millisecond': 'MMM DD',
				           //  'second': 'MMM DD',
				           //  'minute': 'MMM DD',
				           //  'hour': 'MMM DD',
				           //  'day': 'MMM DD',
				           //  'week': 'MMM DD',
				           //  'month': 'MMM DD',
				           //  'quarter': 'MMM DD',
				            'year': 'YY MMM DD',
				          }
				        }
				      }],
					},
					legend: {
					    display: false,
					},
					// title: {
					//     display: true,
					//     text: 'P&L Performance',
					//     fontColor: '#333333',
					//     fontFamily: '"open_sansregular","AvenirNextLTPro",Arial,Helvetica,sans-serif',
					//     fontStyle:'bold',
					//     position: 'top',
					//     fontSize: 16
					// },
					// legend: {
					//     display: true,
					//     labels: {
					//         fontColor: '#666666'
					//     }
					// },
					elements: { point: { radius: 0 } },	
				}
			});


			var transactions_table = $('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')).find(".transactions_table");
			transactions_table.empty();

			var trade_log = $("<table>",{}).append('<tr><th>Trigger date</th><th>Equity</th><th>Buy/Sell</th><th>Qty</th><th>Price</th><th>Cumulative P&L</th><th>Trigger type</th></tr>');
			var prev_pnl = 0;
			data = backtest_result_response[k];
			for(var i = 0; i <= data.trade_log.length - 1; i++){
				if(data.trade_log[i][3]!=0)
					{
					trade_row = '<tr>';
					date = new Date(data.trade_log[i][0]);
					// trade_row += '<td>'+dateFormat(date, "dS - mmmm - yyyy, h:MM:ss TT")+'</td>';
					// trade_row += '<td>'+dateFormat(date, "dd - mmm - yyyy, hh:MM:ss A")+'</td>';
					trade_row += '<td>'+moment(date).format("DD - MMM - YYYY, hh:mm:ss A")+'</td>';
					// trade_row += '<td>'+data.trade_log[i][1]+'</td>';
					trade_row += '<td>'+sym+' '+seg+'</td>';
					
					if (data.trade_log[i][2]=='BUY')
						trade_row += '<td class="buy_tag">'+data.trade_log[i][2]+'</td>'
					else
						trade_row += '<td class="sell_tag">'+data.trade_log[i][2]+'</td>'

					trade_row += '<td>'+data.trade_log[i][3]+'</td>'
					trade_row += '<td>'+parseFloat(data.trade_log[i][4]).toFixed(2)+'</td>'
					t_pnl = parseFloat(data.trade_log[i][5]);
					if ( prev_pnl<t_pnl)
						trade_row += '<td class="profit">'+t_pnl.toFixed(2)+'</td>'
					else
						trade_row += '<td class="loss">'+t_pnl.toFixed(2)+'</td>'
					prev_pnl = t_pnl;

					portfolio_val = parseFloat(data.trade_log[i][6]);

					trade_row += '<td>'+parseFloat(portfolio_val).toFixed(2)+'</td>'
					
					trade_row += '</tr>';
					trade_log.append(trade_row);
				}
			}

			transactions_table.append(trade_log);
		}
	}
}

function broker_toggle(e){
	// backtest_results_row = $(e.target).closest('.backtest_results_row')[0];
	backtest_results_row = $(e.target).closest('.multiple_backtest_row').find('.multiple_backtest_row_first');
	k = backtest_results_row.id;
	k = e.target.id;
	// [seg,sym] = k.split('_');
	rounding = 2
	if (seg=='CDS-FUT')
		rounding = 4
	if($(e.target).is(':checked')){
    $(e.target).closest('p').attr('data-tooltip-bottom','Adjusted for brokerage and other charges (does not include stamp duty and DP charges)');
		if (k!=undefined && backtest_result_response[k]!=null && backtest_result_response[k]!=undefined)
		{
			[adj_pnl,max_cap_used] = processListToXYList_brokerage(k,backtest_result_response[k].trade_log,backtest_result_response[k].pnl);
			adj_final_pnl = adj_pnl[adj_pnl.length-1].y;
			pnl_div = $(backtest_results_row).find('.pnl');

			stroke = '#06d092';
			var addColor1 = 'rgba(6,208,146, 0.15)';
      		var addColor2 = 'rgba(6,208,146, 0)';

			if(adj_final_pnl<0.0){
				stroke = '#f43b51';
				addColor1 = 'rgba(255,66,88, 0)';
				addColor2 = 'rgba(255,66,88, 0.15)';
			}
		    
			if (adj_final_pnl>=0)
				{
					color = '#06d092';
					img_url = "/static/imgs/icon-arrow-up-green.png";	
					adj_return = adj_final_pnl/max_cap_used*100;
					pnl_div.html('<p><span><img src='+img_url+'>&nbsp;</span><span style="color:'+color+'">'+adj_final_pnl+'&nbsp;</span><span style="color:'+color+'" "="">( +'+adj_return.toFixed(2)+'%)&nbsp;</span></p>');
				}
			else
				{
					color = '#ff4343';
					img_url = "/static/imgs/icon-arrow-down-red.png";
					adj_return = adj_final_pnl/max_cap_used*100;
					pnl_div.html('<p><span><img src='+img_url+'>&nbsp;</span><span style="color:'+color+'">'+adj_final_pnl+'&nbsp;</span><span style="color:'+color+'" "="">( '+adj_return.toFixed(2)+'%)&nbsp;</span></p>');
				}
			// var ctx = document.getElementById(k.replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").getContext('2d');
			// var ctx = $('#'+k+"pnl_chartContainer_new");

			$('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").replaceWith('<canvas id="'+k.replace('/','_--_').replace(/ /g,'_-_')+'pnl_chartContainer_new"></canvas>');
			// var ctx = $('#'+k+"pnl_chartContainer_new")[0].getContext('2d');

			var ctx = document.getElementById(k.replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").getContext('2d');

			var gradient = ctx.createLinearGradient(0, 0, 0, 400);
		    gradient.addColorStop(0, addColor1);
		    gradient.addColorStop(0.8, addColor2);

			var pnl_chartContainer_new = new Chart(ctx,{
				type: 'line',
				scaleSteps : 4,
		    	data: {
		    		// labels: ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
					datasets: [{
					    label: 'P&L',
					    data: adj_pnl,
					    // backgroundColor:'rgba(255,255,255,0)',
					    backgroundColor: gradient,
					    // borderColor: '#2288ff',
					    borderColor: stroke,
					    borderWidth: 2,
					    lineTension: 0,
          				strokeColor: stroke,
					    // pointStyle: 'star',
					    // point: { radius: 0 },
					    hoverRadius: 5
					}]
		    	},
		    	options: {
		    		scales: {
		            yAxes: [{
		            	gridLines: {
							color: '#ecf0f1',
							zeroLineBorderDash: [5, 5],
							zeroLineColor: '#ecf0f1'
								},
		                ticks: {
		                	fontColor: '#9ea1a4',
		                    beginAtZero:true,
		                    // maxTicksLimit:1
		                    // ticks: {min: 0, max:4}
		                }
		            }],
		            	xAxes: [{
				        type: 'time',
				        position: 'bottom',
				         gridLines: {
								display: false,
								color: '#ecf0f1',
								zeroLineBorderDash: [5, 5],
								zeroLineColor: '#ecf0f1'
						},
						ticks: {
							fontColor: '#9ea1a4'
						},
				        time: {
				          displayFormats: {
				          	// 'millisecond': 'MMM DD',
				           //  'second': 'MMM DD',
				           //  'minute': 'MMM DD',
				           //  'hour': 'MMM DD',
				           //  'day': 'MMM DD',
				           //  'week': 'MMM DD',
				           //  'month': 'MMM DD',
				           //  'quarter': 'MMM DD',
				            'year': 'YY MMM DD',
				          }
				        }
				      }],
					},
					legend: {
					    display: false,
					},
					// title: {
					//     display: true,
					//     text: 'P&L Performance',
					//     fontColor: '#333333',
					//     fontFamily: '"open_sansregular","AvenirNextLTPro",Arial,Helvetica,sans-serif',
					//     fontStyle:'bold',
					//     position: 'top',
					//     fontSize: 16
					// },
					// legend: {
					//     display: true,
					//     labels: {
					//         fontColor: '#666666'
					//     }
					// },
					elements: { point: { radius: 0 } },	
				}
			});


			var transactions_table = $('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')).find(".transactions_table");
			transactions_table.empty();

			data = backtest_result_response[k];
			if(data.trade_log[0][7]!=undefined)
				var trade_log = $("<table>",{}).append('<tr><th>Trigger date</th><th>Equity</th><th>Buy/Sell</th><th>Qty</th><th>Price</th><th>Cumulative P&L</th><th>Trigger type</th></tr>');
			else
				var trade_log = $("<table>",{}).append('<tr><th>Trigger date</th><th>Equity</th><th>Buy/Sell</th><th>Qty</th><th>Price</th><th>Cumulative P&L</th></tr>');

			var prev_pnl = 0;
			var total_brokerage_till_now = 0.0
			for(var i = 0; i <= data.trade_log.length - 1; i++){
				if(data.trade_log[i][3]!=0)
					{
					trade_row = '<tr>';
					date = new Date(data.trade_log[i][0]);
					// trade_row += '<td>'+dateFormat(date, "dS - mmmm - yyyy, h:MM:ss TT")+'</td>';
					// trade_row += '<td>'+dateFormat(date, "dd - mmm - yyyy, hh:MM:ss A")+'</td>';
					trade_row += '<td>'+moment(date).format("DD - MMM - YYYY, hh:mm:ss A")+'</td>';
					// trade_row += '<td>'+data.trade_log[i][1]+'</td>';
					trade_row += '<td>'+sym+' '+seg+'</td>';
					
					if (data.trade_log[i][2]=='BUY')
						trade_row += '<td class="buy_tag">'+data.trade_log[i][2]+'</td>'
					else
						trade_row += '<td class="sell_tag">'+data.trade_log[i][2]+'</td>'

					trade_row += '<td>'+data.trade_log[i][3]+'</td>'
					trade_row += '<td>'+parseFloat(data.trade_log[i][4]).toFixed(rounding)+'</td>'
					t_pnl = parseFloat(data.trade_log[i][5])
					total_brokerage_till_now += broker_cal(seg,sym,parseFloat(data.trade_log[i][3]),parseFloat(data.trade_log[i][4]));
					t_pnl -= total_brokerage_till_now;
					if ( prev_pnl<=t_pnl)
						trade_row += '<td class="profit">'+t_pnl.toFixed(2)+'</td>'
					else
						trade_row += '<td class="loss">'+t_pnl.toFixed(2)+'</td>'
					prev_pnl = t_pnl;

					portfolio_val = parseFloat(data.trade_log[i][6]) - total_brokerage_till_now;

					// trade_row += '<td>'+parseFloat(portfolio_val).toFixed(2)+'</td>'
					if(data.trade_log[i][7]!=undefined)
						trade_row += '<td>'+data.trade_log[i][7]+'</td>'
					trade_row += '</tr>';
					trade_log.append(trade_row);
				}
			}

			transactions_table.append(trade_log);
		}
	}else{
		if (k!=undefined && backtest_result_response[k]!=null && backtest_result_response[k]!=undefined)
		{
		// var ctx = document.getElementById(k.replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").getContext('2d');
			$('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").replaceWith('<canvas id="'+k.replace('/','_--_').replace(/ /g,'_-_')+'pnl_chartContainer_new"></canvas>');
			var ctx = document.getElementById(k.replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").getContext('2d');
			max_cap_used = backtest_result_response[k].max_cap_used;
			abs_pnl = processListToXYList(backtest_result_response[k].pnl);
			abs_final_pnl = backtest_result_response[k].final_pnl;//abs_pnl[abs_pnl.length-1].y;
			pnl_div = $(backtest_results_row).find('.pnl');

			stroke = '#06d092';
			var addColor1 = 'rgba(6,208,146, 0.15)';
      		var addColor2 = 'rgba(6,208,146, 0)';

			if(abs_final_pnl<0.0){
				stroke = '#f43b51';
				addColor1 = 'rgba(255,66,88, 0)';
				addColor2 = 'rgba(255,66,88, 0.15)';
			}

			var gradient = ctx.createLinearGradient(0, 0, 0, 400);
		    gradient.addColorStop(0, addColor1);
		    gradient.addColorStop(0.8, addColor2);

			if (abs_final_pnl>=0)
				{
					color = '#06d092';
					img_url = "/static/imgs/icon-arrow-up-green.png";	
					adj_return = abs_final_pnl/max_cap_used*100;//abs_final_pnl/max_cap_used*100;
					pnl_div.html('<p><span><img src='+img_url+'>&nbsp;</span><span style="color:'+color+'">'+abs_final_pnl.toFixed(2)+'&nbsp;</span><span style="color:'+color+'" "="">( +'+adj_return.toFixed(2)+'%)&nbsp;</span></p>');
				}
			else
				{
					color = '#ff4343';
					img_url = "/static/imgs/icon-arrow-down-red.png";
					adj_return = abs_final_pnl/max_cap_used*100;//abs_final_pnl/max_cap_used*100;
					pnl_div.html('<p><span><img src='+img_url+'>&nbsp;</span><span style="color:'+color+'">'+abs_final_pnl.toFixed(2)+'&nbsp;</span><span style="color:'+color+'" "="">( '+adj_return.toFixed(2)+'%)&nbsp;</span></p>');
				}
			var pnl_chartContainer_new = new Chart(ctx,{
				type: 'line',
				scaleSteps : 4,
		    	data: {
		    		// labels: ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
					datasets: [{
					    label: 'P&L',
					    data: abs_pnl,
					    // backgroundColor:'rgba(255,255,255,0)',
					    backgroundColor: gradient,
					    // borderColor: '#2288ff',
					    borderColor: stroke,
					    borderWidth: 2,
					    lineTension: 0,
          				strokeColor: stroke,
					    // pointStyle: 'star',
					    // point: { radius: 0 },
					    hoverRadius: 5
					}]
		    	},
		    	options: {
		    		scales: {
		            yAxes: [{
		            	gridLines: {
							color: '#ecf0f1',
							zeroLineBorderDash: [5, 5],
							zeroLineColor: '#ecf0f1'
								},
		                ticks: {
		                	fontColor: '#9ea1a4',
		                    beginAtZero:true,
		                    // maxTicksLimit:1
		                    // ticks: {min: 0, max:4}
		                }
		            }],
		            	xAxes: [{
				        type: 'time',
				        position: 'bottom',
				         gridLines: {
								display: false,
								color: '#ecf0f1',
								zeroLineBorderDash: [5, 5],
								zeroLineColor: '#ecf0f1'
						},
						ticks: {
							fontColor: '#9ea1a4'
						},
				        time: {
				          displayFormats: {
				          	// 'millisecond': 'MMM DD',
				           //  'second': 'MMM DD',
				           //  'minute': 'MMM DD',
				           //  'hour': 'MMM DD',
				           //  'day': 'MMM DD',
				           //  'week': 'MMM DD',
				           //  'month': 'MMM DD',
				           //  'quarter': 'MMM DD',
				            'year': 'YY MMM DD',
				          }
				        }
				      }],
					},
					legend: {
					    display: false,
					},
					// title: {
					//     display: true,
					//     text: 'P&L Performance',
					//     fontColor: '#333333',
					//     fontFamily: '"open_sansregular","AvenirNextLTPro",Arial,Helvetica,sans-serif',
					//     fontStyle:'bold',
					//     position: 'top',
					//     fontSize: 16
					// },
					// legend: {
					//     display: true,
					//     labels: {
					//         fontColor: '#666666'
					//     }
					// },
					elements: { point: { radius: 0 } },	
				}
			});


			var transactions_table = $('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')).find(".transactions_table");
			transactions_table.empty();

			data = backtest_result_response[k];
			if(data.trade_log[0][7]!=undefined)
				var trade_log = $("<table>",{}).append('<tr><th>Trigger date</th><th>Equity</th><th>Buy/Sell</th><th>Qty</th><th>Price</th><th>Cumulative P&L</th><th>Trigger type</th></tr>');
			else
				var trade_log = $("<table>",{}).append('<tr><th>Trigger date</th><th>Equity</th><th>Buy/Sell</th><th>Qty</th><th>Price</th><th>Cumulative P&L</th></tr>');

			var prev_pnl = 0;
			for(var i = 0; i <= data.trade_log.length - 1; i++){
				if(data.trade_log[i][3]!=0)
					{
					trade_row = '<tr>';
					date = new Date(data.trade_log[i][0]);
					// trade_row += '<td>'+dateFormat(date, "dS - mmmm - yyyy, h:MM:ss TT")+'</td>';
					// trade_row += '<td>'+dateFormat(date, "dd - mmm - yyyy, hh:MM:ss A")+'</td>';
					trade_row += '<td>'+moment(date).format("DD - MMM - YYYY, hh:mm:ss A")+'</td>';
					// trade_row += '<td>'+data.trade_log[i][1]+'</td>';
					trade_row += '<td>'+sym+' '+seg+'</td>';
					
					if (data.trade_log[i][2]=='BUY')
						trade_row += '<td class="buy_tag">'+data.trade_log[i][2]+'</td>'
					else
						trade_row += '<td class="sell_tag">'+data.trade_log[i][2]+'</td>'

					trade_row += '<td>'+data.trade_log[i][3]+'</td>'
					trade_row += '<td>'+parseFloat(data.trade_log[i][4]).toFixed(rounding)+'</td>'
					t_pnl = parseFloat(data.trade_log[i][5]);
					if ( prev_pnl<t_pnl)
						trade_row += '<td class="profit">'+t_pnl.toFixed(2)+'</td>'
					else
						trade_row += '<td class="loss">'+t_pnl.toFixed(2)+'</td>'
					prev_pnl = t_pnl;

					portfolio_val = parseFloat(data.trade_log[i][6]);

					// trade_row += '<td>'+parseFloat(portfolio_val).toFixed(2)+'</td>'
					if(data.trade_log[i][7]!=undefined)
						trade_row += '<td>'+data.trade_log[i][7]+'</td>'
					trade_row += '</tr>';
					trade_log.append(trade_row);
				}
			}

			transactions_table.append(trade_log);
		}
	}
}

window.onload = function () {
 //  	$('.loader_parent').bind('ajaxStart', function(){
 //    $(this).show();
	// }).bind('ajaxStop', function(){
	//     $(this).hide();
	// });
    // $(".loader_parent_backtest").fadeIn();
	// $( document ).ajaxStart(function() {
 //      $( ".loader_parent_backtest" ).fadeIn();
 //    });
 //    $( document ).ajaxStop(function() {
 //      $( ".loader_parent_backtest" ).fadeOut();
 //    });
	// if (run_backtest_flag == true)
	// 	run_backtest();
}
// window.onload = function () {
	
// }
var piechartContainer_new;
var pnl_chartContainer_new;
var orders_chartContainer_new;
function back_test_input_valid(algo_uuid,initial_capital,
	            from_datepicker,
	            to_datepicker,
	            commission,symbols,stop_loss,take_profit,quantity,interval){
  // if(!isNaN(quantity) && quantity.toString().indexOf('.') != -1){
  //   show_snackbar(null,'Quantity must be positve integer');
  //   $(".loader_parent").fadeOut();
  //   // return false;
  // }
  if(!isNaN(quantity) && parseFloat(quantity)<0){
    show_snackbar(null,'Quantity must be positve integer');
    $(".loader_parent").fadeOut();
    return false;
  }
  if(!isNaN(quantity) && parseFloat(quantity)==0){
    show_snackbar(null,'Quantity must not be 0');
    $(".loader_parent").fadeOut();
    return false;
  }
  if(!isNaN(quantity) && parseFloat(quantity)>10000000){
    show_snackbar(null,'Quantity too high');
    $(".loader_parent").fadeOut();
    return false;
  }
  if(isNaN(quantity)){
    show_snackbar(null,'Quantity must be a positive integer');
    $(".loader_parent").fadeOut();
    return false;
  }
  if(quantity==null || quantity== undefined || quantity==''){
    show_snackbar(null,'Quantity must be a positive integer');
    $(".loader_parent").fadeOut();
    return false;
  }
  if(isNaN(parseFloat(initial_capital))|| parseFloat(initial_capital)<1){
  	show_snackbar(null,'Initial capital must be a positive number');
    $(".loader_parent").fadeOut();
    return false;
  }
  if(stop_loss==null || stop_loss== undefined || stop_loss==''){
    show_snackbar(null,'Stop loss percentage must be a positive number between 0 and 100');
    $(".loader_parent").fadeOut();
    return false;
  }
  if(take_profit==null || take_profit== undefined || take_profit==''){
    show_snackbar(null,'Target profit percentage must be a positive number between 0 and 100');
    $(".loader_parent").fadeOut();
    return false;
  }
  if(parseFloat(take_profit)==0){
    show_snackbar(null,'Target profit percentage cannot be 0%');
    $(".loader_parent").fadeOut();
    return false;
  }
  // if(parseFloat(take_profit)>95){
  //   show_snackbar(null,'Target profit cannot less than 0% !');
  //   $(".loader_parent").fadeOut();
  //   return false;
  // }
  var stop_loss_rep = stop_loss.replace('.','');
  if(stop_loss_rep.indexOf('.')>-1){
    show_snackbar(null,'Stop loss percentage must be between 0 to 10000');
    $(".loader_parent").fadeOut();
    return false;
  }
  var take_profit_rep = take_profit.replace('.','');
  if(take_profit_rep.indexOf('.')>-1){
    show_snackbar(null,'Stop loss percentage must be between 0 to 10000');
    $(".loader_parent").fadeOut();
    return false;
  }
  // if(quantity.indexOf('.')>-1){
  //   show_snackbar(null,'Quantity must be a positive integer');
  //   $(".loader_parent").fadeOut();
  //   return false;
  // }
  if(parseFloat(take_profit)<0 || parseFloat(take_profit)>=10000){
    show_snackbar(null,'Target profit percentage must be between 0% to 10000%');
    $(".loader_parent").fadeOut();
    return false;
  }
  if(parseFloat(take_profit)<0 || parseFloat(take_profit)>=100000 || isNaN(take_profit)){
    show_snackbar(null,'Target profit percentage must be between 0% to 100%');
    $(".loader_parent").fadeOut();
    return false;
  }
  if(parseFloat(stop_loss)==0){
    show_snackbar(null,'Stop loss percentage cannot be 0%');
    $(".loader_parent").fadeOut();
    return false;
  }
  // if(parseFloat(stop_loss)>95){
  //   show_snackbar(null,'Stop loss cannot be 0% !');
  //   $(".loader_parent").fadeOut();
  //   return false;
  // }
  if(parseFloat(stop_loss)<0 || parseFloat(stop_loss)>=100000 || isNaN(stop_loss)){
    show_snackbar(null,'Stop loss percentage must be between 0 to 100');
    $(".loader_parent").fadeOut();
    return false;
  }
  var startDate = moment(from_datepicker,'DD/MM/YYYY');
  var endDate = moment(to_datepicker,'DD/MM/YYYY');
  switch(interval){
  	case "min":
  		if(endDate-startDate>(90-1)*24*3600000){
			show_snackbar(null,'Select a shorter backtest period for the candle interval');
			return false;
		  	}
  		break;
  	case "3min":
  		if(endDate-startDate>(90-1)*24*3600000){
			show_snackbar(null,'Select a shorter backtest period for the candle interval');
			return false;
		  	}
  		break;
  	case "5min":
  		if(endDate-startDate>(90-1)*24*3600000){
			show_snackbar(null,'Select a shorter backtest period for the candle interval');
			return false;
		  	}
  		break;
  	case "10min":
  		if(endDate-startDate>(90-1)*24*3600000){
			show_snackbar(null,'Select a shorter backtest period for the candle interval');
			return false;
		  	}
  		break;
  	case "15min":
  		if(endDate-startDate>(90-1)*24*3600000){
			show_snackbar(null,'Select a shorter backtest period for the candle interval');
			return false;
		  	}
  		break;
  	case "30min":
  		if(endDate-startDate>(90-1)*24*3600000){
			show_snackbar(null,'Select a shorter backtest period for the candle interval');
			return false;
		  	}
  		break;
  	case "hour":
  		if(endDate-startDate>(365-1)*24*3600000){
			show_snackbar(null,'Select a shorter backtest period for the candle interval');
			return false;
		  	}
  		break;
  	case "day":
  		if(endDate-startDate>(365-1)*24*3600000*10){
			show_snackbar(null,'Select a shorter backtest period for the candle interval');
			return false;
		  	}
  		break;
  }
  return true;
}

function exportToCsv(filename, rows) {
		try{
			ga('send', {hitType: 'event', eventCategory: 'Download backtest result', eventAction: 'Download backtest result', eventLabel: 'Backtest page', eventValue: 1});
        }
        catch(e){

        }
        var processRow = function (row) {
            var finalVal = '';
            for (var j = 0; j < row.length; j++) {
                var innerValue = row[j] === null ? '' : row[j].toString();
                if (row[j] instanceof Date) {
                    innerValue = row[j].toLocaleString();
                };
                var result = innerValue.replace(/"/g, '""');
                if (result.search(/("|,|\n)/g) >= 0)
                    result = '"' + result + '"';
                if (j > 0)
                    finalVal += ',';
                if (j==0)
                	{
                		result_temp = result;
                		result = moment(result).format("DD MMM YYYY hh:mm:ss A");
                		if(result == "Invalid date")
                			result = result_temp;
                	}
                if(j==6 && row[j]!="Trigger Type")
                  {
                    if(row[j+1]!=undefined)
                      {
                        finalVal += '"' + row[j+1] + '"';
                        j++;
                      }
                  }
                else
                  finalVal += result;
            }
            return finalVal + '\n';
        };

        var csvFile = '';
        for (var i = 0; i < rows.length; i++) {
            csvFile += processRow(rows[i]);
        }

        var blob = new Blob([csvFile], { type: 'text/csv;charset=utf-8;' });
        if (navigator.msSaveBlob) { // IE 10+
            navigator.msSaveBlob(blob, filename);
        } else {
            var link = document.createElement("a");
            if (link.download !== undefined) { // feature detection
                // Browsers that support HTML5 download attribute
                var url = URL.createObjectURL(blob);
                link.setAttribute("href", url);
                link.setAttribute("download", filename);
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
        }
    }

function clear_plot(){
	// $("#metrics").find("tr:gt(0)").remove();
	// $("#trade_log").find("tr:gt(0)").remove();
	$(".charts").each(function(){$(this).hide()});
    $(".transactions_table").hide();
    $(".condition_not_met").hide();
    $(".low_capital").hide();
}

function refresh_result(algo_uuid,k,msg,seg,sym){
	backtest_result_response[k] = msg[k];
	data = msg[k];
	backtest_result_response[k]=data;
	var backtest_results_row = $("<div>", {id: k, "class": "backtest_results_row"});

	var backtest_results_left = $("<div>",{"class":"backtest_results_left"});
	var results_section = $("<div>",{"class":"results_section"}).append('<div class="chart_section" id="chart_section"><div class="chart_header"><div class="equity_section"><p class="company_name">'+sym+' <span class="exc_symbol">'+seg+'</span></p></div><div class="brokerage_section"><p data-tooltip-bottom="Adjusted for brokerage and other charges (does not include stamp duty and DP charges)">Brokerage&nbsp;&nbsp;&nbsp;<label class="switch"><input class="brokerage_toggle" id="'+k.replace('/','_--_').replace(/ /g,'_-_')+'" type="checkbox"><span class="slider"></span></label></p></div></div><div class="chart_body"><canvas id="'+k.replace('/','_--_').replace(/ /g,'_-_')+'pnl_chartContainer_new"></canvas></div></div>');
	//+data.win_count/(data.win_count+data.loss_count)+
	color = '#06d092';
	img_url = "/static/imgs/icon-arrow-up-green.png";
	if(data.final_pnl<0){
		color = '#ff4343';
		img_url = "/static/imgs/icon-arrow-down-red.png";
	}
	var pnl_section = $("<div>",{"class":"pnl_section", "id":"pnl_section"}).append('<div class="pnl"><p>P&L&nbsp;<span><img src="'+img_url+'">&nbsp;</span><span style="color:'+color+'">'+parseFloat(data.final_pnl).toFixed(2)+'&nbsp;</span><span style="color:'+color+'"">('+parseFloat(data.final_pnl/data.max_cap_used*100).toFixed(2)+'%)&nbsp;</span></p></div><div class="streak"><div class="streak_body"><div data-tooltip-top="'+data.win_count+"/"+(data.win_count+data.loss_count)+' winning trades" class="wins" style="width:'+data.win_count/(data.win_count+data.loss_count)*100+'%"></div><div class="losses" data-tooltip-top="'+data.loss_count+"/"+(data.win_count+data.loss_count)+' losing trades" style="width:'+data.loss_count/(data.win_count+data.loss_count)*100+'%"></div></div></div><div class="results_table"><table><!--<td>Alpha</td><td>0.079</td></tr><tr><td>Beta</td><td>0.597</td></tr>--><!--<tr><td>Volatility</td><td>'+parseFloat(data.volatility).toFixed(2)+'%</td></tr><tr><td>Sharpe Ratio</td><td>'+parseFloat(data.sharpe).toFixed(2)+'</td></tr>--><!--<tr><td>Sortino</td><td>'+parseFloat(data.volatility).toFixed(2)+'</td></tr>-->' +'<tr><td>Total number of signals</td><td>'+data.total_number_of_signals+'</td></tr>'+'<tr><td>Number of wins</td><td>'+data.win_count+'</td></tr>'+'<tr><td>Number of losses</td><td>'+data.loss_count+'</td></tr>'+'<tr><td>Winning streak</td><td>'+data.winning_streak+'</td></tr>'+'<tr><td>Losing streak</td><td>'+data.lossing_streak+'</td></tr>'+'<tr><td>Max gains</td><td>'+parseFloat(data.maximum_gain).toFixed(2)+'</td></tr>'+'<tr><td>Max loss</td><td>'+parseFloat(data.maximum_loss).toFixed(2)+'</td></tr>'+'<tr><td>Avg gain/winning trade</td><td>'+parseFloat(data.average_gain_per_winning_trade).toFixed(2)+'</td></tr>'+'<tr><td>Avg loss/losing trade</td><td>'+parseFloat(data.average_gain_per_losing_trade).toFixed(2)+'</td></tr>' +'<tr><td>Max Drawdown</td><td>'+parseFloat(data.max_draw).toFixed(2)+'%</td></tr></table></div>');
	
	results_section.append(pnl_section);

	backtest_results_left.append(results_section);

	var transactions_section = $('<div>',{"class":"transactions_section", "id":"transactions_section"}).append('<p>Transaction Details <span><img src="/static/imgs/new/transactions_dropdown.svg"></span></p>');

	backtest_results_left.append(transactions_section);

	var transactions_table = $("<div>",{"class":"transactions_table","style":"display:none;"});

	var trade_log = $("<table>",{}).append('<tr><th>Trigger date</th><th>Equity</th><th>Buy/Sell</th><th>Qty</th><th>Price</th><th>Cumulative P&L</th><th>Trigger type</th></tr>');
	var prev_pnl = 0;
	rounding = 2
	if (seg=='CDS-FUT')
		rounding = 4
	for(var i = 0; i <= data.trade_log.length - 1; i++){
		if(data.trade_log[i][3]!=0)
			{
			trade_row = '<tr>';
			date = new Date(data.trade_log[i][0]);
			// trade_row += '<td>'+dateFormat(date, "dS - mmmm - yyyy, h:MM:ss TT")+'</td>';
			// trade_row += '<td>'+dateFormat(date, "dd - mmm - yyyy, hh:MM:ss A")+'</td>';
			trade_row += '<td>'+moment(date).format("DD - MMM - YYYY, hh:mm:ss A")+'</td>';
			// trade_row += '<td>'+data.trade_log[i][1]+'</td>';
			trade_row += '<td>'+sym+' '+seg+'</td>';
			
			if (data.trade_log[i][2]=='BUY')
				trade_row += '<td class="buy_tag">'+data.trade_log[i][2]+'</td>'
			else
				trade_row += '<td class="sell_tag">'+data.trade_log[i][2]+'</td>'

			trade_row += '<td>'+data.trade_log[i][3]+'</td>'
			trade_row += '<td>'+parseFloat(data.trade_log[i][4]).toFixed(rounding)+'</td>'
			t_pnl = parseFloat(data.trade_log[i][5])
			if ( prev_pnl<t_pnl)
				trade_row += '<td class="profit">'+t_pnl.toFixed(2)+'</td>'
			else
				trade_row += '<td class="loss">'+t_pnl.toFixed(2)+'</td>'

			prev_pnl = t_pnl;
			trade_row += '<td>'+data.trade_log[i][7]+'</td>'
			trade_row += '</tr>';
			trade_log.append(trade_row);
		}
	}

	transactions_table.append(trade_log);

	backtest_results_left.append(transactions_table);
	// backtest_results_left complete

	var backtest_results_right = $("<div>",{"class":"backtest_results_right"});
	backtest_results_right.append('<div class="fundamentals_section" id="fundamentals_section"><table><caption>Stock Performance</caption><tr><td>Period High</td><td>'+parseFloat(data.period_high).toFixed(2)+'</td></tr><tr><td>Period Low</td><td>'+parseFloat(data.period_low).toFixed(2)+'</td></tr><tr><td>Period return</td><td>'+parseFloat(data.period_return).toFixed(2)+'%</td></tr><!--<tr><td>Period Volatility</td><td>10%</td></tr>--></table></div>');

	var actions_section = $("<div>",{"class":"actions_section"});
	transactions_table_label = [["Trigger date","Equity","Buy/Sell","Qty","Price","Cumulative P&L","Trigger Type"]];
	if(deployed_seg_sym.includes(seg+'_'+sym)){
		// actions_section.html('<table class="actions_buttons"><tr><td><button class="force_stop" onclick=\'force_stop(event,"'+deployed_seg_sym_deployment_uuid[seg+'_'+sym]+'")\'><span><img src="/static/imgs/icon-force-stop.png"></span>&nbsp;&nbsp;&nbsp;Stop</button></td></tr><tr><td><button class="download"><span><img src="/static/imgs/icon-download.png"></span>&nbsp;&nbsp;&nbsp;Download</button></td></tr></table><div class="social_buttons"><span><button><img src="/static/imgs/icon-linkedin.png"></button></span><span><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button><img src="/static/imgs/icon-facebook.png"></button></span><span><button><img src="/static/imgs/icon-twitter.png"></button></span></div>');
		actions_section.html('<table class="actions_buttons" id="actions_buttons"><tr><td><button class="deploy_disabled" data-tooltip-top="Select strategies to deploy" onclick=\'force_stop(event,"'+deployed_seg_sym_deployment_uuid[seg+'_'+sym]+'")\'><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button><input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" disabled></td></tr><tr><td><button class="download" data-tooltip-top="Download backtest trade details" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button><button class="share" data-tooltip-top="Get sharable link" onclick="generate_shareable_link(event,\''+algo_uuid+'\',\''+seg+'_'+sym+'\')"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button id="linkedin_'+seg+'_'+sym+'" onclick=\'on_share_input_select(event,"linkedin","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-linkedin.png"></button></span><span style="display:none;"><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button id="fb_'+seg+'_'+sym+'" onclick=\'on_share_input_select(event,"fb","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-facebook.png"></button></span><span><button id="twitter_'+seg+'_'+sym+'" onclick=\'on_share_input_select(event,"twitter","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-twitter.png"></button></span></div><div class="share_window"><input type="text" name="" onclick="on_share_input_select(event);"></div>');
	}
	else{
		actions_section.html('<table class="actions_buttons" id="actions_buttons"><tr><td><button class="deploy" id="deploy" onclick=\'deploy_algorithm_popup("'+algo_uuid+'","'+sym+'","'+seg+'")\'"><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button><input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" onclick="select_any(event,$(this))"></td></tr><tr><td><button class="download" data-tooltip-top="Download backtest trade details" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button><button class="share" data-tooltip-top="Get sharable link" onclick="generate_shareable_link(event,\''+algo_uuid+'\',\''+seg+'_'+sym+'\')"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button id="linkedin_'+seg+'_'+sym+'" onclick=\'on_share_input_select(event,"linkedin","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-linkedin.png"></button></span><span style="display:none;"><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button id="fb_'+seg+'_'+sym+'" onclick=\'on_share_input_select(event,"fb","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-facebook.png"></button></span><span><button id="twitter_'+seg+'_'+sym+'" onclick=\'on_share_input_select(event,"twitter","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-twitter.png"></button></span></div><div class="share_window"><input type="text" name="" onclick="on_share_input_select(event);"></div>');
	}

	backtest_results_right.append(actions_section);
	// backtest_results_right complete

	backtest_results_row.append(backtest_results_left);
	backtest_results_row.append(backtest_results_right);
	
	$('.backtest_results_body').append(backtest_results_row);

	transactions_section.click(function(){
		// alert($(this).attr("class"));
		$(this).toggleClass("expandable-color");
		$(this).parentsUntil(".backtest_results_row").find(".transactions_table").slideToggle();
		if($(this).find("img").attr("src") == "/static/imgs/new/transactions_dropdown.svg"){
		$(this).find("img").attr("src", "/static/imgs/new/transactions_dropup.svg");	
		}
		else{
		$(this).find("img").attr("src", "/static/imgs/new/transactions_dropdown.svg");
		}
	});

	// var ctx = document.getElementById(k.replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").getContext('2d');
	$('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").replaceWith('<canvas id="'+k.replace('/','_--_').replace(/ /g,'_-_')+'pnl_chartContainer_new"></canvas>');
	var ctx = document.getElementById(k.replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").getContext('2d');
	
	var pnl_chartContainer_new = new Chart(ctx,{
		type: 'line',
		scaleSteps : 4,
    	data: {
    		// labels: ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
			datasets: [{
			    label: 'P&L',
			    data: processListToXYList(data.pnl),
			    backgroundColor:'rgba(255,255,255,0)',
			    borderColor: '#2288ff',
			    borderWidth: 2,
			    lineTension: 0,
			    // pointStyle: 'star',
			    // point: { radius: 0 },
			    hoverRadius: 5
			}]
    	},
    	options: {
    		scales: {
            yAxes: [{
            	gridLines: {
					color: '#ecf0f1',
					zeroLineBorderDash: [5, 5],
					zeroLineColor: '#ecf0f1'
						},
                ticks: {
                	fontColor: '#9ea1a4',
                    beginAtZero:true,
                    // maxTicksLimit:1
                    // ticks: {min: 0, max:4}
                }
            }],
            	xAxes: [{
		        type: 'time',
		        position: 'bottom',
		         gridLines: {
						display: false,
						color: '#ecf0f1',
						zeroLineBorderDash: [5, 5],
						zeroLineColor: '#ecf0f1'
				},
				ticks: {
					fontColor: '#9ea1a4'
				},
		        time: {
		          displayFormats: {
		          	// 'millisecond': 'MMM DD',
		           //  'second': 'MMM DD',
		           //  'minute': 'MMM DD',
		           //  'hour': 'MMM DD',
		           //  'day': 'MMM DD',
		           //  'week': 'MMM DD',
		           //  'month': 'MMM DD',
		           //  'quarter': 'MMM DD',
		            'year': 'YY MMM DD',
		          }
		        }
		      }],
			},
			legend: {
			    display: false,
			},
			// title: {
			//     display: true,
			//     text: 'P&L Performance',
			//     fontColor: '#333333',
			//     fontFamily: '"open_sansregular","AvenirNextLTPro",Arial,Helvetica,sans-serif',
			//     fontStyle:'bold',
			//     position: 'top',
			//     fontSize: 16
			// },
			// legend: {
			//     display: true,
			//     labels: {
			//         fontColor: '#666666'
			//     }
			// },
			elements: { point: { radius: 0 } },	
		}
	});
	$('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+' .brokerage_toggle:checkbox').on('change',function(e){
		broker_toggle(e);
	});
}

function refresh_result_sequential(algo_uuid,k,msg,seg,sym){
	backtest_result_response[k] = msg[k];
	data = msg[k];
	backtest_result_response[k]=data;
	// k = k.replace('&','.');
	var backtest_results_row = $("#"+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_'));

	var backtest_results_left = $("<div>",{"class":"backtest_results_left"});
	var results_section = $("<div>",{"class":"results_section"}).append('<div class="chart_section" id="chart_section"><div class="chart_header"><div class="equity_section"><p class="company_name">'+sym+' <span class="exc_symbol">'+seg+'</span></p></div><div class="brokerage_section"><p data-tooltip-bottom="Adjusted for brokerage and other charges (does not include stamp duty and DP charges)">Brokerage&nbsp;&nbsp;&nbsp;<label class="switch"><input class="brokerage_toggle" id="'+k.replace('/','_--_').replace(/ /g,'_-_')+'" type="checkbox"><span class="slider"></span></label></p></div></div><div class="chart_body"><canvas id="'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+'pnl_chartContainer_new"></canvas></div></div>');
	//+data.win_count/(data.win_count+data.loss_count)+
	color = '#06d092';
	img_url = "/static/imgs/icon-arrow-up-green.png";
	if(data.final_pnl<0){
		color = '#ff4343';
		img_url = "/static/imgs/icon-arrow-down-red.png";
	}
	var pnl_section = $("<div>",{"class":"pnl_section", "id":"pnl_section"}).append('<div class="pnl"><p>P&L&nbsp;<span><img src="'+img_url+'">&nbsp;</span><span style="color:'+color+'">'+parseFloat(data.final_pnl).toFixed(2)+'&nbsp;</span><span style="color:'+color+'"">('+parseFloat(data.final_pnl/data.max_cap_used*100).toFixed(2)+'%)&nbsp;</span></p></div><div class="streak"><div class="streak_body"><div data-tooltip-top="'+data.win_count+"/"+(data.win_count+data.loss_count)+' winning trades" class="wins" style="width:'+data.win_count/(data.win_count+data.loss_count)*100+'%"></div><div class="losses" data-tooltip-top="'+data.loss_count+"/"+(data.win_count+data.loss_count)+' losing trades" style="width:'+data.loss_count/(data.win_count+data.loss_count)*100+'%"></div></div></div><div class="results_table"><table><!--<td>Alpha</td><td>0.079</td></tr><tr><td>Beta</td><td>0.597</td></tr>--><!--<tr><td>Volatility</td><td>'+parseFloat(data.volatility).toFixed(2)+'%</td></tr><tr><td>Sharpe Ratio</td><td>'+parseFloat(data.sharpe).toFixed(2)+'</td></tr>--><!--<tr><td>Sortino</td><td>'+parseFloat(data.volatility).toFixed(2)+'</td></tr>-->' +'<tr><td>Total number of signals</td><td>'+data.total_number_of_signals+'</td></tr>'+'<tr><td>Number of wins</td><td>'+data.win_count+'</td></tr>'+'<tr><td>Number of losses</td><td>'+data.loss_count+'</td></tr>'+'<tr><td>Winning streak</td><td>'+data.winning_streak+'</td></tr>'+'<tr><td>Losing streak</td><td>'+data.lossing_streak+'</td></tr>'+'<tr><td>Max gains</td><td>'+parseFloat(data.maximum_gain).toFixed(2)+'</td></tr>'+'<tr><td>Max loss</td><td>'+parseFloat(data.maximum_loss).toFixed(2)+'</td></tr>'+'<tr><td>Avg gain/winning trade</td><td>'+parseFloat(data.average_gain_per_winning_trade).toFixed(2)+'</td></tr>'+'<tr><td>Avg loss/losing trade</td><td>'+parseFloat(data.average_gain_per_losing_trade).toFixed(2)+'</td></tr>' +'<tr><td>Max Drawdown</td><td>'+parseFloat(data.max_draw).toFixed(2)+'%</td></tr></table></div>');
	results_section.append(pnl_section);

	backtest_results_left.append(results_section);

	var transactions_section = $('<div>',{"class":"transactions_section", "id":"transactions_section"}).append('<p>Transaction Details <span><img src="/static/imgs/new/transactions_dropdown.svg"></span></p>');

	backtest_results_left.append(transactions_section);

	var transactions_table = $("<div>",{"class":"transactions_table","style":"display:none;"});

	var trade_log = $("<table>",{}).append('<tr><th>Trigger date</th><th>Equity</th><th>Buy/Sell</th><th>Qty</th><th>Price</th><th>Cumulative P&L</th><th>Trigger type</th></tr>');
	var prev_pnl = 0;
	rounding = 2
	if (seg=='CDS-FUT')
		rounding = 4
	for(var i = 0; i <= data.trade_log.length - 1; i++){
		if(data.trade_log[i][3]!=0)
			{
			trade_row = '<tr>';
			date = new Date(data.trade_log[i][0]);
			// trade_row += '<td>'+dateFormat(date, "dS - mmmm - yyyy, h:MM:ss TT")+'</td>';
			// trade_row += '<td>'+dateFormat(date, "dd - mmm - yyyy, hh:MM:ss A")+'</td>';
			trade_row += '<td>'+moment(date).format("DD - MMM - YYYY, hh:mm:ss A")+'</td>';
			// trade_row += '<td>'+data.trade_log[i][1]+'</td>';
			trade_row += '<td>'+sym+' '+seg+'</td>';
			
			if (data.trade_log[i][2]=='BUY')
				trade_row += '<td class="buy_tag">'+data.trade_log[i][2]+'</td>'
			else
				trade_row += '<td class="sell_tag">'+data.trade_log[i][2]+'</td>'

			trade_row += '<td>'+data.trade_log[i][3]+'</td>'
			trade_row += '<td>'+parseFloat(data.trade_log[i][4]).toFixed(rounding)+'</td>'
			t_pnl = parseFloat(data.trade_log[i][5])
			if ( prev_pnl<=t_pnl)
				trade_row += '<td class="profit">'+t_pnl.toFixed(2)+'</td>'
			else
				trade_row += '<td class="loss">'+t_pnl.toFixed(2)+'</td>'
			prev_pnl = t_pnl;

			trade_row += '<td>'+data.trade_log[i][7]+'</td>'
			trade_row += '</tr>';
			trade_log.append(trade_row);
		}
	}

	transactions_table.append(trade_log);

	backtest_results_left.append(transactions_table);
	// backtest_results_left complete

	var backtest_results_right = $("<div>",{"class":"backtest_results_right"});
	backtest_results_right.append('<div class="fundamentals_section" id="fundamentals_section"><table><caption>Stock Performance</caption><tr><td>Period High</td><td>'+parseFloat(data.period_high).toFixed(2)+'</td></tr><tr><td>Period Low</td><td>'+parseFloat(data.period_low).toFixed(2)+'</td></tr><tr><td>Period return</td><td>'+parseFloat(data.period_return).toFixed(2)+'%</td></tr><!--<tr><td>Period Volatility</td><td>10%</td></tr>--></table></div>');

	var actions_section = $("<div>",{"class":"actions_section"});
  transactions_table_label = [["Trigger date","Equity","Buy/Sell","Qty","Price","Cumulative P&L","Trigger Type"]];
	if(deployed_seg_sym.includes(seg+'_'+sym)){
		// actions_section.html('<table class="actions_buttons"><tr><td><button class="force_stop" onclick=\'force_stop(event,"'+deployed_seg_sym_deployment_uuid[seg+'_'+sym]+'")\'><span><img src="/static/imgs/icon-force-stop.png"></span>&nbsp;&nbsp;&nbsp;Stop</button></td></tr><tr><td><button class="download"><span><img src="/static/imgs/icon-download.png"></span>&nbsp;&nbsp;&nbsp;Download</button></td></tr></table><div class="social_buttons"><span><button><img src="/static/imgs/icon-linkedin.png"></button></span><span><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button><img src="/static/imgs/icon-facebook.png"></button></span><span><button><img src="/static/imgs/icon-twitter.png"></button></span></div>');
		actions_section.html('<table class="actions_buttons" id="actions_buttons"><tr><td><button class="deploy_disabled" data-tooltip-top="Select strategies to deploy" onclick=\'force_stop(event,"'+deployed_seg_sym_deployment_uuid[seg+'_'+sym]+'")\'><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button><input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" disabled></td></tr><tr><td><button data-tooltip-top="Download backtest trade details" class="download" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button><button class="share" data-tooltip-top="Get sharable link" onclick="generate_shareable_link(event,\''+algo_uuid+'\',\''+seg+'_'+sym+'\')"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button id="linkedin_'+seg+'_'+sym+'" onclick=\'on_share_input_select(event,"linkedin","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-linkedin.png"></button></span><span style="display:none;"><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button id="fb_'+seg+'_'+sym+'" onclick=\'on_share_input_select(event,"fb","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-facebook.png"></button></span><span><button id="twitter_'+seg+'_'+sym+' onclick=\'on_share_input_select(event,"twitter","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-twitter.png"></button></span></div><div class="share_window"><input type="text" name="" onclick="on_share_input_select(event);"></div>');
	}
	else{
		actions_section.html('<table class="actions_buttons" id="actions_buttons"><tr><td><button class="deploy" id="deploy" onclick=\'deploy_algorithm_popup("'+algo_uuid+'","'+sym+'","'+seg+'")\'><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button><input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" onclick="select_any(event,$(this))"></td></tr><tr><td><button data-tooltip-top="Download backtest trade details" class="download" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button><button class="share" data-tooltip-top="Get sharable link" onclick="generate_shareable_link(event,\''+algo_uuid+'\',\''+seg+'_'+sym+'\')"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button id="linkedin_'+seg+'_'+sym+'" onclick=\'on_share_input_select(event,"linkedin","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-linkedin.png"></button></span><span style="display:none;"><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button id="fb_'+seg+'_'+sym+'" onclick=\'on_share_input_select(event,"fb","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-facebook.png"></button></span><span><button id="twitter_'+seg+'_'+sym+'" onclick=\'on_share_input_select(event,"twitter","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-twitter.png"></button></span></div><div class="share_window"><input type="text" name="" onclick="on_share_input_select(event);"></div>');
	}

	backtest_results_right.append(actions_section);
	// backtest_results_right complete
	backtest_results_row.html('');
	backtest_results_row.append(backtest_results_left);
	backtest_results_row.append(backtest_results_right);
	
	// $('.backtest_results_body').append(backtest_results_row);

	transactions_section.click(function(){
		// alert($(this).attr("class"));
		$(this).toggleClass("expandable-color");
		$(this).parentsUntil(".backtest_results_row").find(".transactions_table").slideToggle();
		if($(this).find("img").attr("src") == "/static/new/transactions_dropdown.svg"){
		$(this).find("img").attr("src", "/static/imgs/new/transactions_dropup.svg");	
		}
		else{
		$(this).find("img").attr("src", "/static/imgs/new/transactions_dropdown.svg");
		}
	});

	// var ctx = document.getElementById(k.replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").getContext('2d');
	$('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").replaceWith('<canvas id="'+k.replace('/','_--_').replace(/ /g,'_-_')+'pnl_chartContainer_new"></canvas>');
	var ctx = document.getElementById(k.replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").getContext('2d');
	
	var pnl_chartContainer_new = new Chart(ctx,{
		type: 'line',
		scaleSteps : 4,
    	data: {
    		// labels: ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
			datasets: [{
			    label: 'P&L',
			    data: processListToXYList(data.pnl),
			    backgroundColor:'rgba(255,255,255,0)',
			    borderColor: '#2288ff',
			    borderWidth: 2,
			    lineTension: 0,
			    // pointStyle: 'star',
			    // point: { radius: 0 },
			    hoverRadius: 5
			}]
    	},
    	options: {
    		scales: {
            yAxes: [{
            	gridLines: {
					color: '#ecf0f1',
					zeroLineBorderDash: [5, 5],
					zeroLineColor: '#ecf0f1'
						},
                ticks: {
                	fontColor: '#9ea1a4',
                    beginAtZero:true,
                    // maxTicksLimit:1
                    // ticks: {min: 0, max:4}
                }
            }],
            	xAxes: [{
		        type: 'time',
		        position: 'bottom',
		         gridLines: {
						display: false,
						color: '#ecf0f1',
						zeroLineBorderDash: [5, 5],
						zeroLineColor: '#ecf0f1'
				},
				ticks: {
					fontColor: '#9ea1a4'
				},
		        time: {
		          displayFormats: {
		          	// 'millisecond': 'MMM DD',
		           //  'second': 'MMM DD',
		           //  'minute': 'MMM DD',
		           //  'hour': 'MMM DD',
		           //  'day': 'MMM DD',
		           //  'week': 'MMM DD',
		           //  'month': 'MMM DD',
		           //  'quarter': 'MMM DD',
		            'year': 'YY MMM DD',
		          }
		        }
		      }],
			},
			legend: {
			    display: false,
			},
			// title: {
			//     display: true,
			//     text: 'P&L Performance',
			//     fontColor: '#333333',
			//     fontFamily: '"open_sansregular","AvenirNextLTPro",Arial,Helvetica,sans-serif',
			//     fontStyle:'bold',
			//     position: 'top',
			//     fontSize: 16
			// },
			// legend: {
			//     display: true,
			//     labels: {
			//         fontColor: '#666666'
			//     }
			// },
			elements: { point: { radius: 0 } },	
		}
	});
	$('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+' .brokerage_toggle:checkbox').on('change',function(e){
		broker_toggle(e);
	});
	fetch_billing_status();
}

function refresh_error(k,msg){
	data = msg[k];
	try{
		[seg,sym] = k.split("_");
		if(k!='runtime' && k!='updated_time'){
			var backtest_results_row = $("<div>", {id: k, "class": "backtest_results_row"});
			var backtest_results_left = $("<div>",{"class":"backtest_results_left"});
			var results_section = $("<div>",{"class":"results_section"}).append('<div class="chart_section"><div class="chart_header"><div class="equity_section"><p class="company_name">'+sym+' <span class="exc_symbol">'+seg+'</span></p></div><div class="brokerage_section"><p></p></div></div><div class="chart_body"><div id="'+k.replace('/','_--_').replace(/ /g,'_-_')+'pnl_chartContainer_new"><p></p></div></div></div>');
			backtest_results_left.append(results_section);
			backtest_results_row.append(backtest_results_left);
			$('.backtest_results_body').append(backtest_results_row);
			$("#"+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").html(data['error_msg']);
		}
	}
	catch(err){
		return;
	}
}
function refresh_error_sequential(seg_sym,k,msg){
	data = msg[k];
	try{
		[seg,sym] = seg_sym.split("_");
		if(k!='runtime' && k!='updated_time'){
			var backtest_results_row = $("#"+seg_sym.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_'));
			var backtest_results_left = $("<div>",{"class":"backtest_results_left"});
			var results_section = $("<div>",{"class":"results_section"}).append('<div class="chart_section"><div class="chart_header"><div class="equity_section"><p class="company_name">'+sym+' <span class="exc_symbol">'+seg+'</span></p></div><div class="brokerage_section"><p></p></div></div><div class="chart_body"><div id="'+k.replace('/','_--_').replace(/ /g,'_-_')+'pnl_chartContainer_new"><p></p></div></div></div>');
			backtest_results_row.html('');
			backtest_results_left.append(results_section);
			backtest_results_row.append(backtest_results_left);
			// $('.backtest_results_body').append(backtest_results_row);
			$("#"+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").html(data['error_msg']);
		}
	}
	catch(err){
		return;
	}
}

function on_share_input_select2(e,platform,algo_uuid,id){
	// var t = e.target;
	// t.focus();
	// t.setSelectionRange(0, t.value.length);
	// t.select();
	// var x = document.execCommand ("copy", false, null);
	// if(x==true){
	// 	show_snackbar(null,'Link copied to clipboard','success',callback=null,show_time=3000);
	// }
	if($('#'+platform+'_'+id.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')).data('sharable_link')==undefined){
		generate_shareable_link2(event,algo_uuid,id,platform);
		return;
	}
	url =  "https://" + 'streak.tech'+'/backtest_shared/'+$('#'+platform+'_'+id.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')).data('sharable_link');
	switch(platform){
		case 'fb':
			share_to_facebook(url,"StreakTech");
			break;
		case 'twitter':
			share_to_twitter(url,"StreakTech");
			break;
		case 'linkedin':
			share_to_linkedin(url,"StreakTech");
			break;
	}
}

function on_share_input_select(e,platform,id){
	// var t = e.target;
	// t.focus();
	// t.setSelectionRange(0, t.value.length);
	// t.select();
	// var x = document.execCommand ("copy", false, null);
	// if(x==true){
	// 	show_snackbar(null,'Link copied to clipboard','success',callback=null,show_time=3000);
	// }
	url =  "https://" + 'streak.tech'+'/backtest_shared/'+$('#'+platform+'_'+id.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')).data('sharable_link');
	switch(platform){
		case 'fb':
			share_to_facebook(url,"StreakTech");
			break;
		case 'twitter':
			share_to_twitter(url,"StreakTech");
			break;
		case 'linkedin':
			share_to_linkedin(url,"StreakTech");
			break;
	}
}

// function copyToClipboardFF(text) {
//   window.prompt ("Copy to clipboard: Ctrl C, Enter", text);
// }

// function copyToClipboard() {
//   var success   = true,
//       range     = document.createRange(),
//       selection;

//   // For IE.
//   if (window.clipboardData) {
//     window.clipboardData.setData("Text", input.val());        
//   } else {
//     // Create a temporary element off screen.
//     var tmpElem = $('<div>');
//     tmpElem.css({
//       position: "absolute",
//       left:     "-1000px",
//       top:      "-1000px",
//     });
//     // Add the input value to the temp element.
//     tmpElem.text(input.val());
//     $("body").append(tmpElem);
//     // Select temp element.
//     range.selectNodeContents(tmpElem.get(0));
//     selection = window.getSelection ();
//     selection.removeAllRanges ();
//     selection.addRange (range);
//     // Lets copy.
//     try { 
//       success = document.execCommand ("copy", false, null);
//     }
//     catch (e) {
//       copyToClipboardFF(input.val());
//     }
//     if (success) {
//       alert ("The text is on the clipboard, try to paste it!");
//       // remove temp element.
//       tmpElem.remove();
//     }
//   }
// }

function refresh_error_sequential2(seg_sym,k,msg){
	// data = msg[k];
	// error_msg = msg["error_msg"];
	error_msg = msg;
	if(error_msg=="Wrong inputs")
		error_msg = 'Unable to fetch data for the given backtest period, kindly try again with smaller period or after some time';
	try{
			[seg,sym] = seg_sym.split("_");
		// if(k!='runtime' && k!='updated_time'){
			var backtest_results_row = $("#"+seg_sym.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_'));
			// backtest_results_row.addClass('empty_backtest_results_row');
			// var backtest_results_left = $("<div>",{"class":"backtest_results_left"});
			backtest_results_row.html('<div class="empty_backtest_results_row" id="empty_backtest_results_row"> <div class="backtest_results_left"> <div class="results_section"> <div class="chart_section"> <div class="chart_header"> <div class="equity_section"> <p class="company_name">'+sym+'&nbsp;<span class="exc_symbol">'+seg+'</span></p> <!-- <p >: CANBK</p> --> </div> <div class="brokerage_section"> <p> </p> </div> </div> <div class="chart_body"> <p class="backtest_row_error_message_display">'+error_msg+'</p> </div> </div> <div class="pnl_section"> <div class="pnl"> <p>P&L&nbsp;<span>(N.A)&nbsp;</span><span>(N.A)&nbsp;</span></p> </div> <div class="streak"> <div class="streak_body"> <div class="wins"></div> <div class="losses"></div> </div> </div> <div class="results_table"> <table> <tr><td>Total number of signals</td><td>- / -</td></tr><tr><td>Number of wins</td><td>- / -</td></tr><tr><td>Number of losses</td><td>- / -</td></tr><tr><td>Winning streak</td><td>- / -</td></tr><tr><td>Losing streak</td><td>- / -</td></tr><tr><td>Max gains</td><td>- / -</td></tr><tr><td>Max loss</td><td>- / -</td></tr><tr><td>Avg gain/winning trade</td><td>- / -</td></tr><tr><td>Avg loss/losing trade</td><td>- / -</td></tr><tr><td>Max Drawdown</td><td>- / -</td></tr> </table> </div> </div> </div> <div class="empty_transactions_section"> <p>Transaction Details <span><img src="/static/imgs/new/transactions_dropdown.svg"></span></p> </div> </div> <div class="backtest_results_right"> <div class="fundamentals_section"> <table> <caption>Stock Performance</caption> <tr><td>Period High</td><td>- / -</td></tr><tr><td>Period Low</td><td>- / -</td></tr><tr><td>Period return</td><td>- / -</td></tr> </table> </div> <div class="actions_section"> <table class="actions_buttons"> <tr> <td> <button class="deploy"><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button> </td> </tr> <tr> <td> <button class="download"><span><img src="/static/imgs/icon-new-download.png"></span></button> <button class="empty_share"><span><img src="/static/imgs/icon-share.png"></span></button> </td> </tr> </table> <div class="social_buttons"> <span><button style="display:none"><img src="/static/imgs/icon-linkedin.png"></button></span> <span style="display:none;"><button><img src="/static/imgs/icon-whatsapp.png"></button></span> <span><button><img src="/static/imgs/icon-facebook.png"></button></span> <span><button><img src="/static/imgs/icon-twitter.png"></button></span> </div> </div> </div> </div>');
		// }
	}
	catch(err){
		return;
	}
}

function disable_edit(){
	var algo_uuid = $("#au_cc").val();
	var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
	$.get('/is_algorithm_deployed',{'csrfmiddlewaretoken':csrfmiddlewaretoken,
        'algo_uuid':algo_uuid
    }).done(function (data){
        // if algo not deployed
        if(data['status']=='success'){
        	// $('.edit_strategy').removeClass("action_buttons_disabled");
        	// $('.edit_strategy').find('img').attr("src","/static/imgs/icon-edit.png");
        	// $(".edit_strategy").attr("data-tooltip-bottom", "Edit algo");
        	$(".edit_algo_summary").html("<img id='edit_strategy' onclick='edit_algorithm();' src='/static/imgs/new/create.svg'>");
        }
		else if(data['deployed']){
			// $('.edit_strategy').addClass("action_buttons_disabled");
			// $('.edit_strategy').find('img').attr("src","/static/imgs/icon-edit-disabled.png");
			// $(".edit_strategy").attr("data-tooltip-bottom", "Deployed algo cannot be edited");
			$(".edit_algo_summary").html("<img id='edit_strategy' onclick='show_snackbar(null,\"Cannot edit deployed algo\");' src='/static/imgs/new/create.svg'>");
        }
        // alert('Algo delete_button')

            // if some error 
            // alert('Some specific error, like a script is live, etc')
        }).fail(
            function(){
                alert('Some specific error, like a script is live, etc');
            });
}
function edit_algorithm(){
	var algo_uuid = $("#au_cc").val();
	var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    $.get('/is_algorithm_deployed',{'csrfmiddlewaretoken':csrfmiddlewaretoken,
        'algo_uuid':algo_uuid
    }).done(function (data){
        // if algo not deployed
        if(data['status']=='success'){
        		try{
        			ga('send', {hitType: 'event', eventCategory: 'Edit algo', eventAction: 'Edit algo initiated', eventLabel: 'Backtest page'});
        		}
		        catch(e){

		        }
                window.location='/algorithm?algo_uuid='+data['algo_uuid']
            }
        // alert('Algo delete_button')

            // if some error 
            // alert('Some specific error, like a script is live, etc')
        }).fail(
            function(){
                alert('Some specific error, like a script is live, etc');
            });
}
function refresh_result_blank(algo_uuid,k,seg,sym){

	var backtest_results_row = $('<div>', {id: k, "class": "backtest_results_row"});
	
	$('.backtest_results_body').append(backtest_results_row);

	// $("#"+k).html('<div style="margin: auto;"><img src="/static/imgs/backtest-loading-gif.gif"><p>Generating Backtest Results of '+[sym,seg].join(' ')+'&nbsp;&nbsp;&nbsp;<!--<span><!--100%--></span>--></p><div id="myProgress"><div id="myBar"></div></div></div>');
	$('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')).html('<div class="empty_backtest_results_row" id="loading_backtest_results_row"> <div class="backtest_results_left"> <div class="results_section"> <div class="chart_section"> <div class="chart_header"> <div class="equity_section"> <p class="company_name">'+sym+'&nbsp;<span class="exc_symbol">'+seg+'</span></p> <!-- <p >: CANBK</p> --> </div> </div> <div class="chart_body"> <div class="backtest_row_loader"><div id="myBtProgress"><div id="myBtBar"></div></div> <p>Generating Backtest Results&nbsp;&nbsp;&nbsp;<span><!--100%--></span></p> </div> </div> </div> <div class="pnl_section"> <div class="pnl"> <p>P&L&nbsp;<span>(N.A)&nbsp;</span><span>(N.A)&nbsp;</span></p> </div> <div class="streak"> <div class="streak_body"> <div class="wins"></div> <div class="losses"></div> </div> </div> <div class="results_table"> <table> <tr><td>Total number of signals</td><td>- / -</td></tr><tr><td>Number of wins</td><td>- / -</td></tr><tr><td>Number of losses</td><td>- / -</td></tr><tr><td>Winning streak</td><td>- / -</td></tr><tr><td>Losing streak</td><td>- / -</td></tr><tr><td>Max gains</td><td>- / -</td></tr><tr><td>Max loss</td><td>- / -</td></tr><tr><td>Avg gain/winning trade</td><td>- / -</td></tr><tr><td>Avg loss/losing trade</td><td>- / -</td></tr><tr><td>Max Drawdown</td><td>- / -</td></tr> </table> </div> </div> </div> <div class="empty_transactions_section"> <p>Transaction Details <span><img src="/static/imgs/new/transactions_dropdown.svg"></span></p> </div> </div> <div class="backtest_results_right"> <div class="fundamentals_section"> <table> <caption>Stock Performance</caption> <tr><td>Period High</td><td>- / -</td></tr><tr><td>Period Low</td><td>- / -</td></tr><tr><td>Period return</td><td>- / -</td></tr> </table> </div> <div class="actions_section"> <table class="actions_buttons"> <tr> <td> <button class="deploy"><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button> </td> </tr> <tr> <td> <button class="download"><span><img src="/static/imgs/icon-new-download.png"></span></button> <button class="empty_share"><span><img src="/static/imgs/icon-share.png"></span></button> </td> </tr> </table> <div class="social_buttons"> <span><button><img src="/static/imgs/icon-linkedin.png"></button></span> <span style="display:none;"><button><img src="/static/imgs/icon-whatsapp.png"></button></span> <span><button><img src="/static/imgs/icon-facebook.png"></button></span> <span><button><img src="/static/imgs/icon-twitter.png"></button></span> </div> </div> </div> </div>')
}

function run_backtest_sequential() {
	run_backtest_multi();
	return;
	if(Object.keys(equity_added).length === 0)
		return;
	$('.empty_backtest_results_body').hide();
	var algo_uuid = $("#au_cc").val();
	var algo_name = $("#an_cc").val();
	var algo_desc = $("#ad_cc").val();
	// var from_datepicker = $("#from_datepicker").val();
	// var to_datepicker = $("#to_datepicker").val();
	var entry_str = $("#et_cc").val();
	var exit_logic = $("#ex_cc").val();
	var position_type = $("#pt_cc").val();

	var user_uuid = $("#ui_cc").val();

	var from_datepicker = null;
	var to_datepicker = null;
	var initial_capital = $("#ip_initial_capital").val();
	var quantity = $("#ip_quantity").val();
	var stop_loss = $("#ip_stoploss").val();
	var take_profit = $("#ip_takeprofit").val();
	var holding_type = holding_type_mapping[$("#ip_holding_type").val()];
	var interval = interval_mapping[$("#ip_interval").val()];

	// advanced parameters
	// var holding_type = adv_holding_type;
	var chart_type = adv_chart_type;
	var trading_start_time = adv_trading_start_time;
	var trading_stop_time = adv_trading_stop_time;
	var trade_time_given = "False";
	if(trading_stop_time!=''&&trading_start_time!=''&&trading_stop_time>trading_start_time){
	trade_time_given = "True";
	}
	//----------------------//

	// [from_datepicker,to_datepicker] = $('#date_range').val().split(' – ');
	[from_datepicker,to_datepicker] = [elements.start_input.value,elements.stop_input.value]
	
	if (holding_type=='MIS' && interval=='day') 
	{
		show_snackbar(null,'Cannot run MIS with day candle interval');
		return;
	}

	holding_type_latest = holding_type;
	
	var commission = 0;//$("#commission option:selected").val();
	symbols = [];
	for(sym in equity_added){
		seg = equity_added[sym];
		symbols.push([seg.split('_')[0],sym]);
	}
	if (back_test_input_valid(algo_uuid,initial_capital,
	            from_datepicker,
	            to_datepicker,
	            commission,symbols,stop_loss,take_profit,quantity,interval)!=true)
	{
		// alert error
		return;
	}
	
	$('.run_backtest').attr('style',"background-color: #c7c7c7 !important;cursor: no-drop !important");
	$('.run_backtest').attr('onclick',';');
	$(".run_backtest").html("<img src='/static/imgs/button-loading-rect.gif' id='button_loading'>");
	var ga_eq = JSON.stringify(equity_added).split(",").length;
	$.get('/get_subscription_limit',{
    }).done(function (data){
    	if(data['status']=="success")
    	{
    		if(data['valid']==true){
    			if(data['backtest']>0){
    				var max_count = 0
					$('.backtest_results_body').html('');

					for(sym in equity_added){
						seg = equity_added[sym];
            sym = sym.split('_')[0]
						refresh_result_blank(algo_uuid,seg+'_'+sym,seg,sym);
						max_count += 1;
					}

					var count = 0;
					// perform a post call to the view , passing the params
					// loop_backtest: 
					var params = {
						'algo_uuid':algo_uuid,//.hexDecode(),
						'algo_name':algo_name,//.hexDecode(),
						'algo_desc':algo_desc,//.hexDecode(),
						'user_uuid':user_uuid,
						'initial_capital':initial_capital,
						'action_str':entry_str,//.hexDecode(),
						'action_str_exit':exit_logic,
						'action_type':position_type.toUpperCase(),
						'quantity':quantity,
						'symbols':[symbols[count]],
						'stop_loss':stop_loss,
						'take_profit':take_profit,
						'dt_start':from_datepicker,
						'dt_stop':to_datepicker,
						'min_candle_freq':min_candle_freq,
						'time_frame':interval,
						'commission':commission,
						// advanced parameters
						'holding_type':holding_type,
						'chart_type':chart_type,
						'trade_time_given':trade_time_given,
						'trading_start_time':trading_start_time,
						'trading_stop_time':trading_stop_time
					};
					bt_url = "";
					lmda_vs_ec2_select();
					refresh_algo_summary()
					switch(url_selector){
						case 1: bt_url = bt_url2;
								break;
						case 2: bt_url = bt_url2;
								break;
						default:bt_url = bt_url2;
					}
					var settings = {
					  "async": true,
					  "crossDomain": true,
					  "url": bt_url,
					  "method": "POST",
					  "headers": {
					  },
					  "beforeSend": function() {
			               myBtBarLoader(symbols[count][0]+'_'+symbols[count][1],bt_loading_time);
			          },
					  // "data": "{\"action_str\":\"5 min sma crosses 10 min sma\",\"action_type\":\"BUY\",\"symbols\":[[\"NSE\",\"CANBK\"],[\"NSE\",\"ICICIBANK\"]],\n         \"quantity\":1,\"initial_capital\":1000000,\"dt_start\":\"09/11/2017\",\"dt_stop\":\"09/12/2017\",\"time_frame\":\"min\",\"commission\":40,\n         \"take_profit\":1,\"stop_loss\":0.5\n         }",
					  "data":JSON.stringify(params),
					  "timeout": 200000,//40 sec timeout
					}
					// myBtBarLoader(k,1000);
					$.ajax(settings).done(function(msg){
						try {
							if(msg['status']=='error'){
								k = symbols[count][0]+'_'+symbols[count][1];
								refresh_error_sequential2(symbols[count][0]+'_'+symbols[count][1],k,msg['error_msg']);
							}
							else{
								// var msg = JSON.parse(msg);
								if(Object.keys(msg).length>0) // if the response has data clear the result rows
									// $('.backtest_results_body').html('');
								for(var k in msg)
								{
									data = msg[k];
									if(data['error_msg']!=undefined){
										refresh_error_sequential2(symbols[count][0]+'_'+symbols[count][1],k,data['error_msg'])
									}else{
										[seg,sym] = [null,null];
										try{
											[seg,sym] = data.symbol.split("_");
											refresh_result_sequential(algo_uuid,k,msg,seg,sym);
										}
										catch(e){
											// show the respective error msg in the plot region
											refresh_error_sequential(symbols[count][0]+'_'+symbols[count][1],k,msg);
										}
									}
								}
							}
						}
						catch(err) {
							console.log(err);
						  	$(".loader_parent_backtest").fadeOut();
						  	$('.ti_msg_popup').show();
							$('.ti_msg_popup> div').show(); 
							$('.ti_msg').html('No trades were executed for this algo');
							clear_plot();
						}
						count += 1;
						if(count<max_count)
						{
							// continue loop_backtest;
							run_backtest_recusive(symbols,params,count,max_count)
						}else{
							// break finished_backtest;
							$('.run_backtest').html('Run Backtest');
							$('.run_backtest').attr('style',"background-color: #07c389;cursor: pointer !important");
							$('.run_backtest').attr('onclick','run_backtest_sequential()');
							return;
						}
					}).fail(function(){
						$('.run_backtest').html('Run Backtest');
						$('.run_backtest').attr('style',"background-color: #07c389;cursor: pointer !important");
						$('.run_backtest').attr('onclick','run_backtest_sequential()');
						k = symbols[count][0]+'_'+symbols[count][1];
						refresh_error_sequential2(symbols[count][0]+'_'+symbols[count][1],k,'Backtest has timed out, our servers are not reachable. Please try again.');
					});

					// finished_backtest:
					count = 0;
    			}else{
    				show_snackbar(null,'Backtest daily limit reached');
    				$('.run_backtest').html('Run Backtest');
					$('.run_backtest').attr('style',"background-color: #07c389;cursor: pointer !important");
					$('.run_backtest').attr('onclick','run_backtest_sequential()');
    			}
    		}
    	}else{
        msg_err = data['error_msg'];
        if (msg_err == undefined)
          msg_err = 'Unable to get subscription status';
        show_snackbar(null,msg_err);
    		$('.run_backtest').html('Run Backtest');
			$('.run_backtest').attr('style',"background-color: #07c389;cursor: pointer !important");
			$('.run_backtest').attr('onclick','run_backtest_sequential()');
    	}
    }).fail(function(){
    	$('.run_backtest').html('Run Backtest');
		$('.run_backtest').attr('style',"background-color: #07c389;cursor: pointer !important");
		$('.run_backtest').attr('onclick','run_backtest_sequential()');
    });
}

function run_backtest_recusive(symbols,params,count,max_count){
	if(count==max_count)
		return;
	params['symbols']=[symbols[count]];
	bt_url = "";
	lmda_vs_ec2_select();
	switch(url_selector){
		case 1: bt_url = bt_url2;
				break;
		case 2: bt_url = bt_url2;
				break;
		default:bt_url = bt_url2;
	}
	var settings = {
	  "async": true,
	  "crossDomain": true,
	  "url": bt_url,
	  "beforeSend": function() {
           myBtBarLoader(symbols[count][0]+'_'+symbols[count][1],bt_loading_time);
      },
	  "method": "POST",
	  "headers": {
	  },
	  // "data": "{\"action_str\":\"5 min sma crosses 10 min sma\",\"action_type\":\"BUY\",\"symbols\":[[\"NSE\",\"CANBK\"],[\"NSE\",\"ICICIBANK\"]],\n         \"quantity\":1,\"initial_capital\":1000000,\"dt_start\":\"09/11/2017\",\"dt_stop\":\"09/12/2017\",\"time_frame\":\"min\",\"commission\":40,\n         \"take_profit\":1,\"stop_loss\":0.5\n         }",
	  "data":JSON.stringify(params),
	  "timeout": 200000,//40 sec timeout
	}

	$.ajax(settings).done(function(msg){
		// try {
		// 	// var msg = JSON.parse(msg);
		// 	if(Object.keys(msg).length>0) // if the response has data clear the result rows
		// 		// $('.backtest_results_body').html('');
		// 	for(var k in msg)
		// 	{
		// 		data = msg[k];
		// 		[seg,sym] = [null,null];
		// 		try{
		// 			[seg,sym] = data.symbol.split("_");
		// 			refresh_result_sequential(params.algo_uuid,k,msg,seg,sym);
		// 		}
		// 		catch(e){
		// 			// show the respective error msg in the plot region
		// 			refresh_error_sequential(symbols[count][0]+'_'+symbols[count][1],k,msg);
		// 			;
		// 		}
		// 	}
		// }
		try {
			if(msg['status']=='error'){
				try{
					ga('send', {hitType: 'event', eventCategory: 'Backtest error', eventAction: msg['error_msg'], eventLabel: 'Backtest page', eventValue:1});
				}
				catch(e){
					
				}
				refresh_error_sequential2(symbols[count][0]+'_'+symbols[count][1],k,msg['error_msg']);
			}
			else{
				// var msg = JSON.parse(msg);
				if(Object.keys(msg).length>0) // if the response has data clear the result rows
					// $('.backtest_results_body').html('');
				for(var k in msg)
				{
					data = msg[k];
					if(data['error_msg']!=undefined){
						refresh_error_sequential2(symbols[count][0]+'_'+symbols[count][1],k,data['error_msg'])
					}else{
						[seg,sym] = [null,null];
						try{
							[seg,sym] = data.symbol.split("_");

							// try{
							// 	ga('send', {hitType: 'event', eventCategory: 'Backtest', eventAction: 'Backtest successful Individual', eventLabel: 'Backtest page'});
							// 	alert("BT successful individual ");
							// }
							// catch(e){
								
							// }
							refresh_result_sequential(params.algo_uuid,k,msg,seg,sym);
						}
						catch(e){
							// show the respective error msg in the plot region
							try{
								ga('send', {hitType: 'event', eventCategory: 'Backtest error', eventAction: data['error_msg'], eventLabel: 'Backtest page', eventValue:1});
							}
							catch(e){
								
							}
							refresh_error_sequential(symbols[count][0]+'_'+symbols[count][1],k,msg);
						}
					}
				}
			}
		}
		catch(err) {
			console.log(err);
		  	$(".loader_parent_backtest").fadeOut();
		  	$('.ti_msg_popup').show();
			$('.ti_msg_popup> div').show(); 
			$('.ti_msg').html('No trades were executed for the algo');
			clear_plot();
		}
		count += 1;
		if(count<max_count)
		{
			// continue loop_backtest;
			run_backtest_recusive(symbols,params,count,max_count)
		}else{
			// break finished_backtest;
			$('.run_backtest').html('Run Backtest');
			$('.run_backtest').attr('style',"background-color: #07c389;cursor: pointer !important");
			$('.run_backtest').attr('onclick','run_backtest_sequential()');
			return
		}
	}).fail(function(){
		$('.run_backtest').html('Run Backtest');
		$('.run_backtest').attr('style',"background-color: #07c389;cursor: pointer !important");
		$('.run_backtest').attr('onclick','run_backtest_sequential()');
	}).complete(function(){
		$('.run_backtest').html('Run Backtest');
		$('.run_backtest').attr('style',"background-color: #07c389;cursor: pointer !important");
		$('.run_backtest').attr('onclick','run_backtest_sequential()');
	});
}

function run_backtest() {
  // $(".loader_parent_backtest" ).fadeIn();
  var algo_uuid = $("#au_cc").val();
  var algo_name = $("#an_cc").val();
  var algo_desc = $("#ad_cc").val();
  // var from_datepicker = $("#from_datepicker").val();
  // var to_datepicker = $("#to_datepicker").val();
  var entry_str = $("#et_cc").val();
  var exit_logic = $("#ex_cc").val();
  var position_type = $("#pt_cc").val();

  var user_uuid = $("#ui_cc").val();

  var from_datepicker = null;
  var to_datepicker = null;
  var initial_capital = $("#ip_initial_capital").val();
  var quantity = $("#ip_quantity").val();
  var stop_loss = $("#ip_stoploss").val();
  var take_profit = $("#ip_takeprofit").val();
  var holding_type = holding_type_mapping[$("#ip_holding_type").val()];
  var interval = interval_mapping[$("#ip_interval").val()];

  // [from_datepicker,to_datepicker] = $('#date_range').val().split(' – ');
  [from_datepicker,to_datepicker] = [elements.start_input.value,elements.stop_input.value]

  if (holding_type=='MIS' && interval=='day') 
	{
		show_snackbar(null,'Cannot run MIS with day candle interval');
		return;
	}

  holding_type_latest = holding_type;

  var commission = 0;//$("#commission option:selected").val();

  symbols = [];
  for(sym in equity_added){
  	seg = equity_added[sym];
  	symbols.push([seg,sym.split('_')[0]]);
  }
  if (back_test_input_valid(algo_uuid,initial_capital,
                from_datepicker,
                to_datepicker,
                commission)==true)
  {
    // perform a post call to the view , passing the params
    params = {
      'algo_uuid':algo_uuid,//.hexDecode(),
      'algo_name':algo_name,//.hexDecode(),
      'algo_desc':algo_desc,//.hexDecode(),
      'user_uuid':user_uuid,
      'initial_capital':initial_capital,
      'action_str':entry_str,//.hexDecode(),
      'action_str_exit':exit_logic,
      'action_type':position_type.toUpperCase(),
      'quantity':quantity,
      'symbols':symbols,
      'stop_loss':stop_loss,
      'take_profit':take_profit,
      'dt_start':from_datepicker,
      'dt_stop':to_datepicker,
      'min_candle_freq':min_candle_freq,
      'time_frame':interval,
      'commission':commission,
      'holding_type':holding_type
    };
	// clear_plot();

    // post('/submit_algorithm/', params);
	// var request = $.ajax({
	//   url: "/run_backtest",
	//   type: "GET",
	//   data: params,
	//   timeout: 400000,//40 sec timeout
	//   dataType: "html"
	// });
	bt_url = "";
	lmda_vs_ec2_select();
	switch(url_selector){
		case 1: bt_url = bt_url2;
				break;
		case 2: bt_url = bt_url2;
				break;
		default:bt_url = bt_url2;
	}
	var settings = {
	  "async": true,
	  "crossDomain": true,
	  "url": bt_url,
	  "method": "POST",
	  "headers": {
	  },
	  // "data": "{\"action_str\":\"5 min sma crosses 10 min sma\",\"action_type\":\"BUY\",\"symbols\":[[\"NSE\",\"CANBK\"],[\"NSE\",\"ICICIBANK\"]],\n         \"quantity\":1,\"initial_capital\":1000000,\"dt_start\":\"09/11/2017\",\"dt_stop\":\"09/12/2017\",\"time_frame\":\"min\",\"commission\":40,\n         \"take_profit\":1,\"stop_loss\":0.5\n         }",
	  "data":JSON.stringify(params),
	  "timeout": 100000,//40 sec timeout
	}
	// for(sym in equity_added){
	// 	seg = equity_added[sym];
	// 	refresh_result_blank(algo_uuid,seg+'_'+sym,seg,sym);
	// }
	$.ajax(settings).done(function (msg){
		try {
			// var msg = JSON.parse(msg);
			if(Object.keys(msg).length>0) // if the response has data clear the result rows
				$('.backtest_results_body').html('');

			for(var k in msg)
			{
				data = msg[k];
				[seg,sym] = [null,null];
				try{
					[seg,sym] = data.symbol.split("_");
					refresh_result(algo_uuid,k,msg,seg,sym);
				}
				catch(e){
					// show the respective error msg in the plot region
					refresh_error(k,msg);
					continue;
				}
			}
		}
		catch(err) {
			console.log(err);
		  	$(".loader_parent_backtest").fadeOut();
		  	$('.ti_msg_popup').show();
			$('.ti_msg_popup> div').show(); 
			$('.ti_msg').html('No trades were executed for the algo');
			clear_plot();
		}

		$(".loader_parent_backtest" ).fadeOut();
	}).fail(function(jqXHR, textStatus) {
	  $(".loader_parent_backtest").fadeOut();
	  if(textStatus==="timeout") {
	  }
	  else{
		// alert( "Request failed: " + textStatus );
		$(".loader_parent_backtest").fadeOut();
	  	$('.ti_msg_popup').show();
		$('.ti_msg_popup> div').show(); 
		$('.ti_msg').html('Backtest timed out.<br> Please try again.<br> In case the error persists, email us at care@{---}.com');
		clear_plot();
	  }
	});
  }
  else{
    close_popup();
    // alert('Some error');
  }

  try{

  }catch(e){
              
  }
}

function run_backtest_multi(){
	if(Object.keys(equity_added).length === 0)
		return;
	$('.empty_backtest_results_body').hide();
	var algo_uuid = $("#au_cc").val();
	var algo_name = $("#an_cc").val();
	var algo_desc = $("#ad_cc").val();
	// var from_datepicker = $("#from_datepicker").val();
	// var to_datepicker = $("#to_datepicker").val();
	var entry_str = $("#et_cc").val();
	var exit_logic = $("#ex_cc").val();
	var position_type = $("#pt_cc").val();

	var user_uuid = $("#ui_cc").val();

	var from_datepicker = null;
	var to_datepicker = null;
	var initial_capital = $("#ip_initial_capital").val();
	var quantity = $("#ip_quantity").val();
	var stop_loss = $("#ip_stoploss").val();
	var take_profit = $("#ip_takeprofit").val();
	var holding_type = holding_type_mapping[$("#ip_holding_type").val()];
	var interval = interval_mapping[$("#ip_interval").val()];

	// advanced parameters
	// var holding_type = adv_holding_type;
	var chart_type = adv_chart_type;
	var trading_start_time = adv_trading_start_time;
	var trading_stop_time = adv_trading_stop_time;
	var trade_time_given = "False";
	if(trading_stop_time!=''&&trading_start_time!=''&&trading_stop_time>trading_start_time){
	trade_time_given = "True";
	}
	//----------------------//
	// [from_datepicker,to_datepicker] = $('#date_range').val().split(' – ');
	[from_datepicker,to_datepicker] = [elements.start_input.value,elements.stop_input.value]
	
	if (holding_type=='MIS' && interval=='day') 
	{
		show_snackbar(null,'Cannot run MIS with day candle interval');
		return;
	}

	holding_type_latest = holding_type;
	
	var commission = 0;//$("#commission option:selected").val();
	symbols = [];
	for(sym in equity_added){
		seg = equity_added[sym];
		symbols.push([seg,sym.split('_')[0]]);
	}
	if (back_test_input_valid(algo_uuid,initial_capital,
	            from_datepicker,
	            to_datepicker,
	            commission,symbols,stop_loss,take_profit,quantity,interval)!=true)
	{
		// alert error
		return;
	}
	
	$('.run_backtest').attr('style',"background-color: #c7c7c7 !important;cursor: no-drop !important");
	$('.run_backtest').attr('onclick',';');
	$(".run_backtest").html("<img src='/static/imgs/button-loading-rect.gif' id='button_loading'>");
	var ga_eq = JSON.stringify(equity_added).split(",").length;
	try{
		ga('send', {hitType: 'event', eventCategory: 'Backtest initiated', eventAction: 'Backtest initiated', eventLabel: 'Backtest page', eventValue:ga_eq});
	}
	catch(e){
		
	}
	$.get('/get_subscription_limit',{
    }).done(function (data){
    	if(data['status']=="success")
    	{
    		if(data['valid']==true){
    			if(data['backtest']>0){
    				var max_count = 0
					// $('.backtest_results_body').html('');
					if($('.backtest_results_body .multiple_backtest_header')[0]==undefined){
						$('.backtest_results_body').html('');
						$('.backtest_results_body').html('<div class="multiple_backtest_results"><div class="multiple_backtest_results_table" id="multiple_backtest_results_table"><div class="multiple_backtest_header"><div class="expand_row_title"></div><div class="live_indicator_title"><p></p></div><div class="scrip_title"><p>Instrument</p></div><div class="ltp_title"><p>LTP</p></div><div class="pnl_title"><p>Backtest P&L</p></div><div class="streak_row_title"><p>Wins vs Losses</p></div><div class="signals_title"><p>Signals</p></div><div class="wins_title"><p>Wins</p></div><div class="losses_title"><p>Losses</p></div><div class="winning_streak_title"><p>WS</p></div><div class="losing_streak_title"><p>LS</p></div><div class="max_drawdown_title"><p>Max. DD</p></div><!-- <div class="action_deploy_title"></div> --><div class="action_download_title"></div><!-- <div class="action_share_title"></div> --><div class="checkbox_title"><input type="checkbox" name="" class="deploy_all_checkbox" id="deploy_all_checkbox" onclick="select_all(event,$(this))"></div></div><div class="multiple_backtest_body"></div></div></div>');
    				}
    				else{
						$('.backtest_results_body').html('<div class="multiple_backtest_results"><div class="multiple_backtest_results_table" id="multiple_backtest_results_table"><div class="multiple_backtest_header"><div class="expand_row_title"></div><div class="live_indicator_title"><p></p></div><div class="scrip_title"><p>Instrument</p></div><div class="ltp_title"><p>LTP</p></div><div class="pnl_title"><p>Backtest P&L</p></div><div class="streak_row_title"><p>Wins vs Losses</p></div><div class="signals_title"><p>Signals</p></div><div class="wins_title"><p>Wins</p></div><div class="losses_title"><p>Losses</p></div><div class="winning_streak_title"><p>WS</p></div><div class="losing_streak_title"><p>LS</p></div><div class="max_drawdown_title"><p>Max. DD</p></div><!-- <div class="action_deploy_title"></div> --><div class="action_download_title"></div><!-- <div class="action_share_title"></div> --><div class="checkbox_title"><input type="checkbox" name="" class="deploy_all_checkbox" id="deploy_all_checkbox" onclick="select_all(event,$(this))"></div></div><div class="multiple_backtest_body"></div></div></div>');
    				}

					for(sym in equity_added){
						seg = equity_added[sym];
            sym = sym.split('_')[0]
						refresh_result_blank_multi(algo_uuid,seg+'_'+sym,seg,sym);
						max_count += 1;
					}

					var count = 0;
					// perform a post call to the view , passing the params
					// loop_backtest: 
					var params = {
						'algo_uuid':algo_uuid,//.hexDecode(),
						'algo_name':algo_name,//.hexDecode(),
						'algo_desc':algo_desc,//.hexDecode(),
						'user_uuid':user_uuid,
						'initial_capital':initial_capital,
						'entry_logic':entry_str,//.hexDecode(),
						'exit_logic':exit_logic,
						'position_type':position_type.toUpperCase(),
						'position_qty':quantity,
						'symbols':[symbols[count]],
						'stop_loss':stop_loss,
						'take_profit':take_profit,
						'dt_start':from_datepicker,
						'dt_stop':to_datepicker,
						'min_candle_freq':min_candle_freq,
						'time_frame':interval,
						'commission':commission,
						// advanced parameters
						'holding_type':holding_type,
						'chart_type':chart_type,
						'trade_time_given':trade_time_given,
						'trading_start_time':trading_start_time,
						'trading_stop_time':trading_stop_time,
						'algo_pref':algo_pref
					};
					bt_url = "";
					lmda_vs_ec2_select();
					refresh_algo_summary()
					switch(url_selector){
						case 1: bt_url = bt_url2;
								break;
						case 2: bt_url = bt_url2;
								break;
						default:bt_url = bt_url2;
					}
					var settings = {
					  "async": true,
					  "crossDomain": true,
					  "url": bt_url,
					  "method": "POST",
					  "headers": {
					  },
					  "beforeSend": function() {
			               myBtBarLoader(symbols[count][0]+'_'+symbols[count][1],bt_loading_time);
			          },
					  // "data": "{\"action_str\":\"5 min sma crosses 10 min sma\",\"action_type\":\"BUY\",\"symbols\":[[\"NSE\",\"CANBK\"],[\"NSE\",\"ICICIBANK\"]],\n         \"quantity\":1,\"initial_capital\":1000000,\"dt_start\":\"09/11/2017\",\"dt_stop\":\"09/12/2017\",\"time_frame\":\"min\",\"commission\":40,\n         \"take_profit\":1,\"stop_loss\":0.5\n         }",
					  "data":JSON.stringify(params),
					  "timeout": 200000,//40 sec timeout
					}
					// myBtBarLoader(k,1000);
					$.ajax(settings).done(function(msg){
						try {
							if(msg['status']=='error'){
								k = symbols[count][0]+'_'+symbols[count][1];
								refresh_error_sequential2_multi(symbols[count][0]+'_'+symbols[count][1],k,msg['error_msg']);
								try{
									ga('send', {hitType: 'event', eventCategory: 'Backtest error bulk', eventAction: msg['error_msg'], eventLabel: 'Backtest page', eventValue:ga_eq});
								}catch(e){

								}
							}
							else{
								// var msg = JSON.parse(msg);
								if(Object.keys(msg).length>0) // if the response has data clear the result rows
									// $('.backtest_results_body').html('');
								for(var k in msg)
								{
									data = msg[k];
									if(data['error_msg']!=undefined){
										refresh_error_sequential2_multi(symbols[count][0]+'_'+symbols[count][1],k,data['error_msg']);
										try{
											ga('send', {hitType: 'event', eventCategory: 'Backtest error', eventAction:data['error_msg'] , eventLabel: 'Backtest page', eventValue:1});
										}catch(e){

										}
									}else{
										[seg,sym] = [null,null];
										try{
											[seg,sym] = data.symbol.split("_");
											refresh_result_sequential_multi(algo_uuid,k,msg,seg,sym);
                      try{
  											ga('send', {hitType: 'event', eventCategory: 'Backtest successful', eventAction:'Backtest successful', eventLabel: 'Backtest page', eventValue:1});
                      }
                      catch(e){
                        
                      }
										}
										catch(e){
											// show the respective error msg in the plot region
											refresh_error_sequential_multi(symbols[count][0]+'_'+symbols[count][1],k,msg);
										}
									}
								}
							}
						}
						catch(err) {
							console.log(err);
						  	$(".loader_parent_backtest").fadeOut();
						  	$('.ti_msg_popup').show();
							$('.ti_msg_popup> div').show(); 
							$('.ti_msg').html('No trades were executed for this algo');
							clear_plot();
						}
						count += 1;
						if(count<max_count)
						{
							// continue loop_backtest;
							run_backtest_recusive_multi(symbols,params,count,max_count)
						}else{
							// break finished_backtest;
							$('.run_backtest').html('Run Backtest');
							$('.run_backtest').attr('style',"background-color: #07c389;cursor: pointer !important");
							$('.run_backtest').attr('onclick','run_backtest_sequential()');
							return;
						}
					}).fail(function(e){
						$('.run_backtest').html('Run Backtest');
						$('.run_backtest').attr('style',"background-color: #07c389;cursor: pointer !important");
						$('.run_backtest').attr('onclick','run_backtest_sequential()');
						k = symbols[count][0]+'_'+symbols[count][1];
						refresh_error_sequential2_multi(symbols[count][0]+'_'+symbols[count][1],k,'Backtest has timed out, our servers are not reachable. Please try again.');
						try{
							ga('send', {hitType: 'event', eventCategory: 'Backtest error bulk', eventAction: 'Backtest has timed out, our servers are not reachable', eventLabel: 'Backtest page', eventValue: ga_eq});
						}catch(e){

						}
					});

					// finished_backtest:
					count = 0;
    			}else{
    				show_snackbar(null,'Backtest daily limit reached');
    				$('.run_backtest').html('Run Backtest');
					$('.run_backtest').attr('style',"background-color: #07c389;cursor: pointer !important");
					$('.run_backtest').attr('onclick','run_backtest_sequential()');
    			}
    		}
    	}else{
        msg_err = data['error_msg'];
        if (msg_err == undefined)
          msg_err = 'Unable to get subscription status';
    		show_snackbar(null,msg_err);
    		$('.run_backtest').html('Run Backtest');
			$('.run_backtest').attr('style',"background-color: #07c389;cursor: pointer !important");
			$('.run_backtest').attr('onclick','run_backtest_sequential()');
    	}
    }).fail(function(){
    	$('.run_backtest').html('Run Backtest');
		$('.run_backtest').attr('style',"background-color: #07c389;cursor: pointer !important");
		$('.run_backtest').attr('onclick','run_backtest_sequential()');
    });
}

function refresh_error_sequential2_multi(seg_sym,k,msg){
	// data = msg[k];
	// error_msg = msg["error_msg"];
	error_msg = msg;
	if(error_msg=="Wrong inputs")
		error_msg = 'Unable to fetch data for the given backtest period, kindly try again with smaller period or after some time';
	try{
			[seg,sym] = seg_sym.split("_");
		// if(k!='runtime' && k!='updated_time'){
			var backtest_results_row = $("#"+seg_sym.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_'));
			// backtest_results_row.addClass('empty_backtest_results_row');
			// var backtest_results_left = $("<div>",{"class":"backtest_results_left"});
			// backtest_results_row.html('<div class="empty_backtest_results_row" id="empty_backtest_results_row"> <div class="backtest_results_left"> <div class="results_section"> <div class="chart_section"> <div class="chart_header"> <div class="equity_section"> <p class="company_name">'+sym+'&nbsp;<span class="exc_symbol">'+seg+'</span></p> <!-- <p >: CANBK</p> --> </div> <div class="brokerage_section"> <p> </p> </div> </div> <div class="chart_body"> <p class="backtest_row_error_message_display">'+error_msg+'</p> </div> </div> <div class="pnl_section"> <div class="pnl"> <p>P&L&nbsp;<span>(N.A)&nbsp;</span><span>(N.A)&nbsp;</span></p> </div> <div class="streak"> <div class="streak_body"> <div class="wins"></div> <div class="losses"></div> </div> </div> <div class="results_table"> <table> <tr><td>Total number of signals</td><td>- / -</td></tr><tr><td>Number of wins</td><td>- / -</td></tr><tr><td>Number of losses</td><td>- / -</td></tr><tr><td>Winning streak</td><td>- / -</td></tr><tr><td>Losing streak</td><td>- / -</td></tr><tr><td>Max gains</td><td>- / -</td></tr><tr><td>Max loss</td><td>- / -</td></tr><tr><td>Avg gain/winning trade</td><td>- / -</td></tr><tr><td>Avg loss/losing trade</td><td>- / -</td></tr><tr><td>Max Drawdown</td><td>- / -</td></tr> </table> </div> </div> </div> <div class="empty_transactions_section"> <p>Transaction Details <span><img src="/static/imgs/icon-down-arrow.png"></span></p> </div> </div> <div class="backtest_results_right"> <div class="fundamentals_section"> <table> <caption>Stock Performance</caption> <tr><td>Period High</td><td>- / -</td></tr><tr><td>Period Low</td><td>- / -</td></tr><tr><td>Period return</td><td>- / -</td></tr> </table> </div> <div class="actions_section"> <table class="actions_buttons"> <tr> <td> <button class="deploy"><span><img src="/static/imgs/icon-deploy.png"></span>&nbsp;&nbsp;&nbsp;Deploy</button> </td> </tr> <tr> <td> <button class="download"><span><img src="/static/imgs/icon-new-download.png"></span></button> <button class="empty_share"><span><img src="/static/imgs/icon-share.png"></span></button> </td> </tr> </table> <div class="social_buttons"> <span><button style="display:none"><img src="/static/imgs/icon-linkedin.png"></button></span> <span style="display:none;"><button><img src="/static/imgs/icon-whatsapp.png"></button></span> <span><button><img src="/static/imgs/icon-facebook.png"></button></span> <span><button><img src="/static/imgs/icon-twitter.png"></button></span> </div> </div> </div> </div>');
		// }
			backtest_results_row.html('<div class="multiple_backtest_row_first_empty"><div class="live_indicator_detail"><span class="indicator_grey"></span></div><div class="scrip_row_detail"> <div class="equity_section"> <p class="company_name">'+sym+' &nbsp;<span class="exc_symbol">'+seg+'</span></p> </div> </div><div class="empty_row_detail"><p>'+error_msg+'</p> <!--<p><img src="/static/imgs/button-loading-rect.gif"></p>--> </div><!--<div class="expand_row_detail"><img src="/static/imgs/bt_down.svg"></div><div class="action_download_row_detail"> <button class="download" data-tooltip-top="Download backtest trade details"><span><img src="/static/imgs/icon-download-grey-new.png"></span></button> </div> <div class="checkbox_row_detail"> <input type="checkbox" name="" <input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" disabled> </div>--></div><div class="multiple_backtest_row_second" data-toggle="false"><div class="multiple_backtest_row_second_wrapper"></div></div>');
			// $('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')).html('<div class="multiple_backtest_row_first_empty"><div class="scrip_row_detail"> <div class="equity_section"> <p class="company_name">'+sym+' &nbsp;<span class="exc_symbol">'+seg+'</span></p> </div> </div><div class="empty_row_detail"><!--<p>No trades happend</p>--> <span class="loading-dots-container" id="update_top_performance1"><div class="loading-dots"><div class="loading-dots--dot"></div><div class="loading-dots--dot"></div><div class="loading-dots--dot"></div><div class="loading-dots--dot"></div><div class="loading-dots--dot"></div></div></span></div><div class="action_deploy_row_detail"> </div> <div class="action_download_row_detail"> <button class="download" data-tooltip-top="Download backtest trade details"><span><img src="/static/imgs/icon-download-grey-new.png"></span></button> </div><div class="checkbox_row_detail"> <input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" disabled> </div></div><div class="multiple_backtest_row_second" data-toggle="false"><div class="multiple_backtest_row_second_wrapper"></div></div>');

	}
	catch(err){
		return;
	}
}

function refresh_result_blank_multi(algo_uuid,k,seg,sym){

	var backtest_results_row = $('<div>', {id: k.replace('/','_--_').replace(/ /g,'_-_'), "class": "multiple_backtest_row"});
	
	backtest_results_row.addClass('multiple_backtest_row_empty');
	$('.backtest_results_body .multiple_backtest_body').append(backtest_results_row);

	// $("#"+k).html('<div style="margin: auto;"><img src="/static/imgs/backtest-loading-gif.gif"><p>Generating Backtest Results of '+[sym,seg].join(' ')+'&nbsp;&nbsp;&nbsp;<!--<span><!--100%--></span>--></p><div id="myProgress"><div id="myBar"></div></div></div>');
	// $('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')).html('<div class="multiple_backtest_row_first"><div class="live_indicator_detail"><span class="indicator_grey"></span></div><div class="scrip_row_detail"> <div class="equity_section"> <p class="company_name">'+sym+' &nbsp;<span class="exc_symbol">'+seg+'</span></p> </div> </div> <div class="ltp_row_detail token__'+seg+'_'+sym+'"> <p>0.0</p> </div> <div class="pnl_row_detail"> <div class="pnl"> <p><span>NA&nbsp;</span><span>(1.2%)&nbsp;</span></p> </div> </div> <div class="streak_row_detail"> <div class="streak"> <div class="streak_body"> <div class="wins"></div> <div class="losses"></div> </div> </div> </div> <div class="max_drawdown_row_detail"> <p>NA%</p> </div> <div class="winning_streak_row_detail"> <p>-</p> </div> <div class="losing_streak_row_detail"> <p>-</p> </div> <div class="action_deploy_row_detail"> <button class="deploy_disabled" id="deploy"><span><img src="/static/imgs/icon-deploy.png"></span>&nbsp;&nbsp;&nbsp;Deploy</button> </div> <div class="action_download_row_detail"> <button class="download" data-tooltip-top="Download backtest trade details"><span><img src="/static/imgs/icon-new-download.png"></span></button> </div> <div class="action_share_row_detail"> <button class="share" data-tooltip-top="Get sharable link"><span><img src="/static/imgs/icon-share.png"></span></button> </div> <div class="checkbox_row_detail"> <input type="checkbox" name=""> </div></div><div class="multiple_backtest_row_second"></div>');
	// $('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')).html('<div class="multiple_backtest_row_first_empty"><div class="live_indicator_detail"><span class="indicator_grey"></span></div><div class="scrip_row_detail"> <div class="equity_section"> <p class="company_name">'+sym+' &nbsp;<span class="exc_symbol">'+seg+'</span></p> </div> </div><div class="empty_row_detail"><!--<p>No trades happend</p>--> <p><img src="/static/imgs/button-loading-rect.gif"></p></div><div class="action_deploy_row_detail"> <button class="deploy_disabled" id="deploy"><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button> </div> <div class="action_download_row_detail"> <button class="download" data-tooltip-top="Download backtest trade details"><span><img src="/static/imgs/icon-download-grey-new.png"></span></button> </div> <div class="action_share_row_detail"> <div class="social_buttons" style=""><span><button id="linkedin_'+seg+'_'+sym+'" ><img src="/static/imgs/icon-linkedin.png"></button></span><span style="display:none;"><button id="whatsapp_'+seg+'_'+sym+'" ><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button id="fb_'+seg+'_'+sym+'" ><img src="/static/imgs/icon-facebook.png"></button></span><span><button id="twitter_'+seg+'_'+sym+'"><img src="/static/imgs/icon-twitter.png"></button></span></div> </div> <div class="checkbox_row_detail"> <input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" disabled> </div></div><div class="multiple_backtest_row_second" data-toggle="false"><div class="multiple_backtest_row_second_wrapper"></div></div>');
	// $('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')).html('<div class="multiple_backtest_row_first_empty"><div class="live_indicator_detail"><span class="indicator_grey"></span></div><div class="scrip_row_detail"> <div class="equity_section"> <p class="company_name">'+sym+' &nbsp;<span class="exc_symbol">'+seg+'</span></p> </div> </div><div class="empty_row_detail"><!--<p>No trades happend</p>--> <span class="loading-dots-container" id="update_top_performance1"><div class="loading-dots"><div class="loading-dots--dot"></div><div class="loading-dots--dot"></div><div class="loading-dots--dot"></div><div class="loading-dots--dot"></div><div class="loading-dots--dot"></div></div></span></div><div class="action_deploy_row_detail"> <button class="deploy_disabled" id="deploy"><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button> </div> <div class="action_download_row_detail"> <button class="download" data-tooltip-top="Download backtest trade details"><span><img src="/static/imgs/icon-download-grey-new.png"></span></button> </div> <div class="action_share_row_detail"> <div class="social_buttons" style=""><span><button id="linkedin_'+seg+'_'+sym+'" ><img src="/static/imgs/icon-linkedin.png"></button></span><span style="display:none;"><button id="whatsapp_'+seg+'_'+sym+'" ><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button id="fb_'+seg+'_'+sym+'" ><img src="/static/imgs/icon-facebook.png"></button></span><span><button id="twitter_'+seg+'_'+sym+'"><img src="/static/imgs/icon-twitter.png"></button></span></div> </div> <div class="checkbox_row_detail"> <input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" disabled> </div></div><div class="multiple_backtest_row_second" data-toggle="false"><div class="multiple_backtest_row_second_wrapper"></div></div>');
	$('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')).html('<div class="multiple_backtest_row_first_empty"><div class="live_indicator_detail"><span class="indicator_grey"></span></div><div class="scrip_row_detail"> <div class="equity_section"> <p class="company_name">'+sym+' &nbsp;<span class="exc_symbol">'+seg+'</span></p> </div> </div><div class="empty_row_detail"><!--<p>No trades happend</p>--> <span class="loading-dots-container" id="update_top_performance1"><div class="loading-dots"><div class="loading-dots--dot"></div><div class="loading-dots--dot"></div><div class="loading-dots--dot"></div><div class="loading-dots--dot"></div><div class="loading-dots--dot"></div></div></span></div><div class="action_deploy_row_detail"> </div> <!--<div class="expand_row_detail"><img src="/static/imgs/bt_down.svg"></div><div class="action_download_row_detail"> <button class="download" data-tooltip-top="Download backtest trade details"><span><img src="/static/imgs/icon-download-grey-new.png"></span></button> </div><div class="checkbox_row_detail"> <input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" disabled> </div>--></div><div class="multiple_backtest_row_second" data-toggle="false"><div class="multiple_backtest_row_second_wrapper"></div></div>');

}

function refresh_error_sequential_multi(seg_sym,k,msg){
	data = msg[k];
	try{
		[seg,sym] = seg_sym.split("_");
		if(k!='runtime' && k!='updated_time'){
			var backtest_results_row = $("#"+seg_sym.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_'));
			var backtest_results_left = $("<div>",{"class":"backtest_results_left"});
			var results_section = $("<div>",{"class":"results_section"}).append('<div class="chart_section"><div class="chart_header"><div class="equity_section"><p class="company_name">'+sym+' <span class="exc_symbol">'+seg+'</span></p></div><div class="brokerage_section"><p></p></div></div><div class="chart_body"><div id="'+k.replace('/','_--_').replace(/ /g,'_-_')+'pnl_chartContainer_new"><p></p></div></div></div>');
			backtest_results_row.html('');
			backtest_results_left.append(results_section);
			backtest_results_row.append(backtest_results_left);
			// $('.backtest_results_body').append(backtest_results_row);
			$("#"+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").html(data['error_msg']);
			try{
				ga('send', {hitType: 'event', eventCategory: 'Backtest error', eventAction:data['error_msg'], eventLabel: 'Backtest page', eventValue:1});
			}catch(e){

			}
		}
	}
	catch(err){
		return;
	}
}

function load_backtest(k,toggle_open){
	if (k!=undefined && backtest_result_response[k]!=null && backtest_result_response[k]!=undefined && $('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").is(':visible') && toggle_open)
		{
			$('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").replaceWith('<canvas id="'+k.replace('/','_--_').replace(/ /g,'_-_')+'pnl_chartContainer_new"></canvas>');
			// var ctx = $('#'+k+"pnl_chartContainer_new")[0].getContext('2d');

			var ctx = document.getElementById(k.replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").getContext('2d');

			stroke = '#06d092'
			var addColor1 = 'rgba(6,208,146, 0.15)';
      		var addColor2 = 'rgba(6,208,146, 0)';

			if(backtest_result_response[k].final_pnl<0.0){
				stroke = '#f43b51';
				addColor1 = 'rgba(255,66,88, 0)';
				addColor2 = 'rgba(255,66,88, 0.15)';
			}

			var gradient = ctx.createLinearGradient(0, 0, 0, 400);
		    gradient.addColorStop(0, addColor1);
		    gradient.addColorStop(0.8, addColor2);

			var pnl_chartContainer_new = new Chart(ctx,{
				type: 'line',
				scaleSteps : 4,
		    	data: {
		    		// labels: ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
					datasets: [{
					    label: 'P&L',
					    data: processListToXYList(backtest_result_response[k].pnl),
					    // backgroundColor:'rgba(255,255,255,0)',
					    backgroundColor: gradient,
					    // borderColor: '#2288ff',
					    borderColor: stroke,
					    borderWidth: 2,
					    lineTension: 0,
          				strokeColor: stroke,
					    // pointStyle: 'star',
					    // point: { radius: 0 },
					    hoverRadius: 5
					}]
		    	},
		    	options: {
		    		scales: {
		            yAxes: [{
		            	gridLines: {
							color: '#ecf0f1',
							zeroLineBorderDash: [5, 5],
							zeroLineColor: '#ecf0f1'
								},
		                ticks: {
		                	fontColor: '#9ea1a4',
		                    beginAtZero:true,
		                    // maxTicksLimit:1
		                    // ticks: {min: 0, max:4}
		                }
		            }],
		            	xAxes: [{
				        type: 'time',
				        position: 'bottom',
				         gridLines: {
								display: false,
								color: '#ecf0f1',
								zeroLineBorderDash: [5, 5],
								zeroLineColor: '#ecf0f1'
						},
						ticks: {
							fontColor: '#9ea1a4'
						},
				        time: {
				          displayFormats: {
				          	// 'millisecond': 'MMM DD',
				           //  'second': 'MMM DD',
				           //  'minute': 'MMM DD',
				           //  'hour': 'MMM DD',
				           //  'day': 'MMM DD',
				           //  'week': 'MMM DD',
				           //  'month': 'MMM DD',
				           //  'quarter': 'MMM DD',
				            'year': 'YY MMM DD',
				          }
				        }
				      }],
					},
					legend: {
					    display: false,
					},
					// title: {
					//     display: true,
					//     text: 'P&L Performance',
					//     fontColor: '#333333',
					//     fontFamily: '"open_sansregular","AvenirNextLTPro",Arial,Helvetica,sans-serif',
					//     fontStyle:'bold',
					//     position: 'top',
					//     fontSize: 16
					// },
					// legend: {
					//     display: true,
					//     labels: {
					//         fontColor: '#666666'
					//     }
					// },
					elements: { point: { radius: 0 } },	
				}
			});
			$('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+' .brokerage_toggle:checkbox').on('change',function(e){
				broker_toggle(e);
			});
		}
}

function refresh_result_multi(algo_uuid,k,msg,seg,sym){

  if(['runtime', 'updated_time', 'updated'].indexOf(k) > -1){
  	if(seg !== seg.toUpperCase() || sym !== sym.toUpperCase()){
  		return;
  	}
  }

	backtest_result_response[k] = msg[k];
	data = msg[k];
	backtest_result_response[k]=data;
	// var backtest_results_row = $("<div>", {id: k, "class": "backtest_results_row"});

	var backtest_results_row = $('<div>', {id: k.replace('/','_--_').replace(/ /g,'_-_'), "class": "multiple_backtest_row"});
	
	backtest_results_row.addClass('multiple_backtest_row_empty');
	$('.backtest_results_body .multiple_backtest_body').append(backtest_results_row);
	// $('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')).html('<div class="multiple_backtest_row_first_empty"><div class="live_indicator_detail"><span class="indicator_grey"></span></div><div class="scrip_row_detail"> <div class="equity_section"> <p class="company_name">'+sym+' &nbsp;<span class="exc_symbol">'+seg+'</span></p> </div> </div><div class="empty_row_detail"><!--<p>No trades happend</p>--> <p><img src="/static/imgs/button-loading-rect.gif"></p></div><div class="action_deploy_row_detail"> <button class="deploy_disabled" id="deploy"><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button> </div> <div class="action_download_row_detail"> <button class="download" data-tooltip-top="Download backtest trade details"><span><img src="/static/imgs/icon-download-grey-new.png"></span></button> </div> <div class="action_share_row_detail"> <button class="share" data-tooltip-top="Get sharable link"><span><img src="/static/imgs/icon-share2.png"></span></button> </div> <div class="checkbox_row_detail"> <input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" onclick="select_any(event,$(this))"> </div></div><div class="multiple_backtest_row_second" data-toggle="false"><div class="multiple_backtest_row_second_wrapper"></div></div>');
	dep_indicator_color = '<div class="live_indicator_detail"><span class="indicator_grey"></span></div>';
	if(deployed_seg_sym.includes(seg+'_'+sym)){
		dep_indicator_color = '<div class="live_indicator_detail"><span class="indicator_green"></span></div>';
	}

	$('#'+k.replace('&','\\&').replace(/ /g,'_-_')).html('<div class="multiple_backtest_row_first_empty">'+dep_indicator_color+'<div class="scrip_row_detail"> <div class="equity_section"> <p class="company_name">'+sym+' &nbsp;<span class="exc_symbol">'+seg+'</span></p> </div> </div><div class="empty_row_detail"><!--<p>No trades happend</p>--> <span class="loading-dots-container" id="update_top_performance1"><div class="loading-dots"><div class="loading-dots--dot"></div><div class="loading-dots--dot"></div><div class="loading-dots--dot"></div><div class="loading-dots--dot"></div><div class="loading-dots--dot"></div></div></span></div><div class="action_deploy_row_detail"> <button class="deploy_disabled" data-tooltip-top="Select strategies to deploy" id="deploy"><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button> </div> <!--<div class="expand_row_detail"><img src="/static/imgs/bt_down.svg"></div><div class="action_download_row_detail"> <button class="download" data-tooltip-top="Download backtest trade details"><span><img src="/static/imgs/icon-download-grey-new.png"></span></button> </div> <div class="action_share_row_detail"> <button class="share" data-tooltip-top="Get sharable link"><span><img src="/static/imgs/icon-share2.png"></span></button> </div> <div class="checkbox_row_detail"> <input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" onclick="select_any(event,$(this))"> </div>--></div><div class="multiple_backtest_row_second" data-toggle="false"><div class="multiple_backtest_row_second_wrapper"></div></div>');

	var backtest_results_left = $("<div>",{"class":"backtest_results_left"});
	var results_section = $("<div>",{"class":"results_section"}).append('<div class="chart_section" id="chart_section"><div class="chart_header"><div class="equity_section"><!--<p class="company_name">'+sym+' <span class="exc_symbol">'+seg+'</span></p>--></div><div class="brokerage_section"><p data-tooltip-bottom="Adjusted for brokerage and other charges (does not include stamp duty and DP charges)">Brokerage&nbsp;&nbsp;&nbsp;<label class="switch"><input class="brokerage_toggle" id="'+k.replace('/','_--_').replace(/ /g,'_-_')+'" type="checkbox"><span class="slider"></span></label></p></div></div><div class="chart_body"><canvas id="'+k.replace('/','_--_').replace(/ /g,'_-_')+'pnl_chartContainer_new"></canvas></div></div>');
	//+data.win_count/(data.win_count+data.loss_count)+
	color = '#06d092';
	img_url = "/static/imgs/icon-arrow-up-green.png";
	if(data.final_pnl<0){
		color = '#ff4343';
		img_url = "/static/imgs/icon-arrow-down-red.png";
	}
	var pnl_section = $("<div>",{"class":"pnl_section", "id":"pnl_section"}).append('<!--<div class="pnl"><p>P&L&nbsp;<span><img src="'+img_url+'">&nbsp;</span><span style="color:'+color+'">'+parseFloat(data.final_pnl).toFixed(2)+'&nbsp;</span><span style="color:'+color+'"">('+parseFloat(data.final_pnl/data.max_cap_used*100).toFixed(2)+'%)&nbsp;</span></p></div><div class="streak"><div class="streak_body"><div data-tooltip-top="'+data.win_count+"/"+(data.win_count+data.loss_count)+' winning trades" class="wins" style="width:'+data.win_count/(data.win_count+data.loss_count)*100+'%"></div><div class="losses" data-tooltip-top="'+data.loss_count+"/"+(data.win_count+data.loss_count)+' losing trades" style="width:'+data.loss_count/(data.win_count+data.loss_count)*100+'%"></div></div></div>--><div class="results_table"><table><!--<td>Alpha</td><td>0.079</td></tr><tr><td>Beta</td><td>0.597</td></tr>--><!--<tr><td>Volatility</td><td>'+parseFloat(data.volatility).toFixed(2)+'%</td></tr><tr><td>Sharpe Ratio</td><td>'+parseFloat(data.sharpe).toFixed(2)+'</td></tr>--><!--<tr><td>Sortino</td><td>'+parseFloat(data.volatility).toFixed(2)+'</td></tr>-->' +'<tr><td>Total number of signals</td><td>'+data.total_number_of_signals+'</td></tr>'+'<tr><td>Number of wins</td><td>'+data.win_count+'</td></tr>'+'<tr><td>Number of losses</td><td>'+data.loss_count+'</td></tr>'+'<tr><td>Winning streak</td><td>'+data.winning_streak+'</td></tr>'+'<tr><td>Losing streak</td><td>'+data.lossing_streak+'</td></tr>'+'<tr><td>Max gains</td><td>'+parseFloat(data.maximum_gain).toFixed(2)+'</td></tr>'+'<tr><td>Max loss</td><td>'+parseFloat(data.maximum_loss).toFixed(2)+'</td></tr>'+'<tr><td>Avg gain/winning trade</td><td>'+parseFloat(data.average_gain_per_winning_trade).toFixed(2)+'</td></tr>'+'<tr><td>Avg loss/losing trade</td><td>'+parseFloat(data.average_gain_per_losing_trade).toFixed(2)+'</td></tr>' +'<tr><td>Max Drawdown</td><td>'+parseFloat(data.max_draw).toFixed(2)+'%</td></tr></table></div>');
	
	results_section.append(pnl_section);

	backtest_results_left.append(results_section);

	var transactions_section = $('<div>',{"class":"transactions_section", "id":"transactions_section"}).append('<p>Transaction Details <span><img src="/static/imgs/new/transactions_dropdown.svg"></span></p>');

	backtest_results_left.append(transactions_section);

	var transactions_table = $("<div>",{"class":"transactions_table","style":"display:none;"});

	if(data.trade_log[0][7]==undefined)
		var trade_log = $("<table>",{}).append('<tr><th>Trigger date</th><th>Equity</th><th>Buy/Sell</th><th>Qty</th><th>Price</th><th>Cumulative P&L</th></tr>');
	else
		var trade_log = $("<table>",{}).append('<tr><th>Trigger date</th><th>Equity</th><th>Buy/Sell</th><th>Qty</th><th>Price</th><th>Cumulative P&L</th><th>Trigger type</th></tr>');
	var prev_pnl = 0;
	rounding = 2
	if (seg=='CDS-FUT')
		rounding = 4
	for(var i = 0; i <= data.trade_log.length - 1; i++){
		if(data.trade_log[i][3]!=0)
			{
			trade_row = '<tr>';
			date = new Date(data.trade_log[i][0]);
			// trade_row += '<td>'+dateFormat(date, "dS - mmmm - yyyy, h:MM:ss TT")+'</td>';
			// trade_row += '<td>'+dateFormat(date, "dd - mmm - yyyy, hh:MM:ss A")+'</td>';
			trade_row += '<td>'+moment(date).format("DD - MMM - YYYY, hh:mm:ss A")+'</td>';
			// trade_row += '<td>'+data.trade_log[i][1]+'</td>';
			trade_row += '<td>'+sym+' '+seg+'</td>';
			
			if (data.trade_log[i][2]=='BUY')
				trade_row += '<td class="buy_tag">'+data.trade_log[i][2]+'</td>'
			else
				trade_row += '<td class="sell_tag">'+data.trade_log[i][2]+'</td>'

			trade_row += '<td>'+data.trade_log[i][3]+'</td>'
			trade_row += '<td>'+parseFloat(data.trade_log[i][4]).toFixed(rounding)+'</td>'
			t_pnl = parseFloat(data.trade_log[i][5])
			if ( prev_pnl<t_pnl)
				trade_row += '<td class="profit">'+t_pnl.toFixed(2)+'</td>'
			else
				trade_row += '<td class="loss">'+t_pnl.toFixed(2)+'</td>'

			prev_pnl = t_pnl;
			if(data.trade_log[i][7]==undefined)
				akajdslkasj=1;
			else
				trade_row += '<td>'+data.trade_log[i][7]+'</td>'
			trade_row += '</tr>';
			trade_log.append(trade_row);
		}
	}

	transactions_table.append(trade_log);

	backtest_results_left.append(transactions_table);
	// backtest_results_left complete

	var backtest_results_right = $("<div>",{"class":"backtest_results_right"});
	backtest_results_right.append('<div class="fundamentals_section" id="fundamentals_section"><table><!--<caption>Stock Performance</caption>--><tr><td>Period High</td><td>'+parseFloat(data.period_high).toFixed(2)+'</td></tr><tr><td>Period Low</td><td>'+parseFloat(data.period_low).toFixed(2)+'</td></tr><tr><td>Period return</td><td>'+parseFloat(data.period_return).toFixed(2)+'%</td></tr><!--<tr><td>Period Volatility</td><td>10%</td></tr>--></table></div>');

	var actions_section = $("<div>",{"class":"actions_section"});
  transactions_table_label = [["Trigger date","Equity","Buy/Sell","Qty","Price","Cumulative P&L","Trigger Type"]];
	if(deployed_seg_sym.includes(seg+'_'+sym)){
		// actions_section.html('<table class="actions_buttons"><tr><td><button class="force_stop" onclick=\'force_stop(event,"'+deployed_seg_sym_deployment_uuid[seg+'_'+sym]+'")\'><span><img src="/static/imgs/icon-force-stop.png"></span>&nbsp;&nbsp;&nbsp;Stop</button></td></tr><tr><td><button class="download"><span><img src="/static/imgs/icon-download.png"></span>&nbsp;&nbsp;&nbsp;Download</button></td></tr></table><div class="social_buttons"><span><button><img src="/static/imgs/icon-linkedin.png"></button></span><span><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button><img src="/static/imgs/icon-facebook.png"></button></span><span><button><img src="/static/imgs/icon-twitter.png"></button></span></div>');
		actions_section.html('<!--<table class="actions_buttons" id="actions_buttons"><tr><td><button class="deploy_disabled" data-tooltip-top="Select strategies to deploy" onclick=\'force_stop(event,"'+deployed_seg_sym_deployment_uuid[seg+'_'+sym]+'")\'><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button><input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" disabled></td></tr><tr><td><button data-tooltip-top="Download backtest trade details" class="download" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button><button class="share" data-tooltip-top="Get sharable link" onclick="generate_shareable_link(event,\''+algo_uuid+'\',\''+seg+'_'+sym+'\')"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button id="linkedin_'+seg+'_'+sym+'" onclick=\'on_share_input_select(event,"linkedin","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-linkedin.png"></button></span><span style="display:none;"><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button id="fb_'+seg+'_'+sym+'" onclick=\'on_share_input_select(event,"fb","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-facebook.png"></button></span><span><button id="twitter_'+seg+'_'+sym+' onclick=\'on_share_input_select(event,"twitter","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-twitter.png"></button></span></div><div class="share_window"><input type="text" name="" onclick="on_share_input_select(event);"></div>-->');
	}
	else{
		actions_section.html('<!--<table class="actions_buttons" id="actions_buttons"><tr><td><button class="deploy" id="deploy" onclick=\'deploy_algorithm_popup("'+algo_uuid+'","'+sym+'","'+seg+'")\'><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button><input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" onclick="select_any(event,$(this))"></td></tr><tr><td><button data-tooltip-top="Download backtest trade details" class="download" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button><button class="share" data-tooltip-top="Get sharable link" onclick="generate_shareable_link(event,\''+algo_uuid+'\',\''+seg+'_'+sym+'\')"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button id="linkedin_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"linkedin","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-linkedin.png"></button></span><span style="display:none;"><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button id="fb_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"fb","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-facebook.png"></button></span><span><button id="twitter_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"twitter","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-twitter.png"></button></span></div><div class="share_window"><input type="text" name="" onclick="on_share_input_select(event);"></div>-->');
	}

	backtest_results_right.append(actions_section);
	// backtest_results_right complete

	backtest_share_button = '<div class="social_buttons" style=""><span><button id="linkedin_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"linkedin","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-linkedin.png"></button></span><span style="display:none;"><button id="whatsapp_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"whatsapp","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button id="fb_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"fb","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-facebook.png"></button></span><span><button id="twitter_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"twitter","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-twitter.png"></button></span></div>';

	if(deployed_seg_sym.includes(seg+'_'+sym)){
		// if algo is deployed
		backtest_results_multi_row = '<div class="live_indicator_detail"><span class="indicator_green"></span></div><div class="scrip_row_detail"> <div class="equity_section"> <p class="company_name">CANBK&nbsp;<span class="exc_symbol">NSE</span></p> </div> </div> <div class="ltp_row_detail"> <p class="token__'+seg+'_'+sym.replace(/ /g,'_-_')+'"><span class="ltp"><span class="sub_ltp">0.0</span></span></p> </div> <div class="pnl_row_detail"> <div class="pnl"> <p><span>0.0&nbsp;</span><span>(0.0%)&nbsp;</span></p> </div> </div> <div class="streak_row_detail"> <div class="streak"> <div class="streak_body"> <div class="wins"></div> <div class="losses"></div> </div> </div> </div> <div class="max_drawdown_row_detail"> <p>-0.0%</p> </div> <div class="winning_streak_row_detail"> <p>5</p> </div> <div class="losing_streak_row_detail"> <p>6</p> </div> <div class="action_deploy_row_detail"><button class="deploy_disabled" data-tooltip-top="Select strategies to deploy" onclick=\'force_stop(event,"'+deployed_seg_sym_deployment_uuid[seg+'_'+sym]+'")\'><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button></div> <div class="action_download_row_detail"> <button data-tooltip-top="Download backtest trade details" class="download" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button><button class="share" data-tooltip-top="Get sharable link" onclick="generate_shareable_link(event,\''+algo_uuid+'\',\''+seg+'_'+sym+'\')"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button id="linkedin_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"linkedin","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-linkedin.png"></button> </div> <div class="action_share_row_detail"> <button class="share" data-tooltip-top="Get sharable link" onclick="generate_shareable_link(event,\''+algo_uuid+'\',\''+seg+'_'+sym+'\')"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button id="linkedin_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"linkedin","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-linkedin.png"></button></span><span style="display:none;"><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button id="fb_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"fb","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-facebook.png"></button></span><span><button id="twitter_'+seg+'_'+sym+' onclick=\'on_share_input_select2(event,"twitter","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-twitter.png"></button> </div> <div class="checkbox_row_detail"> <input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" disabled> </div>';

		// backtest_row_first_html = '<div class="multiple_backtest_row_first"><div class="scrip_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="equity_section"> <p class="company_name">'+sym+' &nbsp;<span class="exc_symbol">'+seg+'</span></p> </div> </div> <div class="ltp_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p class="token__'+seg+'_'+sym+'"><span class="ltp"><span class="sub_ltp">0.0</span></span></p> </div> <div class="pnl_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="pnl"> <p><span><img src="'+img_url+'">&nbsp;</span><span style="color:'+color+'">'+parseFloat(data.final_pnl).toFixed(2)+'&nbsp;</span><span style="color:'+color+'"">('+parseFloat(data.final_pnl/data.max_cap_used*100).toFixed(2)+'%)&nbsp;</span></p> </div> </div> <div class="streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="streak"> <div class="streak_body"> <div data-tooltip-top="'+data.win_count+"/"+(data.win_count+data.loss_count)+' winning trades" class="wins" style="width:'+data.win_count/(data.win_count+data.loss_count)*100+'%"></div><div class="losses" data-tooltip-top="'+data.loss_count+"/"+(data.win_count+data.loss_count)+' losing trades" style="width:'+data.loss_count/(data.win_count+data.loss_count)*100+'%"></div> </div> </div> </div> <div class="max_drawdown_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p>'+parseFloat(data.max_draw).toFixed(2)+'%</p> </div> <div class="winning_streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p>'+data.winning_streak+'</p> </div> <div class="losing_streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p>'+data.lossing_streak+'</p> </div> <div class="action_deploy_row_detail"> <button class="deploy_disabled" onclick=\'force_stop(event,"'+deployed_seg_sym_deployment_uuid[seg+'_'+sym]+'")\'><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button> </div> <div class="action_download_row_detail"> <button class="download" data-tooltip-top="Download backtest trade details" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button> </div> <div class="action_share_row_detail"> ' +backtest_share_button+ ' </div> <div class="checkbox_row_detail"> <input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" disabled> </div></div>';

		backtest_row_first_html = '<div class="multiple_backtest_row_first"><div class="live_indicator_detail"><span class="indicator_green"></span></div><div class="scrip_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="equity_section"> <p class="company_name">'+sym+' &nbsp;<span class="exc_symbol">'+seg+'</span></p> </div> </div> <div class="ltp_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p class="token__'+seg+'_'+sym.replace('/','_--_').replace(/ /g,'_-_')+'"><span class="ltp"><span class="sub_ltp">0.0</span></span></p> </div> <div class="pnl_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="pnl"> <p><span><img src="'+img_url+'">&nbsp;</span><span style="color:'+color+'">'+parseFloat(data.final_pnl).toFixed(2)+'&nbsp;</span><span style="color:'+color+'"">('+parseFloat(data.final_pnl/data.max_cap_used*100).toFixed(2)+'%)&nbsp;</span></p> </div> </div> <div class="streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="streak"> <div class="streak_body"> <div data-tooltip-top="'+data.win_count+"/"+(data.win_count+data.loss_count)+' winning trades" class="wins" style="width:'+data.win_count/(data.win_count+data.loss_count)*100+'%"></div><div class="losses" data-tooltip-top="'+data.loss_count+"/"+(data.win_count+data.loss_count)+' losing trades" style="width:'+data.loss_count/(data.win_count+data.loss_count)*100+'%"></div> </div> </div> </div> <div class="signals_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+data.total_number_of_signals+'</p></div><div class="wins_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+data.win_count+'</p></div><div class="losses_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+data.loss_count+'</p></div><div class="winning_streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+data.winning_streak+'</p></div><div class="losing_streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+data.lossing_streak+'</p></div><div class="max_drawdown_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+parseFloat(data.max_draw).toFixed(2)+'%</p></div><div class="expand_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><img src="/static/imgs/bt_down.svg"></div><div class="action_download_row_detail"> <button class="download" data-tooltip-top="Download backtest trade details" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button> </div><div class="checkbox_row_detail"> <input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" onclick="select_any(event,$(this))" disabled> </div></div>';

		//<div class="max_drawdown_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p>'+parseFloat(data.max_draw).toFixed(2)+'%</p> </div> <div class="winning_streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p>'+data.winning_streak+'</p> </div> <div class="losing_streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p>'+data.lossing_streak+'</p> </div> <div class="action_deploy_row_detail"> <button class="deploy_disabled" onclick=\'force_stop(event,"'+deployed_seg_sym_deployment_uuid[seg+'_'+sym]+'")\'><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button> </div> <div class="action_download_row_detail"> <button class="download" data-tooltip-top="Download backtest trade details" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button> </div> <div class="action_share_row_detail"> ' +backtest_share_button+ ' </div> <div class="checkbox_row_detail"> <input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" disabled> </div></div>';

	}else{
		backtest_results_multi_row = '<div class="expand_row_detail"><img src="/static/imgs/bt_down.svg"></div><div class="live_indicator_detail"><span class="indicator_grey"></span></div><div class="scrip_row_detail"> <div class="equity_section"> <p class="company_name">CANBK&nbsp;<span class="exc_symbol">NSE</span></p> </div> </div> <div class="ltp_row_detail"> <p class="token__'+seg+'_'+sym.replace('/','_--_').replace(/ /g,'_-_')+'"><span class="ltp"><span class="sub_ltp">0.0</span></span></p> </div> <div class="pnl_row_detail"> <div class="pnl"> <p><span>3456.89&nbsp;</span><span>(1.2%)&nbsp;</span></p> </div> </div> <div class="streak_row_detail"> <div class="streak"> <div class="streak_body"> <div class="wins"></div> <div class="losses"></div> </div> </div> </div> <div class="max_drawdown_row_detail"> <p>'+parseFloat(data.max_draw).toFixed(2)+'%</p> </div> <div class="winning_streak_row_detail"> <p>5</p> </div> <div class="losing_streak_row_detail"> <p>6</p> </div> <div class="action_deploy_row_detail"><button class="deploy" id="deploy" onclick=\'deploy_algorithm_popup("'+algo_uuid+'","'+sym+'","'+seg+'")\'><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button></div> <div class="action_download_row_detail"> <button data-tooltip-top="Download backtest trade details" class="download" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button><button class="share" data-tooltip-top="Get sharable link" onclick="generate_shareable_link(event,\''+algo_uuid+'\',\''+seg+'_'+sym+'\')"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button id="linkedin_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"linkedin","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-linkedin.png"></button> </div> <div class="action_share_row_detail"> <button class="share" data-tooltip-top="Get sharable link" onclick="generate_shareable_link(event,\''+algo_uuid+'\',\''+seg+'_'+sym+'\')"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button id="linkedin_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"linkedin","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-linkedin.png"></button></span><span style="display:none;"><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button id="fb_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"fb","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-facebook.png"></button></span><span><button id="twitter_'+seg+'_'+sym+' onclick=\'on_share_input_select2(event,"twitter","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-twitter.png"></button> </div> <div class="checkbox_row_detail"> <input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" onclick="select_any(event,$(this))"></div>';

		// backtest_row_first_html = '<div class="multiple_backtest_row_first" ><div class="scrip_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="equity_section"> <p class="company_name">'+sym+' &nbsp;<span class="exc_symbol">'+seg+'</span></p> </div> </div> <div class="ltp_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p class="token__'+seg+'_'+sym+'"><span class="ltp"><span class="sub_ltp">0.0</span></span></p> </div> <div class="pnl_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="pnl"> <p><span><img src="'+img_url+'">&nbsp;</span><span style="color:'+color+'">'+parseFloat(data.final_pnl).toFixed(2)+'&nbsp;</span><span style="color:'+color+'"">('+parseFloat(data.final_pnl/data.max_cap_used*100).toFixed(2)+'%)&nbsp;</span></p> </div> </div> <div class="streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="streak"> <div class="streak_body"> <div data-tooltip-top="'+data.win_count+"/"+(data.win_count+data.loss_count)+' winning trades" class="wins" style="width:'+data.win_count/(data.win_count+data.loss_count)*100+'%"></div><div class="losses" data-tooltip-top="'+data.loss_count+"/"+(data.win_count+data.loss_count)+' losing trades" style="width:'+data.loss_count/(data.win_count+data.loss_count)*100+'%"></div> </div> </div> </div> <div class="max_drawdown_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p>'+parseFloat(data.max_draw).toFixed(2)+'%</p> </div> <div class="winning_streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p>'+data.winning_streak+'</p> </div> <div class="losing_streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p>'+data.lossing_streak+'</p> </div> <div class="action_deploy_row_detail"> <button class="deploy" id="deploy" onclick=\'deploy_algorithm_popup("'+algo_uuid+'","'+sym+'","'+seg+'")\'"><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button> </div> <div class="action_download_row_detail"> <button class="download" data-tooltip-top="Download backtest trade details" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button> </div> <div class="action_share_row_detail"> ' +backtest_share_button+ ' </div> <div class="checkbox_row_detail"> <input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" onclick="select_any(event,$(this))"> </div></div>';

		backtest_row_first_html = '<div class="multiple_backtest_row_first"><div class="live_indicator_detail"><span class="indicator_grey"></span></div><div class="scrip_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="equity_section"> <p class="company_name">'+sym+' &nbsp;<span class="exc_symbol">'+seg+'</span></p> </div> </div>  <div class="ltp_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p class="token__'+seg+'_'+sym.replace('/','_--_').replace(/ /g,'_-_')+'"><span class="ltp"><span class="sub_ltp">0.0</span></span></p> </div> <div class="pnl_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="pnl"> <p><span><img src="'+img_url+'">&nbsp;</span><span style="color:'+color+'">'+parseFloat(data.final_pnl).toFixed(2)+'&nbsp;</span><span style="color:'+color+'"">('+parseFloat(data.final_pnl/data.max_cap_used*100).toFixed(2)+'%)&nbsp;</span></p> </div> </div> <div class="streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="streak"> <div class="streak_body"> <div data-tooltip-top="'+data.win_count+"/"+(data.win_count+data.loss_count)+' winning trades" class="wins" style="width:'+data.win_count/(data.win_count+data.loss_count)*100+'%"></div><div class="losses" data-tooltip-top="'+data.loss_count+"/"+(data.win_count+data.loss_count)+' losing trades" style="width:'+data.loss_count/(data.win_count+data.loss_count)*100+'%"></div> </div> </div> </div> <div class="signals_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+data.total_number_of_signals+'</p></div><div class="wins_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+data.win_count+'</p></div><div class="losses_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+data.loss_count+'</p></div><div class="winning_streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+data.winning_streak+'</p></div><div class="losing_streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+data.lossing_streak+'</p></div><div class="max_drawdown_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+parseFloat(data.max_draw).toFixed(2)+'%</p></div><div class="expand_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><img src="/static/imgs/bt_down.svg"></div><div class="action_download_row_detail"> <button class="download" data-tooltip-top="Download backtest trade details" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button> </div><div class="checkbox_row_detail"> <input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" onclick="select_any(event,$(this))"> </div></div>';
	}


	backtest_results_row.find('.multiple_backtest_row_first_empty').replaceWith(backtest_row_first_html);
	backtest_results_row.removeClass('multiple_backtest_row_empty');


	backtest_results_row.find('.multiple_backtest_row_second .multiple_backtest_row_second_wrapper').append(backtest_results_left);
	backtest_results_row.find('.multiple_backtest_row_second .multiple_backtest_row_second_wrapper').append(backtest_results_right);
	
	// $('.backtest_results_body').append(backtest_results_row);
	// $('.multiple_backtest_body').append(backtest_results_row);

	transactions_section.click(function(){
		// alert($(this).attr("class"));
		$(this).toggleClass("expandable-color");
		$(this).parent('.backtest_results_left').find('.transactions_table').toggle();
		// $(this).parentsUntil(".backtest_results_row").find(".transactions_table").slideToggle();
		if($(this).find("img").attr("src") == "/static/imgs/new/transactions_dropdown.svg"){
		$(this).find("img").attr("src", "/static/imgs/new/transactions_dropup.svg");	
		}
		else{
		$(this).find("img").attr("src", "/static/imgs/new/transactions_dropdown.svg");
		}
	});

	// var ctx = document.getElementById(k.replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").getContext('2d');
	$('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").replaceWith('<canvas id="'+k.replace('/','_--_').replace(/ /g,'_-_')+'pnl_chartContainer_new"></canvas>');
	// var ctx = document.getElementById(k.replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").getContext('2d');
	
	// var pnl_chartContainer_new = new Chart(ctx,{
	// 	type: 'line',
	// 	scaleSteps : 4,
 //    	data: {
 //    		// labels: ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
	// 		datasets: [{
	// 		    label: 'P&L',
	// 		    data: processListToXYList(data.pnl),
	// 		    backgroundColor:'rgba(255,255,255,0)',
	// 		    borderColor: '#2288ff',
	// 		    borderWidth: 2,
	// 		    lineTension: 0,
	// 		    // pointStyle: 'star',
	// 		    // point: { radius: 0 },
	// 		    hoverRadius: 5
	// 		}]
 //    	},
 //    	options: {
 //    		scales: {
 //            yAxes: [{
 //            	gridLines: {
	// 				color: '#ecf0f1',
	// 				zeroLineBorderDash: [5, 5],
	// 				zeroLineColor: '#ecf0f1'
	// 					},
 //                ticks: {
 //                	fontColor: '#9ea1a4',
 //                    beginAtZero:true,
 //                    // maxTicksLimit:1
 //                    // ticks: {min: 0, max:4}
 //                }
 //            }],
 //            	xAxes: [{
	// 	        type: 'time',
	// 	        position: 'bottom',
	// 	         gridLines: {
	// 					display: false,
	// 					color: '#ecf0f1',
	// 					zeroLineBorderDash: [5, 5],
	// 					zeroLineColor: '#ecf0f1'
	// 			},
	// 			ticks: {
	// 				fontColor: '#9ea1a4'
	// 			},
	// 	        time: {
	// 	          displayFormats: {
	// 	          	// 'millisecond': 'MMM DD',
	// 	           //  'second': 'MMM DD',
	// 	           //  'minute': 'MMM DD',
	// 	           //  'hour': 'MMM DD',
	// 	           //  'day': 'MMM DD',
	// 	           //  'week': 'MMM DD',
	// 	           //  'month': 'MMM DD',
	// 	           //  'quarter': 'MMM DD',
	// 	            'year': 'YY MMM DD',
	// 	          }
	// 	        }
	// 	      }],
	// 		},
	// 		legend: {
	// 		    display: false,
	// 		},
	// 		// title: {
	// 		//     display: true,
	// 		//     text: 'P&L Performance',
	// 		//     fontColor: '#333333',
	// 		//     fontFamily: '"open_sansregular","AvenirNextLTPro",Arial,Helvetica,sans-serif',
	// 		//     fontStyle:'bold',
	// 		//     position: 'top',
	// 		//     fontSize: 16
	// 		// },
	// 		// legend: {
	// 		//     display: true,
	// 		//     labels: {
	// 		//         fontColor: '#666666'
	// 		//     }
	// 		// },
	// 		elements: { point: { radius: 0 } },	
	// 	}
	// });
	// $('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+' .brokerage_toggle:checkbox').on('change',function(e){
	// 	broker_toggle(e);
	// });
	setTimeout(function(){
		refresh_ltp_subscription();
	},1000);
}

function refresh_result_sequential_multi(algo_uuid,k,msg,seg,sym){
	backtest_result_response[k] = msg[k];
	data = msg[k];
	backtest_result_response[k]=data;
	// k = k.replace('&','.');
	var backtest_results_row = $("#"+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_'));

	var backtest_results_left = $("<div>",{"class":"backtest_results_left"});
	var results_section = $("<div>",{"class":"results_section"}).append('<div class="chart_section" id="chart_section"><div class="chart_header"><div class="equity_section"><!--<p class="company_name">'+sym+' <span class="exc_symbol">'+seg+'</span></p>--></div><div class="brokerage_section"><p data-tooltip-bottom="Adjusted for brokerage and other charges (does not include stamp duty and DP charges)">Brokerage&nbsp;&nbsp;&nbsp;<label class="switch"><input class="brokerage_toggle" id="'+k.replace('/','_--_').replace(/ /g,'_-_')+'" type="checkbox"><span class="slider"></span></label></p></div></div><div class="chart_body"><canvas id="'+k.replace('/','_--_').replace(/ /g,'_-_')+'pnl_chartContainer_new"></canvas></div></div>');
	//+data.win_count/(data.win_count+data.loss_count)+
	color = '#06d092';
	img_url = "/static/imgs/icon-arrow-up-green.png";
	if(data.final_pnl<0){
		color = '#ff4343';
		img_url = "/static/imgs/icon-arrow-down-red.png";
	}
	var pnl_section = $("<div>",{"class":"pnl_section", "id":"pnl_section"}).append('<!--<div class="pnl"><p>P&L&nbsp;<span><img src="'+img_url+'">&nbsp;</span><span style="color:'+color+'">'+parseFloat(data.final_pnl).toFixed(2)+'&nbsp;</span><span style="color:'+color+'"">('+parseFloat(data.final_pnl/data.max_cap_used*100).toFixed(2)+'%)&nbsp;</span></p></div><div class="streak"><div class="streak_body"><div data-tooltip-top="'+data.win_count+"/"+(data.win_count+data.loss_count)+' winning trades" class="wins" style="width:'+data.win_count/(data.win_count+data.loss_count)*100+'%"></div><div class="losses" data-tooltip-top="'+data.loss_count+"/"+(data.win_count+data.loss_count)+' losing trades" style="width:'+data.loss_count/(data.win_count+data.loss_count)*100+'%"></div></div></div>--><div class="results_table"><table><!--<td>Alpha</td><td>0.079</td></tr><tr><td>Beta</td><td>0.597</td></tr>--><!--<tr><td>Volatility</td><td>'+parseFloat(data.volatility).toFixed(2)+'%</td></tr><tr><td>Sharpe Ratio</td><td>'+parseFloat(data.sharpe).toFixed(2)+'</td></tr>--><!--<tr><td>Sortino</td><td>'+parseFloat(data.volatility).toFixed(2)+'</td></tr>-->' +'<tr><td>Total number of signals</td><td>'+data.total_number_of_signals+'</td></tr>'+'<tr><td>Number of wins</td><td>'+data.win_count+'</td></tr>'+'<tr><td>Number of losses</td><td>'+data.loss_count+'</td></tr>'+'<tr><td>Winning streak</td><td>'+data.winning_streak+'</td></tr>'+'<tr><td>Losing streak</td><td>'+data.lossing_streak+'</td></tr>'+'<tr><td>Max gains</td><td>'+parseFloat(data.maximum_gain).toFixed(2)+'</td></tr>'+'<tr><td>Max loss</td><td>'+parseFloat(data.maximum_loss).toFixed(2)+'</td></tr>'+'<tr><td>Avg gain/winning trade</td><td>'+parseFloat(data.average_gain_per_winning_trade).toFixed(2)+'</td></tr>'+'<tr><td>Avg loss/losing trade</td><td>'+parseFloat(data.average_gain_per_losing_trade).toFixed(2)+'</td></tr>' +'<tr><td>Max Drawdown</td><td>'+parseFloat(data.max_draw).toFixed(2)+'%</td></tr></table></div>');
	results_section.append(pnl_section);

	backtest_results_left.append(results_section);

	var transactions_section = $('<div>',{"class":"transactions_section", "id":"transactions_section"}).append('<p>Transaction Details <span><img src="/static/imgs/new/transactions_dropdown.svg"></span></p>');

	backtest_results_left.append(transactions_section);

	var transactions_table = $("<div>",{"class":"transactions_table","style":"display:none;"});

	var trade_log = $("<table>",{}).append('<tr><th>Trigger date</th><th>Equity</th><th>Buy/Sell</th><th>Qty</th><th>Price</th><th>Cumulative P&L</th><th>Trigger type</th></tr>');
	var prev_pnl = 0;
	rounding = 2
	if (seg=='CDS-FUT')
		rounding = 4
	for(var i = 0; i <= data.trade_log.length - 1; i++){
		if(data.trade_log[i][3]!=0)
			{
			trade_row = '<tr>';
			date = new Date(data.trade_log[i][0]);
			// trade_row += '<td>'+dateFormat(date, "dS - mmmm - yyyy, h:MM:ss TT")+'</td>';
			// trade_row += '<td>'+dateFormat(date, "dd - mmm - yyyy, hh:MM:ss A")+'</td>';
			trade_row += '<td>'+moment(date).format("DD - MMM - YYYY, hh:mm:ss A")+'</td>';
			// trade_row += '<td>'+data.trade_log[i][1]+'</td>';
			trade_row += '<td>'+sym+' '+seg+'</td>';
			
			if (data.trade_log[i][2]=='BUY')
				trade_row += '<td class="buy_tag">'+data.trade_log[i][2]+'</td>'
			else
				trade_row += '<td class="sell_tag">'+data.trade_log[i][2]+'</td>'

			trade_row += '<td>'+data.trade_log[i][3]+'</td>'
			trade_row += '<td>'+parseFloat(data.trade_log[i][4]).toFixed(rounding)+'</td>'
			t_pnl = parseFloat(data.trade_log[i][5])
			if ( prev_pnl<=t_pnl)
				trade_row += '<td class="profit">'+t_pnl.toFixed(2)+'</td>'
			else
				trade_row += '<td class="loss">'+t_pnl.toFixed(2)+'</td>'
			prev_pnl = t_pnl;

			trade_row += '<td>'+data.trade_log[i][7]+'</td>'
			trade_row += '</tr>';
			trade_log.append(trade_row);
		}
	}

	transactions_table.append(trade_log);

	backtest_results_left.append(transactions_table);
	// backtest_results_left complete

	var backtest_results_right = $("<div>",{"class":"backtest_results_right"});
	backtest_results_right.append('<div class="fundamentals_section" id="fundamentals_section"><table><!--<caption>Stock Performance</caption>--><tr><td>Period High</td><td>'+parseFloat(data.period_high).toFixed(2)+'</td></tr><tr><td>Period Low</td><td>'+parseFloat(data.period_low).toFixed(2)+'</td></tr><tr><td>Period return</td><td>'+parseFloat(data.period_return).toFixed(2)+'%</td></tr><!--<tr><td>Period Volatility</td><td>10%</td></tr>--></table></div>');

	var actions_section = $("<div>",{"class":"actions_section"});
  transactions_table_label = [["Trigger date","Equity","Buy/Sell","Qty","Price","Cumulative P&L","Trigger Type"]];
	if(deployed_seg_sym.includes(seg+'_'+sym)){
		// actions_section.html('<table class="actions_buttons"><tr><td><button class="force_stop" onclick=\'force_stop(event,"'+deployed_seg_sym_deployment_uuid[seg+'_'+sym]+'")\'><span><img src="/static/imgs/icon-force-stop.png"></span>&nbsp;&nbsp;&nbsp;Stop</button></td></tr><tr><td><button class="download"><span><img src="/static/imgs/icon-download.png"></span>&nbsp;&nbsp;&nbsp;Download</button></td></tr></table><div class="social_buttons"><span><button><img src="/static/imgs/icon-linkedin.png"></button></span><span><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button><img src="/static/imgs/icon-facebook.png"></button></span><span><button><img src="/static/imgs/icon-twitter.png"></button></span></div>');
		actions_section.html('<!--<table class="actions_buttons" id="actions_buttons"><tr><td><button class="deploy_disabled" data-tooltip-top="Select strategies to deploy" onclick=\'force_stop(event,"'+deployed_seg_sym_deployment_uuid[seg+'_'+sym]+'")\'><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button><input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" disabled></td></tr><tr><td><button data-tooltip-top="Download backtest trade details" class="download" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button><button class="share" data-tooltip-top="Get sharable link" onclick="generate_shareable_link(event,\''+algo_uuid+'\',\''+seg+'_'+sym+'\')"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button id="linkedin_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"linkedin","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-linkedin.png"></button></span><span style="display:none;"><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button id="fb_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"fb","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-facebook.png"></button></span><span><button id="twitter_'+seg+'_'+sym+' onclick=\'on_share_input_select2(event,"twitter","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-twitter.png"></button></span></div><div class="share_window"><input type="text" name="" onclick="on_share_input_select(event);"></div>-->');
	}
	else{
		actions_section.html('<!--<table class="actions_buttons" id="actions_buttons"><tr><td><button class="deploy" id="deploy" onclick=\'deploy_algorithm_popup("'+algo_uuid+'","'+sym+'","'+seg+'")\'><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button><input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" onclick="select_any(event,$(this))"></td></tr><tr><td><button data-tooltip-top="Download backtest trade details" class="download" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button><button class="share" data-tooltip-top="Get sharable link" onclick="generate_shareable_link(event,\''+algo_uuid+'\',\''+seg+'_'+sym+'\')"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button id="linkedin_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"linkedin","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-linkedin.png"></button></span><span style="display:none;"><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button id="fb_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"fb","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-facebook.png"></button></span><span><button id="twitter_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"twitter","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-twitter.png"></button></span></div><div class="share_window"><input type="text" name="" onclick="on_share_input_select(event);"></div>-->');
	}

	backtest_results_right.append(actions_section);
	// backtest_results_right complete
	// backtest_results_row.html('');

	backtest_share_button = '<button class="share" data-tooltip-top="Get sharable link" onclick="generate_shareable_link(event,\''+algo_uuid+'\',\''+seg+'_'+sym+'\')"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button id="linkedin_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"linkedin","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-linkedin.png"></button> </div> <div class="action_share_row_detail"> <button class="share" data-tooltip-top="Get sharable link" onclick="generate_shareable_link(event,\''+algo_uuid+'\',\''+seg+'_'+sym+'\')"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button id="linkedin_'+seg+'_'+sym+'" onclick=\'on_share_input_select(event,"linkedin","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-linkedin.png"></button></span><span style="display:none;"><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button id="fb_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"fb","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-facebook.png"></button></span><span><button id="twitter_'+seg+'_'+sym+' onclick=\'on_share_input_select2(event,"twitter","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-twitter.png"></button>';

	// backtest_share_button = '<button class="share" data-tooltip-top="Get sharable link" onclick="generate_shareable_link(event,\''+algo_uuid+'\',\''+seg+'_'+sym+'\')"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button id="linkedin_'+seg+'_'+sym+'" onclick=\'on_share_input_select(event,"linkedin","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-linkedin.png"></button></span><span style="display:none;"><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button id="fb_'+seg+'_'+sym+'" onclick=\'on_share_input_select(event,"fb","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-facebook.png"></button></span><span><button id="twitter_'+seg+'_'+sym+'" onclick=\'on_share_input_select(event,"twitter","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-twitter.png"></button></span></div><div class="share_window"><input type="text" name="" onclick="on_share_input_select(event);"></div>';

	backtest_share_button = '<div class="social_buttons" style=""><span><button id="linkedin_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"linkedin","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-linkedin.png"></button></span><span style="display:none;"><button id="whatsapp_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"whatsapp","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button id="fb_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"fb","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-facebook.png"></button></span><span><button id="twitter_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"twitter","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-twitter.png"></button></span></div>';

	if(deployed_seg_sym.includes(seg+'_'+sym)){
		// if algo is deployed
		backtest_results_multi_row = '<div class="expand_row_detail"><img src="/static/imgs/bt_down.svg"></div><div class="live_indicator_detail"><span class="indicator_green"></span></div><div class="scrip_row_detail"> <div class="equity_section"> <p class="company_name">CANBK&nbsp;<span class="exc_symbol">NSE</span></p> </div> </div> <div class="ltp_row_detail"> <p class="token__'+seg+'_'+sym.replace(/ /g,'_-_')+'"><span class="ltp"><span class="sub_ltp">0.0</span></span></p> </div> <div class="pnl_row_detail"> <div class="pnl"> <p><span>0.0&nbsp;</span><span>(0.0%)&nbsp;</span></p> </div> </div> <div class="streak_row_detail"> <div class="streak"> <div class="streak_body"> <div class="wins"></div> <div class="losses"></div> </div> </div> </div> <div class="max_drawdown_row_detail"> <p>-0.0%</p> </div> <div class="winning_streak_row_detail"> <p>5</p> </div> <div class="losing_streak_row_detail"> <p>6</p> </div> <div class="action_deploy_row_detail"><button class="deploy_disabled" data-tooltip-top="Select strategies to deploy" onclick=\'force_stop(event,"'+deployed_seg_sym_deployment_uuid[seg+'_'+sym]+'")\'><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button></div> <div class="action_download_row_detail"> <button data-tooltip-top="Download backtest trade details" class="download" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button><button class="share" data-tooltip-top="Get sharable link" onclick="generate_shareable_link(event,\''+algo_uuid+'\',\''+seg+'_'+sym+'\')"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button id="linkedin_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"linkedin","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-linkedin.png"></button> </div> <div class="action_share_row_detail"> <button class="share" data-tooltip-top="Get sharable link" onclick="generate_shareable_link(event,\''+algo_uuid+'\',\''+seg+'_'+sym+'\')"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button id="linkedin_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"linkedin","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-linkedin.png"></button></span><span style="display:none;"><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button id="fb_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"fb","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-facebook.png"></button></span><span><button id="twitter_'+seg+'_'+sym+' onclick=\'on_share_input_select2(event,"twitter","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-twitter.png"></button> </div> <div class="checkbox_row_detail"> <input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" disabled> </div>';

		// backtest_row_first_html = '<div class="multiple_backtest_row_first"><div class="scrip_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="equity_section"> <p class="company_name">'+sym+' &nbsp;<span class="exc_symbol">'+seg+'</span></p> </div> </div> <div class="ltp_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p class="token__'+seg+'_'+sym+'"><span class="ltp"><span class="sub_ltp">0.0</span></span></p> </div> <div class="pnl_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="pnl"> <p><span><img src="'+img_url+'">&nbsp;</span><span style="color:'+color+'">'+parseFloat(data.final_pnl).toFixed(2)+'&nbsp;</span><span style="color:'+color+'"">('+parseFloat(data.final_pnl/data.max_cap_used*100).toFixed(2)+'%)&nbsp;</span></p> </div> </div> <div class="streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="streak"> <div class="streak_body"> <div data-tooltip-top="'+data.win_count+"/"+(data.win_count+data.loss_count)+' winning trades" class="wins" style="width:'+data.win_count/(data.win_count+data.loss_count)*100+'%"></div><div class="losses" data-tooltip-top="'+data.loss_count+"/"+(data.win_count+data.loss_count)+' losing trades" style="width:'+data.loss_count/(data.win_count+data.loss_count)*100+'%"></div> </div> </div> </div> <div class="max_drawdown_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p>'+parseFloat(data.max_draw).toFixed(2)+'%</p> </div> <div class="winning_streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p>'+data.winning_streak+'</p> </div> <div class="losing_streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p>'+data.lossing_streak+'</p> </div> <div class="action_deploy_row_detail"> <button class="deploy_disabled" onclick=\'force_stop(event,"'+deployed_seg_sym_deployment_uuid[seg+'_'+sym]+'")\'><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button> </div> <div class="action_download_row_detail"> <button class="download" data-tooltip-top="Download backtest trade details" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button> </div> <div class="action_share_row_detail"> ' +backtest_share_button+ ' </div> <input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" disabled"></div>';
		backtest_row_first_html = '<div class="multiple_backtest_row_first"><div class="live_indicator_detail"><span class="indicator_green"></span></div><div class="scrip_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="equity_section"> <p class="company_name">'+sym+' &nbsp;<span class="exc_symbol">'+seg+'</span></p> </div> </div> <div class="ltp_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p class="token__'+seg+'_'+sym.replace('/','_--_').replace(/ /g,'_-_')+'"><span class="ltp"><span class="sub_ltp">0.0</span></span></p> </div> <div class="pnl_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="pnl"> <p><span><img src="'+img_url+'">&nbsp;</span><span style="color:'+color+'">'+parseFloat(data.final_pnl).toFixed(2)+'&nbsp;</span><span style="color:'+color+'"">('+parseFloat(data.final_pnl/data.max_cap_used*100).toFixed(2)+'%)&nbsp;</span></p> </div> </div> <div class="streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="streak"> <div class="streak_body"> <div data-tooltip-top="'+data.win_count+"/"+(data.win_count+data.loss_count)+' winning trades" class="wins" style="width:'+data.win_count/(data.win_count+data.loss_count)*100+'%"></div><div class="losses" data-tooltip-top="'+data.loss_count+"/"+(data.win_count+data.loss_count)+' losing trades" style="width:'+data.loss_count/(data.win_count+data.loss_count)*100+'%"></div> </div> </div> </div> <div class="signals_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+data.total_number_of_signals+'</p></div><div class="wins_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+data.win_count+'</p></div><div class="losses_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+data.loss_count+'</p></div><div class="winning_streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+data.winning_streak+'</p></div><div class="losing_streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+data.lossing_streak+'</p></div><div class="max_drawdown_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+parseFloat(data.max_draw).toFixed(2)+'%</p></div><div class="expand_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><img src="/static/imgs/bt_down.svg"></div><div class="action_download_row_detail"> <button class="download" data-tooltip-top="Download backtest trade details" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button> </div><div class="checkbox_row_detail"><input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" disabled> </div></div>';

	}else{
		backtest_results_multi_row = '<div class="live_indicator_detail"><span class="indicator_grey"></span></div><div class="scrip_row_detail"> <div class="equity_section"> <p class="company_name">CANBK&nbsp;<span class="exc_symbol">NSE</span></p> </div> </div> <div class="ltp_row_detail"> <p class="token__'+seg+'_'+sym.replace('/','_--_').replace(/ /g,'_-_')+'"><span class="ltp"><span class="sub_ltp">0.0</span></span></p> </div> <div class="pnl_row_detail"> <div class="pnl"> <p><span>0.0&nbsp;</span><span>(0.0%)&nbsp;</span></p> </div> </div> <div class="streak_row_detail"> <div class="streak"> <div class="streak_body"> <div class="wins"></div> <div class="losses"></div> </div> </div> </div> <div class="max_drawdown_row_detail"> <p>'+parseFloat(data.max_draw).toFixed(2)+'%</p> </div> <div class="winning_streak_row_detail"> <p>5</p> </div> <div class="losing_streak_row_detail"> <p>6</p> </div> <div class="action_deploy_row_detail"><button class="deploy" id="deploy" onclick=\'deploy_algorithm_popup("'+algo_uuid+'","'+sym+'","'+seg+'")\'><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button></div> <div class="action_download_row_detail"> <button data-tooltip-top="Download backtest trade details" class="download" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button><button class="share" data-tooltip-top="Get sharable link" onclick="generate_shareable_link(event,\''+algo_uuid+'\',\''+seg+'_'+sym+'\')"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button id="linkedin_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"linkedin","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-linkedin.png"></button> </div> <div class="action_share_row_detail"> <button class="share" data-tooltip-top="Get sharable link" onclick="generate_shareable_link(event,\''+algo_uuid+'\',\''+seg+'_'+sym+'\')"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button id="linkedin_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"linkedin","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-linkedin.png"></button></span><span style="display:none;"><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button id="fb_'+seg+'_'+sym+'" onclick=\'on_share_input_select2(event,"fb","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-facebook.png"></button></span><span><button id="twitter_'+seg+'_'+sym+' onclick=\'on_share_input_select2(event,"twitter","'+algo_uuid+'","'+seg+'_'+sym+'");\'><img src="/static/imgs/icon-twitter.png"></button> </div> <div class="checkbox_row_detail"> <input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" onclick="select_any(event,$(this))"></div>';

		// backtest_row_first_html = '<div class="multiple_backtest_row_first" ><div class="scrip_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="equity_section"> <p class="company_name">'+sym+' &nbsp;<span class="exc_symbol">'+seg+'</span></p> </div> </div> <div class="ltp_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p class="token__'+seg+'_'+sym+'"><span class="ltp"><span class="sub_ltp">0.0</span></span></p> </div> <div class="pnl_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="pnl"> <p><span><img src="'+img_url+'">&nbsp;</span><span style="color:'+color+'">'+parseFloat(data.final_pnl).toFixed(2)+'&nbsp;</span><span style="color:'+color+'"">('+parseFloat(data.final_pnl/data.max_cap_used*100).toFixed(2)+'%)&nbsp;</span></p> </div> </div> <div class="streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="streak"> <div class="streak_body"> <div data-tooltip-top="'+data.win_count+"/"+(data.win_count+data.loss_count)+' winning trades" class="wins" style="width:'+data.win_count/(data.win_count+data.loss_count)*100+'%"></div><div class="losses" data-tooltip-top="'+data.loss_count+"/"+(data.win_count+data.loss_count)+' losing trades" style="width:'+data.loss_count/(data.win_count+data.loss_count)*100+'%"></div> </div> </div> </div> <div class="max_drawdown_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p>'+parseFloat(data.max_draw).toFixed(2)+'%</p> </div> <div class="winning_streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p>'+data.winning_streak+'</p> </div> <div class="losing_streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p>'+data.lossing_streak+'</p> </div> <div class="action_deploy_row_detail"> <button class="deploy" id="deploy" onclick=\'deploy_algorithm_popup("'+algo_uuid+'","'+sym+'","'+seg+'")\'"><span><img src="/static/imgs/icon-deploy.png"></span>Deploy</button> </div> <div class="action_download_row_detail"> <button class="download" data-tooltip-top="Download backtest trade details" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button> </div> <div class="action_share_row_detail"> ' +backtest_share_button+ ' </div> <div class="checkbox_row_detail"> <input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" onclick="select_any(event,$(this))"> </div></div>';
		backtest_row_first_html = '<div class="multiple_backtest_row_first"><div class="live_indicator_detail"><span class="indicator_grey"></span></div><div class="scrip_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="equity_section"> <p class="company_name">'+sym+' &nbsp;<span class="exc_symbol">'+seg+'</span></p> </div> </div> <div class="ltp_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <p class="token__'+seg+'_'+sym.replace('/','_--_').replace(/ /g,'_-_')+'"><span class="ltp"><span class="sub_ltp">0.0</span></span></p> </div> <div class="pnl_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="pnl"> <p><span><img src="'+img_url+'">&nbsp;</span><span style="color:'+color+'">'+parseFloat(data.final_pnl).toFixed(2)+'&nbsp;</span><span style="color:'+color+'"">('+parseFloat(data.final_pnl/data.max_cap_used*100).toFixed(2)+'%)&nbsp;</span></p> </div> </div> <div class="streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"> <div class="streak"> <div class="streak_body"> <div data-tooltip-top="'+data.win_count+"/"+(data.win_count+data.loss_count)+' winning trades" class="wins" style="width:'+data.win_count/(data.win_count+data.loss_count)*100+'%"></div><div class="losses" data-tooltip-top="'+data.loss_count+"/"+(data.win_count+data.loss_count)+' losing trades" style="width:'+data.loss_count/(data.win_count+data.loss_count)*100+'%"></div> </div> </div> </div> <div class="signals_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+data.total_number_of_signals+'</p></div><div class="wins_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+data.win_count+'</p></div><div class="losses_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+data.loss_count+'</p></div><div class="winning_streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+data.winning_streak+'</p></div><div class="losing_streak_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+data.lossing_streak+'</p></div><div class="max_drawdown_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><p>'+parseFloat(data.max_draw).toFixed(2)+'%</p></div><div class="expand_row_detail" onclick="toggle_multi_backtest_row(event,\''+k+'\')"><img src="/static/imgs/bt_down.svg"></div><div class="action_download_row_detail"> <button class="download" data-tooltip-top="Download backtest trade details" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button> </div><div class="checkbox_row_detail"> <input type="checkbox" name="" class="deploy_checkbox" id="deploy_checkbox__'+seg+'_'+sym+'" onclick="select_any(event,$(this))"> </div></div>';
	}


	backtest_results_row.find('.multiple_backtest_row_first_empty').replaceWith(backtest_row_first_html);
	backtest_results_row.removeClass('multiple_backtest_row_empty');


	backtest_results_row.find('.multiple_backtest_row_second .multiple_backtest_row_second_wrapper').append(backtest_results_left);
	backtest_results_row.find('.multiple_backtest_row_second .multiple_backtest_row_second_wrapper').append(backtest_results_right);
	
	// $('.backtest_results_body').append(backtest_results_row);

	transactions_section.click(function(){
		// alert($(this).attr("class"));
		$(this).toggleClass("expandable-color");
		$(this).parent('.backtest_results_left').find('.transactions_table').toggle();
		// $(this).parentsUntil(".backtest_results_row").find(".transactions_table").slideToggle();
		if($(this).find("img").attr("src") == "/static/imgs/new/transactions_dropdown.svg"){
		$(this).find("img").attr("src", "/static/imgs/new/transactions_dropup.svg");	
		}
		else{
		$(this).find("img").attr("src", "/static/imgs/new/transactions_dropdown.svg");
		}
	});

	// backtest_results_row.find('.multiple_backtest_row_second').show();
	// var ctx = document.getElementById(k.replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").getContext('2d');
	$('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").replaceWith('<canvas id="'+k.replace('/','_--_').replace(/ /g,'_-_')+'pnl_chartContainer_new"></canvas>');

	// var ctx = document.getElementById(k.replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").getContext('2d');
	// return;
	
	// var pnl_chartContainer_new = new Chart(ctx,{
	// 	type: 'line',
	// 	scaleSteps : 4,
 //    	data: {
 //    		// labels: ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
	// 		datasets: [{
	// 		    label: 'P&L',
	// 		    data: processListToXYList(data.pnl),
	// 		    backgroundColor:'rgba(255,255,255,0)',
	// 		    borderColor: '#2288ff',
	// 		    borderWidth: 2,
	// 		    lineTension: 0,
	// 		    // pointStyle: 'star',
	// 		    // point: { radius: 0 },
	// 		    hoverRadius: 5
	// 		}]
 //    	},
 //    	options: {
 //    		scales: {
 //            yAxes: [{
 //            	gridLines: {
	// 				color: '#ecf0f1',
	// 				zeroLineBorderDash: [5, 5],
	// 				zeroLineColor: '#ecf0f1'
	// 					},
 //                ticks: {
 //                	fontColor: '#9ea1a4',
 //                    beginAtZero:true,
 //                    // maxTicksLimit:1
 //                    // ticks: {min: 0, max:4}
 //                }
 //            }],
 //            	xAxes: [{
	// 	        type: 'time',
	// 	        position: 'bottom',
	// 	         gridLines: {
	// 					display: false,
	// 					color: '#ecf0f1',
	// 					zeroLineBorderDash: [5, 5],
	// 					zeroLineColor: '#ecf0f1'
	// 			},
	// 			ticks: {
	// 				fontColor: '#9ea1a4'
	// 			},
	// 	        time: {
	// 	          displayFormats: {
	// 	          	// 'millisecond': 'MMM DD',
	// 	           //  'second': 'MMM DD',
	// 	           //  'minute': 'MMM DD',
	// 	           //  'hour': 'MMM DD',
	// 	           //  'day': 'MMM DD',
	// 	           //  'week': 'MMM DD',
	// 	           //  'month': 'MMM DD',
	// 	           //  'quarter': 'MMM DD',
	// 	            'year': 'YY MMM DD',
	// 	          }
	// 	        }
	// 	      }],
	// 		},
	// 		legend: {
	// 		    display: false,
	// 		},
	// 		// title: {
	// 		//     display: true,
	// 		//     text: 'P&L Performance',
	// 		//     fontColor: '#333333',
	// 		//     fontFamily: '"open_sansregular","AvenirNextLTPro",Arial,Helvetica,sans-serif',
	// 		//     fontStyle:'bold',
	// 		//     position: 'top',
	// 		//     fontSize: 16
	// 		// },
	// 		// legend: {
	// 		//     display: true,
	// 		//     labels: {
	// 		//         fontColor: '#666666'
	// 		//     }
	// 		// },
	// 		elements: { point: { radius: 0 } },	
	// 	}
	// });
	// $('#'+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+' .brokerage_toggle:checkbox').on('change',function(e){
	// 	broker_toggle(e);
	// });
	fetch_billing_status();
	// attach_toggle_multi_backtest_row(k);
	setTimeout(function(){
		refresh_ltp_subscription();
	},1000);
}

function run_backtest_recusive_multi(symbols,params,count,max_count){
	if(count==max_count)
		return;
	params['symbols']=[symbols[count]];
	bt_url = "";
	lmda_vs_ec2_select();
	switch(url_selector){
		case 1: bt_url = bt_url2;
				break;
		case 2: bt_url = bt_url2;
				break;
		default:bt_url = bt_url2;
	}
	var settings = {
	  "async": true,
	  "crossDomain": true,
	  "url": bt_url,
	  "beforeSend": function() {
           myBtBarLoader(symbols[count][0]+'_'+symbols[count][1],bt_loading_time);
      },
	  "method": "POST",
	  "headers": {
	  },
	  // "data": "{\"action_str\":\"5 min sma crosses 10 min sma\",\"action_type\":\"BUY\",\"symbols\":[[\"NSE\",\"CANBK\"],[\"NSE\",\"ICICIBANK\"]],\n         \"quantity\":1,\"initial_capital\":1000000,\"dt_start\":\"09/11/2017\",\"dt_stop\":\"09/12/2017\",\"time_frame\":\"min\",\"commission\":40,\n         \"take_profit\":1,\"stop_loss\":0.5\n         }",
	  "data":JSON.stringify(params),
	  "timeout": 200000,//40 sec timeout
	}

	$.ajax(settings).done(function(msg){
		// try {
		// 	// var msg = JSON.parse(msg);
		// 	if(Object.keys(msg).length>0) // if the response has data clear the result rows
		// 		// $('.backtest_results_body').html('');
		// 	for(var k in msg)
		// 	{
		// 		data = msg[k];
		// 		[seg,sym] = [null,null];
		// 		try{
		// 			[seg,sym] = data.symbol.split("_");
		// 			refresh_result_sequential(params.algo_uuid,k,msg,seg,sym);
		// 		}
		// 		catch(e){
		// 			// show the respective error msg in the plot region
		// 			refresh_error_sequential(symbols[count][0]+'_'+symbols[count][1],k,msg);
		// 			;
		// 		}
		// 	}
		// }
		try {
			if(msg['status']=='error'){
				try{
					ga('send', {hitType: 'event', eventCategory: 'Backtest error', eventAction: msg['error_msg'], eventLabel: 'Backtest page', eventValue:1});
				}
				catch(e){
					
				}
				refresh_error_sequential2_multi(symbols[count][0]+'_'+symbols[count][1],k,msg['error_msg']);
			}
			else{
				// var msg = JSON.parse(msg);
				if(Object.keys(msg).length>0) // if the response has data clear the result rows
					// $('.backtest_results_body').html('');
				for(var k in msg)
				{
					data = msg[k];
					if(data['error_msg']!=undefined){
						refresh_error_sequential2_multi(symbols[count][0]+'_'+symbols[count][1],k,data['error_msg'])
						try{
							ga('send', {hitType: 'event', eventCategory: 'Backtest error', eventAction: data['error_msg'], eventLabel: 'Backtest page', eventValue:1});
						}catch(e){

						}
					}else{
						[seg,sym] = [null,null];
						try{
							[seg,sym] = data.symbol.split("_");

							try{
								ga('send', {hitType: 'event', eventCategory: 'Backtest successful', eventAction: 'Backtest successful', eventLabel: 'Backtest page', eventValue:1});
							}
							catch(e){
								
							}
							refresh_result_sequential_multi(params.algo_uuid,k,msg,seg,sym);
						}
						catch(e){
							// show the respective error msg in the plot region
							// try{
							// 	ga('send', {hitType: 'event', eventCategory: 'Backtest', eventAction: 'Backtest error (Individual)', eventLabel: 'Backtest page'});
							// }
							// catch(e){
								
							// }
							refresh_error_sequential_multi(symbols[count][0]+'_'+symbols[count][1],k,msg);
						}
					}
				}
			}
		}
		catch(err) {
			console.log(err);
		  	$(".loader_parent_backtest").fadeOut();
		  	$('.ti_msg_popup').show();
			$('.ti_msg_popup> div').show(); 
			$('.ti_msg').html('No trades were executed for the algo');
			clear_plot();
		}
		count += 1;
		if(count<max_count)
		{
			// continue loop_backtest;
			run_backtest_recusive_multi(symbols,params,count,max_count)
		}else{
			// break finished_backtest;
			$('.run_backtest').html('Run Backtest');
			$('.run_backtest').attr('style',"background-color: #07c389;cursor: pointer !important");
			$('.run_backtest').attr('onclick','run_backtest_sequential()');
			return
		}
	}).fail(function(){
		$('.run_backtest').html('Run Backtest');
		$('.run_backtest').attr('style',"background-color: #07c389;cursor: pointer !important");
		$('.run_backtest').attr('onclick','run_backtest_sequential()');
	}).complete(function(){
    if(count==max_count){
  		$('.run_backtest').html('Run Backtest');
  		$('.run_backtest').attr('style',"background-color: #07c389;cursor: pointer !important");
  		$('.run_backtest').attr('onclick','run_backtest_sequential()');
    }
	});
}

function processListToXYList(packedlist){
	var xyList = [];
	for(var i=0;i<packedlist.length;i++){
		xyList.push({
			x:new Date(packedlist[i][0]),
			y:parseFloat(packedlist[i][1].toFixed(2)),
			pnltext:parseFloat(packedlist[i][1].toFixed(2))
		});
	}
	return xyList;
}
function round(value, decimals) {
  return Number(Math.round(value+'e'+decimals)+'e-'+decimals);
}
function broker_cal(seg,sym,qty,price,type='CNC'){
  comm = '';
  if(seg=='MCX')
    {
      comm = sym.split(/[0-9]/)[0];
    }
	type = holding_type_latest;
	ttt = 0; // total tax and charges
	if(seg=='NSE')
	{
		turnover = Math.abs(qty)*price;
		if(type=='MIS')
		{
			ttt += (20<turnover*0.0001?20:turnover*0.0001);
		}
		ttt += (0.00325/100*turnover); //Transaction charges
		ttt += (0.18*ttt); // GST on broker+transaction charges
		if(type=='MIS' && qty<0)
			ttt += (0.025*turnover/100); // STT
		else if(type!='MIS')
			ttt += (0.1*turnover/100); // STT
		ttt += 15*(turnover/10000000); //SEBI charges
	}
	else if(seg=='NFO-FUT')
	{
		turnover = Math.abs(qty)*price;
		ttt += (20<turnover*0.0001?20:turnover*0.0001);
		ttt += 0.0021/100*turnover; //Transaction charges
		ttt += 0.18*ttt; // GST on broker+transaction charges
		if(qty<0)
			ttt += 0.01*turnover/100; // STT
		ttt += 15*(turnover/10000000); //SEBI charges
	}
	else if(seg=='CDS-FUT')
	{
		turnover = Math.abs(qty)*price;
		ttt += (20<turnover*0.0001?20:turnover*0.0001);
		ttt += 0.0009/100*turnover; //Transaction charges
		ttt += 0.0002/100*turnover; //Transaction charges
		ttt += 0.18*ttt; // GST on broker+transaction charges
		if(qty<0)
			ttt += 0.0; // STT
		ttt += 15*(turnover/10000000); //SEBI charges
	}
  else if(seg=='MCX' && comm!='')
  {
    group = COMMODITY_MULTIPLIER_MAP[comm].slice(-1);
    turnover = Math.abs(qty)*price;
    ttt += (20<turnover*0.0001?20:turnover*0.0001); // brokerage
    if(group=='a')
    {
      ttt += 0.0026/100*turnover; //Transaction charges
      ttt += 0.001/100*turnover; //Transaction charges
    }
    else if(group=='b')
    {
      switch(comm){
        case 'PEPPER':
          ttt += 0.00005/100*turnover; //Transaction charges
          break;
        case 'CASTORSEED':
          ttt += 0.0005/100*turnover; //Transaction charges
          break;
        case 'RBDPMOLEIN':
          ttt += 0.001/100*turnover; //Transaction charges
          break;
      }
      ttt += 0.001/100*turnover; //Transaction charges
    }
    ttt += 0.18*ttt; // GST on broker+transaction charges
    if(qty<0 && COMMODITY_TYPE[comm]=='NAGRI')
      ttt += 0.01*turnover/100; // STT
    ttt += 15*(turnover/10000000); //SEBI charges
  }
	return ttt;
}
COMMODITY_MULTIPLIER_MAP = {
  ALUMINI: "1000a",
  ALUMINIUM: "5000a",
  CARDAMOM: "100a",
  CASTORSEED: "100b",
  COPPER: "1000a",
  COPPERM: "250a",
  COTTON: "25a",
  CPO: "1000a",
  CRUDEOIL: "100a",
  CRUDEOILM: "10a",
  GOLD: "100a",
  GOLDGUINEA: "1a",
  GOLDM: "10a",
  GOLDPETAL: "1a",
  LEAD: "5000a",
  LEADMINI: "1000a",
  MENTHOIL: "360a",
  NATURALGAS: "1250a",
  NICKEL: "250a",
  NICKELM: "100a",
  PEPPER: "10b",
  RBDPMOLEIN: "1000b",
  SILVER: "30a",
  SILVERM: "5a",
  SILVERMIC: "1a",
  ZINC: "5000a",
  ZINCMINI: "1000a"
}
COMMODITY_TYPE = {
    'ALUMINI': 'NAGRI',
    'ALUMINIUM': 'NAGRI',
    'CARDAMOM': 'AGRI',
    'CASTORSEED': 'AGRI',
    'COPPER': 'NAGRI',
    'COPPERM': 'NAGRI',
    'COTTON': 'IAGRI',
    'CPO': 'IAGRI',
    'CRUDEOIL': 'NAGRI',
    'CRUDEOILM': 'NAGRI',
    'GOLD': 'NAGRI',
    'GOLDGUINEA': 'NAGRI',
    'GOLDM': 'NAGRI',
    'GOLDPETAL': 'NAGRI',
    'LEAD': 'NAGRI',
    'LEADMINI': 'NAGRI',
    'MENTHOIL': 'NAGRI',
    'NATURALGAS': 'NAGRI',
    'NICKEL': 'NAGRI',
    'NICKELM': 'NAGRI',
    'PEPPER': 'AGRI',
    'RBDPMOLEIN': 'NAGRI',
    'SILVER': 'NAGRI',
    'SILVERM': 'NAGRI',
    'SILVERMIC': 'NAGRI',
    'ZINC': 'NAGRI',
    'ZINCMINI': 'NAGRI'
}
function processListToXYList_brokerage(seg_sym,trade_log,packedlist){
	var xyList = [];
	var trade_dict = {};
	var max_cap_used = 0;
	[seg,sym] = seg_sym.split('_');
	for (var i=0;i<trade_log.length;i++){
		trade_dict[trade_log[i][0]]=trade_log[i].slice(1,6);
	}
	total_brokerage_till_now = 0.0;
	for(var i=0;i<packedlist.length;i++){
		if(trade_dict[packedlist[i][0]]!=undefined)
			{
			price = trade_dict[packedlist[i][0]][3];
			qty = trade_dict[packedlist[i][0]][2];
			// cap = 
			brokerage = broker_cal(seg,sym,qty,price);
			total_brokerage_till_now += brokerage
			// console.log(brokerage);
			adj_price = parseFloat((packedlist[i][1]-total_brokerage_till_now).toFixed(2)); //adj_price= adj_pnl
			// console.log(adj_price);
			if(max_cap_used<Math.abs(qty)*price+brokerage)
				max_cap_used = Math.abs(qty)*price+brokerage;
			xyList.push({
						x:new Date(packedlist[i][0]),
						y:adj_price,
						pnltext:parseFloat(adj_price.toFixed(2))
					});
			}
		else{
			adj_price = parseFloat((packedlist[i][1]-total_brokerage_till_now).toFixed(2)); //adj_price= adj_pnl
			// console.log(adj_price);
			xyList.push({
						x:new Date(packedlist[i][0]),
						y:adj_price,
						pnltext:parseFloat(adj_price.toFixed(2))
					});
		}
	}
	return [xyList,max_cap_used];
}

// function deploy_algorithm(algo_uuid,sym,seg){
// 	params = {
// 		'algo_uuid':algo_uuid,
// 		'sym':sym,
// 		'seg':seg
// 	};

// 	take_profit = $('#ip_takeprofit').val();
// 	stop_loss = $('#ip_stoploss').val();
// 	quantity = $('#ip_quantity').val();
// 	interval = $('#ip_interval').val();

// 	broker = $('#ip_broker').val();
// 	frequency = $('#ip_frequency').val();
// 	live_period = $('#ip_live_period').val();

// 	var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();

// 	params['take_profit']=take_profit;
// 	params['stop_loss']=stop_loss;
// 	params['quantity']=quantity;
// 	params['interval']=interval;
// 	params['broker']=broker;
// 	params['frequency']=frequency;
// 	params['live_period']=live_period;
// 	params['seg_sym']=seg+'_'+sym;
// 	params['csrfmiddlewaretoken']=csrfmiddlewaretoken;

// 	$.post('/deploy_algorithm/',params,function(data){
// 		if(data['status']=='success'){
// 			window.location = '/dashboard';
// 			// var redirect = '/dashboard/';
// 			// delete params["html_block"];
// 			// params['algo_uuid']=data['algo_uuid'];
// 			// $.redirectPost(redirect, params);
// 		}
// 		else{
// 			// handle any error from save algorithm
// 		}
// 	});
// };

function edit_button(action_uuid){
    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    var action_uuid = action_uuid;

    // sending a post request 
    post('/algorithm',{
            'csrfmiddlewaretoken':csrfmiddlewaretoken,
            'action_uuid':action_uuid,
        },"post");
}

var click_action_uuid = null;
var click_obj = null;

function deploy_action(action_uuid,obj){
    action_uuid = click_action_uuid;
    obj = click_obj;
    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    var action_uuid = action_uuid;
    var broker_linked = false;
    try{
        if (!broker_linked && $("#trading_terms_checkbox").prop('checked')==true)
            {
            close_popup();
            // window.open('/broker_login?redirect=dashboard','targetWindow','toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=500,height=700');
            newWindow = popupWindowCenter('/broker_login?redirect=dashboard','Broker Login','500','700');
            newWindow.onunload = function(e){ 
                // alert(e.target.documentURI);
                if(e.target.documentURI.indexOf('status=success&request_token') != -1)
                    {
                        // sending a post request 
                        params = {
                                'csrfmiddlewaretoken':csrfmiddlewaretoken,
                                'action_uuid':action_uuid,
                            };

                        var request = $.ajax({
                          url: "/deploy_action",
                          type: "POST",
                          data: params,
                          dataType: "html"
                        });

                        request.done(function(msg) {
                            var msg = JSON.parse(msg);
                            if (msg['status']==true){
                                swal("Success","Algo Deployed","success");
                                window.location='/orders'
                                // location.reload();
                                // $(obj.parentElement).toggleClass('pause_button');
                                // $(obj.parentElement).html("<button type=\"submit\" class=\"pause_button\" onclick=\"pause_button('"+action_uuid+"',this);ga('send', 'event', 'Pause Algorithm', 'Dashboard Page');\">Pause</button>");
                            }
                        });

                        request.fail(function(jqXHR, textStatus) {
                          console.log( "Request failed: " + textStatus );
                        });

                    }
                }
            }
        }
    catch(e){
            console.log(e)
            swal("Could not connect with broker, please try to deploy again");
        }
}
function deploy_button(action_uuid=null,obj=null){
    click_action_uuid = action_uuid;
    click_obj = obj;
    // swal('This feature is only available to prime members. To activate Deployed Algorithms write to care@{---}.com');
    // popup_show();
    if (action_uuid == '0')
        swal({
        title: "",
        text: "<p class='prime_message'>This feature is only available to <b>prime members</b>.<br><br>Please write to <b style='color:#333333 !important;'>care@{---}.com</b> to activate this feature.</p>",
        html: true});
    else
        popup_show();
}

function force_stop(event,deployment_uuid){
    // force_stop_button(deployment_uuid)   
}
function refresh_algo_summary(){
	var algo_name = $("#an_cc").val();
	var algo_desc = $("#ad_cc").val();
	// var from_datepicker = $("#from_datepicker").val();
	// var to_datepicker = $("#to_datepicker").val();
	var entry = $("#et_cc").val();
	var exit = $("#ex_cc").val();
	var position_type = $("#pt_cc").val();
	if (position_type.toUpperCase() == 'BUY')
		var position_type_exit = 'SELL'
	else
		var position_type_exit = 'BUY'

	var algo_name = $("#an_cc").val();
	var c_position_qty = $("#ip_quantity").val();
	var c_stop_loss = $("#ip_stoploss").val();
	var c_take_profit = $("#ip_takeprofit").val();
	var holding_type = holding_type_mapping[$("#ip_holding_type").val()];
	var c_interval = interval_mapping[$("#ip_interval").val()];

	c_chart_type = to_title(adv_chart_type);
	c_trading_start_time = adv_trading_start_time;
	c_trading_stop_time = adv_trading_stop_time;

	var entry = $("#et_cc").val();
	var exit = $("#ex_cc").val();

	if (entry!=''){
    	if (position_type == 'Buy'|| position_type == 'BUY')
			var position_type_exit = 'SELL';
		else
			var position_type_exit = 'BUY';

    	var entry_str = '';
    	entry_str = position_type+' '+c_position_qty+' shares when '+entry
    	var exit_str='';
		if(exit!='')
    		exit_str = position_type_exit+' '+c_position_qty+' shares when '+exit+' or '+' at Stop loss of '+c_stop_loss+'% or Take profit of '+c_take_profit+'%';
	    else{
	       exit_str = position_type_exit+' '+c_position_qty+' shares at Stop loss of '+c_stop_loss+'% or Take profit of '+c_take_profit+'%';
	    }

	    c_interval_str = '';
		if(c_chart_type=='Heikinashi')
			c_chart_type = 'heikin-Ashi';

		var enter_trade_between_time = 'Enter trade between '+c_trading_start_time+' to '+c_trading_stop_time;
	    switch(c_interval){//Enter trade between : '+c_trading_start_time+' - '+c_trading_stop_time; break;
	        case 'min': c_interval_str = '1 minute interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
	        case '3min': c_interval_str = '3 minute interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
	        case '5min': c_interval_str = '5 minute interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
	        case '10min': c_interval_str = '10 minute interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
	        case '15min': c_interval_str = '15 minute interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
	        case '30min': c_interval_str = '30 minute interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
	        case 'hour': c_interval_str = '1 hour interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
	        case 'day': c_interval_str = '1 day interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
	       }
	    // algo_summary = '<p class="entry_heading"><img src="/static/imgs/new/entry.svg"><span>Entry</span></p> <p class="dashboard_condition_summary"> '+entry_str+' at '+c_interval_str+enter_trade_between_time+'</p> <p class="exit_heading"><img src="/static/imgs/new/exit.svg"><span>Exit</span></p> <p class="dashboard_condition_summary"> '+exit_str+' at '+c_interval_str+'</p> <p class="interval_heading">Candle interval</p> <p class="dashboard_condition_summary" style="padding-bottom: 0px;">'+c_interval_str+'</p>';
	    algo_summary = '<p class="entry_heading"><img src="/static/imgs/new/entry.svg"><span>Entry</span></p> <p class="dashboard_condition_summary"> '+entry_str+' at '+c_interval_str+enter_trade_between_time+'</p> <p class="exit_heading"><img src="/static/imgs/new/exit.svg"><span>Exit</span></p> <p class="dashboard_condition_summary"> '+exit_str+' at '+c_interval_str+'</p>';
	    $('.algo_summary').html(algo_summary);
	 }
	$('.entry_heading').next('.dashboard_condition_summary');
	$('.exit_heading').next('.dashboard_condition_summary');
}

function deploy_algorithm_popup_multi(algo_uuid){

	var deploy_instrument_list = [];
	$('.backtest_results_body').find(".deploy_checkbox").each(function(i,obj){
      	 if(!obj.disabled && obj.checked){
      	 	id = obj.id;
      	 	id = id.split('__')[1].split('_')
      	 	deploy_instrument_list.push(id);	
      	 }
      });

    if(deploy_instrument_list.length==0){
        return
    }
  for(var k=0; k<deploy_instrument_list.length;k++){
    if(deploy_instrument_list[k][0]=='MCX' && subscription_status.subscription_plan!=undefined &&subscription_status.subscription_plan!='ultimate'){
      show_snackbar(null,'MCX is only available in ultimate plan');
      // obj.checked = false;
      return;
    }
  }
	var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    var params = {
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/get_subscription_limit/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 10000,//40 sec timeout
    };

    $.ajax(settings).done(function (msg){
    	if(msg.status=='success'){

    		backtest_remaining = Math.max(msg['backtest'],0);
	        deployments_remaining= Math.max(msg['deployments_remaining'],0)
	        if(deployments_remaining<deploy_instrument_list.length){
	            show_snackbar(null,'You are trying to deploy more than the remaining deployments');
	            return;
	        }

	        $('body').addClass('body_scroll');
  			var algo_name = $("#an_cc").val();
  			var algo_desc = $("#ad_cc").val();
  			// var from_datepicker = $("#from_datepicker").val();
  			// var to_datepicker = $("#to_datepicker").val();
  			var entry = $("#et_cc").val();
  			var exit = $("#ex_cc").val();
  			var position_type = $("#pt_cc").val();
  			if (position_type.toUpperCase() == 'BUY')
  				var position_type_exit = 'SELL'
  			else
  				var position_type_exit = 'BUY'

  			var quantity = $("#ip_quantity").val();
  			var stop_loss = $("#ip_stoploss").val();
  			var take_profit = $("#ip_takeprofit").val();
  			var holding_type = holding_type_mapping[$("#ip_holding_type").val()];
  			var interval = interval_mapping[$("#ip_interval").val()];
        if(adv_chart_type.includes('enko')){
          if(['ultimate'].indexOf(subscription_status.subscription_plan) < 0
            ){
              show_snackbar(null,'Upgrade to ultimate plan, to use Renko Chart');
              return false;
          }
        }
  			var c_chart_type = to_title(adv_chart_type);
  			c_interval_str = '';
  			if(c_chart_type=='Heikinashi')
  				c_chart_type = 'heikin-Ashi';
  			// $('#trading_terms_checkbox:checked').removeAttr('checked');
  		    $('.deploy_summary_heading p').html(algo_name);

  		    var c_interval_str = '';
  		    switch(interval){
  		        case 'min':$('#interval_condition_summary').html('1 Minute, '+c_chart_type+' chart</br>Enter trade between : '+c_trading_start_time+' to '+c_trading_stop_time);
  		        	c_interval_str = '1 minute interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
  		        case '3min':$('#interval_condition_summary').html('3 Minute, '+c_chart_type+' chart</br>Enter trade between : '+c_trading_start_time+' to '+c_trading_stop_time);
  		        	c_interval_str = '3 minute interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
  		        case '5min':$('#interval_condition_summary').html('5 Minute, '+c_chart_type+' chart</br>Enter trade between : '+c_trading_start_time+' to '+c_trading_stop_time);
  		        	c_interval_str = '5 minute interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
  		        case '10min':$('#interval_condition_summary').html('10 Minute, '+c_chart_type+' chart</br>Enter trade between : '+c_trading_start_time+' to '+c_trading_stop_time);
  		        	c_interval_str = '10 minute interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
  		        case '15min':$('#interval_condition_summary').html('15 Minute, '+c_chart_type+' chart</br>Enter trade between : '+c_trading_start_time+' to '+c_trading_stop_time);
  		        	c_interval_str = '15 minute interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
  		        case '30min':$('#interval_condition_summary').html('30 Minute, '+c_chart_type+' chart</br>Enter trade between : '+c_trading_start_time+' to '+c_trading_stop_time);
  		        	c_interval_str = '30 minute interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
  		        case 'hour':$('#interval_condition_summary').html('1 Hour, '+c_chart_type+' chart</br>Enter trade between : '+c_trading_start_time+' to '+c_trading_stop_time);
  		        	c_interval_str = '1 hour interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
  		        case 'day':$('#interval_condition_summary').html('1 Day, '+c_chart_type+' chart</br>Enter trade between : '+c_trading_start_time+' to '+c_trading_stop_time);
  		        	c_interval_str = '1 day interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
  		    }
  		    $('#interval_condition_summary').hide();

  		    if(deploy_instrument_list.length==1){
  			    $('#entry_condition_summary').html(position_type+' '+quantity+' shares of '+deploy_instrument_list[0][1]+' when '+entry+' at '+c_interval_str+'Enter trade between '+c_trading_start_time+' to '+c_trading_stop_time);
  			    
  			    if(exit!='' && exit!=undefined)
  			        $('#exit_condition_summary').html(position_type_exit+' '+quantity+' shares when '+exit+' or '+' at Stop loss of '+stop_loss+'% or Take profit of '+take_profit+'%'+' at '+c_interval_str);
  			    else{
  			        $('#exit_condition_summary').html(position_type_exit+' '+quantity+' shares of '+deploy_instrument_list[0][1]+' at Stop loss of '+stop_loss+'% or Take profit of '+take_profit+'%'+' at '+c_interval_str);
  			    }
  			    $('.deploy_heading p').text("Deploy");
  		    }else{
  		    	$('#entry_condition_summary').html(position_type+' '+quantity+' shares'+' when '+entry+' at '+c_interval_str+'Enter trade between '+c_trading_start_time+' to '+c_trading_stop_time);
  	            if(exit!='')
  	                $('#exit_condition_summary').html(position_type_exit+' '+quantity+' shares when '+exit+' or '+' at Stop loss of '+stop_loss+'% or Take profit of '+take_profit+'%'+' at '+c_interval_str);
  	            else{
  	                $('#exit_condition_summary').html(position_type_exit+' '+quantity+' shares at Stop loss of '+stop_loss+'% or Take profit of '+take_profit+'%'+' at '+c_interval_str);
  	            }
  	            $('.deploy_heading p').text("Deploy Multiple Instruments");
  		    }

  		    // $('.popup').show();
  		    if ($('#trading_terms_checkbox:checked').is(':checked') && (first_time_deploy == "false")){
  		    	$('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
  		    	// $('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'");');
  		    	$('.deploy_confirm').attr('onclick','deploy_algorithm_multi("'+algo_uuid+'",\''+JSON.stringify(deploy_instrument_list)+'\');');
  		    }
  		    else{
  		    	$('.deploy_confirm').css({'background-color':'#c7c7c7 !important','cursor': 'no-drop'});
  		    	$('.deploy_confirm').unbind('click');
  		    	$('#trading_terms_checkbox:checked').removeAttr('checked');
  		    }

  		    // if ((first_time_deploy == "true") && !($('#trading_terms_checkbox:checked').is(':checked'))){
  		    // 	$('.deploy_confirm').css({'background-color':'#c7c7c7 !important','cursor': 'no-drop'});
  		    // 	$('.deploy_confirm').unbind('click');
  		    // 	$('#trading_terms_checkbox:checked').removeAttr('checked');
  		    // }
  		    // else if($('#trading_terms_checkbox:checked').is(':checked')){
  		    // 	$('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
  		    // 	$('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'");');
  		    // }
  		    $.get('/get_subscription_limit',{
  		    }).done(function (data){
  		    	if(data['status']=="success")
  		    	{
  		    		if(data['valid']==true){
  			    		if(Math.max(data['deployments_remaining'],0)<1){
  			    			show_snackbar(null,'Deployments limits reached');
  			    			$( ".loader_parent" ).fadeOut();
  				            $(".deploy_confirm").html('Confirm');
  				            $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
  				            // $('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'");');
  				            $('.deploy_confirm').attr('onclick','deploy_algorithm_multi("'+algo_uuid+'",\''+JSON.stringify(deploy_instrument_list)+'\');');
  				            $('#trading_terms_checkbox:checked').removeAttr('checked');
  				            close_popup();
  				            return;
  			    		}else{
  			    			$('.popup').show();
  			    			try{
  		                    	ga('send', {hitType: 'event', eventCategory: 'Deploy initiated', eventAction: 'Deploy initiated', eventLabel: 'Backtest page', eventValue: deploy_instrument_list.length});
  		                    }catch(e){
  		              
  		            		}
  			    		}
  				    }
  				}
          else if(msg.status=='error'){
            msg_err = data['error_msg'];
            if (msg_err == undefined)
              msg_err = 'Unable to get subscription status';
            show_snackbar(null,msg_err);
            return
          }
  			});
  		    $('#trading_terms_checkbox').change(function(){
  		        if($('#trading_terms_checkbox:checked').is(':checked')){
  		            $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
  		            // $('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'");');
  		            $('.deploy_confirm').attr('onclick','deploy_algorithm_multi("'+algo_uuid+'",\''+JSON.stringify(deploy_instrument_list)+'\');');
  		        }else{
  		            $('.deploy_confirm').css({'background-color':'#c7c7c7 !important','cursor': 'no-drop'});
  		           	$('.deploy_confirm').removeAttr('onclick');
  		        }

  		    });
    	}
      else if(msg.status=='error'){
        msg_err = data['error_msg'];
        if (msg_err == undefined)
          msg_err = 'Unable to get subscription status';
        show_snackbar(null,msg_err);
        return
      }
	});
	// $('body').addClass('body_scroll');
	// var algo_name = $("#an_cc").val();
	// var algo_desc = $("#ad_cc").val();
	// // var from_datepicker = $("#from_datepicker").val();
	// // var to_datepicker = $("#to_datepicker").val();
	// var entry = $("#et_cc").val();
	// var exit = $("#ex_cc").val();
	// var position_type = $("#pt_cc").val();
	// if (position_type == 'BUY')
	// 	var position_type_exit = 'SELL'
	// else
	// 	var position_type_exit = 'BUY'

	// var quantity = $("#ip_quantity").val();
	// var stop_loss = $("#ip_stoploss").val();
	// var take_profit = $("#ip_takeprofit").val();
	// var holding_type = $("#ip_holding_type").val()
	// var interval = $("#ip_interval").val();

	// // $('#trading_terms_checkbox:checked').removeAttr('checked');
 //    $('.deploy_summary_heading p').html(algo_name);
 //    $('#entry_condition_summary').html(position_type+' '+quantity+' shares of '+sym+' when '+entry+'.');
    
 //    if(exit!='' && exit!=undefined)
 //        $('#exit_condition_summary').html(position_type_exit+' '+quantity+' shares when '+exit+' or '+' at Stop loss of '+stop_loss+'% or Take profit of '+take_profit+'%.');
 //    else{
 //        $('#exit_condition_summary').html(position_type_exit+' '+quantity+' shares of '+sym+' at Stop loss of '+stop_loss+'% or Take profit of '+take_profit+'%.');
 //    }
 //    switch(interval){
 //        case 'min':$('#interval_condition_summary').html('1 Minute');break;
 //        case '3min':$('#interval_condition_summary').html('3 Minute');break;
 //        case '5min':$('#interval_condition_summary').html('5 Minute');break;
 //        case '10min':$('#interval_condition_summary').html('10 Minute');break;
 //        case '15min':$('#interval_condition_summary').html('15 Minute');break;
 //        case '30min':$('#interval_condition_summary').html('30 Minute');break;
 //        case 'hour':$('#interval_condition_summary').html('1 Hour');break;
 //        case 'day':$('#interval_condition_summary').html('1 Day');break;
 //    }
 //    // $('.popup').show();
 //    if ($('#trading_terms_checkbox:checked').is(':checked') && (first_time_deploy == "false")){
 //    	$('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
 //    	$('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'");');
 //    }
 //    else{
 //    	$('.deploy_confirm').css({'background-color':'#c7c7c7 !important','cursor': 'no-drop'});
 //    	$('.deploy_confirm').unbind('click');
 //    	$('#trading_terms_checkbox:checked').removeAttr('checked');
 //    }

 //    // if ((first_time_deploy == "true") && !($('#trading_terms_checkbox:checked').is(':checked'))){
 //    // 	$('.deploy_confirm').css({'background-color':'#c7c7c7 !important','cursor': 'no-drop'});
 //    // 	$('.deploy_confirm').unbind('click');
 //    // 	$('#trading_terms_checkbox:checked').removeAttr('checked');
 //    // }
 //    // else if($('#trading_terms_checkbox:checked').is(':checked')){
 //    // 	$('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
 //    // 	$('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'");');
 //    // }
 //    $.get('/get_subscription_limit',{
 //    }).done(function (data){
 //    	if(data['status']=="success")
 //    	{
 //    		if(data['valid']==true){
	//     		if(Math.max(data['deployments_remaining'],0)<1){
	//     			show_snackbar(null,'Deployments limits reached');
	//     			$( ".loader_parent" ).fadeOut();
	// 	            $(".deploy_confirm").html('<span><img src="/static/imgs/icon-deploy-confirm.png"></span>&nbsp;&nbsp;Confirm');
	// 	            $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
	// 	            $('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'");');
	// 	            $('#trading_terms_checkbox:checked').removeAttr('checked');
	// 	            close_popup();
	// 	            return;
	//     		}else{
	//     			$('.popup').show();
	//     			try{
 //                    ga('send', {hitType: 'event', eventCategory: 'Deployment', eventAction: 'Deploy initiated', eventLabel: 'Backtest page'});
 //                    }catch(e){
              
 //            		}
	//     		}
	// 	    }
	// 	}
	// });
 //    $('#trading_terms_checkbox').change(function(){
 //        if($('#trading_terms_checkbox:checked').is(':checked')){
 //            $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
 //            $('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'");');
 //        }else{
 //            $('.deploy_confirm').css({'background-color':'#c7c7c7 !important','cursor': 'no-drop'});
 //           	$('.deploy_confirm').removeAttr('onclick');
 //        }

 //    });
}

function deploy_algorithm_multi(algo_uuid,seg_sym_list){
    params = {
        'algo_uuid':algo_uuid,
        'seg_sym_list':seg_sym_list
    };

    take_profit = $('#ip_takeprofit').val();
    stop_loss = $('#ip_stoploss').val();
    quantity = $('#ip_quantity').val();
    interval =  interval_mapping[$("#ip_interval").val()];

    // live_period_mapping = {'Intraday (MIS)':1,'Overnight (CNC/NRML)':30}
    live_period_mapping = {'Notification Only':30,'Paper trading':30,'Auto trading':30}
    broker = $('#ip_broker').val();
    frequency = $('#ip_frequency').val();
    live_period = live_period_mapping[$('#ip_live_period').val()];
    variety = $('#ip_variety').val();
 //  	// advanced parameters
 //    var holding_type = $('#ip_holding_type').val();
	// var chart_type = $('#ip_chart_type').val();
	// var trading_start_time = $('#trading_start_time').val();
	// var trading_stop_time = $('#trading_stop_time').val();
	// var trade_time_given = false;
	// if(trading_stop_time!=''&&trading_start_time!=''&&trading_stop_time>trading_start_time){
	// trade_time_given = true;
	// }

    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();

    params['take_profit']=take_profit;
    params['stop_loss']=stop_loss;
    params['quantity']=quantity;
    params['interval']=interval;
    params['broker']=broker;
    params['frequency']=parseInt(frequency)-1;
    params['live_period']=live_period;
    params['variety']=variety;
    if (live_period!=1)
      params['variety']='REGULAR';
    // // advanced parameters
    // params['holding_type'] = holding_type;
    // params['chart_type'] = chart_type;
    // params['trading_start_time'] = trading_start_time;
    // params['trading_stop_time'] = trading_stop_time;
    // params['trade_time_given'] = trade_time_given;

    // params['seg_sym']=seg+'_'+sym;
    params['csrfmiddlewaretoken']=csrfmiddlewaretoken;

    $(".deploy_confirm").html("<img src='/static/imgs/button-loading-rect.gif' id='button_loading'>");
    $('.deploy_confirm').removeAttr('onclick');
    $.post('/deploy_algorithm_multi/',params,function(data){
        if(data['status']=='success'){
        	try{
            	ga('send', {hitType: 'event', eventCategory: 'Deploy confirmed', eventAction: 'Deploy confirmed', eventLabel: 'Backtest page', eventValue: JSON.parse(seg_sym_list).length});
            }catch(e){
              
            }
            window.location = '/order_log';
            // var redirect = '/dashboard/';
            // delete params["html_block"];
            // params['algo_uuid']=data['algo_uuid'];
            // $.redirectPost(redirect, params);
        }
        else{
            // handle any error from save algorithm
            $( ".loader_parent" ).fadeOut();
            $(".deploy_confirm").html('Confirm');
            $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
            // $('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'");');
            $('.deploy_confirm').attr('onclick','deploy_algorithm_multi("'+algo_uuid+'",\''+JSON.stringify(seg_sym_list)+'\');');
            $('#trading_terms_checkbox:checked').removeAttr('checked');
            close_popup();
            show_snackbar(null,'Some error occured, please try again!');
        }
    }).fail(function(){
        $( ".loader_parent" ).fadeOut();
        $(".deploy_confirm").html('Confirm');
        $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
        // $('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'");');
        $('.deploy_confirm').attr('onclick','deploy_algorithm_multi("'+algo_uuid+'",\''+JSON.stringify(seg_sym_list)+'\');');
        $('#trading_terms_checkbox:checked').removeAttr('checked');
        close_popup();
        show_snackbar(null,'Some error occured, please try again!');
    });
    $('body').removeClass('body_scroll');
};

// function deploy_algorithm(algo_uuid,sym,seg) ussing these params, fetch the entry,exit etc
function deploy_algorithm_popup(algo_uuid,sym,seg){
	$('body').addClass('body_scroll');
	var algo_name = $("#an_cc").val();
	var algo_desc = $("#ad_cc").val();
	// var from_datepicker = $("#from_datepicker").val();
	// var to_datepicker = $("#to_datepicker").val();
	var entry = $("#et_cc").val();
	var exit = $("#ex_cc").val();
	var position_type = $("#pt_cc").val();
	if (position_type.toUpperCase() == 'BUY')
		var position_type_exit = 'SELL'
	else
		var position_type_exit = 'BUY'

	var quantity = $("#ip_quantity").val();
	var stop_loss = $("#ip_stoploss").val();
	var take_profit = $("#ip_takeprofit").val();
	var holding_type = holding_type_mapping[$("#ip_holding_type").val()];
	var interval = interval_mapping[$("#ip_interval").val()];

	// $('#trading_terms_checkbox:checked').removeAttr('checked');
    $('.deploy_summary_heading p').html(algo_name);
    $('#entry_condition_summary').html(position_type+' '+quantity+' shares of '+sym+' when '+entry+'');
    
    if(exit!='' && exit!=undefined)
        $('#exit_condition_summary').html(position_type_exit+' '+quantity+' shares when '+exit+' or '+' at Stop loss of '+stop_loss+'% or Take profit of '+take_profit+'%');
    else{
        $('#exit_condition_summary').html(position_type_exit+' '+quantity+' shares of '+sym+' at Stop loss of '+stop_loss+'% or Take profit of '+take_profit+'%');
    }
    switch(interval){
        case 'min':$('#interval_condition_summary').html('1 Minute');break;
        case '3min':$('#interval_condition_summary').html('3 Minute');break;
        case '5min':$('#interval_condition_summary').html('5 Minute');break;
        case '10min':$('#interval_condition_summary').html('10 Minute');break;
        case '15min':$('#interval_condition_summary').html('15 Minute');break;
        case '30min':$('#interval_condition_summary').html('30 Minute');break;
        case 'hour':$('#interval_condition_summary').html('1 Hour');break;
        case 'day':$('#interval_condition_summary').html('1 Day');break;
    }
    // $('.popup').show();
    if ($('#trading_terms_checkbox:checked').is(':checked') && (first_time_deploy == "false")){
    	$('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
    	$('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'");');
    }
    else{
    	$('.deploy_confirm').css({'background-color':'#c7c7c7 !important','cursor': 'no-drop'});
    	$('.deploy_confirm').unbind('click');
    	$('#trading_terms_checkbox:checked').removeAttr('checked');
    }

    // if ((first_time_deploy == "true") && !($('#trading_terms_checkbox:checked').is(':checked'))){
    // 	$('.deploy_confirm').css({'background-color':'#c7c7c7 !important','cursor': 'no-drop'});
    // 	$('.deploy_confirm').unbind('click');
    // 	$('#trading_terms_checkbox:checked').removeAttr('checked');
    // }
    // else if($('#trading_terms_checkbox:checked').is(':checked')){
    // 	$('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
    // 	$('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'");');
    // }
    $.get('/get_subscription_limit',{
    }).done(function (data){
    	if(data['status']=="success")
    	{
    		if(data['valid']==true){
	    		if(Math.max(data['deployments_remaining'],0)<1){
	    			show_snackbar(null,'Deployments limits reached');
	    			$( ".loader_parent" ).fadeOut();
		            $(".deploy_confirm").html('Confirm');
		            $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
		            $('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'");');
		            $('#trading_terms_checkbox:checked').removeAttr('checked');
		            close_popup();
		            return;
	    		}else{
	    			$('.popup').show();
	    			// try{
        //             	ga('send', {hitType: 'event', eventCategory: 'Deployment', eventAction: 'Deploy initiated', eventLabel: 'Backtest page'});
        //             	alert("Deploy initiated multi");
        //             }catch(e){
              
        //     		}
	    		}
		    }
		}
    else if(msg.status=='error'){
        msg_err = data['error_msg'];
        if (msg_err == undefined)
          msg_err = 'Unable to get subscription status';
        show_snackbar(null,msg_err);
        return
      }
	});
    $('#trading_terms_checkbox').change(function(){
        if($('#trading_terms_checkbox:checked').is(':checked')){
            $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
            $('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'");');
        }else{
            $('.deploy_confirm').css({'background-color':'#c7c7c7 !important','cursor': 'no-drop'});
           	$('.deploy_confirm').removeAttr('onclick');
        }

    });
}
function deploy_algorithm(algo_uuid,sym,seg){
    params = {
        'algo_uuid':algo_uuid,
        'sym':sym,
        'seg':seg
    };

    take_profit = $('#ip_takeprofit').val();
    stop_loss = $('#ip_stoploss').val();
    quantity = $('#ip_quantity').val();
    interval = interval_mapping[$("#ip_interval").val()];

    broker = $('#ip_broker').val();
    frequency = $('#ip_frequency').val();
    live_period = $('#ip_live_period').val();

    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();

    params['take_profit']=take_profit;
    params['stop_loss']=stop_loss;
    params['quantity']=quantity;
    params['interval']=interval;
    params['broker']=broker;
    params['frequency']=frequency;
    params['live_period']=live_period;
    params['seg_sym']=seg+'_'+sym;
    params['csrfmiddlewaretoken']=csrfmiddlewaretoken;

    $(".deploy_confirm").html("<img src='/static/imgs/button-loading-rect.gif' id='button_loading'>");
    $('.deploy_confirm').removeAttr('onclick');
    $.post('/deploy_algorithm/',params,function(data){
        if(data['status']=='success'){
            window.location = '/order_log';
            // try{
            // 	ga('send', {hitType: 'event', eventCategory: 'Deployment', eventAction: 'Deploy confirmed', eventLabel: 'Backtest page'});
            // }catch(e){
              
            // }
            // var redirect = '/dashboard/';
            // delete params["html_block"];
            // params['algo_uuid']=data['algo_uuid'];
            // $.redirectPost(redirect, params);
        }
        else{
            // handle any error from save algorithm
            $( ".loader_parent" ).fadeOut();
            $(".deploy_confirm").html('Confirm');
            $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
            $('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'");');
            $('#trading_terms_checkbox:checked').removeAttr('checked');
            close_popup();
            show_snackbar(null,'Some error occured, please try again!');
        }
    }).fail(function(){
        $( ".loader_parent" ).fadeOut();
        $(".deploy_confirm").html('Confirm');
        $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
        $('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'");');
        $('#trading_terms_checkbox:checked').removeAttr('checked');
        close_popup();
        show_snackbar(null,'Some error occured, please try again!');
    });
    $('body').removeClass('body_scroll');
};

function generate_shareable_link2(event,algo_uuid,seg_sym,platform){
	// try{
	// 	ga('send', {hitType: 'event', eventCategory: 'Share backtest results', eventAction: 'Share backtest results', eventLabel: 'Backtest page'});
	// }
	// catch(e){
		
	// }
	params = {
		'algo_uuid':algo_uuid,
		'seg_sym':seg_sym
	}
	var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
	params['csrfmiddlewaretoken']=csrfmiddlewaretoken;
	
	$(event.target).html('<span><img src="/static/imgs/button-loading-sq-blue.gif"></span>');

	$.post('/generate_shareable_link/',params,function(data){
        if(data['status']=='success'){
            // console.log(window.location.protocol + "//" + window.location.host+'/backtest_shared/'+data['sharable_link']);
            $(event.target).parents(".actions_section").find(".share_window input").val(window.location.protocol + "//" + window.location.host+'/backtest_shared/'+data['sharable_link']);
            var t_v = true;
            $('#fb_'+seg_sym.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')).data('sharable_link',data['sharable_link']);
            $('#twitter_'+seg_sym.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')).data('sharable_link',data['sharable_link']);
            $('#linkedin_'+seg_sym.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')).data('sharable_link',data['sharable_link']);
            if(!$(event.target).parents(".actions_section").find(".social_buttons").is(":visible"))
            	{
            		t_v = false;
            	}
            if(!t_v)
            {
            	$(event.target).parents(".actions_section").find(".social_buttons").show();
				t = $(event.target).parents(".actions_section").find(".social_buttons input");
        		// t.focus();
  		// 		t[0].setSelectionRange(0, t.val().length);
				t.select();
        		t_v = true;
            }else{
            	$(event.target).parents(".actions_section").find(".share_window").hide();
            }
        }
        else{
            // handle any error from save algorithm
            console.log(data);
        }
		$(event.target).html('<span><img src="/static/imgs/icon-share.png"></span>');
		url =  "https://" + 'streak.tech'+'/backtest_shared/'+$('#'+platform+'_'+seg_sym.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')).data('sharable_link');
		switch(platform){
			case 'fb':
				share_to_facebook(url,"StreakTech");
				break;
			case 'twitter':
				share_to_twitter(url,"StreakTech");
				break;
			case 'linkedin':
				share_to_linkedin(url,"StreakTech");
				break;
		}
    }).complete(function(){
		$(event.target).html('<span><img src="/static/imgs/icon-share.png"></span>');
    });
}

function generate_shareable_link(event,algo_uuid,seg_sym){
	// try{
	// 	ga('send', {hitType: 'event', eventCategory: 'Share backtest results', eventAction: 'Share backtest results', eventLabel: 'Backtest page'});
	// }
	// catch(e){
		
	// }
	params = {
		'algo_uuid':algo_uuid,
		'seg_sym':seg_sym
	}
	var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
	params['csrfmiddlewaretoken']=csrfmiddlewaretoken;
	
	$(event.target).html('<span><img src="/static/imgs/button-loading-sq-blue.gif"></span>');

	$.post('/generate_shareable_link/',params,function(data){
        if(data['status']=='success'){
            // console.log(window.location.protocol + "//" + window.location.host+'/backtest_shared/'+data['sharable_link']);
            $(event.target).parents(".actions_section").find(".share_window input").val(window.location.protocol + "//" + window.location.host+'/backtest_shared/'+data['sharable_link']);
            var t_v = true;
            $('#fb_'+seg_sym.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')).data('sharable_link',data['sharable_link']);
            $('#twitter_'+seg_sym.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')).data('sharable_link',data['sharable_link']);
            $('#linkedin_'+seg_sym.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')).data('sharable_link',data['sharable_link']);
            if(!$(event.target).parents(".actions_section").find(".social_buttons").is(":visible"))
            	{
            		t_v = false;
            	}
            if(!t_v)
            {
            	$(event.target).parents(".actions_section").find(".social_buttons").show();
				t = $(event.target).parents(".actions_section").find(".social_buttons input");
        		// t.focus();
  		// 		t[0].setSelectionRange(0, t.val().length);
				t.select();
        		t_v = true;
            }else{
            	$(event.target).parents(".actions_section").find(".share_window").hide();
            }
        }
        else{
            // handle any error from save algorithm
            console.log(data);
        }
		$(event.target).html('<span><img src="/static/imgs/icon-share.png"></span>');
    }).complete(function(){
		$(event.target).html('<span><img src="/static/imgs/icon-share.png"></span>');
    });
}

function myBtBarLoader(k,tf) {
  var le = $("#"+k.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+" #myBtBar");
  if (le.length!=1)
  	return
  var elem = le[0];   
  var width = 1;
  var id = setInterval(frame, tf);
  function frame() {
    if (width >= 95) {
      clearInterval(id);
    } else {
      width++; 
      elem.style.width = width + '%'; 
    }
  }
}

// function show_advanced_section(){
//   $('#ip_holding_type').val(adv_holding_type);
//   $('#ip_chart_type').val(adv_chart_type);
//   $('#trading_start_time').val(adv_trading_start_time);
//   $('#trading_stop_time').val(adv_trading_stop_time);

//     $(".advanced_section_popup").show();
//     $("body").addClass('body_scroll');
// }