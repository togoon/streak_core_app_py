from django.conf import settings
from django.shortcuts import redirect,render
from django.middleware import csrf
from django_redis import get_redis_connection
from django.http import JsonResponse
import pickle
import itertools
import json,csv
from coreapp import models
import hashlib
import requests,urllib
import traceback
import uuid
import datetime
import random
import base64
from mongoengine import DoesNotExist
import ams_helper
import ujson


def scan_redis_key(conn,regx,key_list=False):
	cur = '0'  # set initial cursor to 0
	keys_count = 0
	keys_list = []
	key = None
	while cur:
		cur, keys = conn.scan(cur, match=regx)
		# print("Iteration results:", keys)
		if(len(keys)>0):
			keys_count += 1
			keys_list = keys_list + keys
			if not key_list:
				break

	if keys_count>0 and not key_list:
		key = keys_list[0].decode("utf-8")
	if key_list:
		return keys_list
	return key

def place_order_crypto(request):
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
		exchange = request.POST.get('exchange','')
		symbol = urllib.unquote(unicode(request.POST.get('symbol','')).encode('utf-8'))
		segment = request.POST.get('segment','')
		transaction_type = request.POST.get('transaction_type','')
		order_type = request.POST.get('order_type','')
		quantity = request.POST.get('quantity',"0.0")
		product = request.POST.get('product','')
		trade_price = request.POST.get('price',"0.0")
		account_name = request.POST.get('account_name','')
		validity = request.POST.get('validity','GTC')
		tpsl_key = request.POST.get('tpsl_key','')
		broker = request.POST.get('broker','')

		if notification_uuid == '':
			return JsonResponse({"status":"error",'error-type':'Unkown notif'})
		
		conn = get_redis_connection("default")
		
		try:
			notifs = conn.get('today_notification:'+user_uuid)
			notifs = ujson.loads(notifs)
			notif_used = notifs['used'].get(notification_uuid,0)
			if notif_used:
				return JsonResponse({"status":"error","error_msg":"Notification used"})
		except:
			print traceback.format_exc()

		key_prefix = ':'.join(['deployed',user_uuid,'*',deployment_uuid])
		deployed_keys = scan_redis_key(conn,key_prefix)
		# print 'zzzzzzzzzzzzzzzzzzzzzz11111111111',key_prefix
		if(deployed_keys is None):
			print 'deployment_uuid not present'
			return JsonResponse({"status":"success",'error-type':'Algo not live','error_msg':'Algo not live'})

		if order_type=='undefined':
			dep_obj = ujson.loads(conn.get(deployed_keys))
			order_type = dep_obj.get('order_type','MARKET')

		if order_type == 'MARKET':
			t_price = conn.get('ltp_'+segment+'_'+symbol)
			if t_price:
				trade_price = t_price
				
		res = ams_helper.create_order(user_uuid,exchange,account_name,symbol,transaction_type,order_type,quantity,trade_price)
		if res.get('status_code',200)!=200:
			return JsonResponse({"status":"error","error_msg":res['data']}) 
		else:
			broker_order = models.BrokerOrder(user_uuid=user_uuid,
				algo_uuid=algo_uuid,
				algo_name=algo_name,
				deployment_uuid=deployment_uuid,
				order_id=res['data']['order_id'],
				status=res['data']['status'],
				order_payload = {
					"api_key":'',
					"access_token":'',
					"tradingsymbol":symbol,
					"segment":segment,
					"exchange":exchange,
					"account_name":account_name,
					"transaction_type":transaction_type,
					"order_type":order_type,
					"variety":'REGULAR',
					"quantity":quantity,
					"trigger_price":trade_price,
					"product":product,
					"validity":validity,
					"order_placement":"manual"
				}
			)
			broker_order.save()

			pipeline = conn.pipeline()

			redis_key = scan_redis_key(conn,'deployed:'+user_uuid+':*:'+deployment_uuid)

			notifs['used'][notification_uuid]=1 # mark notitification as used(actioned upon)

			conn.set('today_notification:'+user_uuid,ujson.dumps(notifs))
			ex_time = int((datetime.datetime.now().replace(hour=3,minute=0,second=0)+datetime.timedelta(days=1)).strftime('%s')) - int(datetime.datetime.now().strftime('%s'))
			conn.expire('today_notification:'+user_uuid,ex_time)
			
			if redis_key:
				r = conn.get(redis_key)
				# ttl = con.ttl(redis_key)
				try:
					if r:
						r = json.loads(r)
						if(r['algo_obj']['action_type']!=notification['transaction_type']):
							r['SL_placed']=1
							r['SL_order_id']=res['data']['order_id']
							r['SL_order_api_key']=''
							r['SL_order_access_token']=''
							# pipeline.set(redis_key,json.dumps(r))
							# if(int(ttl) > -1):
							# 	pipeline.expire(redis_key,ttl)
						# r['frequency_utilized']=r.get('frequency_utilized',0)+1
				except:
					print traceback.format_exc()
					# r = {}
					pass
				# print r
				# pipeline.set(redis_key,r)
				# pipeline.expire(redis_key,1)
				# pipeline.publish(settings.ENV+'-deployment_channel','DEL:'+redis_key)

			curr_time = datetime.datetime.now()
			
			order_id = res['data']['order_id']
			order_status = res['data']['status']

			notification_msg = "You ordered"
			notification_data = {'notification-type':'order-placement','notification_msg':notification_msg,'action_type':transaction_type,'transaction_type':transaction_type,
				'trigger_time':int(curr_time.strftime('%s')),
				'trigger_price':trade_price,
				'segment':segment,'symbol':symbol,
				'seg':segment,'sym':symbol,'quantity':quantity,'broker':broker,'notification_time':curr_time.isoformat(),
				'user_uuid':user_uuid,
				'algo_uuid':algo_uuid,
				'algo_name':algo_name,
				'deployment_uuid':deployment_uuid,
				'account_name':account_name,
				'order_type':order_type,
				'order_id':order_id,
				'order_status':order_status,
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
			notification_data = {'notification-type':'order-placement','notification_msg':notification_msg,'action_type':transaction_type,'transaction_type':transaction_type,
				'trigger_time':int(curr_time.strftime('%s')),
				'trigger_price':trade_price,
				'segment':segment,'symbol':symbol,
				'seg':segment,'sym':symbol,'quantity':quantity,'broker':broker,'notification_time':curr_time.isoformat(),
				'user_uuid':user_uuid,
				'algo_uuid':algo_uuid,
				'algo_name':algo_name,
				'deployment_uuid':deployment_uuid,
				'account_name':account_name,
				'order_type':order_type,
				'order_id':order_id,
				'order_status':order_status,
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

			return JsonResponse({"status":"success","data":res['data']}) 
	return JsonResponse({"status":"error","error_msg":"method"}) 

def place_order_crypto_tpsl(request):
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
		exchange = request.POST.get('exchange','')
		symbol = urllib.unquote(unicode(request.POST.get('symbol','')).encode('utf-8'))
		segment = request.POST.get('segment','')
		transaction_type = request.POST.get('transaction_type','')
		order_type = request.POST.get('order_type','')
		quantity = request.POST.get('quantity',"0.0")
		product = request.POST.get('product','')
		trade_price = request.POST.get('price',"0.0")
		account_name = request.POST.get('account_name','')
		validity = request.POST.get('validity','GTC')
		tpsl_key = request.POST.get('tpsl_key','')
		broker = request.POST.get('broker','')

		if notification_uuid == '':
			return JsonResponse({"status":"error",'error-type':'Unkown notif'})
		
		conn = get_redis_connection("default")
		
		try:
			notifs = conn.get('today_notification:'+user_uuid)
			notifs = ujson.loads(notifs)
			notif_used = notifs['used'].get(notification_uuid,0)
			if notif_used:
				return JsonResponse({"status":"error","error_msg":"Notification used"})
		except:
			print traceback.format_exc()

		key_prefix = ':'.join(['deployed',user_uuid,'*',deployment_uuid])
		deployed_keys = scan_redis_key(conn,key_prefix)
		# print 'zzzzzzzzzzzzzzzzzzzzzz11111111111',key_prefix
		if(deployed_keys is None):
			print 'deployment_uuid not present'
			return JsonResponse({"status":"success",'error-type':'Algo not live','error_msg':'Algo not live'})

		if order_type=='undefined':
			dep_obj = ujson.loads(conn.get(deployed_keys))
			order_type = dep_obj.get('order_type','MARKET')

		if order_type == 'MARKET':
			t_price = conn.get('ltp_'+segment+'_'+symbol)
			if t_price:
				trade_price = t_price
				
		res = ams_helper.create_order(user_uuid,exchange,account_name,symbol,transaction_type,order_type,quantity,trade_price)
		if res.get('status_code',200)!=200:
			return JsonResponse({"status":"error","error_msg":res['data']}) 
		else:
			broker_order = models.BrokerOrder(user_uuid=user_uuid,
				algo_uuid=algo_uuid,
				algo_name=algo_name,
				deployment_uuid=deployment_uuid,
				order_id=res['data']['order_id'],
				status=res['data']['status'],
				order_payload = {
					"api_key":'',
					"access_token":'',
					"tradingsymbol":symbol,
					"segment":segment,
					"exchange":exchange,
					"account_name":account_name,
					"transaction_type":transaction_type,
					"order_type":order_type,
					"variety":'REGULAR',
					"quantity":quantity,
					"trigger_price":trade_price,
					"product":product,
					"validity":validity,
					"order_placement":"manual"
				}
			)
			broker_order.save()

			pipeline = conn.pipeline()

			redis_key = scan_redis_key(conn,'deployed:'+user_uuid+':*:'+deployment_uuid)

			notifs['used'][notification_uuid]=1 # mark notitification as used(actioned upon)

			conn.set('today_notification:'+user_uuid,ujson.dumps(notifs))
			ex_time = int((datetime.datetime.now().replace(hour=3,minute=0,second=0)+datetime.timedelta(days=1)).strftime('%s')) - int(datetime.datetime.now().strftime('%s'))
			conn.expire('today_notification:'+user_uuid,ex_time)
			
			if redis_key:
				r = conn.get(redis_key)
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
			
			order_id = res['data']['order_id']
			order_status = res['data']['status']

			notification_msg = "You ordered"
			notification_data = {'notification-type':'order-placement','notification_msg':notification_msg,'action_type':transaction_type,'transaction_type':transaction_type,
				'trigger_time':int(curr_time.strftime('%s')),
				'trigger_price':trade_price,
				'segment':segment,'symbol':symbol,
				'seg':segment,'sym':symbol,'quantity':quantity,'broker':broker,'notification_time':curr_time.isoformat(),
				'user_uuid':user_uuid,
				'algo_uuid':algo_uuid,
				'algo_name':algo_name,
				'deployment_uuid':deployment_uuid,
				'account_name':account_name,
				'order_type':order_type,
				'order_id':order_id,
				'order_status':order_status,
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
			notification_data = {'notification-type':'order-placement','notification_msg':notification_msg,'action_type':transaction_type,'transaction_type':transaction_type,
				'trigger_time':int(curr_time.strftime('%s')),
				'trigger_price':trade_price,
				'segment':segment,'symbol':symbol,
				'seg':segment,'sym':symbol,'quantity':quantity,'broker':broker,'notification_time':curr_time.isoformat(),
				'user_uuid':user_uuid,
				'algo_uuid':algo_uuid,
				'algo_name':algo_name,
				'deployment_uuid':deployment_uuid,
				'account_name':account_name,
				'order_type':order_type,
				'order_id':order_id,
				'order_status':order_status,
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

			return JsonResponse({"status":"success","data":res['data']})

def place_order_crypto_direct(request):
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
		exchange = request.POST.get('exchange','')
		symbol = urllib.unquote(unicode(request.POST.get('symbol','')).encode('utf-8'))
		segment = request.POST.get('segment','')
		transaction_type = request.POST.get('transaction_type','')
		order_type = request.POST.get('order_type','')
		quantity = request.POST.get('quantity',"0.0")
		product = request.POST.get('product','')
		trade_price = request.POST.get('price',"0.0")
		account_name = request.POST.get('account_name','')
		validity = request.POST.get('validity','GTC')
		tpsl_key = request.POST.get('tpsl_key','')
		broker = request.POST.get('broker','')

		conn = get_redis_connection("default")
		if order_type=='undefined':
			dep_obj = ujson.loads(conn.get(deployed_keys))
			order_type = dep_obj.get('order_type','MARKET')

		if order_type == 'MARKET':
			t_price = conn.get('ltp_'+segment+'_'+symbol)
			if t_price:
				trade_price = t_price
				
		res = ams_helper.create_order(user_uuid,exchange,account_name,symbol,transaction_type,order_type,quantity,trade_price)
		if res.get('status_code',200)!=200:
			return JsonResponse({"status":"error","error_msg":res['data']}) 
		else:
			broker_order = models.BrokerOrder(user_uuid=user_uuid,
				algo_uuid=algo_uuid,
				algo_name=algo_name,
				deployment_uuid='DIRECT_'+exchange.lower()+'_'+symbol.lower(),
				order_id=res['data']['order_id'],
				status=res['data']['status'],
				order_payload = {
					"api_key":'',
					"access_token":'',
					"tradingsymbol":symbol,
					"segment":segment,
					"exchange":exchange,
					"account_name":account_name,
					"transaction_type":transaction_type,
					"order_type":order_type,
					"variety":'REGULAR',
					"quantity":quantity,
					"trigger_price":trade_price,
					"product":product,
					"validity":validity,
					"order_placement":"manual"
				}
			)
			broker_order.save()

			return JsonResponse({"status":"success","data":res['data']}) 
	return JsonResponse({"status":"error","error_msg":"method"}) 

def place_order_crypto_(request):
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
			trade_price = float(request.POST.get('trade_price',0))
			account_name = request.POST.get('account_name','')

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
				return JsonResponse({"status":"success",'error-type':'Algo not live'})

			if account_name==None or account_name=='':
				# if account name is not present in the algo object or is blank, notification is for paper trade
				return JsonResponse({"status":"error",'error-type':'Account name not present'})
			# setting up crypto related stuff
			exchange_obj = None
			try:
				exchange_obj = getattr(ccxt,segment.lower())
				echange_markets = exchange_obj.load_markets()
				if(symbol.endswith('/USD') and echange_markets.get('BTC/USD',None)==None):
					symbol.replace('/USD','/USDT')
			except:
				return JsonResponse({"status":"error",'error-type':'Unsupported exchange'})
			if exchange_obj == None:
				return JsonResponse({"status":"error",'error-type':'Unsupported exchange'})

			exchange_account = None
			try:
				exchange_account = db.ExchangeAccount.objects.get(user_uuid=user_uuid,account_name=account_name)
			except:
				return JsonResponse({"status":"error",'error-type':'Account not found'})

			if exchange_account:
				api_key = exchange_account.api_key 
				api_secret = exchange_account.api_secret 
				exchange_obj.apiKey = api_key
				exchange_obj.secret = api_secret

				try:
					if trade_price == 0:
						if not exchange.has['createMarketOrder']:
							exchange_obj.getattr('create_market_'+transaction_type.lower()+'_order')(symbol, quantity, {})
					else:
						exchange_obj.getattr('create_limit_'+transaction_type.lower()+'_order')(symbol, quantity,trade_price, {})
				except ccxt.base.errors.NotSupported:
					return JsonResponse({"status":"error",'error-type':'Unsupported order'})
				except ccxt.base.errors.AuthenticationError:
					return JsonResponse({"status":"error",'error-type':'Incorrect API or permissions'})
				except ccxt.base.errors.InsufficientFunds:
					return JsonResponse({"status":"error",'error-type':'Insufficient funds'})
				except ccxt.base.errors.InvalidAddress:
					return JsonResponse({"status":"error",'error-type':'Insufficient funds'})
				except ccxt.base.errors.OrderNotFound:
					return JsonResponse({"status":"error",'error-type':'Insufficient funds'})
				except ccxt.base.errors.InvalidOrder:
					return JsonResponse({"status":"error",'error-type':'Invalid order'})
				except ccxt.base.errors.ExchangeNotAvailable:
					return JsonResponse({"status":"error",'error-type':'Exchange error'})

			# access_token = request.session.get('access_token','')
			# public_token = request.session.get('public_token','')
			# user_broker_id = request.session.get('user_broker_id','')
			# broker = 'zerodha'

			# if access_token=='' or public_token=='' or user_broker_id=='':
			# 	print 'probably kite login popup'
			# 	return JsonResponse({"status":"error",'error-type':'noauth'})

			# payload = {
			#   "api_key":settings.KITE_API_KEY,
			#   "access_token":access_token,
			#   "tradingsymbol":symbol,
			#   "exchange":exchange,
			#   "transaction_type":transaction_type,
			#   "order_type":order_type,
			#   "quantity":quantity,
			#   "product":product,
			#   "validity":validity
			# }

			# # print payload
			# headers = {}
			# if settings.KITE_HEADER == True:
			# 	headers = {"X-Kite-Version":"3"}
			# 	auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
			# 	headers["Authorization"] = "token {}".format(auth_header)
			# response = requests.request("POST","https://api.kite.trade/orders/regular", data=payload,headers=headers)
			# if response.status_code == 200:
			# 	response_json = json.loads(response.text)
			# 	if response_json['status']=="success":
			# 		try:
						#update holdings for algorithm using webhook 
						# holding = HoldingsForAlgorithm.objects.get(user_uuid=user_uuid,deployment_uuid=deployment_uuid)
						# holding.position[segment+'_'+symbol]['qty']=
			broker_order = models.BrokerOrder(user_uuid=user_uuid,
				algo_uuid=algo_uuid,
				algo_name=algo_name,
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
					"trade_price":trade_price
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
				'seg':segment,'sym':symbol,'quantity':quantity,'broker':segment,'notification_time':curr_time.isoformat(),
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
			# 			return JsonResponse({'status':'success'})
			# 		except:
			# 			print traceback.format_exc()
			# 			return JsonResponse({'status':'error'})
			# 	else:
			# 		return JsonResponse({'status':'error','order_response':response_json,'response_code':response.status_code})
			# else:
			# 	return JsonResponse({'status':'error','response_code':response.status_code,'error-type':'Session expired, re-login required','error_msg':'Session expired, re-login required'})
			return JsonResponse({'status':'success'})
		except:
			print traceback.format_exc()

	return JsonResponse({'status':'error'})
