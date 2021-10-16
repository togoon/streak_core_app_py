$(window).load(function() {
    // Animate loader off screen
    $(".loader_parent").fadeOut();
  });
var pagination = 0;
var g_limit = 100;
var g_status = 0;
var order_log_live_obj = {}
var order_log_live_list = {}
var order_log_stopped_obj = {}
var order_log_stopped_list = {}
var action_buttons=false;
var current = 'waiting';
var first_loading = true;
var waiting_count = 0;
var entered_count = 0;
var stopped_count = 0;
var page_loading = true;
var take_action_order_window_params={};

$(document).ready(function() {
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
    var popElement = document.getElementsByClassName("menu_dots");
    document.addEventListener('click', function(event) {
        if (action_buttons){
            $(".action_buttons").slideUp();
            setTimeout(function(){ 
                $(".menu_dots>p>img").fadeOut();
            }, 400);
            action_buttons = false;
        }
    });
    $(".menu_dots>p>img").click(function(e){
        // alert($(this).parents(".menu_dots").find(".action_buttons").className);
        $(".action_buttons").slideUp();
        $(this).parents(".menu_dots").find('.action_buttons').slideDown();
        action_buttons = true;
        e.stopPropagation();
    });
    $(".algo_details").click(function(){
        $(".algo_details_popup").show();
        $("body").addClass("body_scroll");
    });
    $(".algo_details_popup").click(function(e){
    // alert($(".order_log_popup").has(e.target).length);
    // alert($(".order_log_popup").is(e.target));
    if(($(".algo_details_popup").has(e.target).length == 0)&&($(".algo_details_popup").is(e.target))){
      $("body").removeClass("body_scroll");
      $(".close_algo_details_popup").parents(".body").find(".algo_details_popup").fadeOut();
    }
    });
    $("#take_tour, #take_tour_mobile").click(function(){
        hopscotch.startTour(orders_tour());
    });
    $(".orders_details_title_outer").hover(function(){
        $(this).find(".menu_dots img").show();
    });
    $(".orders_details_title_outer").mouseleave(function(){
        $(this).find(".menu_dots img").hide();
    });
    $(".recent_notif, .icon-order-log").click(function(){
        // $(this).parents(".orders_details").find(".orders_details_body").slideToggle();
        // $(".orders_details_body").hide();
        $("body").addClass("body_scroll");
        $(".order_log_popup").show();
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
        $(".loader_parent").fadeIn();
        // load_order_log(status,g_limit,pagination);
        load_order_log_dict(status,g_limit,pagination);
    });
    $('.loading-dots-container').show();
    // load_order_log(0,g_limit,0);
    load_order_log_dict(0,g_limit,0);

    $('#ip_variety').autocomplete({
      source: function(request,response){
        results = ['REGULAR','BO'];
        live_period_mapping = {'Intraday (MIS)':1,'Overnight (CNC/NRML)':30}
        if((live_period_mapping[$('#ip_live_period').val()]!= 1)){
          results = ['REGULAR'];
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

function search_waiting(){
  q = $('#waiting_search_input').val();
  x = $('#waiting_orders .orders_details div[class^="token__"]');
  x.each(function(i){
    if(q.replace(/ /g,'')==''){
       $(x[i]).closest('.orders_details').removeClass('add_opacity');
    }
    else{
      data_str = $(x[i]).data('search-val');
      // all_d = $(x[i]).find('div>div');
      // for(j=0;j<x.length;j++){
      //   if($(x[j]).data('search-val')!=undefined)
      //     data_str =data_str+$(x[j]).data('search-val');
      // }
      if(data_str)
          if(data_str.toLowerCase().search(q)==-1){
            $(x[i]).closest('.orders_details').addClass('add_opacity');
          }
          else{
            $(x[i]).closest('.orders_details').removeClass('add_opacity');
          }
    }
  });
}

function search_entered(){
  q = $('#entered_search_input').val();
  x = $('#entered_orders .orders_details div[class^="token__"]');
  x.each(function(i){
    if(q.replace(/ /g,'')==''){
       $(x[i]).closest('.orders_details').removeClass('add_opacity');
    }
    else{
      data_str = $(x[i]).data('search-val');
      // all_d = $(x[i]).find('div>div');
      // for(j=0;j<x.length;j++){
      //   if($(x[j]).data('search-val')!=undefined)
      //     data_str =data_str+$(x[j]).data('search-val');
      // }
      if(data_str)
          if(data_str.toLowerCase().search(q)==-1){
            $(x[i]).closest('.orders_details').addClass('add_opacity');
          }
          else{
            $(x[i]).closest('.orders_details').removeClass('add_opacity');
          }
    }
  });
}

function search_stopped(){
  q = $('#stopped_search_input').val();
  x = $('#stopped_orders .orders_details div[class^="token__"]');
  x.each(function(i){
    if(q.replace(/ /g,'')==''){
       $(x[i]).closest('.orders_details').removeClass('add_opacity');
    }
    else{
      data_str = $(x[i]).data('search-val');
      // all_d = $(x[i]).find('div>div');
      // for(j=0;j<x.length;j++){
      //   if($(x[j]).data('search-val')!=undefined)
      //     data_str =data_str+$(x[j]).data('search-val');
      // }
      if(data_str)
          if(data_str.toLowerCase().search(q)==-1){
            $(x[i]).closest('.orders_details').addClass('add_opacity');
          }
          else{
            $(x[i]).closest('.orders_details').removeClass('add_opacity');
          }
    }
  });
}

function populate_order_log(dep_id,status="live",take_action_notification_data=null){
    $("body").addClass("body_scroll");
    $(".order_log_popup").show();
    if(status=='live'){
        deployed_obj = order_log_live_obj[dep_id];
        log = order_log_live_obj[dep_id].logs;
    }
    else{
        deployed_obj = order_log_stopped_obj[dep_id];
        log = order_log_stopped_obj[dep_id].logs;
    }

    if(log == null||log == undefined){
        return;
        }
    // algo loop
    try{
       
        progress_section = $('.progress_section_orderlog');
        prompter = $('<div class="prompter_orderlog"></div>');
        
        progress_section.html('');
        // log loop
        blank_row = '<div class="status_row"><div></div><div class="status_tag_orderlog"><p></p></div><div class="status_detail_orderlog"><p></p><p></p></div></div>';
        // prompter.append(blank_row);
        for(var j=0;j<log.length;j++)
            {
                tag_class = log[j].log_tag.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
                desc_class = log[j].log_tag.toLowerCase().split('-').join('_').split(' ').join('_')+'_desc';
                log_image = log[j].log_tag.toLowerCase().split('-').join('_').split(' ').join('_');
                if(['Buy alert','Sell alert','Bought','Sold'].includes(log[j].log_tag)){
                    if(deployed_obj.algo_obj.action_type!=log[j].notification_data.action_type)
                        log_image = 'exit_'+log_image;
                    else
                        log_image = 'entry_'+log_image;
                }
                if(!['Waiting','Stopped','Completed','Force stopped','Algo Expired'].includes(log[j].log_tag) && (log[j].notification_data!=null || log[j].notification_data!={}))
                    { // this requires notification_data to be present
                        if(log[j].notification_data.trigger_price=="0" && log[j].notification_data.order_type!="SL" && log[j].notification_data.order_type!='LIMIT')
                            log[j].notification_data.trigger_price = 'MARKET';
                        else
                            {
                                if(log[j].log_message.indexOf('SL-M')!=-1)
                                    {
                                        log[j].notification_data.trigger_price = 'TRIGGER PRICE   '+ parseFloat(log[j].notification_data.trigger_price).toFixed(2)
                                    }
                                else if(log[j].notification_data.order_type=="LIMIT" || log[j].notification_data.order_type=="SL") 
                                    {
                                      if(log[j].log_tag!="Cancelled")
                                        log[j].notification_data.trigger_price = log[j].notification_data.price;
                                    }
                                else{
                                    log[j].notification_data.trigger_price = '  '+parseFloat(log[j].notification_data.trigger_price).toFixed(2)
                                    }
                            }

                        if(['Rejected'].includes(log[j].log_tag))
                            status_row = '<div class="status_row"><div><span><img src="/static/imgs/new/orderlog/'+log_image+'.svg"></span></div><div class="status_tag_orderlog"><p><span class="'+tag_class+'" >'+log[j].log_tag+'</span></p></div><div class="status_detail_orderlog"><p>'+log[j].log_message+'&nbsp;<span class="'+desc_class+'">'+log[j].notification_data.action_type+' '+log[j].notification_data.quantity+' shares of '+log[j].notification_data.symbol+' at '+log[j].notification_data.trigger_price+'</span><span id="rejected" onclick="show_order_details_notif(\''+log[j].notification_data.order_id+'\')">Rejected</span></p><p>'+moment(log[j].notification_data.notification_time).format('h:mm:ss A on DD/MM/YYYY')+'</p></div></div>';
                        else if(['Bought','Sold'].includes(log[j].log_tag))
                          status_row = '<div class="status_row"><div><span><img src="/static/imgs/new/orderlog/'+log_image+'.svg"></span></div><div class="status_tag_orderlog"><p><span class="'+tag_class+'" >'+log[j].log_tag+'</span></p></div><div class="status_detail_orderlog"><p>'+log[j].log_message+'&nbsp;<span class="'+desc_class+'">'+log[j].notification_data.action_type+' '+log[j].notification_data.quantity+' shares of '+log[j].notification_data.symbol+' at '+log[j].notification_data.average_price+'</span><span id="details" class="details" onclick="show_order_details_notif(\''+log[j].notification_data.order_id+'\')">Completed</span></p><p>'+moment(log[j].notification_data.notification_time).format('h:mm:ss A on DD/MM/YYYY')+'</p></div></div>';
                        else
                          {
                            if(take_action_notification_data!=null && j==0 && !['User action','At Exchange','SL-M Cancelled'].includes(log[j].log_tag))
                            {
                              take_action_notification_data = JSON.stringify(take_action_notification_data);
                              status_row = '<div class="status_row"><div><span><img src="/static/imgs/new/orderlog/'+log_image+'.svg"></span></div><div class="status_tag_orderlog"><p><span class="'+tag_class+'" >'+log[j].log_tag+'</span></p></div><div class="status_detail_orderlog"><p>'+log[j].log_message+'&nbsp;<span class="'+desc_class+'">'+log[j].notification_data.action_type+' '+log[j].notification_data.quantity+' shares of '+log[j].notification_data.symbol+' at '+log[j].notification_data.trigger_price+'</span><span class="details" onclick=\'take_action(event,'+take_action_notification_data+')\'>Take action</span></p><p>'+moment(log[j].notification_data.notification_time).format('h:mm:ss A on DD/MM/YYYY')+'</p></div></div>'; 
                            }
                            else if(take_action_notification_data==null && log[j].log_tag=='Cancelled'){
                              status_row = '<div class="status_row"><div><span><img src="/static/imgs/new/orderlog/'+log_image+'.svg"></span></div><div class="status_tag_orderlog"><p><span class="'+'" >'+log[j].log_tag+'</span></p></div><div class="status_detail_orderlog"><p>'+log[j].log_message+'&nbsp;<span class="'+desc_class+'">'+log[j].notification_data.action_type+' '+log[j].notification_data.quantity+' shares of '+log[j].notification_data.symbol+'</span></p><p>'+moment(log[j].notification_data.notification_time).format('h:mm:ss A on DD/MM/YYYY')+'</p></div></div>';
                            }
                            else
                              {
                                if (log[j].notification_data.order_type=="LIMIT" || log[j].notification_data.order_type=="SL")
                                  {
                                    log[j].notification_data.trigger_price = log[j].notification_data.price;
                                  }  

                                status_row = '<div class="status_row"><div><span><img src="/static/imgs/new/orderlog/'+log_image+'.svg"></span></div><div class="status_tag_orderlog"><p><span class="'+tag_class+'" >'+log[j].log_tag+'</span></p></div><div class="status_detail_orderlog"><p>'+log[j].log_message+'&nbsp;<span class="'+desc_class+'">'+log[j].notification_data.action_type+' '+log[j].notification_data.quantity+' shares of '+log[j].notification_data.symbol+' at '+log[j].notification_data.trigger_price+'</span></p><p>'+moment(log[j].notification_data.notification_time).format('h:mm:ss A on DD/MM/YYYY')+'</p></div></div>';
                              }
                          }
                    }
                else
                   { 
                    status_row ='<div class="status_row"><div><span><img src="/static/imgs/new/orderlog/'+log_image+'.svg"></span></div><div class="status_tag_orderlog"><p><span class="'+tag_class+'">'+log[j].log_tag+'</span></p></div><div class="status_detail_orderlog"><p class="'+desc_class+'">'+log[j].log_message+'&nbsp;</p><p>'+moment(log[j].created_at).format('h:mm:ss A on DD/MM/YYYY')+'</p></div></div>';
                    }
                prompter.append(status_row);
            }

        progress_section.append(prompter);
        progress_line = $('<div class="progress_line"></div>');
        progress_section.append(progress_line);
    }
    catch(e){
        console.log(e);
    }
    $(".recent_notif, .icon-order-log").click(function(){
        $(this).parents(".orders_details").find(".orders_details_body").slideToggle();
    // $(".orders_details_body").hide();
    });

}
// function close_order_log_popup () {
//     $(".close_popup").parents(".body").find(".order_log_popup").fadeOut();
//     $("body").removeClass("body_scroll");
// }
function close_orders_popup() {
    $(".close_popup").parents(".body").find(".force_stop_popup").fadeOut();
    $("body").removeClass("body_scroll");
    $(".stop_options").fadeOut();
    setTimeout(function(){ 
        $('.force_stop_popup').removeClass('take_position_popup');
        }, 1000);
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
            var variety = msg.variety;
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
        refresh_waiting();
        refresh_entered();
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
    $('.stop_sub_heading').show();
    $('.force_stop_popup, .stop_options .stop_heading').show();
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
                show_snackbar(null,'Strategy has been stopped successfully','success');
                console.log(msg.status);
                $('.exit_position, .stop_options').hide();$('.algo_stopped').show();
                //===>>>// setTimeout(function(){ window.location = '/order_log/'; }, 3000); 
                refresh_waiting(); 
                refresh_stopped(); 
            }
        else{
            $('.force_stop_popup').hide();
            show_snackbar(null,'Error occured, please try again');
            }
        }).fail(function(msg){
            $('.force_stop_popup').hide();
            show_snackbar(null,'Error occured, please try again');
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
                if (msg.variety=="BO" && msg.parent_order_id==msg.order_id)
                {
                  show_snackbar(null,'Exit BO from order book');
                  if(window.location.href.indexOf('/orderbook/')!=-1){

                  }
                  else{
                    window.location='/orderbook/?platform=all&variety=BOE';
                    return;
                  }
                }

                exit_window = $('.exit_window');
                exit_window.find('.exit_header').removeClass('exit_header_buy');
                exit_window.find('.exit_header').removeClass('exit_header_sell');
                $('.stop_heading').show();
                $('.stop_sub_heading').show();
                $('.back').show();
                $('.exit_position_section').removeAttr('style');

                if (positions == {})
                    {
                        $('.stop_sub_heading').hide();
                        exit_window.find('.exit_header').html("<p style=\"text-align: center !important;color: #192024;\">No positions to exit</p>");
                        exit_window.find('.exit_body').html('<div  id="notif_actions"><button id="buy" onclick="keep_position_open(\''+deployment_uuid+'\');">Confirm</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div>');
                    }
                else{
                        // seg_sym = [];
                        // for(var k in positions) seg_sym.push(k)
                        if(positions.qty==0){
                            $('.stop_sub_heading').hide();
                            exit_window.find('.exit_header').html("<p style=\"text-align: center !important;color: #192024;\">No positions to exit</p>");
                            exit_window.find('.exit_body').html('<div  id="notif_actions"><button id="buy" onclick="keep_position_open(\''+deployment_uuid+'\');">Confirm</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div>');
                        }
                        else if(positions.qty!=0 && msg.parent_order_id!='' && msg.variety=='BO'){
                            transaction_type = 'Buy';
                            if(positions.qty<0){
                              transaction_type = 'Sell';
                            }
                            // exit_window.find('.exit_header').addClass('exit_header_'+transaction_type.toLowerCase());
                            [seg,sym] = [msg['seg'],msg['sym']];
                            exit_window.find('.exit_header').html("<p class='stop_sub_heading cancel_order_det' style='color: #383838 !important'>Exit BO for "+" "+sym+"&nbsp; and cancel pending orders<br><span>#"+msg.order_id+"</span></p>");
                            exit_window.find('.exit_body').html('<div id="cancel_order_actions"><button id="cancel_order_confirm" onclick="exit_bo_now_force_stop(\''+deployment_uuid+'\',\''+seg+'\',\''+sym+'\','+Math.abs(positions.qty)+',\'MARKET\',\'SELL\',\''+product+'\',\'DAY\',\''+msg.algo_uuid+'\',\''+msg.algo_name+'\',\''+msg.order_id+'\',\''+msg.parent_order_id+'\',\''+msg.variety+'\')">Exit</button><button id="cancel_order_close" onclick="close_orders_popup();">Close</button></div></div>');
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

                            // exit_window.find('.exit_body').html('<div class="exit_options">'+x+'<div class="exit_qty"><p>Quantity</p><input type="number" id="position_qty" name="" value="'+Math.abs(positions.qty)+'"></div></div><div><div class="radio_options"><div><span id="sell_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MARKET</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div></div><div class="exit_price"><p>Price</p><input type="number" id="position_price" name="" value="0"></div></div></div><div  id="notif_actions"><button id="sell" onclick="exit_position_now_force_stop(\''+deployment_uuid+'\',\''+seg+'\',\''+sym+'\','+Math.abs(positions.qty)+',\'MARKET\',\'SELL\',\''+product+'\',\'DAY\',\''+msg.algo_uuid+'\',\''+msg.algo_name+'\');">Sell</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div>');
                            
                            exit_window.find('.exit_body').html('<div class="exit_options">'+x+'<div class="notif_left"><div class="exit_qty"><p>Qty.</p><input type="number" id="position_qty" name="" value="'+Math.abs(positions.qty)+'" readonly></div><div class="exit_qty"><p>Price</p><input type="number" name="" id="position_price" value="'+0+'" readonly></div></div></div><div><div class="radio_options"><div><span id="sell_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MARKET</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL-M</p></div></div><div class="notif_right"><div class="exit_price"><p>Trigger price</p><input type="number" class="bg-stripe" id="position_trigger_price" name="" value="0" readonly></div><div class="exit_price"><p>Disclosed qty.</p><input type="number" class="bg-stripe" id="position_disclosed_qty" name="" value="0" readonly></div></div></div></div><div id="notif_actions"><button id="sell" onclick="exit_position_now_force_stop(\''+deployment_uuid+'\',\''+seg+'\',\''+sym+'\','+Math.abs(positions.qty)+',\'MARKET\',\'SELL\',\''+product+'\',\'DAY\',\''+msg.algo_uuid+'\',\''+msg.algo_name+'\');">Sell</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div>');
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

                            // exit_window.find('.exit_body').html('<div class="exit_options">'+x+'<div class="exit_qty"><p>Quantity</p><input type="number" id="position_qty" name="" value="'+Math.abs(positions.qty)+'"></div></div><div><div class="radio_options"><div><span id="buy_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MARKET</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div></div><div class="exit_price"><p>Price</p><input type="number" id="position_price" name="" value="0"></div></div></div><div  id="notif_actions"><button id="buy" onclick="exit_position_now_force_stop(\''+deployment_uuid+'\',\''+seg+'\',\''+sym+'\','+Math.abs(positions.qty)+',\'MARKET\',\'BUY\',\''+product+'\',\'DAY\',\''+msg.algo_uuid+'\',\''+msg.algo_name+'\');">Buy</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div>');

                            exit_window.find('.exit_body').html('<div class="exit_options">'+x+'<div class="notif_left"><div class="exit_qty"><p>Qty.</p><input type="number" id="position_qty" name="" value="'+Math.abs(positions.qty)+'" readonly></div><div class="exit_qty"><p>Price</p><input type="number" name="" id="position_price" value="'+0+'" readonly></div></div></div><div><div class="radio_options"><div><span id="buy_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MARKET</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL-M</p></div></div><div class="notif_right"><div class="exit_price"><p>Trigger price</p><input type="number" class="bg-stripe" id="position_trigger_price" name="" value="0" readonly></div><div class="exit_price"><p>Disclosed qty.</p><input type="number" class="bg-stripe" id="position_disclosed_qty" name="" value="0" readonly></div></div></div></div><div id="notif_actions"><button id="buy" onclick="exit_position_now_force_stop(\''+deployment_uuid+'\',\''+seg+'\',\''+sym+'\','+Math.abs(positions.qty)+',\'MARKET\',\'BUY\',\''+product+'\',\'DAY\',\''+msg.algo_uuid+'\',\''+msg.algo_name+'\');">Buy</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div>');
                        }
                    }

            }
        else
           { 
            // alert(msg.status);
            $('.force_stop_popup').hide();
            show_snackbar(null,'Error occured, please try again');
           }

    }).fail(function(msg){
        // console.log(msg);
        $('.force_stop_popup').hide();
        show_snackbar(null,'Error occured, please try again');
    }).complete(function(){
        $('#exit_positions_now').html('Exit positions now');
        $('#exit_positions_now').removeAttr('onclick');
        $('#exit_positions_now').removeAttr('style');
        $('#exit_positions_now').attr('onclick',"exit_position_now('"+deployment_uuid+"');");
    });
}
function exit_bo_now_force_stop(deployment_uuid,seg,sym,quantity,order_type,transaction_type,product,validity,algo_uuid,algo_name,order_id,parent_order_id,variety){

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
        'order_id':order_id,
        'parent_order_id':parent_order_id,
        'variety':variety,
        'csrfmiddlewaretoken':csrfmiddlewaretoken
    }

    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/exit_bo_now_force_stop/',
      "method": "POST",
      "headers": {
      },
      "data":params,
      "timeout": 10000,//40 sec timeout
    }
    $.ajax(settings).done(function (msg){
        if(msg.status=='success')
            {
                show_snackbar(null,'Strategy has been stopped successfully','success');
                console.log(msg.status);
                $('.exit_position, .stop_options').hide();$('.algo_stopped').show();
                //===>>>// setTimeout(function(){ window.location = '/order_log/'; }, 3000); 
                refresh_waiting(); 
                refresh_stopped(); 
            }
        else{
            $('.force_stop_popup').hide();
            show_snackbar(null,'Error occured, please try again');
            }
        }).fail(function(msg){
            $('.force_stop_popup').hide();
            show_snackbar(null,'Error occured, please try again');
        });
    // $('.exit_position, .stop_options').hide();$('.algo_stopped').show();
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
                show_snackbar(null,'Strategy has been stopped successfully','success');
                $('.exit_position, .stop_options').hide();$('.algo_stopped').show();
                // $('#close_orders_popup_div').unbind('click');
                // $('#close_orders_popup_div').prop('onclick',null).off('click');
                // $('#close_orders_popup_div').prop('onclick',function(){
                //===>>>// setTimeout(function(){ window.location = '/order_log/'; }, 3000);
                // }).on('click');
                refresh_waiting(); 
                refresh_stopped(); 
            }
        else
           { 
            // alert(msg.status);
            $('.force_stop_popup').hide();
            show_snackbar(null,msg.error_msg);
           }

    }).fail(function(msg){
        // console.log(msg);
        $('.force_stop_popup').hide();
        show_snackbar(null,'Error occured, please try again');
    });
}
// function show_more_click(){
//     pagination += 1;
//     load_order_log(g_status,g_limit,pagination,false); 
//     refresh_ltp_subscription();
//     refresh_pnl_subscription();  
// }
function show_more_click(){
    pagination += 1;
    // load_order_log(g_status,g_limit,pagination,false); 
    load_order_log_dict(0,g_limit,pagination,false);
    load_order_log_dict(-1,g_limit,pagination,false)
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
            algo_summary = '<div class="algo_summary"><p class="entry_heading">Entry</p> <p class="dashboard_condition_summary"> '+entry_str+' at '+c_interval_str+enter_trade_between_time+'</p> <p class="exit_heading">Exit</p> <p class="dashboard_condition_summary"> '+exit_str+' at '+c_interval_str+'</p></div>';
        }
    }
    catch(e){
        // console.log(e);
    }
    return algo_summary;
}

