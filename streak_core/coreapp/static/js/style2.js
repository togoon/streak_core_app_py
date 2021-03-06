window.onbeforeunload = function(){
  // window.scrollTo(0,0);
}

// // // //
document.addEventListener('contextmenu', event => event.preventDefault());
document.onkeydown = function(e) {
  if(location.host!='127.0.0.1')
  {
    if(e.keyCode == 123) {
      return false;
      }
    if(e.ctrlKey && e.shiftKey && e.keyCode == 'I'.charCodeAt(0)){
      return false;
      }
    if(e.ctrlKey && e.shiftKey && e.keyCode == 'J'.charCodeAt(0)){
      return false;
      }
    if(e.ctrlKey && e.shiftKey && e.keyCode == 'C'.charCodeAt(0)){
      return false;
      }
    if(e.ctrlKey && e.keyCode == 'U'.charCodeAt(0)){
      return false;
      }
  }
}
var element = new Image;
var devtoolsOpen = false;
element.__defineGetter__("id", function() {
    devtoolsOpen = true; // This only executes when devtools is open.
    // console.log('element');
});

function devtoolslog_func(){
  // if(location.pathname!='/')
    // window.location='/logout';
  return '...';
};

setInterval(function() {
    // devtoolsOpen = false;
    if(!devtoolsOpen && location.pathname!='/' && location.host!='127.0.0.1')
    {
      // console.log(element);
      console.log(devtoolslog_func());
    }
    if(devtoolsOpen){
      // alert(devtoolsOpen);
      if(location.pathname!='/' && location.host!='127.0.0.1')
        window.location='/logout';
    }
    // document.getElementById('output').innerHTML += (devtoolsOpen ? "dev tools is open\n" : "dev tools is closed\n");
}, 1000);

(function () {
  'use strict';
  var devtools = {
    open: false,
    orientation: null
  };
  var threshold = 160;
  var emitEvent = function (state, orientation) {
    window.dispatchEvent(new CustomEvent('devtoolschange', {
      detail: {
        open: state,
        orientation: orientation
      }
    }));
  };

  setInterval(function () {
    var widthThreshold = window.outerWidth - window.innerWidth > threshold;
    var heightThreshold = window.outerHeight - window.innerHeight > threshold;
    var orientation = widthThreshold ? 'vertical' : 'horizontal';

    if (!(heightThreshold && widthThreshold) &&
      ((window.Firebug && window.Firebug.chrome && window.Firebug.chrome.isInitialized) || widthThreshold || heightThreshold)) {
      if (!devtools.open || devtools.orientation !== orientation) {
        emitEvent(true, orientation);
      }

      devtools.open = true;
      devtools.orientation = orientation;
    } else {
      if (devtools.open) {
        emitEvent(false, null);
      }

      devtools.open = false;
      devtools.orientation = null;
    }
  }, 500);

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = devtools;
  } else {
    window.devtools = devtools;
  }
})();

// get notified when it's opened/closed or orientation changes
window.addEventListener('devtoolschange', function (e) {
  // console.log('is DevTools open?', e.detail.open);
  // console.log('and DevTools orientation?', e.detail.orientation);
  if(location.pathname!='/' && location.host!='127.0.0.1')
        window.location='/logout';
});
// // // //

