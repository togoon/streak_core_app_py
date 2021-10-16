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

def screener_complete_score(screener_state='',equities='',screener_logic='',take_profit='',stop_loss=''):
	percent_complete=25 
	if len(screener_state.get("expressions",[]))>0: 
		percent_complete = percent_complete+100 
	return min(100,percent_complete)

def copy_screener(request):
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
		return JsonResponse({"status":"error","error":"auth"},status=401)

	if request.method=="POST":
		# return JsonResponse({"status":"error","error_msg":"Unsupported method"})
		# post_data = ujson.loads(request.body)
		post_data = request.POST
		# post_data = ujson.loads(post_data)
		screener_uuid = post_data.get('screener_uuid',"")
		discover_screener = post_data.get('discover',"true")
		screener_name = post_data.get('screener_name',"")

		screener = None
		try:
			if discover_screener!='true':
				screener = models.Screener.objects.get(user_uuid=user_uuid,screener_uuid=screener_uuid,complete=True)
			else:
				screener = models.Screener.objects.get(screener_uuid=screener_uuid,sample=True)
			if screener:
				screener_state = screener.screener_state
				screener_uuid = str(uuid.uuid4())
				screener_desc = screener.screener_desc
				screener_logic = screener.screener_logic
				time_frame = screener.time_frame
				chart_type = screener.chart_type
				universe = screener.universe
				basket_name = screener.basket_name
				basket_symbols = screener.basket_symbols
				screener_result = screener.screener_result
				tags = screener.tags
				complete = screener.complete
				percent_complete = screener.percent_complete

				screener_item = models.Screener(
								user_uuid=user_uuid,
								screener_uuid = screener_uuid,
								screener_name = screener_name,
								screener_first_name = screener_name,
								screener_desc = screener_desc,
								screener_state = screener_state,
								screener_logic = screener_logic,
								time_frame = time_frame,
								chart_type = chart_type,
								universe = universe,
								screener_result=screener_result,
								tags = tags,
								basket_name = basket_name,
								basket_symbols=basket_symbols,
								complete=complete,
								percent_complete=percent_complete  
								)

				screener_item.save()
				try:	
					archive_entry = ujson.loads(screener_item.to_json()) 

					# archive_entry['owner'] = screener_item.user_uuid 
					archive_entry['symbol_count'] =  len(archive_entry['screener_result'])

					del archive_entry['screener_state'] 
					del archive_entry['screener_result']
					archive_entry.pop('_id','') 
					archive_entry['last_updated']=datetime.datetime.now().isoformat()
					data = {"id":screener_uuid,'document':archive_entry} 
					# print "Mongo screener save time ",time.time()-st
					archive_screener_function(data,False)
					# print "Screener archive call ",time.time()-st
				except:
					print traceback.format_exc()
						
				return JsonResponse({'status':'success','screener_uuid':screener_uuid})
			else:
				return JsonResponse({'status':'error','error_msg':"No scanner found"})
		except DoesNotExist:
			print("screener_uuid",screener_uuid)
			# print(traceback.format_exc())
			return JsonResponse({'status':'error','error_msg':"Scanner not found"})
		except:
			print(traceback.format_exc())
			return JsonResponse({'status':'error','error_msg':"Unexpected error, please try in some time"})
	return JsonResponse({'status':'error','error_msg':"Invalid method"})
		

