from django.shortcuts import render,redirect
from django.http import JsonResponse
import random
import uuid
import datetime
import traceback
from django.conf import settings
from django_redis import get_redis_connection
from coreapp import models
import json
import time
import math
import urllib
import ujson
import requests
from coreapp.views.discover import view_calculator
from coreapp.views.utility import get_deployment_keys

def dashboard_(request):

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
		return redirect('home')
	# fetch the algorithms and then get the backtest results and live results over websocket
	# TODO move the websocket part to Go for better scale

	page_limit = 10
	# fetching backtest result for the algorithm
	algo_snap_query = """
					function(){
						var results = [];
						results = db[collection].aggregate([{
						$lookup: {
						    from: "backtest_meta",
						    localField: "algo_uuid",
						    foreignField: "algo_uuid",
						    as: "backtest"
							}
						},{
						$lookup: {
						    from: "deployed_algorithm",
						    localField: "algo_uuid",
						    foreignField: "algo_uuid",
						    as: "deployed"
							}
						},
						{
						$match:{
							user_uuid : "%s"
							}
						},
						{ 
						$project : { 
							    "_id" : 1,
							    "algo_uuid" : 1,
							    "algo_name" : 1,
							    "algo_desc" : 1,
							    "entry_logic" : 1,
							    "time_frame": 1,
							    "exit_logic" : 1,
							    "entry_logic" : 1,
							    "position_type" : 1,
							    "quantity" : 1,
							    "stop_loss" : 1,
							    "take_profit" : 1,
							    "backtest" : 1,
							    "deployed" : { 
							    	$filter: 
							    	{ 
							    		input: "$deployed", 
							        	as: "deployed", 
							        	cond: {
							        	 $and:[
							        	 {$gte: [ "$$deployed.expiration_time", ISODate("%s") ]},
							        	 {$eq: [ "$$deployed.status",0 ]}
							        	 ]
							        	} 
							      	} 
							    },
							    "created_at" : 1,
							    "updated_at" : 1
						     }
						},
						{
						$sort:{"updated_at":1,"backtest":1,"deployed":1}
						}
						]);
						return results;
					}"""%(user_uuid,datetime.datetime.now().isoformat())
	algo_snaps = models.Algorithm.objects.exec_js(algo_snap_query)
	algo_batch = algo_snaps['_batch']#[:page_limit]

	redis_con = get_redis_connection("default")

	algo_batch2 = []
	for a in algo_batch:
		if a['algo_uuid'] == a['algo_name']:
			algo = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_uuid = a['algo_uuid']
					)
			algo.delete()
		else:
			algo_batch2.append(a)

	algo_batch = algo_batch2
	st = time.time()
	# print algo_batch
	for backtests in algo_batch:
		res = redis_con.keys("deployed:"+user_uuid+':'+backtests['algo_uuid']+':*')
		if len(res)>0:
			backtests['algo_deployed']=True

		if len(backtests['backtest'])!=0:
			c = 0
			for b in backtests['backtest']:#[0]['backtest_result'].keys():
				# res2 = redis_con.keys("deployed:"+user_uuid+':'+backtests['algo_uuid']+':'+b+':*')
				res2 = redis_con.keys("deployed:"+user_uuid+':'+backtests['algo_uuid']+':'+b['seg_sym']+':*')
				if len(res2)>0:
					# backtests['backtest'][0]['backtest_result'][b]['sym_deployed']=True
					# print 'yo'
					backtests['backtest'][c]['backtest_result'][b['seg_sym']]['sym_deployed']=True
				c += 1
	# print algo_batch
	print time.time()-st

	return render(request,'dashboard.html',{'algo':algo_batch})


