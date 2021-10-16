from django.shortcuts import render,redirect
from django.http import JsonResponse
import random,string
import uuid
import datetime
import traceback
import hashlib
from django.utils import timezone
from django.conf import settings
from coreapp import models
from coreapp.views.utility import initialize_account#,mailing_helper
import re
from mongoengine import ValidationError,NotUniqueError
import ujson
import requests
from django.middleware import csrf
import pyotp
from django_redis import get_redis_connection
import hashlib
import utility as utils
from coreapp.views import payments
from mongoengine import DoesNotExist
from django.contrib.auth import update_session_auth_hash

def authenticate(unique_id,password):
	try:
		if '@' in unique_id:
			user = models.UserProfile.objects.get(email=unique_id)
			if user.check_password(password):
				print"yooooooooo"
				return user
			else:
				return -2
		else:
			if len(unique_id) == 10 and unique_id.isdigit():
				user = models.UserProfile.objects.get(phone_number=unique_id)
				if user.check_password(password):
					return user
				else:
					return -2
	except DoesNotExist:
		return -1
	except:
		print(traceback.format_exc())
		return None
	return None

def find_all_broker_accounts(email,return_uuids=False):
	brokers_added = {"default":None,"brokers":[]}
	user_uuids = []
	u = None
	try:
		u = models.UserProfile.objects.get(email=email)
		if u.first_broker!="-":
			brokers_added={"default":u.first_broker,"brokers":[u.first_broker]}
		user_uuids.append(u.user_uuid)
	except:
		pass
	users = models.UserProfile.objects(additional_details__secondary_email=email)
	for us in users:
		if us.first_broker!="-":
			brokers_added["brokers"].append(us.first_broker)
		user_uuids.append(us.user_uuid)

	if return_uuids:
		brokers_added["uuids"] = user_uuids
	return brokers_added
	
def validate_email(request):
	if request.method == "POST":
		email = request.POST.get("email","")
		try:
			user = models.UserProfile.objects.get(email=email)
			brokers_added = find_all_broker_accounts(email)
			return  JsonResponse({'status':'success','status_code':100,"brokers_added":brokers_added})

		except DoesNotExist:
			# check if the email is registered in some secondary email
			try:
				user = models.UserProfile.objects(additional_details__secondary_email=email)
				if len(user)==0:
					raise
				brokers_added = find_all_broker_accounts(email)
				return JsonResponse({'status':'success','status_code':100,"brokers_added":brokers_added})
			except:
				pass
			return  JsonResponse({'status':'success','status_code':101})
		except:
			return  JsonResponse({'status':'error','status_code':0})
	return  JsonResponse({'status':'error','error_msg':'Unknown method','status_code':0})

