var filter='Streak';
$(window).load(function() {
    // Animate loader off screen
    $(".loader_parent").fadeOut();
  });

function search_positions(){
  q = $('#positions_search_input').val();
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
        console.log('data_str',data_str)
        $(x[i]).removeClass('add_opacity');
      }
    }
  });
}

function search_holdings(){
  q = $('#holdings_search_input').val();
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
        console.log('data_str',data_str)
        $(x[i]).removeClass('add_opacity');
      }
    }
  });
}

function platform_update(e,plat){
  filter = plat;
  var menu_selected = $('.portfolio_menu_selected')[0].id
  if(menu_selected=='holdings_option'){
    fetch_holdings();
  }
  else{
    fetch_positions();
  }
  img = $(e).find('.logo_tag img').attr('src');
  $(".fancy_filter_options").slideToggle();
  $('.fancy_filter_select .logo_tag_big img').attr('src',img);
}

function show_positions(){
    $("#holdings").hide();
    $("#positions").show();
    $("#holdings_option").removeClass("portfolio_menu_selected");
    $("#positions_option").addClass("portfolio_menu_selected");
    $('#app_holdings .holdings_body').hide();
    $('#app_holdings .holdings_header').hide();
    // $('#app_positions .holdings_body').show();
}
function show_holdings(){
    $("#positions").hide();
    $("#holdings").show();
    $("#positions_option").removeClass("portfolio_menu_selected");
    $("#holdings_option").addClass("portfolio_menu_selected"); 
    $('#app_holdings .holdings_body').show();
    $('#app_holdings .holdings_header').show();
    $('#app_positions .holdings_body').hide();
}
function close_order_details_popup () {
    $(".close_popup").parents(".body").find(".order_details_popup").fadeOut();
    $("body").removeClass("body_scroll");
}
function close_exit_all_popup () {
    $(".close_popup").parents(".body").find(".exit_all_popup").fadeOut();
    $("body").removeClass("body_scroll");
}
function attach_user_actions(){
    $("#positions .positions_details_row").hover(function(){
      $(this).find(".positions_row_order_details span").show();
      if($(this).find(".positions_row_quantity p").text()!='0')
        $(this).find(".exit_all").show();
    });
    $("#positions .positions_details_row").mouseleave(function(){
      $(this).find(".exit_all").hide();
      $(this).find(".positions_row_order_details span").hide();
    });
    $("#app_positions .positions_details_row, #app_holdings .positions_details_row").click(function(){
      $(this).find(".positions_details_row_hidden").toggle();
    });
    $(".positions .exit_all, .holdings .exit_all").css({"display" : "none"});
    $("#app_positions .positions_details_row_hidden, #app_holdings .positions_details_row_hidden").hide();
    $(".holding_details_row").hover(function(){
      if($(this).find(".row_quantity p").text()!='0')
        $(this).find(".exit_all").show();
    });
    $(".holding_details_row").mouseleave(function(){
      $(this).find(".exit_all").hide();
    });
    $(".exit_all_popup").click(function(e){
    // alert($(".exit_all_popup").has(e.target).length);
    // alert($(".exit_all_popup").is(e.target));
      if(($(".exit_all_popup").has(e.target).length == 0)&&($(".exit_all_popup").is(e.target))){
        $("body").removeClass("body_scroll");
        $(".close_popup").parents(".body").find(".exit_all_popup").fadeOut();
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
      if(sorting_type=='asc')
        return $(a).find("."+column+" p").text() <= $(b).find("."+column+" p").text();
      else
        return $(a).find("."+column+" p").text() >= $(b).find("."+column+" p").text();
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

$(document).ready(function(){
    $('#portfolio_platform').val('All');
    if(window.location.href.indexOf('#holding')!=-1)
        fetch_holdings();
    else
      fetch_positions();
    $("#holdings_option").click(function(){
        fetch_holdings();
    });
    $("#positions_option").click(function(){
        fetch_positions();
    });
    $("#positions .positions_details_row").hover(function(){
      $(this).find(".exit_all").show();
      $(this).find(".positions_row_order_details span").show();
    });
    $("#positions .positions_details_row").mouseleave(function(){
      $(this).find(".exit_all").hide();
      $(this).find(".positions_row_order_details span").hide();
    });
    $(".positions .exit_all, .holdings .exit_all").css({"display" : "none"});
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
    $(".exit_all_popup").click(function(e){
    // alert($(".exit_all_popup").has(e.target).length);
    // alert($(".exit_all_popup").is(e.target));
    if(($(".exit_all_popup").has(e.target).length == 0)&&($(".exit_all_popup").is(e.target))){
      $("body").removeClass("body_scroll");
      $(".close_popup").parents(".body").find(".exit_all_popup").fadeOut();
    }
    });
    $(".fancy_filter_select").click(function(){
      $(".fancy_filter_options").slideToggle();
    });
    // $("#take_tour, #take_tour_mobile").click(function(){
    //     hopscotch.startTour(portfolio_tour());
    // });
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

        // fetch_positions();
        // console.log(ui.item.value);
        filter = ui.item.value;
        var menu_selected = $('.portfolio_menu_selected')[0].id
        if(menu_selected=='holdings_option'){
          fetch_holdings();
        }
        else{
          fetch_positions();
        }

        hide_show();
        
      }
    }).focus(function() {
      $(this).autocomplete('search', '');
    });

    setInterval(refresh_portfolio,45000);
});

function hide_show(){
  $('#portfolio_platform').hide();
  setTimeout(function(){ 
    $('#portfolio_platform').show();
  }, 10);
}

function refresh_portfolio(){
  $('#update_top_performance1').show();
  var menu_selected = $('.portfolio_menu_selected')[0].id
  if(menu_selected=='holdings_option'){
    fetch_holdings();
  }
  else{
    fetch_positions();
  }
}
function fetch_positions(){
    $('#update_top_performance1').show();
    var params = {
      'filter':filter
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/fetch_positions/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 10000,//40 sec timeout
    }

    $.ajax(settings).done(function (msg){
        if(msg.status=='success'){
            if(msg.positions.length==0){
                $('.positions_details_row').each(function(){
                      $(this).remove();
                });
                $('.profit').html('N/A');
                $('.profit').attr('style','color: #bfc7d1 !important;font-weight: 400 !important;');
                $('.empty_holdings').hide();
                $('.empty_positions').show();
                $('.positions_body').hide();
                $('#app_holdings .holdings_body').hide();
                $('#app_holdings .holdings_header').hide();
                $('#app_positions .holdings_body').hide();
                
                $('#positions_option').text('Positions');
                $('#positions_heading_title').text('Positions');
            }
            else{
              $('.empty_holdings').hide();
              $('.empty_positions').hide();
              $('.positions_body').show();
              $('#app_holdings .holdings_body').hide();
              $('#app_holdings .holdings_header').hide();
              $('#app_positions .holdings_body').show();

              $('#positions_option').text('Positions ('+msg.positions.length+')');
              $('#positions_heading_title').text('Positions ('+msg.positions.length+')');
              // filling the orders portfolio
              positions = msg.positions;
              total_pnl = 0.0;
              $('.positions_body .positions_details_row').each(function(){
                      $(this).parent().remove()
              });
              $('#app_positions .holdings_body').html('');

              for(var i=0;i<positions.length;i++){

                segment = 'NSE'
                if (positions[i].exchange=='NSE')
                  segment = 'NSE'
                else if (positions[i].exchange=='NFO')
                  if(positions[i].tradingsymbol.endsWith('FUT'))
                    segment = 'NFO-FUT'
                  else
                    segment = 'NFO-OPT'
                else if (positions[i].exchange=='CDS')
                  if(positions[i].tradingsymbol.endsWith('FUT'))
                    segment = 'CDS-FUT'
                  else
                    segment = 'CDS-OPT'
                else if (positions[i].exchange=='MCX')
                  if(positions[i].tradingsymbol.endsWith('FUT'))
                    segment = 'MCX'
                  else
                    segment = 'MCX-OPT'

                uid = positions[i]['user_uuid'];
                
                closed_positions = '';

                if(positions[i].quantity==0){
                  closed_positions = 'closed_positions';
                }
                
                modified_html = '';
                if(positions[i].modified==1)
                  modified_html='<span data-tooltip-top="Looks like you have taken manual positions through Kite" class="exclamatory_mark">!</span>';

                part1 = '<div class="token__'+segment+'_'+positions[i].tradingsymbol+'"><div class="positions_details_row '+closed_positions+'"><div class="positions_row_product" data-val="'+positions[i].product+'"><p class="'+positions[i].product.toLowerCase()+'_tag">'+positions[i].product+'</p></div><div class="positions_row_instrument"  data-val="'+positions[i].tradingsymbol+'"><p>'+positions[i].tradingsymbol+'<span>&nbsp;'+positions[i].exchange+'</span>'+modified_html+'</p></div><div class="positions_row_quantity"><p>'+positions[i].quantity+'</p></div><div class="positions_row_avg_price" data-val="'+parseFloat(positions[i].average_price).toFixed(2)+'"><p>&#8377;&nbsp;'+parseFloat(positions[i].average_price).toFixed(2)+'</p></div>'
                
                part3 = '<div class="positions_row_ltp"><p class="ltp"><span class="sub_title">&nbsp;</span><span class="sub_ltp">0.0</span></p></div>';

                pnl_change = '0.0%';
                pnl_change_class = '';
                if(parseFloat(positions[i].pnl)>0)
                  {
                    pnl = '<div class="positions_row_pnl" data-val="'+positions[i].pnl+'" data-multiplier='+positions[i].multiplier+' data-sell_value='+positions[i].sell_value+' data-buy_value='+positions[i].buy_value+' data-pnl='+positions[i].pnl+' id="ulive__'+uid+'"><p class="profit">&#8377;&nbsp;+'+parseFloat(positions[i].pnl).toFixed(2)+'<span>&nbsp;<!--(2.3%)--></span></p></div>'; 
                  pnl_change = parseFloat((parseFloat(positions[i].pnl)/(positions[i].average_price*positions[i].multiplier*positions[i].quantity))*100).toFixed(2)+"%";
                  pnl_change_class = 'profit';
                }
                else
                  {
                    pnl = '<div class="positions_row_pnl" data-val="'+parseFloat(positions[i].pnl).toFixed(2)+'" data-multiplier='+positions[i].multiplier+' data-sell_value='+positions[i].sell_value+' data-buy_value='+positions[i].buy_value+' data-pnl='+positions[i].pnl+' id="ulive__'+uid+'"><p class="loss">&#8377;&nbsp;'+parseFloat(positions[i].pnl).toFixed(2)+'<span>&nbsp;<!--(2.3%)--></span></p></div>';
                  pnl_change = parseFloat((parseFloat(positions[i].pnl)/(positions[i].average_price*positions[i].multiplier*positions[i].quantity))*100).toFixed(2)+"%";
                  pnl_change_class = 'loss';
                }

                if(positions[i].quantity==0){
                  pnl_change = "0.0%";
                }

                total_pnl += parseFloat(positions[i].pnl);
                var order_type = 'MARKET';
                var quantity = positions[i].quantity;
                var product = positions[i].product.toUpperCase();
                // part4 = '<div class="positions_row_change"><p><span class="exit_all" id="exit_all" onclick=\"exit_all(event,"'+positions[i].tradingsymbol+'","'+positions[i].exchange+'","'+positions[i].product.toUpperCase()+'",\''+positions_obj+'\')\" style="display:none">Exit all</span></p></div><div class="positions_row_order_details"><p onclick="fetch_specific_position(\''+positions[i].tradingsymbol+'\',\''+positions[i].exchange+'\',\''+positions[i].product+'\')">Details<span><img src="/static/imgs/icon-right-grey.png"></span></p></div></div></div>';
                part4 = '<div class="positions_row_order_details"><p class='+pnl_change_class+' onclick="fetch_specific_position(\''+positions[i].tradingsymbol+'\',\''+positions[i].exchange+'\',\''+positions[i].product+'\')">'+pnl_change+'<span>Details</span></p></div><div class="positions_row_change"><p><span class="exit_all" id="exit_all" onclick="exit_all(event,\''+positions[i].tradingsymbol+'\',\''+positions[i].exchange+'\',\''+positions[i].product.toUpperCase()+'\',\''+order_type+'\','+quantity+')"">Exit all</span></p></div></div></div>';
                $('.positions_details_title').after(part1+part3+pnl+part4);

                // adding this for app_UI

                var app_part1 = '<div class="token__'+segment+'_'+positions[i].tradingsymbol+'"><div class="positions_details_row '+closed_positions+'"><div class="positions_details_row_top"><div class="positions_row_product"><p class="'+positions[i].product.toLowerCase()+'_tag">'+positions[i].product+'</p></div><div class="positions_row_quantity"><p>Qty: '+positions[i].quantity+'</p></div><div class="positions_row_ltp"><p class="ltp"><span class="sub_title">&nbsp;</span><span class="sub_ltp">0.0</span></p></div></div><div class="positions_details_row_bottom"><div class="positions_row_instrument"><p>'+positions[i].tradingsymbol+'<span>&nbsp;'+positions[i].exchange+'</span>'+modified_html+'</p></div><div class="positions_row_avg_price"><p>&#8377;&nbsp;'+parseFloat(positions[i].average_price).toFixed(2)+'</p></div>'+pnl+'</div><div class="positions_details_row_hidden">';
                var app_part2 = '<div class="positions_row_order_details"><p onclick="fetch_specific_position(\''+positions[i].tradingsymbol+'\',\''+positions[i].exchange+'\',\''+positions[i].product+'\')">'+pnl_change+'<span>Details</span></p></div><div class="positions_row_change"><p><span class="exit_all" id="exit_all" onclick="exit_all(event,\''+positions[i].tradingsymbol+'\',\''+positions[i].exchange+'\',\''+positions[i].product.toUpperCase()+'\',\''+order_type+'\','+quantity+')"">Exit all</span></p></div></div></div></div></div>'

                $('#app_positions .holdings_body').prepend(app_part1+app_part2);
              }
              // if(total_pnl!=0)
                // $('#app_positions .holdings_body').append('<div class="positions_total_row"><div class="positions_total"><p>Total&nbsp;</p><p class="positions_total_pnl" style="color: #bfc7d1;font-weight: 400;">NA</p></div></div>');
                $('#app_positions .holdings_body').append('<div class="positions_total_row"><div class="positions_row_product"><p></p></div><div class="positions_row_instrument"><p></p></div><div class="positions_row_quantity"><p></p></div><div class="positions_row_avg_price"><p></p></div><div class="positions_row_ltp"><p>Total</p></div><div class="positions_row_pnl"><p class="positions_total_pnl">+0.0<span>&nbsp;</span></p></div><div class="positions_row_order_details"><p></p></div><div class="positions_row_change"><p></p></div></div>');
              if(total_pnl>=0)
                {
                  $('.positions_total_pnl').html('&#8377;&nbsp;+'+parseFloat(total_pnl).toFixed(2));
                  $('.positions_total_pnl').removeAttr('style');
                  $('.positions_total_pnl').removeClass('loss');
                  $('.positions_total_pnl').addClass('profit');

                }
              else
                {
                  $('.positions_total_pnl').html('&#8377;&nbsp;'+parseFloat(total_pnl).toFixed(2));
                  $('.positions_total_pnl').removeAttr('style');
                  $('.positions_total_pnl').removeClass('profit');
                  $('.positions_total_pnl').addClass('loss');
                }
              setTimeout(function(){
                  refresh_ltp_subscription();
              },1000);
            }
            $('.login_required_popup').hide();
        }else if(msg.status=="error" && msg.error=="auth"){
            console.log('Broker login required');
            $('.login_required_popup').show();
            show_snackbar(null,'Login required',callback=function(){window.location="/";});
            $('.positions_details_row').each(function(){
                      $(this).remove();
                });
            $('.profit').html('N/A');
            $('.profit').attr('style','color: #bfc7d1 !important;font-weight: 400 !important;');
            $('.empty_holdings').hide();
            $('.empty_positions').show();
            $('.positions_body').hide();
            $('#app_holdings .holdings_body').hide();
            $('#app_holdings .holdings_header').hide();
            $('#app_positions .holdings_body').hide();

            $('#positions_option').text('Positions');
            $('#positions_heading_title').text('Positions');
        }
    }).fail(function(){
        $('.positions_details_row').each(function(){
                      $(this).remove();
                });
        $('#app_positions .holdings_body').html('');
        $('.profit').html('N/A');
        $('.profit').attr('style','color: #bfc7d1 !important;font-weight: 400 !important;');
        $('.empty_holdings').hide();
        $('.empty_positions').show();
        $('.positions_body').hide();
        $('#app_holdings .holdings_body').hide();
        $('#app_holdings .holdings_header').hide();
        $('#app_positions .holdings_body').hide();

        $('#positions_option').text('Positions');
        $('#positions_heading_title').text('Positions');
    }).complete(function(){
        show_positions();
        attach_user_actions();
        $('#update_top_performance1').hide();
        fetch_holdings_dummy();
    });
}

function stop_and_exit_all(event,symbol,exchange,product,order_type,quantity){
    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    var params = {
    'symbol':symbol,
    'exchange':exchange,
    'product':product,
    'order_type':order_type,
    'quantity':quantity,
    'csrfmiddlewaretoken':csrfmiddlewaretoken
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/exit_all/',
      "method": "POST",
      "headers": {
      },
      "data":params,
      "timeout": 40000,//40 sec timeout
      "retries": 3
    }
    ////////////////
    // $(event.target).attr('style','background-color:rgba(255, 67, 67, 0.8);border-color:rgba(255, 67, 67, 0.8);');
    $(event.target).html("<img src='/static/imgs/button-loading-rect.gif' id='button_loading'>");
    $(event.target).css({'cursor': 'no-drop'});
    $(event.target).removeAttr('onclick');
    ////////////////
    $.ajax(settings).done(function (msg){
        if(msg.status=='success'){
          refresh_portfolio();
          show_snackbar(null,'Order placed','success');
          close_exit_all_popup();
        }else{
          refresh_portfolio();
          show_snackbar(null,'Some error');
          close_exit_all_popup();
        }
      }).complete(function(){
      }).fail(function(){
        $(event.target).removeAttr('style');
        $(event.target).html("<img src=\"/static/imgs/icon-force-stop.png\">&nbsp;&nbsp;Stop");
        $(event.target).css({'cursor': 'pointer'});
        $(event.target).attr('onclick','stop_and_exit_all(event,\''+symbol+'\',\''+exchange+'\',\''+product+'\',\''+order_type+'\','+quantity+');');
      });
}
function exit_all(event,symbol,exchange,product,order_type,quantity){
    var params = {
    'symbol':symbol,
    'exchange':exchange,
    'product':product
    };

    if(product=="BO")
    {
      show_snackbar(null,'Exit BO from order book');
      if(window.location.href.indexOf('/orderbook/')!=-1){

      }
      else{
        window.location='/orderbook/?platform=all&variety=BOE';
        return;
      }
    }

    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/get_live_algos/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 40000,//40 sec timeout
      "retries": 3
    }
    $.ajax(settings).done(function (msg){
        if(msg.status=='success'){
          $('.exit_all_popup').show();$('body').addClass('body_scroll');
          var exit_algo_names = $('#exit_algo_names');
          exit_algo_names.empty();
          for(var i=0;i<msg.algo_names.length;i++){
            exit_algo_names.append('<span><span></span>&nbsp;'+msg.algo_names[i]+'</span>');
          }

            exit_window = $('.exit_window');
            exit_window.find('.exit_header').removeClass('exit_header_buy');
            exit_window.find('.exit_header').removeClass('exit_header_sell');
            $('.stop_heading').show();
            $('.stop_sub_heading').show();
            $('.back').show();
            $('.exit_position_section').removeAttr('style');
            if(quantity>=0)
            {
                exit_window.find('.exit_header').addClass('exit_header_sell');
                exit_window.find('.exit_header').removeClass('exit_header_buy');
                [seg,sym] = [segment,symbol];
                exit_window.find('.exit_header').html("<p>Sell "+sym+"&nbsp;x"+Math.abs(quantity)+'<br><span>At market on '+seg+'</span></p>');

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

                // exit_window.find('.exit_body').html('<div class="exit_options">'+x+'<div class="exit_qty"><p>Quantity</p><input type="number" id="position_qty" name="" value="'+Math.abs(positions.qty)+'"></div></div><div><div class="radio_options"><div><span id="sell_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MARKET</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div></div><div class="exit_price"><p>Price</p><input type="number" id="position_price" name="" value="0"></div></div></div><div  id="notif_actions"><button id="sell" onclick="exit_position_now_force_stop(\''+deployment_uuid+'\',\''+seg+'\',\''+sym+'\','+Math.abs(positions.qty)+',\'MARKET\',\'SELL\',\''+product+'\',\'DAY\',\''+msg.algo_uuid+'\',\''+msg.algo_name+'\');">Sell</button><button id="cancel" onclick="close_exit_all_popup();">Cancel</button></div>');
                
                exit_window.find('.exit_body').html('<div class="exit_options">'+x+'<div class="notif_left"><div class="exit_qty"><p>Qty.</p><input type="number" id="position_qty" name="" value="'+Math.abs(quantity)+'" readonly></div><div class="exit_qty"><p>Price</p><input type="number" name="" id="position_price" value="'+0+'" readonly></div></div></div><div><div class="radio_options"><div><span id="sell_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MARKET</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL-M</p></div></div><div class="notif_right"><div class="exit_price"><p>Trigger price</p><input type="number" class="bg-stripe" id="position_trigger_price" name="" value="0" readonly></div><div class="exit_price"><p>Disclosed qty.</p><input type="number" class="bg-stripe" id="position_disclosed_qty" name="" value="0" readonly></div></div></div></div><div id="notif_actions"><button id="sell" onclick="stop_and_exit_all(event,\''+symbol+'\',\''+exchange+'\',\''+product+'\',\''+order_type+'\','+quantity+');">Sell</button><button id="cancel" onclick="close_exit_all_popup();">Cancel</button></div>');
            }
            else{
                exit_window.find('.exit_header').addClass('exit_header_buy');
                exit_window.find('.exit_header').removeClass('exit_header_sell');
                [seg,sym] = [segment,symbol];
                exit_window.find('.exit_header').html("<p>Buy "+sym+"&nbsp;x"+Math.abs(quantity)+'<br><span>At market on '+seg+'</span></p>');

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

                // exit_window.find('.exit_body').html('<div class="exit_options">'+x+'<div class="exit_qty"><p>Quantity</p><input type="number" id="position_qty" name="" value="'+Math.abs(positions.qty)+'"></div></div><div><div class="radio_options"><div><span id="buy_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MARKET</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div></div><div class="exit_price"><p>Price</p><input type="number" id="position_price" name="" value="0"></div></div></div><div  id="notif_actions"><button id="buy" onclick="exit_position_now_force_stop(\''+deployment_uuid+'\',\''+seg+'\',\''+sym+'\','+Math.abs(positions.qty)+',\'MARKET\',\'BUY\',\''+product+'\',\'DAY\',\''+msg.algo_uuid+'\',\''+msg.algo_name+'\');">Buy</button><button id="cancel" onclick="close_exit_all_popup();">Cancel</button></div>');
                
                exit_window.find('.exit_body').html('<div class="exit_options">'+x+'<div class="notif_left"><div class="exit_qty"><p>Qty.</p><input type="number" id="position_qty" name="" value="'+Math.abs(quantity)+'" readonly></div><div class="exit_qty"><p>Price</p><input type="number" name="" id="position_price" value="'+0+'" readonly></div></div></div><div><div class="radio_options"><div><span id="buy_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MARKET</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL-M</p></div></div><div class="notif_right"><div class="exit_price"><p>Trigger price</p><input type="number" class="bg-stripe" id="position_trigger_price" name="" value="0" readonly></div><div class="exit_price"><p>Disclosed qty.</p><input type="number" class="bg-stripe" id="position_disclosed_qty" name="" value="0" readonly></div></div></div></div><div id="notif_actions"><button id="buy" onclick="stop_and_exit_all(event,\''+symbol+'\',\''+exchange+'\',\''+product+'\',\''+order_type+'\','+quantity+');">Buy</button><button id="cancel" onclick="close_exit_all_popup();">Cancel</button></div>');
            }

        }else{

        }
      }).complete(function(){
          refresh_portfolio();
      }).fail(function(){
      });
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

    $('.order_details_header').html('');
    $('.order_details_body').html('');
    $.ajax(settings).done(function (msg){
        if(msg.status=='success'){
          if(msg.positions.length=1){
            positions = msg.positions;
            pnl = '';
            if(parseFloat(positions[0].pnl)>0)
              pnl = '<p class="profit">+'+parseFloat(positions[0].pnl).toFixed(2)+'<span>&nbsp;<!--(2.3%)--></span></p>'; 
            else
              pnl = '<p class="loss">'+parseFloat(positions[0].pnl).toFixed(2)+'<span>&nbsp;<!--(2.3%)--></span></p>';
            
            status = 'CLOSED';
            status_tag = 'closed_tag';
            if(positions[0].quantity!=0){
              status = 'OPEN';
              status_tag = 'open_tag';
            }
            order_details_header = '<div class="order_name"> <p class="'+positions[0].product.toLowerCase()+'_tag">'+positions[0].product+'</p><p>'+positions[0].tradingsymbol+'<span>'+positions[0].exchange+'</span></p><p class="'+status_tag+' tags">'+status+'</p>';


            // order_details_body = '<div class="order_details_row"> <div> <p>Previous Close</p> <p>'+positions[0].close_price+'</p> </div> <div> <p>LTP</p> <p>'+positions[0].last_price+'</p> </div> <div> <p>Day\'s P&amp;L</p> '+pnl+' </div> </div> <div class="order_details_row"> <div> <p>Buy Qty.</p> <p>'+positions[0].buy_quantity+'</p> </div> <div> <p>Buy Price</p> <p>'+parseFloat(positions[0].buy_price).toFixed(2)+'</p> </div> <div> <p>Buy Value</p> <p>'+parseFloat(positions[0].buy_value).toFixed(2)+'</p> </div> </div> <div class="order_details_row"> <div> <p>Sell Qty.</p> <p>'+parseFloat(positions[0].sell_quantity).toFixed(2)+'</p> </div> <div> <p>Sell Price</p> <p>'+parseFloat(positions[0].sell_price).toFixed(2)+'</p> </div> <div> <p>Sell Value</p> <p>'+parseFloat(positions[0].sell_value).toFixed(2)+'</p> </div> </div>';

            order_details_body = '<div class="order_details_row"> <div> <p>Net qty.</p> <p>'+positions[0].quantity+'</p> </div> <div> <p>Carry forward qty.</p> <p>'+positions[0].overnight_quantity+'</p> </div> <div> <p>Avg. price</p> <p>'+parseFloat(positions[0].average_price).toFixed(2)+'</p> </div> <div> <p>Last price</p> <p>'+positions[0].last_price+'</p> </div> <div> <p>Last close price</p> <p>'+positions[0].close_price+'</p> </div> <div> <p>P&L</p> <p>'+parseFloat(positions[0].pnl).toFixed(2)+'</p> </div> <div> <p>Day\'s P&amp;L</p> <p>'+parseFloat(positions[0].m2m).toFixed(2)+'<p> </div> <div> <p>Product</p> <p>'+positions[0].product+'</p> </div> </div> <div class="order_details_row"></div> <div class="order_details_row"><div class="order_details_right"><div> <p class="title_tags">Buys</p> <p></p> </div><div> <p>Qty.</p> <p>'+positions[0].buy_quantity+'</p> </div><div> <p>Price</p> <p>'+parseFloat(positions[0].buy_price).toFixed(2)+'</p> </div> <div> <p>Value</p> <p>'+positions[0].buy_value+'</p> </div></div><div class="order_details_right"><div><p class="title_tags">Sells</p> <p></p> </div><div> <p>Qty.</p> <p>'+positions[0].sell_quantity+'</p> </div><div> <p>Price</p> <p>'+parseFloat(positions[0].sell_price).toFixed(2)+'</p> </div> <div> <p>Value</p> <p>'+positions[0].sell_value+'</p> </div></div></div>';

            $('.order_details_header').html(order_details_header);
            $('.order_details_body').html(order_details_body);
          }
        }
    });
}

