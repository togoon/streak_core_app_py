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
import ujson
import math
from coreapp.views.utility import update_usage_util,update_usage_util_count
from backtest import fetch_instruments
from mongoengine import ValidationError,NotUniqueError

def view_calculator_(viewer_dict):
	now = datetime.datetime.now()
	hour = now.hour
	weekday = now.weekday()+1
	multiplier = (hour/12.0)
	if multiplier>1:
		multiplier -= 1
	multiplier /= 2.0
	viewer_list = viewer_dict.keys()
	count = 0
	con = get_redis_connection("default")
	live_veiws_dict = con.get("live_veiws_dict")
	if live_veiws_dict is not None and not (hour>8 and hour<9):
		live_veiws_dict = ujson.loads(live_veiws_dict)
		viewer_dict = live_veiws_dict.get("viewer_dict",{})
		viewer_list = viewer_dict.keys()
		last_time = int(live_veiws_dict.get('time',now.strftime("%s")))
		time_delta = random.gauss(0,float(int(now.strftime("%s"))-last_time)/3600.0)
		print("time_delta",time_delta)
		for v in viewer_list:
			count += 1
			viewer_dict[v]=abs(int(viewer_dict[v]+(multiplier*(1.0/count)*time_delta*abs(random.gauss(0,10)))))
			if weekday>5:
				viewer_dict[v] = int(viewer_dict[v]*random.random()/3.0)
	else:
		for v in viewer_list:
			count += 1
			viewer_dict[v]=int(random.randint(200,250)*multiplier*(1.0/count)*random.random()*abs(random.gauss(0,50)))
			if weekday>5:
				viewer_dict[v] = int(viewer_dict[v]*random.random()/3.0)
				
	con = con.set("live_veiws_dict",ujson.dumps({"time":now.strftime("%s"),"viewer_dict":viewer_dict}))
		
	return viewer_dict

def view_calculator(viewer_dict):
	now = datetime.datetime.now()
	hour = now.hour
	minute = now.minute
	weekday = now.weekday()+1
	multiplier = (hour/12.0)
	if multiplier>1:
		multiplier -= 1
	multiplier /= 2.0
	offset = (hour*60+minute)/720.0
	viewer_list = viewer_dict.keys()
	count = 0
	con = get_redis_connection("default")
	live_veiws_dict = con.get("live_veiws_dict")
	reset_random = random.randint(0,11111)
	increase = math.pi * 2 / 720;
	n = now.strftime("%s")
	if live_veiws_dict != None:
		try:
			live_veiws_dict_ = ujson.loads(live_veiws_dict)
			n = live_veiws_dict_.get("time",now.strftime("%s"))
		except:
			n = now.strftime("%s")

	if live_veiws_dict is not None and not (hour>8 and hour<9) or reset_random%17==0:
		live_veiws_dict = ujson.loads(live_veiws_dict)
		viewer_dict = live_veiws_dict.get("viewer_dict",{})
		viewer_list = viewer_dict.keys()
		last_time = int(live_veiws_dict.get('time',now.strftime("%s")))
		time_delta = random.gauss(0,float(int(now.strftime("%s"))-last_time)/3600.0)
		time_delta_ = float(int(now.strftime("%s"))-last_time)
		print("time_delta",time_delta)
		if time_delta_<60:
			for v in viewer_list:
				count += 1
				viewer_dict[v]=max(random.randint(1,15),abs(int(viewer_dict[v]+(multiplier*(1.0/count)*time_delta*random.gauss(0,8)))))
				# viewer_dict[v]=int((random.randint(100,150)+math.sin(increase*(multiplier+time_delta/720.0)+offset) / 2 + 500)*multiplier*(1.0/count)*abs(random.gauss(0,40)))
				if weekday>5:
					viewer_dict[v] = int(viewer_dict[v]*random.random()/3.0)
		else:
			n = now.strftime("%s")
			for v in viewer_list:
				count += 1
				viewer_dict[v]=int((random.randint(100,150)+math.sin(increase*multiplier+offset) / 2 + 500)*multiplier*(1.0/count)*abs(random.gauss(0,20)))

				if weekday>5:
					viewer_dict[v] = int(viewer_dict[v]*random.random()/3.0)
	else:
		for v in viewer_list:
			count += 1
			viewer_dict[v]=int((random.randint(100,150)+math.sin(increase*multiplier+offset) / 2 + 500)*multiplier*(1.0/count)*abs(random.gauss(0,40)))

			if weekday>5:
				viewer_dict[v] = int(viewer_dict[v]*random.random()/3.0)
	
	con = con.set("live_veiws_dict",ujson.dumps({"time":n,"viewer_dict":viewer_dict}))
		
	return viewer_dict

