$(window).load(function() {
    // Animate loader off screen
    $(".loader_parent").fadeOut();
  });
var pagination = 0;
var g_limit = 20;
var g_status = 0;
$(document).ready( function() {
//     $('.force_stop').hover(function(){
//         if($(this).find("img").attr("src") == "/static/imgs/icon-force-stop.png"){
//             $(this).find("img").attr('src','/static/imgs/icon-force-stop-white.png');
//         }
//         else{
//             $(this).find("img").attr('src','/static/imgs/icon-force-stop.png');
//         }
//     });
//     $('.bt_graph').hover(function(){
//         if($(this).find("img").attr("src") == "/static/imgs/icon-bt-graph-brown.png"){
//             $(this).find("img").attr('src','/static/imgs/icon-bt-graph-white.png');
//         }
//         else{
//             $(this).find("img").attr('src','/static/imgs/icon-bt-graph-brown.png');
//         }
//     });
    $(".recent_notif, .icon-order-log").click(function(){
        $(this).parents(".orders_details").find(".orders_details_body").slideToggle();
        // $(".orders_details_body").hide();
    });
    //  $(".recent_notif").hover(function(){
    //     $(this).find("img").toggleClass("icon-order-log-hover");
    // });
    $(".algo_section").click(function(){
        $(".algo_title p").removeClass("highlighted");
        $(".equities td").removeClass("highlighted");
        $(".algo_title img").hide();
        $(this).find(".algo_title p").addClass("highlighted");
        $(this).find(".equities td").addClass("highlighted");
        $(this).find(".algo_title img").show();
    });
    $(".equities_row tr").click(function(){
        $(".equity_pointer").removeClass("highlighted_pointer");
        $(this).find(".equity_pointer").addClass("highlighted_pointer");
    });
    $(".algo_title").click(function(){
        $(".equity_pointer").removeClass("highlighted_pointer");
        $(this).parentsUntil(".orders_left").find(".equities_row:first-child .equity_pointer").addClass("highlighted_pointer");
    });
    $(".bt_graph").click(function(){
        $(".results_section").hide();
        $(this).parentsUntil(".orders_details_title").find(".results_section").fadeIn();
    });
    $(".results_section").mouseleave(function(){
        $(".results_section").hide();
    });
    $(".algo_status").change(function(){
        status = parseInt($(this).val());
        pagination = 0;
        g_status = status;
        load_order_log(status,g_limit,pagination);
    });
    load_order_log(0,g_limit,0);
});
function close_orders_popup() {
    $(".close_popup").parents(".body").find(".force_stop_popup").fadeOut();
    $("body").removeClass("body_scroll");
}
function close_order_details_popup () {
    $(".close_popup").parents(".body").find(".order_details_popup").fadeOut();
    $("body").removeClass("body_scroll");
}
function force_stop(event,deployment_uuid){
    force_stop_button(deployment_uuid);
    $('#keep_positions_open').html('Keep positions open');
    $('#keep_positions_open').removeAttr('onclick');
    $('#exit_positions_now').removeAttr('style');
    $('#keep_positions_open').attr('onclick',
        "keep_position_open('"+deployment_uuid+"');"       
    );

    $('#exit_positions_now').html('Exit positions now');
    $('#exit_positions_now').removeAttr('onclick');
    $('#exit_positions_now').removeAttr('style');
    $('#exit_positions_now').attr('onclick',"exit_position_now('"+deployment_uuid+"');");
}
function force_stop_button(deployment_uuid){
    $('.exit_position, .algo_stopped').hide();$('.force_stop_popup, .stop_options').show();
    // $('#keep_positions_open').unbind('click');
    // $('#keep_positions_open').on('click',function(){
    //     keep_position_open(deployment_uuid);       
    // });

    // $('#exit_positions_now').unbind('click');
    // $('#exit_positions_now').on('click',function(){
    //     exit_position_now(deployment_uuid);
    // });
}