def screener(request):
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

	if request.method=="POST":
		if not user_is_auth:
			return JsonResponse({"status":"error","error":"auth"},status=401)
		# return JsonResponse({"status":"error","error_msg":"Unsupported method"})
		st = time.time()
		# post_data = ujson.loads(request.body)
		post_data = request.POST.get('data','{}')
		post_data = ujson.loads(post_data)
		screener_state = post_data.get('screener_state',{})
		screener_name = post_data.get('screener_name',"")
		screener_uuid = post_data.get('screener_uuid',"")
		screener_desc = post_data.get('screener_desc','')
		screener_logic = post_data.get('screener_logic','')
		time_frame = post_data.get('time_frame','')
		chart_type = post_data.get('chart_type','').lower()
		universe = post_data.get('universe','')
		basket_name = post_data.get('basket_name','')
		basket_symbols = post_data.get('basket_symbols',[])
		screener_result = post_data.get('screener_result',{})

		# if basket_symbols:
		# 	basket_symbols = urllib.unquote(basket_symbols).decode('utf8') 
		# 	basket_symbols = ujson.loads(basket_symbols)
		# else:
		# 	basket_symbols = []
		complete = True
		percent_complete = screener_complete_score(screener_state) 
		if percent_complete<95:
			complete = False
		tags = post_data.get("tags",[])
		# try:
		# 	sc = models.Screener.objects(user_uuid=user_uuid,screener_name=screener_name) 
		# 	if len(sc)>0: 
		# 		return JsonResponse({'status':"error",'error_msg':"Error saving, screener with same name exits"})
		# except:
		# 	print traceback.format_exc()
		# 	pass

		if screener_uuid=="":
			try:
				sc = models.Screener.objects(user_uuid=user_uuid,screener_name=screener_name)
				if len(sc)>0:
					return JsonResponse({'status':"error",
									'error_msg':"Error saving, screener with same name exits"
									})
			except:
				print traceback.format_exc()
				pass
			screener_uuid = str(uuid.uuid4())
			try:
				screener_item = models.Screener(
								user_uuid=user_uuid,
								screener_uuid = screener_uuid,
								screener_name = screener_name,
								screener_first_name = screener_name,
								screener_desc = screener_desc,
								screener_state = screener_state,
								screener_logic = screener_logic,
								time_frame = time_frame,
								chart_type = chart_type,
								universe = universe,
								screener_result=screener_result,
								tags = tags,
								basket_name = basket_name,
								basket_symbols=basket_symbols,
								complete=complete,
								percent_complete=percent_complete 
								)

				screener_item.save()
				try:	
					archive_entry = ujson.loads(screener_item.to_json()) 

					# archive_entry['owner'] = screener_item.user_uuid 
					archive_entry['symbol_count'] =  len(archive_entry['screener_result'])

					del archive_entry['screener_state'] 
					del archive_entry['screener_result']
					archive_entry.pop('_id','') 
					archive_entry['last_updated']=datetime.datetime.now().isoformat()
					data = {"id":screener_uuid,'document':archive_entry} 
					print "Mongo screener save time ",time.time()-st
					archive_screener_function(data,False)
					print "Screener archive call ",time.time()-st
				except:
					print traceback.format_exc()
						
				return JsonResponse({'status':'success','screener_uuid':screener_uuid})
			except:
				print traceback.format_exc()
		else:
			try:
				live = False
				try:
					screener_alerts = models.ScreenerAlert.objects.get(user_uuid=user_uuid,screener_uuid=screener_uuid,status=0)
					live = True
					alert_uuid = screener_alerts.alert_uuid
				except:
					print traceback.format_exc()
					live = False

				screener_item = models.Screener.objects.get(user_uuid=user_uuid,screener_uuid=screener_uuid)
				screener_item['screener_name'] = screener_name
				screener_item['screener_desc'] = screener_desc
				screener_item['screener_state'] = screener_state
				screener_item['screener_logic'] = screener_logic
				screener_item['time_frame'] = time_frame
				screener_item['chart_type'] = chart_type
				screener_item['universe'] = universe
				screener_item['screener_result'] = screener_result
				screener_item['tags'] = tags
				screener_item['basket_name'] = basket_name
				screener_item['basket_symbols'] = basket_symbols
				screener_item['complete'] = complete
				screener_item['percent_complete']=percent_complete 
				screener_item.save()
				try:	
					archive_entry = ujson.loads(screener_item.to_json()) 

					# archive_entry['owner'] = screener_item.user_uuid 
					archive_entry['symbol_count'] =  len(archive_entry['screener_result'])
					archive_entry['live'] = live
					del archive_entry['screener_state'] 
					del archive_entry['screener_result']
					archive_entry.pop('_id','') 
					archive_entry['last_updated']=datetime.datetime.now().isoformat()
					data = {"id":screener_uuid,'document':archive_entry}
					print "Mongo screener save time ",time.time()-st
					archive_screener_function(data,False) 
					print "Screener archive call ",time.time()-st
				except:
					print traceback.format_exc()
				return JsonResponse({'status':'success','screener_uuid':screener_uuid})
			except:
				screener_uuid = str(uuid.uuid4())
				try:
					screener_item = models.Screener(
								user_uuid=user_uuid,
								screener_uuid = screener_uuid,
								screener_name = screener_name,
								screener_desc = screener_desc,
								screener_state = screener_state,
								screener_logic = screener_logic,
								time_frame = time_frame,
								chart_type = chart_type,
								universe = universe,
								screener_result=screener_result,
								tags = tags,
								basket_name = basket_name,
								basket_symbols=basket_symbols,
								complete=complete,
								percent_complete=percent_complete
								)
					screener_item.save()
					try:	
						archive_entry = ujson.loads(screener_item.to_json()) 

						# archive_entry['owner'] = screener_item.user_uuid 
						archive_entry['symbol_count'] =  len(archive_entry['screener_result'])

						del archive_entry['screener_state']
						del archive_entry['screener_result']
						archive_entry.pop('_id','') 
						archive_entry['last_updated']=datetime.datetime.now().isoformat()
						data = {"id":screener_uuid,'document':archive_entry} 
						print "Mongo screener save time ",time.time()-st
						archive_screener_function(data,False) 
						print "Screener archive call ",time.time()-st
					except:
						print traceback.format_exc()

					return JsonResponse({'status':'success','screener_uuid':screener_uuid})
				except:
					print traceback.format_exc()

	elif request.method=="GET":
		screener_uuid = request.GET.get("screener_uuid","")
		live = False
		alert_uuid = ''
		try:
			if screener_uuid=="":
				return JsonResponse({'status':'error','error_msg':"Screener not found"})
			sample_flag = request.GET.get("sample",None)
			max_count = int(request.GET.get('max_count',0))
			if sample_flag is None or sample_flag=='false':
				if not user_is_auth:
					return JsonResponse({"status":"error","error":"auth"},status=401)
				screener = models.Screener.objects.get(user_uuid=user_uuid,screener_uuid=screener_uuid)
			else:
				screener = models.Screener.objects.get(sample=True,screener_uuid=screener_uuid)

			if screener.sample == True:
				con = get_redis_connection('screener_cache')
				try:
					# con_default = get_redis_connection('default')
					con.publish('scanner_info',ujson.dumps({"user_uuid": user_uuid, "chart_type":screener.chart_type , "sector": screener.universe, "condition": screener.screener_logic, "time_frame": screener_time_frame_mapping.get(screener.time_frame,screener.time_frame)}))
				except:
					print traceback.format_exc()
					
				screener_cache = con.get('screener_cron_'+screener_time_frame_mapping.get(screener.time_frame,screener.time_frame))
				screener_cache = ujson.loads(screener_cache)
				screener.screener_result = screener_cache.get(screener.screener_uuid,[])
			# else:
			try:
				screener_alerts = models.ScreenerAlert.objects.get(user_uuid=user_uuid,screener_uuid=screener_uuid,status=0)
				live = True
				alert_uuid = screener_alerts.alert_uuid
				screener['screener_result'] = screener_alerts.results
				screener['screener_state']['last_scan'] = datetime.datetime.strftime(screener_alerts.updated_at,"%I:%M %p %d/%m/%Y")#HH:MM A DD/MM/YYYY
			except:
				print traceback.format_exc()
				live = False
			screener = ujson.loads(screener.to_json())
			screener['status']="success"
			screener['live']=live
			screener['alert_uuid']=alert_uuid
			if max_count==-1:
				screener.pop("screener_state",{})
			return JsonResponse(screener)
		except:
			# print traceback.format_exc(),user_uuid,screener_uuids
			return JsonResponse({'status':'error','error_msg':"Screener not found"})
		
	return JsonResponse({'status':'error','error_msg':'Unkown method'})