def marketplace(request):
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

	# if not user_is_auth:
	# 	if resp_json:
	# 		return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)
	# 	return redirect('home')
	if request.method == "GET":
		payload = request.GET
	elif request.method == "POST":
		payload = request.POST
	else:
		return JsonResponse({"status":"error","error":"Invalid method","error_msg":"Invalid method"},status=403)


	filter_dict = payload.get("filter",None)
	search = payload.get("search","")
	search_key = payload.get("search","")
	search_list = search.strip().split(" ")
	filter_tag = payload.get("filter_tag",None)

	all_tags = [
		"trend following",
		"price action",
		"mean reversion",
		"momentum",
		"miscellaneous",
		"pivot points",
		"overlays",
		"options strategies"
	]

	if filter_tag is None or filter_tag=="":
		filter_tag = all_tags+[""]
	else:
		filter_tag = [filter_tag]

	action_type = [1,-1]
	chart_type = ["candlestick","heikinashi","renko"]
	time_frame = ["min","3min","5min","10min","15min","30min","hour","day"]
	backtest_pnl = [-1000,1000]
	max_dd = [-100,100]
	favourite = False
	if filter_dict:
		filter_dict = urllib.unquote(filter_dict).decode('utf8') 
		print("filter_dict",filter_dict)
		filter_dict = ujson.loads(filter_dict)
		filter_map = {
			"overlays" : ["sma", "ema", "dema", "tema", "wma", "tma", "moving average", "ubb", "lbb", "mbb", "parabolic sar", "supertrend", "alligator"],
			"momentum" : ["rsi", "adx", "aroon", "macd", "cci", "mfi", "di", "willr", "trix", "proc", "mom", "stochastic", "trend", "cmo"],
			"volume" : [" obv", "volume"],
			"volatility" : [" natr", " tr ", " atr ", "vortex"],
			"price action" : ["number", "close", "open", "high", "low", "prev", "pivot", "opening range", "vwap"],
			"chart patterns" : ["morning", "kicking", "spinning", "engulfing", "homing", "soldiers", "abandoned", "tri star", "advance", "conceal", "stick"],
			"bullish":1,
			"bearish":-1,
			"backtest_pnl":[-1000,1000],
			"max_dd":[-100,100]
		}

		favourite = filter_dict.get('favourite',False)

		for i in filter_dict.get("entry_logic",[]):
			search_list += filter_map.get(i,[])
		for i in filter_dict.get("exit_logic",[]):
			search_list += filter_map.get(i,[])

		a_type = filter_dict.get("position_type",[])
		if filter_dict.get("position_type",None) is None:
			a_type = filter_dict.get("action_type",[])
		if len(a_type)!=0:
			t_a = []
			for a in a_type:
				if a == "bullish":
					t_a.append(1)
				else:
					t_a.append(-1)
			action_type = t_a

		c_type = filter_dict.get("chart_type",[])
		if len(c_type)!=0:
			c_type = [c.lower().replace("-a","A").split("(")[0] for c in c_type]
			chart_type = c_type

		t_type = filter_dict.get("time_frame",[])
		if len(t_type)!=0:
			time_frame = t_type

		b_pnl = filter_dict.get("backtest_pnl",[])
		if len(b_pnl)!=0:
			backtest_pnl = b_pnl

		m_dd = filter_dict.get("max_dd",[])
		if len(m_dd)!=0:
			max_dd = m_dd

	page_limit = int(payload.get('page_limit',10))
	page_num = int(payload.get('page',1))

	search = " ".join(search_list+chart_type)

	marketplace_obj = []
	marketplace_dict = {}
	# published_algos = models.PublishedAlgos._get_collection().find({"publish_status":{ "$in": [1,2]}},{ 'html_block':0,'_id':0,'algo_obj':0 }).sort([("updated_at",-1),("publish_status",-1)])

	print(chart_type,time_frame,action_type,search,filter_dict)
	if search!="" and len(search)>2 and filter_dict:
		print("search query 1",{"publish_status":{ "$in": [1,2]},"position_type":{ "$in": action_type},"time_frame":{ "$in": time_frame},"$text": { "$search": search },"tagged_class":{"$in":filter_tag}},{ 'html_block':0,'_id':0,'algo_obj':0 })
		published_algos = models.PublishedAlgos._get_collection().find({"publish_status":{ "$in": [1,2]},"position_type":{ "$in": action_type},"time_frame":{ "$in": time_frame},"$text": { "$search": search },"tagged_class":{"$in":filter_tag}},{ 'html_block':0,'_id':0,'algo_obj':0 }).sort([("updated_at",-1),("publish_status",-1)])
	elif filter_dict:
		print("search query 2")
		published_algos = models.PublishedAlgos._get_collection().find({"publish_status":{ "$in": [1,2]},"position_type":{ "$in": action_type},"time_frame":{ "$in": time_frame},"tagged_class":{"$in":filter_tag}},{ 'html_block':0,'_id':0,'algo_obj':0 }).sort([("updated_at",-1),("publish_status",-1)])
	else:
		print("search query 3")		
		published_algos = models.PublishedAlgos._get_collection().find({"publish_status":{ "$in": [1,2]},"position_type":{ "$in": action_type},"time_frame":{ "$in": time_frame},"tagged_class":{"$in":filter_tag}},{ 'html_block':0,'_id':0,'algo_obj':0 }).sort([("updated_at",-1),("publish_status",-1)])

	cur_i = 0
	viewer_dict = {}
	publisher_dict = {}

	subscribed_algos = models.SubscribedAlgos._get_collection().find({'user_uuid':user_uuid,"subscription_expiry":{ "$gt": datetime.datetime.now()},"subscription_status":1},{'_id':0 ,'algo_obj':0}).sort([("updated_at",-1)])
	subscribed_algos_list = []
	subscribed_algos_list_algo_uuid = {}
	for s in subscribed_algos:
		subscribed_algos_list.append([s["publishing_uuid"],s["algo_subscription_uuid"]])
		# Because when faving subscribed algo, algo_subscription_uuid is sent unlike algo_uuid in discover 
		subscribed_algos_list_algo_uuid[s["algo_uuid"]]=s["algo_subscription_uuid"]

	fav_obj = {}
	if favourite:
		con = get_redis_connection("default")
		# print("user_uuid",user_uuid)
		fav_obj = con.get("screener_favorites:"+user_uuid)
		# print(fav_obj)
		if fav_obj:
			fav_obj = ujson.loads(fav_obj).get('discover',{})

	for a in published_algos:
		viewer_dict[a["algo_uuid"]]=0
		a["algo_state"]={}
		a["algo_calc"]={}
		# if a['algo_uuid']=="b1a8e325-0c00-4763-97bd-d33360d6bf67":
		# 	print "b1a8e325-0c00-4763-97bd-d33360d6bf67"
		if search_key!="" and len(search_key)>2:
			if search_key not in a["algo_name"] and search_key not in a["algo_desc"] and search_key not in a["entry_logic"] and search_key not in a["exit_logic"]:
				continue
		if len(search_list)>1:
			p = False
			for s in search_list:
				if s!="" and s!=" ":
					if s not in a["algo_name"] and s not in a["algo_desc"] and s not in a["entry_logic"] and s not in a["exit_logic"]:
						p = False
					else:
						p = True
						break
			if not p:
				continue

		if favourite and fav_obj:
			# print(fav_obj.get(a.get("algo_uuid"),None),a.get("algo_uuid")) 
			# print(fav_obj,a.get("publishing_uuid"))
			# if subscribed_algos_list_algo_uuid.get(a.get("algo_uuid"),None) is not None:
			# 	# print(subscribed_algos_list_algo_uuid.get(a.get("algo_uuid"),None),fav_obj.get(subscribed_algos_list_algo_uuid.get(a.get("algo_uuid"),None),None))
			# 	if fav_obj.get(subscribed_algos_list_algo_uuid.get(a.get("algo_uuid"),None),None) is None:
			# 		# print("continue-->2",a["algo_name"])
			# 		continue
			# else:
			if fav_obj.get(a.get("algo_uuid"),None) is None:
				# print("continue-->2",a["algo_name"])
				continue
				
		marketplace_obj.append(a)
		# print(a["algo_name"],a["algo_uuid"],search_key)

		marketplace_dict[a['algo_uuid']]=a


	viewer_dict = view_calculator(viewer_dict)
	con = get_redis_connection("default")
	market_place_sorted_list_time = datetime.datetime.now()
	if (market_place_sorted_list_time.hour>0 and market_place_sorted_list_time.hour<2 or random.randint(0,1001)%500==0):
		vd_sorted = sorted(viewer_dict.items(), key = lambda x: x[1],reverse=True)	
		con.set("market_place_sorted_list",ujson.dumps(vd_sorted))
	else:
		market_place_sorted_list = con.get("market_place_sorted_list")
		if market_place_sorted_list:
			vd_sorted = ujson.loads(market_place_sorted_list)
		else:
			vd_sorted = sorted(viewer_dict.items(), key = lambda x: x[1],reverse=True)
			con.set("market_place_sorted_list",ujson.dumps(vd_sorted))

	marketplace_obj2=[]
	total_algo_count = 0
	viewer_dict_to_return = {}
	for v in vd_sorted:
		a = marketplace_dict.get(v[0],None)
		if a is not None:
			if(max(0,page_num-1)*page_limit<=cur_i<max(0,page_num-1)*page_limit+page_limit):
				# backtest = models.PublishedBacktestsMeta._get_collection().find({'algo_uuid':a['algo_uuid'],"backtest_result_meta.returns":{"$gte":backtest_pnl[1],"$lte":backtest_pnl[0]},"backtest_result_meta.max_draw":{"$gte":max_dd[1],"$lte":max_dd[0]}},{'_id':0 ,'algo_obj':0}).sort([("backtest_result_meta.returns",-1)])
				backtest = models.PublishedBacktestsMeta._get_collection().find({'algo_uuid':a['algo_uuid']},{'_id':0 ,'algo_obj':0}).sort([("backtest_result_meta.returns",-1)])

				b_list = []
				avg_return_pct = 0
				avg_return = 0
				absolute_pnl = 0
				absolute_pnl_pct = 0
				avg_win_loss_ratio = 0.0
				avg_winning_streak = 0
				avg_lossing_streak = 0
				sym_count = 0
				sym_pnl = []
				sym_max_cap_used = []

				for b in backtest:	
					# TODO Remove algo condition related objects
					sym_count = sym_count + 1
					k = b["seg_sym"]
					if k in b["backtest_result"].keys():
						sym_pnl.append(b["backtest_result"][k]["final_pnl"])
						sym_max_cap_used.append(b["backtest_result"][k]["max_cap_used"])
						avg_winning_streak = avg_winning_streak+int(b["backtest_result"][k]["winning_streak"])
						avg_lossing_streak = avg_lossing_streak+int(b["backtest_result"][k]["lossing_streak"])
						try:
							avg_win_loss_ratio = avg_win_loss_ratio+float(b["backtest_result"][k]["average_gain_per_winning_trade"])/abs(float(b["backtest_result"][k]["average_gain_per_losing_trade"]))
						except:
							pass
					b_list.append(b)

				if len(sym_pnl)>0 and sum(sym_max_cap_used)>0:
					absolute_pnl_pct = (sum(sym_pnl)/sum(sym_max_cap_used))*100
					absolute_pnl = sum(sym_pnl)
					avg_winning_streak = avg_winning_streak/float(sym_count)
					avg_lossing_streak = avg_lossing_streak/float(sym_count)
					avg_win_loss_ratio = avg_win_loss_ratio/float(sym_count)
					
				if len(b_list)>0:
					a['backtest'] = b_list

				a["absolute_pnl"]=absolute_pnl
				a["absolute_pnl_pct"]=absolute_pnl_pct
				a["avg_winning_streak"]=avg_winning_streak
				a["avg_lossing_streak"]=avg_lossing_streak
				a["avg_win_loss_ratio"]=avg_win_loss_ratio
						
				marketplace_obj2.append(a)
				viewer_dict_to_return[a["algo_uuid"]]=viewer_dict.get(a["algo_uuid"],0)
			cur_i += 1
			total_algo_count = total_algo_count+1
		# marketplace_dict[a['algo_uuid']]=a
		# if a is not None:
			# if len(a.get('backtest',[]))>0:
				# marketplace_obj.append(a)

	subscribed_algos_deployed = models.DeployedAlgorithm._get_collection().find({'user_uuid':user_uuid,"expiration_time":{ "$gt": datetime.datetime.now()},"explore_algo":True},{'_id':0 }).sort([("updated_at",-1)])
	subscribed_algos_deployed_list = []
	for d in subscribed_algos_deployed:
		subscribed_algos_deployed_list.append([d["algo_uuid"],d["segment_symbol"]])

	publishers = models.PublisherBio._get_collection().find({"user_uuid":{"$in":publisher_dict.keys()}},{"user_uuid":1,"publisher_name":1,"publisher_bio":1,"_id":0})

	for p in publishers:
		publisher_dict[p["user_uuid"]]={"publisher_name":p["publisher_name"],"publisher_bio":p["publisher_bio"]}

	if(payload.get('resp','')=='json'):
		# print algo_batch
		# return JsonResponse({'algo':marketplace_obj[max(0,page_num-1)*page_limit:max(1,page_num)*page_limit],'pages':int(math.ceil(len(marketplace_obj)/(page_limit*1.0))),'status':'success',"subscribed_algos":subscribed_algos_list,"subscribed_algos_deployed":subscribed_algos_deployed_list,"viewer_dict":viewer_dict})
		return JsonResponse({'algo':marketplace_obj2[0:page_limit],'pages':int(math.ceil(total_algo_count/(page_limit*1.0))),'status':'success',"subscribed_algos":subscribed_algos_list,"subscribed_algos_deployed":subscribed_algos_deployed_list,"viewer_dict":viewer_dict_to_return,"publisher_details":publisher_dict,"all_tags":all_tags})
	# elif resp_json:
		# return JsonResponse({'algo':marketplace_obj[max(0,page_num-1)*page_limit:max(1,page_num)*page_limit],'pages':int(math.ceil(len(marketplace_obj)/(page_limit*1.0))),'status':'success',"subscribed_algos":subscribed_algos_list,"subscribed_algos_deployed":subscribed_algos_deployed_list,"viewer_dict":viewer_dict})
	return JsonResponse({'algo':marketplace_obj2[0:page_limit],'pages':int(math.ceil(total_algo_count/(page_limit*1.0))),'status':'success',"subscribed_algos":subscribed_algos_list,"subscribed_algos_deployed":subscribed_algos_deployed_list,"viewer_dict":viewer_dict_to_return,"publisher_details":publisher_dict,"all_tags":all_tags})

def submit_for_publication(request):
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
		if resp_json:
			return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)
		return redirect('home')
	if request.method=='POST':
		payload = request.POST
		algo_uuid = payload.get('algo_uuid',"")
		algo_desc = payload.get('publishing_note',"")
		algo_name = payload.get('publishing_name',"")
		tagged_class = payload.get('publishing_class',"").lower()
		pricing = payload.get('pricing',"0")
		public = payload.get('public',False)

		if public == 'false':
			public = False
		elif public == 'true':
			public = True

		try:
			if user_uuid == "eff87bd6-bbec-4db5-809c-740b0a828253":
				algorithm_item = models.Algorithm.objects.get(
					algo_uuid = algo_uuid
					)
				user_uuid = algorithm_item.user_uuid
			else:
				algorithm_item = models.Algorithm.objects.get(
					algo_uuid = algo_uuid,
					user_uuid = user_uuid
					)
			publishing_uuid = str(uuid.uuid4())
			
			algo_obj = {}
			backtests = models.Backtest._get_collection().find({'user_uuid':user_uuid,'algo_uuid':algorithm_item.algo_uuid},{'_id':0})
			for pb in backtests:
				try:
					algo_obj = pb['algo_obj']
					algo_obj['algo_name'] = algo_name
					algo_obj['public'] = public
					algo_obj['algo_desc'] = algo_desc
					algo_obj['published_algo'] = True
					# algo_obj.pop
					published_backtest=models.PublishedBacktests(
						user_uuid=user_uuid,
						publishing_uuid=publishing_uuid,
						algo_uuid=pb['algo_uuid'],
						seg_sym=pb['seg_sym'],
						backtest_result=pb['backtest_result'],
						algo_obj=algo_obj,
						runtime=pb['runtime']
						)
					published_backtest.save()
				except:
					print(traceback.format_exc())

			backtests_meta = models.BacktestMeta._get_collection().find({'user_uuid':user_uuid,'algo_uuid':algorithm_item.algo_uuid},{'_id':0})
			for pb in backtests_meta:
				try:
					algo_obj = pb['algo_obj']
					algo_obj['algo_name'] = algo_name
					algo_obj['public'] = public
					algo_obj['algo_desc'] = algo_desc
					algo_obj['published_algo'] = True
					# algo_obj.pop
					published_backtest=models.PublishedBacktestsMeta(
						user_uuid=user_uuid,
						publishing_uuid=publishing_uuid,
						algo_uuid=pb['algo_uuid'],
						seg_sym=pb['seg_sym'],
						backtest_result=pb['backtest_result'],
						algo_obj=algo_obj,
						runtime=pb['runtime'],
						backtest_result_meta = pb['backtest_result_meta']
						)
					published_backtest.save()
				except:
					print(traceback.format_exc())
			if algo_obj!={}:
				published_algo = models.PublishedAlgos(
					algo_name = algo_name,
					algo_desc = algo_desc,
					user_uuid = algorithm_item.user_uuid,
					algo_uuid = algorithm_item.algo_uuid,
					publishing_uuid = publishing_uuid,
					time_frame = algorithm_item.time_frame,
					symbols = algorithm_item.symbols, # symbols which are part of the stategy logic
					position_type = algorithm_item.position_type,
					entry_logic = algorithm_item.entry_logic,
					exit_logic = algorithm_item.exit_logic,
					quantity = algorithm_item.quantity,
					take_profit = algorithm_item.take_profit,
					stop_loss = algorithm_item.stop_loss,
					create_plus = algorithm_item.create_plus,
					# advanced fields
					holding_type = algorithm_item.holding_type,
					min_candle_freq = algorithm_item.min_candle_freq,
					chart_type = algorithm_item.chart_type,
					trade_time_given = algorithm_item.trade_time_given,
					trading_start_time = algorithm_item.trading_start_time,
					trading_stop_time = algorithm_item.trading_stop_time,
					algo_state = algorithm_item.algo_state,
					# algo_calc = algorithm_item.algo_calc,
					subscription_price = {"monthly_pricing":float(pricing)},
					algo_obj=algo_obj,
					tagged_class=tagged_class,
					public = public
					)
				if public:
					published_algo.algo_state = algorithm_item.algo_state
				published_algo.save()
			else:
				return JsonResponse({"status":"error","error_msg":"No backtest found, error publishing, please contact support@streak.world"})

			return JsonResponse({"status":"success","msg":"Content successfully submited to review, our team will reach out to you"})
		except:
			print(traceback.format_exc())
			return JsonResponse({"status":"error","error":"Error publishing, please reach out to us at support@streak.world","error_msg":"Error publishing, please reach out to us at support@streak.world"},status=403)

	return JsonResponse({"status":"error","error":"Invalid method","error_msg":"Invalid method"},status=403)