function select_all(e, t) {
    var c = 0;
    if (t.is(':checked')) {
      $('.stop_checkbox').each(function(i,obj){
        if(obj && !obj.disabled)
            {
                obj.checked = true
                c += 1;
            }
        }); 
      } 
    else {
      $('.stop_checkbox').each(function(i,obj){
        if(obj && !obj.disabled)
            {
                obj.checked = false
                // c += 1;
            }
        });
    }
    if(c>0){
      $('.stop_all_appear').slideDown();
      $('.stop_all_appear .stop_all').removeClass('stop_all_disabled'); 
    }else{
      $('.stop_all_appear').slideUp();
      $('.stop_all_appear .stop_all').addClass('stop_all_disabled');
    }
}

function select_any(e, t) {
    // $(t[0].parentElement.parentElement.parentElement).find('.stop_all_checkbox')[0].checked

    // $(t[0].parentElement.parentElement.parentElement).find('.stop_checkbox input');

    var stop_instrument_list = [];
    var c = 0;
    $('.stop_checkbox').each(function(i,obj){
        c += 1;
        if(obj.checked)
        {
            stop_instrument_list.push($(obj.parentElement.parentElement.parentElement).find('div')[0].id);
        }
    });

    if(stop_instrument_list.length>0){
        // $(t[0].parentElement.parentElement.parentElement).find('.deploy').removeClass('deploy_disabled');
        // if($(t[0].parentElement.parentElement.parentElement).find('.stop_all_holder').is(':hidden')){
        $('.stop_all_appear').slideDown();
        $('.stop_all_appear .stop_all').removeClass('stop_all_disabled');
        // }
    }
    else{

        // $(t[0].parentElement.parentElement.parentElement).find('.deploy').addClass('deploy_disabled');
        $('.stop_all_checkbox')[0].checked = false;
        $('.stop_all_appear').slideUp();
        $('.stop_all_appear .stop_all').addClass('stop_all_disabled');
        // $(t[0].parentElement.parentElement.parentElement).find('.stop_all_holder').slideUp();
        // if(!$(t[0].parentElement.parentElement.parentElement).find('.stop_all_holder').is(':hidden')){
        // $(t[0].parentElement.parentElement.parentElement).find('.stop_all_holder').slideUp();
        // }
    }
    if(c>0 && c==stop_instrument_list.length){
        $('.stop_all_checkbox')[0].checked = true;   
    }
    else{
        $('.stop_all_checkbox')[0].checked = false;
    }

}

function show_stop_waiting(){
  var stop_instrument_list = [];
  var c = 0;
  $('.stop_checkbox').each(function(i,obj){
      c += 1;
      if(obj.checked)
      {
          stop_instrument_list.push($(obj.parentElement.parentElement.parentElement).find('div')[0].id);
      }
  });
  if(stop_instrument_list.length>0){
        // $(t[0].parentElement.parentElement.parentElement).find('.deploy').removeClass('deploy_disabled');
        // if($(t[0].parentElement.parentElement.parentElement).find('.stop_all_holder').is(':hidden')){
        $('.stop_all_appear').slideDown();
        $('.stop_all_appear .stop_all').removeClass('stop_all_disabled');
        // }
    }
    else{

        // $(t[0].parentElement.parentElement.parentElement).find('.deploy').addClass('deploy_disabled');
        $('.stop_all_appear').slideUp();
        $('.stop_all_appear .stop_all').addClass('stop_all_disabled');
        // $(t[0].parentElement.parentElement.parentElement).find('.stop_all_holder').slideUp();
        // if(!$(t[0].parentElement.parentElement.parentElement).find('.stop_all_holder').is(':hidden')){
        // $(t[0].parentElement.parentElement.parentElement).find('.stop_all_holder').slideUp();
        // }
    }
}
function show_algo_details(dep_id,status){
    algo_obj = null;
    if(status=='live')
      algo_obj = order_log_live_obj[dep_id].algo_obj;
    else
      algo_obj = order_log_stopped_obj[dep_id].algo_obj;
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
            $('.algo_details_window').html(algo_summary);
            $('.algo_details_popup').fadeIn();$('body').addClass('body_scroll');
        }
    }
    catch(e){
        console.log(e);
    }
    return algo_summary;
}
function load_waiting(){
    // load_order_log_dict(0,50,0,false)
    current = 'waiting';
    g_status = 0;

    orders_right_waiting = $('#waiting_orders');
    orders_right_entered = $('#entered_orders');
    orders_right_stopped = $('#stopped_orders');
    if(current=='waiting'){
        orders_right_waiting.show();
        $('#waiting_bar').attr('style','display:flex!important');
        
        orders_right_entered.hide();
        orders_right_stopped.hide();

        $('#entered_bar').hide();
        $('#stopped_bar').hide();

        $('#waiting_option').addClass('deployed_menu_selected');
        $('#entered_option').removeClass('deployed_menu_selected');
        $('#stopped_option').removeClass('deployed_menu_selected');
        $('.checkbox_title > .stop_all_checkbox').show();
        $('.stop_all_appear .stop_all').addClass('stop_all_disabled');
        $('.stop_all_appear').slideUp();
        show_stop_waiting();

    }else if(current=='entered'){
        orders_right_entered.show();
        $('#entered_bar').attr('style','display:flex!important');

        orders_right_waiting.hide();
        orders_right_stopped.hide();

        $('#waiting_bar').hide();
        $('#stopped_bar').hide();

        $('#entered_option').addClass('deployed_menu_selected');
        $('#waiting_option').removeClass('deployed_menu_selected');
        $('#stopped_option').removeClass('deployed_menu_selected');
        $('.checkbox_title > .stop_all_checkbox').hide();
        $('.stop_all_appear .stop_all').addClass('stop_all_disabled');
        $('.stop_all_appear').slideUp();
    }else if(current=='stopped'){
        $('#stopped_bar').attr('style','display:flex!important');
        orders_right_stopped.show();

        orders_right_entered.hide();
        orders_right_waiting.hide();

        $('#entered_bar').hide();
        $('#waiting_bar').hide();

        $('#stopped_option').addClass('deployed_menu_selected');
        $('#entered_option').removeClass('deployed_menu_selected');
        $('#waiting_option').removeClass('deployed_menu_selected');
        $('.checkbox_title > .stop_all_checkbox').hide();
        $('.stop_all_appear .stop_all').addClass('stop_all_disabled');
        $('.stop_all_appear').slideUp();
    }
}