def get_last_alert(request):
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
		return JsonResponse({"status":"error","error":"auth"},status=401)
	if request.method=="GET":
		screener_uuid = request.POST.get("screener_uuid","")
		try:
			screener_alerts = models.ScreenerAlert.objects.get(user_uuid=user_uuid,screener_uuid=screener_uuid,status=0)
			live = True
			alert_uuid = screener_alerts.alert_uuid
			return ({"status":"success","results":screener_alerts.results,"last_scan":screener_alerts})#HH:MM A DD/MM/YYYY
		except DoesNotExist:
			pass
		except:
			print traceback.format_exc()
		return ({"status":"error","results":[],"last_scan":""})
	return JsonResponse({'status':'error','error_msg':'Unkown method'})

def remove_screener(request):
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
		return JsonResponse({"status":"error","error":"auth"},status=401)
	if request.method=="POST":
		screener_uuid = request.POST.get("screener_uuid","")
		try:
			if screener_uuid=="":
				return JsonResponse({'status':'error','error_msg':"Screener not found"})	
			screener = models.Screener.objects.get(user_uuid=user_uuid,screener_uuid=screener_uuid)
			url = "https://s.streak.tech/screeners/" 
			headers = {"content-type":"application/json"} 
			payload = {
					"id":screener.screener_uuid
		  		}
			try: 
				response = requests.delete(url, json=payload, headers=headers,timeout=1)
				if response.status_code!=200: 
					print response.text,response.status_code 
					return JsonResponse({'status':'success','error_msg':'Error deleting the screener'})
				else:
					screener.delete()
					return JsonResponse({'status':'success'})
			except:
				return JsonResponse({'status':'success','error_msg':'Network error while deleting the screener'})
			return JsonResponse({'status':'success'})
		except:
			print traceback.format_exc()
			# print traceback.format_exc(),user_uuid,screener_uuids
			return JsonResponse({'status':'error','error_msg':"Screener not found"})
	return JsonResponse({'status':'error','error_msg':'Unkown method'})

