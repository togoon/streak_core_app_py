$(window).load(function() {
    // Animate loader off screen
    $(".loader_parent").fadeOut();
  });
function show_profile(){
    $("#user_billing").hide();
    $("#profile").show();
    $("#billing_option").removeClass("myaccount_menu_selected");
    $("#profile_option").addClass("myaccount_menu_selected");
}
subscription_plan_popup_function = {'basic':'start_subscription_popup',
                                    'premium':'start_subscription_popup_premium',
                                    'ultimate':'start_subscription_popup_ultimate',
                                    }
function show_billing(){
    var params = {
        // 'deployment_uuid':dep_id,
    };
  var settings = {
      "async": true,
      "crossDomain": true,
      "url": '/fetch_billing/',
      "method": "GET",
      "headers": {
      },
      "data":params,
      "timeout": 10000,//40 sec timeout
    };
  $.ajax(settings).done(function (msg){
    if(msg.status=='success')
      {
        $("#profile").hide();
        // alert();
        $("#user_billing").show();
        $("#profile_option").removeClass("myaccount_menu_selected");
        $("#billing_option").addClass("myaccount_menu_selected");
        user_subscription = JSON.parse(msg.user_subscription);
        if(user_subscription.user_broker_id)
          $('.payment_description').html('Kite - '+user_subscription.user_broker_id);

        if(msg.subscription_status.subscription_plan=="Free trial plan")
        {
          $('.plan_descriptions').html('<p>No active subscription</p>');
          $('.cancel_subscription').html('Start subscription');
          $('.cancel_subscription').attr('onclick','start_subscription_free_popup();');
        }
        else if(msg.subscription_status.subscription_valid){
            $('.plan_icon').html('<img src="/static/imgs/new/home/plan'+msg.subscription_status.subscription_type+'.svg">');
            $('.plan_icon').addClass('plan_icon'+msg.subscription_status.subscription_type);
            if(msg.subscription_status.subscription_type!=0)
              $('.plan_descriptions').html('<p class="plan_title">'+to_title(msg.subscription_status.subscription_plan)+'<span>&#8377; '+parseFloat(msg.subscription_status.current_subscription_price).toFixed(0)+' + GST / month</span></p><p class="plan_sub_desc plan_sub_desc'+msg.subscription_status.subscription_type+'"><span></span> '+msg.subscription_status.total_backtest+' Backtests per day</p><p class="plan_sub_desc plan_sub_desc'+msg.subscription_status.subscription_type+'"><span></span> '+msg.subscription_status.total_deployments+' Live deployments at a time</p>');
            else
              $('.plan_descriptions').html('<p class="plan_title">7 days free trial<span></span></p><p class="plan_sub_desc plan_sub_desc'+msg.subscription_status.subscription_type+'"><span></span> '+msg.subscription_status.total_backtest+' Backtests per day</p><p class="plan_sub_desc plan_sub_desc'+msg.subscription_status.subscription_type+'"><span></span> '+msg.subscription_status.total_deployments+' Live deployments at a time</p>');
            $('.cancel_subscription').html('Cancel auto renew');
            $('.cancel_subscription').attr('onclick','cancel_subscription_popup();');
            if(!msg.subscription_status.subscription_autorenew){
              $('.cancel_subscription').html('Enable auto renew');
              $('.cancel_subscription').attr('onclick',subscription_plan_popup_function[msg.subscription_status.subscription_plan]+'(\'restart\');'); 
            }
            if(msg.subscription_status.subscription_type==0){
              $('.cancel_subscription').html('Start subscription');
              $('.cancel_subscription').attr('onclick','start_subscription_free_popup(\''+msg.subscription_status.subscription_plan+'\',\'restart\',\'False\');');
              $('.change_plan').hide();
            }
            else{
              $('.change_plan').show();
              $('.change_plan').attr('onclick','change_subscription_plan_popup(\''+msg.subscription_status.subscription_plan+'\',\'first\',\'True\');');
            }
        }
        else{
            $('.plan_description').html('<p>No active subscription</p>');
            $('.cancel_subscription').html('Start subscription');
            $('.cancel_subscription').attr('onclick','start_subscription_free_popup();');
        }
        if(msg.subscription_status.subscription_autorenew && msg.subscription_status.next_billing_date!='N/A'){
          date = moment(msg.subscription_status.next_billing_date).format("DD/MMM/YYYY");
          if(msg.subscription_status.renew_plan!=msg.subscription_status.subscription_plan && msg.subscription_status.renew_plan!= undefined && msg.subscription_status.renew_plan!='')
            $('.billing_section_subtitle').html('Next billing date - '+date+' ( '+to_title(msg.subscription_status.renew_plan)+' ) ');
          else
            $('.billing_section_subtitle').html('Next billing date - '+date);
        }
        else{
          if(msg.subscription_status.renew_plan!=msg.subscription_status.subscription_plan && msg.subscription_status.renew_plan!= undefined && msg.subscription_status.renew_plan!='')
            $('.billing_section_subtitle').html('Next billing date - '+'N/A');//+' ( '+to_title(msg.subscription_status.renew_plan)+' ) ');
          else
            $('.billing_section_subtitle').html('Next billing date - N/A');
        }
        $('.billing_table').html('<div class="billing_details_title"> <div class="billing_row_date_title"><p>Date</p></div> <div class="billing_row_description_title"><p>Plan</p></div> <div class="billing_row_period_title"><p>Billing period</p></div> <div class="billing_row_method_title"><p>Payment method</p></div> <div class="billing_row_subtotal_title"><p>Sub-total</p></div> <div class="billing_row_total_title"><p>Total</p></div> <div class="billing_row_download_title"><p></p></div> </div>');
        for(var i=0; i<msg.user_subscription_log.length; i++){
          row = JSON.parse(msg.user_subscription_log[i]);
          if(parseFloat(row.subscription_total_price)!=0)
            {
              billing_row = '<div class="billing_details_row"> <div class="billing_row_date"><p>'+moment(row.created_at['$date']).utcOffset(0).format("DD/MMM/YYYY")+'</p></div> <div class="billing_row_description"><p>'+row.subscription_plan+'</p></div> <div class="billing_row_period"><p>'+moment(row.subscription_start['$date']).utcOffset(0).format("DD/MMM/YYYY")+'&nbsp;-&nbsp;'+moment(row.subscription_stop['$date']).utcOffset(0).format("DD/MMM/YYYY")+'</p></div> <div class="billing_row_method"><p><span><img src="/static/imgs/new/kite.svg"></span>'+row.user_broker_id+'</p></div> <div class="billing_row_subtotal"><p>&#8377&nbsp;'+parseFloat(row.subscription_price).toFixed(2)+'&nbsp;<span class="tax">(+&nbsp;&#8377&nbsp;'+parseFloat(row.subscription_tax).toFixed(2)+'&nbsp;Tax)</span></p></div> <div class="billing_row_total"><p>&#8377&nbsp;'+parseFloat(row.subscription_total_price).toFixed(0)+'</p></div> <div class="billing_row_download"><p><img src="/static/imgs/download_bill.png"></p></div> </div>';
              $('.billing_table').append(billing_row);
            }
        }
      }
    });

}
$(document).ready(function(){
    if(window.location.href.indexOf('#billing')!=-1)
    {
        show_billing();
    }
    $("#billing_option").click(function(){
        show_billing(); 
    });
    $("#profile_option").click(function(){
        show_profile();
    });

    $('.cancel_subscription_message button').attr('style','background-color: #989fa7;border: 1px solid #bfc7d1;');
    $('.cancel_subscription_message button').attr('onclick','show_snackbar(null,\'Check the box if you are sure\')')

    $('#cancel_subscription_checkbox').on('change',function(){
      if($('input[name=cancel_subscription_checkbox]:checked').is(':checked')){
        $('.cancel_subscription_message button').attr('style','background-color: #ff4343;border: 1px solid #ff4343')
        $('.cancel_subscription_message button').attr('onclick','cancel_subscription();');
      }else{
        $('.cancel_subscription_message button').attr('style','background-color: #989fa7;border: 1px solid #bfc7d1;');
        $('.cancel_subscription_message button').attr('onclick','show_snackbar(null,\'Check the box if you are sure\')')
      }
    });

    $("#save_probile_changes_btn").click(function(){
      var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
      full_name = $('#account_name').val()
      phone_number = $('#account_phone_number').val()
      email = $('#account_email').val()
        var params = {
        // 'deployment_uuid':dep_id,
        'csrfmiddlewaretoken':csrfmiddlewaretoken,
        'full_name':full_name,
        'phone_number':phone_number,
        'email':email
          };
        var settings = {
            "async": true,
            "crossDomain": true,
            "url": '/save_profile_change/',
            "method": "POST",
            "headers": {
            },
            "data":params,
            "timeout": 10000,//40 sec timeout
          };
        $.ajax(settings).done(function (msg){
          if(msg.status=='success')
            {
              show_snackbar(null,'Profile updated',type='success');
            }
          else if(msg.status=='error'){
              show_snackbar(null,msg.msg);
          }else{
              show_snackbar(null,'Error occured while saving, try again');
          }
        });
    });
});