function load_entered(){
    // load_order_log_dict(0,50,0,false)
    current = 'entered';
    g_status = 0;

    orders_right_waiting = $('#waiting_orders');
    orders_right_entered = $('#entered_orders');
    orders_right_stopped = $('#stopped_orders');
    if(current=='waiting'){
        orders_right_waiting.show();
        $('#waiting_bar').attr('style','display:flex!important');
        
        orders_right_entered.hide();
        orders_right_stopped.hide();

        $('#entered_bar').hide();
        $('#stopped_bar').hide();

        $('#waiting_option').addClass('deployed_menu_selected');
        $('#entered_option').removeClass('deployed_menu_selected');
        $('#stopped_option').removeClass('deployed_menu_selected');
        $('.checkbox_title > .stop_all_checkbox').show();
        $('.stop_all_appear .stop_all').addClass('stop_all_disabled');
        $('.stop_all_appear').slideUp();
        show_stop_waiting();
    }else if(current=='entered'){
        orders_right_entered.show();
        $('#entered_bar').attr('style','display:flex!important');

        orders_right_waiting.hide();
        orders_right_stopped.hide();

        $('#waiting_bar').hide();
        $('#stopped_bar').hide();

        $('#entered_option').addClass('deployed_menu_selected');
        $('#waiting_option').removeClass('deployed_menu_selected');
        $('#stopped_option').removeClass('deployed_menu_selected');
        $('.checkbox_title > .stop_all_checkbox').hide();
        $('.stop_all_appear .stop_all').addClass('stop_all_disabled');
        $('.stop_all_appear').slideUp();
    }else if(current=='stopped'){
        orders_right_stopped.show();
        $('#stopped_bar').attr('style','display:flex!important');

        orders_right_entered.hide();
        orders_right_waiting.hide();

        $('#entered_bar').hide();
        $('#waiting_bar').hide();

        $('#stopped_option').addClass('deployed_menu_selected');
        $('#entered_option').removeClass('deployed_menu_selected');
        $('#waiting_option').removeClass('deployed_menu_selected');
        $('.checkbox_title > .stop_all_checkbox').hide();
        $('.stop_all_appear .stop_all').addClass('stop_all_disabled');
        $('.stop_all_appear').slideUp();
    }
}

function load_stopped(){
    // load_order_log_dict(0,50,0,false)
    current = 'stopped';
    g_status = -1;
    
    orders_right_waiting = $('#waiting_orders');
    orders_right_entered = $('#entered_orders');
    orders_right_stopped = $('#stopped_orders');

    if(current=='waiting'){
        orders_right_waiting.show();
        $('#waiting_bar').attr('style','display:flex!important');
        
        orders_right_entered.hide();
        orders_right_stopped.hide();

        $('#entered_bar').hide();
        $('#stopped_bar').hide();

        $('#waiting_option').addClass('deployed_menu_selected');
        $('#entered_option').removeClass('deployed_menu_selected');
        $('#stopped_option').removeClass('deployed_menu_selected');
        $('.checkbox_title > .stop_all_checkbox').show();
        $('.stop_all_appear .stop_all').addClass('stop_all_disabled');
        $('.stop_all_appear').slideUp();
    }else if(current=='entered'){
        orders_right_entered.show();
        $('#entered_bar').attr('style','display:flex!important');

        orders_right_waiting.hide();
        orders_right_stopped.hide();

        $('#waiting_bar').hide();
        $('#stopped_bar').hide();

        $('#entered_option').addClass('deployed_menu_selected');
        $('#waiting_option').removeClass('deployed_menu_selected');
        $('#stopped_option').removeClass('deployed_menu_selected');
        $('.checkbox_title > .stop_all_checkbox').hide();
        $('.stop_all_appear .stop_all').addClass('stop_all_disabled');
        $('.stop_all_appear').slideUp();
    }else if(current=='stopped'){
        $('#stopped_bar').attr('style','display:flex!important');
        orders_right_stopped.show();

        orders_right_entered.hide();
        orders_right_waiting.hide();

        $('#entered_bar').hide();
        $('#waiting_bar').hide();

        $('#stopped_option').addClass('deployed_menu_selected');
        $('#entered_option').removeClass('deployed_menu_selected');
        $('#waiting_option').removeClass('deployed_menu_selected');
        $('.checkbox_title > .stop_all_checkbox').hide();
        $('.stop_all_appear .stop_all').addClass('stop_all_disabled');
        $('.stop_all_appear').slideUp();
    }
}

function stop_all_waiting(event){
  $('.stop_all_appear .stop_all')[0].classList
  if($('.stop_all_appear .stop_all').attr('class').split(/\s+/).indexOf('stop_all_disabled')>-1){
    return
  }
  $('.loading-dots-container').show();
  $('.stop_all_appear .stop_all').addClass('stop_all_disabled');
  var stop_instrument_list = [];
  $('.stop_checkbox').each(function(i,obj){
        if(obj.checked)
        {
            stop_instrument_list.push($(obj.parentElement.parentElement.parentElement).find('div')[0].id);
        }
    });
  if(stop_instrument_list.length<1){
    show_snackbar(null,'Select an algo to stop');
    return;
  }
  var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
  var list_len = stop_instrument_list.length;
  var params = {
      'deployment_uuids':encodeURI(JSON.stringify(stop_instrument_list)),
      'csrfmiddlewaretoken':csrfmiddlewaretoken
  }

  // $('.exit_position, .stop_options').show();
  var settings = {
    "async": true,
    "crossDomain": true,
    "url": '/stop_waiting_algos/',
    "method": "POST",
    "headers": {
    },
    "data":params,
    "timeout": 10000,//40 sec timeout
  }
  $.ajax(settings).done(function (msg){
        if(msg.status=='success')
            {
              if(list_len){
                if(list_len>1){
                  show_snackbar(null,'Strategies have been stopped successfully','success');
                }
                else{
                  show_snackbar(null,'Strategy has been stopped successfully','success');
                }
              }
              else{
                  show_snackbar(null,'Strategies have been stopped successfully','success');
              }

                // show_snackbar(null,'Algos have been stopped successfully','success');
                console.log(msg.status);
                $('.exit_position, .stop_options').hide();$('.algo_stopped').show();
                //===>>>// setTimeout(function(){ window.location = '/order_log/'; }, 3000); 
                refresh_waiting(); 
                refresh_stopped(); 
            }
        else{
            $('.force_stop_popup').hide();
            show_snackbar(null,'Error occured, please try again');
            }
        $('.stop_all_appear .stop_all').removeClass('stop_all_disabled');
        refresh_waiting();
        $('.stop_all_checkbox')[0].checked = false;
        $('.loading-dots-container').hide();
      }).fail(function(msg){
          $('.force_stop_popup').hide();
          show_snackbar(null,'Error occured, please try again');
        $('.stop_all_appear .stop_all').removeClass('stop_all_disabled');
        $('.loading-dots-container').hide();
      });
}
function refresh_waiting(){
    $('.loading-dots-container').show();
    load_order_log_dict(0,g_limit,0);
}

function refresh_entered(){
    $('.loading-dots-container').show();
    load_order_log_dict(0,g_limit,0);
}

