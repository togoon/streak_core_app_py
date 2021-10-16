run_backtest_flag = true;

backtest_result_response = {};
$(document).ready(function(){

});

function processListToXYList(packedlist){
	var xyList = [];
	for(var i=0;i<packedlist.length;i++){
		xyList.push({
			x:new Date(packedlist[i][0]),
			y:parseInt(packedlist[i][1]),
			pnltext:parseInt(packedlist[i][1])
		});
	}
	return xyList;
}
function broker_toggle(e){
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
			// var ctx = document.getElementById(k+"pnl_chartContainer_new").getContext('2d');
			$('#'+k.replace('&','\\&')+"pnl_chartContainer_new").replaceWith('<canvas id="'+k+'pnl_chartContainer_new"></canvas>');
			var ctx = document.getElementById(k+"pnl_chartContainer_new").getContext('2d');
	
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


			var transactions_table = $('#'+k.replace('&','\\&')).find(".transactions_table");
			transactions_table.empty();

			var trade_log = $("<table>",{}).append('<tr><th>Trigger Date</th><th>Equity</th><th>Buy/Sell</th><th>Qty</th><th>Price</th><th>Profit/Loss</th><th>Portfolio Value</th></tr>');
			var prev_pnl = 0;
			data = backtest_result_response[k];
			for(var i = 0; i <= data.trade_log.length - 1; i++){
				if(data.trade_log[i][3]!=0)
					{
					trade_row = '<tr>';
					date = new Date(data.trade_log[i][0]);
					// trade_row += '<td>'+dateFormat(date, "dS - mmmm - yyyy, h:MM:ss TT")+'</td>';
					// trade_row += '<td>'+dateFormat(date, "dd - mmm - yyyy, hh:MM:ss")+'</td>';
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
					t_pnl -= broker_cal(seg,sym,parseFloat(data.trade_log[i][3]),parseFloat(data.trade_log[i][4]));
					if (t_pnl>=0 && prev_pnl<t_pnl)
						trade_row += '<td class="profit">'+t_pnl.toFixed(2)+'</td>'
					else
						trade_row += '<td class="loss">'+t_pnl.toFixed(2)+'</td>'
					prev_pnl = t_pnl;

					portfolio_val = parseFloat(data.trade_log[i][6]) - broker_cal(seg,sym,parseFloat(data.trade_log[i][3]),parseFloat(data.trade_log[i][4]));

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
		// var ctx = document.getElementById(k+"pnl_chartContainer_new").getContext('2d');
			$('#'+k.replace('&','\\&')+"pnl_chartContainer_new").replaceWith('<canvas id="'+k+'pnl_chartContainer_new"></canvas>');
			var ctx = document.getElementById(k+"pnl_chartContainer_new").getContext('2d');
			max_cap_used = backtest_result_response[k].max_cap_used;
			abs_pnl = processListToXYList(backtest_result_response[k].pnl);
			abs_final_pnl = abs_pnl[abs_pnl.length-1].y;
			pnl_div = $(backtest_results_row).find('.pnl');
			if (abs_final_pnl>=0)
				{
					color = '#06d092';
					img_url = "/static/imgs/icon-arrow-up-green.png";	
					adj_return = abs_final_pnl/max_cap_used*100;//abs_final_pnl/max_cap_used*100;
					pnl_div.html('<p>P&amp;L&nbsp;<span><img src='+img_url+'>&nbsp;</span><span style="color:'+color+'">'+abs_final_pnl+'&nbsp;</span><span style="color:'+color+'" "="">( +'+adj_return.toFixed(2)+'%)&nbsp;</span></p>');
				}
			else
				{
					color = '#ff4343';
					img_url = "/static/imgs/icon-arrow-down-red.png";
					adj_return = abs_final_pnl/max_cap_used*100;//abs_final_pnl/max_cap_used*100;
					pnl_div.html('<p>P&amp;L&nbsp;<span><img src='+img_url+'>&nbsp;</span><span style="color:'+color+'">'+abs_final_pnl+'&nbsp;</span><span style="color:'+color+'" "="">( '+adj_return.toFixed(2)+'%)&nbsp;</span></p>');
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


			var transactions_table = $('#'+k.replace('&','\\&')).find(".transactions_table");
			transactions_table.empty();

			var trade_log = $("<table>",{}).append('<tr><th>Trigger Date</th><th>Equity</th><th>Buy/Sell</th><th>Qty</th><th>Price</th><th>Profit/Loss</th><th>Portfolio Value</th></tr>');
			var prev_pnl = 0;
			data = backtest_result_response[k];
			for(var i = 0; i <= data.trade_log.length - 1; i++){
				if(data.trade_log[i][3]!=0)
					{
					trade_row = '<tr>';
					date = new Date(data.trade_log[i][0]);
					// trade_row += '<td>'+dateFormat(date, "dS - mmmm - yyyy, h:MM:ss TT")+'</td>';
					// trade_row += '<td>'+dateFormat(date, "dd - mmm - yyyy, hh:MM:ss")+'</td>';
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
					if (t_pnl>=0 && prev_pnl<t_pnl)
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

function broker_cal(seg,sym,qty,price,type='CNC'){
	ttt = 0; // total tax and charges
	if(seg='NSE')
	{
		turnover = Math.abs(qty)*price;
		// if(type=='MIS')
		// {
			ttt += (20>turnover*0.0001?20:turnover*0.0001);
		// }
		ttt += 0.00325/100*turnover; //Transaction charges
		ttt += 0.18*ttt; // GST on broker+transaction charges
		if(type=='MIS' && qty<0)
			ttt += 0.025*turnover/100; // STT
		else	
			ttt += 0.1*turnover/100; // STT
		ttt += 15*(turnover/10000000); //SEBI charges
	}
	else if(seg='NFO-FUT')
	{
		turnover = Math.abs(qty)*price;
		ttt += (20>turnover*0.0001?20:turnover*0.0001);
		ttt += 0.0021/100*turnover; //Transaction charges
		ttt += 0.18*ttt; // GST on broker+transaction charges
		if(qty<0)
			ttt += 0.01*turnover/100; // STT
		ttt += 15*(turnover/10000000); //SEBI charges
	}
	return ttt;
}
function processListToXYList_brokerage(seg_sym,trade_log,packedlist){
	var xyList = [];
	var trade_dict = {};
	var max_cap_used = 0;
	[seg,sym] = seg_sym.split('_');
	for(var i=0;i<packedlist.length;i++){
		if(trade_dict[packedlist[i][0]]!=undefined)
			{
			price = trade_dict[packedlist[i][0]][3];
			qty = trade_dict[packedlist[i][0]][2];
			// cap = 
			brokerage = broker_cal(seg,sym,qty,price);
			total_brokerage_till_now += brokerage
			// console.log(brokerage);
			adj_price = parseInt(packedlist[i][1]-total_brokerage_till_now); //adj_price= adj_pnl
			// console.log(adj_price);
			if(max_cap_used<Math.abs(qty)*price+brokerage)
				max_cap_used = Math.abs(qty)*price+brokerage;
			xyList.push({
						x:new Date(packedlist[i][0]),
						y:adj_price,
						pnltext:parseInt(adj_price)
					});
			}
		else{
			adj_price = parseInt(packedlist[i][1]-total_brokerage_till_now); //adj_price= adj_pnl
			// console.log(adj_price);
			xyList.push({
						x:new Date(packedlist[i][0]),
						y:adj_price,
						pnltext:parseInt(adj_price)
					});
		}
	}
	return [xyList,max_cap_used];
}

function refresh_result(algo_uuid,k,msg,seg,sym){
	backtest_result_response[k] = msg[k];
	data = msg[k];
	backtest_result_response[k]=data;
	var backtest_results_row = $("<div>", {id: k, "class": "backtest_results_row"});

	var backtest_results_left = $("<div>",{"class":"backtest_results_left"});
	var results_section = $("<div>",{"class":"results_section"}).append('<div class="chart_section"><div class="chart_header"><div class="equity_section"><p class="company_name">'+sym+' <span class="exc_symbol">'+seg+'</span></p></div><div class="brokerage_section"><p data-tooltip-bottom="Adjusted for brokerage and other charges (does not include stamp duty and DP charges)">Brokerage&nbsp;&nbsp;&nbsp;<label class="switch"><input class="brokerage_toggle" type="checkbox"><span class="slider"></span></label></p></div></div><div class="chart_body"><canvas id="'+k+'pnl_chartContainer_new"></canvas></div></div>');
	//+data.win_count/(data.win_count+data.loss_count)+
	color = '#06d092';
	img_url = "/static/imgs/icon-arrow-up-green.png";
	if(data.final_pnl<0){
		color = '#ff4343';
		img_url = "/static/imgs/icon-arrow-down-red.png";
	}
	var pnl_section = $("<div>",{"class":"pnl_section"}).append('<div class="pnl"><p>P&L&nbsp;<span><img src="'+img_url+'">&nbsp;</span><span style="color:'+color+'">'+parseFloat(data.final_pnl).toFixed(2)+'&nbsp;</span><span style="color:'+color+'"">('+parseFloat(data.final_pnl/data.max_cap_used*100).toFixed(2)+'%)&nbsp;</span></p></div><div class="streak"><div class="streak_body"><div data-tooltip-top="'+data.win_count+"/"+(data.win_count+data.loss_count)+' winning trades" class="wins" style="width:'+data.win_count/(data.win_count+data.loss_count)*100+'%"></div><div class="losses" data-tooltip-top="'+data.loss_count+"/"+(data.win_count+data.loss_count)+' losing trades" style="width:'+data.loss_count/(data.win_count+data.loss_count)*100+'%"></div></div></div><div class="results_table"><table><!--<td>Alpha</td><td>0.079</td></tr><tr><td>Beta</td><td>0.597</td></tr>--><!--<tr><td>Volatility</td><td>'+parseFloat(data.volatility).toFixed(2)+'%</td></tr><tr><td>Sharpe Ratio</td><td>'+parseFloat(data.sharpe).toFixed(2)+'</td></tr>--><!--<tr><td>Sortino</td><td>'+parseFloat(data.volatility).toFixed(2)+'</td></tr>-->' +'<tr><td>Total number of signals</td><td>'+data.total_number_of_signals+'</td></tr>'+'<tr><td>Number of wins</td><td>'+data.win_count+'</td></tr>'+'<tr><td>Number of losses</td><td>'+data.loss_count+'</td></tr>'+'<tr><td>Winning streak</td><td>'+data.winning_streak+'</td></tr>'+'<tr><td>Losing streak</td><td>'+data.lossing_streak+'</td></tr>'+'<tr><td>Max gains</td><td>'+parseFloat(data.maximum_gain).toFixed(2)+'</td></tr>'+'<tr><td>Max loss</td><td>'+parseFloat(data.maximum_loss).toFixed(2)+'</td></tr>'+'<tr><td>Avg gain/winning trade</td><td>'+parseFloat(data.average_gain_per_winning_trade).toFixed(2)+'</td></tr>'+'<tr><td>Avg loss/losing trade</td><td>'+parseFloat(data.average_gain_per_losing_trade).toFixed(2)+'</td></tr>' +'<tr><td>Max Drawdown</td><td>'+parseFloat(data.max_draw).toFixed(2)+'%</td></tr></table></div>');
	results_section.append(pnl_section);

	backtest_results_left.append(results_section);

	var transactions_section = $('<div>',{"class":"transactions_section"}).append('<p>Transaction Details <span><img src="/static/imgs/icon-down-arrow.png"></span></p>');

	backtest_results_left.append(transactions_section);

	var transactions_table = $("<div>",{"class":"transactions_table","style":"display:none;"});

	var trade_log = $("<table>",{}).append('<tr><th>Trigger Date</th><th>Equity</th><th>Buy/Sell</th><th>Qty</th><th>Price</th><th>Profit/Loss</th><th>Portfolio Value</th></tr>');
	var prev_pnl = 0;
	for(var i = 0; i <= data.trade_log.length - 1; i++){
		if(data.trade_log[i][3]!=0)
			{
			trade_row = '<tr>';
			date = new Date(data.trade_log[i][0]);
			// trade_row += '<td>'+dateFormat(date, "dS - mmmm - yyyy, h:MM:ss TT")+'</td>';
			// trade_row += '<td>'+dateFormat(date, "dd - mmm - yyyy, hh:MM:ss")+'</td>';
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
			if (t_pnl>=0 && prev_pnl<t_pnl)
				trade_row += '<td class="profit">'+t_pnl.toFixed(2)+'</td>'
			else
				trade_row += '<td class="loss">'+t_pnl.toFixed(2)+'</td>'

			prev_pnl = t_pnl;
			trade_row += '<td>'+parseFloat(data.trade_log[i][6]).toFixed(2)+'</td>'
			trade_row += '</tr>';
			trade_log.append(trade_row);
		}
	}

	transactions_table.append(trade_log);

	backtest_results_left.append(transactions_table);
	// backtest_results_left complete

	var backtest_results_right = $("<div>",{"class":"backtest_results_right"});
	backtest_results_right.append('<div class="fundamentals_section"><table><caption>Stock Performance</caption><tr><td>Period High</td><td>'+parseFloat(data.period_high).toFixed(2)+'</td></tr><tr><td>Period Low</td><td>'+parseFloat(data.period_low).toFixed(2)+'</td></tr><tr><td>Period return</td><td>'+parseFloat(data.period_return).toFixed(2)+'%</td></tr><!--<tr><td>Period Volatility</td><td>10%</td></tr>--></table></div>');

	var actions_section = $("<div>",{"class":"actions_section"});
	transactions_table_label = [["Date","Symbol","Action","Qty","Price","Profit/Loss","Portfolio Value"]];
	if(deployed_seg_sym.includes(seg+'_'+sym)){
		// actions_section.html('<table class="actions_buttons"><tr><td><button class="force_stop" onclick=\'force_stop(event,"'+deployed_seg_sym_deployment_uuid[seg+'_'+sym]+'")\'><span><img src="/static/imgs/icon-force-stop.png"></span>&nbsp;&nbsp;&nbsp;Stop</button></td></tr><tr><td><button class="download"><span><img src="/static/imgs/icon-download.png"></span>&nbsp;&nbsp;&nbsp;Download</button></td></tr></table><div class="social_buttons"><span><button><img src="/static/imgs/icon-linkedin.png"></button></span><span><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button><img src="/static/imgs/icon-facebook.png"></button></span><span><button><img src="/static/imgs/icon-twitter.png"></button></span></div>');
		actions_section.html('<!--<table class="actions_buttons"><tr><td><button class="deploy_disabled" onclick=\'force_stop(event,"'+deployed_seg_sym_deployment_uuid[seg+'_'+sym]+'")\'><span><img src="/static/imgs/icon-deploy.png"></span>&nbsp;&nbsp;&nbsp;Automate</button></td></tr><tr><td><button class="download" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button><button class="share" onclick="generate_shareable_link(\''+algo_uuid+'\',\''+seg+'_'+sym+'\')"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button><img src="/static/imgs/icon-linkedin.png"></button></span><span><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button><img src="/static/imgs/icon-facebook.png"></button></span><span><button><img src="/static/imgs/icon-twitter.png"></button></span></div>-->');
	}
	else{
		actions_section.html('<!--<table class="actions_buttons"><tr><td><button class="deploy" onclick=\'deploy_algorithm_popup("'+algo_uuid+'","'+sym+'","'+seg+'")\'><span><img src="/static/imgs/icon-deploy.png"></span>&nbsp;&nbsp;&nbsp;Automate</button></td></tr><tr><td><button class="download" onclick="exportToCsv(\''+k+'.csv\',transactions_table_label.concat(backtest_result_response[\''+k+'\'].trade_log))"><span><img src="/static/imgs/icon-new-download.png"></span></button><button class="share" onclick="generate_shareable_link(\''+algo_uuid+'\',\''+seg+'_'+sym+'\')"><span><img src="/static/imgs/icon-share.png"></span></button></td></tr></table><div class="social_buttons"><span><button><img src="/static/imgs/icon-linkedin.png"></button></span><span><button><img src="/static/imgs/icon-whatsapp.png"></button></span><span><button><img src="/static/imgs/icon-facebook.png"></button></span><span><button><img src="/static/imgs/icon-twitter.png"></button></span></div>-->');
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
	$('#'+k.replace('&','\\&')+"pnl_chartContainer_new").replaceWith('<canvas id="'+k+'pnl_chartContainer_new"></canvas>');
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
	$('#'+k.replace('&','\\&')+' .brokerage_toggle:checkbox').on('change',function(e){
		broker_toggle(e);
	});
}
function refresh_error(k,msg){
	data = msg[k];
	try{
		[seg,sym] = k.split("_");
		if(k!='runtime' && k!='updated_time'){
			var backtest_results_row = $("<div>", {id: k, "class": "backtest_results_row"});
			var backtest_results_left = $("<div>",{"class":"backtest_results_left"});
			var results_section = $("<div>",{"class":"results_section"}).append('<div class="chart_section"><div class="chart_header"><div class="equity_section"><p class="company_name">'+sym+' <span class="exc_symbol">'+seg+'</span></p></div><div class="brokerage_section"><p></p></div></div><div class="chart_body"><div id="'+k+'pnl_chartContainer_new"><p></p></div></div></div>');
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