def fetch_backtest_chart(request):
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
		if resp_json:
			return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)
		return redirect('home')

	if request.method=='GET':
		algo_uuid = request.GET.get('algo_uuid','')
		publishing_uuid = request.GET.get('publishing_uuid','')
		algo_subscription_uuid = request.GET.get('algo_subscription_uuid','')
		max_count = int(request.GET.get('max_count',250))
		seg_sym = request.GET.get('seg_sym',"")
		tl = request.GET.get('tl',"false")
		if (algo_uuid!=''):
			try:
				avg_return_pct = 0
				avg_return = 0
				absolute_pnl = 0
				absolute_pnl_pct = 0
				sym_count = 0
				sym_pnl = []
				sym_max_cap_used = []
				pb = models.Backtest._get_collection().find({'user_uuid':user_uuid,"algo_uuid":algo_uuid},{'_id':0 ,'algo_obj':0})
				pb_resp = []
				for b in pb:
					if seg_sym!=b["seg_sym"] and seg_sym!="":
						continue
					k = b["seg_sym"]
					if k in b["backtest_result"].keys():
						if max_count==-1 or tl == "true":
							pass
						elif max_count == -2:	
							b["backtest_result"][k]["pnl"] = []
						else:
							b["backtest_result"][k]["pnl"]=downsample(b["backtest_result"][k]["pnl"],max_count)
							z = b["backtest_result"][k].pop("trade_log","")
						sym_count = sym_count + 1
						
						sym_pnl.append(b["backtest_result"][k]["final_pnl"])
						sym_max_cap_used.append(b["backtest_result"][k]["max_cap_used"])

						pb_resp.append(b)
				# return JsonResponse({"status":"success","backtests":pb_resp})
				if len(sym_pnl)>0 and sum(sym_max_cap_used)>0:
					absolute_pnl_pct = (sum(sym_pnl)/sum(sym_max_cap_used))*100
					absolute_pnl = sum(sym_pnl)
				return JsonResponse({"status":"success","backtests":pb_resp,"absolute_pnl":absolute_pnl,"absolute_pnl_pct":absolute_pnl_pct})
			except:
				print(traceback.format_exc())
				return JsonResponse({"status":"error","error_msg":"Unkown error"})
		# elif (algo_subscription_uuid!=''):
		# 	try:
		# 		pb = models.SubscribeAlgoBacktest._get_collection().find({'algo_subscription_uuid':algo_subscription_uuid},{'_id':0 ,'algo_obj':0})
		# 		pb_resp = []
		# 		for b in pb:
		# 			pb_resp.append(b)

		# 		return JsonResponse({"status":"success","backtests":pb_resp})
		# 	except:
		# 		print(traceback.format_exc())
		# 		return JsonResponse({"status":"error","error_msg":"Unkown error"})
		else:
			return JsonResponse({"status":"error","error_msg":"Invalid Strategy"})
	
	return JsonResponse({"status":"error","error_msg":"Invalid method"})

def fetch_marketplace_chart(request):
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

	# if not user_is_auth:
	# 	if resp_json:
	# 		return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)
	# 	return redirect('home')

	if request.method=='GET':
		publishing_uuid = request.GET.get('publishing_uuid','')
		algo_subscription_uuid = request.GET.get('algo_subscription_uuid','')
		max_count = int(request.GET.get('max_count',250))
		seg_sym = request.GET.get('seg_sym',"")
		tl = request.GET.get('tl',"false")
		st = time.time()
		if (publishing_uuid!=''):
			try:
				pb = models.PublishedBacktests._get_collection().find({'publishing_uuid':publishing_uuid},{'_id':0 ,'algo_obj':0})
				avg_return_pct = 0
				avg_return = 0
				absolute_pnl = 0
				absolute_pnl_pct = 0
				sym_count = 0
				sym_pnl = []
				sym_max_cap_used = []
				pb_resp = []
				for b in pb:
					if seg_sym!=b["seg_sym"] and seg_sym!="":
						continue
					k = b["seg_sym"]
					if k in b["backtest_result"].keys():
						if max_count==-2:
							z = b["backtest_result"][k].pop("pnl","")
						elif max_count==-1 or tl == "true":
							pass
						else:	
							b["backtest_result"][k]["pnl"]=downsample(b["backtest_result"][k]["pnl"],max_count)
							z = b["backtest_result"][k].pop("trade_log","")
						sym_count = sym_count + 1
						
						sym_pnl.append(b["backtest_result"][k]["final_pnl"])
						sym_max_cap_used.append(b["backtest_result"][k]["max_cap_used"])

						pb_resp.append(b)
				print('time ------>',time.time()-st)
				# return JsonResponse({"status":"success","backtests":pb_resp})
				if len(sym_pnl)>0 and sum(sym_max_cap_used)>0:
					absolute_pnl_pct = (sum(sym_pnl)/sum(sym_max_cap_used))*100
					absolute_pnl = sum(sym_pnl)
				return JsonResponse({"status":"success","backtests":pb_resp,"absolute_pnl":absolute_pnl,"absolute_pnl_pct":absolute_pnl_pct})
			except:
				print(traceback.format_exc())
				return JsonResponse({"status":"error","error_msg":"Unkown error"})
		elif (algo_subscription_uuid!=''):
			try:
				pb = models.SubscribeAlgoBacktest._get_collection().find({'algo_subscription_uuid':algo_subscription_uuid},{'_id':0 ,'algo_obj':0})
				avg_return_pct = 0
				avg_return = 0
				absolute_pnl = 0
				absolute_pnl_pct = 0
				sym_count = 0
				sym_pnl = []
				sym_max_cap_used = []
				pb_resp = []	
				pb_resp = []
				for b in pb:
					if seg_sym!=b["seg_sym"] and seg_sym!="":
						continue
					k = b["seg_sym"]
					if k in b["backtest_result"].keys():
						if max_count==-2:
							z = b["backtest_result"][k].pop("pnl","")
						elif max_count==-1 or tl == "true":
							pass
						else:
							b["backtest_result"][k]["pnl"]=downsample(b["backtest_result"][k]["pnl"],max_count)
							z = b["backtest_result"][k].pop("trade_log","")
						sym_count = sym_count + 1
						
						sym_pnl.append(b["backtest_result"][k]["final_pnl"])
						sym_max_cap_used.append(b["backtest_result"][k]["max_cap_used"])

						pb_resp.append(b)
				print('time ------>',time.time()-st)
				# return JsonResponse({"status":"success","backtests":pb_resp})
				if len(sym_pnl)>0 and sum(sym_max_cap_used)>0:
					absolute_pnl_pct = (sum(sym_pnl)/sum(sym_max_cap_used))*100
					absolute_pnl = sum(sym_pnl)
				return JsonResponse({"status":"success","backtests":pb_resp,"absolute_pnl":absolute_pnl,"absolute_pnl_pct":absolute_pnl_pct})
			except:
				print(traceback.format_exc())
				return JsonResponse({"status":"error","error_msg":"Unkown error"})
		else:
			return JsonResponse({"status":"error","error_msg":"Invalid publication"})
	
	return JsonResponse({"status":"error","error_msg":"Invalid method"})
# def downsample(pnl,max_count=1000.0):
# 	pnl_col = zip(*pnl)
# 	step = int(len(pnl)/max_count)
# 	pnl_new = []
# 	max_count_float = float(max_count)
# 	max_count = int(max_count)
# 	if len(pnl)<1000:
# 		return pnl
# 	for i in xrange(0,len(pnl)):
# 		if len(pnl_col)>2:
# 			pnl_new.append([pnl_col[0][i],max(pnl_col[1][i:i+step]),max(pnl_col[2][i:i+step])])
# 		else:
# 			pnl_new.append([pnl_col[0][i],max(pnl_col[1][i:i+step])])
# 		i+=step
# 	return pnl_new
def downsample(pnl,max_count=250.0):
	if pnl is None:
		return []
	# print(pnl,type(pnl))
	pnl_col = zip(*pnl)
	step = int(len(pnl)/max_count)
	pnl_new = []
	max_count_float = float(max_count)
	max_count = int(max_count)
	if len(pnl)<250:
		return pnl
	# print("downsample size",step,len(pnl))
	i = 0 
	try:
		for i in xrange(0,max_count):
			# d_len = len(pnl_col[1][i*step+max_count:i+max_count+step])
			# if d_len==0:
			if len(pnl_col)>2:
				# print("------",len(pnl_col[2][i*max_count:i*max_count+step]))
				pnl_new.append([pnl_col[0][i],sum(pnl_col[1][i*step:i*step+step])/len(pnl_col[1][i*step:i*step+step]),sum(pnl_col[2][i*step:i*step+step])/len(pnl_col[2][i*step:i*step+step])])
			else:
				pnl_new.append([pnl_col[0][i],sum(pnl_col[1][i*step:i*step+step])/len(pnl_col[1][i*step:i*step+step])])
		# if len(pnl)%max_count>0:
		# 	if len(pnl_col)>2:
		# 		pnl_new.append([pnl_col[0][i+1],sum(pnl_col[1][i*(max_count+1):i*(max_count+1)+step])/len(pnl_col[1][i*(max_count+1):i*(max_count+1)+step]),sum(pnl_col[2][i*(max_count+1):i*(max_count+1)+step])/len(pnl_col[2][i*(max_count+1):i*(max_count+1)+step])])
		# 	else:
		# 		pnl_new.append([pnl_col[0][i+1],sum(pnl_col[1][i*(max_count+1):i*(max_count+1)+step])/len(pnl_col[1][i*(max_count+1):i*(max_count+1)+step])])
			# i+=step
	except:
		print(i*step,i*step+step,len(pnl))
		print(traceback.format_exc())
	# print("downsample size",count)
	return pnl_new
	