def dashboard__(request):

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
		return redirect('home')
	# fetch the algorithms and then get the backtest results and live results over websocket
	# TODO move the websocket part to Go for better scale

	page_limit = 10
	page_num = int(request.GET.get('page',1))
	# fetching backtest result for the algorithm
	algo_snap_query = """
					function(){
						var results = [];
						results = db[collection].aggregate([{
						$lookup: {
						    from: "backtest_meta",
						    localField: "algo_uuid",
						    foreignField: "algo_uuid",
						    as: "backtest"
							}
						},{
						$lookup: {
						    from: "deployed_algorithm",
						    localField: "algo_uuid",
						    foreignField: "algo_uuid",
						    as: "deployed"
							}
						},
						{
						$match:{
							user_uuid : "%s"
							}
						},
						{ 
						$project : { 
							    "_id" : 1,
							    "algo_uuid" : 1,
							    "algo_name" : 1,
							    "algo_desc" : 1,
							    "entry_logic" : 1,
							    "time_frame": 1,
							    "exit_logic" : 1,
							    "entry_logic" : 1,
							    "position_type" : 1,
							    "quantity" : 1,
							    "stop_loss" : 1,
							    "take_profit" : 1,
							    "backtest" : 1,
							    "deployed" : { 
							    	$filter: 
							    	{ 
							    		input: "$deployed", 
							        	as: "deployed", 
							        	cond: {
							        	 $and:[
							        	 {$gte: [ "$$deployed.expiration_time", ISODate("%s") ]},
							        	 {$eq: [ "$$deployed.status",0 ]}
							        	 ]
							        	} 
							      	} 
							    },
							    "created_at" : 1,
							    "updated_at" : 1
						     }
						},
						{
						$sort:{"updated_at":1,"backtest":1,"deployed":1}
						}
						]);
						return results;
					}"""%(user_uuid,datetime.datetime.now().isoformat())

	algo_snap_query_dict = [{
						'$lookup': {
						    'from': "backtest_meta",
						    'localField': "algo_uuid",
						    'foreignField': "algo_uuid",
						    'as': "backtest"
							}
						},{
						'$lookup': {
						    'from': "deployed_algorithm",
						    'localField': "algo_uuid",
						    'foreignField': "algo_uuid",
						    'as': "deployed"
							}
						},
						{
						'$match':{
							'user_uuid' : user_uuid
							}
						},
						{ 
						'$project' : { 
							    "_id" : 1,
							    "algo_uuid" : 1,
							    "algo_name" : 1,
							    "algo_desc" : 1,
							    "entry_logic" : 1,
							    "time_frame": 1,
							    "exit_logic" : 1,
							    "entry_logic" : 1,
							    "position_type" : 1,
							    "quantity" : 1,
							    "stop_loss" : 1,
							    "take_profit" : 1,
							    "backtest" : 1,
							    "deployed" : { 
							    	'$filter': 
							    	{ 
							    		'input': "$deployed", 
							        	'as': "deployed", 
							        	'cond': {
							        	'$and':[
							        	 {'$gte': [ "$$deployed.expiration_time", datetime.datetime.now().isoformat()]},
							        	 {'$eq': [ "$$deployed.status",0 ]}
							        	 ]
							        	} 
							      	} 
							    },
							    "created_at" : 1,
							    "updated_at" : 1
						     }
						},
						{
						'$sort':{"updated_at":-1,"backtest":1,"deployed":1}
						}
						]

	algo_snap_query_dict = [{
						'$lookup': {
						    'from': "backtest_meta",
						    'localField': "algo_uuid",
						    'foreignField': "algo_uuid",
						    'as': "backtest"
							}
						},{
						'$lookup': {
						    'from': "deployed_algorithm",
						    'localField': "algo_uuid",
						    'foreignField': "algo_uuid",
						    'as': "deployed"
							}
						},
						{
						'$match':{
							'user_uuid' : user_uuid
							}
						},
						{ 
						'$project' : { 
							    "_id" : 1,
							    "algo_uuid" : 1,
							    "algo_name" : 1,
							    "algo_desc" : 1,
							    "entry_logic" : 1,
							    "time_frame": 1,
							    "exit_logic" : 1,
							    "entry_logic" : 1,
							    "position_type" : 1,
							    "quantity" : 1,
							    "stop_loss" : 1,
							    "take_profit" : 1,
							    "backtest" : 1,
							    "deployed" : { 
							    	'$filter': 
							    	{ 
							    		'input': "$deployed", 
							        	'as': "deployed", 
							        	'cond': {
							        	'$and':[
							        	 {'$gte': [ "$$deployed.expiration_time", datetime.datetime.now().isoformat()]},
							        	 {'$eq': [ "$$deployed.status",0 ]}
							        	 ]
							        	} 
							      	} 
							    },
							    "created_at" : 1,
							    "updated_at" : 1
						     }
						},
						{
						'$sort':{"updated_at":-1,"backtest":1,"deployed":1}
						},
						{'$skip' : max(0,page_num-1)*page_limit },
						{'$limit' : page_limit }
						]
	st = time.time()
	# algo_snaps = models.Algorithm.objects.exec_js(algo_snap_query)
	algo_batch = models.Algorithm._get_collection().aggregate(algo_snap_query_dict)
	# print algo_snaps
	# algo_batch = algo_snaps['_batch']#[:page_limit]

	redis_con = get_redis_connection("default")

	algo_batch2 = []
	for a in algo_batch:
		if a['algo_uuid'] == a['algo_name']:
			algo = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_uuid = a['algo_uuid']
					)
			algo.delete()
		else:
			algo_batch2.append(a)

	algo_batch = algo_batch2
	# print time.time()-st
	# print algo_batch
	for backtests in algo_batch[max(0,page_num-1)*page_limit:max(1,page_num)*page_limit]:
		res = redis_con.keys("deployed:"+user_uuid+':'+backtests['algo_uuid']+':*')
		if len(res)>0:
			backtests['algo_deployed']=True

		if len(backtests['backtest'])!=0:
			c = 0
			for b in backtests['backtest']:#[0]['backtest_result'].keys():
				# res2 = redis_con.keys("deployed:"+user_uuid+':'+backtests['algo_uuid']+':'+b+':*')
				res2 = redis_con.keys("deployed:"+user_uuid+':'+backtests['algo_uuid']+':'+b['seg_sym']+':*')
				if len(res2)>0:
					# backtests['backtest'][0]['backtest_result'][b]['sym_deployed']=True
					# print 'yo'
					backtests['backtest'][c]['backtest_result'][b['seg_sym']]['sym_deployed']=True
				c += 1
	# print algo_batch
	print('time taken',time.time()-st)

	return render(request,'dashboard.html',{'algo':algo_batch})