def my_screeners(request):
	resp_json = False
	if(request.META.get('HTTP_X_CSRFTOKEN',None)):
		resp_json = True
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# user_uuid = '613942e5-9198-42dd-bec7-473f27f1bdc1'
	# user_is_auth = True
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		request.session['user_is_auth'] = True
		request.session['user_uuid'] = '123'
		user_uuid = '123'

	if not user_is_auth:
		if resp_json:
			return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)
		return redirect('home')
	# fetch the algorithms and then get the backtest results and live results over websocket
	# TODO move the websocket part to Go for better scale

	if request.method=='POST':
		payload = request.POST
	else:
		payload = request.GET

	page_limit = int(payload.get('page_limit',10))
	page_num = int(payload.get('page',1))
	screener_uuids = payload.get('screener_uuids',None)
	# fetching backtest result for the algorithm
	st = time.time()
	# fetching all the algos
	if screener_uuids and screener_uuids!='':
		if request.method=='POST':
			screener_uuids = urllib.unquote(screener_uuids).decode('utf8') 
			screener_uuids = ujson.loads(screener_uuids)
		else:
			screener_uuids = str(screener_uuids).split(',')
				
		screener_batch = models.Screener._get_collection().find({'user_uuid':user_uuid,"algo_uuid":{ "$in": screener_uuids}},{'_id':0 }).sort([("updated_at",-1)])
	elif screener_uuids=='':
		screener_batch = []
	else:
		screener_batch = models.Screener._get_collection().find({'user_uuid':user_uuid},{'_id':0 }).sort([("updated_at",-1)])
	# algo_batch = models.Algorithm._get_collection().find({'user_uuid':user_uuid}).sort([("updated_at",-1)]).skip(max(0,page_num-1)*page_limit).limit(page_limit)
	# algo_snaps = models.Algorithm.objects.exec_js(algo_snap_query)
	# algo_batch = models.Algorithm._get_collection().aggregate(algo_snap_query_dict)
	# print algo_snaps
	# algo_batch = algo_snaps['_batch']#[:page_limit]
	redis_con = get_redis_connection("default")

	screener_batch2 = []
	cur_i = 0
	for a in screener_batch:
		cur_i += 1
		if a['screener_uuid'] == a['screener_name']:
			screener = models.Screener.objects.get(
					user_uuid = user_uuid,
					screener_uuid = a['screener_uuid']
					)
			screener.delete()
			cur_i -= 1
		else:
			a.pop('screener_state','')
			screener_batch2.append(a)

	print('time taken dashboard',time.time()-st)
	screener_batch = screener_batch2
	# print time.time()-st
	# print algo_batch
	# print len(algo_batch)
	if(request.GET.get('resp','')=='json'):
		# print algo_batch
		return JsonResponse({'screeners':screener_batch[max(0,page_num-1)*page_limit:max(1,page_num)*page_limit],'pages':int(math.ceil(len(screener_batch)/(page_limit*1.0))),'status':'success'})
	
	return JsonResponse({'screeners':screener_batch[max(0,page_num-1)*page_limit:max(1,page_num)*page_limit],'pages':int(math.ceil(len(screener_batch)/(page_limit*1.0))),'status':'success'})

	# return render(request,'dashboard.html',{'algo':screener_batch})

