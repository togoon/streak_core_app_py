from django.shortcuts import render,redirect
from django.http import JsonResponse
# import haslib
import random
import uuid
import datetime
import traceback
from django.conf import settings
from django_redis import get_redis_connection
from coreapp import models
from coreapp.views.utility import update_usage_util,get_deployment_keys,dynamic_sym_params_generator
import string
import json,ujson
import re
import urllib
import time
import requests
import calendar
from mongoengine import DoesNotExist
monthMap = {}
monthMap[1] = "JAN"
monthMap[2] = "FEB"
monthMap[3] = "MAR"
monthMap[4] = "APR"
monthMap[5] = "MAY"
monthMap[6] = "JUN"
monthMap[7] = "JUL"
monthMap[8] = "AUG"
monthMap[9] = "SEP"
monthMap[10] = "OCT"
monthMap[11] = "NOV"
monthMap[12] = "DEC"

def backtest(request):
	resp_json = False
	if(request.META.get('HTTP_X_CSRFTOKEN',None)):
		resp_json = True
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		if resp_json:
			return JsonResponse({"status":"error","error":"auth"},status=401)
		return redirect('login')
		
	if request.method == "GET":
		#return JsonResponse({"status":"error","error":"auth"},status=401)
		algo_uuid = request.GET.get('algo_uuid','')
		max_count = int(request.GET.get('max_count',-1))
		if (algo_uuid==''):
			algo = models.Algorithm._get_collection().find({'user_uuid':user_uuid}).sort([("created_at",-1)]).limit(1)
			for a in algo:
				algo_uuid = a.get('algo_uuid','')
				# print 'yoooooo algo uuid',algo_uuid
		try:
			st = time.time()

			if max_count==-3:
				backtest_count = models.BacktestMeta.objects(algo_uuid = algo_uuid,
                                                user_uuid = user_uuid).count()
				backtest_item = models.BacktestMeta.objects(
						algo_uuid = algo_uuid,
						user_uuid = user_uuid
						)
			else:
				backtest_item = models.Backtest.objects(
						algo_uuid = algo_uuid,
						user_uuid = user_uuid
						)
				backtest_count = models.Backtest.objects(algo_uuid = algo_uuid,
                                                user_uuid = user_uuid).count()
			
			print '...............................',time.time()-st,backtest_count
			if backtest_count<1:
				print 'yoooooo'
			backtest_0 = backtest_item[0]
			print '--########-----##########--',time.time()-st
			algo_name = backtest_0.algo_obj['algo_name']
			print '--########-----####---######--',time.time()-st
			
			algo_desc = backtest_0.algo_obj.get('algo_desc','')
			position_type = backtest_0.algo_obj['action_type']
			position_qty = backtest_0.algo_obj['quantity']
			entry_logic = backtest_0.algo_obj['action_str']
			# exit_logic = backtest_item.algo_obj['exit_logic']
			exit_logic = backtest_0.algo_obj.get('action_str_exit','')
			take_profit = backtest_0.algo_obj['take_profit']
			stop_loss = backtest_0.algo_obj['stop_loss']
			ip_interval = backtest_0.algo_obj['time_frame']
			holding_type = backtest_0.algo_obj.get('holding_type','MIS')

			# advanced parameters
			chart_type = backtest_0.algo_obj.get('chart_type','candlestick')
			trade_time_given = backtest_0.algo_obj.get('trade_time_given',"False")
			trading_start_time = backtest_0.algo_obj.get('trading_start_time','09:00')
			trading_stop_time = backtest_0.algo_obj.get('trading_stop_time','23:30')
			create_plus = backtest_0.algo_obj.get('create_plus',False)
			daily_strategy_cycle = backtest_0.algo_obj.get('daily_strategy_cycle','-')
			tpsl_type = backtest_0.algo_obj.get('tpsl_type','pct')
			max_allocation =backtest_0.algo_obj.get('max_allocation','')
			position_sizing_type = backtest_0.algo_obj.get('position_sizing_type','-')
			#--------------------#

			start_time = backtest_0.algo_obj['dt_start']
			stop_time = backtest_0.algo_obj['dt_stop']
			
			try:
				min_candle_freq = backtest_0.algo_obj['min_candle_freq']
			except:
				min_candle_freq = 1000
			equities = {}
			print '--##################--',time.time()-st
			backtest_items_json = ujson.loads(backtest_item.to_json())
			backtest_items_list = []
			scripList = []
			# coding for v4 web to return data values from the also algo state
			# algo = models.Algorithm._get_collection().find_one({'user_uuid':user_uuid,'algo_uuid':algo_uuid})
			# algo_name = algo["algo_name"]
			# algo_desc = algo["algo_desc"]
			# position_type = algo["algo_state"].get("positionType","BUY")
			# position_qty = algo["algo_state"].get("quantity","0")
			# entry_logic = algo["entry_logic"]
			# exit_logic = algo["exit_logic"]
			# take_profit = algo["algo_state"].get("takeProfit","0")
			# min_candle_freq = algo["min_candle_freq"]
			# ip_interval = algo["time_frame"]
			# scripListAlgo = algo["algo_state"].get("scripList",[])
			# scripListDict = {}
			# for sl in scripListAlgo:
			# 	scripListDict[sl["segment"]+"_"+["symbol"]]=1

			for bt in backtest_items_json:
				for k in bt['algo_obj']['symbols']: 
					equities[k[1]]=k[0]
					scripList.append({"symbol":k[1],"segment":k[0]})
				k2 = bt["seg_sym"]
				if k2 in bt["backtest_result"].keys():
					if max_count==-3:
						bt["backtest_result_meta"]={}
					elif max_count==-1:
						pass
					elif max_count == -2:	
						bt["backtest_result"][k2]["pnl"] = []
					else:
						bt["backtest_result"][k2]["pnl"]=downsample(bt["backtest_result"][k2]["pnl"],max_count)
				backtest_items_list.append(bt)
					# equities.append(k[0]+'_'+k[1])

			print '-------------------------',time.time()-st
			if len(backtest_items_list)>0:
				bt_o_seg_sym = backtest_items_list[0].get("seg_sym","")
				bt_o_runparams = backtest_items_list[0]["backtest_result"].get(bt_o_seg_sym)
				# if bt_o_runparams.get("user_uuid","")!=user_uuid:
				# 	backtest_items_list[0]["algo_obj"]["scripList"]=scripList
				# 	backtest_items_list[len(backtest_items_list)-1]["algo_obj"]["scripList"]=scripList
			# { "dt_stop" : "10/08/2017", "stop_loss" : "4.0", "algo_uuid" : "4fcc3234-d02f-4cbb-8cb1-b35d353b8971", "initial_capital" : "100000", "time_frame" : "hour", "user_uuid" : "123", "dt_start" : "10/08/2016", "symbols" : [ [ "NSE", "HDFCBANK" ] ], "commission" : 0, "action_type" : "BUY", "take_profit" : "4.0", "action_str" : "2 min SMA higher than 4 min SMA", "algo_name" : "Cloned from ABC", "algo_desc" : "aaaa", "quantity" : "10" }
			redis_con = get_redis_connection("default")

			algo_deployed=False
			deployed_seg_sym = []
			deployed_seg_sym_deployment_uuid = {}
			# res = redis_con.keys('deployed:'+user_uuid+':'+algo_uuid+':*')
			res = get_deployment_keys({"user_uuid":user_uuid,"algo_uuid":algo_uuid,"status":0,"expiration_time":{"$gte":datetime.datetime.now()}})

			# res = models.DeployedAlgorithm.objects(user_uuid=user_uuid,algo_uuid=algo_uuid,status=0)
			if len(res)>0:
				algo_deployed=True
				for k in res:
					k = k.split(':')
					deployed_seg_sym.append(k[3])
					deployed_seg_sym_deployment_uuid[k[3]] = k[-1]

			# algo_pref = 
			print '--###########2222222#######--',time.time()-st
			if(request.GET.get('resp','')=='json' or resp_json):
				return JsonResponse({'status':'success',
					'user_uuid':user_uuid,
					'algo_uuid':algo_uuid,
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
					'daily_strategy_cycle':daily_strategy_cycle,
					'tpsl_type': tpsl_type,
					'max_allocation':max_allocation,
					'position_sizing_type':position_sizing_type,
					#----------------#
					'bt_url1':settings.BT_URL1,
					'bt_url2':settings.BT_URL2,
					'run_backtest_flag':False,
					'backtest_results':backtest_items_json,#.items()
					'algo_deployed':algo_deployed,
					'deployed_seg_sym':deployed_seg_sym,
					'deployed_seg_sym_deployment_uuid':deployed_seg_sym_deployment_uuid})

			return render(request,'multiple_backtests.html',
				{'status':'success',
					'user_uuid':user_uuid,
					'algo_uuid':algo_uuid,
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
					'daily_strategy_cycle':daily_strategy_cycle,
					'tpsl_type': tpsl_type,
					'max_allocation':max_allocation,
					'position_sizing_type':position_sizing_type,
					#----------------#
					'bt_url1':settings.BT_URL1,
					'bt_url2':settings.BT_URL2,
					'run_backtest_flag':False,
					'backtest_results':backtest_item.to_json(),#.items()
					'algo_deployed':algo_deployed,
					'deployed_seg_sym':json.dumps(deployed_seg_sym),
					'deployed_seg_sym_deployment_uuid':json.dumps(deployed_seg_sym_deployment_uuid)
					})
		except:
			print traceback.format_exc()
			try:
				algo = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_uuid = algo_uuid
					)
				printable = set(string.printable)

				algo_name = algo.algo_name#.decode('hex')
				algo_desc = algo.algo_desc#.decode('hex')
				position_type = algo.position_type
				if(int(position_type)==1):
					position_type = 'BUY'
				elif(int(position_type)==-1):
					position_type = 'SELL'
				else:
					position_type = 'HOLD'

				position_qty = algo.quantity
				# equities = algo.get('equities','').decode('hex')#'\x00{\x00"\x00H\x00D\x00F\x00C\x00B\x00A\x00N\x00K\x00"\x00:\x00"\x00N\x00S\x00E\x00"\x00}'
				equities = []
				# print equities
				entry_logic = algo.entry_logic#.decode('hex')
				exit_logic = algo.exit_logic#.decode('hex')
				take_profit = algo.take_profit
				stop_loss = algo.stop_loss
				create_plus = algo.create_plus
				try:
					min_candle_freq = algo.min_candle_freq
				except:
					min_candle_freq = 1000
				curr_time = datetime.datetime.now()
				start_time = datetime.datetime.strftime(curr_time-datetime.timedelta(6*365/6-1),'%d/%m/%Y')
				stop_time = datetime.datetime.strftime(curr_time,'%d/%m/%Y')
				# TODO if algo_uuid != '', run some task to save it, etc
				# try:
				# 	if algo_uuid == '':
				# 		algo_uuid = request.session.pop('algo_uuid','')

				# 	assert algo_uuid != ''
				# except:
				# 	# redirect to dashboard if algo_uuid is none
				# 	pass
				print 'algo_uuid',algo_uuid
				holding_type_temp = 'MIS'
				# if(ip_interval=='day'):
				# 	holding_type_temp = 'CNC'
				# print('trading_start_time',trading_start_time)
				if(request.GET.get('resp','')=='json' or resp_json):
					return JsonResponse({'status':'success',
							'user_uuid':user_uuid,
							'algo_uuid':algo_uuid,
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
							'ip_interval':algo.time_frame,
							'holding_type':holding_type_temp,
							# advanced fields
							'chart_type':'candlestick',
							'trade_time_given':False,
							'trading_start_time':'09:00',
							'trading_stop_time':'23:59',
							'create_plus':create_plus,
							'daily_strategy_cycle':'-',
							'tpsl_type': 'pct',
							'max_allocation':'',
							'position_sizing_type':'-',
							#----------------#
							'start_time':start_time,
							'stop_time':stop_time,
							'bt_url1':settings.BT_URL1,
							'bt_url2':settings.BT_URL2,
							'algo_deployed':False,
							'deployed_seg_sym':[],
							'backtest_results':[],
							'deployed_seg_sym_deployment_uuid':{}
							})

				return render(request,'multiple_backtests.html',
							{'status':'success',
							'user_uuid':user_uuid,
							'algo_uuid':algo_uuid,
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
							'ip_interval':'hour',
							'holding_type':holding_type_temp,
							# advanced fields
							'chart_type':'candlestick',
							'trade_time_given':False,
							'trading_start_time':'09:00',
							'trading_stop_time':'23:30',
							'create_plus':create_plus,
							#----------------#
							'start_time':start_time,
							'stop_time':stop_time,
							'bt_url1':settings.BT_URL1,
							'bt_url2':settings.BT_URL2,
							'algo_deployed':False,
							'deployed_seg_sym':[],
							'backtest_results':[],
							'deployed_seg_sym_deployment_uuid':{}
							})
			except:
				print traceback.format_exc()
				pass
			print traceback.format_exc()
			if(request.GET.get('resp','')=='json'):
				print algo_uuid
				return JsonResponse({'status':'error','error':'Strategy not found'})
			return redirect('dashboard')
			# return JsonResponse({'status':'error'})
		# use user_uuid and algo_uuid to fetch the list of mongosave backtests
		# try:
		# 	if algo_uuid == '':
		# 		algo_uuid = request.session.pop('algo_uuid','')

		# 	assert algo_uuid != ''
		# except:
		# 	# redirect to dashboard if algo_uuid is none
		# 	pass
		return render(request,'multiple_backtests.html',
					{'status':'success',
					'user_uuid':user_uuid
					})

	if request.method == "POST":
		printable = set(string.printable)

		algo_uuid = request.POST.get('algo_uuid','')#.decode('hex')
		# .decode("hex")
		# print algo_uuid
		algo_name = request.POST.get('algo_name','')#.decode('hex')
		algo_desc = request.POST.get('algo_desc','')#.decode('hex')
		position_type = request.POST.get('position_type','')
		position_qty = request.POST.get('position_qty','')
		ip_interval = request.POST.get('time_frame','hour')

		equities = request.POST.get('equities','').decode('hex')#'\x00{\x00"\x00H\x00D\x00F\x00C\x00B\x00A\x00N\x00K\x00"\x00:\x00"\x00N\x00S\x00E\x00"\x00}'
		equities = eval(filter(lambda x: x in printable, equities))
		# print equities
		entry_logic = request.POST.get('entry_logic')#.decode('hex')
		exit_logic = request.POST.get('exit_logic')#.decode('hex')
		take_profit = request.POST.get('take_profit').strip('%')
		stop_loss = request.POST.get('stop_loss').strip('%')

		min_candle_freq = request.POST.get('min_candle_freq',1000)
		
		holding_type = request.POST.get('holding_type','MIS')
		# advanced parameters
		chart_type = request.POST.get('chart_type','candlestick')
		trade_time_given = request.POST.get('trade_time_given',"False")
		if(trade_time_given=="True"):
			trade_time_given = "True"
		else:
			trade_time_given = "False"
		trading_start_time = request.POST.get('trading_start_time','09:00')
		trading_stop_time = request.POST.get('trading_stop_time','23:30')
		daily_strategy_cycle = request.POST.get('daily_strategy_cycle','-')
		tpsl_type = request.POST.get('tpsl_type','pct')
		max_allocation =request.POST.get('max_allocation','')
		position_sizing_type =request.POST.get('position_sizing_type','-')
		#--------------------#
		# print('trading_start_time',trading_start_time)
		curr_time = datetime.datetime.now()
		start_time = datetime.datetime.strftime(curr_time-datetime.timedelta(6*365/6-1),'%d/%m/%Y')
		stop_time = datetime.datetime.strftime(curr_time,'%d/%m/%Y')
		# TODO if algo_uuid != '', run some task to save it, etc
		# try:
		# 	if algo_uuid == '':
		# 		algo_uuid = request.session.pop('algo_uuid','')

		# 	assert algo_uuid != ''
		# except:
		# 	# redirect to dashboard if algo_uuid is none
		# 	pass
		print 'algo_uuid',algo_uuid
		holding_type_temp = 'MIS'
		if(ip_interval=='day'):
			holding_type_temp = 'CNC'

		# load any save preference
		[initial_capital,start_time,stop_time,holding_type,periodicity]=[10000000,start_time,stop_time,holding_type_temp,ip_interval]
		conn = get_redis_connection("default")
		resp = conn.hget('bt_pref',user_uuid+'_'+ip_interval)
		if resp == None:
			[initial_capital,start_time,stop_time,holding_type,periodicity]=[10000000,start_time,stop_time,holding_type_temp,ip_interval]
		elif(len(resp)!=5):
			[initial_capital,start_time,stop_time,holding_type,periodicity]=[10000000,start_time,stop_time,holding_type_temp,ip_interval]
		else:
			resp = resp.split(':')
			[initial_capital,start_time,stop_time,holding_type,periodicity] = resp

		if holding_type!=request.POST.get('holding_type','MIS') and request.POST.get('holding_type','MIS')!='MIS':
			holding_type = request.POST.get('holding_type','MIS')
		# return JsonResponse({'status':'success',
		# 	'initial_capital':initial_capital,
		# 	'dt_start':dt_start,
		# 	'dt_stop':dt_stop,
		# 	'holding_type':holding_type,
		# 	'interval':periodicity
		# 	})holding_type
		return render(request,'multiple_backtests.html',
					{'status':'success',
					'user_uuid':user_uuid,
					'algo_uuid':algo_uuid,
					'algo_name':algo_name,
					'algo_desc':algo_desc,
					'position_type':position_type,
					'position_qty':position_qty,
					'equities':equities,
					'entry_logic':entry_logic,
					'exit_logic':exit_logic,
					'take_profit':take_profit,
					'stop_loss':stop_loss,
					# addition data to populate andn default backtest
					'ip_interval':periodicity,
					'holding_type':holding_type,
					'start_time':start_time,
					'stop_time':stop_time,
					'min_candle_freq':min_candle_freq,
					# advanced fields
					'chart_type':chart_type,
					'trade_time_given':trade_time_given,
					'trading_start_time':trading_start_time,
					'trading_stop_time':trading_stop_time,
					'daily_strategy_cycle':daily_strategy_cycle,
					'tpsl_type': tpsl_type,
					'max_allocation':max_allocation,
					'position_sizing_type':position_sizing_type,
					#----------------#
					'bt_url1':settings.BT_URL1,
					'bt_url2':settings.BT_URL2
					})

	return JsonResponse({'success':'error','error_msg':'Unknown'})

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

