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
import traceback
from coreapp import models
from mongoengine import DoesNotExist
import datetime


def update_activity(request,activity):
	user_uuid = request.session.get('user_uuid','')
	if user_uuid == "":
		return
	try:
		user_activity = models.UserActivity.objects.get(user_uuid=user_uuid)
		if activity=="login":
			user_activity.login_count = user_activity.login_count + 1
			algo_count = models.Algorithm.objects(user_uuid = user_uuid).count()
			backtest_count = models.BacktestMeta.objects(user_uuid = user_uuid).count()
			deployed_count = models.DeployedAlgorithm.objects(user_uuid = user_uuid).count()
			notification_count = models.OrderLog.objects(user_uuid = user_uuid).count()
			screeners = models.Screener.objects(user_uuid = user_uuid).count()
			alerts = models.ScreenerAlert.objects(user_uuid = user_uuid).count()

			phone_number_added = 0
			profile_pic_changed = 0
			try:
				user_profile = models.UserProfile.objects.get(user_uuid = user_uuid)
				if user_profile.phone_number!="" and len(user_profile.phone_number)>8:
					phone_number_added = 1
				if user_profile.phone_number!="" and len(user_profile.phone_number)>8:
					phone_number_added = 1

				user_subscription_count = models.UserSubscriptionLog.objects(user_uuid = user_uuid).count()
				user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
			except:
				print("user_profile,error",traceback.format_exc())

			if user_activity:
				print("heeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeerrrrrrrrrrrrrrrrrrrrrrre")
				user_activity.algorithms = algo_count
				user_activity.backtests = backtest_count
				user_activity.deployments = deployed_count
				user_activity.notifications = notification_count
				user_activity.screeners = screeners
				user_activity.alerts = alerts
				user_activity.phone_number_added = phone_number_added
				user_activity.profile_pic_changed = profile_pic_changed
				user_activity.subscriptions = user_subscription_count
				user_activity.subscription_validity = user_subscription.subscription_validity
				print user_subscription.subscription_validity,user_subscription.subscription_type,user_uuid
				user_activity.subscription_type = user_subscription.subscription_type
				user_activity.subscription_period = user_subscription.subscription_period

		user_activity.save()
	except DoesNotExist:
		if activity=="login":
			user_activity = models.UserActivity(user_uuid=user_uuid,login_count=1)
			user_activity.save()
	except:
		print(traceback.format_exc())

def add_session_log(request):
	user_uuid = request.session.get('user_uuid','')
	try:
		REMOTE_ADDR = request.META.get("REMOTE_ADDR","")
		HTTP_USER_AGENT = request.META.get("HTTP_USER_AGENT","")
		user_session = models.UserSessionLog(
											user_uuid=user_uuid,
											login_count = 0,
											login_ip = REMOTE_ADDR,
											device = HTTP_USER_AGENT
											)

		user_session.save()
	except:
		pass

