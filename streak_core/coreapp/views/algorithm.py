from django.shortcuts import render,redirect
from django.http import JsonResponse
from django_redis import get_redis_connection
import random
import uuid
import string
import datetime
import traceback
from django.conf import settings
from coreapp import models
import ujson
import requests
import os
from utility import get_deployment_keys
from mongoengine import ValidationError,NotUniqueError

from NSPEngine import Action,Strategy

def algorithm(request):
	
	# if request.method == "GET":
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True

	if not user_is_auth:
		return redirect('home')

	if request.method == "GET":
		
		algo_uuid = request.GET.get('algo_uuid','')
		if algo_uuid == '':
			return render(request,'algorithm2.html',
					{'status':'success'
					})

		try:
			algo = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_uuid = algo_uuid,
					status = 0
					)
			return render(request,'algorithm2.html',
							{'algo':algo,
							'status':'success'}
							)

		except models.Algorithm.DoesNotExist:
			# TODO log error
			if settings.DEBUG:
				print traceback.format_exc()
			return redirect('dashboard')


	if request.method == "POST":

		post_request_keys = request.POST.keys()
		if 'algo_name' in post_request_keys and 'algo_desc' in post_request_keys:

			algo_name = request.POST['algo_name']
			algo_desc = request.POST['algo_desc']
			return render(request,'algorithm2.html',
							{'algo_name':algo_name,
							'algo_desc':algo_desc
							})

		algo_uuid = request.POST.get('algo_uuid','')
		try:
			algo = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_uuid = algo_uuid
					)
			algo.status = 0 # created/autosaved 
			algo.save()

			return render(request,'algorithm2.html',
							{'algo':algo,
							'status':'success'}
							)

		except models.Algorithm.DoesNotExist:
			# TODO log error
			if settings.DEBUG:
				print traceback.format_exc()
			return redirect('dashboard')

		except:
			# TODO log error
			if settings.DEBUG:
				print traceback.format_exc()
			return redirect('home')

	error = {}

	if 'redirect_from' in request.session.keys():
		pass

	return render(request,'algorithm2.html',
					{'status':'success'
					})

def algorithm3(request):
	
	# if request.method == "GET":
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True

	if not user_is_auth:
		return redirect('home')

	if request.method == "GET":
		
		algo_uuid = request.GET.get('algo_uuid','')
		if algo_uuid == '':
			return render(request,'algorithm3.html',
					{'status':'success'
					})

		try:
			algo = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_uuid = algo_uuid,
					status = 0
					)
			return render(request,'algorithm3.html',
							{'algo':algo,
							'status':'success'}
							)

		except models.Algorithm.DoesNotExist:
			# TODO log error
			if settings.DEBUG:
				print traceback.format_exc()
			return redirect('dashboard')


	if request.method == "POST":

		post_request_keys = request.POST.keys()
		if 'algo_name' in post_request_keys and 'algo_desc' in post_request_keys:

			algo_name = request.POST['algo_name']
			algo_desc = request.POST['algo_desc']
			return render(request,'algorithm3.html',
							{'algo_name':algo_name,
							'algo_desc':algo_desc
							})

		algo_uuid = request.POST.get('algo_uuid','')
		try:
			algo = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_uuid = algo_uuid
					)
			algo.status = 0 # created/autosaved 
			algo.save()

			return render(request,'algorithm3.html',
							{'algo':algo,
							'status':'success'}
							)

		except models.Algorithm.DoesNotExist:
			# TODO log error
			if settings.DEBUG:
				print traceback.format_exc()
			return redirect('dashboard')

		except:
			# TODO log error
			if settings.DEBUG:
				print traceback.format_exc()
			return redirect('home')

	error = {}

	if 'redirect_from' in request.session.keys():
		pass

	return render(request,'algorithm3.html',
					{'status':'success'
					})

# curr in use
def algorithm3_(request):
	resp_json = False
	if(request.META.get('HTTP_X_CSRFTOKEN',None)):
		resp_json = True
	# if request.method == "GET":
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True

	if not user_is_auth:
		if(request.method == "GET"):
			if(request.GET.get('stock',None)!=None):
				request.session['stock'] = request.GET.get('stock',None)
				try:
					conn = get_redis_connection("default")
					ref_count = conn.get('kite_menu_ref')
					if not ref_count:
						ref_count = 1
					else:
						ref_count = int(str(ref_count))+1
					conn.set('kite_menu_ref',ref_count)
					ref_count = conn.get('kite_menu_ref')
				except:
					pass
				return redirect('broker_login')
			if(request.GET.get('resp','')=='json' and user_uuid!=''):
				return JsonResponse({'error_msg':'Session expired, relogin required','status':'error'})
			if resp_json and user_uuid!='':
				return JsonResponse({'error_msg':'Session expired, relogin required','status':'error'})
		return JsonResponse({'error_msg':'Session expired, relogin required','status':'error'})
		# return redirect('home')

	if request.method == "GET":
		
		algo_uuid = request.GET.get('algo_uuid','')
		if algo_uuid == '':
			equities = None
			if 'stock' in request.GET.keys():
				try:
					conn = get_redis_connection("default")
					ref_count = conn.get('kite_menu_ref')
					if not ref_count:
						ref_count = 1
					else:
						ref_count = int(str(ref_count))+1
					conn.set('kite_menu_ref',ref_count)
					ref_count = conn.get('kite_menu_ref')
				except:
					pass
			if 'stock' in request.session.keys():
				equities = request.session.pop('stock','')
			return render(request,'algorithm3_.html',
					{'status':'success',
					'equities':equities
					})

		try:
			algo = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_uuid = algo_uuid
					)
			algo = ujson.loads(algo.to_json())
			try:
				equities = []
				backtest_item = models.BacktestMeta.objects(
						algo_uuid = algo_uuid,
						user_uuid = user_uuid
						)
				for b in backtest_item:
					if len(b['algo_obj']['symbols'][0])>0:
						equities.append({"segment":b['algo_obj']['symbols'][0][0],"symbol":b['algo_obj']['symbols'][0][1]})
						# equities.append(k['algo_obj']['symbols'])
				print equities
				# print algo['algo_state']['scripList']
				if equities!=[] and algo['algo_state'].get('scripList',None) is None:
					print '---------------'
					algo['algo_state']['scripList'] = equities
			except:
				print traceback.format_exc()
				pass
			res = get_deployment_keys({"user_uuid":user_uuid,"algo_uuid":algo_uuid,"status":0,"expiration_time":{"$gte":datetime.datetime.now()}})
			algo_live = False
			if len(res)>1:
				algo_live = True
			# if(request.GET.get('resp','')=='json' or resp_json):
			return JsonResponse({'algo':algo,'algo_live':algo_live,'status':'success'})
			# return render(request,'algorithm3_.html',
							# {'algo':algo,
							# 'status':'success'}
							# )

		except models.Algorithm.DoesNotExist:
			# TODO log error
			# if settings.DEBUG:
			print traceback.format_exc()
			return JsonResponse({'error_msg':"Strategy not found",'status':'error'})


	if request.method == "POST":

		post_request_keys = request.POST.keys()
		if 'algo_name' in post_request_keys and 'algo_desc' in post_request_keys:

			algo_name = request.POST['algo_name']
			algo_desc = request.POST['algo_desc']
			return render(request,'algorithm3_.html',
							{'algo_name':algo_name,
							'algo_desc':algo_desc
							})

		algo_uuid = request.POST.get('algo_uuid','')
		try:
			algo = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_uuid = algo_uuid
					)
			algo.status = 0 # created/autosaved 
			algo.save()

			res = get_deployment_keys({"user_uuid":user_uuid,"algo_uuid":algo_uuid,"status":0,"expiration_time":{"$gte":datetime.datetime.now()}})
			algo_live = False
			if len(res)>1:
				algo_live = True

			if(request.POST.get('resp','')=='json' or resp_json):
				return JsonResponse({'algo':ujson.loads(algo.to_json()),'status':'success'})
			return render(request,'algorithm3_.html',
							{'algo':algo,
							'algo_live':algo_live,
							'status':'success'}
							)

		except models.Algorithm.DoesNotExist:
			# TODO log error
			if settings.DEBUG:
				print traceback.format_exc()
			return redirect('dashboard')

		except:
			# TODO log error
			if settings.DEBUG:
				print traceback.format_exc()
			return redirect('home')

	error = {}

	if 'redirect_from' in request.session.keys():
		pass

	return render(request,'algorithm3_.html',
					{'status':'success'
					})