def add_pricetrigger(token,trigger): 
	try: 
		conn = get_redis_connection("default") 
		triggers = 'notification_triggers:'+str(token) 
		triggers_list = conn.get(triggers) 
		u = [] 
		if triggers_list is None: 
			u = [str(trigger)] 
		else: 
			u = ujson.loads(triggers_list) 
			u.append(str(trigger)) 
		update_response = conn.set(triggers,ujson.dumps(u)) 
		print('updated redis with new list status',update_response) 
	except: 
		print(traceback.format_exc()) 

def fetch_instruments(seg_sym_list,token=False):
	url = "https://s.streak.tech/instruments/exact_search_ninja/symbols"

	payload = json.dumps({"symbols":  seg_sym_list})
	headers = {
	    'content-type': "application/json",
	    }

	response = requests.request("POST", url, data=payload, headers=headers)
	resp = {}
	try:
		resp = json.loads(response.text)['data']
		if token:
			resp = {r['segment']+'_'+r['symbol']:str(r['lot_size'])+','+str(r['instrument_token']) for r in resp}
		else:
			resp = {r['segment']+'_'+r['symbol']:r['lot_size'] for r in resp}
	except:
		print(seg_sym_list,type(seg_sym_list))
		print(traceback.format_exc())
	return resp

def fetch_instruments_basic(symbol,year,month,instrumentType,token=False):
	url = "https://s.streak.tech/instruments/basic_search"

	payload = json.dumps({"limit":20,"search": symbol + year + month ,"search_fields":["name","symbol","segment"],"return_fields":["segment","symbol","name","from","to","strike","lot_size","instrument_token","expiry"],"include_baskets":False,"instrument_types": [ instrumentType ]})
	headers = {
	    'content-type': "application/json",
	    }

	response = requests.request("POST", url, data=payload, headers=headers)
	resp = {}
	try:
		resp = json.loads(response.text)['data']
		print("resp--->",payload)
		for r in resp:
			return r
		# if token:
		# 	resp = {r['segment']+'_'+r['symbol']:str(r['lot_size'])+','+str(r['instrument_token']) for r in resp}
		# else:
		# 	resp = {r['segment']+'_'+r['symbol']:r['lot_size'] for r in resp}
	except:
		print(symbol,year,month,instrumentType,type(symbol))
		print(traceback.format_exc())
	return resp

