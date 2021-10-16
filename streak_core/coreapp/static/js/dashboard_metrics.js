$(window).load(function() {
    $(".loader_parent").fadeOut();
});
var action_buttons=false;

var t = [];

var s = [];

$(document).ready(function(){
	update_dashboard_usage_metrics();
	update_alerts_mertics();
	update_dashboard_funds();
  update_top_performance2();
	update_samples2();
	update_news();
	setInterval(update_dashboard_usage_metrics, 60000*0.5);
	setInterval(update_alerts_mertics, 60000*0.8);
	setInterval(update_dashboard_funds, 60000*1);
	setInterval(update_top_performance2, 60000*10);
	setInterval(update_dashboard_usage_metrics, 60000*5);
	setInterval(update_news, 60000*1);


  var popElement = document.getElementsByClassName("row_action_desc");
  document.addEventListener('click', function(event) {
    if (action_buttons){
        $(".action_buttons").slideUp();
        setTimeout(function(){ 
            $(".row_action_desc>p>img").fadeOut();
        }, 400);
        action_buttons = false;
    }
  $(".algo_details_popup").click(function(e){
    // alert($(".order_log_popup").has(e.target).length);
    // alert($(".order_log_popup").is(e.target));
    if(($(".algo_details_popup").has(e.target).length == 0)&&($(".algo_details_popup").is(e.target))){
      $("body").removeClass("body_scroll");
      $(".close_algo_details_popup").parents(".body").find(".algo_details_popup").fadeOut();
    }
    });
  });
  // $(".row_action_desc>p>img").click(function(e){
  //   // alert($(this).parents(".menu_dots").find(".action_buttons").className);
  //   $(".action_buttons").slideUp();
  //   $(this).parents(".row_action_desc").find('.action_buttons').slideDown();
  //   action_buttons = true;
  //   e.stopPropagation();
  // });
  // $(".row_action_desc>p>img").off("click");
  $(".row_action_desc>p>img").click(function(e){
      // alert($(this).parents(".menu_dots").find(".action_buttons").className);
      $(".action_buttons").slideUp();
      $(".row_action_desc>p>img").hide();
      $(this).parents(".row_action_desc").find('p>img').show();
      $(this).parents(".row_action_desc").find('.action_buttons').slideDown();
      action_buttons = true;
      e.stopPropagation();
  });

  $(".algos_desc_row").hover(function(){
    $(this).find(".row_action_desc>p>img").show();
  });
  $(".algos_desc_row").mouseleave(function(){
    $(this).find(".row_action_desc>p>img").hide();
  });

  var time = new Date().getHours()
  u_name_short = to_title(u_name.split(' ')[0]);
    if (time >= 4 && time < 16) {
      if (time < 12) {
        $('#greeting_top').html('<p class="greeting greeting_gm_4am"><img src="/static/imgs/new/fancy/sun.svg">Good Morning, '+u_name_short+'</p>');
      } else {
        $('#greeting_top').html('<p class="greeting greeting_ga_12pm"><img src="/static/imgs/new/fancy/sun.svg">Good Afternoon, '+u_name_short+'</p>');
      }
    } else if (time >= 16 && time < 18) {
      $('#greeting_top').html('<p class="greeting greeting_ge_4pm"><img src="/static/imgs/new/fancy/sunset.svg">Good Evening, '+u_name_short+'</p>');
    } else if (time >= 18 || time < 4) {
      $('#greeting_top').html('<p class="greeting greeting_ge_6pm"><img src="/static/imgs/new/fancy/moon.svg">Good Evening, '+u_name_short+'</p>');
    }
});

function update_news(){

}

function update_dashboard_usage_metrics(){
	var params = {
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/fetch_dashboard_usage_metrics/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 40000,//40 sec timeout
    }

    $("#usage_header_loader").show();
    $.ajax(settings).done(function (msg){
    	 if(msg.status=='success'){
        $('#algo_created').html(msg.usage_metric.total_created);
        $('#algo_backtested').html(msg.usage_metric.backtest);
    	 	$('#algo_deployed').html(msg.usage_metric.deployed);
    	 }
    }).complete(function(){
      $("#usage_header_loader").hide();
    });
}

