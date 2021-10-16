equity_added = {}

url_selector = 1;
run_backtest_flag = true;
function lmda_vs_ec2_select(){
	var interval = $("#ip_interval").val();
	[from_datepicker,to_datepicker] = $('#date_range').val().split(' – ');
	var day_range = Math.abs(new Date(to_datepicker)-new Date(from_datepicker))/(1000*3600*24);
	var equity_added_len = Object.keys(equity_added).length;

	if(interval=='min' && day_range>10 && equity_added_len>3)
		url_selector = 2;
	else if(interval=='5min' && day_range>52 && equity_added_len>3)
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
}
$(window).scroll(function(){
		var margin = $(".test_headers").height();
		if($(window).scrollTop() > 70){
			// $(".header").css({"position" : "relative"});
			$(".header").hide();
			$(".test_headers").css({"top" : "0px"},{"margin-top" : "0px"});
			$(".backtest_results").css({"margin-top" : "0px"});
			$(".test_headers").css({"box-shadow" : "0 2px 4px 0 rgba(0, 0, 0, 0.03)"});
		}
		else{
			// $(".header").css({"position" : "fixed"});
			$(".header").show();
			$(".test_headers").css({"top" : "70px"},{"margin-top" : "0px"});
			$(".backtest_results").css({"margin-top" : margin+"px"});
			$(".test_headers").css({"box-shadow" : "none"});
		}
	});
 $(document).ready(function(){
  	Chart.defaults.global.defaultFontColor = '#7f8fa4';
	Chart.defaults.global.defaultFontFamily = "'Roboto', sans-serif";
	Chart.defaults.global.defaultFontSize = 10;
	Chart.defaults.global.defaultFontStyle = 'normal';
    $("#from_datepicker").datepicker();
    $("#to_datepicker").datepicker();
    $(".charts").each(function(){$(this).hide()});
    $(".transactions_table").hide();
    $(".condition_not_met").hide();
    $(".low_capital").hide();
    var margin = $(".test_headers").height();
    $(".backtest_results").css({"margin-top" : margin+"px"});
    $(".added_equities img").click(function(){
		$(this).parentsUntil('.added_equities').hide();
	});
	disable_edit();
  });
  $(document).ready(function(){
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
	$(".share").click(function(){
    	$(this).parents(".actions_section").find(".social_buttons").fadeToggle();
  	});
 	$('.added_equities span').each(function(e){
 		if($(this).data('syms')!=null){
 			[sym,seg]=$(this).data('syms').split('_');
 			equity_added[sym]=seg;
 		}
 	});
 	$(".added_equities img").click(function(){
		x = $($($(this).parentsUntil('.added_equities')).find('span')[0]).data('syms');
		if(x!=null){
			[sym,seg] = x.split('_');
			delete equity_added[sym];
		}
		$(this).parentsUntil('.added_equities').remove();
	});

 	$( "#equities_input" ).autocomplete({
	  source: function(request,response){
		params = {'query':request['term'].toLowerCase()}
		$.get('/autocomplete/', params,function(data) {
			// alert(data);
			if(data['status']=='success'){

				response($.map(data['results'], function (el) {
					 return {
						 label: el[0]+'-'+el[4],
						 value: el[1]+' '+el[4] //assumption, symbols and segment name does not have space in between
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
	   		$('.added_equities').append('<span><span data-syms="'+val[0]+'_'+val[1]+'">'+ui.item.value+'</span><span><img src="/static/imgs/icon-strategy-remove_equity.png"></span></span>');
		   	// symbols.push(ui.item.value.split(' ').reverse());
		   	// ui.item.value = "";
		   	$(".added_equities img").click(function(){

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
			});
			
			equity_added[val[0]]=val[1];
			$($('.adding_equities_section div span')[0]).css("background-color", "#06D092");
			$($('.adding_equities_section div span')[0]).css("border-color", "#B1FDE6");

	   	}
		$("#equities_input").val('');
	    $("#equities_input").focus();
	   	return false
	   }
	});

 	if (run_backtest_flag == true)
		run_backtest();
  });
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
function back_test_input_valid(){
  return true;
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
	data = msg[k];

	var backtest_results_row = $("<div>", {id: k, "class": "backtest_results_row"});

	var backtest_results_left = $("<div>",{"class":"backtest_results_left"});
	var results_section = $("<div>",{"class":"results_section"}).append('<div class="chart_section"><div class="chart_header"><div class="equity_section"><p class="company_name">'+sym+' <span class="exc_symbol">'+seg+'</span></p></div><div class="brokerage_section"><p>Brokerage&nbsp;&nbsp;&nbsp;<label class="switch"><input class="brokerage_toggle" type="checkbox" checked><span class="slider"></span></label></p></div></div><div class="chart_body"><canvas id="'+k+'pnl_chartContainer_new"></canvas></div></div>');
	//+data.win_count/(data.win_count+data.loss_count)+
	color = '#06d092';
	img_url = "/static/imgs/icon-arrow-up-green.png";
	if(data.final_pnl<0){
		color = '#ff4343';
		img_url = "/static/imgs/icon-arrow-down-red.png";
	}
	var pnl_section = $("<div>",{"class":"pnl_section"}).append('<div class="pnl"><p>P&L&nbsp;<span><img src="'+img_url+'">&nbsp;</span><span style="color:'+color+'">'+parseFloat(data.final_pnl).toFixed(2)+'&nbsp;</span><span style="color:'+color+'"">('+parseFloat(data.return).toFixed(2)+'%)&nbsp;</span></p></div><div class="streak"><div class="streak_body"><div class="wins" style="width:'+data.win_count/(data.win_count+data.loss_count)*100+'%"></div><div class="losses" style="width:'+data.loss_count/(data.win_count+data.loss_count)*100+'%"></div></div></div><div class="results_table"><table><!--<td>Alpha</td><td>0.079</td></tr><tr><td>Beta</td><td>0.597</td></tr>--><tr><td>Volatility</td><td>'+parseFloat(data.volatility).toFixed(2)+'%</td></tr><tr><td>Sharpe Ratio</td><td>'+parseFloat(data.sharpe).toFixed(2)+'<!--</td></tr><tr><td>Sortino</td><td>'+parseFloat(data.volatility).toFixed(2)+'</td></tr>--><tr><td>Max Drawdown</td><td>'+parseFloat(data.max_draw).toFixed(2)+'%</td></tr></table></div>');
	results_section.append(pnl_section);

	backtest_results_left.append(results_section);

	var transactions_section = $('<div>',{"class":"transactions_section"}).append('<p>Transaction Details <span><img src="/static/imgs/icon-down-arrow.png"></span></p>');

	backtest_results_left.append(transactions_section);

	var transactions_table = $("<div>",{"class":"transactions_table","style":"display:none;"});

	var trade_log = $("<table>",{}).append('<tr><th>Date</th><th>Equity</th><th>Buy/Sell</th><th>Qty</th><th>Price</th><th>Profit/Loss</th><th>Portfolio Value</th></tr>');
	for(var i = 0; i <= data.trade_log.length - 1; i++){
		if(data.trade_log[i][3]!=0)
			{
			trade_row = '<tr>';
			date = new Date(data.trade_log[i][0]);
			// trade_row += '<td>'+dateFormat(date, "dS - mmmm - yyyy, h:MM:ss TT")+'</td>';
			trade_row += '<td>'+dateFormat(date, "dd - mmm - yyyy, h:MM:ss")+'</td>';
			trade_row += '<td>'+data.trade_log[i][1]+'</td>'
			trade_row += '<td>'+data.trade_log[i][2]+'</td>'
			trade_row += '<td>'+data.trade_log[i][3]+'</td>'
			trade_row += '<td>'+parseFloat(data.trade_log[i][4]).toFixed(2)+'</td>'
			trade_row += '<td>'+parseFloat(data.trade_log[i][5]).toFixed(2)+'</td>'
			trade_row += '<td>'+parseFloat(data.trade_log[i][6]).toFixed(2)+'</td>'
			trade_row += '</tr>';
			trade_log.append(trade_row);
		}
	}

	transactions_table.append(trade_log);

	backtest_results_left.append(transactions_table);
	// backtest_results_left complete

	var backtest_results_right = $("<div>",{"class":"backtest_results_right"});
	backtest_results_right.append('<div class="fundamentals_section"><table><caption>Stock Performance</caption><tr><td>1 Mo. Return</td><td>-7.46%</td></tr><tr><td>1 Yr. Return</td><td>-12.85%</td></tr><tr><td>52 Wk High</td><td>1082.70</td></tr><tr><td>52 Wk Low</td><td>860.00</td></tr><tr><td>P/E</td><td>14.47</td></tr><tr><td>Div. Yield</td><td>2.84%</td></tr></table></div>');

	var actions_section = $("<div>",{"class":"actions_section"});
	if(deployed_seg_sym.includes(seg+'_'+sym)){
		// actions_section.html('<table class="actions_buttons"><tr><td><button class="force_stop" onclick=\'force_stop(event,"'+deployed_seg_sym_deployment_uuid[seg+'_'+sym]+'")\'><span><img src="/static/imgs/icon-force-stop.png"></span>&nbsp;&nbsp;&nbsp;Stop</button></td></tr><tr><td><button class="download"><span><img src="/static/imgs/icon-download.png"></span>&nbsp;&nbsp;&nbsp;Download</button></td></tr></table><div class="social_buttons"><span><button><img src="/static/imgs/icon-linkedin.png"></button></span><span><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button><img src="/static/imgs/icon-facebook.png"></button></span><span><button><img src="/static/imgs/icon-twitter.png"></button></span></div>');
		actions_section.html('<table class="actions_buttons"><tr><td><button class="deploy_disabled" onclick=\'force_stop(event,"'+deployed_seg_sym_deployment_uuid[seg+'_'+sym]+'")\'><span><img src="/static/imgs/icon-deploy.png"></span>&nbsp;&nbsp;&nbsp;Automate</button></td></tr><tr><td><button class="download"><span><img src="/static/imgs/icon-new-download.png"></span></button><button class="share"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button><img src="/static/imgs/icon-linkedin.png"></button></span><span><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button><img src="/static/imgs/icon-facebook.png"></button></span><span><button><img src="/static/imgs/icon-twitter.png"></button></span></div>');
	}
	else{
		actions_section.html('<table class="actions_buttons"><tr><td><button class="deploy" onclick=\'deploy_algorithm_popup("'+algo_uuid+'","'+sym+'","'+seg+'")\'><span><img src="/static/imgs/icon-deploy.png"></span>&nbsp;&nbsp;&nbsp;Automate</button></td></tr><tr><td><button class="download"><span><img src="/static/imgs/icon-new-download.png"></span></button><button class="share"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button><img src="/static/imgs/icon-linkedin.png"></button></span><span><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button><img src="/static/imgs/icon-facebook.png"></button></span><span><button><img src="/static/imgs/icon-twitter.png"></button></span></div>');
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
		if($(this).find("img").attr("src") == "/static/imgs/icon-down-arrow.png"){
		$(this).find("img").attr("src", "/static/imgs/icon-up-arrow.png");	
		}
		else{
		$(this).find("img").attr("src", "/static/imgs/icon-down-arrow.png");
		}
	});

	// var ctx = document.getElementById(k+"pnl_chartContainer_new").getContext('2d');
	var ctx = document.getElementById(k+"pnl_chartContainer_new").getContext('2d');
	
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
                	fontColor: '#7f8fa4',
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
					fontColor: '#7f8fa4'
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

function refresh_error(k,msg){
	data = msg[k];
	try{
		[seg,sym] = k.split("_");
		if(k!='runtime' && k!='updated_time'){
			var backtest_results_row = $("<div>", {id: k, "class": "backtest_results_row"});
			var backtest_results_left = $("<div>",{"class":"backtest_results_left"});
			var results_section = $("<div>",{"class":"results_section"}).append('<div class="chart_section"><div class="chart_header"><div class="equity_section"><p class="company_name">'+sym+' <span class="exc_symbol">'+seg+'</span></p></div><div class="brokerage_section"><p>Brokerage&nbsp;&nbsp;&nbsp;<label class="switch"><input class="brokerage_toggle" type="checkbox" checked><span class="slider"></span></label></p></div></div><div class="chart_body"><div id="'+k+'pnl_chartContainer_new"><p></p></div></div></div>');
			backtest_results_left.append(results_section);
			backtest_results_row.append(backtest_results_left);
			$('.backtest_results_body').append(backtest_results_row);
			$("#"+k+"pnl_chartContainer_new").html(data['error_msg']);
		}
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
        	$('.edit_strategy').removeClass("action_buttons_disabled");
        	$('.edit_strategy').find('img').attr("src","/static/imgs/icon-edit.png");
        }
		else if(data['deployed']){
			$('.edit_strategy').addClass("action_buttons_disabled");
			$('.edit_strategy').find('img').attr("src","/static/imgs/icon-edit-disabled.png");
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
function run_backtest() {
  $(".loader_parent_backtest" ).fadeIn();
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
  var interval = $("#ip_interval").val();

  [from_datepicker,to_datepicker] = $('#date_range').val().split(' – ');

  var commission = 0;//$("#commission option:selected").val();
  symbols = [];
  for(sym in equity_added){
  	seg = equity_added[sym];
  	symbols.push([seg,sym]);
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
      'action_type':position_type.toUpperCase(),
      'quantity':quantity,
      'symbols':symbols,
      'stop_loss':stop_loss,
      'take_profit':take_profit,
      'dt_start':from_datepicker,
      'dt_stop':to_datepicker,
      'time_frame':interval,
      'commission':commission
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
	  "timeout": 60000,//40 sec timeout
	}

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
			$('.ti_msg').html('No trades got executed for the strategy !');
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
  ga('send', 'event', 'Backtest Ran');
}

function processListToXYList(packedlist){
	var xyList = []
	for(var i=0;i<packedlist.length;i++){
		xyList.push({
			x:new Date(packedlist[i][0]),
			y:parseInt(packedlist[i][1]),
			pnltext:parseInt(packedlist[i][1])
		});
	}
	return xyList;
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
                                swal("Success","Algorithm Deployed","success");
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

	var quantity = $("#ip_quantity").val();
	var stop_loss = $("#ip_stoploss").val();
	var take_profit = $("#ip_takeprofit").val();
	var interval = $("#ip_interval").val();

    $('.deploy_summary_heading p').html(algo_name);
    $('#entry_condition_summary').html(entry);
    
    if(exit!='')
        $('#exit_condition_summary').html(entry);
    else{
        $('#exit_condition_summary').html('Sell '+quantity+' shares of '+sym+' at Stop loss of '+stop_loss+'% or Take profit of '+take_profit+'%.');
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
    $('.popup').show();
    $('.deploy_confirm').css('background-color','#bfc7d1 !important');
    $('.deploy_confirm').unbind('click');
    $('#trading_terms_checkbox').change(function(){
        if($('#trading_terms_checkbox:checked').is(':checked')){
            $('.deploy_confirm').css('background-color','#06d092 !important');
            $('.deploy_confirm').bind('click',function(){
                deploy_algorithm(algo_uuid,sym,seg);
            });
        }else{
            $('.deploy_confirm').css('background-color','#bfc7d1 !important');
            $('.deploy_confirm').unbind('click');
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
    interval = $('#ip_interval').val();

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

    $.post('/deploy_algorithm/',params,function(data){
        if(data['status']=='success'){
            window.location = '/dashboard';
            // var redirect = '/dashboard/';
            // delete params["html_block"];
            // params['algo_uuid']=data['algo_uuid'];
            // $.redirectPost(redirect, params);
        }
        else{
            // handle any error from save algorithm
        }
    });
    $('body').removeClass('body_scroll');
};