function refresh_stopped(){
    $('.loading-dots-container').show();
    load_order_log_dict(-1,200,0);
}
function load_order_log(status,limit,page,clear=true){
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
      "timeout": 40000,//40 sec timeout
    }
    $('.empty_orders_right').hide();
    switch(parseInt(status)) {
        case 0:$(".status_select select").attr("style","color : #3c4858 !important"); break;
        case -1:$(".status_select select").attr("style","color : #3c4858 !important"); break;
        case 1:$(".status_select select").attr("style","color : #3c4858 !important"); break;
    }
    // $(".loader_parent").fadeIn();
    $.ajax(settings).done(function (msg){
        $(".loader_parent").fadeOut();
        // console.log(msg);
        orders_right = $('.orders_right');
        if(clear)
            orders_right.html('');

        log = msg.grouped_orders
        if(log == null){
            return;
            }
        // algo loop
        try{
            if (log.length<1){
                switch(parseInt(status)) {
                    case 0:no_orders_html = '<div class="empty_orders_right"> <img src="/static/imgs/new/empty/algos-empty.svg"> <p><a href="/dashboard">No strategies</a></p> </div> '; break;
                    case -1:no_orders_html = '<div class="empty_orders_right"> <img src="/static/imgs/new/empty/algos-empty.svg"> <p><a href="/dashboard">No strategies</a></p> </div> '; break;
                    case 1:no_orders_html = '<div class="empty_orders_right"> <img src="/static/imgs/new/empty/algos-empty.svg"> <p><a href="/dashboard">No strategies</a></p> </div> '; break;
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
                    title = $('<div class=token__'+algo.segment_symbol.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+'></div>');
                    switch(parseInt(status)) {
                        case 0:title.append('<div><p class="algo_status_live">'+'Live'+'</p></div>'); break;
                        case -1:title.append('<div><p class="algo_status_stopped">'+'Stopped'+'</p></div>'); break;
                        case 1:title.append('<div><p class="algo_status_completed">'+'Completed'+'</p></div>'); break;
                    }
                    title_algo_name = '<div class="algo_row"><p data-tooltip-top="Click to view algo" id="view_algo_details" class="algo_name view_algo_details">'+algo.algo_name+'<span class="algo_detail_icon"><img src="/static/imgs/icon-more.png"></span></p> <p class="deployed_date">'+moment(algo.deployment_time).format('h:mm:ss A on DD/MM/YYYY')+'</p> <div class="algo_detail_window" id="algo_detail_window" style="display: none;">'+format_algo_summary(algo.algo_obj)+'</div>';

                    title.append(title_algo_name);
                    title.append('<div><p class="eq_name">'+algo.symbol+'<span>&nbsp;'+algo.segment+'</span></p><p class="ltp" id="instrument_token"><span class="sub_title">LTP:&nbsp;&nbsp;</span><span class="sub_ltp">0.0</span></p></div>');

                    title_tag_class = algo.logs[0].log_tag.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
                    title_desc_class = algo.logs[0].log_tag.toLowerCase().split('-').join('_').split(' ').join('_')+'_desc';
                    // if(!['Waiting','Stopped','Completed','Force stopped'].includes(algo.logs[0].log_tag) && algo.logs[0].notification_data!=null)
                    //     {
                    //     if(algo.logs[0].notification_data.trigger_price=="0")
                    //         algo.logs[0].notification_data.trigger_price = 'MARKET';
                    //     else
                    //         top_trigger_price = '  '+ algo.logs[0].notification_data.trigger_price
                    //     // if(algo.logs[0].notification_data.action_type=="SELL" && algo.logs[0].notification_data.type!="take-profit" && algo.logs[0].notification_data.type!="inrange" && algo.logs[0].notification_data.type!="stop-loss")
                    //     //     algo.logs[0].log_tag = 'sold'
                    //     // else if(algo.logs[0].notification_data.action_type=="BUY" && algo.logs[0].notification_data.type!="take-profit" && algo.logs[0].notification_data.type!="inrange" && algo.logs[0].notification_data.type!="stop-loss")
                    //     //     algo.logs[0].log_tag = 'bought'

                    //     // title.append('<div class="recent_notif"><div class="notif_message"><p>'+algo.logs[0].log_message+'</p><p class="'+algo.logs[0].notification_data.action_type+'_notification">'+algo.logs[0].notification_data.action_type+' '+algo.logs[0].notification_data.quantity+' stocks at INR '+algo.logs[0].notification_data.trigger_price+'</p></div><div class="view_order_log" style="display: none;"><button>View Order log</button></div></div>');
                    //     title.append('<div class="status_row"><div class="status_tag"><p><!--<span class="'+title_tag_class+'" >'+algo.logs[0].log_tag+'</span>--></p></div><div><span></span></div><div class="status_detail"><p>'+algo.logs[0].log_message+'&nbsp;<span class="'+title_desc_class+'">'+algo.logs[0].notification_data.action_type+' '+algo.logs[0].notification_data.quantity+' shares of '+algo.logs[0].notification_data.symbol+' at '+top_trigger_price+'</span></p><p>'+moment(algo.logs[0].notification_data.notification_time).format('h:mm:ss A on DD/MM/YYYY')+'</p></div></div>');
                    //     }
                    // else
                    //     {
                        title.append('<div class="status_row"><div class="status_detail" id="status_detail_title"><p><span>'+algo.logs[0].log_message+'</span></p><p>'+moment(algo.logs[0].created_at).format('h:mm:ss A on DD/MM/YYYY')+'</p></div></div>');
                        // }

                    title.append('<div class="target_prices"> <!--<p class="target_prices_first"><span class="bought_b">B</span>&nbsp;<span class="taken_position_qty">100</span><span class="taken_position_price">&nbsp;at 546.32</span></p> <p class="target_prices_second"><span class="waiting_sl">SL:&nbsp;543.78</span>&nbsp;<span class="waiting_tp">TP:&nbsp;650.94</span></p> --></div>');
                    // console.log('AAAAAAAAAAAAAAAAAAAAAAAAAAA')
                    // console.log(algo.logs[0])
                    try{
                        tp = null;
                        sl = null;
                        // if(status==0)
                        // {
                        if(!['Waiting','Stopped','Completed','Force stopped','Algo Expired','User action','At Exchange','SL-M Cancelled'].includes(algo.logs[0].log_tag))
                            {
                                tp = algo.algo_obj.take_profit;
                                sl = algo.algo_obj.stop_loss;
                                // console.log(algo.logs[0].log_tag)
                            }
                        // }
                    }catch(e){
                        tp = null;
                        sl = null;
                    }

                    title.append('<div class="new_pnl_div"><p class="pnl" id="live__'+algo.deployment_uuid+'" data-tp='+tp+' data-sl='+sl+'><span class="sub_title">P&amp;L:&nbsp;&nbsp;</span><span style="color: #8b9096;font-weight: 400;">&nbsp;</span><span style="color: #8b9096;font-weight: 400;">NA&nbsp;</span><span style="color: #8b9096;font-weight: 400;" style="display:none">(NA%)&nbsp;</span></p><p class="target_prices_second"></p></div>');

                    force_stop_div = $('<div></div>');
                    // $('.exit_position, .algo_stopped').hide();$('.force_stop_popup, .stop_options').show();$('body').addClass('body_scroll');
                    if (parseInt(status)==0)
                        force_stop_div.append('<button class="force_stop" onclick="force_stop(event,\''+algo.deployment_uuid+'\')"><img src="/static/imgs/icon-force-stop.png">&nbsp;&nbsp;Stop</button>');
                    //force_stop_div.append('<button class="bt_graph" onclick="show_backtest(event,\''+algo.deployment_uuid+'\',\''+algo.segment_symbol+'\')"><img src="/static/imgs/icon-bt-graph-brown.png"></button>');
                    force_stop_div.append('<div class="results_section" style="display: none;"></div>');
                    force_stop_div.append('<button class="icon-order-log" ><img src="/static/imgs/icon-view-order-details.png"></button>');

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
                            tag_class = algo.logs[j].log_tag.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
                            desc_class = algo.logs[j].log_tag.toLowerCase().split('-').join('_').split(' ').join('_')+'_desc';
                            if(!['Waiting','Stopped','Completed','Force stopped','Algo Expired','User action','At Exchange','SL-M Cancelled'].includes(algo.logs[j].log_tag) && (algo.logs[j].notification_data!=null || algo.logs[j].notification_data!={}))
                                { // this requires notification_data to be present
                                    if(algo.logs[j].notification_data.trigger_price=="0")
                                        algo.logs[j].notification_data.trigger_price = 'MARKET';
                                    else
                                        {
                                            if(algo.logs[j].log_message.indexOf('SL-M')!=-1){
                                                algo.logs[j].notification_data.trigger_price = 'TRIGGER PRICE   '+ parseFloat(algo.logs[j].notification_data.trigger_price).toFixed(2)
                                            }
                                            else{
                                                algo.logs[j].notification_data.trigger_price = '  '+ parseFloat(algo.logs[j].notification_data.trigger_price).toFixed(2)
                                            }
                                        }
                                    // if(algo.logs[j].notification_data.action_type=="SELL" && (algo.logs[j].notification_data.action_type=='Bought'||algo.logs[j].notification_data.action_type=='Sold') && algo.logs[j].notification_data.type!="take-profit")
                                    //     algo.logs[j].log_tag = 'sold';
                                    // else if(algo.logs[j].notification_data.action_type=="Buy" && (algo.logs[j].notification_data.action_type=='Bought'||algo.logs[j].notification_data.action_type=='Sold') && algo.logs[j].notification_data.type!="take-profit")
                                    //     algo.logs[j].log_tag = 'bought';
                                    // console.log(algo.logs[j].notification_data.action_type);
                                    if(['Rejected'].includes(algo.logs[j].log_tag))
                                        status_row = '<div class="status_row"><div class="status_tag"><p><span class="'+tag_class+'" >'+algo.logs[j].log_tag+'</span></p></div><div><span></span></div><div class="status_detail"><p>'+algo.logs[j].log_message+'&nbsp;<span class="'+desc_class+'">'+algo.logs[j].notification_data.action_type+' '+algo.logs[j].notification_data.quantity+' shares of '+algo.logs[j].notification_data.symbol+' at '+algo.logs[j].notification_data.trigger_price+'</span><span class="details" onclick="show_order_details_notif(\''+algo.logs[j].notification_data.order_id+'\')">Rejected</span></p><p>'+moment(algo.logs[j].notification_data.notification_time).format('h:mm:ss A on DD/MM/YYYY')+'</p></div></div>';
                                    else if(['Bought','Sold'].includes(algo.logs[j].log_tag))
                                        status_row = '<div class="status_row"><div class="status_tag"><p><span class="'+tag_class+'" >'+algo.logs[j].log_tag+'</span></p></div><div><span></span></div><div class="status_detail"><p>'+algo.logs[j].log_message+'&nbsp;<span class="'+desc_class+'">'+algo.logs[j].notification_data.action_type+' '+algo.logs[j].notification_data.quantity+' shares of '+algo.logs[j].notification_data.symbol+' at '+algo.logs[j].notification_data.trigger_price+'</span><span class="details" onclick="show_order_details_notif(\''+algo.logs[j].notification_data.order_id+'\',\'Complete\')">Completed</span></p><p>'+moment(algo.logs[j].notification_data.notification_time).format('h:mm:ss A on DD/MM/YYYY')+'</p></div></div>';
                                    else{
                                        if(['Buy alert','Sell alert','Target profit alert','Stop loss alert'].includes(algo.logs[j].log_tag)){
                                            var take_action_notification_data = algo.logs[j].notification_data;
                                            take_action_notification_data = JSON.stringify(take_action_notification_data);
                                            // console.log(algo.logs[j].log_tag+'---'+j+'--------'+algo.logs.length);
                                            if(j==0 && parseInt(status)==0)
                                                {
                                                    status_row = '<div class="status_row"><div class="status_tag"><p><span class="'+tag_class+'" >'+algo.logs[j].log_tag+'</span></p></div><div><span></span></div><div class="status_detail"><p>'+algo.logs[j].log_message+'&nbsp;<span class="'+desc_class+'">'+algo.logs[j].notification_data.action_type+' '+algo.logs[j].notification_data.quantity+' shares of '+algo.logs[j].notification_data.symbol+' at '+algo.logs[j].notification_data.trigger_price+'</span><span class="details" onclick=\'take_action(event,'+take_action_notification_data+')\'>Take action</span></p><p>'+moment(algo.logs[j].notification_data.notification_time).format('h:mm:ss A on DD/MM/YYYY')+'</p></div></div>';
                                                }
                                            else{
                                                status_row = '<div class="status_row"><div class="status_tag"><p><span class="'+tag_class+'" >'+algo.logs[j].log_tag+'</span></p></div><div><span></span></div><div class="status_detail"><p>'+algo.logs[j].log_message+'&nbsp;<span class="'+desc_class+'">'+algo.logs[j].notification_data.action_type+' '+algo.logs[j].notification_data.quantity+' shares of '+algo.logs[j].notification_data.symbol+' at '+algo.logs[j].notification_data.trigger_price+'</span></p><p>'+moment(algo.logs[j].notification_data.notification_time).format('h:mm:ss A on DD/MM/YYYY')+'</p></div></div>';
                                            }
                                        }else{
                                            // user actions come here
                                            status_row = '<div class="status_row"><div class="status_tag"><p><span class="'+tag_class+'" >'+algo.logs[j].log_tag+'</span></p></div><div><span></span></div><div class="status_detail"><p>'+algo.logs[j].log_message+'&nbsp;<span class="'+desc_class+'">'+algo.logs[j].notification_data.action_type+' '+algo.logs[j].notification_data.quantity+' shares of '+algo.logs[j].notification_data.symbol+' at '+algo.logs[j].notification_data.trigger_price+'</span></p><p>'+moment(algo.logs[j].notification_data.notification_time).format('h:mm:ss A on DD/MM/YYYY')+'</p></div></div>';
                                            if(algo.logs[j].notification_data.status=='CANCELLED' && algo.logs[j].notification_data.order_type=='SL-M'){
                                                    status_row = '<div class="status_row"><div class="status_tag"><p><span class="'+tag_class+'" >'+algo.logs[j].log_tag+'</span></p></div><div><span></span></div><div class="status_detail"><p>'+algo.logs[j].log_message+'&nbsp;<span class="'+desc_class+'">'+algo.logs[j].notification_data.action_type+' '+algo.logs[j].notification_data.quantity+' shares of '+algo.logs[j].notification_data.symbol+'</span></p><p>'+moment(algo.logs[j].notification_data.notification_time).format('h:mm:ss A on DD/MM/YYYY')+'</p></div></div>';
                                                }
                                        }
                                    }

                                }
                            else
                               { 
                                status_row ='<div class="status_row"><div class="status_tag"><p><span class="'+tag_class+'">'+algo.logs[j].log_tag+'</span></p></div><div><span></span></div><div class="status_detail"><p class="'+desc_class+'">'+algo.logs[j].log_message+'&nbsp;</p><p>'+moment(algo.logs[j].created_at).format('h:mm:ss A on DD/MM/YYYY')+'</p></div></div>';
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
            // $(this).parents(".orders_details").find(".orders_details_body").slideToggle();
            // $(".orders_details_body").hide();
            $("body").addClass("body_scroll");
            $(".order_log_popup").show();
        });
        
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
        $(".loader_parent").fadeOut();
        switch(parseInt(status)) {
            case 0:no_orders_html = '<div class="empty_orders_right"> <img src="/static/imgs/new/empty/algos-empty.svg"> <p><a href="/dashboard">No strategies</a></p> </div> '; break;
            case -1:no_orders_html = '<div class="empty_orders_right"> <img src="/static/imgs/new/empty/algos-empty.svg"> <p><a href="/dashboard">No strategies</a></p> </div> '; break;
            case 1:no_orders_html = '<div class="empty_orders_right"> <img src="/static/imgs/new/empty/algos-empty.svg"> <p><a href="/dashboard">No strategies</a></p> </div> '; break;
        }
        $('.orders_right').html(no_orders_html);
        $('.empty_orders_right').show();
    }).complete(function(){
        $(".loader_parent").fadeOut();
    });
    setTimeout(function(){
        refresh_ltp_subscription();
        refresh_pnl_subscription();
    },1000);
}

function update_order_log(order_obj,order_list,status,initial=false){
    orders_right_waiting = $('#waiting_orders');
    orders_right_entered = $('#entered_orders');
    orders_right_stopped = $('#stopped_orders');
        
    if(initial){
        
        if(status=="live"){
            orders_right_waiting.html('');
            orders_right_entered.html('');
            
            waiting_count = 0;
            entered_count = 0;
        }
        else if(status=="stopped"){
            orders_right_stopped.html('');
            stopped_count = 0;
        }

        for(var i=0;i<order_list.length;i++){
            algo = order_list[i]

            orders_details = $('<div class="orders_details"></div>');
            orders_details_title_outer = $('<div class="orders_details_title_outer"></div>');
            orders_details_title = $('<div class="orders_details_title"></div>');
            title = $('<div class=token__'+algo.segment_symbol.replace('&','\\&').replace('/','_--_').replace(/ /g,'_-_')+' id="'+algo.deployment_uuid+'" data-search-val="'+algo.segment_symbol+algo.algo_name+'"></div>');
            
            live_indicator = '<div class="live_indicator_detail"><span class="indicator_grey"></span></div>';
            if(status=='live')
                live_indicator = '<div class="live_indicator_detail"><span class="indicator_green"></span></div>';
            else
                live_indicator = '<div class="live_indicator_detail"><span class="indicator_grey"></span></div>';

            title.append(live_indicator);
            
            // title_algo_name = '<div class="algo_row"><p data-tooltip-top="Click to view algo" id="view_algo_details" class="algo_name view_algo_details">'+algo.algo_name+'<span class="algo_detail_icon"><img src="/static/imgs/icon-more.png"></span></p> <p class="deployed_date">'+moment(algo.deployment_time).format('h:mm:ss A on DD/MM/YYYY')+'</p> <div class="algo_detail_window" id="algo_detail_window" style="display: none;">'+format_algo_summary(algo.algo_obj)+'</div>';
            title_algo_name = '<div class="algo_row"><p id="view_algo_details" class="algo_name view_algo_details">'+algo.algo_name+'<!--<span class="algo_detail_icon"><img src="/static/imgs/icon-more.png"></span>--></p> <!--<p class="deployed_date">'+moment(algo.deployment_time).format('h:mm:ss A on DD/MM/YYYY')+'</p><div class="algo_detail_window" id="algo_detail_window" style="display: none;">'+format_algo_summary(algo.algo_obj)+'--></div>';
            title.append(title_algo_name);

            title.append('<div class="scrip_row_detail"><p class="eq_name">'+algo.symbol+'<span>&nbsp;'+algo.segment+'</span></p></div>');

            if(algo.status==0){
                if(['Buy alert','Sell alert','Target profit alert','Stop loss alert'].includes(algo.logs[0].log_tag) && status=='live')
                {
                  if(algo.logs[0].log_tag=="Buy alert")
                    title.append('<div class="status_row"><p><img src="/static/imgs/new/alert_blue.gif"></p></div>');
                  else if(algo.logs[0].log_tag=="Sell alert")
                    title.append('<div class="status_row"><p><img src="/static/imgs/new/alert_orange.gif"></p></div>');
                  else if(algo.logs[0].log_tag=="Target profit alert")
                    title.append('<div class="status_row"><p><img src="/static/imgs/new/alert_green.gif"></p></div>');
                  else if(algo.logs[0].log_tag=="Stop loss alert")
                    title.append('<div class="status_row"><p><img src="/static/imgs/new/alert_red.gif"></p></div>');
                }
                else{
                    title.append('<div class="status_row"><p></p></div>');
                }               
            }else{
                    title.append('<div class="status_row"><p></p></div>');
            }
            
            title.append('<div class="ltp_row_detail"><p class="ltp" id="instrument_token"><!--<span class="sub_title">LTP:&nbsp;&nbsp;</span>--><span class="sub_ltp">0.0</span></p></div>');

            try{
                tp = null;
                sl = null;
                // if(status==0)
                // {
                // if(!['Waiting','Stopped','Completed','Force stopped','Algo Expired'].includes(algo.logs[0].log_tag))
                    {
                        tp = algo.algo_obj.take_profit;
                        sl = algo.algo_obj.stop_loss;
                        // console.log(algo.logs[0].log_tag)
                    }
                // }
            }catch(e){
                tp = null;
                sl = null;
            }

            title.append('<div class="new_pnl_div"><p class="pnl" id="live__'+algo.deployment_uuid+'" data-tp='+tp+' data-sl='+sl+'><!--<span class="sub_title">P&amp;L:&nbsp;&nbsp;</span>--><span style="color: #8b9096;font-weight: 400;">&nbsp;</span><span class="na_class">NA</span><!--<span style="color: #8b9096;font-weight: 400;" style="display:none">(NA%)&nbsp;</span>-></p><p class="target_prices_second"></p></div>');

            title.append('<div class="positions_row_detail target_prices_order"><p class="target_prices_first"><span class="na_class">NA</span></p></div>');

            title_tag_class = algo.logs[0].log_tag.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
            title_desc_class = algo.logs[0].log_tag.toLowerCase().split('-').join('_').split(' ').join('_')+'_desc';

            // tag_class = algo.logs[0].log_tag.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
            // desc_class = algo.logs[0].log_tag.toLowerCase().split('-').join('_').split(' ').join('_')+'_desc';

            title.append('<!--<div class="status_row"><div class="status_detail" id="status_detail_title"><p><span>'+algo.logs[0].log_message+'</span></p><p>'+moment(algo.logs[0].created_at).format('h:mm:ss A on DD/MM/YYYY')+'</p></div></div>-->');
            title.append('<div class="target_prices"><p class="target_prices_second"><span class="na_class">NA</span></p></div>');
            // console.log('AAAAAAAAAAAAAAAAAAAAAAAAAAA')
            // console.log(algo.logs[0])

            menu_dots_div = $('<div class="menu_dots"><p><img src="/static/imgs/new/menu_dots.svg"></p></div>');
            // $('.exit_position, .algo_stopped').hide();$('.force_stop_popup, .stop_options').show();$('body').addClass('body_scroll');
            action_buttons_div = $('<div class="action_buttons"></div>');


            if(algo.status!=0){
                action_buttons_div.append('<button class="icon-order-log" onclick="populate_order_log(\''+algo.deployment_uuid+'\',\'stopped\')"><img src="/static/imgs/new/orderlog.svg">Order log</button>')
              action_buttons_div.append('<button class="algo_details" onclick="show_algo_details(\''+algo.deployment_uuid+'\',\'stopped\');"><img src="/static/imgs/new/algo_details.svg">Strategy details</button>');
              //deploy_algorithm_multi_popup
              action_buttons_div.append('<button class="deploy" onclick="deploy_algorithm_multi_popup(event,$(this),\''+algo.algo_obj.algo_name+'\',\''+algo.algo_obj.action_str+'\',\''+algo.algo_obj.action_str_exit+'\',\''+algo.algo_obj.action_type+'\',\''+algo.algo_obj.quantity+'\',\''+algo.algo_obj.take_profit+'\',\''+algo.algo_obj.stop_loss+'\',\''+algo.algo_obj.time_frame+'\',\''+algo.deployment_uuid+'\',\''+algo.algo_obj.chart_type+'\',\''+algo.algo_obj.trading_start_time+'\',\''+algo.algo_obj.trading_stop_time+'\',\''+algo.segment_symbol+'\');"><img src="/static/imgs/new/r.svg">Re-deploy</button>');
            }else{
              var take_action_notification_data = null
              if(['Buy alert','Sell alert','Target profit alert','Stop loss alert'].includes(algo.logs[0].log_tag) && status=='live')
                {
                  take_action_notification_data = algo.logs[0].notification_data;
                  take_action_notification_data = JSON.stringify(take_action_notification_data);
                }
                
                action_buttons_div.append('<button class="icon-order-log" onclick=\'populate_order_log("'+algo.deployment_uuid+'","live",'+take_action_notification_data+')\'><img src="/static/imgs/new/orderlog.svg">Order log</button>')
            action_buttons_div.append('<button class="algo_details" onclick="show_algo_details(\''+algo.deployment_uuid+'\',\'live\');"><img src="/static/imgs/new/algo_details.svg">Strategy details</button>');

            }



            if(['Buy alert','Sell alert','Target profit alert','Stop loss alert'].includes(algo.logs[0].log_tag) && status=='live')
                {
                    var take_action_notification_data = algo.logs[0].notification_data;
                    take_action_notification_data = JSON.stringify(take_action_notification_data);
                    status_row = '<div class="status_row"><div class="status_tag_orderlog"><p><span class="'+title_tag_class+'" >'+algo.logs[0].log_tag+'</span></p></div><div><span></span></div><div class="status_detail_orderlog"><p>'+algo.logs[0].log_message+'&nbsp;<span class="'+title_desc_class+'">'+algo.logs[0].notification_data.action_type+' '+algo.logs[0].notification_data.quantity+' shares of '+algo.logs[0].notification_data.symbol+' at '+algo.logs[0].notification_data.trigger_price+'</span><span class="details" onclick=\'take_action(event,'+take_action_notification_data+')\'>Take action</span></p><p>'+moment(algo.logs[0].notification_data.notification_time).format('h:mm:ss A on DD/MM/YYYY')+'</p></div></div>';
                    action_buttons_div.append('<button class="take_action" onclick=\'take_action(event,'+take_action_notification_data+')\'><img src="/static/imgs/new/take_action.svg">Take action</button>');

                    orders_details_title.attr('onclick',"take_action(event,"+take_action_notification_data+")");

                }
            else{

                    var take_action_notification_data = algo.logs[0].notification_data;
                    take_action_notification_data = JSON.stringify(take_action_notification_data);
                    status_row = '<div class="status_row"><div class="status_tag_orderlog"><p><span class="'+title_tag_class+'" >'+algo.logs[0].log_tag+'</span></p></div><div><span></span></div><div class="status_detail_orderlog"><p>'+algo.logs[0].log_message+'&nbsp;<span class="'+title_desc_class+'">'+algo.logs[0].notification_data.action_type+' '+algo.logs[0].notification_data.quantity+' shares of '+algo.logs[0].notification_data.symbol+' at '+algo.logs[0].notification_data.trigger_price+'</span></p><p>'+moment(algo.logs[0].notification_data.notification_time).format('h:mm:ss A on DD/MM/YYYY')+'</p></div></div>';
            }
            
            if (status!='stopped')
                action_buttons_div.append('<button class="force_stop" onclick="force_stop(event,\''+algo.deployment_uuid+'\')"><img src="/static/imgs/new/stop.svg">Stop</button>');
            // else
                // action_buttons_div.append('<button class="deploy" onclick="deploy(event,\''+algo.deployment_uuid+'\')"><img src="/static/imgs/new/r.svg">Re-deploy</button>');

        
            //force_stop_div.append('<button class="bt_graph" onclick="show_backtest(event,\''+algo.deployment_uuid+'\',\''+algo.segment_symbol+'\')"><img src="/static/imgs/icon-bt-graph-brown.png"></button>');
            // force_stop_div.append('<div class="results_section" style="display: none;"></div>');
            // force_stop_div.append('<button class="icon-order-log" ><img src="/static/imgs/icon-view-order-details.png"></button>');

            if(algo.status===0 && !algo.algorithm_position.positions.qty){
              title.append('<div class="checkbox_row_detail"> <input type="checkbox" name="" class="stop_checkbox" id="stop_checkbox__'+algo.segment_symbol+'" onclick="select_any(event,$(this))"> </div>');
            }
            menu_dots_div.append(action_buttons_div);
            title.append(menu_dots_div);
            orders_details_title.html(title);
            orders_details_title_outer.append(orders_details_title);

            orders_details_body = $('<div class="orders_details_body" style="display:none;"></div>');
            progress_section = $('<div class="progress_section"></div>');
            prompter = $('<div class="prompter"></div>');
            
            // log loop
            blank_row = '<div class="status_row"><div class="status_tag_orderlog"><p></p></div><div></div><div class="status_detail_orderlog"><p></p><p></p></div></div>';
            prompter.append(blank_row);
            orders_details_body.append(progress_section);
            orders_details.append(orders_details_title_outer);
            // orders_details.append(orders_details_body)
            if(algo.status === 0 && algo.algorithm_position && algo.algorithm_position.positions.qty){
                orders_right_entered.append(orders_details);
                entered_count += 1
            }else if(algo.status === 0){
                waiting_count += 1
                orders_right_waiting.append(orders_details);
            }else{
                stopped_count += 1
                orders_right_stopped.append(orders_details);
            }
        }


        $(".menu_dots>p>img").off("click");
        $(".menu_dots>p>img").click(function(e){
                // alert($(this).parents(".menu_dots").find(".action_buttons").className);
                $(".action_buttons").slideUp();
                $(".menu_dots>p>img").hide();
                $(this).parents(".menu_dots").find('p>img').show();
                $(this).parents(".menu_dots").find('.action_buttons').slideDown();
                action_buttons = true;
                e.stopPropagation();
            });
    }

    if(current=='waiting'){
        orders_right_waiting.show();
        $('#waiting_bar').attr('style','display:flex!important');
        
        orders_right_entered.hide();
        orders_right_stopped.hide();

        $('#entered_bar').hide();
        $('#stopped_bar').hide();
    }else if(current=='entered'){
        orders_right_entered.show();
        $('#entered_bar').attr('style','display:flex!important');

        orders_right_waiting.hide();
        orders_right_stopped.hide();

        $('#waiting_bar').hide();
        $('#stopped_bar').hide();
    }else if(current=='stopped'){
        orders_right_stopped.show();
        $('#stopped_bar').attr('style','display:flex!important');

        orders_right_entered.hide();
        orders_right_waiting.hide();

        $('#entered_bar').hide();
        $('#waiting_bar').hide();
    }


    if(status=="live"){
      if(waiting_count!=0){
            $('#waiting_option').text('Waiting ('+waiting_count+')');
            $('#waiting_heading_title').text('Waiting ('+waiting_count+')');
          }
        else{
            $('#waiting_option').text('Waiting');
            $('#waiting_heading_title').text('Waiting');
            orders_right_waiting.html('<div class="empty_orders_right"><img src="/static/imgs/new/empty/algos-empty.svg"><p>No strategies waiting</p></div>');
            $('.stop_all_appear').slideUp();
            $('.stop_all_appear .stop_all').addClass('stop_all_disabled');
          }
        if(entered_count!=0){
            $('#entered_option').text('Entered ('+entered_count+')');
            $('#entered_heading_title').text('Entered ('+entered_count+')');
            if(page_loading)
            {
              load_entered();
              page_loading = false;
            }

          }
        else{
            $('#entered_option').text('Entered');
            $('#entered_heading_title').text('Entered');
            orders_right_entered.html('<div class="empty_orders_right"><img src="/static/imgs/new/empty/algos-empty.svg"><p>No strategies entered</p></div>');
          }
    }
    else if(status=='stopped'){
      if(stopped_count!=0)
          {
            $('#stopped_option').text('Stopped ('+stopped_count+')');
            $('#stopped_heading_title').text('Stopped ('+stopped_count+')');
          }
        else{
            $('#stopped_option').text('Stopped');
            $('#stopped_heading_title').text('Stopped');
            orders_right_stopped.html('<div class="empty_orders_right"><img src="/static/imgs/new/empty/algos-empty.svg"><p>No strategies stopped</p></div>');
          }
    }

    $('.loading-dots-container').hide();
    $(".orders_details_title_outer").hover(function(){
        $(this).find(".menu_dots img").show();
    });
    $(".orders_details_title_outer").mouseleave(function(){
        if(!$(this).find('.action_buttons').is(':visible')){
            $(this).find(".menu_dots>p>img").hide();
        }
        // console.log($(this).find('.action_buttons').is('visible'));
    });
    // setTimeout(function(){
    //     refresh_ltp_subscription();
    //     refresh_pnl_subscription();
    // },1000);
}

function load_order_log_dict(status,limit,page,clear=true){
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
      "timeout": 40000,//40 sec timeout
    }
    // $('.empty_orders_right').hide();
    switch(parseInt(status)) {
        case 0:$(".status_select select").attr("style","color : #3c4858 !important"); break;
        case -1:$(".status_select select").attr("style","color : #3c4858 !important"); break;
        case 1:$(".status_select select").attr("style","color : #3c4858 !important"); break;
    }
    $('.loading-dots-container').show();
    // $(".loader_parent").fadeIn();
    $.ajax(settings).done(function (msg){
        $(".loading-dots-container").fadeOut();
        // console.log(msg);
        // orders_right = $('.orders_right');
        // if(clear)
            // orders_right.html('');

        log = msg.grouped_orders
        if(log == null){
            return;
            }

        // algo loop
        try{
            if (log.length<1){
                switch(parseInt(status)) {
                    case 0:no_orders_html = '<div class="empty_orders_right"> <img src="/static/imgs/new/empty/algos-empty.svg"> <p><a href="/dashboard">No strategies</a></p> </div> '; break;
                    case -1:no_orders_html = '<div class="empty_orders_right"> <img src="/static/imgs/new/empty/algos-empty.svg"> <p><a href="/dashboard">No strategies</a></p> </div> '; break;
                    case 1:no_orders_html = '<div class="empty_orders_right"> <img src="/static/imgs/new/empty/algos-empty.svg"> <p><a href="/dashboard">No strategies</a></p> </div> '; break;
                }
                // $('.orders_right').html(no_orders_html);
                // $('.empty_orders_right').show();

                if(status==0){
                        order_log_live_obj = {};
                        order_log_live_list = [];
                        orders_right_waiting = $('#waiting_orders');
                        orders_right_entered = $('#entered_orders');
                        orders_right_waiting.html('');
                        orders_right_entered.html('');

                        $('#waiting_option').text('Waiting');
                        $('#waiting_heading_title').text('Waiting');

                        $('#entered_option').text('Entered');
                        $('#entered_heading_title').text('Entered');
            
                    }
                else{
                    order_log_stopped_obj = {};
                    order_log_stopped_list = [];
                    orders_right_stopped = $('#stopped_orders');
                    $('#stopped_option').text('Stopped');
                    $('#stopped_heading_title').text('Stopped');
                }

                if(status==0)
                {
                    order_log_live_obj = temp_order_log_obj;
                    order_log_live_list = temp_order_log_list;
                    update_order_log({},[],'live',true);
                }
                else{
                    order_log_stopped_obj = temp_order_log_obj;
                    order_log_stopped_list = temp_order_log_list;
                    update_order_log({},[],'stopped',true);
                }
            }
            else
            {   
                var temp_order_log_obj = {};
                var temp_order_log_list = [];
                for (var i = 0; i<log.length; i++){
                    try{
                        algo = log[i];
                        temp_order_log_obj[algo.deployment_uuid] = algo;
                        temp_order_log_list.push(algo);
                    }catch(e){
                        console.log(e);
                    }
                }

                if(status==0)
                {
                    order_log_live_obj = temp_order_log_obj;
                    order_log_live_list = temp_order_log_list;
                    update_order_log(order_log_live_obj,order_log_live_list,'live',true);
                }
                else{
                    order_log_stopped_obj = temp_order_log_obj;
                    order_log_stopped_list = temp_order_log_list;
                    update_order_log(order_log_stopped_obj,order_log_stopped_list,'stopped',true);
                }
            }

            // if(msg.pages>pagination+1){
            //     $('.show_more_eq').show();
            // }
            // else{
            //     $('.show_more_eq').hide();                
            // }
        }
        catch(e){
            console.log(e);
        }
        $(".recent_notif, .icon-order-log").click(function(){
            // $(this).parents(".orders_details").find(".orders_details_body").slideToggle();
            // $(".orders_details_body").hide();
            $("body").addClass("body_scroll");
            $(".order_log_popup").show();
        });
        
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
        $(".loading-dots-container").fadeOut();
        switch(parseInt(status)) {
            case 0:no_orders_html = '<div class="empty_orders_right"> <img src="/static/imgs/new/empty/algos-empty.svg"> <p><a href="/dashboard">No strategies</a></p> </div> '; break;
            case -1:no_orders_html = '<div class="empty_orders_right"> <img src="/static/imgs/new/empty/algos-empty.svg"> <p><a href="/dashboard">No strategies</a></p> </div> '; break;
            case 1:no_orders_html = '<div class="empty_orders_right"> <img src="/static/imgs/new/empty/algos-empty.svg"> <p><a href="/dashboard">No strategies</a></p> </div> '; break;
        }
        $('.orders_right').html(no_orders_html);
        $('.empty_orders_right').show();
    }).complete(function(){
        $(".loading-dots-container").fadeOut();
        if(status==0 && first_loading==true)
            {
                load_order_log_dict(-1,g_limit*5,0);
                first_loading = false;
            }
        else if(first_loading==true)
            {
                load_order_log_dict(0,g_limit,0);
                first_loading = false;
            }
    });
    
    setTimeout(function(){
        refresh_ltp_subscription();
        refresh_pnl_subscription();
    },1000);
    
    // $(".menu_dots>p>img").click(function(e){
    //     // alert($(this).parents(".menu_dots").find(".action_buttons").className);
    //     $(".action_buttons").slideUp();
    //     $(".menu_dots>p>img").hide();
    //     $(this).parents(".menu_dots").find('p>img').show();
    //     $(this).parents(".menu_dots").find('.action_buttons').slideDown();
    //     action_buttons = true;
    //     e.stopPropagation();
    // });
}