# not being used
def algorithm4(request):
	
	# if request.method == "GET":
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True

	if not user_is_auth:
		return redirect('home')

	if request.method == "GET":
		
		algo_uuid = request.GET.get('algo_uuid','')
		if algo_uuid == '':
			return render(request,'algorithm4.html',
					{'status':'success'
					})

		try:
			algo = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_uuid = algo_uuid,
					status = 0
					)
			return render(request,'algorithm4.html',
							{'algo':algo,
							'status':'success'}
							)

		except models.Algorithm.DoesNotExist:
			# TODO log error
			if settings.DEBUG:
				print traceback.format_exc()
			return redirect('dashboard')


	if request.method == "POST":

		post_request_keys = request.POST.keys()
		if 'algo_name' in post_request_keys and 'algo_desc' in post_request_keys:

			algo_name = request.POST['algo_name']
			algo_desc = request.POST['algo_desc']
			return render(request,'algorithm4.html',
							{'algo_name':algo_name,
							'algo_desc':algo_desc
							})

		algo_uuid = request.POST.get('algo_uuid','')
		try:
			algo = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_uuid = algo_uuid
					)
			algo.status = 0 # created/autosaved 
			algo.save()

			return render(request,'algorithm4.html',
							{'algo':algo,
							'status':'success'}
							)

		except models.Algorithm.DoesNotExist:
			# TODO log error
			if settings.DEBUG:
				print traceback.format_exc()
			return redirect('dashboard')

		except:
			# TODO log error
			if settings.DEBUG:
				print traceback.format_exc()
			return redirect('home')

	error = {}

	if 'redirect_from' in request.session.keys():
		pass

	return render(request,'algorithm4.html',
					{'status':'success'
					})

import NSPEngine.strategy_parser as sp
parsing_tree_algo = None
with open(os.path.dirname(os.path.abspath(__file__))+'/../../js_parsing_tree_original.json') as parsing_tree_file:
	parsing_tree_algo = ujson.load(parsing_tree_file)['main']
	parsing_temp = []

candle_freq_map = {'min':10,
						'3min':9,
						'5min':8,
						'10min':7,
						'15min':6,
						'30min':5,
						'45min':4,
						'hour':3,
						'day':2,
						};
candle_map = {"min":'1 Minute',"3min":'3 Minutes',"5min":'5 Minutes',"10min":'10 Minutes',"15min":'15 Minutes',"30min":'30 Minutes',"hour":'1 Hour',"day":'1 Day'};
chart_map = {"heikinAshi":'Heikin-Ashi Chart', "candlestick":'Candlestick chart'}
order_type_map = {"MIS":'MIS', "CNC":'CNC/NRML', "CNC/NRML":'CNC/NRML'}
comparator_map = {"above":"higher than","below":"lower than"}
def indicator_objs(action_str):
	entryIndicators = []
	e = sp.EvalGenerator2(action_str)
	e.generate_eval()
	parsed_list = e.parsed_list
	indicator_str_all = e.main_parser.indicator_str_all
	and_or_list = ['and']

	if parsed_list:
		count = 0
		print 'length',len(parsed_list)
		if parsed_list==[{'indicator_list': [], 'comparator': ''}]:
			entryIndicators = [
							{
								"indicator": "Indicator",
								"compareIndicator": "Indicator",
								"id": str(uuid.uuid1().int>>64),
								"comparator": "Comparator"
							}
						]
			return [entryIndicators,['and']]
		for condition in parsed_list:
			elem_dict = {}
			if(count%2!=1):
#				 if (indicator_str_all)
				print indicator_str_all
				print indicator_str_all[count/2],count
				elem_indicator = indicator_str_all[count/2]
				if(elem_indicator[-1]):
					elem_dict['indicator']=elem_indicator[0][0].strip()
					elem_dict['comparator']=comparator_map.get(elem_indicator[-1].strip(),elem_indicator[-1].strip())
					elem_dict['comparatorItem']={"name":comparator_map.get(elem_indicator[-1].strip(),elem_indicator[-1].strip())}
					elem_dict['compareIndicator']=elem_indicator[0][-1].strip()
				else:
					elem_dict['indicator']=elem_indicator[0][0].strip()
					elem_dict['comparator']="N/A"
					elem_dict['compareIndicator']="N/A"
			indicator_list = condition.get('indicator_list',[])
			if(condition.get('comparator','')!=' at '):
				for i in range(len(indicator_list)):
					elem = indicator_list[i]
					if i == 0:
						if(elem.get('indicator',"")=='price'):
							elem_dict['indicatorItem'] = parsing_tree_algo['indicator']["at_price"]
						elif(elem.get('indicator',"")=='float'):
							elem_dict['indicatorItem'] = parsing_tree_algo['indicator']["number"]
						else:
							elem_dict['indicatorItem'] = parsing_tree_algo['indicator'][elem.get('indicator',"")]
						if(elem.get('indicator',"") in ["opening_range","opening_range_volume"]):
							elem_dict["selected_candle_interval"] = candle_freq_map[elem.get('params',{})["Range"]]
						elif(elem.get('indicator',"") in ["prev_n","prev_n_vol"]):
							elem_dict["selected_candle_interval"]=candle_freq_map[elem.get('params',{})["candle"]]
						else:
							elem_dict["selected_candle_interval"]=None
						if(elem.get('params',{})!={"offset": []}):
							# elem_dict['indicatorDetails'] = elem.get('params',{})
							if(elem.get('indicator',"")=='float'):
								elem_dict['indicatorDetails'] = {"number": elem.get('params',{'value':"0.0"})["value"].strip()}
							else:
								elem_dict['indicatorDetails'] = elem.get('params',{})
						else:
							elem_dict['indicatorDetails'] = {}
					if i == 1:
						if(elem.get('indicator',"")=='price'):
							elem_dict['compareIndicatorItem'] = parsing_tree_algo['indicator']["at_price"]
						elif(elem.get('indicator',"")=='float'):
							elem_dict['compareIndicatorItem'] = parsing_tree_algo['indicator']["number"]
						else:
							elem_dict['compareIndicatorItem'] = parsing_tree_algo['indicator'][elem.get('indicator',"")]
						if(elem.get('params',{})!={"offset": []}):
							# elem_dict['compareIndicatorDetails'] = elem.get('params',{})
							if(elem.get('indicator',"")=='float'):
								elem_dict['compareIndicatorDetails'] = {"number": elem.get('params',{'value':"0.0"})["value"].strip()}
							else:
								elem_dict['compareIndicatorDetails'] = elem.get('params',{})
						else:
							elem_dict['compareIndicatorDetails'] = {}
	#				 print condition.get('indicator_list',[]),len(condition.get('indicator_list',[]))
					if type(elem)==dict:
						print('condition elem',elem.get('params',""))
			else:
				elem = indicator_list[1]
				elem_dict['indicatorItem'] = parsing_tree_algo['indicator']["at_price"]
				elem_dict['indicatorDetails'] = elem.get('params',{})
				elem_dict['indicator']=action_str
				elem_dict['comparator']='N/A'
				elem_dict['comparatorItem']={}
				elem_dict['compareIndicator']='N/A'
				if(elem_dict!={}):
					elem_dict['id']=str(uuid.uuid1().int>>64)
					elem_dict['andor']="and"
					elem_dict["compareIndicatorValid"]=True
					elem_dict["indicatorValid"]=True
					entryIndicators.append(elem_dict)
				break
			if(elem_dict!={}):
				elem_dict['id']=str(uuid.uuid1().int>>64)
				elem_dict['andor']="and"
				elem_dict["compareIndicatorValid"]=True
				elem_dict["indicatorValid"]=True
				entryIndicators.append(elem_dict)
			else:
				if(len(entryIndicators)>0):
					entryIndicators[-1]['andor']=condition.get("condition","and")
					and_or_list.append(condition.get("condition","and"))