def clone_published(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({'status':'error'})

	if request.method == 'POST':
		publishing_uuid = request.POST.get('publishing_uuid','')
		algo_name = request.POST.get('algo_name','')

		if publishing_uuid == '':
			return JsonResponse({'status':'error','error':'Strategy not present'})

		try:
			algo = models.PublishedAlgos.objects.get(
					publishing_uuid = publishing_uuid
					)
			
			cloned_algo_uuid = str(uuid.uuid4())

			algorithm_item = models.Algorithm(
								algo_name = algo_name,
								algo_desc = algo.algo_desc,
								user_uuid = user_uuid,
								algo_uuid = cloned_algo_uuid,
								entry_logic = algo.entry_logic,
								exit_logic = algo.exit_logic,
								symbols = algo.symbols, # symbols which are part of the stategy logic
								position_type = algo.position_type,
								quantity = algo.quantity,
								take_profit = algo.take_profit,
								stop_loss = algo.stop_loss,
								time_frame = algo.time_frame,
								# advanced fields
								holding_type = algo.holding_type,
								chart_type = algo.chart_type,		
								trade_time_given = algo.trade_time_given,
								trading_start_time = algo.trading_start_time,
								trading_stop_time = algo.trading_stop_time,
								algo_state=algo.algo_state,
								create_plus=algo.create_plus,
								#-----------------#
								html_block = "",
								owner=algo.user_uuid
								)

			algorithm_item['algo_state']['algo_name']=algo_name
			algorithm_item.save()
			# pbo = models.PublishedBacktestsMeta._get_collection().find({'publishing_uuid':publishing_uuid},{'_id':0}).sort([("updated_at",-1)]).limit(1)
			# db.published_backtests_meta.find().sort({"created_at":-1}).limit(1)
			scripList = []

			# print(pbo["algo_obj"]['scripList'])

			pb = models.PublishedBacktests._get_collection().find({'publishing_uuid':publishing_uuid},{'_id':0})
			for b in pb:
				b["algo_obj"]["algo_name"]=algo_name
				b["algo_obj"]["user_uuid"]=user_uuid
				b["algo_obj"]["algo_uuid"]=cloned_algo_uuid
				sb = models.Backtest(
					user_uuid=user_uuid,
					algo_uuid=cloned_algo_uuid,
					# publishing_uuid=b["publishing_uuid"],
					# algo_subscription_uuid=algo_subscription_uuid,
					seg_sym=b["seg_sym"],
					backtest_result=b["backtest_result"],
					algo_obj=b["algo_obj"],
					runtime=b["runtime"]
					)
				sb.save()

			pbm = models.PublishedBacktestsMeta._get_collection().find({'publishing_uuid':publishing_uuid},{'_id':0})
			for b in pbm:
				b["algo_obj"]["algo_name"]=algo_name
				b["algo_obj"]["user_uuid"]=user_uuid
				b["algo_obj"]["algo_uuid"]=cloned_algo_uuid
				seg_sym = b["seg_sym"].split("_")
				scripList.append({"symbol":seg_sym[1],"segment":seg_sym[0]})
				sbm = models.BacktestMeta(
					user_uuid=user_uuid,
					algo_uuid=cloned_algo_uuid,
					# publishing_uuid=b["publishing_uuid"],
					# algo_subscription_uuid=algo_subscription_uuid,
					seg_sym=b["seg_sym"],
					backtest_result=b["backtest_result"],
					algo_obj=b["algo_obj"],
					runtime=b["runtime"]
					)
				sbm.save()

			if len(scripList)>0:
				algorithm_item['algo_state']['scripList'] = scripList
			algorithm_item.save()

			return JsonResponse({'algo_uuid':cloned_algo_uuid,
							'status':'success'})

		except models.Algorithm.DoesNotExist:
			# TODO log error
			# if settings.DEBUG:
			print traceback.format_exc()
			return JsonResponse({'status':'error','error':'Strategy not present'})
		except NotUniqueError:
			print traceback.format_exc()
			return JsonResponse({'status':'error','error':'Strategy name already used'})

	return JsonResponse({'status':'error','error':'This sample algo has already been used'})

def marketplace_backtest(request):
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

	# if not user_is_auth:
	# 	if resp_json:
	# 		return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)
	# 	return redirect('home')
	if request.method=='GET':
		publishing_uuid = request.GET.get('publishing_uuid','')
		algo_subscription_uuid = request.GET.get('algo_subscription_uuid','')
		max_count = int(request.GET.get('max_count',-1))
		if (publishing_uuid=='' and algo_subscription_uuid==""):
			return JsonResponse({"status":"error","error":"Invalid publication"})
		try:
			con = get_redis_connection("default")
			usage = con.get('daily_usage:'+user_uuid)
			if usage:
				u = eval(usage)
				plans = {"free":20,"basic":200,"premium":500,"ultimate":1000}
				user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
				if u.get("backtest",-1)>plans.get(user_subscription.subscription_plan,0)+50:
					if user_subscription.subscription_plan==0:
						return JsonResponse({"status":"error","error":"Kindly upgraded to any of our paid plans as you have reached daily limit.","error_msg":"Kindly upgraded to any of our paid plans as you have reached daily limit."})
					return JsonResponse({"status":"error","error":"Backtest daily limit reached, please upgrade to higher plan","error_msg":"Backtest daily limit reached, please upgrade to higher plan"})

		except:
			print(traceback.format_exc())

		try:
			st = time.time()
			published_algo = None
			backtest_item = None
			backtest_count = 0
			publisher_name = ""
			publisher_bio = ""
			publisher_img_url = ""
			if publishing_uuid!="":
				published_algo = models.PublishedAlgos.objects.get(publishing_uuid = publishing_uuid)
				
				# if published_algo.status<1 and published_algo.user_uuid!=user_uuid:
				# 	return JsonResponse({"status":"error","error":"Algo not accessible"})

				backtest_item = models.PublishedBacktests.objects(
							publishing_uuid = publishing_uuid
							)
				
				backtest_count = models.PublishedBacktests.objects(publishing_uuid = publishing_uuid).count()
			else:
				published_algo = models.SubscribedAlgos.objects.get(user_uuid=user_uuid,algo_subscription_uuid = algo_subscription_uuid)
				publishing_uuid = published_algo.publishing_uuid
				if published_algo.user_uuid!=user_uuid:
					return JsonResponse({"status":"error","error":"Strategy not accessible"})

				backtest_item = models.SubscribeAlgoBacktest.objects(user_uuid=user_uuid,
							algo_subscription_uuid = algo_subscription_uuid
							)
				
				backtest_count = models.SubscribeAlgoBacktest.objects(user_uuid=user_uuid,algo_subscription_uuid = algo_subscription_uuid).count()
				

			try:
				if published_algo is not None:
					try:
						publisher = models.PublisherBio.objects.get(user_uuid=published_algo.user_uuid)
						publisher_name = publisher.publisher_name
						publisher_bio = publisher.publisher_bio
						publisher_img_url = publisher.publisher_img_url
					except:
						pass
				if request.GET.get('publishing_uuid','')=='':
					# feth
					original_published_algo = models.PublishedAlgos.objects.get(publishing_uuid=publishing_uuid)
					# added vote to backtest response
					upvotes = original_published_algo.upvotes
					downvotes = original_published_algo.downvotes
					score = original_published_algo.score
					view_count = original_published_algo.total_views
				elif request.GET.get('publishing_uuid','')!='' and published_algo is not None:
					upvotes = published_algo.upvotes
					downvotes = published_algo.downvotes
					score = published_algo.score
					view_count = published_algo.total_views
					published_algo.total_views = published_algo.total_views+1
					published_algo.save()
			except:
				print(traceback.format_exc())
				pass

			print '...............................',time.time()-st,backtest_count
			if backtest_count<1:
				print 'yoooooo'
			else:
				try:
					if request.GET.get('resp')=="json":
						update_usage_util_count(user_uuid,'backtest',1)
						update_usage_util_count(user_uuid,'view_backtest',backtest_count)
					pass
				except:
					print traceback.format_exc()

			backtest_0 = backtest_item[0]
			print '--########-----##########--',time.time()-st
			algo_name = published_algo.algo_name

			print '--########-----####---######--',time.time()-st
			algo_desc = published_algo.algo_desc
			position_type = backtest_0.algo_obj['action_type']
			position_qty = backtest_0.algo_obj['quantity']
			entry_logic = backtest_0.algo_obj['action_str']
			# exit_logic = backtest_item.algo_obj['exit_logic']
			exit_logic = backtest_0.algo_obj.get('action_str_exit','')
			take_profit = backtest_0.algo_obj['take_profit']
			stop_loss = backtest_0.algo_obj['stop_loss']
			ip_interval = backtest_0.algo_obj['time_frame']
			holding_type = backtest_0.algo_obj.get('holding_type','MIS')
			create_plus = backtest_0.algo_obj.get('create_plus',False)
			# advanced parameters
			chart_type = backtest_0.algo_obj.get('chart_type','candlestick')
			trade_time_given = backtest_0.algo_obj.get('trade_time_given',"False")
			trading_start_time = backtest_0.algo_obj.get('trading_start_time','00:00')
			trading_stop_time = backtest_0.algo_obj.get('trading_stop_time','23:59')
			#--------------------#

			start_time = backtest_0.algo_obj['dt_start']
			stop_time = backtest_0.algo_obj['dt_stop']
			
			try:
				min_candle_freq = backtest_0.algo_obj['min_candle_freq']
			except:
				min_candle_freq = 1000
			equities = []
			print '--##################--',time.time()-st
			#for bt in backtest_item:
			#	for k in bt.algo_obj['symbols']: 
			#		equities.append(k[0]+'_'+k[1])
			backtest_items_json = ujson.loads(backtest_item.to_json())
			backtest_items_list = []
			equities = {}
			scripList = []
			for bt in backtest_items_json:
				for k in bt['algo_obj']['symbols']:
					print("kkkkk",k)
					equities[k[1]]=k[0]
					scripList.append({"symbol":k[1],"segment":k[0]})
				k2 = bt["seg_sym"]
				if k2 in bt["backtest_result"].keys():
					if max_count==-3:
						bt["backtest_result"][k2]["pnl"] = []
						bt["backtest_result"][k2]["trade_log"] = []
					elif max_count==-1:
						pass
					elif max_count == -2:	
						bt["backtest_result"][k2]["pnl"] = []
					else:
						bt["backtest_result"][k2]["pnl"]=downsample(bt["backtest_result"][k2]["pnl"],max_count)
				backtest_items_list.append(bt)

			if len(backtest_items_list)>0:
				backtest_items_list[0]["algo_obj"]["scripList"]=scripList
				backtest_items_list[len(backtest_items_list)-1]["algo_obj"]["scripList"]=scripList
			print '-------------------------',time.time()-st
			# { "dt_stop" : "10/08/2017", "stop_loss" : "4.0", "algo_uuid" : "4fcc3234-d02f-4cbb-8cb1-b35d353b8971", "initial_capital" : "100000", "time_frame" : "hour", "user_uuid" : "123", "dt_start" : "10/08/2016", "symbols" : [ [ "NSE", "HDFCBANK" ] ], "commission" : 0, "action_type" : "BUY", "take_profit" : "4.0", "action_str" : "2 min SMA higher than 4 min SMA", "algo_name" : "Cloned from ABC", "algo_desc" : "aaaa", "quantity" : "10" }
			# redis_con = get_redis_connection("default")
			algo_subscribed = False
			algo_deployed=False
			deployed_seg_sym = []
			deployed_seg_sym_deployment_uuid = {}

			if algo_subscription_uuid!="" and user_uuid!='':
				redis_con = get_redis_connection("default")

				algo_deployed=False
				deployed_seg_sym = []
				deployed_seg_sym_deployment_uuid = {}
				# res = redis_con.keys('deployed:'+user_uuid+':'+algo_subscription_uuid+':*')
				deployed_algos_mongo = models.DeployedAlgorithm._get_collection().find({"user_uuid":user_uuid,"algo_uuid":algo_subscription_uuid,"status":0,"expiration_time":{"$gte":datetime.datetime.now()}})

				deployed_algo = []
				for a in deployed_algos_mongo:
					x = [a["user_uuid"],a["algo_uuid"],a["segment_symbol"],a["algo_obj"]["time_frame"],a["deployment_uuid"]]
					dkey = 'deployed:'+":".join(x)
					deployed_algo.append(dkey)
				res = deployed_algo
				if len(res)>0:
					algo_deployed=True
					for k in res:
						k = k.split(':')
						deployed_seg_sym.append(k[3])
						deployed_seg_sym_deployment_uuid[k[3]] = k[-1]
				algo_subscribed = True

			if publishing_uuid!="" and user_uuid!='':
				sb = models.SubscribedAlgos._get_collection().find({'user_uuid':user_uuid,"publishing_uuid":publishing_uuid,"subscription_expiry":{ "$gt": datetime.datetime.now()}},{'_id':0 })
				sb_list = []
				for s in sb:
					sb_list.append(s)

				# print "subscriber algo count",sb
				if len(sb_list)>0:
					algo_subscribed = True
					algo_subscription_uuid = sb_list[-1]['algo_subscription_uuid']
				# try:
				# 	if published_algo is not None:
				# 		publisher = models.PublisherBio.objects.get(user_uuid=published_algo.user_uuid)
				# 		publisher_name = publisher.publisher_name
				# 		publisher_bio = publisher.publisher_bio
				# 		publisher_img_url = publisher.publisher_img_url
					
				# 	if request.GET.get('publishing_uuid','')=='':
				# 		# feth
				# 		original_published_algo = models.PublishedAlgos.objects.get(publishing_uuid=publishing_uuid)
				# 		# added vote to backtest response
				# 		upvotes = original_published_algo.upvotes
				# 		downvotes = original_published_algo.downvotes
				# 		score = original_published_algo.score
				# 		view_count = original_published_algo.total_views
				# 	elif request.GET.get('publishing_uuid','')!='' and published_algo is not None:
				# 		upvotes = published_algo.upvotes
				# 		downvotes = published_algo.downvotes
				# 		score = published_algo.score
				# 		view_count = published_algo.total_views
				# except:
				# 	print(traceback.format_exc())
				# 	pass
			sp = {}
			# res = redis_con.keys('deployed:'+user_uuid+':'+algo_uuid+':*')
			# if len(res)>0:
			# 	algo_deployed=True
			# 	for k in res:
			# 		k = k.split(':')
			# 		deployed_seg_sym.append(k[3])
			# 		deployed_seg_sym_deployment_uuid[k[3]] = k[-1]
			p_id = request.GET.get('publishing_uuid',publishing_uuid)

			# con = get_redis_connection("default")
			# live_views_dict = con.get("live_veiws_dict")
			# if live_views_dict is None:
			# 	view_count = 0
			# else:
			# 	try:
			# 		view_dict = ujson.loads(live_views_dict)
			# 		view_count = int(view_dict["viewer_dict"].get(published_algo.algo_uuid,0))
			# 	except:
			# 		print(traceback.format_exc())
			# 		view_count = 0
			
			voted = None
			try:
				interaction = models.Interaction._get_collection().find_one({'user_uuid':user_uuid,'element_uuid':p_id,'interaction_type':'vote'})
				if interaction is not None:
					if interaction['interaction_action']=="upvote":
						voted = True
					else:
						voted = False
			except:
				print(traceback.format_exc())
			# algo_pref = 
			try:
				sp = published_algo.subscription_price
			except:
				pass
			public = True
			print '--###########2222222#######--',time.time()-st
			if(request.GET.get('resp','')=='json' or resp_json):
				return JsonResponse({'status':'success',
					'user_uuid':user_uuid,
					'publishing_uuid':publishing_uuid,
					'algo_subscription_uuid':algo_subscription_uuid,
					'algo_name':algo_name,
					'algo_desc':algo_desc,
					'position_type':position_type,
					'position_qty':position_qty,
					'equities':equities,
					'entry_logic':entry_logic,
					'exit_logic':exit_logic,
					'take_profit':take_profit,
					'stop_loss':stop_loss,
					'min_candle_freq':min_candle_freq,
					# addition data to populate andn default backtest
					'ip_interval':ip_interval,
					'start_time':start_time,
					'stop_time':stop_time,
					'holding_type':holding_type,
					# advanced fields
					'chart_type':chart_type,
					'trade_time_given':trade_time_given,
					'trading_start_time':trading_start_time,
					'trading_stop_time':trading_stop_time,
					'create_plus':create_plus,
					#----------------#
					'bt_url1':settings.BT_URL1,
					'bt_url2':settings.BT_URL2,
					'run_backtest_flag':False,
					'backtest_results':backtest_items_list,#ujson.loads(backtest_item.to_json()),#.items()
					'algo_deployed':algo_deployed,
					'algo_subscribed':algo_subscribed,
					'deployed_seg_sym':deployed_seg_sym,
					'deployed_seg_sym_deployment_uuid':deployed_seg_sym_deployment_uuid,
					'publisher_name':publisher_name,
					'publisher_bio':publisher_bio,
					'publisher_img_url':publisher_img_url,
					'published_algo_price':sp,
					'upvotes':upvotes,
					'downvotes':downvotes,
					'score':score,
					'public':public,
					'view_count':view_count,
					'voted':voted})

			return render(request,'multiple_backtests.html',
				{'status':'success',
					'user_uuid':user_uuid,
					'publishing_uuid':publishing_uuid,
					'algo_subscription_uuid':algo_subscription_uuid,
					'algo_name':algo_name,
					'algo_desc':algo_desc,
					'position_type':position_type,
					'position_qty':position_qty,
					'equities':equities,
					'entry_logic':entry_logic,
					'exit_logic':exit_logic,
					'take_profit':take_profit,
					'stop_loss':stop_loss,
					'min_candle_freq':min_candle_freq,
					# addition data to populate andn default backtest
					'ip_interval':ip_interval,
					'start_time':start_time,
					'stop_time':stop_time,
					'holding_type':holding_type,
					# advanced fields
					'chart_type':chart_type,
					'trade_time_given':trade_time_given,
					'trading_start_time':trading_start_time,
					'trading_stop_time':trading_stop_time,
					'create_plus':create_plus,
					#----------------#
					'bt_url1':settings.BT_URL1,
					'bt_url2':settings.BT_URL2,
					'run_backtest_flag':False,
					'backtest_results':backtest_item.to_json(),#.items()
					'algo_deployed':algo_deployed,
					'algo_subscribed':algo_subscribed,
					'deployed_seg_sym':ujson.dumps(deployed_seg_sym),
					'deployed_seg_sym_deployment_uuid':ujson.dumps(deployed_seg_sym_deployment_uuid)
					})
		except:
			print traceback.format_exc()
			return JsonResponse({'status':'error','error':'Published backtest not found','error_msg':'Published backtest not found'})

		return JsonResponse({'status':'error','error':'Algo not found','error_msg':'Algo not found'})
	return JsonResponse({'status':'error','error':'Invalid method','error_msg':'Invalid method'})

def marketplace_deploy(request):
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
		# if resp_json:
		return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)
		# return redirect('home')
	if request.method=='POST':
		algo_subscription_uuid = request.POST.get('algo_subscription_uuid','')
		seg_sym_list = request.POST.get('seg_sym_list','')
		seg_sym_quantity_list = request.POST.get('seg_sym_quantity_list','')
		if seg_sym_quantity_list=="":
			seg_sym_quantity_list = seg_sym_list
		frequency = request.POST.get('frequency','1')
		live_period = request.POST.get('live_period','1') # this is in days
		deployment_type = request.POST.get('deployment_type','') # this is in days
		broker = request.POST.get('broker','zerodha')
		# trade_account = request.POST.get('trade_account','')
		take_profit = request.POST.get('take_profit','')
		stop_loss = request.POST.get('stop_loss','')
		quantity = request.POST.get('quantity','')
		periodicity = request.POST.get('interval','hour')
		
		holding_type = request.POST.get('holding_type','')
		algo_live_for = request.POST.get('algo_live_for','1')
		variety = request.POST.get('variety','REGULAR')
		sound_name = request.POST.get('sound_name','default') 
		order_type = request.POST.get('order_type','MARKET')
		# # advanced parameters
		# chart_type = request.POST.get('chart_type','candlestick')
		# trade_time_given = request.POST.get('trade_time_given',"False")
		# if(trade_time_given=='True'):
		# 	trade_time_given = True
		# else:
		# 	trade_time_given = False
		# trading_start_time = request.POST.get('trading_start_time','09:15')
		# trading_stop_time = request.POST.get('trading_stop_time','15:30')
		# #--------------------#
		
		try:
			seg_sym_list = urllib.unquote(unicode(seg_sym_list).encode('utf-8'))
		except:
			print 'error: seg_sym_list',seg_sym_list
			print traceback.format_exc()
			return JsonResponse({'status':'error'})
		con = get_redis_connection("default")
		pipeline = con.pipeline()
		try:
			seg_sym_list = eval(seg_sym_list.replace('"','\"'))
		except:
			print 'error: seg_sym_list',seg_sym_list
			print traceback.format_exc()
			return JsonResponse({'status':'error'})

		try:
			seg_sym_quantity_list = eval(seg_sym_quantity_list.replace('"','\"'))
		except:
			print('error: seg_sym_list',seg_sym_quantity_list)
			print(traceback.format_exc())
			return JsonResponse({'status':'error'})

		multi_deploy_success = True
		multi_deploy_error_list = []
		# print seg_sym_list,len(seg_sym_list),seg_sym_dict
		seg_sym_dict = fetch_instruments(seg_sym_list)
		# assert 1==2
		deployed_len = 0
		st = time.time()
		for seg_sym in seg_sym_quantity_list:
			# seg_sym = s
			print seg_sym
			try:
				try:
					subscribed_algo = models.SubscribedAlgos.objects.get(user_uuid=user_uuid,algo_subscription_uuid=algo_subscription_uuid,subscription_expiry__gte=datetime.datetime.now(),subscription_status=1)
				except models.SubscribedAlgos.DoesNotExist:
					return JsonResponse({"status":"error","error_msg":"No valid subscription for strategy found"})
				except:
					print(traceback.format_exc())
					return JsonResponse({"status":"error","error_msg":"Unknown error"})

				now = datetime.datetime.now()
				try:
					quantity = str(seg_sym[2])
				except:
					quantity = request.POST.get('quantity','')
				# ex_date = now.replace(day=now.day+int(live_period))
				product = ''
				seg_sym = seg_sym[0]+'_'+seg_sym[1]
				print seg_sym
				[segment,symbols]=seg_sym.split('_')
				# account_name = trade_account
				# exchange = segment.lower()
				# if len(seg_sym)<=3:
				# 	if segment.lower() in exchanges_str and trade_account=='':
				# 		# only when choosing account based on default account
				# 		for s in default_accounts.keys():
				# 			if segment.lower() in s.lower():
				# 				account_name = default_accounts[s]
				# 				exchange = s
				# 	elif segment.lower() in exchanges_str:
				# 		# only when deciding the exchange when account name is given
				# 		for s in default_accounts.keys():
				# 			if account_name == default_accounts[s]:
				# 				exchange = s
				# 	elif deployment_type=='Auto trading':
				# 		print('No account name given nor any account is present')
				# 		continue
				# else:
				# 	exchange = segment.lower()
				# 	account_name = s[3]
				# 	try:
				# 		account_id = s[4]
				# 	except:
				# 		account_id = ''

				product = ''
				# seg_sym = seg_sym[0]+'_'+seg_sym[1]
				# [segment,symbols]=seg_sym.split('_')

				if holding_type!='' and holding_type!=None:
					if holding_type=='MIS':
						product = 'MIS'
					else:
						if segment == 'NSE':
							product = 'CNC'
						elif ('NFO' in segment):
							product = 'NRML'
						elif ('CDS' in segment):
							product = 'NRML'
						elif ('MCX' in segment):
							product = 'NRML'
						elif ('INDICES' in segment):
							product = 'CNC'
				else:
					if int(live_period) == 1:
						product = 'MIS'
					else:
						if segment == 'NSE':
							product = 'CNC'
						elif ('NFO' in segment):
							product = 'NRML'
						elif ('CDS' in segment):
							product = 'NRML'
						elif ('MCX' in segment):
							product = 'NRML'
						elif ('INDICES' in segment):
							product = 'CNC'

				if ('MCX' in segment):
					variety = 'REGULAR'

				if product == '':
					return JsonResponse({'status':'error','error':'Unknown product type'})

				ex_date = datetime.datetime.today() + datetime.timedelta(days=int(live_period))
				ex_date = ex_date.replace(hour=0,minute=0,second=0)
				expiration_sec = int(float(ex_date.strftime('%s'))-float(now.strftime('%s')))
				# check if backtest
				print("seg_sym",seg_sym)
				bt_result = models.SubscribeAlgoBacktest.objects.get(user_uuid=user_uuid,algo_subscription_uuid=algo_subscription_uuid,seg_sym=seg_sym)
				if seg_sym in bt_result['backtest_result'].keys():
					# in seg_sym backtested already, then it is deployable
					# deployed algorithm redis entry format =>
					# 'deployed'+':'+user_uuid+':'+algo_uuid+':'+seg_sym+':'+periodicity+':'+deployment_uuid=>{algo as json}
					# add storage time in redis
					bt_result['algo_obj']['user_uuid'] = user_uuid
					bt_result['algo_obj']['algo_uuid'] = algo_subscription_uuid
					if quantity!='':
						bt_result['algo_obj']['quantity'] = quantity
					if periodicity!='':
						bt_result['algo_obj']['time_frame'] = periodicity
					if take_profit!='':
						bt_result['algo_obj']['take_profit'] = take_profit
					if stop_loss!='':
						bt_result['algo_obj']['stop_loss'] = stop_loss
					
					bt_result['algo_obj']['deployment_time'] = datetime.datetime.now().isoformat()
					bt_result['algo_obj']['deployment_type'] = deployment_type
					bt_result['algo_obj']['product'] = product
					bt_result['algo_obj']['variety'] = variety
					bt_result['algo_obj']['sound_name'] = sound_name 
					bt_result['algo_obj']['algo_live_for'] = algo_live_for

					deployment_uuid = str(uuid.uuid4())

					if '@' in bt_result['algo_obj'].get('action_str',''):
						itoken = con.keys('instruments:*:'+seg_sym.split('_')[1]+':*:'+seg_sym.split('_')[0]+':*')
						if len(itoken)!=1: # missing instrument
							# return JsonResponse({'status':'error'})
							multi_deploy_error_list.append(seg_sym.split('_'))
						itoken = itoken[0].split(':')[1]
						reg = r"@*(\d+\.*\d*)\D*of\D*(\d+\.*\d*)"
						r = re.findall(reg,bt_result['algo_obj']['action_str'])
						[pr,rn]=r[0]					
						# set 123:abcd:PRICETRIGGER:2524673:IR1:68.30:0.1:0.0:algo_name 68.30
						x = [user_uuid,deployment_uuid,'PRICETRIGGER',itoken,'IR1',pr,rn,'0.0',bt_result['algo_obj']['algo_name'],bt_result['algo_obj']['action_type'],bt_result['algo_obj']['quantity'],algo_subscription_uuid,product,symbols,segment,variety,bt_result['algo_obj']['take_profit'],bt_result['algo_obj']['stop_loss'],bt_result['algo_obj'].get('tpsl_type','pct'),deployment_type,periodicity]
						pipeline.set(':'.join(x),pr)
						add_pricetrigger(itoken,':'.join(x)) 
						pipeline.expire(':'.join(x),expiration_sec)
					
					x = [user_uuid,algo_subscription_uuid,seg_sym,periodicity,deployment_uuid]

					# keys = con.scan_iter(match='deployed:'+user_uuid+':'+algo_subscription_uuid+':'+seg_sym+':'+periodicity+':*')

					deployed_algos_mongo = models.DeployedAlgorithm._get_collection().find({"user_uuid":user_uuid,"algo_uuid":algo_subscription_uuid,"segment_symbol":seg_sym,"algo_obj.time_frame":periodicity,"status":0,"expiration_time":{"$gte":datetime.datetime.now()}})
					deployed_algo = []
					for a in deployed_algos_mongo:
						x = [a["user_uuid"],a["algo_uuid"],a["segment_symbol"],periodicity,a["deployment_uuid"]]
						dkey = 'deployed:'+":".join(x)
						deployed_algo.append(dkey)
					keys = deployed_algo

					keys_count = 0
					keys_list = []
					for k in keys:
						keys_list.append(k)
						keys_count += 1
					if keys_count>0:
						redis_key = keys_list[0]
					else:
						redis_key = 'deployed:'+':'.join(x)
					# +user_uuid+':'+algo_uuid+':'+seg_sym+':'+periodicity+':'+deployment_uuid
					redis_entry = ujson.dumps({'user_uuid':user_uuid,
											'algo_uuid':algo_subscription_uuid,
											'seg_sym':seg_sym,
											'frequency':frequency,
											'broker':broker,
											'deployment_uuid':deployment_uuid,
											'algo_obj':bt_result['algo_obj'],
											'status':0,
											"expiration_time":ex_date.isoformat(),
											'algo_live_for':algo_live_for,
											'order_type':order_type,
											'variety':variety,
											"explore_algo":True
						})
					pipeline.set(redis_key,redis_entry)
					pipeline.expire(redis_key,expiration_sec)
					# settings.ENV,
					pipeline.publish(settings.ENV+'-deployment_channel-crypto','ADD:'+redis_key)
					# store the log in mongo because of longer storage requirements
					deployed_algo = models.DeployedAlgorithm(
						user_uuid=user_uuid,
						algo_uuid=algo_subscription_uuid,
						algo_name=subscribed_algo.algo_name,
						algo_obj=bt_result['algo_obj'],
						deployment_uuid=deployment_uuid,
						deployment_type=deployment_type,
						order_type=order_type,
						broker=broker,
						segment_symbol =  seg_sym,
						symbol =  seg_sym.split('_')[1],
						segment =  seg_sym.split('_')[0],
						deployment_time = datetime.datetime.now(),
						expiration_time = ex_date,
						frequency = frequency,
						live_period = live_period,
						status = 0,
						explore_algo = True
						)

					holding_for_algo = models.HoldingsForAlgorithm(user_uuid=user_uuid,
						algo_uuid=algo_subscription_uuid,
						algo_name=subscribed_algo.algo_name,
						deployment_uuid=deployment_uuid,
						deployment_type=deployment_type,
						algo_reference = deployed_algo,
						symbol =  seg_sym.split('_')[1],
						segment =  seg_sym.split('_')[0],
						# exchange = exchange,
						product = product,
						position = {'qty':'0.0','last_order_average_price':'0.0'},
						pnl={'final_pnl':'0.0','returns':'0.0'}, # this hodls the realized pnl and realised returns,
						explore_algo = True
						)

					order_start_log = models.OrderLog(
						user_uuid=user_uuid,
						algo_uuid=algo_subscription_uuid,
						deployment_uuid=deployment_uuid,
						deployment_type=deployment_type,
						log_tag="Waiting",
						log_message="Waiting for first trigger event",
						explore_algo = True
						)

					# fetch_single_backtest_result = """
					# function(){
					# var results = [];
					# results = db[collection].findOne({user_uuid:"%s","algo_uuid":"%s","backtest_result.%s":{$exists:true}},{"backtest_result.%s":1,"algo_obj":1,"algo_uuid":1,"updated_at":1,"_id":0});
					# return results;
					# }"""%(user_uuid,algo_uuid,seg_sym,seg_sym)

					# backtest_result = models.SubscribeAlgoBacktest._get_collection().find_one({"user_uuid" : user_uuid,"algo_subscription_uuid":algo_subscription_uuid,"backtest_result.%s"%seg_sym:{"$exists":True}},{"backtest_result.%s"%seg_sym:1,"algo_obj":1,"algo_uuid":1,"updated_at":1,"_id":0})
					# fetch_single_backtest_result_dict = {user_uuid:"%s","algo_uuid":"%s","backtest_result.%s":{$exists:true}},{"backtest_result.%s":1,"algo_obj":1,"algo_uuid":1,"updated_at":1,"_id":0});
					# return results;
					# }
					# backtest_result = models.BacktestMeta.objects.exec_js(fetch_single_backtest_result)
					# backtest_result = models.Algorithm._get_collection().aggregate(algo_snap_query_dict) 
					# if backtest_result==None:
						# multi_deploy_error_list.append(seg_sym.split('_'))
						# return JsonResponse({'status':'success','msg':'Missing backtest'})

					# this is the backtest spanpshot for orders log
					order_log_backtest = models.OrderLogBacktest(user_uuid=user_uuid,algo_uuid=algo_subscription_uuid,deployment_uuid=deployment_uuid,
						backtest_result=bt_result['backtest_result'][seg_sym],
						algo_obj=bt_result['algo_obj']
						)

					# st2 = time.time()
					deployed_algo.save()
					holding_for_algo.save()
					order_start_log.save()
					order_log_backtest.save()
					pipeline.execute()
					update_usage_util(user_uuid,'deployed')
					# print(time.time()-st2)
					deployed_len += 1
				else:
					multi_deploy_error_list.append(seg_sym.split('_'))

			except:
				print traceback.format_exc()
				# return JsonResponse({'status':'error'})
				multi_deploy_success = False

		print(time.time()-st)
		if deployed_len==0:
			multi_deploy_success = False
		if(multi_deploy_success):
			return JsonResponse({'status':'success'})
		else:
			# if deployment_type=='Auto trading':
			# 	return JsonResponse({'status':'error','error_msg':"Exchange account not added for auto trading"})
			return JsonResponse({'status':'error','multi_deploy_error_list':multi_deploy_error_list})

	return JsonResponse({'status':'error'})		