function fetch_holdings_dummy(){
    var params = {
      'filter':filter
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/fetch_holdings/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 10000,//40 sec timeout
    }

    $.ajax(settings).done(function (msg){
        if(msg.status=='success'){
            if(msg.positions.length==0){
                $('#holdings_option').text('Holdings');
                $('#holdings_heading_title').text('Holdings');
            }else{
              $('#holdings_option').text('Holdings ('+msg.positions.length+')');
              $('#holdings_heading_title').text('Holdings ('+msg.positions.length+')');
            }
          }
      });
  }
function fetch_positions_dummy(){
    var params = {
      'filter':filter
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/fetch_positions/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 10000,//40 sec timeout
    }

    $.ajax(settings).done(function (msg){
        if(msg.status=='success'){
            if(msg.positions.length==0){
              $('#positions_option').text('Positions');
              $('#positions_heading_title').text('Positions');
            }else{
              $('#positions_option').text('Positions ('+msg.positions.length+')');
              $('#positions_heading_title').text('Positions ('+msg.positions.length+')');
            }
          }
      });
  }
function fetch_holdings(){
    $('#update_top_performance1').show();
    var params = {
      'filter':filter
    };
    var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/fetch_holdings/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 10000,//40 sec timeout
    }

    $.ajax(settings).done(function (msg){
        if(msg.status=='success'){
            if(msg.positions.length==0){
                $('.holding_details_row').each(function(){
                      $(this).remove();
                });
                $('#app_holdings .holdings_body').html('');

                $('profit_and_loss .profit').html('N/A');
                $('profit_and_loss .profit').attr('style','color: #bfc7d1 !important;font-weight: 400 !important;');
                $('.current_value .header_content').html('<p>&#8377;&nbsp;&nbsp;0</p><p>Current value</p>');
                $('.total_investment .header_content').html('<p>&#8377;&nbsp;&nbsp;0</p><p>Total investment</p>');
                $('.profit_and_loss .header_content').html('<p>&#8377;&nbsp;&nbsp;0</p><p>P&L</p>');
                $('.empty_holdings').show();
                $('.empty_positions').hide();
                $('.holdings_body').hide();
                $('.holdings_header').hide();
                $('#app_holdings .holdings_body').hide();
                $('#app_holdings .holdings_header').hide();
                $('#app_positions .holdings_body').hide();
                $('#holdings_option').text('Holdings');
                $('#holdings_heading_title').text('Holdings');
            }
            else{
              $('.empty_holdings').hide();
              $('.empty_positions').hide();
              $('.holdings_body').show();
              $('.holdings_header').show();
              $('#app_holdings .holdings_body').show();
              $('#app_holdings .holdings_header').show();
              $('#app_positions .holdings_body').hide();

              $('#holdings_option').text('Holdings ('+msg.positions.length+')');
              $('#holdings_heading_title').text('Holdings ('+msg.positions.length+')');
              // filling the orders holding
              positions = msg.positions;
              total_pnl = 0.0;
              current_value = 0.0;
              total_investment = 0.0;
              percent_pnl = 0.0;

              $('.holding_details_row').each(function(){
                    $(this).remove();
                });
              $('#app_holdings .holdings_body').html('');
              
              for(var i=0;i<positions.length;i++){

                segment = 'NSE'
                if (positions[i].exchange=='NSE')
                  segment = 'NSE'
                else if (positions[i].exchange=='NFO')
                  if(positions[i].tradingsymbol.endsWith('FUT'))
                    segment = 'NFO-FUT'
                  else
                    segment = 'NFO-OPT'
                else if (positions[i].exchange=='CDS')
                  if(positions[i].tradingsymbol.endsWith('FUT'))
                    segment = 'CDS-FUT'
                  else
                    segment = 'CDS-OPT'
                else if (positions[i].exchange=='MCX')
                  if(positions[i].tradingsymbol.endsWith('FUT'))
                    segment = 'MCX'
                  else
                    segment = 'MCX-OPT'

                total_pnl += parseFloat(positions[i].pnl);
                
                uid = positions[i]['user_uuid'];

                current_value += positions[i].average_price*(positions[i].realised_quantity+positions[i].t1_quantity)+positions[i].pnl;
                total_investment += positions[i].average_price*(positions[i].realised_quantity+positions[i].t1_quantity);

                if(parseFloat(positions[i].pnl)>0)
                  pnl = '<div class="row_pnl" id="ulive__'+uid+'"><p class="profit">&#8377;&nbsp;+'+parseFloat(positions[i].pnl).toFixed(2)+'<span>&nbsp;<!--(2.3%)--></span></p></div>'; 
                else
                  pnl = '<div class="row_pnl" id="ulive__'+uid+'"><p class="loss">&#8377;&nbsp;'+parseFloat(positions[i].pnl).toFixed(2)+'<span>&nbsp;<!--(2.3%)--></span></p></div>';
                // '<div class="row_pnl"><p class="ltp"><span class="sub_title">LTP:&nbsp;&nbsp;</span><span class="sub_ltp">0.0</span></p></div>'

                modified_html = '';
                if(positions[i].modified==1)
                  modified_html = '<span data-tooltip-top="Looks like you have taken manual positions through Kite" class="exclamatory_mark">!</span>';

                var order_type = 'MARKET';
                var quantity = positions[i].realised_quantity;
                var product = positions[i].product.toUpperCase();

                var net_change = parseFloat(positions[i].pnl/((positions[i].realised_quantity+positions[i].t1_quantity)*positions[i].average_price)*100).toFixed(2)
                if(net_change>0){
                  net_change = '<p class="profit">'+net_change+'%</p>';
                }else if(net_change<0){
                  net_change = '<p class="loss">'+net_change+'%</p>';
                }else{
                  net_change = '<p>'+net_change+'%</p>';
                }

                var day_change_percent =(positions[i].day_change_percentage).toFixed(2)
                if(day_change_percent>0){
                  day_change_percent = '<p class="profit">'+day_change_percent+'%';
                }else if(day_change_percent<0){
                  day_change_percent = '<p class="loss">'+day_change_percent+'%';
                }else{
                  day_change_percent = '<p>'+day_change_percent+'%';
                }

                part1 = '<div class="token__'+segment+'_'+positions[i].tradingsymbol+'"><div class="holding_details_row"><div class="row_instrument" data-val="'+positions[i].tradingsymbol+'"><p>'+positions[i].tradingsymbol+'<span>&nbsp;'+positions[i].exchange+'</span>'+modified_html+'</p></div><div class="row_quantity" data-val="'+(positions[i].realised_quantity+positions[i].t1_quantity)+'"><p>'+(positions[i].realised_quantity+positions[i].t1_quantity)+'</p></div> <div class="row_avg_cost" data-val="'+parseFloat(positions[i].average_price).toFixed(2)+'"><p>&#8377;&nbsp;'+parseFloat(positions[i].average_price).toFixed(2)+'</p></div> <div class="row_ltp"><p class="ltp"><span class="sub_title"></span><span class="sub_ltp">0.0</span></p></div> <div class="row_current_value" data-val="'+parseFloat(positions[i].average_price*(positions[i].realised_quantity+positions[i].t1_quantity)+positions[i].pnl).toFixed(2)+'"><p><span class="sub_ltp_curr_value">'+parseFloat(positions[i].average_price*(positions[i].realised_quantity+positions[i].t1_quantity)+positions[i].pnl).toFixed(2)+'</span></p></div>'+pnl+'<div class="row_net_change">'+net_change+'</div> <div class="positions_row_change">'+day_change_percent+'<span class="exit_all" id="exit_all" onclick="exit_all(event,\''+positions[i].tradingsymbol+'\',\''+positions[i].exchange+'\',\''+positions[i].product.toUpperCase()+'\',\''+order_type+'\','+(positions[i].realised_quantity+positions[i].t1_quantity)+')">Exit all</span></p></div> </div></div>'
                
                $('.holding_details_title').after(part1);

                // adding this for app_UI

                var app_part1 = '<div class="token__'+segment+'_'+positions[i].tradingsymbol+'"><div class="positions_details_row"><div class="positions_details_row_top"><div class="positions_row_product"><p class="'+positions[i].product.toLowerCase()+'_tag">'+positions[i].product+'</p></div><div class="row_quantity"><p>Qty: '+(positions[i].realised_quantity+positions[i].t1_quantity)+'</p></div><div class="row_ltp"><p class="ltp"><span class="sub_title"></span><span class="sub_ltp">0.0</span></p></div></div><div class="positions_details_row_bottom"><div class="row_instrument"><p>'+positions[i].tradingsymbol+'<span>&nbsp;'+positions[i].exchange+'</span>'+modified_html+'</p></div><div class="row_avg_cost"><p>&#8377;&nbsp;'+parseFloat(positions[i].average_price).toFixed(2)+'</p></div>'+pnl+'</div><div class="positions_details_row_hidden">';
                var app_part2 = '<div class="positions_row_change"><p>'+(positions[i].day_change_percentage).toFixed(2)+'<span class="exit_all" id="exit_all" onclick="exit_all(event,\''+positions[i].tradingsymbol+'\',\''+positions[i].exchange+'\',\''+positions[i].product.toUpperCase()+'\',\''+order_type+'\','+(positions[i].realised_quantity+positions[i].t1_quantity)+')"">Exit all</span></p></div></div></div></div></div>'

                $('#app_holdings .holdings_body').prepend(app_part1+app_part2);
                
              }

              if(total_investment!=0.0){
                $('.total_investment .header_content').html('<p>&#8377;&nbsp;&nbsp;'+parseFloat(total_investment).toFixed(2)+'</p><p>Total investment</p>');
                percent_pnl = parseFloat(total_pnl/total_investment*100).toFixed(2);
              }
              else{
                $('.total_investment .header_content').html('<p>&nbsp;-</p><p>Total investment</p>');
                percent_pnl = '-';
              }
              if(current_value!=0.0){
                $('.current_value .header_content').html('<p>&#8377;&nbsp;&nbsp;'+parseFloat(current_value).toFixed(2)+'</p><p>Current value</p>');
              }
              else{
                $('.current_value .header_content').html('<p>&nbsp;-</p><p>Current value</p>');
              }

              if(total_pnl>=0)
                {
                  if(total_investment!=0.0)
                    {
                      $('.profit_and_loss .profit_and_loss_value').html('&#8377;&nbsp;&nbsp;'+parseFloat(total_pnl).toFixed(2)+'&nbsp;<span>(+'+percent_pnl+'%)</span>');
                    }
                  else
                    $('.profit_and_loss .profit_and_loss_value').html('&#8377;&nbsp;&nbsp;'+parseFloat(total_pnl).toFixed(2)+'&nbsp;<span></span>');
                  $('.positions_total_pnl').removeAttr('style');
                  $('.positions_total_pnl').removeClass('loss');
                  $('.positions_total_pnl').addClass('profit');

                  $('.profit_and_loss .profit_and_loss_value').removeAttr('style');
                  $('.profit_and_loss .profit_and_loss_value').removeClass('loss');
                  $('.profit_and_loss .profit_and_loss_value').addClass('profit');
                }
              else
                {
                  if(total_investment!=0.0)
                    $('.profit_and_loss .profit_and_loss_value').html('&#8377;&nbsp;&nbsp;'+parseFloat(total_pnl).toFixed(2)+'&nbsp;<span>('+percent_pnl+'%)</span>');
                  else
                    $('.profit_and_loss .profit_and_loss_value').html('&#8377;&nbsp;&nbsp;'+parseFloat(total_pnl).toFixed(2)+'&nbsp;<span></span>');
                  $('.profit_and_loss').removeAttr('style');
                  $('.positions_total_pnl').removeClass('profit');
                  $('.positions_total_pnl').addClass('loss');

                  $('.profit_and_loss .profit_and_loss_value').removeAttr('style');
                  $('.profit_and_loss .profit_and_loss_value').removeClass('profit');
                  $('.profit_and_loss .profit_and_loss_value').addClass('loss');

                  // $('.profit_and_loss .profit_and_loss_value').removeAttr('style');
                  // $('.profit_and_loss .profit_and_loss_value').removeClass('loss');
                  // $('.profit_and_loss .profit_and_loss_value').addClass('profit');
                }
              setTimeout(function(){
                  refresh_ltp_subscription();
              },1000);
            }
            $('.login_required_popup').hide();
        }else if(msg.status=="error" && msg.error=="auth"){
            console.log('Broker login required');
            $('.login_required_popup').show();
            show_snackbar(null,'Login required',callback=function(){window.location="/";});
            $('.holding_details_row').each(function(){
                      $(this).remove();
                });
            $('profit_and_loss .profit').html('N/A');
            $('profit_and_loss .profit').attr('style','color: #bfc7d1 !important;font-weight: 400 !important;');
            $('.current_value .header_content').html('<p>&#8377;&nbsp;0</p><p>Current value</p>');
            $('.total_investment .header_content').html('<p>&#8377;&nbsp;0</p><p>Total investment</p>');
            $('.empty_holdings').show();
            $('.empty_positions').hide();
            $('.holdings_body').hide();
            $('.holdings_header').hide();
            $('#app_holdings .holdings_body').hide();
            $('#app_holdings .holdings_header').hide();
            $('#app_positions .holdings_body').hide();

            $('#holdings_option').text('Holdings');
            $('#holdings_heading_title').text('Holdings');
        }
    }).fail(function(){
        $('.holding_details_row').each(function(){
                      $(this).remove();
                });
        $('profit_and_loss .profit').html('N/A');
        $('profit_and_loss .profit').attr('style','color: #bfc7d1 !important;font-weight: 400 !important;');
        $('.current_value .header_content').html('<p>&#8377;&nbsp;0</p><p>Current value</p>');
        $('.total_investment .header_content').html('<p>&#8377;&nbsp;0</p><p>Total investment</p>');
        $('.empty_holdings').show();
        $('.empty_positions').hide();
        $('.holdings_body').hide();
        $('.holdings_header').hide();
        $('#app_holdings .holdings_body').hide();
        $('#app_holdings .holdings_header').hide();
        $('#app_positions .holdings_body').hide();
    }).complete(function(){
        show_holdings();
        attach_user_actions();
        $('#update_top_performance1').hide();
        fetch_positions_dummy();
        // $('#holdings_option').text('Holdings');
        // $('#holdings_heading_title').text('Holdings');
    });
}
