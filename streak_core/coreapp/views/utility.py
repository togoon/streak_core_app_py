#This will contain all the experince utility components like auto-complete, fetching json tree, etc

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
from mongoengine import NotUniqueError
import os
#import kiteconnect
from django.middleware import csrf

import os
import time
import payments
import razorpay
import userflow
from coreapp.views.ams_helper import *
import re
from django.contrib.auth import update_session_auth_hash

parsing_tree = None
with open(os.path.dirname(os.path.abspath(__file__))+'/../../js_parsing_tree_original.json') as parsing_tree_file:	
	parsing_tree = json.load(parsing_tree_file)['main']
	parsing_temp = []
	for i in parsing_tree['indicator'].keys():
		x = parsing_tree['indicator'][i]
		x['id']=i
		parsing_temp.append(x)

	parsing_tree = parsing_temp

def load_autocomplete_data(request):
	"""
	load autocomplete data into redis for instruments lookup
	http://localhost/broker_login_url/?json=true&kite3=true
	eg: /loadautocomplete/?secret=testing
	"""
	if request.method == 'GET':
		if request.GET.get('secret') == settings.AUTOCOMPLTE_SECRET:
			import csv
			csv_path = "instruments"
			con = get_redis_connection("default")
			pipeline = con.pipeline()
			pipeline.delete('stock_lookup')
			pipeline.delete('stock_lookup_symbol')
			with open(csv_path, "rb") as file_obj:
				reader = csv.reader(file_obj)
				c = 0
				for row in reader:
					if c:
						x = row[2].split('-')
						if not row[2][-3:] in ['-BL','-BE'] and row[9] in ['EQ','FUT'] and row[11] in ['NSE','NFO','CDS','MCX-FUT'] and ('-' not in row[2] or len(x[-1])>2):
							if row[3] == '':
								row[3] = row[2]
								if 'FUT' in row[3]:
									row[3] = row[3].split('1')
									row[3] = row[3][0]+row[3][-1][-3:]
							pipeline.zadd('stock_lookup',0,"{}:{}:{}:{}:{}".format(
								row[3].lower(), # name
								row[2].lower(), # trading symbol
								row[9].lower(), # instrument_type
								row[10].lower(), # segment
								row[11].lower(), # exchange
								row[1]) # exchange token
							)
							pipeline.zadd('stock_lookup_symbol',0,"{}:{}:{}:{}:{}".format(
								row[2].lower(), # trading symbol
								row[2].lower(), # trading symbol
								row[9].lower(), # instrument_type
								row[10].lower(), # segment
								row[11].lower(), # exchange
								row[1]) # exchange token
							)
							pipeline.set('instruments:'+':'.join(row[:3]+row[4:]),row[3].lower())
					else:
						c = 1 # for not storing 1st row of csv

			pipeline.set("instruments:265:1:SENSEX:0.0::0.0:0.0:0:EQ:INDICES:BSE","SENSEX")
			pipeline.execute()

			#TODO load indicator autocomplete data

			return JsonResponse({'status':'success'})
	return JsonResponse({'status':'error'})

def autocomplete(request):
	"""
	autocomplete for instruments lookup
	eg: /autocomplete/?query=hd
	"""
	# preform autocomplete
	con = get_redis_connection("default")
	query = request.GET.get('query',None)
	results = []
	if query:
		query2 = query.replace(' ','')
		data = con.zrangebylex('stock_lookup', "[{}".format(query2.lower()), "[{}\xff".format(query2))
		# print("found {} items".format(len(data)))
		if len(data)>10:
			data = data[:10]

		data1 = con.zrangebylex('stock_lookup', "[{}".format(query.lower()), "[{}\xff".format(query))
		# print("found {} items".format(len(data)))
		if len(data1)>10:
			data1 = data1[:10]

		# query = query.replace(' ','')
		data2 = con.zrangebylex('stock_lookup_symbol', "[{}".format(query.lower()), "[{}\xff".format(query))
		# print("found {} items".format(len(data)))
		if len(data)>10:
			data2 = data2[:10]

		resp = {}
		for index, item in enumerate(data2+data1+data):
			item = item.decode("utf-8")
			item = item.split(':')
			if resp.get(item[1],'')=='' and item[3]!='nse-indices':
				results.append([i.upper() for i in item])
				resp[item[1]]=item[1]

		user_uuid = request.session.get('user_uuid','')
		if user_uuid != '':
			try:
				baskets = con.hgetall('baskets_'+user_uuid)
				if baskets != None:
					baskets_list = baskets.keys()
					for b in baskets_list:
						if query.lower() in b.lower():
							print query,b
							results = [[b,b,'basket','',len(baskets[b])]]+results
							resp[b] = b
					# if any(query.lower() in b.lower() for b in baskets):
					# 	print baskets
					# 	results = [b]+results
					# 	resp[b] = b
			except:
				pass
	return JsonResponse({'status':'success','results':sorted(results, key = lambda ele : len(ele[0]))})

def search_dict(s):
	s = s.lower() # it is a nice feature to ignore case
	s_item = {}
	for item in parsing_tree:
		s_item['name'] = item['name']
		s_item['description'] = item['description']
		s_item['tag'] = item['tag']
		s_item['tooltip'] = item['tooltip']

		if any(s in v.lower() for v in s_item.values()): # if any value contains s
		# for k,v in item.iteritems():
		# 	if not isinstance(v,list) and k in ['name','description','tag','tooltip']:
		# 		if s in v.lower():
			yield item['id'] # spit out the item, this is a generator function

def search_dict2(s):
	s = s.lower() # it is a nice feature to ignore case
	s_item = {}
	for item in parsing_tree:
		s_item['name'] = item['name']
		s_item['description'] = item['description']
		s_item['tag'] = item['tag']
		s_item['class'] = item['class']
		s_item['tooltip'] = item['tooltip']
		if any(s in v.lower() for v in s_item.values()): # if any value contains s
		# for k,v in item.iteritems():
		# 	if not isinstance(v,list) and k in ['name','description','tag','tooltip']:
		# 		if s in v.lower():
			yield [item['id'],item['description']] # spit out the item, this is a generator function


def update_device_token(request):
	if request.method=='POST':
		UserDeviceToken.objects.save

	return JsonResponse({'status':'success'})
	
def autocomplete_indicators(request):
	"""
	autocomplete for instruments lookup
	eg: /autocomplete/?query=hd
	"""
	# preform autocomplete

	query = request.GET.get('query',None)

	results = set()

	if parsing_tree and query:
		# iterate over at most 5 first results
		for result in itertools.islice(search_dict(query), 10):   
			results.add(result)

		# if len(data)>20:
		# 	data = data[:20]
		# for index, item in enumerate(data):
		# 	item = item.decode("utf-8")
		# 	item = item.split(':')
		# 	results.append([i.upper() for i in item])

	return JsonResponse({'status':'success','results':list(results)})

def autocomplete_indicators2(request):
	"""
	autocomplete for instruments lookup
	eg: /autocomplete/?query=hd
	"""
	# preform autocomplete

	query = request.GET.get('query',None)

	results = dict()

	if parsing_tree and query:
		# iterate over at most 5 first results
		for result in itertools.islice(search_dict2(query), 20):   
			results[result[0]]=result

		# if len(data)>20:
		# 	data = data[:20]
		# for index, item in enumerate(data):
		# 	item = item.decode("utf-8")
		# 	item = item.split(':')
		# 	results.append([i.upper() for i in item])
	response = list()
	for k,v in results.iteritems():
		response.append(v)

	response = sorted(response, key = lambda ele : len(ele[0]))[:10]
	return JsonResponse({'status':'success','results':response})

def update_preference(request):
	user_uuid = request.session.get('user_uuid','123')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:

	# if not user_is_auth:
	# 	return JsonResponse({'status':'error'})

	if request.method == "POST":
		indicator = request.POST.get('indicator',None)
		con = get_redis_connection("default")
		if indicator:
			# fetch if already exists
			res = con.hget('user_pref',user_uuid)
			pref = {}
			if res:
				pref = eval(res)
				if indicator not in pref.keys():
					pref[indicator]=1
				else:
					pref[indicator]+=1
			else:
				pref[indicator]=1
			pickle_pref = pickle.dumps(pref)
			con.hset('user_pref',user_uuid,pref)
		return JsonResponse({'status':'success'})
	return JsonResponse({'status':'error'})

def user_preference(request):
	user_uuid = request.session.get('user_uuid','123')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:

	if not user_is_auth:
		return JsonResponse({'status':'error','error_msg':'Session expired'})

	if request.method == "POST":
		prefs = request.POST.get('prefs',None)
		con = get_redis_connection("default")
		if prefs:
			con.hset('user_pref',user_uuid,pref)
		return JsonResponse({'status':'success'})
	if request.method == "GET":
		con = get_redis_connection("default")
		if prefs:
			prefs = con.hget('user_pref',user_uuid)
		return JsonResponse({'status':'success','prefs':prefs})
	return JsonResponse({'status':'error','error_msg':'Invalid method'})

def update_preference2(request):
	user_uuid = request.session.get('user_uuid','123')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:

	# if not user_is_auth:
	# 	return JsonResponse({'status':'error'}))

	if request.method == "POST":
		indicator = request.POST.get('indicator',None)
		con = get_redis_connection("default")
		if indicator:
			# fetch if already exists
			res = con.hget('user_pref',user_uuid)
			pref = ''#[]
			if res:
				pref = res
				if indicator not in pref:
					pref=indicator+','+pref
				else:
					pref.replace(indicator+',','')
			else:
				pref=indicator+','
			# pickle_pref = pickle.dumps(pref)
			con.hset('user_pref',user_uuid,pref)
		return JsonResponse({'status':'success'})
	return JsonResponse({'status':'error'})

def load_preference2(request):
	user_uuid = request.session.get('user_uuid','123')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:

	# if not user_is_auth:
	# 	return JsonResponse({'status':'error'})

	if request.method == "GET":
		res = []
		if user_uuid:
			con = get_redis_connection("default")
			res = con.hget('user_pref',user_uuid)
			if res:
				if res[-1]==',':
					res=res[:-1]
				pref = res.split(',')
				res = pref 
				return JsonResponse({'status':'success','ti_indicators':list(res)})
			else:
				return JsonResponse({'status':'success','ti_indicators':list([])})
	return JsonResponse({'status':'success'})

def load_preference(request):
	user_uuid = request.session.get('user_uuid','123')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:

	# if not user_is_auth:
	# 	return JsonResponse({'status':'error'})
	if request.method == "GET":
		res = []
		if user_uuid:
			con = get_redis_connection("default")
			res = con.hget('user_pref',user_uuid)
			if res:
				pref = eval(res)
				res,temp = zip(*sorted(pref.items(),key=lambda(k,v):v,reverse=True))
		return JsonResponse({'status':'success','ti_indicators':list(res)})
	return JsonResponse({'status':'success'})

def is_algorithm_deployed(request):
	user_uuid = request.session.get('user_uuid','123')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:

	# if not user_is_auth:
	# 	return JsonResponse({'status':'error'})
	if request.method == 'GET':
		algo_uuid = request.GET.get('algo_uuid','')
		
		if algo_uuid=='':
			return JsonResponse({'status':'error'})

		con = get_redis_connection("default")
		# res = con.keys('deployed:*:'+algo_uuid+':*')
		res = get_deployment_keys({"algo_uuid":algo_uuid,"status":0,"expiration_time":{"$gte":datetime.datetime.now()}})
		if len(res)<1:
			return JsonResponse({'status':'success','algo_uuid':algo_uuid})
		else:
			return JsonResponse({'status':'error','error':'Strategy already deployed with some equity','deployed':True})
	return JsonResponse({'status':'error'})

def is_sym_seg_deployed(sym_seg):
	con = get_redis_connection("default")
	res = con.keys('deployed:*:user_uuid:algo_uuid'+sym_seg+':*')
	if len(res)>0:
		return True
	return False

def get_positions(request):
	
	user_uuid = request.session.get('user_uuid','123')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:

	# if not user_is_auth:
	# 	return JsonResponse({'status':'error'})

	if request.method == "GET":
		try:
			algo_uuid = request.GET.get('algo_uuid','')
			deployment_uuid = request.GET.get('deployment_uuid','')
			position = models.HoldingsForAlgorithm.objects.get(user_uuid=user_uuid,algo_uuid=algo_uuid,deployment_uuid=deployment_uuid)
			return JsonResponse({'status':'success','position':json.loads(position.to_json())})
		except:
			print traceback.format_exc()

	return JsonResponse({'status':'error'})

def get_live_algos_util(user_uuid,algo_uuid,sym,seg):
	algo_name = []
	try:
		sym_seg = seg+'_'+sym;
		con = get_redis_connection("default")
		# res = con.keys('deployed:*:'+user_uuid+':*:'+sym_seg+':*')
		res = get_deployment_keys({"user_uuid":user_uuid,"segment_symbol":seg_sym,"status":0,"expiration_time":{"$gte":datetime.datetime.now()}})
		if len(res)>0:
			for r in res:
				algo_obj = con.get(r)
				if algo_obj:
					algo_obj = ujson.loads(algo_obj)
					algo_name.append(algo_obj['algo_obj']['algo_name'])
	except:
		print traceback.format_exc()

	return algo_name