var positionsDict = {};
var notificationsDict = {'notifications':[],unread_count: 0,'used':{}};
var notification_audio = new Audio('/static/js/notification_audio.mp3');
var subscription_status = {};
// onDocument load, load notifications
// on notification update notificationsObject
// on notification show, mark notification as read and update in redis
var subscription_clicked = false;
$(document).ready(function(){
  // $(window).scrollTop(0);
  // var v1 = document.getElementById("v1");
  // var v2 = document.getElementById("v2");
  $(document).keydown(function(e){
   if (e.keyCode == 27) 
    { 
      $("body").removeClass("body_scroll");
      $(".close").parents("body").find(".popup").fadeOut();
      $(".close_popup").parents(".body").find(".order_details_popup").fadeOut();
      $(".close_popup").parents(".body").find(".force_stop_popup").fadeOut();
      setTimeout(function(){ 
        $('.force_stop_popup').removeClass('take_position_popup');
        }, 1000);
      $(".close_popup").parents(".body").find(".order_log_popup").fadeOut();
      $(".close_popup").parents(".body").find(".delete_strategy_popup").fadeOut();
      $(".close_popup").parents(".body").find(".exit_all_popup").fadeOut();
      $(".welcome_popup, .subscription_popup, #cancel_subscription_popup").hide();
      $('.my_baskets_popup, .feedback_popup, .advanced_section_popup').fadeOut();
    } 
  });
  $(".popup").click(function(e){
    // alert($(".popup").has(e.target).length);
    // alert($(".popup").is(e.target));
    if(($(".popup").has(e.target).length == 0)&&($(".popup").is(e.target))){
      $("body").removeClass("body_scroll");
      $(".close").parents("body").find(".popup").fadeOut();
    }
  });
  $(".order_details_popup").click(function(e){
    // alert($(".order_details_popup").has(e.target).length);
    // alert($(".order_details_popup").is(e.target));
    if(($(".order_details_popup").has(e.target).length == 0)&&($(".order_details_popup").is(e.target))){
      $("body").removeClass("body_scroll");
      $(".close_popup").parents(".body").find(".order_details_popup").fadeOut();
    }
  });
  $(".force_stop_popup").click(function(e){
    // alert($(".force_stop_popup").has(e.target).length);
    // alert($(".force_stop_popup").is(e.target));
    if(($(".force_stop_popup").has(e.target).length == 0)&&($(".force_stop_popup").is(e.target))){
      $("body").removeClass("body_scroll");
      $(".close_popup").parents(".body").find(".force_stop_popup").fadeOut();
      setTimeout(function(){ 
        $('.force_stop_popup').removeClass('take_position_popup');
        }, 1000);
      // $('.force_stop_popup').removeClass('take_position_popup');
    }
  });
  $("#cancel_subscription_popup").click(function(e){
    // alert($("#cancel_subscription_popup").has(e.target).length);
    // alert($("#cancel_subscription_popup").is(e.target));
    if(($("#cancel_subscription_popup").has(e.target).length == 0)&&($("#cancel_subscription_popup").is(e.target))){
      $("body").removeClass("body_scroll");
      $("#cancel_subscription_popup").fadeOut();
    }
  });
  $(".my_baskets_popup").click(function(e){
    // alert($("#cancel_subscription_popup").has(e.target).length);
    // alert($("#cancel_subscription_popup").is(e.target));
    if(($(".my_baskets_popup").has(e.target).length == 0)&&($(".my_baskets_popup").is(e.target))){
      $("body").removeClass("body_scroll");
      $(".my_baskets_popup").fadeOut();
    }
  });
  $(".feedback_popup").click(function(e){
    if(($(".feedback_popup").has(e.target).length == 0)&&($(".feedback_popup").is(e.target))){
      $("body").removeClass("body_scroll");
      $(".feedback_popup").fadeOut();
    }
  });
  $(".advanced_section_popup").click(function(e){
    if(($(".advanced_section_popup").has(e.target).length == 0)&&($(".advanced_section_popup").is(e.target))){
      $("body").removeClass("body_scroll");
      $(".advanced_section_popup").fadeOut();
    }
  });
  $("#acc_menu, #new_menu, #more_menu, #notification_details, #mobile_acc_menu").hide();
  $(".q").click(function(){
  $(this).parent().find(".a").slideToggle();
  // $(".body").css({"margin-top": "70px"}); 
  });
  $('#view_algo_details').click(function(){
    $('#algo_detail_window').show();
  });
  $('#algo_detail_window').mouseleave(function(){
    $('#algo_detail_window').hide();
  });
  // $(".a").show();
  // Paste this after showing  $(".body").css({"margin-top": "5px"});
  // $("#error_box").hide();
  $("#user_icon").hover(function(){
    $("#more_menu, #notification_details").hide();
    if(window.location.href.indexOf('/mobile_')!=-1||window.location.href.indexOf('/alerts')!=-1){
      $("#notification_details").show();
    }
    $("#acc_menu").show();
  });
  $("#mobile_menu_icon").hover(function(){
    $("#more_menu, #notification_details").hide();
    if(window.location.href.indexOf('/mobile_')!=-1||window.location.href.indexOf('/alerts')!=-1){
      $("#notification_details").show();
    }
    $("#mobile_acc_menu").show();
  });
  $("#more").hover(function(){
    $("#acc_menu, #notification_details, #mobile_acc_menu").hide();
    $("#more_menu").show();
  });
  $("#notifications").hover(function(){
    $("#acc_menu, #more_menu, #mobile_acc_menu").hide();
    if(window.location.href.indexOf('/alerts')==-1){
      $("#notification_details").show();
    }
    // $("#notification_details").show();
    // if($("#notification_details").css('display')!='none')
      // refresh_notification();
  });

  if(window.location.href.indexOf('/alerts')!=-1){
      $("#notification_details").show();
  }

  $("#menu_icon").click(function(){
    $("#new_menu").toggle();
  });
  $("#error_close").click(function(){
    $("#error_box").fadeOut();
    $(".body").css({"margin-top": "70px"}); 
  });
  $("#acc_menu, .menu").mouseleave(function(){
    $("#acc_menu").hide();   
  });
  $("#mobile_acc_menu, .menu").mouseleave(function(){
    $("#mobile_acc_menu").hide();   
  });
  $("#more_menu, .menu").mouseleave(function(){
    $("#more_menu").hide();   
  });
  $(".menu").mouseleave(function(){
    $("#notification_details").hide();
    if(window.location.href.indexOf('/mobile_')!=-1||window.location.href.indexOf('/alerts')!=-1){
      $("#notification_details").show();
    }
  });
  $("#notification_details").mouseleave(function(){
    $("#notification_details").hide();
    if(window.location.href.indexOf('/mobile_')!=-1||window.location.href.indexOf('/alerts')!=-1){
      $("#notification_details").show();
    }
    $('#notif_count').text(0);
    $('#notif_count').hide(); 
    // ajax to mark all notifications as read
    notifications_read();  
  });
  $("#new_menu, .menu").mouseleave(function(){
    $("#new_menu").hide();
  });
  $(".basket").hover(function(){
    $(this).find("button").toggle();
  });
  $(".equities_list img").click(function(){
    $(this).parentsUntil('.equities_list').remove();
  });

  fetch_notifications();
  fetch_billing_status();
  setTimeout(function(){ 
    update_admin();
  }, 20000);


  // subscription
  $('#start_subscription_btn').attr('style','background-color: #989fa7;border: 1px solid #bfc7d1;');
  $('#start_subscription_btn').attr('onclick','show_snackbar(null,\'Check the box if you are sure\')');
  $('#start_subscription_checkbox').on('change',function(){
      if($('#start_subscription_checkbox:checked').is(':checked')){
        $('#start_subscription_btn').attr('style','background-color: #0088ff;border:1px solid #0088ff')
        $('#start_subscription_btn').attr('onclick','start_subscription();');
      }else{
        $('#start_subscription_btn').attr('style','background-color: #989fa7;border: 1px solid #bfc7d1;');
        $('#start_subscription_btn').attr('onclick','show_snackbar(null,\'Check the box if you are sure\')')
      }
    });
});
function fetch_notifications(){
  // notificationsList={}
  var params = {
        // 'deployment_uuid':dep_id,
    };
  var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/notifications_handler/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 60000,//40 sec timeout
    };
  $.ajax(settings).done(function (msg){
    if(msg.status=='success')
      {
        notificationsDict = msg['results'];
        refresh_notification();
        if(window.location.href.indexOf('#notif')!=-1)
          $('#notification_details').show();
      }
  }).complete(function(msg){
    if(window.location.href.indexOf('/mobile_')!=-1){
      $('#notification_details').show();
    }
  });
}
function notifications_read(){
  // notificationsList={}
  var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
  var params = {
        // 'deployment_uuid':dep_id,
        'csrfmiddlewaretoken':csrfmiddlewaretoken
    };
  var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/notifications_handler/',
      "method": "POST",
      "headers": {
      },
      "data":params,
      "timeout": 60000,//40 sec timeout
    };
  $.ajax(settings).done(function (msg){
    if(msg.status=='success')
      {
        console.log('notifications read!')
      }
    else{
      // notifications_read();
      // alert(msg);
      }
  });

}
function refresh_notification(){
  var unread_count = 0;
  notificationsList = notificationsDict.notifications;
  unread_count = notificationsDict.unread_count;
  $('#notification_details').empty();
  if(notificationsList.length==0){
    if(window.location.href.indexOf('alerts')!=-1){
      $('.empty_alerts').show();
      $('.mobile_notification_holder').hide();
    }
    // else{
    //   $('.empty_alerts').hide();
    //   $('.mobile_notification_holder').show();
    // }
    $('#notification_details').append('<li><div class="notif"><p>'+'</p><p><span>'+'No alerts'+'</span></p></div></li>');
  }else if(notificationsList.length>0){
    if(window.location.href.indexOf('alerts')!=-1){
      $('.empty_alerts').hide();
      $('.mobile_notification_holder').show();
    }
  }

  notificationsUsed = notificationsDict['used'];
  for(var i=0; i<notificationsList.length;i++){
    notif = notificationsList[i];
    // if(notif.unread || !notif.open_notif){
    //   unread_count += 1;
    // }
    notifications = "";
    if (notif['notification-type'] == "order-notification")
    {
      // $('#notification_details').show();
      // $($('#notification_details').find('li')[0]).remove();
      dt = moment(notif.notification_time);
      date = dt.format('h:mm:ss a');
      notif_tag = '';
      notif_desc = '';
      // if (notif.sender =='lambda'){
      notif['notification_title'] = notif.action_type + ' alert';
      notif['notification_msg'] = notif.action_type+' '+notif.quantity+' shares of '+notif.symbol+' at &nbsp;&#8377;'+parseFloat(notif.trigger_price).toFixed(2);
      notif_tag = notif['notification_title'].toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
      notif_desc = '';//notif['notification_title'].toLowerCase().split('-').join('_').split(' ').join('_')+'_desc';
      notif_image = notif['notification_title'].toLowerCase().split('-').join('_').split(' ').join('_').replace(' alert','');
      notif_gif = 'alert_blue';
      try{
        if(notif['transaction_type']!=notif['action_type'])
            {
              notif_image = 'exit_'+notif_image;
            }
        else
            notif_image = 'entry_'+notif_image;

          if(action_type.toUpperCase()!='BUY')
              {
                notif_gif = 'alert_orange';
              }
      }catch(e){
        
      }

      if(moment()-dt<60000*5 && notificationsUsed[notif['notification_uuid']]==undefined)
        {
          // }
          a = '<li><div class="notif"><div class="notif_first_line"> <span><img src="/static/imgs/new/orderlog/'+notif_image+'.svg"></span> <p class="notif_tag '+notif_tag+'">'+notif['notification_title']+'</p><span><img src="/static/imgs/new/'+notif_gif+'.gif"></span> <!-- <p class="notif_desc">'+notif.notification_msg+'</p> --> </div> <div class="notif_second_line">  <div class="notif_second_line_desc_container"><p class="notif_desc">'+notif.notification_msg+'</p><p class="notif_algo_name">'+notif.algo_name+'</p></div> <div class="notif_second_line_algoname_container"><p class="notif_take_act">Take action</p> <p class="notif_time_stamp">'+date+'</p></div> </div></div><div class="notif_window"><div class="notif_header notif_header_'+notif.action_type.toLowerCase()+'"><p>'+notif['action_type']+'&nbsp;'+notif['sym']+'&nbsp;x'+notif['quantity']+'&nbsp;Qty<br><span>&#8377;'+parseFloat(notif.trigger_price).toFixed(2)+'&nbsp;on&nbsp;'+notif['seg']+'</span></p></div><div class="notif_body"><div class="notif_options"><div><!--<div class="radio_options"><div><span id="'+notif.action_type.toLowerCase()+'_radio_option"></span>-->'
          // a = '<li><div class="notif"><p>'+date+'</p><p>Notification &nbsp;<span>'+notif.algo_name+'<p>'+notif.notification_msg+'</p>'+'</span></p></div><div class="notif_window"><div class="notif_header"><p>'+notif.notification_msg+'</p></div><div class="notif_body"><div class="notif_options"><div><div class="radio_options"><div><span id="buy_radio_option"></span>'
          // '<div class="radio_options"><div><span id="buy_radio_option"></span><p>CNC</p></div><div><span></span><p id="option_selected">MIS</p>'

          b = '<div class="radio_options"><div><span class="radio_outer"><span class="radio_inner"></span></span><p>MIS</p></div><div><span id="'+notif.action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">CNC</p>';

          if(notif['product']=='MIS')
            {
              if(notif['seg']=='NFO-FUT')
              {
                b = '<div class="radio_options"><div><span id="'+notif.action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MIS</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>NRML</p>';
              }
              else{
                b = '<div class="radio_options"><div><span id="'+notif.action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MIS</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>CNC</p>';
              }
            }
          else if(notif['product']=='NRML'){
            b = '<div class="radio_options"><div><span class="radio_outer"><span class="radio_inner"></span></span><p>MIS</p></div><div><span id="'+notif.action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">NRML</p>';
            }

          notif_state = 'Entry';
          try{
            if(notif['transaction_type']!=notif['action_type']){
              notif_state = 'Exit'; 
            }
          }
          catch(e){

          }
          // c = '</div></div><div class="notif_left"><div class="exit_qty"><p>Qty.</p><input type="number" id="position_qty" name="" value="'+notif.quantity+'" readonly></div><div class="exit_qty"><p>Price</p><input type="number" name="" id="position_price" value="'+0+'" readonly></div></div><div class="notif_options_price"><div class="radio_options"><div><span id="'+action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MARKET</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL-M</p></div></div><div class="notif_right"><div class="exit_price"><p>Trigger price</p><input type="number" id="position_trigger_price" class="bg-stripe" name="" value="0" readonly></div><div class="exit_price"><p>Disclosed qty.</p><input type="number" id="position_disclosed_qty" name="" value="0" readonly></div></div></div></div><div id="notif_actions"><button onclick="place_order(event,\''+notif['notification_uuid']+'\',\''+notif['deployment_uuid']+'\',\''+notif['algo_uuid']+'\',\''+notif['seg']+'\',\''+notif['sym']+'\',\''+notif['quantity']+'\',\''+'MARKET'+'\',\''+notif['action_type'].toUpperCase()+'\',\''+notif['product']+'\',\''+'DAY'+'\',\''+notif.algo_name+'\',\''+(moment()-dt)+'\')" id="'+notif.action_type.toLocaleLowerCase()+'">'+notif.action_type+'</button><button id="cancel" onclick="cancel_notifications(event,\''+notif['deployment_uuid']+'\')">Cancel</button></div></div></div></li>';

          c='</div></div><div class="notif_left"><div class="notif_qty"><p>Qty.</p><input type="number" id="position_qty" name="" value="'+notif.quantity+'" readonly></div><div class="notif_qty"><p>Price</p><input type="number" name="" id="position_price" value="'+0+'" readonly></div></div></div><div class="notif_options_price"><div class="radio_options"><div><span id="'+notif.action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MARKET</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL-M</p></div></div><div class="notif_right"><div class="notif_price"><p>Trigger price</p><input type="number" class="bg-stripe" id="position_trigger_price" name="" value="0" readonly></div><div class="notif_price"><p>Disclosed qty.</p><input type="number" class="bg-stripe" id="position_disclosed_qty" name="" value="0" readonly></div></div></div></div><div id="notif_actions"><button onclick="place_order(event,\''+notif['notification_uuid']+'\',\''+notif['deployment_uuid']+'\',\''+notif['algo_uuid']+'\',\''+notif['seg']+'\',\''+notif['sym']+'\',\''+notif['quantity']+'\',\''+'MARKET'+'\',\''+notif['action_type'].toUpperCase()+'\',\''+notif['product']+'\',\''+'DAY'+'\',\''+notif.algo_name+'\',\''+(moment()-dt)+'\')" id="'+notif.action_type.toLocaleLowerCase()+'">'+to_title(notif.action_type)+'</button><button id="cancel" onclick="cancel_notifications(event,\''+notif['deployment_uuid']+'\',\''+notif['notification_uuid']+'\',\''+notif_state+'\')">Cancel</button></div></div></div></li>';

          $('#notification_details').prepend(a+b+c);
        }
      else{
        // a = '<li><div class="notif"><p>'+date+'</p><p>Notification &nbsp;<span>'+notif.algo_name+'</span></p></div></li>';
        a = '<li><div class="notif"><div class="notif_first_line"> <p class="notif_time_stamp">'+date+'</p> <p class="notif_algo_name">'+notif.algo_name+'</p> <!-- <p class="notif_desc">'+notif.notification_msg+'</p> --> </div> <div class="notif_second_line"> <p class="notif_tag '+notif_tag+'">'+notif['notification_title']+'</p> <p class="notif_desc">'+notif.notification_msg+'</p> </div>';
        a = '<li><div class="notif"><div class="notif_first_line"> <span><img src="/static/imgs/new/orderlog/'+notif_image+'.svg"></span> <p class="notif_tag '+notif_tag+'">'+notif['notification_title']+'</p><span></span></div> <div class="notif_second_line">  <div class="notif_second_line_desc_container"><p class="notif_desc">'+notif.notification_msg+'</p><p class="notif_algo_name">'+notif.algo_name+'</p></div> <div class="notif_second_line_algoname_container"><p class="notif_take_act"></p> <p class="notif_time_stamp">'+date+'</p></div> </div></div></li>';
        $('#notification_details').prepend(a);
      }
    }
    if(notif['notification-type']=='discipline-notif'){
        var dt = moment(notif.notification_time);
        var date = dt.format('h:mm:ss a');
        var notif_tag = '';
        var notif_desc = '';
        // if (notif.sender =='lambda'){
        // notif['notification_title'] = notif.notification_msg;
        var notification_title = notif.notification_msg;
        // notif['notification_msg'] = notif.order_type+' '+notif.action_type+' '+notif.quantity+' shares of '+notif.symbol+' at &nbsp;&#8377;'+parseFloat(notif.trigger_price).toFixed(2);
        var notification_msg = notif.order_type+' '+notif.action_type+' '+notif.quantity+' shares of '+notif.symbol+' at &nbsp;&#8377;'+parseFloat(notif.trigger_price).toFixed(2);
        notif_tag = notif.action_type.toLowerCase()+'_'+notification_title.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
        // console.log(notif);place_sl_m_order_tag
        notif_desc = '';//
        notif_image='slm_buy';
        notif_gif = 'alert_blue';
        try{
          if(notif['action_type'].toUpperCase()!='BUY')
              {
                notif_image = 'slm_sell';
                notif_gif = 'alert_red';
              }
        }catch(e){
          
        }
        if(moment()-dt<60000*5 && notificationsUsed[notif['notification_uuid']]==undefined)
        {
          // }
          a = '<li><div class="notif"><div class="notif_first_line"><span><img src="/static/imgs/new/orderlog/'+notif_image+'.svg"></span><p class="notif_tag '+notif_tag+'">'+notification_title+'</p> <span><img src="/static/imgs/new/'+notif_gif+'.gif"></span> </div> <div class="notif_second_line"> <div class="notif_second_line_desc_container"><p class="notif_desc">'+notification_msg+'</p><p class="notif_algo_name">'+notif.algo_name+'</p></div><div class="notif_second_line_algoname_container"><p class="notif_take_act">Take action</p><p class="notif_time_stamp">'+date+'</p></div> </div></div><div class="notif_window"><div class="notif_header notif_header_'+notif.action_type.toLowerCase()+'"><p>'+notif['action_type']+'&nbsp;'+notif['sym']+'&nbsp;x'+notif['quantity']+'&nbsp;Qty<br><span>&#8377;'+parseFloat(notif.trigger_price).toFixed(2)+'&nbsp;on&nbsp;'+notif['seg']+'</span></p></div><div class="notif_body"><div class="notif_options"><div><!--<div class="radio_options"><div><span id="'+notif.action_type.toLowerCase()+'_radio_option"></span>-->'
          // a = '<li><div class="notif"><p>'+date+'</p><p>Notification &nbsp;<span>'+notif.algo_name+'<p>'+notif.notification_msg+'</p>'+'</span></p></div><div class="notif_window"><div class="notif_header"><p>'+notif.notification_msg+'</p></div><div class="notif_body"><div class="notif_options"><div><div class="radio_options"><div><span id="buy_radio_option"></span>'
          // '<div class="radio_options"><div><span id="buy_radio_option"></span><p>CNC</p></div><div><span></span><p id="option_selected">MIS</p>'

          b = '<div class="radio_options"><div><span class="radio_outer"><span class="radio_inner"></span></span><p>MIS</p></div><div><span id="'+notif.action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">CNC</p>';

          if(notif['product']=='MIS')
            {
              if(notif['seg']=='NFO-FUT')
              {
                b = '<div class="radio_options"><div><span id="'+notif.action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MIS</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>NRML</p>';
              }
              else{
                b = '<div class="radio_options"><div><span id="'+notif.action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MIS</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>CNC</p>';
              }
            }
          else if(notif['product']=='NRML'){
            b = '<div class="radio_options"><div><span class="radio_outer"><span class="radio_inner"></span></span><p>MIS</p></div><div><span id="'+notif.action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">NRML</p>';
            }

          // c = '</div></div><div class="notif_qty"><p>Quantity</p><input type="number" name="" value="'+notif.quantity+'" readonly></div></div><div class="notif_options_price"><div class="radio_options"><div><span id="'+notif.action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">'+notif['order_type']+'</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div></div><div class="notif_price"><p>Price</p><input type="number" name="" readonly></div></div></div><div id="notif_actions"><button onclick="place_order(event,\''+notif['notification_uuid']+'\',\''+notif['deployment_uuid']+'\',\''+notif['algo_uuid']+'\',\''+notif['seg']+'\',\''+notif['sym']+'\',\''+notif['quantity']+'\',\''+notif['order_type']+'\',\''+notif['action_type'].toUpperCase()+'\',\''+notif['product']+'\',\''+'DAY'+'\',\''+notif.algo_name+'\',\''+(moment()-dt)+'\',\''+notif['trigger_price']+'\')" id="'+notif.action_type.toLocaleLowerCase()+'">'+notif.action_type+'</button><button id="cancel" onclick="cancel_notifications(event,\''+notif['deployment_uuid']+'\')">Cancel</button></div></div></div></li>';

          c='</div></div><div class="notif_left"><div class="notif_qty"><p>Qty.</p><input type="number" id="position_qty" name="" value="'+notif.quantity+'" readonly></div><div class="notif_qty"><p>Price</p><input type="number" name="" id="position_price" value="'+0+'" readonly></div></div></div><div class="notif_options_price"><div class="radio_options"><div><span class="radio_outer"><span class="radio_inner"></span></span><p>MARKET</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL</p></div><div><span id="'+notif.action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">SL-M</p></div></div><div class="notif_right"><div class="notif_price"><p>Trigger price</p><input type="number" id="position_trigger_price" name="" value="'+parseFloat(notif['trigger_price']).toFixed(2)+'" readonly></div><div class="notif_price"><p>Disclosed qty.</p><input type="number" class="bg-stripe" id="position_disclosed_qty" name="" value="0" readonly></div></div></div></div><div id="notif_actions"><button onclick="place_order(event,\''+notif['notification_uuid']+'\',\''+notif['deployment_uuid']+'\',\''+notif['algo_uuid']+'\',\''+notif['seg']+'\',\''+notif['sym']+'\',\''+notif['quantity']+'\',\''+notif['order_type']+'\',\''+notif['action_type'].toUpperCase()+'\',\''+notif['product']+'\',\''+'DAY'+'\',\''+notif.algo_name+'\',\''+(moment()-dt)+'\',\''+parseFloat(notif['trigger_price']).toFixed(2)+'\')" id="'+notif.action_type.toLocaleLowerCase()+'">'+to_title(notif.action_type)+'</button><button id="cancel" onclick="cancel_notifications_discipline(event,\''+notif['deployment_uuid']+'\',\''+notif['notification_uuid']+'\')">Cancel</button></div></div></div></li>';

          $('#notification_details').prepend(a+b+c);
          }
        else{
          // a = '<li><div class="notif"><p>'+date+'</p><p>Notification &nbsp;<span>'+notif.algo_name+'</span></p></div></li>';
          a = '<li><div class="notif"><div class="notif_first_line"> <p class="notif_time_stamp">'+date+'</p> <p class="notif_algo_name">'+notif.algo_name+'</p> <!-- <p class="notif_desc">'+notification_msg+'</p> --> </div> <div class="notif_second_line"> <p class="notif_tag '+notif_tag+'">'+notification_title+'</p> <p class="notif_desc">'+notification_msg+'</p> </div>';
          a = '<li><div class="notif"><div class="notif_first_line"> <span><img src="/static/imgs/new/orderlog/'+notif_image+'.svg"></span> <p class="notif_tag '+notif_tag+'">'+notification_title+'</p><span></span></div> <div class="notif_second_line">  <div class="notif_second_line_desc_container"><p class="notif_desc">'+notification_msg+'</p><p class="notif_algo_name">'+notif.algo_name+'</p></div> <div class="notif_second_line_algoname_container"><p class="notif_take_act"></p> <p class="notif_time_stamp">'+date+'</p></div> </div></div></li>';
          $('#notification_details').prepend(a);
        }
    }
    if(notif['notification-type']=='cancel-discipline-notif'){
        var dt = moment(notif.notification_time);
        var date = dt.format('h:mm:ss a');
        var notif_tag = '';
        var notif_desc = '';
        // if (notif.sender =='lambda'){
        // notif['notification_title'] = notif.notification_msg;
        var notification_title = notif.notification_msg;
        // notif['notification_msg'] = notif.order_type+' '+notif.action_type+' '+notif.quantity+' shares of '+notif.symbol+' at &nbsp;&#8377;'+parseFloat(notif.trigger_price).toFixed(2);
        var notification_msg = notif.order_type+' '+notif.action_type+' '+notif.quantity+' shares of '+notif.symbol+' at &nbsp;&#8377;'+parseFloat(notif.trigger_price).toFixed(2);
        notif_tag = notification_title.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
        // console.log(notif);
        notif_desc = '';//
        // if(moment()-dt<60000*5 && notificationsUsed[notif['notification_uuid']]==undefined)
        // {
        //   // }
        //   a = '<li><div class="notif"><div class="notif_first_line"> <p class="notif_time_stamp">'+date+'</p> <p class="notif_algo_name">'+notif.algo_name+'</p> <!-- <p class="notif_desc">'+notification_msg+'</p> --> </div> <div class="notif_second_line"> <p class="notif_tag '+notif_tag+'">'+notification_title+'</p> <p class="notif_desc">'+notification_msg+'</p> </div></div><div class="notif_window"><div class="notif_header notif_header_'+notif.action_type.toLowerCase()+'"><p>'+notif['action_type']+'&nbsp;'+notif['sym']+'&nbsp;x'+notif['quantity']+'&nbsp;Qty<br><span>&#8377;'+parseFloat(notif.trigger_price).toFixed(2)+'&nbsp;on&nbsp;'+notif['seg']+'</span></p></div><div class="notif_body"><div class="notif_options"><div><!--<div class="radio_options"><div><span id="'+notif.action_type.toLowerCase()+'_radio_option"></span>-->'
        //   // a = '<li><div class="notif"><p>'+date+'</p><p>Notification &nbsp;<span>'+notif.algo_name+'<p>'+notif.notification_msg+'</p>'+'</span></p></div><div class="notif_window"><div class="notif_header"><p>'+notif.notification_msg+'</p></div><div class="notif_body"><div class="notif_options"><div><div class="radio_options"><div><span id="buy_radio_option"></span>'
        //   // '<div class="radio_options"><div><span id="buy_radio_option"></span><p>CNC</p></div><div><span></span><p id="option_selected">MIS</p>'

        //   b = '<div class="radio_options"><div><span class="radio_outer"><span class="radio_inner"></span></span><p>MIS</p></div><div><span id="'+notif.action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">CNC</p>';

        //   if(notif['product']=='MIS')
        //     {
        //       if(notif['seg']=='NFO-FUT')
        //       {
        //         b = '<div class="radio_options"><div><span id="'+notif.action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MIS</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>NRML</p>';
        //       }
        //       else{
        //         b = '<div class="radio_options"><div><span id="'+notif.action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MIS</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>CNC</p>';
        //       }
        //     }
        //   else if(notif['product']=='NRML'){
        //     b = '<div class="radio_options"><div><span class="radio_outer"><span class="radio_inner"></span></span><p>MIS</p></div><div><span id="'+notif.action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">NRML</p>';
        //     }

        //   // c = '</div></div><div class="notif_qty"><p>Quantity</p><input type="number" name="" value="'+notif.quantity+'" readonly></div></div><div class="notif_options_price"><div class="radio_options"><div><span id="'+notif.action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">'+notif['order_type']+'</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div></div><div class="notif_price"><p>Price</p><input type="number" name="" readonly></div></div></div><div id="notif_actions"><button onclick="place_order(event,\''+notif['notification_uuid']+'\',\''+notif['deployment_uuid']+'\',\''+notif['algo_uuid']+'\',\''+notif['seg']+'\',\''+notif['sym']+'\',\''+notif['quantity']+'\',\''+notif['order_type']+'\',\''+notif['action_type'].toUpperCase()+'\',\''+notif['product']+'\',\''+'DAY'+'\',\''+notif.algo_name+'\',\''+(moment()-dt)+'\',\''+notif['trigger_price']+'\')" id="'+notif.action_type.toLocaleLowerCase()+'">'+notif.action_type+'</button><button id="cancel" onclick="cancel_notifications(event,\''+notif['deployment_uuid']+'\')">Cancel</button></div></div></div></li>';

        //   c='</div></div><div class="notif_left"><div class="notif_qty"><p>Qty.</p><input type="number" id="position_qty" name="" value="'+notif.quantity+'" readonly></div><div class="notif_qty"><p>Price</p><input type="number" name="" id="position_price" value="'+0+'" readonly></div></div></div><div class="notif_options_price"><div class="radio_options"><div><span class="radio_outer"><span class="radio_inner"></span></span><p>MARKET</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL</p></div><div><span id="'+notif.action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">SL-M</p></div></div><div class="notif_right"><div class="notif_price"><p>Trigger price</p><input type="number" id="position_trigger_price" name="" value="'+parseFloat(notif['trigger_price']).toFixed(2)+'" readonly></div><div class="notif_price"><p>Disclosed qty.</p><input type="number" class="bg-stripe" id="position_disclosed_qty" name="" value="0" readonly></div></div></div></div><div id="notif_actions"><button onclick="place_order(event,\''+notif['notification_uuid']+'\',\''+notif['deployment_uuid']+'\',\''+notif['algo_uuid']+'\',\''+notif['seg']+'\',\''+notif['sym']+'\',\''+notif['quantity']+'\',\''+notif['order_type']+'\',\''+notif['action_type'].toUpperCase()+'\',\''+notif['product']+'\',\''+'DAY'+'\',\''+notif.algo_name+'\',\''+(moment()-dt)+'\',\''+parseFloat(notif['trigger_price']).toFixed(2)+'\')" id="'+notif.action_type.toLocaleLowerCase()+'">'+to_title(notif.action_type)+'</button><button id="cancel" onclick="cancel_notifications_discipline(event,\''+notif['deployment_uuid']+'\',\''+notif['notification_uuid']+'\')">Cancel</button></div></div></div></li>';

        //   $('#notification_details').prepend(a+b+c);
        //   }
        // else{
          // a = '<li><div class="notif"><p>'+date+'</p><p>Notification &nbsp;<span>'+notif.algo_name+'</span></p></div></li>';
          // a = '<li><div class="notif"><div class="notif_first_line"> <p class="notif_time_stamp">'+date+'</p> <p class="notif_algo_name">'+notif.algo_name+'</p> <!-- <p class="notif_desc">'+notification_msg+'</p> --> </div> <div class="notif_second_line"> <p class="notif_tag '+notif_tag+'">'+notification_title+'</p> <p class="notif_desc">'+notification_msg+'</p> </div>';
          if(notificationsUsed[notif['notification_uuid']]==undefined){
              a = '<div class="notif"><div class="notif_first_line"> <p class="notif_time_stamp">'+date+'</p> <p class="notif_algo_name">'+notif.algo_name+'</p> </div> <div class=notif_second_line_cancel_order><div class="notif_second_line_top"> <p class="notif_tag cancel_sl_m_order_tag">CANCEL SL-M ORDER</p> </div><div class="notif_second_line_bottom"> <button id="cancel_order_notif_confirm" onclick="cancel_order_notif(event,\''+notif.order_id+'\',\''+notif['notification_uuid']+'\')">Cancel order</button></div></div></div>';
              a = '<div class="notif"><div class="notif_first_line"> <span><img src="/static/imgs/new/orderlog/cancelled.svg"></span><p class="notif_tag cancel_sl_m_order_tag">CANCEL SL-M ORDER</p><span></span></div> <div class=notif_second_line_cancel_order> <div class="notif_second_line_desc_container"><p class="notif_desc">#'+notif.order_id+'</p><p class="notif_algo_name">'+notif.algo_name+'</p></div><div class="notif_second_line_algoname_container"><p></p><p class="notif_time_stamp">'+date+'</p></div><div class="notif_second_line_top"> <p class="notif_desc">#'+notif.order_id+'</p> </div><div class="notif_second_line_bottom"> <button id="cancel_order_notif_confirm" onclick="cancel_order_notif(event,\''+notif.order_id+'\',\''+notif['notification_uuid']+'\')">Cancel order</button></div></div></div>';
          }
          else{
            a = '<div class="notif"><div class="notif_first_line"> <p class="notif_time_stamp">'+date+'</p> <p class="notif_algo_name">'+notif.algo_name+'</p> </div> <div class=notif_second_line_cancel_order><div class="notif_second_line_top"> <p class="notif_tag cancel_sl_m_order_tag">CANCEL SL-M ORDER</p><p class="notif_desc">#'+notif.order_id+'</p> </div><div class="notif_second_line_bottom" style="display:none"> <button id="cancel_order_notif_confirm" onclick="cancel_order_notif(event,\''+notif.order_id+'\',\''+notif['notification_uuid']+'\')">Cancel order</button></div></div></div>';
            a = '<div class="notif"><div class="notif_first_line"> <span><img src="/static/imgs/new/orderlog/cancelled.svg"></span><p class="notif_tag cancel_sl_m_order_tag">CANCEL SL-M ORDER</p><span></span></div> <div class=notif_second_line_cancel_order> <div class="notif_second_line_desc_container"><p class="notif_desc">#'+notif.order_id+'</p><p class="notif_algo_name">'+notif.algo_name+'</p></div><div class="notif_second_line_algoname_container"><p></p><p class="notif_time_stamp">'+date+'</p></div><div class="notif_second_line_top"> <p class="notif_desc">#'+notif.order_id+'</p> </div><div class="notif_second_line_bottom"></div></div></div>';
          }
          $('#notification_details').prepend(a);
        // }
    }
    if(notif['price_trigger-notification']!=undefined){ // TP/SL notification
      tpsl_key=notif['price_trigger-notification'];
      trigger_time = notif['trigger_time'];
      trigger_price = notif['trigger_price'];
      trigger_type = notif['type'];
      uid = notif['user_uuid'];
      tpsl_array = tpsl_key.split(':');
      userid = tpsl_array[0];
      depid = tpsl_array[1];
      token = tpsl_array[3];
      algo_name = tpsl_array[8];
      action_type = tpsl_array[9];
      quantity = tpsl_array[10];
      algo_uuid = tpsl_array[11];
      product = tpsl_array[12];
      symbol = tpsl_array[13];
      segment = tpsl_array[14];

      notification_title = '';

      if(trigger_type=="take-profit"){
        notification_msg = "Take profit at &nbsp;&#8377; "+parseFloat(trigger_price).toFixed(2);
        notification_title = 'Target profit' + ' alert';
      }
      else if(trigger_type=="stop-loss"){
        notification_msg = "Stop loss at &nbsp;&#8377; "+parseFloat(trigger_price).toFixed(2);
        notification_title = 'Stop loss' + ' alert';
      }else if(trigger_type=="inrange"){
          notification_msg = algo_name+" at price &nbsp;&#8377; "+parseFloat(trigger_price).toFixed(2);
          notification_title = action_type + ' alert';
      }
      // $('#notification_details').show();
      // $($('#notification_details').find('li')[0]).remove();
      dt = moment.unix(trigger_time);
      date = dt.format('h:mm:ss a');

      notification_msg = action_type+' '+quantity+' shares of '+symbol+' at &nbsp;&#8377; '+parseFloat(trigger_price).toFixed(2);

      notif_tag = notification_title.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
      
      notif_desc = '';//notification_title.toLowerCase().split('-').join('_').split(' ').join('_')+'_desc';

      notif_image = notification_title.toLowerCase().split('-').join('_').split(' ').join('_').replace(' alert','');
      notif_gif = 'alert_blue';
      try{
        if(notif['transaction_type']!=notif['action_type'])
            {
              notif_image = 'exit_'+notif_image;
            }
        else
            notif_image = 'entry_'+notif_image;

        if(action_type.toUpperCase()!='BUY')
              {
                notif_gif = 'alert_orange';
              }

        if(trigger_type=="take-profit"){
          notif_image = 'target_profit_alert';
        }
        else if(trigger_type=="stop-loss"){
          notif_image = 'stop_loss_alert';
        }
      }catch(e){
        
      }

      if(moment()-dt<60000*5 && notificationsUsed[notif['notification_uuid']]==undefined)
        {
          // if (notif.sender =='lambda'){
          // console.log(notif);
          // }
          a = '<li><div class="notif"><div class="notif_first_line"> <p class="notif_time_stamp">'+date+'</p> <p class="notif_algo_name">'+algo_name+'</p> <!-- <p class="notif_desc">'+notification_msg+'</p> --> </div> <div class="notif_second_line"> <p class="notif_tag '+notif_tag+'">'+notification_title+'</p> <p class="notif_desc">'+notification_msg+'</p> </div></div><div class="notif_window"><div class="notif_header notif_header_'+action_type.toLowerCase()+'"><p>'+action_type+'&nbsp;'+symbol+'&nbsp;x'+quantity+'&nbsp;Qty<br><span>&#8377;'+parseFloat(trigger_price).toFixed(2)+'&nbsp;on&nbsp;'+segment+'</span></p></div><div class="notif_body"><div class="notif_options"><div><!--<div class="radio_options"><div><span id="'+action_type.toLowerCase()+'_radio_option"></span>-->';
          a = '<li><div class="notif"><div class="notif_first_line"> <span><img src="/static/imgs/new/orderlog/'+notif_image+'.svg"></span> <p class="notif_tag '+notif_tag+'">'+notification_title+'</p><span><img src="/static/imgs/new/'+notif_gif+'.gif"></span> <!-- <p class="notif_desc">'+notification_msg+'</p> --> </div> <div class="notif_second_line">  <div class="notif_second_line_desc_container"><p class="notif_desc">'+notification_msg+'</p><p class="notif_algo_name">'+algo_name+'</p></div> <div class="notif_second_line_algoname_container"><p class="notif_take_act">Take action</p> <p class="notif_time_stamp">'+date+'</p></div> </div></div><div class="notif_window"><div class="notif_header notif_header_'+action_type.toLowerCase()+'"><p>'+action_type+'&nbsp;'+symbol+'&nbsp;x'+quantity+'&nbsp;Qty<br><span>&#8377;'+parseFloat(trigger_price).toFixed(2)+'&nbsp;on&nbsp;'+segment+'</span></p></div><div class="notif_body"><div class="notif_options"><div><!--<div class="radio_options"><div><span id="'+action_type.toLowerCase()+'_radio_option"></span>-->';

          // a = '<li><div class="notif"><p>'+date+'</p><p>Notification &nbsp;<span>'+algo_name+'</span></p></div><div class="notif_window"><div class="notif_header"><p>'+notification_msg+'</p></div><div class="notif_body"><div class="notif_options"><div><div class="radio_options"><div><span id="buy_radio_option"></span>'

          notif_state = 'Entry';
          try{
            if(notif['transaction_type']!=notif['action_type']){
              notif_state = 'Exit'; 
            }
          }
          catch(e){
            
          }

          b = '<div class="radio_options"><div><span class="radio_outer"><span class="radio_inner"></span></span><p>MIS</p></div><div><span id="'+action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">CNC</p>';
          
          if(product=='MIS')
            {
              if(segment=='NFO-FUT')
              {
                b = '<div class="radio_options"><div><span id="'+action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MIS</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>NRML</p>';
              }
              else{
                b = '<div class="radio_options"><div><span id="'+action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MIS</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>CNC</p>';
              }
          }
          else if(product=='NRML'){
            b = '<div class="radio_options"><div><span class="radio_outer"><span class="radio_inner"></span></span><p>MIS</p></div><div><span id="'+action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">NRML</p>';
          }

        // c = '</div></div><div class="notif_qty"><p>Quantity</p><input type="number" name="" value="'+quantity+'" readonly></div></div><div class="notif_options_price"><div class="radio_options"><div><span id="'+action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MARKET</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div></div><div class="notif_price"><p>Price</p><input type="number" name="" readonly></div></div></div><div id="notif_actions"><button onclick="place_order_tpsl(event,\''+notif['notification_uuid']+'\',\''+depid+'\',\''+algo_uuid+'\',\''+token+'\',\''+quantity+'\',\''+'MARKET'+'\',\''+action_type.toUpperCase()+'\',\''+product+'\',\''+'DAY'+'\',\''+tpsl_key+'\',\''+algo_name+'\',\''+(moment()-dt)+'\')" id="'+action_type.toLocaleLowerCase()+'">'+action_type+'</button><button id="cancel" onclick="cancel_notifications(event,\''+depid+'\')">Cancel</button></div></div></div></li>';

        c='</div></div><div class="notif_left"><div class="notif_qty"><p>Qty.</p><input type="number" id="position_qty" name="" value="'+quantity+'" readonly></div><div class="notif_qty"><p>Price</p><input type="number" name="" id="position_price" value="'+0+'" readonly></div></div></div><div class="notif_options_price"><div class="radio_options"><div><span id="'+action_type.toLowerCase()+'_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MARKET</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL-M</p></div></div><div class="notif_right"><div class="notif_price"><p>Trigger price</p><input type="number" class="bg-stripe" id="position_trigger_price" name="" value="0" readonly></div><div class="notif_price"><p>Disclosed qty.</p><input type="number" class="bg-stripe" id="position_disclosed_qty" name="" value="0" readonly></div></div></div></div><div id="notif_actions"><button onclick="place_order_tpsl(event,\''+notif['notification_uuid']+'\',\''+depid+'\',\''+algo_uuid+'\',\''+token+'\',\''+quantity+'\',\''+'MARKET'+'\',\''+action_type.toUpperCase()+'\',\''+product+'\',\''+'DAY'+'\',\''+tpsl_key+'\',\''+algo_name+'\',\''+(moment()-dt)+'\')" id="'+action_type.toLocaleLowerCase()+'">'+to_title(action_type)+'</button><button id="cancel" onclick="cancel_notifications(event,\''+depid+'\',\''+notif['notification_uuid']+'\',\''+notif_state+'\')">Cancel</button></div></div></div></li>';

        $('#notification_details').prepend(a+b+c);
      }
      else{
        // a = '<li><div class="notif"><p>'+date+'</p><p>Notification &nbsp;<span>'+notification_msg+'</span></p></div></li>';
        a = '<li><div class="notif"><div class="notif_first_line"> <p class="notif_time_stamp">'+date+'</p> <p class="notif_algo_name">'+algo_name+'</p> <!-- <p class="notif_desc">'+notification_msg+'</p> --> </div> <div class="notif_second_line"> <p class="notif_tag '+notif_tag+'">'+notification_title+'</p> <p class="notif_desc">'+notification_msg+'</p> </div>';
        a = '<li><div class="notif"><div class="notif_first_line"> <span><img src="/static/imgs/new/orderlog/'+notif_image+'.svg"></span> <p class="notif_tag '+notif_tag+'">'+notification_title+'</p><span></span></div> <div class="notif_second_line">  <div class="notif_second_line_desc_container"><p class="notif_desc">'+notification_msg+'</p><p class="notif_algo_name">'+algo_name+'</p></div> <div class="notif_second_line_algoname_container"><p class="notif_take_act"></p> <p class="notif_time_stamp">'+date+'</p></div> </div></div></li>';

        $('#notification_details').prepend(a);
      }
    }
    if(notif['notification-type']=='order-webhook'){ // this is produced by worker.js
      // $('#notification_details').show();
      date = moment(notif.notification_time).format('h:mm:ss a');
      notification_msg = notif.notification_msg;
      avg_price = parseFloat(notif.average_price).toFixed(2);
      filled_quantity = notif.filled_quantity;
      quantity = notif.quantity;
      action_type2 = notif.action_type;
      
      if(notif['status']=='Completed' || notif['status']=='Algo Expired'){
        notif_tag = notif.status.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
        notif_desc ='';
        notif['notification_title'] = notif.status;
        a = '<li><div class="notif"><div class="notif_first_line"> <p class="notif_time_stamp">'+date+'</p> <p class="notif_algo_name">'+notif.algo_name+'</p> <!-- <p class="notif_desc">'+action_type2+' '+filled_quantity+' of '+quantity+' at &nbsp;&#8377; '+avg_price+'</p> --> </div> <div class="notif_second_line"> <p class="notif_tag '+notif_tag+'">'+notif['notification_title']+'</p> <p class="notif_desc">'+notif['notification_msg']+'</p> </div></li>';

        notif_image = notif.status.toLowerCase().split('-').join('_').split(' ').join('_').replace(' alert','');

        try{

          if(notif['status']=='Completed')
            notif_image = 'algo_complete';
          else if(notif['status']=='Algo Expired')
            notif_image = 'algo_expired';
        }catch(e){
          
        }

        a = '<li><div class="notif"><div class="notif_first_line"><span><img src="/static/imgs/new/orderlog/'+notif_image+'.svg"></span><p class="notif_tag '+notif_tag+'">'+notif['notification_title']+'</p><span></span></div> <div class="notif_second_line"> <div class="notif_second_line_desc_container"><p class="notif_desc">'+notif['notification_msg']+'</p><p class="notif_algo_name">'+notif.algo_name+'</p></div><div class="notif_second_line_algoname_container"><p class="notif_take_act"></p><p class="notif_time_stamp">'+date+'</p></div></div></div></li>';
      }
      else if(notif['status']=='Force stopped'){
        notif_tag = notif.status.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
        notif_desc ='';
        notif['notification_title'] = notif.status;
        a = '<li><div class="notif"><div class="notif_first_line"> <p class="notif_time_stamp">'+date+'</p> <p class="notif_algo_name">'+notif.algo_name+'</p> <!-- <p class="notif_desc">'+action_type2+' '+filled_quantity+' of '+quantity+' at &nbsp;&#8377; '+avg_price+'</p> --> </div> <div class="notif_second_line"> <p class="notif_tag '+notif_tag+'">'+notif['notification_title']+'</p> <p class="notif_desc">'+notif['notification_msg']+'</p> </div></li>';

        notif_image = 'force_stopped';
          
        a = '<li><div class="notif"><div class="notif_first_line"><span><img src="/static/imgs/new/orderlog/'+notif_image+'.svg"></span><p class="notif_tag '+notif_tag+'">'+notif['notification_title']+'</p><span></span></div> <div class="notif_second_line"> <div class="notif_second_line_desc_container"><p class="notif_desc">'+notif['notification_msg']+'</p><p class="notif_algo_name">'+notif.algo_name+'</p></div><div class="notif_second_line_algoname_container"><p class="notif_take_act"></p><p class="notif_time_stamp">'+date+'</p></div></div></div></li>';
      }
      else if(notif['order_type']=='SL-M'){
        if(notif.action_type.toLowerCase()=='buy' && filled_quantity>0){
          action_type2='Bought';
          notif_tag = action_type2.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
          notif['notification_title'] = action_type2;
        }else if(notif.action_type.toLowerCase()=='sell' && filled_quantity>0){
          action_type2='Sold';
          notif_tag = action_type2.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
          notif['notification_title'] = action_type2;
        }
        else if(filled_quantity==0){
          notif_tag = 'SL-M_'+notif.status.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
          notif['notification_title'] = notif.status;
        }

        // + ' alert';
        if(filled_quantity>0)
          notif['notification_msg'] = action_type2+' '+notif.quantity+' shares of '+notif.symbol+' at &#8377; '+parseFloat(notif.trigger_price).toFixed(2);
        
        notif_desc ='';// notif['notification_title'].toLowerCase().split('-').join('_').split(' ').join('_')+'_desc';
            // }
        // a = '<li><div class="notif"><div class="notif_first_line"> <p class="notif_time_stamp">'+date+'</p> <p class="notif_algo_name">'+notif.algo_name+'</p> <!-- <p class="notif_desc">'+action_type2+' '+filled_quantity+' of '+quantity+' at &nbsp;&#8377; '+avg_price+'</p> --> </div> <div class="notif_second_line"> <p class="notif_tag '+notif_tag+'">'+notif['order_type']+' SL-M'+' '+notif['notification_title']+'</p> <p class="notif_desc">SL-M '+action_type2+' '+quantity+' shares of '+notif['symbol']+'</p> </div></li>'
        a = '<li><div class="notif"><div class="notif_first_line"> <p class="notif_time_stamp">'+date+'</p> <p class="notif_algo_name">'+notif.algo_name+'</p> <!-- <p class="notif_desc">'+action_type2+' '+filled_quantity+' of '+quantity+' at &nbsp;&#8377; '+avg_price+'</p> --> </div> <div class="notif_second_line"> <p class="notif_tag '+notif_tag+'">'+'SL-M'+' '+notif['notification_title']+'</p> <p class="notif_desc">SL-M '+action_type2+' '+quantity+' shares of '+notif['symbol']+'</p> </div></li>'

        notif_image = 'slm_'+notif.action_type.toLowerCase();

        a = '<li><div class="notif"><div class="notif_first_line"><span><img src="/static/imgs/new/orderlog/'+notif_image+'.svg"></span><p class="notif_tag '+notif_tag+'">'+notif['notification_title']+'</p><span></span></div> <div class="notif_second_line"> <div class="notif_second_line_desc_container"><p class="notif_desc">SL-M '+action_type2+' '+quantity+' shares of '+notif['symbol']+'</p><p class="notif_algo_name">'+notif.algo_name+'</p></div><div class="notif_second_line_algoname_container"><p class="notif_take_act"></p><p class="notif_time_stamp">'+date+'</p></div></div></div></li>';
      }
      else{
        if(notif.action_type.toLowerCase()=='buy' && filled_quantity>0){
          action_type2='Bought';
          notif_tag = action_type2.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
          notif['notification_title'] = action_type2;
        }else if(notif.action_type.toLowerCase()=='sell' && filled_quantity>0){
          action_type2='Sold';
          notif_tag = action_type2.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
          notif['notification_title'] = action_type2;
        }
        else if(filled_quantity==0){
          notif_tag = notif.status.toLowerCase().split('-').join('_').split(' ').join('_')+'_tag';
          notif['notification_title'] = notif.status;
        }

        // + ' alert';
        if(filled_quantity>0)
          notif['notification_msg'] = action_type2+' '+notif.quantity+' shares of '+notif.symbol+' at &#8377; '+parseFloat(notif.trigger_price).toFixed(2);
        
        notif_desc ='';// notif['notification_title'].toLowerCase().split('-').join('_').split(' ').join('_')+'_desc';
            // }
        a = '<li><div class="notif"><div class="notif_first_line"> <p class="notif_time_stamp">'+date+'</p> <p class="notif_algo_name">'+notif.algo_name+'</p> <!-- <p class="notif_desc">'+action_type2+' '+filled_quantity+' of '+quantity+' at &nbsp;&#8377; '+avg_price+'</p> --> </div> <div class="notif_second_line"> <p class="notif_tag '+notif_tag+'">'+notif['notification_title']+'</p> <p class="notif_desc">'+action_type2+' '+filled_quantity+' of '+quantity+' at &nbsp;&#8377; '+avg_price+'</p> </div></li>';

        notif_image = action_type2.toLowerCase();
        
        try{
          if(filled_quantity==0){
            notif_image = notif.status.toLowerCase();
          }
          if(notif['transaction_type']!=notif['action_type'])
              {
                notif_image = 'exit_'+notif_image;
              }
          else
              notif_image = 'entry_'+notif_image;

        }catch(e){
          
        }

        a = '<li><div class="notif"><div class="notif_first_line"><span><img src="/static/imgs/new/orderlog/'+notif_image+'.svg"></span><p class="notif_tag '+notif_tag+'">'+notif['notification_title']+'</p><span></span></div> <div class="notif_second_line"> <div class="notif_second_line_desc_container"><p class="notif_desc">'+action_type2+' '+filled_quantity+' of '+quantity+' at &nbsp;&#8377; '+avg_price+'</p><p class="notif_algo_name">'+notif.algo_name+'</p></div><div class="notif_second_line_algoname_container"><p class="notif_take_act"></p><p class="notif_time_stamp">'+date+'</p></div></div></div></li>';
        
      }

      // a = '<li> <div class="notif"> <p>'+date+'</p> <p>'+notification_msg+'.&nbsp;<span class="'+action_type2.toLowerCase()+'">'+action_type2+' '+filled_quantity+' of '+quantity+' at '+avg_price+'</span></p> </div> </li>';
      // if(!notif.open_notif)
      // {
        $('#notification_details').prepend(a);
        // $('#notif_count').text(notificationsDict['unread_count']);
      // }
    }
  }
  if(unread_count>0){
    if(window.location.href.indexOf('_alerts')==-1)
    {  
      $('#notif_count').text(notificationsDict['unread_count']);
      // make notif sound;
      $('#notif_count').show();
    }
    notification_audio.play();
  }
  else{
    $('#notif_count').text(0);
    $('#notif_count').hide();
  }
}
function update_notification(){
  var unread_count = 0;
  notificationsList = notificationsDict.notifications;
  unread_count = notificationsDict.unread_count;
  $('#notification_details').empty();
  if(notificationsList.length==0){
    $('#notification_details').append('<li><div class="notif"><p>'+'</p><p><span>'+'No alerts!'+'</span></p></div></li>');
  }
  notificationsUsed = notificationsDict['used'];
  for(var i=0; i<notificationsList.length;i++){
    notif = notificationsList[i];
    // if(notif.unread || !notif.open_notif){
    //   unread_count += 1;
    // }
    notifications = "";
    if (notif['notification-type'] == "order-notification")
    {
      // $('#notification_details').show();
      // $($('#notification_details').find('li')[0]).remove();
      dt = moment(notif.notification_time)
      date = dt.format('h:mm:ss a');
      if(moment()-dt<60000*5 && notificationsUsed[notif['notification_uuid']]==undefined)
        {
          a = '<li><div class="notif"><p>'+date+'</p><p>Notification &nbsp;<span>'+notif.algo_name+'</span></p></div><div class="notif_window"><div class="notif_header"><p>'+notif.notification_msg+'</p></div><div class="notif_body"><div class="notif_options"><div><div class="radio_options"><div><span id="buy_radio_option"></span><p id="option_selected">CNC</p></div><div><span></span><p>MIS</p></div></div><div class="notif_qty"><p>Quantity</p><input type="number" name="" value="'+notif.quantity+'"></div></div><div><div class="radio_options"><div><span id="buy_radio_option"></span><p id="option_selected">MKT</p></div><div><span></span><p>LMT</p></div></div><div class="notif_price"><p>Price</p><input type="number" name=""></div></div></div><div id="notif_actions"><button onclick="place_order(event,\''+notif['notification_uuid']+'\',\''+notif['deployment_uuid']+'\',\''+notif['algo_uuid']+'\',\''+notif['seg']+'\',\''+notif['sym']+'\',\''+notif['quantity']+'\',\''+'MARKET'+'\',\''+notif['action_type'].toUpperCase()+'\',\''+'MIS'+'\',\''+'DAY'+'\',\''+notif.algo_name+'\')" id="'+notif.action_type.toLocaleLowerCase()+'">'+notif.action_type+'</button><button id="cancel" onclick="cancel_notifications(event,\''+notif['deployment_uuid']+'\',\''+notif['notification_uuid']+'\')">Cancel</button></div></div></div></li>';
          $('#notification_details').prepend(a);
        }
      else{
        a = '<li><div class="notif"><p>'+date+'</p><p>Notification &nbsp;<span>'+notif.algo_name+'</span></p></div></li>';
          $('#notification_details').prepend(a);
      }
    }
    if(notif['price_trigger-notification']!=undefined){ // TP/SL notification
      tpsl_key=notif['price_trigger-notification'];
      trigger_time = notif['trigger_time'];
      trigger_price = notif['trigger_price'];
      trigger_type = notif['type'];
      uid = notif['user_uuid'];
      tpsl_array = tpsl_key.split(':');
      userid = tpsl_array[0];
      depid = tpsl_array[1];
      token = tpsl_array[3];
      algo_name = tpsl_array[8];
      action_type = tpsl_array[9];
      quantity = tpsl_array[10];
      algo_uuid = tpsl_array[11];

      if(trigger_type=="take-profit"){
        notification_msg = "Take profit at "+parseFloat(trigger_price).toFixed(2);
      }
      else if(trigger_type=="stop-loss"){
        notification_msg = "Stop loss at "+parseFloat(trigger_price).toFixed(2);
      }
      else if(trigger_type=="inrange"){
          notification_msg = algo_name+" at price "+parseFloat(trigger_price).toFixed(2);
      }
      // $('#notification_details').show();
      // $($('#notification_details').find('li')[0]).remove();
      dt = moment.unix(trigger_time);
      date = dt.format('h:mm:ss a');
      if(moment()-dt<60000*5 && notificationsUsed[notif['notification_uuid']]==undefined)
        {
        a = '<li><div class="notif"><p>'+date+'</p><p>Notification of &nbsp;<span>'+algo_name+'</span></p></div><div class="notif_window"><div class="notif_header"><p>'+notification_msg+'</p></div><div class="notif_body"><div class="notif_options"><div><div class="radio_options"><div><span id="buy_radio_option"></span><p id="option_selected">CNC</p></div><div><span></span><p>MIS</p></div></div><div class="notif_qty"><p>Quantity</p><input type="number" name="" value="'+quantity+'" readonly></div></div><div><div class="radio_options"><div><span id="buy_radio_option"></span><p id="option_selected">MKT</p></div><div><span></span><p>LMT</p></div></div><div class="notif_price"><p>Price</p><input type="number" name=""></div></div></div><div id="notif_actions"><button onclick="place_order_tpsl(event,\''+notif['notification_uuid']+'\',\''+depid+'\',\''+algo_uuid+'\',\''+token+'\',\''+quantity+'\',\''+'MARKET'+'\',\''+action_type.toUpperCase()+'\',\''+'MIS'+'\',\''+'DAY'+'\',\''+tpsl_key+'\',\''+algo_name+'\')" id="'+action_type.toLocaleLowerCase()+'">'+action_type+'</button><button id="cancel" onclick="cancel_notifications(event,\''+depid+'\',\''+notif['notification_uuid']+'\')">Cancel</button></div></div></div></li>';
        $('#notification_details').prepend(a);}
      else{
        a = '<li><div class="notif"><p>'+date+'</p><p>Notification &nbsp;<span>'+notification_msg+'</span></p></div></li>';
        $('#notification_details').prepend(a);
      }
    }
    if(notif['notification-type']=='order-webhook'){ // this is produced by worker.js
      // $('#notification_details').show();
      date = moment(notif.notification_time).format('h:mm:ss a');
      notification_msg = notif.notification_msg;
      avg_price = parseFloat(notif.average_price).toFixed(2);
      filled_quantity = notif.filled_quantity;
      quantity = notif.quantity;
      action_type2 = notif.action_type;
      
      if(notif.action_type.toLowerCase()=='buy'){
        action_type2='Bought';
      }else if(notif.action_type.toLowerCase()=='sell'){
        action_type2='Sold';
      }

      a = '<li> <div class="notif"> <p>'+date+'</p> <p>'+notification_msg+'.&nbsp;<span class="'+action_type2.toLowerCase()+'">'+action_type2+' '+filled_quantity+' of '+quantity+' at '+avg_price+'</span></p> </div> </li>';
      if(!notif.open_notif)
      {
        $('#notification_details').prepend(a);
        // $('#notif_count').text(notificationsDict['unread_count']);
      }
    }
  }
  if(unread_count>0){
    $('#notif_count').text(notificationsDict['unread_count']);
    // make notif sound;
    $('#notif_count').show();
  }
  else{
    $('#notif_count').text(0);
    $('#notif_count').hide();
  }
}
function show_snackbar(e,msg,type='error',callback=null,show_time=8000){
  $(".snackbar").show();
  if(type=='error'){
    $(".snackbar").find('p').addClass('snackbar_error');
  }
  else{
   $(".snackbar").find('p').removeClass('snackbar_error'); 
  }
  $(".snackbar p").text(msg);
  $(".snackbar").removeClass("animated, bounceInUp");
  // $(".snackbar").fadeOut(4000);
  setTimeout(function() { $(".snackbar").fadeOut(2000) }, show_time);
  $(".snackbar").addClass("animated, bounceInUp");
  if(callback){
    setTimeout(function(){ 
      callback();
    }, 5000);
  }
}

function close_popup () {
    $(".close").parents("body").find(".popup").fadeOut();
    $("body").removeClass("body_scroll");
}
function popup_show (){
    // alert('In here');
    $('.popup').show();
    $('.popup div').show();
}
function ti_done(data,r,ev,id) {
  // alert('yo')
  txt = ''
  syntax = data['syntax']
  syntax = syntax.split(' ')

  var default_value = false;

  for(var j=0; j<syntax.length; j++){

    if(syntax[j].includes('<') && syntax[j].includes('>'))
      {
        
        default_value = false;
        // found = false;
        for (var i=0; i < data['params'].length;i++){
          if(syntax[j].includes(data['params'][i][0])){
            // found = true;
            if($('#'+data['params'][i][0]+r).val()==data['params'][i][1] && data['params'][i][0]!='period' && data['params'][i][0]!='range_percentage' && data['params'][i][0]!='price'){
            // console.log(data['params'][i][0],$('#'+data['params'][i][0]+r).val());
              default_value = true;
              continue;
            }
            txt += $('#'+data['params'][i][0]+r).val() + ' ';
          }
        }
        // if(found)
      }
      else{
        if(default_value==true){
          default_value=false;
          // console.log(syntax[j]);
          j+=1;
          continue
        }
        txt += syntax[j] + ' ';
      }     
  }

  // txt trimming
  if(txt.endsWith('with ')){
    txt.replace('with ','');
  }

  $('.ti_popup').hide();
  $('.ti_popup div').hide();
  $('#ti_name').empty();
  $("#ti_populate").find("tr").remove();

  if (txt!='' && txt!=' ')
  {
    span_elem = document.createElement('span');
    span_elem.setAttribute("draggable", "false");
    span_elem.setAttribute("ondragstart", "drag(event);");
    span_elem.setAttribute("class", "ti");
    span_elem.setAttribute("id", ''+id+r);
    // span_elem.innerHTML = '<span draggable="true" ondragstart="drag(event);" class="ti" id="'+id+r+'">&nbsp;'+txt+'&nbsp;<img width=10px height=10px src="/static/imgs/close.png" onclick="toggle_parent_span(\''+id+r+'\')"></span>';
    span_elem.innerHTML = '&nbsp;'+txt+'&nbsp;<img width=10px height=10px src="/static/imgs/close.png" onclick="remove_id(\''+id+r+'\')">';
  
    ev.target.appendChild(span_elem
      );
  }
}

function gen_span(data,txt){

}

function ti_popup_show (data,ev,id){
    // alert('In here');
    $('#ti_name').empty();
    $('#ti_name').html(data['title']);

    r = parseInt(Math.random()*100);
    if(data['params'].length==0){
      $('.ti_popup div').fadeOut();
      $('.ti_popup').fadeOut();
      // call gen_span here for items without any param
      span_elem = document.createElement('span');
      span_elem.setAttribute("draggable", "false");
      span_elem.setAttribute("ondragstart", "drag(event);");
      span_elem.setAttribute("class", "ti");
      span_elem.setAttribute("id", ''+id+r);
      span_elem.innerHTML = document.getElementById(id).innerHTML+'&nbsp;<img width=10px height=10px src="/static/imgs/close.png" onclick="remove_id(\''+id+r+'\')">';
      ev.target.appendChild(span_elem);
    }
    else{
      $('.ti_popup').show();
      $('.ti_popup div').show();

      $("#ti_populate").find("tr").remove();
      for (var i=0;i< data['params'].length;i++){
        row = '<tr>';
        if(data['params'][i][0]=='offset')
          row += '<th style="text-transform:capitalize;">'+data['params'][i][3].replace('_',' ')+'</th>';
        else
          row += '<th style="text-transform:capitalize;">'+data['params'][i][0].replace('_',' ')+'</th>';
        if(data['params'][i][0]=='range_percentage')
          row += '<th><input id="'+data['params'][i][0]+r+'" type="number" name="" step="'+data['params'][i][4]+'" min="0" value='+ data['params'][i][1] +'></th>';
        else
          row += '<th><input id="'+data['params'][i][0]+r+'" type="number" name="" step="1" min="0" value='+ data['params'][i][1] +'></th>';
        // row += '<th><input id="'+data['params'][i][0]+r+'" type="number" name="" step="1" min="0" value='+ (''+data['params'][i][1]).toUpperCase()[0]+(''+data['params'][i][1]).slice(1).toLowerCase() +'></th>';
        row += '</tr>';
        $("#ti_populate").append(row);
      }
      $('.done').unbind('click');
      $(".done").click(function(){ti_done(data,r,ev,id);});
    }
}
   
function post(path, params, method) {
    method = method || "post"; // Set method to post by default if not specified.

    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);

    for(var key in params) {
        if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);

            form.appendChild(hiddenField);
         }
    }

    document.body.appendChild(form);
    form.submit();
}