def dashboard(request):
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
	# fetch the algorithms and then get the backtest results and live results over websocket
	# TODO move the websocket part to Go for better scale

	if request.method=='POST':
		payload = request.POST
	else:
		payload = request.GET

	page_limit = int(payload.get('page_limit',10))
	page_num = int(payload.get('page',1))
	algo_uuids = payload.get('algo_uuids',None)
	# fetching backtest result for the algorithm
	algo_snap_query = """
					function(){
						var results = [];
						results = db[collection].aggregate([{
						$lookup: {
						    from: "backtest_meta",
						    localField: "algo_uuid",
						    foreignField: "algo_uuid",
						    as: "backtest"
							}
						},{
						$lookup: {
						    from: "deployed_algorithm",
						    localField: "algo_uuid",
						    foreignField: "algo_uuid",
						    as: "deployed"
							}
						},
						{
						$match:{
							user_uuid : "%s"
							}
						},
						{ 
						$project : { 
							    "_id" : 1,
							    "algo_uuid" : 1,
							    "algo_name" : 1,
							    "algo_desc" : 1,
							    "entry_logic" : 1,
							    "time_frame": 1,
							    "exit_logic" : 1,
							    "entry_logic" : 1,
							    "position_type" : 1,
							    "quantity" : 1,
							    "stop_loss" : 1,
							    "take_profit" : 1,
							    "backtest" : 1,
							    "deployed" : { 
							    	$filter: 
							    	{ 
							    		input: "$deployed", 
							        	as: "deployed", 
							        	cond: {
							        	 $and:[
							        	 {$gte: [ "$$deployed.expiration_time", ISODate("%s") ]},
							        	 {$eq: [ "$$deployed.status",0 ]}
							        	 ]
							        	} 
							      	} 
							    },
							    "created_at" : 1,
							    "updated_at" : 1
						     }
						},
						{
						$sort:{"updated_at":1,"backtest":1,"deployed":1}
						}
						]);
						return results;
					}"""%(user_uuid,datetime.datetime.now().isoformat())

	algo_snap_query_dict = [{
						'$lookup': {
						    'from': "backtest_meta",
						    'localField': "algo_uuid",
						    'foreignField': "algo_uuid",
						    'as': "backtest"
							}
						},{
						'$lookup': {
						    'from': "deployed_algorithm",
						    'localField': "algo_uuid",
						    'foreignField': "algo_uuid",
						    'as': "deployed"
							}
						},
						{
						'$match':{
							'user_uuid' : user_uuid
							}
						},
						{ 
						'$project' : { 
							    "_id" : 1,
							    "algo_uuid" : 1,
							    "algo_name" : 1,
							    "algo_desc" : 1,
							    "entry_logic" : 1,
							    "time_frame": 1,
							    "exit_logic" : 1,
							    "entry_logic" : 1,
							    "position_type" : 1,
							    "quantity" : 1,
							    "stop_loss" : 1,
							    "take_profit" : 1,
							    "backtest" : 1,
							    "deployed" : { 
							    	'$filter': 
							    	{ 
							    		'input': "$deployed", 
							        	'as': "deployed", 
							        	'cond': {
							        	'$and':[
							        	 {'$gte': [ "$$deployed.expiration_time", datetime.datetime.now().isoformat()]},
							        	 {'$eq': [ "$$deployed.status",0 ]}
							        	 ]
							        	} 
							      	} 
							    },
							    "created_at" : 1,
							    "updated_at" : 1
						     }
						},
						{
						'$sort':{"updated_at":-1,"backtest":1,"deployed":1}
						}
						]

	algo_snap_query_dict = [{
						'$lookup': {
						    'from': "backtest_meta",
						    'localField': "algo_uuid",
						    'foreignField': "algo_uuid",
						    'as': "backtest"
							}
						},{
						'$lookup': {
						    'from': "deployed_algorithm",
						    'localField': "algo_uuid",
						    'foreignField': "algo_uuid",
						    'as': "deployed"
							}
						},
						{
						'$match':{
							'user_uuid' : user_uuid
							}
						},
						{ 
						'$project' : { 
							    "_id" : 1,
							    "algo_uuid" : 1,
							    "algo_name" : 1,
							    "algo_desc" : 1,
							    "entry_logic" : 1,
							    "time_frame": 1,
							    "exit_logic" : 1,
							    "entry_logic" : 1,
							    "position_type" : 1,
							    "quantity" : 1,
							    "stop_loss" : 1,
							    "take_profit" : 1,
							    "backtest" : 1,
							    "deployed" : { 
							    	'$filter': 
							    	{ 
							    		'input': "$deployed", 
							        	'as': "deployed", 
							        	'cond': {
							        	'$and':[
							        	 {'$gte': [ "$$deployed.expiration_time", datetime.datetime.now().isoformat()]},
							        	 {'$eq': [ "$$deployed.status",0 ]}
							        	 ]
							        	} 
							      	} 
							    },
							    "created_at" : 1,
							    "updated_at" : 1
						     }
						},
						{
						'$sort':{"updated_at":-1,"backtest":1,"deployed":1}
						},
						{'$skip' : max(0,page_num-1)*page_limit },
						{'$limit' : page_limit }
						]
	st = time.time()


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
		"overlays"
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
			"volume" : ["obv", "volume"],
			"volatility" : ["natr", "tr", "atr", "vortex"],
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

	# fetching all the algos
	if algo_uuids and algo_uuids!='':
		if request.method=='POST':
			algo_uuids = urllib.unquote(algo_uuids).decode('utf8') 
			algo_uuids = ujson.loads(algo_uuids)
		else:
			algo_uuids = str(algo_uuids).split(',')
				
		algo_batch = models.Algorithm._get_collection().find({'user_uuid':user_uuid,"algo_uuid":{ "$in": algo_uuids}},{ 'html_block':0,'_id':0 }).sort([("updated_at",-1)])
	elif algo_uuids=='':
		algo_batch = []
	elif search!="" and len(search)>2 and filter_dict:
		algo_batch = models.Algorithm._get_collection().find({'user_uuid':user_uuid,"position_type":{ "$in": action_type},"time_frame":{ "$in": time_frame}},{ 'html_block':0,'_id':0 }).sort([("updated_at",-1)])
	elif filter_dict:
		algo_batch = models.Algorithm._get_collection().find({'user_uuid':user_uuid,"position_type":{ "$in": action_type},"time_frame":{ "$in": time_frame}},{ 'html_block':0,'_id':0 }).sort([("updated_at",-1)])
	else:
		algo_batch = models.Algorithm._get_collection().find({'user_uuid':user_uuid},{ 'html_block':0,'_id':0 }).sort([("updated_at",-1)])
	# algo_batch = models.Algorithm._get_collection().find({'user_uuid':user_uuid}).sort([("updated_at",-1)]).skip(max(0,page_num-1)*page_limit).limit(page_limit)
	# algo_snaps = models.Algorithm.objects.exec_js(algo_snap_query)
	# algo_batch = models.Algorithm._get_collection().aggregate(algo_snap_query_dict)
	# print algo_snaps
	# algo_batch = algo_snaps['_batch']#[:page_limit]
	redis_con = get_redis_connection("default")

	algo_batch2 = []
	cur_i = 0

	fav_obj = {}
	if favourite:
		con = get_redis_connection("default")
		fav_obj = con.get("screener_favorites:"+user_uuid)
		if fav_obj:
			fav_obj = ujson.loads(fav_obj).get('strategy',{})

	algo_batch_len = algo_batch.count()

	for a in algo_batch:#.skip(max(0,page_num-1)*page_limit):
		cur_i += 1
		if a['algo_uuid'] == a['algo_name']:
			algo = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_uuid = a['algo_uuid']
					)
			print("deleting algo ",a['algo_uuid'])
			algo.delete()
			cur_i -= 1
		else:
			if search_key!="" and len(search_key)>2:
				if search_key not in a["algo_name"] and search_key not in a["algo_desc"] and search_key not in a["entry_logic"] and search_key not in a["exit_logic"]:
					continue

			if favourite:
				print(fav_obj,a.get("algo_uuid"))
				if fav_obj.get(a.get("algo_uuid"),None) is None:
					# print("continue-->2",a["algo_name"])
					continue
			a["algo_state"]={}
			a["algo_calc"]={}
			if(max(0,page_num-1)*page_limit<=cur_i<=max(0,page_num-1)*page_limit+page_limit):
				backtest = models.BacktestMeta._get_collection().find({'user_uuid':user_uuid,'algo_uuid':a['algo_uuid']},{'_id':0 })
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

				a['backtest'] = b_list

				a["absolute_pnl"]=absolute_pnl
				a["absolute_pnl_pct"]=absolute_pnl_pct
				a["avg_winning_streak"]=avg_winning_streak
				a["avg_lossing_streak"]=avg_lossing_streak
				a["avg_win_loss_ratio"]=avg_win_loss_ratio

				deployed = models.DeployedAlgorithm._get_collection().find({'user_uuid':user_uuid,'algo_uuid':a['algo_uuid'],"expiration_time":{"$gte":datetime.datetime.now()},"status":0},{'_id':0 })
				d_list = []
				for d in deployed:
					d["segment_symbol"]=d["segment"]+"_"+d["symbol"]
					d_list.append(d)
				a['deployed'] = d_list

			elif (cur_i>max(0,page_num-1)*page_limit+page_limit):
				break
			algo_batch2.append(a)

	print('time taken dashboard',time.time()-st)
	algo_batch = algo_batch2
	depl_algo_dict = {}
	depl_algo_cur = models.DeployedAlgorithm._get_collection().find({"user_uuid":user_uuid,"status":0})
	depl_algo_id_dict = {}
	for d in depl_algo_cur:
		depl_algo_dict[d["algo_uuid"]+d["segment"]+"_"+d["symbol"]]=d["status"]
		depl_algo_id_dict[d["algo_uuid"]]=depl_algo_id_dict.get(d["algo_uuid"],0)+1
	# print time.time()-st
	# print algo_batch
	for backtests in algo_batch[max(0,page_num-1)*page_limit:max(1,page_num)*page_limit]:
		if backtests.get('deployed',None) is not None:
			if(len(backtests['deployed'])>0):
				# res = redis_con.keys("deployed:"+user_uuid+':'+backtests['algo_uuid']+':*')
				# res = models.DeployedAlgorithm._get_collection().find({"user_uuid":user_uuid,"algo_uuid":backtests['algo_uuid'],"status":0}).count()
				res = depl_algo_id_dict.get(backtests["algo_uuid"],0)
				if res>0:
					backtests['algo_deployed']=True

				if len(backtests.get('backtest',[]))!=0:
					c = 0
					for b in backtests['backtest']:#[0]['backtest_result'].keys():
						# res2 = redis_con.keys("deployed:"+user_uuid+':'+backtests['algo_uuid']+':'+b+':*')
						# res2 = redis_con.keys("deployed:"+user_uuid+':'+backtests['algo_uuid']+':'+b['seg_sym']+':*')
						# res2 = models.DeployedAlgorithm._get_collection().find({"user_uuid":user_uuid,"algo_uuid":backtests['algo_uuid'],"segment_symbol":b['seg_sym'],"status":0}).count()
						if depl_algo_dict.get(backtests["algo_uuid"]+b['seg_sym'],None) is not None:
							# backtests['backtest'][0]['backtest_result'][b]['sym_deployed']=True
							# print 'yo'
							backtests['backtest'][c]['backtest_result'][b['seg_sym']]['sym_deployed']=True
						c += 1
	# print len(algo_batch)
	if(request.GET.get('resp','')=='json'):
		# print algo_batch
		return JsonResponse({'algo':algo_batch[max(0,page_num-1)*page_limit:max(1,page_num)*page_limit],'pages':int(math.ceil(algo_batch_len/(page_limit*1.0))),'status':'success'})
	elif resp_json:
		return JsonResponse({'algo':algo_batch[max(0,page_num-1)*page_limit:max(1,page_num)*page_limit],'pages':int(math.ceil(algo_batch_len/(page_limit*1.0))),'status':'success'})

	return render(request,'dashboard.html',{'algo':algo_batch})

