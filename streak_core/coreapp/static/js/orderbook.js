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
    $("#take_tour, #take_tour_mobile").click(function(){
        // hopscotch.startTour(orders_tour());
    });
    // $(".recent_notif, .icon-order-log").click(function(){
    //     $(this).parents(".orders_details").find(".orders_details_body").slideToggle();
    //     // $(".orders_details_body").hide();
    // });
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
        load_order_book(status,g_limit,pagination);
    });
    status = 0;
    if($.urlParam('platform')=='all')
        status = 0;
    if($.urlParam('variety')=='BO'){
        show_snackbar(null,'Exit BO from orderbook','success');
    }

    load_order_book(status,g_limit,0);
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
      "timeout": 10000,//40 sec timeout
    }
    $(event.target).attr('style','background-color:rgba(255, 67, 67, 0.8);border-color:rgba(255, 67, 67, 0.8);');
    $(event.target).html("<img style='width:100%;height:auto;' src='/static/imgs/button-loading-rect.gif' id='button_loading'>");
    $(event.target).css({'cursor': 'no-drop'});
    $(event.target).removeAttr('onclick');

    $.ajax(settings).done(function (msg){
        if(msg.status=='success')
        {
            var positions = msg.positions;
            if(positions.qty == undefined || positions.qty==0){
                keep_position_open(deployment_uuid);
            }else{
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

                $(event.target).removeAttr('style');
                $('#exit_positions_now').attr('onclick',"exit_position_now('"+deployment_uuid+"');");
                $(event.target).html("<img src=\"/static/imgs/icon-force-stop.png\">&nbsp;&nbsp;Stop");
                $(event.target).css({'cursor': 'pointer'});
                $(event.target).attr('onclick','force_stop(event,\''+deployment_uuid+'\')');
            }
        }
    }).fail(function(msg){
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

        $(event.target).removeAttr('style');
        $('#exit_positions_now').attr('onclick',"exit_position_now('"+deployment_uuid+"');");
        $(event.target).html("<img src=\"/static/imgs/icon-force-stop.png\">&nbsp;&nbsp;Stop");
        $(event.target).css({'cursor': 'pointer'});
        $(event.target).attr('onclick','force_stop(event,\''+deployment_uuid+'\')');
    }).complete(function(msg){
        // $(event.target).html("<img src=\"/static/imgs/icon-force-stop.png\">&nbsp;&nbsp;Stop");
        // $(event.target).css({'cursor': 'pointer'});
        // $(event.target).attr('onclick','force_stop(event,\''+deployment_uuid+'\')');
    });
    // force_stop_button(deployment_uuid);
    // $('#keep_positions_open').html('Keep positions open');
    // $('#keep_positions_open').removeAttr('onclick');
    // $('#exit_positions_now').removeAttr('style');
    // $('#keep_positions_open').attr('onclick',
    //     "keep_position_open('"+deployment_uuid+"');"       
    // );

    // $('#exit_positions_now').html('Exit positions now');
    // $('#exit_positions_now').removeAttr('onclick');
    // $('#exit_positions_now').removeAttr('style');
    // $('#exit_positions_now').attr('onclick',"exit_position_now('"+deployment_uuid+"');");
}
function force_stop2(event,deployment_uuid){
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
      "timeout": 10000,//40 sec timeout
    }
    $.ajax(settings).done(function (msg){
        if(msg.status=='success')
            {
                show_snackbar(null,'Algo has been stopped successfully','success');
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
      "timeout": 10000,//40 sec timeout
    }

    $.ajax(settings).done(function (msg){
        if(msg.status=='success')
            {
                positions = msg.positions;
                product = msg.product;
                exit_window = $('.exit_window');
                exit_window.find('.exit_header').removeClass('exit_header_buy');
                exit_window.find('.exit_header').removeClass('exit_header_sell');
                if (positions == {})
                    {
                        exit_window.find('.exit_header').html("<p>No positions to exit</p>");
                        exit_window.find('.exit_body').html('<div  id="notif_actions"><button id="buy" onclick="keep_position_open(\''+deployment_uuid+'\');">Confirm</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div>');
                    }
                else{
                        // seg_sym = [];
                        // for(var k in positions) seg_sym.push(k)
                        if(positions.qty==0){
                            exit_window.find('.exit_header').html("<p>No positions to exit</p>");
                            exit_window.find('.exit_body').html('<div  id="notif_actions"><button id="buy" onclick="keep_position_open(\''+deployment_uuid+'\');">Confirm</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div>');
                        }
                        else if(positions.qty>=0){
                            exit_window.find('.exit_header').addClass('exit_header_sell');
                            [seg,sym] = [msg['seg'],msg['sym']];
                            exit_window.find('.exit_header').html("<p>Sell "+sym+"&nbsp;x"+positions.qty+'<br><span>At market on '+seg+'</span></p>');

                            x = '<div><div class="radio_options"><div><span class="radio_outer"><span class="radio_inner"></span></span><p>MIS</p></div><div><span id="sell_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">CNC</p></div></div>';

                            if(product=='MIS'){
                                if(seg=='NFO-FUT'){
                                    x = '<div><div class="radio_options"><div><span id="sell_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MIS</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>NRML</p></div></div>';
                                }
                                else{
                                    x = '<div><div class="radio_options"><div><span id="sell_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MIS</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>CNC</p></div></div>';
                                }
                            }
                            else if(product=='NRML'){
                                x = '<div><div class="radio_options"><div><span class="radio_outer"><span class="radio_inner"></span></span><p>MIS</p></div><div><span id="sell_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">NRML</p></div></div>'
                            }

                            exit_window.find('.exit_body').html('<div class="exit_options">'+x+'<div class="exit_qty"><p>Quantity</p><input type="number" id="position_qty" name="" value="'+Math.abs(positions.qty)+'"></div></div><div><div class="radio_options"><div><span id="sell_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MARKET</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div></div><div class="exit_price"><p>Price</p><input type="number" id="position_price" name="" value="0"></div></div></div><div  id="notif_actions"><button id="sell" onclick="exit_position_now_force_stop(\''+deployment_uuid+'\',\''+seg+'\',\''+sym+'\','+positions.qty+',\'MARKET\',\'SELL\',\''+product+'\',\'DAY\',\''+msg.algo_uuid+'\',\''+msg.algo_name+'\');">Sell</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div>');
                        }
                        else if(positions.qty<0){
                            exit_window.find('.exit_header').addClass('exit_header_buy');
                            [seg,sym] = [msg['seg'],msg['sym']];
                            exit_window.find('.exit_header').html("<p>Buy "+sym+"&nbsp;x"+Math.abs(positions.qty)+'<br><span>At market on '+seg+'</span></p>');

                            x = '<div><div class="radio_options"><div><span class="radio_outer"><span class="radio_inner"></span></span><p>MIS</p></div><div><span id="buy_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">CNC</p></div></div>';
                            
                            if(product=='MIS'){
                                if(seg=='NFO-FUT'){
                                    x = '<div><div class="radio_options"><div><span id="buy_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MIS</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>NRML</p></div></div>';
                                }
                                else{
                                    x = '<div><div class="radio_options"><div><span id="buy_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MIS</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>CNC</p></div></div>';
                                }
                            }
                            else if(product=='NRML'){
                                x = '<div><div class="radio_options"><div><span class="radio_outer"><span class="radio_inner"></span></span><p>MIS</p></div><div><span id="buy_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">NRML</p></div></div>'
                            }

                            exit_window.find('.exit_body').html('<div class="exit_options">'+x+'<div class="exit_qty"><p>Quantity</p><input type="number" id="position_qty" name="" value="'+Math.abs(positions.qty)+'"></div></div><div><div class="radio_options"><div><span id="buy_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MARKET</p></div><div><span class="radio_outer"><span class="radio_inner"><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div></div><div class="exit_price"><p>Price</p><input type="number" id="position_price" name="" value="0"></div></div></div><div  id="notif_actions"><button id="buy" onclick="exit_position_now_force_stop(\''+deployment_uuid+'\',\''+seg+'\',\''+sym+'\','+Math.abs(positions.qty)+',\'MARKET\',\'BUY\',\''+product+'\',\'DAY\',\''+msg.algo_uuid+'\',\''+msg.algo_name+'\');">BUY</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div>');
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
    //   "timeout": 10000,//40 sec timeout
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
      "timeout": 10000,//40 sec timeout
    }

    $.ajax(settings).done(function (msg){
        if(msg.status=='success')
            {   
                show_snackbar(null,'Algo has been stopped successfully','success');
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
    load_order_book(g_status,g_limit,pagination,false); 
    refresh_ltp_subscription();
    refresh_pnl_subscription();  
}
function format_algo_summary(algo_obj){

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
            algo_summary = '<div class="algo_summary"><p class="entry_heading">Entry</p> <p class="dashboard_condition_summary"> '+entry_str+'</p> <p class="exit_heading">Exit</p> <p class="dashboard_condition_summary"> '+exit_str+'</p> <p class="interval_heading">Candle interval</p> <p class="dashboard_condition_summary" style="padding-bottom: 0px;">'+c_interval_str+'</p></div>';
        }
    }
    catch(e){
        // console.log(e);
    }
    return algo_summary;
}
function load_order_book(status,limit,page,clear=true){
	var platform = ''
	if(status=="0")
		platform = 'all';
	if(status=="1")
		platform = 'streak';
    var params = {
        'platform':platform,
        'limit':limit,
        'page':page
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/fetch_order_book/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 10000,//40 sec timeout
    }
    $('.empty_orders_right').hide();
    switch(parseInt(status)) {
        case 0:$(".status_select select").attr("style","color : #3c4858 !important"); break;
        case 1:$(".status_select select").attr("style","color : #3c4858 !important"); break;
        case -1:$(".status_select select").attr("style","color : #3c4858 !important"); break;
    }
    $.ajax(settings).done(function (msg){
        // console.log(msg);
        orders_right = $('.orders_right');
        if(clear)
            orders_right.html('');

        log = msg.orders
        if(log == null){
            return;
            }
        // algo loop
        try{
            if (log.length<1){
                switch(parseInt(status)) {
                    case 0:no_orders_html = '<div class="empty_orders_right" style="display: none;"> <img src="/static/imgs/empty-orders.png"> <p><a href="/dashboard">No algos</a></p> </div> '; break;
                    case -1:no_orders_html = '<div class="empty_orders_right" style="display: none;"> <img src="/static/imgs/empty-orders.png"> <p><a href="/dashboard">No algos</a></p> </div> '; break;
                    case 1:no_orders_html = '<div class="empty_orders_right" style="display: none;"> <img src="/static/imgs/empty-orders.png"> <p><a href="/dashboard">No algos</a></p> </div> '; break;
                }
                $('.orders_right').html(no_orders_html);
                $('.empty_orders_right').show();
            }
            else
            for (var i = log.length-1; i>=0; i--){
                try{
                    algo = log[i];
                    orders_details = $('<div class="orders_details"></div>');
                    orders_details_title_outer = $('<div class="orders_details_title_outer"></div>');
                    orders_details_title = $('<div class="orders_details_title"></div>');
                    segment_symbol = algo.exchange+'_'+algo.tradingsymbol;
                    title = $('<div class='+segment_symbol+'></div>');
                    // switch(parseInt(status)) {
                    //     case 0:title.append('<div><p class="algo_status_live">'+'Live'+'</p></div>'); break;
                    //     case -1:title.append('<div><p class="algo_status_stopped">'+'Stopped'+'</p></div>'); break;
                    //     case 1:title.append('<div><p class="algo_status_completed">'+'Completed'+'</p></div>'); break;
                    // }
                    
                    title.append('<div><p class="eq_name">'+moment(algo.order_timestamp).format('h:mm:ss A')+'</p><p class="ltp" id="instrument_token"></p></div>');
                    title.append('<div><p class="eq_name">'+algo.transaction_type+'</p><p class="ltp" id="instrument_token"></p></div>');
                    // if(!['Waiting','Stopped','Completed','Force stopped'].includes(algo.logs[0].log_tag) && algo.logs[0].notification_data!=null)
                    //     {
                    //     if(algo.logs[0].notification_data.trigger_price=="0")
                    //         algo.logs[0].notification_data.trigger_price = 'MARKET';
                    //     else
                    //         top_trigger_price = '&#8377; '+ algo.logs[0].notification_data.trigger_price
                    //     // if(algo.logs[0].notification_data.action_type=="SELL" && algo.logs[0].notification_data.type!="take-profit" && algo.logs[0].notification_data.type!="inrange" && algo.logs[0].notification_data.type!="stop-loss")
                    //     //     algo.logs[0].log_tag = 'sold'
                    //     // else if(algo.logs[0].notification_data.action_type=="BUY" && algo.logs[0].notification_data.type!="take-profit" && algo.logs[0].notification_data.type!="inrange" && algo.logs[0].notification_data.type!="stop-loss")
                    //     //     algo.logs[0].log_tag = 'bought'

                    //     // title.append('<div class="recent_notif"><div class="notif_message"><p>'+algo.logs[0].log_message+'</p><p class="'+algo.logs[0].notification_data.action_type+'_notification">'+algo.logs[0].notification_data.action_type+' '+algo.logs[0].notification_data.quantity+' stocks at INR '+algo.logs[0].notification_data.trigger_price+'</p></div><div class="view_order_log" style="display: none;"><button>View Order log</button></div></div>');
                    //     title.append('<div class="status_row"><div class="status_tag"><p><!--<span class="'+title_tag_class+'" >'+algo.logs[0].log_tag+'</span>--></p></div><div><span></span></div><div class="status_detail"><p>'+algo.logs[0].log_message+'&nbsp;<span class="'+title_desc_class+'">'+algo.logs[0].notification_data.action_type+' '+algo.logs[0].notification_data.quantity+' shares of '+algo.logs[0].notification_data.symbol+' at '+top_trigger_price+'</span></p><p>'+moment(algo.logs[0].notification_data.notification_time).format('h:mm:ss A on DD/MM/YYYY')+'</p></div></div>');
                    //     }
                    // else
                    //     {
                        title.append('<div class="status_row"><div class="status_detail" id="status_detail_title"><p><span>'+algo.tradingsymbol+'</span></p><p>'+algo.exchange+'</p></div></div>');
                        // }

                    title.append('<div class="target_prices"><p class="target_prices_first">&nbsp;<span class="taken_position_qty">'+algo.filled_quantity+'/'+algo.quantity+'</span></p></div>');
                    // console.log('AAAAAAAAAAAAAAAAAAAAAAAAAAA')
                    // console.log(algo.logs[0])
                    title.append('<div class="new_pnl_div"><p class="pnl"><span class="sub_title"></span><span style="color: #8b9096;font-weight: 400;">'+algo.average_price+'&nbsp;</span></p><p class="target_prices_second"></p></div>');
                    title.append('<div class="status_row"><div class="status_detail" id="status_detail_title"><p><span>'+algo.product+'</span></p></div></div>');
                    title.append('<div class="status_row"><div class="status_detail" id="status_detail_title"><p><span>'+algo.status+'</span></p></div></div>');

                    force_stop_div = $('<div></div>');
                    // $('.exit_position, .algo_stopped').hide();$('.force_stop_popup, .stop_options').show();$('body').addClass('body_scroll');
                    //force_stop_div.append('<button class="bt_graph" onclick="show_backtest(event,\''+algo.deployment_uuid+'\',\''+algo.segment_symbol+'\')"><img src="/static/imgs/icon-bt-graph-brown.png"></button>');
                    force_stop_div.append('<div class="results_section" style="display: none;"></div>');
                    var algo_str = JSON.stringify(algo); 
                    force_stop_div.append('<button class="icon-order-log" data-tooltip-top="View order log" onclick=\'show_order_details('+algo_str+')\'><img src="/static/imgs/icon-view-order-details.png"></button>');

                    title.append(force_stop_div);

                    orders_details_title.html(title);
                    orders_details_title_outer.append(orders_details_title);

                    orders_details_body = $('<div class="orders_details_body" style="display:none;"></div>');
                    progress_section = $('<div class="progress_section"></div>');
                    prompter = $('<div class="prompter"></div>');
                    
                    // log loop
                    blank_row = '<div class="status_row"><div class="status_tag"><p></p></div><div></div><div class="status_detail"><p></p><p></p></div></div>';
                    prompter.append(blank_row);
                    
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
        // $(".recent_notif, .icon-order-log").click(function(){
        //     $(this).parents(".orders_details").find(".orders_details_body").slideToggle();
        // // $(".orders_details_body").hide();
        // });
        
        $('.view_algo_details').click(function(event){
            $(event.target).closest('div').find('.algo_detail_window').show();
          });
        $('.algo_detail_window').mouseleave(function(event){
            $('.algo_detail_window').hide();
        });
        if (first_time_orders == "true"){
            hopscotch.startTour(orders_tour());
        }
    }).fail(function(msg){
        switch(parseInt(status)) {
            case 0:no_orders_html = '<div class="empty_orders_right" style="display: none;"> <img src="/static/imgs/empty-orders.png"> <p><a href="/dashboard">No Orders</a></p> </div> '; break;
            case -1:no_orders_html = '<div class="empty_orders_right" style="display: none;"> <img src="/static/imgs/empty-orders.png"> <p><a href="/dashboard">No Orders</a></p> </div> '; break;
            case 1:no_orders_html = '<div class="empty_orders_right" style="display: none;"> <img src="/static/imgs/empty-orders.png"> <p><a href="/dashboard">No Orders</a></p> </div> '; break;
        }
        $('.orders_right').html(no_orders_html);
        $('.empty_orders_right').show();
    });
    setTimeout(function(){
        refresh_ltp_subscription();
        refresh_pnl_subscription();
    },1000);
}

function show_order_details(order){
    // order = JSON.parse(order);
    order_status = order;
    if(order_status.status=='COMPLETE'){
        green_style = 'style="color: #06c579 !important"'
    }
    else{
        green_style = ''
    }
    if(order_status.exchange_order_id==null)
    	order_status.exchange_order_id = '—';
    if(order_status.exchange_timestamp==null)
    	order_status.exchange_timestamp = '—';
    
    $('.order_details_popup').show();$('body').addClass('body_scroll');
    order_details_header = '<div class="order_name"> <p>'+order_status.tradingsymbol+'<span>'+order_status.exchange+'</span></p> <p>'+order_status.transaction_type+' '+order_status.quantity+' shares at '+order_status.order_type+'</p> </div> <div class="order_avg_price"> <p>Avg. Price</p> <p>'+order_status.average_price+'</p> </div> <div class="order_filled_qty"> <p>Filled Quantity</p> <p>'+order_status.filled_quantity+' of '+order_status.quantity+'</p> </div>';
    $('.order_details_header').html(order_details_header);

    order_details_body = '<div class="order_details_row"> <div> <p>Price</p> <p>'+order_status.price+'</p> </div> <div> <p>Trigger Price</p> <p>'+order_status.trigger_price+'</p> </div> <div> <p>Order placed by</p> <p>'+order_status.placed_by+'</p> </div> </div> <div class="order_details_row"> <div> <p>Order Type</p> <p>'+order_status.order_type+'</p> </div> <div> <p>Product Validity</p> <p>'+order_status.product+'/'+order_status.validity+'</p> </div> <div> <p>Time</p> <p>'+order_status.order_timestamp+'</p> </div> </div> <div class="order_details_row"> <div> <p>Order ID</p> <p>'+order_status.order_id+'</p> </div> <div> <p>Exchange order ID</p> <p>'+order_status.exchange_order_id+'</p> </div> <div> <p>Exchange Time</p> <p>'+order_status.exchange_timestamp+'</p> </div> </div> <div class="order_details_row"> <div class="status"> <p>Status</p> <p '+green_style+'>'+order_status.status+'</p> </div> <div id="status_message"> <p>STATUS MESSAGE</p> <p >'+order_status.status_message+'</p> </div> </div>'
    $('.order_details_body').html(order_details_body);
}

function take_action(notification_data) {
    console.log(notification_data);
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