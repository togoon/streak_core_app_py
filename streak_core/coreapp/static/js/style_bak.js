window.onbeforeunload = function(){
  window.scrollTo(0,0);
}

var positionsDict = {};
var notificationsDict = {'notifications':[],unread_count: 0,'used':{}};
// onDocument load, load notifications
// on notification update notificationsObject
// on notification show, mark notification as read and update in redis
$(document).ready(function(){
  // $(window).scrollTop(0);
  // var v1 = document.getElementById("v1");
  // var v2 = document.getElementById("v2");
  $("#acc_menu, #new_menu, #more_menu, #notification_details").hide();
  $(".q").click(function(){
  $(this).parent().find(".a").slideToggle();
  // $(".body").css({"margin-top": "70px"}); 
  });
  // $(".a").show();
  // Paste this after showing  $(".body").css({"margin-top": "5px"});
  // $("#error_box").hide();
  $("#user_icon").hover(function(){
    $("#more_menu, #notification_details").hide();
    $("#acc_menu").show();
  });
  $("#more").hover(function(){
    $("#acc_menu, #notification_details").hide();
    $("#more_menu").show();
  });
  $("#notifications").hover(function(){
    $("#acc_menu, #more_menu").hide();
    $("#notification_details").show();
    // if($("#notification_details").css('display')!='none')
    //   refresh_notification();
  });
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
  $("#more_menu, .menu").mouseleave(function(){
    $("#more_menu").hide();   
  });
  $(".menu").mouseleave(function(){
    $("#notification_details").hide();
  });
  $("#notification_details").mouseleave(function(){
    $("#notification_details").hide();
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
    $(this).parentsUntil('.equities_list').hide();
  });

  fetch_notifications();
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
      "timeout": 5000,//40 sec timeout
    };
  $.ajax(settings).done(function (msg){
    if(msg.status=='success')
      {
        notificationsDict = msg['results'];
        update_notification();
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
      "timeout": 5000,//40 sec timeout
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
      dt = moment(notif.notification_time);
      date = dt.format('h:mm a on MM/DD/YYYY ');
      if(moment()-dt<60000*5 && notificationsUsed[notif['notification_uuid']]==undefined)
        {
          a = '<li><div class="notif"><p>'+date+'</p><p>Notification &nbsp;<span>'+notif.algo_name+'</span></p></div><div class="notif_window"><div class="notif_header"><p>'+notif.notification_msg+'</p></div><div class="notif_body"><div class="notif_options"><div><div class="radio_options"><div><span id="buy_radio_option"></span><p id="option_selected">CNC</p></div><div><span></span><p>MIS</p></div></div><div class="notif_qty"><p>Quantity</p><input type="number" name="" value="'+notif.quantity+'"></div></div><div><div class="radio_options"><div><span id="buy_radio_option"></span><p id="option_selected">MKT</p></div><div><span></span><p>LMT</p></div></div><div class="notif_price"><p>Price</p><input type="number" name=""></div></div></div><div><button onclick="place_order(event,\''+notif['notification_uuid']+'\',\''+notif['deployment_uuid']+'\',\''+notif['algo_uuid']+'\',\''+notif['seg']+'\',\''+notif['sym']+'\',\''+notif['quantity']+'\',\''+'MARKET'+'\',\''+notif['action_type'].toUpperCase()+'\',\''+'MIS'+'\',\''+'DAY'+'\')" id="'+notif.action_type.toLocaleLowerCase()+'">'+notif.action_type+'</button></div></div></div></li>';
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
      }else if(trigger_type=="inrange"){
          notification_msg = algo_name+" at price "+parseFloat(trigger_price).toFixed(2);
      }
      // $('#notification_details').show();
      // $($('#notification_details').find('li')[0]).remove();
      dt = moment.unix(trigger_time);
      date = dt.format('h:mm a on MM/DD/YYYY');
      if(moment()-dt<60000*5 && notificationsUsed[notif['notification_uuid']]==undefined)
        {
        a = '<li><div class="notif"><p>'+date+'</p><p>Notification of &nbsp;<span>'+algo_name+'</span></p></div><div class="notif_window"><div class="notif_header"><p>'+notification_msg+'</p></div><div class="notif_body"><div class="notif_options"><div><div class="radio_options"><div><span id="buy_radio_option"></span><p id="option_selected">CNC</p></div><div><span></span><p>MIS</p></div></div><div class="notif_qty"><p>Quantity</p><input type="number" name="" value="'+quantity+'" readonly></div></div><div><div class="radio_options"><div><span id="buy_radio_option"></span><p id="option_selected">MKT</p></div><div><span></span><p>LMT</p></div></div><div class="notif_price"><p>Price</p><input type="number" name=""></div></div></div><div><button onclick="place_order_tpsl(event,\''+notif['notification_uuid']+'\',\''+depid+'\',\''+algo_uuid+'\',\''+token+'\',\''+quantity+'\',\''+'MARKET'+'\',\''+action_type.toUpperCase()+'\',\''+'MIS'+'\',\''+'DAY'+'\',\''+tpsl_key+'\')" id="'+action_type.toLocaleLowerCase()+'">'+action_type+'</button></div></div></div></li>';
        $('#notification_details').prepend(a);}
      else{
        a = '<li><div class="notif"><p>'+date+'</p><p>Notification &nbsp;<span>'+notification_msg+'</span></p></div></li>';
        $('#notification_details').prepend(a);
      }
    }
    if(notif['notification-type']=='order-webhook'){ // this is produced by worker.js
      // $('#notification_details').show();
      date = moment(notif.notification_time).format('h:mm a on MM/DD/YYYY');
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
      date = dt.format('h:mm a on MM/DD/YYYY ');
      if(moment()-dt<60000*5 && notificationsUsed[notif['notification_uuid']]==undefined)
        {
          a = '<li><div class="notif"><p>'+date+'</p><p>Notification &nbsp;<span>'+notif.algo_name+'</span></p></div><div class="notif_window"><div class="notif_header"><p>'+notif.notification_msg+'</p></div><div class="notif_body"><div class="notif_options"><div><div class="radio_options"><div><span id="buy_radio_option"></span><p id="option_selected">CNC</p></div><div><span></span><p>MIS</p></div></div><div class="notif_qty"><p>Quantity</p><input type="number" name="" value="'+notif.quantity+'"></div></div><div><div class="radio_options"><div><span id="buy_radio_option"></span><p id="option_selected">MKT</p></div><div><span></span><p>LMT</p></div></div><div class="notif_price"><p>Price</p><input type="number" name=""></div></div></div><div><button onclick="place_order(event,\''+notif['notification_uuid']+'\',\''+notif['deployment_uuid']+'\',\''+notif['algo_uuid']+'\',\''+notif['seg']+'\',\''+notif['sym']+'\',\''+notif['quantity']+'\',\''+'MARKET'+'\',\''+notif['action_type'].toUpperCase()+'\',\''+'MIS'+'\',\''+'DAY'+'\')" id="'+notif.action_type.toLocaleLowerCase()+'">'+notif.action_type+'</button></div></div></div></li>';
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
      date = dt.format('h:mm a on MM/DD/YYYY');
      if(moment()-dt<60000*5 && notificationsUsed[notif['notification_uuid']]==undefined)
        {
        a = '<li><div class="notif"><p>'+date+'</p><p>Notification of &nbsp;<span>'+algo_name+'</span></p></div><div class="notif_window"><div class="notif_header"><p>'+notification_msg+'</p></div><div class="notif_body"><div class="notif_options"><div><div class="radio_options"><div><span id="buy_radio_option"></span><p id="option_selected">CNC</p></div><div><span></span><p>MIS</p></div></div><div class="notif_qty"><p>Quantity</p><input type="number" name="" value="'+quantity+'" readonly></div></div><div><div class="radio_options"><div><span id="buy_radio_option"></span><p id="option_selected">MKT</p></div><div><span></span><p>LMT</p></div></div><div class="notif_price"><p>Price</p><input type="number" name=""></div></div></div><div><button onclick="place_order_tpsl(event,\''+notif['notification_uuid']+'\',\''+depid+'\',\''+algo_uuid+'\',\''+token+'\',\''+quantity+'\',\''+'MARKET'+'\',\''+action_type.toUpperCase()+'\',\''+'MIS'+'\',\''+'DAY'+'\',\''+tpsl_key+'\')" id="'+action_type.toLocaleLowerCase()+'">'+action_type+'</button></div></div></div></li>';
        $('#notification_details').prepend(a);}
      else{
        a = '<li><div class="notif"><p>'+date+'</p><p>Notification &nbsp;<span>'+notification_msg+'</span></p></div></li>';
        $('#notification_details').prepend(a);
      }
    }
    if(notif['notification-type']=='order-webhook'){ // this is produced by worker.js
      // $('#notification_details').show();
      date = moment(notif.notification_time).format('h:mm a on MM/DD/YYYY');
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
function show_snackbar(e,msg,type='error',callback=null){
  $(".snackbar").show();
  if(type=='error'){
    $(".snackbar").find('p').addClass('snackbar_error');
  }
  else{
   $(".snackbar").find('p').removeClass('snackbar_error'); 
  }
  $(".snackbar p").text(msg);
  $(".snackbar").removeClass("animated, bounceInUp");
  $(".snackbar").fadeOut(6000);
  $(".snackbar").addClass("animated, bounceInUp");
  if(callback){
    setTimeout(function(){ 
      callback();
    }, 2000);
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
        if (event.data['notification-type'] == "order-notification")
        {
          // refresh_notification();
          notificationsDict['notifications'].push(event.data);
          notificationsDict['unread_count']+=1;
          refresh_notification();
          $('#notification_details').show();
          // $($('#notification_details').find('li')[0]).remove();
          // date = moment(event.data.notification_time).format('h:mm a on MM/DD/YYYY ');
          // a = '<li><div class="notif"><p>'+date+'</p><p>Notification &nbsp;<span>'+event.data.algo_name+'</span></p></div><div class="notif_window"><div class="notif_header"><p>'+event.data.notification_msg+'</p></div><div class="notif_body"><div class="notif_options"><div><div class="radio_options"><div><span id="buy_radio_option"></span><p id="option_selected">CNC</p></div><div><span></span><p>MIS</p></div></div><div class="notif_qty"><p>Quantity</p><input type="number" name="" value="'+event.data.quantity+'"></div></div><div><div class="radio_options"><div><span id="buy_radio_option"></span><p id="option_selected">MKT</p></div><div><span></span><p>LMT</p></div></div><div class="notif_price"><p>Price</p><input type="number" name=""></div></div></div><div><button onclick="place_order(event,\''+event.data['notification_uuid']+'\',\''+event.data['deployment_uuid']+'\',\''+event.data['algo_uuid']+'\',\''+event.data['seg']+'\',\''+event.data['sym']+'\',\''+event.data['quantity']+'\',\''+'MARKET'+'\',\''+event.data['action_type'].toUpperCase()+'\',\''+'MIS'+'\',\''+'DAY'+'\')" id="'+event.data.action_type.toLocaleLowerCase()+'">'+event.data.action_type+'</button></div></div></div></li>';
          // $('#notification_details').prepend(a);
          // $('#notif_count').text(notificationsDict['unread_count']+1);
          // $('#notif_count').show();
          refresh_order_log();
      }
      if(event.data['notification-type']=='ltp'){
        for(var t=0;t<event.data['ticks'].length;t++){
          tick = event.data['ticks'][t];
          // sym_segList[tick['Token']] = event.data['ticks'][0];
          sym_segDict = event.data['sym_segDict'];
          sym_seg = sym_segDict[tick['Token']];
          x = $('.token__'+sym_seg);
          x.each(function(i){
            // x[i].
              sub_ltp = $(x[i]).find('.ltp .sub_ltp')
              ltp_change = parseFloat(tick['NetPriceChangeFromClosingPrice']).toFixed(2);
              ltp_val = tick['LastTradedPrice'];
              if(ltp_change<0)
              {
                ltp_text = ltp_val+' ( '+ltp_change+'%)';
                sub_ltp.text(ltp_text);
                sub_ltp.removeClass('loss');
                sub_ltp.removeClass('profit');
                sub_ltp.addClass('loss');
              }
              else{
                ltp_text = ltp_val+' ( +'+ltp_change+'%)';
                sub_ltp.text(ltp_text);
                sub_ltp.removeClass('loss');
                sub_ltp.removeClass('profit');
                sub_ltp.addClass('profit');
              }
          });
          if(positionsDict[sym_seg]!=undefined){
            for (var k in positionsDict[sym_seg]){
              avg_price = positionsDict[sym_seg][k]['last_order_average_price'];
              qty = positionsDict[sym_seg][k]['qty'];
              net_pnl = positionsDict[sym_seg][k]['final_pnl'];
              net_ret = positionsDict[sym_seg][k]['returns'];
              
              if(net_pnl==undefined)
                net_pnl = 0.0;
              if(net_ret==undefined)
                net_ret = 0.0;

              if(avg_price==0 && qty == 0 && net_pnl == 0){
                $('#live__'+k).html('<span class="sub_title">P&L:&nbsp;&nbsp;</span><span style="color: #bfc7d1;font-weight: 400;">&nbsp;</span><span style="color: #bfc7d1;font-weight: 400;">'+'NA'+'&nbsp;</span><span style="color: #bfc7d1;font-weight: 400;">('+'NA'+'%)&nbsp;</span>');
                continue;
              }
              else if(net_pnl!=0 && net_ret!=0 && qty==0)
              {
                if(net_pnl>=0){
                  $('#live__'+k).html('<span class="sub_title">P&L:&nbsp;&nbsp;</span><span><img src="/static/imgs/icon-arrow-up-green.png">&nbsp;</span><span>+'+net_pnl+'&nbsp;</span><span>( +'+net_ret+'%)&nbsp;</span>');
                }
                else{
                  $('#live__'+k).html('<span class="sub_title">P&L:&nbsp;&nbsp;</span><span><img src="/static/imgs/icon-arrow-down-red.png">&nbsp;</span><span class="loss">'+net_pnl+'&nbsp;</span><span class="loss">( '+net_ret+'%)&nbsp;</span>');
                }
                console.log(sym_seg+'average_price'+avg_price)
              }
              else if(qty>0)
              {
                pnl = parseFloat((tick['LastTradedPrice']-avg_price)*qty+net_pnl).toFixed(2);
                if(avg_price!=0)
                  ret = parseFloat(100*(tick['LastTradedPrice']-avg_price+net_pnl)/avg_price).toFixed(2);
                else
                  ret=0

                console.log(sym_seg+pnl);
                if(window.location.href.indexOf('/portfolio/')!=-1){
                  $('#live__'+k).closest('.positions_row_change').html('');
                }
                if(pnl>=0 && avg_price!=0){
                  if(avg_price==0){
                    $('#live__'+k).html('<span class="sub_title">P&L:&nbsp;&nbsp;</span><span><img src="/static/imgs/icon-arrow-up-green.png">&nbsp;</span><span>+'+pnl+'&nbsp;</span><span>&nbsp;</span>');
                  }
                  else{
                    $('#live__'+k).html('<span class="sub_title">P&L:&nbsp;&nbsp;</span><span><img src="/static/imgs/icon-arrow-up-green.png">&nbsp;</span><span>+'+pnl+'&nbsp;</span><span>( +'+ret+'%)&nbsp;</span>');
                  }
                }
                else{
                  if(avg_price==0){
                    $('#live__'+k).html('<span class="sub_title">P&L:&nbsp;&nbsp;</span><span><img src="/static/imgs/icon-arrow-down-red.png">&nbsp;</span><span class="loss">'+pnl+'&nbsp;</span><span class="loss">&nbsp;</span>');
                  }
                  else{
                    $('#live__'+k).html('<span class="sub_title">P&L:&nbsp;&nbsp;</span><span><img src="/static/imgs/icon-arrow-down-red.png">&nbsp;</span><span class="loss">'+pnl+'&nbsp;</span><span class="loss">( '+ret+'%)&nbsp;</span>');
                  }
                }
              }
            }
          }
        }
      }
      if(event.data['notification-type']=='state'){ // this is produced by worker.js
        if(event.data['state']=='ready'){
          refresh_ltp_subscription();
          refresh_pnl_subscription();
        }
      }
      if(event.data['price_trigger-notification']!=undefined){ // TP/SL notification
        notificationsDict['unread_count']+=1;
        notificationsDict['notifications'].push(event.data);
        refresh_notification();
        // tpsl_key=event.data['price_trigger-notification'];
        // trigger_time = event.data['trigger_time'];
        // trigger_price = event.data['trigger_price'];
        // trigger_type = event.data['type'];
        // uid = event.data['user_uuid'];
        // tpsl_array = tpsl_key.split(':');
        // userid = tpsl_array[0];
        // depid = tpsl_array[1];
        // token = tpsl_array[3];
        // algo_name = tpsl_array[8];
        // action_type = tpsl_array[9];
        // quantity = tpsl_array[10];
        // algo_uuid = tpsl_array[11];

        // if(trigger_type=="take-profit"){
        //   notification_msg = "Take profit at "+parseFloat(trigger_price).toFixed(2);
        // }
        // else if(trigger_type=="stop-loss"){
        //   notification_msg = "Stop loss at "+parseFloat(trigger_price).toFixed(2);
        // }
        // else if(trigger_type=="inrange"){
        //   notification_msg = algo_name+" at price "+parseFloat(trigger_price).toFixed(2);
        // }
        $('#notification_details').show();
        // // $($('#notification_details').find('li')[0]).remove();
        // date = moment.unix(trigger_time).format('h:mm a on MM/DD/YYYY');
        // a = '<li><div class="notif"><p>'+date+'</p><p>Notification of &nbsp;<span>'+algo_name+'</span></p></div><div class="notif_window"><div class="notif_header"><p>'+notification_msg+'</p></div><div class="notif_body"><div class="notif_options"><div><div class="radio_options"><div><span id="buy_radio_option"></span><p id="option_selected">CNC</p></div><div><span></span><p>MIS</p></div></div><div class="notif_qty"><p>Quantity</p><input type="number" name="" value="'+quantity+'" readonly></div></div><div><div class="radio_options"><div><span id="buy_radio_option"></span><p id="option_selected">MKT</p></div><div><span></span><p>LMT</p></div></div><div class="notif_price"><p>Price</p><input type="number" name=""></div></div></div><div><button onclick="place_order_tpsl(event,\''+event.data['notification_uuid']+'\',\''+depid+'\',\''+algo_uuid+'\',\''+token+'\',\''+quantity+'\',\''+'MARKET'+'\',\''+action_type.toUpperCase()+'\',\''+'MIS'+'\',\''+'DAY'+'\',\''+tpsl_key+'\')" id="'+action_type.toLocaleLowerCase()+'">'+action_type+'</button></div></div></div></li>';
        // $('#notification_details').prepend(a);
        // $('#notif_count').text(notificationsDict['unread_count']);
        // $('#notif_count').show();
        refresh_order_log();

      }
      if(event.data['notification-type']=='order-webhook'){ // this is produced by worker.js
        // refresh_notification();
        notificationsDict['notifications'].push(event.data);
        notificationsDict['unread_count']+=1;
        refresh_notification();
        // date = moment(event.data.notification_time).format('h:mm a on MM/DD/YYYY');
        // notification_msg = event.data.notification_msg;
        // avg_price = parseFloat(event.data.average_price).toFixed(2);
        // filled_quantity = event.data.filled_quantity;
        // quantity = event.data.quantity;
        // action_type2 = event.data.action_type;
        
        // if(event.data.action_type.toLowerCase()=='buy'){
        //   action_type2='Bought';
        // }else if(event.data.action_type.toLowerCase()=='sell'){
        //   action_type2='Sold';
        // }

        // a = '<li> <div class="notif"> <p>'+date+'</p> <p>'+notification_msg+'.&nbsp;<span class="'+action_type2.toLowerCase()+'">'+action_type2+' '+filled_quantity+' of '+quantity+' at '+avg_price+'</span></p> </div> </li>';
        // if(!event.data.open_notif)
        // {
        //   $('#notification_details').prepend(a);
        //   $('#notif_count').text(notificationsDict['unread_count']);
        //   $('#notif_count').show();
        // }
        // $('#notif_count').text(notificationsDict['unread_count']);
        // $('#notif_count').show();
        $('#notification_details').show();
        refresh_order_log();
      }
      console.log(event.data);
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
      load_order_log(status,10,pagination);
    }
    catch(e){
      
    }
  }
}
function refresh_ltp_subscription(){
  x = $("[class^=token__]");
  x.each(function(i){
    [t,seg_sym]=x[i].className.split('__');
    if (typeof(w) != "undefined") {
      w.postMessage(['subscribe',seg_sym]);
    }
  });
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
      "timeout": 5000,//40 sec timeout
    };

  $.ajax(settings).done(function (msg){
    if(msg.status=='success')
      {
        positions = msg.positions;
        // seg_sym = [];
        // for(var k in positions) seg_sym.push(k)
        seg_sym =[msg.seg+'_'+msg.sym]
        if(positionsDict[seg_sym[0]] == undefined)
            positionsDict[seg_sym[0]]={};

        positionsDict[seg_sym[0]][dep_id]={
          "last_order_average_price":positions.last_order_average_price,
          "qty":positions.qty,
          "pnl":positions.pnl
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
function log_in_kite(){
  // newWindow = popupWindowCenter('/broker_login?redirect=popup','Kite login','500','700')
  //   newWindow.onunload = function(e){
  //     // win = window.opener;
  //     // if(!win.closed)
  //     if(e.target.documentURI.indexOf('status=success&request_token=')!=-1){
  //       // alert('yo');
  //       window.location='/dashboard';
  //     }
  //   }
  window.location='/broker_login';
}
function place_order(event,notification_uuid,deployment_uuid,algo_uuid,seg,sym,quantity,order_type,transaction_type,product,validity){
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
        'csrfmiddlewaretoken':csrfmiddlewaretoken
    }

    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/place_order/',
      "method": "POST",
      "headers": {
      },
      "data":params,
      "timeout": 5000,//40 sec timeout
    }
    $.ajax(settings).done(function (msg){
        if(msg.status=='used')
        {
          notificationsDict['used'][notification_uuid]=1;
          show_snackbar(null,'This notification is already used!','success');
          $(me).closest('.notif_window').remove();
        }
        else if(msg.status=='success')
        {
          console.log(msg.status);
          $('.exit_position, .stop_options').hide();$('.algo_stopped').show();
          show_snackbar(null,'Order sent to exchange','success');
          notificationsDict['used'][notification_uuid]=1;
          $(me).closest('.notif_window').remove();
          // setTimeout(function(){ 
          //   // window.location = '/dashboard/';
          //   }, 2000);
          // TODO hide the notification or delete it
        }else{
          show_snackbar(null,'Order not placed, please try again!');
        }
    }).fail(function(msg){
        // alert('Some error, please try again');
        show_snackbar(null,'Connection error, please try again!');
    }).complete(function(){
            $(me).data('requestRunning', false);
            $(me).removeAttr('style');
    });
}

function place_order_tpsl(event,notification_uuid,deployment_uuid,algo_uuid,token,quantity,order_type,transaction_type,product,validity,tpsl_key){
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
      "timeout": 5000,//40 sec timeout
    }
    $.ajax(settings).done(function (msg){
        if(msg.status=='used')
        {
          notificationsDict['used'][notification_uuid]=1;
          show_snackbar(null,'This notification is already used!','success');
          $(me).closest('.notif_window').remove();
        }
        else if(msg.status=='success')
        {
          console.log(msg.status);
          $('.exit_position, .stop_options').hide();$('.algo_stopped').show();
          show_snackbar(null,'Order sent to exchange','success');
          // setTimeout(function(){ 
          //   // window.location = '/dashboard/';
          //   }, 2000);
          // TODO hide the notification or delete it
          $(me).closest('.notif_window').remove();
        }else{
          show_snackbar(null,'Order not placed, please try again!');
        }
    }).fail(function(msg){
        show_snackbar(null,'Connection error, please try again!');
    }).complete(function(){
            $(me).data('requestRunning', false);
            $(me).removeAttr('style');
    });
}