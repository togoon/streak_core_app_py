from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import redirect,render
from django.middleware import csrf
from django_redis import get_redis_connection
from django.utils.http import is_safe_url
import pickle
import itertools
import ujson
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
import os
import re
from django.middleware import csrf
import os
import time
import razorpay
from cryptography.fernet import Fernet

# Client = razorpay.Client(auth=("rzp_test_9qXm8CDw4htAZX", "g6TG7jjGJeQBmtbJTITJlSFZ"))
Client = razorpay.Client(auth=("rzp_live_WB01mw43jBEnd2", "WY90FLN36iEzfJo6Xv7hmDOF"))
plans = {
						'free':
						{'daily_backtests': 50, 'subscription_tax': 0, 'subscription_plan': 'free', 'subscription_price': 0, 'plan_id': 0, 'subscription_validity_date': 7, 'daily_deploys': 5, 'subscription_total_price': 0, 'subscription_product': 'free','note':'Free trial till 30th Nov 2018','subscription_period':30,'varity':{}
						},
						'basic':{
						'daily_backtests': 200, 'subscription_tax': 90, 'subscription_plan': 'basic', 'subscription_price': 500, 'plan_id': 1, 'subscription_validity_date': 30, 'daily_deploys': 25, 'subscription_total_price': 590, 'subscription_product': 'basic','note':'Free for all Zerodha Clients till 31st July, 18','subscription_period':30,'varity':{'1':{'price':500,'tax':90,'total':590,'days_validity':29,'plan_value':500,'razor_plan_id':'plan_CTTJfQOGNL1bWh'},
				'3':{'price':1350,'tax':243,'total':1593,'days_validity':89,'plan_value':1500,'razor_plan_id':'plan_CTTJfQOGNL1bWh'},
				'6':{'price':2400,'tax':432,'total':2832,'days_validity':179,'plan_value':3000,'razor_plan_id':'plan_CTTJfQOGNL1bWh'},
				'12':{'price':4200,'tax':756,'total':4956,'days_validity':365,'plan_value':6000,'razor_plan_id':'plan_CTTJfQOGNL1bWh'}}
						},
						'premium':{
						'daily_backtests': 500, 'subscription_tax': 162, 'subscription_plan': 'premium', 'subscription_price': 900, 'plan_id': 2, 'subscription_validity_date': 30, 'daily_deploys': 50, 'subscription_total_price': 1062, 'subscription_product': 'premium','note':'Starts from 1st July, 18','subscription_period':30,'varity':{'1':{'price':900,'tax':162,'total':1062,'days_validity':29,'plan_value':900,'razor_plan_id':'plan_CTTJfQOGNL1bWh'},
				'3':{'price':2430,'tax':437.4,'total':4667.4,'days_validity':89,'plan_value':2700,'razor_plan_id':'plan_CTTJfQOGNL1bWh'},
				'6':{'price':4320,'tax':777.6,'total':5097.6,'days_validity':179,'plan_value':5400,'razor_plan_id':'plan_CTTJfQOGNL1bWh'},
				'12':{'price':7560,'tax':1360.8,'total':8920.8,'days_validity':365,'plan_value':10800,'razor_plan_id':'plan_CTTJfQOGNL1bWh'}}
						},
						'ultimate':{
						'daily_backtests': 1000, 'subscription_tax': 252, 'subscription_plan': 'ultimate', 'subscription_price': 1400, 'plan_id': 3, 'subscription_validity_date': 30, 'daily_deploys': 100, 'subscription_total_price': 1652, 'subscription_product': 'ultimate','note':'Starts from 1st July, 18','time':'30 minutes','subscription_period':30,'varity':{'1':{'price':1400,'tax':252,'total':1652,'days_validity':29,'plan_value':1400,'razor_plan_id':'plan_CTTJfQOGNL1bWh'},
				'3':{'price':3780,'tax':680.4,'total':4460.4,'days_validity':89,'plan_value':4200,'razor_plan_id':'plan_CTTJfQOGNL1bWh'},
				'6':{'price':6720,'tax':1209.6,'total':7929.6,'days_validity':179,'plan_value':8400,'razor_plan_id':'plan_CTTJfQOGNL1bWh'},
				'12':{'price':11760,'tax':2116.8,'total':13876.8,'days_validity':365,'plan_value':16800,'razor_plan_id':'plan_CTTJfQOGNL1bWh'}}
						}
				}

methods = {
		"entity": "methods",
		"card": True,
		"debit_card": True,
		"credit_card": True,
		"card_networks": {
			"AMEX": 0,
			"DICL": 1,
			"MC": 1,
			"MAES": 1,
			"VISA": 1,
			"JCB": 1,
			"RUPAY": 1,
			"BAJAJ": 0
		},
		"amex": False,
		"netbanking": {
			"AUBL": "AU Small Finance Bank",
			"ABPB": "Aditya Birla Idea Payments Bank",
			"AIRP": "Airtel Payments Bank",
			"ALLA": "Allahabad Bank",
			"ANDB": "Andhra Bank",
			"UTIB": "Axis Bank",
			"BBKM": "Bank of Bahrein and Kuwait",
			"BARB_R": "Bank of Baroda - Retail Banking",
			"BKID": "Bank of India",
			"MAHB": "Bank of Maharashtra",
			"CNRB": "Canara Bank",
			"CSBK": "Catholic Syrian Bank",
			"CBIN": "Central Bank of India",
			"CIUB": "City Union Bank",
			"CORP": "Corporation Bank",
			"COSB": "Cosmos Co-operative Bank",
			"DCBL": "DCB Bank",
			"BKDN": "Dena Bank",
			"DEUT": "Deutsche Bank",
			"DBSS": "Development Bank of Singapore",
			"DLXB": "Dhanlaxmi Bank",
			"ESFB": "Equitas Small Finance Bank",
			"FDRL": "Federal Bank",
			"HDFC": "HDFC Bank",
			"ICIC": "ICICI Bank",
			"IBKL": "IDBI",
			"IDFB": "IDFC FIRST Bank",
			"IDIB": "Indian Bank",
			"IOBA": "Indian Overseas Bank",
			"INDB": "Indusind Bank",
			"JAKA": "Jammu and Kashmir Bank",
			"JSBP": "Janata Sahakari Bank (Pune)",
			"KARB": "Karnataka Bank",
			"KVBL": "Karur Vysya Bank",
			"KKBK": "Kotak Mahindra Bank",
			"LAVB_C": "Lakshmi Vilas Bank - Corporate Banking",
			"LAVB_R": "Lakshmi Vilas Bank - Retail Banking",
			"NKGS": "NKGSB Co-operative Bank",
			"ORBC": "Oriental Bank of Commerce",
			"PMCB": "Punjab & Maharashtra Co-operative Bank",
			"PSIB": "Punjab & Sind Bank",
			"PUNB_R": "Punjab National Bank - Retail Banking",
			"RATN": "RBL Bank",
			"SRCB": "Saraswat Co-operative Bank",
			"SVCB": "Shamrao Vithal Co-operative Bank",
			"SIBL": "South Indian Bank",
			"SCBL": "Standard Chartered Bank",
			"SBBJ": "State Bank of Bikaner and Jaipur",
			"SBHY": "State Bank of Hyderabad",
			"SBIN": "State Bank of India",
			"SBMY": "State Bank of Mysore",
			"STBP": "State Bank of Patiala",
			"SBTR": "State Bank of Travancore",
			"SYNB": "Syndicate Bank",
			"TMBL": "Tamilnadu Mercantile Bank",
			"TNSC": "Tamilnadu State Apex Co-operative Bank",
			"UCBA": "UCO Bank",
			"UBIN": "Union Bank of India",
			"UTBI": "United Bank of India",
			"VIJB": "Vijaya Bank",
			"YESB": "Yes Bank"
		},
		"wallet": {
			"payzapp": True,
			"olamoney": True,
			"freecharge": True
		},
		"emi": False,
		"upi": True,
		"cardless_emi": [],
		"recurring": {
			"card": {
				"credit": [
					"MasterCard",
					"Visa"
				]
			}
		},
		"upi_intent": True
	}

redirectUrl = 'https://streak.zerodha.com/account?'