function popupWindowCenter(url, title, w, h) {  
    // Fixes dual-screen position                         Most browsers      Firefox  
    var dualScreenLeft = window.screenLeft != undefined ? window.screenLeft : screen.left;  
    var dualScreenTop = window.screenTop != undefined ? window.screenTop : screen.top;  
              
    width = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth ? document.documentElement.clientWidth : screen.width;  
    height = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight ? document.documentElement.clientHeight : screen.height;  
              
    var left = ((width / 2) - (w / 2)) + dualScreenLeft;  
    var top = ((height / 2) - (h / 2)) + dualScreenTop;  
    var newWindow = window.open(url, title, 'scrollbars=yes, width=' + w + ', height=' + h + ', top=' + top + ', left=' + left);  
  
    // Puts focus on the newWindow  
    if (window.focus) {  
        newWindow.focus();  
    }
    return newWindow;
}  
function arrayUnique(array) {
    var a = array.concat();
    for(var i=0; i<a.length; ++i) {
        for(var j=i+1; j<a.length; ++j) {
            if(a[i] === a[j])
                a.splice(j--, 1);
        }
    }

    return a;
}

// $(window).load(function() {
//     // Animate loader off screen
//     $(".loader_parent").fadeOut();
//   });

// String.prototype.hexEncode = function(){
//     var hex, i;

