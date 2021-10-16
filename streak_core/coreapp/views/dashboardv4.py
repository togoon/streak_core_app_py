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
from mongoengine import DoesNotExist,NotUniqueError
import os
import re
from django.middleware import csrf
import os
import time
import ujson
import math

screener_time_frame_mapping = { 
			"1 Minute":"min", 
			"5 Minutes":"5min", 
			"10 Minutes":"10min", 
			"15 Minutes":"15min", 
			"30 Minutes":"30min", 
			"1 Hour":"hour", 
			"1 Day":"day", 
			}

def get_top_movers(request):
	resp_json = False
	if(request.META.get('HTTP_X_CSRFTOKEN',None)):
		resp_json = True
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1c':
		user_uuid = 'e7ad2fc7-9e1c-4fe6-8d34-fb9a8a15a650'
		user_is_auth = True
		request.session['user_is_auth'] = True
		request.session['user_uuid'] = '123'
		user_uuid = 'e7ad2fc7-9e1c-4fe6-8d34-fb9a8a15a650'

	if not user_is_auth:
		if resp_json:
			return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)

	if request.method!='GET':
		return JsonResponse({"status":"error","error":"Invalid method","error_msg":"Invalid method"})
	else:
		payload = request.GET

	con = get_redis_connection('screener_cache')
	# s&p 100 top losers "c102f76b-9050-4cde-a26d-bb496213e802"
	# s&p 500 top losers "dd0000e2-8812-4eb3-9091-0bf413773553"
	# s&p 100 top gainers "40bd0685-4673-4448-9cf9-9d77dc1dea17"
	# s&p 500 top gainers "f59eb60b-9649-44fb-9ea3-558f34b55a76"
	screener_cache = con.get('screener_cron_day')
	screener_cache = ujson.loads(screener_cache)
	seg_filter = payload.get("filter","")
	screener_uuid = []
	if seg_filter=="" or seg_filter=="US Equity":
		screener_uuid = ["f59eb60b-9649-44fb-9ea3-558f34b55a76","40bd0685-4673-4448-9cf9-9d77dc1dea17","dd0000e2-8812-4eb3-9091-0bf413773553","c102f76b-9050-4cde-a26d-bb496213e802"]
	screener_result = []
	# print(screener_cache.keys())
	for s in screener_uuid:
		screener_result = screener_result + screener_cache.get(s,[])

	return JsonResponse({"status":"success","top_movers":screener_result})


def partial_complete(request):
	resp_json = False
	if(request.META.get('HTTP_X_CSRFTOKEN',None)):
		resp_json = True
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1c':
		# user_uuid = 'e7ad2fc7-9e1c-4fe6-8d34-fb9a8a15a650'
		user_is_auth = True
		request.session['user_is_auth'] = True
		# request.session['user_uuid'] = '123'
		# user_uuid = 'e7ad2fc7-9e1c-4fe6-8d34-fb9a8a15a650'

	if not user_is_auth:
		return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)

	if request.method!='GET':
		return JsonResponse({"status":"error","error":"Invalid method","error_msg":"Invalid method"})
	else:
		payload = request.GET

	partial_algos = []
	partial_algo = models.Algorithm._get_collection().find({"user_uuid":user_uuid,"complete":False}).sort([("updated_at",-1)]).limit(10)
	for p in partial_algo:
		t = p
		t["algo_state"] = ""
		t["html_block"] = ""
		if t.get("complete",True) and t.get("percent_complete",100)==100:
			backtest = models.BacktestMeta._get_collection().find({'user_uuid':user_uuid,'algo_uuid':t['algo_uuid']},{'_id':0 })
			if backtest.count()<1:
				t["percent_complete"]=99
				t["complete"] = False
		if t.get("complete",True) is False:
			t.pop("_id","")
			partial_algos.append(t)

	partial_screeners = []
	partial_screener = models.Screener._get_collection().find({"user_uuid":user_uuid}).sort([("updated_at",-1)]).limit(10)
	# print(parital_screener.count(),user_uuid)
	for p in partial_screener:
		t = p
		# print(t["screener_state"])
		if(t["screener_state"].get("last_scan","")=="" and (t.get("screener_result",[]))==0):
			scanner_live = models.ScreenerAlert._get_collection().count({"user_uuid":user_uuid,"screener_uuid":t["screener_uuid"],"status":0})
			if scanner_live==0:
				t["screener_state"]=""
				t["percent_complete"] = 75
				t["complete"] = False
				t.pop("_id","")
				partial_screeners.append(t)

	return JsonResponse({"status":"success","partial_algos":partial_algos,"partial_screeners":partial_screeners})


def get_banner(request):
	pass


def dashboard_card(request):
	pass 