def generate_subscription(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		return JsonResponse({"status":"success",'valid':True,'backtest':100,'deployments_remaining':5})
	
	if request.method!='POST':
		return JsonResponse({"status":"error","error_msg":"Unsupport method"})
	# generates addons price for subscription along with subscription
	# or
	# generates amount to be charged to the user
	# user_uuid = "eff87bd6-bbec-4db5-809c-740b0a828253"
	# print 'request.META.items()',request.META.items()
	post_data = ujson.loads(request.body)
	plan_to_subscribe = post_data.get('plan_to_subscribe','basic').lower()
	subscription_plan = post_data.get('plan_to_subscribe','basic').lower()
	subscription_period = post_data.get('subscription_period','1').lower()
	subscription_instance = post_data.get('subscription_instance','first')
	subscription_renewal = post_data.get('subscription_renewal',True)
	subscription_change = post_data.get('subscription_change',False)
	subscription_price = post_data.get('subscription_price','')

	username = post_data.get('username','')
	contact = post_data.get('contact','')
	email = post_data.get('email','')

	if contact=="":
		contact = user_uuid
	if email == "":
		return JsonResponse({"status":"error","error_msg":"Unknown user"})
	if username=="":
		username = email

	# con = get_redis_connection("default")
	# plans = con.get('subscriptions_plans')
	available_plans = plans #ujson.loads(plans)
	price_to_charge = available_plans[subscription_plan]['varity'][subscription_period]['price']
	days_validity = available_plans[subscription_plan]['varity'][subscription_period]['days_validity']
	plan_value = available_plans[subscription_plan]['varity'][subscription_period]['days_validity']
	print (available_plans[subscription_plan]['varity'][subscription_period],user_uuid)
	plan_id = available_plans[subscription_plan]['varity'][subscription_period]['razor_plan_id']
	subscription_id = None
	addons = []
	subscription_payment_type = "checkout"
	subscription_obj = {}
	payment_id = ''
	try:
		user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)

		if subscription_period!="1":
			customer = None
			try:
				usp_objs = models.UserSubscriptionPayment.objects(user_uuid=user_uuid,subscription_payment_type="order").order_by('created_at')
				if len(usp_objs)==0:
					raise
				else:
					# print usp_objs[len(usp_objs)-1].to_json()
					customer = usp_objs[len(usp_objs)-1]["customer"]
			except:
				print(user_uuid,traceback.format_exc())
				pass
			print("user_uuid,customer",user_uuid,customer)
			if customer is None or customer=={}:
				print("customer",customer,{"name":username,"contact":contact,"email":email,"fail_existing":"0"})
				try:
					customer = Client.customer.create(data={"name":username,"contact":contact,"email":email,"fail_existing":"0"})
					print("customer",customer)
				except:
					try:
						customer = Client.customer.create(data={"name":username,"contact":contact,"email":email,"fail_existing":"0"})
						print("customer",customer)
					except:
						customer = Client.customer.create(data={"name":username,"contact":contact,"email":email,"fail_existing":"0"})
						print("customer",customer,{"name":username,"contact":contact,"email":email,"fail_existing":"0"})

			if customer.get("id","")=="":
				return JsonResponse({"status":"error","error_msg":"Unknown customer"})
			try:
				# cards = Client.token.all(customer_id=customer.get("id",""))
				url = "https://api.razorpay.com/v1/preferences"

				querystring = {"key_id":"rzp_live_WB01mw43jBEnd2","customer_id":customer.get("id","")}

				headers = {
					'Referer': "https://api.razorpay.com/v1/checkout/public"
					}
				response = requests.request("GET", url, headers=headers, params=querystring)
				print(user_uuid,response)
				response = ujson.loads(response.text)
				# print("user_uuid",user_uuid,response)
				methods = response.get('methods',{})
				cards = response['customer']['tokens']
			except:
				print user_uuid,traceback.format_exc(),customer
				cards = {
						  "entity" : "collection", 
						  "count" : 0, 
						  "items" : []
						}
		else:
			customer = {}
			cards = {
					  "entity" : "collection", 
					  "count" : 0, 
					  "items" : []
					}
			methods = {}

		current_subscription_type = user_subscription.subscription_type
		current_subscription_period = user_subscription.subscription_period
		current_subscription_validity = user_subscription.subscription_validity
		prev_subscription_validity = user_subscription.subscription_validity
		subscription_start = prev_subscription_validity
		
		current_plan = available_plans.get(user_subscription.subscription_plan,available_plans['free'])
		if user_subscription.subscription_plan!="free":
			curr_days_validity = available_plans[user_subscription.subscription_plan]['varity'][user_subscription.subscription_period].get('days_validity')
		else:
			curr_days_validity = 0 

		if user_subscription.subscription_price<11:
			current_plan = available_plans.get("free")
			current_subscription_type = 0
			current_subscription_period = "1"
		# if(current_subscription_type==0): # if free trial, then start the subscription from today
		# # print "checking subscription duration is valid"
		# 	if plan_to_subscribe['plan_id']==1:
		# 		subscription_validity = datetime.datetime.today()+datetime.timedelta(days=days_validity)#,datetime.datetime(2018, 7, 31, 23, 59, 59))#+1)
		# 	else:
		# 		subscription_validity = datetime.datetime.today()+datetime.timedelta(days=days_validity)#+1)
		# 	subscription_start = datetime.datetime.today()
		# else:
		# 	subscription_validity = datetime.datetime.today()+datetime.timedelta(days=days_validity)

		# renewing current subscription
		if(current_subscription_validity>datetime.datetime.today() and current_subscription_type > 0 and subscription_change==False and available_plans[plan_to_subscribe]['plan_id']==current_subscription_type and current_subscription_period == subscription_period):
			price_to_charge = price_to_charge
			payment_data = {}
			subscription_active = False
			if subscription_period == '1' and subscription_renewal:
				price_to_charge = 0
				new_validity = prev_subscription_validity
				new_validity = new_validity.replace(hour=23,minute=59,second=59)
				addons = [{"item":{"name":"Enabling auto-renwal","amount":int(price_to_charge*100),"currency":"INR"}}]
				print addons
				subscription_data = {'id':'1'}#Client.subscription.create(data={"plan_id":plan_id,"total_count":12,"start_at":int(new_validity.strftime("%s")),"addons":addons,"customer_id":customer.get("id","")})
				# TODO store response in db
				subscription_payment_type = "subscription"
				renew_plan = available_plans[subscription_plan]['subscription_plan']
				renew_plan_type = available_plans[subscription_plan]['plan_id']
				payment_data = subscription_data
				subscription_active = True
			else:
				# order_data = Client.order.create(data={"amount":price_to_charge,"currency":"INR","payment_capture":1})
				# # TODO store response in db
				# subscription_payment_type = "order"
				# multi month plan don't support renewal
				return JsonResponse({"status":"error","error_msg":"Plan action not support"})

			subscription_obj = {'subscription_type':available_plans[subscription_plan]['plan_id'],
			'subscription_product':available_plans[subscription_plan]['subscription_product'],
			'subscription_plan' : available_plans[subscription_plan]['subscription_plan'],
			'subscription_start' : datetime.datetime.today(),
			'subscription_stop' : new_validity,
			'subscription_validity' : new_validity,
			'subscription_price' : max(price_to_charge,0),
			'subscription_tax' : round(max(0,price_to_charge)*0.18,2),
			'subscription_total_price' : round(max(0,price_to_charge)*1.18,2),
			'subscription_instance' : 'restart',
			'subscription_payment_method' : 'razorpay',
			'subscription_period' : subscription_period,
			'subscription_promotion' : '',
			'payment_data':subscription_data,
			'renew_plan':renew_plan,
			'renew_plan_type':renew_plan_type,
			'subscription_active':subscription_active
			}

			subscription_obj['user_uuid'] = user_uuid
			subscription_obj['subscription_uuid'] = user_subscription.subscription_uuid
			subscription_obj['subscription_log_uuid'] = str(uuid.uuid4())
			subscription_obj['payment_uuid'] = str(uuid.uuid4())
			subscription_obj['latest_subscription_id'] = subscription_obj['subscription_log_uuid']
			subscription_obj['subscription_payment_type'] = subscription_payment_type
			
			usp = models.UserSubscriptionPayment(user_uuid=subscription_obj['user_uuid'],
				subscription_uuid=subscription_obj['subscription_uuid'],
				payment_uuid=subscription_obj['payment_uuid'],
				subscription=subscription_obj,
				subscription_payment_type=subscription_payment_type,
				payment_data = payment_data,
				customer = customer
				)
			payment_id = subscription_obj['payment_uuid']
			usp.save()

		# upgrading to higher plan
		elif (current_subscription_validity>datetime.datetime.today() and current_subscription_type > 0 and (available_plans[plan_to_subscribe]['plan_id']>current_subscription_type or int(current_subscription_period) < int(subscription_period) or (available_plans[plan_to_subscribe]['plan_id']==current_subscription_type and int(current_subscription_period) < int(subscription_period)))):
			days_charged = max((curr_days_validity-(current_subscription_validity-datetime.datetime.today()).days),0)
			price_utilised = user_subscription.subscription_price/curr_days_validity*days_charged
			price_to_charge = max(available_plans[subscription_plan]['varity'][subscription_period]['price']-(current_plan['varity'][user_subscription.subscription_period]['price']-price_utilised),0)
			price_to_charge = round(price_to_charge,2)
			
			new_validity = datetime.datetime.today()+datetime.timedelta(days=days_validity+1)
			new_validity = new_validity.replace(hour=23,minute=59,second=59)
			payment_data = {}
			subscription_active = False
			print "upgrading to higher plan",curr_days_validity,days_charged,price_utilised,price_to_charge,available_plans[subscription_plan]['varity'][subscription_period]['price'],(current_plan['varity'][user_subscription.subscription_period]['price']-price_utilised),new_validity
			if price_to_charge < 100:
				price_to_charge = None #raise an error msg
				return JsonResponse({"status":"error","error_msg":"Subscription value too low, please write to support@streak.tech"})
			else:
				if subscription_period == '1' and subscription_renewal:
					addons = [{"item":{"name":"Upgrade charge","amount":int(price_to_charge*100),"currency":"INR"}}]
					subscription_data = {'id':'1'}#Client.subscription.create(data={"plan_id":plan_id,"total_count":12,"start_at":int(new_validity.strftime("%s")),"addons":addons,"customer_id":customer.get("id","")})
					subscription_payment_type = "subscription"
					renew_plan = available_plans[subscription_plan]['subscription_plan']
					renew_plan_type = available_plans[subscription_plan]['plan_id']
					payment_data = subscription_data
					subscription_active = True
					# TODO store response in db
				else:
					try:
						order_data = Client.order.create(data={"amount":int(round(max(0,price_to_charge)*1.18,2)*100),"currency":"INR","payment_capture":1})
					except:
						try:
							order_data = Client.order.create(data={"amount":int(round(max(0,price_to_charge)*1.18,2)*100),"currency":"INR","payment_capture":1})
						except:
							order_data = Client.order.create(data={"amount":int(round(max(0,price_to_charge)*1.18,2)*100),"currency":"INR","payment_capture":1})
								
					# TODO store response in db
					subscription_payment_type = "order"
					renew_plan = ""
					renew_plan_type = -1
					payment_data = order_data


			subscription_obj = {'subscription_type':available_plans[subscription_plan]['plan_id'],
			'subscription_product':available_plans[subscription_plan]['subscription_product'],
			'subscription_plan' : available_plans[subscription_plan]['subscription_plan'],
			'subscription_start' : datetime.datetime.today(),
			'subscription_stop' : new_validity,
			'subscription_validity' : new_validity,
			'subscription_price' : max(price_to_charge,0),
			'subscription_tax' : round(max(0,price_to_charge)*0.18,2),
			'subscription_total_price' : round(max(0,price_to_charge)*1.18,2),
			'subscription_instance' : 'upgrade',
			'subscription_payment_method' : 'razorpay',
			'subscription_period' : subscription_period,
			'subscription_promotion' : '',
			'renew_plan':renew_plan,
			'renew_plan_type':renew_plan_type,
			'subscription_active':subscription_active
			}

			subscription_obj['user_uuid'] = user_uuid
			subscription_obj['subscription_uuid'] = user_subscription.subscription_uuid
			subscription_obj['subscription_log_uuid'] = str(uuid.uuid4())
			subscription_obj['payment_uuid'] = str(uuid.uuid4())
			subscription_obj['latest_subscription_id'] = subscription_obj['subscription_log_uuid']
			subscription_obj['subscription_payment_type'] = subscription_payment_type

			usp = models.UserSubscriptionPayment(user_uuid=subscription_obj['user_uuid'],
				subscription_uuid=subscription_obj['subscription_uuid'],
				payment_uuid=subscription_obj['payment_uuid'],
				subscription=subscription_obj,
				subscription_payment_type = subscription_payment_type,
				payment_data = payment_data,
				customer = customer
				)
			payment_id = subscription_obj['payment_uuid']
			usp.save()
		# downgrading to lower plan
		elif (current_subscription_validity>datetime.datetime.today() and current_subscription_type > 0 and (available_plans[plan_to_subscribe]['plan_id']<current_subscription_type or (available_plans[plan_to_subscribe]['plan_id']==current_subscription_type and int(current_subscription_period) > int(subscription_period)))): 
			# if current plan period is 1m plan and is beening downgraded, then return subscription id and charge card validation
			print 'downgrading to lower plan'
			price_to_charge = 0
			payment_data = {}
			subscription_active = False
			if price_to_charge < 100:
				if subscription_period == '1' and subscription_renewal and current_subscription_period== '1':
					new_validity = prev_subscription_validity
					new_validity = new_validity.replace(hour=23,minute=59,second=59)
					addons = []
					subscription_data = {'id':'1'}#Client.subscription.create(data={"plan_id":plan_id,"total_count":12,"start_at":int(new_validity.strftime("%s")),"customer_id":customer.get("id","")})
					subscription_payment_type = "subscription"

					renew_plan = available_plans[subscription_plan]['subscription_plan']
					renew_plan_type = available_plans[subscription_plan]['plan_id']
					payment_data = subscription_data
					subscription_active = True
					subscription_obj = {'subscription_type':available_plans[subscription_plan]['plan_id'],
					'subscription_product':available_plans[subscription_plan]['subscription_product'],
					'subscription_plan' : available_plans[subscription_plan]['subscription_plan'],
					'subscription_start' : user_subscription.subscription_validity - datetime.timedelta(days=available_plans[user_subscription.subscription_plan]['varity'][subscription_period]['days_validity']+1),
					'subscription_stop' : user_subscription.subscription_validity,
					'subscription_validity':user_subscription.subscription_validity,
					'subscription_instance' : 'downgrade',
					'subscription_price' : max(price_to_charge,0),
					'subscription_tax' : round(max(0,price_to_charge)*0.18,2),
					'subscription_total_price' : round(max(0,price_to_charge)*1.18,2),

					'latest_subscription_id':user_subscription.latest_subscription_id,
					'subscription_payment_method' : 'razorpay',
					'subscription_period' : subscription_period,
					'subscription_promotion' : '',
					'renew_plan':renew_plan,
					'renew_plan_type':renew_plan_type,
					'subscription_active':subscription_active
					}

					subscription_obj['user_uuid'] = user_uuid
					subscription_obj['subscription_uuid'] = user_subscription.subscription_uuid
					subscription_obj['subscription_log_uuid'] = str(uuid.uuid4())
					subscription_obj['payment_uuid'] = str(uuid.uuid4())
					subscription_obj['subscription_payment_type'] = subscription_payment_type

					usp = models.UserSubscriptionPayment(user_uuid=subscription_obj['user_uuid'],
					subscription_uuid=subscription_obj['subscription_uuid'],
					payment_uuid=subscription_obj['payment_uuid'],
					subscription=subscription_obj,
					subscription_payment_type = subscription_payment_type,
					payment_data = payment_data,
					customer = customer
					)
					payment_id = subscription_obj['payment_uuid']
					usp.save()
				else:
					# TODO just update in the subscriptions that plan has been changed
					# order_data = Client.order.create(data={"amount":price_to_charge,"currency":"INR","payment_capture":1})
					# subscription_payment_type = "order"
					return JsonResponse({"status":"error","error_msg":"Plan action not support"})
		else:
			# starting fresh subscription
			price_to_charge = price_to_charge
			new_validity = datetime.datetime.today()+datetime.timedelta(days=days_validity+1)
			new_validity = new_validity.replace(hour=23,minute=59,second=59)
			payment_data = {}
			subscription_active = False
			if subscription_period == '1' and subscription_renewal:
				addons = [{"item":{"name":"Upgrade plan pro-rata","amount":int(price_to_charge*100),"currency":"INR"}}]
				subscription_data = {'id':'1'}#Client.subscription.create(data={"plan_id":plan_id,"total_count":12,"start_at":int(new_validity.strftime("%s")),"addons":addons,"customer_id":customer.get("id","")})
				subscription_payment_type = "subscription"
				renew_plan = available_plans[subscription_plan]['subscription_plan']
				renew_plan_type = available_plans[subscription_plan]['plan_id']
				payment_data = subscription_data
				subscription_active = True
			else:
				try:
					order_data = Client.order.create(data={"amount":int(round(max(0,price_to_charge)*1.18,2)*100),"currency":"INR","payment_capture":1})
				except:
					try:
						order_data = Client.order.create(data={"amount":int(round(max(0,price_to_charge)*1.18,2)*100),"currency":"INR","payment_capture":1})
					except:
						order_data = Client.order.create(data={"amount":int(round(max(0,price_to_charge)*1.18,2)*100),"currency":"INR","payment_capture":1})

				subscription_payment_type = "order"
				renew_plan = ""
				renew_plan_type = -1
				payment_data = order_data

			subscription_obj = {'subscription_type':available_plans[subscription_plan]['plan_id'],
				'subscription_product':available_plans[subscription_plan]['subscription_product'],
				'subscription_plan' : available_plans[subscription_plan]['subscription_plan'],
				'subscription_start' : datetime.datetime.today(),
				'subscription_stop' : new_validity,
				'subscription_validity' : new_validity,
				'subscription_price' : max(price_to_charge,0),
				'subscription_tax' : round(max(0,price_to_charge)*0.18,2),
				'subscription_total_price' : round(max(0,price_to_charge)*1.18,2),
				'subscription_instance' : 'first',
				'subscription_payment_method' : 'razorpay',
				'subscription_period' : subscription_period,
				'subscription_promotion' : '',
				"renew_plan":renew_plan,
				"renew_plan_type":renew_plan_type,
				"subscription_active":subscription_active
				}

			subscription_obj['user_uuid'] = user_uuid
			subscription_obj['subscription_uuid'] = user_subscription.subscription_uuid
			subscription_obj['subscription_log_uuid'] = str(uuid.uuid4())
			subscription_obj['payment_uuid'] = str(uuid.uuid4())
			subscription_obj['latest_subscription_id'] = subscription_obj['subscription_log_uuid']
			subscription_obj['subscription_payment_type'] = subscription_payment_type
			usp = models.UserSubscriptionPayment(user_uuid=subscription_obj['user_uuid'],
				subscription_uuid=subscription_obj['subscription_uuid'],
				payment_uuid=subscription_obj['payment_uuid'],
				subscription=subscription_obj,
				subscription_payment_type=subscription_payment_type,
				payment_data=payment_data,
				customer = customer
				)
			payment_id=subscription_obj['payment_uuid']
			usp.save()

	except razorpay.errors.BadRequestError:
		print traceback.format_exc()
		return JsonResponse({"status":"error","error_msg":"Bad request"})
	except razorpay.errors.GatewayError:
		print traceback.format_exc()
		return JsonResponse({"status":"error","error_msg":"Gateway error"})
	except razorpay.errors.ServerError:
		print traceback.format_exc()
		return JsonResponse({"status":"error","error_msg":"Server error"})
	except:
		print traceback.format_exc()
		return JsonResponse({"status":"error","error_msg":"Error reaching payment gateway, PLEASE TRY AGAIN!"})

	print subscription_period
	app_true = post_data.get('app',False)
	encrypted = ""
	if app_true:
		sid = request.session.session_key
		msg = "rzp_live_WB01mw43jBEnd2"+"_"+user_uuid
		f = Fernet(key)
		encrypted = f.encrypt(msg)
	if subscription_period=='1' and subscription_renewal:
		return JsonResponse({"status":"success","price":price_to_charge,"tax":round(max(0,price_to_charge)*0.18,2),"total_price":round(max(0,price_to_charge)*1.18,2),"subscription_id":subscription_data['id'],"addons":addons,"subscription_payment_type":subscription_payment_type,"payment_id":payment_id,"customer_id":customer.get("id",""),"tokens":cards,"methods":methods})
	else:
		if app_true:
			return JsonResponse({"status":"success","price":price_to_charge,"tax":round(max(0,price_to_charge)*0.18,2),"total_price":round(max(0,price_to_charge)*1.18,2),"order_id":order_data['id'],"currency":"INR","subscription_payment_type":subscription_payment_type,"payment_id":payment_id,"customer_id":customer.get("id",""),"tokens":cards,"methods":methods,"token":encrypted})

		return JsonResponse({"status":"success","price":price_to_charge,"tax":round(max(0,price_to_charge)*0.18,2),"total_price":round(max(0,price_to_charge)*1.18,2),"order_id":order_data['id'],"currency":"INR","subscription_payment_type":subscription_payment_type,"payment_id":payment_id,"customer_id":customer.get("id",""),"tokens":cards,"methods":methods})

	return JsonResponse({"status":"error","error_msg":"Error reaching payment gateway, PLEASE TRY AGAIN!"})