function show_order_details(order_id,type='Rejected'){
    var params = {
        'order_id':order_id
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/show_order_details/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 10000,//40 sec timeout
    }
    $.ajax(settings).done(function (msg){
        // console.log(msg);
        if (msg.status=="success"){

            if(type=='Complete'){
                green_style = 'style="color: #06c579 !important"'
            }
            else{
                green_style = ''
            }
            $('.order_details_popup').show();$('body').addClass('body_scroll');
            order = JSON.parse(msg.order);
            order_status = order.order_status;
            order_details_header = '<div class="order_name"> <p>'+order_status.tradingsymbol+'<span>'+order_status.exchange+'</span></p> <p>'+order_status.transaction_type+' '+order_status.quantity+' shares at '+order_status.order_type+'</p> </div> <div class="order_avg_price"> <p>Avg. Price</p> <p>'+order_status.average_price+'</p> </div> <div class="order_filled_qty"> <p>Filled Quantity</p> <p>'+order_status.filled_quantity+' of '+order_status.quantity+'</p> </div>';
            $('.order_details_header').html(order_details_header);

            order_details_body = '<div class="order_details_row"> <div> <p>Price</p> <p>'+order_status.price+'</p> </div> <div> <p>Trigger Price</p> <p>'+order_status.trigger_price+'</p> </div> <div> <p>Order placed by</p> <p>'+order_status.user_id+'</p> </div> </div> <div class="order_details_row"> <div> <p>Order Type</p> <p>'+order_status.order_type+'</p> </div> <div> <p>Product Validity</p> <p>'+order_status.product+'/'+order_status.validity+'</p> </div> <div> <p>Time</p> <p>'+order_status.order_timestamp+'</p> </div> </div> <div class="order_details_row"> <div> <p>Order ID</p> <p>'+order_status.order_id+'</p> </div> <div> <p>Exchange order ID</p> <p>'+order_status.exchange_order_id+'</p> </div> <div> <p>Exchange Time</p> <p>'+order_status.exchange_timestamp+'</p> </div> </div> <div class="order_details_row"> <div class="status"> <p>Status</p> <p '+green_style+'>'+order_status.status+'</p> </div> <div id="status_message"> <p>STATUS MESSAGE</p> <p >'+order_status.status_message+'</p> </div> </div>'
            $('.order_details_body').html(order_details_body);
        }
        else{
            show_snackbar(null,'Error fetching order details');
            }
    }).fail(function(){
        show_snackbar(null,'Error fetching order details');
    });
}

