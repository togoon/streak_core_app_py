from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import redirect,render
from django.middleware import csrf
from django_redis import get_redis_connection
from django.utils.http import is_safe_url
import pickle
import itertools
import ujson
import json,csv
import urllib
from coreapp import models
import hashlib
import requests
import traceback
import uuid
import datetime
import random
import base64
from mongoengine import DoesNotExist
from mongoengine import ValidationError,NotUniqueError
import os
#import kiteconnect
from django.middleware import csrf

import os
import time
import payments
import razorpay
import userflow
from coreapp.views import userflow
import utility as utils 
from django.contrib.auth import update_session_auth_hash

def get_deployment_keys(query): 
	# query = {"user_uuid":user_uuid,"status":0} 
	depl_algo_list = [] 
	depl_algo_cur = models.DeployedAlgorithm._get_collection().find(query) 
	# depl_algo_id_dict = {} 
	for d in depl_algo_cur: 
		x = "deployed:" + d['user_uuid'] + ":" + d['algo_uuid'] + ":" + d["segment"] + "_" + d["symbol"] + ":" + d["algo_obj"]["time_frame"] + ":" + d["deployment_uuid"] 
		depl_algo_list.append(x) 
		# depl_algo_dict[d["algo_uuid"]+d["segment_symbol"]]=d["status"] 
		# depl_algo_id_dict[d["algo_uuid"]]=depl_algo_id_dict.get(d["algo_uuid"],0)+1 
	return depl_algo_list 

def override_with_ams(func):
	def inner(request):
		BROKER = request.session.get("broker","zerodha")
		# print "broker",BROKER
		print("*******Using AMS override*******",BROKER)
		if BROKER in ["ab","5paisa"]:
			print("*******Using AMS Function*******",BROKER)
			# return func(request)
			func_name = func.__name__
			if func_name == "fetch_positions":
				return ams_fetch_positions(request)
			elif func_name == "fetch_holdings":
				return ams_fetch_holdings(request)
			elif func_name == "fetch_order_book":
				return ams_fetch_order_book(request)
			elif func_name == "place_order_discipline":
				return ams_place_order_discipline(request)
			elif func_name == "place_order_tpsl_new":
				return ams_place_order_tpsl_new(request)
			elif func_name == "place_order_direct":
				return ams_place_order_direct(request)
			elif func_name == "place_order_new":
				return ams_place_order_new(request)
			elif func_name == "fetch_dashboard_funds":
				return ams_fetch_dashboard_funds(request)
			elif func_name == "exit_all":
				return ams_exit_all(request)
			elif func_name == "cancel_order_click":
				return ams_cancel_order_click(request)
			elif func_name == "exit_position_now_force_stop":
				return ams_exit_position_now_force_stop(request)
			elif func_name == "fetch_open_positions":
				return ams_fetch_open_positions(request)
			elif func_name == "fetch_specific_position":
				return ams_fetch_specific_position(request)
			elif func_name == "whats_new3":
				return ab_whats_new3(request)
		else:
			return func(request)
	return inner

AMS_ROOT_URL = "http://3.6.90.57:8085"
version = "v1"
base_header = {
	    'Content-Type': "application/json"
	    }
strategy_code = 'Test'

def reponse_handler(response):
	if response.status_code == 200 or response.status_code == 201:
		try:
			return (True,ujson.loads(response.text),200)
		except:
			print(traceback.format_exc())
			return (False,{},response.status_code)
	else:
		try:
			return (False,ujson.loads(response.text),response.status_code)
		except:
			print(traceback.format_exc())
			return (False,{"message":"Server reponse error, please try again"},response.status_code)


def fetch_user_details(user_uuid,service):
	url = AMS_ROOT_URL + "/"+ version+ "/users/details"
	payload = ujson.dumps({"user_uuid":user_uuid ,"service":service})

	headers = base_header
	response = requests.request("POST", url, data=payload, headers=headers,timeout=2)
	success,resp_json,status_code = reponse_handler(response)
	# print("fetch_user_details",resp_json)
	if success:
		return resp_json["data"]
	else:
		print("error fetching user detials",resp_json)
		return None

def validate_session(auth_token,service):
	url =  AMS_ROOT_URL + "/"+ version+ "/users/sso-login"
	profile = None
	error_msg = None
	if auth_token=="":
		return  None,"Invalid token received"
	if service =="5paisa":
		credentials = {"params_map":{"cookie":auth_token}}
		payload = ujson.dumps({"user_uuid":"" ,"service":service,"async_validate":False,"credentials": credentials})
		headers = base_header
		response = requests.request("POST", url, data=payload, headers=headers,timeout=2)
		success,resp_json,status_code = reponse_handler(response)
		if success:
			username = resp_json.get("client_code","")

			if "@" not in username:
				user_broker_id = username
			else:
				user_broker_id = ""
			profile = resp_json.get("data",{}).get("body",{}).get("EquityProfile",[])
			if len(profile)>0:
				profile = profile[0]
			else:
				return  None,"Invalid session credentials, please try again"
			profile["broker_id"] = username
		elif status_code == 403:
			return  None,"Invalid credentials, 3 wrong retires will block you account, so check your credentials properly"
	return profile,error_msg

def register_user_with_ams(user_uuid,service,user_broker_id,auth_token):
	url = AMS_ROOT_URL + "/"+ version+ "/users/token"
	profile = None
	error_msg = None
	if auth_token=="":
		return  None,"Invalid token received"
	if service =="5paisa":
		headers = base_header
		credentials = {"username":user_broker_id,"params_map":{"token":user_broker_id}}
		payload = ujson.dumps({"user_uuid":user_uuid ,"service":service,"async_validate":False,"credentials": credentials})
		response = requests.request("POST", url, data=payload, headers=headers,timeout=11)
		success,resp_json,status_code = reponse_handler(response)
		print "RESGISTERING NEW USER WITH AMS->",payload,resp_json
		if success:
			username = resp_json.get("client_code","")

			if "@" not in username:
				user_broker_id = username
			else:
				user_broker_id = ""
			profile = resp_json.get("data",{}).get("body",{}).get("EquityProfile",[])
			if len(profile)>0:
				profile = profile[0]
			else:
				return  None,"Invalid session credentials, please try again"
			profile["broker_id"] = username
		elif status_code == 403:
			return  None,"Invalid credentials, 3 wrong retires will block you account, so check your credentials properly"
	return profile,error_msg

def ams_login(request):
	url = AMS_ROOT_URL + "/"+ version+ "/users"

	# payload = "{\n\t \"user_uuid\": \"4ef7f521-6c7b-476e-bc0f-fb4a1323b1e1\",\n\t \"exchange\": \"coinbasepro\",\n\t \"account_name\": \"primary coinbase\",\n\t \"credentials\": {\n           \"api_key\": \"1799372bad7b0825929aa1bbd94f3a74\",\n\t\t           \"api_secret\": \"FnxauMJnagC9Pip78eqJb0eze/3SougKsGsYWGlJaUZASTRXoVzl+2MeGsgDXRnLcM9UaWDUB8ESJInuArnBsA==\",\n\t\t           \"api_passphrase\": \"j4oic6fpdog\"\n\t\t           }\n\t}\n"
	# payload = ujson.dumps({"user_uuid": user_uuid,"exchange":exchange,"account_name": account_name,"credentials": credentials})
	if request.method == 'POST':
		username = request.POST.get("username","").strip().upper()
		broker = request.POST.get("broker","").lower()
		password = request.POST.get("password","")
		dob = request.POST.get("dob","")
		service = request.POST.get("service","zerodha").lower()

		if username == "" or password == "":
			return JsonResponse({"status":"error","error_msg":"Invalid credentials"})

		credentials = {"username":username,"password":password,"params_map":{"DOB":dob}}
		if "@" not in username:
			user_broker_id = username
		else:
			user_broker_id = ""

		user = None
		user_status = 100
		try: 
			user = models.UserProfile.objects.get(user_broker_id=username)

			adding_broker = request.POST.get('adding_broker','')
			if (adding_broker=="true" or adding_broker==True):
				return JsonResponse({"status":"error","error_msg":"Broker account already exists, please log in directly"})

			user_uuid = user.user_uuid
			if user.email == username+"@"+service and user.additional_details.get("secondary_email","")=="":
				user_status = 100
			user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
			userflow.add_session_log(request)
			userflow.update_activity(request,"login")
			if user_subscription.subscription_instance == 'dual':
				user_subscription.subscription_instance = 'dual_trial'
				user_subscription.subscription_validity= max(datetime.datetime.today() + datetime.timedelta(days=int(7)),datetime.datetime(2021, 1, 31, 23, 59, 59))
				user_subscription.subscription_type = 0
				user_subscription.subscription_product = 'free'
				user_subscription.subscription_plan = 'free'
				user_subscription.subscription_price = 0
				user_subscription.subscription_tax = 0
				user_subscription.subscription_total_price = 0
				user_subscription.save()
				request.session['first_time_login_for_plan'] = True
				request.session['first_time_login'] = True

			partner_ref = request.session.pop('partner_ref','')
			partner_ref_ip = request.session.pop('partner_ref_ip','')
			if(partner_ref!='' and partner_ref_ip==request.META.get('HTTP_X_FORWARDED_FOR','')):
				map_user = {
							"user_broker_id": user.user_broker_id,
							"service":service,
							"new_user": False,
							"referral_code": partner_ref,
							"partner_ref_ip":partner_ref_ip
							}
				con = get_redis_connection('default')
				con.publish('partner_ref',ujson.dumps(map_user))
		except DoesNotExist:
			user_uuid = str(uuid.uuid4())
		
		payload = ujson.dumps({"user_uuid":user_uuid ,"service":service,"async_validate":False,"credentials": credentials})

		headers = base_header
		response = requests.request("POST", url, data=payload, headers=headers,timeout=11)
		success,resp_json,status_code = reponse_handler(response)
		print resp_json
		if success:
			user_uuid_original = request.POST.get('user_uuid','')
			adding_broker = request.POST.get('adding_broker','')
			if user_uuid_original!="" and (adding_broker=="true" or adding_broker==True):
				user_uuid = user_uuid_original
				user = models.UserProfile.objects.get(user_uuid=user_uuid_original)
				user.user_broker_id = user_broker_id
				# user.first_name = session_data['data']['user_name']
				user.first_broker = service
				# if user.email!=session_data['data']['email'].lower():
					# user_profile.additional_details["secondary_email"] = session_data['data']['email'].lower()
				# broker_session = models.BrokerSession.objects(user_broker_id=user_broker_id).modify(upsert=True,
				# set__user_broker_id=user_broker_id,
				# set__access_token=access_token, 
				# set__public_token=public_token,
				# set__user_uuid=user_uuid)
				# user.save()
				v_pref = 3
				user_details = fetch_user_details(user_uuid,service)
				if user_details:
					user.first_name = user_details.get("user_name",username).title()
					if user_details.get("user_email_id",None) is not None:
						if user_details.get("user_email_id","").lower()!= user.email:
							user.additional_details["secondary_email"] = user_details.get("user_email_id","").lower()
				try:
					user.save()
				except:
					return JsonResponse({"status":"error",'error_msg':"Error adding broker acocunt to the email, please contact support[@]streak.tech"})
					# user.email = username+"@"+service
				user_status = 100
				update_session_auth_hash(request,request.session.session_key)
				request.session["broker"]=service
				request.session["full_broker_name"]=broker
				request.session["broker_full_name"]=service
				request.session["user_broker_id"]=username
				request.session['user_uuid'] = user_uuid
				request.session['user_email'] = user.email.lower()
				request.session['user_is_auth'] = True
				request.session['terms_accepted'] = False
				# print "request.session['terms_accepted']",request.session['terms_accepted']
				request.session['first_time_login'] = True
				request.session['first_time_login_for_plan']=True
				request.session['first_time_algos'] = True
				request.session['first_time_dashboard'] = True
				request.session['first_time_create_algorithm'] = True
				request.session['first_time_orders'] = True
				request.session['first_time_backtest'] = True
				request.session['first_time_deploy'] = True
				request.session['first_time_orderbook'] = True
				request.session['first_time_portfolio'] = True
				request.session['session_secret'] = utils.generate_random_hash()
				return JsonResponse({"status":"success",'csrf':csrf.get_token(request),'sessionid':request.session.session_key,"version":v_pref})
			request.session["broker"]=service
			request.session["full_broker_name"]=broker
			request.session["broker_full_name"]=service
			request.session["user_broker_id"]=username
			if user is None:
				user = models.UserProfile(user_uuid=user_uuid,
										email = username+"@"+service,
										user_broker_id = username,
										first_name = '',
										last_name = '',
										phone_number = '',
										password =  '',
										status = 1)
				user.user_broker_id = username
				user.first_broker = service

				user_details = fetch_user_details(user_uuid,service)
				if user_details:
					user.first_name = user_details.get("user_name",username).title()
					if user_details.get("user_email_id",None) is not None:
						user.email = user_details.get("user_email_id",username+"@"+service).lower()
						utils.send_initial_emails(user_uuid=user_uuid,email=user_details.get("user_email_id",username+"@"+service).lower(),name=user.first_name)
				try:
					user.save()
				except NotUniqueError:
					user.email = username+"@"+service
					user.additional_details["secondary_email"] = user_details.get("user_email_id","").lower()
					user.save()
				user_status = 100

				subscription_validity = max(datetime.datetime.today() + datetime.timedelta(days=int(7)),datetime.datetime(2021, 4, 30, 23, 59, 59))
				if service=="5paisa":
					subscription_validity = max(datetime.datetime.today() + datetime.timedelta(days=int(7)),datetime.datetime(2021, 6, 30, 23, 59, 59))
				subscription_uuid=str(uuid.uuid4())
				subscription_log_uuid = str(uuid.uuid4())
				user_subscription = models.UserSubscription(user_uuid=user_uuid,
					subscription_uuid=subscription_uuid,
					subscription_validity= subscription_validity,
					latest_subscription_id = subscription_log_uuid,
					user_broker_id = user.user_broker_id,
					subscription_instance = 'trial'
					)
				user.save()

				user_subscription_log = models.UserSubscriptionLog(user_uuid=user_uuid,
					subscription_log_uuid = subscription_log_uuid,
					subscription_uuid = subscription_uuid,
					subscription_start = datetime.datetime.today(),
					subscription_stop = subscription_validity,
					user_broker_id = user.user_broker_id,
					subscription_instance = 'trial'
					)

				user_subscription_log.save()
				user_subscription.save()

				request.session['user_uuid'] = user_uuid
				request.session['user_name'] = username
				request.session['user_email'] = user_details.get("user_email_id","").lower()
				request.session['user_is_auth'] = True
				request.session['terms_accepted'] = False
				# print "request.session['terms_accepted']",request.session['terms_accepted']
				request.session['first_time_login'] = True
				request.session['first_time_login_for_plan']=True
				request.session['first_time_algos'] = True
				request.session['first_time_dashboard'] = True
				request.session['first_time_create_algorithm'] = True
				request.session['first_time_orders'] = True
				request.session['first_time_backtest'] = True
				request.session['first_time_deploy'] = True
				request.session['first_time_orderbook'] = True
				request.session['first_time_portfolio'] = True
				request.session['session_secret'] = utils.generate_random_hash()
				# initialize_account(user_uuid)
				partner_ref = request.session.pop('partner_ref','')
				partner_ref_ip = request.session.pop('partner_ref_ip','')
				userflow.add_session_log(request)
				userflow.update_activity(request,"login")
				if(partner_ref!='' and partner_ref_ip==request.META.get('HTTP_X_FORWARDED_FOR','')):
					map_user = {
								"user_broker_id": user.user_broker_id,
								"service":service,
								"new_user": True,
								"referral_code": partner_ref,
								"partner_ref_ip":partner_ref_ip
								}
					con = get_redis_connection('default')
					con.publish('partner_ref',ujson.dumps(map_user))


			if user is not None:
				request.session['user_uuid'] = user.user_uuid
				request.session['user_name'] = user.first_name
				request.session['user_email'] = user.additional_details.get("secondary_email","")
				request.session['terms_accepted'] = user.terms_accepted

				if (user.phone_number==''):
					request.session['show_phone_popup'] = True

				request.session['user_is_auth'] = True
				request.session['user_status'] = user_status

				if not request.session.session_key:
					request.session.save()
				utils.update_usage_util(user_uuid,'',clear=False)

				mobile_web = False
				v_pref = 1
				
				try:
					if any(word in request.META['HTTP_USER_AGENT'] for word in ["Android","webOS","iPhone","iPad","iPod","BlackBerry","IEMobile","Opera Mini"]):
						mobile_web = True
						v_pref = 1

					if not mobile_web:
						conn = get_redis_connection('default')
						q = conn.get('user_version_pref'+user_uuid)
						if q is None:
							v_pref = 1
							if request.session.get('first_time_login',False)==True:
								v_pref=3
						else:
							try:
								v_pref = int(q)
							except:
								v_pref = 3
				except:
					pass
				return JsonResponse({'status':'success','user_status':user_status,'csrf':csrf.get_token(request),'sessionid':request.session.session_key,"version":v_pref})	
		elif status_code == 403:
				return  JsonResponse({'status':'error','error_msg':'Invalid credentials, 3 wrong retires will block you account, so check your credentials properly'})
		else:
			if resp_json.get("message")=="some error occurred with service" and service=="ab":
				resp_json["message"]= "Some error occurred with service, probably try login after resetting password on brokers trading terminal"
			elif resp_json.get("message")=='username/password for the given service is not valid' or 'service' in resp_json.get("message") and service=="ab":
				con = get_redis_connection('default')
				ab = con.get("ab_login_issue")
				if ab is None:
					date = datetime.datetime.now()
					ab = {"ids":[username],"date_created":date}
					con.set("ab_login_issue",ujson.dumps(ab))
				else:
					try:
						ab = ujson.loads(ab)
						if username not in ab['ids']:
							ab['ids'].append(username)
						con.set("ab_login_issue",ujson.dumps(ab))
					except:
						date = datetime.datetime.now()
						ab = {"ids":[username],"date_created":date}
						con.set("ab_login_issue",ujson.dumps(ab))
				if datetime.datetime.now().weekday()+1>=5:
					resp_json["message"]= "User ID not enabled by broking for Streak, we have a raised a request to enable it, please check back in a week"
				else:
					resp_json["message"]= "User ID not enabled by broker for Streak, we have a raised a request to enable it, please check back on a Monday"
			return JsonResponse({'status':'error','error_msg':resp_json.get("message",'Unknow error occured, please try again in sometime')})
	else:
		return JsonResponse({"status":"error","error_msg":"Invalid method"})