def dashboard_metrics(request):
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
		print 'no auth'
		if resp_json:
			return JsonResponse({"status":"error","error":"auth"},status=401)
		return redirect('home')

	if(request.session.get('stock',None)!=None):
		return redirect('strategy')
	
	subscription_start_before_login = False
	subscription_start_before_login_subscription_plan = 'None'
	subscription_start_before_login_subscription_plan_id = -1
	if(request.session.pop('subscription_start_before_login',False)):
		subscription_start_before_login = True
		subscription_start_before_login_subscription_plan = request.session.pop('subscription_start_before_login_subscription_plan','None')
		subscription_start_before_login_subscription_plan_id = request.session.pop('subscription_start_before_login_subscription_plan_id',-1)

	con = get_redis_connection("default")
	phrase_keys = con.keys('dashboard_metrics_phrases:*')
	welcome_phrase = {}
	if phrase_keys:
		i = random.randint(0,len(phrase_keys)-1)
		p = con.get(phrase_keys[i])
		welcome_phrase = eval(p)

	img_url = con.get('whats_new2')
	if img_url is not None:
		img_url = json.loads(img_url)
		link_to = unicode(img_url['web'].get('linkTo',''))
		img_url = unicode(img_url['web'].get('img',''))
		if img_url=='':
			img_url = 'https://streak.zerodha.com/static/imgs/new/mcx.png'
	else:
		img_url = 'https://streak.zerodha.com/static/imgs/new/mcx.png'
	show_phone_popup = request.session.pop('show_phone_popup',False)
	return render(request,'dashboard_metrics.html',{'subscription_start_before_login':subscription_start_before_login,'subscription_start_before_login_subscription_plan':subscription_start_before_login_subscription_plan,'subscription_start_before_login_subscription_plan_id':subscription_start_before_login_subscription_plan_id,'welcome_phrase':welcome_phrase,'show_phone_popup':show_phone_popup})