#				 print('------------>',elem_dict)
			count+=1
#	 print entryIndicators
	if len(entryIndicators)==0:
		entryIndicators = [
							{
								"indicator": "Indicator",
								"compareIndicator": "Indicator",
								"id":str(uuid.uuid1().int>>64),
								"comparator": "Comparator"
							}
						]
	return [entryIndicators,and_or_list]

# algo_bridge('Supertrend(7,3) lower than Supertrend(5,3) and 20 sma higher than rsi(10) and Stick sandwich(Bullish) is formed and Price @ 110 in range of 0.5%')
# indicator_objs('')

def algo_state_create(algo_name,entry_str,exit_str,take_profit,stop_loss,seg_sym_list,candle_interval,
					  position_type,
					  quantity,
					  chart_type="candlestick",
					  holding_type="CNC",
					  trading_start_time="09:00",
					  trading_stop_time="23:30"):
	algo_state = {}
	algo_state['algo_name']=algo_name
	algo_state['takeProfit']=str(take_profit)
	algo_state['stopLoss']=str(stop_loss)
	algo_state['candleInterval']=candle_map[candle_interval]
	algo_state['time_frame']=candle_interval
	scripList = []
	for s in seg_sym_list:
		scripList.append({"segment":s[0],"symbol":s[1]})
	algo_state['scripList']=scripList
	if(position_type==1):
		position_type = 'Buy'
	elif(position_type==-1):
		position_type = 'Sell'
	algo_state['positionType']=position_type
	algo_state['quantity']=str(quantity)
	
	[x,y]=indicator_objs(entry_str)
	algo_state['entryIndicators'] = x
	algo_state['entryAndOrs'] = y
	[x_,y_]=indicator_objs(exit_str)
	algo_state['exitIndicators'] = x_
	algo_state['exitAndOrs'] = y_
	
	algo_state["scrollEnabled"]=True
	algo_state["editMode"]=True
	algo_state["disabled"]=False
	algo_state["showScripModal"]=False
	algo_state["showScripList"]=False
	algo_state["showExitIndicator"]=False
	
	if(exit_str!=''):
		algo_state["showExitIndicator"]=True
		
#	 algo_state["csrftoken"]=str(uuid.uuid4())
	
	algo_state["scripValue"]=""
	algo_state["algoNameValid"]=True
	algo_state["scripValid"]=True
	if len(scripList)==0:
		algo_state["scripValid"]=False

	algo_state["entryValid"]=True
	algo_state["exitValid"]=True
	algo_state["positionValid"]=True
	
	if('enko' not in chart_type):
		algo_state["chart_type"]=chart_map[chart_type]
	else:
		# print chart_type
		algo_state["chart_type"]=chart_type

	algo_state["order_type"]=order_type_map[holding_type]
	algo_state["trading_start_time"]=trading_start_time.replace(':',' : ')
	algo_state["trading_stop_time"]=trading_stop_time.replace(':',' : ')
	algo_state["gotAlgoState"]=True
	algo_state["show_advance"]=False
	
	# return ujson.dumps(algo_state)
	return algo_state

def algo_complete_score(equities,entry_logic,algo_state,take_profit,stop_loss,quantity=0): 
	# name = 25
	# stock = 50
	# entry = 75
	# sl/tp = 100
	# 100 
	percent_complete=25 
	if len(equities)!=0: 
		percent_complete = percent_complete+25 
	if len(algo_state.get("entryIndicators",[]))>0: 
		percent_complete = percent_complete+25
	# if quantity!=0.0:   
	# 	percent_complete = percent_complete+21 
	if take_profit!='0.0' and take_profit!='' and stop_loss!='0.0' and stop_loss!='':   
		percent_complete = 100
	# if stop_loss!='0.0' and stop_loss!='':   
	# 	percent_complete = percent_complete+18 
	return min(100,percent_complete) 