function switch_order_type_orders(event,switch_to,deployment_uuid){
  order_window_param = take_action_order_window_params[deployment_uuid];
  notif_data = order_window_param[22];
  if (order_window_param[12]!="Entry" && switch_to=='BO'){
    show_snackbar(null,'BO is not available for while exiting');
    return;
  }
  if (order_window_param[5]!="MIS" && switch_to=='BO'){
    show_snackbar(null,'BO is not available for NRML');
    return;
  }
  if(switch_to=='LIMIT'){
    order_window_param[3]='LIMIT';
    notif_data['order_type']='LIMIT';
    order_window = update_take_action(event,notif_data);
  }
  if(switch_to=='MARKET'){
    order_window_param[3]='MARKET';
    notif_data['order_type']='MARKET';
    order_window_param[10]='REGULAR';
    notif_data['variety']='REGULAR';
    order_window = update_take_action(event,notif_data);
  }
  if(switch_to=='REGULAR'){
    order_window_param[10]='REGULAR';
    notif_data['variety']='REGULAR';
    order_window = update_take_action(event,notif_data);
  }
  if(switch_to=='BO' && order_window_param[5]=='MIS' && order_window_param[2]!='MCX'){
    order_window_param[3]='LIMIT';
    order_window_param[10]='BO';
    notif_data['order_type']='LIMIT';
    notif_data['variety']='BO';
    order_window = update_take_action(event,notif_data);
  }
}

