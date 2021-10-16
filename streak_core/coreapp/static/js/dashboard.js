var action_buttons=false;
$(document).ready( function() {
    // $('.force_stop').hover(function(){
    //     if($(this).find("img").attr("src") == "/static/imgs/icon-force-stop.png"){
    //         $(this).find("img").attr('src','/static/imgs/icon-force-stop-white.png');
    //     }
    //     else{
    //         $(this).find("img").attr('src','/static/imgs/icon-force-stop.png');
    //     }
    // });
    // $('.deploy').hover(function(){
    //     if($(this).find("img").attr("src") == "/static/imgs/icon-dashboard-deploy.png"){
    //         $(this).find("img").attr('src','/static/imgs/icon-dashboard-deploy-white.png');
    //     }
    //     else{
    //         $(this).find("img").attr('src','/static/imgs/icon-dashboard-deploy.png');
    //     }
    // });
    // Dashboard action buttons when diasbled
    // icon-dashboard-backtest-disabled
    // icon-dashboard-scan-disabled
    // icon-delete-disabled
    // icon-edit-disabled
    // icon-create-similar-disabled
    // and use class "action_buttons_disabled" for the respective button

    // $(".action_buttons").click(function(e){
    // // alert($(".popup").has(e.target).length);
    // // alert($(".popup").is(e.target));
    //     if(($(".action_buttons").has(e.target).length == 0)&&($(".action_buttons").is(e.target))){
    //       $(".action_buttons").fadeOut();
    //     }
    //     e.stopPropagation();
    // });

    // $(".action_buttons").click(function(e) {
    // //Hide the menus if visible
    //     if(e.target.outerHTML.indexOf('menu_dots')==-1)
    //         $(".action_buttons").fadeOut();
    // });
    var popElement = document.getElementsByClassName("action_buttons");
    document.addEventListener('click', function(event) {
        if (action_buttons){
            $(".action_buttons").slideUp();
            action_buttons = false;
            $('.menu_dots>p>img').hide();
        }
    });

    $('.dashboard_algo_section').click(function(e){
        console.log('here');
        eq_section = $(e.currentTarget).siblings('.dashboard_equities_section');
        eq_section.slideToggle();
        if($(e.currentTarget).find('.menu_backtests img').attr('src')=="/static/imgs/new/dropdown.svg"){
            $(e.currentTarget).find('.menu_backtests img').attr('src',"/static/imgs/new/dropup.svg");
        }
        else{
            $(e.currentTarget).find('.menu_backtests img').attr('src',"/static/imgs/new/dropdown.svg");
        }
    });

    $("#ip_live_period").change(function(){
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
    });
    $(".menu_dots>p>img").click(function(e){
        // alert($(this).parents(".menu_dots").find(".action_buttons").className);
        $('.menu_dots>p>img').hide();
        $(this).show();
        $(".action_buttons").slideUp();
        $(this).parents(".action_section").find('.action_buttons').slideDown();
        action_buttons = true;
        e.stopPropagation();
    });

    $( "#algos_search_input" ).autocomplete({
      source: function(request,response){
        // params = {'query':request['term'].toLowerCase()}
        var params = {
                "limit": 10,
                "user_uuid": uid,
                "search": request['term'].toLowerCase(),
                "search_fields": ["algo_name", "action_str", "symbols"],
                "return_fields": ["algo_name", "algo_uuid"]
                }

        var settings = {
          "async": true,
          "crossDomain": true,
          "url": 'https://s.streak.tech/algorithms/basic_search',
          "method": "POST",
          "headers": {
            "Content-Type": "application/json"
          },
          "data":JSON.stringify(params),
          "timeout": 10000,//40 sec timeout
        };

        $.ajax(settings).done(function(data) {
            // alert(data);
            if(data['data']!=undefined){

                response($.map(data['data'], function (el) {
                     return {
                         label: el['algo_name'],
                         value: el['algo_name'],
                         u_id: el['algo_uuid'],  //assumption, symbols and segment name does not have space in between
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
            $("#algos_search_input").val('');
            $("#algos_search_input").focus();
            }
       $("#algos_search_input").val('');
       $("#algos_search_input").focus();
       // ui.item.value = "";
        },
       select:function(event, ui){
        // console.log('selected');
        // console.log(ui['item'])
        //     val = ui.item.value.split(' ');
        //     if(val.length>2){
        //         // var temp = val[1];
        //         val[0]=val[0]+' '+val[1];
        //         val[1]=val[2];
        //     }
        //     if(Object.keys(equity_added).length>=20)
        //      {
        //          show_snackbar(null,'Cannot add more than 20 instruments');
        //          return false;
        //      }
        // if(val[val.length-1]!='NSE' && val[val.length-1]!='NFO-FUT' && val[val.length-1]!='INDICES' && val[val.length-1]!='CDS-FUT' && val[val.length-1]!='MCX'){
        //        var basket_name = ui.item.value.split(' ').slice(0,val.length-1).join(' ');
        //        load_basket(basket_name);
        //        $("#algos_search_input").val('');
        //        $("#algos_search_input").focus();
        //        return false;
        //        }
        //     if(equity_added[val[0]]==null)
        //     {
        //         $('.added_equities').append('<span><span data-syms="'+val[0]+'_'+val[1]+'">'+ui.item.value+'</span><span><img src="/static/imgs/icon-strategy-remove_equity.png"></span></span>');
        //      // symbols.push(ui.item.value.split(' ').reverse());
        //      // ui.item.value = "";
        //      $(".added_equities img").click(function(){

        //      x = $($($(this).parentsUntil('.added_equities')).find('span')[0]).data('syms');
        //      if(x!=null){
        //          [sym,seg] = x.split('_');
        //          delete equity_added[sym];
        //      }
        //      $(this).parentsUntil('.added_equities').remove();

        //      if(Object.keys(equity_added).length==0){
        //          $($('.adding_equities_section div span')[0]).css("background-color", "#ADADAD");
        //          $($('.adding_equities_section div span')[0]).css("border-color", "#F3F3F3");
        //      }
        //  });
            
        //  equity_added[val[0]]=val[1];
        //  $($('.adding_equities_section div span')[0]).css("background-color", "#06D092");
        //  $($('.adding_equities_section div span')[0]).css("border-color", "#B1FDE6");
        //     }
        window.location.href='/backtests/?algo_uuid='+ui.item.u_id;
        $("#algos_search_input").val('');
        $("#algos_search_input").focus();
        return false
       }
    });
    
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
            else if($('#ip_live_period').val()== 'Paper trading'){
              $("#mis_disclaimer_deploy").html("The algo will perform paper trades when the signals are generated, algo is live for 30 days.");
              $('#trading_terms_checkbox').removeAttr("disabled");
            }
            else{
                $("#mis_disclaimer_deploy").html("Note: All SL-M orders for CNC strategies are valid only for today till 3:15 PM and will not be placed on the consecutive day.");
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


    // $(".dashboard_algo_section > div.action_section > div > div > p").click(function(e){
    //   // alert($(this).parents(".menu_dots").find(".action_buttons").className);
    //   $(".action_buttons").slideUp();
    //   $(".row_action_desc>p>img").hide();
    //   $(this).parents(".row_action_desc").find('p>img').show();
    //   $(this).parents(".row_action_desc").find('.action_buttons').slideDown();
    //   action_buttons = true;
    //   e.stopPropagation();
    // });
    $('.menu_dots>p>img').hide();
    $(".dashboard_algo_section").hover(function(){
      $(this).find("div.action_section > div > div > p > img").show();
    });

    $(".dashboard_algo_section").mouseleave(function(){
      if(action_buttons && $(this).find('.action_buttons').is(":visible"))
        $(this).find("div.action_section > div > div > p > img").show();
      else
        $(this).find("div.action_section > div > div > p > img").hide();
    });

});
$(window).load(function() {
    // Animate loader off screen
    $(".loader_parent").fadeOut();
});
function close_orders_popup () {
    $(".close_popup").parents(".body").find(".force_stop_popup").fadeOut();
    $("body").removeClass("body_scroll");
}
function close_order_details_popup () {
    $(".close_popup").parents(".body").find(".order_details_popup").fadeOut();
    $("body").removeClass("body_scroll");
}
function close_order_log_popup () {
    $(".close_popup").parents(".body").find(".order_log_popup").fadeOut();
    $("body").removeClass("body_scroll");
} 
function close_delete_strategy_popup () {
    $(".close_popup").parents(".body").find(".delete_strategy_popup").fadeOut();
    $("body").removeClass("body_scroll");
}
function show_hidden(event){
    div = event.target.parentElement.parentElement;
    t = event.target.parentElement;
    $(t).css('position','inherit');
    $(t).html('<p>Show less&nbsp;&nbsp;&nbsp;<img src="/static/imgs/icon-up-arrow.png"></p>');
    $(t).attr('onclick','hide_overflow()');
    divs = $(div).find('[class^=token__]');
    for(var i=0;i<divs.length;i++){
        $(divs[i]).show();
    }
}
function hide_overflow(){
    $('.dashboard_equities_section').hide();
    // $('.dashboard_equities_section').each(function(){
    //     divs = $(this).find('[class^=token__]');
    //     // if(divs.length>5){
    //         // if($(this).find(".show_more_eq").length>=1)
    //         //     $(this).find(".show_more_eq").remove()
    //         // $(this).append('<div class="show_more_eq" style="background-color: #ebeef0;" onclick="show_hidden(event)"><p>Show more&nbsp;&nbsp;&nbsp;<img src="/static/imgs/icon-dashboard-show-more.png"></p></div>');
    //         // for(var i=5;i<divs.length;i++){
    //             $(divs[i]).hide();
    //         // }
    //     // }
    // });
}
$(document).ready( function() {
    $(".order_log_popup").click(function(e){
    // alert($(".order_log_popup").has(e.target).length);
    // alert($(".order_log_popup").is(e.target));
    if(($(".order_log_popup").has(e.target).length == 0)&&($(".order_log_popup").is(e.target))){
      $("body").removeClass("body_scroll");
      $(".close_popup").parents(".body").find(".order_log_popup").fadeOut();
    }
    });
    $(".delete_strategy_popup").click(function(e){
    // alert($(".delete_strategy_popup").has(e.target).length);
    // alert($(".delete_strategy_popup").is(e.target));
    if(($(".delete_strategy_popup").has(e.target).length == 0)&&($(".delete_strategy_popup").is(e.target))){
      $("body").removeClass("body_scroll");
      $(".close_popup").parents(".body").find(".delete_strategy_popup").fadeOut();
    }
    });
    hide_overflow();
    $(".pause_button").click(function(){
        // alert("In here");
        var value = $(this).text();
        // alert(value);
        if(value == 'Pause'){
            // alert("True"+value);
            $(this).text('Resume');
            $(this).addClass('resume_button');
        }
        else
        {
            // alert("False"+value);
            $(this).text('Pause');
            $(this).removeClass('resume_button');
        }
    });
    // $( document ).ajaxStart(function() {
    //   $( ".loader_parent" ).fadeIn();
    // });
    
    // $( document ).ajaxStop(function() {
    //   $( ".loader_parent" ).fadeOut();
    // });
    // refresh_ltp_subscription();
});
var click_action_uuid = null;
var click_obj = null;

function edit_button(action_uuid){
    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    var action_uuid = action_uuid;
    // sending a post request 
    post('/strategy',{
            'csrfmiddlewaretoken':csrfmiddlewaretoken,
            'action_uuid':action_uuid,
        },"post");
}


function algo_order_details(algo_uuid){
    post('/orders',{
        'algo_uuid':algo_uuid
    },"get");
}
function algo_order_log(algo_uuid){
    alert(algo_uuid);
    // post('/save_backtests',{
    //     'algo_uuid':algo_uuid
    // },"get");
}
function edit_algo(event,algo_uuid){
    // taking user to the algorithm page
    // post('/algorithm',{
    //     'algo_uuid':algo_uuid
    // },"get");
    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    $.get('/is_algorithm_deployed',{'csrfmiddlewaretoken':csrfmiddlewaretoken,
        'algo_uuid':algo_uuid
    }).done(function (data){
        // if algo not deployed
        if(data['status']=='success'){
                try{
                ga('send', {hitType: 'event', eventCategory: 'Edit algo', eventAction: 'Edit algo initiated', eventLabel: 'Algos page'});
                }catch(e){
                  
                }
                window.location='/strategy?algo_uuid='+data['algo_uuid']
            }
        // alert('Algo delete_button')

            // if some error 
            // alert('Some specific error, like a script is live, etc')
        }).fail(
            function(){
                alert('Some specific error, like a script is live, etc');
            });
      event.stopPropagation();
}
function algo_clone(event,algo_uuid){
    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    $.post('/create_similar_strategy/',{
        'csrfmiddlewaretoken':csrfmiddlewaretoken,
        'algo_uuid':algo_uuid
        }).done(function (data){
            // if algo deleted
            if(data['status']=='success'){
              try{
                ga('send', {hitType: 'event', eventCategory: 'Create Similar algo', eventAction: 'Create Similar algo initiated', eventLabel: 'Algos page'});
              }
              catch(e){
              }
                window.location='/create_similar_strategy?algo_uuid='+algo_uuid+'&cloned=1'
            }
            // alert('Algo delete_button')

            // if some error 
            // alert('Some specific error, like a script is live, etc')
        }).fail(
            function(){
                alert('Some specific error, like a script is live, etc');
            });

    event.stopPropagation();
}
function algo_backtests(ev,algo_uuid){
    $(ev.target).html("<img src='/static/imgs/button-loading-rect.gif' id='button_loading'>");
    $(ev.target).css({'cursor': 'no-drop'});
    $(ev.target).removeAttr('onclick');
    try{
      ga('send', {hitType: 'event', eventCategory: 'Backtest Results', eventAction: 'Backtest Results', eventLabel: 'Algos page'});
    }
    catch(e){
    }

    post('/backtests',{
        'algo_uuid':algo_uuid
    },"get");
    event.stopPropagation();
}
function power_scan(algo_uuid){
    post('/power_scan',{
        'algo_uuid':algo_uuid
    },"get");
}
function algo_delete(event,algo_uuid){
    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    $('.algo_deleted').html("<img src='/static/imgs/button-loading-rect.gif' id='button_loading'>");
    $('.algo_deleted').css({'cursor': 'no-drop'});
    $('.algo_deleted').removeAttr('onclick');
    // show pop up for confirmation
    $.post('/algorithm_remove/',{
        'csrfmiddlewaretoken':csrfmiddlewaretoken,
        'algo_uuid':algo_uuid
        }).done(function (data){
            // if algo deleted
            if(data['status']='success')
            {   
                // $(event.target.parentElement.parentElement.parentElement.parentNode).remove();
                $('#'+algo_uuid).remove();
                // alert('Algo delete_button')
                $('.delete_strategy').hide();
                $('.algo_deleted').show();
                $('#confirm_delete_strategy').attr('onclick','');
                blank_dashboard = '<div class="empty_dashboard_body" style=""><img src="/static/imgs/empty-dashboard.png"><p>No Strategies.<br><a href="/strategy">Create a new strategy</a></p></div>';
                if($('.dashboard_row').length<1)
                    $('.dashboard_body').html(blank_dashboard);
                ga('send', {hitType: 'event', eventCategory: 'Delete algo', eventAction: 'Delete algo confirmed', eventLabel: 'Algos page'});
                setTimeout(function(){ close_delete_strategy_popup();}, 3200);
            }
            else// if some error 
            // alert('Some specific error, like a script is live, etc')
            {   
                $('.delete_strategy_popup').hide();
                show_snackbar(null,'Some error occured, please try again!');
            }
            $('.algo_deleted').html('<img src="/static/imgs/new/algo_deleted.gif"><p class="stop_heading">Algo deleted</p><p class="stop_sub_heading">This algo along with backtest results has been deleted</p>');
        }).fail(
            function(){
                // alert('Some specific error, like a script is live, etc');
                $('.delete_strategy_popup').hide();
                show_snackbar(null,'Some error occured, please try again!');
                $('.algo_deleted').html('<img src="/static/imgs/new/algo_deleted.gif"><p class="stop_heading">Algo Deleted</p><p class="stop_sub_heading">This algo along with backtest results has been deleted</p>');
        });
    $('body').removeClass('body_scroll'); 
    event.stopPropagation();
}

function select_all(e, t) {
    var c = 0;
    if (t.is(':checked')) {
      // $(e).find('input').attr('disabled', true);
      // $($(t[0].parentElement.parentElement).find('div[class^="token__"]')[0]).find('.deploy_checkbox input')[0].checked = true
      $(t[0].parentElement.parentElement.parentElement.parentElement).find('div[class^="token__"]').each(function(i,obj){
        if($(obj).find('.deploy_checkbox input')[0] && !$(obj).find('.deploy_checkbox input')[0].disabled)
            {
                $(obj).find('.deploy_checkbox input')[0].checked = true
                c += 1;
            }
      });
      if(c>0)
        t.parent().parent().siblings('.deploy_appear').find('.deploy').removeClass('deploy_disabled');
        // t.prev().removeClass('deploy_disabled');
        // if(t.parent().parent().siblings('.deploy_appear').find('.deploy_holder').is(':hidden')){
        //     t.parent().parent().siblings('.deploy_appear').find('.deploy_holder').slideDown();
        // }
    } else {
      // $(e).find('input').removeAttr('disabled');
      $(t[0].parentElement.parentElement.parentElement.parentElement).find('div[class^="token__"]').each(function(i,obj){
        if($(obj).find('.deploy_checkbox input')[0] && !$(obj).find('.deploy_checkbox input')[0].disabled)
            $(obj).find('.deploy_checkbox input')[0].checked = false
      });
        t.parent().parent().siblings('.deploy_appear').find('.deploy').addClass('deploy_disabled');
      // if(!t.parent().parent().siblings('.deploy_appear').find('.deploy_holder').is(':hidden')){
      //       t.parent().parent().siblings('.deploy_appear').find('.deploy_holder').slideUp();
      // }
      // t.prev().addClass('deploy_disabled');
    }
}

function selected_any(e, t) {
    // $(t[0].parentElement.parentElement.parentElement).find('.deploy_all_checkbox')[0].checked

    // $(t[0].parentElement.parentElement.parentElement).find('.deploy_checkbox input');

    var deploy_instrument_list = [];
    var c = 0;
    $(t[0].parentElement.parentElement.parentElement).find('.deploy_checkbox input').each(function(i,obj){
        c += 1;
        if(obj.checked)
        {
            if($(obj).data("deploy-params_segment")=='MCX' && subscription_status.subscription_plan!=undefined &&subscription_status.subscription_plan!='ultimate'){
              show_snackbar(null,'MCX is only available in ultimate plan'); 
              obj.checked = false;
              c -= 1;
              return;
            }
            deploy_instrument_list.push([$(obj).data("deploy-params_segment"),$(obj).data("deploy-params_symbol")]);
        }
    });

    if(deploy_instrument_list.length>0){
        $(t[0].parentElement.parentElement.parentElement).find('.deploy').removeClass('deploy_disabled');
        if($(t[0].parentElement.parentElement.parentElement).find('.deploy_holder').is(':hidden')){
        $(t[0].parentElement.parentElement.parentElement).find('.deploy_holder').slideDown();
        }
    }
    else{

        $(t[0].parentElement.parentElement.parentElement).find('.deploy').addClass('deploy_disabled');
        $(t[0].parentElement.parentElement.parentElement).find('.deploy_all_checkbox')[0].checked = false;
        // $(t[0].parentElement.parentElement.parentElement).find('.deploy_holder').slideUp();
        if(!$(t[0].parentElement.parentElement.parentElement).find('.deploy_holder').is(':hidden')){
        // $(t[0].parentElement.parentElement.parentElement).find('.deploy_holder').slideUp();
        }
    }
    if(c>0 && c==deploy_instrument_list.length){
        $(t[0].parentElement.parentElement.parentElement).find('.deploy_all_checkbox')[0].checked = true;   
    }
    else{
        $(t[0].parentElement.parentElement.parentElement).find('.deploy_all_checkbox')[0].checked = false;
    }

}

function deploy_algorithm_multi_popup(event,t,algo_name,entry,exit,position_type,quantity,take_profit,stop_loss,interval,algo_uuid,chart_type,trading_start_time,trading_stop_time){

    var deploy_instrument_list = [];

    // $($($(th[0].parentElement.parentElement).find('div[class^="token__"]')[0]).find('.deploy_checkbox input')[0]).data("deploy-params_symbol");
    $(t[0].parentElement.parentElement.parentElement.parentElement).find('div[class^="token__"]').each(function(i,obj){
        if($(obj).find('.deploy_checkbox input')[0])
        {
            var r = $(obj).find('.deploy_checkbox input')[0];
            if(r.checked){
                deploy_instrument_list.push([$(r).data("deploy-params_segment"),$(r).data("deploy-params_symbol")]);
            }
        }
      });

    for(var k=0; k<deploy_instrument_list.length;k++){
      if(deploy_instrument_list[k][0]=='MCX' && subscription_status.subscription_plan!=undefined &&subscription_status.subscription_plan!='ultimate'){
        show_snackbar(null,'MCX is only available in ultimate plan');
        // obj.checked = false;
        return;
      }
    }
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
    if(deploy_instrument_list.length==0){
        return
    }
    $.ajax(settings).done(function (msg){
    if(msg.status=='success')
      {
        backtest_remaining = Math.max(msg['backtest'],0);
        deployments_remaining = Math.max(msg['deployments_remaining'],0)
        if(deployments_remaining<deploy_instrument_list.length){
            show_snackbar(null,'You are trying to deploy more than the remaining deployments');
            return;
        }
        $('body').addClass('body_scroll');
        $('.deploy_summary_heading p').html(algo_name);
        // $('#trading_terms_checkbox:checked').removeAttr('checked');
        if (position_type == 1){
            var position_type_entry = 'BUY'
            var position_type_exit = 'SELL'
        }
        else{
            var position_type_entry = 'SELL'
            var position_type_exit = 'BUY'
        }
        if(chart_type.includes('enko')){
          if(['ultimate'].indexOf(subscription_status.subscription_plan) < 0
            ){
              show_snackbar(null,'Upgrade to ultimate plan, to use Renko Chart');
              return false;
          }
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

        if(deploy_instrument_list.length==1){
            $('#entry_condition_summary').html(position_type_entry+' '+quantity+' shares of '+deploy_instrument_list[0][1]+' when '+entry+' at '+c_interval_str+'Enter trade between '+trading_start_time+' to '+trading_stop_time);
            if(exit!='')
                $('#exit_condition_summary').html(position_type_exit+' '+quantity+' shares when '+exit+' or '+' at Stop loss of '+stop_loss+'% or Take profit of '+take_profit+'%'+' at '+c_interval_str);
            else{
                $('#exit_condition_summary').html(position_type_exit+' '+quantity+' shares of '+deploy_instrument_list[0][1]+' at Stop loss of '+stop_loss+'% or Take profit of '+take_profit+'%'+' at '+c_interval_str);
            }
            $('.deploy_heading p').text("Deploy");
        }
        else{
            $('#entry_condition_summary').html(position_type_entry+' '+quantity+' shares'+' when '+entry+' at '+c_interval_str+'Enter trade between '+trading_start_time+' to '+trading_stop_time);
            if(exit!='')
                $('#exit_condition_summary').html(position_type_exit+' '+quantity+' shares when '+exit+' or '+' at Stop loss of '+stop_loss+'% or Take profit of '+take_profit+'%'+' at '+c_interval_str);
            else{
                $('#exit_condition_summary').html(position_type_exit+' '+quantity+' shares at Stop loss of '+stop_loss+'% or Take profit of '+take_profit+'%'+' at '+c_interval_str);
            }
            $('.deploy_heading p').text("Deploy Multiple Scrips");
        }

        // $('.popup').show();
        if ($('#trading_terms_checkbox:checked').is(':checked') && (first_time_deploy == "false")){
            $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
            $('.deploy_confirm').attr('onclick','deploy_algorithm_multi("'+algo_uuid+'",\''+JSON.stringify(deploy_instrument_list)+'\',"'+position_type+'","'+quantity+'","'+take_profit+'","'+stop_loss+'","'+interval+'");');
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
                        $('.deploy_confirm').attr('onclick','deploy_algorithm_multi("'+algo_uuid+'",\''+JSON.stringify(deploy_instrument_list)+'\',"'+position_type+'","'+quantity+'","'+take_profit+'","'+stop_loss+'","'+interval+'");');
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
                $('.deploy_confirm').attr('onclick','deploy_algorithm_multi("'+algo_uuid+'",\''+JSON.stringify(deploy_instrument_list)+'\',"'+position_type+'","'+quantity+'","'+take_profit+'","'+stop_loss+'","'+interval+'");');
            }else{
                $('.deploy_confirm').css({'background-color':'#8b9096 !important','cursor': 'no-drop'});
                $('.deploy_confirm').removeAttr('onclick');
            }

        });

      }
    }).fail(function(){
      show_snackbar(null,'Unable to fetch usage,kindly check your network')
    });

    // $('body').addClass('body_scroll');
    // $('.deploy_summary_heading p').html(algo_name);
    // // $('#trading_terms_checkbox:checked').removeAttr('checked');
    // if (position_type == 1){
    //     var position_type_entry = 'BUY'
    //     var position_type_exit = 'SELL'
    // }
    // else{
    //     var position_type_entry = 'SELL'
    //     var position_type_exit = 'BUY'
    // }

    // if(deploy_instrument_list<0){
    //     return
    // }
    // if(deploy_instrument_list==1){
    //     $('#entry_condition_summary').html(position_type_entry+' '+quantity+' shares of '+sym+' when '+entry+'.');
    //     if(exit!='')
    //         $('#exit_condition_summary').html(position_type_exit+' '+quantity+' shares when '+exit+' or '+' at Stop loss of '+stop_loss+'% or Take profit of '+take_profit+'%.');
    //     else{
    //         $('#exit_condition_summary').html(position_type_exit+' '+quantity+' shares of '+sym+' at Stop loss of '+stop_loss+'% or Take profit of '+take_profit+'%.');
    //     }
    //     $('#deploy_heading p').text("Deploy");
    // }
    // else{
    //     $('#entry_condition_summary').html(position_type_entry+' '+quantity+' shares'+' when '+entry+'.');
    //     if(exit!='')
    //         $('#exit_condition_summary').html(position_type_exit+' '+quantity+' shares when '+exit+' or '+' at Stop loss of '+stop_loss+'% or Take profit of '+take_profit+'%.');
    //     else{
    //         $('#exit_condition_summary').html(position_type_exit+' '+quantity+' shares at Stop loss of '+stop_loss+'% or Take profit of '+take_profit+'%.');
    //     }
    //     $('#deploy_heading p').text("Deploy Multiple Scrips");
    // }

    // switch(interval){
    //     case 'min':$('#interval_condition_summary').html('1 Minute');break;
    //     case '3min':$('#interval_condition_summary').html('3 Minute');break;
    //     case '5min':$('#interval_condition_summary').html('5 Minute');break;
    //     case '10min':$('#interval_condition_summary').html('10 Minute');break;
    //     case '15min':$('#interval_condition_summary').html('15 Minute');break;
    //     case '30min':$('#interval_condition_summary').html('30 Minute');break;
    //     case 'hour':$('#interval_condition_summary').html('1 Hour');break;
    //     case 'day':$('#interval_condition_summary').html('1 Day');break;
    // }
    // // $('.popup').show();
    // if ($('#trading_terms_checkbox:checked').is(':checked') && (first_time_deploy == "false")){
    //     $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
    //     $('.deploy_confirm').attr('onclick','deploy_algorithm_multi("'+algo_uuid+'",\''+JSON.stringify(deploy_instrument_list)+'\',"'+position_type+'","'+quantity+'","'+take_profit+'","'+stop_loss+'","'+interval+'");');
    //     // algo_name,entry,exit,position_type,quantity,take_profit,stop_loss,interval,algo_uuid,sym,seg
    // }
    // else{
    //     $('.deploy_confirm').css({'background-color':'#8b9096 !important','cursor': 'no-drop'});
    //     $('.deploy_confirm').unbind('click');
    //     $('#trading_terms_checkbox:checked').removeAttr('checked');
    // }
    // // $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
    // // $('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'");');
    // $.get('/get_subscription_limit',{
    //     }).done(function (data){
    //     if(data['status']=="success")
    //     {
    //         if(data['valid']==true){
    //             if(Math.max(data['deployments_remaining'],0)<1){
    //                 show_snackbar(null,'Deployments limits reached');
    //                 $( ".loader_parent" ).fadeOut();
    //                 $(".deploy_confirm").html('<span><img src="/static/imgs/icon-deploy-confirm.png"></span>&nbsp;&nbsp;Confirm');
    //                 $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
    //                 $('.deploy_confirm').attr('onclick','deploy_algorithm_multi("'+algo_uuid+'",\''+JSON.stringify(deploy_instrument_list)+'\',"'+position_type+'","'+quantity+'","'+take_profit+'","'+stop_loss+'","'+interval+'");');
    //                 $('#trading_terms_checkbox:checked').removeAttr('checked');
    //                 close_popup();
    //                 return;
    //             }else{
    //                 $('.popup').show();
                    
    //                 try{
    //                     ga('send', {hitType: 'event', eventCategory: 'Deployment', eventAction: 'Deploy initiated', eventLabel: 'Algos page'});
    //                 }catch(e){
              
    //                 }
    //             }
    //         }
    //     }
    // });
    // $('#trading_terms_checkbox').change(function(){
    //     if($('#trading_terms_checkbox:checked').is(':checked')){
    //         $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
    //         $('.deploy_confirm').attr('onclick','deploy_algorithm_multi("'+algo_uuid+'",\''+JSON.stringify(deploy_instrument_list)+'\',"'+position_type+'","'+quantity+'","'+take_profit+'","'+stop_loss+'","'+interval+'");');
    //     }else{
    //         $('.deploy_confirm').css({'background-color':'#8b9096 !important','cursor': 'no-drop'});
    //         $('.deploy_confirm').removeAttr('onclick');
    //     }

    // });
}

function deploy_algorithm_multi(algo_uuid,seg_sym_list,position_type,quantity,take_profit,stop_loss,interval){
    params = {
        'algo_uuid':algo_uuid,
        'seg_sym_list':seg_sym_list
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
    params['variety']=variety;
    if (live_period!=1)
      params['variety']='REGULAR';
    // params['seg_sym']=seg+'_'+sym;
    params['csrfmiddlewaretoken']=csrfmiddlewaretoken;
    $( ".loader_parent" ).fadeIn();
    $(".deploy_confirm").html("<img src='/static/imgs/button-loading-rect.gif' id='button_loading'>");
    $.post('/deploy_algorithm_multi/',params,function(data){
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
            $('.deploy_confirm').attr('onclick','deploy_algorithm_multi("'+algo_uuid+'",\''+JSON.stringify(seg_sym_list)+'\',"'+position_type+'","'+quantity+'","'+take_profit+'","'+stop_loss+'","'+interval+'");');
            $('#trading_terms_checkbox:checked').removeAttr('checked');
            close_popup();
            show_snackbar(null,'Some error occured, please try again!');       
        }
    }).fail(function(){
        $( ".loader_parent" ).fadeOut();
        $(".deploy_confirm").html('<span><img src="/static/imgs/icon-deploy-confirm.png"></span>&nbsp;&nbsp;Confirm');
        $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
        $('.deploy_confirm').attr('onclick','deploy_algorithm_multi("'+algo_uuid+'",\''+JSON.stringify(seg_sym_list)+'\',"'+position_type+'","'+quantity+'","'+take_profit+'","'+stop_loss+'","'+interval+'");');
        $('#trading_terms_checkbox:checked').removeAttr('checked');
        close_popup();
        show_snackbar(null,'Some error occured, please try again!');
    });
    $('body').removeClass('body_scroll');
};

function deploy_algorithm_popup(algo_name,entry,exit,position_type,quantity,take_profit,stop_loss,interval,algo_uuid,sym,seg){
    $('body').addClass('body_scroll');
    $('.deploy_summary_heading p').html(algo_name);
    // $('#trading_terms_checkbox:checked').removeAttr('checked');
    if (position_type == 1){
        var position_type_entry = 'BUY'
        var position_type_exit = 'SELL'
    }
    else{
        var position_type_entry = 'SELL'
        var position_type_exit = 'BUY'
    }

    $('#entry_condition_summary').html(position_type_entry+' '+quantity+' shares of '+sym+' when '+entry+'');
    if(exit!='')
        $('#exit_condition_summary').html(position_type_exit+' '+quantity+' shares when '+exit+' or '+' at Stop loss of '+stop_loss+'% or Take profit of '+take_profit+'%');
    else{
        $('#exit_condition_summary').html(position_type_exit+' '+quantity+' shares of '+sym+' at Stop loss of '+stop_loss+'% or Take profit of '+take_profit+'%');
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
    // $('.popup').show();
    if ($('#trading_terms_checkbox:checked').is(':checked') && (first_time_deploy == "false")){
        $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
        $('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'","'+position_type+'","'+quantity+'","'+take_profit+'","'+stop_loss+'","'+interval+'");');
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
                    $(".deploy_confirm").html('<span><img src="/static/imgs/icon-deploy-confirm.png"></span>&nbsp;&nbsp;Confirm');
                    $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
                    $('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'","'+position_type+'","'+quantity+'","'+take_profit+'","'+stop_loss+'","'+interval+'");');
                    $('#trading_terms_checkbox:checked').removeAttr('checked');
                    close_popup();
                    return;
                }else{
                    $('.popup').show();
                    
                    // try{
                    //     ga('send', {hitType: 'event', eventCategory: 'Deployment', eventAction: 'Deploy initiated', eventLabel: 'Algos page'});
                    // }catch(e){
              
                    // }
                }
            }
        }
    });
    $('#trading_terms_checkbox').change(function(){
        if($('#trading_terms_checkbox:checked').is(':checked')){
            $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
            $('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'","'+position_type+'","'+quantity+'","'+take_profit+'","'+stop_loss+'","'+interval+'");');
        }else{
            $('.deploy_confirm').css({'background-color':'#8b9096 !important','cursor': 'no-drop'});
            $('.deploy_confirm').removeAttr('onclick');
        }

    });
}
function deploy_algorithm(algo_uuid,sym,seg,position_type,quantity,take_profit,stop_loss,interval){
    params = {
        'algo_uuid':algo_uuid,
        'sym':sym,
        'seg':seg
    };

    // take_profit = $('#ip_takeprofit').val();
    // stop_loss = $('#ip_stoploss').val();
    // quantity = $('#ip_quantity').val();
    // interval = $('#ip_interval').val();

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
    $( ".loader_parent" ).fadeIn();
    $(".deploy_confirm").html("<img src='/static/imgs/button-loading-rect.gif' id='button_loading'>");
    $.post('/deploy_algorithm/',params,function(data){
        // $( ".loader_parent" ).fadeOut();
        if(data['status']=='success'){
            window.location = '/order_log';
            // try{
            //     ga('send', {hitType: 'event', eventCategory: 'Deployment', eventAction: 'Deploy confirmed', eventLabel: 'Algos page'});
            // }catch(e){
              
            // }
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
            $('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'","'+position_type+'","'+quantity+'","'+take_profit+'","'+stop_loss+'","'+interval+'");');
            $('#trading_terms_checkbox:checked').removeAttr('checked');
            close_popup();
            show_snackbar(null,'Some error occured, please try again!');       
        }
    }).fail(function(){
        $( ".loader_parent" ).fadeOut();
        $(".deploy_confirm").html('<span><img src="/static/imgs/icon-deploy-confirm.png"></span>&nbsp;&nbsp;Confirm');
        $('.deploy_confirm').css({'background-color':'#0088ff !important','cursor': 'pointer'});
        $('.deploy_confirm').attr('onclick','deploy_algorithm("'+algo_uuid+'","'+sym+'","'+seg+'","'+position_type+'","'+quantity+'","'+take_profit+'","'+stop_loss+'","'+interval+'");');
        $('#trading_terms_checkbox:checked').removeAttr('checked');
        close_popup();
        show_snackbar(null,'Some error occured, please try again!');
    });
    $('body').removeClass('body_scroll');
};

function test_button(action_uuid){
    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    var action_uuid = action_uuid;

    $.post('/update_session',{'action_uuid':action_uuid,'csrfmiddlewaretoken':csrfmiddlewaretoken}, function(data) {
        // alert(data);
        }).done(function(){
            // sending a post request 
            post('/test',{
                    // 'csrfmiddlewaretoken':csrfmiddlewaretoken,
                    // 'action_uuid':action_uuid,
                },"get");
        });
}

function delete_button(event,algo_uuid){
    $('.algo_deleted').hide();$('.delete_strategy_popup').show();$('.delete_strategy').show();$('body').addClass('body_scroll')
    $('#confirm_delete_strategy').attr('onclick','algo_delete(event,\''+algo_uuid+'\')');
    try{
      ga('send', {hitType: 'event', eventCategory: 'Delete algo', eventAction: 'Delete algo initiated', eventLabel: 'Algos page'});
    }catch(e){
      
    }

    // var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    // var action_uuid = action_uuid;

    // // sending a post request 
    // params = {
    //         'csrfmiddlewaretoken':csrfmiddlewaretoken,
    //         'action_uuid':action_uuid,
    //     };

    // var request = $.ajax({
    //   url: "/remove_action",
    //   type: "POST",
    //   data: params,
    //   dataType: "html"
    // });

    // request.done(function(msg) {
    //     var msg = JSON.parse(msg);
    //     if (msg['status']==true){
    //         location.reload();
    //     }
    // });

    // request.fail(function(jqXHR, textStatus) {
    //   console.log( "Request failed: " + textStatus );
    // });
    event.stopPropagation();
}



// function show_order_details(order_id){
//     var params = {
//         'order_id':order_id
//     };
//     var settings = {
//       "async": true,
//       "crossDomain": true,
//       "url": '/show_order_details/',
//       "method": "GET",
//       "headers": {
//       },
//       "data":params,
//       "timeout": 10000,//40 sec timeout
//     }
//     $.ajax(settings).done(function (msg){
//         // console.log(msg);
//         if (msg.status=="success"){
//             $('.order_details_popup').show();$('body').addClass('body_scroll');
//             order = JSON.parse(msg.order);
//             order_status = order.order_status;
//             order_details_header = '<div class="order_name"> <p>'+order_status.tradingsymbol+'<span>'+order_status.exchange+'</span></p> <p>'+order_status.transaction_type+' '+order_status.quantity+' shares at '+order_status.order_type+'</p> </div> <div class="order_avg_price"> <p>Avg. Price</p> <p>'+order_status.average_price+'</p> </div> <div class="order_filled_qty"> <p>Filled Quantity</p> <p>'+order_status.filled_quantity+' of '+order_status.quantity+'</p> </div>';
//             $('.order_details_header').html(order_details_header);

//             order_details_body = '<div class="order_details_row"> <div> <p>Price</p> <p>'+order_status.price+'</p> </div> <div> <p>Trigger Price</p> <p>'+order_status.trigger_price+'</p> </div> <div> <p>Order placed by</p> <p>'+order_status.user_id+'</p> </div> </div> <div class="order_details_row"> <div> <p>Order Type</p> <p>'+order_status.order_type+'</p> </div> <div> <p>Product Validity</p> <p>'+order_status.product+'/'+order_status.validity+'</p> </div> <div> <p>Time</p> <p>'+order_status.order_timestamp+'</p> </div> </div> <div class="order_details_row"> <div> <p>Order ID</p> <p>'+order_status.order_id+'</p> </div> <div> <p>Exchange order ID</p> <p>'+order_status.exchange_order_id+'</p> </div> <div> <p>Exchange Time</p> <p>'+order_status.exchange_timestamp+'</p> </div> </div> <div class="order_details_row"> <div class="status"> <p>Status</p> <p>'+order_status.status+'</p> </div> <div id="status_message"> <p>STATUS MESSAGE</p> <p>'+order_status.status_message+'</p> </div> </div>'
//             $('.order_details_body').html(order_details_body);
//         }
//         else{
//             show_snackbar(null,'Error fetching order details');
//             }
//     }).fail(function(){
//         show_snackbar(null,'Error fetching order details');
//     });
// }

function deploy_onclick(action_uuid,obj){
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
                                swal("Success","Algo deployed","success");
                                window.location='/orders'
                                // location.reload();
                                // $(obj.parentElement).toggleClass('pause_button');
                                $(obj.parentElement).html("<button type=\"submit\" class=\"pause_button\" onclick=\"pause_button('"+action_uuid+"',this);\">Pause</button>");
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
            swal("Could not connect to broker, please try to deploy again");
        }
    
    click_action_uuid = null;
    click_obj = null;
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

function pause_button(action_uuid,obj){
    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    var action_uuid = action_uuid;

    // sending a post request 
    params = {
            'csrfmiddlewaretoken':csrfmiddlewaretoken,
            'action_uuid':action_uuid,
        };

    var request = $.ajax({
      url: "/pause_action",
      type: "POST",
      data: params,
      dataType: "html"
    });

    request.done(function(msg) {
        var msg = JSON.parse(msg);
        if (msg['status']==true){
            swal("Success","Algo paused","success");
            // location.reload();
            $(obj.parentElement).html("<button type=\"submit\" class=\"deploy_button\" onclick=\"deploy_button('"+action_uuid+"',this);\">Deploy</button>");
        }
    });

    request.fail(function(jqXHR, textStatus) {
      console.log( "Request failed: " + textStatus );
    });
}
// function pause_button(action_uuid){
    
// }

function create_algorithm(){
  var algo_name = $("#algo_name").val();
  if (algo_name==''){
    swal('Enter a name for your algo');
    return;
  }
  var algo_description = $("#algo_description").val();
  var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();

  post('/strategy',{
            'action_name':algo_name,
            'action_desc':algo_description,
            'csrfmiddlewaretoken':csrfmiddlewaretoken
        },"post");
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
            positions = msg.positions;
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
function force_stop_button(deployment_uuid){
    $('.exit_position, .algo_stopped').hide();$('.force_stop_popup, .stop_options').show();
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
                console.log(msg.status);
                $('.exit_position, .stop_options').hide();$('.algo_stopped').show();
                setTimeout(function(){ window.location = '/dashboard/'; }, 2000);
            }
        else{
            $('.force_stop_popup').hide();
            show_snackbar(null,'Some error occured, please try again!');
        }
        }).fail(function(msg){
            // alert('Some error, please try again');
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
                        exit_window.find('.exit_body').html('<div  id="notif_actions"><button id="buy" class="force_stop_action" onclick="keep_position_open(\''+deployment_uuid+'\');">Confirm</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div>');
                    }
                else{
                        // seg_sym = [];
                        // for(var k in positions) seg_sym.push(k)
                        if(positions.qty==0){
                            exit_window.find('.exit_header').html("<p>No positions to exit</p>");
                            exit_window.find('.exit_body').html('<div  id="notif_actions"><button id="buy" class="force_stop_action" onclick="keep_position_open(\''+deployment_uuid+'\');">Confirm</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div>');
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

                            // x = '<div><div class="radio_options"><div><span id="sell_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MIS</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>CNC</p></div></div>';
                            // else if(product=='CNC')
                            //     x = '<div><div class="radio_options"><div><span id="sell_radio_option"></span><p id="option_selected">CNC</p></div><div><span></span><p>MIS</p></div></div>';

                            // exit_window.find('.exit_body').html('<div class="exit_options">'+x+'<div class="exit_qty"><p>Quantity</p><input type="number" id="position_qty" name="" value="'+positions.qty+'"></div></div><div><div class="radio_options"><div><span id="sell_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MARKET</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div></div><div class="exit_price"><p>Price</p><input type="number" id="position_price" name="" value="0"></div></div></div><div  id="notif_actions"><button id="sell" onclick="exit_position_now_force_stop(\''+deployment_uuid+'\',\''+seg+'\',\''+sym+'\','+positions.qty+',\'MARKET\',\'SELL\',\''+product+'\',\'DAY\',\''+msg.algo_uuid+'\',\''+msg.algo_name+'\');">Sell</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div>');

                            exit_window.find('.exit_body').html('<div class="exit_options">'+x+'<div class="notif_left"><div class="exit_qty"><p>Qty.</p><input type="number" id="position_qty" name="" value="'+Math.abs(positions.qty)+'" readonly></div><div class="exit_qty"><p>Price</p><input type="number" name="" id="position_price" value="'+0+'" readonly></div></div></div><div><div class="radio_options"><div><span id="sell_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MARKET</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL-M</p></div></div><div class="notif_right"><div class="exit_price"><p>Trigger price</p><input type="number" class="bg-stripe" id="position_trigger_price" name="" value="0" readonly></div><div class="exit_price"><p>Disclosed qty.</p><input type="number" class="bg-stripe" id="position_disclosed_qty" name="" value="0" readonly></div></div></div></div><div id="notif_actions"><button id="sell" onclick="exit_position_now_force_stop(\''+deployment_uuid+'\',\''+seg+'\',\''+sym+'\','+Math.abs(positions.qty)+',\'MARKET\',\'SELL\',\''+product+'\',\'DAY\',\''+msg.algo_uuid+'\',\''+msg.algo_name+'\');">Sell</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div>');
                        }
                        else if(positions.qty<0){
                            exit_window.find('.exit_header').addClass('exit_header_buy');
                            [seg,sym] = [msg['seg'],msg['sym']];
                            exit_window.find('.exit_header').html("<p>Buy "+sym+"&nbsp;x"+positions.qty+'<br><span>At market on '+seg+'</span></p>');

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

                            // exit_window.find('.exit_body').html('<div class="exit_options">'+x+'<div class="exit_qty"><p>Quantity</p><input type="number" id="position_qty" name="" value="'+Math.abs(positions.qty)+'"></div></div><div><div class="radio_options"><div><span id="buy_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MARKET</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div></div><div class="exit_price"><p>Price</p><input type="number" id="position_price" name="" value="0"></div></div></div><div  id="notif_actions"><button id="buy" onclick="exit_position_now_force_stop(\''+deployment_uuid+'\',\''+seg+'\',\''+sym+'\','+Math.abs(positions.qty)+',\'MARKET\',\'BUY\',\''+product+'\',\'DAY\',\''+msg.algo_uuid+'\',\''+msg.algo_name+'\');">BUY</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div>');
                            exit_window.find('.exit_body').html('<div class="exit_options">'+x+'<div class="notif_left"><div class="exit_qty"><p>Qty.</p><input type="number" id="position_qty" name="" value="'+Math.abs(positions.qty)+'" readonly></div><div class="exit_qty"><p>Price</p><input type="number" name="" id="position_price" value="'+0+'" readonly></div></div></div><div><div class="radio_options"><div><span id="buy_radio_option" class="radio_outer"><span class="radio_inner"></span></span><p id="option_selected">MARKET</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>LIMIT</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL</p></div><div><span class="radio_outer"><span class="radio_inner"></span></span><p>SL-M</p></div></div><div class="notif_right"><div class="exit_price"><p>Trigger price</p><input type="number" class="bg-stripe" id="position_trigger_price" name="" value="0" readonly></div><div class="exit_price"><p>Disclosed qty.</p><input type="number" class="bg-stripe" id="position_disclosed_qty" name="" value="0" readonly></div></div></div></div><div id="notif_actions"><button id="buy" onclick="exit_position_now_force_stop(\''+deployment_uuid+'\',\''+seg+'\',\''+sym+'\','+Math.abs(positions.qty)+',\'MARKET\',\'BUY\',\''+product+'\',\'DAY\',\''+msg.algo_uuid+'\',\''+msg.algo_name+'\');">Buy</button><button id="cancel" onclick="close_orders_popup();">Cancel</button></div>');
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
                $('.exit_position, .stop_options').hide();$('.algo_stopped').show();
                // $('#close_orders_popup_div').unbind('click');
                // $('#close_orders_popup_div').prop('onclick',null).off('click');
                // $('#close_orders_popup_div').prop('onclick',function(){
                setTimeout(function(){ window.location = '/dashboard/'; }, 2000);
                show_snackbar(null,'Algo has been stopped successfully','success');
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