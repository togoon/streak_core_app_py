$(window).load(function() {
    // Animate loader off screen
    $(".loader_parent").fadeOut();
});

function all_filled(){
	if($('.full_name').val()!='' && $('.phone_number').val()!='' && $('.email').val() && $('.phone_number').val().length>=10 && $('.phone_number').val().length<=13 && $('.email').val().indexOf('@')!=-1 && $('.email').val().indexOf('.')!=-1){
	  	$('#form_submit').css({'cursor': 'pointer'});
	  	$('#form_submit').attr('style','background-color: #0088ff;');
	    $('#form_submit').attr('onclick','form_submit_click();ga("send", "event", "Signup", "Submit Click");');
	}
	else{
		$('#form_submit').css({'cursor': 'no-drop'});	
		$('#form_submit').attr('style','background-color: #989fa7;border: 1px solid #bfc7d1;');
    	$('#form_submit').attr('onclick','show_snackbar(null,\'Fill all the fields correctly\');ga("send", "event", "Signup", "Submit Click");');
	}
}
function form_submit_click(){
		full_name = $('.full_name').val()
		phone_number = $('.phone_number').val()
		email = $('.email').val()
		if(phone_number.length<10 || phone_number.length>13){
	      	 show_snackbar(null,'Enter a valid 10 digit phone number');
				return false;
		}
		if(full_name.length<3){
	      	 show_snackbar(null,'Name too short');
				return false;
		}
		if(full_name.length>50){
	      	 show_snackbar(null,'Name too long');
				return false;
		}
		if(email.length<5){
	      	 show_snackbar(null,'Email too short');
				return false;
		}
		if(email.length>50){
	      	 show_snackbar(null,'Email too long');
				return false;
		}
		var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
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
	      "url": '/save_lead/',
	      "method": "POST",
	      "headers": {
	      },
	      "data":params,
	      "timeout": 10000,//40 sec timeout
	    };
	  $('#form_submit').css({'cursor': 'no-drop'})
	  $.ajax(settings).done(function (msg){
	    if(msg.status=='success')
	      {
	      	 // show_snackbar(null,'Details submitted, our team will get back to you',type='success');
	      	 $('.signup_sec').html('<div class="signup_logo"><img src="/static/imgs/logo_icon.svg"></div><p class="signup_complete">Sign up successful</p><p class="signup_complete_subtitle">We will get in touch with you shortly.</p>')
	      }
	      else{
	      	if(msg.status=='error' && msg.error=='inputs'){
	      	 show_snackbar(null,msg.msg);
	      	}else{
		      	 show_snackbar(null,'Unkown error, please try again');
	      	}
	      }
		}).fail(function(){
		    show_snackbar(null,'Check your internet and please try again');
		}).complete(function(){
	  		$('#form_submit').css({'cursor': 'pointer'})
		});
}
$(document).ready(function() {
	$('#form_submit').css({'cursor': 'no-drop'});
	$('#form_submit').attr('style','background-color: #989fa7;border: 1px solid #bfc7d1;');
    $('#form_submit').attr('onclick','show_snackbar(null,\'Fill all the fields\');ga("send", "event", "Signup", "Submit Click");');

    $('.full_name').on('focus',function(){all_filled();});
    $('.phone_number').on('focus',function(){all_filled();});
    $('.email').on('focus',function(){all_filled();});

    $('.full_name').on('change input',function(){all_filled();});
    $('.phone_number').on('change input',function(){all_filled();});
    $('.email').on('change input',function(){all_filled();});

	$('#signup_form').submit(function(){
		event.preventDefault();
		return false;
	});
	
});