function take_action(e,notification_data) {
    console.log(notification_data, 'notification_data');
    if((e.target.parentElement.className=='action_buttons'||e.target.parentElement.className=='menu_dots') && (e.target.parentElement.className!="take_action" && e.target.className!="take_action"))
      {
        e.stopPropagation();
        return
      }
    notif = notification_data;
    var quantity = null;
    var product = null;
    var symbol = null;
    var segment = null;
    var algo_uuid = null;
    var algo_name = null;
    var transaction_type = null;
    var deployment_uuid = null;
    var notification_uuid = null;
    var notification_msg = null;
    var notification_title = null;
    var notification_time = null;
    var dt = null;
    var notification_tag = null;
    var notif_state = null;
    var price = 0;
    if(notif['notification-type'] == "order-notification"){
        dt = moment(notif.notification_time)
        notification_time = dt.format('h:mm:ss a');
        notification_title = notif.action_type + ' alert';
        notification_msg = notif.action_type+' '+notif.quantity+' shares of '+notif.symbol+' at &nbsp; '+parseFloat(notif.trigger_price).toFixed(2);
        notification_tag = notification_title.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
        quantity = parseInt(notif['quantity']);
        product = notif['product'];
        symbol = notif['sym'];
        segment = notif['seg'];
        algo_uuid = notif['algo_uuid'];
        algo_name = notif['algo_name'];
        transaction_type = notif['action_type'];
        deployment_uuid = notif['deployment_uuid'];
        notification_uuid = notif['notification_uuid']
        price = parseFloat(notif.trigger_price);
        order_type = notif['order_type'];
        variety = notif['variety'];
        target_profit = notif['target_profit'];
        stop_loss = notif['stop_loss'];
        tpsl_type = notif['tpsl_type'];
        notification_tag = notification_title.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
        tag = '';
        validity = 'DAY';
        disclosed_qty = 0;
        onclick_confirm = 'place_order_take_action';
        notif_state = 'Entry';

        if(notif['sender']!='lambda'){
              notif_state = 'Exit';
        }

        order_type = 'MARKET';
        if(variety=='BO' && tp!=null && sl!=null && product=='MIS' && segment!='MCX'){
          order_type = 'LIMIT';
        }
        notification_tag = notification_title.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
    }
    if(notif['price_trigger-notification']!=undefined){
        tpsl_key=notif['price_trigger-notification'];
        trigger_time = notif['trigger_time'];
        trigger_price = notif['trigger_price'];
        trigger_type = notif['type'];
        tpsl_array = tpsl_key.split(':');
        deployment_uuid = tpsl_array[1];
        token = tpsl_array[3];
        algo_name = tpsl_array[8];
        transaction_type = tpsl_array[9];
        action_type = transaction_type;
        quantity = parseInt(tpsl_array[10]);
        algo_uuid = tpsl_array[11];
        product = tpsl_array[12];
        symbol = tpsl_array[13];
        segment = tpsl_array[14];
        notification_uuid = notif['notification_uuid'];

        price = trigger_price;
        order_type = notif['order_type'];
        variety = notif['variety'];
        target_profit = notif['target_profit'];
        stop_loss = notif['stop_loss'];
        tpsl_type = notif['tpsl_type'];
        tag = '';
        validity = 'DAY';
        disclosed_qty = 0;
        onclick_confirm = 'place_order_take_action';

        order_type = 'MARKET';
        if(variety=='BO' && tp!=null && sl!=null && product=='MIS' && segment!='MCX'){
          order_type = 'LIMIT';
        }

        if(trigger_type=="take-profit"){
        notification_msg = "Take profit at &nbsp;  "+parseFloat(trigger_price).toFixed(2);
        notification_title = 'Target profit' + ' alert';
        notif_state = 'Exit';
          }
          else if(trigger_type=="stop-loss"){
            notification_msg = "Stop loss at &nbsp;  "+parseFloat(trigger_price).toFixed(2);
            notification_title = 'Stop loss' + ' alert';
            notif_state = 'Exit';

          }else if(trigger_type=="inrange"){
              notification_msg = algo_name+" at price &nbsp;  "+parseFloat(trigger_price).toFixed(2);
              notification_title = action_type + ' alert';
              notif_state = 'Entry';
          }
        notification_msg = action_type+' '+quantity+' shares of '+symbol+' at &nbsp;  '+parseFloat(trigger_price).toFixed(2);
        dt = moment.unix(trigger_time);
        notification_time = dt.format('h:mm:ss a');
        notification_tag = notification_title.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
      
    }
    if(quantity && product && symbol && segment && algo_uuid && algo_name && transaction_type && deployment_uuid && notification_msg && notification_title && notification_time && notification_tag && notification_uuid && order_type){

        if(variety=='BO' && tp!=null && sl!=null && product=='MIS' && segment!='MCX'){
          if (variety=='BO' && notif_state!=null){
            if(notif_state=='Exit'){
              show_snackbar(null,'Exit BO from order book');
              if(window.location.href.indexOf('/orderbook/')!=-1){

              }
              else{
                window.location='/orderbook/?platform=all&variety=BO';
                return;
              }
            }
          }
        }

        $('.order_log_popup').fadeOut();$('body').removeClass('body_scroll');

        $('.force_stop_popup, .exit_position').show();
        $('.force_stop_popup').addClass('take_position_popup');
        $('.stop_heading').hide();
        $('.stop_sub_heading').hide();
        $('.algo_stopped').hide()
        $('.back').hide();
        $('.exit_position_section').attr('style','border-top: 0px solid #e2e2e2;')
        exit_window = $('.exit_window');
        exit_window.find('.exit_header').removeClass('exit_header_buy');
        exit_window.find('.exit_header').removeClass('exit_header_sell');

        if(transaction_type=='BUY'){
            exit_window.find('.exit_header').addClass('exit_header_buy');
            exit_window.find('.exit_header').html("<p>Buy "+symbol+"&nbsp;x"+quantity+'<br><span>At market on '+segment+'</span></p>');
            x = '<div><div class="radio_options"><div><span class="radio_outer"><span class="radio_inner"></span></span><p>MIS</p></div><div><span id="'+transaction_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">CNC</p></div></div>';
        }
        else if(transaction_type=='SELL'){
            exit_window.find('.exit_header').addClass('exit_header_sell');
            exit_window.find('.exit_header').html("<p>Sell "+symbol+"&nbsp;x"+quantity+'<br><span>At market on '+segment+'</span></p>');
            x = '<div><div class="radio_options"><div><span class="radio_outer"><span class="radio_inner"></span></span><p>MIS</p></div><div><span id="sell_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">CNC</p></div></div>';
        }
        if(product=='MIS'){
            if(segment=='NFO-FUT'){
                x = '<div><div class="radio_options"><div><span id="'+transaction_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MIS</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>NRML</p></div></div>';
            }
            else{
                x = '<div><div class="radio_options"><div><span id="'+transaction_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MIS</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>CNC</p></div></div>';
            }
        }
        else if(product=='NRML'){
            x = '<div><div class="radio_options"><div><span class="radio_outer"><span class="radio_inner"></span></span><p>MIS</p></div><div><span id="'+transaction_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">NRML</p></div></div>'
        }

        if(order_type=='LIMIT' && (variety!='BO' || segment=='MCX')){
          order_price_html = parseFloat(price);
          order_price_readonly = '';
          bg_stripe = '';
          additional_options = '<div class="notif_left_more_options"></div>';
          cursor_style = 'style="cursor: text !important;"';
          order_type_html = '<div class="exit_qty"><p>Price</p><input '+cursor_style+' class="'+bg_stripe+'" type="number" name="" id="position_price" value="'+order_price_html+'"></div></div></div><div><div class="radio_options"><div onclick=switch_order_type_orders(event,"MARKET",\''+deployment_uuid+'\')><span class="radio_outer"><span class="radio_inner"></span></span><p>MARKET</p></div><div onclick=switch_order_type_orders(event,"LIMIT",\''+deployment_uuid+'\')><span id="'+transaction_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">LIMIT</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL-M</p></div></div><div class="notif_right"><div class="exit_price"><p>Trigger price</p><input type="number" class="bg-stripe" id="position_trigger_price" name="" value="0" readonly></div>';
          exit_window.find('.exit_body').html('<div class="exit_options">'+x+'<div class="notif_left"><div class="exit_qty"><p>Qty.</p><input type="number" id="position_qty" name="" value="'+Math.abs(quantity)+'" readonly></div>'+order_type_html+'<div class="exit_price"><p>Disclosed qty.</p><input type="number" class="bg-stripe" id="position_disclosed_qty" name="" value="0" readonly></div></div></div></div>'+additional_options+'<div class="bottom_more_options"><div class="reg_bo"><div class="radio_options"><div onclick=switch_order_type_orders(event,"REGULAR",\''+deployment_uuid+'\')><span class="radio_outer"><span class="radio_inner"></span></span><p>Regular</p></div><div onclick=switch_order_type_orders(event,"BO",\''+deployment_uuid+'\')><span  id="'+transaction_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">BO</p></div></div></div><div id="notif_actions"><button id="'+transaction_type.toLowerCase()+'" onclick="place_order_take_action(event,\''+notification_uuid+'\',\''+deployment_uuid+'\',\''+algo_uuid+'\',\''+segment+'\',\''+symbol+'\',\''+Math.abs(quantity)+'\',\''+order_type+'\',\''+transaction_type.toUpperCase()+'\',\''+product+'\',\''+validity+'\',\''+algo_name.toString()+'\',\''+1+'\',\''+price+'\',\''+variety+'\',\''+notif_state+'\');">'+to_title(transaction_type)+'</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div></div>');
          exit_window.find('.exit_body').attr('id','exit_body'+deployment_uuid);
        }
        else if(variety=='BO' && tp!=null && sl!=null && product=='MIS' && segment!='MCX'){
          // if (variety=='BO' && notif_state!=null){
          //   if(notif_state=='Exit'){
          //     show_snackbar(null,'Exit BO from order book');
          //     if(window.location.href.indexOf('/orderbook/')!=-1){

          //     }
          //     else{
          //       window.location='/orderbook/?platform=all&variety=BO';
          //       return;
          //     }
          //   }
          // }
          order_price_html = parseFloat(price);
          order_price_readonly = '';
          bg_stripe = '';
          order_type= 'LIMIT';
          cursor_style = 'style="cursor: text !important;"';
          if(tpsl_type!='pct')
          {
            squareoff_val = parseFloat(target_profit);
            stoploss_val = parseFloat(stop_loss);
            trailing_stoploss = '0';
          }
          else{
            squareoff_val = parseFloat(parseFloat(price)*parseFloat(target_profit)/100).toFixed(2);
            stoploss_val = parseFloat(parseFloat(price)*parseFloat(stop_loss)/100).toFixed(2);
            trailing_stoploss = '0';
          }
          additional_options = '<div class="notif_left_more_options"><div class="notif_qty"><p>Stoploss</p><input '+cursor_style+' type="number" id="stoploss" name="" value="'+stoploss_val+'" '+order_price_readonly+'></div><div class="notif_qty"><p>Target</p><input '+cursor_style+' type="number" name="" id="squareoff" value="'+squareoff_val+'" '+order_price_readonly+'></div><div class="notif_qty"><p>Trailing stoploss</p><input '+cursor_style+' type="number" name="" id="trailing_stoploss" value="0" '+order_price_readonly+'></div></div>';
          order_type_html = '<div class="exit_qty"><p>Price</p><input '+cursor_style+' class="'+bg_stripe+'" type="number" name="" id="position_price" value="'+order_price_html+'"></div></div></div><div><div class="radio_options"><div onclick=switch_order_type_orders(event,"MARKET",\''+deployment_uuid+'\')><span class="radio_outer"><span class="radio_inner"></span></span><p>MARKET</p></div><div onclick=switch_order_type_orders(event,"LIMIT",\''+deployment_uuid+'\')><span id="'+transaction_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">LIMIT</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL-M</p></div></div><div class="notif_right"><div class="exit_price"><p>Trigger price</p><input type="number" class="bg-stripe" id="position_trigger_price" name="" value="0" readonly></div>';
          exit_window.find('.exit_body').html('<div class="exit_options">'+x+'<div class="notif_left"><div class="exit_qty"><p>Qty.</p><input type="number" id="position_qty" name="" value="'+Math.abs(quantity)+'" readonly></div>'+order_type_html+'<div class="exit_price"><p>Disclosed qty.</p><input type="number" class="bg-stripe" id="position_disclosed_qty" name="" value="0" readonly></div></div></div></div>'+additional_options+'<div class="bottom_more_options"><div class="reg_bo"><div class="radio_options"><div onclick=switch_order_type_orders(event,"REGULAR",\''+deployment_uuid+'\')><span class="radio_outer"><span class="radio_inner"></span></span><p>Regular</p></div><div onclick=switch_order_type_orders(event,"BO",\''+deployment_uuid+'\')><span class="radio_outer" id="'+transaction_type.toLowerCase()+'_radio_option"><span class="radio_inner"></span></span><p id="option_selected">BO</p></div></div></div><div id="notif_actions"><button id="'+transaction_type.toLowerCase()+'" onclick="place_order_take_action(event,\''+notification_uuid+'\',\''+deployment_uuid+'\',\''+algo_uuid+'\',\''+segment+'\',\''+symbol+'\',\''+Math.abs(quantity)+'\',\''+order_type+'\',\''+transaction_type.toUpperCase()+'\',\''+product+'\',\''+validity+'\',\''+algo_name.toString()+'\',\''+1+'\',\''+price+'\',\''+variety+'\',\''+notif_state+'\');">'+to_title(transaction_type)+'</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div></div>');
          exit_window.find('.exit_body').attr('id','exit_body'+deployment_uuid);
        }
        else{
          // additional_options = '<div class="notif_left_more_options"><div class="notif_qty"><p>Stoploss</p><input type="number" id="position_stoploss" name="" value="1" readonly=""></div><div class="notif_qty"><p>Target</p><input type="number" name="" id="position_target" value="0" readonly=""></div><div class="notif_qty"><p>Trailing stoploss</p><input type="number" name="" id="position_trailing_stoploss" value="0" readonly=""></div></div>';
          additional_options = '<div class="notif_left_more_options"></div>';
          order_type_html = '<div class="exit_qty"><p>Price</p><input type="number" name="" id="position_price" value="'+0+'" class="bg-stripe" readonly></div></div></div><div><div class="radio_options"><div onclick=switch_order_type_orders(event,"MARKET",\''+deployment_uuid+'\')><span id="'+transaction_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MARKET</p></div><div onclick=switch_order_type_orders(event,"LIMIT",\''+deployment_uuid+'\')><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL-M</p></div></div><div class="notif_right"><div class="exit_price"><p>Trigger price</p><input type="number" class="bg-stripe" id="position_trigger_price" name="" value="0" readonly></div>';
          exit_window.find('.exit_body').html('<div class="exit_options">'+x+'<div class="notif_left"><div class="exit_qty"><p>Qty.</p><input type="number" id="position_qty" name="" value="'+Math.abs(quantity)+'" readonly></div>'+order_type_html+'<div class="exit_price"><p>Disclosed qty.</p><input type="number" class="bg-stripe" id="position_disclosed_qty" name="" value="0" readonly></div></div></div></div>'+additional_options+'<div class="bottom_more_options"><div class="reg_bo"><div class="radio_options"><div onclick=switch_order_type_orders(event,"REGULAR",\''+deployment_uuid+'\')><span id="'+transaction_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">Regular</p></div><div onclick=switch_order_type_orders(event,"BO",\''+deployment_uuid+'\')><span class="radio_outer"><span class="radio_inner"></span></span><p>BO</p></div></div></div><div id="notif_actions"><button id="'+transaction_type.toLowerCase()+'" onclick="place_order_take_action(event,\''+notification_uuid+'\',\''+deployment_uuid+'\',\''+algo_uuid+'\',\''+segment+'\',\''+symbol+'\',\''+Math.abs(quantity)+'\',\''+order_type+'\',\''+transaction_type.toUpperCase()+'\',\''+product+'\',\''+validity+'\',\''+algo_name.toString()+'\',\''+1+'\',\''+price+'\',\''+variety+'\',\''+notif_state+'\');">'+to_title(transaction_type)+'</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div></div>');
          exit_window.find('.exit_body').attr('id','exit_body'+deployment_uuid);
        }

        take_action_order_window_params[deployment_uuid]=[transaction_type,symbol,segment,order_type,quantity,product,price,trigger_price,disclosed_qty,validity,variety,tag,notif_state,algo_name,algo_uuid,deployment_uuid,notification_uuid,notification_time,onclick_confirm,target_profit,stop_loss,tpsl_type,notification_data];

    }
}

function place_order_take_action(event,notification_uuid,deployment_uuid,algo_uuid,seg,sym,quantity,order_type,transaction_type,product,validity,algo_name,dt=0,trigger_price=0.0,variety='REGULAR',notif_state=''){
    var me = $(event.target);

    if ( $(me).data('requestRunning') ) {
        return;
    }
    $(me).data('requestRunning', true);
    $(me).attr('style','cursor:no-drop');

    var exch = seg;
    [exch,t]=seg.split('-');
    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    var params = {
        'notification_uuid':notification_uuid,
        'deployment_uuid':deployment_uuid,
        'algo_uuid':algo_uuid,
        'exch':exch,
        'seg':seg,
        'sym':sym,
        'order_type':order_type,
        'transaction_type':transaction_type,
        'quantity':quantity,
        'product':product,
        'validity':validity,
        'algo_name':algo_name,
        'trigger_price':trigger_price,
        'notif_state':notif_state,
        'csrfmiddlewaretoken':csrfmiddlewaretoken
    }

    if(order_type=='LIMIT'){
      price=$('#exit_body'+deployment_uuid+' '+'#position_price').val();
      params['price']=price;
      params['order_type']=order_type;
    }
    if(order_type=='LIMIT' && variety=='BO' && product=='MIS' && seg!='MCX'){
      squareoff=$('#exit_body'+deployment_uuid+' '+'#squareoff').val();
      stoploss=$('#exit_body'+deployment_uuid+' '+'#stoploss').val();
      trailing_stoploss=$('#exit_body'+deployment_uuid+' '+'#trailing_stoploss').val();
      params['variety']=variety;
      params['squareoff']=squareoff;
      params['stoploss']=stoploss;
      params['trailing_stoploss']=trailing_stoploss;

    }

    var req_url = /place_order/;
    if(order_type=='SL-M'||order_type=='SL'){
      req_url = /place_order_discipline/;
    }
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": req_url,
      "method": "POST",
      "headers": {
      },
      "data":params,
      "timeout": 10000,//40 sec timeout
    }
    if(dt>60000*5){
      notificationsDict['used'][notification_uuid]=1;
      $(me).closest('.notif_window').remove();
      show_snackbar(null,'This notification is expired');
      return;
    }
    $.ajax(settings).done(function (msg){
        if(msg.status=='used')
        {
          notificationsDict['used'][notification_uuid]=1;
          $(me).closest('.notif_window').remove();
          show_snackbar(null,'This notification is already used!','success');
        }
        else if(msg.status=='success')
        {
          if(msg['error-type']!= undefined){
            show_snackbar(null,msg['error-type']);
            notificationsDict['used'][notification_uuid]=1;
            $(me).closest('.notif_window').remove();
            mark_notification_used(notification_uuid);
          }
          else{
            console.log(msg.status);
            $('.exit_position, .stop_options').hide();$('.algo_stopped').show();
            notificationsDict['used'][notification_uuid]=1;
            $(me).closest('.notif_window').remove();
            show_snackbar(null,'Order sent to exchange','success');
            // setTimeout(function(){ 
            //   // window.location = '/dashboard/';
            //   }, 2000);
            // TODO hide the notification or delete it
            refresh_order_log();
            mark_notification_used(notification_uuid);
          }

            try{
              $(".close_popup").parents(".body").find(".force_stop_popup").fadeOut();
            }catch(e){
              
            }
        }else{
          show_snackbar(null,'Order not placed, please try again.');
          $('.login_required_popup').show();
        }
    }).fail(function(msg){
        // alert('Error, please try again');
        show_snackbar(null,'Connection error, please try again');
    }).complete(function(){
            $(me).data('requestRunning', false);
            $(me).removeAttr('style');
            refresh_notification();
    });
}

function update_take_action(e,notification_data) {
    console.log(notification_data, 'notification_data');
    // if((e.target.parentElement.className=='action_buttons'||e.target.parentElement.className=='menu_dots') && (e.target.parentElement.className!="take_action" && e.target.className!="take_action"))
    //   {
    //     e.stopPropagation();
    //     return
    //   }
    notif = notification_data;
    var quantity = null;
    var product = null;
    var symbol = null;
    var segment = null;
    var algo_uuid = null;
    var algo_name = null;
    var transaction_type = null;
    var deployment_uuid = null;
    var notification_uuid = null;
    var notification_msg = null;
    var notification_title = null;
    var notification_time = null;
    var dt = null;
    var notification_tag = null;
    var price = 0;
    if(notif['notification-type'] == "order-notification"){
        dt = moment(notif.notification_time)
        notification_time = dt.format('h:mm:ss a');
        notification_title = notif.action_type + ' alert';
        notification_msg = notif.action_type+' '+notif.quantity+' shares of '+notif.symbol+' at &nbsp;&#8377;'+parseFloat(notif.trigger_price).toFixed(2);
        notification_tag = notification_title.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
        quantity = parseInt(notif['quantity']);
        product = notif['product'];
        symbol = notif['sym'];
        segment = notif['seg'];
        algo_uuid = notif['algo_uuid'];
        algo_name = notif['algo_name'];
        transaction_type = notif['action_type'];
        deployment_uuid = notif['deployment_uuid'];
        notification_uuid = notif['notification_uuid']
        price = parseFloat(notif.trigger_price);
        order_type = notif['order_type'];
        variety = notif['variety'];
        target_profit = notif['target_profit'];
        stop_loss = notif['stop_loss'];
        tpsl_type = notif['tpsl_type'];
        notification_tag = notification_title.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
        tag = '';
        validity = 'DAY';
        disclosed_qty = 0;
        onclick_confirm = 'place_order_take_action';
        notif_state = 'Entry';

        if(notif['sender']!='lambda'){
              notif_state = 'Exit';
        }

        if(order_type==undefined)
          order_type = 'MARKET';
        
        if(variety=='BO' && tp!=null && sl!=null && product=='MIS' && segment!='MCX'){
          order_type = 'LIMIT';
        }

        notification_tag = notification_title.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
    }
    if(notif['price_trigger-notification']!=undefined){
        tpsl_key=notif['price_trigger-notification'];
        trigger_time = notif['trigger_time'];
        trigger_price = notif['trigger_price'];
        trigger_type = notif['type'];
        tpsl_array = tpsl_key.split(':');
        deployment_uuid = tpsl_array[1];
        token = tpsl_array[3];
        algo_name = tpsl_array[8];
        transaction_type = tpsl_array[9];
        action_type = transaction_type;
        quantity = parseInt(tpsl_array[10]);
        algo_uuid = tpsl_array[11];
        product = tpsl_array[12];
        symbol = tpsl_array[13];
        segment = tpsl_array[14];
        notification_uuid = notif['notification_uuid'];

        price = trigger_price;
        order_type = notif['order_type'];
        variety = notif['variety'];
        target_profit = notif['target_profit'];
        stop_loss = notif['stop_loss'];
        tpsl_type = notif['tpsl_type'];
        tag = '';
        validity = 'DAY';
        disclosed_qty = 0;
        onclick_confirm = 'place_order_take_action';

        if(order_type==undefined)
          order_type = 'MARKET';
        if(variety=='BO' && tp!=null && sl!=null && product=='MIS' && segment!='MCX'){
          order_type = 'LIMIT';
        }
        if(trigger_type=="take-profit"){
        notification_msg = "Take profit at &nbsp;&#8377; "+parseFloat(trigger_price).toFixed(2);
        notification_title = 'Target profit' + ' alert';
        notif_state = 'Exit';
          }
          else if(trigger_type=="stop-loss"){
            notification_msg = "Stop loss at &nbsp;&#8377; "+parseFloat(trigger_price).toFixed(2);
            notification_title = 'Stop loss' + ' alert';
            notif_state = 'Exit';

          }else if(trigger_type=="inrange"){
              notification_msg = algo_name+" at price &nbsp;&#8377; "+parseFloat(trigger_price).toFixed(2);
              notification_title = action_type + ' alert';
              notif_state = 'Entry';
          }
        notification_msg = action_type+' '+quantity+' shares of '+symbol+' at &nbsp;&#8377; '+parseFloat(trigger_price).toFixed(2);
        dt = moment.unix(trigger_time);
        notification_time = dt.format('h:mm:ss a');
        notification_tag = notification_title.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
      
    }
    if(quantity && product && symbol && segment && algo_uuid && algo_name && transaction_type && deployment_uuid && notification_msg && notification_title && notification_time && notification_tag && notification_uuid && order_type){
        $('.order_log_popup').fadeOut();$('body').removeClass('body_scroll');

        $('.force_stop_popup, .exit_position').show();
        $('.force_stop_popup').addClass('take_position_popup');
        $('.stop_heading').hide();
        $('.stop_sub_heading').hide();
        $('.algo_stopped').hide()
        $('.back').hide();
        $('.exit_position_section').attr('style','border-top: 0px solid #e2e2e2;')
        exit_window = $('.exit_window');
        exit_window.find('.exit_header').removeClass('exit_header_buy');
        exit_window.find('.exit_header').removeClass('exit_header_sell');

        if(transaction_type=='BUY'){
            exit_window.find('.exit_header').addClass('exit_header_buy');
            exit_window.find('.exit_header').html("<p>Buy "+symbol+"&nbsp;x"+quantity+'<br><span>At market on '+segment+'</span></p>');
            x = '<div><div class="radio_options"><div><span class="radio_outer"><span class="radio_inner"></span></span><p>MIS</p></div><div><span id="'+transaction_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">CNC</p></div></div>';
        }
        else if(transaction_type=='SELL'){
            exit_window.find('.exit_header').addClass('exit_header_sell');
            exit_window.find('.exit_header').html("<p>Sell "+symbol+"&nbsp;x"+quantity+'<br><span>At market on '+segment+'</span></p>');
            x = '<div><div class="radio_options"><div><span class="radio_outer"><span class="radio_inner"></span></span><p>MIS</p></div><div><span id="sell_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">CNC</p></div></div>';
        }
        if(product=='MIS'){
            if(segment=='NFO-FUT'){
                x = '<div><div class="radio_options"><div><span id="'+transaction_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MIS</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>NRML</p></div></div>';
            }
            else{
                x = '<div><div class="radio_options"><div><span id="'+transaction_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MIS</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>CNC</p></div></div>';
            }
        }
        else if(product=='NRML'){
            x = '<div><div class="radio_options"><div><span class="radio_outer"><span class="radio_inner"></span></span><p>MIS</p></div><div><span id="'+transaction_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">NRML</p></div></div>'
        }

        if(order_type=='LIMIT' && (variety!='BO' || segment=='MCX')){
          order_price_html = parseFloat(price);
          order_price_readonly = '';
          bg_stripe = '';
          cursor_style = 'style="cursor: text !important;"';
          additional_options = '<div class="notif_left_more_options"></div>';
          order_type_html = '<div class="exit_qty"><p>Price</p><input '+cursor_style+' class="'+bg_stripe+'" type="number" name="" id="position_price" value="'+order_price_html+'"></div></div></div><div><div class="radio_options"><div onclick=switch_order_type_orders(event,"MARKET",\''+deployment_uuid+'\')><span class="radio_outer"><span class="radio_inner"></span></span><p>MARKET</p></div><div onclick=switch_order_type_orders(event,"LIMIT",\''+deployment_uuid+'\')><span id="'+transaction_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">LIMIT</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL-M</p></div></div><div class="notif_right"><div class="exit_price"><p>Trigger price</p><input type="number" class="bg-stripe" id="position_trigger_price" name="" value="0" readonly></div>';
          exit_window.find('.exit_body').html('<div class="exit_options">'+x+'<div class="notif_left"><div class="exit_qty"><p>Qty.</p><input type="number" id="position_qty" name="" value="'+Math.abs(quantity)+'" readonly></div>'+order_type_html+'<div class="exit_price"><p>Disclosed qty.</p><input type="number" class="bg-stripe" id="position_disclosed_qty" name="" value="0" readonly></div></div></div></div>'+additional_options+'<div class="bottom_more_options"><div class="reg_bo"><div class="radio_options"><div onclick=switch_order_type_orders(event,"REGULAR",\''+deployment_uuid+'\')><span id="'+transaction_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">Regular</p></div><div onclick=switch_order_type_orders(event,"BO",\''+deployment_uuid+'\')><span class="radio_outer"><span class="radio_inner"></span></span><p>BO</p></div></div></div><div id="notif_actions"><button id="'+transaction_type.toLowerCase()+'" onclick="place_order_take_action(event,\''+notification_uuid+'\',\''+deployment_uuid+'\',\''+algo_uuid+'\',\''+segment+'\',\''+symbol+'\',\''+Math.abs(quantity)+'\',\''+order_type+'\',\''+transaction_type.toUpperCase()+'\',\''+product+'\',\''+validity+'\',\''+algo_name.toString()+'\',\''+1+'\',\''+price+'\',\''+variety+'\',\''+notif_state+'\');">'+to_title(transaction_type)+'</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div></div>');
          exit_window.find('.exit_body').attr('id','exit_body'+deployment_uuid);
        }
        else if(variety=='BO' && tp!=null && sl!=null && product=='MIS' && segment!='MCX'){
          order_price_html = parseFloat(price);
          order_price_readonly = '';
          bg_stripe = '';
          order_type= 'LIMIT';
          cursor_style = 'style="cursor: text !important;"';
          if(tpsl_type!='pct')
          {
            squareoff_val = parseFloat(target_profit);
            stoploss_val = parseFloat(stop_loss);
            trailing_stoploss = '0';
          }
          else{
            squareoff_val = parseFloat(parseFloat(price)*parseFloat(target_profit)/100).toFixed(2);
            stoploss_val = parseFloat(parseFloat(price)*parseFloat(stop_loss)/100).toFixed(2);
            trailing_stoploss = '0';
          }
          additional_options = '<div class="notif_left_more_options"><div class="notif_qty"><p>Stoploss</p><input '+cursor_style+' type="number" id="stoploss" name="" value="'+stoploss_val+'" '+order_price_readonly+'></div><div class="notif_qty"><p>Target</p><input '+cursor_style+' type="number" name="" id="squareoff" value="'+squareoff_val+'" '+order_price_readonly+'></div><div class="notif_qty"><p>Trailing stoploss</p><input '+cursor_style+' type="number" name="" id="trailing_stoploss" value="0" '+order_price_readonly+'></div></div>';
          order_type_html = '<div class="exit_qty"><p>Price</p><input class="'+bg_stripe+'" type="number" name="" id="position_price" value="'+order_price_html+'"></div></div></div><div><div class="radio_options"><div onclick=switch_order_type_orders(event,"MARKET",\''+deployment_uuid+'\')><span class="radio_outer"><span class="radio_inner"></span></span><p>MARKET</p></div><div onclick=switch_order_type_orders(event,"LIMIT",\''+deployment_uuid+'\')><span id="'+transaction_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">LIMIT</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL-M</p></div></div><div class="notif_right"><div class="exit_price"><p>Trigger price</p><input type="number" class="bg-stripe" id="position_trigger_price" name="" value="0" readonly></div>';
          exit_window.find('.exit_body').html('<div class="exit_options">'+x+'<div class="notif_left"><div class="exit_qty"><p>Qty.</p><input type="number" id="position_qty" name="" value="'+Math.abs(quantity)+'" readonly></div>'+order_type_html+'<div class="exit_price"><p>Disclosed qty.</p><input type="number" class="bg-stripe" id="position_disclosed_qty" name="" value="0" readonly></div></div></div></div>'+additional_options+'<div class="bottom_more_options"><div class="reg_bo"><div class="radio_options"><div onclick=switch_order_type_orders(event,"REGULAR",\''+deployment_uuid+'\')><span class="radio_outer"><span class="radio_inner"></span></span><p>Regular</p></div><div onclick=switch_order_type_orders(event,"BO",\''+deployment_uuid+'\')><span class="radio_outer" id="'+transaction_type.toLowerCase()+'_radio_option"><span class="radio_inner"></span></span><p id="option_selected">BO</p></div></div></div><div id="notif_actions"><button id="'+transaction_type.toLowerCase()+'" onclick="place_order_take_action(event,\''+notification_uuid+'\',\''+deployment_uuid+'\',\''+algo_uuid+'\',\''+segment+'\',\''+symbol+'\',\''+Math.abs(quantity)+'\',\''+order_type+'\',\''+transaction_type.toUpperCase()+'\',\''+product+'\',\''+validity+'\',\''+algo_name.toString()+'\',\''+1+'\',\''+price+'\',\''+variety+'\',\''+notif_state+'\');">'+to_title(transaction_type)+'</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div></div>');
          exit_window.find('.exit_body').attr('id','exit_body'+deployment_uuid);
        }
        else{
          // additional_options = '<div class="notif_left_more_options"><div class="notif_qty"><p>Stoploss</p><input type="number" id="position_stoploss" name="" value="1" readonly=""></div><div class="notif_qty"><p>Target</p><input type="number" name="" id="position_target" value="0" readonly=""></div><div class="notif_qty"><p>Trailing stoploss</p><input type="number" name="" id="position_trailing_stoploss" value="0" readonly=""></div></div>';
          additional_options = '<div class="notif_left_more_options"></div>';
          order_type_html = '<div class="exit_qty"><p>Price</p><input type="number" name="" id="position_price" value="'+0+'" class="bg-stripe" readonly></div></div></div><div><div class="radio_options"><div onclick=switch_order_type_orders(event,"MARKET",\''+deployment_uuid+'\')><span id="'+transaction_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MARKET</p></div><div onclick=switch_order_type_orders(event,"LIMIT",\''+deployment_uuid+'\')><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL-M</p></div></div><div class="notif_right"><div class="exit_price"><p>Trigger price</p><input type="number" class="bg-stripe" id="position_trigger_price" name="" value="0" readonly></div>';
          exit_window.find('.exit_body').html('<div class="exit_options">'+x+'<div class="notif_left"><div class="exit_qty"><p>Qty.</p><input type="number" id="position_qty" name="" value="'+Math.abs(quantity)+'" readonly></div>'+order_type_html+'<div class="exit_price"><p>Disclosed qty.</p><input type="number" class="bg-stripe" id="position_disclosed_qty" name="" value="0" readonly></div></div></div></div>'+additional_options+'<div class="bottom_more_options"><div class="reg_bo"><div class="radio_options"><div onclick=switch_order_type_orders(event,"REGULAR",\''+deployment_uuid+'\')><span id="'+transaction_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">Regular</p></div><div onclick=switch_order_type_orders(event,"BO",\''+deployment_uuid+'\')><span class="radio_outer"><span class="radio_inner"></span></span><p>BO</p></div></div></div><div id="notif_actions"><button id="'+transaction_type.toLowerCase()+'" onclick="place_order_take_action(event,\''+notification_uuid+'\',\''+deployment_uuid+'\',\''+algo_uuid+'\',\''+segment+'\',\''+symbol+'\',\''+Math.abs(quantity)+'\',\''+order_type+'\',\''+transaction_type.toUpperCase()+'\',\''+product+'\',\''+validity+'\',\''+algo_name.toString()+'\',\''+1+'\',\''+price+'\',\''+variety+'\',\''+notif_state+'\');">'+to_title(transaction_type)+'</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div></div>');
          exit_window.find('.exit_body').attr('id','exit_body'+deployment_uuid);
        }

        take_action_order_window_params[deployment_uuid]=[transaction_type,symbol,segment,order_type,quantity,product,price,trigger_price,disclosed_qty,validity,variety,tag,notif_state,algo_name,algo_uuid,deployment_uuid,notification_uuid,notification_time,onclick_confirm,target_profit,stop_loss,tpsl_type,notification_data];

    }
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

function deploy_algorithm_multi_popup(event,t,algo_name,entry,exit,position_type,quantity,take_profit,stop_loss,interval,algo_uuid,chart_type,trading_start_time,trading_stop_time,seg_sym){

    var deploy_instrument_list = [1];

    // $($($(th[0].parentElement.parentElement).find('div[class^="token__"]')[0]).find('.deploy_checkbox input')[0]).data("deploy-params_symbol");

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
    if(msg.status=='success')
      {
        backtest_remaining = Math.max(msg['backtest'],0);
        deployments_remaining= Math.max(msg['deployments_remaining'],0)
        if(deployments_remaining<deploy_instrument_list.length){
            show_snackbar(null,'You are trying to deploy more than the remaining deployments');
            return;
        }
        $('body').addClass('body_scroll');
        $('.deploy_summary_heading p').html(algo_name);
        // $('#trading_terms_checkbox:checked').removeAttr('checked');
        if (position_type == 1 || position_type =='BUY'){
            var position_type_entry = 'BUY'
            var position_type_exit = 'SELL'
        }
        else{
            var position_type_entry = 'SELL'
            var position_type_exit = 'BUY'
        }
        if(chart_type.toLowerCase()=='heikinAshi'){
          chart_type = 'heikin-ashi';
        }
        var c_interval_str = '';
        switch(interval){
            case 'min':$('#interval_condition_summary').html('1 Minute, '+chart_type+' chart</br>Enter trade between : '+trading_start_time+' to '+trading_stop_time);
                c_interval_str = '1 minute interval using '+chart_type.toLowerCase()+' chart.</br>'; break;
            case '3min':$('#interval_condition_summary').html('3 Minute, '+chart_type+' chart</br>Enter trade between : '+trading_start_time+' to '+trading_stop_time);
                c_interval_str = '3 minute interval using '+chart_type.toLowerCase()+' chart.</br>'; break;
            case '5min':$('#interval_condition_summary').html('5 Minute, '+chart_type+' chart</br>Enter trade between : '+trading_start_time+' to '+trading_stop_time);
                c_interval_str = '5 minute interval using '+chart_type.toLowerCase()+' chart.</br>'; break;
            case '10min':$('#interval_condition_summary').html('10 Minute, '+chart_type+' chart</br>Enter trade between : '+trading_start_time+' to '+trading_stop_time);
                c_interval_str = '10 minute interval using '+chart_type.toLowerCase()+' chart.</br>'; break;
            case '15min':$('#interval_condition_summary').html('15 Minute, '+chart_type+' chart</br>Enter trade between : '+trading_start_time+' to '+trading_stop_time);
                c_interval_str = '15 minute interval using '+chart_type.toLowerCase()+' chart.</br>'; break;
            case '30min':$('#interval_condition_summary').html('30 Minute, '+chart_type+' chart</br>Enter trade between : '+trading_start_time+' to '+trading_stop_time);
                c_interval_str = '30 minute interval using '+chart_type.toLowerCase()+' chart.</br>'; break;
            case 'hour':$('#interval_condition_summary').html('1 Hour, '+chart_type+' chart</br>Enter trade between : '+trading_start_time+' to '+trading_stop_time);
                c_interval_str = '1 hour interval using '+chart_type.toLowerCase()+' chart.</br>'; break;
            case 'day':$('#interval_condition_summary').html('1 Day, '+chart_type+' chart</br>Enter trade between : '+trading_start_time+' to '+trading_stop_time);
                c_interval_str = '1 day interval using '+chart_type.toLowerCase()+' chart.</br>'; break;
        }
        $('#interval_condition_summary').hide();
        [segment,symbol] = seg_sym.split('_');
            $('#entry_condition_summary').html(position_type_entry+' '+quantity+' shares of '+symbol+' when '+entry+' at '+c_interval_str+'Enter trade between '+trading_start_time+' to '+trading_stop_time);
            if(exit!='')
                $('#exit_condition_summary').html(position_type_exit+' '+quantity+' shares when '+exit+' or '+' at Stop loss of '+stop_loss+'% or Take profit of '+take_profit+'%'+' at '+c_interval_str);
            else{
                $('#exit_condition_summary').html(position_type_exit+' '+quantity+' shares of '+symbol+' at Stop loss of '+stop_loss+'% or Take profit of '+take_profit+'%'+' at '+c_interval_str);
            }
            $('.deploy_heading p').text("Deploy");

        // $('.popup').show();
        if ($('#trading_terms_checkbox:checked').is(':checked') && (first_time_deploy == "false")){
            $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
            $('.deploy_confirm').attr('onclick','deploy_algorithm_multi_r("'+algo_uuid+'",\''+seg_sym+'\',"'+position_type+'","'+quantity+'","'+take_profit+'","'+stop_loss+'","'+interval+'");');
            // algo_name,entry,exit,position_type,quantity,take_profit,stop_loss,interval,algo_uuid,sym,seg
        }
        else{
            $('.deploy_confirm').css({'background-color':'#8b9096 !important','cursor': 'no-drop'});
            $('.deploy_confirm').unbind('click');
            $('#trading_terms_checkbox:checked').removeAttr('checked');
        }
        // $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
        // $('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'");');
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
                        $('.deploy_confirm').attr('onclick','deploy_algorithm_multi_r("'+algo_uuid+'",\''+seg_sym+'\',"'+position_type+'","'+quantity+'","'+take_profit+'","'+stop_loss+'","'+interval+'");');
                        $('#trading_terms_checkbox:checked').removeAttr('checked');
                        close_popup();
                        return;
                    }else{
                        $('.popup').show();
                        
                        try{
                            ga('send', {hitType: 'event', eventCategory: 'Deploy initiated', eventAction: 'Deploy initiated', eventLabel: 'Algos page', eventValue: deploy_instrument_list.length});
                        }catch(e){
                  
                        }
                    }
                }
            }
        });
        $('#trading_terms_checkbox').change(function(){
            if($('#trading_terms_checkbox:checked').is(':checked')){
                $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
                $('.deploy_confirm').attr('onclick','deploy_algorithm_multi_r("'+algo_uuid+'",\''+seg_sym+'\',"'+position_type+'","'+quantity+'","'+take_profit+'","'+stop_loss+'","'+interval+'");');
            }else{
                $('.deploy_confirm').css({'background-color':'#8b9096 !important','cursor': 'no-drop'});
                $('.deploy_confirm').removeAttr('onclick');
            }

        });

      }
    }).fail(function(){
      show_snackbar(null,'Unable to fetch usage,kindly check your network')
    });
}