def submit_algorithm(request):
	"""
	Submit algorithm enables creating and updation of algorithm
	parameters
	----------
	request - This the django request object

	NOTE : This method can be made more efficient as it currently directly stores the entry logic and not the action, requires action parsing evey time
	"""
	print request.META.items()
	if request.method == 'POST' or request.method== 'GET':
		user_uuid = request.session.get('user_uuid', '')
		user_is_auth = request.session.get('user_is_auth', False)

		if settings.ENV == "local" or settings.ENV == 'local1':
			user_uuid = '123'
			user_is_auth = True
		if not user_is_auth:
			return JsonResponse({'error':['Session expired, relogin required'],'status':'error'})
			# return redirect('home')

		printable = set(string.printable)
		
		algo_uuid = request.POST.get('algo_uuid','')
		algo_name = request.POST.get('algo_name','').strip('<>/,{}')
		algo_desc = request.POST.get('algo_desc','').strip('<>/,{}')
		
		position_type = request.POST.get('position_type','')
		position_qty = request.POST.get('position_qty','')
		if position_qty=="":
			position_qty = 0.0
		quantity = float(position_qty)
		
		entry_logic = request.POST.get('entry_logic','').replace(" undefined "," and ")
		exit_logic = request.POST.get('exit_logic','').replace(" undefined "," and ")

		take_profit = request.POST.get('take_profit','0.0').strip('%')
		stop_loss = request.POST.get('stop_loss','0.0').strip('%')
		if stop_loss=="":
			stop_loss = '0.0'
		if take_profit=="":
			take_profit = '0.0'
		time_frame = request.POST.get('time_frame','day')
		cover_proportion = request.POST.get('cover_proportion',1)

		min_candle_freq = request.POST.get('min_candle_freq',1000)
		
		create_plus = request.POST.get('create_plus',None)
		if create_plus is None or create_plus=='false':
			create_plus = False
		else:
			create_plus = True

		equities = request.POST.get('equities','').decode('hex')#'\x00{\x00"\x00H\x00D\x00F\x00C\x00B\x00A\x00N\x00K\x00"\x00:\x00"\x00N\x00S\x00E\x00"\x00}'
		if equities!="": 
			equities = eval(filter(lambda x: x in printable, equities)) 
		else: 
			equities = {}

		print equities.items()
		if(equities!={}):
			equities = [[v,k.replace('_'+v,'')] for k,v in equities.items()]
		else:
			equities = []
		print equities
		# advanced fields
		holding_type = request.POST.get('holding_type','MIS')
		trade_time_given = request.POST.get('trade_time_given',"False")
		if(trade_time_given=='True'):
			trade_time_given = "True"
		else:
			trade_time_given = "False"
		trading_start_time = request.POST.get('trading_start_time','09:00')
		trading_stop_time = request.POST.get('trading_stop_time','23:30')
		chart_type = request.POST.get('chart_type','candlestick')
		daily_strategy_cycle = request.POST.get('daily_strategy_cycle','-')
		tpsl_type = request.POST.get('tpsl_type','pct')
		max_allocation = request.POST.get('max_allocation','')
		position_sizing_type = request.POST.get('position_sizing_type','')
		#-----------------#
		html_block = request.POST.get('html_block','')

		algo_state_str = request.POST.get('algo_state',"{}") 
		if algo_state_str=="": 
			algo_state_str = "{}" 
		algo_state = ujson.loads(algo_state_str)

		if(algo_state=={} and entry_logic!=""):
			try:
				algo_state = algo_state_create(algo_name,
											entry_logic,
											exit_logic,
											take_profit,
											stop_loss,
											equities,
											time_frame,
											position_type,
											quantity,
											chart_type=chart_type,
											holding_type=holding_type,
											trading_start_time=trading_start_time,
											trading_stop_time=trading_stop_time)
			except:
				print(traceback.format_exc())
				try:
					url = "https://mailing.streak.solutions/streak_mail/user_feedback/send_mail"
					method = "POST"
					params = {}
					params = {"subject":"Strategy state creation error "+algo_uuid+":"+user_uuid,"reply_to":"support@streak.tech","body_data":str(traceback.format_exc()),"sender": "support@streak.tech"}
					headers = {"content-type":"application/json"}
					response = requests.request(method,url,data=ujson.dumps(params),headers=headers)
					if(response.status_code!=200):
						print('Mail sent for algo state',response.text)
				except:
					print('Mail sent for algo state',traceback.format_exc())

		symbols = {}
		#TODO log UUID

		errors = []
		if take_profit == "":
			errors.append('Take profit not provided')
		elif stop_loss == "":
			errors.append('Stop loss not provided')

		percent_complete = algo_complete_score(equities,entry_logic,algo_state,take_profit,stop_loss,quantity)
		complete = True 
		if percent_complete<95: 
			complete = False 

		if algo_uuid != '':
			# updating existing strategy
			try:
				algorithm_item = models.Algorithm.objects.get(
					algo_uuid = algo_uuid,
					user_uuid = user_uuid
					)
				# action = Action(
				# 	entry_logic = algorithm_item.entry_logic,
				# 	position_type = algorithm_item.position_type,
				# 	exit_logic = algorithm_item.exit_logic
				# 	)
				# print("entry_logic:",entry_logic,"exit_logic",exit_logic)
				action = Action(
					entry_logic = entry_logic,
					position_type = position_type,
					exit_logic = exit_logic
					)
				# temporarily updating in algorithm_item
				# algorithm_item.time_frame = time_frame
				# algorithm_item.cover_proportion = cover_proportion

				# strategy = Strategy(
				# 	strategy_name = algorithm_item.algo_name,
				# 	action = action,
				# 	symbols = algorithm_item.symbols, # symbols which are part of the strategy
				# 	quantity = algorithm_item.quantity,
				# 	take_profit = algorithm_item.take_profit,
				# 	stop_loss = algorithm_item.stop_loss,
				# 	time_frame = algorithm_item.time_frame,
				# 	cover_proportion = algorithm_item.cover_proportion
				# 	)
				strategy = Strategy(
					strategy_name = algo_name,
					action = action,
					symbols = symbols, # symbols which are part of the strategy
					quantity = quantity,
					take_profit = take_profit,
					stop_loss = stop_loss,
					time_frame = time_frame,
					cover_proportion = cover_proportion
					)

				if not action.is_valid() and entry_logic!='':
					errors.append('Action decoding error. \n{}\n{}'.format(action.get_entry_generator_error(),action.get_exit_generator_error()))
					return JsonResponse({'status':False,
										'error':errors,
										'error_msg':','.join(errors)
										})

				algorithm_item.algo_name = algo_name
				algorithm_item.algo_desc = algo_desc

				algorithm_item.user_uuid = user_uuid
				algorithm_item.algo_uuid = algo_uuid
				
				algorithm_item.entry_logic = entry_logic
				algorithm_item.exit_logic = exit_logic

				algorithm_item.time_frame = time_frame
				
				algorithm_item.position_type = action.position_type

				algorithm_item.quantity = strategy.quantity

				algorithm_item.take_profit = float(strategy.take_profit)
				algorithm_item.stop_loss = float(strategy.stop_loss)
				
				algorithm_item.min_candle_freq = int(min_candle_freq)

				if (html_block!=''):
					algorithm_item.html_block = html_block

				algorithm_item.algo_state = algo_state
				algorithm_item.algo_calc = action.get_as_dict()
				algorithm_item.create_plus=create_plus

				# advanced fields
				algorithm_item.holding_type = holding_type				
				algorithm_item.chart_type = chart_type	
				algorithm_item.trade_time_given = trade_time_given
				algorithm_item.trading_start_time = trading_start_time		
				algorithm_item.trading_stop_time = trading_stop_time

				algorithm_item.percent_complete = percent_complete
				algorithm_item.complete = complete
				algorithm_item.daily_strategy_cycle = daily_strategy_cycle
				algorithm_item.max_allocation = max_allocation
				algorithm_item.position_sizing_type = position_sizing_type
				algorithm_item.tpsl_type = tpsl_type
				#-----------------#
				if algorithm_item.status == 1:
					algorithm_item.status = 2 # if algo was live, pause it

				try:
					algorithm_item.save(clean=False)
					# TODO handle deployment live state based on the database
					models.Backtest.objects(algo_uuid=algo_uuid,user_uuid=user_uuid).delete()
					models.BacktestMeta.objects(algo_uuid=algo_uuid,user_uuid=user_uuid).delete()
					request.session['algo_uuid'] = algo_uuid

					# updating top performers
					con = get_redis_connection("default")
					top_performers = con.get('top_performers:'+user_uuid)
					if top_performers:
						top_performers = eval(top_performers)
						new_top_performers = {'backtests':[]}
						for a in top_performers['backtests']:
							if a[0] != algo_uuid:
								new_top_performers['backtests'].append(a)
						new_top_performers['backtests'] = sorted(new_top_performers['backtests'],key=lambda li:li[-1], reverse=True)
						con.set('top_performers:'+user_uuid,ujson.dumps(new_top_performers))

					return JsonResponse({'status':'success','algo_uuid':algo_uuid})

				except Exception:
					# TODO log the error
					if settings.DEBUG:
						print(traceback.format_exc())

					return JsonResponse({'status':'error'})
			except models.Algorithm.DoesNotExist:
				# TODO log errors
				errors.append('Strategy not found')
				return JsonResponse({
									'status':'error',
									'error':errors,
									'error_msg':','.join(errors)
									})

		if algo_uuid =='':
			if ":" in algo_name:
				errors = ["Strategy name has an invalid character, kindly use alphabet and numbers"]
				return JsonResponse({'status':False,
								'error':errors,
								'error_msg':','.join(errors)
								})
			try:
				algorithm_item = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_name = algo_name
					)
				if algorithm_item:
					errors.append('Strategy name already used, please use a different name.')
					return JsonResponse({'status':False,
								'error':errors,
								'error_msg':','.join(errors)
								})
			except:
				pass
		# creating a new action entry
		algo_uuid = str(uuid.uuid4())

		# step 1, create an action
		action = Action(
					entry_logic = entry_logic,
					position_type = position_type,
					exit_logic = exit_logic
						)
		# step 2, validate the action text parsing
		if not action.is_valid() and entry_logic!='':
			# TODO log errors

			errors.append('Action decoding error. \n{}\n{}'.format(action.get_entry_generator_error,action.get_exit_generator_error))

			return JsonResponse({'status':False,
								'error':errors,
								'error_msg':','.join(errors)
								})
		strategy = Strategy(
					strategy_name = algo_name,
					action = action,
					symbols = symbols, # symbols which are part of the strategy
					quantity = quantity,
					take_profit = take_profit,
					stop_loss = stop_loss,
					time_frame = time_frame,
					cover_proportion = cover_proportion
					)

		# print algo_state
		# print type(algo_state)
		print algo_uuid
		algorithm_item = models.Algorithm(
								algo_name = algo_name,
								algo_fist_name = algo_name,
								algo_desc = algo_desc,
								user_uuid = user_uuid,
								algo_uuid = algo_uuid,
								entry_logic = entry_logic,
								exit_logic = exit_logic,
								time_frame = time_frame,
								symbols = symbols, # symbols which are part of the stategy logic
								position_type = action.position_type,
								quantity = quantity,
								take_profit = take_profit,
								stop_loss = stop_loss,
								# advanced fields
								holding_type = holding_type,
								min_candle_freq = min_candle_freq,
								chart_type = chart_type,		
								trade_time_given = trade_time_given,
								trading_start_time = trading_start_time,
								trading_stop_time = trading_stop_time,
								algo_state = algo_state,
								algo_calc = action.get_as_dict(),
								create_plus=create_plus,
								percent_complete = percent_complete, 
								complete = complete,
								daily_strategy_cycle = daily_strategy_cycle,
								max_allocation = max_allocation,
								position_sizing_type = position_sizing_type,
								tpsl_type = tpsl_type,
								#-----------------#
								html_block = html_block
								)

		try:
			algorithm_item.save()
			# this sets the session variable so that on loading of any new page
			request.session['algo_uuid'] = algo_uuid # must be set so that we can identify wether an edit is being made or a new algo is being saved with the same name
			# print algo_uuid
			return JsonResponse({'status':'success','algo_uuid':algo_uuid})

		except:
			print traceback.format_exc()
			try:
				if request.session.get('algo_uuid',None):
					algorithm_item = models.Algorithm.objects(user_uuid=user_uuid,algo_name=algo_name).modify(upsert=True,
										  set__algo_desc=algo_desc,
										  set__entry_logic=entry_logic, 
										  set__exit_logic=exit_logic,
										  set__time_frame = time_frame,
										  set__symbols=symbols, 
										  set__position_type=action.position_type, 
										  set__quantity=quantity, 
										  set__take_profit=take_profit, 
										  set__stop_loss=stop_loss,
										  # advanced fields
										  set__holding_type = holding_type,
										  set__chart_type = chart_type,
										  set__trade_time_given = trade_time_given,
										  set__trading_start_time = trading_start_time,
										  set__trading_stop_time = trading_stop_time,
										  set__algo_state = algo_state,
										  set__algo_calc = action.get_as_dict(),
										  set__create_plus=create_plus,
										  set__percent_complete = percent_complete, 
										  set__complete = complete,
										  set__daily_strategy_cycle = daily_strategy_cycle,
										  set__max_allocation = max_allocation,
										  set__position_sizing_type = position_sizing_type,
										  set__tpsl_type = tpsl_type,
										  #-----------------#
										  set__html_block = html_block)

					algo_uuid = request.session.get('algo_uuid','')
					return JsonResponse({'status':'success','algo_uuid':algo_uuid})
				else:
					errors.append('Strategy name already used, please use a different name.')
					return JsonResponse({'status':'success','error':errors,
									'error_msg':','.join(errors)})
			except:
				# TODO log error
				if settings.DEBUG:
					print traceback.format_exc()
				print "Some error",traceback.format_exc()

				return JsonResponse({'status':False,
									'error':errors,
									'error_msg':','.join([])
									})

	else:
		print "wrong request type"
		return JsonResponse({'status':'error',
									'error_msg':'Unkown method'})