def dashboard_carousel(request):
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
	
	if request.method!="GET":
		return JsonResponse({"status":"error","error_msg":"Method"})

	login_count = 0
	resp_dict_banner1={
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/1.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"navigation",
						"action_url":"/strategies?tab=discover",
						"external_url":False,
						"description":"Discover strategies"
					}
	resp_dict_banner2={
					"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/2.png",
					"image_overlay_text":"",
					"image_overlay_position":"",
					"action_type":"popup",
					"action_url":"/demo_request",
					"external_url":False,
					"description":"Demo request"
					}
	resp_dict_banner3={
					"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/3.png",
					"image_overlay_text":"",
					"image_overlay_position":"",
					"action_type":"navigation",
					"action_url":"/market_watch",
					"external_url":False,
					"description":"Technicals"
					}
	resp_dict_banner4={
					"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/4.png",
					"image_overlay_text":"",
					"image_overlay_position":"",
					"action_type":"navigation",
					"action_url":"/account?tab=profile",
					"external_url":False,
					"description":"Update profile picture"
					}
	dashboard_response = [resp_dict_banner2,resp_dict_banner1,resp_dict_banner3,resp_dict_banner4]
	# return JsonResponse({"status":"success","dashboard_carousel":dashboard_response[0:4]})
	try:
		user_activity = models.UserActivity.objects.get(user_uuid=user_uuid)
		login_count = user_activity.login_count
		
		# logic for banner 1
		if login_count <=1:
			resp_dict_banner1 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/1.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"navigation",
						"action_url":"/strategies?tab=discover",
						"external_url":False,
						"description":"Discover strategies"
						}
		elif login_count <=2:
			resp_dict_banner1 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/5.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"navigation",
						"action_url":"/create",
						"external_url":False,
						"description":"Create strategy"
						}

		elif login_count <=3:
			resp_dict_banner1 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/6.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"navigation",
						"action_url":"/scans/popular'",
						"external_url":False,
						"description":"Discover scanner"
						}
		else:
			if user_activity.algorithms < 3 and user_activity.screeners!=0: 
				resp_dict_banner1 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/5.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"navigation",
						"action_url":"/create",
						"external_url":False,
						"description":"Create strategy"
						}
			elif user_activity.screeners%2==0:
				resp_dict_banner1 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/7.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"navigation",
						"action_url":"/scanner",
						"external_url":False,
						"description":"Create scanner"
						}
			else:
				resp_dict_banner1 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/1.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"navigation",
						"action_url":"/strategies?tab=discover",
						"external_url":False,
						"description":"Discover strategies"
						}


		# logic for banner 2
		if login_count > - 1:
			print user_activity.demo_requested,user_activity.subscription_validity,user_activity.demo_schedule_date
			if user_activity.demo_schedule_date is None and user_activity.subscription_validity < datetime.datetime.now():
				resp_dict_banner2 = {
								"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/2.png",
								"image_overlay_text":"",
								"image_overlay_position":"",
								"action_type":"popup",
								"action_url":"/demo_request",
								"external_url":False,
								"description":"Demo request"
								}
			if user_activity.demo_schedule_date is None and user_activity.subscription_validity > datetime.datetime.now():
				if login_count%2==0:
						action_url = "https://www.youtube.com/watch?v=jNEVC6CkCT4"
						resp_dict_banner2 = {
								"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/Webinar.png",
								"image_overlay_text":"",
								"image_overlay_position":"",
								"action_type":"external",
								"action_url":action_url,
								"external_url":True,
								"description":"Webinar"
								}
				else:
					action_url = "https://zerodha.com/varsity/module/technical-analysis/"
					resp_dict_banner2 = {
							"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/Varsity.png",
							"image_overlay_text":"",
							"image_overlay_position":"",
							"action_type":"external",
							"action_url":action_url,
							"external_url":True,
							"description":"Varsity"
							}
			elif (not user_activity.demo_requested > 3 and user_activity.subscription_validity < datetime.datetime.now()) and user_activity.demo_schedule_date<datetime.datetime.now():
					resp_dict_banner2 = {
								"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/2.png",
								"image_overlay_text":"",
								"image_overlay_position":"",
								"action_type":"popup",
								"action_url":"/demo_request",
								"external_url":False,
								"description":"Demo request"
								}
			else:
				if user_uuid in ["79299a13-3595-40cf-a47f-b3e5edfc1dca","6de09528-dfc3-4858-86eb-99cd7c47156e"]:
					resp_dict_banner2 = {
								"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/Learnapp.png",
								"image_overlay_text":"",
								"image_overlay_position":"",
								"action_type":"",
								"action_url":"",
								"external_url":True,
								"description":"Webinar"
								}
				elif user_activity.demo_schedule_date>datetime.datetime.now():
					remaining_hours = (user_activity.demo_schedule_date - datetime.datetime.now()).seconds//3600
					if remaining_hours < 1:
						image_overlay_text = "Join demo now, it starts in less than an hour"
						action_url = "https://bit.ly/2z7FfhG"
					else:
						image_overlay_text = "Demo starts in "+ str(remaining_hours) +" hours"
						action_url = "https://bit.ly/2z7FfhG"

					resp_dict_banner2 = {
							"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/2_blank.png",
							"image_overlay_text":image_overlay_text,
							"image_overlay_position_left":20,
							"image_overlay_position_top":20,
							"image_overlay_background_color": '#F7FAFE',
							"image_overlay_text_color": '#000000',
							"image_overlay_position":"top-center",
							"action_type":"external",
							"action_url":action_url,
							"external_url":True,
							"description":"Demo request"
							}
				else:
					if login_count%2==0:
						action_url = "https://www.youtube.com/watch?v=jNEVC6CkCT4"
						resp_dict_banner2 = {
								"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/Webinar.png",
								"image_overlay_text":"",
								"image_overlay_position":"",
								"action_type":"external",
								"action_url":action_url,
								"external_url":True,
								"description":"Webinar"
								}
					else:
						action_url = "https://zerodha.com/varsity/module/technical-analysis/"
						resp_dict_banner2 = {
								"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/Varsity.png",
								"image_overlay_text":"",
								"image_overlay_position":"",
								"action_type":"external",
								"action_url":action_url,
								"external_url":True,
								"description":"Varsity"
								}


		elif login_count <=2:
			resp_dict_banner2 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/2.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"popup",
						"action_url":"/demo_request",
						"external_url":False,
						"description":"Demo request"
						}
		elif login_count <=3:
			resp_dict_banner2 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/2.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"popup",
						"action_url":"/demo_request",
						"external_url":False,
						"description":"Demo request"
						}
		else:
			if user_activity.subscription_validity < datetime.datetime.now() and user_activity.subscription_type==3:
				resp_dict_banner2 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/10.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"popup",
						"action_url":"/demo_request?type=expert_call",
						"external_url":False,
						"description":"Demo request"
						}
			else:
				resp_dict_banner2 = {
							"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/2.png",
							"image_overlay_text":"",
							"image_overlay_position":"",
							"action_type":"popup",
							"action_url":"/demo_request",
							"external_url":False,
							"description":"Demo request"
							}

		# logic for banner 3
		if login_count >-1:
			if login_count<=2 and login_count%2==0:
				resp_dict_banner3 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/3.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"navigation",
						"action_url":"/market_watch",
						"external_url":False,
						"description":"Technicals"
						}
			else:
				if login_count%3==1:
					action_url = "https://www.youtube.com/watch?v=jNEVC6CkCT4"
					resp_dict_banner3 = {
							"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/Webinar.png",
							"image_overlay_text":"",
							"image_overlay_position":"",
							"action_type":"external",
							"action_url":action_url,
							"external_url":True,
							"description":"Webinar"
							}
				else:
					resp_dict_banner3 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/8.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"navigation",
						"action_url":"/market_watch?tab=top_movers",
						"external_url":False,
						"description":"Top movers"
						}

		elif login_count <=2:
			resp_dict_banner3 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/3.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"navigation",
						"action_url":"/market_watch",
						"external_url":False,
						"description":"Technicals"
						}
		elif login_count <=3:
			resp_dict_banner3 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/3.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"navigation",
						"action_url":"/market_watch",
						"external_url":False,
						"description":"Technicals"
						}
		else:
			resp_dict_banner3 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/3.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"navigation",
						"action_url":"/market_watch",
						"external_url":False,
						"description":"Technicals"
						}

		# logic for banner 4
		if login_count >-1:
			if user_activity.profile_pic_changed<=0 and user_activity.phone_number_added==0:
				resp_dict_banner4 = {
							"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/4.png",
							"image_overlay_text":"",
							"image_overlay_position":"",
							"action_type":"navigation",
							"action_url":"/account?tab=profile",
							"external_url":False,
							"description":"Update profile picture"
							}
			elif (user_activity.subscription_validity < datetime.datetime.now() or user_activity.subscription_type!=3 or user_activity.subscription_period!="12") and login_count%2==0:
				resp_dict_banner4 = {
							"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/Subscribe.png",
							"image_overlay_text":"",
							"image_overlay_position":"",
							"action_type":"navigation",
							"action_url":"/billing",
							"external_url":False,
							"description":"Update Subscription"
							}
			else:
				invite_msg = "Never miss an opportunity, with Streak do strategic trading without coding, join now, visit "+urllib.quote_plus("https://streak.tech?utm_source=appshare")
				resp_dict_banner4={
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/11.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"social_share",
						"action_url":"/invite?title=Join Streak now&message="+invite_msg+"&img_url=https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/share_banner.png",
						"external_url":False,
						"description":"Invite friends"
					}

		elif login_count <=2:
			if user_activity.profile_pic_changed<=0 and user_activity.phone_number_added==0:
				resp_dict_banner4 = {
							"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/4.png",
							"image_overlay_text":"",
							"image_overlay_position":"",
							"action_type":"navigation",
							"action_url":"/account?tab=profile",
							"external_url":False,
							"description":"Update profile picture"
							}
			else:
				resp_dict_banner4 = {
							"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/8.png",
							"image_overlay_text":"",
							"image_overlay_position":"",
							"action_type":"navigation",
							"action_url":"/market_watch?tab=top_movers",
							"external_url":False,
							"description":"Top movers"
							}
		elif login_count <=3:
			if user_activity.profile_pic_changed<=0 and user_activity.phone_number_added==0:
				resp_dict_banner4 = {
							"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/4.png",
							"image_overlay_text":"",
							"image_overlay_position":"",
							"action_type":"navigation",
							"action_url":"/account?tab=profile",
							"external_url":False,
							"description":"Update profile"
							}
			else:
				resp_dict_banner4 = {
							"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/9.png",
							"image_overlay_text":"",
							"image_overlay_position":"",
							"action_type":"external",
							"action_url":"https://t.me/StreakTech",
							"external_url":False,
							"description":"Telegram channel"
							}
		else:
			if user_activity.profile_pic_changed<=0 and user_activity.phone_number_added==0:
				resp_dict_banner4 = {
							"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/4.png",
							"image_overlay_text":"",
							"image_overlay_position":"",
							"action_type":"navigation",
							"action_url":"/account?tab=profile",
							"external_url":False,
							"description":"Update profile picture"
							}
			else:
				resp_dict_banner4 = {
							"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/9.png",
							"image_overlay_text":"",
							"image_overlay_position":"",
							"action_type":"external",
							"action_url":"https://t.me/StreakTech",
							"external_url":False,
							"description":"Telegram channel"
							}

		if any(word in request.META['HTTP_USER_AGENT'] for word in ["webOS","iPhone","iPad","iPod"]):
			resp_dict_banner2 = {
								"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/offer_img1.png",
								"image_overlay_text":"",
								"image_overlay_position":"",
								"action_type":"external",
								"action_url":"/account?tab=pricing",
								"external_url":False,
								"description":"Festive offer"
								}
		dashboard_response = [resp_dict_banner2,resp_dict_banner1,resp_dict_banner3,resp_dict_banner4]
	except:
		print traceback.format_exc()
		update_activity(request,"login")
		if any(word in request.META['HTTP_USER_AGENT'] for word in ["webOS","iPhone","iPad","iPod"]):
			resp_dict_banner2 = {
							"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/offer_img1.png",
							"image_overlay_text":"",
							"image_overlay_position":"",
							"action_type":"external",
							"action_url":"/account?tab=pricing",
							"external_url":False,
							"description":"Festive offer"
							}
		dashboard_response = [resp_dict_banner2,resp_dict_banner1,resp_dict_banner3,resp_dict_banner4]
		print traceback.format_exc()
	return JsonResponse({"status":"success","dashboard_carousel":dashboard_response[0:4]})