def welcome_algo(request):
	resp_json = False
	if(request.META.get('HTTP_X_CSRFTOKEN',None)):
		resp_json = True
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "localc" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
		request.session['user_is_auth'] = True
		request.session['user_uuid'] = '123'
	# user_uuid = '0f2dd64c-c1b6-4eca-8ea1-fd08e3251c7b'

	if not user_is_auth:
		if resp_json:
			return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)
		return redirect('home')

	# fetch the algorithms and then get the backtest results and live results over websocket
	# TODO move the websocket part to Go for better scale

	page_limit = int(request.GET.get('page_limit',10))
	page_num = int(request.GET.get('page',1))
	# fetching backtest result for the algorithm
	algo_snap_query = """
					function(){
						var results = [];
						results = db[collection].aggregate([{
						$lookup: {
						    from: "backtest_meta",
						    localField: "algo_uuid",
						    foreignField: "algo_uuid",
						    as: "backtest"
							}
						},{
						$lookup: {
						    from: "deployed_algorithm",
						    localField: "algo_uuid",
						    foreignField: "algo_uuid",
						    as: "deployed"
							}
						},
						{
						$match:{
							user_uuid : "%s"
							}
						},
						{ 
						$project : { 
							    "_id" : 1,
							    "algo_uuid" : 1,
							    "algo_name" : 1,
							    "algo_desc" : 1,
							    "entry_logic" : 1,
							    "time_frame": 1,
							    "exit_logic" : 1,
							    "entry_logic" : 1,
							    "position_type" : 1,
							    "quantity" : 1,
							    "stop_loss" : 1,
							    "take_profit" : 1,
							    "backtest" : 1,
							    "deployed" : { 
							    	$filter: 
							    	{ 
							    		input: "$deployed", 
							        	as: "deployed", 
							        	cond: {
							        	 $and:[
							        	 {$gte: [ "$$deployed.expiration_time", ISODate("%s") ]},
							        	 {$eq: [ "$$deployed.status",0 ]}
							        	 ]
							        	} 
							      	} 
							    },
							    "created_at" : 1,
							    "updated_at" : 1
						     }
						},
						{
						$sort:{"updated_at":1,"backtest":1,"deployed":1}
						}
						]);
						return results;
					}"""%(user_uuid,datetime.datetime.now().isoformat())

	algo_snap_query_dict = [{
						'$lookup': {
						    'from': "backtest_meta",
						    'localField': "algo_uuid",
						    'foreignField': "algo_uuid",
						    'as': "backtest"
							}
						},{
						'$lookup': {
						    'from': "deployed_algorithm",
						    'localField': "algo_uuid",
						    'foreignField': "algo_uuid",
						    'as': "deployed"
							}
						},
						{
						'$match':{
							'user_uuid' : user_uuid
							}
						},
						{ 
						'$project' : { 
							    "_id" : 1,
							    "algo_uuid" : 1,
							    "algo_name" : 1,
							    "algo_desc" : 1,
							    "entry_logic" : 1,
							    "time_frame": 1,
							    "exit_logic" : 1,
							    "entry_logic" : 1,
							    "position_type" : 1,
							    "quantity" : 1,
							    "stop_loss" : 1,
							    "take_profit" : 1,
							    "backtest" : 1,
							    "deployed" : { 
							    	'$filter': 
							    	{ 
							    		'input': "$deployed", 
							        	'as': "deployed", 
							        	'cond': {
							        	'$and':[
							        	 {'$gte': [ "$$deployed.expiration_time", datetime.datetime.now().isoformat()]},
							        	 {'$eq': [ "$$deployed.status",0 ]}
							        	 ]
							        	} 
							      	} 
							    },
							    "created_at" : 1,
							    "updated_at" : 1
						     }
						},
						{
						'$sort':{"updated_at":-1,"backtest":1,"deployed":1}
						}
						]

	algo_snap_query_dict = [{
						'$lookup': {
						    'from': "backtest_meta",
						    'localField': "algo_uuid",
						    'foreignField': "algo_uuid",
						    'as': "backtest"
							}
						},{
						'$lookup': {
						    'from': "deployed_algorithm",
						    'localField': "algo_uuid",
						    'foreignField': "algo_uuid",
						    'as': "deployed"
							}
						},
						{
						'$match':{
							'user_uuid' : user_uuid
							}
						},
						{ 
						'$project' : { 
							    "_id" : 1,
							    "algo_uuid" : 1,
							    "algo_name" : 1,
							    "algo_desc" : 1,
							    "entry_logic" : 1,
							    "time_frame": 1,
							    "exit_logic" : 1,
							    "entry_logic" : 1,
							    "position_type" : 1,
							    "quantity" : 1,
							    "stop_loss" : 1,
							    "take_profit" : 1,
							    "backtest" : 1,
							    "deployed" : { 
							    	'$filter': 
							    	{ 
							    		'input': "$deployed", 
							        	'as': "deployed", 
							        	'cond': {
							        	'$and':[
							        	 {'$gte': [ "$$deployed.expiration_time", datetime.datetime.now().isoformat()]},
							        	 {'$eq': [ "$$deployed.status",0 ]}
							        	 ]
							        	} 
							      	} 
							    },
							    "created_at" : 1,
							    "updated_at" : 1
						     }
						},
						{
						'$sort':{"updated_at":-1,"backtest":1,"deployed":1}
						},
						{'$skip' : max(0,page_num-1)*page_limit },
						{'$limit' : page_limit }
						]
	st = time.time()
	# fetching all the algos
	algo_batch = models.Algorithm._get_collection().find({'user_uuid':user_uuid},{ 'html_block':0,'_id':0 }).sort([("updated_at",-1)]).limit(5)
	# algo_batch = models.Algorithm._get_collection().find({'user_uuid':user_uuid}).sort([("updated_at",-1)]).skip(max(0,page_num-1)*page_limit).limit(page_limit)
	# algo_snaps = models.Algorithm.objects.exec_js(algo_snap_query)
	# algo_batch = models.Algorithm._get_collection().aggregate(algo_snap_query_dict)
	# print algo_snaps
	# algo_batch = algo_snaps['_batch']#[:page_limit]
	redis_con = get_redis_connection("default")

	algo_batch2 = []
	cur_i = 0
	backtest_found = False
	for a in algo_batch:
		cur_i += 1
		if a['algo_uuid'] == a['algo_name']:
			algo = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_uuid = a['algo_uuid']
					)
			algo.delete()
			cur_i -= 1
		else:
			if(max(0,page_num-1)*page_limit<=cur_i<=max(0,page_num-1)*page_limit+page_limit):
				# print ';;;;;;;;;;;;;;;',user_uuid,a['algo_uuid']
				backtest = models.Backtest._get_collection().find({'user_uuid':user_uuid,'algo_uuid':a['algo_uuid']},{'_id':0 })
				b_list = []
				for b in backtest:
					backtest_found
					b_list.append(b)
				if b_list!=[]:
					backtest_found = True
				a['backtest'] = b_list
				d_list = []
				a['deployed'] = d_list
				if b_list!=[]:
					algo_batch2.append(a)
			if backtest_found==True:
				break

	print('time taken dashboard',time.time()-st)
	algo_batch = algo_batch2
	# print time.time()-st
	# print algo_batch
	for backtests in algo_batch[max(0,page_num-1)*page_limit:max(1,page_num)*page_limit]:
		res = redis_con.keys("deployed:"+user_uuid+':'+backtests['algo_uuid']+':*')
		if len(res)>0:
			backtests['algo_deployed']=True

		if len(backtests.get('backtest',[]))!=0:
			c = 0
			for b in backtests['backtest']:#[0]['backtest_result'].keys():
				# res2 = redis_con.keys("deployed:"+user_uuid+':'+backtests['algo_uuid']+':'+b+':*')
				# res2 = redis_con.keys("deployed:"+user_uuid+':'+backtests['algo_uuid']+':'+b['seg_sym']+':*')
				res2 = get_deployment_keys({"user_uuid":user_uuid,"algo_uuid":backtests['algo_uuid'],"segment_symbol":b['seg_sym'],"status":0,"expiration_time":{"$gte":datetime.datetime.now()}})
				if len(res2)>0:
					# backtests['backtest'][0]['backtest_result'][b]['sym_deployed']=True
					# print 'yo'
					backtests['backtest'][c]['backtest_result'][b['seg_sym']]['sym_deployed']=True
				c += 1
	# print len(algo_batch)
	# if(request.GET.get('resp','')=='json'):
		# print algo_batch
		# return JsonResponse({'algo':algo_batch[max(0,page_num-1)*page_limit:max(1,page_num)*page_limit],'pages':int(math.ceil(len(algo_batch)/(page_limit*1.0))),'status':'success'})
	# elif resp_json:
	return JsonResponse({'algo':algo_batch[max(0,page_num-1)*page_limit:max(1,page_num)*page_limit],'total_pages':int(math.ceil(len(algo_batch)/(page_limit*1.0))),'status':'success'})

	# return render(request,'dashboard.html',{'algo':algo_batch})