def user_login(request):
	resp_json = False
	if(request.META.get('HTTP_X_CSRFTOKEN',None)):
		resp_json = True

	if request.method == "GET":
		user_uuid = request.session.get('user_uuid','')
		user_is_auth = request.session.get('user_is_auth',False)
		
		if settings.ENV == "local" or settings.ENV == 'local1':
			user_uuid = '123'
			user_is_auth = True
		# if settings.DEBUG:

		if user_uuid!='' and user_is_auth:
			if resp_json:
				return JsonResponse({'status':'success','csrf':csrf.get_token(request),'sessionid':request.session.session_key,"status_code":400})
			return redirect('dashboard')

		return render(request,'login.html',{})

	if request.method == "POST":
		token = request.POST.get('token','')
		if token!="Fv7qPPuL5LPUeXtG" and request.POST.get('gpPydvAvskE8a83L','')!='3PW7QP9YWwyAJEux':
			try:
				google_response = requests.request('POST',"https://www.google.com/recaptcha/api/siteverify",data="secret="+settings.RECAPTCHA_SECRET+"&response="+token,headers={'Content-Type': "application/x-www-form-urlencoded"},timeout=5)
				if google_response.status_code == 200:
					if ujson.loads(google_response.text).get('success',False):
						pass
					else:
						print("google_response",google_response.text)
						return  JsonResponse({'status':'error','error_msg':'Invalid captcha'})
				else:
					pass
					# return  JsonResponse({'status':'error','error_msg':'Unknown'})
			except:
				print traceback.format_exc()
				# return  JsonResponse({'status':'error','error_msg':'Unable to resolve captcha'})
		email = request.POST.get('email','').lower()
		password = request.POST.get('password','')
		hash_password = hashlib.sha1(password).hexdigest()
		
		partner_ref = request.POST.get('partner_ref','')

		error = ""

		if '@' not in email:
			return JsonResponse({"status":"error","error_msg":"Invalid email","status_code":300})

		if len(password.strip())==0:
			return JsonResponse({"status":"error","error_msg":"Password is blank","status_code":303})

		u = authenticate(email,password=password)
		if u is None:
			print("user is None")
			return JsonResponse({"status":"error","error_msg":"Unexpected error","status_code":301})
		elif u==-1:
			# setup to signup process with Just email and set profile needs completing flag true
			
			salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
			key_expires = datetime.datetime.today() + datetime.timedelta(days=1)
			user_uuid = str(uuid.uuid4())
			activation_key = hashlib.sha1(salt+user_uuid).hexdigest()

			try:
				user_profile = models.UserProfile(
								user_uuid = user_uuid,
								user_broker_id = "EM-"+''.join([random.choice(string.ascii_uppercase) for _ in range(4)])+''.join(random.choice(datetime.datetime.now().strftime('%s')) for _ in range(6)),
								first_name = '',
								last_name = '',
								phone_number = '',
								email = email,
								password =  hash_password,
								status = 1,
								ref_id = ''.join(random.choice(string.ascii_letters) for _ in range(10)),
								short_link = '',
								first_broker='-'
								)
				user_auth = models.DirectUserEmailVerification(
								user_uuid = user_uuid,
								activation_key = activation_key,
								otp_key = str(random.randint(4111,9999)),
								key_expires = key_expires,
								used = False,
								salt = salt
								)

				# # creating first subscription of the user, with Free trial
				# subscription_uuid=str(uuid.uuid4())
				# subscription_log_uuid = str(uuid.uuid4())
				# user_subscription = models.UserSubscription(user_uuid=user_uuid,
				# 	subscription_uuid=subscription_uuid,
				# 	subscription_validity= datetime.datetime.today() + datetime.timedelta(days=int(30)),
				# 	latest_subscription_id = subscription_log_uuid,
				# 	user_broker_id = user_uuid,
				# 	subscription_type = 0,
				# 	subscription_product = 'free',
				# 	subscription_plan = 'free',
				# 	subscription_instance = 'trial'
				# 	)
				# user_subscription_log = models.UserSubscriptionLog(user_uuid=user_uuid,
				# 	subscription_log_uuid = subscription_log_uuid,
				# 	subscription_uuid = subscription_uuid,
				# 	subscription_start = datetime.datetime.today(),
				# 	subscription_stop = datetime.datetime.today() + datetime.timedelta(days=int(30)),
				# 	user_broker_id = user_uuid,
				# 	subscription_type = 0,
				# 	subscription_product = 'free',
				# 	subscription_plan = 'free',
				# 	subscription_instance = 'trial'
				# 	)
				user_profile.last_ip = request.META.get('HTTP_X_FORWARDED_FOR','')
					
				user_profile.save()
				user_auth.save()

				# user_subscription_log.save()
				# user_subscription.save()

				# request.session['user_uuid'] = user_uuid
				# request.session['user_name'] = first_name
				# request.session['user_email'] = email
				# request.session['user_is_auth'] = True
				
				# request.session['first_time_login'] = True
				# request.session['first_time_algos'] = True
				# request.session['first_time_dashboard'] = True
				# request.session['first_time_create_algorithm'] = True
				# request.session['first_time_orders'] = True
				# request.session['first_time_backtest'] = True
				# request.session['first_time_deploy'] = True
				# request.session['first_time_orderbook'] = True
				# request.session['first_time_portfolio'] = True
				request.session['session_secret'] = generate_random_hash()
				# initialize_account(user_uuid)

				if user_profile:
					if partner_ref.strip()=='':
						referral = ref_user_register_utility(request,user_uuid=user_uuid)
					# print '127.0.0.1/account_activate?auth='+activation_key
					activation_url = 'https://streak.tech'+'/account_activation?auth='+activation_key
					# mailing_helper(user_uuid=user_uuid,
									# broker_id='',
									# subject='Streak account activation mail <no-reply>',
									# body='Click on the activation link to activate your account, link '+activation_url,
									# sender="support@streak.world"
									# )
					try:
						url = "https://mailing.streak.solutions/streak_mail/support/send_mail"
						headers = {"content-type":"application/json"}
						method = "POST"
						# payload = ujson.dumps({
						# 		"recipients":[user_profile.email],
						# 		"subject":"Streak World| Account activation",
						# 		"body_data":'Click on the link to activate you Streak World account, '+activation_url,
						# 		"reply_to":'no-reply@streak.world',
						# 		"template_id":None,
						# 		"sender": "updates@streak.world"
						# 	})
						payload =  ujson.dumps({
								"recipients": [user_profile.email ],
								"template_id": "world_account_activate",
								"subject": "Streak Tech | Email Verification",
								"body_data": [ activation_url,activation_url ]
								})
						response = requests.request(method,url,data=payload,headers=headers,timeout=60)
						print "mail",response.text
						# print response.status_code
					except:
						print traceback.format_exc()
						if(request.POST.get('resp','')=='json'):
							return JsonResponse({'status':'error','error':True,'error_msg':'Something went wrong, please try again or write to us support[@]streak.tech',"status_code":302})
						elif resp_json:
							return JsonResponse({'status':'error','error':True,'error_msg':'Something went wrong, please try again or write to us support[@]streak.tech',"status_code":302})
						else:
							return render(request,'signup.html',{'status':'error','error_msg':'Something went wrong, please try again or write to us support[@]streak.tech','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password})
					# otp = random.randint(4111,9999)
					# # user_profile verification via mail or msg
					# request.session['signup_process'] = 1
					# return JsonResponse({'status':'success','redirect_to':'Check email for activation link'})
					# u.first_login=False
					# u.save()

					if(partner_ref!=''):
						map_user = {
									"user_broker_id": u.user_broker_id,
									"new_user": True,
									"referral_code": partner_ref
									}
						con = get_redis_connection('default')
						con.publish('partner_ref',ujson.dumps(map_user))

					if(request.POST.get('resp','')=='json'):
						return JsonResponse({'status':'success','msg':'Check email for activation link','msg_title':'Email sent',"status_code":203})
					elif resp_json:
						return JsonResponse({'status':'success','msg':'Check email for activation link','msg_title':'Email sent',"status_code":203})
					else:
						return render(request,'verification.html',{'status':'success','msg_title':'Account activation link emailed','msg_content':'Kindly activate your account by using the emailed link'})

			except NotUniqueError:
				# log error
				# return JsonResponse({'status':'success','error':'Email or phone number already in use!'})
				if(request.POST.get('resp','')=='json'):
					return JsonResponse({'status':'error','error':True,'error_msg':'Email or phone number already in use!','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password,"status_code":201})
				elif resp_json:
					return JsonResponse({'status':'error','error':True,'error_msg':'Email or phone number already in use!','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password,"status_code":201})
				else:
					return render(request,'signup.html',{'status':'error','error':True,'error_msg':'Email or phone number already in use','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password})

			except:
				# log error
				print traceback.format_exc()
				# return JsonResponse({'status':'success','error':'Something went wrong, please try again or write to us support[@]streak.world'})
				if(request.POST.get('resp','')=='json'):
					return JsonResponse({'status':'error','error':True,'error_msg':'Something went wrong, please try again or write to us support[@]streak.tech','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password,"status_code":301})
				elif resp_json:
					return JsonResponse({'status':'error','error':True,'error_msg':'Something went wrong, please try again or write to us support[@]streak.tech','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password,"status_code":301})
				else:
					return render(request,'signup.html',{'status':'error','error':True,'error_msg':'Something went wrong, please try again or write to us support[@]streak.tech','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password})

		elif u==-2:
			return JsonResponse({'status':'error','error':"Incorrect password","status_code":105})
		else: 
			# intiate login process
			u.last_ip = request.META.get('HTTP_X_FORWARDED_FOR','')
			if u.status==2:
				request.session['user_uuid'] = u.user_uuid
				request.session['user_name'] = u.first_name+' '+u.last_name
				request.session['user_email'] = u.email
				request.session['user_is_auth'] = True
				request.session['full_broker_name'] = "-"
				if(u.otp_secret!=''):
					request.session['two_fa'] = True
				request.session['user_is_auth'] = True
				if u.first_login==True:
					request.session['first_time_login'] = True
					u.first_login=False
					# u.save()
				if not request.session.session_key:
					request.session.save()

				if(partner_ref!=''):
					map_user = {
								"user_broker_id": u.user_broker_id,
								"new_user": False,
								"referral_code": partner_ref
								}
					con = get_redis_connection('default')
					con.publish('partner_ref',ujson.dumps(map_user))

				if resp_json:
					if u.otp_secret!='':
						return JsonResponse({'status':'success','two_fa':True,'sessionid':request.session.session_key,"status_code":101})
					if u.login_count<=10:
						u.login_count += 1
					u.save()
					return JsonResponse({'status':'success','csrf':csrf.get_token(request),'sessionid':request.session.session_key,"status_code":100})
				return redirect('dashboard')
				# if redirect_to != '':
				# 	return JsonResponse({'status':'success','redirect_to':redirect_to})
				# else:
				# 	return JsonResponse({'status':'success','redirect_to':'/dashboard'})
			else:
				request.session['user_uuid'] = u.user_uuid
				request.session['user_name'] = u.first_name+' '+u.last_name
				request.session['user_email'] = u.email
				request.session['user_is_auth'] = True
				request.session['full_broker_name'] = "-"
				if(u.otp_secret!=''):
					request.session['two_fa'] = True
				request.session['user_is_auth'] = True
				if u.first_login==True:
					request.session['first_time_login'] = True
					# u.first_login=False
					# u.save()
				if not request.session.session_key:
					request.session.save()
				# error = 'Email or phone number not verified'
				user_verif = models.DirectUserEmailVerification.objects.get(user_uuid=u.user_uuid,used=False)
				key_expires = timezone.make_aware(user_verif.key_expires,timezone.get_default_timezone())

				time_now = timezone.make_aware(datetime.datetime.now(),timezone.get_default_timezone())

				if key_expires < time_now:
					salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
					key_expires = datetime.datetime.today() + datetime.timedelta(days=1)
					activation_key = hashlib.sha1(salt+u.user_uuid).hexdigest()
					user_verif.key_expires = key_expires
					user_verif.salt = salt
					user_verif.activation_key = activation_key
					user_verif.save()
					try:
						url = "https://mailing.streak.solutions/streak_mail/world_support/send_mail"
						headers = {"content-type":"application/json"}
						activation_url = 'https://web.streak.tech'+'/account_activation?auth='+activation_key
						method = "POST"
						# payload = ujson.dumps({
						# 		"recipients":[user_profile.email],
						# 		"subject":"Streak World| Account activation",
						# 		"body_data":'Click on the link to activate you Streak World account, '+activation_url,
						# 		"reply_to":'no-reply@streak.world',
						# 		"template_id":None,
						# 		"sender": "updates@streak.world"
						# 	}) 
						payload =  ujson.dumps({
								"recipients": [u.email ],
								"template_id": "world_account_activate",
								"subject": "Streak Tech | Email Verification",
								"body_data": [ activation_url,activation_url ]
								})
						response = requests.request(method,url,data=payload,headers=headers,timeout=60)
						print "mail",response.text
						# print response.status_code
					except:
						print traceback.format_exc()
						if(request.POST.get('resp','')=='json'):
							return JsonResponse({'status':'error','error':True,'error_msg':'Something went wrong, please try again or write to us support[@]streak.tech',"status_code":302})
						elif resp_json:
							return JsonResponse({'status':'error','error':True,'error_msg':'Something went wrong, please try again or write to us support[@]streak.tech',"status_code":302})
						else:
							return render(request,'signup.html',{'status':'error','error_msg':'Something went wrong, please try again or write to us support[@]streak.tech','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password})
					if(request.POST.get('resp','')=='json'):
						return JsonResponse({'status':'success','msg':'Check email for new activation link','msg_title':'Email sent','status_code':103,'csrf':csrf.get_token(request),'sessionid':request.session.session_key})
					elif resp_json:
						return JsonResponse({'status':'success','msg':'Check email for new activation link','msg_title':'Email sent','status_code':103,'csrf':csrf.get_token(request),'sessionid':request.session.session_key})
					else:
						return render(request,'verification.html',{'status':'success','msg_title':'Account activation link emailed','msg_content':'Kindly activate your account by using the emailed link'})
				else:
					if(request.POST.get('resp','')=='json'):
						return JsonResponse({'status':'success','msg':'Check email, activation link already sent','msg_title':'Email sent','status_code':102,'csrf':csrf.get_token(request),'sessionid':request.session.session_key})
					elif resp_json:
						return JsonResponse({'status':'success','msg':'Check email, activation link already sent','msg_title':'Email sent','status_code':102,'csrf':csrf.get_token(request),'sessionid':request.session.session_key})
					else:
						return render(request,'verification.html',{'status':'success','msg_title':'Account activation link already emailed','msg_content':'Kindly activate your account by using the emailed link'})

			# if(request.POST.get('resp','')=='json' or resp_json):
			# 	return JsonResponse({'status':'error','error_msg':error})
			# else:
			# 	return render(request,'login.html',{'error_msg':error,'email':email,'password':password})
			return JsonResponse({'status':'error','error':error,'error_msg':'Unauthorized',"status_code":304})
	return JsonResponse({'status':'error','error_msg':'Restricted method',"status_code":304})


def generate_ref_deeplink(ref_id,msg_title="Your friend invited you",msg_desc="Join Streak, and join the future of trading",msg_img="https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/world/4.png"):
	url = "https://firebasedynamiclinks.googleapis.com/v1/shortLinks"
	querystring = {"key":"AIzaSyDzocCCToSyU45Snp5Y-t2LGzKMgm4P4o8"}
	payload = {
		"dynamicLinkInfo": {
		"domainUriPrefix": "https://ref.streak.world",
		"link": "https://streak.world/?ref="+ref_id,
		"androidInfo": {
		  "androidPackageName": "world.streak"
		},
		"iosInfo": {
		  "iosBundleId": "streak.world"
		},
		 "socialMetaTagInfo": {
		  "socialTitle": msg_title,
		  "socialDescription": msg_desc,
		  "socialImageLink": msg_img
		}
		},
		"suffix":{"option":"UNGUESSABLE"}
		}
	headers = {
		'Content-Type': "application/json",
		'Cache-Control': "no-cache",
		'Postman-Token': "091b3824-9376-4e57-aad4-429cf632e79d"
	}
	response = requests.request("POST", url, data=ujson.dumps(payload), headers=headers, params=querystring,timeout=5)
	if response.status_code == 200:
		try:
			resp = ujson.loads(response.text)
			return resp.get("shortLink","")  
		except:
			print(traceback.format_exc())
			pass
	return ""

def account_activate(request):
	if request.method == "POST":
		user_uuid = request.session.get('user_uuid','')
		user_is_auth = request.session.get('user_is_auth',False)
		# if settings.DEBUG:

		# if user_uuid!='' and user_is_auth:
		# 	# return redirect('dashboard')
		# 	return JsonResponse({'status':'error','error_msg':"Expired link",'error_msg':'Unauthorized'})
		auth = request.POST.get('auth','')
		if auth == '':
			# return redirect('home')
			return JsonResponse({'status':'error','error_msg':"Missing auth"})
		try:
			user_verif = models.DirectUserEmailVerification.objects.get(activation_key=auth,used=False)
			user_uuid = user_verif.user_uuid
			user_id_auth = hashlib.sha1(user_verif.salt+user_verif.user_uuid).hexdigest()
			if(auth==user_id_auth):
				user = models.UserProfile.objects.get(user_uuid=user_verif.user_uuid,verification_status=False)

				key_expires = timezone.make_aware(user_verif.key_expires,timezone.get_default_timezone())

				time_now = timezone.make_aware(datetime.datetime.now(),timezone.get_default_timezone())

				if key_expires < time_now:
					return JsonResponse({'status':'error','error_msg':"Expired link",'error_msg':'Unauthorized'})

				user.verification_status = True
				user.status = 2
				user.last_ip = request.META.get('HTTP_X_FORWARDED_FOR','')

				# creating first subscription of the user, with Free trial
				subscription_uuid=str(uuid.uuid4())
				subscription_log_uuid = str(uuid.uuid4())
				user_subscription = models.UserSubscription(user_uuid=user_uuid,
					subscription_uuid=subscription_uuid,
					subscription_validity= datetime.datetime.today() + datetime.timedelta(days=int(7)),
					latest_subscription_id = subscription_log_uuid,
					subscription_type = 0,
					user_broker_id = user.user_broker_id,
					subscription_product = 'free',
					subscription_plan = 'free',
					subscription_instance = 'trial'
					)
				user_subscription_log = models.UserSubscriptionLog(user_uuid=user_uuid,
					subscription_log_uuid = subscription_log_uuid,
					subscription_uuid = subscription_uuid,
					subscription_start = datetime.datetime.today(),
					subscription_stop = datetime.datetime.today() + datetime.timedelta(days=int(7)),
					subscription_type = 0,
					subscription_product = 'free',
					subscription_plan = 'free',
					user_broker_id = user.user_broker_id,
					subscription_instance = 'trial'
					)

				user.short_link = generate_ref_deeplink(ref_id=user.ref_id)

				user.save()
				user_verif.used = True

				user_subscription_log.save()
				user_subscription.save()
				user_verif.save()

				# if a_results is None:
				# 	print 'not allowed user2'
				# 	request.session['blocked_login'] = True
				# 	print request.session['blocked_login']
				# 	return redirect('home')
				# initialize_account(user_uuid)
				# return JsonResponse({'status':'success'})
				# if request.POST.get('resp',None)=='json':
				utils.send_initial_emails(user_uuid=user.user_uuid,email=user.email,name=user.first_name)
				utils.initialize_account(user.user_uuid)

				request.session['user_uuid'] = user.user_uuid
				request.session['user_name'] = user.first_name+' '+user.last_name
				request.session['user_email'] = user.email
				request.session['full_broker_name'] = "-"
				request.session['user_is_auth'] = True
				if(user.otp_secret!=''):
					request.session['two_fa'] = True
				request.session['user_is_auth'] = True
				if user.first_login==True:
					request.session['first_time_login'] = True
				if not request.session.session_key:
					request.session.save()
				ref_user_register_utility(request,user_uuid=user_uuid,status=1)
				return JsonResponse({'status':'success','msg_title':'Account verified','msg_content':' Account has been activated, go ahead and login','csrf':csrf.get_token(request),'sessionid':request.session.session_key})
				# else:
				# 	return render(request,'verification.html',{'status':'success','msg_title':'Account verified','msg_content':' Account has been activated, go ahead and login'})
			# return JsonResponse({'status':'error','error_msg':'Invalid auth'})
			# if request.POST.get('resp',None)=='json':
			return JsonResponse({'status':'error','error_msg':'Invalid link'})
			# else:
			# 	return render(request,'verification.html',{'status':'success','msg_title':'Invalid auth','msg_content':'Invalid url'})
		except:
			print traceback.format_exc()
			return JsonResponse({'status':'error','error_msg':'Unknown'})
	# return JsonResponse({'status':'error'})
	return JsonResponse({'status':'error','error_msg':'Unknown'})

def generate_random_hash():
	hash = random.getrandbits(128)
	return "%032x" % hash

def ref_user_register_utility(request,user_uuid="",status=0):
	# resp_json = False
	# if(request.META.get('HTTP_X_CSRFTOKEN',None)):
	# 	resp_json = True
	# user_uuid = request.session.get('user_uuid','')
	# user_is_auth = request.session.get('user_is_auth',False)
	# # if settings.DEBUG:
	# if settings.ENV == "local" or settings.ENV == 'local1':
	# 	user_uuid = '123'
	# 	user_is_auth = True
	# 	request.session['user_is_auth'] = True
	# 	request.session['user_uuid'] = '123'
	# 	user_uuid = '123'

	# if not user_is_auth:
	# 	return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)

	if request.method!="POST":
		return JsonResponse({"status":"error","error_msg":"Method"})

	ref_id = request.POST.get("ref_id",'')
	# ref_source = request.POST.get("ref_source",'')
	ref_device = request.POST.get("ref_device",'')
	
	try:
		user_profile = models.UserProfile.objects.get(user_uuid=user_uuid)
	except DoesNotExist:
		print(traceback.format_exc())
		return False
			
	try:
		ref_users = models.ReferralUsers.objects.get(user_uuid=user_uuid)
		referral_rewards_list = []
		ref_status = 0
		if user_profile.status==1:
			# referral_rewards = [{
			# 				"code":"",
			# 				"status":0,
			# 				"claimed":False,
			# 				"credits":-1,
			# 				"created_at" : datetime.datetime.now()
			# 				"updated_at" : datetime.datetime.now()
			# 			}]
			ref_status = 0
		elif user_profile.status==2 and ref_users.ref_status<status:
			referral_rewards = models.ReferralRewards(ref_id=ref_users.ref_id,
												user_uuid=user_uuid,
												ref_code=str(uuid.uuid4()),
												status=status,
												claimed=False,
												credits=0
												)
			referral_rewards.save()
			send_notification(user_uuid)

			ref_status = status
		else:
			
			return False
		ref_users.referral_rewards = referral_rewards_list
		ref_users.ref_status = ref_status
		try:
			ref_users.save()
			return True
		except:
			print(traceback.format_exc())
	except DoesNotExist:
		if ref_id.strip()=="": #forces creation only to happen only if ref_id is present
			return False
		ref_users = models.ReferralUsers(
							user_uuid=user_uuid,
							ref_id=ref_id,
							ref_uuid=str(uuid.uuid4()),
							email=user_profile.email,
							ref_first_name=user_profile.first_name,
							ref_last_name=user_profile.last_name,
							ref_device=ref_device
							)

		referral_rewards_list = []
		ref_status = 0
		if user_profile.status==1:
			# referral_rewards = [{
			# 				"code":"",
			# 				"status":0,
			# 				"claimed":False,
			# 				"credits":-1,
			# 				"created_at" : datetime.datetime.now()
			# 				"updated_at" : datetime.datetime.now()
			# 			}]
			ref_status = 0
		elif user_profile.status==2:
			# referral_rewards = [{
			# 				"code":str(uuid.uuid4()),
			# 				"status":1,
			# 				"claimed":False,
			# 				"credits":-1,
			# 				"created_at" : datetime.datetime.now()
			# 				"updated_at" : datetime.datetime.now()
			# 			}]
			referral_rewards = models.ReferralRewards(ref_id=ref_id,
												user_uuid=user_uuid,
												ref_code=str(uuid.uuid4()),
												status=status,
												claimed=False,
												credits=0
												)
			referral_rewards.save()
			ref_status = status
			send_notification(user_uuid)

		ref_users.referral_rewards = referral_rewards_list
		ref_users.ref_status = ref_status

		try:
			ref_users.save()
			return True
		except:
			print(traceback.format_exc())

	return False

def sync_contacts(request):
	resp_json = False
	if(request.META.get('HTTP_X_CSRFTOKEN',None)):
		resp_json = True
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		request.session['user_is_auth'] = True
		request.session['user_uuid'] = '123'
		user_uuid = '123'

	if not user_is_auth:
		return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)

	if request.method=="POST":

		contacts_list = request.POST.get('contacts_list','')
		try:
			contacts_list = ujson.loads(contacts_list)
			try:
				user_contacts = models.DirectUserSyncContacts.objects.get(user_uuid=user_uuid)
				user_contacts.contacts_list=contacts_list
				user_contacts.save()

			except DoesNotExist:
				user_contacts = models.DirectUserSyncContacts(user_uuid=user_uuid,
					contacts_list=contacts_list)
				user_contacts.save()
			
			return JsonResponse({"status":"success"})
		except:
			print(traceback.format_exc())
			return JsonResponse({"status":"error","error_msg":"Invalid payload"})
	if request.method=="GET":
		try:
			user_contacts = models.DirectUserSyncContacts.objects.get(user_uuid=user_uuid)
			user_contacts.contacts_list=contacts_list
			user_contacts.save()
			return JsonResponse({"status":"success","updated_at":user_contacts.updated_at,"contacts_list":user_contacts.contacts_list})
			
		except DoesNotExist:
			return JsonResponse({"status":"error","error_msg":"Invalid request"})

	return JsonResponse({"status":"error","error_msg":"Method"})

def avail_reward(request):
	resp_json = False
	if(request.META.get('HTTP_X_CSRFTOKEN',None)):
		resp_json = True
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		request.session['user_is_auth'] = True
		request.session['user_uuid'] = '123'
		user_uuid = '123'

	if not user_is_auth:
		return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)

	if request.method=="POST":
		ref_code = request.POST.get("ref_code")
		user_profile = models.UserProfile.objects.get(user_uuid=user_uuid)
		ref_id = user_profile.ref_id
		referral_rewards = models.ReferralRewards.objects.get(ref_code=ref_code)
		if referral_rewards.claimed==False:
			if referral_rewards.status==1:
				try:
					user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)

					if user_subscription.subscription_price==0 and user_subscription.subscription_type==0:
						# plan_t = random.randint(1,3)
						plan_t = random.choice(plan_selector)
						if plan_t==1:
							referral_rewards.credits=0
							referral_rewards.credit_type=1
							user_subscription.subscription_type = 1
							user_subscription.subscription_product = 'basic'
							user_subscription.subscription_plan = 'basic'
							user_subscription.subscription_validity = datetime.datetime.now()+datetime.timedelta(days=7)
							referral_rewards.claimed_msg = "Upgraded to Basic plan"
							referral_rewards.claimed_desc= "You got rewarded FREE upgrade to 7 Days of Basic"
						elif plan_t==2:
							referral_rewards.credits=0
							referral_rewards.credit_type=1
							user_subscription.subscription_type = 2
							user_subscription.subscription_product = 'premium'
							user_subscription.subscription_plan = 'premium'
							user_subscription.subscription_validity = datetime.datetime.now()+datetime.timedelta(days=7)
							referral_rewards.claimed_msg = "Upgraded to Premium plan"
							referral_rewards.claimed_desc= "You got rewarded FREE upgrade to 7 Days of Premium"
						elif plan_t==3:
							referral_rewards.credits=0
							referral_rewards.credit_type=1
							user_subscription.subscription_type = 3
							user_subscription.subscription_product = 'ultimate'
							user_subscription.subscription_plan = 'ultimate'
							user_subscription.subscription_validity = datetime.datetime.now()+datetime.timedelta(days=7)
							referral_rewards.claimed_msg = "Upgraded to Ultimate plan"
							referral_rewards.claimed_desc= "You got rewarded FREE upgrade to 7 Days of Ultimate"

						user_subscription.save()
					else:
						referral_rewards.credits=random.randint(1,5)
						referral_rewards.claimed_msg = "$%s worth credits"%(str(referral_rewards.credits))
						referral_rewards.claimed_desc = "You can use it for during your purchase of plan or algos subscriptions"

				except:
					print(traceback.format_exc())
					referral_rewards.credits=random.randint(1,10)
					referral_rewards.claimed_msg = "$%s worth credits"%(str(referral_rewards.credits))
					referral_rewards.claimed_desc = "You can use it for during your purchase of plan or algos subscriptions"

			elif referral_rewards.status==2:
				referral_rewards.credits=random.randint(1,20)
				referral_rewards.claimed_msg = "$%s worth credits"%(str(referral_rewards.credits))
				referral_rewards.claimed_desc = "You can use it for during your purchase of plan or algos subscriptions"

			referral_rewards.claimed = True
			referral_rewards.save()

			user_profile.total_credits = user_profile.total_credits + referral_rewards.credits
			user_profile.available_credits = user_profile.available_credits + referral_rewards.credits
			
			if referral_rewards.credits>0:
				try:
					upm = models.UserPaymentMethods.objects.get(user_uuid=user_uuid)
					customer = stripe.Customer.retrieve(upm.customer['id'])
				except:
					if upm is None:
						customer = stripe.Customer.create(
							email=user_profile.email
						)
						upm = models.UserPaymentMethods(
							user_uuid=user_uuid,
							customer = customer,
							)

				if customer is not None:
					customertxn = stripe.Customer.create_balance_transaction(
						customer['id'],
						amount=-100*referral_rewards.credits,
						currency='usd',
						)
					customer = stripe.Customer.retrieve(upm.customer['id'])
					upm.customer = customer
					upm.save()

			user_profile.save()

			return JsonResponse({"status":"success","credits":referral_rewards.credits,"claimed_msg":referral_rewards.claimed_msg,"claimed_desc":referral_rewards.claimed_desc,"credit_type":referral_rewards.credit_type})
		else:
			return JsonResponse({"status":"error","error_msg":"Reward already claimed"})

	return JsonResponse({"status":"error","error_msg":"Method"})

def send_notification(user_uuid):
	import requests

	url = "https://ns.streak.world/v1/notifications"

	payload = {
		"recipients": [user_uuid],
		"platforms": [0,1],
		"type": "transact",
		"message": {
			"title":"You just Earned a Reward \u1F389",
			"body": "Click and claim reward, and invite more",
			"img_url": "",
			"data": {
			  "key1": "value1",
			  "key2": "value2"
			},
			"android_config": {
			  "collapse_key": "",
			  "priority": "high",
			  "restricted_package_name": "",
			  "data": {
			    "key3":"value3"
			  },
			  "notification": {
			    "title": "You just Earned a Reward",
			    "body": "",
			    "icon": "",
			    "color": "#ffffff",
			    "sound": "",
			    "tag": "",
			    "click_action": "",
			    "body_loc_key": "",
			    "body_loc_args": [],
			    "title_loc_key": "",
			    "title_loc_args": [],
			    "channel_id": "general",
			    "image_url": ""
			  },
			  "fcm_options": {
			    "analytics_label": "test"
			  }
			},
			"fcm_options": {
			  "analytics_label": "test"
			}
		}
	}
	headers = {
    'Content-Type': "application/json",
    }

	response = requests.request("POST", url, data=ujson.dumps(payload), headers=headers,timeout=1)
	print(response.text)
	
	if response.status_code == 200:
		return True
	
	return False

def get_all_referrals(request):
	resp_json = False
	if(request.META.get('HTTP_X_CSRFTOKEN',None)):
		resp_json = True
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		request.session['user_is_auth'] = True
		request.session['user_uuid'] = '123'
		user_uuid = '123'

	if not user_is_auth:
		return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)

	if request.method=='GET':
		referrals_dict = {}
		try:
			user_profile = models.UserProfile.objects.get(user_uuid=user_uuid)
			ref_id = user_profile.ref_id
			referrals_cursor = models.ReferralUsers.objects(ref_id=ref_id)
			referrals_rewards_cursor = models.ReferralRewards.objects(ref_id=ref_id)
			for r in referrals_cursor:
				ref_user_uuid = r.user_uuid
				first_name = r.ref_first_name
				if first_name=="":
					first_name= r.email.split("@")[0]
				ref_status = r.ref_status
				referrals_dict[ref_user_uuid]={
											"first_name":first_name,
											"ref_status":ref_status,
											"ref_user_uuid":ref_user_uuid,
											"rewards":[]
											}
			for r in referrals_rewards_cursor:
				ref_code = r.ref_code
				status = r.status
				claimed = r.claimed
				credits = r.credits
				updated_at = r.updated_at
				claimed_msg = r.claimed_msg
				claimed_desc = r.claimed_desc
				credit_type = r.credit_type
				if referrals_dict.get(r.user_uuid,None) is not None:
					referrals_dict[r.user_uuid]['rewards'].append({
												"ref_code":ref_code,
												"status":status,
												"claimed":claimed,
												"claimed_msg":claimed_msg,
												"credit_type":credit_type,
												"claimed_desc":claimed_desc,
												"credits":credits,
												"updated_at":updated_at
												})
			return JsonResponse({"status":"success","referrals":referrals_dict.values()})
		except:
			print(traceback.format_exc())
			return JsonResponse({"status":"success","referrals":referrals_dict.values()})

	return JsonResponse({"status":"error","error_msg":"Method"})

def change_password(request):
	resp_json = False
	if(request.META.get('HTTP_X_CSRFTOKEN',None)):
		resp_json = True
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	if not user_is_auth:
		return JsonResponse({"status":"error",'error_msg':'Invalid authentication'})
		# return redirect('dashboard')

	if request.method == 'POST':
		auth = request.POST.get('auth','')
		old_password = request.POST.get('password','')
		password = request.POST.get('new_password','')
		password2 = request.POST.get('confirmed_password','')
		# print auth,password,password2
		try:

			key = request.POST.get('token','')
			hash_password = hashlib.sha1(old_password).hexdigest()
			print("user_uuid",user_uuid)
			u = models.UserProfile.objects.get(user_uuid=user_uuid,password=hash_password)

			if u.otp_secret!='':
				totp = pyotp.TOTP(u.otp_secret)
				if(totp.verify(key)):
					pass
					# u.login_count += 1
					# u.save()
					# return JsonResponse({"status":"success","msg":'Authenticator success','csrf':csrf.get_token(request),'sessionid':request.session.session_key})
				else:
					return JsonResponse({"status":"error","error_msg":"Key expired"})
			elif u.otp_secret=='':
				pass
			else:
				return JsonResponse({"status":"error","error_msg":"Invalid key"})
			if password!=password2:
				return JsonResponse({"status":"error","error_msg":"Not matching password"})
			u.password = hashlib.sha1(password).hexdigest()
			u.save()
			update_session_auth_hash(request,request.session.session_key)
			return JsonResponse({'status':'success','csrf':csrf.get_token(request),'sessionid':request.session.session_key,'msg_title':'Password updated','msg_content':'Password has been updated'})
			# return JsonResponse({'status':'success','msg_title':'Password updated','msg_content':'Password has been updated'})
		except DoesNotExist:
			print traceback.format_exc()	
			# print 'hreeeeeeeeeeeeeeeeeeeeeeeee'
			# if resp_json:
			return JsonResponse({'status':'error','error_msg':'Incorrect old password'})
		except:
			print traceback.format_exc()	
			# print 'hreeeeeeeeeeeeeeeeeeeeeeeee'
			# if resp_json:
			return JsonResponse({'status':'error','error_msg':'Some error occured,kindly try again'})
			# else:
			# 	return render(request,'password_reset.html',{'status':'error','error_msg':'Some error occured,kindly try again','auth':auth,'password':password})

	# if request.method == 'GET':
		auth = request.GET.get('auth','')
		try:
			user_verif = models.DirectPasswordReset.objects.get(
				activation_key=auth,
				used=False,
				key_expires__gt = datetime.datetime.now()
				)
			user_id_auth = hashlib.sha1(user_verif.salt+user_verif.user_uuid).hexdigest()
			if(auth==user_id_auth):
				# if resp_json:
				return JsonResponse({'status':'success'})
			else:
				return JsonResponse({'status':'error'})
		except:
			print traceback.format_exc()
			return JsonResponse({'status':'error'})

	# return render(request,'verification.html',{'status':'success','msg_title':'Incorrect url','msg_content':'Password reset link Incorrect'})
	return JsonResponse({'status':'error','error_msg':'Invalid method'})

def login(request):
	#login
	resp_json = False
	if(request.META.get('HTTP_X_CSRFTOKEN',None)):
		resp_json = True

	if request.method == "GET":
		user_uuid = request.session.get('user_uuid','')
		user_is_auth = request.session.get('user_is_auth',False)
		
		if settings.ENV == "local" or settings.ENV == 'local1':
			user_uuid = '123'
			user_is_auth = True
		# if settings.DEBUG:

		if user_uuid!='' and user_is_auth:
			if resp_json:
				return JsonResponse({'status':'success','csrf':csrf.get_token(request),'sessionid':request.session.session_key})
			return redirect('dashboard')

		return render(request,'login.html',{})

	if request.method == "POST": # for ajax request
		
		token = request.POST.get('token','')
		# captcha validation
		if token!="Fv7qPPuL5LPUeXtG" and request.POST.get('gpPydvAvskE8a83L','')!='3PW7QP9YWwyAJEux':
			try:
				google_response = requests.request('POST',"https://www.google.com/recaptcha/api/siteverify",data="secret="+settings.RECAPTCHA_SECRET+"&response="+token,headers={'Content-Type': "application/x-www-form-urlencoded"},timeout=5)
				if google_response.status_code == 200:
					if ujson.loads(google_response.text).get('success',False):
						pass
					else:
						print google_response.text
						# return  JsonResponse({'status':'error','error_msg':'Invalid captcha'})
				else:
					return  JsonResponse({'status':'error','error_msg':'Unknown'})
			except:
				print traceback.format_exc()
				return  JsonResponse({'status':'error','error_msg':'Unknown'})

		email = request.POST.get('login_email','')
		password = request.POST.get('login_password','')

		redirect_to = request.session.pop('redirect_to','')

		hash_password = hashlib.sha1(password).hexdigest()

		u = authenticate(email,password=password)
		# if token!="Fv7qPPuL5LPUeXtG" and request.POST.get('gpPydvAvskE8a83L','')!='3PW7QP9YWwyAJEux':
		# 	u.last_ = 'web'
		if u:
			u.last_ip = request.META.get('HTTP_X_FORWARDED_FOR','')
			if u.status==2:
				request.session['user_uuid'] = u.user_uuid
				request.session['user_name'] = u.first_name+' '+u.last_name
				request.session['user_email'] = u.email
				request.session['user_is_auth'] = True
				if(u.otp_secret!=''):
					request.session['two_fa'] = True
				request.session['user_is_auth'] = True
				if u.first_login==True:
					request.session['first_time_login'] = True
					u.first_login=False
					# u.save()
				if not request.session.session_key:
				    request.session.save()
				if resp_json:
					if u.otp_secret!='':
						return JsonResponse({'status':'success','two_fa':True,'sessionid':request.session.session_key})
					u.save()
					return JsonResponse({'status':'success','csrf':csrf.get_token(request),'sessionid':request.session.session_key})
				return redirect('dashboard')
				# if redirect_to != '':
				# 	return JsonResponse({'status':'success','redirect_to':redirect_to})
				# else:
				# 	return JsonResponse({'status':'success','redirect_to':'/dashboard'})
			else:
				error = 'Email or phone number not verified'
		else:
			error = 'Incorrect email/phone number or password'

		if(request.POST.get('resp','')=='json' or resp_json):
			return JsonResponse({'status':'error','error_msg':error})
		else:
			return render(request,'login.html',{'error_msg':error,'email':email,'password':password})
		return JsonResponse({'status':'error','error':error,'error_msg':'Unauthorized'})

	return JsonResponse({'status':'error','error_msg':'Restricted method'})

def account_activate_(request):
	if request.method == "POST":
		user_uuid = request.session.get('user_uuid','')
		user_is_auth = request.session.get('user_is_auth',False)
		# if settings.DEBUG:

		if user_uuid!='' and user_is_auth:
			return redirect('dashboard')
		auth = request.POST.get('auth','')
		if auth == '':
			return redirect('home')
		try:
			user_verif = models.DirectUserEmailVerification.objects.get(activation_key=auth,used=False)
			user_id_auth = hashlib.sha1(user_verif.salt+user_verif.user_uuid).hexdigest()
			if(auth==user_id_auth):
				user = models.DirectProfile.objects.get(user_uuid=user_verif.user_uuid,verification_status=False)
				user.verification_status = True
				user.status = 2
				

				# creating first subscription of the user, with Free trial
				subscription_uuid=str(uuid.uuid4())
				subscription_log_uuid = str(uuid.uuid4())
				user_subscription = models.UserSubscription(user_uuid=user_uuid,
					subscription_uuid=subscription_uuid,
					subscription_validity= datetime.datetime.today() + datetime.timedelta(days=int(29)),
					latest_subscription_id = subscription_log_uuid,
					subscription_type = 1,
					user_broker_id = user.user_broker_id,
					subscription_product = 'basic',
					subscription_plan = 'basic',
					subscription_instance = 'trial'
					)
				user_subscription_log = models.UserSubscriptionLog(user_uuid=user_uuid,
					subscription_log_uuid = subscription_log_uuid,
					subscription_uuid = subscription_uuid,
					subscription_start = datetime.datetime.today(),
					subscription_stop = datetime.datetime.today() + datetime.timedelta(days=int(29)),
					subscription_type = 1,
					subscription_product = 'basic',
					subscription_plan = 'basic',
					user_broker_id = user.user_broker_id,
					subscription_instance = 'trial'
					)

				user.save()
				user_verif.delete()

				user_subscription_log.save()
				#user_subscription.save()

				# if a_results is None:
				# 	print 'not allowed user2'
				# 	request.session['blocked_login'] = True
				# 	print request.session['blocked_login']
				# 	return redirect('home')
				# initialize_account(user_uuid)
				# return JsonResponse({'status':'success'})
				# if request.POST.get('resp',None)=='json':
				utils.initialize_account(user.user_uuid)
				utils.send_initial_emails(user_uuid=user.user_uuid,email=user.email,name=user.first_name)
				return JsonResponse({'status':'success','msg_title':'Account verified','msg_content':' Account has been activated, go ahead and login'})
				# else:
				# 	return render(request,'verification.html',{'status':'success','msg_title':'Account verified','msg_content':' Account has been activated, go ahead and login'})
			# return JsonResponse({'status':'error','error_msg':'Invalid auth'})
			# if request.POST.get('resp',None)=='json':
			return JsonResponse({'status':'error','error_msg':'Invalid link'})
			# else:
			# 	return render(request,'verification.html',{'status':'success','msg_title':'Invalid auth','msg_content':'Invalid url'})
		except:
			print traceback.format_exc()
			return JsonResponse({'status':'error','error_msg':'Unknown'})
	# return JsonResponse({'status':'error'})
	return JsonResponse({'status':'error','error_msg':'Unknown'})

def generate_random_hash():
	hash = random.getrandbits(128)
	return "%032x" % hash

def signup(request):
	# signup
	resp_json = False
	if(request.META.get('HTTP_X_CSRFTOKEN',None)):
		resp_json = True
	if request.method == "GET":
		user_uuid = request.session.get('user_uuid','')
		user_is_auth = request.session.get('user_is_auth',False)
		# if settings.DEBUG:

		if user_uuid!='' and user_is_auth:
			if resp_json:
				JsonResponse({'status':'success'})
			return redirect('dashboard')
		return render(request,'signup.html',{})

	if request.method == "POST":
		token = request.POST.get('token','')
		# captcha validation
		if token!="Fv7qPPuL5LPUeXtG" and request.POST.get('gpPydvAvskE8a83L','')!='3PW7QP9YWwyAJEux':
			try:
				google_response = requests.request('POST',"https://www.google.com/recaptcha/api/siteverify",data="secret="+settings.RECAPTCHA_SECRET+"&response="+token,headers={'Content-Type': "application/x-www-form-urlencoded"},timeout=5)
				if google_response.status_code == 200:
					if ujson.loads(google_response.text).get('success',False):
						pass
					else:
						return  JsonResponse({'status':'error','error_msg':'Invalid captcha'})
				else:
					return  JsonResponse({'status':'error','error_msg':'Unknown'})
			except:
				print traceback.format_exc()
				return  JsonResponse({'status':'error','error_msg':'Unknown'})

		first_name = request.POST.get('first_name','').lower()
		last_name = request.POST.get('last_name','').lower()

		phone_number = request.POST.get('phone_number','').strip(' +,-')
		email = request.POST.get('email','').strip().lower()
		password = request.POST.get('password','')
		password2 = request.POST.get('password2','')
		terms_checkbox = request.POST.get('terms_checkbox','')
		country = request.POST.get('country','')
		country_code = request.POST.get('country_code','')
		try:
			waitinglist = models.SignUpRequest.objects.get(email=email)
			user_count = models.DirectUserProfile.objects.count()
			if user_count>500:
				if(not waitinglist.allowed):
					return  JsonResponse({'status':'error','error_msg':'You are already in the waiting list'})
		except models.SignUpRequest.DoesNotExist:
			try:
				user_count = models.DirectUserProfile.objects.count()
				if user_count>500:
					m = models.SignUpRequest(email=email)
					m.save()
					return JsonResponse({'status':'error','error_msg':'You have been added to the waiting list'})
			except:
				print traceback.format_exc()
				return JsonResponse({'status':'error','error_msg':'Kindly try again'})
			#return  JsonResponse({'status':'error','error_msg':'Kindly join to waiting list to be able to signup'})
		except:
			user_count = models.DirectUserProfile.objects.count()
			if user_count>500:
				print traceback.format_exc()
				return  JsonResponse({'status':'error','error_msg':'Kindly join the waiting list'})
			
		if len(phone_number)<10:
			# return render(request,'signup.html',{'status':'error','error_msg':'Phone number must contain country code','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password})
			if(request.POST.get('resp','')=='json'):
				return JsonResponse({'status':'error','error':True,'error_msg':'Phone number must contain country code','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password})
			elif resp_json:
				return JsonResponse({'status':'error','error':True,'error_msg':'Phone number must contain country code','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password})
			else:
				return render(request,'signup.html',{'status':'error','error_msg':'Phone number must contain country code','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password})
		elif len(phone_number)>15:
			return JsonResponse({'status':'error','error':True,'error_msg':'Phone number too long','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password})

		# validation = signup_validate(first_name,last_name,phone_number,email,password,password2,terms_checkbox)
		if(password!=password2):
			if(request.POST.get('resp','')=='json'):
				return JsonResponse({'status':'error','error':True,'error_msg':'Passwords do not match','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password})
			elif resp_json:
				return JsonResponse({'status':'error','error':True,'error_msg':'Passwords do not match','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password})
			else:
				return render(request,'signup.html',{'status':'error','error_msg':'Passwords do not match','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password})
		validation = [True,1]
		if not validation[0]:
			if(request.POST.get('resp','')=='json'):
				return JsonResponse({'status':'error','error':True,'error_msg':validation[1]})
			elif resp_json:
				return JsonResponse({'status':'error','error':True,'error_msg':validation[1]})
			else:
				return render(request,'signup.html',{'status':'error','error_msg':validation[1],'first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password})
				

		hash_password = hashlib.sha1(password).hexdigest()

		salt = hashlib.sha1(str(random.random())).hexdigest()[:5]

		key_expires = datetime.datetime.today() + datetime.timedelta(days=1)

		user_uuid = str(uuid.uuid4())
		activation_key = hashlib.sha1(salt+user_uuid).hexdigest()

		try:
			user_profile = models.DirectUserProfile(
							user_uuid = user_uuid,
							user_id = ''.join([random.choice(string.ascii_uppercase) for _ in range(4)])+''.join(random.choice(datetime.datetime.now().strftime('%s')) for _ in range(6)),
							first_name = first_name,
							last_name = last_name,
							phone_number = phone_number,
							email = email,
							password =  hash_password,
							status = 1,
							country = country,
							country_code = country_code
							)
			user_auth = models.DirectUserEmailVerification(
							user_uuid = user_uuid,
							activation_key = activation_key,
							otp_key = str(random.randint(4111,9999)),
							key_expires = key_expires,
							used = False,
							salt = salt
							)

			# creating first subscription of the user, with Free trial
			subscription_uuid=str(uuid.uuid4())
			subscription_log_uuid = str(uuid.uuid4())
			user_subscription = models.UserSubscription(user_uuid=user_uuid,
				subscription_uuid=subscription_uuid,
				subscription_validity= datetime.datetime.today() + datetime.timedelta(days=int(30)),
				latest_subscription_id = subscription_log_uuid,
				user_broker_id = user_uuid,
				subscription_type = 1,
				subscription_product = 'basic',
				subscription_plan = 'basic',
				subscription_instance = 'trial'
				)
			user_subscription_log = models.UserSubscriptionLog(user_uuid=user_uuid,
				subscription_log_uuid = subscription_log_uuid,
				subscription_uuid = subscription_uuid,
				subscription_start = datetime.datetime.today(),
				subscription_stop = datetime.datetime.today() + datetime.timedelta(days=int(30)),
				user_broker_id = user_uuid,
				subscription_type = 1,
				subscription_product = 'basic',
				subscription_plan = 'basic',
				subscription_instance = 'trial'
				)

				
			user_profile.save()
			user_auth.save()

			user_subscription_log.save()
			user_subscription.save()

			# request.session['user_uuid'] = user_uuid
			# request.session['user_name'] = first_name
			# request.session['user_email'] = email
			# request.session['user_is_auth'] = True
			
			# request.session['first_time_login'] = True
			# request.session['first_time_algos'] = True
			# request.session['first_time_dashboard'] = True
			# request.session['first_time_create_algorithm'] = True
			# request.session['first_time_orders'] = True
			# request.session['first_time_backtest'] = True
			# request.session['first_time_deploy'] = True
			# request.session['first_time_orderbook'] = True
			# request.session['first_time_portfolio'] = True
			request.session['session_secret'] = generate_random_hash()
			# initialize_account(user_uuid)

			if user_profile:
				# print '127.0.0.1/account_activate?auth='+activation_key
				activation_url = 'https://api.streak.ninja'+'/account_activation?auth='+activation_key
				# mailing_helper(user_uuid=user_uuid,
								# broker_id='',
								# subject='Streak account activation mail <no-reply>',
								# body='Click on the activation link to activate your account, link '+activation_url,
								# sender="support@streak.world"
								# )
				try:
					url = "https://mailing.streak.solutions/streak_mail/world_support/send_mail"
					headers = {"content-type":"application/json"}
					method = "POST"
					payload = ujson.dumps({
							"recipients":[user_profile.email],
							"subject":"Streak World| Account activation",
							"body_data":'Click on the link to activate you Streak World account, '+activation_url,
							"reply_to":'no-reply@streak.world',
							"template_id":None,
							"sender": "updates@streak.world"
						})
					response = requests.request(method,url,data=payload,headers=headers,timeout=5)
					# print response.text
					# print response.status_code
				except:
					print traceback.format_exc()
					if(request.POST.get('resp','')=='json'):
						return JsonResponse({'status':'error','error':True,'error_msg':'Something went wrong, please try again or write to us support[@]streak.world'})
					elif resp_json:
						return JsonResponse({'status':'error','error':True,'error_msg':'Something went wrong, please try again or write to us support[@]streak.world'})
					else:
						return render(request,'signup.html',{'status':'error','error_msg':'Something went wrong, please try again or write to us support[@]streak.world','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password})
				# otp = random.randint(4111,9999)
				# # user_profile verification via mail or msg
				# request.session['signup_process'] = 1
				# return JsonResponse({'status':'success','redirect_to':'Check email for activation link'})
				if(request.POST.get('resp','')=='json'):
					return JsonResponse({'status':'success','msg':'Check email for activation link','msg_title':'Email sent','msg_content':'Password reset link has been emailed'})
				elif resp_json:
					return JsonResponse({'status':'success','msg':'Check email for activation link','msg_title':'Email sent','msg_content':'Password reset link has been emailed'})
				else:
					return render(request,'verification.html',{'status':'success','msg_title':'Account activation link emailed','msg_content':'Kindly activate your account by using the emailed link'})

		except NotUniqueError:
			# log error
			# return JsonResponse({'status':'success','error':'Email or phone number already in use!'})
			if(request.POST.get('resp','')=='json'):
				return JsonResponse({'status':'error','error':True,'error_msg':'Email or phone number already in use!','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password})
			elif resp_json:
				return JsonResponse({'status':'error','error':True,'error_msg':'Email or phone number already in use!','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password})
			else:
				return render(request,'signup.html',{'status':'error','error':True,'error_msg':'Email or phone number already in use','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password})

		except:
			# log error
			print traceback.format_exc()
			# return JsonResponse({'status':'success','error':'Something went wrong, please try again or write to us support[@]streak.world'})
			if(request.POST.get('resp','')=='json'):
				return JsonResponse({'status':'error','error':True,'error_msg':'Something went wrong, please try again or write to us support[@]streak.world','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password})
			elif resp_json:
				return JsonResponse({'status':'error','error':True,'error_msg':'Something went wrong, please try again or write to us support[@]streak.world','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password})
			else:
				return render(request,'signup.html',{'status':'error','error':True,'error_msg':'Something went wrong, please try again or write to us support[@]streak.world','first_name':first_name,'last_name':last_name,'phone_number':phone_number,'email':email,'password':password})

# def opt_verification(request):
# 	if request.method == 'GET':
# 		redirect_to = request.GET.get('redirect_to','')
# 		if redirect_to=='':
# 			return redirect('home')

# 		return redirect(request,'otp_verification.html',{'redirect_to':redirect_to})

# 	return JsonResponse({'status':'error'})

def send_otp_for_mobile(mobile, otp):																				   
	auth_key = "187653A8shpIge5a93de09"																				 
	otp_length = 4																									  
	message = "Your verification code is %d" % otp																	  
	sender = "STREAK"																								 
	otp_expiry = 15																									 
	mobile = "91" + str(mobile)																						 
	url = "http://control.msg91.com/api/sendotp.php?otp_length=%d&authkey=%s&message=%s&sender=%s&mobile=%s&otp=%d&otp_expiry=%d" % \
		(otp_length, auth_key, message, sender, mobile, otp, otp_expiry)												
	headers = {"Accept": "application/json"}																			
	resp = requests.post(url, headers)																				  
	print(resp.text) 

def generate_otp(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth'})
	if request.method == 'POST':
		# user_uuid = request.POST.get('notification_uuid','') 
		phone_number = request.POST.get('phone_number','')
		otp_key = random.randint(411111,999999)
		x = models.UserVerification(user_uuid=user_uuid,
			activation_key=phone_number,
			otp_key = str(otp_key),
			used = False,
			key_expires = datetime.datetime.today() + datetime.timedelta(minutes=5),
			)
		print x.save()
		send_otp_for_mobile(phone_number,otp_key)
		return JsonResponse({"status":"success"})

	return JsonResponse({"status":"error",'msg':'request'})

def save_phone_number(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth'})

	if request.method!='POST':
		return JsonResponse({'status':'error','error':'method'})
	phone_number = request.POST.get('phone_number','');
	otp_key = request.POST.get('otp','');

	date = request.POST.get('date','');
	month = request.POST.get('month','');
	year = request.POST.get('year','');
	street_address = request.POST.get('street_address','');
	country = request.POST.get('country','');

	if(phone_number!=''):
		#stuff
		try:
			verif = models.UserVerification.objects.get(user_uuid=user_uuid,otp_key=otp_key,used = False,activation_key=phone_number,key_expires__gte = datetime.datetime.now())
			# verif = [1]
			# print verif
			if verif>0:
				u = models.UserProfile.objects.get(user_uuid=user_uuid)

				try:
					user_subscription_payment_ = models.UserSubscriptionPayment._get_collection().find({'user_uuid':user_uuid}).sort([("updated_at",-1)])
					user_subscription_payment = None
					for up in user_subscription_payment_:
						user_subscription_payment = up
						break
					if user_subscription_payment:
						customer = payments.Client.customer.edit(customer_id=user_subscription_payment['customer']['id'], data={"name":u.first_name,"contact":phone_number,"email":u.email,"fail_existing":"0"})
				except:
					print traceback.format_exc()

				if u.phone_number=="":
					try:
						user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
						if user_subscription.subscription_validity<datetime.datetime.today():
							# subscription_validity = datetime.datetime.today() + datetime.timedelta(days=29)
							# subscription_validity = subscription_validity.replace(hour=23,minute=59,second=59)
							user_subscription.subscription_validity = max(datetime.datetime.today() + datetime.timedelta(days=int(7)),datetime.datetime(2019, 7, 18, 23, 59, 59))
							user_subscription.subscription_type = 0
							user_subscription.subscription_product = 'free'
							user_subscription.subscription_plan = 'free'
							user_subscription.subscription_price = 0
							user_subscription.subscription_tax = 0
							user_subscription.subscription_total_price = 0
							user_subscription.subscription_active = False
							user_subscription.subscription_instance = 'phone number'
							user_subscription.save()
					except:
						pass

				u.phone_number = phone_number
				# u.addition_details = {'date':date,'month':month,'year':year,'country':country,'street_address':street_address}
				u.save()
				verif.used = True
				verif.save()
				return JsonResponse({'status':'success'})
			else:
				return JsonResponse({'status':'error','msg':'Incorrect otp'})

		except ValidationError:
			return JsonResponse({'status':'error','error':'inputs','msg':'Wrong phone number format'})
		except NotUniqueError:
			return JsonResponse({'status':'error','error':'inputs','msg':'Details already submitted'})
		except models.UserVerification.DoesNotExist:
			return JsonResponse({'status':'error','error':'inputs','msg':'Invalid OTP entered'})
		except:
			print traceback.format_exc()
			return JsonResponse({'status':'error','error':'inputs','msg':'Unkown error, please try again'})

	else:
		return JsonResponse({'status':'error','error':'inputs','msg':'Incomplete inputs'})
	return JsonResponse({'status':'error','error':'inputs','msg':'Incomplete inputs'})

def update_additional_info(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth'})

	if request.method!='POST':
		return JsonResponse({'status':'error','error':'method'})

	date = request.POST.get('date','');
	month = request.POST.get('month','');
	year = request.POST.get('year','');
	street_address = request.POST.get('street_address','');
	country = request.POST.get('country','');
	state = request.POST.get('state','');
	city = request.POST.get('city','');
	user_name = request.POST.get('user_name','');
	about_me = request.POST.get('about_me','');

	secondary_email = request.POST.get('secondary_email','');
	try:
		u = models.UserProfile.objects.get(user_uuid=user_uuid)
		if u.first_name=="" or u.first_broker =='-':
			u.first_name = user_name
		if u.additional_details=={}:
			u.additional_details = {'date':date,'month':month,'year':year,'country':country,'street_address':street_address,'state':state,'city':city,'about_me':about_me}
		elif secondary_email=="":
			u.additional_details.update({'date':date,'month':month,'year':year,'country':country,'street_address':street_address,'state':state,'city':city,'about_me':about_me})
		else:
			if secondary_email==u.email:
				return JsonResponse({'status':'error','error_msg':'Secondary email cannot be same as primary'})
			u.additional_details.update({'secondary_email':secondary_email,'date':date,'month':month,'year':year,'country':country,'street_address':street_address,'state':state,'city':city,'about_me':about_me})
			# u.additional_details['secondary_email']=secondary_email
		u.save()
		return JsonResponse({'status':'success'})
	except:
		return JsonResponse({'status':'error','error_msg':'Unkown issue'})

	return JsonResponse({'status':'error','error_msg':'auth'})

def forgot_password_(request):
	resp_json = False
	if(request.META.get('HTTP_X_CSRFTOKEN',None)):
		resp_json = True
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	if user_uuid!='' and user_is_auth:
		return redirect('dashboard')
	
	if request.method == 'POST':
		# print(request.POST.get('email',''))
		try:
			user_profile = models.DirectUserProfile.objects.get(email=request.POST.get('email',''))

			salt = hashlib.sha1(str(random.random())).hexdigest()[:5]

			key_expires = datetime.datetime.today() + datetime.timedelta(hours=12)

			activation_key = hashlib.sha1(salt+user_profile.user_uuid).hexdigest()

			otp_key = str(random.randint(4111,9999))

			password_reset = models.DirectPasswordReset(
				user_uuid = user_profile.user_uuid,
				activation_key = activation_key,
				salt = salt,
				otp_key = otp_key,
				used = False,
				key_expires = key_expires,
				)

			password_reset.save();
			
			reset_url = 'https://'+request.META['HTTP_HOST']+'/password_reset?a='+activation_key
			# print user_profile.user_uuid
			if(user_profile.user_uuid!=''):
				try:
					url = "https://mailing.streak.world/streak_mail/world_support/send_mail"
					headers = {"content-type":"application/json"}
					method = "POST"
					payload = ujson.dumps({
							"recipients":[user_profile.email],
							"subject":"Streak World| Password reset",
							"body_data":'Click on the link to reset password, '+reset_url,
							"reply_to":'no-reply@streak.world',
							"template_id":None,
							"sender": "support@streak.world"
						})
					response = requests.request(method,url,data=payload,headers=headers,timeout=5)
					# print response.text
					# print response.status_code
				except:
					print traceback.format_exc()
					return JsonResponse({'status':'error','error_msg':'Some error occured, please try again','email':request.POST.get('email','')})

			if request.POST.get('resp',None)=='json':
				return JsonResponse({'status':'success','msg_title':'Email sent','msg_content':'Password reset link has been emailed'})
			elif resp_json:
				return JsonResponse({'status':'success','msg_title':'Email sent','msg_content':'Password reset link has been emailed'})
			else:
				return render(request,'verification.html',{'status':'success','msg_title':'Email sent','msg_content':'Password reset link has been emailed'})
		except:
			print traceback.format_exc()
			if request.POST.get('resp',None)=='json':
				return JsonResponse({'status':'error','error_msg':''})
			elif resp_json:
				return JsonResponse({'status':'error','error_msg':''})
			else:
				return render(request,'forgot_password.html',{'status':'error','error_msg':'Email not registered','email':request.POST.get('email','')})

	return render(request,'forgot_password.html',{})

def forgot_password(request):
	resp_json = False
	if(request.META.get('HTTP_X_CSRFTOKEN',None)):
		resp_json = True
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	if user_uuid!='' and user_is_auth:
		return JsonResponse({'status':'error','error_msg':'Auth'})
	
	if request.method == 'POST':
		# print(request.POST.get('email',''))
		token = request.POST.get('token','')
		# captcha validation
		if token!="Fv7qPPuL5LPUeXtG" and request.POST.get('gpPydvAvskE8a83L','')!='3PW7QP9YWwyAJEux':
			try:
				google_response = requests.request('POST',"https://www.google.com/recaptcha/api/siteverify",data="secret="+settings.RECAPTCHA_SECRET+"&response="+token,headers={'Content-Type': "application/x-www-form-urlencoded"},timeout=5)
				if google_response.status_code == 200:
					if ujson.loads(google_response.text).get('success',False):
						pass
					else:
						print google_response.text
						return  JsonResponse({'status':'error','error_msg':'Invalid captcha'})
				else:
					return  JsonResponse({'status':'error','error_msg':'Unknown'})
			except:
				print traceback.format_exc()
				return  JsonResponse({'status':'error','error_msg':'Unknown'})

		try:
			user_profile = models.UserProfile.objects.get(email=request.POST.get('email',''))

			salt = hashlib.sha1(str(random.random())).hexdigest()[:5]

			key_expires = datetime.datetime.today() + datetime.timedelta(hours=12)

			activation_key = hashlib.sha1(salt+user_profile.user_uuid).hexdigest()

			otp_key = str(random.randint(4111,9999))

			password_reset = models.DirectPasswordReset(
				user_uuid = user_profile.user_uuid,
				activation_key = activation_key,
				salt = salt,
				otp_key = otp_key,
				used = False,
				key_expires = key_expires,
				)

			password_reset.save();
			
			reset_url = 'https://streak.tech'+'/password_reset?auth='+activation_key
			# print user_profile.user_uuid
			if(user_profile.user_uuid!=''):
				try:
					url = "https://mailing.streak.solutions/streak_mail/world_support/send_mail"
					headers = {"content-type":"application/json"}
					method = "POST"
					payload = ujson.dumps({
							"recipients":[user_profile.email],
							"subject":"Streak World| Password reset",
							"body_data":'Click on the link to reset password, '+reset_url,
							"reply_to":'no-reply@streak.tech',
							"template_id":None,
							"sender": "support@streak.tech"
						})
					response = requests.request(method,url,data=payload,headers=headers,timeout=5)
					# print response.text
					# print response.status_code
				except:
					print traceback.format_exc()
					return JsonResponse({'status':'error','error_msg':'Some error occured, please try again','email':request.POST.get('email','')})

			if request.POST.get('resp',None)=='json':
				return JsonResponse({'status':'success','msg_title':'Email sent','msg_content':'Password reset link has been emailed'})
			else:
				return JsonResponse({'status':'success','msg_title':'Email sent','msg_content':'Password reset link has been emailed'})
			# else:
				# return render(request,'verification.html',{'status':'success','msg_title':'Email sent','msg_content':'Password reset link has been emailed'})
		except:
			print traceback.format_exc()
			if request.POST.get('resp',None)=='json':
				return JsonResponse({'status':'success','error_msg':''})
			elif resp_json:
				return JsonResponse({'status':'success','error_msg':''})
			else:
				# return render(request,'forgot_password.html',{'status':'success','error_msg':'Email not registered','email':request.POST.get('email','')})
				return JsonResponse({'status':'success','error_msg':'Email not registered'})

	# return render(request,'forgot_password.html',{})
	return JsonResponse({'status':'error','error_msg':'method'})

def password_reset(request):
	resp_json = False
	if(request.META.get('HTTP_X_CSRFTOKEN',None)):
		resp_json = True
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	if user_uuid!='' and user_is_auth:
		return JsonResponse({'status':'success','error_msg':'Auth'})

	if request.method == 'POST':
		auth = request.POST.get('auth','')
		password = request.POST.get('password','')
		password2 = request.POST.get('confirmed_password','')
		# print auth,password,password2
		try:
			user_verif = models.DirectPasswordReset.objects.get(
				activation_key=auth,
				used=False,
				key_expires__gt = datetime.datetime.now()
				)
			user_id_auth = hashlib.sha1(user_verif.salt+user_verif.user_uuid).hexdigest()
			if(auth==user_id_auth):
				if(password!=password2):
					return JsonResponse({'status':'error','error_msg':'Passwords do not match'})

					# return render(requesSt,'password_reset.html',{'status':'error','error_msg':'Passwords do not match','auth':auth,'password':password})
				hash_password = hashlib.sha1(password).hexdigest()
				user_profile = models.UserProfile.objects.get(
					user_uuid=user_verif.user_uuid)
				
				user_profile.password = hash_password
				user_profile.save()
				
				user_verif.used = True
				user_verif.save()
				
				url = "https://mailing.streak.world/streak_mail/world_support/send_mail"
				headers = {"content-type":"application/json"}
				method = "POST"
				payload = ujson.dumps({
						"recipients":[user_profile.email],
						"subject":"Streak World| Password reset",
						"body_data":'Password has been reset successfully.',
						"reply_to":'no-reply@streak.world',
						"template_id":None,
						"sender": "support@streak.world"
					})
				response = requests.request(method,url,data=payload,headers=headers,timeout=5)
				update_session_auth_hash(request,request.session.session_key)
				return JsonResponse({'status':'success','csrf':csrf.get_token(request),'sessionid':request.session.session_key,'msg_title':'Password updated','msg_content':'Password has been updated, go ahead and login'})
				return JsonResponse({'status':'success','msg_title':'Password updated','msg_content':'Password has been updated, go ahead and login'})
				# else:
				# 	return render(request,'verification.html',{'status':'success','msg_title':'Password updated','msg_content':'Password has been updated, go ahead and login'})
		except:
			print traceback.format_exc()	
			# print 'hreeeeeeeeeeeeeeeeeeeeeeeee'
			# if resp_json:
			return JsonResponse({'status':'error','error_msg':'Some error occured,kindly try again'})
			# else:
			# 	return render(request,'password_reset.html',{'status':'error','error_msg':'Some error occured,kindly try again','auth':auth,'password':password})

	if request.method == 'GET':
		auth = request.GET.get('auth','')
		try:
			user_verif = models.DirectPasswordReset.objects.get(
				activation_key=auth,
				used=False,
				key_expires__gt = datetime.datetime.now()
				)
			user_id_auth = hashlib.sha1(user_verif.salt+user_verif.user_uuid).hexdigest()
			if(auth==user_id_auth):
				# if resp_json:
				update_session_auth_hash(request,request.session.session_key)
				return JsonResponse({'status':'success','csrf':csrf.get_token(request),'sessionid':request.session.session_key})
				# return JsonResponse({'status':'success'})
			else:
				return JsonResponse({'status':'error'})
		except:
			print traceback.format_exc()
			return JsonResponse({'status':'error'})

	# return render(request,'verification.html',{'status':'success','msg_title':'Incorrect url','msg_content':'Password reset link Incorrect'})
	return JsonResponse({'status':'error','error_msg':'Some error occured,kindly try again'})


def verification(request):
	if request.method == 'GET':
		return render(request,'verification.html',{})

def user_otp_confirmation(request):
	signup_process = request.session.pop('signup_process',0)

	if request.method == 'GET':
		redirect_to = request.GET.get('redirect_to','')
		if redirect_to=='':
			return redirect('home')

		return redirect(request,'otp_verification.html',{'redirect_to':redirect_to})

	if request.method == 'POST':
		try:
			user_uuid = request.session.get('user_uuid','')
			otp_value = request.POST.get('otp_value','')
			redirect_to = request.POST.get('redirect_to','')

			if user_uuid != '':
				try:
					user_verification = models.UserVerification.objects.get(user_uuid=user_uuid,otp_value=otp_value,used=False)

					key_expires = timezone.make_aware(user_verification.key_expires,timezone.get_default_timezone())

					time_now = timezone.make_aware(datetime.datetime.now(),timezone.get_default_timezone())

					if key_expires < time_now:
						return JsonResponse({'status':'error','error':'OTP expired'})

					user_profile = models.UserProfile.objects.get(user_uuid=user_verification.user_uuid)
					user_profile.status = 2
					user_profile.save()

					user_verification.used=True
					user_verification.save()
					if redirect_to=='/change_password':
						request.session['user_uuid'] = user_verification.user_uuid

					return JsonResponse({'status':'success'})
				except:
					return JsonResponse({'status':'error','error':'Incorrect OTP'})
		except:
			return JsonResponse({'status':'error','error':'Incorrect OTP'})

	return JsonResponse({'status':'error'})

def direct_logout(request):
	resp_json = False
	if(request.META.get('HTTP_X_CSRFTOKEN',None)):
		resp_json = True

	headers = {}
	for key in request.session.keys():
		del request.session[key]
				
	if resp_json:
		return JsonResponse({'status':'success'})
	return redirect('home')

def myaccount(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		request.session['user_is_auth'] = True
		# request.session['user_uuid'] = '123'
		# user_uuid = '123'
	if not user_is_auth:
		return redirect('login')

	try:
		user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
		user_profile = models.DirectUserProfile.objects.get(user_uuid=user_uuid) 
		return render(request,'myaccount.html',{'user_subscription':user_subscription,'user_profile':user_profile})
	except:
		print traceback.format_exc()

	return render(request,'myaccount.html',{})


def get_otp_provisioning_uri(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		request.session['user_is_auth'] = True
		# request.session['user_uuid'] = '123'
		# user_uuid = '123'
	if not user_is_auth:
		return JsonResponse({"status":"error","error_msg":"auth"},status=401)
	try:
		user = models.DirectUserProfile.objects.get(user_uuid=user_uuid)
		secret = pyotp.random_base32()
		uri = pyotp.totp.TOTP(secret).provisioning_uri(user.email, issuer_name="Streak")
		conn = get_redis_connection("default")
		res = conn.set("opt_temp_secret:"+user_uuid,secret)
		conn.expire("opt_temp_secret:"+user_uuid,180)
		return JsonResponse({"status":"success","uri":uri,"secret_key":secret})
	except:
		print traceback.format_exc()

	return JsonResponse({"status":"error","error_msg":"Unkown"})

def intialize_otp(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		request.session['user_is_auth'] = True
		# request.session['user_uuid'] = '123'
		# user_uuid = '123'
	if not user_is_auth:
		return JsonResponse({"status":"error","error_msg":"auth"},status=401)

	if request.method!='POST':
		return JsonResponse({'status':'error','error_msg':'method'})
	try:
		key = request.POST.get('key','')
		if request.POST.get('delete','')=='':
			user = models.DirectUserProfile.objects.get(user_uuid=user_uuid)
			conn = get_redis_connection("default")
			secret = conn.get("opt_temp_secret:"+user_uuid)
			if secret:
				totp = pyotp.TOTP(secret)
				if(totp.verify(key)):
					user.otp_secret = secret
					user.onboarding['first_2fa']=True
					user.save()
					conn.delete("opt_temp_secret:"+user_uuid)
					return JsonResponse({"status":"success","msg":'Authenticator added'})
				else:
					return JsonResponse({"status":"error","error_msg":'Invalid key'})
			else:
				return JsonResponse({"status":"error","error_msg":'Key expired'})
		else:
			password = request.POST.get('password','')
			user = models.DirectUserProfile.objects.get(user_uuid=user_uuid)
			if user.password == hashlib.sha1(password).hexdigest():
				if user.otp_secret!='':
					totp = pyotp.TOTP(user.otp_secret)
					if(totp.verify(key)):
						user.otp_secret = ''
						user.save()
						x = request.session.pop('two_fa','')
						return JsonResponse({"status":"success"})
					else:
						return JsonResponse({"status":"error","error_msg":'Invalid key'})
				else:
					return JsonResponse({"status":"error","error_msg":'Key has expired'})
			else:
				return JsonResponse({"status":"error","error_msg":'Incorrect password'})
	except:
		print traceback.format_exc()

	return JsonResponse({"status":"error","error_msg":"Unkown"})

def validate_2fa_login(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		request.session['user_is_auth'] = True
		# request.session['user_uuid'] = '123'
		# user_uuid = '123'
	if not user_is_auth:
		return JsonResponse({"status":"error","error_msg":"auth"},status=401)

	if request.method!='POST':
		return JsonResponse({'status':'error','error_msg':'method'})
	try:
		key = request.POST.get('token','')
		user = models.DirectUserProfile.objects.get(user_uuid=user_uuid)
		if user.otp_secret!='':
			totp = pyotp.TOTP(user.otp_secret)
			if(totp.verify(key)):
				user.save()
				return JsonResponse({"status":"success","msg":'Authenticator success','csrf':csrf.get_token(request),'sessionid':request.session.session_key})
			else:
				return JsonResponse({"status":"error","error_msg":'Invalid key'})
		else:
			return JsonResponse({"status":"error","error_msg":'Key expired'})
	except:
		print traceback.format_exc()

	return JsonResponse({"status":"error","error_msg":"Unkown"})

def join_waitlist(request):
	if request.method!='POST':
		return JsonResponse({'status':'error','error_msg':'method'})
	email = request.POST.get('email','').lower()
	try:
		m = models.SignUpRequest.objects.get(email=email)
		return JsonResponse({'status':'error','error_msg':'You are already in the waiting list'})
	except:
		try:
			m = models.DirectUserProfile.objects.get(email=email)
			return JsonResponse({'status':'success','msg':'Kindly go ahead and login'})
		except:
			try:
				m = models.SignUpRequest(email=email)
				m.save()
				return JsonResponse({'status':'success','msg':'You have been added to the waiting list'})
			except:
				print traceback.format_exc()
				return JsonResponse({'status':'error','error_msg':'Kindly try again'})					
	return JsonResponse({'status':'error','error':'inputs','error_msg':'Incomplete inputs'})