function update_alerts_mertics(){
	var params = {
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/fetch_alerts_mertics/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 40000,//40 sec timeout
    }
    $("#usage_header_loader").show();
    $.ajax(settings).done(function (msg){
    	 if(msg.status=='success'){
    	 	$('#notif_sent').html(msg.alert_metrics.sent);
    	 	$('#notif_action_taken').html(msg.alert_metrics.confirmed);
    	 	$('#notif_expired').html(msg.alert_metrics.exp_can);
    	 }
    }).complete(function(){
      $("#usage_header_loader").hide();
    });
}
function samples_click(ev,algo_uuid){
	var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
	var params = {
		'csrfmiddlewaretoken':csrfmiddlewaretoken,
        'algo_uuid':algo_uuid
    };
    $(ev.target).css({'cursor': 'no-drop'});
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/clone_sample/',
      "method": "POST",
      "headers": {
      },
      "data":params,
      "timeout": 40000,//40 sec timeout
    }
    $.ajax(settings).done(function (msg){
    	if(msg.status=='success'){
    		window.location.href = '/strategy/?algo_uuid='+msg.algo_uuid+'#sample'
    	}
        $(ev.target).css({'cursor': 'pointer'});
    }).fail(function(){
        $(ev.target).css({'cursor': 'pointer'});
    });
}
function top_performer_click(ev,algo_uuid){
    // $(ev.target).html("<img src='/static/imgs/button-loading-rect.gif' id='button_loading'>");
    $(ev.target).css({'cursor': 'no-drop'});
    // $(ev.target).removeAttr('onclick');
    $.get('/get_subscription_valid/',{
    }).done(function (data){
        if(data['status']=="success")
        {
          post('/backtests/',{
                'algo_uuid':algo_uuid
            },"get");
        }else{
            show_snackbar(null,'Please update your subscription to avail all the services!');
            // $(ev.target).html("Backtest results&nbsp;<img src=\"/static/imgs/icon-forward.png\">");
            $(ev.target).css({'cursor': 'pointer'});
            // $(ev.target).attr('onclick','algo_backtests(event,\''+algo_uuid+'\')');
            // $(ev.target).focusout();
        }
    }).fail(function(){
        show_snackbar(null,'Some error occured, please try again!');
        // $(ev.target).html("Backtest results&nbsp;<img src=\"/static/imgs/icon-forward.png\">");
        $(ev.target).css({'cursor': 'pointer'});
        $(ev.target).attr('onclick','algo_backtests(event,\''+algo_uuid+'\')');
        // $(ev.target).focusout();
    });
}
function update_dashboard_funds(){
	var params = {
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/fetch_dashboard_funds/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 40000,//40 sec timeout
    }

    $.ajax(settings).done(function (msg){
    	 if(msg.status=='success'){
    	 	$('#available_funds').html('&#8377;'+parseFloat(msg.funds.available_balance).toFixed(2));
    	 	$('#margin_funds').html('&#8377;'+parseFloat(msg.funds.margins_used).toFixed(2));
    	 	$('#account_funds').html('&#8377;'+parseFloat(msg.funds.account_value).toFixed(2));

        $('#commodity_available_funds').html('&#8377;'+parseFloat(msg.commodity_funds.available_balance).toFixed(2));
        $('#commodity_margin_funds').html('&#8377;'+parseFloat(msg.commodity_funds.margins_used).toFixed(2));
        $('#commodity_account_funds').html('&#8377;'+parseFloat(msg.commodity_funds.account_value).toFixed(2));

        $('.login_required_popup').hide();

    	 }
    	 else if(msg.status=='error'){
    	 	if(msg.error=="Login required, session expired"){
          // $('.login_required_popup').show();
        }
    	 }
    });
}