def favorite_screener(request):
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
		return JsonResponse({"status":"error","error":"auth"},status=401)

	if request.method=="POST":
		con = get_redis_connection("default")
		screener_uuid = request.POST.get('sid','')
		filter_key = request.POST.get('filter','')
		fav_type = request.POST.get('fav_type',"screener")

		del_flag = request.POST.get('del',None)

		fav_key = fav_type+"_favorites:"
		favorites = con.get(fav_key+user_uuid)
		if not del_flag:
			if not favorites:
				favorites = {}
				favorites[filter_key] = {screener_uuid:datetime.datetime.now()}
				con.set(fav_key+user_uuid,ujson.dumps(favorites))
			else:
				favorites = ujson.loads(favorites)
				if filter_key in favorites.keys():
					favorites[filter_key][screener_uuid]=datetime.datetime.now()
				else:
					favorites[filter_key] = {screener_uuid:datetime.datetime.now()}

				con.set(fav_key+user_uuid,ujson.dumps(favorites))
			return JsonResponse({"status":"success"})
		else:
			if not favorites:
				return JsonResponse({"status":"success"})
			else:
				favorites = ujson.loads(favorites)
				if filter_key in favorites.keys():
					favorites[filter_key].pop(screener_uuid,'')
					con.set(fav_key+user_uuid,ujson.dumps(favorites))
				return JsonResponse({"status":"success"})
	if request.method=="GET":
		con = get_redis_connection("default")
		filter_key = request.GET.get('filter','')
		fav_type = request.GET.get('fav_type',"screener")
		fav_key = fav_type+"_favorites:"
		favorites = con.get(fav_key+user_uuid)
		if not favorites:
			favorites = {}
		else:
			favorites = ujson.loads(favorites)
			if filter_key!='':
				favorites = favorites.get(filter_key,{})
		return JsonResponse({"status":"success","favorites":favorites})
	return JsonResponse({"status":"error","error_msg":"Unkown method"})