def profile_carousel(request):
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
	
	if request.method!="GET":
		return JsonResponse({"status":"error","error_msg":"Method"})

	login_count = 0
	invite_msg = "Never miss an opportunity, with Streak do strategic trading without coding, join now, visit "+urllib.quote_plus("https://streak.tech?utm_source=appshare")
	resp_dict_banner1={
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/11.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"social_share",
						"action_url":"/invite?title=Join Streak now&message="+invite_msg+"&img_url=https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/share_banner.png",
						"external_url":False,
						"description":"Invite friends"
					}
	resp_dict_banner2={
					"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/9.png",
					"image_overlay_text":"",
					"image_overlay_position":"",
					"action_type":"external",
					"action_url":"https://t.me/StreakTech",
					"external_url":False,
					"description":"Telegram channel"
					}
	resp_dict_banner3={
					"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/3.png",
					"image_overlay_text":"",
					"image_overlay_position":"",
					"action_type":"navigation",
					"action_url":"/create",
					"external_url":False,
					"description":"Create strategy",
					}
	resp_dict_banner4={
					"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/4.png",
					"image_overlay_text":"",
					"image_overlay_position":"",
					"action_type":"navigation",
					"action_url":"/market_watch?tab=top_movers",
					"external_url":False,
					"description":"Top movers"
					}
	dashboard_response = [resp_dict_banner1,resp_dict_banner2,resp_dict_banner3,resp_dict_banner3]
		
	try:
		user_activity = models.UserActivity.objects.get(user_uuid=user_uuid)
		login_count = user_activity.login_count
		
		# logic for banner 1
		if login_count >-1:
			resp_dict_banner1 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/1.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"navigation",
						"action_url":"/strategies?tab=discover",
						"external_url":False,
						"description":"Discover strategies"
						}
		elif login_count <=2:
			resp_dict_banner1 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/6.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"navigation",
						"action_url":"/scans/popular'",
						"external_url":False,
						"description":"Discover scanner"
						}
		elif login_count <=3:
			resp_dict_banner1 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/7.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"navigation",
						"action_url":"/scanner",
						"external_url":False,
						"description":"Create scanner"
						}
		else:
			resp_dict_banner1 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/7.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"navigation",
						"action_url":"/scanner",
						"external_url":False,
						"description":"Create scanner"
						}


		# logic for banner 2
		if login_count >-1:
			resp_dict_banner2 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/2.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"popup",
						"action_url":"/demo_request",
						"external_url":False,
						"description":"Demo request"
						}
		elif login_count <=2:
			resp_dict_banner2 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/2.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"popup",
						"action_url":"/demo_request",
						"external_url":False,
						"description":"Demo request"
						}
		elif login_count <=3:
			resp_dict_banner2 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/2.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"popup",
						"action_url":"/demo_request",
						"external_url":False,
						"description":"Demo request"
						}
		else:
			resp_dict_banner2 = {
						"image_url":"https://streak-public-assets.s3.ap-south-1.amazonaws.com/images/dashboard/2.png",
						"image_overlay_text":"",
						"image_overlay_position":"",
						"action_type":"popup",
						"action_url":"/demo_request",
						"external_url":False,
						"description":"Demo request"
						}

		# dashboard_response = [resp_dict_banner1,resp_dict_banner2,resp_dict_banner3,resp_dict_banner3]
	except:
		update_activity(request,"login")
		dashboard_response = [resp_dict_banner1,resp_dict_banner2,resp_dict_banner3,resp_dict_banner3]
		print traceback.format_exc()
	return JsonResponse({"status":"success","profile_carousel":dashboard_response[0:2]})


"""
BANNER 1

New user : Incomplete actions
Show Discover strategies till one backtest done

Partial and no strategies -> Complete you first strategy

0 stratgies -> Create first strategy 


Discover scanner till 0 scan run

Partial and no strategies -> Complete you first scanner

0 stratgies -> Create first scanner



BANNER 2

Demo request till taken or upto monthly plans, free trial, plan expired etc

Advanced demo for retention, when monthly plan 2 weeks before expiry and notifications


Upcoming webinars - save the dates / on click (add to your calendar)/ if on same day take to youtube/ and keep watch now till next webinar is scheduled 

Varsity

And 

other educational material


BANNER 3


Create watchlist - till first watchlist created

top movers - always show


Trending stocks technicals and strategies

.... 

....

BANNER 4


Profile pic

Phone number

Subscribe 

referral

rate us

share
"""