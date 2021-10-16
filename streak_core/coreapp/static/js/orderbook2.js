var platform='All';
var open_orders = 0;
var executed_orders = 0;
$(window).load(function() {
    // Animate loader off screen
    $(".loader_parent").fadeOut();
  });
function show_open(){
    $("#holdings").hide();
    $("#positions").show();
    $("#holdings_option").removeClass("portfolio_menu_selected");
    $("#positions_option").addClass("portfolio_menu_selected");
}
function show_executed(){
    $("#positions").hide();
    $("#holdings").show();
    $("#positions_option").removeClass("portfolio_menu_selected");
    $("#holdings_option").addClass("portfolio_menu_selected"); 
}

function close_order_details_popup () {
    $(".close_popup").parents(".body").find(".order_details_popup").fadeOut();
    $("body").removeClass("body_scroll");
}
function close_cancel_order_popup () {
    $(".close_popup").parents(".body").find(".cancel_order_popup").fadeOut();
    $("body").removeClass("body_scroll");
}

function attach_user_actions(){
  $("#positions .positions_details_row").hover(function(){
      $(this).find(".cancel_order").show();
      $(this).find(".positions_row_order_details span").show();
    });
  $("#positions .positions_details_row").mouseleave(function(){
    $(this).find(".cancel_order").hide();
    $(this).find(".positions_row_order_details span").hide();
  });
  $("#holdings .positions_details_row").hover(function(){
      $(this).find(".cancel_order").show();
      $(this).find(".positions_row_order_details span").show();
    });
  $("#holdings .positions_details_row").mouseleave(function(){
    $(this).find(".cancel_order").hide();
    $(this).find(".positions_row_order_details span").hide();
  });
  $("#app_positions .positions_details_row, #app_holdings .positions_details_row").click(function(){
      $(this).find(".positions_details_row_hidden").toggle();
    });
  $(".positions .cancel_order, .holdings .cancel_order, .positions .positions_row_order_details span, .holdings .positions_row_order_details span").css({"display" : "none"});
  $("#app_positions .positions_details_row_hidden, #app_holdings .positions_details_row_hidden").hide();
  $(".cancel_order_popup").click(function(e){
    // alert($(".cancel_order_popup").has(e.target).length);
    // alert($(".cancel_order_popup").is(e.target));
    if(($(".cancel_order_popup").has(e.target).length == 0)&&($(".cancel_order_popup").is(e.target))){
    $("body").removeClass("body_scroll");
    $(".close_popup").parents(".body").find(".cancel_order_popup").fadeOut();
    }
  });
}
$(document).ready(function(){
    if(window.location.href.indexOf('#executed')!=-1)
        fetch_executed_orders();
    else
      fetch_open_orders();
    $("#holdings_option").click(function(){
        fetch_executed_orders();
    });
    $("#positions_option").click(function(){
        fetch_open_orders();
    });
    $("#positions .positions_details_row").hover(function(){
      $(this).find(".cancel_order").show();
      $(this).find(".positions_row_order_details span").show();
    });
    $("#positions .positions_details_row").mouseleave(function(){
      $(this).find(".cancel_order").hide();
      $(this).find(".positions_row_order_details span").hide();
    });
    $(".positions .cancel_order, .holdings .cancel_order, .positions .positions_row_order_details span, .holdings .positions_row_order_details span").css({"display" : "none"});
    $("#app_positions .positions_details_row_hidden, #app_holdings .positions_details_row_hidden").hide();
    $("#app_positions .positions_details_row, #app_holdings .positions_details_row").click(function(){
      $(this).find(".positions_details_row_hidden").toggle();
    });
    $(".positions_details_title>div, .holding_details_title>div").hover(function(){
      $(this).find("img").show();
    });
    $(".positions_details_title>div, .holding_details_title>div").mouseleave(function(){
      $(this).find("img").hide();
    });
    $(".cancel_order_popup").click(function(e){
    // alert($(".cancel_order_popup").has(e.target).length);
    // alert($(".cancel_order_popup").is(e.target));
    if(($(".cancel_order_popup").has(e.target).length == 0)&&($(".cancel_order_popup").is(e.target))){
      $("body").removeClass("body_scroll");
      $(".close_popup").parents(".body").find(".cancel_order_popup").fadeOut();
    }
    });
    // $("#take_tour, #take_tour_mobile").click(function(){
    //     hopscotch.startTour(orderbook_tour());
    // });
    $(".fancy_filter_select").click(function(){
      $(".fancy_filter_options").slideToggle();
    });
    $('#portfolio_platform').autocomplete({
      source: function(request,response){
        results = ['All','Streak'];
        x = $.map(results, function (el) {
        // console.log(el)
         return {
           label: el,//+'<span>('+el[1]+')</span>',
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
          $(this).val(ui.item.value);
          $(this).attr('data-val-text',ui.item.value);
          $(this).focusout();
          $(this).blur();

          // fetch_open_orders();
          // console.log(ui.item.value);
          platform = ui.item.value;
          var menu_selected = $('.portfolio_menu_selected')[0].id
          if(menu_selected=='holdings_option'){
            fetch_executed_orders();
          }
          else{
            fetch_open_orders();
          }

          hide_show();

        }
      }).focus(function() {
        $(this).autocomplete('search', '');
      });

    setInterval(refresh_orderbook,45000);

    $('#executed_orders_search_input')
});

function platform_update(e,plat){
   platform = plat;
  var menu_selected = $('.portfolio_menu_selected')[0].id
  if(menu_selected=='holdings_option'){
    fetch_executed_orders();
  }
  else{
    fetch_open_orders();
  }
  img = $(e).find('.logo_tag img').attr('src');
  $(".fancy_filter_options").slideToggle();
  $('.fancy_filter_select .logo_tag_big img').attr('src',img);
}

function hide_show(){
  $('#portfolio_platform').hide();
  setTimeout(function(){ 
    $('#portfolio_platform').show();
  }, 10);
}

function refresh_orderbook(){
  var menu_selected = $('.portfolio_menu_selected')[0].id
  fetch_orders();
  // if(menu_selected=='holdings_option'){
  //   fetch_executed_orders();
  // }
  // else{
  //   fetch_open_orders();
  // }
}

function search_open_orders(){
  q = $('#open_orders_search_input').val();
  x = $('.positions_body div[class^="token__"]');
  x.each(function(i){
    if(q.replace(/ /g,'')==''){
      $(x[i]).removeClass('add_opacity');
    }
    else{
      data_str = '';
      all_d = $(x[i]).find('div>div');
      for(j=0;j<all_d.length;j++){
        if($(all_d[j]).data('val')!=undefined)
          data_str =data_str+$(all_d[j]).data('val');
      }
      if(data_str.toLowerCase().search(q)==-1){
        $(x[i]).addClass('add_opacity');
      }
      else{
        $(x[i]).removeClass('add_opacity');
      }
    }
  });
}

function search_executed_orders(){
  q = $('#executed_orders_search_input').val().toLowerCase();
  x = $('.holdings_body div[class^="token__"]');
  x.each(function(i){
    if(q.replace(/ /g,'')==''){
      $(x[i]).removeClass('add_opacity');
    }
    else{
      data_str = '';
      all_d = $(x[i]).find('div>div');
      for(j=0;j<all_d.length;j++){
        if($(all_d[j]).data('val')!=undefined)
          data_str =data_str+$(all_d[j]).data('val');
      }
      if(data_str.toLowerCase().search(q)==-1){
        $(x[i]).addClass('add_opacity');
      }
      else{
        $(x[i]).removeClass('add_opacity');
      }
    }
  });
}

function sort_column(e){
  // console.log(e);
  var target_column = $(e.currentTarget);
  var target_column_id = e.currentTarget.id;
  var column = e.currentTarget.classList[0].replace('_title','');
  var img = $(e.currentTarget).find('img').attr('src');
  var img_rev = "/static/imgs/new/dropup.svg";
  sorting_type = 'desc';
  if(img == "/static/imgs/new/dropup.svg"){
    img_rev = "/static/imgs/new/dropdown.svg";
    sorting_type = 'asc';
  }
  var parent_div_id = e.currentTarget.parentElement.parentElement.parentElement.id;
  var section_class_name = e.currentTarget.parentElement.className;
  // if (target_column.data('sort-type')===undefined)
  //   {
  //     sorting_type = 'desc';
  //   }
  // else if(target_column.data('sort-type')=='desc'){
  //     sorting_type = 'asc';
  // }
  // else{
  //     sorting_type = 'desc';
  // }

  var $table = $('#'+parent_div_id+' div[class^="token__"]');
  var orderedDivs = $table.sort(function (a, b) {
      if(target_column_id=='positions_row_ltp_title5'){
        console.log($(a).find("."+target_column_id).text(),$(b).find("."+target_column_id).text());
        if(sorting_type=='asc'){
        return $(a).find("."+target_column_id).text() <= $(a).find("."+target_column_id).text();
        // return $(a).find("."+column+" p").text() <= $(b).find("."+column+" p").text();
        }
        else{
          return $(a).find("."+target_column_id).text() <= $(a).find("."+target_column_id).text();
          // return $(a).find("."+column+" p").text() >= $(b).find("."+column+" p").text();
        }
      }
      else{
        console.log($(a).find("."+target_column_id).data('val'),$(b).find("."+target_column_id).data('val'));
        if(sorting_type=='asc'){
        return $(a).find("."+target_column_id).data('val') <= $(b).find("."+target_column_id).data('val');
        // return $(a).find("."+column+" p").text() <= $(b).find("."+column+" p").text();
        }
        else{
          return $(a).find("."+target_column_id).data('val') > $(b).find("."+target_column_id).data('val');
          // return $(a).find("."+column+" p").text() >= $(b).find("."+column+" p").text();
        }
      }
  });
  $("div."+parent_div_id+" ."+parent_div_id+'_body').html(e.currentTarget.parentElement.outerHTML);
  for(i=0;i<orderedDivs.length;i++){
    $("div."+parent_div_id+" ."+parent_div_id+'_body').append(orderedDivs[i]);
  }
  
  $('#'+target_column_id).attr('data-sort-type',sorting_type);
  $('#'+target_column_id+' img').attr('src',img_rev);

  $(".positions_details_title>div, .holding_details_title>div").hover(function(){
    $(this).find("img").show();
  });
  $(".positions_details_title>div, .holding_details_title>div").mouseleave(function(){
    $(this).find("img").hide();
  });
}

function fetch_executed_orders(){
  refresh_orderbook();
  show_executed();
  // $('.holdings_body').show();
  // $('.positions_body').hide();
  if(executed_orders==0){
    $('.empty_holdings').show();
    $('.empty_positions').hide();
    $('.holdings_body').hide();
    $('#holdings .header_bar').hide();
    $('#app_positions .holdings_body').hide();
    $('#app_holdings .holdings_body').hide();
    $('.positions_body').hide();
    $('#positions .header_bar').hide();
  }else{
    $('.positions_body').hide();
    $('#positions .header_bar').hide();
    $('.empty_holdings').hide();
    $('.empty_positions').hide();
    $('.holdings_body').show();
    $('#holdings .header_bar').show();
    $('#app_positions .holdings_body').hide();
    $('#app_holdings .holdings_body').show();
  }
}
function fetch_open_orders(){
  refresh_orderbook();
  show_open();
  // $('.holdings_body').hide();
  // $('.positions_body').show();
  if(open_orders==0){
    $('.empty_holdings').hide();
    $('.empty_positions').show();
    $('.holdings_body').hide();
    $('#holdings .header_bar').hide();
    $('#app_positions .holdings_body').hide();
    $('#app_holdings .holdings_body').hide();
    $('.positions_body').hide();
    $('#positions .header_bar').hide();
  }else{
    $('.empty_holdings').hide();
    $('.empty_positions').hide();
    $('.positions_body').show();
    $('#positions .header_bar').show();
    $('.holdings_body').hide();
    $('#holdings .header_bar').hide();
    $('#app_positions .holdings_body').show();
    $('#app_holdings .holdings_body').hide();
  }
}

function fetch_orders(){
    $('.loading-dots-container').show();
    if($.urlParam('platform')=='all')
        platform = $.urlParam('platform')
    if($.urlParam('variety')=='BO'){
        show_snackbar(null,'Exit BO from orderbook','success');
    }
    if($.urlParam('variety')=='BOE'){
        show_snackbar(null,'Exit BO from orderbook and then stop the algo','success');
    }

    var params = {
      'platform':platform
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

    $.ajax(settings).done(function (msg){
        if(msg.status=='success'){
            if(msg.executed.length==0){
                $('.holdings_body .positions_details_row').each(function(){
                  $(this).parent().remove()
                });
                $('#app_holdings .holdings_body').html('');              
                executed_orders = msg.executed.length;

            }else{

              executed_orders = msg.executed.length;

              positions_executed = msg.executed;
              $('.holdings_body .positions_details_row').each(function(){
                  $(this).parent().remove()
              });
              $('#app_holdings .holdings_body').html('');

              for(var i=0;i<positions_executed.length;i++){

                // segment = 'NSE'
                // if (positions_executed[i].exchange=='NSE')
                //   segment = 'NSE'
                // else if (positions_executed[i].exchange=='NFO')
                //   if(positions_executed[i].exchange.endsWith('FUT'))
                //     segment = 'NFO-FUT'
                //   else
                //     segment = 'NFO-OPT'
                segment = positions_executed[i].segment;
                uid = positions_executed[i]['user_uuid'];
                modified_html = '';
                if(positions_executed[i].modified==1)
                  modified_html='<span data-tooltip-top="Looks like you have taken manual positions through Kite" class="exclamatory_mark">!</span>';

                var part1 = '<div class="token__'+segment+'_'+positions_executed[i].tradingsymbol+'"><div class="positions_details_row"><div class="positions_row_product positions_row_product_title4" data-val="'+positions_executed[i].order_timestamp+'"><p>'+moment(positions_executed[i].order_timestamp).format('HH:mm:ss')+'</p></div><div class="positions_row_product positions_row_product_title5" data-val="'+positions_executed[i].transaction_type+'"><p class="'+positions_executed[i].transaction_type.toLowerCase()+'_tag">'+positions_executed[i].transaction_type+'</p></div><div class="positions_row_instrument positions_row_product_title6" data-val="'+positions_executed[i].tradingsymbol+'_'+positions_executed[i].exchange+'"><p>'+positions_executed[i].tradingsymbol+'<span>&nbsp;'+positions_executed[i].exchange+'</span>'+modified_html+'</p></div><div class="positions_row_quantity positions_row_quantity_title7" data-val="'+positions_executed[i].filled_quantity+'"><p>'+parseFloat(positions_executed[i].filled_quantity).toFixed(6)+'/'+parseFloat(positions_executed[i].quantity).toFixed(6)+'</p></div><!--<div class="positions_row_ltp"><p class="ltp"><span class="sub_title">&nbsp;</span><span class="sub_ltp">0.0</span></p></div>--><div class="positions_row_avg_price positions_row_avg_price_title8" data-val="'+positions_executed[i].average_price+'"><p>'+parseFloat(positions_executed[i].average_price).toFixed(2)+'</p></div><div class="positions_row_product  positions_row_product_title9" data-val="'+positions_executed[i].order_placement+'"><p>'+positions_executed[i].order_placement.split(' ')[0].toUpperCase()+'</p></div>'
                
                var part3 = '';
                // if(parseFloat(positions[i].pnl)>0)
                //   pnl = '<div class="positions_row_pnl" data-realised='+positions[i].realised+' id="ulive__'+uid+'"><p class="profit">+'+parseFloat(positions[i].status).toFixed(2)+'<span>&nbsp;<!--(2.3%)--></span></p></div>'; 
                // else
                var status_tag = ''
                if(positions_executed[i].status.toLowerCase()+'_tag'=='cancelled_tag')
                  status_tag = 'cancel_tag'
                else if(positions_executed[i].status.toLowerCase()+'_tag'=='rejected_tag')
                  status_tag = 'REJECTED_tag'
                else
                  status_tag = positions_executed[i].status.toLowerCase()+'_tag'

                var pnl = '<div class="positions_row_pnl positions_row_pnl_title10" data-val="'+positions_executed[i].status+'"><p class="'+status_tag+'">'+positions_executed[i].status+'<span>&nbsp;<!--(2.3%)--></span></p></div>';
                var chg = '';//<div class="positions_row_change"><p style="color: #bfc7d1;font-weight: 400;">NA</p></div>';
                var algo_str = JSON.stringify(positions_executed[i]).replace("'s",'');
                // var part4 = '<div class="positions_row_order_details"><p onclick="fetch_specific_position(\''+positions_executed[i].tradingsymbol+'\',\''+positions_executed[i].exchange+'\',\''+positions_executed[i].product+'\')">Details<span><img src="/static/imgs/icon-right-grey.png"></span></p></div></div></div>';
                var part4 = '<div class="positions_row_order_details"><p onclick=\'show_order_details('+algo_str+')\'><span>Details</span></p></div></div></div>';
                $('.holding_details_title').after(part1+part3+pnl+chg+part4);

                // adding this for app_UI

                var app_part1 = '<div class="token__'+segment+'_'+positions_executed[i].tradingsymbol+'"><div class="positions_details_row"><div class="positions_details_row_top"><div class="positions_row_product"><p class="'+positions_executed[i].transaction_type.toLowerCase()+'_tag">'+positions_executed[i].transaction_type+'</p></div><div class="positions_row_pnl"><p class="'+status_tag+'">'+positions_executed[i].status+'<span>&nbsp;<!--(2.3%)--></span></p></div><div class="positions_row_datetime"><p>'+moment(positions_executed[i].order_timestamp).format('HH:mm:ss')+'</p></div></div><div class="positions_details_row_bottom"><div class="positions_row_instrument"><p>'+positions_executed[i].tradingsymbol+'<span>&nbsp;'+positions_executed[i].exchange+'</span></p></div><div class="positions_row_quantity"><p>Qty:&nbsp;'+positions_executed[i].filled_quantity+'/'+positions_executed[i].quantity+'</p></div><div class="positions_row_avg_price"><p>'+parseFloat(positions_executed[i].average_price).toFixed(2)+'</p></div><div class="positions_row_product"><p>'+positions_executed[i].product+'</p></div></div>';
                var app_part2 = '<div class="positions_details_row_hidden"><div class="positions_row_order_details"><p onclick=\'show_order_details('+algo_str+')\'><span>Details</span></p></div></div></div></div>'

                $('#app_holdings .holdings_body').prepend(app_part1+app_part2);
              }
            }

            if(msg.pending.length==0){
                $('.positions_body .positions_details_row').each(function(){
                      $(this).parent().remove()
                });
                $('#app_positions .holdings_body').html('');

                open_orders = msg.pending.length;
            }
            else{
                open_orders = msg.pending.length;

              // $('.positions_body').show();
              // filling the orders portfolio
              positions = msg.pending;
              $('.positions_body .positions_details_row').each(function(){
                  $(this).parent().remove()
              });
              $('#app_positions .holdings_body').html('');

              for(var i=0;i<positions.length;i++){

                // segment = 'NSE'
                // if (positions[i].exchange=='NSE')
                //   segment = 'NSE'
                // else if (positions[i].exchange=='NFO')
                //   if(positions[i].tradingsymbol.endsWith('FUT'))
                //     segment = 'NFO-FUT'
                //   else
                //     segment = 'NFO-OPT'
                // else if (positions[i].exchange=='CDS')
                //   if(positions[i].tradingsymbol.endsWith('FUT'))
                //     segment = 'CDS-FUT'
                //   else
                //     segment = 'CDS-OPT'
                segment = positions[i].segment;
                uid = positions[i]['user_uuid'];
                
                modified_html = '';
                if(positions[i].modified==1)
                  modified_html='<span data-tooltip-top="Looks like you have taken manual positions through Kite" class="exclamatory_mark">!</span>';
                
                trigger_price_str = '';
                if(positions[i].trigger_price!=undefined)
                  if(positions[i].trigger_price!=0.0)
                    trigger_price_str = ' / '+positions[i].trigger_price+' trg.';

                var part1 = '<div class="token__'+segment+'_'+positions[i].tradingsymbol+'"><div class="positions_details_row"><div class="positions_row_product positions_row_product_title1" data-val="'+positions[i].order_timestamp+'"><p>'+moment(positions[i].order_timestamp).format('HH:mm:ss')+'</p></div><div class="positions_row_product positions_row_product_title2" data-val="'+positions[i].transaction_type+'"><p class="'+positions[i].transaction_type.toLowerCase()+'_tag">'+positions[i].transaction_type+'</p></div><div class="positions_row_instrument positions_row_instrument_title3" data-val="'+positions[i].tradingsymbol+'"><p>'+positions[i].tradingsymbol+'<span>&nbsp;'+positions[i].exchange+'</span>'+modified_html+'</p></div><div class="positions_row_product positions_row_product_title3" data-val="'+positions[i].product+'"><p>'+positions[i].product+'</p></div><div class="positions_row_quantity positions_row_quantity_title4" data-val="'+positions[i].quantity+'"><p>'+parseFloat(positions[i].filled_quantity).toFixed(6)+'/'+parseFloat(positions[i].quantity).toFixed(6)+'</p></div><div class="positions_row_ltp positions_row_ltp_title5"><p class="ltp"><span class="sub_title">&nbsp;</span><span class="sub_ltp">0.0</span></p></div><div class="positions_row_avg_price positions_row_avg_price_title6" data-val="'+positions[i].price+'"><p>'+parseFloat(positions[i].price).toFixed(2)+trigger_price_str+'</p></div>'
                
                var part3 = '';
                // if(parseFloat(positions[i].pnl)>0)
                //   pnl = '<div class="positions_row_pnl" data-realised='+positions[i].realised+' id="ulive__'+uid+'"><p class="profit">+'+parseFloat(positions[i].status).toFixed(2)+'<span>&nbsp;<!--(2.3%)--></span></p></div>'; 
                // else
                var status_tag = ''
                if(positions[i].status.toLowerCase()+'_tag'=='cancelled_tag' || positions[i].status.toLowerCase().indexOf('amo ')>-1)
                  status_tag = 'cancel_tag'
                else
                  status_tag = positions[i].status.toLowerCase()+'_tag'

                var pnl = '<div class="positions_row_pnl positions_row_pnl_title7" data-val="'+positions[i].status+'"><p class="'+status_tag+'">'+positions[i].status+'<span>&nbsp;<!--(2.3%)--></span></p></div>';
                var chg = '';//<div class="positions_row_change"><p style="color: #bfc7d1;font-weight: 400;">NA</p></div>';
                var algo_str = JSON.stringify(positions[i]);
                // var part4 = '<div class="positions_row_order_details"><p onclick="fetch_specific_position(\''+positions_executed[i].tradingsymbol+'\',\''+positions_executed[i].exchange+'\',\''+positions_executed[i].product+'\')">Details<span><img src="/static/imgs/icon-right-grey.png"></span></p></div></div></div>';
                if (positions[i].parent_order_id!=null && positions[i].product=='BO')
                {
                  var part4 = '<div class="positions_row_order_details"><p onclick=\'show_order_details('+algo_str+')\'><span>Details</span></p></div><div class="positions_row_change positions_row_change_title8"><p><span class="cancel_order" id="cancel_order" onclick="show_cancel_order_popup(\''+positions[i].tradingsymbol+'\',\''+positions[i].order_id+'\',\''+positions[i].product+'\',\''+positions[i].parent_order_id+'\')" ">Cancel</span></p></div></div></div>';
                }
                else{
                  var part4 = '<div class="positions_row_order_details"><p onclick=\'show_order_details('+algo_str+')\'><span>Details</span></p></div><div class="positions_row_change positions_row_change_title8"><p><span class="cancel_order" id="cancel_order" onclick="show_cancel_order_popup(\''+positions[i].tradingsymbol+'\',\''+positions[i].order_id+'\')" ">Cancel</span></p></div></div></div>';
                }
                $('.positions_details_title').after(part1+part3+pnl+chg+part4);


                // adding this for app_UI

                var app_part1 = '<div class="token__'+segment+'_'+positions[i].tradingsymbol+'"><div class="positions_details_row"><div class="positions_details_row_top"><div class="positions_row_product"><p class="'+positions[i].transaction_type.toLowerCase()+'_tag">'+positions[i].transaction_type+'</p></div><div class="positions_row_pnl"><p class="'+status_tag+'">'+positions[i].status+'<span>&nbsp;<!--(2.3%)--></span></p></div><div class="positions_row_datetime"><p>'+moment(positions[i].order_timestamp).format('HH:mm:ss')+'</p></div></div><div class="positions_details_row_bottom"><div class="positions_row_instrument"><p>'+positions[i].tradingsymbol+'<span>&nbsp;'+positions[i].exchange+'</span></p></div><div class="positions_row_product"><p>'+positions[i].product+'</p></div><div class="positions_row_quantity"><p>Qty:&nbsp;'+positions[i].filled_quantity+'/'+positions[i].quantity+'</p></div><div class="positions_row_avg_price"><p>'+parseFloat(positions[i].average_price).toFixed(2)+'</p></div></div>';
                if (positions[i].parent_order_id!=null && positions[i].product=='BO')
                {
                  var app_part2 = '<div class="positions_details_row_hidden"><div class="positions_row_order_details"><p onclick=\'show_order_details('+algo_str+')\'><span>Details</span></p></div><div class="positions_row_change"><p><span class="cancel_order" id="cancel_order" onclick="show_cancel_order_popup(\''+positions[i].tradingsymbol+'\',\''+positions[i].order_id+'\',\''+positions[i].product+'\',\''+positions[i].parent_order_id+'\')" ">Cancel</span></p></div></div></div></div>';
                }
                else{
                  var app_part2 = '<div class="positions_details_row_hidden"><div class="positions_row_order_details"><p onclick=\'show_order_details('+algo_str+')\'><span>Details</span></p></div><div class="positions_row_change"><p><span class="cancel_order" id="cancel_order" onclick="show_cancel_order_popup(\''+positions[i].tradingsymbol+'\',\''+positions[i].order_id+'\')" ">Cancel</span></p></div></div></div></div>';
                }
                $('#app_positions .holdings_body').prepend(app_part1+app_part2);
              }
            }
            $('.login_required_popup').hide();
        }else if(msg.status=="error" && (msg.error=="auth"||msg.error=="response error")){
            console.log('Broker login required');
            $('.login_required_popup').show();
            show_snackbar(null,'Login required',callback=function(){window.location="/";});
            $('.positions_details_row').each(function(){
                      $(this).parent().remove()
                });
        }
    }).fail(function(){
        $('.positions_details_row').each(function(){
                      $(this).parent().remove()
                });
        $('.profit').html('N/A');
        $('.profit').attr('style','color: #bfc7d1 !important;font-weight: 400 !important;');
        $('.empty_holdings').hide();
        $('.empty_positions').show();
        $('.positions_body').hide();
        $('#positions .header_bar').hide();
        show_snackbar(null,'Unable to connect to servers',callback=function(){window.location="/";});

    }).complete(function(){
      refresh_ltp_subscription();
      var menu_selected = $('.portfolio_menu_selected')[0].id
      if(menu_selected=='holdings_option'){
        if(executed_orders==0){
          $('.empty_holdings').show();
          $('.empty_positions').hide();
          $('.holdings_body').hide();
          $('#holdings .header_bar').hide();
          $('.positions_body').hide();
          $('#app_holdings .holdings_body').hide();
          $('#app_positions .holdings_body').hide();
          $('.positions_body').hide();
          $('#positions .header_bar').hide();
        }else{
          $('.empty_holdings').hide();
          $('.empty_positions').hide();
          $('.holdings_body').show();
          $('#holdings .header_bar').show();
          $('.positions_body').hide();
          $('#positions .header_bar').hide();
          $('#app_positions .holdings_body').hide();
          $('#app_holdings .holdings_body').show();
        }
      }
      else{
        if(open_orders==0){
          $('.empty_positions').show();
          $('.empty_holdings').hide();
          $('.holdings_body').hide();
          $('#holdings .header_bar').hide();
          $('#app_positions .holdings_body').hide();
          $('#app_holdings .holdings_body').hide();
          $('.positions_body').hide();
          $('#positions .header_bar').hide();
        }else{
          $('.empty_holdings').hide();
          $('.empty_positions').hide();
          $('.positions_body').show();
          $('#positions .header_bar').show();
          $('#app_positions .holdings_body').show();
          $('#app_holdings .holdings_body').hide();
        }
      }
      if(open_orders!=0){
        $('#positions_option').text('Open Orders ('+open_orders+')');
        $('#open_orders_heading_title').text('Open Orders ('+open_orders+')');
      }
      else{
        $('#positions_option').text('Open Orders');
        $('#open_orders_heading_title').text('Open Orders');
      }
      if(executed_orders!=0){
        $('#holdings_option').text('Executed Orders ('+executed_orders+')');
        $('#executed_orders_heading_title').text('Executed Orders ('+executed_orders+')');
      }
      else{
        $('#holdings_option').text('Executed Orders');
        $('#executed_orders_heading_title').text('Executed Orders');
      }

      attach_user_actions();
      $('.loading-dots-container').hide();
    });
}

function show_cancel_order_popup(symbol,order_id,variety="REGULAR",parent_order_id=""){
  $('.cancel_order_popup').show();
  $('body').addClass('body_scroll');
  $('#cancel_order_confirm').attr('onclick','cancel_order(\''+order_id+'\',\''+variety+'\',\''+parent_order_id+'\')');
  $('#cancel_order_confirm').removeAttr('style');
  $('.cancel_order_det').html(symbol+'<br><span>#'+order_id+'</span>')
}

function cancel_order(order_id,variety="REGULAR",parent_order_id=""){
  $('#cancel_order_confirm').removeAttr('onclick');
  $('#cancel_order_confirm').attr('style',"cursor:no-drop");
  var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
  var params = {
    'order_id':order_id,
    'variety':variety,
    'parent_order_id':parent_order_id,
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
          }
        }
    }).complete(function(){
      refresh_orderbook();
      close_cancel_order_popup();
      $('#cancel_order_confirm').removeAttr('style');
    });

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
    if(order_status.status_message==null)
      order_status.status_message = '';
    
    $('.order_details_popup').show();$('body').addClass('body_scroll');
    order_details_header = '<div class="order_name"> <p class="'+order_status.transaction_type+'_tag">'+order_status.transaction_type+'</p><p>'+order_status.tradingsymbol+'<span>'+order_status.exchange+'</span></p><p class="'+order_status.status+'_tag tags">'+order_status.status+'</p>';
    $('.order_details_header').html(order_details_header);

    // order_details_body = '<div class="order_details_row"> <div> <p>Price</p> <p>'+order_status.price+'</p> </div> <div> <p>Trigger Price</p> <p>'+order_status.trigger_price+'</p> </div> <div> <p>Order placed by</p> <p>'+order_status.placed_by+'</p> </div> </div> <div class="order_details_row"> <div> <p>Order Type</p> <p>'+order_status.order_type+'</p> </div> <div> <p>Product Validity</p> <p>'+order_status.product+'/'+order_status.validity+'</p> </div> <div> <p>Time</p> <p>'+order_status.order_timestamp+'</p> </div> </div> <div class="order_details_row"> <div> <p>Order ID</p> <p>'+order_status.order_id+'</p> </div> <div> <p>Exchange order ID</p> <p>'+order_status.exchange_order_id+'</p> </div> <div> <p>Exchange Time</p> <p>'+order_status.exchange_timestamp+'</p> </div> </div> <div class="order_details_row"> <div class="status"> <p>Status</p> <p '+green_style+'>'+order_status.status+'</p> </div> <div id="status_message"> <p>STATUS MESSAGE</p> <p >'+order_status.status_message+'</p> </div> </div>';
    
    order_details_body = '<div class="order_details_row"> <div> <p>Quantity</p> <p>'+parseFloat(order_status.filled_quantity).toFixed(6)+'/'+parseFloat(order_status.quantity).toFixed(6)+'</p> </div> <div> <p>Price</p> <p>'+order_status.price+'</p> </div> <div> <p>Avg. price</p> <p>'+parseFloat(order_status.average_price).toFixed(6)+'</p> </div> <div> <p>Trigger price</p> <p>'+parseFloat(order_status.trigger_price).toFixed(6)+'</p> </div> <div> <p>Order type</p> <p>'+order_status.order_type+'</p> </div> <div> <p>Product</p> <p>'+order_status.product+'</p> </div><div> <p>Validity</p> <p>'+order_status.validity+'</p> </div>  </div> <div class="order_details_row"></div> <div class="order_details_row"> <div> <p>Order ID</p> <p>'+order_status.order_id+'</p> </div> <div> <p>Exchange order ID</p> <p>'+order_status.exchange_order_id+'</p> </div> <div> <p>Time</p> <p>'+order_status.order_timestamp+'</p> </div> <div> <p>Exchange time</p> <p>'+order_status.exchange_timestamp+'</p> </div><div> <p>Placed by</p> <p>'+order_status.placed_by.toUpperCase()+'</p> </div> <div class="status_messages"><p>'+order_status.status_message+'</p></div></div>';
    $('.order_details_body').html(order_details_body);
}
function fetch_specific_position(symbol,exchange,product){
  $('.order_details_popup').show();
  $('body').addClass('body_scroll');
  var params = {
    'symbol':symbol,
    'exchange':exchange,
    'product':product
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/fetch_specific_position/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 10000,//40 sec timeout
      "retries": 3
    }

    $.ajax(settings).done(function (msg){
        if(msg.status=='success'){
          if(msg.positions.length=1){
            positions = msg.positions;
            pnl = '';
            if(parseFloat(positions[0].pnl)>0)
              pnl = '<p class="profit">+'+parseFloat(positions[0].pnl).toFixed(2)+'<span>&nbsp;<!--(2.3%)--></span></p>'; 
            else
              pnl = '<p class="loss">'+parseFloat(positions[0].pnl).toFixed(2)+'<span>&nbsp;<!--(2.3%)--></span></p>';
            
            order_details_header = '<div class="order_name"> <p>'+positions[0].tradingsymbol+'</p> <p>'+positions[0].product+'/'+positions[0].exchange+'</p> </div> <div class="order_net_qty"> <p>Net Qty</p> <p>'+positions[0].quantity+'</p> </div> <div class="order_avg_price"> <p>Avg. Price</p> <p>'+parseFloat(positions[0].average_price).toFixed(2)+'</p> </div> <div class="order_pnl"> <p>P&amp;L</p> '+pnl+' </div>';


            order_details_body = '<div class="order_details_row"> <div> <p>Previous Close</p> <p>'+positions[0].close_price+'</p> </div> <div> <p>LTP</p> <p>'+positions[0].last_price+'</p> </div> <div> <p>Day\'s P&amp;L</p> '+pnl+' </div> </div> <div class="order_details_row"> <div> <p>Buy Qty.</p> <p>'+positions[0].buy_quantity+'</p> </div> <div> <p>Buy Price</p> <p>'+parseFloat(positions[0].buy_price).toFixed(2)+'</p> </div> <div> <p>Buy Value</p> <p>'+parseFloat(positions[0].buy_value).toFixed(2)+'</p> </div> </div> <div class="order_details_row"> <div> <p>Sell Qty.</p> <p>'+parseFloat(positions[0].sell_quantity).toFixed(2)+'</p> </div> <div> <p>Sell Price</p> <p>'+parseFloat(positions[0].sell_price).toFixed(2)+'</p> </div> <div> <p>Sell Value</p> <p>'+parseFloat(positions[0].sell_value).toFixed(2)+'</p> </div> </div>';

            $('.order_details_header').html(order_details_header);
            $('.order_details_body').html(order_details_body);
          }
        }
    });
}