def my_subscribed_algos(request):
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
		if resp_json:
			return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)
		return redirect('home')

	if request.method == "GET":
		payload = request.GET
	elif request.method == "POST":
		payload = request.POST
	else:
		return JsonResponse({"status":"error","error":"Invalid method","error_msg":"Invalid method"},status=403)

	if request.method == "GET" or request.method == "POST":
		page_limit = int(payload.get('page_limit',10))
		page_num = int(payload.get('page',1))
		algo_uuids = payload.get('algo_subscription_uuids',None)


		filter_dict = payload.get("filter",None)
		search = payload.get("search","")
		search_key = payload.get("search","")
		search_list = search.strip().split(" ")
		filter_tag = payload.get("filter_tag",None)

		all_tags = [
			"trend following",
			"price action",
			"mean reversion",
			"momentum",
			"miscellaneous",
			"pivot points",
			"overlays",
			"options strategies"
		]

		if filter_tag is None or filter_tag=="":
			filter_tag = all_tags+[""]
		else:
			filter_tag = [filter_tag]

		action_type = ["BUY","SELL"]
		chart_type = ["candlestick","heikinashi","renko"]
		time_frame = ["min","3min","5min","10min","15min","30min","hour","day"]
		backtest_pnl = [-1000,1000]
		max_dd = [-100,100]
		favourite = False
		if filter_dict:
			filter_dict = urllib.unquote(filter_dict).decode('utf8') 
			filter_dict = ujson.loads(filter_dict)
			filter_map = {
				"overlays" : ["sma", "ema", "dema", "tema", "wma", "tma", "moving average", "ubb", "lbb", "mbb", "parabolic sar", "supertrend", "alligator"],
				"momentum" : ["rsi", "adx", "aroon", "macd", "cci", "mfi", "di", "willr", "trix", "proc", "mom", "stochastic", "trend", "cmo"],
				"volume" : [" obv", "volume"],
				"volatility" : [" natr", " tr ", " atr ", "vortex"],
				"price action" : ["number", "close", "open", "high", "low", "prev", "pivot", "opening range", "vwap"],
				"chart patterns" : ["morning", "kicking", "spinning", "engulfing", "homing", "soldiers", "abandoned", "tri star", "advance", "conceal", "stick"],
				"bullish":1,
				"bearish":-1,
				"backtest_pnl":[-1000,1000],
				"max_dd":[-100,100]
			}

			favourite = filter_dict.get('favourite',False)

			for i in filter_dict.get("entry_logic",[]):
				search_list += filter_map.get(i,[])
			for i in filter_dict.get("exit_logic",[]):
				search_list += filter_map.get(i,[])

			a_type = filter_dict.get("position_type",[])
			if filter_dict.get("position_type",None) is None:
				a_type = filter_dict.get("action_type",[])
			if len(a_type)!=0:
				t_a = []
				for a in a_type:
					if a == "bullish":
						t_a.append("BUY")
					else:
						t_a.append("SELL")
				action_type = t_a

			c_type = filter_dict.get("chart_type",[])
			if len(c_type)!=0:
				c_type = [c.lower().replace("-a","A").split("(")[0] for c in c_type]
				chart_type = c_type

			t_type = filter_dict.get("time_frame",[])
			if len(t_type)!=0:
				time_frame = t_type

			b_pnl = filter_dict.get("backtest_pnl",[])
			if len(b_pnl)!=0:
				backtest_pnl = b_pnl

			m_dd = filter_dict.get("max_dd",[])
			if len(m_dd)!=0:
				max_dd = m_dd

		page_limit = int(payload.get('page_limit',10))
		page_num = int(payload.get('page',1))

		search = " ".join(search_list+chart_type)

		subscribed_algos_obj = []

		if algo_uuids and algo_uuids!='':
			if request.method=='POST':
				algo_uuids = urllib.unquote(algo_uuids).decode('utf8') 
				algo_uuids = ujson.loads(algo_uuids)
			else:
				algo_uuids = str(algo_uuids).split(',')
					
			subscribed_algos = models.SubscribedAlgos._get_collection().find({'user_uuid':user_uuid,"algo_subscription_uuid":{ "$in": algo_uuids}},{ 'html_block':0,'_id':0 }).sort([("updated_at",-1)])
		elif algo_uuids=='':
			subscribed_algos = []
		elif search!="" and len(search)>2 and filter_dict:
			print("here",{'user_uuid':user_uuid,"algo_obj.action_type":{ "$in": action_type},"algo_obj.time_frame":{ "$in": time_frame}},{ 'html_block':0,'_id':0 })
			subscribed_algos = models.SubscribedAlgos._get_collection().find({'user_uuid':user_uuid,"algo_obj.action_type":{ "$in": action_type},"algo_obj.time_frame":{ "$in": time_frame}},{ 'html_block':0,'_id':0 }).sort([("updated_at",-1)])
		elif filter_dict:
			subscribed_algos = models.SubscribedAlgos._get_collection().find({'user_uuid':user_uuid,"algo_obj.position_type":{ "$in": action_type},"algo_obj.time_frame":{ "$in": time_frame}},{ 'html_block':0,'_id':0 }).sort([("updated_at",-1)])
		else:
			subscribed_algos = models.SubscribedAlgos._get_collection().find({'user_uuid':user_uuid,'subscription_status':1},{'_id':0 ,'algo_obj':0}).sort([("updated_at",-1)])
		cur_i = 0
		publisher_dict = {} 
		fav_obj = {}
		if favourite:
			con = get_redis_connection("default")
			fav_obj = con.get("screener_favorites:"+user_uuid)
			if fav_obj:
				fav_obj = ujson.loads(fav_obj).get('discover',{})

		for a in subscribed_algos:
			cur_i += 1
			if search_key!="" and len(search_key)>2:
				if search_key not in a["algo_name"] and search_key not in a["algo_desc"] and search_key not in a["entry_logic"] and search_key not in a["exit_logic"]:
					continue
			if len(search_list)>1:
				p = False
				for s in search_list:
					if s!="" and s!=" ":
						if s not in a["algo_name"] and s not in a["algo_desc"] and s not in a["entry_logic"] and s not in a["exit_logic"]:
							p = False
						else:
							p = True
							break
				if not p:
					continue

			if favourite:
				print(fav_obj,a.get("algo_uuid"))
				if fav_obj.get(a.get("algo_subscription_uuid"),None) is None and fav_obj.get(a.get("algo_uuid"),None) is None:
					continue
				# elif fav_obj.get(a.get("algo_uuid"),None) is None:
				# 	# print("continue-->2",a["algo_name"])
				# 	continue					
			if(max(0,page_num-1)*page_limit<=cur_i<=max(0,page_num-1)*page_limit+page_limit):
				backtest = models.SubscribeAlgoBacktest._get_collection().find({'user_uuid':user_uuid,'algo_uuid':a['algo_uuid']},{'_id':0,"backtest_result":0,"algo_obj":0})
				b_list = []
				for b in backtest:
					# TODO Remove algo condition related objects
					b_list.append(b)
				a['backtest'] = b_list
				publisher_dict[a["user_uuid"]]={}
			subscribed_algos_obj.append(a)

		subscribed_algos_expired = models.SubscribedAlgos._get_collection().find({'user_uuid':user_uuid,"subscription_expiry":{ "$lt": datetime.datetime.now()},'subscription_status':1},{'_id':0 }).sort([("updated_at",-1)])

		subscribed_expired_algos_list = []
		for s in subscribed_algos_expired:
			subscribed_expired_algos_list.append([s["publishing_uuid"],s["algo_subscription_uuid"]])

		subscribed_algos_deployed = models.DeployedAlgorithm._get_collection().find({'user_uuid':user_uuid,"expiration_time":{ "$gt": datetime.datetime.now()},"explore_algo":True},{'_id':0 }).sort([("updated_at",-1)])
		subscribed_algos_deployed_list = []
		for d in subscribed_algos_deployed:
			subscribed_algos_deployed_list.append([d["algo_uuid"],d["segment_symbol"]])

		publishers = models.PublisherBio._get_collection().find({"user_uuid":{"$in":publisher_dict.keys()}},{"user_uuid":1,"publisher_name":1,"publisher_bio":1,"_id":0})

		for p in publishers:
			publisher_dict[p["user_uuid"]]={"publisher_name":p["publisher_name"],"publisher_bio":p["publisher_bio"]}

		if(payload.get('resp','')=='json'):
			# print algo_batch
			return JsonResponse({'algo':subscribed_algos_obj[max(0,page_num-1)*page_limit:max(1,page_num)*page_limit],'pages':int(math.ceil(len(subscribed_algos_obj)/(page_limit*1.0))),'status':'success',"subscribed_expired_algos":subscribed_expired_algos_list,"subscribed_algos_deployed":subscribed_algos_deployed_list,"publisher_details":publisher_dict})
		elif resp_json:
			return JsonResponse({'algo':subscribed_algos_obj[max(0,page_num-1)*page_limit:max(1,page_num)*page_limit],'pages':int(math.ceil(len(subscribed_algos_obj)/(page_limit*1.0))),'status':'success',"subscribed_expired_algos":subscribed_expired_algos_list,"subscribed_algos_deployed":subscribed_algos_deployed_list,"publisher_details":publisher_dict})

	return JsonResponse({"status":"error","error":"Invalid method","error_msg":"Invalid method"},status=403)