function deploy_algorithm_multi_r(deployment_uuid,seg_sym,position_type,quantity,take_profit,stop_loss,interval){
    params = {
        'deployment_uuid':deployment_uuid,
        'seg_sym':seg_sym
    };

    // take_profit = $('#ip_takeprofit').val();
    // stop_loss = $('#ip_stoploss').val();
    // quantity = $('#ip_quantity').val();
    // interval = $('#ip_interval').val();
    live_period_mapping = {'Notification Only':30,'Paper trading':30,'Auto trading':30}
    broker = $('#ip_broker').val();
    frequency = $('#ip_frequency').val();
    live_period = live_period_mapping[$('#ip_live_period').val()];
    variety = $('#ip_variety').val();

    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();

    params['take_profit']=take_profit;
    params['stop_loss']=stop_loss;
    params['quantity']=quantity;
    params['interval']=interval;
    params['broker']=broker;
    params['frequency']=parseInt(frequency)-1;
    params['live_period']=live_period;
    params['deployment_type']=$('#ip_live_period').val();
    params['seg_sym']=seg_sym;
    params['variety']=variety;
    if (live_period!=1)
      params['variety']='REGULAR';
    params['csrfmiddlewaretoken']=csrfmiddlewaretoken;
    $( ".loader_parent" ).fadeIn();
    $(".deploy_confirm").html("<img src='/static/imgs/button-loading-rect.gif' id='button_loading'>");
    $.post('/redeploy_algorithm/',params,function(data){
        // $( ".loader_parent" ).fadeOut();
        if(data['status']=='success'){
            window.location = '/order_log';
            try{
                ga('send', {hitType: 'event', eventCategory: 'Deploy confirmed', eventAction: 'Deploy confirmed', eventLabel: 'Algos page', eventValue: JSON.parse(seg_sym_list).length});
            }catch(e){
              
            }
            // var redirect = '/dashboard/';
            // delete params["html_block"];
            // params['algo_uuid']=data['algo_uuid'];
            // $.redirectPost(redirect, params);
        }
        else{
            // handle any error from save algorithm
            $( ".loader_parent" ).fadeOut();
            $(".deploy_confirm").html('<span><img src="/static/imgs/icon-deploy-confirm.png"></span>&nbsp;&nbsp;Confirm');
            $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
            $('.deploy_confirm').attr('onclick','deploy_algorithm_multi_r("'+deployment_uuid+'",\''+seg_sym+'\',"'+position_type+'","'+quantity+'","'+take_profit+'","'+stop_loss+'","'+interval+'");');
            $('#trading_terms_checkbox:checked').removeAttr('checked');
            close_popup();
            if(data['error_msg']!=undefined)
              show_snackbar(null,'Algo for this scrip is already live');       
            else
              show_snackbar(null,'Some error occured, please try again!');       
        }
    }).fail(function(){
        $( ".loader_parent" ).fadeOut();
        $(".deploy_confirm").html('<span><img src="/static/imgs/icon-deploy-confirm.png"></span>&nbsp;&nbsp;Confirm');
        $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
        $('.deploy_confirm').attr('onclick','deploy_algorithm_multi_r("'+deployment_uuid+'",\''+seg_sym+'\',"'+position_type+'","'+quantity+'","'+take_profit+'","'+stop_loss+'","'+interval+'");');
        $('#trading_terms_checkbox:checked').removeAttr('checked');
        close_popup();
        show_snackbar(null,'Some error occured, please try again!');
    });
    $('body').removeClass('body_scroll');
};