def validate_subscription(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		return JsonResponse({"status":"success",'valid':True,'backtest':100,'deployments_remaining':5})
	
	if request.method!='POST':
		return JsonResponse({"status":"error","error_msg":"Unsupport method"})
	
	# user_uuid = "eff87bd6-bbec-4db5-809c-740b0a828253"

	post_data = ujson.loads(request.body)
	subscription_id = post_data.get('razorpay_payment_id','')#.lower()
	razorpay_payment_id = post_data.get('razorpay_payment_id','')#.lower()
	razorpay_signature = post_data.get('razorpay_signature','')#.lower()
	razorpay_subscription_id = post_data.get('razorpay_subscription_id','')#.lower()
	razorpay_order_id = post_data.get('razorpay_order_id','')#.lower()
	# order_id = post_data.get('order_id','')
	# payment_id = request.POST.get('payment_id','')
	# con = get_redis_connection("default")
	# plans = con.get('subscriptions_plans')
	available_plans = plans #ujson.loads(plans)
	payment_id = post_data.get('payment_id','')
	subscription_payment_type = 'order'
	try:
		# if razorpay_order_id!='':
		# 	payment_id = order_id
		# 	subscription_payment_type = 'order'
		if razorpay_subscription_id != '' and razorpay_order_id=='':
			razorpay_order_id = razorpay_subscription_id
			subscription_payment_type = 'subscription'

		user_subscription_payment = models.UserSubscriptionPayment.objects.get(payment_uuid=payment_id,subscription_payment_type=subscription_payment_type)
		try:
			params_dict = {'razorpay_signature':razorpay_signature,'razorpay_payment_id':razorpay_payment_id,'razorpay_order_id':razorpay_order_id}
			if subscription_payment_type =='subscription':
				params_dict['razorpay_subscription_id']=user_subscription_payment.payment_data['id']
			else:
				params_dict['razorpay_order_id']=user_subscription_payment.payment_data['id']

			try:
				Client.utility.verify_payment_signature(params_dict)
			except:
				try:
					Client.utility.verify_payment_signature(params_dict)
				except:
					Client.utility.verify_payment_signature(params_dict)

			if True:
				user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
				user_subscription.subscription_type = user_subscription_payment.subscription['subscription_type']
				user_subscription.subscription_product = user_subscription_payment.subscription['subscription_product']
				user_subscription.subscription_plan = user_subscription_payment.subscription['subscription_plan']
				user_subscription.subscription_price = user_subscription_payment.subscription['subscription_price']
				user_subscription.subscription_tax = user_subscription_payment.subscription['subscription_tax']
				user_subscription.subscription_total_price = user_subscription_payment.subscription['subscription_total_price']
				user_subscription.subscription_validity = user_subscription_payment.subscription['subscription_validity']
				user_subscription.subscription_instance = user_subscription_payment.subscription['subscription_instance']
				user_subscription.subscription_active = user_subscription_payment.subscription['subscription_active']
				user_subscription.renew_plan = user_subscription_payment.subscription['renew_plan']
				user_subscription.renew_plan_type = user_subscription_payment.subscription['renew_plan_type']
				user_subscription.subscription_period = user_subscription_payment.subscription['subscription_period']

				user_subscription.payment_uuid = user_subscription_payment.payment_uuid


				subscription_log_uuid = user_subscription_payment.subscription['subscription_log_uuid']
				if user_subscription_payment.subscription['subscription_instance']!='downgrade':
					user_subscription_log = models.UserSubscriptionLog(user_uuid=user_uuid,
						subscription_uuid = user_subscription.subscription_uuid,
						subscription_log_uuid = subscription_log_uuid,
						user_broker_id = user_subscription.user_broker_id,
						subscription_type = user_subscription_payment.subscription['subscription_type'],
						subscription_product = user_subscription_payment.subscription['subscription_product'],
						subscription_plan = user_subscription_payment.subscription['subscription_plan'],
						subscription_instance = user_subscription_payment.subscription['subscription_instance'],
						subscription_payment_method = user_subscription_payment.subscription['subscription_payment_method'],
						subscription_period = user_subscription_payment.subscription['subscription_period'],
						subscription_price = max(user_subscription_payment.subscription['subscription_price'],0),
						subscription_tax = round(max(0,user_subscription_payment.subscription['subscription_price'])*0.18,2),
						subscription_total_price = round(max(0,user_subscription_payment.subscription['subscription_price'])*1.18,2),
						subscription_promotion = user_subscription_payment.subscription['subscription_promotion'],
						subscription_start = user_subscription_payment.subscription['subscription_start'],
						subscription_stop = user_subscription_payment.subscription['subscription_stop'],
						payment_uuid = user_subscription_payment.payment_uuid
						)

					user_subscription.latest_subscription_id = subscription_log_uuid
					user_subscription_log.save()
				user_subscription.save()
				return JsonResponse({"status":"success"})
			else:
				return JsonResponse({"status":"error","error_msg":"Subscription did not validated"})
		except razorpay.errors.SignatureVerificationError:
			return JsonResponse({"status":"error","error_msg":"SSubscription did not validate"})
		except:
			print traceback.format_exc()

	except models.UserSubscriptionPayment.DoesNotExist:
		print traceback.format_exc()
		return JsonResponse({"status":"error","error_msg":"Subscription invalid"})
	except:
		print traceback.format_exc()
		return JsonResponse({"status":"error","error_msg":"Unknown error"})
	return JsonResponse({"status":"error","error_msg":"Unknown error"})

def stop_subscription_razorpay(subscription_id):
	resp = Client.subscription.cancel(subscription_id)
	return resp

def subscription_reset(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		return JsonResponse({"status":"success",'valid':True,'backtest':100,'deployments_remaining':5})
	
	if request.method!='POST':
		return JsonResponse({"status":"error","error_msg":"Unsupport method"})
	
	user_uuid = "eff87bd6-bbec-4db5-809c-740b0a828253"
	
	user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
	user_subscription.subscription_type = 0
	user_subscription.subscription_plan = "free"
	user_subscription.subscription_product = "free"
	user_subscription.subscription_validity =  datetime.datetime.today()-datetime.timedelta(days=1)
	user_subscription.renew_plan = ""
	user_subscription.renew_plan_type = -1

	user_subscription.save()
	return JsonResponse({"status":"success"})

def paymentProcess(request):
	#post_data = ujson.loads(request.body)
	post_data = request.POST
	if "application/json" in request.META['CONTENT_TYPE']:
		try:
			post_data = ujson.loads(request.body)
			if post_data is None or post_data=={}:
				post_data = request.POST
		except:
			print(traceback.format_exc())
		
	app_true = post_data.get('app',False)#.lower()
	# post_data = ujson.loads(request.body)
	subscription_id = post_data.get('razorpay_payment_id','')#.lower()
	razorpay_payment_id = post_data.get('razorpay_payment_id','')#.lower()
	razorpay_signature = post_data.get('razorpay_signature','')#.lower()
	razorpay_subscription_id = post_data.get('razorpay_subscription_id','')#.lower()
	razorpay_order_id = post_data.get('razorpay_order_id','')#.lower()
	# order_id = post_data.get('order_id','')
	# payment_id = request.POST.get('payment_id','')
	# con = get_redis_connection("default")
	# plans = con.get('subscriptions_plans')
	available_plans = plans #ujson.loads(plans)
	payment_id = post_data.get('payment_id','')
	subscription_payment_type = 'order'
	#print(
	user_uuid = request.GET.get('user_uuid','')#.lower()
	redirectUrl = 'https://streak.zerodha.com/account?'
	if user_uuid!="":
		conn = get_redis_connection('default')
		q = conn.get('user_version_pref'+user_uuid)
		v_pref = 1
		if q is None:
			v_pref = 1
			# if request.session.get('first_time_login',False)==True:
			# 	v_pref=3
		else:
			try:
				v_pref = int(q)
			except:
				v_pref = 3
		if v_pref==1:
			redirectUrl = 'https://streak.zerodha.com/account?'
		elif v_pref ==3:
			redirectUrl = 'https://streakv3.zerodha.com/account?'
		else:
			redirectUrl = 'https://streak.zerodha.com/account?'

	try:
		# if razorpay_order_id!='':
		#	   payment_id = order_id
		#	   subscription_payment_type = 'order'
		payment_id = razorpay_order_id
		if razorpay_subscription_id != '' and razorpay_order_id=='':
			razorpay_order_id = razorpay_subscription_id
			subscription_payment_type = 'subscription'
			payment_id = razorpay_subscription_id

		try:
			user_profile = models.UserProfile.objects.get(user_uuid=user_uuid)
			print("Payment broker",user_profile.first_broker)
			if user_profile.first_broker == "ab":
				redirectUrl = 'http://streak.angelbroking.com/account?'
			elif user_profile.first_broker == "5paisa":
				redirectUrl = 'http://streak.5paisa.com/account?'
		except:
			print("paymentProcess2",traceback.format_exc())

		user_subscription_payment = models.UserSubscriptionPayment.objects.get(payment_data__id=payment_id)
		user_uuid = user_subscription_payment.user_uuid
		try:
			if post_data.get('error[code]','')!='':
				print(post_data,"Payment error")
				return redirect(redirectUrl+'status=error&msg'+"Subscription did not validate"+"&payment_type="+subscription_payment_type+"&payment_id="+payment_id+"&description="+post_data.get("error[description]","Payment error occured"))
		except:
			print("paymentProcess",traceback.format_exc())

		try:
			params_dict = {'razorpay_signature':razorpay_signature,'razorpay_payment_id':razorpay_payment_id,'razorpay_order_id':razorpay_order_id}
			if subscription_payment_type =='subscription':
				params_dict['razorpay_subscription_id']=user_subscription_payment.payment_data['id']
			else:
				params_dict['razorpay_order_id']=user_subscription_payment.payment_data['id']

			try:
				Client.utility.verify_payment_signature(params_dict)
			except:
				try:
					Client.utility.verify_payment_signature(params_dict)
				except:
					Client.utility.verify_payment_signature(params_dict)

			try:
				payment = Client.payment.fetch(razorpay_payment_id)
				payment_state = payment['notes'].get('state','karnataka')
			except:
				payment_state = 'karnataka'

			user_subscription_payment.payment_data['payment_state']=payment_state
			user_subscription_payment.payment_status = 1
			user_subscription_payment.save()
			
			if True:
				user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
				user_subscription.subscription_type = user_subscription_payment.subscription['subscription_type']
				user_subscription.subscription_product = user_subscription_payment.subscription['subscription_product']
				user_subscription.subscription_plan = user_subscription_payment.subscription['subscription_plan']
				user_subscription.subscription_price = user_subscription_payment.subscription['subscription_price']
				user_subscription.subscription_tax = user_subscription_payment.subscription['subscription_tax']
				user_subscription.subscription_total_price = user_subscription_payment.subscription['subscription_total_price']
				user_subscription.subscription_validity = user_subscription_payment.subscription['subscription_validity']
				try:
					if user_subscription_payment.subscription['subscription_period'] == "12":
						user_subscription.subscription_validity = user_subscription_payment.subscription['subscription_validity'] + datetime.timedelta(days=90)
						if user_subscription["subscription_instance"]=="12w-order-completion":
							user_subscription_payment.subscription['subscription_instance']=user_subscription_payment.subscription['subscription_instance']+"-sms-reminder"
					if user_subscription["subscription_instance"]=="1w-order-completion":
						user_subscription.subscription_validity = user_subscription_payment.subscription['subscription_validity'] + datetime.timedelta(days=7)
						user_subscription_payment.subscription['subscription_instance']=user_subscription_payment.subscription['subscription_instance']+"-sms-reminder"
					if user_subscription["subscription_instance"]=="2w-order-completion":
						user_subscription.subscription_validity = user_subscription_payment.subscription['subscription_validity'] + datetime.timedelta(days=14)
						user_subscription_payment.subscription['subscription_instance']=user_subscription_payment.subscription['subscription_instance']+"-sms-reminder"
				except:
					print(traceback.format_exc())

				user_subscription.subscription_instance = user_subscription_payment.subscription['subscription_instance']
				user_subscription.subscription_active = user_subscription_payment.subscription['subscription_active']
				user_subscription.renew_plan = user_subscription_payment.subscription['renew_plan']
				user_subscription.renew_plan_type = user_subscription_payment.subscription['renew_plan_type']
				user_subscription.subscription_period = user_subscription_payment.subscription['subscription_period']

				user_subscription.payment_uuid = user_subscription_payment.payment_uuid


				subscription_log_uuid = user_subscription_payment.subscription['subscription_log_uuid']
				if user_subscription_payment.subscription['subscription_instance']!='downgrade':
					user_subscription_log = models.UserSubscriptionLog(user_uuid=user_uuid,
						subscription_uuid = user_subscription.subscription_uuid,
						subscription_log_uuid = subscription_log_uuid,
						user_broker_id = user_subscription.user_broker_id,
						subscription_type = user_subscription_payment.subscription['subscription_type'],
						subscription_product = user_subscription_payment.subscription['subscription_product'],
						subscription_plan = user_subscription_payment.subscription['subscription_plan'],
						subscription_instance = user_subscription_payment.subscription['subscription_instance'],
						subscription_payment_method = user_subscription_payment.subscription['subscription_payment_method'],
						subscription_period = user_subscription_payment.subscription['subscription_period'],
						subscription_price = max(user_subscription_payment.subscription['subscription_price'],0),
						subscription_tax = round(max(0,user_subscription_payment.subscription['subscription_price'])*0.18,2),
						subscription_total_price = round(max(0,user_subscription_payment.subscription['subscription_price'])*1.18,2),
						subscription_promotion = user_subscription_payment.subscription['subscription_promotion'],
						subscription_start = user_subscription_payment.subscription['subscription_start'],
						subscription_stop = user_subscription_payment.subscription['subscription_stop'],
						payment_uuid = user_subscription_payment.payment_uuid
						)

					user_subscription.latest_subscription_id = subscription_log_uuid
					user_subscription_log.save()
				user_subscription.save()
				# return JsonResponse({"status":"success"})
				try:
					con4 = get_redis_connection("screener_plan")
					con4.delete('plan_'+user_uuid)
				except:
					pass
				if app_true:
					return JsonResponse({"status":"success","payment_type":subscription_payment_type,"payment_id":payment_id})
				return redirect(redirectUrl+"status=success"+"&payment_type="+subscription_payment_type+"&payment_id="+payment_id)
			else:
				if app_true:
					return JsonResponse({"status":"error","msg":"Subscription did not validate","payment_id":payment_id,"payment_type":subscription_payment_type})
				return redirect(redirectUrl+'status=error&msg='+"Subscription did not validate"+"&payment_type="+subscription_payment_type+"&payment_id="+payment_id)
		except razorpay.errors.SignatureVerificationError:
			if app_true:
				return JsonResponse({"status":"error","msg":"Subscription did not validate","payment_id":payment_id,"payment_type":subscription_payment_type,"description":"Signature is not correct"})
			return redirect(redirectUrl+'status=error&msg='+"Subscription did not validate"+"&payment_type="+subscription_payment_type+"&payment_id="+payment_id+"&description=Signature is not correct")
		except razorpay.errors.ServerError:
			if app_true:
				return JsonResponse({"status":"error","msg":"Subscription did not validate","payment_id":payment_id,"payment_type":subscription_payment_type,"description":"Server error occured"})
			return redirect(redirectUrl+'status=error&msg='+"Subscription did not validate"+"&payment_type="+subscription_payment_type+"&payment_id="+payment_id+"&description=Server error occured")
		except razorpay.errors.GatewayError:
			if app_true:
				return JsonResponse({"status":"error","msg":"Subscription did not validate","payment_id":payment_id,"payment_type":subscription_payment_type,"description":"Server error occured"})
			return redirect(redirectUrl+'status=error&msg='+"Subscription did not validate"+"&payment_type="+subscription_payment_type+"&payment_id="+payment_id+"&description=The gateway request timed out")
		except:
			print traceback.format_exc()
	except models.UserSubscriptionPayment.DoesNotExist:
		print traceback.format_exc()
		if app_true:
			return JsonResponse({"status":"error","msg":"Subscription did not validate","payment_id":payment_id,"payment_type":subscription_payment_type,"description":"User not found"})
		return redirect(redirectUrl+'status=error&msg='+"Subscription invalid"+"&payment_type="+subscription_payment_type+"&payment_id="+payment_id+"&description=User not found")
	except:
		print traceback.format_exc()
		if app_true:
			return JsonResponse({"status":"error","msg":"Subscription did not validate","payment_id":payment_id,"payment_type":subscription_payment_type,"description":"Unexpected error"})
		return redirect(redirectUrl+'status=error&msg='+"Unknown error"+"&payment_type="+subscription_payment_type+"&payment_id="+payment_id+"&description=Unexpected error")
		
	if app_true:
		return JsonResponse({"status":"error","msg":"Subscription did not validate","payment_id":payment_id,"payment_type":subscription_payment_type,"description":"Unexpected error"})	
	return redirect(redirectUrl+'status=error&msg='+"Unknown error"+"&payment_type="+subscription_payment_type+"&payment_id="+payment_id+"&description=Unexpected error")


def fetch_order_preference(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		return JsonResponse({"status":"success",'valid':True,'backtest':100,'deployments_remaining':5})
	
	if request.method!='POST':
		return JsonResponse({"status":"error","error_msg":"Unsupport method"})

	post_data = request.POST
	payment_id = post_data.get('payment_id','')
	user_subscription_payment = {}
	try:
		if payment_id!="":
			user_subscription_payment = models.UserSubscriptionPayment.objects.get(user_uuid=user_uuid,payment_data__id=payment_id)
		else:
			user_subscription_payment_ = models.UserSubscriptionPayment._get_collection().find({'user_uuid':user_uuid}).sort([("updated_at",-1)])
			for u in user_subscription_payment_:
				user_subscription_payment = u
				break


		# print(user_subscription_payment)
		payment_data = user_subscription_payment['payment_data']
		customer = user_subscription_payment.get('customer',{})
		if customer.get("id","")=="":
			return JsonResponse({"status":"error","error_msg":"Unknown customer"})
		try:
			# cards = Client.token.all(customer_id=customer.get("id",""))
			url = "https://api.razorpay.com/v1/preferences"

			querystring = {"key_id":"rzp_live_WB01mw43jBEnd2","customer_id":customer.get("id","")}

			headers = {
				'Referer': "https://api.razorpay.com/v1/checkout/public"
				}
			response = requests.request("GET", url, headers=headers, params=querystring)
			response = ujson.loads(response.text)
			cards = response['customer']['tokens']
			methods = response['methods']
		except:
			print traceback.format_exc()
			cards = {
					  "entity" : "collection", 
					  "count" : 0, 
					  "items" : []
			}
		price = (payment_data['amount']/1.18)/100.0
		tax = price*0.18
		total_price = payment_data['amount']/100.0

		customer_data = customer
		return JsonResponse({"status":"success","tokens":cards,"methods":methods,"customer":customer_data,"payment_data":payment_data,"price":price,"tax":tax,"total_price":total_price})
	except:
		print traceback.format_exc()
		return JsonResponse({"status":"error","error_msg":"Payment not found"})

	return JsonResponse({"status":"error","error_msg":"Unknown error"})


def fetch_payment_preference(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		return JsonResponse({"status":"success",'valid':True,'backtest':100,'deployments_remaining':5})
	
	if request.method!='POST':
		return JsonResponse({"status":"error","error_msg":"Unsupport method"})

	username = request.POST.get("username","")
	contact = request.POST.get("contact","")
	email = request.POST.get("email","")
	if username == "" or email=="":
		return JsonResponse({"status":"error","error_msg":"Missing info"})

	customer = Client.customer.create(data={"name":username,"contact":contact,"email":email,"fail_existing":"0"})
	
	if customer.get("id","")=="":
		return JsonResponse({"status":"error","error_msg":"Unknown customer"})
	try:
		user_subscription_payment = {}
		user_subscription_payment_ = models.UserSubscriptionPayment._get_collection().find({'user_uuid':user_uuid}).sort([("updated_at",-1)])
		for u in user_subscription_payment_:
			user_subscription_payment = u
			break
		subscription_id = user_subscription_payment['payment_data']['id']
		customer_id = user_subscription_payment['payment_data']['customer_id']
		# cards = Client.token.all(customer_id=customer.get("id",""))
		url = "https://api.razorpay.com/v1/preferences"

		querystring = {"key_id":"rzp_live_WB01mw43jBEnd2","customer_id":customer.get("id","")}

		headers = {
			'Referer': "https://api.razorpay.com/v1/checkout/public"
			}
		response = requests.request("GET", url, headers=headers, params=querystring)
		response = ujson.loads(response.text)
		cards = response['customer']['tokens']
		methods = response['methods']
	except:
		print traceback.format_exc()
		subscription_id = ""
		customer_id = ""
		cards = {
				  "entity" : "collection", 
				  "count" : 0, 
				  "items" : []
				}
	return JsonResponse({"status":"success","cards":cards,"methods":methods,"subscription_id":subscription_id,"customer_id":customer_id})

def paymentCardChange(request):
	#post_data = ujson.loads(request.body)
	post_data = request.POST
	subscription_id = post_data.get('razorpay_payment_id','')#.lower()
	razorpay_payment_id = post_data.get('razorpay_payment_id','')#.lower()
	razorpay_signature = post_data.get('razorpay_signature','')#.lower()
	razorpay_subscription_id = post_data.get('razorpay_subscription_id','')#.lower()
	razorpay_order_id = post_data.get('razorpay_order_id','')#.lower()
	# order_id = post_data.get('order_id','')
	# payment_id = request.POST.get('payment_id','')
	# con = get_redis_connection("default")
	# plans = con.get('subscriptions_plans')
	available_plans = plans #ujson.loads(plans)
	payment_id = post_data.get('payment_id','')
	subscription_payment_type = 'order'
	#print(
	
	redirectUrl = 'https://streak.zerodha.com/account?'
	user_uuid = request.GET.get('user_uuid','')#.lower()
	if user_uuid!="":
		conn = get_redis_connection('default')
		q = conn.get('user_version_pref'+user_uuid)
		v_pref = 1
		if q is None:
			v_pref = 1
			# if request.session.get('first_time_login',False)==True:
			# 	v_pref=3
		else:
			try:
				v_pref = int(q)
			except:
				v_pref = 3
		if v_pref==1:
			redirectUrl = 'https://streak.zerodha.com/account?'
		elif v_pref ==3:
			redirectUrl = 'https://streakv3.zerodha.com/account?'
		else:
			redirectUrl = 'https://streak.zerodha.com/account?'
			
	try:
		# if razorpay_order_id!='':
		#	   payment_id = order_id
		#	   subscription_payment_type = 'order'
		payment_id = razorpay_order_id
		if razorpay_subscription_id != '' and razorpay_order_id=='':
			razorpay_order_id = razorpay_subscription_id
			subscription_payment_type = 'subscription'
			payment_id = razorpay_subscription_id
		try:
			params_dict = {'razorpay_signature':razorpay_signature,'razorpay_payment_id':razorpay_payment_id,'razorpay_order_id':razorpay_order_id}
			if subscription_payment_type =='subscription':
				params_dict['razorpay_subscription_id']=razorpay_subscription_id
			else:
				params_dict['razorpay_order_id']=razorpay_order_id

			Client.utility.verify_payment_signature(params_dict)
			if True:
				return redirect(redirectUrl+"status=success"+"&payment_type="+subscription_payment_type+"&payment_id="+payment_id+"&changeCard=True")
			else:
				return redirect(redirectUrl+'status=error&msg'+"Subscription did not validate"+"&payment_type="+subscription_payment_type+"&payment_id="+payment_id)
		except razorpay.errors.SignatureVerificationError:
			return redirect(redirectUrl+'status=error&msg'+"Subscription did not validate"+"&payment_type="+subscription_payment_type+"&payment_id="+payment_id+"&description=Signature is not correct")
		except razorpay.errors.ServerError:
			return redirect(redirectUrl+'status=error&msg'+"Subscription did not validate"+"&payment_type="+subscription_payment_type+"&payment_id="+payment_id+"&description=Server error occured")
		except razorpay.errors.GatewayError:
			return redirect(redirectUrl+'status=error&msg'+"Subscription did not validate"+"&payment_type="+subscription_payment_type+"&payment_id="+payment_id+"&description=The gateway request timed out")
		except:
			print traceback.format_exc()
	except:
		print traceback.format_exc()
		return redirect(redirectUrl+'status=error&msg'+"Unknown error"+"&payment_type="+subscription_payment_type+"&payment_id="+payment_id+"&description=Unexpected error")
	return redirect(redirectUrl+'status=error&msg'+"Unknown error"+"&payment_type="+subscription_payment_type+"&payment_id="+payment_id+"&description=Unexpected error")

def subscribe_to_algo(request):
	pass
	"""creating a payment, valid for 24 hours
	Input -> pub_id and payment_method and customer_id
	create a paymentIntent
	create a customer if doesnot exist
	create payment intent
	return client secret from payment intent
	"""
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		return JsonResponse({"status":"success",'valid':True,'backtest':100,'deployments_remaining':5})
	
	if request.method!='POST':
		return JsonResponse({"status":"error","error_msg":"Unsupport method"})
	post_data = request.POST
	publishing_uuid = post_data.get("publishing_uuid","")
	auto_renew = post_data.get('auto_renew',"true")
	if auto_renew == "false":
		auto_renew = False
	else:
		auto_renew = True

	upm = None
	user_profile = None
	try:
		user_profile = models.UserProfile.objects.get(user_uuid=user_uuid)
		# user_profile = models.DirectUserProfile.objects.get(user_uuid=user_uuid)
		# upm = models.UserPaymentMethods.objects.get(user_uuid=user_uuid)
	except DoesNotExist:
		if user_profile is None:
			return JsonResponse({"status":"error","error_msg":"User not found"})
		# if upm is None:
		# 	customer = stripe.Customer.create(
		# 		email=user_profile.email
		# 	)
		# 	upm = models.UserPaymentMethods(
		# 		user_uuid=user_uuid,
		# 		customer = customer,
		# 		)
		# 	upm.save()
	except:
		return JsonResponse({"status":"error","error_msg":"Unknown reason"})
	# if upm is not None and user_profile is not None:
	if user_profile is not None:
		try:
			published_algo = None
			published_algo = models.PublishedAlgos.objects.get(publishing_uuid=publishing_uuid)
			algo_subscription_uuid = str(uuid.uuid4())
			renewing = False

			if published_algo.subscription_price.get("monthly_pricing",0)==0:
				subscription_expiry = datetime.datetime.now().replace(hour=0,minute=0,second=0)+datetime.timedelta(days=365)
			else:
				subscription_expiry = datetime.datetime.now().replace(hour=0,minute=0,second=0)+datetime.timedelta(days=published_algo.min_subscription_duration)

			subscribe_to_algo = None
			subscribe_to_algo_log = None
			subscription_price = int(published_algo.subscription_price.get("monthly_pricing",0)*100)

			if subscription_price <= 0:
				scripList = []
				try:
					subscribed_algo = models.SubscribedAlgos.objects.get(user_uuid=user_uuid,publishing_uuid=publishing_uuid)
					algo_subscription_uuid = subscribed_algo.algo_subscription_uuid

					if subscribed_algo.subscription_expiry>datetime.datetime.now():
						return JsonResponse({"status":"error","error_msg":"Algo already subscribed","algo_subscription_uuid":algo_subscription_uuid})

					elif subscribed_algo.subscription_expiry<datetime.datetime.now() and subscribed_algo.subscription_active==False:

						subscribed_algo.subscription_expiry = subscription_expiry
						subscribed_algo.algo_name=published_algo.algo_name
						subscribed_algo.algo_desc=published_algo.algo_desc
						subscribed_algo.algo_obj=published_algo.algo_obj
						subscribed_algo.public=published_algo.public
						subscribed_algo.subscription_active = auto_renew
						subscribed_algo.subscription_status = 1

						subscribed_algo.save()

						models.SubscribeAlgoBacktest.objects(user_uuid=user_uuid,algo_subscription_uuid=algo_subscription_uuid,publishing_uuid=publishing_uuid).delete()

						pb = models.PublishedBacktests._get_collection().find({'publishing_uuid':publishing_uuid},{'_id':0})
						
						for b in pb:
							seg_sym = b["seg_sym"].split("_")
							scripList.append({"symbol":seg_sym[1],"segment":seg_sym[0]})
							# scripList = b["algo_obj"]['scripList']
							sb = models.SubscribeAlgoBacktest(
								user_uuid=user_uuid,
								algo_uuid=b["algo_uuid"],
								publishing_uuid=b["publishing_uuid"],
								algo_subscription_uuid=algo_subscription_uuid,
								seg_sym=b["seg_sym"],
								backtest_result=b["backtest_result"],
								algo_obj=b["algo_obj"],
								runtime=b["runtime"]
								)
							sb.save()

						if len(scripList)>0:
							subscribe_to_algo['algo_obj']['scripList'] = scripList
						subscribe_to_algo_log = models.SubscribedAlgosLog(user_uuid=user_uuid,
							algo_uuid=published_algo.algo_uuid,
							algo_subscription_uuid=algo_subscription_uuid,
							algo_name=published_algo.algo_name,
							algo_desc=published_algo.algo_desc,
							publishing_uuid=publishing_uuid,
							subscription_date = datetime.datetime.now(),
							subscription_expiry = subscription_expiry,
							subscription_status = 1
							)
						subscribe_to_algo_log.save()

						# return JsonResponse({"status":"success","msg":"Algo subscription extended","algo_subscription_uuid":algo_subscription_uuid})
					else:
						return JsonResponse({"status":"error","error_msg":"Algo already subscribed","algo_subscription_uuid":algo_subscription_uuid})

				except DoesNotExist:
					subscribe_to_algo = models.SubscribedAlgos(user_uuid=user_uuid,
					algo_uuid=published_algo.algo_uuid,
					algo_subscription_uuid=algo_subscription_uuid,
					algo_name=published_algo.algo_name,
					algo_desc=published_algo.algo_desc,
					publishing_uuid=publishing_uuid,
					subscription_date = datetime.datetime.now(),
					subscription_expiry = subscription_expiry,
					algo_obj=published_algo.algo_obj,
					subscription_active = auto_renew,
					subscription_status = 1,
					public = published_algo.public
					)
					subscribe_to_algo.save()

					pb = models.PublishedBacktests._get_collection().find({'publishing_uuid':publishing_uuid},{'_id':0})
					for b in pb:
						seg_sym = b["seg_sym"].split("_")
						scripList.append({"symbol":seg_sym[1],"segment":seg_sym[0]})
						# scripList = b["algo_obj"]['scripList']
						sb = models.SubscribeAlgoBacktest(
							user_uuid=user_uuid,
							algo_uuid=b["algo_uuid"],
							publishing_uuid=b["publishing_uuid"],
							algo_subscription_uuid=algo_subscription_uuid,
							seg_sym=b["seg_sym"],
							backtest_result=b["backtest_result"],
							algo_obj=b["algo_obj"],
							runtime=b["runtime"]
							)
						sb.save()
					if len(scripList)>0:
						try:
							subscribe_to_algo['algo_obj']['scripList'] = scripList
						except:
							published_algo.algo_obj['scripList'] = scripList
							subscribe_to_algo['algo_obj'] = published_algo.algo_obj

						subscribe_to_algo.save()
					subscribe_to_algo_log = models.SubscribedAlgosLog(user_uuid=user_uuid,
					algo_uuid=published_algo.algo_uuid,
					algo_subscription_uuid=algo_subscription_uuid,
					algo_name=published_algo.algo_name,
					algo_desc=published_algo.algo_desc,
					publishing_uuid=publishing_uuid,
					subscription_date = datetime.datetime.now(),
					subscription_expiry = subscription_expiry,
					subscription_status = 1
					)
					subscribe_to_algo_log.save()


			if published_algo is not None :
				if subscription_price!=0:
					# pi = stripe.PaymentIntent.create(
					# 	customer=upm.customer["id"],
					# 	amount=subscription_price,
					# 	currency="usd",
					# 	payment_method_types=["card"],
					# 	# confirm=True
					# 	metadata={"algo_subscription_uuid":algo_subscription_uuid,"publishing_uuid":publishing_uuid,"auto_renew":auto_renew,"user_uuid":user_uuid}
					# 	)
					# return JsonResponse({"status":"success","client_secret":pi["client_secret"],"algo_subscription_uuid":algo_subscription_uuid})
					return JsonResponse({"status":"success","client_secret":"Setup payment","algo_subscription_uuid":algo_subscription_uuid})
				elif subscribe_to_algo is not None and subscribe_to_algo_log is not None:
					subscribe_to_algo.subscription_status=1
					subscribe_to_algo_log.subscription_status=1
					subscribe_to_algo.save()
					subscribe_to_algo_log.save()
					return JsonResponse({"status":"success","msg":"Strategy successfully subscribed","client_secret":None,"algo_subscription_uuid":algo_subscription_uuid})
		except DoesNotExist:
			print traceback.format_exc()
			return JsonResponse({"status":"error","error_msg":"Algo not found"})
	return JsonResponse({"status":"error","error_msg":"Unknown error"})

api_result_ok = 0
api_result_errors = {
    21000: 'Bad json',
    21002: 'Bad data',
    21003: 'Receipt authentication',
    21004: 'Shared secret mismatch',
    21005: 'Server is unavailable',
    21006: 'Subscription has expired',
    21007: 'Sandbox receipt was sent to the production env',
    21008: 'Production receipt was sent to the sandbox env',
}

# ios_url = 'https://sandbox.itunes.apple.com/verifyReceipt'
ios_url = 'https://buy.itunes.apple.com/verifyReceipt'
bundle_id = 'tech.streak.trade'
STOREKIT_PURCHASED_SECRET = '723bdc4a3ff645e8bd655eca78e9489b'
available_plans_ios = {
						'free':{'daily_backtests': 20, 'subscription_tax': 0, 'subscription_plan': 'free', 'subscription_price': 0, 'plan_id': 0, 'subscription_validity_date': 7, 'daily_deploys': 2, 'subscription_total_price': 0, 'subscription_product': 'free','note':'Free trial till 30th Nov 2018','subscription_period':30},
						'basic':{'daily_backtests': 200, 'subscription_tax': 90, 'subscription_plan': 'basic', 'subscription_price': 500, 'plan_id': 1, 'subscription_validity_date': 30, 'daily_deploys': 25, 'subscription_total_price': 590, 'subscription_product': 'basic','note':'Free for all Zerodha clients till 31st July, 18','subscription_period':30},
						'premium':{'daily_backtests': 500, 'subscription_tax': 162, 'subscription_plan': 'premium', 'subscription_price': 900, 'plan_id': 2, 'subscription_validity_date': 30, 'daily_deploys': 50, 'subscription_total_price': 1062, 'subscription_product': 'premium','note':'Starts from 1st July, 18','subscription_period':30},
						'ultimate':{'daily_backtests': 1000, 'subscription_tax': 252, 'subscription_plan': 'ultimate', 'subscription_price': 1400, 'plan_id': 3, 'subscription_validity_date': 30, 'daily_deploys': 100, 'subscription_total_price': 1652, 'subscription_product': 'ultimate','note':'Starts from 1st July, 18','time':'30 minutes','subscription_period':30}
	}

def receive_subscribe_receipt(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		return JsonResponse({"status":"success",'valid':True,'backtest':100,'deployments_remaining':5})

	if request.method!='POST':
		return JsonResponse({"status":"error","error_msg":"method"})

	receipt = request.POST.get("receipt","")
	product_id = request.POST.get("product_id","")
	receipt_json = {'receipt-data': receipt,'exclude-old-transactions':True}
	receipt_json["password"] = STOREKIT_PURCHASED_SECRET

	headers = {"Content-Type":"application/json"}
	# api_response = requests.post(self.url, json=receipt_json).json()

	response = requests.request("POST", ios_url, data=ujson.dumps(receipt_json), headers=headers)
	if response.status_code == 200:
		response_json = ujson.loads(response.text)
		if response_json['status']!=api_result_ok:
			return JsonResponse({"status":"error","error_msg":api_result_errors.get(response_json['status'],"Unknown API status")})
		elif bundle_id != response_json['receipt']['bundle_id']:
			return JsonResponse({"status":"error","error_msg":"Bundle ID mismatch"})
		else:
			#enable plan with product id
			#extend subscription
			#make entry to subscription log
			try:
				latest_receipt = response_json["latest_receipt_info"][0]
				plan = "free"
				plan_id = 0
				subscription_period = '1'
				if "quarterly" in latest_receipt["product_id"]:
					plan  = latest_receipt["product_id"].replace("_quarterly","")
					subscription_validity = datetime.datetime.today()+datetime.timedelta(days=90)
					subscription_period = '3'
				elif "biyearly" in latest_receipt["product_id"]:
					plan  = latest_receipt["product_id"].replace("_biyearly","")
					subscription_validity = datetime.datetime.today()+datetime.timedelta(days=180)
					subscription_period = '6'
				elif "annual" in latest_receipt["product_id"]:
					plan  = latest_receipt["product_id"].replace("_annual","")
					subscription_validity = datetime.datetime.today()+datetime.timedelta(days=365)
					subscription_period = '12'
				else:
					subscription_period = '3'
					plan = latest_receipt["product_id"]

				subscription_log_uuid =  str(uuid.uuid4())

				plan_to_subscribe = available_plans_ios[plan]

				# subscription_validity = datetime.datetime.fromtimestamp(int(latest_receipt['expires_date_ms'])/1000)

				user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
				user_subscription.subscription_active = False
				user_subscription.subscription_type = plan_to_subscribe['plan_id']
				user_subscription.subscription_product = plan_to_subscribe['subscription_product']
				user_subscription.subscription_plan = plan_to_subscribe['subscription_product']
				user_subscription.subscription_validity = subscription_validity
				user_subscription.latest_subscription_id = subscription_log_uuid
				user_subscription.subscription_price = 0
				user_subscription.subscription_tax = 0
				user_subscription.subscription_total_price = 0
				user_subscription.subscription_active = True
				user_subscription.subscription_period = subscription_period

				user_subscription_log = models.UserSubscriptionLog(
					user_uuid=user_uuid,
					subscription_uuid = user_subscription.subscription_uuid,
					user_broker_id = user_subscription.user_broker_id,
					subscription_log_uuid = subscription_log_uuid,
					subscription_type = plan_to_subscribe['plan_id'],
					subscription_product = plan_to_subscribe['subscription_product'],
					subscription_plan = plan_to_subscribe['subscription_plan'],
					subscription_start = datetime.datetime.today(),
					subscription_stop = subscription_validity,
					subscription_instance = "ios",
					subscription_price = 0,
					subscription_tax = 0,
					subscription_total_price = 0,
					subscription_period = subscription_period,
					subscription_payment_method = "iStore"
					)
				user_subscription_log.save()
				user_subscription.save()
			except DoesNotExist:
				return JsonResponse({"status":"error","error_msg":"User not found"})
			except:
				print(traceback.format_exc())
				return JsonResponse({"status":"error","error_msg":"Unkown error"})
			return JsonResponse({"status":"success","reponse":response_json})
	return JsonResponse({"status":"error","error_msg":"Unknown error"})

def directLinkPayment(user_uuid,plan,plan_period,price,tax,total,payment_id,order_id):
	pass

def razorpay_payment_capture_webhook(request):
	if request.method!="POST":
		post_data = ujson.loads(request.body)
		entity_webhook = post_data.get('entity','')#.lower()
		webhook_signature = request.META.get("X-Razorpay-Signature","")
		webhook_secret = "1278haudk18kdhleh35litylugdlwhdlkaldkhlihfkabdi74723bdc4a3ff645e8bd655eca78e9asakdlkaj489b"
		# valid_signature = Client.utility.verify_webhook_signature(request.body, webhook_signature, webhook_secret)
		# print(valid_signature,post_data)
		if entity_webhook=="event":
			event = post_data.get("event","")
			if event == "payment.captured":
				payload =  post_data.get("payload",{})
				payment = payload.get("payment",None)
				if payment is not None:
					entity = payment.get("entity",None)
					if entity is not None:
						payment_id = entity.get("id","")
						order_id = entity.get("order_id","")
						if order_id!="" and payment_id!="":
							try:
								user_subscription_payment = models.UserSubscriptionPayment.objects.get(payment_data__id=payment_id)
								user_uuid = user_subscription_payment.user_uuid
								try:
									payment = Client.payment.fetch(razorpay_payment_id)
									payment_state = payment['notes'].get('state','karnataka')
								except:
									payment_state = 'karnataka'
								if user_subscription_payment.payment_status==0:
									user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
									user_subscription.subscription_type = user_subscription_payment.subscription['subscription_type']
									user_subscription.subscription_product = user_subscription_payment.subscription['subscription_product']
									user_subscription.subscription_plan = user_subscription_payment.subscription['subscription_plan']
									user_subscription.subscription_price = user_subscription_payment.subscription['subscription_price']
									user_subscription.subscription_tax = user_subscription_payment.subscription['subscription_tax']
									user_subscription.subscription_total_price = user_subscription_payment.subscription['subscription_total_price']
									user_subscription.subscription_validity = user_subscription_payment.subscription['subscription_validity']
									try:
										if user_subscription_payment.subscription['subscription_period'] == "12":
											user_subscription.subscription_validity = user_subscription_payment.subscription['subscription_validity'] + datetime.timedelta(days=90)
											if user_subscription["subscription_instance"]=="12w-order-completion":
												user_subscription_payment.subscription['subscription_instance']=user_subscription_payment.subscription['subscription_instance']+"-sms-reminder"
										if user_subscription["subscription_instance"]=="1w-order-completion":
											user_subscription.subscription_validity = user_subscription_payment.subscription['subscription_validity'] + datetime.timedelta(days=7)
											user_subscription_payment.subscription['subscription_instance']=user_subscription_payment.subscription['subscription_instance']+"-sms-reminder"
										if user_subscription["subscription_instance"]=="2w-order-completion":
											user_subscription.subscription_validity = user_subscription_payment.subscription['subscription_validity'] + datetime.timedelta(days=14)
											user_subscription_payment.subscription['subscription_instance']=user_subscription_payment.subscription['subscription_instance']+"-sms-reminder"
									except:
										print(traceback.format_exc())

									user_subscription.subscription_instance = user_subscription_payment.subscription['subscription_instance']
									user_subscription.subscription_active = user_subscription_payment.subscription['subscription_active']
									user_subscription.renew_plan = user_subscription_payment.subscription['renew_plan']
									user_subscription.renew_plan_type = user_subscription_payment.subscription['renew_plan_type']
									user_subscription.subscription_period = user_subscription_payment.subscription['subscription_period']

									user_subscription.payment_uuid = user_subscription_payment.payment_uuid


									subscription_log_uuid = user_subscription_payment.subscription['subscription_log_uuid']
									if user_subscription_payment.subscription['subscription_instance']!='downgrade':
										user_subscription_log = models.UserSubscriptionLog(user_uuid=user_uuid,
											subscription_uuid = user_subscription.subscription_uuid,
											subscription_log_uuid = subscription_log_uuid,
											user_broker_id = user_subscription.user_broker_id,
											subscription_type = user_subscription_payment.subscription['subscription_type'],
											subscription_product = user_subscription_payment.subscription['subscription_product'],
											subscription_plan = user_subscription_payment.subscription['subscription_plan'],
											subscription_instance = user_subscription_payment.subscription['subscription_instance'],
											subscription_payment_method = user_subscription_payment.subscription['subscription_payment_method'],
											subscription_period = user_subscription_payment.subscription['subscription_period'],
											subscription_price = max(user_subscription_payment.subscription['subscription_price'],0),
											subscription_tax = round(max(0,user_subscription_payment.subscription['subscription_price'])*0.18,2),
											subscription_total_price = round(max(0,user_subscription_payment.subscription['subscription_price'])*1.18,2),
											subscription_promotion = user_subscription_payment.subscription['subscription_promotion'],
											subscription_start = user_subscription_payment.subscription['subscription_start'],
											subscription_stop = user_subscription_payment.subscription['subscription_stop'],
											payment_uuid = user_subscription_payment.payment_uuid
											)

										user_subscription.latest_subscription_id = subscription_log_uuid
										user_subscription_log.save()
									user_subscription.save()
									user_subscription_payment.payment_data['payment_state']=payment_state
									user_subscription_payment.payment_status = 1
									user_subscription_payment.save()
									# return JsonResponse({"status":"success"})
									try:
										con4 = get_redis_connection("screener_plan")
										con4.delete('plan_'+user_uuid)
									except:
										print("plan reset redis connections")
										print(traceback.format_exc())
									print("Payment captured for ",payment_id,user_uuid)
									return JsonResponse({"status":"error","error_msg":"Payment captured successfully"})
								else:
									print("payment laready captured",payment_id)
									return JsonResponse({"status":"error","error_msg":"Payment already captured"})
							except DoesNotExist:
								# user_profile = models.UserProfile.objects.get(user_broker_id="")
								# p = directLinkPayment(user_profile.user_uuid,"ultimate","12",entity.get("amount",0)/1.18,(entity.get("amount",0)/1.18)*0.18,entity.get("amount",0),entity.get("id",""),entity.get("payment_id",""))
								print("payment order id doesnot exit")
							except:
								print("error running payment webhook")
								print(traceback.format_exc())
								print("Unknown")
							return JsonResponse({"status":"error","error_msg":"Unknown"})
						else:
							return JsonResponse({"status":"error","error_msg":"Order id not found"})
					else:
						return JsonResponse({"status":"error","error_msg":"entity not found"})
				else:
					return JsonResponse({"status":"error","error_msg":"payment not found"})
			else:
				return JsonResponse({"status":"error","error_msg":"event not supported"})
	return JsonResponse({"status":"error","error_msg":"method"})