def my_published_algos(request):
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
		if resp_json:
			return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)
		return redirect('home')

	if request.method=='GET':
		
		payload = request.GET
		page_limit = int(payload.get('page_limit',10))
		page_num = int(payload.get('page',1))

		subscribed_algos_obj = []
		subscribed_algos = models.PublishedAlgos._get_collection().find({'user_uuid':user_uuid},{'_id':0 }).sort([("updated_at",-1)])
		cur_i = 0
		publisher_dict = {}
		publishers = models.PublisherBio._get_collection().find({"user_uuid":user_uuid},{"user_uuid":1,"publisher_name":1,"publisher_bio":1,"_id":0})
		for p in publishers:
			publisher_dict[p["user_uuid"]]={"publisher_name":p["publisher_name"],"publisher_bio":p["publisher_bio"]}

		for a in subscribed_algos:
			cur_i += 1
			if(max(0,page_num-1)*page_limit<=cur_i<=max(0,page_num-1)*page_limit+page_limit):
				backtest = models.PublishedBacktests._get_collection().find({'user_uuid':user_uuid,'publishing_uuid':a['publishing_uuid']},{'_id':0 })
				b_list = []
				for b in backtest:
					# TODO Remove algo condition related objects
					b_list.append(b)
				a['backtest'] = b_list
			subscribed_algos_obj.append(a)
		if(payload.get('resp','')=='json'):
			# print algo_batch
			return JsonResponse({'algo':subscribed_algos_obj[max(0,page_num-1)*page_limit:max(1,page_num)*page_limit],'pages':int(math.ceil(len(subscribed_algos_obj)/(page_limit*1.0))),'status':'success',"publisher_details":publisher_dict})
		elif resp_json:
			return JsonResponse({'algo':subscribed_algos_obj[max(0,page_num-1)*page_limit:max(1,page_num)*page_limit],'pages':int(math.ceil(len(subscribed_algos_obj)/(page_limit*1.0))),'status':'success',"publisher_details":publisher_dict})

	return JsonResponse({"status":"error","error":"Invalid method","error_msg":"Invalid method"},status=403)