def set_alert_screener(request): 
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	url = "https://scan.streak.tech/api/set_alert"
	if request.method == 'POST':
		if not user_is_auth:
			return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)

		try:
			screener_uuid = request.POST.get('screener_uuid','')
			screener_logic = request.POST.get('screener_logic','')
			chart_type = request.POST.get('chart_type','')
			time_frame = request.POST.get('time_frame','')
			periodicity = request.POST.get('periodicity','')
			universe = request.POST.get('universe','')
			screener_name = request.POST.get('screener_name','')
			basket_name = request.POST.get('basket_name','')
			basket_symbols = request.POST.get('basket_symbols','')

			screener_logic = urllib.unquote(unicode(screener_logic).encode('utf-8'))
			screener_name = urllib.unquote(unicode(screener_name).encode('utf-8'))
			
			basket_symbols = urllib.unquote(unicode(basket_symbols).encode('utf-8'))
			
			payload = "user_uuid={}&screener_uuid={}&screener_logic={}&chart_type={}&time_frame={}&periodicity={}&universe={}&screener_name={}&basket_name={}&basket_symbols={}".format(user_uuid,screener_uuid,urllib.quote(screener_logic),chart_type,time_frame,periodicity,universe,urllib.quote(screener_name),basket_name,urllib.quote(basket_symbols))
			# payload  = urllib.quote(payload)
			headers = {
				'Content-Type': "application/x-www-form-urlencoded"
				}

			response = requests.request("POST", url, data=payload, headers=headers,timeout=45)
			# print response.text
			# print response.status_code
			print response.text,payload 
			if response.status_code!=200:
				return JsonResponse(ujson.loads(response.text))
			else:
				return JsonResponse({'status':"success"})
		except:
			print(traceback.format_exc())
			return JsonResponse({'status':"error","error_msg":"Unkown error"})
	return JsonResponse({'status':"error","error_msg":"Invalid method"})

def stop_screener_alert(request): 
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	url = "https://scan.streak.tech/api/stop_alert"
	if request.method == 'POST':
		if not user_is_auth:
			return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)

		try:
			alert_uuids = request.POST.get('alert_uuids',None)
			# print(alert_uuids)
			if not alert_uuids:
				return JsonResponse({'status':"error","error_msg":"Invalid scanner"})
			alert_uuids = ujson.loads(urllib.unquote(unicode(alert_uuids).encode('utf-8')))
			payload = {'alert_uuids':alert_uuids}
			headers = {
				'Content-Type': "application/json"
			}
			response = requests.request("POST", url, json=payload, headers=headers,timeout=5)
			# print response.text
			# print response.status_code
			# print response.text,payload 
			if response.status_code!=200:
				return JsonResponse(ujson.loads(response.text))
			else:
				resp = ujson.loads(response.text)
				resp['status']="success"
				return JsonResponse(resp)
		except:
			print(traceback.format_exc())
			return JsonResponse({'status':"error","error_msg":"Unkown error"})
	return JsonResponse({'status':"error","error_msg":"Invalid method"})

def get_alerts_screener(request): 
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	url = "https://scan.streak.tech/api/get_alerts"
	if request.method == 'POST':
		if not user_is_auth:
			return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)

		try:
			status = request.POST.get('status',0)
			
			payload = "user_uuid={}&status={}".format(user_uuid,status)
			# payload  = urllib.quote(payload)
			headers = {
				'Content-Type': "application/x-www-form-urlencoded"
				}

			response = requests.request("POST", url, data=payload, headers=headers,timeout=5)
			# print response.text
			# print response.status_code
			# print response.text,payload 
			if response.status_code!=200:
				return JsonResponse(ujson.loads(response.text))
			else:
				resp = ujson.loads(response.text)
				resp['status']="success"
				return JsonResponse(resp)
		except:
			return JsonResponse({'status':"error","error_msg":"Unkown error"})
	return JsonResponse({'status':"error","error_msg":"Invalid method"}) 