//     var result = "";
//     for (i=0; i<this.length; i++) {
//         hex = this.charCodeAt(i).toString(16);
//         result += ("000"+hex).slice(-4);
//     }

//     return result
// }

// String.prototype.hexDecode = function(){
//     var j;
//     var hexes = this.match(/.{1,4}/g) || [];
//     var back = "";
//     for(j = 0; j<hexes.length; j++) {
//         back += String.fromCharCode(parseInt(hexes[j], 16));
//     }

//     return back;
// }
String.prototype.hexEncode = function(){
    var hex, i;

    var result = "";
    for (i=0; i<this.length; i++) {
        hex = this.charCodeAt(i).toString(16);
        result += ("000"+hex).slice(-4);
    }

    return result

    // utf8 to latin1
    var s = unescape(encodeURIComponent(this))
    var h = ''
    for (var i = 0; i < s.length; i++) {
        h += s.charCodeAt(i).toString(16)
    }
    return h
}

String.prototype.hexDecode = function(){
    var s = ''
    for (var i = 0; i < this.length; i+=2) {
        s += String.fromCharCode(parseInt(this.substr(i, 2), 16))
    }
    return decodeURIComponent(escape(s))
}

// if ('serviceWorker' in navigator) {
//   window.addEventListener('load', function() {
//     navigator.serviceWorker.register('/static/js/sw.js').then(function(registration) {
//       // Registration was successful
//       console.log('ServiceWorker registration successful with scope: ', registration.scope);
//     }, function(err) {
//       // registration failed :(
//       console.log('ServiceWorker registration failed: ', err);
//     });
//   });
// }
var w = undefined;
$(document).ready(function(){
  
  if (typeof(w) == "undefined" && $('.is_auth').length>0)
    {
    w = new Worker("/static/js/worker.js");

    w.onmessage = function (event) {
      notifications = "";
        if (event.data['notification-type'] == "order-notification"  || event.data['notification-type']=='discipline-notif' || event.data['notification-type']=='cancel-discipline-notif')
        {
          // refresh_notification();
          notificationsDict['notifications'].push(event.data);
          notificationsDict['unread_count']+=1;
          refresh_notification();
          $('#notification_details').show();
          refresh_order_log();
          notification_audio.play();
      }
      if(event.data['notification-type']=='ltp'){
        for(var t=0;t<event.data['ticks'].length;t++){
          tick = event.data['ticks'][t];
          // sym_segList[tick['Token']] = event.data['ticks'][0];
          sym_segDict = event.data['sym_segDict'];
          sym_seg = sym_segDict[tick['Token']];
          x = $('.token__'+sym_seg.replace('&','\\&').replace(/ /g,'_-_'));
          x.each(function(i){
            // x[i].
              sub_ltp = $(x[i]).find('.ltp .sub_ltp')
              ltp_change = parseFloat(tick['NetPriceChangeFromClosingPrice']).toFixed(2);
              ltp_val = tick['LastTradedPrice'];
              if(ltp_change<0)
              {
                ltp_text = ltp_val+' ( '+ltp_change+'%)';
                sub_ltp.text(ltp_text);
                // sub_ltp.removeClass('loss');
                // sub_ltp.removeClass('profit');
                // sub_ltp.addClass('loss');
              }
              else{
                ltp_text = ltp_val+' ( +'+ltp_change+'%)';
                sub_ltp.text(ltp_text);
                // sub_ltp.removeClass('loss');
                // sub_ltp.removeClass('profit');
                // sub_ltp.addClass('profit');
              }
          });
          if(positionsDict[sym_seg]!=undefined){
            for (var k in positionsDict[sym_seg]){
              avg_price = positionsDict[sym_seg][k]['last_order_average_price'];
              qty = positionsDict[sym_seg][k]['qty'];
              net_pnl = positionsDict[sym_seg][k]['final_pnl'];
              if(net_pnl==undefined)
                net_pnl = positionsDict[sym_seg][k]['pnl'];

              net_ret = positionsDict[sym_seg][k]['returns'];
              
              if(net_pnl==undefined)
                net_pnl = 0.0;
              if(net_ret==undefined)
                net_ret = 0.0;

              if(avg_price==0 && qty == 0 && net_pnl == 0){
                $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).html('<span style="color: #383838;font-weight: 400;">&nbsp;</span><span class="na_class">NA</span><!--<span style="color: #bfc7d1;font-weight: 400;" style="display:none>('+'NA'+'%)&nbsp;</span>-->');
                continue;
              }
              else if(net_pnl!=0 && qty==0)
              {
                if(net_pnl>=0){
                  $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).html('<span><img src="/static/imgs/icon-arrow-up-green.png">&nbsp;</span><span>+'+parseFloat(net_pnl).toFixed(2)+'&nbsp;</span><span style="display:none">('+net_ret+'%)&nbsp;</span>');
                }
                else{
                  $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).html('<span><img src="/static/imgs/icon-arrow-down-red.png">&nbsp;</span><span class="loss">'+parseFloat(net_pnl).toFixed(2)+'&nbsp;</span><span class="loss" style="display:none">( '+net_ret+'%)&nbsp;</span>');
                }
                // console.log(sym_seg+'average_price'+avg_price)

                // when qty is again at zero, clear target_prices div
                this_live = $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_'));
                this_live_target = this_live.closest('div[class^="token__"]').find('.target_prices');
                try{
                  this_live_target.html('');
                }catch(e){};

              }
              else if(qty!=0)
              {
                pnl = parseFloat((tick['LastTradedPrice']-avg_price)*qty+net_pnl).toFixed(2);
                if(avg_price!=0)
                  ret = parseFloat(100*(tick['LastTradedPrice']-avg_price+net_pnl)/avg_price).toFixed(2);
                else
                  ret=0

                // console.log(sym_seg+pnl);
                if(window.location.href.indexOf('/portfolio/')!=-1){
                  $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).closest('.positions_row_change').html('');
                }
                if(pnl>=0 && avg_price!=0){
                  if(avg_price==0){
                    $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).html('<span><img src="/static/imgs/icon-arrow-up-green.png">&nbsp;</span><span>+'+pnl+'&nbsp;</span><span>&nbsp;</span>');
                  }
                  else{
                    $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).html('<span><img src="/static/imgs/icon-arrow-up-green.png">&nbsp;</span><span>+'+pnl+'&nbsp;</span><span style="display:none">( +'+ret+'%)&nbsp;</span>');
                  }
                }
                else{
                  if(avg_price==0){
                    $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).html('<span><img src="/static/imgs/icon-arrow-down-red.png">&nbsp;</span><span class="loss">'+pnl+'&nbsp;</span><span class="loss">&nbsp;</span>');
                  }
                  else{
                    $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).html('<span><img src="/static/imgs/icon-arrow-down-red.png">&nbsp;</span><span class="loss">'+pnl+'&nbsp;</span><span class="loss" style="display:none">( '+ret+'%)&nbsp;</span>');
                  }
                }
                if($('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).data('tp')!=undefined && $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).data('sl')!=undefined && qty!=0){
                  this_live = $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_'));
                  this_live_target = this_live.closest('div[class^="token__"]').find('.target_prices');
                  
                  av_price = parseFloat(avg_price).toFixed(2);

                  tp = parseFloat($('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).data('tp'));
                  sl = parseFloat($('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).data('sl'));
                  
                  b_s = 'B';
                  b_s_class = 'bought_b';
                  if(qty>0 && tp && sl){
                    b_s = 'B';
                    b_s_class = 'bought_b';
                    tp_price = (1+tp/100)*avg_price;
                    sl_price = (1-sl/100)*avg_price;
                  }
                  else if(qty<0  && tp && sl){
                    b_s = 'S';
                    b_s_class = 'sold_s';
                    tp_price = (1-tp/100)*avg_price;
                    sl_price = (1+sl/100)*avg_price;
                  }
                  target_prices_html = '<p class="target_prices_first"><span class="'+b_s_class+'">'+b_s+'</span>&nbsp;<span class="taken_position_qty">'+qty+'</span><span class="taken_position_price">&nbsp;at '+av_price+'</span></p> <p class="target_prices_second " style="display:none"><span class="waiting_sl"><span>SL:</span>&nbsp;'+parseFloat(sl_price).toFixed(2)+'</span>&nbsp;<span class="waiting_tp"><span>TP:</span>&nbsp;'+parseFloat(tp_price).toFixed(2)+'</span></p> ';
                  this_live_target.html(target_prices_html);

                  // for updating TP, SL below pnl
                  try{
                        if(parseInt(g_status)==0){
                          this_live.parent().find('.target_prices_second').html('<span class="waiting_sl"><span>SL:</span>&nbsp;'+parseFloat(sl_price).toFixed(2)+'</span>&nbsp;<span class="waiting_tp"><span>TP:</span>&nbsp;'+parseFloat(tp_price).toFixed(2)+'</span>');
                        }else{
                          this_live.parent().find('.target_prices_second').html('');
                        }
                      }
                  catch(e){
                        this_live.parent().find('.target_prices_second').html('');
                    }
                }else{
                  this_live = $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_'));
                  this_live_target = this_live.closest('div[class^="token__"]').find('.target_prices');
                  try{
                    // for updating TP, SL below pnl
                    this_live.parent().find('.target_prices_second').html('');
                    this_live_target.html('');
                  }catch(e){};
                }
              }
            }
          }

          if(window.location.href.indexOf('/portfolio/')!=-1){
            // x.find('.positions_row_pnl');
            for(var l=0;l<x.length;l++)
            {
              port_qty = parseInt($(x[l]).find('.positions_row_quantity p').text());
              port_avg_price = parseFloat($(x[l]).find('.positions_row_avg_price p').text());
              port_multiplier = parseFloat($(x[l]).find('.positions_row_pnl').data('multiplier'));
              port_buy_value = parseFloat($(x[l]).find('.positions_row_pnl').data('buy_value'));
              port_sell_value = parseFloat($(x[l]).find('.positions_row_pnl').data('sell_value'));
              port_pnl = parseFloat($(x[l]).find('.positions_row_pnl').data('pnl'));
              if(!port_multiplier || !port_buy_value || !port_sell_value)
                port_pnl_partial = 0;
              if(port_avg_price!=0 && port_qty!=0 && port_avg_price!=NaN)
              {
                var tot_pnl_instrument = parseFloat((tick['LastTradedPrice']*port_qty*port_multiplier)+(port_sell_value-port_buy_value)).toFixed(2);
                if(tot_pnl_instrument>=0){
                      $(x[l]).find('.positions_row_pnl').html('<p class="profit">&#8377;&nbsp;'+parseFloat(tot_pnl_instrument).toFixed(2)+'<span>&nbsp;<!--(2.3%)--></span></p>');
                    }
                    else{
                      $(x[l]).find('.positions_row_pnl').html('<p class="loss">&#8377;&nbsp;'+parseFloat(tot_pnl_instrument).toFixed(2)+'<span>&nbsp;<!--(2.3%)--></span></p>');
                    }
              }else{
                var tot_pnl_instrument = port_pnl;
                if(port_pnl>=0){
                      $(x[l]).find('.positions_row_pnl').html('<p class="profit">&#8377;&nbsp;+'+parseFloat(tot_pnl_instrument).toFixed(2)+'<span>&nbsp;<!--(2.3%)--></span></p>');
                  }
                  else{
                    $(x[l]).find('.positions_row_pnl').html('<p class="loss">&#8377;&nbsp;'+parseFloat(tot_pnl_instrument).toFixed(2)+'<span>&nbsp;<!--(2.3%)--></span></p>');
                  }
              }
            }

            tot_pnl = 0;
            $('.positions_row_pnl').each(function(i,obj){
              tot_pnl+= parseFloat($(obj).find('p').text());
            });
            if(tot_pnl>=0)
            {
              $('.positions_total_pnl').html('&#8377;&nbsp; +'+parseFloat(tot_pnl).toFixed(2));
              $('.positions_total_pnl').removeAttr('style');
              $('.positions_total_pnl').removeClass('loss');
              $('.positions_total_pnl').addClass('profit');
            }
            else
            {
              $('.positions_total_pnl').html('&#8377;&nbsp;'+parseFloat(tot_pnl).toFixed(2));
              $('.positions_total_pnl').removeAttr('style');
              $('.positions_total_pnl').removeClass('profit');
              $('.positions_total_pnl').addClass('loss');
            }
          }
        }
      }
      if(event.data['notification-type']=='ltp-v3'){
        for(var t=0;t<event.data['ticks'].length;t++){
          tick = event.data['ticks'][t];
          // sym_segList[tick['Token']] = event.data['ticks'][0];
          sym_segDict = event.data['sym_segDict'];
          sym_seg = sym_segDict[tick['instrument_token']];
          x = $('.token__'+sym_seg.replace('&','\\&').replace(/ /g,'_-_'));
          x.each(function(i){
            // x[i].
              sub_ltp = $(x[i]).find('.ltp .sub_ltp')
              ltp_change = parseFloat(tick['change']).toFixed(2);
              ltp_val = tick['last_price'];
              if(ltp_change<0)
              {
                if(sym_seg.endsWith('CDS-FUT'))
                  ltp_text = parseFloat(ltp_val).toFixed(4);//+' ( '+ltp_change+'%)';
                else
                  ltp_text = parseFloat(ltp_val).toFixed(2);//+' ( '+ltp_change+'%)';
                // ltp_text = ltp_val;
                sub_ltp.text(ltp_text);
                // sub_ltp.removeClass('loss');
                // sub_ltp.removeClass('profit');
                // sub_ltp.addClass('loss');
              }
              else{
                if(sym_seg.endsWith('CDS-FUT'))
                  ltp_text = parseFloat(ltp_val).toFixed(4);//+' ( '+ltp_change+'%)';
                else
                  ltp_text = parseFloat(ltp_val).toFixed(2);//+' ( '+ltp_change+'%)';
                // ltp_text = ltp_val;
                sub_ltp.text(ltp_text);
                // sub_ltp.removeClass('loss');
                // sub_ltp.removeClass('profit');
                // sub_ltp.addClass('profit');
              }
          });
          if(positionsDict[sym_seg]!=undefined){
            for (var k in positionsDict[sym_seg]){
              avg_price = positionsDict[sym_seg][k]['last_order_average_price'];
              qty = positionsDict[sym_seg][k]['qty'];
              if(sym_seg.split('_')[1]=='CDS-FUT')
                qty = qty*1000;
              net_pnl = positionsDict[sym_seg][k]['final_pnl'];
              if(net_pnl==undefined)
                net_pnl = positionsDict[sym_seg][k]['pnl'];

              net_ret = positionsDict[sym_seg][k]['returns'];
              
              if(net_pnl==undefined)
                net_pnl = 0.0;
              if(net_ret==undefined)
                net_ret = 0.0;

              if(avg_price==0 && qty == 0 && net_pnl == 0){
                $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).html('<span style="color: #bfc7d1;font-weight: 400;">&nbsp;</span><span class="na_class">NA</span><!--<span style="color: #bfc7d1;font-weight: 400;" style="display:none>('+'NA'+'%)&nbsp;</span>-->');
                continue;
              }
              else if(net_pnl!=0 && qty==0)
              {
                if(net_pnl>=0){
                  $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).html('<span><img src="/static/imgs/icon-arrow-up-green.png">&nbsp;</span><span>&#8377;&nbsp;+'+parseFloat(net_pnl).toFixed(2)+'&nbsp;</span><span style="display:none">('+net_ret+'%)&nbsp;</span>');
                }
                else{
                  $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).html('<span><img src="/static/imgs/icon-arrow-down-red.png">&nbsp;</span><span class="loss">&#8377;&nbsp;'+parseFloat(net_pnl).toFixed(2)+'&nbsp;</span><span class="loss" style="display:none">( '+net_ret+'%)&nbsp;</span>');
                }
                // console.log(sym_seg+'average_price'+avg_price)

                // when qty is again at zero, clear target_prices div
                this_live = $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_'));
                this_live_target = this_live.closest('div[class^="token__"]').find('.target_prices');
                try{
                  this_live_target.html('<p class="target_prices_second"><span class="na_class">NA</span></p>');
                }catch(e){
                  console.log(e);
                };

              }
              else if(qty!=0)
              {
                pnl = parseFloat((tick['last_price']-avg_price)*qty+net_pnl).toFixed(2);
                if(avg_price!=0)
                  ret = parseFloat(100*(tick['last_price']-avg_price+net_pnl)/avg_price).toFixed(2);
                else
                  ret=0

                // console.log(sym_seg+pnl);
                if(window.location.href.indexOf('/portfolio/')!=-1){
                  $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).closest('.positions_row_change').html('');
                }
                if(pnl>=0 && avg_price!=0){
                  if(avg_price==0){
                    $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).html('<span><img src="/static/imgs/icon-arrow-up-green.png">&nbsp;</span><span>&#8377;&nbsp;+'+pnl+'&nbsp;</span><span>&nbsp;</span>');
                  }
                  else{
                    $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).html('<span><img src="/static/imgs/icon-arrow-up-green.png">&nbsp;</span><span>&#8377;&nbsp;+'+pnl+'&nbsp;</span><span style="display:none">( +'+ret+'%)&nbsp;</span>');
                  }
                }
                else{
                  if(avg_price==0){
                    $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).html('<span><img src="/static/imgs/icon-arrow-down-red.png">&nbsp;</span><span class="loss">&#8377;&nbsp;'+pnl+'&nbsp;</span><span class="loss">&nbsp;</span>');
                  }
                  else{
                    $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).html('<span><img src="/static/imgs/icon-arrow-down-red.png">&nbsp;</span><span class="loss">&#8377;&nbsp;'+pnl+'&nbsp;</span><span class="loss" style="display:none">( '+ret+'%)&nbsp;</span>');
                  }
                }
                if($('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).data('tp')!=undefined && $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).data('sl')!=undefined && qty!=0){
                  this_live = $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_'));
                  this_live_target = this_live.closest('div[class^="token__"]').find('.target_prices');

                  this_live_order = this_live.closest('div[class^="token__"]').find('.target_prices_order');
                  
                  av_price = parseFloat(avg_price).toFixed(2);

                  tp = parseFloat($('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).data('tp'));
                  sl = parseFloat($('#live__'+k.replace('&','\\&').replace(/ /g,'_-_')).data('sl'));
                  
                  b_s = 'B';
                  b_s_class = 'bought_b';
                  if(qty>0 && tp && sl){
                    b_s = 'B';
                    b_s_class = 'bought_b';
                    tp_price = (1+tp/100)*avg_price;
                    sl_price = (1-sl/100)*avg_price;
                  }
                  else if(qty<0  && tp && sl){
                    b_s = 'S';
                    b_s_class = 'sold_s';
                    tp_price = (1-tp/100)*avg_price;
                    sl_price = (1+sl/100)*avg_price;
                  }
                  target_prices_html ='<p class="target_prices_second"><span class="waiting_sl"><span>SL:</span>&nbsp;'+parseFloat(sl_price).toFixed(2)+'</span>&nbsp;<span class="waiting_tp"><span>TP:</span>&nbsp;'+parseFloat(tp_price).toFixed(2)+'</span></p>';
                  this_live_target.html(target_prices_html);

                  target_avg_price_html = '<p class="target_prices_first"><span class="'+b_s_class+'">'+b_s+'</span>&nbsp;<span class="taken_position_qty">'+qty+'</span><span class="taken_position_price">&nbsp;at '+av_price+'</span></p>';
                  this_live_order.html(target_avg_price_html);
                  // for updating TP, SL below pnl
                  try{
                        if(parseInt(g_status)==0){
                          this_live.parent().find('.target_prices_second').html('<span class="waiting_sl"><span>SL:</span>&nbsp;'+parseFloat(sl_price).toFixed(2)+'</span>&nbsp;<span class="waiting_tp"><span>TP:</span>:&nbsp;'+parseFloat(tp_price).toFixed(2)+'</span>');
                        }else{
                          this_live.parent().find('.target_prices_second').html('<span class="na_class">NA</span>');
                          this_live.parent().find('.target_prices_first').html('<span class="na_class">NA</span>');
                        }
                      }
                  catch(e){
                      console.log(e);
                        this_live.parent().find('.target_prices_second').html('<span class="na_class">NA</span>');
                        this_live.parent().find('.target_prices_second').html('<span class="na_class">NA</span>');
                    }
                }else{
                  this_live = $('#live__'+k.replace('&','\\&').replace(/ /g,'_-_'));
                  this_live_target = this_live.closest('div[class^="token__"]').find('.target_prices');

                  this_live_order = this_live.closest('div[class^="token__"]').find('.target_prices_order');
                  try{
                    // for updating TP, SL below pnl
                    this_live.parent().find('.target_prices_second').html('<span class="na_class">NA</span>');
                    this_live_target.html('<p class="target_prices_second"><span class="na_class">NA</span></p>');

                    this_live.parent().find('.target_prices_first').html('<span class="na_class">NA</span>');
                    this_live_order.html('<p class="target_prices_first"><span class="na_class">NA</span></p>');
                  }catch(e){
                    console.log(e);
                  };
                }
              }
            }
          }

          if(window.location.href.indexOf('/portfolio/')!=-1){
            // x.find('.positions_row_pnl');
            for(var l=0;l<x.length;l++)
            {
              port_qty = parseInt($(x[l]).find('.positions_row_quantity p').text().replace('Qty: ',''));
              port_avg_price = parseFloat($(x[l]).find('.positions_row_avg_price p').text().replace('?????',''));
              port_multiplier = parseFloat($(x[l]).find('.positions_row_pnl').data('multiplier'));
              port_buy_value = parseFloat($(x[l]).find('.positions_row_pnl').data('buy_value'));
              port_sell_value = parseFloat($(x[l]).find('.positions_row_pnl').data('sell_value'));
              port_pnl = parseFloat($(x[l]).find('.positions_row_pnl').data('pnl'));
              if(!port_multiplier || !port_buy_value || !port_sell_value)
                port_pnl_partial = 0;

              port_pnl_change = 0;
              if(port_avg_price!=0 && port_qty!=0 && port_avg_price!=NaN)
              {
                var tot_pnl_instrument = parseFloat((tick['last_price']*port_qty*port_multiplier)+(port_sell_value-port_buy_value)).toFixed(2);
                port_pnl_change = parseFloat((tot_pnl_instrument/(port_avg_price*port_multiplier*port_qty))*100).toFixed(2)
                if(tot_pnl_instrument>=0){
                      $(x[l]).find('.positions_row_pnl').html('<p class="profit">'+parseFloat(tot_pnl_instrument).toFixed(2)+'<span>&nbsp;<!--(2.3%)--></span></p>');
                    // console.log(port_avg_price);
                     $(x[l]).find('.positions_row_order_details p').html(port_pnl_change+'%<span>Details</span>');
                     // 4.50%<span>Details</span>
                    }
                    else{
                      $(x[l]).find('.positions_row_pnl').html('<p class="loss">'+parseFloat(tot_pnl_instrument).toFixed(2)+'<span>&nbsp;<!--(2.3%)--></span></p>');
                    // console.log(port_avg_price);

                      $(x[l]).find('.positions_row_order_details p').html(port_pnl_change+'%<span>Details</span>'); 
                    }
              }else{
                var tot_pnl_instrument = port_pnl;
                if(port_pnl>=0){
                      $(x[l]).find('.positions_row_pnl').html('<p class="profit">'+parseFloat(tot_pnl_instrument).toFixed(2)+'<span>&nbsp;<!--(2.3%)--></span></p>');
                      $(x[l]).find('.positions_row_order_details p').html('0.0%<span>Details</span>');
                  }
                  else{
                    $(x[l]).find('.positions_row_pnl').html('<p class="loss">'+parseFloat(tot_pnl_instrument).toFixed(2)+'<span>&nbsp;<!--(2.3%)--></span></p>');
                    $(x[l]).find('.positions_row_order_details p').html('0.0%<span>Details</span>');
                  }
              }
            }

            tot_pnl = 0;
            temp_pnl = 0;
            $('.positions [id^=ulive__]').each(function(i,obj){
              temp_pnl = parseFloat($(obj).find('p').text());
              if(!isNaN(temp_pnl))
                tot_pnl+= temp_pnl;
            });
            if(tot_pnl>=0)
            {
              $('.positions_total_pnl').html('+'+parseFloat(tot_pnl).toFixed(2));
              $('.positions_total_pnl').removeAttr('style');
              $('.positions_total_pnl').removeClass('loss');
              $('.positions_total_pnl').addClass('profit');
            }
            else
            {
              $('.positions_total_pnl').html(''+parseFloat(tot_pnl).toFixed(2));
              $('.positions_total_pnl').removeAttr('style');
              $('.positions_total_pnl').removeClass('profit');
              $('.positions_total_pnl').addClass('loss');
            }
            if(port_pnl_change>=0)
            {
              $(x[l]).find('.positions_row_order_details p').removeAttr('style');
              $(x[l]).find('.positions_row_order_details p').removeClass('loss');
              $(x[l]).find('.positions_row_order_details p').addClass('profit');
            }
            else
            {
              $(x[l]).find('.positions_row_order_details p').removeAttr('style');
              $(x[l]).find('.positions_row_order_details p').removeClass('profit');
              $(x[l]).find('.positions_row_order_details p').addClass('loss');
            }
          }
        }
      }
      if(event.data['notification-type']=='state'){ // this is produced by worker.js
        if(event.data['state']=='ready'){
          refresh_ltp_subscription();
          refresh_pnl_subscription();
          // setTimeout(function(){ 
          //     update_admin();
          //   }, 20000);
        }
      }
      if(event.data['price_trigger-notification']!=undefined){ // TP/SL notification
        notificationsDict['unread_count']+=1;
        notificationsDict['notifications'].push(event.data);
        refresh_notification();
        $('#notification_details').show();
        refresh_order_log();
        notification_audio.play();
      }
      if(event.data['notification-type']=='order-webhook'){ // this is produced by worker.js
        // refresh_notification();
        notificationsDict['notifications'].push(event.data);
        notificationsDict['unread_count']+=1;
        refresh_notification();
        $('#notification_details').show();
        refresh_order_log();
        notification_audio.play();
        // refresh_positions();
      }
      // console.log(event.data);
      // document.getElementById('result').innerText = event.data;
   };
   // sym_seg='NSE_SBIN';
   // w.postMessage(['subscribe',sym_seg]);
}
});
function refresh_order_log(){
  if(window.location.href.indexOf('/order_log')!=-1){
    try{
      status = parseInt($(".algo_status").val())
      pagination = 0;
      // load_order_log(status,10,pagination);
      load_order_log_dict(0,g_limit,0);
      load_order_log_dict(-1,g_limit,0);
    }
    catch(e){
      
    }
  }
}
function refresh_ltp_subscription(){
  x = $("[class^=token__]");
  x.each(function(i){
    [t,seg_sym]=x[i].className.split('__');
    // if(seg_sym.indexOf('_')!=-1){
    //   [g,s] = seg_sym.split('_');
    //   if(s.endsWith('FUT') && g.indexOf('FUT')==-1){
    //     g = g+'-FUT';
    //     seg_sym = g+'_'+s;
    //   }
    // }
    if (typeof(w) != "undefined") {
      // console.log(seg_sym);
      w.postMessage(['subscribe',seg_sym]);
    }
  });
}