def marketplace_new(request):
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

	# if not user_is_auth:
	# 	if resp_json:
	# 		return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)
	# 	return redirect('home')
	if request.method == "GET":
		payload = request.GET
	elif request.method == "POST":
		payload = request.POST
	else:
		return JsonResponse({"status":"error","error":"Invalid method","error_msg":"Invalid method"},status=403)


	filter_dict = payload.get("filter",None)
	search = payload.get("search","")
	search_key = payload.get("search","")
	search_list = search.strip().split(" ")
	filter_tag = payload.get("filter_tag",None)

	all_tags = [
		"trend following",
		"price action",
		"mean reversion",
		"momentum",
		"miscellaneous",
		"pivot points",
		"overlays",
		"options strategies"
	]

	if filter_tag is None or filter_tag=="":
		filter_tag = all_tags+[""]
	else:
		filter_tag = [filter_tag]

	action_type = [1,-1]
	chart_type = ["candlestick","heikinashi","renko"]
	time_frame = ["min","3min","5min","10min","15min","30min","hour","day"]
	backtest_pnl = [-1000,1000]
	max_dd = [-100,100]
	favourite = False
	if filter_dict:
		filter_dict = urllib.unquote(filter_dict).decode('utf8') 
		filter_dict = ujson.loads(filter_dict)
		filter_map = {
			"overlays" : ["sma", "ema", "dema", "tema", "wma", "tma", "moving average", "ubb", "lbb", "mbb", "parabolic sar", "supertrend", "alligator"],
			"momentum" : ["rsi", "adx", "aroon", "macd", "cci", "mfi", "di", "willr", "trix", "proc", "mom", "stochastic", "trend", "cmo"],
			"volume" : [" obv", "volume"],
			"volatility" : [" natr", " tr ", " atr ", "vortex"],
			"price action" : ["number", "close", "open", "high", "low", "prev", "pivot", "opening range", "vwap"],
			"chart patterns" : ["morning", "kicking", "spinning", "engulfing", "homing", "soldiers", "abandoned", "tri star", "advance", "conceal", "stick"],
			"bullish":1,
			"bearish":-1,
			"backtest_pnl":[-1000,1000],
			"max_dd":[-100,100]
		}

		favourite = filter_dict.get('favourite',False)

		for i in filter_dict.get("entry_logic",[]):
			search_list += filter_map.get(i,[])
		for i in filter_dict.get("exit_logic",[]):
			search_list += filter_map.get(i,[])

		a_type = filter_dict.get("position_type",[])
		if filter_dict.get("position_type",None) is None:
			a_type = filter_dict.get("action_type",[])
		if len(a_type)!=0:
			t_a = []
			for a in a_type:
				if a == "bullish":
					t_a.append(1)
				else:
					t_a.append(-1)
			action_type = t_a

		c_type = filter_dict.get("chart_type",[])
		if len(c_type)!=0:
			c_type = [c.lower().replace("-a","A").split("(")[0] for c in c_type]
			chart_type = c_type

		t_type = filter_dict.get("time_frame",[])
		if len(t_type)!=0:
			time_frame = t_type

		b_pnl = filter_dict.get("backtest_pnl",[])
		if len(b_pnl)!=0:
			backtest_pnl = b_pnl

		m_dd = filter_dict.get("max_dd",[])
		if len(m_dd)!=0:
			max_dd = m_dd

	page_limit = int(payload.get('page_limit',10))
	page_num = int(payload.get('page',1))

	search = " ".join(search_list+chart_type)

	marketplace_obj = []
	marketplace_dict = {}
	now = datetime.datetime.now()
	# published_algos = models.PublishedAlgos._get_collection().find({"publish_status":{ "$in": [1,2]}},{ 'html_block':0,'_id':0,'algo_obj':0 }).sort([("updated_at",-1),("publish_status",-1)])

	print(chart_type,time_frame,action_type,search)
	if search!="" and len(search)>2 and filter_dict:
		published_algos = models.PublishedAlgos._get_collection().find({"publish_status":{ "$in": [1,2]},"position_type":{ "$in": action_type},"time_frame":{ "$in": time_frame},"$text": { "$search": search },"tagged_class":{"$in":filter_tag}},{ 'html_block':0,'_id':0,'algo_obj':0 }).sort([("updated_at",-1),("publish_status",-1)])
	elif filter_dict:
		published_algos = models.PublishedAlgos._get_collection().find({"publish_status":{ "$in": [1,2]},"position_type":{ "$in": action_type},"time_frame":{ "$in": time_frame},"tagged_class":{"$in":filter_tag}},{ 'html_block':0,'_id':0,'algo_obj':0 }).sort([("updated_at",-1),("publish_status",-1)])
	else:
		published_algos = models.PublishedAlgos._get_collection().find({"publish_status":{ "$in": [1,2]},"position_type":{ "$in": action_type},"time_frame":{ "$in": time_frame},"tagged_class":{"$in":filter_tag}},{ 'html_block':0,'_id':0,'algo_obj':0 }).sort([("updated_at",-1),("publish_status",-1)])

	cur_i = 0
	viewer_dict = {}
	publisher_dict = {}

	fav_obj = {}
	if favourite:
		con = get_redis_connection("default")
		fav_obj = con.get("screener_favorites:"+user_uuid)
		if fav_obj:
			fav_obj = ujson.loads(fav_obj).get('discover',{})

	for a in published_algos:
		viewer_dict[a["algo_uuid"]]=a["total_views"]
		a["algo_state"]={}
		a["algo_calc"]={}
		if search_key!="" and len(search_key)>2:
			if search_key not in a["algo_name"] and search_key not in a["algo_desc"] and search_key not in a["entry_logic"] and search_key not in a["exit_logic"]:
				continue

		if len(search_list)>1:
			p = False
			for s in search_list:
				if s!="" and s!=" ":
					if s not in a["algo_name"] and s not in a["algo_desc"] and s not in a["entry_logic"] and s not in a["exit_logic"]:
						p = False
					else:
						p = True
						break
			if not p:
				continue

		if favourite:
			print(fav_obj,a.get("publishing_uuid"))
			if fav_obj.get(a.get("publishing_uuid"),None) is None:
				# print("continue-->2",a["algo_name"])
				continue
				
		marketplace_obj.append(a)
		# print(a["algo_name"],a["algo_uuid"],search_key)

		marketplace_dict[a['algo_uuid']]=a

	# viewer_dict = view_calculator(viewer_dict)
	con = get_redis_connection("default")
	market_place_sorted_list_time = now
	if (market_place_sorted_list_time.hour>0 and market_place_sorted_list_time.hour<2 or random.randint(0,1001)%500==0):
		vd_sorted = sorted(viewer_dict.items(), key = lambda x: x[1],reverse=True)
		con.set("market_place_sorted_dict",ujson.dumps({"updated_at":int(now.strftime("%s")),"market_place_sorted_list":vd_sorted}))
	else:
		market_place_sorted_dict = con.get("market_place_sorted_dict")
		if market_place_sorted_dict is None:
			vd_sorted = sorted(viewer_dict.items(), key = lambda x: x[1],reverse=True)
			con.set("market_place_sorted_dict",ujson.dumps({"updated_at":int(now.strftime("%s")),"market_place_sorted_list":vd_sorted}))
		else:
			market_place_sorted_dict = ujson.loads(market_place_sorted_dict)
			time = market_place_sorted_dict['update_at']
			if int(now.strftime("%s"))-int(time) > 3600:
				vd_sorted = sorted(viewer_dict.items(), key = lambda x: x[1],reverse=True)
				con.set("market_place_sorted_dict",ujson.dumps({"updated_at":int(now.strftime("%s")),"market_place_sorted_list":vd_sorted}))
			else:
				vd_sorted = market_place_sorted_dict.get(market_place_sorted_list,[])

	marketplace_obj2=[]
	for v in vd_sorted:
		a = marketplace_dict.get(v[0],None)
		if a is not None:
			if(max(0,page_num-1)*page_limit<=cur_i<max(0,page_num-1)*page_limit+page_limit):
				# backtest = models.PublishedBacktestsMeta._get_collection().find({'algo_uuid':a['algo_uuid'],"backtest_result_meta.returns":{"$gte":backtest_pnl[1],"$lte":backtest_pnl[0]},"backtest_result_meta.max_draw":{"$gte":max_dd[1],"$lte":max_dd[0]}},{'_id':0 ,'algo_obj':0}).sort([("backtest_result_meta.returns",-1)])
				backtest = models.PublishedBacktestsMeta._get_collection().find({'algo_uuid':a['algo_uuid']},{'_id':0 ,'algo_obj':0}).sort([("backtest_result_meta.returns",-1)])

				b_list = []
				avg_return_pct = 0
				avg_return = 0
				absolute_pnl = 0
				absolute_pnl_pct = 0
				avg_win_loss_ratio = 0.0
				avg_winning_streak = 0
				avg_lossing_streak = 0
				sym_count = 0
				sym_pnl = []
				sym_max_cap_used = []

				for b in backtest:	
					# TODO Remove algo condition related objects
					sym_count = sym_count + 1
					k = b["seg_sym"]
					if k in b["backtest_result"].keys():
						sym_pnl.append(b["backtest_result"][k]["final_pnl"])
						sym_max_cap_used.append(b["backtest_result"][k]["max_cap_used"])
						avg_winning_streak = avg_winning_streak+int(b["backtest_result"][k]["winning_streak"])
						avg_lossing_streak = avg_lossing_streak+int(b["backtest_result"][k]["lossing_streak"])
						try:
							avg_win_loss_ratio = avg_win_loss_ratio+float(b["backtest_result"][k]["average_gain_per_winning_trade"])/abs(float(b["backtest_result"][k]["average_gain_per_losing_trade"]))
						except:
							pass
					b_list.append(b)

				if len(sym_pnl)>0 and sum(sym_max_cap_used)>0:
					absolute_pnl_pct = (sum(sym_pnl)/sum(sym_max_cap_used))*100
					absolute_pnl = sum(sym_pnl)
					avg_winning_streak = avg_winning_streak/float(sym_count)
					avg_lossing_streak = avg_lossing_streak/float(sym_count)
					avg_win_loss_ratio = avg_win_loss_ratio/float(sym_count)
					
				if len(b_list)>0:
					a['backtest'] = b_list

				a["absolute_pnl"]=absolute_pnl
				a["absolute_pnl_pct"]=absolute_pnl_pct
				a["avg_winning_streak"]=avg_winning_streak
				a["avg_lossing_streak"]=avg_lossing_streak
				a["avg_win_loss_ratio"]=avg_win_loss_ratio
						
				marketplace_obj2.append(a)
			cur_i += 1
		# marketplace_dict[a['algo_uuid']]=a
		# if a is not None:
			# if len(a.get('backtest',[]))>0:
				# marketplace_obj.append(a)
	
	subscribed_algos = models.SubscribedAlgos._get_collection().find({'user_uuid':user_uuid,"subscription_expiry":{ "$gt": now},"subscription_status":1},{'_id':0 ,'algo_obj':0}).sort([("updated_at",-1)])
	subscribed_algos_list = []
	for s in subscribed_algos:
		subscribed_algos_list.append([s["publishing_uuid"],s["algo_subscription_uuid"]])

	subscribed_algos_deployed = models.DeployedAlgorithm._get_collection().find({'user_uuid':user_uuid,"expiration_time":{ "$gt": now},"explore_algo":True},{'_id':0 }).sort([("updated_at",-1)])
	subscribed_algos_deployed_list = []
	for d in subscribed_algos_deployed:
		subscribed_algos_deployed_list.append([d["algo_uuid"],d["segment_symbol"]])

	publishers = models.PublisherBio._get_collection().find({"user_uuid":{"$in":publisher_dict.keys()}},{"user_uuid":1,"publisher_name":1,"publisher_bio":1,"_id":0})

	for p in publishers:
		publisher_dict[p["user_uuid"]]={"publisher_name":p["publisher_name"],"publisher_bio":p["publisher_bio"]}

	if(payload.get('resp','')=='json'):
		# print algo_batch
		# return JsonResponse({'algo':marketplace_obj[max(0,page_num-1)*page_limit:max(1,page_num)*page_limit],'pages':int(math.ceil(len(marketplace_obj)/(page_limit*1.0))),'status':'success',"subscribed_algos":subscribed_algos_list,"subscribed_algos_deployed":subscribed_algos_deployed_list,"viewer_dict":viewer_dict})
		return JsonResponse({'algo':marketplace_obj2[0:page_limit],'pages':int(math.ceil(len(marketplace_obj)/(page_limit*1.0))),'status':'success',"subscribed_algos":subscribed_algos_list,"subscribed_algos_deployed":subscribed_algos_deployed_list,"viewer_dict":viewer_dict,"publisher_details":publisher_dict,"all_tags":all_tags})
	elif resp_json:
		# return JsonResponse({'algo':marketplace_obj[max(0,page_num-1)*page_limit:max(1,page_num)*page_limit],'pages':int(math.ceil(len(marketplace_obj)/(page_limit*1.0))),'status':'success',"subscribed_algos":subscribed_algos_list,"subscribed_algos_deployed":subscribed_algos_deployed_list,"viewer_dict":viewer_dict})
		return JsonResponse({'algo':marketplace_obj2[0:page_limit],'pages':int(math.ceil(len(marketplace_obj)/(page_limit*1.0))),'status':'success',"subscribed_algos":subscribed_algos_list,"subscribed_algos_deployed":subscribed_algos_deployed_list,"viewer_dict":viewer_dict,"publisher_details":publisher_dict,"all_tags":all_tags})