def deploy_algorithm_multi_(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return redirect('login')
	if request.method == 'POST':
		algo_uuid = request.POST.get('algo_uuid','')
		seg_sym_list = request.POST.get('seg_sym_list','')
		frequency = request.POST.get('frequency','1')
		live_period = request.POST.get('live_period','1') # this is in days
		deployment_type = request.POST.get('deployment_type','') # this is in days
		broker = request.POST.get('broker','')
		trade_account = request.POST.get('trade_account','')
		take_profit = request.POST.get('take_profit','')
		stop_loss = request.POST.get('stop_loss','')
		quantity = request.POST.get('quantity','')
		periodicity = request.POST.get('interval','hour')
		
		holding_type = request.POST.get('holding_type','')
		algo_live_for = request.POST.get('algo_live_for','1')
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
		
		con = get_redis_connection("default")
		pipeline = con.pipeline()
		default_accounts = con.get('default_trading_accounts'+user_uuid)
		if default_accounts:
			default_accounts = ujson.loads(default_accounts)
		else:
			default_accounts = {}
		exchanges_str = ",".join(default_accounts.keys())
		try:
			seg_sym_list = eval(seg_sym_list.replace('"','\"'))
		except:
			print 'error: seg_sym_list',seg_sym_list
			print traceback.format_exc()
			return JsonResponse({'status':'error'})

		multi_deploy_success = True
		multi_deploy_error_list = []
		seg_sym_dict = fetch_instruments(seg_sym_list)
		print seg_sym_list,len(seg_sym_list),seg_sym_dict
		# assert 1==2
		deployed_len = 0
		st = time.time()
		for seg_sym in seg_sym_list:
			# print seg_sym
			try:
				now = datetime.datetime.now()
				# ex_date = now.replace(day=now.day+int(live_period))
				product = ''
				seg_sym = seg_sym[0]+'_'+seg_sym[1]
				[segment,symbols]=seg_sym.split('_')
				account_name = trade_account
				exchange = segment.lower()
				if segment.lower() in exchanges_str and trade_account=='':
					# only when choosing account based on default account
					for s in default_accounts.keys():
						if segment.lower() in s.lower():
							account_name = default_accounts[s]
							exchange = s
				elif segment.lower() in exchanges_str:
					# only when deciding the exchange when account name is given
					for s in default_accounts.keys():
						if account_name == default_accounts[s]:
							exchange = s
				elif deployment_type=='Auto trading':
					print('No account name given nor any account is present')
					continue
					# if account_name == '':
					# 	continue
				# if holding_type!='' and holding_type!=None:
				# 	if holding_type=='MIS':
				# 		product = 'MIS'
				# 	else:
				# 		if segment == 'NSE':
				# 			product = 'CNC'
				# 		elif ('NFO' in segment):
				# 			product = 'NRML'
				# 		elif ('CDS' in segment):
				# 			product = 'NRML'
				# else:
				# 	if int(live_period) == 1:
				# 		product = 'MIS'
				# 	else:
				# 		if segment == 'NSE':
				# 			product = 'CNC'
				# 		elif ('NFO' in segment):
				# 			product = 'NRML'
				# 		elif ('CDS' in segment):
				# 			product = 'NRML'

				product = 'CNC'
				if product == '':
					return JsonResponse({'status':'error','error':'Unknown product type'})

				ex_date = datetime.datetime.today() + datetime.timedelta(days=int(live_period))
				ex_date = ex_date.replace(hour=0,minute=0,second=0)
				expiration_sec = int(float(ex_date.strftime('%s'))-float(now.strftime('%s')))
				# check if backtest
				bt_result = models.BacktestMeta.objects.get(user_uuid=user_uuid,algo_uuid=algo_uuid,seg_sym=seg_sym)
				if seg_sym in bt_result['backtest_result'].keys():
					# in seg_sym backtested already, then it is deployable
					# deployed algorithm redis entry format =>
					# 'deployed'+':'+user_uuid+':'+algo_uuid+':'+seg_sym+':'+periodicity+':'+deployment_uuid=>{algo as json}
					# add storage time in redis
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

					deployment_uuid = str(uuid.uuid4())

					if '@' in bt_result['algo_obj']['action_str']:
						itoken = con.keys('instruments:*:'+seg_sym.split('_')[1]+':*:'+seg_sym.split('_')[0]+':*')
						if len(itoken)!=1: # missing instrument
							# return JsonResponse({'status':'error'})
							multi_deploy_error_list.append(seg_sym.split('_'))
						itoken = itoken[0].split(':')[1]
						reg = r"@*(\d+\.*\d*)\D*of\D*(\d+\.*\d*)"
						r = re.findall(reg,bt_result['algo_obj']['action_str'])
						[pr,rn]=r[0]					
						# set 123:abcd:PRICETRIGGER:2524673:IR1:68.30:0.1:0.0:algo_name 68.30
						x = [user_uuid,deployment_uuid,'PRICETRIGGER',itoken,'IR1',pr,rn,'0.0',bt_result['algo_obj']['algo_name'],bt_result['algo_obj']['action_type'],bt_result['algo_obj']['quantity'],algo_uuid,product,symbols,segment,deployment_type,exchange,account_name,order_type]
						pipeline.set(':'.join(x),pr)
						add_pricetrigger(itoken,':'.join(x)) 
						pipeline.expire(':'.join(x),expiration_sec)
					
					x = [user_uuid,algo_uuid,seg_sym,periodicity,deployment_uuid]

					keys = con.scan_iter(match='deployed:'+user_uuid+':'+algo_uuid+':'+seg_sym+':'+periodicity+':*')
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
					redis_entry = json.dumps({'user_uuid':user_uuid,
											'algo_uuid':algo_uuid,
											'seg_sym':seg_sym,
											'frequency':frequency,
											'broker':broker,
											'account_name':account_name,
											'exchange':exchange,
											'order_type':order_type,
											'deployment_uuid':deployment_uuid,
											'algo_obj':bt_result['algo_obj'],
											'status':0,
											'expiration_time':ex_date.isoformat()
						})
					pipeline.set(redis_key,redis_entry)
					pipeline.expire(redis_key,expiration_sec)
					# settings.ENV,
					pipeline.publish(settings.ENV+'-deployment_channel','ADD:'+redis_key)
					# store the log in mongo because of longer storage requirements
					deployed_algo = models.DeployedAlgorithm(
						user_uuid=user_uuid,
						algo_uuid=algo_uuid,
						algo_name=bt_result['algo_obj']['algo_name'],
						algo_obj=bt_result['algo_obj'],
						deployment_uuid=deployment_uuid,
						deployment_type=deployment_type,
						account_name=account_name,
						exchange=exchange,
						order_type=order_type,
						broker=broker,
						segment_symbol =  seg_sym,
						symbol =  seg_sym.split('_')[1],
						segment =  seg_sym.split('_')[0],
						deployment_time = datetime.datetime.now(),
						expiration_time = ex_date,
						frequency = frequency,
						live_period = live_period,
						status = 0
						)

					holding_for_algo = models.HoldingsForAlgorithm(user_uuid=user_uuid,
						algo_uuid=algo_uuid,
						algo_name=bt_result['algo_obj']['algo_name'],
						deployment_uuid=deployment_uuid,
						deployment_type=deployment_type,
						algo_reference = deployed_algo,
						symbol =  seg_sym.split('_')[1],
						segment =  seg_sym.split('_')[0],
						exchange = exchange,
						product = product,
						position = {'qty':'0.0','last_order_average_price':'0.0'},
						pnl={'final_pnl':'0.0','returns':'0.0'} # this hodls the realized pnl and realised returns
						)

					order_start_log = models.OrderLog(
						user_uuid=user_uuid,
						algo_uuid=algo_uuid,
						deployment_uuid=deployment_uuid,
						deployment_type=deployment_type,
						log_tag="Waiting",
						log_message="Waiting for first trigger event"
						)

					# fetch_single_backtest_result = """
					# function(){
					# var results = [];
					# results = db[collection].findOne({user_uuid:"%s","algo_uuid":"%s","backtest_result.%s":{$exists:true}},{"backtest_result.%s":1,"algo_obj":1,"algo_uuid":1,"updated_at":1,"_id":0});
					# return results;
					# }"""%(user_uuid,algo_uuid,seg_sym,seg_sym)

					backtest_result = models.BacktestMeta._get_collection().find_one({"user_uuid" : user_uuid,"algo_uuid":algo_uuid,"backtest_result.%s"%seg_sym:{"$exists":True}},{"backtest_result.%s"%seg_sym:1,"algo_obj":1,"algo_uuid":1,"updated_at":1,"_id":0})
					# fetch_single_backtest_result_dict = {user_uuid:"%s","algo_uuid":"%s","backtest_result.%s":{$exists:true}},{"backtest_result.%s":1,"algo_obj":1,"algo_uuid":1,"updated_at":1,"_id":0});
					# return results;
					# }
					# backtest_result = models.BacktestMeta.objects.exec_js(fetch_single_backtest_result)
					# backtest_result = models.Algorithm._get_collection().aggregate(algo_snap_query_dict) 
					if backtest_result==None:
						multi_deploy_error_list.append(seg_sym.split('_'))
						# return JsonResponse({'status':'success','msg':'Missing backtest'})

					# this is the backtest spanpshot for orders log
					order_log_backtest = models.OrderLogBacktest(user_uuid=user_uuid,algo_uuid=algo_uuid,deployment_uuid=deployment_uuid,
						backtest_result=backtest_result['backtest_result'][seg_sym],
						algo_obj=backtest_result['algo_obj']
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
			if deployment_type=='Auto trading':
				return JsonResponse({'status':'error','error_msg':"Exchange account not added for auto trading"})
			return JsonResponse({'status':'error','multi_deploy_error_list':multi_deploy_error_list})

	return JsonResponse({'status':'error'})

def deploy_algorithm_multi(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return redirect('login')
	if request.method == 'POST':
		algo_uuid = request.POST.get('algo_uuid','')
		seg_sym_list = request.POST.get('seg_sym_list','')
		frequency = request.POST.get('frequency','1')
		live_period = request.POST.get('live_period','1') # this is in days
		broker = request.POST.get('broker','zerodha')
		deployment_type = request.POST.get('deployment_type','')
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
		# if frequency=='0' or frequency=='1':
		# 	frequency = str(int(frequency)+1)
		try:
			seg_sym_list = urllib.unquote(unicode(seg_sym_list).encode('utf-8'))
		except:
			pass
		con = get_redis_connection("default")
		pipeline = con.pipeline()
		try:
			seg_sym_list = eval(seg_sym_list.replace('"','\"'))
		except:
			print 'error: seg_sym_list',seg_sym_list
			print traceback.format_exc()
			return JsonResponse({'status':'error'})

		multi_deploy_success = True
		multi_deploy_error_list = []
		seg_sym_dict = fetch_instruments(seg_sym_list)
		print seg_sym_list,len(seg_sym_list),seg_sym_dict
		# assert 1==2
		st = time.time()
		for seg_sym in seg_sym_list:
			# print seg_sym
			try:
				now = datetime.datetime.now()
				# ex_date = now.replace(day=now.day+int(live_period))
				product = ''
				seg_sym = seg_sym[0]+'_'+seg_sym[1]
				[segment,symbols]=seg_sym.split('_')

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
				print seg_sym
				bt_result = models.BacktestMeta.objects.get(user_uuid=user_uuid,algo_uuid=algo_uuid,seg_sym=seg_sym)
				if seg_sym in bt_result['backtest_result'].keys():
					# in seg_sym backtested already, then it is deployable
					# deployed algorithm redis entry format =>
					# 'deployed'+':'+user_uuid+':'+algo_uuid+':'+seg_sym+':'+periodicity+':'+deployment_uuid=>{algo as json}
					# add storage time in redis
					if quantity!='' and quantity!=0:
						bt_result['algo_obj']['quantity'] = str(int(float(quantity))*int(max(seg_sym_dict.get(seg_sym,1),1)))
					if periodicity!='':
						bt_result['algo_obj']['time_frame'] = periodicity
					if take_profit!='':
						bt_result['algo_obj']['take_profit'] = take_profit
					if stop_loss!='':
						bt_result['algo_obj']['stop_loss'] = stop_loss

					if bt_result['algo_obj'].get('scripList',None) is not None:
						bt_result['algo_obj']['scripList']=[]
					
					bt_result['algo_obj']['deployment_time'] = datetime.datetime.now().isoformat()
					bt_result['algo_obj']['deployment_type'] = deployment_type
					bt_result['algo_obj']['product'] = product
					bt_result['algo_obj']['variety'] = variety
					bt_result['algo_obj']['sound_name'] = sound_name 
					bt_result['algo_obj']['algo_live_for'] = algo_live_for

					deployment_uuid = str(uuid.uuid4())

					if '@' in bt_result['algo_obj']['action_str']:
						itoken = con.keys('instruments:*:'+seg_sym.split('_')[1]+':*:'+seg_sym.split('_')[0]+':*')
						if len(itoken)!=1: # missing instrument
							# return JsonResponse({'status':'error'})
							multi_deploy_error_list.append(seg_sym.split('_'))
						itoken = itoken[0].split(':')[1]
						reg = r"@*(\d+\.*\d*)\D*of\D*(\d+\.*\d*)"
						r = re.findall(reg,bt_result['algo_obj']['action_str'])
						[pr,rn]=r[0]					
						# set 123:abcd:PRICETRIGGER:2524673:IR1:68.30:0.1:0.0:algo_name 68.30
						x = [user_uuid,deployment_uuid,'PRICETRIGGER',itoken,'IR1',pr,rn,'0.0',bt_result['algo_obj']['algo_name'],bt_result['algo_obj']['action_type'],str(bt_result['algo_obj']['quantity']),algo_uuid,product,symbols,segment,variety,bt_result['algo_obj']['take_profit'],bt_result['algo_obj']['stop_loss'],bt_result['algo_obj'].get('tpsl_type','pct'),deployment_type,periodicity]
						pipeline.set(':'.join(x),pr)
						add_pricetrigger(itoken,':'.join(x)) 
						pipeline.expire(':'.join(x),expiration_sec)
						bt_result['algo_obj']['lua_val'] = ':'.join(x)
					x = [user_uuid,algo_uuid,seg_sym,periodicity,deployment_uuid]

					# keys = con.keys('deployed:'+user_uuid+':'+algo_uuid+':'+seg_sym+':'+periodicity+':*')
					keys = get_deployment_keys({"user_uuid":user_uuid,"algo_uuid":algo_uuid,"segment_symbol":seg_sym,"algo_obj.time_frame":periodicity,"status":0,"expiration_time":{"$gte":datetime.datetime.now()}}) 
					# keys = models.DeployedAlgorithm._get_collection().find({"user_uuid":user_uuid,"algo_uuid":algo_uuid,"seg_sym":seg_sym,"algo_obj.time_frame":periodicity,"status":0})

					if len(keys)>0:
						redis_key = keys[0]
					else:
						redis_key = 'deployed:'+':'.join(x)
					# +user_uuid+':'+algo_uuid+':'+seg_sym+':'+periodicity+':'+deployment_uuid
					redis_entry = json.dumps({'user_uuid':user_uuid,
											'algo_uuid':algo_uuid,
											'seg_sym':seg_sym,
											'frequency':frequency,
											'broker':broker,
											'deployment_uuid':deployment_uuid,
											'algo_obj':bt_result['algo_obj'],
											'status':0,
											'expiration_time':ex_date.isoformat(),
											'algo_live_for':algo_live_for,
											'order_type':order_type,
											'variety':variety
						})
					pipeline.set(redis_key,redis_entry)
					pipeline.expire(redis_key,expiration_sec)
					# settings.ENV,
					pipeline.publish(settings.ENV+'-deployment_channel','ADD:'+redis_key)
					# store the log in mongo because of longer storage requirements
					deployed_algo = models.DeployedAlgorithm(
						user_uuid=user_uuid,
						algo_uuid=algo_uuid,
						algo_name=bt_result['algo_obj']['algo_name'],
						algo_obj=bt_result['algo_obj'],
						deployment_uuid=deployment_uuid,
						deployment_type = deployment_type,
						segment_symbol =  seg_sym,
						order_type = order_type,
						symbol =  seg_sym.split('_')[1],
						segment =  seg_sym.split('_')[0],
						deployment_time = datetime.datetime.now(),
						expiration_time = ex_date,
						frequency = frequency,
						live_period = live_period,
						status = 0
						)

					holding_for_algo = models.HoldingsForAlgorithm(user_uuid=user_uuid,
						algo_uuid=algo_uuid,
						algo_name=bt_result['algo_obj']['algo_name'],
						deployment_uuid=deployment_uuid,
						deployment_type = deployment_type,
						algo_reference = deployed_algo,
						symbol =  seg_sym.split('_')[1],
						segment =  seg_sym.split('_')[0],
						product = product,
						position = {'qty':0,'last_order_average_price':0.0},
						pnl={'final_pnl':0,'returns':0.0} # this hodls the realized pnl and realised returns
						)

					order_start_log = models.OrderLog(
						user_uuid=user_uuid,
						algo_uuid=algo_uuid,
						deployment_uuid=deployment_uuid,
						deployment_type = deployment_type,
						log_tag="Waiting",
						log_message="Waiting for first trigger event"
						)

					fetch_single_backtest_result = """
					function(){
					var results = [];
					results = db[collection].findOne({user_uuid:"%s","algo_uuid":"%s","backtest_result.%s":{$exists:true}},{"backtest_result.%s":1,"algo_obj":1,"algo_uuid":1,"updated_at":1,"_id":0});
					return results;
					}"""%(user_uuid,algo_uuid,seg_sym,seg_sym)

					# fetch_single_backtest_result_dict = {user_uuid:"%s","algo_uuid":"%s","backtest_result.%s":{$exists:true}},{"backtest_result.%s":1,"algo_obj":1,"algo_uuid":1,"updated_at":1,"_id":0});
					# return results;
					# }
					backtest_result = models.BacktestMeta.objects.exec_js(fetch_single_backtest_result)
					# backtest_result = models.Algorithm._get_collection().aggregate(algo_snap_query_dict) 
					if backtest_result==None:
						multi_deploy_error_list.append(seg_sym.split('_'))
						# return JsonResponse({'status':'success','msg':'Missing backtest'})

					# this is the backtest spanpshot for orders log
					order_log_backtest = models.OrderLogBacktest(user_uuid=user_uuid,algo_uuid=algo_uuid,deployment_uuid=deployment_uuid,
						backtest_result=backtest_result['backtest_result'][seg_sym],
						algo_obj=backtest_result['algo_obj']
						)

					# st2 = time.time()
					deployed_algo.save()
					holding_for_algo.save()
					order_start_log.save()
					order_log_backtest.save()
					pipeline.execute()
					update_usage_util(user_uuid,'deployed')
					# print(time.time()-st2)
			except:
				print traceback.format_exc()
				# return JsonResponse({'status':'error'})
				multi_deploy_success = False

		print(time.time()-st)
		if(multi_deploy_success):
			return JsonResponse({'status':'success'})
		else:
			return JsonResponse({'status':'error','multi_deploy_error_list':multi_deploy_error_list})

	return JsonResponse({'status':'error'})

def redeploy_algorithm(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return redirect('login')
	if request.method == 'POST':
		# print request.POST,request.META.items()
		deployment_uuid = request.POST.get('deployment_uuid','')
		seg_sym = request.POST.get('seg_sym','')
		print seg_sym
		frequency = request.POST.get('frequency','1')
		live_period = request.POST.get('live_period','1') # this is in days
		deployment_type = request.POST.get('deployment_type','') # paper or notification

		broker = request.POST.get('broker','zerodha')
		trade_account = request.POST.get('trade_account','')
		take_profit = request.POST.get('take_profit','')
		stop_loss = request.POST.get('stop_loss','')
		quantity = request.POST.get('quantity','')
		periodicity = request.POST.get('interval','hour')
		variety = request.POST.get('variety','REGULAR')
		sound_name = request.POST.get('sound_name','default')

		holding_type = request.POST.get('holding_type','')
		algo_live_for = request.POST.get('algo_live_for','1')
		order_type = request.POST.get('order_type','MARKET')
		max_allocation = request.POST.get('max_allocation','')
		position_sizing_type = request.POST.get('position_sizing_type','-')
		limit_buffer = request.POST.get('buffer','0')
		default_price = request.POST.get('default_price','close').lower()
		success_flag = True
		# if frequency=='0':
		# 	frequency = str(int(frequency)+1)
		try:
			con = get_redis_connection("default")
			pipeline = con.pipeline()
			default_accounts = con.get('default_trading_accounts'+user_uuid)
			if default_accounts:
				default_accounts = ujson.loads(default_accounts)
			else:
				default_accounts = {}
			exchanges_str = ",".join(default_accounts.keys())
			now = datetime.datetime.now()
			deployed_obj = models.DeployedAlgorithm.objects.get(user_uuid=user_uuid,deployment_uuid=deployment_uuid)
			# ex_date = now.replace(day=now.day+int(live_period))
			product = ''
			print seg_sym,len(seg_sym.split('_')),deployed_obj.symbol
			quantity_update = False
			dynamic_flag = False
			dynamic_contract = ''
			if "dynamic contract".upper() in deployed_obj.symbol:
				seg_sym = deployed_obj.segment.upper()+"_"+deployed_obj.symbol.upper()
				matches = dynamic_sym_params_generator(seg_sym)
				if len(matches)==0:
					print "algo_uuid",deployment_uuid,seg_sym
					return JsonResponse({ "status": "error", "error_msg": "contract not found" })
					# return JsonResponse({'status':'error'})
					multi_deploy_success = False
				else:
					m = matches[0].split(",")
					dynamic_contract = seg_sym
					# seg_sym = m[0]
					dynamic_flag = True
					[segment,symbols]=["",dynamic_contract[1:]]
					basicSearchSym = m[0].split("_")[-1]
					basicSearchSeg = m[0].split("_")[0]
					# print 'm[6]',m[6]
					if m[6].strip()=='SHORT':
						dynamic_action_type = "SELL"
					if basicSearchSeg == "INDICES" :
						if basicSearchSym == "NIFTY 50" :
							basicSearchSym = "NIFTY"
						elif basicSearchSym == "NIFTY BANK" :
							basicSearchSym = "BANKNIFTY"	
					# finalSeg = "NFO-OPT"
					# if segment != "NSE" && segment != "INDICES" && segment == "CDS" :
						# finalSeg = "CDS-OPT"
					seg_sym = m[0]
					seg_sym_bt = dynamic_contract
					month = datetime.datetime.now().strftime('%B').upper()[:3]
					year = str(datetime.datetime.now().year%100)
					# if m[0] not in seg_sym_dict.keys():
					# 	dynamic_seg_sym_obj = fetch_instruments_basic(basicSearchSym,year,month,m[1].strip())
					# 	# if dynamic_seg_sym_obj!={}
					# 	seg_sym_dict[m[0]]=str(dynamic_seg_sym_obj.get('lot_size',1))+','+str(dynamic_seg_sym_obj.get('instrument_token',0))
					# 	print("seg_sym_dict",seg_sym_dict,seg_sym)
			else:
				[segment,symbols]=seg_sym.split('_')
			account_name = trade_account
			exchange = segment.lower()
			if segment.lower() in exchanges_str and trade_account=='':
				# only when choosing account based on default account
				for s in default_accounts.keys():
					if segment.lower() in s.lower():
						account_name = default_accounts[s]
						exchange = s
			elif segment.lower() in exchanges_str:
				# only when deciding the exchange when account name is given
				for s in default_accounts.keys():
					if account_name == default_accounts[s]:
						exchange = s
			elif deployment_type=='Auto trading':
				print('No account name given nor any account is present')
				return JsonResponse({'status':'error','error_msg':'No account name given, and not default account is present'})

			# if int(live_period) == 1:
			# 	product = 'MIS'
			# else:
			# 	if segment == 'NSE':
			# 		product = 'CNC'
			# 	elif ('NFO' in segment):
			# 		product = 'NRML'
			# 	elif ('CDS' in segment):
			# 		product = 'NRML'
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
						elif dynamic_flag:
							product = 'NRML'
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
					elif dynamic_flag:
						product = 'NRML'

			if ('MCX' in segment):
				variety = 'REGULAR'

			if product == '':
				return JsonResponse({'status':'error','error':'Unknown product type'})

			ex_date = datetime.datetime.today() + datetime.timedelta(days=int(live_period))
			ex_date = ex_date.replace(hour=0,minute=0,second=0)
			expiration_sec = int(float(ex_date.strftime('%s'))-float(now.strftime('%s')))
			# check if backtest
			algo_obj = deployed_obj.algo_obj
			algo_uuid = algo_obj.get('algo_uuid','')
			alog_obj_bak = algo_obj
			if max_allocation!="" and algo_uuid!="":
				seg_sym_bt = seg_sym
				if dynamic_flag and dynamic_contract!='':
					bt_result = models.BacktestMeta.objects.get(user_uuid=user_uuid,algo_uuid=algo_uuid,seg_sym=dynamic_contract)
					seg_sym_bt = dynamic_contract
				else:
					bt_result = models.BacktestMeta.objects.get(user_uuid=user_uuid,algo_uuid=algo_uuid,seg_sym=seg_sym)
				if seg_sym_bt in bt_result['backtest_result'].keys():
					# print("dynamic contract ----------------->",seg_sym_bt)
					bt_result['algo_obj']["max_allocation"] = max_allocation
					bt_result['algo_obj']["position_sizing_type"] = position_sizing_type
					alog_obj_bak = bt_result['algo_obj']
					mxq = algo_obj.pop('max_allocation_qty','')
					if mxq!='':
						alog_obj_bak['quantity']=mxq
						quantity_update = True
					algo_obj = alog_obj_bak
			print algo_obj
			if not algo_obj:
				return JsonResponse({'status':'error','error':'Strategy object missing'})
			
			if seg_sym != '' and algo_uuid!='':
				# in seg_sym backtested already, then it is deployable
				# deployed algorithm redis entry format =>
				# 'deployed'+':'+user_uuid+':'+algo_uuid+':'+seg_sym+':'+periodicity+':'+deployment_uuid=>{algo as json}
				# add storage time in redis
				if quantity!='' and quantity!=0 and not quantity_update:
					algo_obj['quantity'] = quantity
				if periodicity!='':
					algo_obj['time_frame'] = periodicity
				if take_profit!='':
					algo_obj['take_profit'] = take_profit
				if stop_loss!='':
					algo_obj['stop_loss'] = stop_loss
				
				algo_obj['deployment_time'] = datetime.datetime.now().isoformat()
				algo_obj['deployment_type'] = deployment_type
				algo_obj['product'] = product
				algo_obj['variety'] = variety

				algo_obj['sound_name'] = sound_name
				algo_obj['algo_live_for'] = algo_live_for

				algo_obj['buffer'] = limit_buffer
				algo_obj['default_price'] = default_price
				algo_obj['order_type'] = order_type
				if algo_obj['order_type']=="MIS":
					algo_obj['order_type'] = "MARKET"
				# if dynamic_flag:
					# print "here",dynamic_action_type
					# algo_obj['action_type'] = dynamic_action_type
					# algo_obj['position_type'] = dynamic_action_type

				deployment_uuid = str(uuid.uuid4())

				if '@' in algo_obj['action_str']:
					itoken = con.keys('instruments:*:'+seg_sym.split('_')[1]+':*:'+seg_sym.split('_')[0]+':*')
					if len(itoken)!=1: # missing instrument
						return JsonResponse({'status':'error'})
					itoken = itoken[0].split(':')[1]
					reg = r"@*(\d+\.*\d*)\D*of\D*(\d+\.*\d*)"
					r = re.findall(reg,algo_obj['action_str'])
					[pr,rn]=r[0]					
					# set 123:abcd:PRICETRIGGER:2524673:IR1:68.30:0.1:0.0:algo_name 68.30
					x = [user_uuid,deployment_uuid,'PRICETRIGGER',itoken,'IR1',pr,rn,'0.0',algo_obj['algo_name'],algo_obj['action_type'],str(algo_obj['quantity']),algo_uuid,product,symbols,segment,variety,algo_obj['take_profit'],algo_obj['stop_loss'],algo_obj.get('tpsl_type','pct'),deployment_type,periodicity]
					pipeline.set(':'.join(x),pr)
					add_pricetrigger(itoken,':'.join(x)) 
					pipeline.expire(':'.join(x),expiration_sec)
					algo_obj['lua_val'] = ':'.join(x)
				
				x = [user_uuid,algo_uuid,seg_sym,periodicity,deployment_uuid]

				# keys = con.keys('deployed:'+user_uuid+':'+algo_uuid+':'+seg_sym+':'+periodicity+':*')
				keys = get_deployment_keys({"user_uuid":user_uuid,"algo_uuid":algo_uuid,"segment_symbol":seg_sym,"algo_obj.time_frame":periodicity,"status":0,"expiration_time":{"$gte":datetime.datetime.now()}})
				if len(keys)>0 and not dynamic_flag :
					return JsonResponse({ "status": "error", "error_msg": "Strategy for this scrip is already live" })
				else:
					redis_key = 'deployed:'+':'.join(x)
				# +user_uuid+':'+algo_uuid+':'+seg_sym+':'+periodicity+':'+deployment_uuid
				redis_entry = json.dumps({'user_uuid':user_uuid,
										'algo_uuid':algo_uuid,
										'seg_sym':seg_sym,
										'frequency':frequency,
										'broker':request.session.get("broker",broker),
										'account_name':account_name,
										'exchange':exchange,
										'order_type':order_type,
										'deployment_uuid':deployment_uuid,
										'algo_obj':algo_obj,
										'status':0,
										'expiration_time':ex_date.isoformat(),
										'algo_live_for':algo_live_for,
										'variety':variety,
										'email':request.session.get('user_email',''),
										# dynamic contract payload
										'dynamic_flag':dynamic_flag,
										'dynamic_contract':dynamic_contract
					})
				pipeline.set(redis_key,redis_entry)
				pipeline.expire(redis_key,expiration_sec)
				# settings.ENV,
				print(redis_key)
				pipeline.publish(settings.ENV+'-deployment_channel','ADD:'+redis_key)
				# store the log in mongo because of longer storage requirements
				deployed_algo = models.DeployedAlgorithm(
					user_uuid=user_uuid,
					algo_uuid=algo_uuid,
					algo_name=deployed_obj['algo_name'],
					algo_obj=algo_obj,
					deployment_uuid=deployment_uuid,
					deployment_type=deployment_type,
					account_name=account_name,
					exchange=exchange,
					order_type=order_type,
					broker=broker,
					segment_symbol =  deployed_obj['segment_symbol'],
					symbol =  deployed_obj['symbol'],#seg_sym.split('_')[1],
					segment =  deployed_obj['segment'],#seg_sym.split('_')[0],
					deployment_time = datetime.datetime.now(),
					expiration_time = ex_date,
					frequency = frequency,
					live_period = live_period,
					status = 0
					)

				holding_for_algo = models.HoldingsForAlgorithm(user_uuid=user_uuid,
					algo_uuid=algo_uuid,
					algo_name=deployed_obj['algo_name'],
					deployment_uuid=deployment_uuid,
					deployment_type=deployment_type,
					algo_reference = deployed_algo,
					symbol =  deployed_obj['symbol'],#seg_sym.split('_')[1],
					segment =  deployed_obj['segment'],#seg_sym.split('_')[0],
					exchange=exchange,
					product = product,
					position = {'qty':0,'last_order_average_price':0.0},
					pnl={'final_pnl':0.0,'returns':0.0} # this hodls the realized pnl and realised returns
					)

				order_start_log = models.OrderLog(
					user_uuid=user_uuid,
					algo_uuid=algo_uuid,
					deployment_uuid=deployment_uuid,
					deployment_type=deployment_type,
					log_tag="Waiting",
					log_message="Waiting for first trigger event"
					)

				# fetch_single_backtest_result = """
				# function(){
				# var results = [];
				# results = db[collection].findOne({user_uuid:"%s","algo_uuid":"%s","backtest_result.%s":{$exists:true}},{"backtest_result.%s":1,"algo_obj":1,"algo_uuid":1,"updated_at":1,"_id":0});
				# return results;
				# }"""%(user_uuid,algo_uuid,seg_sym,seg_sym)

				# backtest_result = models.BacktestMeta.objects.exec_js(fetch_single_backtest_result)

				# if backtest_result==None:
					# return JsonResponse({'status':'success','msg':'Missing backtest'})

				# this is the backtest spanpshot for orders log
				# order_log_backtest = models.OrderLogBacktest(user_uuid=user_uuid,algo_uuid=algo_uuid,deployment_uuid=deployment_uuid,
				# 	backtest_result=backtest_result['backtest_result'][seg_sym],
				# 	algo_obj=algo_obj
				# 	)

				deployed_algo.save()
				holding_for_algo.save()
				order_start_log.save()
				# order_log_backtest.save()
				pipeline.execute()
				update_usage_util(user_uuid,'deployed')
		except:
			print traceback.format_exc()
			success_flag = False

		if success_flag:
			return JsonResponse({'status':'success'})
		else:
			return JsonResponse({'status':'error'})

	return JsonResponse({'status':'error'})

def redeploy_algorithm_internal(request):
	# user_uuid = request.session.get('user_uuid','')
	# user_is_auth = request.session.get('user_is_auth',False)
	# # if settings.DEBUG:
	# if settings.ENV == "local" or settings.ENV == 'local1':
	# 	user_uuid = '123'
	# 	user_is_auth = True
	# if not user_is_auth:
	# 	return redirect('login')
	if request.method == 'POST':
		# print request.POST,request.META.items()
		user_uuid = request.POST.get('user_uuid','')
		deployment_uuid = request.POST.get('deployment_uuid','')
		seg_sym = request.POST.get('seg_sym','')
		print seg_sym
		frequency = request.POST.get('frequency','1')
		live_period = request.POST.get('live_period','1') # this is in days
		deployment_type = request.POST.get('deployment_type','') # paper or notification

		broker = request.POST.get('broker','zerodha')
		trade_account = request.POST.get('trade_account','')
		take_profit = request.POST.get('take_profit','')
		stop_loss = request.POST.get('stop_loss','')
		quantity = request.POST.get('quantity','')
		periodicity = request.POST.get('interval','hour')
		variety = request.POST.get('variety','REGULAR')
		sound_name = request.POST.get('sound_name','default')

		holding_type = request.POST.get('holding_type','')
		algo_live_for = request.POST.get('algo_live_for','1')
		order_type = request.POST.get('order_type','MARKET')

		parent_uuid = request.POST.get('parent_uuid','')

		validate_token = request.POST.get('validate_token','')

		success_flag = True
		# if frequency=='0' or frequency=='1':
		# 	frequency = str(int(frequency)+1)
		try:
			con = get_redis_connection("default")

	  		verification = con.get("application_access_token_cred") 
	  		if verification!=validate_token:
	  			return JsonResponse({'status':'error','error_msg':"Invalid authentication"})

			pipeline = con.pipeline()
			default_accounts = con.get('default_trading_accounts'+user_uuid)
			if default_accounts:
				default_accounts = ujson.loads(default_accounts)
			else:
				default_accounts = {}
			exchanges_str = ",".join(default_accounts.keys())
			now = datetime.datetime.now()
			# ex_date = now.replace(day=now.day+int(live_period))
			deployed_obj = models.DeployedAlgorithm.objects.get(user_uuid=user_uuid,deployment_uuid=deployment_uuid)
			product = ''
			print seg_sym
			dynamic_flag = False
			dynamic_contract = ''
			if "dynamic contract".upper() in deployed_obj.symbol:
				seg_sym = deployed_obj.segment.upper()+"_"+deployed_obj.symbol.upper()
				matches = dynamic_sym_params_generator(seg_sym)
				if len(matches)==0:
					print "algo_uuid",deployment_uuid,seg_sym
					return JsonResponse({ "status": "error", "error_msg": "contract not found" })
					# return JsonResponse({'status':'error'})
					multi_deploy_success = False
				else:
					m = matches[0].split(",")
					dynamic_contract = seg_sym
					# seg_sym = m[0]
					dynamic_flag = True
					[segment,symbols]=["",dynamic_contract[1:]]
					basicSearchSym = m[0].split("_")[-1]
					basicSearchSeg = m[0].split("_")[0]
					# print 'm[6]',m[6]
					if m[6].strip()=='SHORT':
						dynamic_action_type = "SELL"
					if basicSearchSeg == "INDICES" :
						if basicSearchSym == "NIFTY 50" :
							basicSearchSym = "NIFTY"
						elif basicSearchSym == "NIFTY BANK" :
							basicSearchSym = "BANKNIFTY"	
					# finalSeg = "NFO-OPT"
					# if segment != "NSE" && segment != "INDICES" && segment == "CDS" :
						# finalSeg = "CDS-OPT"
					seg_sym = m[0]
					seg_sym_bt = dynamic_contract
					month = datetime.datetime.now().strftime('%B').upper()[:3]
					year = str(datetime.datetime.now().year%100)
					# if m[0] not in seg_sym_dict.keys():
					# 	dynamic_seg_sym_obj = fetch_instruments_basic(basicSearchSym,year,month,m[1].strip())
					# 	# if dynamic_seg_sym_obj!={}
					# 	seg_sym_dict[m[0]]=str(dynamic_seg_sym_obj.get('lot_size',1))+','+str(dynamic_seg_sym_obj.get('instrument_token',0))
					# 	print("seg_sym_dict",seg_sym_dict,seg_sym)
			else:
				[segment,symbols]=seg_sym.split('_')
			account_name = trade_account
			exchange = segment.lower()
			if segment.lower() in exchanges_str and trade_account=='':
				# only when choosing account based on default account
				for s in default_accounts.keys():
					if segment.lower() in s.lower():
						account_name = default_accounts[s]
						exchange = s
			elif segment.lower() in exchanges_str:
				# only when deciding the exchange when account name is given
				for s in default_accounts.keys():
					if account_name == default_accounts[s]:
						exchange = s
			elif deployment_type=='Auto trading':
				print('No account name given nor any account is present')
				return JsonResponse({'status':'error','error_msg':'No account name given, and not default account is present'})

			# if int(live_period) == 1:
			# 	product = 'MIS'
			# else:
			# 	if segment == 'NSE':
			# 		product = 'CNC'
			# 	elif ('NFO' in segment):
			# 		product = 'NRML'
			# 	elif ('CDS' in segment):
			# 		product = 'NRML'
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
						elif dynamic_flag:
							product = 'NRML'
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
					elif dynamic_flag:
						product = 'NRML'

			if ('MCX' in segment):
				variety = 'REGULAR'

			if product == '':
				return JsonResponse({'status':'error','error':'Unknown product type'})

			ex_date = datetime.datetime.today() + datetime.timedelta(days=int(live_period))
			ex_date = ex_date.replace(hour=0,minute=0,second=0)
			expiration_sec = int(float(ex_date.strftime('%s'))-float(now.strftime('%s')))
			# check if backtest
			algo_obj = deployed_obj.algo_obj
			# print algo_obj
			order_type = algo_obj.get('order_type','MARKET')
			if order_type=="MIS":
				order_type="MARKET"
			if not algo_obj:
				return JsonResponse({'status':'error','error':'Strategy object missing'})
			algo_uuid = algo_obj.get('algo_uuid','')
			quantity_update = False
			if algo_obj.get("max_allocation","")!="" and algo_uuid!="":
				max_allocation = algo_obj.get("max_allocation","")
				position_sizing_type = algo_obj.get("position_sizing_type","")
				seg_sym_bt = seg_sym
				if dynamic_flag and dynamic_contract!='':
					bt_result = models.BacktestMeta.objects.get(user_uuid=user_uuid,algo_uuid=algo_uuid,seg_sym=dynamic_contract)
					seg_sym_bt = dynamic_contract
				else:
					bt_result = models.BacktestMeta.objects.get(user_uuid=user_uuid,algo_uuid=algo_uuid,seg_sym=seg_sym)
				if seg_sym_bt in bt_result['backtest_result'].keys():
					# print("dynamic contract ----------------->",seg_sym_bt)
					bt_result['algo_obj']["max_allocation"] = max_allocation
					bt_result['algo_obj']["position_sizing_type"] = position_sizing_type
					alog_obj_bak = bt_result['algo_obj']
					mxq = algo_obj.pop('max_allocation_qty','')
					if mxq!='':
						alog_obj_bak['quantity']=mxq
						quantity_update = True
					alog_obj_bak['buffer'] = algo_obj.get('buffer','')
					alog_obj_bak['default_price'] = algo_obj.get('default_price','')
					alog_obj_bak['order_type'] = algo_obj.get('order_type','')
					order_type = algo_obj.get('order_type','')
					if alog_obj_bak['order_type'] == "MIS":
						alog_obj_bak['order_type'] = "MARKET"
						order_type = "MARKET"
					order_type = alog_obj_bak['order_type']
					algo_obj = alog_obj_bak
			if seg_sym != '' and algo_uuid!='':
				# in seg_sym backtested already, then it is deployable
				# deployed algorithm redis entry format =>
				# 'deployed'+':'+user_uuid+':'+algo_uuid+':'+seg_sym+':'+periodicity+':'+deployment_uuid=>{algo as json}
				# add storage time in redis
				if quantity!='' and quantity!=0 and not quantity_update:
					algo_obj['quantity'] = quantity
				if periodicity!='':
					algo_obj['time_frame'] = periodicity
				if take_profit!='':
					algo_obj['take_profit'] = take_profit
				if stop_loss!='':
					algo_obj['stop_loss'] = stop_loss
				
				algo_obj['deployment_time'] = datetime.datetime.now().isoformat()
				algo_obj['deployment_type'] = deployment_type
				algo_obj['product'] = product
				algo_obj['variety'] = variety

				algo_obj['sound_name'] = sound_name
				algo_obj['algo_live_for'] = algo_live_for
				algo_obj['parent_uuid'] = parent_uuid

				if algo_obj.get('user_uuid','')!=user_uuid:
					algo_obj['user_uuid']=user_uuid

				deployment_uuid = str(uuid.uuid4())

				if '@' in algo_obj['action_str']:
					itoken = con.keys('instruments:*:'+seg_sym.split('_')[1]+':*:'+seg_sym.split('_')[0]+':*')
					if len(itoken)!=1: # missing instrument
						return JsonResponse({'status':'error'})
					itoken = itoken[0].split(':')[1]
					reg = r"@*(\d+\.*\d*)\D*of\D*(\d+\.*\d*)"
					r = re.findall(reg,algo_obj['action_str'])
					[pr,rn]=r[0]					
					# set 123:abcd:PRICETRIGGER:2524673:IR1:68.30:0.1:0.0:algo_name 68.30
					x = [user_uuid,deployment_uuid,'PRICETRIGGER',itoken,'IR1',pr,rn,'0.0',algo_obj['algo_name'],algo_obj['action_type'],str(algo_obj['quantity']),algo_uuid,product,symbols,segment,variety,algo_obj['take_profit'],algo_obj['stop_loss'],algo_obj.get('tpsl_type','pct'),deployment_type,periodicity]
					pipeline.set(':'.join(x),pr)
					add_pricetrigger(itoken,':'.join(x)) 
					pipeline.expire(':'.join(x),expiration_sec)
					algo_obj['lua_val'] = ':'.join(x)
				
				x = [user_uuid,algo_uuid,seg_sym,periodicity,deployment_uuid]

				# keys = con.keys('deployed:'+user_uuid+':'+algo_uuid+':'+seg_sym+':'+periodicity+':*')
				keys = get_deployment_keys({"user_uuid":user_uuid,"algo_uuid":algo_uuid,"segment_symbol":seg_sym,"algo_obj.time_frame":periodicity,"status":0,"expiration_time":{"$gte":datetime.datetime.now()}})
				if len(keys)>0 and not dynamic_flag:
					return JsonResponse({ "status": "error", "error_msg": "Algo for this scrip is already live" })
				else:
					redis_key = 'deployed:'+':'.join(x)
				# +user_uuid+':'+algo_uuid+':'+seg_sym+':'+periodicity+':'+deployment_uuid
				redis_entry = json.dumps({'user_uuid':user_uuid,
										'algo_uuid':algo_uuid,
										'seg_sym':seg_sym,
										'frequency':frequency,
										'broker':broker,
										'account_name':account_name,
										'exchange':exchange,
										'order_type':order_type,
										'deployment_uuid':deployment_uuid,
										'algo_obj':algo_obj,
										'status':0,
										'expiration_time':ex_date.isoformat(),
										'algo_live_for':algo_live_for,
										'variety':variety,
										# dynamic contract payload
										'dynamic_flag':dynamic_flag,
										'dynamic_contract':dynamic_contract
					})
				pipeline.set(redis_key,redis_entry)
				pipeline.expire(redis_key,expiration_sec)
				# settings.ENV,
				pipeline.publish(settings.ENV+'-deployment_channel','ADD:'+redis_key)
				# store the log in mongo because of longer storage requirements
				deployed_algo = models.DeployedAlgorithm(
					user_uuid=user_uuid,
					algo_uuid=algo_uuid,
					algo_name=deployed_obj['algo_name'],
					algo_obj=algo_obj,
					deployment_uuid=deployment_uuid,
					deployment_type=deployment_type,
					account_name=account_name,
					exchange=exchange,
					order_type=order_type,
					broker=broker,
					segment_symbol =  deployed_obj['segment_symbol'],
					symbol = deployed_obj['symbol'],#seg_sym.split('_')[1],
					segment = deployed_obj['segment'],#seg_sym.split('_')[0],
					deployment_time = datetime.datetime.now(),
					expiration_time = ex_date,
					frequency = frequency,
					live_period = live_period,
					status = 0
					)

				holding_for_algo = models.HoldingsForAlgorithm(user_uuid=user_uuid,
					algo_uuid=algo_uuid,
					algo_name=deployed_obj['algo_name'],
					deployment_uuid=deployment_uuid,
					deployment_type=deployment_type,
					algo_reference = deployed_algo,
					symbol = deployed_obj['symbol'],#seg_sym.split('_')[0],
					segment =  deployed_obj['segment'],#seg_sym.split('_')[0],
					exchange=exchange,
					product = product,
					position = {'qty':0,'last_order_average_price':0.0},
					pnl={'final_pnl':0.0,'returns':0.0} # this hodls the realized pnl and realised returns
					)

				order_start_log = models.OrderLog(
					user_uuid=user_uuid,
					algo_uuid=algo_uuid,
					deployment_uuid=deployment_uuid,
					deployment_type=deployment_type,
					log_tag="Waiting",
					log_message="Waiting for first trigger event"
					)

				# fetch_single_backtest_result = """
				# function(){
				# var results = [];
				# results = db[collection].findOne({user_uuid:"%s","algo_uuid":"%s","backtest_result.%s":{$exists:true}},{"backtest_result.%s":1,"algo_obj":1,"algo_uuid":1,"updated_at":1,"_id":0});
				# return results;
				# }"""%(user_uuid,algo_uuid,seg_sym,seg_sym)

				# backtest_result = models.BacktestMeta.objects.exec_js(fetch_single_backtest_result)

				# if backtest_result==None:
					# return JsonResponse({'status':'success','msg':'Missing backtest'})

				# this is the backtest spanpshot for orders log
				# order_log_backtest = models.OrderLogBacktest(user_uuid=user_uuid,algo_uuid=algo_uuid,deployment_uuid=deployment_uuid,
				# 	backtest_result=backtest_result['backtest_result'][seg_sym],
				# 	algo_obj=algo_obj
				# 	)

				deployed_algo.save()
				holding_for_algo.save()
				order_start_log.save()
				# order_log_backtest.save()
				pipeline.execute()
				update_usage_util(user_uuid,'deployed')
		except:
			print traceback.format_exc()
			success_flag = False

		if success_flag:
			return JsonResponse({'status':'success'})
		else:
			return JsonResponse({'status':'error'})

	return JsonResponse({'status':'error'})

def deploy_algorithm(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return redirect('login')
	if request.method == 'POST':
		algo_uuid = request.POST.get('algo_uuid','')
		seg_sym = request.POST.get('seg_sym','')
		frequency = request.POST.get('frequency','1')
		live_period = request.POST.get('live_period','1') # this is in days
		broker = request.POST.get('broker','zerodha')
		take_profit = request.POST.get('take_profit','')
		stop_loss = request.POST.get('stop_loss','')
		quantity = int(float(request.POST.get('quantity','')))
		periodicity = request.POST.get('interval','hour')

		success_flag = True
		try:
			con = get_redis_connection("default")
			pipeline = con.pipeline()
			now = datetime.datetime.now()
			# ex_date = now.replace(day=now.day+int(live_period))
			product = ''
			
			[segment,symbols]=seg_sym.split('_')

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

			product = 'CNC'
			if product == '':
				return JsonResponse({'status':'error','error':'Unknown product type'})

			ex_date = datetime.datetime.today() + datetime.timedelta(days=int(live_period))
			ex_date = ex_date.replace(hour=0,minute=0,second=0)
			expiration_sec = int(float(ex_date.strftime('%s'))-float(now.strftime('%s')))
			# check if backtest
			bt_result = models.BacktestMeta.objects.get(user_uuid=user_uuid,algo_uuid=algo_uuid,seg_sym=seg_sym)
			if seg_sym in bt_result['backtest_result'].keys():
				# in seg_sym backtested already, then it is deployable
				# deployed algorithm redis entry format =>
				# 'deployed'+':'+user_uuid+':'+algo_uuid+':'+seg_sym+':'+periodicity+':'+deployment_uuid=>{algo as json}
				# add storage time in redis
				if quantity!='':
					bt_result['algo_obj']['quantity'] = quantity
				if periodicity!='':
					bt_result['algo_obj']['time_frame'] = periodicity
				if take_profit!='':
					bt_result['algo_obj']['take_profit'] = take_profit
				if stop_loss!='':
					bt_result['algo_obj']['stop_loss'] = stop_loss
				
				bt_result['algo_obj']['deployment_time'] = datetime.datetime.now().isoformat()
				bt_result['algo_obj']['product'] = product
				bt_result['algo_obj']['deployment_type'] = deployment_type

				deployment_uuid = str(uuid.uuid4())

				if '@' in bt_result['algo_obj']['action_str']:
					itoken = con.keys('instruments:*:'+seg_sym.split('_')[1]+':*:'+seg_sym.split('_')[0]+':*')
					if len(itoken)!=1: # missing instrument
						return JsonResponse({'status':'error'})
					itoken = itoken[0].split(':')[1]
					reg = r"@*(\d+\.*\d*)\D*of\D*(\d+\.*\d*)"
					r = re.findall(reg,bt_result['algo_obj']['action_str'])
					[pr,rn]=r[0]					
					# set 123:abcd:PRICETRIGGER:2524673:IR1:68.30:0.1:0.0:algo_name 68.30
					x = [user_uuid,deployment_uuid,'PRICETRIGGER',itoken,'IR1',pr,rn,'0.0',bt_result['algo_obj']['algo_name'],bt_result['algo_obj']['action_type'],bt_result['algo_obj']['quantity'],algo_uuid,product,symbols,segment]
					pipeline.set(':'.join(x),pr)
					add_pricetrigger(itoken,':'.join(x)) 
					pipeline.expire(':'.join(x),expiration_sec)
				
				x = [user_uuid,algo_uuid,seg_sym,periodicity,deployment_uuid]

				keys = con.keys('deployed:'+user_uuid+':'+algo_uuid+':'+seg_sym+':'+periodicity+':*')
				if len(keys)>0:
					redis_key = keys[0]
				else:
					redis_key = 'deployed:'+':'.join(x)
				# +user_uuid+':'+algo_uuid+':'+seg_sym+':'+periodicity+':'+deployment_uuid
				redis_entry = json.dumps({'user_uuid':user_uuid,
										'algo_uuid':algo_uuid,
										'seg_sym':seg_sym,
										'frequency':frequency,
										'broker':broker,
										'deployment_uuid':deployment_uuid,
										'algo_obj':bt_result['algo_obj'],
										'status':0,
										'expiration_time':ex_date.isoformat()
					})
				pipeline.set(redis_key,redis_entry)
				pipeline.expire(redis_key,expiration_sec)
				# settings.ENV,
				pipeline.publish(settings.ENV+'-deployment_channel','ADD:'+redis_key)
				# store the log in mongo because of longer storage requirements
				deployed_algo = models.DeployedAlgorithm(
					user_uuid=user_uuid,
					algo_uuid=algo_uuid,
					algo_name=bt_result['algo_obj']['algo_name'],
					algo_obj=bt_result['algo_obj'],
					deployment_uuid=deployment_uuid,
					segment_symbol =  seg_sym,
					symbol =  seg_sym.split('_')[1],
					segment =  seg_sym.split('_')[0],
					deployment_time = datetime.datetime.now(),
					expiration_time = ex_date,
					frequency = frequency,
					live_period = live_period,
					status = 0
					)

				holding_for_algo = models.HoldingsForAlgorithm(user_uuid=user_uuid,
					algo_uuid=algo_uuid,
					algo_name=bt_result['algo_obj']['algo_name'],
					deployment_uuid=deployment_uuid,
					algo_reference = deployed_algo,
					symbol =  seg_sym.split('_')[1],
					segment =  seg_sym.split('_')[0],
					exchange=exchange,
					product = product,
					position = {'qty':'0.0','last_order_average_price':'0.0'},
					pnl={'final_pnl':'0.0','returns':'0.0'} # this hodls the realized pnl and realised returns
					)

				order_start_log = models.OrderLog(
					user_uuid=user_uuid,
					algo_uuid=algo_uuid,
					deployment_uuid=deployment_uuid,
					log_tag="Waiting",
					log_message="Waiting for first trigger event"
					)

				fetch_single_backtest_result = """
				function(){
				var results = [];
				results = db[collection].findOne({user_uuid:"%s","algo_uuid":"%s","backtest_result.%s":{$exists:true}},{"backtest_result.%s":1,"algo_obj":1,"algo_uuid":1,"updated_at":1,"_id":0});
				return results;
				}"""%(user_uuid,algo_uuid,seg_sym,seg_sym)

				backtest_result = models.BacktestMeta.objects.exec_js(fetch_single_backtest_result)

				if backtest_result==None:
					return JsonResponse({'status':'success','msg':'Missing backtest'})

				# this is the backtest spanpshot for orders log
				order_log_backtest = models.OrderLogBacktest(user_uuid=user_uuid,algo_uuid=algo_uuid,deployment_uuid=deployment_uuid,
					backtest_result=backtest_result['backtest_result'][seg_sym],
					algo_obj=backtest_result['algo_obj']
					)

				deployed_algo.save()
				holding_for_algo.save()
				order_start_log.save()
				order_log_backtest.save()
				pipeline.execute()
				update_usage_util(user_uuid,'deployed')
		except:
			print traceback.format_exc()
			success_flag = False

		if success_flag:
			return JsonResponse({'status':'success'})
		else:
			return JsonResponse({'status':'error'})

	return JsonResponse({'status':'error'})


def backtest_shared(request):
	if request.method == "GET":
		backtest_share_uuid = request.GET.get('sbt','')
		try:
			backtest_item = models.ShareableBacktest.objects(
						backtest_share_uuid = backtest_share_uuid
						)
			assert len(backtest_item)==1
			algo_uuid = backtest_item[0].algo_obj['algo_name']
			algo_name = backtest_item[0].algo_obj['algo_name']
			algo_desc = backtest_item[0].algo_obj.get('algo_desc')
			position_type = backtest_item[0].algo_obj['action_type']
			position_qty = backtest_item[0].algo_obj['quantity']
			entry_logic = backtest_item[0].algo_obj['action_str']
			# exit_logic = backtest_item.algo_obj['exit_logic']
			exit_logic = backtest_item[0].algo_obj.get('action_str_exit','')
			take_profit = backtest_item[0].algo_obj['take_profit']
			stop_loss = backtest_item[0].algo_obj['stop_loss']
			ip_interval = backtest_item[0].algo_obj['time_frame']
			holding_type = backtest_item[0].algo_obj.get('holding_type','CNC')
			start_time = backtest_item[0].algo_obj['dt_start']
			stop_time = backtest_item[0].algo_obj['dt_stop']
			equities = {}
			for bt in backtest_item:
				for k in bt.algo_obj['symbols']: 
					equities[k[1]]= k[0]

			# { "dt_stop" : "10/08/2017", "stop_loss" : "4.0", "algo_uuid" : "4fcc3234-d02f-4cbb-8cb1-b35d353b8971", "initial_capital" : "100000", "time_frame" : "hour", "user_uuid" : "123", "dt_start" : "10/08/2016", "symbols" : [ [ "NSE", "HDFCBANK" ] ], "commission" : 0, "action_type" : "BUY", "take_profit" : "4.0", "action_str" : "2 min SMA higher than 4 min SMA", "algo_name" : "Cloned from ABC", "algo_desc" : "aaaa", "quantity" : "10" }
			redis_con = get_redis_connection("default")

			# algo_deployed=False
			# deployed_seg_sym = []
			# deployed_seg_sym_deployment_uuid = {}
			# res = redis_con.keys('deployed:'+user_uuid+':'+algo_uuid+':*')
			# if len(res)>0:
			# 	algo_deployed=True
			# 	for k in res:
			# 		k = k.split(':')
			# 		deployed_seg_sym.append(k[3])
			# 		deployed_seg_sym_deployment_uuid[k[3]] = k[-1]
			return render(request,'backtest_shared.html',
				{'status':'success',
					'algo_uuid':algo_uuid,
					'algo_name':algo_name,
					'algo_desc':algo_desc,
					'position_type':position_type,
					'position_qty':position_qty,
					'equities':equities,
					'entry_logic':entry_logic,
					'exit_logic':exit_logic,
					'take_profit':take_profit,
					'stop_loss':stop_loss,
					# addition data to populate andn default backtest
					'ip_interval':ip_interval,
					'holding_type':holding_type,
					'start_time':start_time,
					'stop_time':stop_time,
					'bt_url1':settings.BT_URL1,
					'bt_url2':settings.BT_URL2,
					'run_backtest_flag':False,
					'backtest_results':backtest_item.to_json(),#.items()
					# 'algo_deployed':algo_deployed,
					# 'deployed_seg_sym':json.dumps(deployed_seg_sym),
					# 'deployed_seg_sym_deployment_uuid':json.dumps(deployed_seg_sym_deployment_uuid)
					})
		except:
			print traceback.format_exc()
			return redirect('home')
		# use user_uuid and algo_uuid to fetch the list of mongosave backtests
		# try:
		# 	if algo_uuid == '':
		# 		algo_uuid = request.session.pop('algo_uuid','')

		# 	assert algo_uuid != ''
		# except:
		# 	# redirect to dashboard if algo_uuid is none
		# 	pass
	return redirect('home')

def auto_save_backtest_pref(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth or user_uuid=='':
		return redirect('login')

	if request.method == 'POST':
		initial_capital = request.POST.get('initial_capital',10000000)
		dt_start = request.POST.get('dt_start','')
		dt_stop = request.POST.get('dt_stop','')
		holding_type = request.POST.get('holding_type','')
		periodicity = request.POST.get('interval','hour')

		conn = get_redis_connection("default")
		conn.hset('bt_pref',user_uuid+'_'+periodicity,"{}:{}:{}:{}:{}".format(initial_capital,dt_start,dt_stop,holding_type,periodicity))
		return JsonResponse({'status':'success'})

	return JsonResponse({'status':'error','msg':'Type'})

def get_backtest_pref(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth or user_uuid=='':
		return redirect('login')

	if request.method == 'GET':
		interval = request.GET.get('interval','hour')
		conn = get_redis_connection("default")
		resp = conn.hget('bt_pref',user_uuid+'_'+interval)
		if resp == None:
			return JsonResponse({'status':'error','msg':'Not set'})
		
		resp = resp.split(':')
		if(len(resp)!=5):
			return JsonResponse({'status':'error','msg':'Wrong length'})
		[initial_capital,dt_start,dt_stop,holding_type,periodicity] = resp

		return JsonResponse({'status':'success',
			'initial_capital':initial_capital,
			'dt_start':dt_start,
			'dt_stop':dt_stop,
			'holding_type':holding_type,
			'interval':periodicity
			})

	return JsonResponse({'status':'error','msg':'Type'})

def last_date_of_month(year,month,weekday=3):
	lastDayOfMonth = datetime.datetime(year,month,calendar.monthrange(year,month)[1]) 
	while lastDayOfMonth.weekday() != weekday:
		lastDayOfMonth-=datetime.timedelta(days=1)
	return lastDayOfMonth

def deploy_algorithm_multi2(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return redirect('login')
	if request.method == 'POST':
		if request.POST.get('algo_subscription_uuid','')!='':
			try:
				return marketplace_deploy(request)
			except:
				print(traceback.format_exc())
				return JsonResponse({'status':'error',"error":"Unable to deploy discover strategy","error_msg":"Unable to deploy discover strategy"})

		algo_uuid = request.POST.get('algo_uuid','')
		seg_sym_list = request.POST.get('seg_sym_list','')
		seg_sym_quantity_list = request.POST.get('seg_sym_quantity_list','')
		if seg_sym_quantity_list=="":
			seg_sym_quantity_list = seg_sym_list
		frequency = request.POST.get('frequency','1')
		live_period = request.POST.get('live_period','1') # this is in days
		broker = request.POST.get('broker','zerodha')
		deployment_type = request.POST.get('deployment_type','')
		take_profit = request.POST.get('take_profit','')
		stop_loss = request.POST.get('stop_loss','')
		quantity = request.POST.get('quantity','')
		periodicity = request.POST.get('interval','hour')
		
		holding_type = request.POST.get('holding_type','')
		algo_live_for = request.POST.get('algo_live_for','1')
		variety = request.POST.get('variety','REGULAR')
		sound_name = request.POST.get('sound_name','default') 
		order_type = request.POST.get('order_type','MARKET')
		position_sizing_type = request.POST.get('position_sizing_type','-')
		limit_buffer = request.POST.get('buffer','0')
		default_price = request.POST.get('default_price','close').lower()
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
		# if frequency=='0' or frequency=='1':
		# 	frequency = str(int(frequency)+1)
		try:
			seg_sym_list = urllib.unquote(unicode(seg_sym_list).encode('utf-8'))
		except:
			print traceback.format_exc()
			pass
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
		multi_deploy_error_msg = ""
		multi_deploy_error_list = []
		seg_sym_dict = fetch_instruments(seg_sym_list,True)
		print seg_sym_list,len(seg_sym_list),seg_sym_dict
		# assert 1==2
		st = time.time()
		for seg_sym in seg_sym_quantity_list:
			# print seg_sym
			sg = seg_sym
			try:
				dynamic_flag = False
				dynamic_contract = ''
				now = datetime.datetime.now()
				try:
					quantity = str(seg_sym[2])
				except:
					quantity = request.POST.get('quantity','')
				# ex_date = now.replace(day=now.day+int(live_period))
				product = ''
				seg_sym = (seg_sym[0]+'_'+seg_sym[1]).upper()
				seg_sym_bt = seg_sym
				dynamic_action_type = "BUY"
				if "dynamic contract".upper() in seg_sym:
					seg_sym = seg_sym.upper()
					matches = dynamic_sym_params_generator(seg_sym)
					if len(matches)==0:
						print "algo_uuid",algo_uuid,seg_sym_list
						# return JsonResponse({'status':'error'})
						multi_deploy_success = False
					else:
						m = matches[0].split(",")
						dynamic_contract = seg_sym
						# seg_sym = m[0]
						dynamic_flag = True
						[segment,symbols]=["",dynamic_contract[1:]]
						basicSearchSym = m[0].split("_")[-1]
						basicSearchSeg = m[0].split("_")[0]
						# print 'm[6]',m[6]
						if m[6].strip()=='SHORT':
							dynamic_action_type = "SELL"
						if basicSearchSeg == "INDICES" :
							if basicSearchSym == "NIFTY 50" :
								basicSearchSym = "NIFTY"
							elif basicSearchSym == "NIFTY BANK" :
								basicSearchSym = "BANKNIFTY"
						# finalSeg = "NFO-OPT"
						# if segment != "NSE" && segment != "INDICES" && segment == "CDS" :
							# finalSeg = "CDS-OPT"
						seg_sym = m[0]
						seg_sym_bt = dynamic_contract
						year = str(datetime.datetime.now().year%100)
						last_thrusday_of_month = last_date_of_month(now.year,now.month)
						month = datetime.datetime.now().strftime('%B').upper()[:3]
						if now>last_thrusday_of_month:
							month = monthMap[now.month+1]				
						# month="APR"
						if m[0] not in seg_sym_dict.keys():
							dynamic_seg_sym_obj = fetch_instruments_basic(basicSearchSym,year,month,m[1].strip())
							# if dynamic_seg_sym_obj!={}
							# print("dynamic_seg_sym_obj",dynamic_seg_sym_obj)
							seg_sym_dict[m[0]]=str(dynamic_seg_sym_obj.get('lot_size',1))+','+str(dynamic_seg_sym_obj.get('instrument_token',0))
							if m[5].strip()=="WEEKLY" and seg_sym=="INDICES_NIFTY 50":
								seg_sym_dict[m[0]]="75"+','+str(dynamic_seg_sym_obj.get('instrument_token',0))
							print("seg_sym_dict",seg_sym_dict,seg_sym)
				else:
					[segment,symbols]=seg_sym.split('_')

				if order_type == "MIS":
					order_type = "MARKET"
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
						elif dynamic_flag:
							product = 'NRML'
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
						elif dynamic_flag:
							product = 'NRML'

				if ('MCX' in segment):
					variety = 'REGULAR'

				if product == '':
					return JsonResponse({'status':'error','error':'Unknown product type'})

				ex_date = datetime.datetime.today() + datetime.timedelta(days=int(live_period))
				ex_date = ex_date.replace(hour=0,minute=0,second=0)
				expiration_sec = int(float(ex_date.strftime('%s'))-float(now.strftime('%s')))
				# check if backtest
				print("seg_sym",seg_sym_dict,seg_sym,segment,symbols)
				if dynamic_flag and dynamic_contract!='':
					bt_result = models.BacktestMeta.objects.get(user_uuid=user_uuid,algo_uuid=algo_uuid,seg_sym=dynamic_contract)
				else:
					bt_result = models.BacktestMeta.objects.get(user_uuid=user_uuid,algo_uuid=algo_uuid,seg_sym=seg_sym)

				multiplier = 1
				itoken = ''
				if "," in seg_sym_dict.get(seg_sym,"1"):
					multiplier,itoken = seg_sym_dict.get(seg_sym).split(",")
					print 'multiplier',multiplier,itoken,type(multiplier)
					multiplier = int(max(float(multiplier),1))
				else:
					multiplier = int(max(seg_sym_dict.get(seg_sym,1),1))

				print "--->",seg_sym,user_uuid,algo_uuid,seg_sym,multiplier
				# print("aaaaaaaaaaaaaa",seg_sym,bt_result['backtest_result'])
				if seg_sym_bt in bt_result['backtest_result'].keys():
					# in seg_sym backtested already, then it is deployable
					# deployed algorithm redis entry format =>
					# 'deployed'+':'+user_uuid+':'+algo_uuid+':'+seg_sym+':'+periodicity+':'+deployment_uuid=>{algo as json}
					# adding provision for advanced params
					if len(sg)>= 4:
						if sg[3]!="" and sg[3]!="-":
							bt_result['algo_obj']["max_allocation"] = sg[3]
							bt_result['algo_obj']["position_sizing_type"] = position_sizing_type
							quantity = 1.0
					# add storage time in redis
					if quantity!='' and quantity!=0:
						bt_result['algo_obj']['quantity'] = str(int(float(quantity))*multiplier)
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
					if dynamic_flag:
						# print "here",dynamic_action_type
						bt_result['algo_obj']['action_type'] = dynamic_action_type
						bt_result['algo_obj']['position_type'] = dynamic_action_type

					bt_result['algo_obj']['buffer'] = limit_buffer
					bt_result['algo_obj']['default_price'] = default_price
					bt_result['algo_obj']['order_type'] = order_type

					deployment_uuid = str(uuid.uuid4())

					if '@' in bt_result['algo_obj']['action_str']:
						if itoken=='':
							itoken = con.keys('instruments:*:'+seg_sym.split('_')[1]+':*:'+seg_sym.split('_')[0]+':*')
							if len(itoken)!=1: # missing instrument
								# return JsonResponse({'status':'error'})
								multi_deploy_error_list.append(seg_sym.split('_'))
							itoken = itoken[0].split(':')[1]
						reg = r"@*(\d+\.*\d*)\D*of\D*(\d+\.*\d*)"
						r = re.findall(reg,bt_result['algo_obj']['action_str'])
						[pr,rn]=r[0]					
						# set 123:abcd:PRICETRIGGER:2524673:IR1:68.30:0.1:0.0:algo_name 68.30
						x = [user_uuid,deployment_uuid,'PRICETRIGGER',itoken,'IR1',pr,rn,'0.0',bt_result['algo_obj']['algo_name'],bt_result['algo_obj']['action_type'],str(bt_result['algo_obj']['quantity']),algo_uuid,product,symbols,segment,variety,bt_result['algo_obj']['take_profit'],bt_result['algo_obj']['stop_loss'],bt_result['algo_obj'].get('tpsl_type','pct'),deployment_type,periodicity]
						pipeline.set(':'.join(x),pr)
						add_pricetrigger(itoken,':'.join(x)) 
						pipeline.expire(':'.join(x),expiration_sec)
						bt_result['algo_obj']['lua_val'] = ':'.join(x)
					x = [user_uuid,algo_uuid,seg_sym,periodicity,deployment_uuid]

					# keys = con.keys('deployed:'+user_uuid+':'+algo_uuid+':'+seg_sym+':'+periodicity+':*')
					keys = models.DeployedAlgorithm._get_collection().find({"user_uuid":user_uuid,"algo_uuid":algo_uuid,"segment_symbol":seg_sym,"algo_obj.time_frame":periodicity,"status":0,"expiration_time":{"$gte":datetime.datetime.now()}})
					print({"user_uuid":user_uuid,"algo_uuid":algo_uuid,"seg_sym":seg_sym,"algo_obj.time_frame":periodicity,"status":0,"expiration_time":{"$gte":datetime.datetime.now()}},x)
					k0 = None
					for k in keys:
						k0 = k
						print("breaking....ALreadddddddddddddddddddd deployed")
						break
					if k0 is not None and not dynamic_flag:
						x[-1]=k["deployment_uuid"]
						redis_key = 'deployed:'+':'.join(x)
						multi_deploy_error_msg = "Some scrips not deployed as they are already live"
						multi_deploy_success = False
						multi_deploy_error_list.append(seg_sym.split('_'))
						continue
					else:
						redis_key = 'deployed:'+':'.join(x)
					
					# +user_uuid+':'+algo_uuid+':'+seg_sym+':'+periodicity+':'+deployment_uuid
					redis_entry = json.dumps({'user_uuid':user_uuid,
											'algo_uuid':algo_uuid,
											'seg_sym':seg_sym,
											'frequency':frequency,
											'broker':request.session.get("broker",broker),
											'deployment_uuid':deployment_uuid,
											'algo_obj':bt_result['algo_obj'],
											'status':0,
											'expiration_time':ex_date.isoformat(),
											'algo_live_for':algo_live_for,
											'order_type':order_type,
											'variety':variety,
											'email':request.session.get('user_email',''),
											# dynamic contract payload
											'dynamic_flag':dynamic_flag,
											'dynamic_contract':dynamic_contract
						})
					pipeline.set(redis_key,redis_entry)
					pipeline.expire(redis_key,expiration_sec)
					# settings.ENV,
					print("redis_key",redis_key)
					pipeline.publish(settings.ENV+'-deployment_channel','ADD:'+redis_key)
					# store the log in mongo because of longer storage requirements
					deployed_algo = models.DeployedAlgorithm(
						user_uuid=user_uuid,
						algo_uuid=algo_uuid,
						algo_name=bt_result['algo_obj']['algo_name'],
						algo_obj=bt_result['algo_obj'],
						deployment_uuid=deployment_uuid,
						deployment_type = deployment_type,
						segment_symbol =  seg_sym,
						order_type = order_type,
						symbol =  symbols,#seg_sym.split('_')[1],
						segment =  segment,#seg_sym.split('_')[0],
						deployment_time = datetime.datetime.now(),
						expiration_time = ex_date,
						frequency = frequency,
						live_period = live_period,
						status = 0
						)

					holding_for_algo = models.HoldingsForAlgorithm(user_uuid=user_uuid,
						algo_uuid=algo_uuid,
						algo_name=bt_result['algo_obj']['algo_name'],
						deployment_uuid=deployment_uuid,
						deployment_type = deployment_type,
						algo_reference = deployed_algo,
						symbol =  symbols,#seg_sym.split('_')[1],
						segment =  segment,#seg_sym.split('_')[0],
						product = product,
						position = {'qty':0,'last_order_average_price':0.0},
						pnl={'final_pnl':0,'returns':0.0} # this hodls the realized pnl and realised returns
						)

					order_start_log = models.OrderLog(
						user_uuid=user_uuid,
						algo_uuid=algo_uuid,
						deployment_uuid=deployment_uuid,
						deployment_type = deployment_type,
						log_tag="Waiting",
						log_message="Waiting for first trigger event"
						)

					fetch_single_backtest_result = """
					function(){
					var results = [];
					results = db[collection].findOne({user_uuid:"%s","algo_uuid":"%s","backtest_result.%s":{$exists:true}},{"backtest_result.%s":1,"algo_obj":1,"algo_uuid":1,"updated_at":1,"_id":0});
					return results;
					}"""%(user_uuid,algo_uuid,seg_sym_bt,seg_sym_bt)

					# fetch_single_backtest_result_dict = {user_uuid:"%s","algo_uuid":"%s","backtest_result.%s":{$exists:true}},{"backtest_result.%s":1,"algo_obj":1,"algo_uuid":1,"updated_at":1,"_id":0});
					# return results;
					# }
					backtest_result = models.BacktestMeta.objects.exec_js(fetch_single_backtest_result)
					# backtest_result = models.Algorithm._get_collection().aggregate(algo_snap_query_dict) 
					if backtest_result==None:
						multi_deploy_error_list.append(seg_sym_bt.split('_'))
						# return JsonResponse({'status':'success','msg':'Missing backtest'})

					# this is the backtest spanpshot for orders log
					order_log_backtest = models.OrderLogBacktest(user_uuid=user_uuid,algo_uuid=algo_uuid,deployment_uuid=deployment_uuid,
						backtest_result=backtest_result['backtest_result'][seg_sym_bt],
						algo_obj=backtest_result['algo_obj']
						)

					# st2 = time.time()
					deployed_algo.save()
					holding_for_algo.save()
					order_start_log.save()
					order_log_backtest.save()
					pipeline.execute()
					update_usage_util(user_uuid,'deployed')
					# print(time.time()-st2)
			except:
				print traceback.format_exc()
				print "algo_uuid",algo_uuid,seg_sym_list
				# return JsonResponse({'status':'error'})
				multi_deploy_success = False

		print(time.time()-st)
		if(multi_deploy_success):
			return JsonResponse({'status':'success'})
		else:
			return JsonResponse({'status':'error',"error":multi_deploy_error_msg,"error_msg":multi_deploy_error_msg,'multi_deploy_error_list':multi_deploy_error_list})

	return JsonResponse({'status':'error'})

def fast_backtest_shared(request):
	if request.method == "GET":
		backtest_share_uuid = request.GET.get('sbt','')
		max_count = int(request.GET.get('max_count',-1))
		try:
			t = time.time()
			backtest_item = models.ShareableBacktest.objects.get(
						backtest_share_uuid = backtest_share_uuid
						)

			print("1",time.time()-t)
			t = time.time()
			bt_json = ujson.loads(backtest_item.to_json())
			backtest_item = bt_json
			# assert len(backtest_item)==1
			algo_uuid = backtest_item['algo_obj']['algo_name']
			algo_name = backtest_item['algo_obj']['algo_name']
			algo_desc = backtest_item['algo_obj'].get('algo_desc','')
			position_type = backtest_item['algo_obj']['action_type']
			position_qty = backtest_item['algo_obj']['quantity']
			entry_logic = backtest_item['algo_obj']['action_str']
			print("2",time.time()-t)
			t = time.time()
			# exit_logic = backtest_item['algo_obj']['exit_logic']
			exit_logic = backtest_item['algo_obj'].get('action_str_exit','')
			take_profit = backtest_item['algo_obj']['take_profit']
			stop_loss = backtest_item['algo_obj']['stop_loss']
			ip_interval = backtest_item['algo_obj']['time_frame']
			holding_type = backtest_item['algo_obj'].get('holding_type','CNC')
			start_time = backtest_item['algo_obj']['dt_start']
			stop_time = backtest_item['algo_obj']['dt_stop']
			seg_sym = backtest_item['seg_sym']
			k0,k1 = seg_sym.split("_")
			equities = {}
			# for bt in backtest_item:
			# 	for k in bt.algo_obj['symbols']: 
			equities[k1]= k0
			print("3",time.time()-t)
			t = time.time()

			# if backtest_item["backtest_result"].get(seg_sym,None) is not None: 
			# 	backtest_item["backtest_result"][seg_sym]['trade_log']=[]
			# 	backtest_item["backtest_result"][seg_sym]['pnl']=[]
			# advanced parameters
			chart_type = backtest_item['algo_obj'].get('chart_type','candlestick')
			trade_time_given = backtest_item['algo_obj'].get('trade_time_given',"False")
			trading_start_time = backtest_item['algo_obj'].get('trading_start_time','09:00')
			trading_stop_time = backtest_item['algo_obj'].get('trading_stop_time','23:30')
			#--------------------#

			start_time = backtest_item['algo_obj']['dt_start']
			stop_time = backtest_item['algo_obj']['dt_stop']
			public = backtest_item.get('public','')
			print("4",time.time()-t)
			t = time.time()
			if public=="":
				entry_logic = ''
				exit_logic = ''

			backtest_items_json = [bt_json]
			backtest_items_list = []
			for bt in backtest_items_json:
				for k in bt['algo_obj']['symbols']: 
					equities[k[1]]=k[0]
				k2 = bt["seg_sym"]
				if k2 in bt["backtest_result"].keys():
					if max_count==-3:
						bt["backtest_result_meta"]={}
						bt["backtest_result"][k2]["pnl"] = []
					elif max_count==-1:
						pass
					elif max_count == -2:	
						bt["backtest_result"][k2]["pnl"] = []
					else:
						bt["backtest_result"][k2]["pnl"]=downsample(bt["backtest_result"][k2]["pnl"],max_count)
				backtest_items_list.append(bt)
			# { "dt_stop" : "10/08/2017", "stop_loss" : "4.0", "algo_uuid" : "4fcc3234-d02f-4cbb-8cb1-b35d353b8971", "initial_capital" : "100000", "time_frame" : "hour", "user_uuid" : "123", "dt_start" : "10/08/2016", "symbols" : [ [ "NSE", "HDFCBANK" ] ], "commission" : 0, "action_type" : "BUY", "take_profit" : "4.0", "action_str" : "2 min SMA higher than 4 min SMA", "algo_name" : "Cloned from ABC", "algo_desc" : "aaaa", "quantity" : "10" }
			# redis_con = get_redis_connection("default")

			# algo_deployed=False
			# deployed_seg_sym = []
			# deployed_seg_sym_deployment_uuid = {}
			# res = redis_con.keys('deployed:'+user_uuid+':'+algo_uuid+':*')
			# if len(res)>0:
			# 	algo_deployed=True
			# 	for k in res:
			# 		k = k.split(':')
			# 		deployed_seg_sym.append(k[3])
			# 		deployed_seg_sym_deployment_uuid[k[3]] = k[-1]
			return JsonResponse({'status':'success',
					'algo_uuid':algo_uuid,
					"backtest_share_uuid":backtest_share_uuid,
					'algo_name':algo_name,
					'algo_desc':algo_desc,
					'position_type':position_type,
					'position_qty':position_qty,
					'equities':equities,
					'entry_logic':entry_logic,
					'exit_logic':exit_logic,
					'take_profit':take_profit,
					'stop_loss':stop_loss,
					# addition data to populate andn default backtest
					'ip_interval':ip_interval,
					'holding_type':holding_type,
					# advanced fields
					'chart_type':chart_type,
					'trade_time_given':trade_time_given,
					'trading_start_time':trading_start_time,
					'trading_stop_time':trading_stop_time,
					#----------------#
					'start_time':start_time,
					'stop_time':stop_time,
					'bt_url1':settings.BT_URL1,
					'bt_url2':settings.BT_URL2,
					'run_backtest_flag':False,
					'backtest_results':backtest_items_list,#.items()
					'algo_deployed':False,
					'deployed_seg_sym':[],
					'deployed_seg_sym_deployment_uuid':{},
					'public':public
					})
		except:
			print traceback.format_exc()
			return JsonResponse({'status':"error"})
		# use user_uuid and algo_uuid to fetch the list of mongosave backtests
		# try:
		# 	if algo_uuid == '':
		# 		algo_uuid = request.session.pop('algo_uuid','')

		# 	assert algo_uuid != ''
		# except:
		# 	# redirect to dashboard if algo_uuid is none
		# 	pass
	return JsonResponse({'status':"error"})

def fetch_shared_backtest_chart(request):
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
		backtest_share_uuid = request.GET.get('sbt','')
		max_count = int(request.GET.get('max_count',250))
		seg_sym = request.GET.get('seg_sym',"")
		tl = request.GET.get('tl',"false")
		if (backtest_share_uuid!=''):
			try:
				avg_return_pct = 0
				avg_return = 0
				absolute_pnl = 0
				absolute_pnl_pct = 0
				sym_count = 0
				sym_pnl = []
				sym_max_cap_used = []
				pb = models.ShareableBacktest._get_collection().find({"backtest_share_uuid":backtest_share_uuid},{'_id':0 ,'algo_obj':0})
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
		print(algo_subscription_uuid,"algo_subscription_uuid")
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
				print("seg_sym",seg_sym,algo_subscription_uuid)
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

def save_backtest_params(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({'status':'error',"error":"auth","error_msg":"auth"})
	if request.method == 'POST':
		if request.POST.get('algo_uuid','')=='':
			return JsonResponse({'status':'error',"error":"Strategy not provided","error_msg":"Strategy not provided"})

		algo_uuid = request.POST.get('algo_uuid','')
		algo_name = request.POST.get('algo_name','')
		algo_desc = request.POST.get('algo_desc','')
		scripList = request.POST.get('scripList','')
		try:
			algo = models.Algorithm.objects().get(user_uuid=user_uuid,algo_uuid=algo_uuid)
			changed = False
			if algo_name!="":
				algo["algo_name"]=algo_name
				algo["algo_state"]["algo_name"]=algo_name
				changed = True
			if algo_desc!="":
				algo["algo_desc"]=algo_desc
				algo["algo_state"]["algo_desc"]=algo_desc
				changed = True
			if scripList!="":
				cripListDict = ujson.loads(scripList)
				algo["algo_state"]["scripList"]=algo_desc
				changed = True
			if changed:
				algo.save()
			return JsonResponse({'status':'success'})
		except DoesNotExist:
			return JsonResponse({'status':'error',"error":"Strategy not found","error_msg":"Strategy not found"})

		seg_sym_quantity_list = request.POST.get('seg_sym_quantity_list','')
		if seg_sym_quantity_list=="":
			seg_sym_quantity_list = seg_sym_list
	else:
		return JsonResponse({'status':'error',"error":"Invalid method"})
	return JsonResponse({'status':'error',"error":"Invalid method","error_msg":"Invalid method"})