function show_autocomplete_basket(){
  $("#create_basket_equities_input").autocomplete({
    source: function(request,response){
    params = {'query':request['term'].toLowerCase()}
    $.get('/autocomplete/', params,function(data) {
      // alert(data);
      if(data['status']=='success'){

        response($.map(data['results'], function (el) {
          if(el[2]!='basket')
           return {
             label: el[1]+' '+el[3],
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
      $("#create_basket_equities_input").val('');
      $("#create_basket_equities_input").focus();
      }
     $("#create_basket_equities_input").val('');
     $("#create_basket_equities_input").focus();
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
      }
      // if(Object.keys(equity_added).length>=5)
      // {
      //   show_snackbar(null,'Cannot add more than 5 instruments');
      //   return false;
      // }
      // if(equity_added[val[0]]==null)
      // {
          // $('.equities_list').append('<span><span data-syms="'+val[0]+'_'+val[1]+'">'+ui.item.value+'</span><span><img src="/static/imgs/close.png"></span></span>');
          var equity_already_added = false;
          var seg_sym = val[0]+'_'+val[1];
          if($('.equities_list').find('.basket_instrument').length>=20){
            show_snackbar(null,'Cannot add more than 20 instruments');
            return false;
          }
          $('.equities_list').find('.basket_instrument').each(function(e,obj){
            if($(obj).data('syms')==seg_sym){
              equity_already_added = true;
            }
          });
          if(!equity_already_added){
            $('.equities_list').append('<span><span class="basket_instrument" data-syms="'+val[0]+'_'+val[1]+'">'+ui.item.value+'</span><span><img src="/static/imgs/icon-strategy-remove_equity.png"></span></span>');
            // symbols.push(ui.item.value.split(' ').reverse());
            // ui.item.value = "";
            $(".equities_list img").click(function(){
              // $(this).parentsUntil('.equities_list').hide();
              x = $($($(this).parentsUntil('.equities_list')).find('span')[0]).data('syms');
              if(x!=null){
                [sym,seg] = x.split('_');
                // delete equity_added[sym];
              }
              $(this).parentsUntil('.equities_list').remove();
              
              // if(Object.keys(equity_added).length==0){
              //   $($('.adding_equities_section div span')[0]).css("background-color", "hsla(162, 14%, 94%, 1)");
              //   $($('.adding_equities_section div span')[0]).css("border-color", "#dee7f1");
              // }
            });
          
          // equity_added[val[0]]=val[1];
          $($('.adding_equities_section div span')[0]).css("background-color", "#06d092");
          $($('.adding_equities_section div span')[0]).css("border-color", "#bdfbe8");
        }
      // }
      $("#create_basket_equities_input").val('');
      $("#create_basket_equities_input").focus();
      return false
     }
  });
}
function send_feedback(){
  $(".feedback_popup").show();
  $('#feedback_details_text').val('');
  $("body").addClass('body_scroll');
  $('.send_feedback').addClass('send_feedback_disabled');
}
function validate_feedback(){
  if($('#feedback_details_text').val().trim()!=''){
    $('.send_feedback').removeClass('send_feedback_disabled');
  }else{
    $('.send_feedback').addClass('send_feedback_disabled');
  }
}
function my_baskets_load(){
  // $("#create_basket_equities_input").autocomplete({
  //   source: function(request,response){
  //   params = {'query':request['term'].toLowerCase()}
  //   $.get('/autocomplete/', params,function(data) {
  //     // alert(data);
  //     if(data['status']=='success'){

  //       response($.map(data['results'], function (el) {
  //          return {
  //            label: el[1]+' '+el[3],
  //            value: el[1]+' '+el[3] //assumption, symbols and segment name does not have space in between
  //          };
  //        }));
  //     }
  //   });
  //   },
  //   delay: 0,
  //   minLength: 2,
  //   change: function(event,ui)
  //   {
  //   if (ui.item==null)
  //     {
  //     $("#create_basket_equities_input").val('');
  //     $("#create_basket_equities_input").focus();
  //     }
  //    $("#create_basket_equities_input").val('');
  //    $("#create_basket_equities_input").focus();
  //    // ui.item.value = "";
  //   },
  //    select:function(event, ui){
  //     // console.log('selected');
  //     // console.log(ui['item'])
  //     val = ui.item.value.split(' ');
  //     if(val.length>2){
  //       // var temp = val[1];
  //       val[0]=val[0]+' '+val[1];
  //       val[1]=val[2];
  //     }
  //     // if(Object.keys(equity_added).length>=5)
  //     // {
  //     //   show_snackbar(null,'Cannot add more than 5 instruments');
  //     //   return false;
  //     // }
  //     // if(equity_added[val[0]]==null)
  //     // {
  //         // $('.equities_list').append('<span><span data-syms="'+val[0]+'_'+val[1]+'">'+ui.item.value+'</span><span><img src="/static/imgs/close.png"></span></span>');
  //         var equity_already_added = false;
  //         var seg_sym = val[0]+'_'+val[1];
  //         if($('.equities_list').find('.basket_instrument').length>=20){
  //           show_snackbar(null,'Cannot add more than 20 instruments');
  //           return false;
  //         }
  //         $('.equities_list').find('.basket_instrument').each(function(e,obj){
  //           if($(obj).data('syms')==seg_sym){
  //             equity_already_added = true;
  //           }
  //         });
  //         if(!equity_already_added){
  //           $('.equities_list').append('<span><span class="basket_instrument" data-syms="'+val[0]+'_'+val[1]+'">'+ui.item.value+'</span><span><img src="/static/imgs/icon-strategy-remove_equity.png"></span></span>');
  //           // symbols.push(ui.item.value.split(' ').reverse());
  //           // ui.item.value = "";
  //           $(".equities_list img").click(function(){
  //             // $(this).parentsUntil('.equities_list').hide();
  //             x = $($($(this).parentsUntil('.equities_list')).find('span')[0]).data('syms');
  //             if(x!=null){
  //               [sym,seg] = x.split('_');
  //               // delete equity_added[sym];
  //             }
  //             $(this).parentsUntil('.equities_list').remove();
              
  //             // if(Object.keys(equity_added).length==0){
  //             //   $($('.adding_equities_section div span')[0]).css("background-color", "hsla(162, 14%, 94%, 1)");
  //             //   $($('.adding_equities_section div span')[0]).css("border-color", "#dee7f1");
  //             // }
  //           });
          
  //         // equity_added[val[0]]=val[1];
  //         $($('.adding_equities_section div span')[0]).css("background-color", "#06d092");
  //         $($('.adding_equities_section div span')[0]).css("border-color", "#bdfbe8");
  //       }
  //     // }
  //     $("#create_basket_equities_input").val('');
  //     $("#create_basket_equities_input").focus();
  //     return false
  //    }
  // });

  // $('.create_baskets_body, .create_baskets_footer').hide();$('.my_baskets_popup').fadeIn();$('.baskets_body, .baskets_footer').show();$('body').addClass('body_scroll');

   // console.log(instruments_list);
  try{
    // var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    // var basket_name = $('#create_basket_name').val()
    params_admin = {
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/user_baskets/?complete=true',
      "method": "GET",
      "headers": {
      },
      "data":params_admin,
      "timeout": 10000,//40 sec timeout
    }
    $('.baskets_list').html('<div class="baskets_loading"><p>Loading...</p><img src="/static/imgs/button-loading-rect.gif"></div>');
    $('.create_baskets_body, .create_baskets_footer').hide();$('.my_baskets_popup').fadeIn();$('.baskets_body, .baskets_footer').show();$('body').addClass('body_scroll');
    $.ajax(settings).done(function (data){
          if(data['status']=="success"){
            $('.baskets_list').html('');
            for(var i=0;i<data['basket_names_list'].length;i++){
              // data['basket_names_list']
              basket_item = '<div class="basket"><p>'+data['basket_names_list'][i]+'<span class="basket_number">'+JSON.parse(data['baskets'][data['basket_names_list'][i]]).length+'</span></p><button class="edit_basket" onclick="edit_basket(event,\''+data['basket_names_list'][i]+'\')" data-event="not-clicked"><img src="/static/imgs/new/create.svg"></button><button class="delete_basket" onclick="delete_basket(event,\''+data['basket_names_list'][i]+'\')" data-event="not-clicked"><img src="/static/imgs/new/delete.svg"></button></div>';
              $('.baskets_list').append(basket_item);
            }
          $(".basket").hover(function(){
            $(this).find("button").toggle();
          });
          }
          else{
            show_snackbar(null,data['msg']);
          }
    }).fail(
      function(){
        show_snackbar(null,"Error connecting to server, try again.");
        $('.baskets_list').html('<div class="baskets_loading"><p>Error connecting to server, try again.</p></div>');
      }).complete(function(){
      });
  }
  catch(e){
    // $('.create_baskets_body, .create_baskets_footer').hide();$('.baskets_body, .baskets_footer').fadeIn();
  }
}

function edit_basket(event,basket_name){
  try{
    if($(event.target).data('event',"clicked")=="clicked"){
      return;
    }
    // var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    // var basket_name = $('#create_basket_name').val()
    params_admin = {
            'basket_name':basket_name
            };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/user_baskets/',
      "method": "GET",
      "headers": {
      },
      "data":params_admin,
      "timeout": 10000,//40 sec timeout
    }
    $(event.target).html('<img src="/static/imgs/button-loading-rect.gif" style="height: 5px;">');
    $(event.target).data('event',"clicked");
    $(event.target).css('background-color','#f6a622');
    $.ajax(settings).done(function (data){
          if(data['status']=="success"){
            basket_body = '<div class="baskets_header"><p>Edit basket</p></div><div class="create_basket_body"><p>Basket name</p><input type="text" name="" id="create_basket_name" placeholder="Ex: Power sector" data-param="edit" value="'+data['basket_name']+'" readonly><p>Instruments</p><input type="text" name="search_eq" id="create_basket_equities_input" placeholder="Add instruments"><div class="equities_list"></div></div>'
            $('.create_baskets_body').html(basket_body);
            data['basket_instruments'] = JSON.parse(data['basket_instruments']);
            for(var i=0;i<data['basket_instruments'].length;i++){
              // data['basket_instruments']
              var sym_seg = data['basket_instruments'][i].split('_'); 
              basket_item = '<span><span class="basket_instrument" data-syms="'+data['basket_instruments'][i]+'">'+sym_seg[0]+' '+sym_seg[1]+'</span><span><img src="/static/imgs/icon-strategy-remove_equity.png"></span></span>';
              $('.equities_list').append(basket_item);
            }
          // $(".basket").hover(function(){
          //   $(this).find("button").toggle();
          // });
          }
          else{
            show_snackbar(null,data['msg']);
          }
    }).fail(
      function(){
      show_snackbar(null,"Error connecting to server, try again.");
      $(event.target).html('Edit');
      $(event.target).data('event',"not-clicked");
      $(event.target).css('background-color','#FFFFFF');
      // $(event.target).css('display','none');
    }).complete(function(){
      $('.baskets_body, .baskets_footer').hide();$('.create_baskets_body, .create_baskets_footer').fadeIn();
      show_autocomplete_basket();
      $(".equities_list img").click(function(){
        $(this).parentsUntil('.equities_list').remove();
      });
      $(event.target).html('Edit');
      $(event.target).data('event',"not-clicked");
      $(event.target).css('background-color','#FFFFFF');
      // $(event.target).css('display','none');
      // $(".basket").hover(function(){
      //   $(this).find("button").toggle();
      // });
    });
  }
  catch(e){
    // $('.create_baskets_body, .create_baskets_footer').hide();$('.baskets_body, .baskets_footer').fadeIn();
    $(event.target).html('Edit');
    $(event.target).data('event',"not-clicked");
    $(event.target).css('background-color','#FFFFFF');
  }

}

function delete_basket(event,basket_name){
    try{

    if($(event.target).data('event',"clicked")=="clicked"){
      return;
    }
    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    params_admin = {
                    'csrfmiddlewaretoken':csrfmiddlewaretoken,
                    "basket_name":basket_name,
                    "del":true
            };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/user_baskets/',
      "method": "POST",
      "headers": {
      },
      "data":params_admin,
      "timeout": 10000,//40 sec timeout
    }
    
    $(event.target).html('<img src="/static/imgs/button-loading-rect.gif" style="height: 5px;">');
    $(event.target).data('event',"clicked");
    $(event.target).css('background-color','#ff4343');

    $.ajax(settings).done(function (data){
          if(data['status']=="success"){
            show_snackbar(null,"Basket deleted","success");
          }
          else{
            show_snackbar(null,data['msg']);
          }
    }).fail(
      function(){
        show_snackbar(null,"Error connecting to server, try again.");
        $(event.target).html('Delete');
        $(event.target).data('event',"not-clicked");
        $(event.target).css('background-color','#FFFFFF');
      }).complete(function(){
        // $('.create_baskets_body, .create_baskets_footer').hide();$('.baskets_body, .baskets_footer').fadeIn();
        my_baskets_load();
      });
  }
  catch(e){
    // $('.create_baskets_body, .create_baskets_footer').hide();$('.baskets_body, .baskets_footer').fadeIn();
    $(event.target).html('Delete');
    $(event.target).data('event',"not-clicked");
    $(event.target).css('background-color','#FFFFFF');
  }
}

function create_basket(){
  $('.baskets_body, .baskets_footer').hide();$('.create_baskets_body, .create_baskets_footer').fadeIn();
  basket_body = '<div class="baskets_header"><p>New basket</p></div><div class="create_basket_body"><p>Basket name</p><input type="text" name="" id="create_basket_name" placeholder="Ex: Power sector" data-param=""><p>Instruments</p><input type="text" name="search_eq" id="create_basket_equities_input" placeholder="Add instruments"><div class="equities_list"></div></div>'
  $('.create_baskets_body').html(basket_body);
  show_autocomplete_basket();
}

function save_basket(){
  var instruments_list = [];
  $('.equities_list .basket_instrument').each(function(index,element){
    if($($(element)[0]).data('syms')!=undefined){
      // console.log($($(element)[0]).data('syms'));
      instruments_list.push($($(element)[0]).data('syms'));
    }
  });
  if(instruments_list.length<1){
    show_snackbar(null,'No scrips added');
    return
  }
  // console.log(instruments_list);
  try{
    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    var basket_name = $('#create_basket_name').val();

    var edit = $('#create_basket_name').data('param');
    if(edit=="edit"){
      edit = true;
    }else{
      edit = false;
    }
    params_admin = {
                    'csrfmiddlewaretoken':csrfmiddlewaretoken,
                    "basket_name":basket_name,
                    "basket_edit":edit,
                    "basket_instruments":JSON.stringify(instruments_list)
            };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/user_baskets/',
      "method": "POST",
      "headers": {
      },
      "data":params_admin,
      "timeout": 10000,//40 sec timeout
    }
    
    $.ajax(settings).done(function (data){
          if(data['status']=="success"){
            show_snackbar(null,"Basket saved","success");
            $('.create_baskets_body, .create_baskets_footer').hide();$('.baskets_body, .baskets_footer').fadeIn();
            my_baskets_load();
          }
          else{
            show_snackbar(null,data['msg']);
          }
    }).fail(
      function(){
      }).complete(function(){
      });
  }
  catch(e){
    // $('.create_baskets_body, .create_baskets_footer').hide();$('.baskets_body, .baskets_footer').fadeIn();
  }
}

function update_admin(){
  loc = 'some_page';
  if(window.location.href.indexOf('dashboard')!=-1)
    loc = 'dashboard';
  if(window.location.href.indexOf('algorithm')!=-1 || window.location.href.indexOf('strategy')!=-1)
    loc = 'algorithm';
  if(window.location.href.indexOf('backtest')!=-1)
    loc = 'backtest';
  if(window.location.href.indexOf('order_log')!=-1 || window.location.href.indexOf('deployed')!=-1)
    loc = 'order_log';
  if(window.location.href.indexOf('portfolio')!=-1)
    loc = 'portfolio';
  if(window.location.href.indexOf('myaccount')!=-1)
    loc = 'myaccount';
  if(window.location.href.indexOf('alerts')!=-1)
    loc = 'alerts';
  if(window.location.href.indexOf('help')!=-1)
    loc = 'help';
  try{
    params_admin = {"view":loc , "client_id": uid};
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": "https://notif.streak.tech/handle_post/",
      "method": "POST",
      "processData": false,
      "contentType": false,
      "mimeType": "multipart/form-data",
      "timeout": 2000,
      "data": JSON.stringify(params_admin)
    }
    
    $.ajax(settings).done(function (data){
    }).fail(
      function(){
      }).complete(function(){
          setTimeout(function(){ 
            update_admin();
          }, 20000);
      });
  }
  catch(e){

  }
}
function refresh_pnl_subscription_portfolio(){
  x = $("[id^=ulive__]"); // this is of updating positions in portfolio positions page 
  x.each(function(i){
    [t,dep_id]=x[i].id.split('__');
    if (typeof(w) != "undefined") {
      // w.postMessage(['subscribe-pnl',dep_id]);
      update_positionsDict(dep_id);
    }
  });
}
function refresh_pnl_subscription(){
  x = $("[id^=live__]");
  x.each(function(i){
    [t,dep_id]=x[i].id.split('__');
    if (typeof(w) != "undefined") {
      // w.postMessage(['subscribe-pnl',dep_id]);
      update_positionsDict(dep_id);
    }
  });
}
function update_positionsDict(dep_id){
  // fetch_open_positions(dep_id);
  var params = {
        'deployment_uuid':dep_id,
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
    };

  $.ajax(settings).done(function (msg){
    if(msg.status=='success')
      {
        positions = msg.positions;
        pnl = msg.pnl;
        // seg_sym = [];
        // for(var k in positions) seg_sym.push(k)
        seg_sym =[msg.seg+'_'+msg.sym]
        if(positionsDict[seg_sym[0]] == undefined)
            positionsDict[seg_sym[0]]={};

        positionsDict[seg_sym[0]][dep_id]={
          "last_order_average_price":positions.last_order_average_price,
          "qty":positions.qty,
          "pnl":pnl.final_pnl
        }
      }
  });
}
// $(window).unload(function () {
// });
// window.addEventListener( 'beforeunload', function(ev) { 
//      // alert("Are you sure?");
//     return ev.returnValue = 'You will no longer be able to receive notifications';
// })
function log_in_kite(param=''){
  // newWindow = popupWindowCenter('/broker_login?redirect=popup','Kite login','500','700')
  //   newWindow.onunload = function(e){
  //     // win = window.opener;
  //     // if(!win.closed)
  //     if(e.target.documentURI.indexOf('status=success&request_token=')!=-1){
  //       // alert('yo');
  //       window.location='/dashboard';
  //     }
  //   }
  window.location='/broker_login/'+param;
}
function place_order(event,notification_uuid,deployment_uuid,algo_uuid,seg,sym,quantity,order_type,transaction_type,product,validity,algo_name,dt=0,trigger_price=0.0){
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
        'csrfmiddlewaretoken':csrfmiddlewaretoken
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
    });
}