def ams_generic_sso(request):
	url =  AMS_ROOT_URL + "/"+ version+ "/users/sso-login"
	if request.method == 'GET':
		fivepaisacookie = request.COOKIES.get('5paisacookie',"") 
		JwtToken = request.COOKIES.get('JwtToken',"") 
		extraParams = ""
		print("h->>>>",JwtToken,fivepaisacookie)
		if JwtToken!="" and fivepaisacookie!="":
			extraParams = "&5paisacookie="+fivepaisacookie+"&JwtToken="+JwtToken
		return redirect("http://streak.5paisa.com/?vid=streak"+extraParams)
	if request.method == 'POST':
		username = request.POST.get("user_id","").strip()
		broker = request.POST.get("broker","")
		auth_token = request.POST.get("token","")
		service = request.POST.get("service","zerodha")
		profile = {}
		error_msg = None
		user_broker_id = ""
		if service =="5paisa":
			credentials = {"params_map":{"cookie":auth_token}}
			profile,error_msg = validate_session(auth_token,service)
			if error_msg is None:
				user_broker_id = profile.get("broker_id","")
				if username=="":
					username = profile.get("broker_id","").lower()
			else:
				return  JsonResponse({'status':'error','error_msg':error_msg})
			print(profile,error_msg,user_broker_id)

		user = None
		new_user = True
		user_status = 100
		try: 
			user = models.UserProfile.objects.get(user_broker_id=username)

			adding_broker = request.POST.get('adding_broker','')
			if (adding_broker=="true" or adding_broker==True):
				return JsonResponse({"status":"error","error_msg":"Broker account already exists, please log in directly"})
				
			new_user = False
			user_uuid = user.user_uuid
			if user.email == username+"@"+service and user.additional_details.get("secondary_email","")=="":
				user_status = 100
			user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
			userflow.add_session_log(request)
			userflow.update_activity(request,"login")
			if user_subscription.subscription_instance == 'dual':
				user_subscription.subscription_instance = service+'_first_month_free'
				user_subscription.subscription_validity= max(datetime.datetime.today() + datetime.timedelta(days=int(7)),datetime.datetime(2021, 1, 31, 23, 59, 59))
				user_subscription.subscription_type = 0
				user_subscription.subscription_product = 'free'
				user_subscription.subscription_plan = 'free'
				user_subscription.subscription_price = 0
				user_subscription.subscription_tax = 0
				user_subscription.subscription_total_price = 0
				user_subscription.save()
				request.session['first_time_login_for_plan'] = True
				request.session['first_time_login'] = True

			partner_ref = request.session.pop('partner_ref','')
			partner_ref_ip = request.session.pop('partner_ref_ip','')
			if(partner_ref!='' and partner_ref_ip==request.META.get('HTTP_X_FORWARDED_FOR','')):
				map_user = {
							"user_broker_id": user.user_broker_id,
							"service":service,
							"new_user": False,
							"referral_code": partner_ref,
							"partner_ref_ip":partner_ref_ip
							}
				con = get_redis_connection('default')
				con.publish('partner_ref',ujson.dumps(map_user))
		except DoesNotExist:
			print("User desnot exit ",traceback.format_exc())
			user_uuid = str(uuid.uuid4())
			register_user_with_ams(user_uuid,service,user_broker_id,auth_token)
		if profile:
			request.session["broker"]=service
			request.session["full_broker_name"]=service
			request.session["broker_full_name"]=service
			request.session["user_broker_id"]=username
			if service == "5paisa":
				# profile = resp_json.get("data",{}).get("body",{}).get("EquityProfile",[])
				# print(profile)
				# if len(profile)>0:
				# 	profile = profile[0]
				# else:
				# 	return  JsonResponse({'status':'error','error_msg':'Invalid session credentials, please try again'})
				email = profile.get("EmailID","").lower()
				first_name = profile.get("ClientName").lower()
				phone_number = profile.get("MobileNo").lower()
				additional_details = {}
				if email=="":
					email = username+"@"+service
				try:
					address = profile.get("Address").lower().split("|")
					pincode = profile.get("PIN_Code","")
					additional_details = {'street_address':"",'pincode':pincode,"state":address[3],"city":address[2]}
				except:
					address = profile.get("Address","").lower()
					additional_details = {'street_address':""}

				if user is None and new_user:
					user_uuid_original = request.POST.get('user_uuid','')
					adding_broker = request.POST.get('adding_broker','')
					if user_uuid_original!="" and (adding_broker=="true" or adding_broker==True):
						user_uuid = user_uuid_original
						try:
							user = models.UserProfile.objects.get(user_uuid=user_uuid_original)
							user.phone_number = phone_number
							if user.email!=email:
								additional_details["secondary_email"]=email
							user.additional_details = additional_details

						except DoesNotExist:
							JsonResponse({'status':'error','error_msg':"User not found"})
					else:
						user = models.UserProfile(user_uuid=user_uuid,
											email = email,
											user_broker_id = username,
											first_name = first_name,
											last_name = '',
											phone_number = phone_number,
											password =  '',
											status = 1,
											additional_details=additional_details)
					user.user_broker_id = username
					user.first_broker = service

					# user_details = fetch_user_details(user_uuid,service)
					# if user_details:
					# 	user.first_name = user_details.get("user_name",username)
					try:
						user.save()
					except:
						user.email = username+"@"+service
						additional_details["secondary_email"]=email
						user.additional_details = additional_details
						user.save()

					user_status = 100

			if user is not None and new_user:
				subscription_uuid=str(uuid.uuid4())
				subscription_log_uuid = str(uuid.uuid4())
				user_subscription = models.UserSubscription(user_uuid=user_uuid,
					subscription_uuid=subscription_uuid,
					subscription_validity= max(datetime.datetime.today() + datetime.timedelta(days=int(7)),datetime.datetime(2021, 1, 31, 23, 59, 59)),
					latest_subscription_id = subscription_log_uuid,
					user_broker_id = user.user_broker_id,
					subscription_instance = 'trial'
					)
				# user.save()

				user_subscription_log = models.UserSubscriptionLog(user_uuid=user_uuid,
					subscription_log_uuid = subscription_log_uuid,
					subscription_uuid = subscription_uuid,
					subscription_start = datetime.datetime.today(),
					subscription_stop = max(datetime.datetime.today() + datetime.timedelta(days=int(7)),datetime.datetime(2021, 1, 31, 23, 59, 59)),
					user_broker_id = user.user_broker_id,
					subscription_instance = 'trial'
					)

				user_subscription_log.save()
				user_subscription.save()

				request.session['user_uuid'] = user_uuid
				request.session['user_name'] = username
				request.session['user_email'] = ""
				request.session['user_is_auth'] = True
				request.session['terms_accepted'] = False
				# print "request.session['terms_accepted']",request.session['terms_accepted']
				request.session['first_time_login'] = True
				request.session['first_time_login_for_plan']=True
				request.session['first_time_algos'] = True
				request.session['first_time_dashboard'] = True
				request.session['first_time_create_algorithm'] = True
				request.session['first_time_orders'] = True
				request.session['first_time_backtest'] = True
				request.session['first_time_deploy'] = True
				request.session['first_time_orderbook'] = True
				request.session['first_time_portfolio'] = True
				request.session['session_secret'] = utils.generate_random_hash()
				# initialize_account(user_uuid)
				partner_ref = request.session.pop('partner_ref','')
				partner_ref_ip = request.session.pop('partner_ref_ip','')
				userflow.add_session_log(request)
				userflow.update_activity(request,"login")
				if(partner_ref!='' and partner_ref_ip==request.META.get('HTTP_X_FORWARDED_FOR','')):
					map_user = {
								"user_broker_id": user.user_broker_id,
								"service":service,
								"new_user": True,
								"referral_code": partner_ref,
								"partner_ref_ip":partner_ref_ip
								}
					con = get_redis_connection('default')
					con.publish('partner_ref',ujson.dumps(map_user))


			request.session['user_uuid'] = user.user_uuid
			request.session['user_name'] = user.first_name
			request.session['user_email'] = user.additional_details.get("secondary_email","")
			request.session['terms_accepted'] = user.terms_accepted

			if (user.phone_number==''):
				request.session['show_phone_popup'] = True

			request.session['user_is_auth'] = True
			request.session['user_status'] = user_status

			if not request.session.session_key:
				request.session.save()
			utils.update_usage_util(user_uuid,'',clear=False)

			mobile_web = False
			v_pref = 1
			
			try:
				if any(word in request.META['HTTP_USER_AGENT'] for word in ["Android","webOS","iPhone","iPad","iPod","BlackBerry","IEMobile","Opera Mini"]):
					mobile_web = True
					v_pref = 1

				if not mobile_web:
					conn = get_redis_connection('default')
					q = conn.get('user_version_pref'+user_uuid)
					if q is None:
						v_pref = 1
						if request.session.get('first_time_login',False)==True:
							v_pref=3
					else:
						try:
							v_pref = int(q)
						except:
							v_pref = 3
			except:
				pass
			return JsonResponse({'status':'success','user_status':user_status,'csrf':csrf.get_token(request),'sessionid':request.session.session_key,"version":v_pref})	
		elif error_msg is None:
			return  JsonResponse({'status':'error','error_msg':error_msg})
		else:
			return JsonResponse({'status':'error','error_msg':'Unknow error occured, please try again in sometime'})
	else:
		return JsonResponse({"status":"error","error_msg":"Invalid method"})