def get_live_algos(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth'})
	if request.method!='GET':
		return JsonResponse({"status":"error",'error-type':'method'})

	if request.method == "GET":
		try:
			sym = request.GET.get('symbol','').upper()
			seg = request.GET.get('exchange','').upper()
			product = request.GET.get('product','').upper()
			if seg=='CDS':
				seg = 'CDS-FUT'
			elif seg=='MCX':
				seg = 'MCX'
			elif seg=='NFO':
				if str(sym).endswith("CE") or str(sym).endswith("PE"):
					seg = 'NFO-OPT'
			 	else:
					seg = 'NFO-FUT'

			sym_seg = seg+'_'+sym;
			con = get_redis_connection("default")
			# res = con.keys('deployed:'+user_uuid+':*:'+sym_seg+':*')
			res = get_deployment_keys({"user_uuid":user_uuid,"segment_symbol":sym_seg,"status":0,"expiration_time":{"$gte":datetime.datetime.now()}})  
			algo_name = []
			if len(res)>0:
				for r in res:
					algo_obj = con.get(r)
					if algo_obj:
						algo_obj = ujson.loads(algo_obj)
						if algo_obj['algo_obj'].get('product','')==product:
							algo_name.append(algo_obj['algo_obj']['algo_name'])
			return JsonResponse({'status':'success','algo_names':algo_name})
		except:
			print traceback.format_exc()
	return JsonResponse({'status':'error'})

def save_redirect(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error_msg':'Auth'},status=401)
	if request.method == "GET":
		return JsonResponse({'status':'success','redirect_params':request.session.pop("redirect_params","")})
	if request.method == "POST":
		redirect_params = request.POST.get("redirect_params","")
		if redirect_params!="":
			request.session["redirect_params"] = redirect_params
			return JsonResponse({'status':"success"})
		return JsonResponse({'status':'error',"error_msg":"Missing params"})
	return JsonResponse({'status':'error',"error_msg":"Invalid method"})


def initialize_account2(request):
	if request.method=='GET':
		if request.GET.get('secret')=='testing_initialization':
			initialize_account(user_uuid=request.GET.get('user_uuid',''))
			return JsonResponse({'status':'success'})
	return JsonResponse({'status':'error'})

def initialize_account(user_uuid=''):
	if(user_uuid!=''):
		try:
			con = get_redis_connection("default")
			# algo_res = con.get("initializing_algo")
			# r = con.hset('baskets_'+user_uuid,"Coinbase Basket","[{\"from\":\"LTC\",\"id\":\"FKXEvc78j6UWcNkPgQ3gVE\",\"name\":\"LITECOIN to EURO\",\"segment\":\"COINBASE\",\"symbol\":\"LTC/EUR\",\"to\":\"EUR\"},{\"from\":\"ETH\",\"id\":\"5jkekQaNWtBAzY8iGPTZEc\",\"name\":\"ETHEREUM to US DOLLAR\",\"segment\":\"COINBASE\",\"symbol\":\"ETH/USD\",\"to\":\"USD\"},{\"from\":\"ZEC\",\"id\":\"Zr9HTaVKAPiezg6b69T9Lf\",\"name\":\"ETHEREUM to US DOLLAR COIN\",\"segment\":\"COINBASE\",\"symbol\":\"ZEC/USDC\",\"to\":\"USDC\"},{\"from\":\"LTC\",\"id\":\"Qpqq7nfVUPZvcqgvvNoybL\",\"name\":\"LITECOIN to BITCOIN\",\"segment\":\"COINBASE\",\"symbol\":\"LTC/BTC\",\"to\":\"BTC\"},{\"from\":\"ETH\",\"id\":\"cZqgKfejN3ufoX7LXeQwZA\",\"name\":\"ETHEREUM to BITCOIN\",\"segment\":\"COINBASE\",\"symbol\":\"ETH/BTC\",\"to\":\"BTC\"},{\"from\":\"ETH\",\"id\":\"wE7RaFAttszhNQXWUnP6VE\",\"name\":\"ETHEREUM to US DOLLAR COIN\",\"segment\":\"COINBASE\",\"symbol\":\"ETH/USDC\",\"to\":\"USDC\"},{\"from\":\"BTC\",\"id\":\"rXXq6Fjwmp9hnyUN6K6tvZ\",\"name\":\"BITCOIN to US DOLLAR\",\"segment\":\"COINBASE\",\"symbol\":\"BTC/USD\",\"to\":\"USD\"},{\"from\":\"XRP\",\"id\":\"aWRYzg7gaJMwcnEyrFraLR\",\"name\":\"RIPPLE to BITCOIN\",\"segment\":\"COINBASE\",\"symbol\":\"XRP/BTC\",\"to\":\"BTC\"},{\"from\":\"XRP\",\"id\":\"FrCCnCkyqnXxM872Fn4edd\",\"name\":\"RIPPLE to US DOLLAR\",\"segment\":\"COINBASE\",\"symbol\":\"XRP/USD\",\"to\":\"USD\"},{\"from\":\"XRP\",\"id\":\"pMVEpTvrfmwjUB3rJsKyEA\",\"name\":\"RIPPLE to EURO\",\"segment\":\"COINBASE\",\"symbol\":\"XRP/EUR\",\"to\":\"EUR\"}]")
			# r = con.hset('baskets_'+user_uuid,"USDC Basket","[{\"from\":\"EOS\",\"id\":\"EkdTLhwCNqU7v6dFvN2SZi\",\"name\":\"EOS to US DOLLAR COIN\",\"segment\":\"BINANCE\",\"symbol\":\"EOS/USDC\",\"to\":\"USDC\"},{\"from\":\"BAT\",\"id\":\"N8nJKsXEqkZbmiWUzLH95e\",\"name\":\"BAT to US DOLLAR COIN\",\"segment\":\"COINBASE\",\"symbol\":\"BAT/USDC\",\"to\":\"USDC\"},{\"from\":\"ZEC\",\"id\":\"s67k6EM45CgshL5odBYCea\",\"name\":\"ETHEREUM to US DOLLAR COIN\",\"segment\":\"COINBASE\",\"symbol\":\"ZEC/USDC\",\"to\":\"USDC\"},{\"from\":\"ETH\",\"id\":\"6yw79JGNu73fCJdjSvd6x7\",\"name\":\"ETHEREUM to US DOLLAR COIN\",\"segment\":\"COINBASE\",\"symbol\":\"ETH/USDC\",\"to\":\"USDC\"},{\"from\":\"BTC\",\"id\":\"x5n4JBkFB75n6Lrn4kZCKh\",\"name\":\"BITCOIN to US DOLLAR COIN\",\"segment\":\"BINANCE\",\"symbol\":\"BTC/USDC\",\"to\":\"USDC\"},{\"from\":\"ETH\",\"id\":\"2qoyVXhwLkLZbVKBbjHGdk\",\"name\":\"ETHEREUM to US DOLLAR COIN\",\"segment\":\"BINANCE\",\"symbol\":\"ETH/USDC\",\"to\":\"USDC\"},{\"from\":\"LTC\",\"id\":\"QbU42ienFTBDLkoaWD8Vch\",\"name\":\"LITECOIN to US DOLLAR COIN\",\"segment\":\"POLONIEX\",\"symbol\":\"LTC/USDC\",\"to\":\"USDC\"},{\"from\":\"LTC\",\"id\":\"gDxdF9K6nvQEVEqdk4Tiu8\",\"name\":\"LITECOIN to US DOLLAR COIN\",\"segment\":\"BINANCE\",\"symbol\":\"LTC/USDC\",\"to\":\"USDC\"},{\"from\":\"ETH\",\"id\":\"DZbLPjeqLW5vYJshKfaJPW\",\"name\":\"ETHEREUM to US DOLLAR COIN\",\"segment\":\"POLONIEX\",\"symbol\":\"ETH/USDC\",\"to\":\"USDC\"},{\"from\":\"XRP\",\"id\":\"vcKD2rUmmVRScBopMrqAKd\",\"name\":\"RIPPLE to US DOLLAR COIN\",\"segment\":\"POLONIEX\",\"symbol\":\"XRP/USDC\",\"to\":\"USDC\"}]")
			# r = con.hset('baskets_'+user_uuid,"BTC Basket","[{\"id\":\"D9W3EwFAdw3djeDmXy2eYf\",\"name\":\"BITCOIN to US DOLLAR TETHER\",\"segment\":\"HITBTC\",\"symbol\":\"BTC/USDT\"},{\"id\":\"WchdbHqGJowTiSC3NfXkag\",\"name\":\"BITCOIN to US DOLLAR TETHER\",\"segment\":\"BINANCE\",\"symbol\":\"BTC/USDT\"},{\"id\":\"VfdWjVQ6F9JYBbQGt4FbED\",\"name\":\"BITCOIN to US DOLLAR\",\"segment\":\"COINBASE\",\"symbol\":\"BTC/USD\"}]")
			# r = con.hset('baskets_'+user_uuid,"ETH Basket","[{\"id\":\"enrSCRKw4aaeQSCqFhCR5S\",\"name\":\"ETHEREUM to US DOLLAR TETHER\",\"segment\":\"HITBTC\",\"symbol\":\"ETH/USDT\"},{\"id\":\"V3uygxhCBsv4RA3fZVrLmF\",\"name\":\"ETHEREUM to US DOLLAR COIN\",\"segment\":\"COINBASE\",\"symbol\":\"ETH/USDC\"},{\"id\":\"gud3X9rx847SV4XuVj7NH4\",\"name\":\"ETHEREUM to US DOLLAR\",\"segment\":\"COINBASE\",\"symbol\":\"ETH/USD\"},{\"id\":\"MA2XwiTh9znfM5ZPTUZJnM\",\"name\":\"ETHEREUM to US DOLLAR TETHER\",\"segment\":\"BINANCE\",\"symbol\":\"ETH/USDT\"}]")
			# r = con.hset('baskets_'+user_uuid,"LTC Basket","[{\"id\":\"NwqefT2vHCe7YfC3Pyg8PF\",\"name\":\"LITECOIN to US DOLLAR TETHER\",\"segment\":\"BINANCE\",\"symbol\":\"LTC/USDT\"},{\"id\":\"dmYRWhPVnt4M6rcB4XNXfC\",\"name\":\"LITECOIN to US DOLLAR\",\"segment\":\"COINBASE\",\"symbol\":\"LTC/USD\"},{\"id\":\"DCNpe7o5vKsuSmAakFSBcm\",\"name\":\"LITECOIN to US DOLLAR TETHER\",\"segment\":\"HITBTC\",\"symbol\":\"LTC/USDT\"},{\"id\":\"V6pVTrQHzQubbVfYF7TAQ6\",\"name\":\"LITECOIN to BITCOIN\",\"segment\":\"HITBTC\",\"symbol\":\"LTC/BTC\"},{\"id\":\"hysxEHsCMrkcYyAWKofaFc\",\"name\":\"LITECOIN to BITCOIN\",\"segment\":\"BINANCE\",\"symbol\":\"LTC/BTC\"},{\"id\":\"sgJZ2AkDjn2chfm3Cn9hCW\",\"name\":\"LITECOIN to BITCOIN\",\"segment\":\"COINBASE\",\"symbol\":\"LTC/BTC\"}]")
			# r = con.hset('baskets_'+user_uuid,"Binance Basket","[{\"from\":\"EOS\",\"id\":\"HRndVimccGWyuvTzkkNfa8\",\"name\":\"EOS to ETHEREUM\",\"segment\":\"BINANCE\",\"symbol\":\"EOS/ETH\",\"to\":\"ETH\"},{\"from\":\"LTC\",\"id\":\"4p7kTob6ocHyHmDZWvBDm9\",\"name\":\"LITECOIN to US DOLLAR TETHER\",\"segment\":\"BINANCE\",\"symbol\":\"LTC/USDT\",\"to\":\"USDT\"},{\"from\":\"EOS\",\"id\":\"48VzhkVZ8hELC5nV2VTCXn\",\"name\":\"EOS to US DOLLAR COIN\",\"segment\":\"BINANCE\",\"symbol\":\"EOS/USDC\",\"to\":\"USDC\"},{\"from\":\"ETH\",\"id\":\"Rq3UMtMNLkk2tSMm3aD3VL\",\"name\":\"ETHEREUM to BITCOIN\",\"segment\":\"BINANCE\",\"symbol\":\"ETH/BTC\",\"to\":\"BTC\"},{\"from\":\"BTC\",\"id\":\"d35SywfgyDvsfMoEgTraJB\",\"name\":\"BITCOIN to US DOLLAR TETHER\",\"segment\":\"BINANCE\",\"symbol\":\"BTC/USDT\",\"to\":\"USDT\"},{\"from\":\"EOS\",\"id\":\"jbEnwZhXSfWhBShwvT7DoH\",\"name\":\"EOS to US DOLLAR TETHER\",\"segment\":\"BINANCE\",\"symbol\":\"EOS/USDT\",\"to\":\"USDT\"},{\"from\":\"BTC\",\"id\":\"tGViQ78Qu3kQLia7HCg65o\",\"name\":\"BITCOIN to US DOLLAR COIN\",\"segment\":\"BINANCE\",\"symbol\":\"BTC/USDC\",\"to\":\"USDC\"},{\"from\":\"ETH\",\"id\":\"nsoxv7qiA58WLK7LjcyLzV\",\"name\":\"ETHEREUM to US DOLLAR COIN\",\"segment\":\"BINANCE\",\"symbol\":\"ETH/USDC\",\"to\":\"USDC\"},{\"from\":\"EOS\",\"id\":\"EVierwpMS5sBebbkBq3yhF\",\"name\":\"EOS to BITCOIN\",\"segment\":\"BINANCE\",\"symbol\":\"EOS/BTC\",\"to\":\"BTC\"},{\"from\":\"XRP\",\"id\":\"EAa45F7BaeQEDpPexyh65j\",\"name\":\"RIPPLE to BITCOIN\",\"segment\":\"BINANCE\",\"symbol\":\"XRP/BTC\",\"to\":\"BTC\"}]")
			# r = con.hset('baskets_'+user_uuid,"Poloniex Basket","[{\"from\":\"BTC\",\"id\":\"U9GqGSVYMwpy3aWCqFT2SZ\",\"name\":\"BITCOIN to US DOLLAR TETHER\",\"segment\":\"POLONIEX\",\"symbol\":\"BTC/USDT\",\"to\":\"USDT\"},{\"from\":\"ETH\",\"id\":\"g4pmLiTDdnRKQ6H6JWqFP4\",\"name\":\"ETHEREUM to US DOLLAR TETHER\",\"segment\":\"POLONIEX\",\"symbol\":\"ETH/USDT\",\"to\":\"USDT\"},{\"from\":\"LTC\",\"id\":\"5oePk2LHJDduDBdgfTN7ze\",\"name\":\"LITECOIN to US DOLLAR COIN\",\"segment\":\"POLONIEX\",\"symbol\":\"LTC/USDC\",\"to\":\"USDC\"},{\"from\":\"ETH\",\"id\":\"EmwNKHzZ5gXb34p3hPccq8\",\"name\":\"ETHEREUM to BITCOIN\",\"segment\":\"POLONIEX\",\"symbol\":\"ETH/BTC\",\"to\":\"BTC\"},{\"from\":\"LTC\",\"id\":\"dX3v4Ur3KNTJFTLWwgogBk\",\"name\":\"LITECOIN to US DOLLAR TETHER\",\"segment\":\"POLONIEX\",\"symbol\":\"LTC/USDT\",\"to\":\"USDT\"},{\"from\":\"ETH\",\"id\":\"kYvWryaWcvzXhKdQoxfHwg\",\"name\":\"ETHEREUM to US DOLLAR COIN\",\"segment\":\"POLONIEX\",\"symbol\":\"ETH/USDC\",\"to\":\"USDC\"},{\"from\":\"XRP\",\"id\":\"yu5oFRuv5XK7itUZrJ8xQa\",\"name\":\"RIPPLE to US DOLLAR COIN\",\"segment\":\"POLONIEX\",\"symbol\":\"XRP/USDC\",\"to\":\"USDC\"},{\"from\":\"XRP\",\"id\":\"4KMMTALGUWdDBKWi6a7Vv8\",\"name\":\"RIPPLE to US DOLLAR TETHER\",\"segment\":\"POLONIEX\",\"symbol\":\"XRP/USDT\",\"to\":\"USDT\"},{\"from\":\"XRP\",\"id\":\"YqiSnU4YH8WYMqdvySDkVf\",\"name\":\"RIPPLE to BITCOIN\",\"segment\":\"POLONIEX\",\"symbol\":\"XRP/BTC\",\"to\":\"BTC\"},{\"from\":\"LTC\",\"id\":\"k6zMf32CPFi5F7sWUNNDkg\",\"name\":\"LITECOIN to BITCOIN\",\"segment\":\"POLONIEX\",\"symbol\":\"LTC/BTC\",\"to\":\"BTC\"}]")
			# for a in algo_res:
				# models.Algorithm.
			algo_uuids = ['16e5d76a-ffd1-4564-91ba-719ec2a8ea6e']
			algos = models.Algorithm.objects(
					algo_uuid__in = algo_uuids
					)
			backtests = models.Backtest.objects(
					algo_uuid__in = algo_uuids
					)
			backtest_metas = models.BacktestMeta.objects(
					algo_uuid__in = algo_uuids
					)
			for a in algos:
				a.id = None
				a.user_uuid = user_uuid
				algo_uuid = str(uuid.uuid4())
				a.sample = True
				for b in backtests:
					if b.algo_uuid == a.algo_uuid:
						b.id = None
						b.user_uuid = user_uuid
						b.algo_uuid = algo_uuid

				for bm in backtest_metas:
					if bm.algo_uuid == a.algo_uuid:
						bm.id = None
						bm.user_uuid = user_uuid
						bm.algo_uuid = algo_uuid

				a.algo_uuid = algo_uuid

			if len(algos)>0:
				models.Algorithm.objects.insert(algos)
				models.Backtest.objects.insert(backtests)
				models.BacktestMeta.objects.insert(backtest_metas)
		except:
			print traceback.format_exc()
			pass

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

def send_initial_emails(user_uuid='',email='',name=''):
	# print email,name,user_uuid 
	if(email!='' and name!='' and user_uuid!=''):
		name = name.split(" ")[0]
		url = "https://mailing.streak.solutions/streak_mail/support/send_mail"
		headers = {"content-type":"application/json"}
		payload = json.dumps({
			"recipients":[email],
			"subject":"Streak | Welcome to Streak",
			"body_data":[name],
			"template_id":"welcome_new"
		})
		# print payload
		try:
			response = requests.request("POST", url, data=payload, headers=headers)
			# print response.text
			# print response.status_code
		except:
			print traceback.format_exc()

def send_subscription_emails(user_uuid='',email='',plan=''):
	# print email,name,user_uuid 
	if(email!='' and plan!='' and user_uuid!=''):
		url = "https://mailing.streak.solutions/streak_mail/support/send_mail"
		headers = {"content-type":"application/json"}
		payload = json.dumps({
			"recipients":[email],
			"subject":"Streak | "+plan.capitalize()+" to Streak",
			"body_data":[],
			"template_id":"welcome"
		})
		# print payload
		try:
			response = requests.request("POST", url, data=payload, headers=headers)
			# print response.text
			# print response.status_code
		except:
			print traceback.format_exc()

def subscription_status_changed(user_uuid='',user_broker_id='',change_type='',action='',plan='',email=''):
	if(user_uuid!='' and change_type!=''):
		try:
			url = "https://mailing.streak.solutions/streak_mail/billing/send_mail"
			method = "POST"
			params = {"subject":plan+" subscription "+action+" by "+user_broker_id+" user email=> "+email,
				"recipients":['billing@streak.tech']
				,"template_id":None,"reply_to":'support@streak.tech',"body_data":"Subscription "+change_type,"sender": "billing@streak.tech"}
			headers = {"content-type":"application/json"}
			response = requests.request(method,url,data=json.dumps(params),headers=headers,timeout=1)
			# response = requests.request("POST", url, data=payload, headers=headers,timeout=0.100)
		except:
			print traceback.format_exc()

def dummy_login(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	# if user_uuid!='' and user_is_auth:
	# 	return redirect('dashboard')

	if request.POST.get("status",'')== "success" and 'request_token' in request.POST.keys() and request.method=='POST':
		request_token = request.POST.get('request_token')

		if request.META.get("X-REFERER_LOCAL",None):
			# k_data = kite.generate_session(request_token,api_secret='uzya4puhvgt56cmsvwnsx3mjwhsnbmrc')
			h = hashlib.sha256('qh2hb38gqs09kbp6'.encode("utf-8") + request_token.encode("utf-8") + 'uzya4puhvgt56cmsvwnsx3mjwhsnbmrc'.encode("utf-8"))
			checksum = h.hexdigest()
		else:
			h = hashlib.sha256(settings.KITE_API_KEY.encode("utf-8") + request_token.encode("utf-8") + settings.KITE_API_SECRET.encode("utf-8"))
			checksum = h.hexdigest()

		if(request.session.pop('kite3','')=='true'):
			kite = kiteconnect.KiteConnect(api_key=settings.KITE_API_KEY)
			try:
				if request.META.get("X-REFERER_LOCAL",None):
					k_data = kite.generate_session(request_token,api_secret='uzya4puhvgt56cmsvwnsx3mjwhsnbmrc')
					h = hashlib.sha256('qh2hb38gqs09kbp6'.encode("utf-8") + request_token.encode("utf-8") + 'uzya4puhvgt56cmsvwnsx3mjwhsnbmrc'.encode("utf-8"))
					checksum = h.hexdigest()
				else:
					k_data = kite.generate_session(request_token,api_secret=settings.KITE_API_SECRET)
				print k_data
				return JsonResponse(k_data)
			except:
				print traceback.format_exc()
				# redirect('broker_login')

		print 'request.META.get("X-REFERER_LOCAL",None)',request.META.get("X-REFERER_LOCAL",None)
		if request.META.get("X-REFERER_LOCAL",None):
			session_data = session_handler('qh2hb38gqs09kbp6',request_token.encode("utf-8"),checksum)
		else:
			session_data = session_handler(settings.KITE_API_KEY,request_token.encode("utf-8"),checksum)
		try:
			print session_data
			assert session_data != None
			access_token = session_data['data']['access_token']
			public_token = session_data['data']['public_token']
			user_broker_id = session_data['data']['user_id']
			print user_broker_id
			# t_con = get_redis_connection("default")
			# a_results = t_con.get('beta_user_activated:'+user_broker_id)
			# if user_broker_id not in ['YJ3548','RM7807','DR5318','KR0001','DB1254','ZZ9998','DF0185','RO0057','ZO1913', 'RV3544', 'PR0734', 'DS2941','RV5544','DB0447','DA0017','DV1973','ZV3952','ZO1773','Z1967','DN4440','DV2950','RV0538','Z1956','RV5477','DD1025','SS1290','Z1825','Z2293','Z1639','Z1545','PR1843','Z1545','ZS5831','DA9083','Z1523','Z1264','DS6317','DK0315','Z1391','ZK0673','DD1255','Z1715','DN0274','Z1338','DV0337','Z1988','Z1747','DN0617','ZE3100','RB0163','Z1252','Z1229','DS1077','Z2101','ZQ2268','Z2101','DM0470','ZJ0178','DS0422','Z2230','Z1690','Z1702','Z1181','ZU9957','DL0100','DJ9362','DA3646','DL0322','DR0576','ZT4441','DV2793','ZW1962','RM4607','DA6364','RP6600', 'DO0027','PS7067','Z1015','DP3658','ZI9439','DA3056','DG0951','DM0446','DR0117']: 
			# if a_results is None:
			# 	print 'not allowed user'
			# 	return redirect('home') 
			request.session['access_token']=access_token
			request.session['public_token']=public_token
			request.session['user_broker_id']=user_broker_id
			request.session['full_broker_name'] = "zerodha"
			# request.session['first_time_login'] = True
			# request.session['session_secret'] = generate_random_hash()
			# request.session['first_time_algos'] = True
			# request.session['first_time_dashboard'] = True
			# request.session['first_time_create_algorithm'] = True
			# request.session['first_time_orders'] = True
			# request.session['first_time_backtest'] = True
			# request.session['first_time_orderbook'] = True
			# request.session['first_time_portfolio'] = True
			# create user profile 
			session_data['data']['email'] = session_data['data']['email'].lower()
			if 'meta' in session_data['data'].keys():
				if 'demat_consent' in session_data['data'].get('meta',{}).keys():
					request.session['demat_consent']=session_data['data']['meta']['demat_consent']

			try:
				user = models.UserProfile.objects.get(user_broker_id=user_broker_id)

				adding_broker = request.POST.get('adding_broker','')
				if (adding_broker=="true" or adding_broker==True):
					return JsonResponse({"status":"error","error_msg":"Broker account already exists, please log in directly"})
				if user.first_name!=session_data['data']['user_name']:# or user.email!=session_data['data']['email']:
					user_profile = models.UserProfile.objects(user_broker_id=user_broker_id).modify(
								user_uuid = user.user_uuid,
								first_name = session_data['data']['user_name'],
								last_name = '',
								phone_number = '',
								email = session_data['data']['email'],
								password =  '',
								status = 1
								)
				broker_session = models.BrokerSession.objects(user_broker_id=user_broker_id).modify(upsert=True,
					set__user_broker_id=user_broker_id,
					set__access_token=access_token, 
					set__public_token=public_token,
					set__user_uuid=user.user_uuid)

				# if a_results is None:
				# 	print 'not allowed user1'
				# 	request.session['blocked_login'] = True
				# 	print request.session['blocked_login']
				# 	return redirect('home')
				user_uuid = user.user_uuid	
				request.session['user_uuid'] = user.user_uuid
				request.session['user_name'] = user.first_name
				request.session['user_email'] = user.email
				request.session['terms_accepted'] = user.terms_accepted
				if (user.phone_number==''):
					request.session['show_phone_popup'] = True

				request.session['user_is_auth'] = True

				partner_ref = request.session.pop('partner_ref','')
				partner_ref_ip = request.session.pop('partner_ref_ip','')
				if(partner_ref!='' and partner_ref_ip==request.META.get('HTTP_X_FORWARDED_FOR','')):
					map_user = {
								"user_broker_id": user_broker_id,
								"new_user": False,
								"referral_code": partner_ref,
								"partner_ref_ip":partner_ref_ip
								}
					con = get_redis_connection('default')
					con.publish('partner_ref',ujson.dumps(map_user))

				# user.last_login = user.updated_at 
				user.save()
				user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
				userflow.add_session_log(request)
				userflow.update_activity(request,"login")
				if user_subscription.subscription_instance == 'dual':
					user_subscription.subscription_instance = 'dual_trial'
					user_subscription.subscription_validity= max(datetime.datetime.today() + datetime.timedelta(days=int(7)),datetime.datetime(2019, 7, 18, 23, 59, 59))
					user_subscription.subscription_type = 0
					user_subscription.subscription_product = 'free'
					user_subscription.subscription_plan = 'free'
					user_subscription.subscription_price = 0
					user_subscription.subscription_tax = 0
					user_subscription.subscription_total_price = 0
					user_subscription.save()
					request.session['first_time_login_for_plan'] = True
					request.session['first_time_login'] = True
			except:
				print(traceback.format_exc())
				# creating user profile for the first time, i.e. starting free subscription
				print(request.META.items())
				user_uuid_original = request.POST.get('user_uuid','')
				adding_broker = request.POST.get('adding_broker','')
				print("checking if the user_uuid was provided->",user_uuid,user_uuid_original,adding_broker)
				if user_uuid_original!="" and (adding_broker=="true" or adding_broker==True):
					user_uuid = user_uuid_original
					user = models.UserProfile.objects.get(user_uuid=user_uuid_original)
					user.user_broker_id = user_broker_id
					user.first_name = session_data['data']['user_name']
					user.first_broker = "zerodha"
					if user.email!=session_data['data']['email'].lower():
						user.additional_details["secondary_email"] = session_data['data']['email'].lower()
					broker_session = models.BrokerSession.objects(user_broker_id=user_broker_id).modify(upsert=True,
					set__user_broker_id=user_broker_id,
					set__access_token=access_token, 
					set__public_token=public_token,
					set__user_uuid=user_uuid)
					user.save()
					update_session_auth_hash(request,request.session.session_key)
					request.session['user_uuid'] = user_uuid
					request.session['user_name'] = session_data['data']['user_name']
					request.session['user_email'] = session_data['data']['email']
					request.session['full_broker_name'] = "zerodha"
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
					request.session['session_secret'] = generate_random_hash()
				else:
					user_uuid = str(uuid.uuid4())
					broker_session = models.BrokerSession.objects(user_broker_id=user_broker_id).modify(upsert=True,
						set__user_broker_id=user_broker_id,
						set__access_token=access_token, 
						set__public_token=public_token,
						set__user_uuid=user_uuid)
					user_profile = models.UserProfile(
									user_uuid = user_uuid,
									user_broker_id=user_broker_id,
									first_name = session_data['data']['user_name'],
									last_name = '',
									phone_number = '',
									email = session_data['data']['email'],
									password =  '',
									status = 1,
									first_broker = "zerodha"
									)
					# creating first subscription of the user, with Free trial
					subscription_uuid=str(uuid.uuid4())
					subscription_log_uuid = str(uuid.uuid4())
					user_subscription = models.UserSubscription(user_uuid=user_uuid,
						subscription_uuid=subscription_uuid,
						subscription_validity= max(datetime.datetime.today() + datetime.timedelta(days=int(7)),datetime.datetime(2020, 11, 8, 23, 59, 59)),
						latest_subscription_id = subscription_log_uuid,
						user_broker_id = user_broker_id,
						subscription_instance = 'trial'
						)

					try:
						user_profile.save()
					except NotUniqueError:
						user_profile.email = user_broker_id+"@"+"zerodha"
						user_profile.additional_details["secondary_email"] = session_data['data']['email'].lower()
						user_profile.save()

					user_subscription_log = models.UserSubscriptionLog(user_uuid=user_uuid,
						subscription_log_uuid = subscription_log_uuid,
						subscription_uuid = subscription_uuid,
						subscription_start = datetime.datetime.today(),
						subscription_stop = max(datetime.datetime.today() + datetime.timedelta(days=int(7)),datetime.datetime(2020, 11, 8, 23, 59, 59)),
						user_broker_id = user_broker_id,
						subscription_instance = 'trial'
						)

					user_subscription_log.save()
					user_subscription.save()

					# if a_results is None:
					# 	print 'not allowed user2'
					# 	request.session['blocked_login'] = True
					# 	print request.session['blocked_login']
					# 	return redirect('home')
					
					request.session['user_uuid'] = user_uuid
					request.session['user_name'] = session_data['data']['user_name']
					request.session['user_email'] = session_data['data']['email']
					# request.session['full_broker_name'] = "zerodha"
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
					request.session['session_secret'] = generate_random_hash()
					# initialize_account(user_uuid)
					send_initial_emails(user_uuid=user_uuid,email=session_data['data']['email'],name=session_data['data']['user_name'])
					partner_ref = request.session.pop('partner_ref','')
					partner_ref_ip = request.session.pop('partner_ref_ip','')
					userflow.add_session_log(request)
					userflow.update_activity(request,"login")
					if(partner_ref!='' and partner_ref_ip==request.META.get('HTTP_X_FORWARDED_FOR','')):
						map_user = {
									"user_broker_id": user_broker_id,
									"new_user": True,
									"referral_code": partner_ref,
									"partner_ref_ip":partner_ref_ip
									}
						con = get_redis_connection('default')
						con.publish('partner_ref',ujson.dumps(map_user))
		except:
			print 'error'
			print traceback.format_exc()
			# return render(request,'home_temp.html',{'status':'error'})
			return JsonResponse({"status":"error"})
		print 'tsting./..............',request.session.get('app-api','') 
		# if request.session.get('app-api','')=='true':
		# 	# print request.COOKIES
		# 	return JsonResponse({"auth_token":request.META.get("HTTP_COOKIE","")})	

		# # print dir(request.zz)
		# if request.session.pop('redirect','')=='popup':
		# 	# return render(request,'home_temp.html',{'popup':True})	
		# 	return JsonResponse({"status":"error"})

		# if request.session.get('mobile_app','')=='true':
		# 	print 'logging'
		# 	return JsonResponse({"status":"error"})
		if not request.session.session_key:
			request.session.save()
		update_usage_util(user_uuid,'',clear=False)

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
			
		print("AAAAAAAAAAAaa",{"status":"success",'csrf':csrf.get_token(request),'sessionid':request.session.session_key,"version":v_pref})
		
		return JsonResponse({"status":"success",'csrf':csrf.get_token(request),'sessionid':request.session.session_key,"version":v_pref})
		login_response = redirect('dashboard')
		if request.session.get('sample_backtest_algo_uuid','')!='':
			login_response = redirect('sample_backtest')

		salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
		session_token = hashlib.sha1(user_uuid+salt).hexdigest()
		login_response.set_cookie('session_token', session_token, max_age=3600*10,domain='.'+request.META['HTTP_HOST'])
		req_payload = {"key":session_token,"type":"add"}
		req_url = 'https://help.'+request.META['HTTP_HOST']
		print '~~~~~~~~~~~~~~~~~~~~~~~~~',req_url
		try:
			# response = requests.post(req_url+'/update_session',data=req_payload,timeout=0.090)
			# print response.text
			pass
		except:
			print '.............../////////',traceback.format_exc()
			pass
		return login_response #redirect('dashboard')
	else:
		# return render(request,'home_temp.html')
		return JsonResponse({"status":"error"})
	# return render(request,'home_temp.html',{'status':'error'})
	# return render(request,'home_temp.html',{'status':'error'})
	# return redirect('home')
	return JsonResponse({"status":"error"})

def update_to_ultimate(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth','error_msg':"Auth"})
	if request.method=="POST":
		try:
			user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
			if request.session.get('first_time_login_for_plan',False)==True:
				user_subscription.subscription_validity= datetime.datetime.today() + datetime.timedelta(days=int(3))
				user_subscription.subscription_type = 3
				user_subscription.subscription_product = 'ultimate'
				user_subscription.subscription_plan = 'ultimate'
				user_subscription.subscription_price = 0
				user_subscription.subscription_tax = 0
				user_subscription.subscription_total_price = 0
				user_subscription.save()
				request.session['first_time_login_for_plan'] = False
				return JsonResponse({"status":"success"})
		except:
			print(traceback.format_exc())

		return JsonResponse({"status":"error","error_msg":"Invalid request"})
	return JsonResponse({"status":"error","error_msg":"method"})

def update_session(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth','error_msg':"Auth"})
	if request.method=="POST":
		conn = get_redis_connection("default")
		q = conn.get('user_version_pref'+user_uuid)
		v_pref = 1
		if q is None:
			v_pref = 1
		else:
			try:
				v_pref = int(q)
			except:
				v_pref = 3
		return JsonResponse({"status":"success",'csrf':csrf.get_token(request),'sessionid':request.session.session_key,"version":v_pref})
	return JsonResponse({"status":"error"})

def user_version_pref(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth','error_msg':"Auth"})
	if request.method=="GET":
		conn = get_redis_connection("default")
		q = conn.get('user_version_pref'+user_uuid)
		v_pref = 1
		if q is None:
			v_pref = 1
		else:
			try:
				v_pref = int(q)
			except:
				print(traceback.format_exc())
				v_pref = 1

		return JsonResponse({"status":"success",'csrf':csrf.get_token(request),'sessionid':request.session.session_key,"version":v_pref})

	if request.method=="POST":
		try:
			if any(word in request.META['HTTP_USER_AGENT'] for word in ["Android","webOS","iPhone","iPad","iPod","BlackBerry","IEMobile","Opera Mini"]):
				mobile_web = True
				v_pref = 1

			if mobile_web:
				return JsonResponse({"status":"error","error_msg":"Streak 3.0 will come to mobile soon. Meanwhile open the site on a laptop or desktop"})
		except:
			pass
		conn = get_redis_connection("default")
		version = request.POST.get("version",1)
		q = conn.set('user_version_pref'+user_uuid,version)
		return JsonResponse({"status":"success","version":version})		

	return JsonResponse({"status":"error"})

def user_version_pref_switch(request):
	# user_uuid = request.session.get('user_uuid','')
	# user_is_auth = request.session.get('user_is_auth',False)
	# # if settings.DEBUG:
	# if settings.ENV == "local" or settings.ENV == 'local1':
	# 	user_uuid = '123'
	# 	user_is_auth = True
	# if not user_is_auth:
	# 	return redirect("https://www.streak.tech",code=302)
	if request.method=="GET":
		conn = get_redis_connection("default")
		version = int(request.GET.get("v",1))
		user_uuid = request.GET.get("uid",'')
		if user_uuid!='':
			q = conn.set('user_version_pref'+user_uuid,version)
			if version==1:
				return redirect("https://streak.zerodha.com",code=302)
			elif version==3:
				return redirect("https://streakv3.zerodha.com",code=302)
	return redirect("https://www.streak.tech",code=302)


def register_partner(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth','error_msg':"Auth"})
	if request.method=="POST":
		partner_ref = request.POST.get('partner_ref','')
		partner_ref_ip = request.META.get('HTTP_X_FORWARDED_FOR','')
		con = get_redis_connection("default")
		user_broker_id = request.session.get('user_broker_id',"")
		partner_obj = con.get(partner_ref+'_'+partner_ref_ip)
		if(partner_ref!='' and user_broker_id!=""):
			map_user = {
						"user_broker_id": user_broker_id,
						"new_user": request.session.get('first_time_login',False),
						"referral_code": partner_ref,
						"partner_ref_ip":partner_ref_ip
						}
			con.publish('partner_ref',ujson.dumps(map_user))
			con.delete(partner_ref+'_'+partner_ref_ip)
		return  JsonResponse({"status":"success"})
	return  JsonResponse({"status":"error"})

def reinitialize_session(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth'})

	if request.method=="POST" and user_uuid!='' and user_is_auth:
		st = time.time()
		try:
			con = get_redis_connection("screener_plan")
			plan = con.get('plan_'+user_uuid)
			ex_date = datetime.datetime.today()
			ex_date = ex_date.replace(hour=23,minute=59,second=59)
			try:
				user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
				expiration_sec = int(float(ex_date.strftime('%s'))-float(datetime.datetime.now().strftime('%s')))
				if(user_subscription.subscription_validity >= datetime.datetime.today()):
					con.set('plan_'+user_uuid,user_subscription.subscription_type)
					con.expire('plan_'+user_uuid,expiration_sec)
				else:
					# subscription_status['subscription_valid'] = False
					con.set('plan_'+user_uuid,-1)
					con.expire('plan_'+user_uuid,expiration_sec)
				print "reinitialize_session time ",time.time()-st 
				return  JsonResponse({"status":"success","plan":str(user_subscription.subscription_type)})
			except models.UserSubscription.DoesNotExist:
				con.set('plan_'+user_uuid,-1)
				con.expire('plan_'+user_uuid,expiration_sec)
				# print "reinitialize_session time ",time.time()-st 
				return  JsonResponse({"status":"success","plan":str(user_subscription.subscription_type)})
			except:
				print traceback.format_exc()
				return JsonResponse({"status":"error",'error_msg':'Unknown'})
		except:
			print ('reinitialize',traceback.format_exc())
			return JsonResponse({"status":"error",'error_msg':'Unknown'})
	return JsonResponse({"status":"error",'error_msg':'Unknown method'})

def generate_random_hash():
	hash = random.getrandbits(128)
	return "%032x" % hash

def session_handler(api_key,request_token=None,checksum=None,access_token=None):
	url = "https://api-partners.kite.trade/session/token"
	method = "POST"
	params = {}
	if request_token and checksum:
		params = {"api_key":api_key,'request_token':request_token,'checksum':checksum}
	elif access_token:
		params = {"api_key":api_key,'access_token':access_token}
		method = "DELETE"
		print "logging out"
	else:
		return None

	headers = {}
	if settings.KITE_HEADER == True:
		headers = {"X-Kite-Version":"3"}
	response = requests.request(method,url,data=params,headers=headers)
	if response.status_code != 200:
		print response.text,response.reason
		return None

	return json.loads(response.text)

def gen_csrf(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	if not user_is_auth or request.method!='GET':
		return JsonResponse({"status":"error",'error-type':'auth'})
	elif user_uuid!='' and user_is_auth:
		return JsonResponse({"status":"success",'csrf':csrf.get_token(request)})
	return JsonResponse({"status":"error"})

def get_session_status(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth'})
	elif user_uuid!='' and user_is_auth:
		try:
			user_profile = models.UserProfile.objects.get(user_uuid=user_uuid)
			user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)

			subscription_status = {}

			if(user_subscription.subscription_validity >= datetime.datetime.today()):
				subscription_status['subscription_valid'] = True
				subscription_status['current_subscription_price'] = user_subscription.subscription_price
				subscription_status['current_subscription_price'] = user_subscription.subscription_price
				subscription_status['subscription_plan'] = user_subscription.subscription_plan
				subscription_status['subscription_remaining'] = max((user_subscription.subscription_validity-datetime.datetime.today()).days,0)
			else:
				subscription_status['subscription_valid'] = False
				subscription_status['current_subscription_price'] = -1
				subscription_status['subscription_plan'] = user_subscription.subscription_plan
				subscription_status['subscription_remaining'] = -1

			if user_subscription.subscription_type!=0 and user_subscription.subscription_active:
				subscription_status['subscription_autorenew'] = True
				subscription_status['next_billing_date'] = user_subscription.subscription_validity + datetime.timedelta(days=1)
			else:
				subscription_status['subscription_autorenew'] = False
				subscription_status['next_billing_date'] = 'N/A'

			subscription_status['renew_plan'] = user_subscription.renew_plan
			subscription_status['user_broker_id'] = user_profile.user_broker_id

			usage_metric = {}
			con = get_redis_connection("default")
			#user_uuid : {'deployed':0,'backtest':0}
			usage = con.get('daily_usage:'+user_uuid)
			if usage != None:
				usage = eval(usage)
			else:
				usage = {'backtest':0,'deployed':0}

			usage['deployed'] = 0
			# deps_live = con.keys('deployed:'+user_uuid+':*')
			deps_live = models.DeployedAlgorithm._get_collection().find({"user_uuid":user_uuid,"status":0}).count()
			# if(deps_live):
			usage['deployed']=deps_live

			now_time = datetime.datetime.now()
			renewal_time = (now_time.replace(hour=23,minute=0,second=0) - now_time).seconds/3600+2

			usage_metric['backtest'] = usage.get('backtest',0)
			usage_metric['deployed'] = usage.get('deployed',0)
			con2 = get_redis_connection("screener_cache")
			scan_usage = con2.get("screener_usage_"+user_uuid)
			if scan_usage:
				try:
					usage_metric['scan_count'] = int(scan_usage)
				except:
					print(traceback.format_exc())
					usage_metric['scan_count'] = 0
			else:
				usage_metric['scan_count'] = 0
			if user_subscription.subscription_type == 0:
				# print 'yooooooooooooooooooooo',usage.get('backtest',0)
				# user_plan = con.get('user_plans:'+str(user_subscription.subscription_type))
				# if user_plan:
				# 	user_plan = eval(user_plan)
				# 	usage_metric['total_backtest'] = user_plan['daily_backtests']
				# 	usage_metric['total_deployments'] = user_plan['daily_deploys']
				# else:
				# 	usage_metric['total_backtest'] = 100
				# 	usage_metric['total_deployments'] = 5
				usage_metric['total_backtest'] = 50
				usage_metric['total_deployments'] = 5
				usage_metric['total_scan_count'] = 50
			if user_subscription.subscription_type == 1:
				# user_plan = con.get('user_plans:'+str(user_subscription.subscription_type))
				# if user_plan:
				# 	user_plan = eval(user_plan)
				# 	usage_metric['total_backtest'] = user_plan['daily_backtests']
				# 	usage_metric['total_deployments'] = user_plan['daily_deploys']
				# else:
				# 	usage_metric['total_backtest'] = 100
				# 	usage_metric['total_deployments'] = 50
				usage_metric['total_backtest'] = 200
				usage_metric['total_deployments'] = 25
				usage_metric['total_scan_count'] = 100
			if user_subscription.subscription_type == 2:
				# user_plan = con.get('user_plans:'+str(user_subscription.subscription_type))
				# if user_plan:
				# 	user_plan = eval(user_plan)
				# 	usage_metric['total_backtest'] = user_plan['daily_backtests']
				# 	usage_metric['total_deployments'] = user_plan['daily_deploys']
				# else:
				# 	usage_metric['total_backtest'] = 100
				# 	usage_metric['total_deployments'] = 50
				usage_metric['total_backtest'] = 500
				usage_metric['total_deployments'] = 50
				usage_metric['total_scan_count'] = 0
			if user_subscription.subscription_type == 3:
				# user_plan = con.get('user_plans:'+str(user_subscription.subscription_type))
				# if user_plan:
				# 	user_plan = eval(user_plan)
				# 	usage_metric['total_backtest'] = user_plan['daily_backtests']
				# 	usage_metric['total_deployments'] = user_plan['daily_deploys']
				# else:
				# 	usage_metric['total_backtest'] = 100
				# 	usage_metric['total_deployments'] = 50
				usage_metric['total_backtest'] = 1000
				usage_metric['total_deployments'] = 100
				usage_metric['total_scan_count'] = 0

			if(not subscription_status['subscription_valid']):
				usage_metric['total_backtest'] = 0
				usage_metric['total_deployments'] = 0
				usage_metric['total_scan_count'] = 0
				usage_metric['backtest'] = 0
				usage_metric['deployed'] = 0
				usage_metric['scan_count'] = 0
				
			# if user_subscription.subscription_type == 2:
			# 	user_plan = con.get('user_plans:'+str(user_subscription.subscription_type))
			# 	if user_plan:
			# 		user_plan = eval(user_plan)
			# 		usage_metric['total_backtest'] = user_plan['daily_backtests']
			# 		usage_metric['total_deployments'] = user_plan['daily_deploys']
			# 	else:
			# 		usage_metric['total_backtest'] = 500
			# 		usage_metric['total_deployments'] = 100
			default_accounts = con.get('default_trading_accounts'+user_uuid)
			if default_accounts:
				default_accounts = ujson.loads(default_accounts)
			else:
				default_accounts={}
			first_time_login = request.session.pop('first_time_login',False)

			demat_consent = request.session.get('demat_consent','')

			broker = request.session.get("full_broker_name",'')
			if broker == "":
				broker = "zerodha"
				if user_profile.first_broker=="-":
					broker = "-"
			elif broker.lower() == "angel broking":
				broker = "Angel broking"
			return JsonResponse({"status":"success","first_time_login":first_time_login,"user_subscription":{"user_uuid":user_subscription.user_uuid,"user_broker_id":user_profile.user_broker_id,"subscription_uuid":user_subscription.subscription_uuid,"subscription_type":user_subscription.subscription_type,"subscription_product":user_subscription.subscription_product,"subscription_price":user_subscription.subscription_price,"subscription_validity":user_subscription.subscription_validity,"subscription_instance":user_subscription.subscription_instance,"subscription_active":user_subscription.subscription_active,"created_at":user_subscription.created_at,"updated_at":user_subscription.updated_at},'subscription_status':subscription_status,"usage_metric":usage_metric,"user_name":user_profile.first_name,'user_profile':{
				'user_name':user_profile.first_name,'phone_number':user_profile.phone_number,'email':user_profile.email,'broker':broker,"user_uuid":user_subscription.user_uuid,"user_broker_id":user_profile.user_broker_id,"terms_accepted":user_profile.terms_accepted,"additional_details":user_profile.additional_details,"publisher":user_profile.publisher,'demat_consent':demat_consent
				}})
		except:
			print traceback.format_exc()
			pass
			return JsonResponse({"status":"success"})
	return JsonResponse({"status":"error",'error-type':'auth'})

def broker_login_url(request):
	# if request.method=='POST':
	# 	return jsonify({})
	redirect_to = request.GET.get('redirect_to','/')
	x = request.GET.get('kite3','')
	m_true = request.GET.get('m','')
	if x=='true':
		x = '&v=3'
		request.session['kite3'] = 'true'
	else:
		request.session.pop('kite3','')

	if m_true=='true':
		request.session['mobile_app'] = 'true'
	else:
		request.session.pop('mobile_app','')

	broker_api_version = ''
	if settings.KITE_HEADER == True:
		broker_api_version = '&v=3'
	r_url = "https://kite.zerodha.com/connect/login?api_key="+settings.KITE_API_KEY+broker_api_version+x
	# r_url = "https://streak.zerodha.com"
	# partner_ref = request.GET.get('utm_source',None)
	
	# if partner_ref:
	# 	try:
	# 		con = get_redis_connection("default")
	# 		partner_ref_ip=request.META.get('HTTP_X_FORWARDED_FOR','')
	# 		con.set(partner_ref+'_'+partner_ref_ip,'True')
	# 		con.expire(partner_ref+'_'+partner_ref_ip,600)
	# 		r_url = 'https://streak.zerodha.com/?utm_source='+partner_ref+'&utm_medium=internal-partner-link&utm_campaign=subscribe'
	# 	except:
	# 		print('partner_ref:',traceback.format_exc())

	if request.GET.get('redirect','')!='':
		request.session['redirect']=request.GET.get('redirect','')
	return redirect(r_url,code=302)

def broker_login(request):
	# if request.method=='POST':
	# 	return jsonify({})
	redirect_to = request.GET.get('redirect_to','/')
	x = request.GET.get('kite3','')
	m_true = request.GET.get('m','')
	if x=='true':
		x = '&v=3'
		request.session['kite3'] = 'true'
	else:
		request.session.pop('kite3','')

	if m_true=='true':
		request.session['mobile_app'] = 'true'
	else:
		request.session.pop('mobile_app','')

	broker_api_version = ''
	if settings.KITE_HEADER == True:
		broker_api_version = '&v=3'
	# r_url = "https://kite.zerodha.com/connect/login?api_key="+settings.KITE_API_KEY+broker_api_version+x
	r_url = "https://streak.zerodha.com"
	partner_ref = request.GET.get('utm_source',None)
	
	if partner_ref:
		try:
			con = get_redis_connection("default")
			partner_ref_ip=request.META.get('HTTP_X_FORWARDED_FOR','')
			con.set(partner_ref+'_'+partner_ref_ip,'True')
			con.expire(partner_ref+'_'+partner_ref_ip,600)
			r_url = 'https://streak.zerodha.com/?utm_source='+partner_ref+'&utm_medium=internal-partner-link&utm_campaign=subscribe'
		except:
			print('partner_ref:',traceback.format_exc())

	if request.GET.get('redirect','')!='':
		request.session['redirect']=request.GET.get('redirect','')
	return redirect(r_url,code=302)

def logout(request):
	headers = {}
	if settings.KITE_HEADER == True:
		headers = {"X-Kite-Version":"3"}
	response = requests.delete("https://api-partners.kite.trade/session/token?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token','')),headers=headers)
	response = requests.request("DELETE","https://api-partners.kite.trade/session/token?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token','')),headers=headers)
	# if response.status_code == 200:
	for key in request.session.keys():
		del request.session[key]
	return redirect('home')

def subscription_status():
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth'})
	if request.method!='GET':
		return JsonResponse({"status":"error",'error-type':'method'})
	try:
		user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)

		subscription_status = {}

		if(user_subscription.subscription_validity >= datetime.datetime.today()):
			subscription_status['subscription_valid'] = True
			subscription_status['current_subscription_price'] = user_subscription.subscription_price
			subscription_status['current_subscription_price'] = user_subscription.subscription_price
			subscription_status['subscription_plan'] = user_subscription.subscription_plan
			subscription_status['subscription_remaining'] = max((user_subscription.subscription_validity-datetime.datetime.today()).days,0)
		else:
			subscription_status['subscription_valid'] = False
			subscription_status['current_subscription_price'] = -1
			subscription_status['subscription_plan'] = 'N/A'
			subscription_status['subscription_remaining'] = -1

		if user_subscription.subscription_type!=0 and user_subscription.subscription_active:
			subscription_status['subscription_autorenew'] = True
			subscription_status['next_billing_date'] = user_subscription.subscription_validity + datetime.timedelta(days=1)
		else:
			subscription_status['subscription_autorenew'] = False
			subscription_status['next_billing_date'] = 'N/A'

		subscription_status['user_broker_id'] = user_subscription.user_broker_id


		return JsonResponse({"status":"success","user_subscription":user_subscription.to_json(),'subscription_status':subscription_status})
	except:
		print traceback.format_exc()
		pass
	return JsonResponse({"status":"error"})

def fetch_billing_status(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth'})
	if request.method!='GET':
		return JsonResponse({"status":"error",'error-type':'method'})
	try:
		user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)

		subscription_status = {}

		if(user_subscription.subscription_validity >= datetime.datetime.today()):
			subscription_status['subscription_valid'] = True
			subscription_status['current_subscription_price'] = user_subscription.subscription_price
			subscription_status['current_subscription_price'] = user_subscription.subscription_price
			subscription_status['subscription_plan'] = user_subscription.subscription_plan
			subscription_status['subscription_remaining'] = max((user_subscription.subscription_validity-datetime.datetime.today()).days,0)
		else:
			subscription_status['subscription_valid'] = False
			subscription_status['current_subscription_price'] = -1
			subscription_status['subscription_plan'] = user_subscription.subscription_plan
			subscription_status['subscription_remaining'] = -1

		if user_subscription.subscription_type!=0 and user_subscription.subscription_active:
			subscription_status['subscription_autorenew'] = True
			subscription_status['next_billing_date'] = user_subscription.subscription_validity + datetime.timedelta(days=1)
		else:
			subscription_status['subscription_autorenew'] = False
			subscription_status['next_billing_date'] = 'N/A'

		subscription_status['user_broker_id'] = user_subscription.user_broker_id


		return JsonResponse({"status":"success","user_subscription":user_subscription.to_json(),'subscription_status':subscription_status})
	except:
		print traceback.format_exc()
		pass
	return JsonResponse({"status":"error"})

def fetch_billing(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth'})
	if request.method!='GET':
		return JsonResponse({"status":"error",'error-type':'method'})
	try:
		user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
		user_subscription_log = models.UserSubscriptionLog.objects(user_uuid=user_uuid).order_by('-created_at')
		us_log = []
		for sl in user_subscription_log:
			us_log.append(sl.to_json())

		subscription_status = {}
		subscription_status['subscription_type'] = user_subscription.subscription_type
		if(user_subscription.subscription_validity >= datetime.datetime.today()):
			subscription_status['subscription_valid'] = True
			subscription_status['current_subscription_price'] = user_subscription.subscription_price
			subscription_status['current_subscription_total_price'] = user_subscription.subscription_total_price
			subscription_status['subscription_plan'] = user_subscription.subscription_plan
			subscription_status['subscription_remaining'] = max((user_subscription.subscription_validity-datetime.datetime.today()).days,0)
		else:
			subscription_status['subscription_valid'] = False
			subscription_status['current_subscription_price'] = -1
			subscription_status['subscription_plan'] = 'N/A'
			subscription_status['subscription_remaining'] = -1

		if user_subscription.subscription_type!=0 and user_subscription.subscription_active:
			subscription_status['subscription_autorenew'] = True
			subscription_status['next_billing_date'] = user_subscription.subscription_validity + datetime.timedelta(days=1)
		else:
			subscription_status['subscription_autorenew'] = False
			subscription_status['next_billing_date'] = 'N/A'

		subscription_status['user_broker_id'] = user_subscription.user_broker_id

		if user_subscription.subscription_type == 0:
				subscription_status['total_backtest'] = 50
				subscription_status['total_deployments'] = 5
		elif user_subscription.subscription_type == 1:
				subscription_status['total_backtest'] = 200
				subscription_status['total_deployments'] = 25
		elif user_subscription.subscription_type == 2:
				subscription_status['total_backtest'] = 500
				subscription_status['total_deployments'] = 50
		elif user_subscription.subscription_type == 3:
				subscription_status['total_backtest'] = 1000
				subscription_status['total_deployments'] = 100
		else:
			subscription_status['total_backtest'] = 50
			subscription_status['total_deployments'] = 5

		subscription_status['renew_plan'] = user_subscription.renew_plan
		return JsonResponse({"status":"success","user_subscription":user_subscription.to_json(),"user_subscription_log":us_log,'subscription_status':subscription_status})
	except:
		print traceback.format_exc()
		# TODO to be delete in production
		subscription_status = {}
		subscription_status['subscription_valid'] = False
		subscription_status['current_subscription_price'] = -1
		subscription_status['subscription_plan'] = 'N/A'
		subscription_status['subscription_remaining'] = -1
		subscription_status['subscription_autorenew'] = False
		subscription_status['next_billing_date'] = 'N/A'
		return JsonResponse({"status":"success","user_subscription":'{}',"user_subscription_log":[],'subscription_status':subscription_status})
	return JsonResponse({"status":"error"})

@override_with_ams
def place_order_discipline(request):
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

		access_token = request.session.get('access_token','')
		public_token = request.session.get('public_token','')
		user_broker_id = request.session.get('user_broker_id','')
		broker = 'zerodha'

		if access_token=='' or public_token=='' or user_broker_id=='':
			print 'probably kite login popup'
			return JsonResponse({"status":"error",'error-type':'noauth'})

		con = get_redis_connection('default')
		key_prefix = ':'.join(['deployed',user_uuid,'*',deployment_uuid])
		deployed_keys = get_deployment_keys({"user_uuid":user_uuid,"deployment_uuid":deployment_uuid,"status":0}) #con.keys(key_prefix)
		# print 'zzzzzzzzzzzzzzzzzzzzzz11111111111',key_prefix
		if(len(deployed_keys)==0):
			print 'deployment_uuid not present'
			return JsonResponse({"status":"error",'error-type':'Strategy not live','error_msg':'Strategy not live'})


		if segment=='' and exchange=='CDS':
			segment = 'CDS-FUT'
		elif segment=='' and exchange=='MCX':
			segment = 'MCX'
		elif segment=='' and exchange=='NFO':
			if str(symbol).endswith("CE") or str(symbol).endswith("PE"):
				segment = 'NFO-OPT'
			else:
				segment = 'NFO-FUT'
		elif exchange=='NFO-FUT':
			segment = 'NFO-FUT'
			exchange = 'NFO'
		elif exchange=='NFO-OPT':
			segment = 'NFO-OPT'
			exchange = 'NFO'
		elif segment == '':
			segment = 'NSE'
			
		payload = {
		  "api_key":settings.KITE_API_KEY,
		  "access_token":access_token,
		  "tradingsymbol":symbol,
		  "exchange":exchange,
		  "transaction_type":transaction_type,
		  "order_type":order_type,
		  "quantity":quantity,
		  "product":product,
		  "validity":validity,
		  "trigger_price":trigger_price
		}

		# print payload
		headers = {}
		if settings.KITE_HEADER == True:
			headers = {"X-Kite-Version":"3"}
			auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
			headers["Authorization"] = "token {}".format(auth_header)
		response = requests.request("POST","https://api-partners.kite.trade/orders/regular", data=payload,headers=headers)
		if response.status_code == 200:
			response_json = json.loads(response.text)
			if response_json['status']=="success":
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
							"api_key":settings.KITE_API_KEY,
							"access_token":access_token,
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

					keys = deployed_keys #get_deployment_keys({"user_uuid":user_uuid,"deployment_uuid":deployment_uuid}) # con.keys('deployed:'+user_uuid+':*:'+deployment_uuid)
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
							r['SL_order_api_key']=settings.KITE_API_KEY
							r['SL_order_access_token']=access_token
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
				return JsonResponse({'status':'error','order_response':response_json,'response_code':response.status_code})
		else:
			return JsonResponse({'status':'error','response_code':response.status_code,'error-type':'Session expired, re-login required','error_msg':'Session expired, re-login required'})
		return JsonResponse({'status':'error'})
	return JsonResponse({'status':'error'})

def mark_notification_used(request):
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
		con = get_redis_connection("default")
		notifs = con.get('today_notification:'+user_uuid)
		# notifs = ujson.loads(notifs)
		notifs = eval(notifs)
		notif_used = notifs['used'].get(notification_uuid,0)
		if notif_used:
			return JsonResponse({"status":"used"})
		notifs['used'][notification_uuid]=1 # mark notitification as used(actioned upon)
		con.set('today_notification:'+user_uuid,ujson.dumps(notifs))
		ex_time = int((datetime.datetime.now().replace(hour=3,minute=0,second=0)+datetime.timedelta(days=1)).strftime('%s')) - int(datetime.datetime.now().strftime('%s'))
		con.expire('today_notification:'+user_uuid,ex_time)
	return JsonResponse({"status":"success"})

def place_order(request):
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
			notification_uuid = request.POST.get('notification_uuid','')
			if notification_uuid == '':
				return JsonResponse({"status":"error",'error-type':'notifid'})
			try:
				con = get_redis_connection("default")
				notifs = con.get('today_notification:'+user_uuid)
				notifs = ujson.loads(notifs)
				notif_used = notifs['used'].get(notification_uuid,0)
				if notif_used:
					return JsonResponse({"status":"used"})
			except:
				print traceback.format_exc()

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
				return JsonResponse({"status":"error",'error-type':'depid'})

			con = get_redis_connection('default')
			key_prefix = ':'.join(['deployed',user_uuid,'*',deployment_uuid])
			deployed_keys = con.keys(key_prefix)
			# print 'zzzzzzzzzzzzzzzzzzzzzz11111111111',key_prefix
			if(len(deployed_keys)==0):
				print 'deployment_uuid not present'
				return JsonResponse({"status":"error",'error-type':'Strategy not live','error_msg':'Strategy not live'})

			access_token = request.session.get('access_token','')
			public_token = request.session.get('public_token','')
			user_broker_id = request.session.get('user_broker_id','')
			broker = 'zerodha'

			if access_token=='' or public_token=='' or user_broker_id=='':
				print 'probably kite login popup'
				return JsonResponse({"status":"error",'error-type':'noauth'})

			payload = {
			  "api_key":settings.KITE_API_KEY,
			  "access_token":access_token,
			  "tradingsymbol":symbol,
			  "exchange":exchange,
			  "transaction_type":transaction_type,
			  "order_type":order_type,
			  "quantity":quantity,
			  "product":product,
			  "validity":validity
			}

			# print payload
			headers = {}
			if settings.KITE_HEADER == True:
				headers = {"X-Kite-Version":"3"}
				auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
				headers["Authorization"] = "token {}".format(auth_header)
			response = requests.request("POST","https://api-partners.kite.trade/orders/regular", data=payload,headers=headers)
			if response.status_code == 200:
				response_json = json.loads(response.text)
				if response_json['status']=="success":
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
								"api_key":settings.KITE_API_KEY,
								"access_token":access_token,
								"tradingsymbol":symbol,
								"segment":segment,
								"exchange":exchange,
								"transaction_type":transaction_type,
								"order_type":order_type,
								"quantity":quantity,
								"product":product,
								"validity":validity,
								"order_placement":"manual"
							}
						)
						broker_order.save()

						pipeline = con.pipeline()

						# keys = con.keys('deployed:'+user_uuid+':*:'+deployment_uuid)
						# if len(keys)>0:
						# 	redis_key = keys[0]
						# else:
						# 	redis_key = None

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
							'open_notif':False
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
					return JsonResponse({'status':'error','order_response':response_json,'response_code':response.status_code})
			else:
				return JsonResponse({'status':'error','response_code':response.status_code,'error-type':'Session expired, re-login required','error_msg':'Session expired, re-login required'})
			return JsonResponse({'status':'error'})
		except:
			print traceback.format_exc()

	return JsonResponse({'status':'error'})

@override_with_ams
def place_order_new(request):
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
			deployed_keys = get_deployment_keys({"user_uuid":user_uuid,"deployment_uuid":deployment_uuid,"status":0}) # con.keys(key_prefix)
			# print 'zzzzzzzzzzzzzzzzzzzzzz11111111111',key_prefix
			if(len(deployed_keys)==0):
				print 'deployment_uuid not present'
				return JsonResponse({"status":"error",'error-type':'Strategy not live','error_msg':'Strategy not live'})

			access_token = request.session.get('access_token','')
			public_token = request.session.get('public_token','')
			user_broker_id = request.session.get('user_broker_id','')
			broker = 'zerodha'

			if access_token=='' or public_token=='' or user_broker_id=='':
				print 'probably kite login popup'
				return JsonResponse({"status":"error",'error-type':'noauth'})

			if exchange=='CDS-FUT':
				exchange="CDS"
			elif exchange=='NFO-FUT':
				exchange="NFO"
			elif exchange=='NFO-OPT':
				exchange="NFO"
			elif exchange=="NFO":
				if str(symbol).endswith("CE") or str(symbol).endswith("PE"):
					segment = 'NFO-OPT'
				else:
					segment = 'NFO-FUT'
				
			payload = {
			  "api_key":settings.KITE_API_KEY,
			  "access_token":access_token,
			  "tradingsymbol":symbol,
			  "exchange":exchange,
			  "transaction_type":transaction_type,
			  "order_type":order_type,
			  "quantity":quantity,
			  "product":product,
			  "validity":validity
			}
			if order_type=='LIMIT':
				payload['price']=price

			if variety.lower()=='bo':
				payload['variety']=variety.lower()
				payload['squareoff']=squareoff
				payload['stoploss']=stoploss
				if trailing_stoploss!=0:
					payload['trailing_stoploss']=trailing_stoploss

			try:
				notifs['used'][notification_uuid]=1 # mark notitification as used(actioned upon)
				con.set('today_notification:'+user_uuid,ujson.dumps(notifs))
				ex_time = int((datetime.datetime.now().replace(hour=3,minute=0,second=0)+datetime.timedelta(days=1)).strftime('%s')) - int(datetime.datetime.now().strftime('%s'))
				con.expire('today_notification:'+user_uuid,ex_time)
			except:
				pass
			# print payload
			headers = {}
			if settings.KITE_HEADER == True:
				headers = {"X-Kite-Version":"3"}
				auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
				headers["Authorization"] = "token {}".format(auth_header)
			response = requests.request("POST","https://api-partners.kite.trade/orders/"+variety.lower(), data=payload,headers=headers)
			try:
				response_json = json.loads(response.text)
			except:
				return JsonResponse({'status':'error','error':'none','error_msg':'Kite response error'})
			if response.status_code == 200:
				if response_json['status']=="success":
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
					notifs['used'][notification_uuid]=0 # mark notitification as used(actioned upon)
					con.set('today_notification:'+user_uuid,ujson.dumps(notifs))
					ex_time = int((datetime.datetime.now().replace(hour=3,minute=0,second=0)+datetime.timedelta(days=1)).strftime('%s')) - int(datetime.datetime.now().strftime('%s'))
					con.expire('today_notification:'+user_uuid,ex_time)
					return JsonResponse({'status':'error','order_response':response_json,'response_code':response.status_code})
			elif response.status_code==403:
				notifs['used'][notification_uuid]=0 # mark notitification as used(actioned upon)
				con.set('today_notification:'+user_uuid,ujson.dumps(notifs))
				ex_time = int((datetime.datetime.now().replace(hour=3,minute=0,second=0)+datetime.timedelta(days=1)).strftime('%s')) - int(datetime.datetime.now().strftime('%s'))
				con.expire('today_notification:'+user_uuid,ex_time)
				return JsonResponse({'status':'error','response_code':response.status_code,'error-type':'Session expired, re-login required','error_msg':'Session expired, re-login required'})
			elif response.status_code==428:
				notifs['used'][notification_uuid]=0 # mark notitification as used(actioned upon)
				con.set('today_notification:'+user_uuid,ujson.dumps(notifs))
				ex_time = int((datetime.datetime.now().replace(hour=3,minute=0,second=0)+datetime.timedelta(days=1)).strftime('%s')) - int(datetime.datetime.now().strftime('%s'))
				con.expire('today_notification:'+user_uuid,ex_time)
				return JsonResponse({'status':'error','response_code':response.status_code,'error_msg':'Order needs authorisation at depository, please visit kite.zerodha.com to place the order','error-type':'Order needs authorisation at depository, please visit kite.zerodha.com to place the order','error_url':"https://kite.zerodha.com"})
			else:
				notifs['used'][notification_uuid]=0 # mark notitification as used(actioned upon)
				con.set('today_notification:'+user_uuid,ujson.dumps(notifs))
				ex_time = int((datetime.datetime.now().replace(hour=3,minute=0,second=0)+datetime.timedelta(days=1)).strftime('%s')) - int(datetime.datetime.now().strftime('%s'))
				con.expire('today_notification:'+user_uuid,ex_time)
				return JsonResponse({'status':'error','response_code':response.status_code,'error-type':'Session expired, re-login required','error_msg':response_json.get('message',"Unknown error")})
			return JsonResponse({'status':'error'})
		except:
			print traceback.format_exc()

	return JsonResponse({'status':'error'})

def notifications_handler(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error"})

	if request.method == "GET":
		results = {}
		con = get_redis_connection("default")
		results = con.get('today_notification:'+user_uuid)
		if results == None:
			return JsonResponse({'status':'success','results':{'notifications':[],'unread_count':0,'used':{},'read':{}}})
		else:
			return JsonResponse({'status':'success','results':ujson.loads(results)})

	if request.method == 'POST':
		results = {}
		# notification_dict = request.POST.get('notification_dict','{}')
		unread_count = request.POST.get('unread',0)
		con = get_redis_connection("default")
		results = con.get('today_notification:'+user_uuid)
		ex_time = int((datetime.datetime.now().replace(hour=3,minute=0,second=0)+datetime.timedelta(days=1)).strftime('%s')) - int(datetime.datetime.now().strftime('%s'))
		if results == None:
			results = {'notifications':[],'unread_count':unread_count,'used':{},'read':{}}
			con.set('today_notification:'+user_uuid,ujson.dumps(results))
			con.expire('today_notification:'+user_uuid,ex_time)
			return JsonResponse({'status':'success'})
		else:
			results = ujson.loads(results)
			results['unread_count']=unread_count
			con.set('today_notification:'+user_uuid,ujson.dumps(results))
			con.expire('today_notification:'+user_uuid,ex_time)
			return JsonResponse({'status':'success'})
	return JsonResponse({'status':'error'})

def notifications_handler2_(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error"})

	if request.method == "GET":
		results = {}
		con = get_redis_connection("default")
		results = con.get('today_notification:'+user_uuid)
		if results == None:
			return JsonResponse({'status':'success','results':{'notification_dict':{},'unread_count':0,'used':{},'notif_dep_list':[]}})
		else:
			all_notifications = ujson.loads(results)
			notifications = all_notifications['notifications']
			notification_dict = {}
			notification_list_dict = {}
			for n in notifications:
				if n.get('deployment_uuid','') != '' and n.get('deployment_uuid','') not in notification_dict.keys():
					try:
						notification_dict[n.get('deployment_uuid','')]={
							'notifications':[n],
							'algo_name':n.get('algo_name',''),
							'algo_uuid':n.get('algo_uuid',''),
							'deployment_uuid':n.get('deployment_uuid','')
						}
						notification_time = datetime.datetime.strptime(n.get('notification_time',''),'%Y-%m-%dT%H:%M:%S.%f').strftime('%s')
						notification_list_dict[n.get('deployment_uuid','')]=notification_time
					except:
						pass
				elif n.get('alert_uuid')!='':
					try:
						notification_dict[n.get('alert_uuid','')]={
							'notifications':[n],
							'screener_name':n.get('screener_name',''),
							'alert_uuid':n.get('alert_uuid',''),
							'deployment_type':n.get('type',''),	
						}
						notification_time = datetime.datetime.strptime(n.get('notification_time',''),'%Y-%m-%dT%H:%M:%S.%f').strftime('%s')
						notification_list_dict[n.get('alert_uuid','')]=notification_time
					except:
						pass
				else:
					try:
						if n.get('deployment_uuid','') != '':
							notification_dict[n.get('deployment_uuid','')]['notifications'].insert(0,n)
							notification_time = datetime.datetime.strptime(n.get('notification_time',''),'%Y-%m-%dT%H:%M:%S.%f').strftime('%s')
							notification_list_dict[n.get('deployment_uuid','')]=notification_time
					except:
						pass
			notif_dep_list = sorted(notification_list_dict.iteritems(), key=lambda (k,v): (v,k))
			results = {'notification_dict':notification_dict,'used':all_notifications['used'],'unread_count':all_notifications['unread_count'],'notif_dep_list':notif_dep_list}
			return JsonResponse({'status':'success','results':results})

	if request.method == 'POST':
		results = {}
		# notification_dict = request.POST.get('notification_dict','{}')
		unread_count = request.POST.get('unread',0)
		con = get_redis_connection("default")
		results = con.get('today_notification:'+user_uuid)
		ex_time = int((datetime.datetime.now().replace(hour=3,minute=0,second=0)+datetime.timedelta(days=1)).strftime('%s')) - int(datetime.datetime.now().strftime('%s'))
		if results == None:
			results = {'notifications':[],'unread_count':unread_count,'used':{},'read':{}}
			con.set('today_notification:'+user_uuid,ujson.dumps(results))
			con.expire('today_notification:'+user_uuid,ex_time)
			return JsonResponse({'status':'success'})
		else:
			results = ujson.loads(results)
			results['unread_count']=unread_count
			con.set('today_notification:'+user_uuid,ujson.dumps(results))
			con.expire('today_notification:'+user_uuid,ex_time)
			return JsonResponse({'status':'success'})
	return JsonResponse({'status':'error'})		

def notifications_handler2(request): 
	user_uuid = request.session.get('user_uuid','') 
	user_is_auth = request.session.get('user_is_auth',False) 
	if settings.ENV == "local" or settings.ENV == 'local1': 
		user_uuid = '123' 
		user_is_auth = True 
	if not user_is_auth: 
		return JsonResponse({"status":"error"}) 

	if request.method == "GET": 
		results = {} 
		con = get_redis_connection("default") 
		results = con.get('today_notification:'+user_uuid) 
		if results == None: 
			return JsonResponse({'status':'success','results':{'notification_dict':{},'unread_count':0,'used':{},'read':{},'notif_dep_list':[]}}) 
		else: 
			all_notifications = eval(results) 
			notifications = all_notifications['notifications'] 
			notification_dict = {} 
			notification_list_dict = {} 
			for n in notifications:
				# {'notification_uuid': 'be2669b3-4ea2-4693-af30-68289fe7c612', 'trigger_price': '10', 'user_uuid': 'eff87bd6-bbec-4db5-809c-740b0a828253', 'trigger_time': '1526817021', 'price_trigger-notification': 'eff87bd6-bbec-4db5-809c-740b0a828253:8c25f9d8-3fbb-4423-ae45-07d47d2f973d:PRICETRIGGER:7795211:IR1:10:0.5:0.0:Test 301:BUY:1:b7ad0ea7-6c73-477e-9f28-b0cbb48f9b18:MIS:SBIN:NSE', 'type': 'inrange'}
				if n.get('price_trigger-notification','')!='':
					trigger_key = n.get('price_trigger-notification')
					tpsl_array = trigger_key.split(':');
					n_user_uuid = tpsl_array[0];
					n_deployment_uuid = tpsl_array[1];
					n_token = tpsl_array[3];
					n_algo_name = tpsl_array[8];
					n_action_type = tpsl_array[9];
					n_quantity = tpsl_array[10];
					n_algo_uuid = tpsl_array[11];
					n_product = tpsl_array[12];
					n_symbol = tpsl_array[13];
					n_segment = tpsl_array[14];
					try:
						n_variety = tpsl_array[15]
						n_tp = tpsl_array[16]
						n_sl = tpsl_array[17]
						n_tpsl_type = tpsl_array[18]
						n_deployment_type = tpsl_array[19]
					except:
						n_variety = 'REGULAR'
						n_tp = ''
						n_sl = ''
						n_tpsl_type = 'pct'
						n_deployment_type = 'Notifications'

					n['deployment_uuid'] = n_deployment_uuid
					n['user_uuid'] = n_user_uuid
					n['token'] = n_token
					n['algo_name'] = n_algo_name
					n['action_type'] = n_action_type
					n['quantity'] = n_quantity
					n['algo_uuid'] = n_algo_uuid
					n['product'] = n_product
					n['symbol'] = n_symbol
					n['segment'] = n_segment
					n['variety'] = n_variety
					n['target_profit'] = n_tp
					n['stop_loss'] = n_sl
					n['tpsl_type'] = n_tpsl_type
					n['deployment_type'] = n_deployment_type

					n['notification_time'] =  datetime.datetime.fromtimestamp(float(n.get('trigger_time','0'))).strftime('%Y-%m-%dT%H:%M:%S.%f')
				try:
					if n.get('alert_uuid','')=='':
						n['trigger_price'] = float(n['trigger_price'])
				except:
					pass

				if n.get('notification_uuid','') == '':
					n['notification_uuid'] = n.get('deployment_uuid','')+n.get('notification_time','')+str(n.get('trigger_time',''))
				if n.get("order_type","")=="":
					n["order_type"] = "MARKET"
				if n.get('deployment_uuid','') != '' and n.get('deployment_uuid','') not in notification_dict.keys(): 
					try:
						if n.get('notification_uuid','') == '':
							n['notification_uuid'] = n.get('deployment_uuid','')+n.get('notification_time','')
						
						notification_dict[n.get('deployment_uuid','')]={ 
						  'notifications':[n], 
						  'algo_name':n.get('algo_name',''), 
						  'algo_uuid':n.get('algo_uuid',''), 
						  'deployment_uuid':n.get('deployment_uuid',''), 
						  'deployment_type':n.get('deployment_type',''), 
						} 
						notification_time = datetime.datetime.strptime(n.get('notification_time',''),'%Y-%m-%dT%H:%M:%S.%f').strftime('%s')
						notification_list_dict[n.get('deployment_uuid','')]=notification_time 
					except:
						# print traceback.format_exc()
						pass 
				elif n.get('alert_uuid','')!='':
					try:
						notification_dict[n.get('alert_uuid','')]={
							'notifications':[n],
							'screener_name':n.get('screener_name',''),
							'screener_uuid':n.get('screener_uuid',''),
							'alert_uuid':n.get('alert_uuid',''),
							'deployment_type':n.get('type',''),	
						}
						notification_time = datetime.datetime.strptime(n.get('notification_time',''),'%Y-%m-%dT%H:%M:%S.%f').strftime('%s')
						notification_list_dict[n.get('alert_uuid','')]=notification_time
					except:
						pass
				else:
					# print notifications
					try:
						if n.get('deployment_uuid','') != '':
							notification_dict[n.get('deployment_uuid','')]['notifications'].insert(0,n) 
							notification_time = datetime.datetime.strptime(n.get('notification_time',''),'%Y-%m-%dT%H:%M:%S.%f').strftime('%s')
							notification_list_dict[n.get('deployment_uuid','')]=notification_time
					except:
						print traceback.format_exc()
						print n
						pass 
			notif_dep_list = sorted(notification_list_dict.iteritems(), key=lambda (k,v): (v,k),reverse=True) 
			results = {'notification_dict':notification_dict,'used':all_notifications['used'],'read':all_notifications.get('read',{}),'unread_count':all_notifications['unread_count'],'unread_split_count':all_notifications.get('unread_split_count',{"notifications": 0, "paper": 0, "direct": 0,"screener":0}),'notif_dep_list':notif_dep_list} 
			return JsonResponse({'status':'success','results':results}) 
 
	if request.method == 'POST': 
		results = {} 
	# notification_dict = request.POST.get('notification_dict','{}') 
		unread_count = request.POST.get('unread',0) 
		notif_type = request.POST.get('notif_type','notification') 
		con = get_redis_connection("default") 
		results = con.get('today_notification:'+user_uuid) 
		ex_time = int((datetime.datetime.now().replace(hour=3,minute=0,second=0)+datetime.timedelta(days=1)).strftime('%s')) - int(datetime.datetime.now().strftime('%s')) 
		if results == None: 
			results = {'notifications':[],'unread_count':unread_count,'used':{},'read':{},'unread_split_count':{"notifications": 0, "paper": 0, "screener": 0,"direct": 0}} 
			con.set('today_notification:'+user_uuid,ujson.dumps(results)) 
			con.expire('today,_notification:'+user_uuid,ex_time) 
			return JsonResponse({'status':'success'}) 
		else: 
			results = ujson.loads(results) 
			results['unread_count']=unread_count
			if 'unread_split_count' in results.keys():
				if notif_type.lower()=='all':
					results['unread_split_count']= {"notifications":0,"paper":0,"screener":0,"direct": 0}
				results['unread_split_count'][notif_type]=unread_count 
				
			con.set('today_notification:'+user_uuid,ujson.dumps(results)) 
			con.expire('today_notification:'+user_uuid,ex_time) 
			return JsonResponse({'status':'success'}) 
	return JsonResponse({'status':'error'})

def mark_notification_used2(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth'})
	if request.method == "POST":
		results = {} 
	# notification_dict = request.POST.get('notification_dict','{}') 
		unread_count = request.POST.get('unread',0) 
		notif_type = request.POST.get('notif_type','notification') 
		notification_uuids = request.POST.get('notification_uuids',"[]") 
		con = get_redis_connection("default") 
		results = con.get('today_notification:'+user_uuid) 
		ex_time = int((datetime.datetime.now().replace(hour=3,minute=0,second=0)+datetime.timedelta(days=1)).strftime('%s')) - int(datetime.datetime.now().strftime('%s')) 
		if results == None: 
			results = {'notifications':[],'unread_count':unread_count,'used':{},'read':{},'unread_split_count':{"notifications": 0, "paper": 0, "screener": 0,"direct": 0}} 
			con.set('today_notification:'+user_uuid,ujson.dumps(results)) 
			con.expire('today,_notification:'+user_uuid,ex_time) 
			return JsonResponse({'status':'success'}) 
		else: 
			results = ujson.loads(results) 
			results['unread_count']=unread_count
			if 'unread_split_count' in results.keys():
				if notif_type.lower()=='all':
					results['unread_split_count']= {"notifications":0,"paper":0,"screener":0,"direct": 0}
				results['unread_split_count'][notif_type]=unread_count 
			try:
				notification_uuids = ujson.loads(notification_uuids)
				if len(notification_uuids)>0:
					for n in notification_uuids:
						if results.get("read",None) is None:
							results["read"]={n:1}
						else:
							results["read"][n]=1
			except:
				print(traceback.format_exc())
				pass
			# print("results",results["read"])
			con.set('today_notification:'+user_uuid,ujson.dumps(results)) 
			con.expire('today_notification:'+user_uuid,ex_time) 
			return JsonResponse({'status':'success'}) 
	return JsonResponse({"status":"success"})

def fetch_with_token(token):
	if token ==None:
		return None
	results = []
	con = get_redis_connection("default")
	keys = con.keys('instruments:'+token+':*')
	if len(keys)==1:
		return {'status':'success','results':keys[0].split(':')[1:]}
	return None

@override_with_ams
def place_order_tpsl(request):
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
			notifs = ujson.loads(notifs)
			notif_used = notifs['used'].get(notification_uuid,0)
			if notif_used:
				return JsonResponse({"status":"used"})		
		except:
			print traceback.format_exc()

		deployment_uuid = request.POST.get('deployment_uuid','')
		algo_uuid = request.POST.get('algo_uuid','')
		algo_name = request.POST.get('algo_name','')
		token = request.POST.get('token','')
		instrument = fetch_with_token(token)
		if instrument==None:
			return JsonResponse({"status":"error",'instrument':'none','params':[token]})

		con = get_redis_connection('default')
		key_prefix = ':'.join(['deployed',user_uuid,'*',deployment_uuid])
		deployed_keys = con.keys(key_prefix)
		# print 'zzzzzzzzzzzzzzzzzzzzzz11111111111',key_prefix
		if(len(deployed_keys)==0):
			print 'deployment_uuid not present'
			return JsonResponse({"status":"success",'error-type':'Strategy not live','error_msg':'Strategy not live'})

		exchange = instrument['results'][10]
		symbol = instrument['results'][2]
		segment = instrument['results'][9]
		transaction_type = request.POST.get('transaction_type','')
		order_type = request.POST.get('order_type','MARKET')
		tpsl_key = request.POST.get('tpsl_key','')
		# if order_type=='BUY':
		# 	order_type='SELL'
		# elif order_type=='SELL':
		# 	order_type='BUY'

		quantity = int(request.POST.get('quantity',0))
		product = request.POST.get('product','')
		validity = request.POST.get('validity','')

		deployment_uuid = request.POST.get('deployment_uuid','')

		if deployment_uuid == '':
			print 'deployment_uuid not present'
			return JsonResponse({"status":"error",'error_msg':'auth'})

		access_token = request.session.get('access_token','')
		public_token = request.session.get('public_token','')
		user_broker_id = request.session.get('user_broker_id','')
		broker = 'zerodha'

		if access_token=='' or public_token=='' or user_broker_id=='':
			print 'probably kite login popup'
			return JsonResponse({"status":"error","error":"BrokerLogin",'error_msg':'BrokerLogin'})

		payload = {
		  "api_key":settings.KITE_API_KEY,
		  "access_token":access_token,
		  "tradingsymbol":symbol,
		  "exchange":exchange,
		  "transaction_type":transaction_type,
		  "order_type":order_type,
		  "quantity":quantity,
		  "product":product,
		  "validity":validity
		}

		# print payload
		headers = {}
		if settings.KITE_HEADER == True:
			headers = {"X-Kite-Version":"3"}
			auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
			headers["Authorization"] = "token {}".format(auth_header)
		response = requests.request("POST","https://api-partners.kite.trade/orders/regular", data=payload,headers=headers)
		if response.status_code == 200:
			response_json = json.loads(response.text)
			if response_json['status']=="success":
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
							"api_key":settings.KITE_API_KEY,
							"access_token":access_token,
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

					pipeline = con.pipeline()

					keys = con.keys('deployed:'+user_uuid+':*:'+deployment_uuid)
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
						'open_notif':False
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
				return JsonResponse({'status':'error','order_response':response_json,'response_code':response.status_code,'error_msg':'auth'})
		else:
			return JsonResponse({'status':'error','response_code':response.status_code,'error-type':'Session expired, re-login required','error_msg':'Session expired, re-login required'})
		return JsonResponse({'status':'error','error':'none','error_msg':'none'})
	return JsonResponse({'status':'error'})

@override_with_ams
def place_order_tpsl_new(request):
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
		deployed_keys = get_deployment_keys({"user_uuid":user_uuid,"deployment_uuid":deployment_uuid,"status":0}) #con.keys(key_prefix)
		# print 'zzzzzzzzzzzzzzzzzzzzzz11111111111',key_prefix
		if(len(deployed_keys)==0):
			print 'deployment_uuid not present'
			return JsonResponse({"status":"error",'error-type':'Strategy not live','error_msg':'Strategy not live'})

		# exchange = instrument['results'][10]
		# symbol = instrument['results'][2]
		# segment = instrument['results'][9]
		transaction_type = request.POST.get('transaction_type','')
		order_type = request.POST.get('order_type','MARKET')
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
			elif segment=='NFO-OPT':
				exchange="NFO"
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

		access_token = request.session.get('access_token','')
		public_token = request.session.get('public_token','')
		user_broker_id = request.session.get('user_broker_id','')
		broker = 'zerodha'

		if access_token=='' or public_token=='' or user_broker_id=='':
			print 'probably kite login popup'
			return JsonResponse({"status":"error","error":"BrokerLogin",'error_msg':'BrokerLogin'})

		payload = {
		  "api_key":settings.KITE_API_KEY,
		  "access_token":access_token,
		  "tradingsymbol":symbol,
		  "exchange":exchange,
		  "transaction_type":transaction_type,
		  "order_type":order_type,
		  "quantity":quantity,
		  "product":product,
		  "validity":validity
		}
		if order_type=='LIMIT':
			payload['price']=price

		if variety.lower()=='bo':
			payload['price']=price
			payload['variety']=variety.lower()
			payload['squareoff']=squareoff
			payload['stoploss']=stoploss
			if trailing_stoploss!=0:
				payload['trailing_stoploss']=trailing_stoploss

		try:
			notifs['used'][notification_uuid]=1 # mark notitification as used(actioned upon)
			con.set('today_notification:'+user_uuid,ujson.dumps(notifs))
			ex_time = int((datetime.datetime.now().replace(hour=3,minute=0,second=0)+datetime.timedelta(days=1)).strftime('%s')) - int(datetime.datetime.now().strftime('%s'))
			con.expire('today_notification:'+user_uuid,ex_time)
		except:
			pass
		# print payload
		headers = {}
		if settings.KITE_HEADER == True:
			headers = {"X-Kite-Version":"3"}
			auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
			headers["Authorization"] = "token {}".format(auth_header)
		response = requests.request("POST","https://api-partners.kite.trade/orders/"+variety.lower(), data=payload,headers=headers)
		try:
			response_json = json.loads(response.text)
		except:
			return JsonResponse({'status':'error','error':'none','error_msg':'Kite response error'})
		if response.status_code == 200:
			if response_json['status']=="success":
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

					keys = deployed_keys#get_deployment_keys({"user_uuid":user_uuid,"deployment_uuid":deployment_uuid}) #con.keys('deployed:'+user_uuid+':*:'+deployment_uuid)
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
				notifs['used'][notification_uuid]=0 # mark notitification as used(actioned upon)
				con.set('today_notification:'+user_uuid,ujson.dumps(notifs))
				ex_time = int((datetime.datetime.now().replace(hour=3,minute=0,second=0)+datetime.timedelta(days=1)).strftime('%s')) - int(datetime.datetime.now().strftime('%s'))
				con.expire('today_notification:'+user_uuid,ex_time)
				return JsonResponse({'status':'error','order_response':response_json,'response_code':response.status_code,'error_msg':'auth'})
		elif response.status_code == 403:
			notifs['used'][notification_uuid]=0 # mark notitification as used(actioned upon)
			con.set('today_notification:'+user_uuid,ujson.dumps(notifs))
			ex_time = int((datetime.datetime.now().replace(hour=3,minute=0,second=0)+datetime.timedelta(days=1)).strftime('%s')) - int(datetime.datetime.now().strftime('%s'))
			con.expire('today_notification:'+user_uuid,ex_time)
			return JsonResponse({'status':'error','response_code':response.status_code,'error-type':'Session expired, re-login required','error_msg':'Session expired, re-login required'})
		elif response.status_code == 428:
			notifs['used'][notification_uuid]=0 # mark notitification as used(actioned upon)
			con.set('today_notification:'+user_uuid,ujson.dumps(notifs))
			ex_time = int((datetime.datetime.now().replace(hour=3,minute=0,second=0)+datetime.timedelta(days=1)).strftime('%s')) - int(datetime.datetime.now().strftime('%s'))
			con.expire('today_notification:'+user_uuid,ex_time)
			return JsonResponse({'status':'error','response_code':response.status_code,'error_msg':'Order needs authorisation at depository, please visit kite.zerodha.com to place the order','error-type':'Order needs authorisation at depository, please visit kite.zerodha.com to place the order','error_url':"https://kite.zerodha.com"})
		else:
			notifs['used'][notification_uuid]=0 # mark notitification as used(actioned upon)
			con.set('today_notification:'+user_uuid,ujson.dumps(notifs))
			ex_time = int((datetime.datetime.now().replace(hour=3,minute=0,second=0)+datetime.timedelta(days=1)).strftime('%s')) - int(datetime.datetime.now().strftime('%s'))
			con.expire('today_notification:'+user_uuid,ex_time)
			return JsonResponse({'status':'error','response_code':response.status_code,'error-type':'Session expired, re-login required','error_msg':response_json.get('message',"Unknown error")})
		return JsonResponse({'status':'error','error':'none','error_msg':'none'})
	return JsonResponse({'status':'error'})

@override_with_ams
def place_order_direct(request):
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
		tag = request.POST.get('tag','')
		tpsl_key = request.POST.get('tpsl_key','')
		broker = request.POST.get('broker','')
		squareoff = request.POST.get('squareoff','')
		stoploss = request.POST.get('stoploss','')
		trailing_stoploss = request.POST.get('trailing_stoploss','')

		access_token = request.session.get('access_token','')
		public_token = request.session.get('public_token','')
		user_broker_id = request.session.get('user_broker_id','')
		broker = 'zerodha'
		
		if access_token=='' or public_token=='' or user_broker_id=='':
			print 'probably kite login popup'
			return JsonResponse({"status":"error","error":"BrokerLogin",'error_msg':'BrokerLogin'})

		try:
			quantity=int(quantity)
		except:
			return JsonResponse({"status":"error","error_msg":"Invalid quantity"})

		if segment=='' and exchange=='CDS':
			segment = 'CDS-FUT'
		elif segment=='' and exchange=='MCX':
			segment = 'MCX'
		elif segment=='' and exchange=='NFO':
			if str(symbol).endswith("CE") or str(symbol).endswith("PE"):
				segment = 'NFO-OPT'
			else:
				segment = 'NFO-FUT'
		elif exchange=='NFO-FUT':
			segment = 'NFO-FUT'
			exchange = 'NFO'
		elif exchange=='NFO-OPT':
			segment = 'NFO-OPT'
			exchange = 'NFO'
		elif segment == '':
			segment = 'NSE'
			
		payload = {
		  "api_key":settings.KITE_API_KEY,
		  "access_token":access_token,
		  "tradingsymbol":symbol,
		  "exchange":exchange,
		  "transaction_type":transaction_type,
		  "order_type":order_type,
		  "quantity":quantity,
		  "product":product,
		  "validity":validity,
		  "tag":tag
		}
		if variety=='':
			return JsonResponse({"status":"error","error_msg":"Unknown variety"})
		elif variety == 'regular' or variety =='amo':
			if order_type =='LIMIT':
				try:
					payload['price']=float(price)
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid price"})
			elif order_type == 'SL':
				try:
					payload['price']=float(price)
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid price"})
				try:
					payload['trigger_price']=float(trigger_price)
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid trigger price"})
			elif order_type=='SL-M':
				try:
					payload['trigger_price']=float(trigger_price)
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid trigger price"})
			if disclosed_quantity!='':
				try:
					payload['disclosed_quantity']=int(disclosed_quantity)
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid disclosed quantity"})
		elif variety == 'bo':
			if order_type=='MARKET' or order_type=='SL-M':
				return JsonResponse({"status":"error","error_msg":"Invalid order type"})

			if order_type=='LIMIT':
				try:
					payload['price']=float(price)
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid price"})
			elif order_type == 'SL':
				try:
					payload['price']=float(price)
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid price"})
				try:
					payload['trigger_price']=float(trigger_price)
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid trigger price"})

			if squareoff!='':
				try:
					payload['squareoff']=float(squareoff)
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid squareoff price"})
			else:
				return JsonResponse({"status":"error","error_msg":"Invalid squareoff price"})

			if stoploss!='':
				try:
					payload['stoploss']=float(stoploss)
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid stoploss price"})
			else:
				return JsonResponse({"status":"error","error_msg":"Invalid stoploss price"})

			if trailing_stoploss!='':
				try:
					payload['trailing_stoploss']=float(trailing_stoploss)
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid trailing stoploss price"})
			else:
				return JsonResponse({"status":"error","error_msg":"Invalid trailing stoploss price"})

		elif variety == 'co':
			try:
				payload['trigger_price']=float(trigger_price)
			except:
				return JsonResponse({"status":"error","error_msg":"Invalid trigger price"})
			if order_type == 'LIMIT':
				try:
					payload['price']=float(price)
				except:
					return JsonResponse({"status":"error","error_msg":"Invalid price"})
			elif order_type != 'MARKET' and order_type != 'LIMIT':
				return JsonResponse({"status":"error","error_msg":"Invalid order type"})

		headers = {}
		if settings.KITE_HEADER == True:
			headers = {"X-Kite-Version":"3"}
			auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
			headers["Authorization"] = "token {}".format(auth_header)
		print payload,headers
		response = requests.request("POST","https://api-partners.kite.trade/orders/"+variety, data=payload,headers=headers)

		response_json = json.loads(response.text)
		if response.status_code == 200:
			if response_json['status']=="success":
				payload['order_placement']="manual"
				payload['segment']=segment
				payload['broker']=broker
				broker_order = models.BrokerOrder(user_uuid=user_uuid,
				algo_uuid=algo_uuid,
				algo_name=algo_name,
				deployment_uuid='DIRECT_'+exchange.lower()+'_'+symbol.lower(),
				order_id=response_json['data'].get('order_id',''),
				status=response_json['status'],
				order_payload = payload
				)
				broker_order.save()
				return JsonResponse({'status':'success','order_id':response_json['data'].get('order_id','')})
			return JsonResponse({"status":"error","error_msg":response_json['data']}) 
		elif response.status_code == 403:
			print response.text
			return JsonResponse({"status":"error","error_msg":'Session expired, re-login required'}) 
		elif response.status_code == 400:
			print response.text
			return JsonResponse({"status":"error","error_msg":response_json.get('message',"Error placing order")})
		elif response.status_code == 428:
			return JsonResponse({'status':'error','response_code':response.status_code,'error_msg':'Order needs authorisation at depository, please visit kite.zerodha.com to place the order','error-type':'Order needs authorisation at depository, please visit kite.zerodha.com to place the order','error_url':"https://kite.zerodha.com"})
		else:
			print response.text
			return JsonResponse({"status":"error","error_msg":"Unexpected error"})
	return JsonResponse({"status":"error","error_msg":"method"})

def fetch_sym_tokens(request):
	con = get_redis_connection("default")
	seg_sym = request.GET.get('seg_sym',None)
	results = []
	seg,sym = seg_sym.split('_')
	if request.method == 'GET':
		if seg_sym:
			keys = con.keys('instruments:*:'+sym+':*:'+seg+':*')
			if len(keys)==1:
				return JsonResponse({'status':'success','results':keys[0].split(':')[1:]})
	return JsonResponse({'status':'error'})

def fetch_sym_tokens_scan(request):
	con = get_redis_connection("default")
	seg_sym = request.GET.get('seg_sym',None)
	results = []
	seg,sym = seg_sym.split('_')
	if request.method == 'GET':
		if seg_sym:
			keys = con.keys('instruments:*:'+sym+':*:'+seg+':*')
			if len(keys)==1:
				return JsonResponse({'status':'success','results':keys[0].split(':')[1:]})
	return JsonResponse({'status':'error'})

def fetch_sym_tokens2(request):
	con = get_redis_connection("default")
	token = request.GET.get('token',None)
	results = []
	if request.method == 'GET':
		if token:
			keys = con.keys('instruments:*'+token+':*')
			if len(keys)==1:
				return JsonResponse({'status':'success','results':keys[0].split(':')[1:]})
	return JsonResponse({'status':'error'})

def fetch_id(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth and user_uuid!='':
		return JsonResponse({"status":"error"})
	else:
		return JsonResponse({"status":"success","id":user_uuid})

	return JsonResponse({"status":"error"})

def fetch_dashboard_metrics(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error","error":"auth"},status=401)
	
	usage_metric = {}
	alert_metrics = {}
	try:
		user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
		usage_metric = {}
		now_time = datetime.datetime.now()
		renewal_time = (now_time.replace(hour=23,minute=0,second=0) - now_time).seconds/3600+2
		if user_subscription.subscription_validity<datetime.datetime.now():
			usage_metric['backtest'] = 0
			usage_metric['deployed'] = 0
			usage_metric['total_backtest'] = 0
			usage_metric['total_deployments'] = 0
		else:
			con = get_redis_connection("default")
			#user_uuid : {'deployed':0,'backtest':0}
			usage = con.get('daily_usage:'+user_uuid)
			if usage != None:
				usage = eval(usage)
			else:
				usage = {'backtest':0,'deployed':0}

			usage['deployed'] = 0
			# deps_live = con.keys('deployed:'+user_uuid+':*')
			deps_live = get_deployment_keys({"user_uuid":user_uuid,"deployment_uuid":deployment_uuid,"status":0,"expiration_time":{"$gte":datetime.datetime.now()}})
			if(deps_live):
				d_count = 0
				for d in deps_live:
					if '/USDC' not in d:
						d_count+=1
				usage['deployed']=len(deps_live)

			now_time = datetime.datetime.now()
			renewal_time = (now_time.replace(hour=23,minute=0,second=0) - now_time).seconds/3600+2

			usage_metric['backtest'] = usage.get('backtest',0)
			usage_metric['deployed'] = usage.get('deployed',0)
			con.get('user_plans:'+str(user_subscription.subscription_type))
			if user_subscription.subscription_type == 0:
				# print 'yooooooooooooooooooooo',usage.get('backtest',0)
				user_plan = con.get('user_plans:'+str(user_subscription.subscription_type))
				if user_plan:
					user_plan = ujson.loads(user_plan.replace("'",'"'))
					usage_metric['total_backtest'] = user_plan['daily_backtests']
					usage_metric['total_deployments'] = user_plan['daily_deploys']
				else:
					usage_metric['total_backtest'] = 50
					usage_metric['total_deployments'] = 5
			if user_subscription.subscription_type == 1:
				user_plan = con.get('user_plans:'+str(user_subscription.subscription_type))
				if user_plan:
					user_plan = ujson.loads(user_plan.replace("'",'"'))
					usage_metric['total_backtest'] = user_plan['daily_backtests']
					usage_metric['total_deployments'] = user_plan['daily_deploys']
				else:
					usage_metric['total_backtest'] = 200
					usage_metric['total_deployments'] = 25
			if user_subscription.subscription_type == 2:
				user_plan = con.get('user_plans:'+str(user_subscription.subscription_type))
				if user_plan:
					user_plan = ujson.loads(user_plan.replace("'",'"'))
					usage_metric['total_backtest'] = user_plan['daily_backtests']
					usage_metric['total_deployments'] = user_plan['daily_deploys']
				else:
					usage_metric['total_backtest'] = 500
					usage_metric['total_deployments'] = 50
			if user_subscription.subscription_type == 3:
				user_plan = con.get('user_plans:'+str(user_subscription.subscription_type))
				if user_plan:
					user_plan = ujson.loads(user_plan.replace("'",'"'))
					usage_metric['total_backtest'] = user_plan['daily_backtests']
					usage_metric['total_deployments'] = user_plan['daily_deploys']
				else:
					usage_metric['total_backtest'] = 1000
					usage_metric['total_deployments'] = 100

		total_created = models.Algorithm.objects(user_uuid=user_uuid,created_at__gte=now_time.replace(hour=0,minute=0,second=0)).count()
		usage_metric['total_created']=total_created
	except DoesNotExist:
		print traceback.format_exc()
		print 'Creating missing subscription'
		try:
			if(request.session.get('user_broker_id','')!= ''):
				subscription_uuid=str(uuid.uuid4())
				subscription_log_uuid = str(uuid.uuid4())
				user_subscription = models.UserSubscription(user_uuid=user_uuid,
					subscription_uuid=subscription_uuid,
					subscription_validity= max(datetime.datetime.today() + datetime.timedelta(days=int(7)),datetime.datetime(2018, 6, 30, 23, 59, 59)),
					latest_subscription_id = subscription_log_uuid,
					user_broker_id = request.session.get('user_broker_id',''),
					subscription_instance = 'trial'
					)

				user_subscription_log = models.UserSubscriptionLog(user_uuid=user_uuid,
					subscription_log_uuid = subscription_log_uuid,
					subscription_uuid = subscription_uuid,
					subscription_start = datetime.datetime.today(),
					subscription_stop = max(datetime.datetime.today() + datetime.timedelta(days=int(7)),datetime.datetime(2018, 6, 30, 23, 59, 59)), #datetime.datetime.today() + datetime.timedelta(days=int(21)),
					user_broker_id = request.session.get('user_broker_id',''),
					subscription_instance = 'trial'
					)

				user_subscription_log.save()
				user_subscription.save()
			else:
				return JsonResponse({"status":"error","error":"auth broker id null","error_msg":"auth broker id null"})
		except:
			print 'error creating subscription'
			print traceback.format_exc()

		usage_metric['backtest'] = 0
		usage_metric['deployed'] = 0
		usage_metric['total_backtest'] = 50
		usage_metric['total_deployments'] = 5
		usage_metric['total_created']=0
	except:
		print traceback.format_exc()

	try:
		now = datetime.datetime.now()
		order_logs = models.OrderLog.objects(user_uuid=user_uuid,created_at__gte=now.replace(hour=0,minute=0,second=0))
		deployed_algo_order = {}
		for o in order_logs:
			if(o['deployment_uuid'] in deployed_algo_order.keys()):
				deployed_algo_order[o['deployment_uuid']].append(o)
			else:
				deployed_algo_order[o['deployment_uuid']] = [o]

		sent = confirmed = exp_can = exit_confirmed = 0
		for k,order_history in deployed_algo_order.iteritems():
			order_len = len(order_history)
			for i,order in enumerate(order_history):
				log_tag = order["log_tag"]
				created_at = order["created_at"]
				if log_tag in ("Buy alert", "Sell alert"):
					sent += 1
					if i + 1 < order_len and order_history[i + 1]["log_tag"] == "User action":
						confirmed += 1
					if (i + 1 == order_len or order_history[i + 1]["log_tag"] != "User action") and (now - created_at).total_seconds() > 300:
						exp_can += 1
				if log_tag in ("Stop loss alert", "Target profit alert"):
					sent += 1
					if i + 1 < order_len and order_history[i + 1]["log_tag"] == "User action":
						exit_confirmed += 1
					if (i + 1 == order_len or order_history[i + 1]["log_tag"] != "User action") and (now - created_at).total_seconds() > 300:
						exp_can += 1
		alert_metrics = {'sent':sent,'confirmed':confirmed,'exp_can':exp_can}
	except:
		print traceback.format_exc()
	usage_metric.update(alert_metrics)
	resp = {'status':'success'}
	resp.update(usage_metric)
	resp.update(alert_metrics)
	return JsonResponse(resp)

def fetch_dashboard_usage_metrics(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error","error":"auth"},status=401)

	# checking subscription duration is valid
	try:
		user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
		usage_metric = {}
		now_time = datetime.datetime.now()
		renewal_time = (now_time.replace(hour=23,minute=0,second=0) - now_time).seconds/3600+2
		if user_subscription.subscription_validity<datetime.datetime.now():
			usage_metric['backtest'] = 0
			usage_metric['deployed'] = 0
			usage_metric['total_backtest'] = 0
			usage_metric['total_deployments'] = 0
		else:
			con = get_redis_connection("default")
			#user_uuid : {'deployed':0,'backtest':0}
			usage = con.get('daily_usage:'+user_uuid)
			if usage != None:
				usage = eval(usage)
			else:
				usage = {'backtest':0,'deployed':0}

			usage['deployed'] = 0
			# deps_live = con.keys('deployed:'+user_uuid+':*')
			deps_live = get_deployment_keys({"user_uuid":user_uuid,"status":0,"expiration_time":{"$gte":datetime.datetime.now()}})
			if(deps_live):
				usage['deployed']=len(deps_live)

			now_time = datetime.datetime.now()
			renewal_time = (now_time.replace(hour=23,minute=0,second=0) - now_time).seconds/3600+2

			usage_metric['backtest'] = usage.get('backtest',0)
			usage_metric['deployed'] = usage.get('deployed',0)
			con.get('user_plans:'+str(user_subscription.subscription_type))
			if user_subscription.subscription_type == 0:
				# print 'yooooooooooooooooooooo',usage.get('backtest',0)
				user_plan = con.get('user_plans:'+str(user_subscription.subscription_type))
				if user_plan:
					user_plan = ujson.loads(user_plan)
					usage_metric['total_backtest'] = user_plan['daily_backtests']
					usage_metric['total_deployments'] = user_plan['daily_deploys']
				else:
					usage_metric['total_backtest'] = 50
					usage_metric['total_deployments'] = 5
			if user_subscription.subscription_type == 1:
				user_plan = con.get('user_plans:'+str(user_subscription.subscription_type))
				if user_plan:
					user_plan = ujson.loads(user_plan)
					usage_metric['total_backtest'] = user_plan['daily_backtests']
					usage_metric['total_deployments'] = user_plan['daily_deploys']
				else:
					usage_metric['total_backtest'] = 200
					usage_metric['total_deployments'] = 25
			if user_subscription.subscription_type == 2:
				user_plan = con.get('user_plans:'+str(user_subscription.subscription_type))
				if user_plan:
					user_plan = ujson.loads(user_plan)
					usage_metric['total_backtest'] = user_plan['daily_backtests']
					usage_metric['total_deployments'] = user_plan['daily_deploys']
				else:
					usage_metric['total_backtest'] = 500
					usage_metric['total_deployments'] = 50
			if user_subscription.subscription_type == 3:
				user_plan = con.get('user_plans:'+str(user_subscription.subscription_type))
				if user_plan:
					user_plan = ujson.loads(user_plan)
					usage_metric['total_backtest'] = user_plan['daily_backtests']
					usage_metric['total_deployments'] = user_plan['daily_deploys']
				else:
					usage_metric['total_backtest'] = 1000
					usage_metric['total_deployments'] = 100

		total_created = models.Algorithm.objects(user_uuid=user_uuid,created_at__gte=now_time.replace(hour=0,minute=0,second=0)).count()
		usage_metric['total_created']=total_created
		return JsonResponse({"status":"success","usage_metric":usage_metric})
	except DoesNotExist:
		print traceback.format_exc()
		print 'Creating missing subscription'
		try:
			if(request.session.get('user_broker_id','')!= ''):
				subscription_uuid=str(uuid.uuid4())
				subscription_log_uuid = str(uuid.uuid4())
				user_subscription = models.UserSubscription(user_uuid=user_uuid,
					subscription_uuid=subscription_uuid,
					subscription_validity= max(datetime.datetime.today() + datetime.timedelta(days=int(7)),datetime.datetime(2018, 6, 30, 23, 59, 59)),
					latest_subscription_id = subscription_log_uuid,
					user_broker_id = request.session.get('user_broker_id',''),
					subscription_instance = 'trial'
					)

				user_subscription_log = models.UserSubscriptionLog(user_uuid=user_uuid,
					subscription_log_uuid = subscription_log_uuid,
					subscription_uuid = subscription_uuid,
					subscription_start = datetime.datetime.today(),
					subscription_stop = max(datetime.datetime.today() + datetime.timedelta(days=int(7)),datetime.datetime(2018, 6, 30, 23, 59, 59)), #datetime.datetime.today() + datetime.timedelta(days=int(21)),
					user_broker_id = request.session.get('user_broker_id',''),
					subscription_instance = 'trial'
					)

				user_subscription_log.save()
				user_subscription.save()
			else:
				return JsonResponse({"status":"error","error":"auth broker id null","error_msg":"auth broker id null"})
		except:
			print 'error creating subscription'
			print traceback.format_exc()

		usage_metric = {}
		usage_metric['backtest'] = 0
		usage_metric['deployed'] = 0
		usage_metric['total_backtest'] = 50
		usage_metric['total_deployments'] = 5
		usage_metric['total_created']=0
		return JsonResponse({"status":"success","usage_metric":usage_metric})
	except:
		print 'difffffffffff usage_metric error'
		print traceback.format_exc()

	return JsonResponse({"status":"error","error":"unknown"})

def fetch_alerts_mertics(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error","error":"auth"},status=401)
	try:
		now = datetime.datetime.now()
		order_logs = models.OrderLog.objects(user_uuid=user_uuid,created_at__gte=now.replace(hour=0,minute=0,second=0))
		deployed_algo_order = {}
		for o in order_logs:
			if(o['deployment_uuid'] in deployed_algo_order.keys()):
				deployed_algo_order[o['deployment_uuid']].append(o)
			else:
				deployed_algo_order[o['deployment_uuid']] = [o]

		sent = confirmed = exp_can = exit_confirmed = 0
		for k,order_history in deployed_algo_order.iteritems():
			order_len = len(order_history)
			for i,order in enumerate(order_history):
				log_tag = order["log_tag"]
				created_at = order["created_at"]
				if log_tag in ("Buy alert", "Sell alert"):
					sent += 1
					if i + 1 < order_len and order_history[i + 1]["log_tag"] == "User action":
						confirmed += 1
					if (i + 1 == order_len or order_history[i + 1]["log_tag"] != "User action") and (now - created_at).total_seconds() > 300:
						exp_can += 1
				if log_tag in ("Stop loss alert", "Target profit alert"):
					sent += 1
					if i + 1 < order_len and order_history[i + 1]["log_tag"] == "User action":
						exit_confirmed += 1
					if (i + 1 == order_len or order_history[i + 1]["log_tag"] != "User action") and (now - created_at).total_seconds() > 300:
						exp_can += 1
		alert_metrics = {'sent':sent,'confirmed':confirmed,'exp_can':exp_can}
		return JsonResponse({'status':'success','alert_metrics':alert_metrics})
	except:
		print traceback.format_exc()
	return JsonResponse({'status':'error','error':'unknown'})

@override_with_ams
def fetch_dashboard_funds(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True

	if not user_is_auth:
		return JsonResponse({"status":"error","error":"Login required, session expired"})
	try:
		available_balance = margins_used = account_value = 0.0
		headers = {}
		if settings.KITE_HEADER == True:
			headers = {"X-Kite-Version":"3"}
			auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
			headers["Authorization"] = "token {}".format(auth_header)
		response = requests.get("https://api-partners.kite.trade/user/margins/?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token','')),headers=headers)
		print "https://api-partners.kite.trade/user/margins/?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token',''))
		if response.status_code == 200:
			response_json = json.loads(response.text)
			equity_data = response_json['data']['equity']
			available_balance = equity_data['net']
			margins_used = equity_data['utilised']['debits']
			account_value = equity_data['available']['cash']

			commodity_data = response_json['data']['commodity']
			commodity_available_balance = commodity_data['net']
			commodity_margins_used = commodity_data['utilised']['debits']
			commodity_account_value = commodity_data['available']['cash']
			try:
				models.UserFunds.objects(user_uuid=user_uuid).update_one(set__funds_object=response_json['data'], upsert=True)
			except:
				print traceback.format_exc()
			return JsonResponse({"status":"success",'funds':{'available_balance':available_balance,'margins_used':margins_used,'account_value':account_value},'commodity_funds':{'available_balance':commodity_available_balance,'margins_used':commodity_margins_used,'account_value':commodity_account_value}})
		else:
			return JsonResponse({"status":"error","error":"Login required, session expired","error_msg":"Login required, session expired"})
	except:
		print traceback.format_exc()
	return JsonResponse({"status":"error","error":"Login required, session expired","error_msg":"Login required, session expired"})

def update_web_push_subscription(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error","error":"auth"},status=401)
	if request.method=='POST':
		user_id = request.POST.get('id','')
		# print(subscription_payload)
		if(user_id!=''):
			try:
				conn = get_redis_connection("default")
				subscription_str = request.POST.get('subscription_str','{}')
				subscription = json.loads(subscription_str)
				if(subscription):
					subscription_dict = conn.get('web-push-subscription:'+user_id)
					if subscription_dict is not None:
						subscription_dict = json.loads(subscription_dict.decode())
						subscription_dict = {}
						subscription_dict[subscription['endpoint']] = subscription
						# print(subscription)
						conn.set('web-push-subscription:'+user_id,json.dumps(subscription_dict))
					else:
						subscription_dict = {}
						subscription_dict[subscription['endpoint']] = subscription
						conn.set('web-push-subscription:'+user_id,json.dumps(subscription_dict))
					# await send_web_push(user_id,"{}")
					return JsonResponse({'status':'success'})
			except:
				print(traceback.format_exc())
	if request.method=='GET':
		print('Wrong method update_web_push_subscription')
	return JsonResponse({'status':'error'})

def fetch_samples(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error","error":"auth"},status=401)

	try:
		con = get_redis_connection("default")
		samples = con.get('user_samples')
		bt_samples = []
		if samples:
			samples = eval(samples)
			count = 0
			for s in samples['samples']:
				try:
					print('algo_uuid',s[0],'seg_sym',s[2]+'_'+s[1])
					backtest_sample = models.BacktestMeta.objects.get(algo_uuid=s[0],seg_sym=s[2]+'_'+s[1])
					bt_samp = {}
					bt_samp['algo_uuid'] = backtest_sample['algo_uuid']
					# del backtest_sample['backtest_result'][s[2]+'_'+s[1]]['trade_log']
					# del backtest_sample['backtest_result'][s[2]+'_'+s[1]]['pnl']
					del backtest_sample['backtest_result'][s[2]+'_'+s[1]]['run_params']['user_uuid']
					del backtest_sample['algo_obj']['user_uuid']
					bt_samp['algo_obj'] = backtest_sample['algo_obj']
					bt_samp['backtest_result'] = backtest_sample['backtest_result']
					bt_samp['seg_sym'] = backtest_sample['seg_sym']
					bt_samples.append(bt_samp)
					count+=1
					if count>=3:
						break
				except:
					print traceback.format_exc()
		return JsonResponse({"status":"success","samples":bt_samples})
	except:
		pass
	return JsonResponse({"status":"error","error":"unknown"})

def market_observer_samples(request): 
	user_uuid = request.session.get('user_uuid','') 
	user_is_auth = request.session.get('user_is_auth',False) 
	# if settings.DEBUG: 
	if settings.ENV == "local" or settings.ENV == 'local1': 
		user_uuid = '123' 
		user_is_auth = True 
	if request.method!='GET': 
		return JsonResponse({"status":"error","error":"auth"}) 
 	try: 
		con = get_redis_connection("default") 
		samples = con.get('user_samples') 
		bt_samples = [] 
		if samples: 
			samples = eval(samples) 
		for s in samples['samples']:
			try: 
				print('algo_uuid',s[0],'seg_sym',s[2]+'_'+s[1])
				backtest_sample = models.BacktestMeta.objects.get(algo_uuid=s[0],seg_sym=s[2]+'_'+s[1]) 
				bt_samples.append(backtest_sample['algo_obj']) 
			except: 
				print traceback.format_exc() 
		resp = JsonResponse({"status":"success","samples":bt_samples})
		resp["Access-Control-Allow-Credentials"] = "true" 
		resp["Access-Control-Allow-Origin"] = "*"  
		return resp
	except: 
		pass
	resp = JsonResponse({"status":"error","error":"unknown"}) 
	resp["Access-Control-Allow-Credentials"] = "true" 
	resp["Access-Control-Allow-Origin"] = "*" 
	return resp 

def fetch_top_performers(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error","error":"auth"},status=401)

	try:
		con = get_redis_connection("default")
		samples = con.get('top_performers:'+user_uuid)
		bt_samples = []
		if samples:
			samples = eval(samples)
			for s in samples['backtests'][:3]:
				try:
					print('algo_uuid',s[0],'seg_sym',s[1])
					backtest_sample = models.BacktestMeta.objects.get(algo_uuid=s[0],seg_sym=s[1])
					bt_samp = {}
					bt_samp['algo_uuid'] = backtest_sample['algo_uuid']
					# del backtest_sample['backtest_result'][s[1]]['trade_log']
					# del backtest_sample['backtest_result'][s[1]]['pnl']
					del backtest_sample['backtest_result'][s[1]]['run_params']['user_uuid']
					del backtest_sample['algo_obj']['user_uuid']
					bt_samp['algo_obj'] = backtest_sample['algo_obj']
					bt_samp['backtest_result'] = backtest_sample['backtest_result']
					bt_samp['seg_sym'] = backtest_sample['seg_sym']
					bt_samples.append(bt_samp)
				except:
					print traceback.format_exc()
		return JsonResponse({"status":"success","backtests":bt_samples})
	except:
		print traceback.format_exc()
	return JsonResponse({"status":"error","error":"unknown"})


def get_subscription_limit(request): # important function, this gives the value for the top bar and the backtest page limit
	resp_json = False
	if(request.META.get('HTTP_X_CSRFTOKEN',None)):
		resp_json = True
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		return JsonResponse({"status":"success",'valid':True,'backtest':200,'deployments_remaining':5})
	if not user_is_auth:
		if resp_json:
			return JsonResponse({"status":"error","error":"auth"},status=401)
		return JsonResponse({"status":"error","msg":"auth"})

	# checking subscription duration is valid
	try:
		user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
		if user_subscription.subscription_validity<datetime.datetime.now():
			return JsonResponse({"status":"error",'valid':False,'reason':'Subscription duration is over','error_msg':'Subscription duration is over'})

		con = get_redis_connection("default")
		#user_uuid : {'deployed':0,'backtest':0}
		usage = con.get('daily_usage:'+user_uuid)
		if usage != None:
			usage = eval(usage)
		else:
			usage = {'backtest':0,'deployed':0}

		usage['deployed'] = 0
		# deps_live = con.keys('deployed:'+user_uuid+':*')
		deps_live = get_deployment_keys({"user_uuid":user_uuid,"status":0,"expiration_time":{"$gte":datetime.datetime.now()}})
		if(deps_live):
			usage['deployed']=len(deps_live)

		now_time = datetime.datetime.now()
		renewal_time = ((now_time.replace(hour=23,minute=0,second=0) - now_time).seconds/3600+2)%24
		if renewal_time==0:
			renewal_time = 24
		if user_subscription.subscription_type == 0:
			# print 'yooooooooooooooooooooo',usage.get('backtest',0) 
			backtests_remaining = 50 - usage.get('backtest',0)
			deployments_remaining = 5 - usage.get('deployed',0)
			print {"status":"success",'valid':True,'total_backtest':50,'total_deploys':5,'backtest':backtests_remaining,'deployments_remaining':deployments_remaining}
			return JsonResponse({"status":"success",'valid':True,'backtest':backtests_remaining,'total_backtest':50,'total_deploys':5,'deployments_remaining':deployments_remaining,'renewal_time':renewal_time,'subscription_type':user_subscription.subscription_type})
		if user_subscription.subscription_type == 1:
			backtests_remaining = 200 - usage.get('backtest',0)
			deployments_remaining = 25 - usage.get('deployed',0)
			return JsonResponse({"status":"success",'valid':True,'total_backtest':200,'total_deploys':25,'backtest':backtests_remaining,'deployments_remaining':deployments_remaining,'renewal_time':renewal_time,'subscription_type':user_subscription.subscription_type})
		if user_subscription.subscription_type == 2:
			backtests_remaining = 500 - usage.get('backtest',0)
			deployments_remaining = 50 - usage.get('deployed',0)
			return JsonResponse({"status":"success",'valid':True,'total_backtest':500,'total_deploys':50,'backtest':backtests_remaining,'deployments_remaining':deployments_remaining,'renewal_time':renewal_time,'subscription_type':user_subscription.subscription_type})
		if user_subscription.subscription_type == 3:
			backtests_remaining = 1000 - usage.get('backtest',0)
			deployments_remaining = 100 - usage.get('deployed',0)
			return JsonResponse({"status":"success",'valid':True,'total_backtest':1000,'total_deploys':100,'backtest':backtests_remaining,'deployments_remaining':deployments_remaining,'renewal_time':renewal_time,'subscription_type':user_subscription.subscription_type})
	except DoesNotExist:
		print traceback.format_exc()
		print 'Creating missing subscription'
		try:
			if(request.session.get('user_broker_id','')!= ''):
				subscription_uuid=str(uuid.uuid4())
				subscription_log_uuid = str(uuid.uuid4())
				user_subscription = models.UserSubscription(user_uuid=user_uuid,
					subscription_uuid=subscription_uuid,
					subscription_validity= max(datetime.datetime.today() + datetime.timedelta(days=int(7)),datetime.datetime(2018, 11, 30, 23, 59, 59)), #datetime.datetime.today() + datetime.timedelta(days=int(21)),
					latest_subscription_id = subscription_log_uuid,
					user_broker_id = request.session.get('user_broker_id',''),
					subscription_instance = 'trial'
					)

				user_subscription_log = models.UserSubscriptionLog(user_uuid=user_uuid,
					subscription_log_uuid = subscription_log_uuid,
					subscription_uuid = subscription_uuid,
					subscription_start = datetime.datetime.today(),
					subscription_stop = max(datetime.datetime.today() + datetime.timedelta(days=int(7)),datetime.datetime(2018, 11, 30, 23, 59, 59)), #datetime.datetime.today() + datetime.timedelta(days=int(21)),
					user_broker_id = request.session.get('user_broker_id',''),
					subscription_instance = 'trial'
					)

				user_subscription_log.save()
				user_subscription.save()
			else:
				return JsonResponse({"status":"error","error":"auth broker id null"})
		except:
			print 'error creating subscription'
			print traceback.format_exc()

		renewal_time = ((now_time.replace(hour=23,minute=0,second=0) - now_time).seconds/3600+2)%24
		if renewal_time==0:
			renewal_time = 24
		return JsonResponse({"status":"success",'valid':True,'backtest':200,'total_backtest':200,'total_deploys':5,'deployments_remaining':5,'renewal_time':renewal_time,'subscription_type':0})
	except:
		print 'difffffffffff usage_metric error'
		print traceback.format_exc()
	return JsonResponse({"status":"error"})

def get_subscription_valid(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		return JsonResponse({"status":"success",'valid':True,'backtest':100,'deployments_remaining':5})
	if not user_is_auth:
		return JsonResponse({"status":"error"})

	# checking subscription duration is valid
	try:
		user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
		if user_subscription.subscription_validity<datetime.datetime.now():
			return JsonResponse({"status":"error",'valid':False,'reason':'Subscription duration is over'})
		return JsonResponse({"status":"success",'valid':True,'reason':'Subscription is valid'})
	except:
		print traceback.format_exc()
	return JsonResponse({"status":"error"})

def start_subscription(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		return JsonResponse({"status":"success",'valid':True,'backtest':100,'deployments_remaining':5})
	
	if request.method!='POST':
		return JsonResponse({"status":"error","error-type":"method"})

	subscription_plan = request.POST.get('subscription_plan','basic').lower()
	subscription_instance = request.POST.get('subscription_instance','renewal')
	subscription_change = request.POST.get('subscription_change','False')
	print("subscription_plan",subscription_plan)

	available_plans = {
						'free':{'daily_backtests': 20, 'subscription_tax': 0, 'subscription_plan': 'free', 'subscription_price': 0, 'plan_id': 0, 'subscription_validity_date': 7, 'daily_deploys': 2, 'subscription_total_price': 0, 'subscription_product': 'free','note':'Free trial till 30th Nov 2018','subscription_period':30},
						'basic':{'daily_backtests': 200, 'subscription_tax': 90, 'subscription_plan': 'basic', 'subscription_price': 500, 'plan_id': 1, 'subscription_validity_date': 30, 'daily_deploys': 25, 'subscription_total_price': 590, 'subscription_product': 'basic','note':'Free for all Zerodha clients till 31st July, 18','subscription_period':30},
						'premium':{'daily_backtests': 500, 'subscription_tax': 162, 'subscription_plan': 'premium', 'subscription_price': 900, 'plan_id': 2, 'subscription_validity_date': 30, 'daily_deploys': 50, 'subscription_total_price': 1062, 'subscription_product': 'premium','note':'Starts from 1st July, 18','subscription_period':30},
						'ultimate':{'daily_backtests': 1000, 'subscription_tax': 252, 'subscription_plan': 'ultimate', 'subscription_price': 1400, 'plan_id': 3, 'subscription_validity_date': 30, 'daily_deploys': 100, 'subscription_total_price': 1652, 'subscription_product': 'ultimate','note':'Starts from 1st July, 18','time':'30 minutes','subscription_period':30}
						}

	if not user_is_auth:
		request.session['subscription_start_before_login'] = True
		request.session['subscription_start_before_login_subscription_plan_id'] = available_plans.get(subscription_plan,{'daily_backtests': 200, 'subscription_tax': 90, 'subscription_plan': 'basic', 'subscription_price': 500, 'plan_id': 1, 'subscription_validity_date': 30, 'daily_deploys': 25, 'subscription_total_price': 590, 'subscription_product': 'basic','note':'Free for all Zerodha clients till 31st July, 18','subscription_period':30}).get('plan_id',-1)
		request.session['subscription_start_before_login_subscription_plan'] = subscription_plan
		return JsonResponse({"status":"error","error-type":"auth","redirect":"login","error_msg":"Session expired, re-login required"})


	plan_to_subscribe = available_plans.get(subscription_plan,{'daily_backtests': 20, 'subscription_tax': 0, 'subscription_plan': 'free', 'subscription_price': 0, 'plan_id': 0, 'subscription_validity_date': 7, 'daily_deploys': 2, 'subscription_total_price': 0, 'subscription_product': 'free','subscription_period':30})
	
	if request.POST.get('subscription_plan','basic')=="" or request.POST.get('subscription_plan','basic')=="free" or plan_to_subscribe['plan_id']==0:
		return JsonResponse({"status":"error","error_msg":"Invalid subscription request, please write to support@streak.tech"})

	headers = {}
	if settings.KITE_HEADER == True:
		headers = {"X-Kite-Version":"3"}
		auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
		headers["Authorization"] = "token {}".format(auth_header)	
	response = requests.get("https://api-partners.kite.trade/user/margins/?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token','')),headers=headers)
	if response.status_code != 200:
		pass
		# return JsonResponse({"status":"error",'valid':False,'msg':'Login required'})
	else:
		try:
			response_json = json.loads(response.text)
			# if response_json["status"]!="success":
			# 	return JsonResponse({"status":"error",'valid':False,'msg':'Error occured, try again'})
			# el
			if (response_json["status"]=="success" and (response_json["data"]["equity"]["available"]["cash"]+response_json["data"]["equity"]["available"]["intraday_payin"])<max(600,plan_to_subscribe['subscription_total_price'])) and (response_json["status"]=="success" and (response_json["data"]["commodity"]["available"]["cash"]+response_json["data"]["commodity"]["available"]["intraday_payin"])<max(600,plan_to_subscribe['subscription_total_price'])):
				return JsonResponse({"status":"error",'valid':False,'msg':'Insufficient balance','error_msg':'Insufficient balance'})

		except:
			print traceback.format_exc()

	# checking subscription duration is valid
	try:

		user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)

		current_subscription_type = user_subscription.subscription_type
		current_subscription_validity = user_subscription.subscription_validity
		current_plan = available_plans.get(user_subscription.subscription_plan,{'daily_backtests': 200, 'subscription_tax': 90, 'subscription_plan': 'basic', 'subscription_price': 500, 'plan_id': 1, 'subscription_validity_date': 30, 'daily_deploys': 25, 'subscription_total_price': 590, 'subscription_product': 'basic','note':'Free for all Zerodha clients till 31st July, 18','subscription_period':30})

		if user_subscription.subscription_price<11:
			current_plan = available_plans.get("free")
			current_subscription_type = 0

		if current_subscription_validity>datetime.datetime.today() and user_subscription.subscription_period!="1" and user_subscription.subscription_type!=0:
			return JsonResponse({"status":"error",'error_msg':'Cannot downgrade with Zerodha'})

		prev_subscription_validity = user_subscription.subscription_validity
		subscription_start = prev_subscription_validity
		if(current_subscription_type==0): # if free trial, then start the subscription from today
			# print "checking subscription duration is valid"
			if plan_to_subscribe['plan_id']==1:
				subscription_validity = datetime.datetime.today()+datetime.timedelta(days=29)#,datetime.datetime(2018, 7, 31, 23, 59, 59))#+1)
			else:
				subscription_validity = datetime.datetime.today()+datetime.timedelta(days=29)#+1)
			subscription_start = datetime.datetime.today()
		else:
			subscription_validity = datetime.datetime.today()+datetime.timedelta(days=29)#+1)

		subscription_validity = subscription_validity.replace(hour=23,minute=59,second=59)

		
		if plan_to_subscribe['plan_id']>=current_subscription_type:
			user_subscription.subscription_product = plan_to_subscribe['subscription_product']
			user_subscription.subscription_type = plan_to_subscribe['plan_id']
			user_subscription.subscription_plan = plan_to_subscribe['subscription_plan']
		
		user_subscription.subscription_instance = subscription_instance

		# print current_subscription_validity, current_subscription_type,plan_to_subscribe['plan_id']
		# print(current_subscription_validity>datetime.datetime.today() and current_subscription_type > 0 and plan_to_subscribe['plan_id']>current_subscription_type)
		msg = 'Congratulations your subscription has started!'
		if(current_subscription_validity>datetime.datetime.today() and current_subscription_type > 0 and subscription_change=="False" and plan_to_subscribe['plan_id']==current_subscription_type):
			# renewing existing subscription
			user_subscription.subscription_active = True
			user_subscription.renew_plan = ''
			user_subscription.renew_plan_type = -1
			user_subscription.subscription_period = "1"
			user_subscription.save()
			msg = 'Congratulations your subscription has been renewed!'
		elif (current_subscription_validity>datetime.datetime.today() and current_subscription_type > 0 and plan_to_subscribe['plan_id']>current_subscription_type):
			# upgrading to higher plan
			# price_diff = abs(user_subscription.subscription_price-plan_to_subscribe['subscription_price'])
			# price_diff = abs(user_subscription.subscription_price-plan_to_subscribe['subscription_price'])
			

			days_charged = max((current_plan.get('subscription_period',30)-(current_subscription_validity-datetime.datetime.today()).days),0)
			# print 'days_charged',days_charged
			price_utilised = user_subscription.subscription_price/current_plan.get('subscription_period',30)*days_charged
			# print 'price utilised',price_utilised

			print("upgrading to higher plan",price_utilised)
			to_charge = max(plan_to_subscribe['subscription_price']-(current_plan.get('subscription_price',500)-price_utilised),0)
			to_charge = round(to_charge,2)
			# print 'to_charge',to_charge,plan_to_subscribe['subscription_price'],current_plan.get('subscription_price',500)

			user_subscription.subscription_price = plan_to_subscribe['subscription_price']
			user_subscription.subscription_tax = plan_to_subscribe['subscription_tax']
			user_subscription.subscription_total_price = plan_to_subscribe['subscription_total_price']
			user_subscription.subscription_active = True
			user_subscription.renew_plan = plan_to_subscribe['subscription_product']
			user_subscription.renew_plan_type = plan_to_subscribe['plan_id']
			subscription_log_uuid = str(uuid.uuid4())
			user_subscription.latest_subscription_id = subscription_log_uuid
			# subscription_validity = prev_subscription_validity
			subscription_validity = datetime.datetime.today()+datetime.timedelta(days=29+1)
			subscription_validity = subscription_validity.replace(hour=23,minute=59,second=59)
			user_subscription.subscription_validity = subscription_validity
			user_subscription.subscription_period = "1"

			user_subscription_log = models.UserSubscriptionLog(user_uuid=user_uuid,
				subscription_uuid = user_subscription.subscription_uuid,
				user_broker_id = user_subscription.user_broker_id,
				subscription_log_uuid = subscription_log_uuid,
				subscription_type = plan_to_subscribe['plan_id'],
				subscription_product = plan_to_subscribe['subscription_product'],
				subscription_plan = plan_to_subscribe['subscription_plan'],
				subscription_start = datetime.datetime.today(),
				subscription_stop = subscription_validity,
				subscription_instance = subscription_instance,
				subscription_period = "1",
				subscription_price = max(0,to_charge),
				subscription_tax = round(max(0,to_charge)*0.18,2),
				subscription_total_price = round(max(0,to_charge)*1.18,2)
				)

			user_subscription_log.save()
			user_subscription.save()
			msg = 'Congratulations your subscription has been upgraded!'
			try:
				con4 = get_redis_connection("screener_plan")
				con4.delete('plan_'+user_uuid)
			except:
				pass
		elif (current_subscription_validity>datetime.datetime.today() and current_subscription_type > 0 and plan_to_subscribe['plan_id']<=current_subscription_type):
			# upgrading to lower plan
			print('upgrading to lower plan')
			# user_subscription.subscription_price = 0
			# user_subscription.subscription_tax = 0
			# user_subscription.subscription_tax = 0
			user_subscription.subscription_active = True
			user_subscription.renew_plan = plan_to_subscribe['subscription_product']
			user_subscription.renew_plan_type = plan_to_subscribe['plan_id']
			# user_subscription.subscription_price = plan_to_subscribe['subscription_price']
			# user_subscription.subscription_tax = plan_to_subscribe['subscription_tax']
			# user_subscription.subscription_total_price = plan_to_subscribe['subscription_total_price']
			# subscription_log_uuid = str(uuid.uuid4())
			# user_subscription_log = models.UserSubscriptionLog(user_uuid=user_uuid,
			# 	subscription_uuid = user_subscription.subscription_uuid,
			# 	user_broker_id = user_subscription.user_broker_id,
			# 	subscription_log_uuid = subscription_log_uuid,
			# 	subscription_type = plan_to_subscribe['plan_id'],
			# 	subscription_product = plan_to_subscribe['subscription_product'],
			# 	subscription_plan = plan_to_subscribe['subscription_plan'],
			# 	subscription_start = subscription_start,
			# 	subscription_stop = subscription_validity,
			# 	subscription_instance = subscription_instance,
			# 	subscription_price = 0,
			# 	subscription_tax = 0,
			# 	subscription_total_price = 0
			# 	)
			# user_subscription_log.save()
			user_subscription.save()
			msg = 'Your subscription has been downgraded!'
		else:
			#starting fresh subscription
			subscription_log_uuid = str(uuid.uuid4())
			user_subscription.subscription_type = plan_to_subscribe['plan_id']
			user_subscription.subscription_product = plan_to_subscribe['subscription_product']
			user_subscription.subscription_plan = plan_to_subscribe['subscription_product']
			user_subscription.subscription_validity = subscription_validity
			user_subscription.latest_subscription_id = subscription_log_uuid
			user_subscription.subscription_price = plan_to_subscribe['subscription_price']
			user_subscription.subscription_tax = plan_to_subscribe['subscription_tax']
			user_subscription.subscription_total_price = plan_to_subscribe['subscription_total_price']
			user_subscription.subscription_active = True
			user_subscription.subscription_period = "1"


			user_subscription_log = models.UserSubscriptionLog(user_uuid=user_uuid,
											subscription_uuid = user_subscription.subscription_uuid,
											user_broker_id = user_subscription.user_broker_id,
											subscription_log_uuid = subscription_log_uuid,
											subscription_type = plan_to_subscribe['plan_id'],
											subscription_product = plan_to_subscribe['subscription_product'],
											subscription_plan = plan_to_subscribe['subscription_plan'],
											subscription_start = datetime.datetime.today(),
											subscription_stop = subscription_validity,
											subscription_instance = subscription_instance,
											subscription_price = plan_to_subscribe['subscription_price'],
											subscription_tax = plan_to_subscribe['subscription_tax'],
											subscription_total_price = plan_to_subscribe['subscription_total_price'],
											subscription_period = "1"
											)

			user_subscription_log.save()
			user_subscription.save()
			update_usage_util(user_uuid,'backtest',clear=True)
			try:
				con4 = get_redis_connection("screener_plan")
				con4.delete('plan_'+user_uuid)
			except:
				pass

		subscription_status_changed(user_uuid=user_uuid,
			user_broker_id=user_subscription.user_broker_id,
			change_type='started for '+plan_to_subscribe['subscription_plan']+' with validity till '+str(subscription_validity),action='started',plan=plan_to_subscribe['subscription_plan'],email=request.session.get('user_email',''))
		# send_subscription_emails(user_uuid=user_uuid,email)
		return JsonResponse({"status":"success",'valid':True,'msg':msg,'plan_id':plan_to_subscribe['plan_id'],'subscription_plan':plan_to_subscribe['subscription_plan']})
	except:
		print("to be removed in production",traceback.format_exc())
		# TODO, to be removed in production
		subscription_plan = request.POST.get('subscription_plan','free')

		subscription_instance = request.POST.get('subscription_instance','renewal')
		subscription_change = request.POST.get('subscription_change','False')

		subscription_uuid = str(uuid.uuid4())
		subscription_log_uuid = str(uuid.uuid4())
		user_subscription = models.UserSubscription(user_uuid=user_uuid,
					subscription_uuid=subscription_uuid,
					subscription_validity= subscription_validity,
					latest_subscription_id = subscription_log_uuid,
					user_broker_id = request.session['user_broker_id'],
					subscription_type = plan_to_subscribe['plan_id'],
					subscription_instance = 'first',
					subscription_product = plan_to_subscribe['subscription_product'],
					subscription_plan = plan_to_subscribe['subscription_plan'],
					subscription_price = plan_to_subscribe['subscription_price'],
					subscription_tax = plan_to_subscribe['subscription_tax'],
					subscription_total_price = plan_to_subscribe['subscription_total_price'],
					subscription_period = "1",
					subscription_active=True
					)

		user_subscription_log = models.UserSubscriptionLog(user_uuid=user_uuid,
			subscription_log_uuid = subscription_log_uuid,
			subscription_uuid = subscription_uuid,
			subscription_start = datetime.datetime.today(),
			subscription_stop = subscription_validity,
			subscription_product = plan_to_subscribe['subscription_product'],
			subscription_type = plan_to_subscribe['plan_id'],
			subscription_plan = plan_to_subscribe['subscription_plan'],
			user_broker_id = request.session['user_broker_id'],
			subscription_instance = 'first',
			subscription_price = plan_to_subscribe['subscription_price'],
			subscription_tax = plan_to_subscribe['subscription_tax'],
			subscription_total_price = plan_to_subscribe['subscription_total_price'],
			subscription_period = "1"
			)

		user_subscription_log.save()
		user_subscription.save()

		subscription_status_changed(user_uuid=user_uuid,
			user_broker_id=request.session['user_broker_id'],
			change_type='started for '+plan_to_subscribe['subscription_plan']+' with validity till '+str(subscription_validity),action='started',plan=plan_to_subscribe['subscription_plan'],email=request.session.get('user_email',''))
		return JsonResponse({"status":"success",'valid':True,'msg':'Congratulations your subscription has started!','plan_id':plan_to_subscribe['plan_id'],'subscription_plan':plan_to_subscribe['subscription_plan']})
	return JsonResponse({"status":"error"})

def market_observer_samples(request): 
	user_uuid = request.session.get('user_uuid','') 
	user_is_auth = request.session.get('user_is_auth',False) 
	# if settings.DEBUG: 
	if settings.ENV == "local" or settings.ENV == 'local1': 
		user_uuid = '123' 
		user_is_auth = True 
	if request.method!='GET': 
		return JsonResponse({"status":"error","error":"auth"}) 
 	try: 
		con = get_redis_connection("default") 
		samples = con.get('user_samples') 
		bt_samples = [] 
		if samples: 
			# samples = ujson.loads(samples) 
			samples = eval(samples) 
		for s in samples['samples']:
			try: 
				print('algo_uuid',s[0],'seg_sym',s[2]+'_'+s[1])
				backtest_sample = models.BacktestMeta.objects.get(algo_uuid=s[0],seg_sym=s[2]+'_'+s[1]) 
				bt_samples.append(backtest_sample['algo_obj']) 
			except: 
				print traceback.format_exc() 
		resp = JsonResponse({"status":"success","samples":bt_samples})
		resp["Access-Control-Allow-Credentials"] = "true" 
		resp["Access-Control-Allow-Origin"] = "*"  
		return resp
	except: 
		pass
	resp = JsonResponse({"status":"error","error":"unknown"}) 
	resp["Access-Control-Allow-Credentials"] = "true" 
	resp["Access-Control-Allow-Origin"] = "*" 
	return resp 

@override_with_ams
def cancel_order_click(request):
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
		headers = {}
		if settings.KITE_HEADER == True:
			headers = {"X-Kite-Version":"3"}
			auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
			headers["Authorization"] = "token {}".format(auth_header)
		if parent_order_id=='' or parent_order_id==order_id or variety.upper()=='REGULAR':
			response = requests.delete("https://api-partners.kite.trade/orders/regular/{}?api_key={}&access_token={}".format(order_id,settings.KITE_API_KEY,request.session.get('access_token','')),headers=headers)
		else:
			response = requests.delete("https://api-partners.kite.trade/orders/{}/{}?parent_order_id={}&api_key={}&access_token={}".format(variety.lower(),order_id,parent_order_id,settings.KITE_API_KEY,request.session.get('access_token','')),headers=headers)

		if response.status_code != 200:
			# print "https://api-partners.kite.trade/orders/regular/{}?api_key={}&access_token={}".format(order_id,settings.KITE_API_KEY,request.session.get('access_token',''))
			# print response
			# emit to user an alert to cancel the order if not cancelled automatically
			print('need to emit to use to manually cancel')
			return JsonResponse({"status":"success",'error':True,'msg':'Error occured, try again','error_msg':'Error occured, try again'})
		elif response.status_code == 200:
			response_json = json.loads(response.text)
			if response_json['status']=="success":
				return JsonResponse({"status":"success",'msg':'Order cancelled'})
			else:
				return JsonResponse({"status":"success",'error':True,'msg':'Error occured, try again','error_msg':'Error occured, try again'})
	except:
		print traceback.format_exc()
	return JsonResponse({"status":"error"})

def exit_bo_now_force_stop(request):
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
		headers = {}
		if settings.KITE_HEADER == True:
			headers = {"X-Kite-Version":"3"}
			auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
			headers["Authorization"] = "token {}".format(auth_header)
		if parent_order_id=='' or parent_order_id==order_id or variety.upper()=='REGULAR':
			response = requests.delete("https://api-partners.kite.trade/orders/regular/{}?api_key={}&access_token={}".format(order_id,settings.KITE_API_KEY,request.session.get('access_token','')),headers=headers)
		else:
			response = requests.delete("https://api-partners.kite.trade/orders/{}/{}?parent_order_id={}&api_key={}&access_token={}".format(variety.lower(),order_id,parent_order_id,settings.KITE_API_KEY,request.session.get('access_token','')),headers=headers)

		if response.status_code != 200:
			# print "https://api-partners.kite.trade/orders/regular/{}?api_key={}&access_token={}".format(order_id,settings.KITE_API_KEY,request.session.get('access_token',''))
			# print response
			# emit to user an alert to cancel the order if not cancelled automatically
			print('need to emit to use to manually cancel')
			return JsonResponse({"status":"error",'error':True,'msg':'Error occured, try again'+response.text,'error_msg':'Error occured, try again'})
		elif response.status_code == 200:
			response_json = json.loads(response.text)
			if response_json['status']=="success":
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

				deployment_uuid = request.POST.get('deployment_uuid','')

				if deployment_uuid == '':
					print 'deployment_uuid not present'
					return JsonResponse({"status":"error"})
				#update holdings for algorithm using webhook 
				# holding = HoldingsForAlgorithm.objects.get(user_uuid=user_uuid,deployment_uuid=deployment_uuid)
				# holding.position[segment+'_'+symbol]['qty']=
				con = get_redis_connection("default")
				pipeline = con.pipeline()

				keys = con.keys('deployed:'+user_uuid+':*:'+deployment_uuid)
				if len(keys)>0:
					redis_key = keys[0]
				else:
					redis_key = None

				try:
					if redis_key:
						# algo_obj = con.get(redis_key)
						# if algo_obj is not None:
						# 	try:
						# 		algo_obj = eval(algo_obj)
						# 		SL_placed = algo_obj.pop('SL_placed','')
						# 		SL_order_id = algo_obj.pop('SL_order_id','')
						# 		SL_order_api_key = algo_obj.pop('SL_order_api_key','')
						# 		SL_order_access_token = algo_obj.pop('SL_order_access_token','')
						# 		resp = requests.delete("https://api-partners.kite.trade/orders/regular/{}?api_key={}&access_token={}".format(SL_order_id,SL_order_api_key,SL_order_access_token),headers=headers)
						# 	except:
						# 		print traceback.format_exc()
						# else:
						# 	print(redis_key)
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
						deployment_key = con.keys(key_prefix_deployed)
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
								log_message="Strategy stopped by you"
								)
					deployed_algo.save()
					order_stop_log.save()
					pipeline.execute()
					return JsonResponse({'status':'success'})
				except:
					print traceback.format_exc()
					return JsonResponse({'status':'error'})
			else:
				return JsonResponse({"status":"success",'error':True,'msg':'Error occured, try again','error_msg':'Error occured, try again'})
	except:
		print traceback.format_exc()
	return JsonResponse({"status":"error"})

def get_pricing(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		return JsonResponse({"status":"success",'valid':True,'backtest':25,'deployments_remaining':5})
	if not user_is_auth:
		return JsonResponse({"status":"error","error-type":"auth","error_msg":"Session expired, re-login required"})

	available_plans = [
						{'daily_backtests': 50, 'subscription_tax': 0, 'subscription_plan': 'free', 'subscription_price': 0, 'plan_id': 0, 'subscription_validity_date': 7, 'daily_deploys': 5, 'subscription_total_price': 0, 'subscription_product': 'free','note':''},
						{'daily_backtests': 200, 'subscription_tax': 90, 'subscription_plan': 'basic', 'subscription_price': 500, 'plan_id': 1, 'subscription_validity_date': 30, 'daily_deploys': 25, 'subscription_total_price': 590, 'subscription_product': 'basic','note':''},
						{'daily_backtests': 500, 'subscription_tax': 162, 'subscription_plan': 'premium', 'subscription_price': 900, 'plan_id': 2, 'subscription_validity_date': 30, 'daily_deploys': 50, 'subscription_total_price': 1062, 'subscription_product': 'premium','note':''},
						{'daily_backtests': 1000, 'subscription_tax': 252, 'subscription_plan': 'ultimate', 'subscription_price': 1400, 'plan_id': 3, 'subscription_validity_date': 30, 'daily_deploys': 100, 'subscription_total_price': 1652, 'subscription_product': 'ultimate','note':'','time':'30 minutes'}
						]

	return JsonResponse({"status":"success","available_plans":available_plans})

def get_pricing2(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		return JsonResponse({"status":"success",'valid':True,'backtest':25,'deployments_remaining':5})
	if not user_is_auth:
		return JsonResponse({"status":"error","error-type":"auth","error_msg":"Session expired, re-login required"})

	available_plans = [
						{'daily_backtests': 50, 'subscription_tax': 0, 'subscription_plan': 'free', 'subscription_price': 0, 'plan_id': 0, 'subscription_validity_date': 7, 'daily_deploys': 5, 'subscription_total_price': 0, 'subscription_product': 'free','note':''},
						{'daily_backtests': 200, 'subscription_tax': 90, 'subscription_plan': 'basic', 'subscription_price': 500, 'plan_id': 1, 'subscription_validity_date': 30, 'daily_deploys': 25, 'subscription_total_price': 590, 'subscription_product': 'basic','note':''},
						{'daily_backtests': 500, 'subscription_tax': 162, 'subscription_plan': 'premium', 'subscription_price': 900, 'plan_id': 2, 'subscription_validity_date': 30, 'daily_deploys': 50, 'subscription_total_price': 1062, 'subscription_product': 'premium','note':''},
						{'daily_backtests': 1000, 'subscription_tax': 252, 'subscription_plan': 'ultimate', 'subscription_price': 1400, 'plan_id': 3, 'subscription_validity_date': 30, 'daily_deploys': 100, 'subscription_total_price': 1652, 'subscription_product': 'ultimate','note':'','time':'30 minutes','feature':[{'text':'Add upto 10 entry/exit conditions','value':'10'},{'text':'1000 Backtests per day','value':'1000'},{'text':'100 Live algos at a time','value':'100'}]}
						]

	return JsonResponse({"status":"success","available_plans":available_plans})

def get_pricing3(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		return JsonResponse({"status":"success",'valid':True,'backtest':25,'deployments_remaining':5})
	if not user_is_auth:
		return JsonResponse({"status":"error","error-type":"auth","error_msg":"Session expired, re-login required"})

	pricing = [
			{
			"subscription_period":"1 Month",
			"plan":
			[
				{
					"note":"",
					"subscription_period":"1",
					"subscription_tax": 90,
					"subscription_plan": "basic",
					"subscription_price": 500,
					"plan_id": 1,
					"subscription_validity_date": 30,
					"features": [
						{ "label": '<value> Backtests per day', "value": [200] },
						{ "label": '<value> Live strategies at a time', "value": [25] },
						{ "label": '<value> Scans per day', "value": [100] },
					],
					"exclusive":[
						{ "label": '', "value": ["Heikin-Ashi"] },
						{ "label": '<value> entry and exit conditions', "value": [5] }
					],
					"subscription_total_price": 590,
					"subscription_product": "basic"
				},
				{
					"note":"",
					"subscription_period":"1",
					"subscription_tax": 162,
					"subscription_plan": "premium",
					"subscription_price": 900,
					"plan_id": 2,
					"subscription_validity_date": 30,
					"features": [
						{ "label": '<value> Backtests per day', "value": [500] },
						{ "label": '<value> Live strategies at a time', "value": [50] },
						{ "label": '<value> Scans per day', "value": ["Unlimited"] },
					],
					"exclusive":[
						{ "label": '', "value": ["Heikin-Ashi"] },
						{ "label": '<value> entry and exit conditions', "value": [7] }
					],
					"subscription_total_price": 1062,
					"subscription_product": "premium"
				},
				{
					"note":"",
					"subscription_period":"1",
					"subscription_tax": 252,
					"subscription_plan": "ultimate",
					"subscription_price": 1400,
					"plan_id": 3,
					"subscription_validity_date": 30,
					"features": [
							{ "label": '<value> Backtests per day', "value": [1000] },
							{ "label": '<value> Live strategies at a time', "value": [100] },
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
						],
						"exclusive":[
							{ "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> entry and exit conditions', "value": [10] }
						],
					"subscription_total_price": 1652,
					"subscription_product": "ultimate"
				},
			]
			},
			{
				"subscription_period":"3 Months",
				"discount_percentage":10,
				"plan":
				[
					{
						"note":"",
						"subscription_period":"3",
						"subscription_tax": 90,
						"subscription_plan": "basic",
						"subscription_price": 500,
						"plan_id": 1,
						"subscription_validity_date": 90,
						"features": [
							{ "label": '<value> Backtests per day', "value": [200] },
							{ "label": '<value> Live strategies at a time', "value": [25] },
							{ "label": '<value> Scans per day', "value": [100] },
						],
						"exclusive":[
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '<value> entry and exit conditions', "value": [5] }
						],
						"subscription_total_price": 1593,
						"subscription_product": "basic"
					},
					{
						"note":"",
						"subscription_period":"3",
						"subscription_tax": 162,
						"subscription_plan": "premium",
						"subscription_price": 900,
						"plan_id": 2,
						"subscription_validity_date": 90,
						"features": [
							{ "label": '<value> Backtests per day', "value": [500] },
							{ "label": '<value> Live strategies at a time', "value": [50] },
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
						],
						"exclusive":[
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '<value> entry and exit conditions', "value": [7] }
						],
						"subscription_total_price": 1062,
						"subscription_product": "premium"
					},
					{
						"note":"",
						"subscription_period":"3",
						"subscription_tax": 252,
						"subscription_plan": "ultimate",
						"subscription_price": 1400,
						"plan_id": 3,
						"subscription_validity_date": 90,
						"features": [
							{ "label": '<value> Backtests per day', "value": [1000] },
							{ "label": '<value> Live strategies at a time', "value": [100] },
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
						],
						"exclusive":[
							{ "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> entry and exit conditions', "value": [10] }
						],
						"subscription_total_price": 1652,
						"subscription_product": "ultimate"
					},
				]
			},
			{
				"subscription_period":"6 Months",
				"discount_percentage":20,
				"plan":
				[
					{
						"note":"",
						"subscription_period":"6",
						"subscription_tax": 90,
						"subscription_plan": "basic",
						"subscription_price": 500,
						"plan_id": 1,
						"subscription_validity_date": 180,
						"features": [
							{ "label": '<value> Backtests per day', "value": [200] },
							{ "label": '<value> Live strategies at a time', "value": [25] },
							{ "label": '<value> Scans per day', "value": [100] },
						],
						"exclusive":[
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '<value> entry and exit conditions', "value": [5] }
						],
						"subscription_total_price": 590,
						"subscription_product": "basic"
					},
					{
						"note":"",
						"subscription_period":"6",
						"subscription_tax": 162,
						"subscription_plan": "premium",
						"subscription_price": 900,
						"plan_id": 2,
						"subscription_validity_date": 180,
						"features": [
							{ "label": '<value> Backtests per day', "value": [500] },
							{ "label": '<value> Live strategies at a time', "value": [50] },
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
						],
						"exclusive":[
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '<value> entry and exit conditions', "value": [7] }
						],
						"subscription_total_price": 1062,
						"subscription_product": "premium"
					},
					{
						"note":"",
						"subscription_period":"3",
						"subscription_tax": 252,
						"subscription_plan": "ultimate",
						"subscription_price": 1400,
						"plan_id": 3,
						"subscription_validity_date": 180,
						"features": [
							{ "label": '<value> Backtests per day', "value": [1000] },
							{ "label": '<value> Live strategies at a time', "value": [100] },
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
						],
						"exclusive":[
							{ "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> entry and exit conditions', "value": [10] }
						],
						"subscription_total_price": 1652,
						"subscription_product": "ultimate"
					},
				]
			},
			{
				"subscription_period":"12 Months",
				"discount_percentage":30,
				"plan":
				[
					{
						"note":"",
						"subscription_period":"6",
						"subscription_tax": 90,
						"subscription_plan": "basic",
						"subscription_price": 500,
						"plan_id": 1,
						"subscription_validity_date": 180,
						"features": [
							{ "label": '<value> Backtests per day', "value": [200] },
							{ "label": '<value> Live strategies at a time', "value": [25] },
							{ "label": '<value> Scans per day', "value": [100] },
						],
						"exclusive":[
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '<value> entry and exit conditions', "value": [5] }
						],
						"subscription_total_price": 590,
						"subscription_product": "basic"
					},
					{
						"note":"",
						"subscription_period":"6",
						"subscription_tax": 162,
						"subscription_plan": "premium",
						"subscription_price": 900,
						"plan_id": 2,
						"subscription_validity_date": 180,
						"features": [
							{ "label": '<value> Backtests per day', "value": [500] },
							{ "label": '<value> Live strategies at a time', "value": [50] },
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
						],
						"exclusive":[
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '<value> entry and exit conditions', "value": [7] }
						],
						"subscription_total_price": 1062,
						"subscription_product": "premium"
					},
					{
						"note":"",
						"subscription_period":"3",
						"subscription_tax": 252,
						"subscription_plan": "ultimate",
						"subscription_price": 1400,
						"plan_id": 3,
						"subscription_validity_date": 180,
						"features": [
							{ "label": '<value> Backtests per day', "value": [1000] },
							{ "label": '<value> Live strategies at a time', "value": [100] },
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
						],
						"exclusive":[
							{ "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> entry and exit conditions', "value": [10] }
						],
						"subscription_total_price": 1652,
						"subscription_product": "ultimate"
					},
				]
			}

		]

	return JsonResponse({"status":"success","pricing":pricing})

def get_pricing4_web(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		return JsonResponse({"status":"success",'valid':True,'backtest':50,'deployments_remaining':5})
	# if not user_is_auth:
	# 	return JsonResponse({"status":"error","error-type":"auth","error_msg":"Session expired, re-login required"})

	pricing = [
			{
			"subscription_period":"1 Month",
			"plan":
			[
				{
					"note":"",
					"subscription_period":"0",
					"subscription_tax": 0,
					"subscription_plan": "free",
					"subscription_price": 0,
					"plan_id": 0,
					"subscription_validity_date": 7,
					"features": [
						{ "label": '<value> Backtests per day', "value": [50] },
						{ "label": '<value> Live strategies at a time', "value": [5] },
						{ "label": '<value> Scans per day', "value": [50] },
					],
					"exclusive":[
						
					],
					"ultimate_feature":[
						# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
						{ "label": '', "value": ["Heikin-Ashi"] },
						{ "label": '', "value": ["Renko (In basic create)"] },
						{ "label": '', "value": ["MCX (Commodities)"] },
						{ "label": '', "value": ["Options (NFO-OPT)"] },
						{ "label": '', "value": ["Multi-time frame strategy"] },
						{ "label": '<value> Scans per day', "value": ["Unlimited"] }, 
						{ "label": '<value> entry and exit conditions', "value": [10] },
						{ "label": '<value>  handholding session', "value": ["1 hour"] }

					],
					"subscription_total_price": 0,
					"subscription_product": "free"
				},
				{
					"note":"",
					"subscription_period":"1",
					"subscription_tax": 90,
					"subscription_plan": "basic",
					"subscription_price": 500,
					"plan_id": 1,
					"subscription_validity_date": 30,
					"features": [
						{ "label": '<value> Backtests per day', "value": [200] },
						{ "label": '<value> Live strategies at a time', "value": [25] },
						{ "label": '<value> Scans per day', "value": [100] },
					],
					"exclusive":[
						{ "label": '', "value": ["Heikin-Ashi"] },
						{ "label": '<value> entry and exit conditions', "value": [5] }
					],
					"ultimate_feature":[
						# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
						{ "label": '', "value": ["Renko (In basic create)"] },
						{ "label": '', "value": ["MCX (Commodities)"] },
						{ "label": '', "value": ["Options (NFO-OPT)"] },
						{ "label": '', "value": ["Multi-time frame strategy"] }, 
						{ "label": '<value> Scans per day', "value": ["Unlimited"] },
						{ "label": '<value> entry and exit conditions', "value": [10] },
						{ "label": '<value>  handholding session', "value": ["1 hour"] }
					],
					"subscription_total_price": 590,
					"subscription_product": "basic"
				},
				{
					"note":"",
					"subscription_period":"1",
					"subscription_tax": 162,
					"subscription_plan": "premium",
					"subscription_price": 900,
					"plan_id": 2,
					"subscription_validity_date": 30,
					"features": [
						{ "label": '<value> Backtests per day', "value": [500] },
						{ "label": '<value> Live strategies at a time', "value": [50] },
						{ "label": '<value> Scans per day', "value": ["Unlimited"] },
					],
					"exclusive":[
						{ "label": '', "value": ["Heikin-Ashi"] },
						{ "label": '<value> entry and exit conditions', "value": [7] }
					],
					"ultimate_feature":[
						# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
						{ "label": '', "value": ["Renko (In basic create)"] },
						{ "label": '', "value": ["MCX (Commodities)"] },
						{ "label": '', "value": ["Options (NFO-OPT)"] },
						{ "label": '', "value": ["Multi-time frame strategy"] }, 
						{ "label": '<value> entry and exit conditions', "value": [10] },
						{ "label": '<value>  handholding session', "value": ["1 hour"] }
					],
					"subscription_total_price": 1062,
					"subscription_product": "premium"
				},
				{
					"note":"",
					"subscription_period":"1",
					"subscription_tax": 252,
					"subscription_plan": "ultimate",
					"subscription_price": 1400,
					"plan_id": 3,
					"subscription_validity_date": 30,
					"features": [
							{ "label": '<value> Backtests per day', "value": [1000] },
							{ "label": '<value> Live strategies at a time', "value": [100] },
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
					],
					"exclusive":[
						# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
						{ "label": '', "value": ["Heikin-Ashi"] },
						{ "label": '', "value": ["Renko (In basic create)"] },
						{ "label": '', "value": ["MCX (Commodities)"] },
						{ "label": '', "value": ["Options (NFO-OPT)"] },
						{ "label": '', "value": ["Multi-time frame strategy"] }, 
						{ "label": '<value> entry and exit conditions', "value": [10] },
						],
					"ultimate_feature":[
						{ "label": '<value>  handholding session', "value": ["1 hour"] }
					],
					"subscription_total_price": 1652,
					"subscription_product": "ultimate"
				},
			]
			},
			{
				"subscription_period":"3 Months",
				"discount_percentage":10,
				"plan":
				[
					{
						"note":"",
						"subscription_period":"0",
						"subscription_tax": 0,
						"subscription_plan": "free",
						"subscription_price": 0,
						"plan_id": 0,
						"subscription_validity_date": 7,
						"features": [
							{ "label": '<value> Backtests per day', "value": [50] },
							{ "label": '<value> Live strategies at a time', "value": [5] },
							{ "label": '<value> Scans per day', "value": [50] },
						],
						"exclusive":[
							
						],
						"ultimate_feature":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
							{ "label": '<value> entry and exit conditions', "value": [10] },
							{ "label": '<value>  handholding session', "value": ["1 hour"] }

						],
						"subscription_total_price": 0,
						"subscription_product": "free"
					},
					{
						"note":"",
						"subscription_period":"3",
						"subscription_tax": 90,
						"subscription_plan": "basic",
						"subscription_price": 500,
						"plan_id": 1,
						"subscription_validity_date": 90,
						"features": [
							{ "label": '<value> Backtests per day', "value": [200] },
							{ "label": '<value> Live strategies at a time', "value": [25] },
							{ "label": '<value> Scans per day', "value": [100] },
						],
						"exclusive":[
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '<value> entry and exit conditions', "value": [5] }
						],
						"ultimate_feature":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
							{ "label": '<value> entry and exit conditions', "value": [10] },
							{ "label": '<value>  handholding session', "value": ["1 hour"] }

						],
						"subscription_total_price": 1593,
						"subscription_product": "basic"
					},
					{
						"note":"",
						"subscription_period":"3",
						"subscription_tax": 162,
						"subscription_plan": "premium",
						"subscription_price": 900,
						"plan_id": 2,
						"subscription_validity_date": 90,
						"features": [
							{ "label": '<value> Backtests per day', "value": [500] },
							{ "label": '<value> Live strategies at a time', "value": [50] },
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
						],
						"exclusive":[
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '<value> entry and exit conditions', "value": [7] }
						],
						"ultimate_feature":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> entry and exit conditions', "value": [10] },
							{ "label": '<value>  handholding session', "value": ["1 hour"] }
						],
						"subscription_total_price": 1062,
						"subscription_product": "premium"
					},
					{
						"note":"",
						"subscription_period":"3",
						"subscription_tax": 252,
						"subscription_plan": "ultimate",
						"subscription_price": 1400,
						"plan_id": 3,
						"subscription_validity_date": 90,
						"features": [
							{ "label": '<value> Backtests per day', "value": [1000] },
							{ "label": '<value> Live strategies at a time', "value": [100] },
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
						],
						"exclusive":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> entry and exit conditions', "value": [10] }
						],
						"ultimate_feature":[
							{ "label": '<value>  handholding session', "value": ["1 hour"] }
						],
						"subscription_total_price": 1652,
						"subscription_product": "ultimate"
					},
				]
			},
			{
				"subscription_period":"6 Months",
				"discount_percentage":20,
				"plan":
				[

					{
						"note":"",
						"subscription_period":"0",
						"subscription_tax": 0,
						"subscription_plan": "free",
						"subscription_price": 0,
						"plan_id": 0,
						"subscription_validity_date": 7,
						"features": [
							{ "label": '<value> Backtests per day', "value": [50] },
							{ "label": '<value> Live strategies at a time', "value": [5] },
							{ "label": '<value> Scans per day', "value": [50] },
						],
						"exclusive":[
							
						],
						"ultimate_feature":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
							{ "label": '<value> entry and exit conditions', "value": [10]},
							{ "label": '<value>  handholding session', "value": ["1 hour"] } 
						],
						"subscription_total_price": 0,
						"subscription_product": "free"
					},
					{
						"note":"",
						"subscription_period":"6",
						"subscription_tax": 90,
						"subscription_plan": "basic",
						"subscription_price": 500,
						"plan_id": 1,
						"subscription_validity_date": 180,
						"features": [
							{ "label": '<value> Backtests per day', "value": [200] },
							{ "label": '<value> Live strategies at a time', "value": [25] },
							{ "label": '<value> Scans per day', "value": [100] },
						],
						"exclusive":[
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '<value> entry and exit conditions', "value": [5] }
						],
						"ultimate_feature":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
							{ "label": '<value> entry and exit conditions', "value": [10] },
							{ "label": '<value>  handholding session', "value": ["1 hour"] }
						],
						"subscription_total_price": 590,
						"subscription_product": "basic"
					},
					{
						"note":"",
						"subscription_period":"6",
						"subscription_tax": 162,
						"subscription_plan": "premium",
						"subscription_price": 900,
						"plan_id": 2,
						"subscription_validity_date": 180,
						"features": [
							{ "label": '<value> Backtests per day', "value": [500] },
							{ "label": '<value> Live strategies at a time', "value": [50] },
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
						],
						"exclusive":[
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '<value> entry and exit conditions', "value": [7] }
						],
						"ultimate_feature":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> entry and exit conditions', "value": [10] },
							{ "label": '<value>  handholding session', "value": ["1 hour"] }
						],
						"subscription_total_price": 1062,
						"subscription_product": "premium"
					},
					{
						"note":"",
						"subscription_period":"6",
						"subscription_tax": 252,
						"subscription_plan": "ultimate",
						"subscription_price": 1400,
						"plan_id": 3,
						"subscription_validity_date": 180,
						"features": [
							{ "label": '<value> Backtests per day', "value": [1000] },
							{ "label": '<value> Live strategies at a time', "value": [100] },
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
						],
						"exclusive":[
							{ "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> entry and exit conditions', "value": [10] }
						],
						"ultimate_feature":[
							{ "label": '<value>  handholding session', "value": ["1 hour"] }
						],
						"subscription_total_price": 1652,
						"subscription_product": "ultimate"
					},
				]
			},
			{
				"subscription_period":"12 Months",
				"discount_percentage":30,
				"plan":
				[
					{
						"note":"",
						"subscription_period":"0",
						"subscription_tax": 0,
						"subscription_plan": "free",
						"subscription_price": 0,
						"plan_id": 0,
						"subscription_validity_date": 7,
						"features": [
							{ "label": '<value> Backtests per day', "value": [50] },
							{ "label": '<value> Live strategies at a time', "value": [5] },
							{ "label": '<value> Scans per day', "value": [50] },
						],
						"exclusive":[
							
						],
						"ultimate_feature":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
							{ "label": '<value> entry and exit conditions', "value": [10] },
							{ "label": '<value>  handholding session', "value": ["1 hour"] }
						],
						"subscription_total_price": 0,
						"subscription_product": "free"
					},
					{
						"note":"",
						"subscription_period":"12",
						"subscription_tax": 90,
						"subscription_plan": "basic",
						"subscription_price": 500,
						"plan_id": 1,
						"subscription_validity_date": 365,
						"features": [
							{ "label": '<value> Backtests per day', "value": [200] },
							{ "label": '<value> Live strategies at a time', "value": [25] },
							{ "label": '<value> Scans per day', "value": [100] },
						],
						"exclusive":[
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '<value> entry and exit conditions', "value": [5] },
						],
						"ultimate_feature":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
							{ "label": '<value> entry and exit conditions', "value": [10] },
							{ "label": '<value>  handholding session', "value": ["1 hour"] }
						],
						"subscription_total_price": 590,
						"subscription_product": "basic"
					},
					{
						"note":"",
						"subscription_period":"12",
						"subscription_tax": 162,
						"subscription_plan": "premium",
						"subscription_price": 900,
						"plan_id": 2,
						"subscription_validity_date": 365,
						"features": [
							{ "label": '<value> Backtests per day', "value": [500] },
							{ "label": '<value> Live strategies at a time', "value": [50] },
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
						],
						"exclusive":[
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '<value> entry and exit conditions', "value": [7] },
							{ "label": '<value>  handholding session', "value": ["1 hour"] }
						],
						"ultimate_feature":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> entry and exit conditions', "value": [10] }
						],
						"subscription_total_price": 1062,
						"subscription_product": "premium"
					},
					{
						"note":"",
						"subscription_period":"12",
						"subscription_tax": 252,
						"subscription_plan": "ultimate",
						"subscription_price": 1400,
						"plan_id": 3,
						"subscription_validity_date": 365,
						"features": [
							{ "label": '<value> entry and exit conditions', "value": [10] },
							{ "label": '<value> Backtests per day', "value": [1000] },
							{ "label": '<value> Live strategies at a time', "value": [100] },
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
						],
						"exclusive":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value>  handholding session', "value": ["1 hour"] }
						],
						"ultimate_feature":[
						],
						"subscription_total_price": 1652,
						"subscription_product": "ultimate"
					},
				]
			}
		]
	if request.GET.get("broker","").lower() in ["5paisa","ab"]:
		pricing = pricing[1:]
	return JsonResponse({"status":"success","pricing":pricing})

def get_pricing4(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		return JsonResponse({"status":"success",'valid':True,'backtest':50,'deployments_remaining':5})
	# if not user_is_auth:
	# 	return JsonResponse({"status":"error","error-type":"auth","error_msg":"Session expired, re-login required"})

	pricing = [
			{
			"subscription_period":"1 Month",
			"plan":
			[
				{
					"note":"",
					"subscription_period":"0",
					"subscription_tax": 0,
					"subscription_plan": "free",
					"subscription_price": 0,
					"plan_id": 0,
					"subscription_validity_date": 7,
					"features": [
						{ "label": '<value> Backtests per day', "value": [50] },
						{ "label": '<value> Live strategies at a time', "value": [5] },
						{ "label": '<value> Scans per day', "value": [50] },
					],
					"exclusive":[
						
					],
					"ultimate_feature":[
						# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
						{ "label": '', "value": ["Heikin-Ashi"] },
						{ "label": '', "value": ["Renko (In basic create)"] },
						{ "label": '', "value": ["MCX (Commodities)"] },
						{ "label": '', "value": ["Options (NFO-OPT)"] },
						{ "label": '', "value": ["Multi-time frame strategy"] },
						{ "label": '<value> Scans per day', "value": ["Unlimited"] }, 
						{ "label": '<value> entry and exit conditions', "value": [10] },
						{ "label": '<value>  handholding session', "value": ["1 hour"] }

					],
					"subscription_total_price": 0,
					"subscription_product": "free"
				},
				{
					"note":"",
					"subscription_period":"1",
					"subscription_tax": 90,
					"subscription_plan": "basic",
					"subscription_price": 500,
					"plan_id": 1,
					"subscription_validity_date": 30,
					"features": [
						{ "label": '<value> Backtests per day', "value": [200] },
						{ "label": '<value> Live strategies at a time', "value": [25] },
						{ "label": '<value> Scans per day', "value": [100] },
					],
					"exclusive":[
						{ "label": '', "value": ["Heikin-Ashi"] },
						{ "label": '<value> entry and exit conditions', "value": [5] }
					],
					"ultimate_feature":[
						# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
						{ "label": '', "value": ["Renko (In basic create)"] },
						{ "label": '', "value": ["MCX (Commodities)"] },
						{ "label": '', "value": ["Options (NFO-OPT)"] },
						{ "label": '', "value": ["Multi-time frame strategy"] }, 
						{ "label": '<value> Scans per day', "value": ["Unlimited"] },
						{ "label": '<value> entry and exit conditions', "value": [10] },
						{ "label": '<value>  handholding session', "value": ["1 hour"] }
					],
					"subscription_total_price": 590,
					"subscription_product": "basic"
				},
				{
					"note":"",
					"subscription_period":"1",
					"subscription_tax": 162,
					"subscription_plan": "premium",
					"subscription_price": 900,
					"plan_id": 2,
					"subscription_validity_date": 30,
					"features": [
						{ "label": '<value> Backtests per day', "value": [500] },
						{ "label": '<value> Live strategies at a time', "value": [50] },
						{ "label": '<value> Scans per day', "value": ["Unlimited"] },
					],
					"exclusive":[
						{ "label": '', "value": ["Heikin-Ashi"] },
						{ "label": '<value> entry and exit conditions', "value": [7] }
					],
					"ultimate_feature":[
						# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
						{ "label": '', "value": ["Renko (In basic create)"] },
						{ "label": '', "value": ["MCX (Commodities)"] },
						{ "label": '', "value": ["Options (NFO-OPT)"] },
						{ "label": '', "value": ["Multi-time frame strategy"] }, 
						{ "label": '<value> entry and exit conditions', "value": [10] },
						{ "label": '<value>  handholding session', "value": ["1 hour"] }
					],
					"subscription_total_price": 1062,
					"subscription_product": "premium"
				},
				{
					"note":"",
					"subscription_period":"1",
					"subscription_tax": 252,
					"subscription_plan": "ultimate",
					"subscription_price": 1400,
					"plan_id": 3,
					"subscription_validity_date": 30,
					"features": [
							{ "label": '<value> Backtests per day', "value": [1000] },
							{ "label": '<value> Live strategies at a time', "value": [100] },
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
					],
					"exclusive":[
						# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
						{ "label": '', "value": ["Heikin-Ashi"] },
						{ "label": '', "value": ["Renko (In basic create)"] },
						{ "label": '', "value": ["MCX (Commodities)"] },
						{ "label": '', "value": ["Options (NFO-OPT)"] },
						{ "label": '', "value": ["Multi-time frame strategy"] }, 
						{ "label": '<value> entry and exit conditions', "value": [10] },
						],
					"ultimate_feature":[
						{ "label": '<value>  handholding session', "value": ["1 hour"] }
					],
					"subscription_total_price": 1652,
					"subscription_product": "ultimate"
				},
			]
			},
			{
				"subscription_period":"3 Months",
				"discount_percentage":10,
				"plan":
				[
					{
						"note":"",
						"subscription_period":"0",
						"subscription_tax": 0,
						"subscription_plan": "free",
						"subscription_price": 0,
						"plan_id": 0,
						"subscription_validity_date": 7,
						"features": [
							{ "label": '<value> Backtests per day', "value": [50] },
							{ "label": '<value> Live strategies at a time', "value": [5] },
							{ "label": '<value> Scans per day', "value": [50] },
						],
						"exclusive":[
							
						],
						"ultimate_feature":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
							{ "label": '<value> entry and exit conditions', "value": [10] },
							{ "label": '<value>  handholding session', "value": ["1 hour"] }

						],
						"subscription_total_price": 0,
						"subscription_product": "free"
					},
					{
						"product_id":"basic_quaterly",
						"note":"",
						"subscription_period":"3",
						"subscription_tax": 90,
						"subscription_plan": "basic",
						"subscription_price": 500,
						"plan_id": 1,
						"subscription_validity_date": 90,
						"features": [
							{ "label": '<value> Backtests per day', "value": [200] },
							{ "label": '<value> Live strategies at a time', "value": [25] },
							{ "label": '<value> Scans per day', "value": [100] },
						],
						"exclusive":[
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '<value> entry and exit conditions', "value": [5] }
						],
						"ultimate_feature":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
							{ "label": '<value> entry and exit conditions', "value": [10] },
							{ "label": '<value>  handholding session', "value": ["1 hour"] }

						],
						"subscription_total_price": 1593,
						"subscription_product": "basic"
					},
					{
						"product_id":"premium",
						"note":"",
						"subscription_period":"3",
						"subscription_tax": 162,
						"subscription_plan": "premium",
						"subscription_price": 900,
						"plan_id": 2,
						"subscription_validity_date": 90,
						"features": [
							{ "label": '<value> Backtests per day', "value": [500] },
							{ "label": '<value> Live strategies at a time', "value": [50] },
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
						],
						"exclusive":[
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '<value> entry and exit conditions', "value": [7] }
						],
						"ultimate_feature":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> entry and exit conditions', "value": [10] },
							{ "label": '<value>  handholding session', "value": ["1 hour"] }
						],
						"subscription_total_price": 1062,
						"subscription_product": "premium"
					},
					{
						"product_id":"basic",
						"note":"",
						"subscription_period":"3",
						"subscription_tax": 252,
						"subscription_plan": "ultimate",
						"subscription_price": 1400,
						"plan_id": 3,
						"subscription_validity_date": 90,
						"features": [
							{ "label": '<value> Backtests per day', "value": [1000] },
							{ "label": '<value> Live strategies at a time', "value": [100] },
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
						],
						"exclusive":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> entry and exit conditions', "value": [10] }
						],
						"ultimate_feature":[
							{ "label": '<value>  handholding session', "value": ["1 hour"] }
						],
						"subscription_total_price": 1652,
						"subscription_product": "ultimate"
					},
				]
			},
			{
				"subscription_period":"6 Months",
				"discount_percentage":20,
				"plan":
				[

					{
						"note":"",
						"subscription_period":"0",
						"subscription_tax": 0,
						"subscription_plan": "free",
						"subscription_price": 0,
						"plan_id": 0,
						"subscription_validity_date": 7,
						"features": [
							{ "label": '<value> Backtests per day', "value": [50] },
							{ "label": '<value> Live strategies at a time', "value": [5] },
							{ "label": '<value> Scans per day', "value": [50] },
						],
						"exclusive":[
							
						],
						"ultimate_feature":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
							{ "label": '<value> entry and exit conditions', "value": [10]},
							{ "label": '<value>  handholding session', "value": ["1 hour"] } 
						],
						"subscription_total_price": 0,
						"subscription_product": "free"
					},
					{
						"product_id":"basic_biyearly",
						"note":"",
						"subscription_period":"6",
						"subscription_tax": 90,
						"subscription_plan": "basic",
						"subscription_price": 500,
						"plan_id": 1,
						"subscription_validity_date": 180,
						"features": [
							{ "label": '<value> Backtests per day', "value": [200] },
							{ "label": '<value> Live strategies at a time', "value": [25] },
							{ "label": '<value> Scans per day', "value": [100] },
						],
						"exclusive":[
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '<value> entry and exit conditions', "value": [5] }
						],
						"ultimate_feature":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
							{ "label": '<value> entry and exit conditions', "value": [10] },
							{ "label": '<value>  handholding session', "value": ["1 hour"] }
						],
						"subscription_total_price": 590,
						"subscription_product": "basic"
					},
					{
						"product_id":"premium_biyearly",
						"note":"",
						"subscription_period":"6",
						"subscription_tax": 162,
						"subscription_plan": "premium",
						"subscription_price": 900,
						"plan_id": 2,
						"subscription_validity_date": 180,
						"features": [
							{ "label": '<value> Backtests per day', "value": [500] },
							{ "label": '<value> Live strategies at a time', "value": [50] },
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
						],
						"exclusive":[
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '<value> entry and exit conditions', "value": [7] }
						],
						"ultimate_feature":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> entry and exit conditions', "value": [10] },
							{ "label": '<value>  handholding session', "value": ["1 hour"] }
						],
						"subscription_total_price": 1062,
						"subscription_product": "premium"
					},
					{
						"product_id":"ultimate_biyearly",
						"note":"",
						"subscription_period":"6",
						"subscription_tax": 252,
						"subscription_plan": "ultimate",
						"subscription_price": 1400,
						"plan_id": 3,
						"subscription_validity_date": 180,
						"features": [
							{ "label": '<value> Backtests per day', "value": [1000] },
							{ "label": '<value> Live strategies at a time', "value": [100] },
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
						],
						"exclusive":[
							{ "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> entry and exit conditions', "value": [10] }
						],
						"ultimate_feature":[
							{ "label": '<value>  handholding session', "value": ["1 hour"] }
						],
						"subscription_total_price": 1652,
						"subscription_product": "ultimate"
					},
				]
			},
			{
				"subscription_period":"12 Months",
				"discount_percentage":30,
				"plan":
				[
					{
						"note":"",
						"subscription_period":"0",
						"subscription_tax": 0,
						"subscription_plan": "free",
						"subscription_price": 0,
						"plan_id": 0,
						"subscription_validity_date": 7,
						"features": [
							{ "label": '<value> Backtests per day', "value": [50] },
							{ "label": '<value> Live strategies at a time', "value": [5] },
							{ "label": '<value> Scans per day', "value": [50] },
						],
						"exclusive":[
							
						],
						"ultimate_feature":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
							{ "label": '<value> entry and exit conditions', "value": [10] },
							{ "label": '<value>  handholding session', "value": ["1 hour"] }
						],
						"subscription_total_price": 0,
						"subscription_product": "free"
					},
					{
						"product_id":"basic_annual",
						"note":"",
						"subscription_period":"12",
						"subscription_tax": 90,
						"subscription_plan": "basic",
						"subscription_price": 500,
						"plan_id": 1,
						"subscription_validity_date": 365,
						"features": [
							{ "label": '<value> Backtests per day', "value": [200] },
							{ "label": '<value> Live strategies at a time', "value": [25] },
							{ "label": '<value> Scans per day', "value": [100] },
						],
						"exclusive":[
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '<value> entry and exit conditions', "value": [5] }
						],
						"ultimate_feature":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
							{ "label": '<value> entry and exit conditions', "value": [10] },
							{ "label": '<value>  handholding session', "value": ["1 hour"] }
						],
						"subscription_total_price": 590,
						"subscription_product": "basic"
					},
					{
						"product_id":"premium_annual",
						"note":"",
						"subscription_period":"12",
						"subscription_tax": 162,
						"subscription_plan": "premium",
						"subscription_price": 900,
						"plan_id": 2,
						"subscription_validity_date": 365,
						"features": [
							{ "label": '<value> Backtests per day', "value": [500] },
							{ "label": '<value> Live strategies at a time', "value": [50] },
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
						],
						"exclusive":[
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '<value> entry and exit conditions', "value": [7] },
							{ "label": '<value>  handholding session', "value": ["1 hour"] }
						],
						"ultimate_feature":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> entry and exit conditions', "value": [10] }
						],
						"subscription_total_price": 1062,
						"subscription_product": "premium"
					},
					{
						"product_id":"ultimate_annual",
						"note":"",
						"subscription_period":"12",
						"subscription_tax": 252,
						"subscription_plan": "ultimate",
						"subscription_price": 1400,
						"plan_id": 3,
						"subscription_validity_date": 365,
						"features": [
							{ "label": '<value> Backtests per day', "value": [1000] },
							{ "label": '<value> Live strategies at a time', "value": [100] },
							{ "label": '<value> Scans per day', "value": ["Unlimited"] },
						],
						"exclusive":[
							# { "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] },
							{ "label": '', "value": ["Heikin-Ashi"] },
							{ "label": '', "value": ["Renko (In basic create)"] },
							{ "label": '', "value": ["MCX (Commodities)"] },
							{ "label": '', "value": ["Options (NFO-OPT)"] },
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> entry and exit conditions', "value": [10] },
							{ "label": '<value>  handholding session', "value": ["1 hour"] }
						],
						"ultimate_feature":[
						],
						"subscription_total_price": 1652,
						"subscription_product": "ultimate"
					},
				]
			}

		]

	return JsonResponse({"status":"success","pricing":pricing})