def marketplace_tags(request):
	if request.method == 'GET':
		all_tags = [
		("trend following","Trend following strategies"),
		("price action","Price action strategies"),
		("mean reversion","Mean reverting strategies"),
		("momentum","Momentum based strategies"),
		("miscellaneous","Contains strategies with a mix of indicators types"),
		("pivot points","Pivot point based strategies"),
		("overlays","Overlay indicators based strategies"),
		("options strategies","Option contracts strategies")
		]
		tags=[]
		for a in all_tags:
			tags.append({"tag_name":a[0],"tag_description":a[1]})
		return JsonResponse({"status":"success","tags":tags})
	return JsonResponse({"status":"error","error_msg":"Invalid request"})

def screener_tags(request):
	if request.method == 'GET':
		all_tags = [
		("Chart patterns","Chart patterns scanners"),
		("Webinar Scanners","Scanners as seen in webinars"),
		("Bullish","Bullish scanners"),
		("Intraday Bullish","Intraday bullish scanners"),
		("Intraday Bearish","Intraday bearish scanners"),
		("Range Breakout","Range breakout scanners"),
		("Top Gainers","Top gainer scanners"),
		("Crossover","Crossover scanners"),
		("Top Losers","Top losses scanners"),
		("Bearish","Bearish scanners"),
		]
		tags=[]
		for a in all_tags:
			tags.append({"tag_name":a[0],"tag_description":a[1]})
		return JsonResponse({"status":"success","tags":tags})
	return JsonResponse({"status":"error","error_msg":"Invalid request"})