def ams_sso_login(request):
	url = AMS_ROOT_URL + "/"+ version+ "/users/token"

	# payload = "{\n\t \"user_uuid\": \"4ef7f521-6c7b-476e-bc0f-fb4a1323b1e1\",\n\t \"exchange\": \"coinbasepro\",\n\t \"account_name\": \"primary coinbase\",\n\t \"credentials\": {\n           \"api_key\": \"1799372bad7b0825929aa1bbd94f3a74\",\n\t\t           \"api_secret\": \"FnxauMJnagC9Pip78eqJb0eze/3SougKsGsYWGlJaUZASTRXoVzl+2MeGsgDXRnLcM9UaWDUB8ESJInuArnBsA==\",\n\t\t           \"api_passphrase\": \"j4oic6fpdog\"\n\t\t           }\n\t}\n"
	# payload = ujson.dumps({"user_uuid": user_uuid,"exchange":exchange,"account_name": account_name,"credentials": credentials})
	if request.method == 'POST':
		username = request.POST.get("user_id","").strip()
		broker = request.POST.get("broker","")
		auth_token = request.POST.get("token","")
		service = request.POST.get("service","zerodha")

		if username =="":
			auth_code,auth_data,long_token = fetch_user_details_ab(auth_token)
			print("here,,,,,,,,",long_token)
			if auth_code == 200:
				username = auth_data.get("clientID","")
				auth_token = long_token
				print(username,auth_token)
			else:
				return JsonResponse({"status":"error","error_msg":auth_data.get("message","Invalid credentials")})

		if username == "" or auth_token == "":
			return JsonResponse({"status":"error","error_msg":"Invalid credentials"})

		credentials = {"username":username,"auth_token":auth_token}
		if "@" not in username:
			user_broker_id = username
		else:
			user_broker_id = ""

		user = None
		user_status = 100
		try: 
			user = models.UserProfile.objects.get(user_broker_id=username)
			user_uuid = user.user_uuid
			if user.email == username+"@"+service and user.additional_details.get("secondary_email","")=="":
				user_status = 100
			user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
			userflow.add_session_log(request)
			userflow.update_activity(request,"login")
			if user_subscription.subscription_instance == 'dual':
				user_subscription.subscription_instance = service+'_first_month_free'
				user_subscription.subscription_validity= max(datetime.datetime.today() + datetime.timedelta(days=int(7)),datetime.datetime(2021, 1, 31, 23, 59, 59))
				user_subscription.subscription_type = 0
				user_subscription.subscription_product = 'free'
				user_subscription.subscription_plan = 'free'
				user_subscription.subscription_price = 0
				user_subscription.subscription_tax = 0
				user_subscription.subscription_total_price = 0
				user_subscription.save()
				request.session['first_time_login_for_plan'] = True
				request.session['first_time_login'] = True

			partner_ref = request.session.pop('partner_ref','')
			partner_ref_ip = request.session.pop('partner_ref_ip','')
			if(partner_ref!='' and partner_ref_ip==request.META.get('HTTP_X_FORWARDED_FOR','')):
				map_user = {
							"user_broker_id": user.user_broker_id,
							"service":service,
							"new_user": False,
							"referral_code": partner_ref,
							"partner_ref_ip":partner_ref_ip
							}
				con = get_redis_connection('default')
				con.publish('partner_ref',ujson.dumps(map_user))
		except DoesNotExist:
			user_uuid = str(uuid.uuid4())
		
		payload = ujson.dumps({"user_uuid":user_uuid ,"service":service,"async_validate":False,"credentials": credentials})

		headers = base_header
		response = requests.request("POST", url, data=payload, headers=headers,timeout=2)
		success,resp_json,status_code = reponse_handler(response)
		if success:
			request.session["broker"]=service
			request.session["full_broker_name"]='angel broking'
			request.session["broker_full_name"]=service
			request.session["user_broker_id"]=username
			if user is None:
				user = models.UserProfile(user_uuid=user_uuid,
										email = username+"@"+service,
										user_broker_id = username,
										first_name = '',
										last_name = '',
										phone_number = '',
										password =  '',
										status = 1)
				user.user_broker_id = username
				user.first_broker = service

				user_details = fetch_user_details(user_uuid,service)
				if user_details:
					user.first_name = user_details.get("user_name",username)
				user.save()
				user_status = 100

				subscription_uuid=str(uuid.uuid4())
				subscription_log_uuid = str(uuid.uuid4())
				user_subscription = models.UserSubscription(user_uuid=user_uuid,
					subscription_uuid=subscription_uuid,
					subscription_validity= max(datetime.datetime.today() + datetime.timedelta(days=int(7)),datetime.datetime(2021, 1, 31, 23, 59, 59)),
					latest_subscription_id = subscription_log_uuid,
					user_broker_id = user.user_broker_id,
					subscription_instance = 'trial'
					)
				user.save()

				user_subscription_log = models.UserSubscriptionLog(user_uuid=user_uuid,
					subscription_log_uuid = subscription_log_uuid,
					subscription_uuid = subscription_uuid,
					subscription_start = datetime.datetime.today(),
					subscription_stop = max(datetime.datetime.today() + datetime.timedelta(days=int(7)),datetime.datetime(2021, 1, 31, 23, 59, 59)),
					user_broker_id = user.user_broker_id,
					subscription_instance = 'trial'
					)

				user_subscription_log.save()
				user_subscription.save()

				request.session['user_uuid'] = user_uuid
				request.session['user_name'] = username
				request.session['user_email'] = ""
				request.session['user_is_auth'] = True
				request.session['terms_accepted'] = False
				# print "request.session['terms_accepted']",request.session['terms_accepted']
				request.session['first_time_login'] = True
				request.session['first_time_login_for_plan']=True
				request.session['first_time_algos'] = True
				request.session['first_time_dashboard'] = True
				request.session['first_time_create_algorithm'] = True
				request.session['first_time_orders'] = True
				request.session['first_time_backtest'] = True
				request.session['first_time_deploy'] = True
				request.session['first_time_orderbook'] = True
				request.session['first_time_portfolio'] = True
				request.session['session_secret'] = utils.generate_random_hash()
				# initialize_account(user_uuid)
				partner_ref = request.session.pop('partner_ref','')
				partner_ref_ip = request.session.pop('partner_ref_ip','')
				userflow.add_session_log(request)
				userflow.update_activity(request,"login")
				if(partner_ref!='' and partner_ref_ip==request.META.get('HTTP_X_FORWARDED_FOR','')):
					map_user = {
								"user_broker_id": user.user_broker_id,
								"service":service,
								"new_user": True,
								"referral_code": partner_ref,
								"partner_ref_ip":partner_ref_ip
								}
					con = get_redis_connection('default')
					con.publish('partner_ref',ujson.dumps(map_user))


			if user is not None:
				request.session['user_uuid'] = user.user_uuid
				request.session['user_name'] = user.first_name
				request.session['user_email'] = user.additional_details.get("secondary_email","")
				request.session['terms_accepted'] = user.terms_accepted

				if (user.phone_number==''):
					request.session['show_phone_popup'] = True

				request.session['user_is_auth'] = True
				request.session['user_status'] = user_status

				if not request.session.session_key:
					request.session.save()
				utils.update_usage_util(user_uuid,'',clear=False)

				mobile_web = False
				v_pref = 1
				
				try:
					if any(word in request.META['HTTP_USER_AGENT'] for word in ["Android","webOS","iPhone","iPad","iPod","BlackBerry","IEMobile","Opera Mini"]):
						mobile_web = True
						v_pref = 1

					if not mobile_web:
						conn = get_redis_connection('default')
						q = conn.get('user_version_pref'+user_uuid)
						if q is None:
							v_pref = 1
							if request.session.get('first_time_login',False)==True:
								v_pref=3
						else:
							try:
								v_pref = int(q)
							except:
								v_pref = 3
				except:
					pass
				return JsonResponse({'status':'success','user_status':user_status,'csrf':csrf.get_token(request),'sessionid':request.session.session_key,"version":v_pref})	
		elif status_code == 403:
				return  JsonResponse({'status':'error','error_msg':'Invalid credentials, 3 wrong retires will block you account, so check your credentials properly'})
		else:
			return JsonResponse({'status':'error','error_msg':resp_json.get("message",'Unknow error occured, please try again in sometime')})
	else:
		return JsonResponse({"status":"error","error_msg":"Invalid method"})