function format_algo_summary(algo_obj){
    algo_summary = '';
    try{
        var entry = algo_obj.action_str;
        var exit = algo_obj.action_str_exit;
        var algo_name = algo_obj.algo_name;;
        var position_type = algo_obj.action_type;
        var holding_type = algo_obj.holding_type;
        var c_interval = algo_obj.time_frame;
        var c_position_qty = algo_obj.quantity;
        var c_stop_loss = algo_obj.stop_loss;
        var c_take_profit = algo_obj.take_profit;
        if (entry!=''){
            if (position_type == 'BUY')
                var position_type_exit = 'SELL';
            else
                var position_type_exit = 'BUY';

            var entry_str = '';
            entry_str = position_type+' '+c_position_qty+' shares when '+entry+''
            var exit_str='';
            if(exit!='' && exit!=undefined)
                exit_str = position_type_exit+' '+c_position_qty+' shares when '+exit+'';
            else{
               exit_str = position_type_exit+' '+c_position_qty+' shares at Stop loss of '+c_stop_loss+'% or Take profit of '+c_take_profit+'%';
            }

            c_interval_str = '';
            
            switch(c_interval){
                case 'min': c_interval_str = '1 Minute'; break;
                case '5min': c_interval_str = '5 Minute'; break;
                case 'hour': c_interval_str = '1 Hour'; break;
                case 'day': c_interval_str = '1 Day'; break;
               }
            algo_summary = '<h2>'+algo_name+'</h2> <!-- <h2 class="backtest_pnl">Backtested P&L <span class="profit">+12,500 (+10%)</span></h2> --> <p class="algo_entry"><span>Entry:</span><br>'+entry_str+'</p> <p class="algo_exit"><span>Exit:</span><br>'+exit_str+'</p> <p class="algo_interval"><span>Interval:</span><br>'+c_interval_str+'</p>';
        }
    }
    catch(e){
        // console.log(e);
    }
    return algo_summary;
}