def algorithm_clone(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({'status':'error'})

	if request.method == 'GET':
		algo_uuid = request.GET.get('algo_uuid','')
		if algo_uuid == '':
			return render(request,'algorithm3_.html',
					{'status':'success'
					})

		try:
			algo = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_uuid = algo_uuid,
					status = 0
					)
			algo.algo_name = 'Cloned from '+algo.algo_name
			algo.algo_name = ''
			algo.algo_desc = 'null'
			
			return render(request,'algorithm3_.html',
							{'algo':algo,'cloned':True,
							'status':'success'}
							)

		except models.Algorithm.DoesNotExist:
			# TODO log error
			if settings.DEBUG:
				print traceback.format_exc()
			return redirect('dashboard')
	if request.method == 'POST':
		algo_uuid = request.POST.get('algo_uuid','')

		if algo_uuid == '':
			return JsonResponse({'status':'error','error':'Strategy not present'})

		try:
			algo = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_uuid = algo_uuid
					)
			return JsonResponse({'status':'success'})

		except models.Algorithm.DoesNotExist:
			# TODO log error
			# if settings.DEBUG:
			print traceback.format_exc()
			return JsonResponse({'status':'error','error':'Strategy not present'})
	return JsonResponse({'status':'error','error':'Method not present'})

def algorithm_clone2(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({'status':'error','error_msg':'auth'})

	if request.method == 'POST':
		algo_uuid = request.POST.get('algo_uuid','')
		algo_name = request.POST.get('algo_name','')
		if algo_uuid == '':
			return JsonResponse({'status':'error','error':'Strategy not present'})
		if algo_name.strip(" ./") == '':
			return JsonResponse({'status':'error','error':'Strategy name not provided'})
		try:
			algo = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_uuid = algo_uuid,
					status = 0
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
			
			pb = models.Backtest._get_collection().find({'user_uuid':user_uuid,'algo_uuid':algo_uuid},{'_id':0})
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

			pbm = models.BacktestMeta._get_collection().find({'user_uuid':user_uuid,'algo_uuid':algo_uuid},{'_id':0})
			for b in pbm:
				b["algo_obj"]["algo_name"]=algo_name
				b["algo_obj"]["user_uuid"]=user_uuid
				b["algo_obj"]["algo_uuid"]=cloned_algo_uuid
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
		except:
			print traceback.format_exc()
			return JsonResponse({'status':'error','error':'Unexpected error, please try again in sometime'})
	return JsonResponse({'status':'error','error':'Invalid method'})

def clone_sample(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({'status':'error'})

	if request.method == 'POST':
		algo_uuid = request.POST.get('algo_uuid','')

		if algo_uuid == '':
			return JsonResponse({'status':'error','error':'Strategy not present'})

		try:
			algo = models.Algorithm.objects.get(
					algo_uuid = algo_uuid
					)
			
			cloned_algo_uuid = str(uuid.uuid4())

			algorithm_item = models.Algorithm(
								algo_name = cloned_algo_uuid,
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
								html_block = algo.html_block
								)

			algorithm_item.save()
			return JsonResponse({'algo_uuid':cloned_algo_uuid,
							'status':'success'})

		except models.Algorithm.DoesNotExist:
			# TODO log error
			# if settings.DEBUG:
			print traceback.format_exc()
			return JsonResponse({'status':'error','error':'Strategy not present'})
	return JsonResponse({'status':'error','error':'This sample algo has already been used'})

def clone_sample_backtest(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		if(request.method == "GET"): 
			if(request.GET.get('stock',None)!=None and request.GET.get('algo_uuid',None)!=None): 
				request.session['stock'] = request.GET.getlist('stock') 
				request.session['sample_backtest_algo_uuid'] = request.GET.get('algo_uuid',None) 
				try: 
					conn = get_redis_connection("default") 
					ref_count = conn.get('kite_menu_ref') 
					if not ref_count: 
						ref_count = 1 
					else: 
						ref_count = int(str(ref_count))+1 
					conn.set('kite_menu_ref',ref_count) 
					ref_count = conn.get('kite_menu_ref') 
				except: 
					pass 
				return redirect('broker_login') 
			if(request.GET.get('resp','')=='json' and user_uuid!=''): 
				return JsonResponse({'error_msg':'Session expired, relogin required','status':'error'}) 
		return redirect('home') 

	if request.method == 'GET':
		algo_uuid = request.GET.get('algo_uuid','')

		equities = request.GET.getlist('stock') 
		# request.session['stock'] = request.GET.getlist('stock') 
		# print '............',equities,request.session['stock'],type(request.session['stock']) 
		if algo_uuid!='': 
			try: 
				conn = get_redis_connection("default") 
				ref_count = conn.get('kite_menu_ref') 
				if not ref_count: 
					ref_count = 1 
				else: 
					ref_count = int(str(ref_count))+1 
				conn.set('kite_menu_ref',ref_count) 
				ref_count = conn.get('kite_menu_ref') 
			except: 
				pass 

		if algo_uuid == '':
			if 'stock' in request.session.keys() and 'sample_backtest_algo_uuid' in request.session.keys(): 
				equities = request.session.pop('stock',[]) 
				algo_uuid = request.session.pop('sample_backtest_algo_uuid','') 
				if algo_uuid=='': 
					if(request.GET.get('resp','')=='json' and user_uuid!=''): 
						return JsonResponse({'status':'error','error':'Algo not present'}) 
					return redirect('strategy') 

		try:
			algo = models.Algorithm.objects.get(
					algo_uuid = algo_uuid
					)
			
			cloned_algo_uuid = str(uuid.uuid4())
			algo_name = 'Sample copied on'+datetime.datetime.now().strftime("%d-%h-%y %-H-%-M-%-S")
			algo.algo_state['algo_name']=algo_name
			algorithm_item = models.Algorithm(
								algo_name = algo_name,
								algo_desc = algo.algo_desc,
								user_uuid = user_uuid,
								algo_uuid = cloned_algo_uuid,
								entry_logic = algo.entry_logic,
								exit_logic = algo.exit_logic,
								time_frame = algo.time_frame,
								symbols = algo.symbols, # symbols which are part of the stategy logic
								position_type = algo.position_type,
								quantity = algo.quantity,
								take_profit = algo.take_profit,
								stop_loss = algo.stop_loss,
								# advanced fields
								holding_type = algo.holding_type,
								min_candle_freq = algo.min_candle_freq,
								chart_type = algo.chart_type,		
								trade_time_given = algo.trade_time_given,
								trading_start_time = algo.trading_start_time,
								trading_stop_time = algo.trading_stop_time,
								algo_state = algo.algo_state,
								create_plus = algo.create_plus,
								#-----------------#
								html_block = algo.html_block
								)

			algorithm_item.save()

			algo_uuid = cloned_algo_uuid#algorithm_item['algo_uuid']#.decode('hex')
			# .decode("hex")
			# print algo_uuid
			algo_name = algorithm_item['algo_name']#.decode('hex')
			algo_desc = algorithm_item['algo_desc']#.decode('hex')
			position_type = algorithm_item['position_type']
			if(position_type==1):
				position_type = 'Buy'
			elif(position_type==-1):
				position_type = 'Sell'
			position_qty = algorithm_item['quantity']
			ip_interval = algorithm_item['time_frame']

			# equities = request.GET.getlist('stock')
			equities_d = {}
			for e in equities:
				s = e.split(':')
				if len(s)>1:
					if s[0]=='NFO' or s[0]=='CDS':
						s[0]=s[0]+'-FUT'
					equities_d[s[1]] = s[0]
			#'\x00{\x00"\x00H\x00D\x00F\x00C\x00B\x00A\x00N\x00K\x00"\x00:\x00"\x00N\x00S\x00E\x00"\x00}'
			equities = equities_d
			print equities
			entry_logic = algorithm_item['entry_logic']#request.POST.get('entry_logic')#.decode('hex')
			exit_logic = algorithm_item['exit_logic']#request.POST.get('exit_logic')#.decode('hex')
			take_profit = algorithm_item['take_profit']#request.POST.get('take_profit')
			stop_loss = algorithm_item['stop_loss']#request.POST.get('stop_loss')

			min_candle_freq = algorithm_item['min_candle_freq']
			
			holding_type = algorithm_item['holding_type']
			# advanced parameters
			chart_type = algorithm_item['chart_type']
			trade_time_given = algorithm_item['trade_time_given']
			if(trade_time_given=="True"):
				trade_time_given = "True"
			else:
				trade_time_given = "False"
			trading_start_time = algorithm_item['trading_start_time']
			trading_stop_time = algorithm_item['trading_stop_time']
			create_plus = algorithm_item['create_plus']
			#--------------------#
			# print('trading_start_time',trading_start_time)
			curr_time = datetime.datetime.now()
			date_range_epochs = {
				 'min': 2592000,
				 '3min': 7776000,
				 '5min': 7776000,
				 '10min': 7776000,
				 '15min': 7776000,
				 '30min': 7776000,
				 'hour': 31536000,
				 'day': 157680000
				}
			start_time = datetime.datetime.strftime(curr_time-datetime.timedelta(seconds=date_range_epochs.get(ip_interval.lower(),'hour')),'%d/%m/%Y')
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
			print "-------------------",holding_type
			if (request.GET.get('resp','')=='json' and user_uuid!=''):
				return JsonResponse({'status':'success',
						'user_uuid':user_uuid,
						'algo_uuid':algo_uuid,
						'algo_name':algo_name,
						'algo_desc':algo_desc,
						'position_type':position_type,
						'position_qty':position_qty,
						'quantity':position_qty,
						'equities':equities,
						'entry_logic':entry_logic,
						'exit_logic':exit_logic,
						'take_profit':take_profit,
						'stop_loss':stop_loss,
						# addition data to populate andn default backtest
						'ip_interval':periodicity,
						'time_frame':periodicity,
						'dt_start':start_time,
						'dt_stop':stop_time,
						'holding_type':holding_type,
						'start_time':start_time,
						'stop_time':stop_time,
						'min_candle_freq':min_candle_freq,
						# advanced fields
						'chart_type':chart_type,
						'trade_time_given':trade_time_given,
						'trading_start_time':trading_start_time,
						'trading_stop_time':trading_stop_time,
						'create_plus':create_plus,
						#----------------#
						'bt_url1':settings.BT_URL1,
						'bt_url2':settings.BT_URL2,
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
						'quantity':position_qty,
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
						'create_plus':create_plus,
						#----------------#
						'bt_url1':settings.BT_URL1,
						'bt_url2':settings.BT_URL2,
						'deployed_seg_sym':[],
						'backtest_results':[],
						'deployed_seg_sym_deployment_uuid':{}
						})
			# return JsonResponse({'algo_uuid':cloned_algo_uuid,
			# 				'status':'success'})

		except models.Algorithm.DoesNotExist:
			# TODO log error
			# if settings.DEBUG:
			print traceback.format_exc()
			return JsonResponse({'status':'error','error':'Strategy not present'})
	return JsonResponse({'status':'error','error':'This sample algo has already been used'})

def clone_sample_backtest(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		if(request.method == "GET"): 
			if(request.GET.get('stock',None)!=None and request.GET.get('algo_uuid',None)!=None): 
				request.session['stock'] = request.GET.getlist('stock') 
				request.session['sample_backtest_algo_uuid'] = request.GET.get('algo_uuid',None) 
				try: 
					conn = get_redis_connection("default") 
					ref_count = conn.get('technical_view_menu_ref') 
					if not ref_count: 
						ref_count = 1 
					else: 
						ref_count = int(str(ref_count))+1 
					conn.set('technical_view_menu_ref',ref_count) 
					ref_count = conn.get('technical_view_menu_ref') 
				except: 
					pass 
				return redirect('broker_login') 
			if(request.GET.get('resp','')=='json' and user_uuid!=''): 
				return JsonResponse({'error_msg':'Session expired, relogin required','status':'error'}) 
		return redirect('home') 

	if request.method == 'GET':
		algo_uuid = request.GET.get('algo_uuid','')

		equities = request.GET.getlist('stock') 
		# request.session['stock'] = request.GET.getlist('stock') 
		# print '............',equities,request.session['stock'],type(request.session['stock']) 
		if algo_uuid!='': 
			try: 
				conn = get_redis_connection("default") 
				ref_count = conn.get('technical_view_menu_ref') 
				if not ref_count: 
					ref_count = 1 
				else: 
					ref_count = int(str(ref_count))+1 
				conn.set('technical_view_menu_ref',ref_count) 
				ref_count = conn.get('technical_view_menu_ref') 
			except: 
				pass 

		if algo_uuid == '':
			if 'stock' in request.session.keys() and 'sample_backtest_algo_uuid' in request.session.keys(): 
				equities = request.session.pop('stock',[]) 
				algo_uuid = request.session.pop('sample_backtest_algo_uuid','') 
				if algo_uuid=='': 
					if(request.GET.get('resp','')=='json' and user_uuid!=''): 
						return JsonResponse({'status':'error','error':'Algo not present'}) 
					return redirect('strategy') 

		try:
			algo = models.Algorithm.objects.get(
					algo_uuid = algo_uuid
					)
			
			cloned_algo_uuid = str(uuid.uuid4())
			algo_name = 'Sample copied on '+datetime.datetime.now().strftime("%d-%h-%y %-H-%-M-%-S")
			algo.algo_state['algo_name']=algo_name
			algorithm_item = models.Algorithm(
								algo_name = algo_name,
								algo_desc = algo.algo_desc,
								user_uuid = user_uuid,
								algo_uuid = cloned_algo_uuid,
								entry_logic = algo.entry_logic,
								exit_logic = algo.exit_logic,
								time_frame = algo.time_frame,
								symbols = algo.symbols, # symbols which are part of the stategy logic
								position_type = algo.position_type,
								quantity = algo.quantity,
								take_profit = algo.take_profit,
								stop_loss = algo.stop_loss,
								# advanced fields
								holding_type = algo.holding_type,
								min_candle_freq = algo.min_candle_freq,
								chart_type = algo.chart_type,		
								trade_time_given = algo.trade_time_given,
								trading_start_time = algo.trading_start_time,
								trading_stop_time = algo.trading_stop_time,
								algo_state = algo.algo_state,
								create_plus = algo.create_plus,
								#-----------------#
								html_block = algo.html_block
								)

			algorithm_item.save()

			algo_uuid = cloned_algo_uuid#algorithm_item['algo_uuid']#.decode('hex')
			# .decode("hex")
			# print algo_uuid
			algo_name = algorithm_item['algo_name']#.decode('hex')
			algo_desc = algorithm_item['algo_desc']#.decode('hex')
			position_type = algorithm_item['position_type']
			if(position_type==1):
				position_type = 'Buy'
			elif(position_type==-1):
				position_type = 'Sell'
			position_qty = algorithm_item['quantity']
			ip_interval = algorithm_item['time_frame']

			# equities = request.GET.getlist('stock')
			equities_d = {}
			for e in equities:
				s = e.split(':')
				if len(s)>1:
					if s[0]=='NFO' or s[0]=='CDS': 
						s[0]=s[0]+'-FUT' 
					equities_d[s[1]] = s[0]
			#'\x00{\x00"\x00H\x00D\x00F\x00C\x00B\x00A\x00N\x00K\x00"\x00:\x00"\x00N\x00S\x00E\x00"\x00}'
			equities = equities_d
			print equities
			entry_logic = algorithm_item['entry_logic']#request.POST.get('entry_logic')#.decode('hex')
			exit_logic = algorithm_item['exit_logic']#request.POST.get('exit_logic')#.decode('hex')
			take_profit = algorithm_item['take_profit']#request.POST.get('take_profit')
			stop_loss = algorithm_item['stop_loss']#request.POST.get('stop_loss')

			min_candle_freq = algorithm_item['min_candle_freq']
			
			holding_type = algorithm_item['holding_type']
			# advanced parameters
			chart_type = algorithm_item['chart_type']
			trade_time_given = algorithm_item['trade_time_given']
			if(trade_time_given=="True"):
				trade_time_given = "True"
			else:
				trade_time_given = "False"
			trading_start_time = algorithm_item['trading_start_time']
			trading_stop_time = algorithm_item['trading_stop_time']
			create_plus = algorithm_item['create_plus']
			#--------------------#
			# print('trading_start_time',trading_start_time)
			curr_time = datetime.datetime.now()
			date_range_epochs = {
				 'min': 1296000,
				 '3min': 2592000,
				 '5min': 2592000,
				 '10min': 2592000,
				 '15min': 2592000,
				 '30min': 2592000,
				 'hour': 7776000,
				 'day': 31536000
				}
			start_time = datetime.datetime.strftime(curr_time-datetime.timedelta(seconds=date_range_epochs.get(ip_interval.lower(),'hour')),'%d/%m/%Y')
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
			# holding_type_temp = 'MIS'
			# if(ip_interval=='day'):
			holding_type_temp = 'CNC'
			holding_type = 'CNC'
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
			print "-------------------",holding_type
			# if (request.GET.get('resp','')=='json' and user_uuid!=''):
			return JsonResponse({'status':'success',
					'user_uuid':user_uuid,
					'algo_uuid':algo_uuid,
					'algo_name':algo_name,
					'algo_desc':algo_desc,
					'position_type':position_type,
					'position_qty':position_qty,
					'quantity':position_qty,
					'equities':equities,
					'entry_logic':entry_logic,
					'exit_logic':exit_logic,
					'take_profit':take_profit,
					'stop_loss':stop_loss,
					# addition data to populate andn default backtest
					'ip_interval':periodicity,
					'time_frame':periodicity,
					'dt_start':start_time,
					'dt_stop':stop_time,
					'holding_type':holding_type,
					'start_time':start_time,
					'stop_time':stop_time,
					'min_candle_freq':min_candle_freq,
					# advanced fields
					'chart_type':chart_type,
					'trade_time_given':trade_time_given,
					'trading_start_time':trading_start_time,
					'trading_stop_time':trading_stop_time,
					'create_plus':create_plus,
					#----------------#
					'bt_url1':settings.BT_URL1,
					'bt_url2':settings.BT_URL2,
					'deployed_seg_sym':[],
					'backtest_results':[],
					'deployed_seg_sym_deployment_uuid':{}
					})
			# return render(request,'multiple_backtests.html',
			# 			{'status':'success',
			# 			'user_uuid':user_uuid,
			# 			'algo_uuid':algo_uuid,
			# 			'algo_name':algo_name,
			# 			'algo_desc':algo_desc,
			# 			'position_type':position_type,
			# 			'position_qty':position_qty,
			# 			'equities':equities,
			# 			'entry_logic':entry_logic,
			# 			'exit_logic':exit_logic,
			# 			'take_profit':take_profit,
			# 			'stop_loss':stop_loss,
			# 			# addition data to populate andn default backtest
			# 			'ip_interval':periodicity,
			# 			'holding_type':holding_type,
			# 			'start_time':start_time,
			# 			'stop_time':stop_time,
			# 			'min_candle_freq':min_candle_freq,
			# 			# advanced fields
			# 			'chart_type':chart_type,
			# 			'trade_time_given':trade_time_given,
			# 			'trading_start_time':trading_start_time,
			# 			'trading_stop_time':trading_stop_time,
			# 			#----------------#
			# 			'bt_url1':settings.BT_URL1,
			# 			'bt_url2':settings.BT_URL2
			# 			})
			# return JsonResponse({'algo_uuid':cloned_algo_uuid,
			# 				'status':'success'})

		except models.Algorithm.DoesNotExist:
			# TODO log error
			# if settings.DEBUG:
			print traceback.format_exc()
			return JsonResponse({'status':'error','error':'Algo not present','error_msg':'Algo not present'})
	return JsonResponse({'status':'error','error':'This sample algo has already been used','error_msg':'This sample algo has already been used'})

def algorithm_clone_ajax(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({'status':'error'})

	if request.method == 'POST':
		algo_uuid = request.POST.get('algo_uuid','')

		if algo_uuid == '':
			return JsonResponse({'status':'error','error':'Strategy not present'})

		try:
			algo = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_uuid = algo_uuid
					)
			
			cloned_algo_uuid = str(uuid.uuid4())

			algorithm_item = models.Algorithm(
								algo_name = 'Cloned from '+algo.algo_name,
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
								algo_state = algo.algo_state,
								html_block = algo.html_block
								)

			algorithm_item.save()
			return JsonResponse({'algo_uuid':cloned_algo_uuid,
							'status':'success'})

		except models.Algorithm.DoesNotExist:
			# TODO log error
			# if settings.DEBUG:
			print traceback.format_exc()
			return JsonResponse({'status':'error','error':'Strategy not present'})
	return JsonResponse({'status':'error','error':'Method not present'})
def algorithm_remove(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({'status':'error'})

	if request.method == 'POST':
		algo_uuid = request.POST.get('algo_uuid','')

		if algo_uuid == '':
			return JsonResponse({'status':'error','error':'Strategy not present'})
		try:
			algo = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_uuid = algo_uuid
					)
			algo.delete()
			# updating top performers
			con = get_redis_connection("default")
			top_performers = con.get('top_performers:'+user_uuid)
			if top_performers:
				top_performers = eval(top_performers)
				new_top_performers = {'backtests':[]}
				for a in top_performers['backtests']:
					if a[0] != algo_uuid:
						new_top_performers['backtests'].append(a)
				new_top_performers['backtests'] = sorted(new_top_performers['backtests'],key=lambda li:li[-1], reverse=True)
				con.set('top_performers:'+user_uuid,ujson.dumps(new_top_performers))

			try:
				headers = {"Content-Type":"application/json"}
				params = {"id":algo_uuid}
				response = requests.delete("https://s.streak.tech/algorithms/",data=ujson.dumps(params),headers=headers)
				if response.status_code==500:
					url = "https://mailing.streak.solutions/streak_mail/user_feedback/send_mail"
					method = "POST"
					params = {}
					params = {"subject":"Strategy state creation error "+algo_uuid+":"+user_uuid,"reply_to":"support@streak.tech","body_data":"Error removing algo from elastic index algo_uuid: "+algo_uuid,"sender": "support@streak.tech"}
					headers = {"content-type":"application/json"}
					response = requests.request(method,url,data=ujson.dumps(params),headers=headers)
					if(response.status_code!=200):
						print('Mail sent for algo state',response.text)
			except:
				print traceback.format_exc()
				pass
			return JsonResponse({'status':'success'})

		except models.Algorithm.DoesNotExist:
			# TODO log error
			# if settings.DEBUG:
			print traceback.format_exc()
			return JsonResponse({'status':'error','error':'Strategy not present'})

	return JsonResponse({'status':'error'})

def clone_shared(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		print("aaaaaaaaaa")
		return JsonResponse({"status":"error","error_msg":"auth"})

	if request.method=='POST':
		backtest_share_uuid = request.POST.get('backtest_share_uuid','')
		# print("aaaaaaaaaa")
		try:
			backtest_item = models.ShareableBacktest.objects(
						backtest_share_uuid = backtest_share_uuid
						)
			assert len(backtest_item)==1
			if backtest_item[0].public=="":
				return JsonResponse({'status':'error','error':'Strategy is not public'})

			algo_uuid = backtest_item[0].algo_uuid
			if algo_uuid == '':
				return JsonResponse({'status':'error','error':'Strategy not present'})

			algo = models.Algorithm.objects.get(
					algo_uuid = algo_uuid
					)
			
			cloned_algo_uuid = str(uuid.uuid4())
			
			algorithm_item = models.Algorithm(
								algo_name = cloned_algo_uuid,
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
								#-----------------#
								html_block = algo.html_block
								)

			algorithm_item.save()
			return JsonResponse({'algo_uuid':cloned_algo_uuid,
							'status':'success'})
		except:
			print traceback.format_exc()
			return JsonResponse({'status':'error','error':'Strategy not present'})
	return JsonResponse({'status':'error','error':'Invalid method'})