def get_screener_alert_history(request): 
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	url = "https://scan.streak.tech/api/get_alert_history"
	if request.method == 'POST':
		if not user_is_auth:
			return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)

		try:
			alert_uuid = request.POST.get('alert_uuid',None)
			if not alert_uuid:
				return JsonResponse({'status':"error","error_msg":"Invalid scanner"})
			payload = "alert_uuid={}".format(alert_uuid)
			# payload  = urllib.quote(payload)
			headers = {
				'Content-Type': "application/x-www-form-urlencoded"
				}

			response = requests.request("POST", url, data=payload, headers=headers,timeout=5)
			# print response.text
			# print response.status_code
			print response.text,payload 
			if response.status_code!=200:
				return JsonResponse(ujson.loads(response.text))
			else:
				resp = ujson.loads(response.text)
				resp['status']="success"
				return JsonResponse(resp)
		except:
			print(traceback.format_exc())
			return JsonResponse({'status':"error","error_msg":"Unkown error"})
	return JsonResponse({'status':"error","error_msg":"Invalid method"}) 
 
def load_screener_to_archive(request): 
  # http://127.0.0.1/load_screener_to_archive/?id=OWI1MTExN2QtY2EwNC00YTAyLWFhMGItNzE0NTliOGIyOWUz&secret=testing_initialization&tag=Break Out 
  try:  
	# if request.GET.get('secret','')!='testing_initialization': 
	#   con = get_redis_connection("default")  
	#   samples = con.get('user_samples')  
	#   bt_samples = []  
	#   if samples:  
	#	 samples = eval(samples) 
	# else: 
	if request.method=='GET': 
	  if request.GET.get('secret')=='testing_initialization': 
		sid = request.GET.get('id','') 
		key = base64.urlsafe_b64decode(str(sid)) 
		samples = {'samples': [[key, '', '']]} 
		 
		tag = request.GET.get('tag','') 
		 
		for s in samples['samples']: 
		  try:  
			screener_uuid = s[0] 
			screener = models.Screener.objects.get(screener_uuid=screener_uuid) 
			screener.sample = True 
			# backtest_metas = models.BacktestMeta.objects(screener_uuid=screener_uuid) 
			screener.tags.append(tag) 
			archive_entry = ujson.loads(screener.to_json()) 
 
			archive_entry['owner'] = screener.user_uuid 
 
			del archive_entry['screener_state'] 
			del archive_entry['_id'] 
			del archive_entry['screener_result'] 
			data = {"id":screener_uuid,'document':archive_entry} 
			archive_screener_function(data) 
 
			screener.save() 
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
 
def archive_screener_function(archive_entry,set_cron=True): 
  url = "https://s.streak.tech/screeners/" 
  headers = {"content-type":"application/json"} 
  payload = ujson.dumps(archive_entry) 
  try: 
	response = requests.request("POST", url, json=archive_entry, headers=headers,timeout=1) 
	# print response.text 
	# print response.status_code 
	print response.text,payload 
	if response.status_code!=200: 
	  print response.text,response.status_code 
	else: 
	  redis_con = get_redis_connection("default") 
	  verification = redis_con.get("application_access_token_cred")
	  if set_cron: 
	  	register_screener_cron(archive_entry['document']['screener_logic'], 
				  archive_entry['document']['time_frame'], 
				  archive_entry['document']['screener_uuid'], 
				  archive_entry['document']['chart_type'], 
				  verification,
				  archive_entry['document']['universe'].replace(" ","")
				  ) 
  except: 
	print traceback.format_exc() 
 
def register_screener_cron(screener_logic,time_frame,screener_uuid,chart_type,verification,scan_on): 
  url = "https://scan.streak.tech/api/add_popular" 
  headers = {'Content-Type': "application/x-www-form-urlencoded"}
  screener_logic = urllib.quote(screener_logic) 
  payload = "logic={}&time_frame={}&screener_uuid={}&verification={}&scan_on={}".format(screener_logic,screener_time_frame_mapping[time_frame],screener_uuid,verification,scan_on)
  try: 
	response = requests.request("POST",url, data=payload, headers=headers) 
	# print response.text 
	# print response.status_code 
	print 'register cron',response.text,payload 
	if response.status_code!=200: 
	  print response.text,response.status_code 
  except: 
	print traceback.format_exc()