function place_order_tpsl(event,notification_uuid,deployment_uuid,algo_uuid,token,quantity,order_type,transaction_type,product,validity,tpsl_key,algo_name,dt=0){
    var me = $(event.target);

    if ( $(me).data('requestRunning') ) {
        return;
    }
    $(me).data('requestRunning', true);
    $(me).attr('style','cursor:no-drop');

    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    var params = {
        'notification_uuid':notification_uuid,
        'deployment_uuid':deployment_uuid,
        'algo_uuid':algo_uuid,
        'token':token,
        'order_type':order_type,
        'transaction_type':transaction_type,
        'quantity':quantity,
        'product':product,
        'validity':validity,
        'tpsl_key':tpsl_key,
        'algo_name':algo_name,
        'csrfmiddlewaretoken':csrfmiddlewaretoken
    }

    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/place_order_tpsl/',
      "method": "POST",
      "headers": {
      },
      "data":params,
      "timeout": 10000,//40 sec timeout
    }
    if(dt>60000*5){
      notificationsDict['used'][notification_uuid]=1;
      $(me).closest('.notif_window').remove();
      show_snackbar(null,'This notification is expired!');
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
          }
          else{
            console.log(msg.status);
            notificationsDict['used'][notification_uuid]=1;
            $(me).closest('.notif_window').remove();
            $('.exit_position, .stop_options').hide();$('.algo_stopped').show();
            show_snackbar(null,'Order sent to exchange','success');
            refresh_order_log();
            // setTimeout(function(){ 
            //   // window.location = '/dashboard/';
            //   }, 2000);
            // TODO hide the notification or delete it
          }
        }else{
          show_snackbar(null,'Order not placed, please try again.');
          $('.login_required_popup').show();
        }
    }).fail(function(msg){
        show_snackbar(null,'Connection error, please try again.');
    }).complete(function(){
            $(me).data('requestRunning', false);
            $(me).removeAttr('style');
    });
}