function exit_position_now_force_stop(deployment_uuid,seg,sym,quantity,order_type,transaction_type,product,validity,algo_uuid,algo_name){

    $('#force_stop_action').html("<img src='/static/imgs/button-loading-rect.gif' id='button_loading'>");
    $('#force_stop_action').css({'cursor': 'no-drop'});
    $('#force_stop_action').removeAttr('onclick');

    var exch = seg;
    [exch,t]=seg.split('-');
    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    var params = {
        'deployment_uuid':deployment_uuid,
        'algo_uuid':algo_uuid,
        'algo_name':algo_name,
        'exch':exch,
        'seg':seg,
        'sym':sym,
        'order_type':order_type,
        'transaction_type':transaction_type,
        'quantity':quantity,
        'product':product,
        'validity':validity,
        'csrfmiddlewaretoken':csrfmiddlewaretoken
    }

    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/exit_position_now_force_stop/',
      "method": "POST",
      "headers": {
      },
      "data":params,
      "timeout": 5000,//40 sec timeout
    }
    $.ajax(settings).done(function (msg){
        if(msg.status=='success')
            {
                console.log(msg.status);
                $('.exit_position, .stop_options').hide();$('.algo_stopped').show();
                setTimeout(function(){ window.location = '/order_log/'; }, 3000);
            }
        else{
            $('.force_stop_popup').hide();
            show_snackbar(null,'Some error occured, please try again!');
            }
        }).fail(function(msg){
            $('.force_stop_popup').hide();
            show_snackbar(null,'Some error occured, please try again!');
        });
    // $('.exit_position, .stop_options').hide();$('.algo_stopped').show();
}
function fetch_open_positions(deployment_uuid){
    var params = {
        'deployment_uuid':deployment_uuid,
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/fetch_open_positions/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 5000,//40 sec timeout
    }

    $.ajax(settings).done(function (msg){
        if(msg.status=='success')
            {
                positions = msg.positions;
                exit_window = $('.exit_window');
                if (positions == {})
                    {
                        exit_window.find('.exit_header').html("<p>No positions to exit</p>");
                        exit_window.find('.exit_body').html('<div><button id="buy" onclick="keep_position_open(\''+deployment_uuid+'\');">Confirm</button></div>');
                    }
                else{
                        // seg_sym = [];
                        // for(var k in positions) seg_sym.push(k)
                        if(positions.qty==0){
                            exit_window.find('.exit_header').html("<p>No positions to exit</p>");
                            exit_window.find('.exit_body').html('<div><button id="buy" onclick="keep_position_open(\''+deployment_uuid+'\');">Confirm</button></div>');
                        }
                        else if(positions.qty>=0){
                            [seg,sym] = [msg['seg'],msg['sym']];
                            exit_window.find('.exit_header').html("<p>SELL "+positions.qty+' AT MARKET</p>');
                            exit_window.find('.exit_body').html('<div class="exit_options"><div><div class="radio_options"><div><span></span><p>CNC</p></div><div><span id="buy_radio_option"></span><p id="option_selected">MIS</p></div></div><div class="exit_qty"><p>Quantity</p><input type="number" id="position_qty" name="" value="'+positions.qty+'"></div></div><div><div class="radio_options"><div><span id="buy_radio_option"></span><p id="option_selected">MKT</p></div><div><span></span><p>LMT</p></div></div><div class="exit_price"><p>Price</p><input type="number" id="position_price" name="" value="0"></div></div></div><div><button id="sell" onclick="exit_position_now_force_stop(\''+deployment_uuid+'\',\''+seg+'\',\''+sym+'\','+positions.qty+',\'MARKET\',\'SELL\',\'MIS\',\'DAY\',\''+msg.algo_uuid+'\',\''+msg.algo_name+'\');">Sell</button></div>');
                        }
                        else if(positions[seg_sym[0]].qty<0){
                            [seg,sym] = [msg['seg'],msg['sym']];
                            exit_window.find('.exit_header').html("<p>SELL "+positions.qty+' AT MARKET</p>');
                            exit_window.find('.exit_body').html('<div class="exit_options"><div><div class="radio_options"><div><span></span><p>CNC</p></div><div><span id="buy_radio_option"></span><p id="option_selected">MIS</p></div></div><div class="exit_qty"><p>Quantity</p><input type="number" id="position_qty" name="" value="'+positions.qty+'"></div></div><div><div class="radio_options"><div><span id="buy_radio_option"></span><p id="option_selected">MKT</p></div><div><span></span><p>LMT</p></div></div><div class="exit_price"><p>Price</p><input type="number" id="position_price" name="" value="0"></div></div></div><div><button id="buy" onclick="exit_position_now_force_stop(\''+deployment_uuid+'\',\''+seg+'\',\''+sym+'\','+positions.qty+',\'MARKET\',\'BUY\',\'MIS\',\'DAY\',\''+msg.algo_uuid+'\',\''+msg.algo_name+'\');">BUY</button></div>');
                        }
                    }

            }
        else
           { 
            // alert(msg.status);
            $('.force_stop_popup').hide();
            show_snackbar(null,'Some error occured, please try again!');
           }

    }).fail(function(msg){
        // console.log(msg);
        $('.force_stop_popup').hide();
        show_snackbar(null,'Some error occured, please try again!');
    }).complete(function(){
        $('#exit_positions_now').html('Exit positions now');
        $('#exit_positions_now').removeAttr('onclick');
        $('#exit_positions_now').removeAttr('style');
        $('#exit_positions_now').attr('onclick',"exit_position_now('"+deployment_uuid+"');");
    });
}
function exit_position_now(deployment_uuid){
    // TODO put a 
    $('.stop_options, .algo_stopped').hide();
    
    // 1. Fetch the latest position for this algo
    // 2. Show exit_position in according to the data fetched

    $('.exit_position').show();
    $('#exit_positions_now').html("<img src='/static/imgs/button-loading-rect.gif' id='button_loading'>");
    $('#exit_positions_now').css({'cursor': 'no-drop'});
    $('#exit_positions_now').removeAttr('onclick');
    fetch_open_positions(deployment_uuid);
    // var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    // var params = {
    //     'deployment_uuid':deployment_uuid,
    //     'csrfmiddlewaretoken':csrfmiddlewaretoken
    // };
    // var settings = {
    //   "async": true,
    //   "crossDomain": true,
    //   "url": '/exit_with_positions_open/',
    //   "method": "POST",
    //   "headers": {
    //   },
    //   "data":params,
    //   "timeout": 5000,//40 sec timeout
    // }

    // $.ajax(settings).done(function (msg){
    //     if(msg.status=='success')
    //         {
    //             $('.exit_position, .stop_options').hide();$('.algo_stopped').show();
    //             // $('#close_orders_popup_div').unbind('click');
    //             // $('#close_orders_popup_div').prop('onclick',null).off('click');
    //             // $('#close_orders_popup_div').prop('onclick',function(){
    //             setTimeout(function(){ window.location = '/order_log/'; }, 3000);
    //             // }).on('click');
    //         }
    //     else
    //        { 
    //         alert(msg.status);
    //        }

    // }).fail(function(msg){
    //     console.log(msg);
    // });
}
function keep_position_open(deployment_uuid){

    $('#keep_positions_open').html("<img src='/static/imgs/button-loading-rect.gif' id='button_loading'>");
    $('#keep_positions_open').css({'cursor': 'no-drop'});
    $('#keep_positions_open').removeAttr('onclick');

    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    var params = {
        'deployment_uuid':deployment_uuid,
        'csrfmiddlewaretoken':csrfmiddlewaretoken
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/exit_with_positions_open/',
      "method": "POST",
      "headers": {
      },
      "data":params,
      "timeout": 5000,//40 sec timeout
    }

    $.ajax(settings).done(function (msg){
        if(msg.status=='success')
            {
                $('.exit_position, .stop_options').hide();$('.algo_stopped').show();
                // $('#close_orders_popup_div').unbind('click');
                // $('#close_orders_popup_div').prop('onclick',null).off('click');
                // $('#close_orders_popup_div').prop('onclick',function(){
                setTimeout(function(){ window.location = '/order_log/'; }, 3000);
                // }).on('click');
            }
        else
           { 
            // alert(msg.status);
            $('.force_stop_popup').hide();
            show_snackbar(null,'Some error occured, please try again!');
           }

    }).fail(function(msg){
        // console.log(msg);
        $('.force_stop_popup').hide();
        show_snackbar(null,'Some error occured, please try again!');
    });
}
function show_more_click(){
    pagination += 1;
    load_order_log(g_status,g_limit,pagination);   
}
function load_order_log(status,limit,page){
    var params = {
        'status':status,
        'limit':limit,
        'page':page
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/fetch_order_log/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 5000,//40 sec timeout
    }
    $('.empty_orders_right').hide();
    switch(parseInt(status)) {
        case 0:$(".status_select select").attr("style","color : #06d092 !important"); break;
        case -1:$(".status_select select").attr("style","color : rgba(255, 67, 67, 0.7) !important"); break;
        case 1:$(".status_select select").attr("style","color : rgba(245, 166, 35, 0.9) !important"); break;
    }
    $.ajax(settings).done(function (msg){
        // console.log(msg);
        orders_right = $('.orders_right');
        orders_right.html('');
        log = msg.grouped_orders
        if(log == null){
            return;
            }
        // algo loop
        try{
            if (log.length<1){
                switch(parseInt(status)) {
                    case 0:no_orders_html = '<div class="empty_orders_right" style="display: none;"> <img src="/static/imgs/empty-orders.png"> <p>No algorithm live yet.<br>Go to <a href="/dashboard">backtest results</a> to deploy a algorithm.</p> </div> '; break;
                    case -1:no_orders_html = '<div class="empty_orders_right" style="display: none;"> <img src="/static/imgs/empty-orders.png"> <p>No algorithm stopepd yet.<br>Go to <a href="/dashboard">backtest results</a> to deploy a algorithm.</p> </div> '; break;
                    case 1:no_orders_html = '<div class="empty_orders_right" style="display: none;"> <img src="/static/imgs/empty-orders.png"> <p>No algorithm archived yet.<br>Go to <a href="/dashboard">backtest results</a> to deploy a algorithm.</p> </div> '; break;
                }
                $('.orders_right').html(no_orders_html);
                $('.empty_orders_right').show();
            }
            else
            for (var i = 0; i<log.length; i++){
                try{
                    algo = log[i];
                    orders_details = $('<div class="orders_details"></div>');
                    orders_details_title_outer = $('<div class="orders_details_title_outer"></div>');
                    orders_details_title = $('<div class="orders_details_title"></div>');
                    title = $('<div class=token__'+algo.segment_symbol+'></div>');
                    title.append('<div><p class="algo_name">'+algo.algo_name+'</p></div>');
                    title.append('<div><p class="deployed_date">'+moment(algo.deployment_time).format('h:mm:ss A on MM/DD/YYYY ')+'</p></div>');
                    switch(parseInt(status)) {
                        case 0:title.append('<div><p class="algo_status_live">'+'Live'+'</p></div>'); break;
                        case -1:title.append('<div><p class="algo_status_stopped">'+'Stopped'+'</p></div>'); break;
                        case 1:title.append('<div><p class="algo_status_completed">'+'Completed'+'</p></div>'); break;
                    }
                    title.append('<div><p class="eq_name">'+algo.symbol+'<span>&nbsp;'+algo.segment+'</span></p></div>');
                    title.append('<div><p class="ltp" id="instrument_token"><span class="sub_title">LTP:&nbsp;&nbsp;</span><span class="sub_ltp">0.0</span></p></div>');
                    if(!['Waiting','Stopped','Completed'].includes(algo.logs[0].log_tag) && algo.logs[0].notification_data!=null)
                        {
                         if(algo.logs[0].notification_data.trigger_price=="0")
                            algo.logs[0].notification_data.trigger_price = 'MARKET';
                        // if(algo.logs[0].notification_data.action_type=="SELL" && algo.logs[0].notification_data.type!="take-profit" && algo.logs[0].notification_data.type!="inrange" && algo.logs[0].notification_data.type!="stop-loss")
                        //     algo.logs[0].log_tag = 'sold'
                        // else if(algo.logs[0].notification_data.action_type=="BUY" && algo.logs[0].notification_data.type!="take-profit" && algo.logs[0].notification_data.type!="inrange" && algo.logs[0].notification_data.type!="stop-loss")
                        //     algo.logs[0].log_tag = 'bought'

                        title.append('<div class="recent_notif"><div class="notif_message"><p>'+algo.logs[0].log_message+'</p><p class="'+algo.logs[0].notification_data.action_type+'_notification">'+algo.logs[0].notification_data.action_type+' '+algo.logs[0].notification_data.quantity+' stocks at INR '+algo.logs[0].notification_data.trigger_price+'</p></div><div class="view_order_log" style="display: none;"><button>View Order log</button></div></div>');
                        }
                    else
                        {
                            title.append('<div class="recent_notif"><div class="notif_message"><p>'+algo.logs[0].log_message+'</p></div><div class="view_order_log" style="display: none;"><button>View Order log</button></div></div>');
                        }

                    title.append('<div><p class="pnl" id="live__'+algo.deployment_uuid+'"><span class="sub_title">P&amp;L:&nbsp;&nbsp;</span><span style="color: #bfc7d1;font-weight: 400;">&nbsp;</span><span style="color: #bfc7d1;font-weight: 400;">NA&nbsp;</span><span style="color: #bfc7d1;font-weight: 400;">(NA%)&nbsp;</span></p></div>');

                    force_stop_div = $('<div></div>');
                    // $('.exit_position, .algo_stopped').hide();$('.force_stop_popup, .stop_options').show();$('body').addClass('body_scroll');
                    if (parseInt(status)==0)
                        force_stop_div.append('<button class="force_stop" onclick="force_stop(event,\''+algo.deployment_uuid+'\')"><img src="/static/imgs/icon-force-stop.png">&nbsp;&nbsp;Stop</button>');
                    //force_stop_div.append('<button class="bt_graph" onclick="show_backtest(event,\''+algo.deployment_uuid+'\',\''+algo.segment_symbol+'\')"><img src="/static/imgs/icon-bt-graph-brown.png"></button>');
                    force_stop_div.append('<div class="results_section" style="display: none;"></div>');
                    force_stop_div.append('<button class="icon-order-log"><img src="/static/imgs/icon-view-order-details.png"></button>');

                    title.append(force_stop_div);

                    orders_details_title.html(title);
                    orders_details_title_outer.append(orders_details_title);

                    orders_details_body = $('<div class="orders_details_body" style="display:none;"></div>');
                    progress_section = $('<div class="progress_section"></div>');
                    prompter = $('<div class="prompter"></div>');
                    
                    // log loop
                    blank_row = '<div class="status_row"><div class="status_tag"><p></p></div><div></div><div class="status_detail"><p></p><p></p></div></div>';
                    prompter.append(blank_row);
                    for(var j=0;j<algo.logs.length;j++)
                        {
                            if(!['Waiting','Stopped','Completed'].includes(algo.logs[j].log_tag) && (algo.logs[j].notification_data!=null || algo.logs[j].notification_data!={}))
                                { // this requires notification_data to be present
                                    if(algo.logs[j].notification_data.trigger_price=="0")
                                        algo.logs[j].notification_data.trigger_price = 'MARKET';
                                    // if(algo.logs[j].notification_data.action_type=="SELL" && (algo.logs[j].notification_data.action_type=='Bought'||algo.logs[j].notification_data.action_type=='Sold') && algo.logs[j].notification_data.type!="take-profit")
                                    //     algo.logs[j].log_tag = 'sold';
                                    // else if(algo.logs[j].notification_data.action_type=="Buy" && (algo.logs[j].notification_data.action_type=='Bought'||algo.logs[j].notification_data.action_type=='Sold') && algo.logs[j].notification_data.type!="take-profit")
                                    //     algo.logs[j].log_tag = 'bought';
                                    console.log(algo.logs[j].notification_data.action_type);
                                    status_row = '<div class="status_row"><div class="status_tag"><p><span>'+algo.logs[j].log_tag+'</span></p></div><div><span></span></div><div class="status_detail"><p>'+algo.logs[j].log_message+'&nbsp;<span>'+algo.logs[j].notification_data.action_type+' '+algo.logs[j].notification_data.quantity+' stocks at INR '+algo.logs[j].notification_data.trigger_price+'</span></p><p>'+moment(algo.logs[j].notification_data.notification_time).format('h:mm:ss A on MM/DD/YYYY ')+'</p></div></div>';
                                }
                            else
                               { 
                                status_row ='<div class="status_row"><div class="status_tag"><p><span>'+algo.logs[j].log_tag+'</span></p></div><div><span></span></div><div class="status_detail"><p>'+algo.logs[j].log_message+'&nbsp;</p><p>'+moment(algo.logs[j].created_at).format('h:mm:ss A on MM/DD/YYYY ')+'</p></div></div>';
                                }
                            prompter.append(status_row);
                        }

                    progress_section.append(prompter);
                    progress_line = $('<div class="progress_line"></div>');
                    progress_section.append(progress_line);
                    orders_details_body.append(progress_section);
                    orders_details.append(orders_details_title_outer)
                    orders_details.append(orders_details_body)
                    orders_right.append(orders_details);
                }catch(e){
                    console.log(e);
                }
            }

            if(msg.pages>pagination+1){
                $('.show_more_eq').show();
            }
            else{
                $('.show_more_eq').hide();                
            }
        }
        catch(e){
            console.log(e);
        }
        $(".recent_notif, .icon-order-log").click(function(){
            $(this).parents(".orders_details").find(".orders_details_body").slideToggle();
        // $(".orders_details_body").hide();
        });
    }).fail(function(msg){
        switch(parseInt(status)) {
            case 0:no_orders_html = '<div class="empty_orders_right" style="display: none;"> <img src="/static/imgs/empty-orders.png"> <p>No algorithm live yet.<br>Go to <a href="/dashboard">backtest results</a> to deploy a algorithm.</p> </div> '; break;
            case -1:no_orders_html = '<div class="empty_orders_right" style="display: none;"> <img src="/static/imgs/empty-orders.png"> <p>No algorithm stopepd yet.<br>Go to <a href="/dashboard">backtest results</a> to deploy a algorithm.</p> </div> '; break;
            case 1:no_orders_html = '<div class="empty_orders_right" style="display: none;"> <img src="/static/imgs/empty-orders.png"> <p>No algorithm archived yet.<br>Go to <a href="/dashboard">backtest results</a> to deploy a algorithm.</p> </div> '; break;
        }
        $('.orders_right').html(no_orders_html);
        $('.empty_orders_right').show();
    });
    setTimeout(function(){
        refresh_ltp_subscription();
    },1000);
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

function show_backtest(event,deployment_uuid,segment_symbol){
    var params = {
        'deployment_uuid':deployment_uuid,
        'segment_symbol':segment_symbol
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/fetch_single_backtest/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 10000,//40 sec timeout
    }

    $(event.target).unbind('click');
    $(event.target).prop('onclick',null).off('click');
    $.ajax(settings).done(function (msg){
        // console.log(msg);
        if (msg.status=="success"){
            bt_result = JSON.parse(msg.backtest_result);
            results_section = $(event.target.nextElementSibling);
            chart_section = $('<div class="chart_section"></div>');        
            chart_header = $('<div class="chart_header"></div>');

            [seg,sym] = bt_result.backtest_result.symbol.split('_');
            equity_section = '<div class="equity_section"><!--<p class="company_name">'+msg.company_name+'</p>--><p class="exc_symbol">'+seg+': '+sym+'</p></div>';      
            chart_header.append(equity_section);

            chart_body = $('<div class="chart_body"></div>');
            canvas = $('<canvas id="pnl_chartContainer_new">')

            var ctx = canvas;

            chart_body.append(ctx);
            
            chart_section.append(chart_header);
            chart_section.append(chart_body);

            pnl_section = $('<div class="pnl_section"></div>');

            chart_pnl = '<div class="chart_pnl"><p>P&amp;L&nbsp;<span><img src="/static/imgs/icon-arrow-up-green.png">&nbsp;</span><span>'+bt_result.backtest_result.final_pnl+'&nbsp;</span><span>('+bt_result.backtest_result.return+'%)&nbsp;</span></p></div>';

            win_count = bt_result.backtest_result.win_count;
            loss_count = bt_result.backtest_result.loss_count;

            streak_chart = '<div class="streak_chart"><div class="streak_chart_body"><div class="wins" style="width:'+(win_count/(win_count+loss_count)*100)+'% !important"></div><div class="losses" style="width:'+(loss_count/(win_count+loss_count)*100)+'% !important"></div></div></div>';

            results_table = $('<div class="results_table"></div>');
            results_table_t = $('<table></table');
            results_table_body = $('<tbody></tbody>');
            results_table_body.append('<tr><td>Volatility</td><td>'+parseFloat(bt_result.backtest_result.volatility).toFixed(2)+'%</td></tr>')
            results_table_body.append('<tr><td>Sharpe</td><td>'+parseFloat(bt_result.backtest_result.sharpe).toFixed(2)+'</td></tr>')
            results_table_body.append('<tr><td>Downside Risk</td><td>'+parseFloat(bt_result.backtest_result.downside_risk).toFixed(2)+'%</td></tr>');
            results_table_t.append(results_table_body);
            results_table.append(results_table_t);

            pnl_section.append(chart_pnl);
            pnl_section.append(streak_chart);
            pnl_section.append(results_table);

            results_section.html('')
            results_section.append(chart_section);
            results_section.append(pnl_section);
            results_section.show();
            // results_section.css("display", "block");

            var pnl_chartContainer_new = new Chart(ctx,{
                    type: 'line',
                    scaleSteps : 4,
                    data: {
                        // labels: ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
                        datasets: [{
                            label: 'P&L',
                            data: processListToXYList(bt_result.backtest_result.pnl),
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
        else{

        }

    }).then(function(){
        $(".results_section").mouseleave(function(){
                $(".results_section").hide();
            });
        $(event.target).bind('click');
        $(event.target).on('click',function(event){
            show_backtest(event,deployment_uuid,segment_symbol);       
        });
    });
}