def ams_add_email(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error","error":"auth"},status=401)
	if request.method == 'POST':
		email = request.POST.get("email","")
		user = None
		try:
			user = models.UserProfile.objects.get(email=email)
			return JsonResponse({"status":"error","error_msg":"User with email already registered"})

		except DoesNotExist:
			try:
				user = models.UserProfile.objects.get(user_uuid=user_uuid)
				if user.email == user.user_broker_id+"@"+user.first_broker and user.additional_details.get("secondary_email","")=="":
					user.additional_details['secondary_email'] = email
					user.save()
					request.session['user_email'] = user.additional_details.get("secondary_email","")
					utils.send_initial_emails(user_uuid=user_uuid,email=user.additional_details.get("secondary_email",""),name=user.first_name)
					return JsonResponse({"status":"success","msg":"Email added"})
				else:
					return JsonResponse({"status":"error","error_msg":"User with email already registered"})
			except DoesNotExist:
				return JsonResponse({"status":"error","error_msg":"User not found"})
	return JsonResponse({"status":"error","error_msg":"Invalid method"})

#incomplete
def ams_logout(request):
	# if response.status_code == 200:
	for key in request.session.keys():
		del request.session[key]
	return JsonResponse({"status":"success"})

def fetch_user_details_ab(token):
	url1 = "https://openapis.angelbroking.com/openApi/user/FetchToken"
	secret_token = hashlib.sha256(settings.AB_API_SECRET+"|"+token) #+"|"+ request_token.encode("utf-8") + settings.AB_API_SECRET.encode("utf-8"))
	secret_token = secret_token.hexdigest()
	payload1 = ujson.dumps({"shortToken":token,"hash":secret_token})
	response = requests.request("POST", url1, data=payload1,headers={"Content-Type":"application/json","X-api-key":settings.AB_API_KEY},timeout=2)
	success,response_json,status_code = reponse_handler(response)
	print(payload1,response_json)
	if status_code==200:
		long_token = response_json.get("data",{}).get("authToken","")
		if long_token == "":
			print response_json
			return response_json.get("statusCode",401),response_json.get("data",{"message":response_json.get("message","Error in Authentication")}),""

		url = "https://openapis.angelbroking.com/openApi/user/GetUserDetails"
		headers = {"Authorization":long_token}
		payload = ujson.dumps({})
		response = requests.request("POST", url, data=payload, headers=headers,timeout=2)
		success,response_json,status_code = reponse_handler(response)
		print(payload,response_json,status_code)
		if status_code==200:
			if response_json.get("statusCode",401)==200:
				# print response_json
				return 200,response_json.get("data",{"message":response_json.get("message","success")}),long_token
			else:
				return response_json.get("statusCode",401),response_json.get("data",{"message":response_json.get("message","Error in Authentication")}),long_token
		else:
			return status_code,None,long_token

def ams_fetch_positions(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error"})
	if request.method!='GET':
		return JsonResponse({"status":"error","error":"type"})

	headers = {}
	if settings.KITE_HEADER == True:
		headers = {"X-Kite-Version":"3"}
		auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
		headers["Authorization"] = "token {}".format(auth_header)
	url = AMS_ROOT_URL + "/"+ version+ "/get_positions"
	payload = ujson.dumps({"user_uuid": user_uuid,"service": request.session.get("broker","zerodha")})
	
	headers = base_header
	response = requests.request("POST", url, data=payload, headers=headers)
	# print(response.text,payload,url)
	if response.status_code == 200:
		response_json = ujson.loads(response.text)
		if response_json.get('data',None) is None:
			return JsonResponse({"status":"error","error":"auth",'error_msg':response_json.get('message')})
		else:
			positions = models.PositionsOfInstrument.objects(user_uuid=user_uuid,updated_at__gte=datetime.datetime.now().replace(hour=3,minute=0,second=0))
			print 'pppppppp',positions,'2017-11-10T01:00:00.969619',datetime.datetime.now().replace(hour=1,minute=0,second=0).isoformat()
			# print user_uuid
			if positions==[] and request.GET.get('filter','').lower()=='streak':
				return JsonResponse({"status":"success","positions":[]})
			else:
				adj_positions = []
				# adj_positions = response_json['data']['net']
				# adj_positions[0]['deployment_uuid']='111111111111'
				for n in response_json['data']['net']:
					if(request.GET.get('filter','').lower()=='all'):
						n['modified']=0	
						n['user_uuid']=user_uuid
						if n["exchange"]=="NFO":
							if (n['tradingsymbol'].endswith("CE") or n['tradingsymbol'].endswith("PE")):
								n["segment"]="NFO-OPT"
							else:
								n["segment"]="NFO-FUT"
						elif n["exchange"]=="CDS":
							n["segment"]="CDS-FUT"
						else:
							n["segment"]=n["exchange"]
						adj_positions.append(n)
					else:
						for p in positions:
							if(n['tradingsymbol']==p['symbol'] and n['product']==p['product']):
								if(n['quantity']==p['quantity']):
									n['modified']=0	
								else:
									n['modified']=1							
								n['user_uuid']=p['user_uuid']
								if n["exchange"]=="NFO":
									if (n['tradingsymbol'].endswith("CE") or n['tradingsymbol'].endswith("PE")):
										n["segment"]="NFO-OPT"
									else:
										n["segment"]="NFO-FUT"
								elif n["exchange"]=="CDS":
									n["segment"]="CDS-FUT"
								else:
									n["segment"]=n["exchange"]
								adj_positions.append(n)
				return JsonResponse({"status":"success","positions":adj_positions})
		# else:
		# 	return JsonResponse({"status":"error","error":"response error"})		
	elif response.status_code == 403:
		return JsonResponse({"status":"error","error":"auth",'error_msg':'Session expired, relogin required'})

	return JsonResponse({"status":"error"})

def ams_fetch_holdings(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error","error_msg":"auth"})
	if request.method!='GET':
		return JsonResponse({"status":"error","error":"type"})

	headers = {}
	if settings.KITE_HEADER == True:
		headers = {"X-Kite-Version":"3"}
		auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
		headers["Authorization"] = "token {}".format(auth_header)
	url = AMS_ROOT_URL + "/"+ version+ "/get_holdings"

	payload = ujson.dumps({"user_uuid": user_uuid,"strategy_code":"","service": request.session.get("broker","zerodha")})
	
	headers = base_header
	response = requests.request("POST", url, data=payload, headers=headers,timeout=5)
	# print "hhhhhhhhhhhhhhhhhhh",response.text,payload
	if response.status_code == 200:
		response_json = ujson.loads(response.text)
		# print(response_json,payload,url)
		if response_json.get('data',None) is None:
			return JsonResponse({"status":"error","error":"auth",'error_msg':response_json.get('message')})
		if "data" in response_json.keys():
			# positions = models.HoldingsForAlgorithm.objects(user_uuid=user_uuid,product='CNC',position__qty__ne = 0).order_by("updated_at")
			# holdings = models.HoldingsForAlgorithm._get_collection().find({'user_uuid':user_uuid,"status":{ "$in": [-1,-2,-3]},"deployment_time":{"$gte":datetime.datetime.now().replace(hour=0,minute=0,second=0)}}).sort([("updated_at",-1)])
			holding_algos = models.DeployedAlgorithm.objects(user_uuid=user_uuid,algo_obj__product='CNC',status=0)
			# print holding_algos
			if holding_algos==[] and request.GET.get('filter','').lower()=='streak':
				return JsonResponse({"status":"success","positions":[]})
			else:
				adj_positions = []
				adj_holdings_list = []
				# adj_positions = response_json['data']['net']
				# adj_positions[0]['deployment_uuid']='111111111111'
				for n in response_json['data']:#['net']:
					if(request.GET.get('filter','').lower()=='all'):
						n['modified']=0
						n['product']='CNC'	
						n['user_uuid']=user_uuid
						adj_positions.append(n)
					else:
						for p in holding_algos:
							n['product']='CNC'	
							if(n['tradingsymbol']==p['symbol'] and n['product']==p['algo_obj']['product']) and p['symbol'] not in adj_holdings_list:
								adj_holdings_list.append(p['symbol'])
								# print p['position']['qty']
								n['modified']=0	
								# if(n['quantity']+n['t1_quantity']==p['position']['qty']):
								# 	pass
								# else:
								# 	n['modified']=1							
								n['user_uuid']=p['user_uuid']
								adj_positions.append(n)
				return JsonResponse({"status":"success","positions":adj_positions})
		else:
			return JsonResponse({"status":"error","error":"response error"})		
	elif response.status_code == 403:
		return JsonResponse({"status":"error","error":"auth",'error_msg':'Session expired, relogin required'})

	return JsonResponse({"status":"error"})

def ams_fetch_order_book(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({'status':'error','error':'auth'})

	if request.method=="GET":
		platform = request.GET.get('platform','streak').lower()
		if platform not in ['streak','all']:
			return JsonResponse({'status':'error','error':'unkown platform'})
		if platform == 'streak':
			orders = []
			url = AMS_ROOT_URL + "/"+ version+ "/orders/get"
			payload = ujson.dumps({"user_uuid": user_uuid,"service": request.session.get("broker","zerodha")})
			
			headers = base_header
			response = requests.request("POST", url, data=payload, headers=headers,timeout=3)
			success,response_json,status_code = reponse_handler(response)
			# print "https://api-partners.kite.trade/orders?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token',''))
			if status_code == 200:
				if response_json.get('data',None) is not None:
					orders = response_json['data']
					executed = []
					pending = []
					now = datetime.datetime.now()
					br_o = models.BrokerOrder.objects(user_uuid=user_uuid,created_at__gte = now.replace(hour=0,minute=0,second=0))
					br_order_depid = {}
					br_orders_list = []
					try:
						for b in br_o:
							br_orders_list.append(b.order_id)
							br_order_depid[b.order_id]=b["deployment_uuid"]
					except:
						print(traceback.format_exc())
						br_orders_list = [b.order_id for b in br_o]
						pass
					for o in orders:
						o['order_timestamp']=datetime.datetime.strptime(o['order_timestamp'],"%d-%b-%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
						print(o['order_id'],user_uuid,br_orders_list)
						o['status'] = o.get('status','').upper()
						if (o['order_id'] in br_orders_list):
							if "DIRECT_" in br_order_depid.get(o['order_id'],""):
								o["order_tag"]="direct"
							else:
								o["order_tag"]="strategy"
							if o['status'] in ['COMPLETE','REJECTED','CANCELLED','CANCELLED AMO'] or 'CANCELLED' in o['status'] or 'REJECTED' in o['status']:
								o['user_uuid']=user_uuid
								executed.append(o)
							else:
								pending.append(o)
					return JsonResponse({"status":"success","orders":orders,'pending':pending,'executed':executed,'platform':platform})
				else:
					return JsonResponse({"status":"error","error":"response error",'error_msg':response_json.get('message',"Session expired, relogin required")})
			else:
				return JsonResponse({"status":"error","error":"response error",'error_msg':response_json.get('message',"Session expired, relogin required")})
			return JsonResponse({'status':'success'})
		if platform == 'all':
			try:
				orders = []
				url = AMS_ROOT_URL + "/"+ version+ "/orders/get"
				payload = ujson.dumps({"user_uuid": user_uuid,"service": request.session.get("broker","zerodha")})
				
				headers = base_header
				response = requests.request("POST", url, data=payload, headers=headers,timeout=5)
				success,response_json,status_code = reponse_handler(response)
				# print("https://api-partners.kite.trade/orders?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token','')))
				if status_code == 200:
					if response_json.get('data',None) is not None:
						orders = response_json['data']
						executed = []
						pending = []

						now = datetime.datetime.now()
						br_o = models.BrokerOrder.objects(user_uuid=user_uuid,created_at__gte = now.replace(hour=0,minute=0,second=0))
						br_order_depid = {}
						br_orders_list = []
						try:
							for b in br_o:
								br_orders_list.append(b.order_id)
								br_order_depid[b.order_id]=b["deployment_uuid"]
						except:
							print(traceback.format_exc())
							br_orders_list = [b.order_id for b in br_o]
							pass

						for o in orders:
							o['order_timestamp']=datetime.datetime.strptime(o['order_timestamp'],"%d-%b-%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
							o['status'] = o.get('status','').upper()
							if (o['order_id'] in br_orders_list):
								if "DIRECT_" in br_order_depid.get(o['order_id']):
									o["order_tag"]="direct"
								else:
									o["order_tag"]="strategy"
							else:
								o["order_tag"]=request.session.get("broker","zerodha").lower()# "ab"

							if o['status'] in ['COMPLETE','REJECTED','CANCELLED','CANCELLED AMO'] or 'CANCELLED' in o['status'] or 'REJECTED' in o['status']:
								o['user_uuid']=user_uuid
								executed.append(o)
							else:
								pending.append(o)
						return JsonResponse({"status":"success","orders":orders,'pending':pending,'executed':executed,'platform':platform})
					else:
						return JsonResponse({"status":"error","error":"response error",'error_msg':response_json.get('message',"Session expired, relogin required")})
				else:
					return JsonResponse({"status":"error","error":"response error",'error_msg':'Session expired, relogin required'})	
			except:
				print(traceback.format_exc())
				return JsonResponse({"status":"error","error":"response error",'error_msg':'Error fetching orderbook from the broker.'})
	return JsonResponse({})

def ams_place_order_direct(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error","error":"auth"},status=401)

	if request.method == "POST":
		notification_uuid = request.POST.get('notification_uuid','')
		deployment_uuid = request.POST.get('deployment_uuid','')
		algo_uuid = request.POST.get('algo_uuid','')
		algo_name = request.POST.get('algo_name','')
		exchange = request.POST.get('exchange','').upper()
		symbol = urllib.unquote(unicode(request.POST.get('tradingsymbol','')).encode('utf-8'))
		segment = request.POST.get('segment','')
		transaction_type = request.POST.get('transaction_type','')
		order_type = request.POST.get('order_type','').upper()
		quantity = request.POST.get('quantity',"0.0")
		product = request.POST.get('product','')
		price = request.POST.get('price',"0.0")
		trigger_price = request.POST.get('trigger_price','')
		disclosed_quantity = request.POST.get('disclosed_quantity','')
		account_name = request.POST.get('account_name','')
		validity = request.POST.get('validity','GTC')
		variety = request.POST.get('variety','GTC').lower()
		tag = request.POST.get('tag','Test')
		tpsl_key = request.POST.get('tpsl_key','')
		broker = request.POST.get('broker','')
		squareoff = request.POST.get('squareoff','')
		stoploss = request.POST.get('stoploss','')
		trailing_stoploss = request.POST.get('trailing_stoploss','')

		access_token = request.session.get('access_token','')
		public_token = request.session.get('public_token','')
		user_broker_id = request.session.get('user_broker_id','')
		broker = request.session.get('broker','')
		
		if user_broker_id=='':
			print 'probably kite login popup'
			return JsonResponse({"status":"error","error":"BrokerLogin",'error_msg':'BrokerLogin'})

		try:
			quantity=str(int(quantity))
		except:
			return JsonResponse({"status":"error","error_msg":"Invalid quantity"})

		if segment=='' and exchange=='CDS':
			segment = 'CDS-FUT'
		if exchange=='CDS-FUT':
			segment = 'CDS-FUT'
			exchange = 'CDS'
		elif segment=='' and exchange=='MCX':
			segment = 'MCX'
		elif segment=='' and exchange=='NFO':
			if str(symbol).endswith("CE") or str(symbol).endswith("PE"):
				segment = 'NFO-OPT'
			else:
				segment = 'NFO-FUT'
		elif segment == '':
			segment = 'NSE'
		elif exchange=='NFO-FUT':
			segment = 'NFO-FUT'
			exchange = 'NFO'
		elif exchange=='NFO-OPT': 
			segment = 'NFO-OPT' 
			exchange="NFO"
			
		payload = {
		  # "api_key":settings.KITE_API_KEY,
		  # "access_token":access_token,
		  "tradingsymbol":symbol,
		  "exchange":exchange,
		  "transaction_type":transaction_type,
		  "order_type":order_type,
		  "quantity":quantity,
		  "product":product,
		  "validity":validity,
		  "tag":tag
		}
		payload = {
		  "symbol":symbol,
		  "exchange":exchange,
		  "tradingsymbol":symbol,
		  "segment":segment,
		  "transaction_type":transaction_type,
		  "order_type":order_type,
		  "quantity":quantity,
		  "product":product,
		  "validity":validity,
		  "strategy_code": tag,
		  "trigger_price":trigger_price,
		  "user_uuid":user_uuid,
		  "is_amo": False,
		  "service":request.session.get("broker","zerodha")
		}
		
		if variety=='':
			return JsonResponse({"status":"error","error_msg":"Unknown variety"})
		elif variety == 'regular' or variety =='amo':
			if variety.lower()=='amo':
				payload["is_amo"]=True
			if order_type =='LIMIT':
				try:
					payload['price']=str(float(price))
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid price"})
			elif order_type == 'SL':
				try:
					payload['price']=str(float(price))
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid price"})
				try:
					payload['trigger_price']=str(float(trigger_price))
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid trigger price"})
			elif order_type=='SL-M':
				try:
					payload['trigger_price']=str(float(trigger_price))
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid trigger price"})
			if disclosed_quantity!='':
				try:
					payload['disclosed_quantity']=str(int(disclosed_quantity))
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid disclosed quantity"})
		elif variety == 'bo':
			if order_type=='MARKET' or order_type=='SL-M':
				return JsonResponse({"status":"error","error_msg":"Invalid order type"})

			if order_type=='LIMIT':
				try:
					payload['price']=str(float(price))
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid price"})
			elif order_type == 'SL':
				try:
					payload['price']=str(float(price))
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid price"})
				try:
					payload['trigger_price']=str(float(trigger_price))
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid trigger price"})

			if squareoff!='':
				try:
					payload['squareoff']=str(float(squareoff))
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid squareoff price"})
			else:
				return JsonResponse({"status":"error","error_msg":"Invalid squareoff price"})

			if stoploss!='':
				try:
					payload['stoploss']=str(float(stoploss))
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid stoploss price"})
			else:
				return JsonResponse({"status":"error","error_msg":"Invalid stoploss price"})

			if trailing_stoploss!='':
				try:
					payload['trailing_stoploss']=str(float(trailing_stoploss))
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid trailing stoploss price"})
			else:
				return JsonResponse({"status":"error","error_msg":"Invalid trailing stoploss price"})

		elif variety == 'co':
			try:
				payload['trigger_price']=str(float(trigger_price))
			except:
				return JsonResponse({"status":"error","error_msg":"Invalid trigger price"})
			if order_type == 'LIMIT':
				try:
					payload['price']=str(float(price))
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid price"})
			elif order_type != 'MARKET' and order_type != 'LIMIT':
				return JsonResponse({"status":"error","error_msg":"Invalid order type"})

		url = AMS_ROOT_URL + "/"+ version+ "/orders/create"
		payload["user_uuid"]=user_uuid
		payload["service"]=request.session.get("broker","zerodha")

		# payload = ujson.dumps(payload)
		
		headers = base_header
		response = requests.request("POST", url, data=ujson.dumps(payload), headers=headers)
		print(payload,response.text,url)
		success,response_json,status_code = reponse_handler(response)
		if status_code == 200:
			if 'price' in payload.keys():
				payload['price'] = float(payload['price'])
			if 'stoploss' in payload.keys():
				payload['stoploss'] = float(payload['stoploss'])
			if 'squareoff' in payload.keys():
				payload['squareoff'] = float(payload['squareoff'])
			if 'disclosed_quantity' in payload.keys():
				payload['disclosed_quantity'] = int(payload['disclosed_quantity'])
			if 'trailing_stoploss' in payload.keys():
				payload['trailing_stoploss'] = float(payload['trailing_stoploss'])
			if 'trigger_price' in payload.keys():
				payload['trigger_price'] = float(payload['trigger_price'])
			if 'quantity' in payload.keys():
				payload['quantity'] = int(payload['quantity'])

			if response_json.get('data',None) is not None:
				payload['order_placement']="manual"
				payload['segment']=segment
				payload['broker']=broker
				broker_order = models.BrokerOrder(user_uuid=user_uuid,
				algo_uuid=algo_uuid,
				algo_name=algo_name,
				deployment_uuid='DIRECT_'+exchange.lower()+'_'+symbol.lower(),
				order_id=response_json['data'].get('order_id',''),
				order_payload = payload
				)
				broker_order.save()
				return JsonResponse({'status':'success','order_id':response_json['data'].get('order_id','')})
			return JsonResponse({"status":"error","error_msg":response_json.get('message',"Error placing order")}) 
		elif status_code == 403:
			print response.text
			return JsonResponse({"status":"error","error_msg":'Session expired, re-login required'}) 
		elif status_code == 400:
			print response_json
			return JsonResponse({"status":"error","error_msg":response_json.get('message',"Error placing order")})
		elif status_code == 428:
			return JsonResponse({'status':'error','response_code':response.status_code,'error_msg':'Order needs authorisation at depository, please visit broker trading terminal to place the order','error-type':'Order needs authorisation at depository, please visit broker trading terminal to place the order','error_url':""})
		else:
			print response_json
			return JsonResponse({"status":"error","error_msg":response_json.get("message","Unexpected error")})
	return JsonResponse({"status":"error","error_msg":"method"})

def ams_place_order_discipline(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth'})
	if request.method == "POST":
		notification_uuid = request.POST.get('notification_uuid','')
		if notification_uuid == '':
			return JsonResponse({"status":"error",'error-type':'notifid'})

		try:
			con = get_redis_connection("default")
			notifs = con.get('today_notification:'+user_uuid)
			notifs = ujson.loads(notifs)
			notif_used = notifs['used'].get(notification_uuid,0)
			if notif_used:
				return JsonResponse({"status":"error","error_msg":"Notification used"})
		except:
			print traceback.format_exc()
			
		deployment_uuid = request.POST.get('deployment_uuid','')
		algo_uuid = request.POST.get('algo_uuid','')
		algo_name = request.POST.get('algo_name','')
		exchange = request.POST.get('exch','').upper()
		symbol = request.POST.get('sym','')
		segment = request.POST.get('seg','')
		transaction_type = request.POST.get('transaction_type','')
		order_type = request.POST.get('order_type','')
		quantity = int(request.POST.get('quantity',0))
		product = request.POST.get('product','')
		validity = request.POST.get('validity','')
		trigger_price = float(request.POST.get('trigger_price',0))

		deployment_uuid = request.POST.get('deployment_uuid','')

		if deployment_uuid == '':
			print 'deployment_uuid not present'
			return JsonResponse({"status":"error",'error-type':'depid'})

		user_broker_id = request.session.get('user_broker_id','')
		broker = request.session.get("broker","zerodha")

		if user_broker_id=='':
			print 'probably kite login popup'
			return JsonResponse({"status":"error",'error-type':'noauth'})

		con = get_redis_connection('default')
		key_prefix = ':'.join(['deployed',user_uuid,'*',deployment_uuid])
		deployed_keys = get_deployment_keys({"user_uuid":user_uuid,"deployment_uuid":deployment_uuid,"status":0}) #con.keys(key_prefix)
		# print 'zzzzzzzzzzzzzzzzzzzzzz11111111111',key_prefix
		if(len(deployed_keys)==0):
			print 'deployment_uuid not present'
			return JsonResponse({"status":"error",'error-type':'Strategy not live','error_msg':'Strategy not live'})

		payload = {
		  "symbol":symbol,
		  "exchange":exchange,
		  "segment":segment,
		  "transaction_type":transaction_type,
		  "order_type":order_type,
		  "quantity":str(quantity),
		  "product":product,
		  "validity":validity,
		  "strategy_code": strategy_code,
		  "trigger_price":str(trigger_price),
		  "user_uuid":user_uuid,
		  "is_amo": False,
		  "service":request.session.get("broker","zerodha")
		}

		# print payload
		# headers = {}
		# if settings.KITE_HEADER == True:
		# 	headers = {"X-Kite-Version":"3"}
		# 	auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
		# 	headers["Authorization"] = "token {}".format(auth_header)
		# response = requests.request("POST","https://api-partners.kite.trade/orders/regular", data=payload,headers=headers)
		url = AMS_ROOT_URL + "/"+ version+ "/orders/create"
		# payload = ujson.dumps({"user_uuid": user_uuid,"service_name": request.session.get("broker","zerodha")})
		
		headers = base_header
		response = requests.request("POST", url, data=ujson.dumps(payload), headers=headers)
		success,response_json,status_code = reponse_handler(response)
		if status_code == 200:
			if 'price' in payload.keys():
				payload['price'] = float(payload['price'])
			if 'stoploss' in payload.keys():
				payload['stoploss'] = float(payload['stoploss'])
			if 'squareoff' in payload.keys():
				payload['squareoff'] = float(payload['squareoff'])
			if 'disclosed_quantity' in payload.keys():
				payload['disclosed_quantity'] = int(payload['disclosed_quantity'])
			if 'trailing_stoploss' in payload.keys():
				payload['trailing_stoploss'] = float(payload['trailing_stoploss'])
			if 'trigger_price' in payload.keys():
				payload['trigger_price'] = float(payload['trigger_price'])
			if 'quantity' in payload.keys():
				payload['quantity'] = int(payload['quantity'])
			if response_json.get('data',None) is not None:
				try:
					#update holdings for algorithm using webhook 
					# holding = HoldingsForAlgorithm.objects.get(user_uuid=user_uuid,deployment_uuid=deployment_uuid)
					# holding.position[segment+'_'+symbol]['qty']=
					broker_order = models.BrokerOrder(user_uuid=user_uuid,
						algo_uuid=algo_uuid,
						# algo_name=algo_name,
						deployment_uuid=deployment_uuid,
						order_id=response_json['data']['order_id'],
						order_payload = {
							# "api_key":settings.KITE_API_KEY,
							# "access_token":access_token,
							"tradingsymbol":symbol,
							"segment":segment,
							"exchange":exchange,
							"transaction_type":transaction_type,
							"order_type":order_type,
							"quantity":quantity,
							"product":product,
							"validity":validity,
							"trigger_price":trigger_price
						}
					)
					broker_order.save()

					pipeline = con.pipeline()

					keys = deployed_keys #get_deployment_keys({"user_uuid":user_uuid,"deployment_uuid":deployment_uuid}) #con.keys('deployed:'+user_uuid+':*:'+deployment_uuid)
					if len(keys)>0:
						redis_key = keys[0]
					else:
						redis_key = None

					notifs['used'][notification_uuid]=1 # mark notitification as used(actioned upon)
					con.set('today_notification:'+user_uuid,ujson.dumps(notifs))
					ex_time = int((datetime.datetime.now().replace(hour=3,minute=0,second=0)+datetime.timedelta(days=1)).strftime('%s')) - int(datetime.datetime.now().strftime('%s'))
					con.expire('today_notification:'+user_uuid,ex_time)

					# if redis_key:
					# 	r = con.get(redis_key)
					# 	try:
					# 		r = json.loads(r)
					# 		r['frequency_utilized']=r.get('frequency_utilized',0)+1
					# 	except:
					# 		print traceback.format_exc()
					# 		# r = {}
					# 		pass
						# print r
						# pipeline.set(redis_key,r)
						# pipeline.expire(redis_key,1)
						# pipeline.publish(settings.ENV+'-deployment_channel','DEL:'+redis_key)

					if redis_key:
						r = con.get(redis_key)
						ttl = con.ttl(redis_key)
						try:
							r = json.loads(r)
							r['SL_placed']=1
							r['SL_order_id']=response_json['data']['order_id']
							r['SL_order_api_key']=""
							r['SL_order_access_token']=""
							pipeline.set(redis_key,ujson.dumps(r))
							if(int(ttl) > -1):
								pipeline.expire(redis_key,ttl)
						except:
							print traceback.format_exc()
							# r = {}
							return False

					curr_time = datetime.datetime.now()
					
					notification_msg = "You placed SL-M order"
					notification_data = {'notification-type':'order-placement','notification_msg':notification_msg,'action_type':transaction_type,
						'trigger_time':int(curr_time.strftime('%s')),
						'trigger_price':trigger_price,
						'segment':segment,'symbol':symbol,
						'seg':segment,'sym':symbol,'quantity':quantity,'broker':broker,'notification_time':curr_time.isoformat(),
						'user_uuid':user_uuid,
						'algo_uuid':algo_uuid,
						'algo_name':algo_name,
						'deployment_uuid':deployment_uuid,
						"trigger_price":trigger_price,
						'open_notif':False
						}

					order_stop_log = models.OrderLog(
								user_uuid=user_uuid,
								algo_uuid=algo_uuid,
								deployment_uuid=deployment_uuid,
								log_tag="User action",
								log_message=notification_msg,
								notification_data=notification_data
								)
					order_stop_log.save()

					curr_time = datetime.datetime.now()

					# notification_msg = "Order sent to exchange"
					# notification_data = {'notification-type':'order-placement','notification_msg':notification_msg,'action_type':transaction_type,
					# 	'trigger_time':int(curr_time.strftime('%s')),
					# 	'trigger_price':0,
					# 	'segment':segment,'symbol':symbol,
					# 	'seg':segment,'sym':symbol,'quantity':quantity,'broker':broker,'notification_time':curr_time.isoformat(),
					# 	'user_uuid':user_uuid,
					# 	'algo_uuid':algo_uuid,
					# 	'algo_name':algo_name,
					# 	'deployment_uuid':deployment_uuid,
					# 	'open_notif':False
					# 	}

					# order_stop_log = models.OrderLog(
					# 			user_uuid=user_uuid,
					# 			algo_uuid=algo_uuid,
					# 			deployment_uuid=deployment_uuid,
					# 			log_tag="At Exchange",
					# 			log_message=notification_msg,
					# 			notification_data=notification_data
					# 			)
					# order_stop_log.save()
					pipeline.execute()
					return JsonResponse({'status':'success'})
				except:
					print traceback.format_exc()
					return JsonResponse({'status':'error'})
			else:
				return JsonResponse({'status':'error','order_response':response_json,'response_code':status_code,"error_msg":response_json.get("message","Unexpected error")})
		else:
			return JsonResponse({'status':'error','response_code':status_code,'error-type':'Session expired, re-login required',"error_msg":response_json.get("message",'Session expired, re-login required')})
	return JsonResponse({'status':'error'})

def ams_place_order_tpsl_new(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error_msg':'auth'})
	if request.method == "POST":
		notification_uuid = request.POST.get('notification_uuid','')
		if notification_uuid == '':
			return JsonResponse({"status":"error",'error-type':'notifid','error_msg':'notifid'})
		
		try:
			con = get_redis_connection("default")
			notifs = con.get('today_notification:'+user_uuid)
			notifs = eval(notifs)
			notif_used = notifs['used'].get(notification_uuid,0)
			if notif_used:
				return JsonResponse({"status":"error","error_msg":"Notification used"})		
		except:
			print traceback.format_exc()

		deployment_uuid = request.POST.get('deployment_uuid','')
		algo_uuid = request.POST.get('algo_uuid','')
		algo_name = request.POST.get('algo_name','')
		token = request.POST.get('token','')
		# instrument = fetch_with_token(token)
		# if instrument==None:
		# 	return JsonResponse({"status":"error",'instrument':'none','params':[token]})

		con = get_redis_connection('default')
		key_prefix = ':'.join(['deployed',user_uuid,'*',deployment_uuid])
		deployed_keys = con.keys(key_prefix)
		# print 'zzzzzzzzzzzzzzzzzzzzzz11111111111',key_prefix
		if(len(deployed_keys)==0):
			print 'deployment_uuid not present'
			return JsonResponse({"status":"error",'error-type':'Strategy not live','error_msg':'Strategy not live'})

		# exchange = instrument['results'][10]
		# symbol = instrument['results'][2]
		# segment = instrument['results'][9]
		transaction_type = request.POST.get('transaction_type','')
		order_type = request.POST.get('order_type','')
		tpsl_key = request.POST.get('tpsl_key','')
		tpsl_key_list = tpsl_key.split(":")
		if len(tpsl_key_list)<11:
			return JsonResponse({"status":"error","error_msg":"Invalid order request"})
		segment = tpsl_key_list[14]
		symbol = tpsl_key_list[13]
		if segment!='':
			if segment=='CDS-FUT':
				exchange = 'CDS'
			elif segment=='MCX':
				exchange = 'MCX'
			elif segment == 'NFO-FUT':
				 exchange ='NFO'
			elif segment == "NSE":
				exchange = 'NSE'
			elif segment=="NFO":
				exchange="NFO"
				if str(symbol).endswith("CE") or str(symbol).endswith("PE"):
					segment = 'NFO-OPT'
				else:
					segment = 'NFO-FUT'
			elif segment == 'NFO-OPT':
				 exchange ='NFO'
		else:
			return JsonResponse({"status":"error","error_msg":"Unknown segment"})
		# if order_type=='BUY':
		# 	order_type='SELL'
		# elif order_type=='SELL':
		# 	order_type='BUY'

		quantity = int(request.POST.get('quantity',0))
		product = request.POST.get('product','')
		validity = request.POST.get('validity','')

		# new parameters handling
		variety = request.POST.get('variety','REGULAR')
		price = float(request.POST.get('price',0.0))
		squareoff = float(request.POST.get('squareoff',0.0))
		stoploss = float(request.POST.get('stoploss',0.0))
		trailing_stoploss = float(request.POST.get('trailing_stoploss',0.0))
		notif_state = request.POST.get('notif_state','')

		deployment_uuid = request.POST.get('deployment_uuid','')

		if deployment_uuid == '':
			print 'deployment_uuid not present'
			return JsonResponse({"status":"error",'error_msg':'auth'})

		user_broker_id = request.session.get('user_broker_id','')
		broker = request.session.get("broker","zerodha")

		if  user_broker_id=='':
			print 'probably kite login popup'
			return JsonResponse({"status":"error","error":"BrokerLogin",'error_msg':'BrokerLogin'})

		payload = {
		  # "api_key":settings.KITE_API_KEY,
		  # "access_token":access_token,
		  "tradingsymbol":symbol,
		  "exchange":exchange,
		  "transaction_type":transaction_type,
		  "order_type":order_type,
		  "quantity":quantity,
		  "product":product,
		  "validity":validity
		}

		payload = {
		  "symbol":symbol,
		  "tradingsymbol":symbol,
		  "exchange":exchange,
		  "segment":segment,
		  "transaction_type":transaction_type,
		  "order_type":order_type,
		  "quantity":str(quantity),
		  "product":product,
		  "validity":validity,
		  "strategy_code": strategy_code,
		  # "trigger_price":str(trigger_price),
		  "user_uuid":user_uuid,
		  "is_amo": False,
		  "service":request.session.get("broker","zerodha")
		}

		if order_type=='LIMIT':
			payload['price']=str(price)

		if variety.lower()=='bo':
			payload['price']=str(price)
			payload['variety']=variety.lower()
			payload['squareoff']=str(squareoff)
			payload['stoploss']=str(stoploss)
			if trailing_stoploss!=0:
				payload['trailing_stoploss']=str(trailing_stoploss)

		if variety.lower()=='amo':
			payload["is_amo"]=True
		# print payload
		url = AMS_ROOT_URL + "/"+ version+ "/orders/create"
		# payload = ujson.dumps({"user_uuid": user_uuid,"service_name": request.session.get("broker","zerodha")})
		
		headers = base_header
		response = requests.request("POST", url, data=ujson.dumps(payload), headers=headers)
		success,response_json,status_code = reponse_handler(response)
		if status_code == 200:
			if 'price' in payload.keys():
				payload['price'] = float(payload['price'])
			if 'stoploss' in payload.keys():
				payload['stoploss'] = float(payload['stoploss'])
			if 'squareoff' in payload.keys():
				payload['squareoff'] = float(payload['squareoff'])
			if 'disclosed_quantity' in payload.keys():
				payload['disclosed_quantity'] = int(payload['disclosed_quantity'])
			if 'trailing_stoploss' in payload.keys():
				payload['trailing_stoploss'] = float(payload['trailing_stoploss'])
			if 'trigger_price' in payload.keys():
				payload['trigger_price'] = float(payload['trigger_price'])
			if 'quantity' in payload.keys():
				payload['quantity'] = int(payload['quantity'])
			if response_json.get('data',None) is not None:
				try:
					if len(deployed_keys)==1 and notif_state.lower()=='entry':
						dep_obj = con.get(deployed_keys[0])
						dep_obj_ttl = con.ttl(deployed_keys[0])
						dep_obj = eval(dep_obj)
						if variety!=dep_obj['algo_obj'].get('variety','REGULAR'):
							print('updating variety to',variety)
							dep_obj['algo_obj']['variety'] = variety
							con.set(deployed_keys[0],json.dumps(dep_obj))
							con.expire(deployed_keys[0],dep_obj_ttl)
					#update holdings for algorithm using webhook 
					# holding = HoldingsForAlgorithm.objects.get(user_uuid=user_uuid,deployment_uuid=deployment_uuid)
					# holding.position[segment+'_'+symbol]['qty']=
					payload['segment']=segment
					broker_order = models.BrokerOrder(user_uuid=user_uuid,
						algo_uuid=algo_uuid,
						# algo_name=algo_name,
						deployment_uuid=deployment_uuid,
						order_id=response_json['data']['order_id'],
						order_payload = payload
					)
					broker_order.save()

					pipeline = con.pipeline()

					keys = get_deployment_keys({"user_uuid":user_uuid,"deployment_uuid":deployment_uuid}) #con.keys('deployed:'+user_uuid+':*:'+deployment_uuid)
					if len(keys)>0:
						redis_key = keys[0]
					else:
						redis_key = None

					notifs['used'][notification_uuid]=1 # mark notitification as used(actioned upon)
					con.set('today_notification:'+user_uuid,ujson.dumps(notifs))
					ex_time = int((datetime.datetime.now().replace(hour=3,minute=0,second=0)+datetime.timedelta(days=1)).strftime('%s')) - int(datetime.datetime.now().strftime('%s'))
					con.expire('today_notification:'+user_uuid,ex_time)

					if redis_key:
						r = con.get(redis_key)
						try:
							if r:
								r = json.loads(r)
								r['frequency_utilized']=r.get('frequency_utilized',0)+1
						except:
							print traceback.format_exc()
							# r = {}
							pass
						# print r
						# pipeline.set(redis_key,r)
						# pipeline.expire(redis_key,1)
						# pipeline.publish(settings.ENV+'-deployment_channel','DEL:'+redis_key)

					curr_time = datetime.datetime.now()
					
					notification_msg = "You ordered"
					notification_data = {'notification-type':'order-placement','notification_msg':notification_msg,'action_type':transaction_type,
						'trigger_time':int(curr_time.strftime('%s')),
						'trigger_price':0,
						'segment':segment,'symbol':symbol,
						'seg':segment,'sym':symbol,'quantity':quantity,'broker':broker,'notification_time':curr_time.isoformat(),
						'user_uuid':user_uuid,
						'algo_uuid':algo_uuid,
						'algo_name':algo_name,
						'deployment_uuid':deployment_uuid,
						'open_notif':False,
						'order_type':order_type,
						'price':price
						}

					order_stop_log = models.OrderLog(
								user_uuid=user_uuid,
								algo_uuid=algo_uuid,
								deployment_uuid=deployment_uuid,
								log_tag="User action",
								log_message=notification_msg,
								notification_data=notification_data
								)
					order_stop_log.save()

					curr_time = datetime.datetime.now()
					notification_msg = "Order sent to exchange"
					notification_data = {'notification-type':'order-placement','notification_msg':notification_msg,'action_type':transaction_type,
						'trigger_time':int(curr_time.strftime('%s')),
						'trigger_price':0,
						'segment':segment,'symbol':symbol,
						'seg':segment,'sym':symbol,'quantity':quantity,'broker':broker,'notification_time':curr_time.isoformat(),
						'user_uuid':user_uuid,
						'algo_uuid':algo_uuid,
						'algo_name':algo_name,
						'deployment_uuid':deployment_uuid,
						'open_notif':False,
						'order_type':order_type,
						'price':price
						}

					order_stop_log = models.OrderLog(
								user_uuid=user_uuid,
								algo_uuid=algo_uuid,
								deployment_uuid=deployment_uuid,
								log_tag="At Exchange",
								log_message=notification_msg,
								notification_data=notification_data
								)
					order_stop_log.save()
					if tpsl_key!='' and ':IR1:' not in tpsl_key:
						pipeline.delete(tpsl_key)
					pipeline.execute()
					return JsonResponse({'status':'success'})
				except:
					print traceback.format_exc()
					return JsonResponse({'status':'error','error_msg':'Unknown error'})
			else:
				error_msg = response_json.get("message","auth")
				return JsonResponse({'status':'error','order_response':response_json,'response_code':response.status_code,"error_msg":error_msg})
		elif response.status_code == 403:
			return JsonResponse({'status':'error','response_code':status_code,'error-type':'Session expired, re-login required',"error_msg":response_json.get("message",'Session expired, re-login required')})
		elif response.status_code == 428:
			return JsonResponse({'status':'error','response_code':status_code,'error_msg':'Order needs authorisation at depository, please visit broker trading terminal to place the order','error-type':'Order needs authorisation at depository, please visit broker trading terminal to place the order','error_url':""})
		else:
			return JsonResponse({'status':'error','response_code':response.status_code,'error-type':'Session expired, re-login required','error_msg':response_json.get('message',"Unknown error")})
		return JsonResponse({'status':'error','error':'none','error_msg':'none'})
	return JsonResponse({'status':'error'})

def ams_place_order_new(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth'})
	if request.method == "POST":
		try:
			print"here"
			notification_uuid = request.POST.get('notification_uuid','')
			if notification_uuid == '':
				return JsonResponse({"status":"error",'error-type':'notifid'})
			try:
				con = get_redis_connection("default")
				notifs = con.get('today_notification:'+user_uuid)
				notifs = eval(notifs)
				notif_used = notifs['used'].get(notification_uuid,0)
				if notif_used:
					return JsonResponse({"status":"error","error_msg":"Notification used"})
			except:
				print traceback.format_exc()

			deployment_uuid = request.POST.get('deployment_uuid','')
			algo_uuid = request.POST.get('algo_uuid','')
			algo_name = request.POST.get('algo_name','')
			exchange = request.POST.get('exch','').upper()
			symbol = request.POST.get('sym','')
			segment = request.POST.get('seg','')
			transaction_type = request.POST.get('transaction_type','')
			order_type = request.POST.get('order_type','MARKET')
			quantity = int(request.POST.get('quantity',0))
			product = request.POST.get('product','')
			validity = request.POST.get('validity','')

			# new parameters handling
			variety = request.POST.get('variety','REGULAR')
			price = float(request.POST.get('price',0.0))
			squareoff = float(request.POST.get('squareoff',0.0))
			stoploss = float(request.POST.get('stoploss',0.0))
			trailing_stoploss = float(request.POST.get('trailing_stoploss',0.0))
			
			notif_state = request.POST.get('notif_state','')
			
			deployment_uuid = request.POST.get('deployment_uuid','')

			if deployment_uuid == '':
				print 'deployment_uuid not present'
				return JsonResponse({"status":"error",'error-type':'depid'})

			con = get_redis_connection('default')
			key_prefix = ':'.join(['deployed',user_uuid,'*',deployment_uuid])
			deployed_keys = get_deployment_keys({"user_uuid":user_uuid,"deployment_uuid":deployment_uuid,"status":0})# con.keys(key_prefix)
			# print 'zzzzzzzzzzzzzzzzzzzzzz11111111111',key_prefix
			if(len(deployed_keys)==0):
				print 'deployment_uuid not present'
				return JsonResponse({"status":"error",'error-type':'Strategy not live','error_msg':'Strategy not live'})

			access_token = request.session.get('access_token','')
			public_token = request.session.get('public_token','')
			user_broker_id = request.session.get('user_broker_id','')
			broker = request.session.get("broker","zerodha")

			if user_broker_id=='':
				print 'probably kite login popup'
				return JsonResponse({"status":"error",'error-type':'noauth'})

			if exchange=='CDS-FUT':
				exchange="CDS"
			elif exchange=='NFO-OPT':
				exchange="NFO"
			elif exchange=='NFO-FUT':
				exchange="NFO"
				
			payload = {
			  # "api_key":settings.KITE_API_KEY,
			  # "access_token":access_token,
			  "tradingsymbol":symbol,
			  "exchange":exchange,
			  "transaction_type":transaction_type,
			  "order_type":order_type,
			  "quantity":quantity,
			  "product":product,
			  "validity":validity
			}

			payload = {
				"symbol":symbol,
				"tradingsymbol":symbol,
				"exchange":exchange,
				"segment":segment,
				"transaction_type":transaction_type,
				"order_type":order_type,
				"quantity":str(quantity),
				"product":product,
				"validity":validity,
				"strategy_code": strategy_code,
				# "trigger_price":str(trigger_price),
				"user_uuid":user_uuid,
				"is_amo": False,
				"service":request.session.get("broker","zerodha")
			}

			if order_type=='LIMIT':
				payload['price']=str(price)

			if variety.lower()=='bo':
				payload['variety']=variety.lower()
				payload['squareoff']=str(squareoff)
				payload['stoploss']=str(stoploss)
				if trailing_stoploss!=0:
					payload['trailing_stoploss']=str(trailing_stoploss)

			if variety.lower()=='amo':
				payload["is_amo"]=True
			# print payload
			url = AMS_ROOT_URL + "/"+ version+ "/orders/create"
			# payload = ujson.dumps({"user_uuid": user_uuid,"service_name": request.session.get("broker","zerodha")})
			
			headers = base_header
			response = requests.request("POST", url, data=ujson.dumps(payload), headers=headers)
			success,response_json,status_code = reponse_handler(response)
			print("ams_place_order_new->",response_json,response.text,payload)
			if status_code == 200:
				if 'price' in payload.keys():
					payload['price'] = float(payload['price'])
				if 'stoploss' in payload.keys():
					payload['stoploss'] = float(payload['stoploss'])
				if 'squareoff' in payload.keys():
					payload['squareoff'] = float(payload['squareoff'])
				if 'disclosed_quantity' in payload.keys():
					payload['disclosed_quantity'] = int(payload['disclosed_quantity'])
				if 'trailing_stoploss' in payload.keys():
					payload['trailing_stoploss'] = float(payload['trailing_stoploss'])
				if 'trigger_price' in payload.keys():
					payload['trigger_price'] = float(payload['trigger_price'])
				if 'quantity' in payload.keys():
					payload['quantity'] = int(payload['quantity'])
				if response_json.get('data',None) is not None:
					try:
						if len(deployed_keys)==1 and notif_state.lower()=='entry':
							dep_obj = con.get(deployed_keys[0])
							dep_obj_ttl = con.ttl(deployed_keys[0])
							dep_obj = eval(dep_obj)
							if variety!=dep_obj['algo_obj'].get('variety','REGULAR'):
								print('updating variety to',variety)
								dep_obj['algo_obj']['variety'] = variety
								con.set(deployed_keys[0],json.dumps(dep_obj))
								con.expire(deployed_keys[0],dep_obj_ttl)
						#update holdings for algorithm using webhook 
						# holding = HoldingsForAlgorithm.objects.get(user_uuid=user_uuid,deployment_uuid=deployment_uuid)
						# holding.position[segment+'_'+symbol]['qty']=
						payload['segment']=segment
						broker_order = models.BrokerOrder(user_uuid=user_uuid,
							algo_uuid=algo_uuid,
							# algo_name=algo_name,
							deployment_uuid=deployment_uuid,
							order_id=response_json['data']['order_id'],
							order_payload = payload
						)
						broker_order.save()

						pipeline = con.pipeline()

						keys = deployed_keys #get_deployment_keys({"user_uuid":user_uuid,"deployment_uuid":deployment_uuid}) #con.keys('deployed:'+user_uuid+':*:'+deployment_uuid)
						if len(keys)>0:
							redis_key = keys[0]
						else:
							redis_key = None

						notifs['used'][notification_uuid]=1 # mark notitification as used(actioned upon)
						con.set('today_notification:'+user_uuid,ujson.dumps(notifs))
						ex_time = int((datetime.datetime.now().replace(hour=3,minute=0,second=0)+datetime.timedelta(days=1)).strftime('%s')) - int(datetime.datetime.now().strftime('%s'))
						con.expire('today_notification:'+user_uuid,ex_time)

						# if redis_key:
						# 	r = con.get(redis_key)
						# 	try:
						# 		r = json.loads(r)
						# 		r['frequency_utilized']=r.get('frequency_utilized',0)+1
						# 	except:
						# 		print traceback.format_exc()
						# 		# r = {}
						# 		pass
							# print r
							# pipeline.set(redis_key,r)
							# pipeline.expire(redis_key,1)
							# pipeline.publish(settings.ENV+'-deployment_channel','DEL:'+redis_key)
						curr_time = datetime.datetime.now()
						
						notification_msg = "You ordered"
						notification_data = {'notification-type':'order-placement','notification_msg':notification_msg,'action_type':transaction_type,
							'trigger_time':int(curr_time.strftime('%s')),
							'trigger_price':0,
							'segment':segment,'symbol':symbol,
							'seg':segment,'sym':symbol,'quantity':quantity,'broker':broker,'notification_time':curr_time.isoformat(),
							'user_uuid':user_uuid,
							'algo_uuid':algo_uuid,
							'algo_name':algo_name,
							'deployment_uuid':deployment_uuid,
							'open_notif':False,
							'order_type':order_type,
							'price':price
							}

						order_stop_log = models.OrderLog(
									user_uuid=user_uuid,
									algo_uuid=algo_uuid,
									deployment_uuid=deployment_uuid,
									log_tag="User action",
									log_message=notification_msg,
									notification_data=notification_data
									)
						order_stop_log.save()

						curr_time = datetime.datetime.now()

						notification_msg = "Order sent to exchange"
						notification_data = {'notification-type':'order-placement','notification_msg':notification_msg,'action_type':transaction_type,
							'trigger_time':int(curr_time.strftime('%s')),
							'trigger_price':0,
							'segment':segment,'symbol':symbol,
							'seg':segment,'sym':symbol,'quantity':quantity,'broker':broker,'notification_time':curr_time.isoformat(),
							'user_uuid':user_uuid,
							'algo_uuid':algo_uuid,
							'algo_name':algo_name,
							'deployment_uuid':deployment_uuid,
							'open_notif':False,
							'order_type':order_type,
							'price':price
							}

						order_stop_log = models.OrderLog(
									user_uuid=user_uuid,
									algo_uuid=algo_uuid,
									deployment_uuid=deployment_uuid,
									log_tag="At Exchange",
									log_message=notification_msg,
									notification_data=notification_data
									)
						order_stop_log.save()
						pipeline.execute()
						return JsonResponse({'status':'success'})
					except:
						print traceback.format_exc()
						return JsonResponse({'status':'error'})
				else:
					error_msg = response_json.get("message","")
					return JsonResponse({'status':'error','order_response':response_json,'response_code':response.status_code,"error_msg":error_msg})
			elif response.status_code==403:
				return JsonResponse({'status':'error','response_code':response.status_code,'error-type':'Session expired, re-login required','error_msg':'Session expired, re-login required'})
			elif response.status_code==428:
				return JsonResponse({'status':'error','response_code':response.status_code,'error_msg':'Order needs authorisation at depository, please visit broker trading terminal to place the order','error-type':'Order needs authorisation at depository, please visit broker trading terminal to place the order','error_url':""})
			else:
				return JsonResponse({'status':'error','response_code':response.status_code,'error-type':'Session expired, re-login required','error_msg':response_json.get('message',"Unknown error")})
			return JsonResponse({'status':'error'})
		except:
			print traceback.format_exc()

	return JsonResponse({'status':'error'})

def ams_cancel_order_click(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		return JsonResponse({"status":"success",'valid':True,'backtest':25,'deployments_remaining':5})
	if not user_is_auth:
		return JsonResponse({"status":"error","error-type":"auth","error_msg":"Session expired, re-login required"})

	if request.method!='POST':
		return JsonResponse({"status":"error","error-type":"method"})
	
	# checking subscription duration is valid
	try:
		order_id = request.POST.get('order_id')
		parent_order_id = request.POST.get('parent_order_id','')
		variety = request.POST.get('variety','REGULAR')
		# headers = {}
		# if settings.KITE_HEADER == True:
		# 	headers = {"X-Kite-Version":"3"}
		# 	auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
		# 	headers["Authorization"] = "token {}".format(auth_header)
		# if parent_order_id=='' or parent_order_id==order_id or variety.upper()=='REGULAR':
		# 	response = requests.delete("https://api-partners.kite.trade/orders/regular/{}?api_key={}&access_token={}".format(order_id,settings.KITE_API_KEY,request.session.get('access_token','')),headers=headers)
		# else:
		# 	response = requests.delete("https://api-partners.kite.trade/orders/{}/{}?parent_order_id={}&api_key={}&access_token={}".format(variety.lower(),order_id,parent_order_id,settings.KITE_API_KEY,request.session.get('access_token','')),headers=headers)

		url = AMS_ROOT_URL + "/"+ version+ "/orders/cancel"
		payload = {"user_uuid": user_uuid,"service": request.session.get("broker","zerodha"),"is_amo":False,"order_id":order_id}
		if variety.lower()=='amo':
			payload["is_amo"]=True

		payload = ujson.dumps(payload) 
		
		headers = base_header
		response = requests.request("POST", url, data=payload, headers=headers)
		success,response_json,status_code = reponse_handler(response)
		if status_code == 200:
			if response_json.get('data',None) is not None:
				return JsonResponse({"status":"success",'msg':'Order cancelled'})
		elif status_code==403:
			return JsonResponse({'status':'error','response_code':status_code,'error-type':'Session expired, re-login required','error_msg':'Session expired, re-login required'})
		else:
			return JsonResponse({'status':'error','response_code':status_code,'error-type':'Session expired, re-login required','error_msg':response_json.get('message',"Unknown error")})
	except:
		print traceback.format_exc()
	return JsonResponse({"status":"error"})

def ams_fetch_dashboard_funds(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True

	if not user_is_auth:
		return JsonResponse({"status":"error","error":"Login required, session expired"})
	try:
		url = AMS_ROOT_URL + "/"+ version+ "/get_rms_limit"
		payload = ujson.dumps({"user_uuid": user_uuid,"service": request.session.get("broker","zerodha")})
		
		headers = base_header
		response = requests.request("POST", url, data=payload, headers=headers)
		print("response",response.text,payload,url)
		success,response_json,status_code = reponse_handler(response)
		if status_code == 200:
			if response_json.get('data',None) is not None:
				# response_json = json.loads(response.text)
				# equity_data = response_json['data']['equity']
				# available_balance = equity_data['net']
				# margins_used = equity_data['utilised']['debits']
				# account_value = equity_data['available']['cash']

				# commodity_data = response_json['data']['commodity']
				# commodity_available_balance = commodity_data['net']
				# commodity_margins_used = commodity_data['utilised']['debits']
				# commodity_account_value = commodity_data['available']['cash']
				try:
					models.UserFunds.objects(user_uuid=user_uuid).update_one(set__funds_object=response_json['data'], upsert=True)
				except:
					print traceback.format_exc()
				if request.session.get("broker","")=="5paisa" and response_json.get('data',None) is not None:
					response_json['data']['account_value']=response_json['data'].get('ALB',0)
					response_json['data']['available_balance']=response_json['data'].get('AvailableMargin',0)
					response_json['data']['margins_used']=response_json['data'].get('Mgn4Position',0)

				return JsonResponse({"status":"success",'funds':response_json.get('data')})
		elif status_code==403:
			return JsonResponse({'status':'error','response_code':status_code,'error-type':'Session expired, re-login required','error_msg':'Session expired, re-login required'})
		else:
			return JsonResponse({'status':'error','response_code':status_code,'error-type':'Session expired, re-login required','error_msg':response_json.get('message',"Unknown error")})
	except:
		print traceback.format_exc()
	return JsonResponse({"status":"error","error":"Login required, session expired","error_msg":"Login required, session expired"})

def ams_exit_all(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error"})
	if request.method == "POST":
		exchange = request.POST.get('exchange','')
		symbol = request.POST.get('symbol','')
		segment = request.POST.get('segment','')
		order_type = request.POST.get('order_type','')
		quantity = int(request.POST.get('quantity',0))
		trigger_price = int(request.POST.get('trigger_price',0))
		variety = request.POST.get('variety','REGULAR').lower()
		product = request.POST.get('product','')
		validity = request.POST.get('validity','DAY')
		price = request.POST.get('price',"0.0")

		if quantity == 0:
			print 'quantity not present'
			return JsonResponse({"status":"error"})

		access_token = request.session.get('access_token','')
		public_token = request.session.get('public_token','')
		user_broker_id = request.session.get('user_broker_id','')

		if user_broker_id=='':
			print 'probably kite login popup'
			return JsonResponse({"status":"error"})

		transaction_type = ''
		if(quantity>0):
			transaction_type='SELL'
		elif(quantity<0):
			transaction_type='BUY'

		payload = {
		  # "api_key":settings.KITE_API_KEY,
		  # "access_token":access_token,
		  "tradingsymbol":symbol,
		  "exchange":exchange,
		  "transaction_type":transaction_type,
		  "order_type":order_type,
		  "quantity":abs(quantity),
		  "product":product,
		  "validity":validity
		}

		if symbol.endswith("-EQ") and exchange=="NSE":
			symbol = symbol.replace("-EQ","")

		if segment=='' and exchange=='CDS':
			segment = 'CDS-FUT'
		if exchange=='CDS-FUT':
			segment = 'CDS-FUT'
			exchange = 'CDS'
		elif segment=='' and exchange=='MCX':
			segment = 'MCX'
		elif segment=='' and exchange=='NFO':
			if str(symbol).endswith("CE") or str(symbol).endswith("PE"):
				segment = 'NFO-OPT'
			else:
				segment = 'NFO-FUT'
		elif segment == '':
			segment = 'NSE'

		payload = {
			"symbol":symbol,
			"exchange":exchange,
			"tradingsymbol":symbol,
			"segment":segment,
			"transaction_type":transaction_type,
			"order_type":order_type,
			"quantity":str(abs(quantity)),
			"product":product,
			"validity":validity,
			"strategy_code": strategy_code,
			"trigger_price":str(trigger_price),
			"user_uuid":user_uuid,
			"is_amo": False,
			"service":request.session.get("broker","zerodha")
		}

		if order_type =='LIMIT':
			try:
				payload['price']=str(float(price))
			except:
				return JsonResponse({"status":"error","error_msg":"Invalid price"})

		if variety.lower()=='amo':
			payload["is_amo"]=True

		# print payload
		url = AMS_ROOT_URL + "/"+ version+ "/orders/create"
		# payload = ujson.dumps({"user_uuid": user_uuid,"service_name": request.session.get("broker","zerodha")})
		
		headers = base_header
		response = requests.request("POST", url, data=ujson.dumps(payload), headers=headers)
		success,response_json,status_code = reponse_handler(response)
		print(payload,response_json)
		if status_code == 200:
			if response_json.get('data',None) is not None:
				try:
					deployed_algos = models.DeployedAlgorithm.objects.filter(user_uuid=user_uuid,segment_symbol=segment+"_"+symbol,algo_obj__product=product,status=0)
					# print deployed_algos,exchange
					try:
						if len(deployed_algos)>0:
							broker_order = models.BrokerOrder(user_uuid=user_uuid,
								deployment_uuid=deployed_algos[0].deployment_uuid,
								algo_uuid=deployed_algos[0].algo_uuid,
								algo_name=deployed_algos[0].algo_name,
								order_id=response_json['data']['order_id'],
								order_payload = {
									"api_key":"",
									"access_token":"",
									"tradingsymbol":symbol,
									"segment":segment,
									"exchange":exchange,
									"transaction_type":transaction_type,
									"order_type":order_type,
									"quantity":abs(quantity),
									"product":product,
									"validity":validity,
									"price":price
								}
							)
							broker_order.save()
					except:
						print(traceback.format_exc())

					for d in deployed_algos:
						deployment_uuid = d.deployment_uuid
						models.DeployedAlgorithm.objects(user_uuid=user_uuid,deployment_uuid=deployment_uuid).update_one(status=-1)

						con = get_redis_connection('default')
						key_prefix = ':'.join(['deployed',user_uuid,'*',deployment_uuid])
						deployed_keys = con.keys(key_prefix)
						pipe = con.pipeline()
						for keys in deployed_keys:
							algo_obj = con.get(keys)
							if algo_obj is not None: # remove any associated SL-M 
								try:
									try:
										algo_obj = eval(algo_obj)
									except:
										algo_obj = ujson.loads(algo_obj) 
									SL_placed = algo_obj.pop('SL_placed','')
									SL_order_id = algo_obj.pop('SL_order_id','')
									SL_order_api_key = algo_obj.pop('SL_order_api_key','')
									SL_order_access_token = algo_obj.pop('SL_order_access_token','')
									resp = requests.delete("https://api-partners.kite.trade/orders/regular/{}?api_key={}&access_token={}".format(SL_order_id,SL_order_api_key,SL_order_access_token),headers=headers)
								except:
									print traceback.format_exc()
							pipe.delete(keys)
							pipe.publish(settings.ENV+'-deployment_channel','DEL:'+keys) # update websocket worker
						if deployment_uuid!='':
							key_prefix_deployed = 'deployed:'+user_uuid+':*:'+deployment_uuid
							key_prefix_price_trigger = user_uuid+':'+deployment_uuid+':PRICETRIGGER:*'
							deployment_key = con.keys(key_prefix_deployed)
							for k in deployment_key:
								pipe.delete(k) # delete the algo from redis
							price_trigger_key = con.keys(key_prefix_price_trigger)
							for k in price_trigger_key:
								pipe.delete(k) # delete any associate price triggers
						res = pipe.execute()
					return JsonResponse({"status":"success"})
				except:
					print traceback.format_exc()
					return JsonResponse({"status":"error"})
				#update holdings for algorithm using webhook 
				# holding = HoldingsForAlgorithm.objects.get(user_uuid=user_uuid,deployment_uuid=deployment_uuid)
				# holding.position[segment+'_'+symbol]['qty']=
				# broker_order = models.BrokerOrder(user_uuid=user_uuid,
				# 	deployment_uuid=deployment_uuid,
				# 	algo_uuid=algo_uuid,
				# 	algo_name=algo_name,
				# 	order_id=response_json['data']['order_id'],
				# 	order_payload = {
				# 		"api_key":settings.KITE_API_KEY,
				# 		"access_token":access_token,
				# 		"tradingsymbol":symbol,
				# 		"segment":segment,
				# 		"exchange":exchange,
				# 		"transaction_type":transaction_type,
				# 		"order_type":order_type,
				# 		"quantity":quantity,
				# 		"product":product,
				# 		"validity":validity
				# 	}
				# )
				# broker_order.save()

				# con = get_redis_connection("default")
				# pipeline = con.pipeline()

				# keys = con.keys('deployed:'+user_uuid+':*:'+deployment_uuid)
				# if len(keys)>0:
				# 	redis_key = keys[0]
				# else:
				# 	redis_key = None

				# try:
				# 	if redis_key:
				# 		pipeline.delete(redis_key)
				# 		pipeline.expire(redis_key,1)
				# 		pipeline.publish(settings.ENV+'-deployment_channel','DEL:'+redis_key)
				# 		del_keys =  con.keys(user_uuid+':'+deployment_uuid+':PRICETRIGGER:*:IR1:*')
				# 		if len(del_keys)==1:
				# 			pipeline.delete(del_keys[0])

				# 	if deployment_uuid!='':
				# 		key_prefix_deployed = 'deployed:'+user_uuid+':*:'+deployment_uuid
				# 		key_prefix_price_trigger = user_uuid+':'+deployment_uuid+':PRICETRIGGER:*'
				# 		deployment_key = con.keys(key_prefix_deployed)
				# 		for k in deployment_key:
				# 			pipeline.delete(k)
				# 		price_trigger_key = con.keys(key_prefix_price_trigger)
				# 		for k in price_trigger_key:
				# 			pipeline.delete(k)

				# 	deployed_algo = models.DeployedAlgorithm.objects.get(deployment_uuid=deployment_uuid,algo_uuid=algo_uuid)
				# 	deployed_algo.status = -1
				# 	deployed_algo.expiration_time = datetime.datetime.now()

				# 	order_stop_log = models.OrderLog(
				# 				user_uuid=user_uuid,
				# 				algo_uuid=deployed_algo.algo_uuid,
				# 				deployment_uuid=deployment_uuid,
				# 				log_tag="Force stopped",
				# 				log_message="Strategy stopped by you"
				# 				)
				# 	deployed_algo.save()
				# 	order_stop_log.save()
				# 	pipeline.execute()
				return JsonResponse({'status':'success'})
				# except:
				# 	return JsonResponse({'status':'error'})
			else:
				error_msg = response_json.get("message","")
				return JsonResponse({'status':'error','order_response':response_json,'response_code':response.status_code,"error_msg":error_msg})
		else:
			return JsonResponse({'status':'error','response_code':status_code,'error_msg':response_json.get('message','Session expired, re-login required')})
		return JsonResponse({'status':'error'})

	return JsonResponse({"status":"error","error_msg":"method"})
def ams_exit_position_now_force_stop(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error"})
	if request.method == "POST":
		deployment_uuid = request.POST.get('deployment_uuid','')
		algo_uuid = request.POST.get('algo_uuid','')
		algo_name = request.POST.get('algo_name','')
		exchange = request.POST.get('exch','')
		symbol = request.POST.get('sym','')
		segment = request.POST.get('seg','')
		transaction_type = request.POST.get('transaction_type','')
		order_type = request.POST.get('order_type','')
		quantity = int(request.POST.get('quantity',0))
		product = request.POST.get('product','')
		validity = request.POST.get('validity','')

		deployment_uuid = request.POST.get('deployment_uuid','')

		if deployment_uuid == '':
			print 'deployment_uuid not present'
			return JsonResponse({"status":"error"})

		access_token = request.session.get('access_token','')
		public_token = request.session.get('public_token','')
		user_broker_id = request.session.get('user_broker_id','')

		if exchange=='CDS-FUT':
			exchange="CDS"
		elif exchange=='NFO-OPT':
			exchange="NFO"
		elif exchange=='NFO-FUT':
			exchange="NFO"

		payload = {
		  "symbol":symbol,
		  "tradingsymbol":symbol,
		  "exchange":exchange,
		  "segment":segment,
		  "transaction_type":transaction_type,
		  "order_type":order_type,
		  "quantity":str(abs(quantity)),
		  "product":product,
		  "validity":validity,
		  "strategy_code": strategy_code,
		  "user_uuid":user_uuid,
		  "is_amo": False,
		  "service":request.session.get("broker","zerodha")
		}

		# print payload
		url = AMS_ROOT_URL + "/"+ version+ "/orders/create"
		# payload = ujson.dumps({"user_uuid": user_uuid,"service_name": request.session.get("broker","zerodha")})
		
		headers = base_header
		response = requests.request("POST", url, data=ujson.dumps(payload), headers=headers)
		success,response_json,status_code = reponse_handler(response)
		print(response_json,response.text,payload)
		if status_code == 200:
			if response_json.get('data',None) is not None:
			# if response_json['status']=="success":
				#update holdings for algorithm using webhook 
				# holding = HoldingsForAlgorithm.objects.get(user_uuid=user_uuid,deployment_uuid=deployment_uuid)
				# holding.position[segment+'_'+symbol]['qty']=
				broker_order = models.BrokerOrder(user_uuid=user_uuid,
					deployment_uuid=deployment_uuid,
					algo_uuid=algo_uuid,
					# algo_name=algo_name,
					order_id=response_json['data']['order_id'],
					order_payload = {
						"tradingsymbol":symbol,
						"segment":segment,
						"exchange":exchange,
						"transaction_type":transaction_type,
						"order_type":order_type,
						"quantity":quantity,
						"product":product,
						"validity":validity
					}
				)
				broker_order.save()

				con = get_redis_connection("default")
				pipeline = con.pipeline()

				# keys = con.keys('deployed:'+user_uuid+':*:'+deployment_uuid)
				keys = get_deployment_keys({"user_uuid":user_uuid,"deployment_uuid":deployment_uuid})
				if len(keys)>0:
					redis_key = keys[0]
				else:
					redis_key = None

				try:
					if redis_key:
						algo_obj = con.get(redis_key)
						if algo_obj is not None:
							try:
								try:
									algo_obj = eval(algo_obj)
								except:
									algo_obj = ujson.loads(algo_obj)
								SL_placed = algo_obj.pop('SL_placed','')
								SL_order_id = algo_obj.pop('SL_order_id','')
								SL_order_api_key = algo_obj.pop('SL_order_api_key','')
								SL_order_access_token = algo_obj.pop('SL_order_access_token','')
								# resp = requests.delete("https://api-partners.kite.trade/orders/regular/{}?api_key={}&access_token={}".format(SL_order_id,SL_order_api_key,SL_order_access_token),headers=headers)
								order_id = SL_order_id
								parent_order_id = ''
								variety = 'REGULAR'

								url = AMS_ROOT_URL + "/"+ version+ "/orders/cancel"
								payload = {"user_uuid": user_uuid,"service": request.session.get("broker","zerodha"),"is_amo":False,"order_id":order_id}
								if variety.lower()=='amo':
									payload["is_amo"]=True
								payload = ujson.dumps(payload) 
								
								headers = base_header
								response = requests.request("POST", url, data=payload, headers=headers)
								success,response_json,status_code = reponse_handler(response)
								# if status_code == 200:
								# 	if response_json.get('data',None) is not None:
								# 		return JsonResponse({"status":"success",'msg':'Order cancelled'})
								# elif status_code==403:
								# 	return JsonResponse({'status':'error','response_code':status_code,'error-type':'Session expired, re-login required','error_msg':'Session expired, re-login required'})
								# else:
								# 	return JsonResponse({'status':'error','response_code':status_code,'error-type':'Session expired, re-login required','error_msg':response_json.get('message',"Unknown error")})
							except:
								print traceback.format_exc()
						else:
							print(redis_key)
							# return

						pipeline.delete(redis_key)
						pipeline.expire(redis_key,1)
						pipeline.publish(settings.ENV+'-deployment_channel','DEL:'+redis_key)
						del_keys =  con.keys(user_uuid+':'+deployment_uuid+':PRICETRIGGER:*:IR1:*')
						if len(del_keys)==1:
							pipeline.delete(del_keys[0])

					if deployment_uuid!='':
						key_prefix_deployed = 'deployed:'+user_uuid+':*:'+deployment_uuid
						key_prefix_price_trigger = user_uuid+':'+deployment_uuid+':PRICETRIGGER:*'
						# deployment_key = con.keys(key_prefix_deployed)
						deployment_key = keys#con.keys(key_prefix_deployed)
						for k in deployment_key:
							pipeline.delete(k)
						price_trigger_key = con.keys(key_prefix_price_trigger)
						for k in price_trigger_key:
							pipeline.delete(k)

					deployed_algo = models.DeployedAlgorithm.objects.get(deployment_uuid=deployment_uuid,algo_uuid=algo_uuid)
					deployed_algo.status = -1
					deployed_algo.expiration_time = datetime.datetime.now()

					order_stop_log = models.OrderLog(
								user_uuid=user_uuid,
								algo_uuid=deployed_algo.algo_uuid,
								deployment_uuid=deployment_uuid,
								log_tag="Force stopped",
								log_message="Algo stopped by you"
								)
					deployed_algo.save()
					order_stop_log.save()
					pipeline.execute()
					return JsonResponse({'status':'success'})
				except:
					return JsonResponse({'status':'error'})
			else:
				error_msg = response_json.get("message","")
				return JsonResponse({'status':'error','order_response':response_json,'response_code':response.status_code,"error_msg":error_msg})
		else:
			return JsonResponse({'status':'error','response_code':response.status_code})
		return JsonResponse({'status':'error'})

def ams_fetch_open_positions(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error"})
	if request.method == "GET":
		deployment_uuid = request.GET.get('deployment_uuid','')
		if deployment_uuid == '':
			print 'deployment_uuid not present'
			return JsonResponse({"status":"error"})
		positions = models.HoldingsForAlgorithm.objects.get(deployment_uuid=deployment_uuid,user_uuid=user_uuid)
		latest_order = models.BrokerOrder.objects(deployment_uuid=deployment_uuid,user_uuid=user_uuid).order_by('-id').first()
		resp = {"status":"success","positions":positions.position,"pnl":positions.pnl,'algo_uuid':positions['algo_uuid'],'seg':positions.segment,'sym':positions.symbol,'algo_name':positions['algo_name'],'product':positions.product}
		if latest_order:
			try:
				resp['variety'] = latest_order['order_payload'].get('variety','REGULAR').upper()
				resp['order_id'] = latest_order['order_id']
				resp['parent_order_id'] = latest_order['order_status'].get('parent_order_id',resp['order_id'])
			except:
				resp['variety'] = 'REGULAR'
				print traceback.format_exc()
		return JsonResponse(resp)

	return JsonResponse({"status":"error"})

def ams_fetch_specific_position(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error"})

	if request.method!='GET':
		return JsonResponse({"status":"error"})

	headers = {}
	if settings.KITE_HEADER == True:
		headers = {"X-Kite-Version":"3"}
		auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
		headers["Authorization"] = "token {}".format(auth_header)
	url = AMS_ROOT_URL + "/"+ version+ "/get_positions"
	payload = ujson.dumps({"user_uuid": user_uuid,"service": request.session.get("broker","zerodha")})
	
	headers = base_header
	response = requests.request("POST", url, data=payload, headers=headers)
	# print(response.text,payload,url)
	# print 'request url',"https://api-partners.kite.trade/portfolio/positions/?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token',''))

	if response.status_code == 200:
		response_json = ujson.loads(response.text)
		if response_json.get('data',None) is None:
			return JsonResponse({"status":"error","error":"auth",'error_msg':response_json.get('message')})
		else:
			positions = models.PositionsOfInstrument.objects(user_uuid=user_uuid,updated_at__gte=datetime.datetime.now().replace(hour=3,minute=0,second=0))
			if positions==[]:
				return JsonResponse({"status":"success","positions":[]})
			else:
				adj_positions = []
				for n in response_json['data']['net']:
					if(n['tradingsymbol']==request.GET.get('symbol','') and n['exchange']==request.GET.get('exchange','') and n['product']==request.GET.get('product','')):
						adj_positions.append(n)
				return JsonResponse({"status":"success","positions":adj_positions})
		# else:
		# 	return JsonResponse({"status":"error","error":"response error"})
	elif response.status_code == 403:
		return JsonResponse({"status":"error","error":"auth",'error_msg':'Session expired, relogin required'})
	return JsonResponse({"status":"error"})


def ab_whats_new3(request):
	# conn = get_redis_connection("default")
	# content = conn.get('whats_new3')
	# try:
	# 	resp = json.loads(content)
	# except:
	resp = {'web': {'data': [],'img':''}, 'app': {'data': [],'img': ''}}
	return JsonResponse(resp)