function format_algo_summary2(algo_obj){
    algo_summary = '';
    try{
        var entry = algo_obj.action_str;
        var exit = algo_obj.action_str_exit;
        var algo_name = algo_obj.action_name;;
        var position_type = algo_obj.action_type;
        var holding_type = algo_obj.holding_type;
        var c_interval = algo_obj.time_frame;
        var c_position_qty = algo_obj.quantity;
        var c_stop_loss = algo_obj.stop_loss;
        var c_take_profit = algo_obj.take_profit;
        var c_chart_type = algo_obj.chart_type;
        var c_trading_start_time = algo_obj.trading_start_time;
        var c_trading_stop_time = algo_obj.trading_stop_time;
        if(c_trading_start_time==undefined)
            c_trading_start_time = '00:00';
        if(c_trading_stop_time==undefined)
            c_trading_stop_time = '23:59';
        if(c_chart_type==undefined)
            c_chart_type = 'Candlestick';
        else
            c_chart_type = to_title(c_chart_type);
            if(c_chart_type=='Heikinashi')
                c_chart_type = 'Heikin-Ashi';

        if (entry!=''){
            if (position_type == 'BUY')
                var position_type_exit = 'SELL';
            else
                var position_type_exit = 'BUY';

            var entry_str = '';
            entry_str = position_type+' '+c_position_qty+' shares when '+entry+''
            var exit_str='';
            if(exit!='' && exit!=undefined)
                exit_str = position_type_exit+' '+c_position_qty+' shares when '+exit+' or '+' at Stop loss of '+c_stop_loss+'% or Take profit of '+c_take_profit+'%';
            else{
               exit_str = position_type_exit+' '+c_position_qty+' shares at Stop loss of '+c_stop_loss+'% or Take profit of '+c_take_profit+'%';
            }

            c_interval_str = '';
            var enter_trade_between_time = 'Enter trade between '+c_trading_start_time+' to '+c_trading_stop_time;
            switch(c_interval){
                case 'min': c_interval_str = '1 minute interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
                case '3min': c_interval_str = '3 minute interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
                case '5min': c_interval_str = '5 minute interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
                case '10min': c_interval_str = '10 minute interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
                case '15min': c_interval_str = '15 minute interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
                case '30min': c_interval_str = '30 minute interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
                case 'hour': c_interval_str = '1 hour interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
                case 'day': c_interval_str = '1 day interval using '+c_chart_type.toLowerCase()+' chart.</br>'; break;
               }
            // algo_summary = '<div class="algo_summary"><p class="entry_heading">Entry</p> <p class="dashboard_condition_summary"> '+entry_str+' at '+c_interval_str+enter_trade_between_time+'</p> <p class="exit_heading">Exit</p> <p class="dashboard_condition_summary"> '+exit_str+' at '+c_interval_str+'</p> <p class="interval_heading">Candle interval</p> <p class="dashboard_condition_summary" style="padding-bottom: 0px;">'+c_interval_str+'</p></div>';
            algo_summary = '<div class="deploy_summary_heading"><p>'+algo_obj.algo_name+'</p></div><div class="algo_summary"><p class="entry_heading"><img src="/static/imgs/new/entry.svg"><span>Entry</span></p> <p class="dashboard_condition_summary"> '+entry_str+' at '+c_interval_str+enter_trade_between_time+'</p> <p class="exit_heading"><img src="/static/imgs/new/exit.svg"><span>Exit</span></p> <p class="dashboard_condition_summary"> '+exit_str+' at '+c_interval_str+'<br></p></div>';
        }
    }
    catch(e){
        console.log(e);
    }
    return algo_summary;
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

function plot_helper(ctx,pnl){
	return new Chart(ctx,{
						type: 'line',
						scaleSteps : 4,
				    	data: {
				    		// labels: ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
							datasets: [{
							    label: 'P&L',
							    data: processListToXYList(pnl),
							    backgroundColor:'rgba(255,255,255,0)',
							    borderColor: '#0088ff',
							    borderWidth: 2,
							    lineTension: 0,
							    // fill: true,
							    // fontSize: 10,
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
				                	fontColor: '#7f8fa4',
				                    beginAtZero:true,
				                    fontSize: 8
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
									fontColor: '#7f8fa4',
									fontSize: 8
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
}

function update_samples(){
  $('#update_top_performance1').show();
	var params = {
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/fetch_samples/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 40000,//40 sec timeout
    }

    $.ajax(settings).done(function (msg){
      
      if(msg.status=='success'){
      var sample_algos_parent = $('#sample_algos_parent');
      var sample_algos = sample_algos_parent.find('.sample_algos')
      for(var i=0;i<sample_algos.length;i++){
        try{
          $(sample_algos[i]).removeClass('top_performers_empty');
					var summary = format_algo_summary(msg.samples[i]['algo_obj'])
					var algo_div = $('<div class="algo">'+summary+'</div>');
					var algo_result_div = $('<div class="algo_result"><h2 class="backtest_pnl">Backtested P&L <span class="profit">+'+msg.samples[i]['backtest_result'][msg.samples[i]['seg_sym']].final_pnl.toFixed(2)+' (+'+(msg.samples[i]['backtest_result'][msg.samples[i]['seg_sym']].final_pnl/msg.samples[i]['backtest_result'][msg.samples[i]['seg_sym']].max_cap_used*100).toFixed(2)+'%)</span></h2> <div class="result_chart" id="'+msg.samples[i].algo_uuid+msg.samples[i]['seg_sym']+'sample_pnl_chartContainer_new"> <canvas id="'+msg.samples[i].algo_uuid+msg.samples[i]['seg_sym']+'sample_pnl_chartContainer_new"></canvas> </div> <div class="algo_cta"> <button class="try" id="try_'+i+'" onclick="samples_click(event,\''+msg.samples[i].algo_uuid+'\');ga(\'send\', {hitType: \'event\', eventCategory: \'Sample Algo Go\', eventAction: \'Sample Algo Go\', eventLabel: \'Dashboard page\'});">GO</button> </div></div>');
					$(sample_algos[i]).html('');
					$(sample_algos[i]).append(algo_div);
					$(sample_algos[i]).append(algo_result_div);
					$('#'+msg.samples[i].algo_uuid+msg.samples[i]['seg_sym'].replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+"sample_pnl_chartContainer_new").replaceWith('<canvas id="'+msg.samples[i].algo_uuid+msg.samples[i]['seg_sym']+'sample_pnl_chartContainer_new"></canvas>');
					// var ctx = document.getElementById(msg.samples[i].algo_uuid+msg.samples[i]['seg_sym']+"sample_pnl_chartContainer_new").getContext('2d');
					// var pnl_chartContainer_new = plot_helper(ctx,msg.samples[i]['backtest_result'][msg.samples[i]['seg_sym']]['pnl'])
				}catch(e){
					// console.log(e);
				}
			}
		}
  }).complete(function(){
    $('#update_top_performance1').hide();
  });
}

function myBtBarLoader(k,tf) {
  var le = $("#"+k+" #myBtBar");
  if (le.length!=1)
    {
      return;
    }
  var elem = le[0];   
  var width = 1;
  function frame() {
    if (width >= 95) {
      clearInterval(id);
    } else {
      width++; 
      elem.style.width = width + '%'; 
    }
  }
  var id = setInterval(frame, tf);
}

function update_top_performance(){
  $('#update_top_performance2').show();
	var params = {
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/fetch_top_performers/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 400000,//40 sec timeout
    }

    $.ajax(settings).done(function (msg){
    	 if(msg.status=='success'){
			
			var sample_algos_parent = $('#top_performers_algos_parent');
			var sample_algos = sample_algos_parent.find('.top_performers')
			for(var i=0;i<msg.backtests.length;i++){
				try{
          $(sample_algos[i]).removeClass('top_performers_empty');
					var summary = format_algo_summary(msg.backtests[i]['algo_obj'])
					var algo_div = $('<div class="algo">'+summary+'</div>');
					var algo_result_div = $('<div class="algo_result"><h2 class="backtest_pnl">Backtested P&L <span class="profit">+'+msg.backtests[i]['backtest_result'][msg.backtests[i]['seg_sym']].final_pnl.toFixed(2)+' (+'+(msg.backtests[i]['backtest_result'][msg.backtests[i]['seg_sym']].final_pnl/msg.backtests[i]['backtest_result'][msg.backtests[i]['seg_sym']].max_cap_used*100).toFixed(2)+'%)</span></h2> <div class="result_chart" id="'+msg.backtests[i].algo_uuid+msg.backtests[i].seg_sym+'pnl_chartContainer_new"> <canvas id="'+msg.backtests[i].algo_uuid+msg.backtests[i].seg_sym+'pnl_chartContainer_new"></canvas> </div> <div class="algo_cta"> <button class="try" onclick="top_performer_click(event,\''+msg.backtests[i].algo_uuid+'\');ga(\'send\', {hitType: \'event\', eventCategory: \'Backtest Results\', eventAction: \'Backtest Results\', eventLabel: \'Dashboard page\'});">Results&nbsp;<img src="/static/imgs/icon-forward.png"></button> </div></div>');
					$(sample_algos[i]).html('');
					$(sample_algos[i]).append(algo_div);
					$(sample_algos[i]).append(algo_result_div);
					$('#'+msg.backtests[i].algo_uuid+msg.backtests[i].seg_sym.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+"pnl_chartContainer_new").replaceWith('<canvas id="'+msg.backtests[i].algo_uuid+msg.backtests[i].seg_sym+'pnl_chartContainer_new"></canvas>');
					// var ctx = document.getElementById(msg.backtests[i].algo_uuid+msg.backtests[i].seg_sym+"pnl_chartContainer_new").getContext('2d');
					// var pnl_chartContainer_new = plot_helper(ctx,msg.backtests[i]['backtest_result'][msg.backtests[i]['seg_sym']]['pnl'])
				}catch(e){
					// console.log(e);
				}
			}
      var z = Math.max(0,3-msg.backtests.length);
      if(z>0){
        for(var i=msg.backtests.length;i<3;i++){
          try{
            $(sample_algos[i]).html('<div class="algo"><h2>No top performer</h2></div><div class="algo_result"><h2 class="backtest_pnl">Backtested P&L <span class="profit">N/A (N/A)</span></h2><div class="result_chart"></div><div class="algo_cta"><button class="try">Results&nbsp;<img src="/static/imgs/icon-forward.png"></button></div></div>');
          }catch(e){

          }
        }

      }
		}  	
  }).complete(function(){
    $('#update_top_performance2').hide();
  });
}

function show_algo_summary(a,i){
  $('.algo_details_window').html(a[i]);
  $('.algo_details_popup').fadeIn();$('body').addClass('body_scroll');
}
function algo_backtests(ev,algo_uuid){
    $(ev.target).html("<img src='/static/imgs/button-loading-rect.gif' id='button_loading'>");
    $(ev.target).css({'cursor': 'no-drop'});
    $(ev.target).removeAttr('onclick');
    ga('send', {hitType: 'event', eventCategory: 'Backtest Results', eventAction: 'Backtest Results', eventLabel: 'Algos page'});

    // $.get('/get_subscription_valid/',{ 
    // }).done(function (data){ 
    //     if(data['status']=="success") 
    //     { 
    post('/backtests/',{ 
          'algo_uuid':algo_uuid 
      },"get"); 
    //     }else{ 
    //         show_snackbar(null,'Please update your subscription to avail all the services!'); 
    //         $(ev.target).html("Backtest results&nbsp;<img src=\"/static/imgs/icon-forward.png\">"); 
    //         $(ev.target).css({'cursor': 'pointer'}); 
    //         $(ev.target).attr('onclick','algo_backtests(event,\''+algo_uuid+'\')'); 
    //         // $(ev.target).focusout(); 
    //     } 
    // }).fail(function(){ 
    //     show_snackbar(null,'Some error occured, please try again!'); 
    //     $(ev.target).html("Backtest results&nbsp;<img src=\"/static/imgs/icon-forward.png\">"); 
    //     $(ev.target).css({'cursor': 'pointer'}); 
    //     $(ev.target).attr('onclick','algo_backtests(event,\''+algo_uuid+'\')'); 
    //     // $(ev.target).focusout(); 
    // }); 
}

function update_top_performance2(){
  var params = {
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/fetch_top_performers/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 400000,//40 sec timeout
    }
    $("#top_performers_loader").show();
    $('#top_performers_table').html('<div class="loading_top_performers"><p>Loading...</p></div>');
    $.ajax(settings).done(function (msg){
    if(msg.status=='success'){
      
      var sample_algos_parent = $('#top_performers_table');
      sample_algos_parent.html('');
      
      t = [];

      var title_row = '<div class="algos_title_row"><div class="row_algo_title"><p>Strategies</p></div><div class="row_instrument_title"><p>Instrument</p></div><div class="row_pnl_title"><p>P&L</p></div><div class="row_action_title"><p></p></div></div>';

      sample_algos_parent.append($(title_row));
      var top_performers_count = 0
      // var sample_algos = sample_algos_parent.find('.top_performers')
      for(var i=0;i<msg.backtests.length;i++){
        if(top_performers_count>=3){
          break;
        }
        try{

          var algo_div = $('<div class="algos_desc_row"></div>');

          var row_disc_div = $('<div class="row_algo_desc"><div class="algo_avatar algo_avatar'+(i+1)+'"><p>'+msg.backtests[i]['algo_obj'].algo_name[0].toUpperCase()+'</p></div><p>'+msg.backtests[i]['algo_obj'].algo_name+'</p></div>');

          var row_disc_desc = $('<div class="row_instrument_desc"><p>'+msg.backtests[i].seg_sym.split('_')[1]+'&nbsp;<span>'+msg.backtests[i].seg_sym.split('_')[0]+'</span></p></div>');

          var row_pnl = $('<div class="row_pnl_desc"></div>')

          if(msg.backtests[i].backtest_result[msg.backtests[i].seg_sym].final_pnl>=0)
            {
              row_pnl = $('<div class="row_pnl_desc"><p class="profit"><span><img src="/static/imgs/icon-arrow-up-green.png"></span>'+msg.backtests[i]['backtest_result'][msg.backtests[i]['seg_sym']].final_pnl.toFixed(2)+'(+'+(msg.backtests[i]['backtest_result'][msg.backtests[i]['seg_sym']].final_pnl/msg.backtests[i]['backtest_result'][msg.backtests[i]['seg_sym']].max_cap_used*100).toFixed(2)+'%)</p></div>');
              top_performers_count = top_performers_count+1;
            }
          else
            continue;
            // row_pnl = $('<div class="row_pnl_desc"><p class="loss"><span><img src="/static/imgs/icon-arrow-down-red.png"></span>'+msg.backtests[i]['backtest_result'][msg.backtests[i]['seg_sym']].final_pnl.toFixed(2)+'('+(msg.backtests[i]['backtest_result'][msg.backtests[i]['seg_sym']].final_pnl/msg.backtests[i]['backtest_result'][msg.backtests[i]['seg_sym']].max_cap_used*100).toFixed(2)+'%)</p></div>');

          t[i]=format_algo_summary2(msg.backtests[i].algo_obj);
          var row_action_desc = $('<div class="row_action_desc"><p><img style="display:none" src="/static/imgs/new/menu_dots.svg"></p><div class="action_buttons" style="display:none"><button class="algo_details" onclick="show_algo_summary(t,'+i+');"><img src="/static/imgs/new/algo_details.svg">Strategy details</button><div  onclick="samples_click(event,\''+msg.backtests[i].algo_uuid+'\');ga(\'send\', {hitType: \'event\', eventCategory: \'Top Algo Go\', eventAction: \'Top Algo Go\', eventLabel: \'Dashboard page\'});"><button class="icon-create-similar"><img src="/static/imgs/new/copy.svg">Copy</button></div><div><button class="icon-dashboard-backtest" id="icon-dashboard-backtest" onclick="algo_backtests(event,\''+msg.backtests[i].algo_uuid+'\')"><img src="/static/imgs/new/b.svg">Backtests</button></div></div></div>');

          algo_div.append(row_disc_div);
          algo_div.append(row_disc_desc);
          algo_div.append(row_pnl);
          algo_div.append(row_action_desc);
          sample_algos_parent.append(algo_div);
          // var ctx = document.getElementById(msg.backtests[i].algo_uuid+msg.backtests[i].seg_sym+"pnl_chartContainer_new").getContext('2d');
          // var pnl_chartContainer_new = plot_helper(ctx,msg.backtests[i]['backtest_result'][msg.backtests[i]['seg_sym']]['pnl'])
        }catch(e){
          console.log(e);
        }
      }
      // var z = Math.max(0,3-msg.backtests.length);
      // z =1;
      if(msg.backtests.length == 0){
        $('#top_performers_table').html('<div class="before_top_performers"><img src="/static/imgs/new/empty/algos-empty.svg"><p class="backtest_row_error_message_display">No top performers</p><button onclick="window.location=\'/strategy\'">Create strategy</button></div>');
        // for(var i=msg.backtests.length;i<3;i++){
        //   try{
        //      $('#top_performers_table').html('<div class="before_top_performers"><img src="/static/imgs/new/empty/algos-empty.svg"><p class="backtest_row_error_message_display">No top performers</p><button onclick="window.location=\'/strategy\'">Create algo</button></div>');
        //   }catch(e){
        //     console.log(e);
        //   }
        // }
      }
    }   
  }).complete(function(){
    $('#update_top_performance2').hide();

    $("#top_performers_loader").hide();
    $(".row_action_desc>p>img").off("click");
    $(".row_action_desc>p>img").click(function(e){
      // alert($(this).parents(".menu_dots").find(".action_buttons").className);
      $(".action_buttons").slideUp();
      $(".row_action_desc>p>img").hide();
      $(this).parents(".row_action_desc").find('p>img').show();
      $(this).parents(".row_action_desc").find('.action_buttons').slideDown();
      action_buttons = true;
      e.stopPropagation();
    });

    $(".algos_desc_row").hover(function(){
      $(this).find(".row_action_desc>p>img").show();
    });
    $(".algos_desc_row").mouseleave(function(){
      $(this).find(".row_action_desc>p>img").hide();
    });
  });
}


function update_samples2(){
  $('#update_top_performance1').show();
  var params = {
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/fetch_samples/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 40000,//40 sec timeout
    }
    
    $("#samples_loader").show();
    $('#samples_table').html('<div class="loading_sample_algos"><p>Loading...</p></div>');

    $.ajax(settings).done(function (msg){
       if(msg.status=='success'){
      
      var sample_algos_parent = $('#samples_table');
      sample_algos_parent.html('');
      s = [];
      var title_row = '<div class="algos_title_row"><div class="row_algo_title"><p>Strategies</p></div><div class="row_instrument_title"><p>Instrument</p></div><div class="row_pnl_title"><p>P&L</p></div><div class="row_action_title"><p></p></div></div>';

      sample_algos_parent.append($(title_row));

      // var sample_algos = sample_algos_parent.find('.top_performers')
      for(var i=0;i<Math.min(msg.samples.length,3);i++){
        try{

          var algo_div = $('<div class="algos_desc_row"></div>');

          var row_disc_div = $('<div class="row_algo_desc"><div class="algo_avatar algo_avatar'+(i+1+3)+'"><p>'+msg.samples[i]['algo_obj'].algo_name[0].toUpperCase()+'</p></div><p>'+msg.samples[i]['algo_obj'].algo_name+'</p></div>');

          var row_disc_desc = $('<div class="row_instrument_desc"><p>'+msg.samples[i].seg_sym.split('_')[1]+'&nbsp;<span>'+msg.samples[i].seg_sym.split('_')[0]+'</span></p></div>');

          var row_pnl = $('<div class="row_pnl_desc"></div>')

          if(msg.samples[i].backtest_result[msg.samples[i].seg_sym].final_pnl>=0)
            row_pnl = $('<div class="row_pnl_desc"><p class="profit"><span><img src="/static/imgs/icon-arrow-up-green.png"></span>'+msg.samples[i]['backtest_result'][msg.samples[i]['seg_sym']].final_pnl.toFixed(2)+'(+'+(msg.samples[i]['backtest_result'][msg.samples[i]['seg_sym']].final_pnl/msg.samples[i]['backtest_result'][msg.samples[i]['seg_sym']].max_cap_used*100).toFixed(2)+'%)</p></div>');
          else
            row_pnl = $('<div class="row_pnl_desc"><p class="loss"><span><img src="/static/imgs/icon-arrow-up-red.png"></span>'+msg.samples[i]['backtest_result'][msg.samples[i]['seg_sym']].final_pnl.toFixed(2)+'('+(msg.samples[i]['backtest_result'][msg.samples[i]['seg_sym']].final_pnl/msg.samples[i]['backtest_result'][msg.samples[i]['seg_sym']].max_cap_used*100).toFixed(2)+'%)</p></div>');

          s[i]=format_algo_summary2(msg.samples[i].algo_obj);

          var row_action_desc = $('<div class="row_action_desc"><p><img style="display:none" src="/static/imgs/new/menu_dots.svg"></p><div class="action_buttons" style="display:none"><button class="algo_details" onclick="show_algo_summary(s,'+i+');"><img src="/static/imgs/new/algo_details.svg">Strategy details</button><div onclick="samples_click(event,\''+msg.samples[i].algo_uuid+'\');ga(\'send\', {hitType: \'event\', eventCategory: \'Sample Algo Go\', eventAction: \'Sample Algo Go\', eventLabel: \'Dashboard page\'});"><button class="icon-create-similar"><img src="/static/imgs/new/copy.svg">Copy</button></div></div></div>');

          algo_div.append(row_disc_div);
          algo_div.append(row_disc_desc);
          algo_div.append(row_pnl);
          algo_div.append(row_action_desc);
          sample_algos_parent.append(algo_div);
          // var ctx = document.getElementById(msg.backtests[i].algo_uuid+msg.backtests[i].seg_sym+"pnl_chartContainer_new").getContext('2d');
          // var pnl_chartContainer_new = plot_helper(ctx,msg.backtests[i]['backtest_result'][msg.backtests[i]['seg_sym']]['pnl'])
        }catch(e){
          console.log(e);
        }
      }
    }   
  }).complete(function(){
    $('#update_top_performance2').hide();

    $("#samples_loader").hide();
    $(".row_action_desc>p>img").off("click");
    $(".row_action_desc>p>img").click(function(e){
      // alert($(this).parents(".menu_dots").find(".action_buttons").className);
      $(".action_buttons").slideUp();
      $(".row_action_desc>p>img").hide();
      $(this).parents(".row_action_desc").find('p>img').show();
      $(this).parents(".row_action_desc").find('.action_buttons').slideDown();
      action_buttons = true;
      e.stopPropagation();
    });

    $(".algos_desc_row").hover(function(){
      $(this).find(".row_action_desc>p>img").show();
    });
    $(".algos_desc_row").mouseleave(function(){
      $(this).find(".row_action_desc>p>img").hide();
    });
  });
}