def discover_watch_list(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error","msg":"auth"})
	
	fixed_watch_list = ["NSE-INDICES_NIFTY 50","NSE-INDICES_NIFTY BANK","NSE_RELIANCE","NSE_HDFC","NSE_SBIN","NSE_TATASTEEL","NSE_TCS","NSE_ICICIBANK","NSE_INFY","NSE_L&TFH","NSE_TATAMOTORS"]

	if request.method == 'GET':
		instruments_list = []
		conn = get_redis_connection("default")

		dw = conn.get('discover_watch_list_'+user_uuid)
		if dw is not None:
			dw = ujson.loads(dw)
			instruments_list = dw.get('instruments_list',[])
		if dw is None or len(instruments_list)==0:
			# if len(instruments_list)<10:
			instruments_list += fixed_watch_list
			conn.set('discover_watch_list_'+user_uuid,ujson.dumps({'instruments_list':instruments_list}))
		# print saved_baskets
		return JsonResponse({"status":"success","instruments_list":instruments_list})

	if request.method == 'POST':
		seg_sym = request.POST.get('seg_sym','')
		basket_del = request.POST.get('del','false')

		conn = get_redis_connection("default")
		if seg_sym!='' and not basket_del!='false':
			dw = conn.get('discover_watch_list_'+user_uuid)
			if dw is not None:
				dw = ujson.loads(dw)
				instruments_list = dw.get('instruments_list',[])
				instruments_list = [seg_sym] + instruments_list
				dw['instruments_list']=list(set(instruments_list))
				conn.set('discover_watch_list_'+user_uuid,ujson.dumps(dw))
			else:
				dw = {'instruments_list':[seg_sym]}
				conn.set('discover_watch_list_'+user_uuid,ujson.dumps(dw))
		elif seg_sym!='' and basket_del=='true':
			dw = conn.get('discover_watch_list_'+user_uuid)
			if dw is not None:
				dw = ujson.loads(dw)
				instruments_list = dw.get('instruments_list',[])
				instruments_list_new = []
				for i in instruments_list:
					if i!=seg_sym:
						instruments_list_new.append(i)
				dw['instruments_list']=instruments_list_new
				conn.set('discover_watch_list_'+user_uuid,ujson.dumps(dw))
			# else:
			# 	dw = {'instruments_list':[seg_sym]}
			# 	conn.set('discover_watch_list_'+user_uuid,ujson.loads(dw))

		return JsonResponse({"status":"success"})

	# if request.method == 'DELETE':
	# 	basket_name = request.DELETE.get('basket_name','')
	# 	if(basket_name==''):
	# 		return JsonResponse({"status":"error","msg":"Basket name missing"})
	# 	conn = get_redis_connection("default")
	# 	basket_deleted = conn.hdel('baskets_'+user_uuid,basket_name)
	# 	return JsonResponse({"status":"success"})

	return JsonResponse({"status":"error","msg":"unknown"})

def dashboard_discover(request):
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

	fixed_watch_list = ["NSE-INDICES_NIFTY 50","NSE-INDICES_NIFTY BANK","NSE_RELIANCE","NSE_HDFC","NSE_SBIN","NSE_TATASTEEL","NSE_TCS","NSE_ICICIBANK","NSE_INFY","NSE_L&TFH","NSE_TATAMOTORS"]

	if request.method!='GET':
		return JsonResponse({"status":"error","error":"Invalid method","error_msg":"Invalid method"},status=403)
	else:
		page_limit = int(request.GET.get('page_limit',40))
		page_num = int(request.GET.get('page',1))
		seg_sym = request.GET.get('seg_sym',"")
		# making set of stocks in user holdings and positions
		instruments_list = []
		discover_obj = []
		instruments_dict = {}
		conn = get_redis_connection("default")
		dw = conn.get('discover_watch_list_'+user_uuid)

		if seg_sym=="":
			headers = {}
			if settings.KITE_HEADER == True:
				headers = {"X-Kite-Version":"3"}
				auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
				headers["Authorization"] = "token {}".format(auth_header)

			try: 
				response = requests.get("https://api-partners.kite.trade/portfolio/holdings/?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token','')),headers=headers,timeout=1)
				# print 'request url',"https://api-partners.kite.trade/portfolio/holdings/?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token',''))
				
				if response.status_code == 200:
					response_json = json.loads(response.text)
					if response_json['status']=="success":
						for n in response_json['data']:
			 				segment = 'NSE'
							if n['exchange']=='MCX':
			 					segment = 'MCX'
			 				elif n['exchange']=='NFO':
			 					if str(n['tradingsymbol']).endswith("CE") or str(n['tradingsymbol']).endswith("PE"):
			 						segment = 'NFO-OPT'
			 					else:
			 						segment = 'NFO-FUT'
			 				elif n['exchange']=='CDS':
			 					segment = 'CDS-FUT'
			 				else:
			 					segment = n['exchange']

							# instruments_list.append([segment+"_"+n['tradingsymbol'],segment,n['tradingsymbol']])
							instruments_dict[segment+"_"+n['tradingsymbol']]=[segment,n['tradingsymbol']]

				response = requests.get("https://api-partners.kite.trade/portfolio/positions/?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token','')),headers=headers,timeout=1)
				# print 'request url',"https://api-partners.kite.trade/portfolio/positions/?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token',''))
				if response.status_code == 200:
					response_json = json.loads(response.text)
					if response_json['status']=="success":
						for n in response_json['data']["net"]:
			 				segment = 'NSE'
							if n['exchange']=='MCX':
			 					segment = 'MCX'
			 				elif n['exchange']=='NFO':
			 					if str(n['tradingsymbol']).endswith("CE") or str(n['tradingsymbol']).endswith("PE"):
			 						segment = 'NFO-OPT'
			 					else:
			 						segment = 'NFO-FUT'
			 				elif n['exchange']=='CDS':
			 					segment = 'CDS-FUT'
			 				else:
			 					segment = n['exchange']

							# instruments_list.append(segment+"_"+n['tradingsymbol'])
							instruments_dict[segment+"_"+n['tradingsymbol']]=[segment,n['tradingsymbol']]
			except:
				print(traceback.format_exc())
				
			instruments_list = instruments_dict.keys()
			instruments_list_1 = instruments_list + fixed_watch_list
		else:
			instruments_dict = {seg_sym:seg_sym}
			instruments_list_1 = [seg_sym]
			instruments_list = instruments_list_1

		if instruments_dict!={}:
			backtest = models.PublishedBacktestsMeta._get_collection().find({"seg_sym":{"$in":instruments_list_1}},{'_id':0 ,'algo_obj':0}).sort([("backtest_result_meta.returns",-1)])
		else:
			backtest = models.PublishedBacktestsMeta._get_collection().find({},{'_id':0 ,'algo_obj':0}).sort([("backtest_result_meta.returns",-1)])

		b_list = []
		b_dict = {}
		publishing_uuid_list = []
		for b in backtest:
			# TODO Remove algo condition related objects
			# print (b_dict,b_dict.get(b["publishing_uuid"],""))
			if b["publishing_uuid"] not in b_dict.keys():
				b_dict[b["publishing_uuid"]]=[b]
			else:
				if b.get("backtest_result_meta",{}).get("returns",0)>b_dict[b["publishing_uuid"]][0].get("backtest_result_meta",{}).get("returns",0):
					b_dict[b["publishing_uuid"]]=[b]
			# publishing_uuid_list.append(b["publishing_uuid"])
			# b_list.append(b)
		publishing_uuid_list = b_dict.keys()
		published_algos = models.PublishedAlgos._get_collection().find({"publish_status":{ "$in": [1,2]},"publishing_uuid":{"$in":publishing_uuid_list}},{ 'html_block':0,'_id':0,'algo_obj':0 }).sort([("updated_at",-1),("publish_status",-1)])
		cur_i = 0
		viewer_dict = {}
		for a in published_algos:
			viewer_dict[a["algo_uuid"]]=0
			a["backtests"]=b_dict[a["publishing_uuid"]]
			discover_obj.append(a)
		subscribed_algos_list = []

		viewer_dict = view_calculator(viewer_dict)
		# for s in subscribed_algos:
		# 	subscribed_algos_list.append([s["publishing_uuid"],s["algo_subscription_uuid"]])

		# subscribed_algos_deployed = models.DeployedAlgorithm._get_collection().find({'user_uuid':user_uuid,"subscription_expiry":{ "$gt": datetime.datetime.now()},"explore_algo":True},{'_id':0 }).sort([("updated_at",-1)])
		subscribed_algos_deployed_list = []
		# for d in subscribed_algos_deployed:
		# 	subscribed_algos_deployed_list.append([d["algo_uuid"],d["segment_symbol"]])
		instruments_list_saved = []
		
		if dw is not None:
			dw = ujson.loads(dw)
			instruments_list_saved = dw.get('instruments_list',[])
			instruments_list = instruments_list_saved
		if len(instruments_list)<10 and (dw is None or len(instruments_list_saved)==0):
			instruments_list += fixed_watch_list
		instruments_list = list(set(instruments_list))
		if dw is None:
			dw = {}
			dw['instruments_list']=list(set(instruments_list))
			conn.set('discover_watch_list_'+user_uuid,ujson.dumps(dw))
			
		if(request.GET.get('resp','')=='json'):
			# print algo_batch
			return JsonResponse({'algo':discover_obj[max(0,page_num-1)*page_limit:max(1,page_num)*page_limit],'pages':int(math.ceil(len(discover_obj)/(page_limit*1.0))),'status':'success',"subscribed_algos":subscribed_algos_list,"subscribed_algos_deployed":subscribed_algos_deployed_list,"instruments_list":instruments_list,"viewer_dict":viewer_dict})
		elif resp_json:
			return JsonResponse({'algo':discover_obj[max(0,page_num-1)*page_limit:max(1,page_num)*page_limit],'pages':int(math.ceil(len(discover_obj)/(page_limit*1.0))),'status':'success',"subscribed_algos":subscribed_algos_list,"subscribed_algos_deployed":subscribed_algos_deployed_list,"instruments_list":instruments_list,"viewer_dict":viewer_dict})
		# return JsonResponse({"status":"error","error":"Invalid method","error_msg":"Invalid method"},status=403)
	return JsonResponse({"status":"error","error_msg":"Unknwon error"})


def dashboard_recommendations(request):
	# Title
	# body
	# button
	# Subscribe
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

	top_banner = {"image_urls":[],"actionable_url":[]}
	central_banner = {}
	user_subscription = None
	try:
		user_subscription = models.UserSubscription.objects.get(user_uuid=user_uuid)
		# print(user_subscription.subscription_type!=3 , user_subscription.subscription_period!="12" , user_subscription.subscription_type>0 , user_subscription.subscription_validity>datetime.datetime.now())

		if not (user_subscription.subscription_type==3 and user_subscription.subscription_period=="12") and user_subscription.subscription_type>0 and user_subscription.subscription_validity>datetime.datetime.now():
			# title = "Get 30% off"
			title = "Festive Offer"
			# body = "Upgrade plan and get great discounts"
			body = "Upgrade to any annual plan and get flat 30% off + plan extension for 3 additional months"
			tag = "promotional"
			actionable = "Subscribe"
			actionable_url = "/billing"
			central_banner = {"title":title,"body":body,"tag":tag,"actionable":actionable,"actionable_url":actionable_url}
		elif user_subscription.subscription_type==0 and user_subscription.subscription_validity>datetime.datetime.now():
			# title = "Get 30% off"
			title = "Festive Offer"
			# body = "Trial expires soon, subscribe now for uninterrupted service"
			body = "Buy any annual plan and get flat 30% off + plan extension for 3 additional months"
			tag = "promotional"
			actionable = "Subscribe"
			actionable_url = "/billing"
			central_banner = {"title":title,"body":body,"tag":tag,"actionable":actionable,"actionable_url":actionable_url}
		elif user_subscription.subscription_validity<datetime.datetime.now():
			# title = "Get 30% off"
			title = "Festive Offer"
			# body = "Your plan has expired, subscribe now get going"
			body = "Buy any annual plan and get flat 30% off + plan extension for 3 additional months"
			tag = "promotional"
			actionable = "Subscribe"
			actionable_url = "/billing"
			central_banner = {"title":title,"body":body,"tag":tag,"actionable":actionable,"actionable_url":actionable_url}

	except:
		print(traceback.format_exc())


	return JsonResponse({"status":"success","top_banner":top_banner,"central_banner":central_banner})