def cancel_subscription(request):
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
		user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
		# if user_subscription.subscription_payment_method=='razorpay':
		try:
			usp = models.UserSubscriptionPayment.objects.get(user_uuid=user_uuid,payment_uuid=user_subscription.payment_uuid)
			response = payments.stop_subscription_razorpay(usp.payment_data['id'])
		except razorpay.errors.BadRequestError:
			print traceback.format_exc()
		except models.UserSubscriptionPayment.DoesNotExist:
			print traceback.format_exc()
			# return JsonResponse({"status":"error","error_msg":"No valid subscription found"})
		user_subscription.subscription_active = False
		user_subscription.save()
		subscription_status_changed(user_uuid=user_uuid,
			user_broker_id=user_subscription.user_broker_id,
			change_type='stopped for '+user_subscription.subscription_plan+' with validity till '+str(user_subscription.subscription_validity),action='stopped',plan=user_subscription.subscription_plan,email=request.session.get('user_email',''))
		return JsonResponse({"status":"success",'valid':True,'msg':'Your subscription has been canceled, but you can continue using the services till the current subscription is valid!'})
	except:
		print traceback.format_exc()
	return JsonResponse({"status":"error"})

def update_usage(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	# if not user_is_auth:
	# 	return JsonResponse({"status":"error"})

	if request.method=='POST':
		usage = {'backtest':0,'deployed':0}
		usage_type = request.POST.get('usage','')
		if user_uuid == '' and user_uuid not in request.POST.keys():
			return JsonResponse({"status":"error"}) 
		elif user_uuid == '':
			user_uuid = request.POST.get('user_uuid','')
		# print 'usage_type',usage_type
		if usage_type=='':
			return JsonResponse({})

		return JsonResponse(update_usage_util(user_uuid,usage_type))

	return JsonResponse({})

def update_usage_util(user_uuid,usage_type,clear=False):
	con = get_redis_connection("default")
	#user_uuid : {'deployed':0,'backtest':0}
	if clear:
		con.delete('daily_usage:'+user_uuid)
		return {'status':'success'}

	usage = con.get('daily_usage:'+user_uuid)
	if usage != None:
		usage = eval(usage)
	else:
		usage = {'backtest':0,'deployed':0}

	if usage_type in usage.keys():
		usage[usage_type]+=1

	ex_date = datetime.datetime.today()# + datetime.timedelta(days=int(1))
	ex_date = ex_date.replace(hour=23,minute=59,second=59)
	expiration_sec = int(float(ex_date.strftime('%s'))-float(datetime.datetime.now().strftime('%s')))
	con.set('daily_usage:'+user_uuid,ujson.dumps(usage))
	con.expire('daily_usage:'+user_uuid,expiration_sec)
	return {'status':'success'}

def update_usage_util_count(user_uuid,usage_type,count=0,clear=False):
	con = get_redis_connection("default")
	#user_uuid : {'deployed':0,'backtest':0}
	if clear:
		con.delete('daily_usage:'+user_uuid)
		return {'status':'success'}

	usage = con.get('daily_usage:'+user_uuid)
	if usage != None:
		usage = eval(usage)
	else:
		usage = {'backtest':0,'deployed':0}

	if usage_type in usage.keys():
		usage[usage_type]+=count
	else:
		usage[usage_type]=count
		
	ex_date = datetime.datetime.today()# + datetime.timedelta(days=int(1))
	ex_date = ex_date.replace(hour=23,minute=59,second=59)
	expiration_sec = int(float(ex_date.strftime('%s'))-float(datetime.datetime.now().strftime('%s')))
	con.set('daily_usage:'+user_uuid,ujson.dumps(usage))
	con.expire('daily_usage:'+user_uuid,expiration_sec)
	return {'status':'success'}

def generate_shareable_link(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	# if not user_is_auth:
	# 	return JsonResponse({"status":"error"})

	if request.method=='POST':
		algo_uuid = request.POST.get('algo_uuid','')
		if not user_is_auth:
			# and (algo_uuid!='' or algo_subscription_uuid!=''):
			return JsonResponse({"status":"error","error_msg":"auth"})
		algo_subscription_uuid = request.POST.get('algo_subscription_uuid','')
		publishing_uuid = request.POST.get('publishing_uuid','')
		seg_sym = request.POST.get('seg_sym','')
		public = request.POST.get('public','')
		try:
			if algo_uuid!="":
				bt = models.Backtest.objects.get(user_uuid=user_uuid,algo_uuid=algo_uuid,seg_sym=seg_sym)
				backtest_share_uuid = str(uuid.uuid4())
				algo_obj = bt.algo_obj
				# if public=="":
				# 	algo_obj['action_str'] = ''
				# 	algo_obj['action_str_exit'] = ''
				bt_share = models.ShareableBacktest(
					backtest_share_uuid=backtest_share_uuid,
					user_uuid = bt.user_uuid,
					algo_uuid = bt.algo_uuid,
					seg_sym = bt.seg_sym,
					backtest_result = bt.backtest_result,
					algo_obj = algo_obj,
					runtime = bt.runtime,
					public = public
					)
				bt_share.save()
			elif publishing_uuid !="":
				backtest_share_uuid = ""
				bt = models.PublishedBacktests.objects.get(publishing_uuid=publishing_uuid,seg_sym=seg_sym)
				backtest_share_uuid = str(uuid.uuid4())
				bt_share = models.ShareableBacktest(
					backtest_share_uuid=backtest_share_uuid,
					user_uuid = bt.user_uuid,
					algo_uuid = bt.algo_uuid,
					seg_sym = bt.seg_sym,
					backtest_result = bt.backtest_result,
					algo_obj = bt.algo_obj,
					runtime = bt.runtime
					)
				bt_share.save()
				pass
			elif algo_subscription_uuid !="":
				pass
				backtest_share_uuid=""
				bt = models.SubscribeAlgoBacktest.objects.get(algo_subscription_uuid=algo_subscription_uuid,user_uuid=user_uuid,seg_sym=seg_sym)
				backtest_share_uuid = str(uuid.uuid4())
				bt_share = models.ShareableBacktest(
					backtest_share_uuid=backtest_share_uuid,
					user_uuid = bt.user_uuid,
					algo_uuid = bt.algo_uuid,
					seg_sym = bt.seg_sym,
					backtest_result = bt.backtest_result,
					algo_obj = bt.algo_obj,
					runtime = bt.runtime
					)
				bt_share.save()
			return JsonResponse({'status':'success','sharable_link':'?sbt='+backtest_share_uuid,"backtest_share_uuid":backtest_share_uuid})
		except:
			print traceback.format_exc()
			return JsonResponse({"status":"error","error_msg":"Unexpected error, please try again"})
	return JsonResponse({})


def show_order_details(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error","error_msg":"User auth"})

	if request.method=='GET':
		try:
			order_id = request.GET.get('order_id','')
			resp = models.BrokerOrder.objects.get(order_id=order_id)
			return JsonResponse({"status":"success","order":ujson.loads(resp.to_json())})
		except:
			print traceback.format_exc()
			return JsonResponse({"status":"error","error":"Order ID not found","error_msg":"Order ID not found"})
	return JsonResponse({})		

def index(request):
	# print request.session.get('blocked_login',False)
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)

	if request.method == 'GET':
		fivepaisacookie = request.COOKIES.get('5paisacookie',"") 
		JwtToken = request.COOKIES.get('JwtToken',"") 
		extraParams = ""
		allGetParams = ""
		for i in request.GET.items():
			i = list(i)
			if i[0]=="vid":
				i[1]=i[1]+"-auth"
			allGetParams += "=".join(i)+"&"

		if JwtToken!="" and fivepaisacookie!="":
			extraParams = "5paisacookie="+fivepaisacookie+"&JwtToken="+JwtToken
		print("h->>>>",JwtToken,fivepaisacookie,"https://streak.5paisa.com/create_session?"+allGetParams+extraParams)
		return redirect("https://streak.5paisa.com/create_session?"+allGetParams+extraParams)

	partner_ref = request.GET.get('ref',None)
	if partner_ref and request.META.get('HTTP_HOST','')!='streak.zerodha.com':
		url_is_safe = is_safe_url('https://streak.zerodha.com/?ref='+partner_ref)
		return redirect('https://streak.zerodha.com/?ref='+partner_ref)
	elif partner_ref and request.META.get('HTTP_HOST','')=='streak.zerodha.com':
	# elif partner_ref:
		request.session['partner_ref'] = partner_ref
	if user_is_auth and user_uuid!='':
		# if request.session.get('app-api','')=='true':
		# 	# print request.COOKIES
		# 	return JsonResponse({"auth_token":request.META.get("HTTP_COOKIE","")})	

		# print dir(request.zz)
		if request.session.pop('redirect','')=='popup':
			# return render(request,'home_temp.html',{'popup':True})	
			return redirect('home')

		if request.session.get('mobile_app','')=='true':
			print 'logging'
			return redirect('mobile_alerts')
		return redirect('dashboard')
	blocked_login = request.session.pop('blocked_login',False)
	return redirect("https://streak.tech")
	# return render(request,'index.html',{'blocked_login':blocked_login})

def first_login_complete(request):
	if request.method == 'POST':
		if request.session['session_secret'] == request.POST.get('session_secret'):
			if request.POST.get('first_time','') == 'first_time_skip':
				request.session.pop('first_time_login','')
				request.session.pop('first_time_algos','')
				request.session.pop('first_time_dashboard','')
				request.session.pop('first_time_create_algorithm','')
				request.session.pop('first_time_backtest','')
				request.session.pop('first_time_deploy','')
				request.session.pop('first_time_orderbook','')
				request.session.pop('first_time_portfolio','')
			else:
				request.session.pop(request.POST.get('first_time',''),'')
			# request.session.pop('session_secret')
		return JsonResponse({'status':'success'})		
	return JsonResponse({'status':'error'})

def encode_vig_cipher(key, clear):
	enc = []
	for i in range(len(clear)):
		key_c = key[i % len(key)]
		enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
		enc.append(enc_c)
	return base64.urlsafe_b64encode("".join(enc))

def decode_vig_cipher(key, enc):
	dec = []
	enc = base64.urlsafe_b64decode(enc)
	for i in range(len(enc)):
		key_c = key[i % len(key)]
		dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
		dec.append(dec_c)
	return "".join(dec)

def mobile_alerts(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	if user_uuid=='' or not user_is_auth:
		return redirect('mobile_landing')
	if request.method == 'GET':
		notification_uuid = request.GET.get('notification_uuid','')
		user_broker_id_e = request.GET.get('u','')
		user_broker_id = decode_vig_cipher(settings.KITE_API_SECRET,user_broker_id_e)
		return render(request,'mobile_alert.html',{})
	return redirect('mobile_landing')

@override_with_ams
def exit_all(request):
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
		product = request.POST.get('product','')
		validity = request.POST.get('validity','DAY')
		price = request.POST.get('price',"0.0")

		if quantity == 0:
			print 'quantity not present'
			return JsonResponse({"status":"error"})

		access_token = request.session.get('access_token','')
		public_token = request.session.get('public_token','')
		user_broker_id = request.session.get('user_broker_id','')

		if access_token=='' or public_token=='' or user_broker_id=='':
			print 'probably kite login popup'
			return JsonResponse({"status":"error"})

		transaction_type = ''
		if(quantity>0):
			transaction_type='SELL'
		elif(quantity<0):
			transaction_type='BUY'

		payload = {
		  "api_key":settings.KITE_API_KEY,
		  "access_token":access_token,
		  "tradingsymbol":symbol,
		  "exchange":exchange,
		  "transaction_type":transaction_type,
		  "order_type":order_type,
		  "quantity":abs(quantity),
		  "product":product,
		  "validity":validity
		}

		if segment=='' and exchange=='CDS':
			segment = 'CDS-FUT'
		elif segment=='' and exchange=='MCX':
			segment = 'MCX'
		elif segment=='' and exchange=='NFO':
			if str(symbol).endswith("CE") or str(symbol).endswith("PE"):
				segment = 'NFO-OPT'
			else:
				segment = 'NFO-FUT'
		elif exchange=='NFO-FUT':
			segment = 'NFO-FUT'
			exchange = 'NFO'
		elif exchange=='NFO-OPT':
			segment = 'NFO-OPT'
			exchange = 'NFO'
		elif segment == '':
			segment = 'NSE'

		if order_type =='LIMIT':
			try:
				payload['price']=float(price)
			except:
				return JsonResponse({"status":"error","error_msg":"Invalid price"})
		# print payload
		headers = {}
		if settings.KITE_HEADER == True:
			headers = {"X-Kite-Version":"3"}
			auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
			headers["Authorization"] = "token {}".format(auth_header)
		response = requests.request("POST","https://api-partners.kite.trade/orders/regular", data=payload,headers=headers)
		if response.status_code == 200:
			response_json = json.loads(response.text)
			if response_json['status']=="success":
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
									"api_key":settings.KITE_API_KEY,
									"access_token":access_token,
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
				return JsonResponse({'status':'error','order_response':response_json,'response_code':response.status_code})
		else:
			return JsonResponse({'status':'error','response_code':response.status_code,'error-type':'Session expired, re-login required','error_msg':'Session expired, re-login required'})
		return JsonResponse({'status':'error'})

def beta_signup(request):
	return JsonResponse({})

def market_watch_new(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error","msg":"auth"})
	
	if request.method == 'GET':
		market_watch_name = request.GET.get('market_watch_name','')
		complete_market_watch = request.GET.get('complete',False)
		# print(basket_name)

		conn = get_redis_connection("default")
		if market_watch_name == '':
			saved_market_watch = conn.hgetall('market_watch_'+user_uuid)
			market_watch_names_list = saved_market_watch.keys()

			saved_baskets = conn.hgetall('baskets_'+user_uuid)
			basket_names_list = saved_baskets.keys()
			formated_backtest = {}
			for k,v in saved_baskets.iteritems():
				instruments = ujson.loads(v)
				if len(instruments)==0:
					continue
				if len(instruments)>0:
					if type(instruments[0])==type("str"):
						continue
				instruments_updated = []
				for x in instruments:
					# print(x,type(x))
					# print k,x,type(x),type(u'str')
					if type(x)==type(u'str'):
						if len(x.split("_"))==2:
							sym,seg = x.split("_")
							x = {}
							x["symbol"] = sym
							x["segment"] = seg
							x["seg_sym"] = x["segment"]+"_"+x["symbol"]
							x["id"]=str(uuid.uuid4())
						# else:
						# 	print("yooooo")
							# continue
					if type(x)!=type({}):
						continue
					if x.get("id",None) is None:
						continue
					x["seg_sym"] = x["segment"]+"_"+x["symbol"]
					instruments_updated.append(x)
				if len(instruments_updated)==0:
					continue
				if k not in saved_market_watch.keys():
					saved_market_watch[k]=ujson.dumps({"thumbnail":"","listName":k,"instrumentList":instruments_updated})
			# print saved_baskets
			if complete_market_watch:
				return JsonResponse({"status":"success","market_watch_names_list":saved_market_watch.keys(),"market_watches":saved_market_watch})
			else:
				return JsonResponse({"status":"success","market_watch_names_list":market_watch_names_list})
		else:
			market_watch_instruments = conn.hget('market_watch_'+user_uuid,market_watch_name)
			if market_watch_instruments == None:
				try:
					# market_watch_instruments = conn.hget('market_watch_'+user_uuid,market_watch_name)
					saved_baskets = conn.hgetall('baskets_'+user_uuid)
					# print ('ssssssssss',user_uuid,saved_baskets,market_watch_name)
					if saved_baskets is not None:
						# basket_names_list = saved_baskets.keys()
						formated_backtest = {}
						for k,v in saved_baskets.iteritems():
							print k,market_watch_name
							if k == str(market_watch_name):
								print(k,market_watch_name)
								instruments =  ujson.loads(v)
								if len(instruments)==0:
									continue
								if len(instruments)>0:
									if type(instruments[0])==type("str"):
										continue
								instruments_updated = []
								for x in instruments:
									# print(x,type(x))
									if type(x)!=type({}):
										continue
									if x.get("id",None) is None:
										continue
									x["seg_sym"] = x["segment"]+"_"+x["symbol"]
									instruments_updated.append(x)
								if len(instruments_updated)==0:
									continue
								# if k not in saved_market_watch:
								saved_market_watch=ujson.dumps({"thumbnail":"","listName":k,"instrumentList":instruments_updated})
								return JsonResponse({"status":"success","market_watch_name":market_watch_name,"market_watch_instruments":saved_market_watch})
					else:
						pass
				except:
					print(traceback.format_exc())
				print("hereeeeeeeeeee")
				return JsonResponse({"status":"success","market_watch_name":market_watch_name,"market_watch_instruments":ujson.dumps({})})

			# basket_instruments = saved_basket.keys()
			return JsonResponse({"status":"success","market_watch_name":market_watch_name,"market_watch_instruments":market_watch_instruments})
		
		return JsonResponse({"status":"error"})
	
	if request.method == 'POST':
		market_watch_name = request.POST.get('market_watch_name','')
		updated_name = request.POST.get('update_name','')
		# icon = request.GET.get('icon','')
		market_watch_instruments = request.POST.get('market_watch_instruments','{}')

		if market_watch_instruments == 'undefined':
			market_watch_instruments = '{}'
		market_watch_edit = request.POST.get('market_watch_edit','false')
		market_watch_del = request.POST.get('del',False)
		complete_market_watch = request.POST.get('complete',False)

		# print basket_instruments
		if(market_watch_name==''):
			return JsonResponse({"status":"error","msg":"Market watch name missing"})

		conn = get_redis_connection("default")
		
		if market_watch_del or updated_name!='':
			market_watch_deleted = conn.hdel('market_watch_'+user_uuid,market_watch_name)
			try:
				basket_deleted = conn.hdel('baskets_'+user_uuid,market_watch_name)
			except:
				pass
			if updated_name=='':
				if complete_market_watch:
					saved_market_watch = conn.hgetall('market_watch_'+user_uuid)
					market_watch_names_list = saved_market_watch.keys()
					# print saved_baskets
					return JsonResponse({"status":"success","market_watch_names_list":market_watch_names_list,"market_watches":saved_market_watch})
				return JsonResponse({"status":"success"})
		
		saved_market_watch = conn.hgetall('market_watch_'+user_uuid)
		if updated_name!='':
			market_watch_name = updated_name
		if(saved_market_watch==None): # if the user has not market watches
			saved_market_watch = {market_watch_name:market_watch_instruments}
		
		# print 'basket_edit.....',basket_edit,saved_baskets.keys()
		if(market_watch_name in saved_market_watch.keys() and market_watch_edit!='true'):
			return JsonResponse({"status":"error","msg":"Market watch with same name already exists","error_msg":"Market watch with same name already exists"})

		r = conn.hset('market_watch_'+user_uuid,market_watch_name,market_watch_instruments)
		if complete_market_watch:
			saved_market_watch = conn.hgetall('market_watch_'+user_uuid)
			market_watch_names_list = saved_market_watch.keys()
			# get saved_baskets

			saved_baskets = conn.hgetall('baskets_'+user_uuid)
			basket_names_list = saved_baskets.keys()
			formated_backtest = {}
			for k,v in saved_baskets.iteritems():
				instruments = ujson.loads(v)
				if len(instruments)==0:
					continue
				if len(instruments)>0:
					if type(instruments[0])==type("str"):
						continue
				instruments_updated = []
				for x in instruments:
					# print(x,type(x))
					if type(x)!=type({}):
						continue
					if x.get("id",None) is None:
						continue
					x["seg_sym"] = x["segment"]+"_"+x["symbol"]
					instruments_updated.append(x)
				if len(instruments_updated)==0:
					continue
				if k not in saved_market_watch.keys():
					saved_market_watch[k]=ujson.dumps({"thumbnail":"","listName":k,"instrumentList":instruments_updated})
			return JsonResponse({"status":"success","market_watch_names_list":market_watch_names_list,"market_watches":saved_market_watch})
		return JsonResponse({"status":"success"})

	# if request.method == 'DELETE':
	# 	basket_name = request.DELETE.get('basket_name','')
	# 	if(basket_name==''):
	# 		return JsonResponse({"status":"error","msg":"Basket name missing"})
	# 	conn = get_redis_connection("default")
	# 	basket_deleted = conn.hdel('baskets_'+user_uuid,basket_name)
	# 	return JsonResponse({"status":"success"})

	return JsonResponse({"status":"error","msg":"unknown"})

def user_baskets(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error","msg":"auth"})
	
	if request.method == 'GET':
		basket_name = request.GET.get('basket_name','')
		complete_baskets = request.GET.get('complete',False)
		# print(basket_name)

		conn = get_redis_connection("default")
		if basket_name == '':
			saved_baskets = conn.hgetall('baskets_'+user_uuid)
			basket_names_list = saved_baskets.keys()
			# print saved_baskets
			if complete_baskets:
				return JsonResponse({"status":"success","basket_names_list":basket_names_list,"baskets":saved_baskets})
			else:
				return JsonResponse({"status":"success","basket_names_list":basket_names_list})
		else:
			basket_instruments = conn.hget('baskets_'+user_uuid,basket_name)
			if basket_instruments == None:
				return JsonResponse({"status":"success","basket_name":basket_name,"basket_instruments":[]})

			# basket_instruments = saved_basket.keys()
			return JsonResponse({"status":"success","basket_name":basket_name,"basket_instruments":basket_instruments})
		
		return JsonResponse({})
	
	if request.method == 'POST':
		basket_name = request.POST.get('basket_name','')
		basket_instruments = request.POST.get('basket_instruments','[]')
		basket_edit = request.POST.get('basket_edit','false')
		basket_del = request.POST.get('del',False)

		# print basket_instruments
		if(basket_name==''):
			return JsonResponse({"status":"error","msg":"Basket name missing"})

		conn = get_redis_connection("default")
		
		if basket_del:
			basket_deleted = conn.hdel('baskets_'+user_uuid,basket_name)
			return JsonResponse({"status":"success"})
		
		saved_baskets = conn.hgetall('baskets_'+user_uuid)
		if(saved_baskets==None):
			saved_baskets = {basket_name:basket_instruments}
		
		# print 'basket_edit.....',basket_edit,saved_baskets.keys()
		if(basket_name in saved_baskets.keys() and basket_edit!='true'):
			return JsonResponse({"status":"error","msg":"Basket with same name already exists","error_msg":"Basket with same name already exists"})

		r = conn.hset('baskets_'+user_uuid,basket_name,basket_instruments)

		return JsonResponse({"status":"success"})

	# if request.method == 'DELETE':
	# 	basket_name = request.DELETE.get('basket_name','')
	# 	if(basket_name==''):
	# 		return JsonResponse({"status":"error","msg":"Basket name missing"})
	# 	conn = get_redis_connection("default")
	# 	basket_deleted = conn.hdel('baskets_'+user_uuid,basket_name)
	# 	return JsonResponse({"status":"success"})

	return JsonResponse({"status":"error","msg":"unknown"})

def submit_feedback(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth or user_uuid=="":
		return JsonResponse({"status":"error","msg":"auth"})
	if request.method == 'POST':
		try:
			body_data = request.POST.get("feedback_details_text","")
			url = "https://mailing.streak.solutions/streak_mail/user_feedback/send_mail"
			method = "POST"
			params = {}
			user = models.UserProfile.objects.get(user_uuid=user_uuid)
			user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
			# print(user.email)
			email = user.email.lower()
			if email == "" or user.user_broker_id+"@"+user.first_broker == email:
				email = user.additional_details.get("secondary_email","").lower()
				if email=="":
					return JsonResponse({"status":"error","msg":"Error submitting due to missing email, try again or directly write to us at support@streak.tech"})
			params = {"subject":"Feedback from "+user.first_name+":"+user.user_broker_id+":"+user_subscription.subscription_plan[0]+":"+user_subscription.subscription_period,"reply_to":email.lower(),"body_data":body_data,"sender": "support@streak.tech"}
			headers = {"content-type":"application/json"}
			response = requests.request(method,url,data=json.dumps(params),headers=headers)
			if(response.status_code!=200):
				print(response.text)
				return JsonResponse({"status":"error","msg":"Submit error, try again","error_msg":"Submit error, try again"})
			return JsonResponse({"status":"success","msg":"Feedback submitted."})
		except:
			print(traceback.format_exc())
			return JsonResponse({"status":"error","msg":"Unknown"})

	return JsonResponse({"status":"error","msg":"method"})

def get_version(request):
	conn = get_redis_connection("default")
	v = conn.get('android_app_version')
	if v == None:
		v = 10
	try:
		v = int(v)
	except:
		v = 10
	return JsonResponse({'v':v})

def get_version4(request):
	# conn = get_redis_connection("default")
	# v = conn.get('android_app_version')
	# if v == None:
	# 	v = 10
	# try:
	# 	v = int(v)
	# except:
	# 	v = 10
	v = {
		"version_code": "2.0.96", 
		"v": "96", 
		"new_v": 96, 
		"new_version_code": "2.0.96", 
		"force_update":96,
		"force_update_ios":72,
		"new_version_date": datetime.datetime.now().isoformat(), 
		"new_version_features": ['Position sizing', 'Dynamic contracts'],
		"version_date": datetime.datetime.now().isoformat(),
		"new_version_fixes": ['Sort fixed in strategy']
		}

	return JsonResponse(v)

def scan_redis_key(conn,regx,key_list=False):
	cur = '0'  # set initial cursor to 0
	keys_count = 0
	keys_list = []
	key = None
	while cur:
		# cur, keys = conn.scan(cur, match=regx)
		keys = conn.keys(regx)
		print("Iteration results:", keys)
		if(len(keys)>0):
			if not key_list:
				return keys[0]
			else:
				return keys
		else:
			if not key_list:
				return ''
			else:
				return [] 
			keys_count += 1
			keys_list = keys_list + keys
			if not key_list:
				break

	if keys_count>0 and not key_list:
		key = keys_list[0].decode("utf-8")
	if key_list:
		return keys_list
	return key
 
def archive_functions(archive_entry): 
  url = "https://s.streak.tech/archives/" 
  headers = {"content-type":"application/json"} 
  payload = json.dumps(archive_entry) 
  try: 
	response = requests.request("POST", url, json=archive_entry, headers=headers) 
	# print response.text 
	# print response.status_code 
	print response.text,payload 
	if response.status_code!=200: 
	  print response.text,response.status_code 
  except: 
	print traceback.format_exc() 
 
def add_to_archive(request): 
  #http://127.0.0.1/add_to_archive/?ukey=hR2MxYTZ4ATNlFTYtEmM4kTL1AzN00SO5EzMtIGZwgDOiVjM&key=2UTY1M2NwgzYxAjZtU2MlhTLwUWO00SNiJGOtQmY5ImZ1ATY&secret=testing_initialization 
  return load_samples_to_archive(request) 
  if request.method=='GET': 
	if request.GET.get('secret')=='testing_initialization': 
	  key = request.GET.get('key','') 
	  key = key[::-1] 
	  print 'kkkkkkkkk',key 
	  algo_uuid = base64.urlsafe_b64decode(str(key)) 
	  ukey = request.GET.get('ukey','') 
	  ukey = ukey[::-1] 
	  user_uuid = base64.urlsafe_b64decode(str(ukey)) 
 
	  algo = models.Algorithm.objects.get(user_uuid=user_uuid,algo_uuid=algo_uuid) 
	  backtest_metas = models.BacktestMeta.objects(user_uuid=user_uuid,algo_uuid=algo_uuid) 
	  archive_entry = ujson.loads(algo.to_json()) 
	  algo_state = algo['algo_state'] 
	  indicators = [i['indicator'] for i in algo_state['entryIndicators']]+[i['indicator'] for i in algo_state['exitIndicators']] 
 
	  archive_entry['indicators'] = indicators 
	  archive_entry['owner_uuid'] = algo['algo_uuid'] 
 
	  del archive_entry['algo_state'] 
	  del archive_entry['_id'] 
	  del archive_entry['user_uuid'] 
	  for b in backtest_metas: 
		archive_entry = algo 
		seg_sym = b['seg_sym'] 
		archive_entry['segment'],archive_entry['symbol'] = seg_sym.split('_') 
		archive_entry['exchange']=archive_entry['segment'].lower() 
		archive_entry['latest_backtest_metrics']=b['backtest_result'][seg_sym] 
		archive_functions(archive_entry) 
	  return JsonResponse({'status':'success'}) 
  return JsonResponse({'status':'error'}) 
 
def load_samples_to_archive(request): 
  # http://127.0.0.1/load_samples_to_archive/?id=lkasjdlkajsd&secret=testing_initialization 
  try:  
	# if request.GET.get('secret','')!='testing_initialization': 
	#   con = get_redis_connection("default")  
	#   samples = con.get('user_samples')  
	#   bt_samples = []  
	#   if samples:  
	#	 samples = eval(samples) 
	# else: 
	samples = {'samples': [[request.GET.get('id',''), '', '']]} 
	for s in samples['samples']: 
	  try:  
		algo_uuid = s[0] 
		algo = models.Algorithm.objects.get(algo_uuid=algo_uuid) 
		backtest_metas = models.BacktestMeta.objects(algo_uuid=algo_uuid) 
		archive_entry = ujson.loads(algo.to_json()) 
		algo_state = algo['algo_state'] 
		indicators = [i['indicator'] for i in algo_state['entryIndicators']]+[i['indicator'] for i in algo_state['exitIndicators']] 
 
		archive_entry['indicators'] = indicators 
		archive_entry['owner_uuid'] = algo['algo_uuid'] 
 
		del archive_entry['algo_state'] 
		del archive_entry['_id'] 
		del archive_entry['user_uuid'] 
		del archive_entry['symbols'] 
		for b in backtest_metas: 
		  # archive_entry = algo 
		  seg_sym = b['seg_sym'] 
		  archive_entry['segment'],archive_entry['symbol'] = seg_sym.split('_') 
		  archive_entry['exchange']=archive_entry['segment'].lower() 
		  archive_entry['latest_backtest_metrics']=b['backtest_result'][seg_sym] 
		  archive_entry['latest_backtest_metrics'][seg_sym] = seg_sym 
		  archive_functions(archive_entry) 
		return JsonResponse({'status':'success'}) 
	  except:  
		print traceback.format_exc()  
	resp = JsonResponse({"status":"success"}) 
	resp["Access-Control-Allow-Credentials"] = "true"  
	resp["Access-Control-Allow-Origin"] = "*"   
	return resp 
  except:  
	pass 
  return JsonResponse({'status':'error'}) 

def fetch_billing_data(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth'})
	if request.method!='GET':
		return JsonResponse({"status":"error",'error-type':'method'})

	recommended_plan = {}
	try:
		recommended_plan = { 
						"note":"", 
						"subscription_period":"12", 
						"subscription_tax": 252, 
						"subscription_plan": "ultimate", 
						"subscription_price": 1400, 
						"plan_id": 3, 
						"subscription_validity_date": 365, 
						"features": [ 
							{ "label": '<value> Backtests per day', "value": [1000] }, 
							{ "label": '<value> Live strategies at a time', "value": [100] }, 
							{ "label": '<value> Scans per day', "value": ["Unlimited"] }, 
						], 
						"exclusive":[ 
							{ "label": 'Schedule a <value> calls with experts', "value": ["30 minutes"] }, 
							{ "label": '', "value": ["Heikin-Ashi"] }, 
							{ "label": '', "value": ["Renko (In basic create)"] }, 
							{ "label": '', "value": ["MCX (Commodities)"] }, 
							{ "label": '', "value": ["Multi-time frame strategy"] }, 
							{ "label": '<value> entry and exit conditions', "value": [10] }  
						], 
						"ultimate_feature":[ 
						], 
						"subscription_total_price": 1625, 
						"subscription_product": "ultimate",
						"discount_percentage":30
					}
		user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)

		subscription_status = {}

		if(user_subscription.subscription_validity >= datetime.datetime.today()):
			subscription_status['subscription_valid'] = True
			subscription_status['current_subscription_price'] = user_subscription.subscription_price
			subscription_status['current_subscription_price'] = user_subscription.subscription_price
			subscription_status['subscription_plan'] = user_subscription.subscription_plan
			subscription_status['subscription_remaining'] = max((user_subscription.subscription_validity-datetime.datetime.today()).days,0)
			subscription_status['subscription_period'] = user_subscription.subscription_period
		else:
			subscription_status['subscription_valid'] = False
			subscription_status['current_subscription_price'] = -1
			subscription_status['subscription_plan'] = user_subscription.subscription_plan
			subscription_status['subscription_remaining'] = -1
			subscription_status['subscription_period'] = ""
			subscription_status['subscription_type'] = -1


		if user_subscription.subscription_type!=0 and user_subscription.subscription_active:
			subscription_status['subscription_autorenew'] = True
			subscription_status['next_billing_date'] = user_subscription.subscription_validity + datetime.timedelta(days=1)
		else:
			subscription_status['subscription_autorenew'] = False
			subscription_status['next_billing_date'] = 'N/A'

		subscription_status['user_broker_id'] = user_subscription.user_broker_id


		user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
		user_subscription_log = models.UserSubscriptionLog.objects(user_uuid=user_uuid).order_by('-created_at')
		us_log = []
		for sl in user_subscription_log:
			us_log.append(sl.to_json())

		subscription_status = {}
		subscription_status['subscription_type'] = user_subscription.subscription_type
		if(user_subscription.subscription_validity >= datetime.datetime.today()):
			subscription_status['subscription_valid'] = True
			subscription_status['current_subscription_price'] = user_subscription.subscription_price
			subscription_status['current_subscription_total_price'] = user_subscription.subscription_total_price
			subscription_status['subscription_plan'] = user_subscription.subscription_plan
			subscription_status['subscription_remaining'] = max((user_subscription.subscription_validity-datetime.datetime.today()).days,0)
			subscription_status['subscription_period'] = user_subscription.subscription_period
		else:
			subscription_status['subscription_valid'] = False
			subscription_status['current_subscription_price'] = -1
			subscription_status['subscription_plan'] = 'N/A'
			subscription_status['subscription_remaining'] = -1
			subscription_status['subscription_period'] = ""
			subscription_status['subscription_type'] = -1


		if user_subscription.subscription_type!=0 and user_subscription.subscription_active:
			subscription_status['subscription_autorenew'] = True
			subscription_status['next_billing_date'] = user_subscription.subscription_validity + datetime.timedelta(days=1)
		else:
			subscription_status['subscription_autorenew'] = False
			subscription_status['next_billing_date'] = 'N/A'

		subscription_status['user_broker_id'] = user_subscription.user_broker_id

		if user_subscription.subscription_type == 0:
				subscription_status['total_backtest'] = 50
				subscription_status['total_deployments'] = 5
		elif user_subscription.subscription_type == 1:
				subscription_status['total_backtest'] = 200
				subscription_status['total_deployments'] = 25
		elif user_subscription.subscription_type == 2:
				subscription_status['total_backtest'] = 500
				subscription_status['total_deployments'] = 50
		elif user_subscription.subscription_type == 3:
				subscription_status['total_backtest'] = 1000
				subscription_status['total_deployments'] = 100
		else:
			subscription_status['total_backtest'] = 50
			subscription_status['total_deployments'] = 5

		if user_subscription.subscription_price==0:
			subscription_status['subscription_plan'] = 'free'
			subscription_status['subscription_type'] = 0

		subscription_status['renew_plan'] = user_subscription.renew_plan
		if user_subscription.subscription_validity<datetime.datetime.now():
			subscription_limit = {'valid':False,'reason':'Subscription duration is over','error_msg':'Subscription duration is over'}
		else:

			con = get_redis_connection("default")
			#user_uuid : {'deployed':0,'backtest':0}
			usage = con.get('daily_usage:'+user_uuid)
			if usage != None:
				usage = eval(usage)
			else:
				usage = {'backtest':0,'deployed':0}

			usage['deployed'] = 0
			# deps_live = con.keys('deployed:'+user_uuid+':*')
			deps_live = get_deployment_keys({"user_uuid":user_uuid,"status":0,"expiration_time":{"$gte":datetime.datetime.now()}})
			if(deps_live):
				# d_count = 0
				# for d in deps_live:
				# 	if '/USDC' not in d:
				# 		d_count+=1
				usage['deployed']=len(deps_live)

			now_time = datetime.datetime.now()
			renewal_time = ((now_time.replace(hour=23,minute=0,second=0) - now_time).seconds/3600+2)%24
			if renewal_time==0:
				renewal_time = 24
			if user_subscription.subscription_type == 0:
				# print 'yooooooooooooooooooooo',usage.get('backtest',0) 
				backtests_remaining = 50 - usage.get('backtest',0)
				deployments_remaining = 5 - usage.get('deployed',0)
				print {'valid':True,'total_backtest':50,'total_deploys':5,'backtest':backtests_remaining,'deployments_remaining':deployments_remaining}
				subscription_limit = {"status":"success",'valid':True,'backtest':backtests_remaining,'total_backtest':20,'total_deploys':2,'deployments_remaining':deployments_remaining,'renewal_time':renewal_time,'subscription_type':user_subscription.subscription_type}
			if user_subscription.subscription_type == 1:
				backtests_remaining = 200 - usage.get('backtest',0)
				deployments_remaining = 25 - usage.get('deployed',0)
				subscription_limit = {'valid':True,'total_backtest':200,'total_deploys':25,'backtest':backtests_remaining,'deployments_remaining':deployments_remaining,'renewal_time':renewal_time,'subscription_type':user_subscription.subscription_type}
			if user_subscription.subscription_type == 2:
				backtests_remaining = 500 - usage.get('backtest',0)
				deployments_remaining = 50 - usage.get('deployed',0)
				subscription_limit = {'valid':True,'total_backtest':500,'total_deploys':50,'backtest':backtests_remaining,'deployments_remaining':deployments_remaining,'renewal_time':renewal_time,'subscription_type':user_subscription.subscription_type}
			if user_subscription.subscription_type == 3:
				backtests_remaining = 1000 - usage.get('backtest',0)
				deployments_remaining = 100 - usage.get('deployed',0)
				subscription_limit = {'valid':True,'total_backtest':1000,'total_deploys':100,'backtest':backtests_remaining,'deployments_remaining':deployments_remaining,'renewal_time':renewal_time,'subscription_type':user_subscription.subscription_type}
		return JsonResponse({"status":"success","user_subscription":user_subscription.to_json(),'subscription_status':subscription_status,'subscription_limit':subscription_limit,"user_subscription_log":us_log,"recommended_plan":recommended_plan})
	except DoesNotExist:
		print traceback.format_exc()
		print 'Creating missing subscription'
		try:
			if(request.session.get('user_broker_id','')!= ''):
				subscription_uuid=str(uuid.uuid4())
				subscription_log_uuid = str(uuid.uuid4())
				user_subscription = models.UserSubscription(user_uuid=user_uuid,
					subscription_uuid=subscription_uuid,
					subscription_validity= max(datetime.datetime.today() + datetime.timedelta(days=int(7)),datetime.datetime(2018, 11, 30, 23, 59, 59)), #datetime.datetime.today() + datetime.timedelta(days=int(21)),
					latest_subscription_id = subscription_log_uuid,
					user_broker_id = request.session.get('user_broker_id',''),
					subscription_instance = 'trial'
					)

				user_subscription_log = models.UserSubscriptionLog(user_uuid=user_uuid,
					subscription_log_uuid = subscription_log_uuid,
					subscription_uuid = subscription_uuid,
					subscription_start = datetime.datetime.today(),
					subscription_stop = max(datetime.datetime.today() + datetime.timedelta(days=int(7)),datetime.datetime(2018, 11, 30, 23, 59, 59)), #datetime.datetime.today() + datetime.timedelta(days=int(21)),
					user_broker_id = request.session.get('user_broker_id',''),
					subscription_instance = 'trial'
					)

				user_subscription_log.save()
				user_subscription.save()

				renewal_time = ((now_time.replace(hour=23,minute=0,second=0) - now_time).seconds/3600+2)%24
				if renewal_time==0:
					renewal_time = 24
				subscription_limit = {'valid':True,'backtest':200,'total_backtest':200,'total_deploys':5,'deployments_remaining':5,'renewal_time':renewal_time,'subscription_type':0}
				return JsonResponse({"status":"success","user_subscription":user_subscription.to_json(),'subscription_status':subscription_status,'subscription_limit':subscription_limit,"user_subscription_log":[],"recommended_plan":recommended_plan})
			else:
				return JsonResponse({"status":"error","error_msg":"auth broker id null"})
		except:
			print 'error creating subscription'
			print traceback.format_exc()

			return JsonResponse({"status":"error","error_msg":"error creating subscription"})
	except:
		print traceback.format_exc()
		pass
	return JsonResponse({"status":"error"})

def deployed_count(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth'})
	if request.method!='GET':
		return JsonResponse({"status":"error",'error-type':'method'})

	deployed_count = {"notifications":0,"paper":0,"screener":0}
	try:
		paper = models.DeployedAlgorithm._get_collection().count({'user_uuid':user_uuid,"deployment_type":"Paper trading","expiration_time":{"$gte":datetime.datetime.now()},"status":0})
		notifications = models.DeployedAlgorithm._get_collection().count({'user_uuid':user_uuid,"deployment_type":"Notifications","expiration_time":{"$gte":datetime.datetime.now()},"status":0})
		screener = models.ScreenerAlert._get_collection().count({'user_uuid':user_uuid,'status':0})
		deployed_count["notifications"]=notifications
		deployed_count["paper"]=paper
		deployed_count["screener"]=screener
		return JsonResponse({"status":"success","deployed_count":deployed_count})

	except:
		print(traceback.format_exc())
		return JsonResponse({"status":"error","deployed_count":deployed_count,"error_msg":"Unknown error, please try again in sometime"})
	return JsonResponse({"status":"error","error_msg":"Invalid method"})

def deployed_count2(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth'})
	if request.method!='GET':
		return JsonResponse({"status":"error",'error-type':'method'})

	deployed_count = {"notifications":{ "waiting": 0, "entered": 0, "stopped": 0 },"paper":{ "waiting": 0, "entered": 0, "stopped": 0 },"screener":{  "entered": 0 }}
	try:
		deployments = models.DeployedAlgorithm._get_collection().find({'user_uuid':user_uuid,"created_at":{"$gte":datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)}})
		# print({'user_uuid':user_uuid,"created_at":{"$gte":datetime.datetime.today()}})
		live_waiting = 0
		live_entered = 0
		live_stopped = 0
		paper_waiting = 0
		paper_entered = 0
		paper_stopped = 0
		for d in deployments:
			if d["status"]<0:
				if d["deployment_type"]=="Paper trading":
					paper_stopped = paper_stopped+1
				else:
					live_stopped = live_stopped+1
			else:
				ha = models.HoldingsForAlgorithm._get_collection().find_one({"user_uuid":d["user_uuid"],"deployment_uuid":d["deployment_uuid"],"algo_uuid":d["algo_uuid"]})
				print(ha)
				if d["deployment_type"]=="Paper trading":
					if ha["position"].get("qty",0)==0:
						paper_waiting = paper_waiting+1
					else:
						paper_entered = paper_entered+1
				else:
					if ha["position"].get("qty",0)==0:
						live_waiting = live_waiting+1
					else:
						live_entered = live_entered+1
		scanner_entered = models.ScreenerAlert._get_collection().count({'user_uuid':user_uuid,'status':0})
		deployed_count = {"notifications":{ "waiting": live_waiting, "entered": live_entered, "stopped": live_stopped },"paper":{ "waiting": paper_waiting, "entered": paper_entered, "stopped": paper_stopped },"screener":{  "entered": scanner_entered }}
		deployed_count["status"]="success"
		return JsonResponse(deployed_count)
	except:
		print(traceback.format_exc())
		deployed_count["status"]="error"
		deployed_count["deployed_count"]="Unknown error, please try again in sometime"
		return JsonResponse(deployed_count)
	return JsonResponse({"status":"error","error_msg":"Invalid method"})

def notifications_count(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth'})
	if request.method!='GET':
		return JsonResponse({"status":"error",'error-type':'method'})
	try:
		con = get_redis_connection("default") 
		results = con.get('today_notification:'+user_uuid) 
		if results == None: 
			return JsonResponse({'status':'success','unread_count':0,'unread_split_count':{"notifications": 0, "paper": 0, "direct": 0}}) 
		else: 
			all_notifications = ujson.loads(results) 
			return JsonResponse({"status":"success",'unread_count':all_notifications['unread_count'],'unread_split_count':all_notifications.get('unread_split_count',{"notifications": 0, "paper": 0, "direct": 0})})
	except:
		print(traceback.format_exc())
		return JsonResponse({"status":"error","error_msg":"Unknown error, please try again in sometime"})
	return JsonResponse({"status":"error","error_msg":"Invalid method"})

def submit_unsubscribe_feedback(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth'})
	if request.method!='POST':
		return JsonResponse({"status":"error",'error-type':'method'})
	try:
		note = request.POST.get("note","")
		reason = request.POST.get("reason","")
		uf = models.UserFeedback(user_uuid=user_uuid,
							note=note,
							reason=reason
			)
		uf.save()
		return JsonResponse({"status":"success"})
	except:
		print(traceback.format_exc())
	return JsonResponse({"status":"error","error_msg":"Invalid method"})

def dynamic_sym_params_generator(dynamic_str):
	d_list = dynamic_str.split("_")
	regex = r"\((.*?)\)"
	matches = re.findall(regex, dynamic_str, re.MULTILINE)
	return matches