function cancel_notifications(event,deployment_uuid,notification_uuid='',notif_state=''){
    var me = $(event.target);

    // if ( $(me).data('requestRunning') ) {
    //     return;
    // }
    // $(me).data('requestRunning', true);
    // notificationsList={}
    var params = {
          // 'deployment_uuid':dep_id,
      };
    var settings = {
        "async": true,
        "crossDomain": true,
        "url": '/notifications_handler/',
        "method": "GET",
        "headers": {
        },
        "data":params,
        "timeout": 60000,//40 sec timeout
      };
    $.ajax(settings).done(function (msg){
      if(msg.status=='success')
        {
          notificationsDict = msg['results'];
          if(notificationsDict['used'][notification_uuid]==undefined){

              notificationsDict['used'][notification_uuid]=1;
              $(me).attr('style','cursor:no-drop');
              // $(me).closest('.notif_window').remove();
              keep_position_open_notif(event,deployment_uuid);

              var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
              var params = {
                  'notification_uuid':notification_uuid,
                  'csrfmiddlewaretoken':csrfmiddlewaretoken
              }
              var settings = {
                "async": true,
                "crossDomain": true,
                "url": '/mark_notification_used/',
                "method": "POST",
                "headers": {
                },
                "data":params,
                "timeout": 10000,//40 sec timeout
              }
              $.ajax(settings).done(function (msg){
                console.log('notification_marked used');
                $(me).closest('.notif_window').remove();
                  try{
                    params_admin = {
                                    "view":'action~cancel_notif~'+deployment_uuid+'~'+notif_state,
                                    "client_id":uid
                                  };
                    var settings_params_admin = {
                      "async": true,
                      "crossDomain": true,
                      "url": "https://notif.streak.tech/handle_post/",
                      "method": "POST",
                      "processData": false,
                      "contentType": false,
                      "mimeType": "multipart/form-data",
                      "timeout": 2000,
                      "data": JSON.stringify(params_admin)
                    }
                    
                    $.ajax(settings_params_admin).done(function (data){
                    }).fail(
                      function(){
                      }).complete(function(){
                      });
                  }
                  catch(e){

                  }
              });

          }else{
            $(me).closest('.notif_window').remove();
          }
          refresh_notification();
          if(window.location.href.indexOf('#notif')!=-1)
            $('#notification_details').show();
        }
    });
}

function cancel_notifications_discipline(event,deployment_uuid,notification_uuid=''){
    // var me = $(event.target);

    // // if ( $(me).data('requestRunning') ) {
    // //     return;
    // // }
    // // $(me).data('requestRunning', true);
    // fetch_notifications();
    // notificationsDict['used'][notification_uuid]=1;
    // $(me).attr('style','cursor:no-drop');
    // // $(me).closest('.notif_window').remove();
    // // keep_position_open_notif(event,deployment_uuid);

    // var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    // var params = {
    //     'notification_uuid':notification_uuid,
    //     'csrfmiddlewaretoken':csrfmiddlewaretoken
    // }
    // var settings = {
    //   "async": true,
    //   "crossDomain": true,
    //   "url": '/mark_notification_used/',
    //   "method": "POST",
    //   "headers": {
    //   },
    //   "data":params,
    //   "timeout": 10000,//40 sec timeout
    // }
    // $.ajax(settings).done(function (msg){
    //   console.log('notification_marked used');
    // });
    var me = $(event.target);

    // if ( $(me).data('requestRunning') ) {
    //     return;
    // }
    // $(me).data('requestRunning', true);
    // notificationsList={}
    var params = {
          // 'deployment_uuid':dep_id,
      };
    var settings = {
        "async": true,
        "crossDomain": true,
        "url": '/notifications_handler/',
        "method": "GET",
        "headers": {
        },
        "data":params,
        "timeout": 60000,//40 sec timeout
      };
    $.ajax(settings).done(function (msg){
      if(msg.status=='success')
        {
          notificationsDict = msg['results'];
          if(notificationsDict['used'][notification_uuid]==undefined){

              notificationsDict['used'][notification_uuid]=1;
              $(me).attr('style','cursor:no-drop');
              $(me).closest('.notif_window').remove();
              // keep_position_open_notif(event,deployment_uuid);

              var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
              var params = {
                  'notification_uuid':notification_uuid,
                  'csrfmiddlewaretoken':csrfmiddlewaretoken
              }
              var settings = {
                "async": true,
                "crossDomain": true,
                "url": '/mark_notification_used/',
                "method": "POST",
                "headers": {
                },
                "data":params,
                "timeout": 10000,//40 sec timeout
              }
              $.ajax(settings).done(function (msg){
                console.log('notification_marked used');
                $(me).closest('.notif_window').remove();
              });

          }else{
            $(me).closest('.notif_window').remove();
          }
          refresh_notification();
          if(window.location.href.indexOf('#notif')!=-1)
            $('#notification_details').show();
        }
    });
}

function keep_position_open_notif(event,deployment_uuid){
    var me = $(event.target);
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
                show_snackbar(null,'Algo stopped since notification was cancelled');

                // show_snackbar(null,'Algo has been stopped successfully','success');
                // $('.exit_position, .stop_options').hide();$('.algo_stopped').show();
                // $('#close_orders_popup_div').unbind('click');
                // $('#close_orders_popup_div').prop('onclick',null).off('click');
                // $('#close_orders_popup_div').prop('onclick',function(){
                // setTimeout(function(){ window.location = '/order_log/'; }, 3000);
                // }).on('click');
                $(me).closest('.notif_window').remove();

            }
        else
           { 
            // alert(msg.status);
            // $('.force_stop_popup').hide();
            // show_snackbar(null,'Error occured, please try again');
            show_snackbar(null,'Error occured, please try again');
            $(me).attr('style','pointer');
           }

    }).fail(function(msg){
        // console.log(msg);
        // $('.force_stop_popup').hide();
        // show_snackbar(null,'Error occured, please try again');
        show_snackbar(null,'Error occured, please try again');
        $(me).attr('style','pointer');
    });
}

function load_basket(basket_name){
  if(Object.keys(equity_added).length>=20)
    {
      show_snackbar(null,'Cannot add more than 20 instruments');
      return false;
    }

  params_admin = {
            'basket_name':basket_name
            };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/user_baskets/',
      "method": "GET",
      "headers": {
      },
      "data":params_admin,
      "timeout": 10000,//40 sec timeout
    }
    
    $.ajax(settings).done(function (data){
    if(data['status']=="success"){
      var val = null;
      data['basket_instruments'] = JSON.parse(data['basket_instruments']);
      for(var i=0;i<data['basket_instruments'].length;i++){
        if(Object.keys(equity_added).length>=20)
        {
          show_snackbar(null,'Cannot add more than 20 instruments');
          return false;
        }
        val = data['basket_instruments'][i].split('_'); 
        if(equity_added[val[0]]==null)
          {
            $('.added_equities').append('<span><span data-syms="'+val[0]+'_'+val[1]+'">'+val[0]+' '+val[1]+'</span><span><img src="/static/imgs/icon-strategy-remove_equity.png"></span></span>');
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
      }
    }
  });
 }

function skip_tour(){
  $('.welcome_popup').fadeOut();
  first_login_complete(ss,'first_time_skip');
}
function start_first_tour(){
  $('.welcome_popup').hide();
  hopscotch.startTour(dashboard_tour());
}
function start_subscription_popup(subscription_instance='first'){
  try{
    $('#start_subscription_btn').attr('style','background-color: #989fa7;border: 1px solid #bfc7d1;');
    $('#start_subscription_btn').attr('onclick','show_snackbar(null,\'Check the box if you are sure\')');
    $('#start_subscription_checkbox').removeAttr('checked')
  }
  catch(e){

  }
  $('.subscription_popup').show();
  // start_subscription(subscription_instance='first');
}
function start_subscription(subscription_instance='first'){
  if(subscription_clicked==true)
    return false

  subscription_clicked = true;
  var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
  var params = {
    'csrfmiddlewaretoken' : csrfmiddlewaretoken,
    'subscription_instance' : subscription_instance
  };
  var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/start_subscription/',
      "method": "POST",
      "headers": {
      },
      "data":params,
      "timeout": 10000,//40 sec timeout
  };
  $.ajax(settings).done(function (msg){
    if(msg.status=="error" && msg.redirect == "login"){
      window.location.href='/broker_login/';
    }
    else if(msg.status=='success')
      {
        $('.subscription_popup').hide();
        $('.cancel_subscription').html('Cancel subscription');
        $('.cancel_subscription').attr('onclick','cancel_subscription_popup();');
        $('.welcome_popup').show();
        $('.welcome_popup').html('<div class="welcome_message"> <img src="/static/imgs/flame-icon-big.png"> <h1>Welcome to Streak</h1><h1>Congratulations, your subscription is successful.</h1> <p><!--A monthly subscription gives you so many more abilities <br> and freedom for building and automating strategies.--></p> <!--<h2>Your Diwali Special plan begins today</h2>--> <button onclick="skip_tour();">Go</button> <!--<p class="skip_tour" onclick="skip_tour();">Go</p>--></div>');
        update_remaining_usage();
      }
    else{
      // notifications_read();
      // alert(msg);
      // show_snackbar(null,'Error occured, please try again');
      if(msg.status=="error"){
          if(msg.msg=='Login required'){
            $('.login_required_popup').show();
            show_snackbar(null,'Login required');
          }
          else if(msg.msg=='Insufficent balance'){
            show_snackbar(null,'Insufficent balance to subscribe');
          }
          else{
            show_snackbar(null,'Error occured, please try again');
          }
        }
        else{
            show_snackbar(null,'Error occured, please try again');
        }
      //////////////
      }
    }).fail(function(msg){
        show_snackbar(null,'Please check your internet connection and try again');
    }).complete(function(msg){
      setTimeout(function(){ 
          subscription_clicked = false;
        }, 2000);
    });
}
function fetch_billing_status(){
  var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
  var params = {
  };
  var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/fetch_billing_status/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 10000,//40 sec timeout
  };
  $.ajax(settings).done(function (msg){
    if(msg.status=='success')
      {
        // '<p id="trial_message">Your 7 day free trial is over. Please subscribe to continue using the services.</p>'
        // <button>Subscribe</button>
        subscription_status = msg.subscription_status;

        if(!msg.subscription_status.subscription_valid){
          $('.trial_box').show();
          if(msg.subscription_status.subscription_plan.indexOf('Free')==-1){
            $('#trial_message').html('Your subscription plan is over. Please subscribe to continue using the services.');
            $('.trial_box button').attr('onclick','start_subscription_popup(\'restart\');');
          }
        }
        else{
          update_remaining_usage();
        }
      }
    else{
      // notifications_read();
      // alert(msg);
      }
  });
}

function get_remaining_usage(){
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
        return {'status':'success','backtest_remaining':backtest_remaining,'deployments_remaining':deployments_remaining}
      }
    }).fail(function(){
      return {'status':'error','backtest_remaining':0,'deployments_remaining':0}
    });
}
function update_remaining_usage(){
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
        // if(msg['valid']==true && msg['subscription_type']!=0){
        if(msg['valid']==true){
          backtest_remaining = Math.max(msg['backtest'],0);
          total_backtest = Math.max(msg['total_backtest'],0);
          total_deploys = Math.max(msg['total_deploys'],0);
          deployments_remaining= Math.max(msg['deployments_remaining'],0);

          $('#counter').html("<span class='bold'>"+backtest_remaining+"</span><span class='small'>&nbsp;/&nbsp;"+total_backtest +"</span>&nbsp;Backtests &nbsp;<span class='bold'>"+deployments_remaining+"</span><span class='small'>&nbsp;/&nbsp;"+total_deploys+"</span>&nbsp;Deploys");
          $('#renewal').html("<span><img src='/static/imgs/new/renew.svg'></span> Renews in "+msg['renewal_time']+" hours");
          $('#counter, #renewal').show();
        }
        // else if(msg['valid']==true && msg['subscription_type']==0){
        //   backtest_remaining = Math.max(msg['backtest'],0);
        //   total_backtest = Math.max(msg['total_backtest'],0);
        //   total_deploys = Math.max(msg['total_deploys'],0);
        //   deployments_remaining= Math.max(msg['deployments_remaining'],0);

        //   $('#counter').removeAttr('onclick');
        //   $('#counter').attr('onclick','start_subscription_popup(subscription_instance=\'first\')');
        //   $('#counter').html("<span></span>B: "+backtest_remaining+"/"+total_backtest+", D: "+deployments_remaining+"/"+total_deploys+" &nbsp;<span></span> Subscribe Now");
        //   $('#counter').attr('data-tooltip-bottom','(B)Backtest and (D)Deployments remaining. Renews in '+msg['renewal_time']+' hours');
        //   $('#counter').show(); 
        // }
      }
    else{
      // notifications_read();
      // alert(msg);
      }
  });
}
function first_login_complete(session_secret,first_time="first_time_algos"){
  if (session_secret==''){
    return;
  }
  var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
  var params = {
        // 'deployment_uuid':dep_id,
        'csrfmiddlewaretoken':csrfmiddlewaretoken,
        'session_secret':session_secret,
        'first_time':first_time
    };
  var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/first_login_complete/',
      "method": "POST",
      "headers": {
      },
      "data":params,
      "timeout": 10000,//40 sec timeout
    };
  $.ajax(settings).done(function (msg){
    if(msg.status=='success')
      {
        console.log('Tour skipped!')
      }
    else{
      // notifications_read();
      // alert(msg);
      }
  });
}

function cancel_subscription_popup(subscription_instance='first'){
  $('#cancel_subscription_popup').fadeIn();
  $('body').addClass('body_scroll');
  $('input:checkbox[name=checkme]').attr('checked',false);
  // start_subscription(subscription_instance='first');
}
function cancel_order_notif(event,order_id,notification_uuid){
  // $('#cancel_order_confirm').removeAttr('onclick');
  // $('#cancel_order_confirm').attr('style',"cursor:no-drop");
  var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
  var params = {
    'order_id':order_id,
    'csrfmiddlewaretoken':csrfmiddlewaretoken,
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/cancel_order_click/',
      "method": "POST",
      "headers": {
      },
      "data":params,
      "timeout": 10000,//40 sec timeout
      "retries": 3
    }
    $.ajax(settings).done(function (msg){
        if(msg.status=='success'){
          if(msg.error==true){
            show_snackbar(null,msg.msg);
          }else{
            show_snackbar(null,msg.msg,type='success');
            notificationsDict['used'][notification_uuid]=1;
            $(event.target).parent().parent().find('.notif_second_line_bottom').hide();
            var params = {
                  'notification_uuid':notification_uuid,
                  'csrfmiddlewaretoken':csrfmiddlewaretoken
            }
            var settings = {
              "async": true,
              "crossDomain": true,
              "url": '/mark_notification_used/',
              "method": "POST",
              "headers": {
              },
              "data":params,
              "timeout": 10000,//40 sec timeout
            }
            $.ajax(settings).done(function (msg){
              console.log('notification_marked used');
            });
          }
        }
    }).complete(function(){
      // refresh_orderbook();
      // close_cancel_order_popup();
      // $('#cancel_order_confirm').removeAttr('style');
    });
}

function submit_feedback(event){
  var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();

  var feedback_details_text = $('#feedback_details_text').val();

  if($(event.target).data('event',"clicked")=="clicked"){
      return;
    }
  if($('#feedback_details_text').val().trim()==''){
    return;
  }

  var params = {
        // 'deployment_uuid':dep_id,
        'csrfmiddlewaretoken':csrfmiddlewaretoken,
        'feedback_details_text':feedback_details_text
    };
  var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/submit_feedback/',
      "method": "POST",
      "headers": {
      },
      "data":params,
      "timeout": 10000,//40 sec timeout
    };

  $(event.target).html('<img src="/static/imgs/button-loading-rect.gif" style="height: 5px;">');
  $(event.target).data('event',"clicked");
  $(event.target).addClass('send_feedback_disabled');

  $.ajax(settings).done(function (msg){
    if(msg.status=='success')
      {
        show_snackbar(null,"Feedback submitted.","Success");
        $('.feedback_popup').fadeOut();$('body').removeClass('body_scroll');
      }
    else{
      // notifications_read();
      // alert(msg);
        show_snackbar(null,"Error submiting feedback, write to us at support@streak.tech.");
      }
  }).fail(function(){
    show_snackbar(null,"Error submiting feedback, write to us at support@streak.tech.");
    show_snackbar(null,"Error connecting to server, try again.");
    $(event.target).html('Submit');
    $(event.target).data('event',"not-clicked");
    $(event.target).removeClass('send_feedback_disabled');
  }).complete(function(){
    $(event.target).html('Submit');
    $(event.target).data('event',"not-clicked");
    $(event.target).removeClass('send_feedback_disabled');
  });
}

function cancel_subscription(subscription_instance='first'){
  if($('input[name=cancel_subscription_checkbox]:checked').is(':checked')){
    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    var params = {
          // 'deployment_uuid':dep_id,
          'csrfmiddlewaretoken':csrfmiddlewaretoken,
      };
    var settings = {
        "async": true,
        "crossDomain": true,
        "url": '/cancel_subscription/',
        "method": "POST",
        "headers": {
        },
        "data":params,
        "timeout": 10000,//40 sec timeout
      };
    $.ajax(settings).done(function (msg){
      if(msg.status=='success')
        {
          show_snackbar(null,msg.msg,'success')
          $('#cancel_subscription_popup').fadeOut();
          $('body').removeClass('body_scroll');
          $('.cancel_subscription').html('Resume subscription');
          $('.cancel_subscription').attr('onclick','start_subscription_popup(\'restart\');'); 
        }
      else{
        show_snackbar(null,'Error occured, please try again');
        }
    }).fail(function(msg){
      show_snackbar(null,'Please check your internet connection and try again');
    });
  }
  else{
    show_snackbar(null,'Check the box if you are sure');
  }
}

function apply_advanced_options(){
  if($('#trading_start_time').val()>$('#trading_stop_time').val()){
    show_snackbar(null,'Trade entry start time cannot be less than stop time');
    return;
  }
  $('.advanced_section_popup').fadeOut();$('body').removeClass('body_scroll');
  try{
    adv_holding_type = $('#ip_holding_type').val();;
    adv_chart_type = $('#ip_chart_type').val();
    adv_trading_start_time = $('#trading_start_time').val();
    adv_trading_stop_time = $('#trading_stop_time').val();
    try{
      refresh_algo_summary();
    }catch(e){

    }
  }catch(e){

  }
}

function logout(){
  // var params = {
  //     };
  //   var settings = {
  //       "async": true,
  //       "crossDomain": true,
  //       "url": 'https://kite.zerodha.com/logout/',
  //       "method": "GET",
  //       "headers": {
  //       },
  //       "data":params,
  //       "timeout": 10000,//40 sec timeout
  //     };
  //   $.ajax(settings).done(function (msg){

  //   }) 
  window.location = "/logout/"
}

function to_title(string) {
    return string.charAt(0).toUpperCase() + string.slice(1).toLowerCase();
}
