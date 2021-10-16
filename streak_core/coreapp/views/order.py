from django.shortcuts import render,redirect
from django.http import JsonResponse
# import haslib
import random
import math
import uuid
import datetime
import traceback
from django.conf import settings
from django_redis import get_redis_connection
from coreapp import models
import string
import json
import requests
import ujson
import urllib
import utility
from coreapp.views.utility import get_deployment_keys
from coreapp.views.ams_helper import *
from mongoengine import DoesNotExist

def fetch_order_log_(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error"})

	if request.method=="GET":
			
		status = int(request.GET.get('status',0))
		page_limit = int(request.GET.get('limit',50))
		paginate = int(request.GET.get('page',0))

		if 'deployment_uuid' in request.GET.keys():
			deployment_uuid = request.GET.get('deployment_uuid','')
			order_logs = models.OrderLog.objects(user_uuid=user_uuid,deployment_uuid=deployment_uuid)
			orders_log_json = json.loads(order_logs.to_json())
			for i in range(len(order_logs)):
				# orders_log_json[i].created_at = 
				orders_log_json[i]['created_at'] = order_logs[i].created_at.isoformat()
			return JsonResponse({'order_logs':list(reversed(orders_log_json))})

		fetch_all_logs_query = """
			function(){
			var results = [];
			results = db[collection].aggregate([
				{
				$lookup:{
					from:"order_log",
					localField:"deployment_uuid",
					foreignField:"deployment_uuid",
					as:"logs"
					}
				},
				{
				$lookup:{
					from:"algorithm_performance",
					localField:"deployment_uuid",
					foreignField:"deployment_uuid",
					as:"performance"
					}
				},
				{
				$match:{
					user_uuid : "%s",
					status:%d,
					"expiration_time":{"$gte":ISODate("%s")}
					}
				},
				{$sort:{"logs":1,"updated_at":1,"performance.updated_at":1}},
				//{
				//$limit : %d
				//}
				]);
				return results;
				}
			"""%(user_uuid,int(status),datetime.datetime.now().isoformat(),int(page_limit))

		if status != 0:
			status_list = [status]
			if status == -1:
				# status_list.append(2)
				status_list.append(-2)
				status_list.append(-3)

			fetch_all_logs_query = """
			function(){
			var results = [];
			results = db[collection].aggregate([
				{
				$lookup:{
					from:"order_log",
					localField:"deployment_uuid",
					foreignField:"deployment_uuid",
					as:"logs"
					}
				},
				{
				$lookup:{
					from:"algorithm_performance",
					localField:"deployment_uuid",
					foreignField:"deployment_uuid",
					as:"performance"
					}
				},
				{
				$match:{
					user_uuid : "%s",
					status:{ $in: %s},
					"deployment_time":{"$gte":ISODate("%s")}
					}
				},
				{$sort:{"logs":1,"updated_at":1,"performance.updated_at":1}},
				//{
				//$limit : %d
				//}
				]);
				return results;
				}
			"""%(user_uuid,status_list,(datetime.datetime.now()-datetime.timedelta(days=2)).isoformat(),int(page_limit))

		order_logs = models.DeployedAlgorithm.objects.exec_js(fetch_all_logs_query)

		grouped_orders = {}
		grouped_orders = order_logs['_batch'][paginate*int(page_limit):int(page_limit)*(paginate+1)]
		for i in range(len(grouped_orders)):
			grouped_orders[i]['logs'] = list(reversed(grouped_orders[i]['logs']))
			for j in range(len(grouped_orders[i]['logs'])):
				# print grouped_orders[i]['logs'][j]['created_at']
				grouped_orders[i]['logs'][j]['created_at'] = grouped_orders[i]['logs'][j]['created_at'].isoformat()
				grouped_orders[i]['logs'][j]['updated_at'] = ''#grouped_orders[i]['logs'][j]['updated_at'].isoformat()
				grouped_orders[i]['logs'][j]['_id'] = str(grouped_orders[i]['logs'][j]['_id'])
			grouped_orders[i]['_id']=str(grouped_orders[i]['_id'])
			grouped_orders[i]['created_at']=grouped_orders[i]['created_at'].isoformat()
			grouped_orders[i]['updated_at']=grouped_orders[i]['updated_at'].isoformat()
		# print grouped_orders
		return JsonResponse({'grouped_orders':grouped_orders,'pages':int(len(order_logs['_batch'])/page_limit)})
	return JsonResponse({"status":"error"})

def fetch_order_log__(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error"})

	if request.method=="GET":
			
		status = int(request.GET.get('status',0))
		page_limit = int(request.GET.get('limit',50))
		paginate = int(request.GET.get('page',0))

		if 'deployment_uuid' in request.GET.keys():
			deployment_uuid = request.GET.get('deployment_uuid','')
			order_logs = models.OrderLog.objects(user_uuid=user_uuid,deployment_uuid=deployment_uuid)
			orders_log_json = json.loads(order_logs.to_json())
			for i in range(len(order_logs)):
				# orders_log_json[i].created_at = 
				orders_log_json[i]['created_at'] = order_logs[i].created_at.isoformat()
			return JsonResponse({'order_logs':list(reversed(orders_log_json))})

		fetch_all_logs_query = """
			function(){
			var results = [];
			results = db[collection].aggregate([
				{
				$lookup:{
					from:"order_log",
					localField:"deployment_uuid",
					foreignField:"deployment_uuid",
					as:"logs"
					}
				},
				{
				$lookup:{
					from:"algorithm_performance",
					localField:"deployment_uuid",
					foreignField:"deployment_uuid",
					as:"performance"
					}
				},
				{
				$match:{
					user_uuid : "%s",
					status:%d,
					"expiration_time":{"$gte":ISODate("%s")}
					}
				},
				{$sort:{"logs":1,"updated_at":1,"performance.updated_at":1}},
				//{
				//$limit : %d
				//}
				]);
				return results;
				}
			"""%(user_uuid,int(status),datetime.datetime.now().isoformat(),int(page_limit))

		fetch_all_logs_query_dict =[
				{
				"$lookup":{
					"from":"order_log",
					"localField":"deployment_uuid",
					"foreignField":"deployment_uuid",
					"as":"logs"
					}
				},
				{
				"$lookup":{
					"from":"algorithm_performance",
					"localField":"deployment_uuid",
					"foreignField":"deployment_uuid",
					"as":"performance"
					}
				},
				{
				"$match":{
					"user_uuid" : user_uuid,
					"status":int(status),
					"expiration_time":{"$gte":datetime.datetime.now()}
					}
				},
				{
					"$sort":{"logs":-1,"updated_at":-1,"performance.updated_at":-1}
				}
			]

		if status != 0:
			status_list = [status]
			if status == -1:
				# status_list.append(2)
				status_list.append(-2)
				status_list.append(-3)

			fetch_all_logs_query = """
			function(){
			var results = [];
			results = db[collection].aggregate([
				{
				$lookup:{
					from:"order_log",
					localField:"deployment_uuid",
					foreignField:"deployment_uuid",
					as:"logs"
					}
				},
				{
				$lookup:{
					from:"algorithm_performance",
					localField:"deployment_uuid",
					foreignField:"deployment_uuid",
					as:"performance"
					}
				},
				{
				$match:{
					user_uuid : "%s",
					status:{ $in: %s},
					"deployment_time":{"$gte":ISODate("%s")}
					}
				},
				{$sort:{"logs":1,"updated_at":1,"performance.updated_at":1}},
				//{
				//$limit : %d
				//}
				]);
				return results;
				}
			"""%(user_uuid,status_list,(datetime.datetime.now()-datetime.timedelta(days=7)).isoformat(),int(page_limit))

			fetch_all_logs_query_dict =[
				{
				"$lookup":{
					"from":"order_log",
					"localField":"deployment_uuid",
					"foreignField":"deployment_uuid",
					"as":"logs"
					}
				},
				{
				"$lookup":{
					"from":"algorithm_performance",
					"localField":"deployment_uuid",
					"foreignField":"deployment_uuid",
					"as":"performance"
					}
				},
				{
				"$match":{
					"user_uuid" : user_uuid,
					"status":{ "$in": status_list},
					"deployment_time":{"$gte":datetime.datetime.now()-datetime.timedelta(days=7)}
					}
				},
				{
					"$sort":{"logs":-1,"updated_at":-1,"performance.updated_at":-1}
				}
			]

		# order_logs = models.DeployedAlgorithm.objects.exec_js(fetch_all_logs_query)
		# print fetch_all_logs_query_dict
		order_log_cursor = models.DeployedAlgorithm._get_collection().aggregate(fetch_all_logs_query_dict)
		order_logs = []

		count = 0
		for o in order_log_cursor:
			count += 1
			order_logs.append(o)
			# if(count>=page_limit):
			# 	break

		grouped_orders = {}
		# grouped_orders = order_logs['_batch'][paginate*int(page_limit):int(page_limit)*(paginate+1)]
		grouped_orders = order_logs[paginate*int(page_limit):int(page_limit)*(paginate+1)]
		for i in range(len(grouped_orders)):
			grouped_orders[i]['logs'] = list(reversed(grouped_orders[i]['logs']))
			for j in range(len(grouped_orders[i]['logs'])):
				# print grouped_orders[i]['logs'][j]['created_at']
				grouped_orders[i]['logs'][j]['created_at'] = grouped_orders[i]['logs'][j]['created_at'].isoformat()
				grouped_orders[i]['logs'][j]['updated_at'] = ''#grouped_orders[i]['logs'][j]['updated_at'].isoformat()
				grouped_orders[i]['logs'][j]['_id'] = str(grouped_orders[i]['logs'][j]['_id'])
			grouped_orders[i]['_id']=str(grouped_orders[i]['_id'])
			grouped_orders[i]['created_at']=grouped_orders[i]['created_at'].isoformat()
			grouped_orders[i]['updated_at']=grouped_orders[i]['updated_at'].isoformat()
		# print grouped_orders
		# print dir(order_log_cursor)
		return JsonResponse({'grouped_orders':grouped_orders,'pages':int(count/page_limit)})
	return JsonResponse({"status":"error"})

def fetch_order_log(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error","error_msg":"Unauthorized"})

	if request.method=="GET":
			
		status = int(request.GET.get('status',0))
		page_limit = int(request.GET.get('limit',50))
		page_num = int(request.GET.get('page',0))

		if 'deployment_uuid' in request.GET.keys():
			deployment_uuid = request.GET.get('deployment_uuid','')
			order_logs = models.OrderLog.objects(user_uuid=user_uuid,deployment_uuid=deployment_uuid)
			orders_log_json = ujson.loads(order_logs.to_json())
			dep_obj = models.DeployedAlgorithm.objects.get(user_uuid=user_uuid,deployment_uuid=deployment_uuid)
			dep_obj = ujson.loads(dep_obj.to_json())
			# dep_obj["seg_sym"]
			if not dep_obj["algo_obj"].get("public",True) and (dep_obj["algo_obj"].get("publishing_uuid","")!="" and dep_obj["algo_obj"].get("public","")!=""): 
				dep_obj["algo_obj"]["action_str"]="" 
				dep_obj["algo_obj"]["action_str_exit"]="" 
			for i in range(len(order_logs)):
				# orders_log_json[i].created_at = 
				if orders_log_json[i].get('notification_data',{}).get('price_trigger-notification','')!='':
					trigger_key = orders_log_json[i].get('notification_data',{}).get('price_trigger-notification')
					tpsl_array = trigger_key.split(':');
					l_user_uuid = tpsl_array[0];
					l_deployment_uuid = tpsl_array[1];
					l_token = tpsl_array[3];
					l_algo_name = tpsl_array[8];
					l_action_type = tpsl_array[9];
					l_quantity = tpsl_array[10];
					l_algo_uuid = tpsl_array[11];
					l_product = tpsl_array[12];
					l_symbol = tpsl_array[13];
					l_segment = tpsl_array[14];
					try:
						l_variety = tpsl_array[15]
						l_tp = tpsl_array[16]
						l_sl = tpsl_array[17]
						l_tpsl_type = tpsl_array[18]
						l_deployment_type = tpsl_array[19]
					except:
						l_variety = 'REGULAR'
						l_tp = ''
						l_sl = ''
						l_tpsl_type = 'pct'
						l_deployment_type = 'Notification Only'

					orders_log_json[i]['notification_data']['deployment_uuid'] = l_deployment_uuid
					orders_log_json[i]['notification_data']['user_uuid'] = l_user_uuid
					orders_log_json[i]['notification_data']['token'] = l_token
					orders_log_json[i]['notification_data']['algo_name'] = l_algo_name
					orders_log_json[i]['notification_data']['action_type'] = l_action_type
					orders_log_json[i]['notification_data']['quantity'] = int(float(l_quantity))
					orders_log_json[i]['notification_data']['algo_uuid'] = l_algo_uuid
					orders_log_json[i]['notification_data']['product'] = l_product
					orders_log_json[i]['notification_data']['symbol'] = l_symbol
					orders_log_json[i]['notification_data']['segment'] = l_segment
					orders_log_json[i]['notification_data']['variety'] = l_variety
					orders_log_json[i]['notification_data']['target_profit'] = l_tp
					orders_log_json[i]['notification_data']['stop_loss'] = l_sl
					orders_log_json[i]['notification_data']['tpsl_type'] = l_tpsl_type
					orders_log_json[i]['notification_data']['deployment_type'] = l_deployment_type

					orders_log_json[i]['notification_data']['notification_time'] =  datetime.datetime.fromtimestamp(float(orders_log_json[i]['notification_data'].get('trigger_time','0'))).strftime('%Y-%m-%dT%H:%M:%S.%f')

				if orders_log_json[i].get('notification_data',None) is not None:
					if orders_log_json[i]['notification_data'].get("order_type","")=="":
						orders_log_json[i]['notification_data']["order_type"]="MARKET"
				orders_log_json[i]['created_at'] = order_logs[i].created_at.isoformat()
			return JsonResponse({'status':'success','order_logs':list(reversed(orders_log_json)),'dep_obj':dep_obj})

		count = 0
		if status==0:
			order_log_cursor = models.DeployedAlgorithm._get_collection().find({'user_uuid':user_uuid,"status":0,"expiration_time":{"$gte":datetime.datetime.now()}}).sort([("updated_at",-1)])
			count = models.DeployedAlgorithm._get_collection().count({'user_uuid':user_uuid,"status":0,"expiration_time":{"$gte":datetime.datetime.now()}})
		if status==-1:
			order_log_cursor = models.DeployedAlgorithm._get_collection().find({'user_uuid':user_uuid,"status":{ "$in": [-1,-2,-3]},"updated_at":{"$gte":datetime.datetime.now().replace(hour=0,minute=0,second=0)}}).sort([("updated_at",-1)])
			count = models.DeployedAlgorithm._get_collection().count({'user_uuid':user_uuid,"status":{ "$in": [-1,-2,-3]},"deployment_time":{"$gte":datetime.datetime.now()-datetime.timedelta(days=7)}})

		order_logs = []

		cur_i = 0
		for o in order_log_cursor:
			# count += 1
			# print o['deployment_uuid']
			cur_i += 1
			if not o["algo_obj"].get("public",True) and (o["algo_obj"].get("publishing_uuid","")!="" and o["algo_obj"].get("public","")!=""): 
				o["algo_obj"]["action_str"]="" 
				o["algo_obj"]["action_str_exit"]="" 
			if(max(0,page_num-1)*page_limit<cur_i<=max(0,page_num-1)*page_limit+page_limit):
				# adding seg sym handling for dynamic contract
				dynamic_flag = False
				if "DYNAMIC CONTRACT" in o["symbol"].upper():
					dynamic_flag = True
					o["segment_symbol"] = o["segment"]+"_"+o["symbol"]
				o["dynamic_flag"] = dynamic_flag

				logs = models.OrderLog._get_collection().find({"user_uuid" : user_uuid,"deployment_uuid":o['deployment_uuid']})#.sort([("created_at",-1)])
				log_list = []
				for l in logs:
					try:
						l['_id']=''
						if l.get('notification_data',{}).get('price_trigger-notification','')!='':
							trigger_key = l['notification_data'].get('price_trigger-notification')
							tpsl_array = trigger_key.split(':');
							l_user_uuid = tpsl_array[0];
							l_deployment_uuid = tpsl_array[1];
							l_token = tpsl_array[3];
							l_algo_name = tpsl_array[8];
							l_action_type = tpsl_array[9];
							l_quantity = tpsl_array[10];
							l_algo_uuid = tpsl_array[11];
							l_product = tpsl_array[12];
							l_symbol = tpsl_array[13];
							l_segment = tpsl_array[14];
							try:
								l_variety = tpsl_array[15]
								l_tp = tpsl_array[16]
								l_sl = tpsl_array[17]
								l_tpsl_type = tpsl_array[18]
								l_deployment_type = tpsl_array[19]
							except:
								l_variety = 'REGULAR'
								l_tp = ''
								l_sl = ''
								l_tpsl_type = 'pct'
								l_deployment_type = 'Notification Only'

							l['notification_data']['deployment_uuid'] = l_deployment_uuid
							l['notification_data']['user_uuid'] = l_user_uuid
							l['notification_data']['token'] = l_token
							l['notification_data']['algo_name'] = l_algo_name
							l['notification_data']['action_type'] = l_action_type
							print(l_quantity,tpsl_array)
							l['notification_data']['quantity'] = int(float(l_quantity))
							l['notification_data']['algo_uuid'] = l_algo_uuid
							l['notification_data']['product'] = l_product
							l['notification_data']['symbol'] = l_symbol
							l['notification_data']['segment'] = l_segment
							l['notification_data']['variety'] = l_variety
							l['notification_data']['target_profit'] = l_tp
							l['notification_data']['stop_loss'] = l_sl
							l['notification_data']['tpsl_type'] = l_tpsl_type
							l['notification_data']['deployment_type'] = l_deployment_type
							
							l['notification_data']['notification_time'] =  datetime.datetime.fromtimestamp(float(l['notification_data'].get('trigger_time','0'))).strftime('%Y-%m-%dT%H:%M:%S.%f')

						if l.get('notification_data',None) is not None:
							if l['notification_data'].get('order_type',"")=="":
								l['notification_data']["order_type"]="MARKET"
						# adding seg sym handling for dynamic contract
						try:
							if dynamic_flag:
								o_seg_sym = l['notification_data'].get('segment',"")+"_"+l['notification_data'].get('symbol',"")
								if o_seg_sym!="_" and o_seg_sym not in o["symbol"]:
									# print("o_seg_sym",o_seg_sym,o["symbol"])
									o["segment_symbol"] = o_seg_sym
						except:
							print(traceback.format_exc())
							pass
						log_list.append(l)
					except:
						print(traceback.format_exc())
				log_list.reverse()
				o['logs'] = log_list
				o['_id']=''

				try:
					positions = models.HoldingsForAlgorithm.objects.get(deployment_uuid=o['deployment_uuid'],user_uuid=user_uuid)
					o['algorithm_position'] = {"status":"success","positions":positions.position,"pnl":positions.pnl,'algo_uuid':positions['algo_uuid'],'seg':positions.segment,'sym':positions.symbol,'algo_name':positions['algo_name'],'product':positions.product}
				except DoesNotExist:
					print(o['deployment_uuid'],traceback.format_exc())
					o['algorithm_position'] = {}
				algorithm_performance = []
				o['performance'] = algorithm_performance
				order_logs.append(o)
			if(cur_i>max(0,page_num-1)*page_limit+page_limit):
				break
		return JsonResponse({'status':'success','grouped_orders':order_logs,'total_count':count,'pages':math.ceil(count/(page_limit*1.0))})
	return JsonResponse({"status":"error","error_msg":"Unsupported method"})

def fetch_single_backtest(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error"})

	# if request.method=="GET":
	# 	algo_uuid = request.GET.get('algo_uuid','')
	# 	segment_symbol = request.GET.get('segment_symbol','')

	# 	fetch_single_backtest_result = """
	# 		function(){
	# 		var results = [];
	# 		results = db[collection].findOne({user_uuid:"%s","algo_uuid":"%s","backtest_result.%s":{$exists:true}},{"backtest_result.%s":1,"algo_obj":1,"algo_uuid":1,"updated_at":1,"_id":0});
	# 		return results;
	# 		}"""%(user_uuid,algo_uuid,segment_symbol,segment_symbol)

	# 	backtest_result = models.Backtest.objects.exec_js(fetch_single_backtest_result)
	# 	return JsonResponse({'status':"success","backtest_result":backtest_result})
	if request.method=="GET":
		deployment_uuid = request.GET.get('deployment_uuid','')
		try:
			backtest_result = models.OrderLogBacktest.objects.get(deployment_uuid=deployment_uuid)
			# print backtest_result,dir(backtest_result)
			# backtest_result['updated_at']=backtest_result['updated_at']
			return JsonResponse({'status':"success","backtest_result":backtest_result.to_json()})
		except:
			print traceback.format_exc()
			return JsonResponse({'status':"error"})

def order_log(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return redirect('login')

	if request.method=="GET":
		con = get_redis_connection('default')
		
		deployment_ids = []

		key_prefix = ':'.join(['deployed',user_uuid])
		# deployed_keys = con.keys(key_prefix+':'+'*')
		deployed_keys = get_deployment_keys({"user_uuid":user_uuid})
		pipe = con.pipeline()
		
		for k in deployed_keys:
			pipe.get(k)
			deployment_ids = k.split(':')[-1]

		live_algos = pipe.execute()

		page_limit = 10
		status=0

		fetch_all_logs_query = """
			function(){
			var results = [];
			results = db[collection].aggregate([
				{
				$lookup:{
					from:"order_log",
					localField:"deployment_uuid",
					foreignField:"deployment_uuid",
					as:"logs"
					}
				},
				{
				$lookup:{
					from:"algorithm_performance",
					localField:"deployment_uuid",
					foreignField:"deployment_uuid",
					as:"performance"
					}
				},
				{
				$match:{
					user_uuid : "%s",
					status:%d
					}
				},
				//{
				//$project:{
				//	"_"
				//	}
				//}
				{
				$limit : %d
				}
				//,{
				//$sort:{"performance.updated_at":1,"logs":1}
				//}
				]);
				return results;
				}
			"""%(user_uuid,status,page_limit)

		# order_logs = models.DeployedAlgorithm.objects.exec_js(fetch_all_logs_query)

		# print order_logs
		grouped_orders = {}
		# grouped_orders = order_logs['_batch']
		# for i in range(len(grouped_orders)):
		# 	grouped_orders[i]['logs'] = list(reversed(grouped_orders[i]['logs']))
		# grouping orders based on their algo names
		# for o in order_logs['_batch']:
		# 	o['segment_symbol']=o['segment_symbol'].split('_')
		# 	if o['algo_name'] not in grouped_orders.keys():
		# 		grouped_orders[o['algo_name']] = [o]
		# 	else:
		# 		grouped_orders[o['algo_name']].append(o)
		"""
			{
			  "ABC": [
			    {
			      "segment_symbol": "NSE_SBIN",
			      "status": 0,
			      "logs": [
			        {
			          "algo_uuid": "4fcc3234-d02f-4cbb-8cb1-b35d353b8971",
			          "_id": "59dcb0938b57df448f0793e9",
			          "user_uuid": "123",
			          "deployment_uuid": "29a71729-34eb-4bb9-b3ae-8965eee1b82a",
			          "log_message": "Waiting for first trigger event"
			        }
			      ],
			      "algo_name": "ABC",
			      "created_at": "2017, 10, 10, 11, 35, 47, 442000",
			      "user_uuid": "123",
			      "updated_at": "2017, 10, 10, 11, 35, 47, 442000",
			      "deployment_time": "2017, 10, 10, 11, 35, 47, 442000",
			      "deployment_uuid": "29a71729-34eb-4bb9-b3ae-8965eee1b82a",
			      "_id": "59dcb0938b57df448f0793e8",
			      "algo_uuid": "4fcc3234-d02f-4cbb-8cb1-b35d353b8971",
			      "performance": []
			    },
			    {
			      "segment_symbol": "NSE_HDFCBANK",
			      "status": 0,
			      "logs": [
			        {
			          "algo_uuid": "4fcc3234-d02f-4cbb-8cb1-b35d353b8971",
			          "_id": "59dcb08f8b57df448f0793e7",
			          "user_uuid": "123",
			          "deployment_uuid": "9bfeb11c-6fc4-4b04-a24e-0ece6fe88524",
			          "log_message": "Waiting for first trigger event"
			        }
			      ],
			      "algo_name": "ABC",
			      "created_at": "2017, 10, 10, 11, 35, 43, 588000",
			      "user_uuid": "123",
			      "updated_at": "2017, 10, 10, 11, 35, 43, 588000",
			      "deployment_time": "2017, 10, 10, 11, 35, 43, 588000",
			      "deployment_uuid": "9bfeb11c-6fc4-4b04-a24e-0ece6fe88524",
			      "_id": "59dcb08f8b57df448f0793e6",
			      "algo_uuid": "4fcc3234-d02f-4cbb-8cb1-b35d353b8971",
			      "performance": []
			    }
			  ]
			}
		"""

		# print grouped_orders
		# for k in deployed_keys:			
		return render(request,'orders.html',{'grouped_orders':grouped_orders})

	return JsonResponse({"status":"error"})

def force_stop_clear(request):
	deployment_uuid = request.POST.get('deployment_uuid','')
	secret_key = request.POST.get('secret_key','')
	if request.method=='POST':
		if deployment_uuid!='' and secret_key!='qwertyqwerty123123':
			# con = get_redis_connection('default')
			# key_prefix_deployed = 'deployed:'+user_uuid+':*:'+deployment_uuid
			# key_prefix_price_trigger = user_uuid+':'+deployment_uuid+':PRICETRIGGER:*'
			# deployment_key = con.keys(key_prefix_deployed)
			# for k in deployment_key:
			# 	con.delete(k)
			# price_trigger_key = con.keys(key_prefix_price_trigger)
			# for k in price_trigger_key:
			# 	con.delete(k)
			try:
				deployed_algo = models.DeployedAlgorithm.objects.get(user_uuid=user_uuid,deployment_uuid=deployment_uuid)
				deployed_algo.status = -1
				deployed_algo.save()

				con = get_redis_connection('default')
				key_prefix = ':'.join(['deployed',user_uuid,'*',deployment_uuid])
				deployed_keys = con.keys(key_prefix)
				pipe = con.pipeline()
				for keys in deployed_keys:
					pipe.delete(key)
					pipe.publish(settings.ENV+'-deployment_channel','DEL:'+key)

				if deployment_uuid!='':
					key_prefix_deployed = 'deployed:'+user_uuid+':*:'+deployment_uuid
					key_prefix_price_trigger = user_uuid+':'+deployment_uuid+':PRICETRIGGER:*'
					deployment_key = con.keys(key_prefix_deployed)
					for k in deployment_key:
						pipe.delete(k)
					price_trigger_key = con.keys(key_prefix_price_trigger)
					for k in price_trigger_key:
						pipe.delete(k)

				res = pipe.execute()
				return JsonResponse({"status":"error"})
			except:
				print traceback.format_exc()
				return JsonResponse({"status":"error"})

	return JsonResponse({"status":"error"})

def force_stop(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error"})

	if request.method=="POST":
		deployment_uuid = request.POST.get('deployment_uuid','')
		algo_uuid = request.POST.get('algo_uuid','')
		seg_sym = request.POST.get('seg_sym','')
		if deployment_uuid!='':
			try:
				deployed_algo = models.DeployedAlgorithm.objects.get(user_uuid=user_uuid,deployment_uuid=deployment_uuid)
				deployed_algo.status = -1
				deployed_algo.save()

				con = get_redis_connection('default')
				key_prefix = ':'.join(['deployed',user_uuid,'*',deployment_uuid])
				# deployed_keys = con.keys(key_prefix)
				deployed_keys = get_deployment_keys({"user_uuid":user_uuid,"deployment_uuid":deployment_uuid})
				pipe = con.pipeline()
				for keys in deployed_keys:
					pipe.delete(key)
					# "fbca525b-6d04-4358-8f41-4fd262f000cb:f2ef4cc7-43c7-416b-b709-f577b4b3c72b:PRICETRIGGER:633601:TP1:SP1:194.71800000000002:188.991:ongc_cloned:SELL:1:ba06306d-1d73-477e-98a6-305325b1108d"
					pipe.publish(settings.ENV+'-deployment_channel','DEL:'+key)

				if deployment_uuid!='':
					key_prefix_deployed = 'deployed:'+user_uuid+':*:'+deployment_uuid
					key_prefix_price_trigger = user_uuid+':'+deployment_uuid+':PRICETRIGGER:*'
					# deployment_key = con.keys(key_prefix_deployed)
					deployment_key = get_deployment_keys({"user_uuid":user_uuid,"deployment_uuid":deployment_uuid})
					for k in deployment_key:
						pipe.delete(k)
					price_trigger_key = con.keys(key_prefix_price_trigger)
					for k in price_trigger_key:
						pipe.delete(k)
				res = pipe.execute()
				return JsonResponse({"status":"error"})
			except:
				print traceback.format_exc()
				return JsonResponse({"status":"error"})
		elif algo_uuid != '' and seg_sym != '':
			try:
				deployed_algo = models.DeployedAlgorithm.objects.get(user_uuid=user_uuid,algo_uuid=algo_uuid,segment_symbol=seg_sym)
				deployed_algo.status = -1
				deployed_algo.save()

				con = get_redis_connection('default')
				key_prefix = ':'.join(['deployed',user_uuid,algo_uuid,seg_sym,'*'])
				# deployed_keys = con.keys(key_prefix)
				deployed_keys = get_deployment_keys({"user_uuid":user_uuid,"algo_uuid":algo_uuid,"segment_symbol":seg_sym})
				pipe = con.pipeline()
				for keys in deployed_keys:
					pipe.delete(key)
					pipe.publish(settings.ENV+'-deployment_channel','DEL:'+key)
				res = pipe.execute()
				return JsonResponse({"status":"error"})
			except:
				print traceback.format_exc()
				return JsonResponse({"status":"error"})


	return JsonResponse({"status":"error"})

def stop_waiting_algos(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error","error":"auth"},status=401)

	if request.method=="POST":
		deployment_uuids = request.POST.get('deployment_uuids','[]')
		deployment_uuids = ujson.loads(urllib.unquote(unicode(deployment_uuids).encode('utf-8')))
		# deployment_uuids = deployment_uuids
		algo_uuid = request.POST.get('algo_uuid','')
		seg_sym = request.POST.get('seg_sym','')
		if deployment_uuids!=[]:
			con = get_redis_connection('default')
			pipeline = con.pipeline()
			msg = ''
			dkeys = models.DeployedAlgorithm._get_collection().find({"user_uuid":user_uuid,"status":0})
			deployed_dict = {}
			for d in dkeys:
				x = [d["user_uuid"],d["algo_uuid"],d["segment_symbol"],d["algo_obj"]["time_frame"],d["deployment_uuid"]]
				if d["deployment_uuid"] in deployed_dict.keys():
					deployed_dict[d["deployment_uuid"]].append('deployed:'+":".join(x))
				else:	
					deployed_dict[d["deployment_uuid"]]=['deployed:'+":".join(x)]
			deployed_keys = None
			for deployment_uuid in deployment_uuids:

				# keys = con.keys('deployed:'+user_uuid+':*:'+deployment_uuid)
				print "deployment_uuid--->",deployment_uuid
				# deployed_keys = utility.scan_redis_key(con,'deployed:'+user_uuid+':*:'+deployment_uuid)
				deployed_keys = deployed_dict.get(deployment_uuid,None)
				if(deployed_keys is None):
					continue
				if len(deployed_keys)>0:
					redis_key = deployed_keys[0]
				print redis_key,'............'

				try:

					holdings = models.HoldingsForAlgorithm.objects.get(deployment_uuid=deployment_uuid,user_uuid=user_uuid)
					#print holdings,dir(holdings.position),'....' ,holdings.position.keys(),type(holdings['position']['qty'])
					if float(holdings['position']['qty'])!=float(0):
						print "holdings['position']['qty']",holdings['position']['qty']
						continue
					try:
						open_order = models.BrokerOrder.objects.get(deployment_uuid=deployment_uuid,user_uuid=user_uuid,order_status={})
						print open_order.order_id,open_order.order_status
						# if open_order:
							# res = ams_helper.cancel_order(user_uuid,open_order.order_payload['exchange'],open_order.order_payload['account_name'],open_order.order_id,open_order.order_payload['tradingsymbol'],'')
							# if res is None:
							# msg = 'Cancel the open orders from Orderbook to stop the algos'
							# else:
							# continue
					except:
						print traceback.format_exc()
						#continue
					if redis_key:
						pipeline.delete(redis_key)
						pipeline.expire(redis_key,1)
						pipeline.publish(settings.ENV+'-deployment_channel','DEL:'+redis_key)
						# del_keys =  con.keys(user_uuid+':'+deployment_uuid+':PRICETRIGGER:*:IR1:*')
						# # print 'del_keys---------',del_keys,user_uuid+':'+deployment_uuid+':PRICETRIGGER:*:IR1*'
						# if len(del_keys)==1:
						# 	pipeline.delete(del_keys[0])
						# del_keys = utility.scan_redis_key(con,user_uuid+':'+deployment_uuid+':PRICETRIGGER:*:IR1:*')
						# if del_keys is not None:
						# 	pipeline.delete(del_keys)
					if deployment_uuid!='':
						key_prefix_deployed = 'deployed:'+user_uuid+':*:'+deployment_uuid
						key_prefix_price_trigger = user_uuid+':'+deployment_uuid+':PRICETRIGGER:*'
						# deployment_key = utility.scan_redis_key(con,key_prefix_deployed,key_list=True)
						deployment_key = deployed_keys
						for k in deployment_key:
							pipeline.delete(k)
						# price_trigger_key = utility.scan_redis_key(con,key_prefix_price_trigger,key_list=True)
						# for k in price_trigger_key:
						# 	pipeline.delete(k)

					deployed_algo = models.DeployedAlgorithm.objects.get(deployment_uuid=deployment_uuid,user_uuid=user_uuid)
					deployed_algo.status = -1
					deployed_algo.expiration_time = datetime.datetime.now()

					order_stop_log = models.OrderLog(
								user_uuid=user_uuid,
								algo_uuid=deployed_algo.algo_uuid,
								deployment_uuid=deployment_uuid,
								log_tag="Force stopped",
								log_message="Algo stopped by you"
								)

					deployed_algo.save()
					order_stop_log.save()
					pipeline.execute()
					print("algo_state updated")
				except:
					print traceback.format_exc()
			return JsonResponse({"status":"success","msg":msg})
		elif algo_uuid != '' and seg_sym != '':
			try:
				deployed_algo = models.DeployedAlgorithm.objects.get(user_uuid=user_uuid,algo_uuid=algo_uuid,segment_symbol=seg_sym)
				deployed_algo.status = -1
				deployed_algo.save()

				con = get_redis_connection('default')
				key_prefix = ':'.join(['deployed',user_uuid,algo_uuid,seg_sym,'*'])
				# deployed_keys = utility.scan_redis_key(con,key_prefix,key_list=True)
				deployed_keys = get_deployment_keys({"user_uuid":user_uuid,"algo_uuid":algo_uuid,"segment_symbol":seg_sym})
				pipe = con.pipeline()
				for keys in deployed_keys:
					pipe.delete(key)
					pipe.publish(settings.ENV+'-deployment_channel','DEL:'+key)
				res = pipe.execute()
				return JsonResponse({"status":"error"})
			except:
				print traceback.format_exc()
				return JsonResponse({"status":"error"})


	return JsonResponse({"status":"error","error_msg":"unkown"})

def portfolio(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return redirect('home')
	return render(request,'portfolio.html',{})

def mobile_portfolio(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return redirect('home')
	return render(request,'mobile_portfolio.html',{})

@override_with_ams
def fetch_positions(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error"})
	if request.method!='GET':
		return JsonResponse({"status":"error","error":"type"})

	headers = {}
	if settings.KITE_HEADER == True:
		headers = {"X-Kite-Version":"3"}
		auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
		headers["Authorization"] = "token {}".format(auth_header)
	response = requests.get("https://api-partners.kite.trade/portfolio/positions/?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token','')),headers=headers)
	# print 'request url',"https://api-partners.kite.trade/portfolio/positions/?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token',''))
	if response.status_code == 200:
		response_json = json.loads(response.text)
		if response_json['status']=="success":
			positions = models.PositionsOfInstrument.objects(user_uuid=user_uuid,updated_at__gte=datetime.datetime.now().replace(hour=3,minute=0,second=0))
			print 'pppppppp',positions,'2017-11-10T01:00:00.969619',datetime.datetime.now().replace(hour=1,minute=0,second=0).isoformat()
			# print user_uuid
			if positions==[] and request.GET.get('filter','').lower()=='streak':
				return JsonResponse({"status":"success","positions":[]})
			else:
				adj_positions = []
				# adj_positions = response_json['data']['net']
				# adj_positions[0]['deployment_uuid']='111111111111'
				for n in response_json['data']['net']:
					if(request.GET.get('filter','').lower()=='all'):
						n['modified']=0	
						n['user_uuid']=user_uuid
						if n["exchange"]=="NFO":
							if (n['tradingsymbol'].endswith("CE") or n['tradingsymbol'].endswith("PE")):
								n["segment"]="NFO-OPT"
							else:
								n["segment"]="NFO-FUT"
						elif n["exchange"]=="CDS":
							n["segment"]="CDS-FUT"
						else:
							n["segment"]=n["exchange"]
						adj_positions.append(n)
					else:
						for p in positions:
							if(n['tradingsymbol']==p['symbol'] and n['product']==p['product']):
								if (n['tradingsymbol'].endswith("CE") or n['tradingsymbol'].endswith("PE")) and p["exch"]=="NFO-OPT":
									continue
								if(n['quantity']==p['quantity']):
									n['modified']=0	
								else:
									n['modified']=1							
								n['user_uuid']=p['user_uuid']
								if n["exchange"]=="NFO":
									if (n['tradingsymbol'].endswith("CE") or n['tradingsymbol'].endswith("PE")):
										n["segment"]="NFO-OPT"
									else:
										n["segment"]="NFO-FUT"
								elif n["exchange"]=="CDS":
									n["segment"]="CDS-FUT"
								else:
									n["segment"]=n["exchange"] 
								adj_positions.append(n)
				return JsonResponse({"status":"success","positions":adj_positions})
		else:
			return JsonResponse({"status":"error","error":"response error"})		
	elif response.status_code == 403:
		return JsonResponse({"status":"error","error":"auth",'error_msg':'Session expired, relogin required'})

	return JsonResponse({"status":"error"})

@override_with_ams
def fetch_specific_position(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error"})

	if request.method!='GET':
		return JsonResponse({"status":"error"})

	headers = {}
	if settings.KITE_HEADER == True:
		headers = {"X-Kite-Version":"3"}
		auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
		headers["Authorization"] = "token {}".format(auth_header)
	response = requests.get("https://api-partners.kite.trade/portfolio/positions/?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token','')),headers=headers)
	# print 'request url',"https://api-partners.kite.trade/portfolio/positions/?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token',''))

	if response.status_code == 200:
		response_json = json.loads(response.text)
		if response_json['status']=="success":
			positions = models.PositionsOfInstrument.objects(user_uuid=user_uuid,updated_at__gte=datetime.datetime.now().replace(hour=3,minute=0,second=0))
			if positions==[]:
				return JsonResponse({"status":"success","positions":[]})
			else:
				adj_positions = []
				for n in response_json['data']['net']:
					if(n['tradingsymbol']==request.GET.get('symbol','') and n['exchange']==request.GET.get('exchange','') and n['product']==request.GET.get('product','')):
						adj_positions.append(n)
				return JsonResponse({"status":"success","positions":adj_positions})
		else:
			return JsonResponse({"status":"error","error":"response error"})
	elif response.status_code == 403:
		return JsonResponse({"status":"error","error":"auth",'error_msg':'Session expired, relogin required'})
	return JsonResponse({"status":"error"})

@override_with_ams
def fetch_holdings(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error"})
	if request.method!='GET':
		return JsonResponse({"status":"error","error":"type"})
	
	headers = {}
	if settings.KITE_HEADER == True:
		headers = {"X-Kite-Version":"3"}
		auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
		headers["Authorization"] = "token {}".format(auth_header)

	response = requests.get("https://api-partners.kite.trade/portfolio/holdings/?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token','')),headers=headers)
	# print 'request url',"https://api-partners.kite.trade/portfolio/holdings/?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token',''))
	if response.status_code == 200:
		response_json = json.loads(response.text)
		if response_json['status']=="success":
			# positions = models.HoldingsForAlgorithm.objects(user_uuid=user_uuid,product='CNC',position__qty__ne = 0).order_by("updated_at")
			# holdings = models.HoldingsForAlgorithm._get_collection().find({'user_uuid':user_uuid,"status":{ "$in": [-1,-2,-3]},"deployment_time":{"$gte":datetime.datetime.now().replace(hour=0,minute=0,second=0)}}).sort([("updated_at",-1)])
			holding_algos = models.DeployedAlgorithm.objects(user_uuid=user_uuid,algo_obj__product='CNC',status=0)
			# print holding_algos
			if holding_algos==[] and request.GET.get('filter','').lower()=='streak':
				return JsonResponse({"status":"success","positions":[]})
			else:
				adj_positions = []
				adj_holdings_list = []
				# adj_positions = response_json['data']['net']
				# adj_positions[0]['deployment_uuid']='111111111111'
				for n in response_json['data']:#['net']:
					if(request.GET.get('filter','').lower()=='all'):
						n['modified']=0
						n['user_uuid']=user_uuid
						adj_positions.append(n)
					else:
						for p in holding_algos:
							# print p['symbol']
							if(n['tradingsymbol']==p['symbol'] and n['product']==p['algo_obj']['product']) and p['symbol'] not in adj_holdings_list:
								adj_holdings_list.append(p['symbol'])
								# print p['position']['qty']
								n['modified']=0	
								# if(n['quantity']+n['t1_quantity']==p['position']['qty']):
								# 	pass
								# else:
								# 	n['modified']=1							
								n['user_uuid']=p['user_uuid']
								adj_positions.append(n)
				return JsonResponse({"status":"success","positions":adj_positions})
		else:
			return JsonResponse({"status":"error","error":"response error"})		
	elif response.status_code == 403:
		return JsonResponse({"status":"error","error":"auth",'error_msg':'Session expired, relogin required'})

	return JsonResponse({"status":"error"})

@override_with_ams
def fetch_open_positions(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error"})
	if request.method == "GET":
		deployment_uuid = request.GET.get('deployment_uuid','')
		if deployment_uuid == '':
			print 'deployment_uuid not present'
			return JsonResponse({"status":"error"})
		positions = models.HoldingsForAlgorithm.objects.get(deployment_uuid=deployment_uuid,user_uuid=user_uuid)
		latest_order = models.BrokerOrder.objects(deployment_uuid=deployment_uuid,user_uuid=user_uuid).order_by('-id').first()
		resp = {"status":"success","positions":positions.position,"pnl":positions.pnl,'algo_uuid':positions['algo_uuid'],'seg':positions.segment,'sym':positions.symbol,'algo_name':positions['algo_name'],'product':positions.product}
		if latest_order:
			try:
				resp['variety'] = latest_order['order_payload'].get('variety','REGULAR').upper()
				resp['order_id'] = latest_order['order_id']
				resp['parent_order_id'] = latest_order['order_status'].get('parent_order_id',resp['order_id'])
			except:
				resp['variety'] = 'REGULAR'
				print traceback.format_exc()
		return JsonResponse(resp)

	return JsonResponse({"status":"error"})

def exit_with_positions_open(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error","error_msg":'auth'})
	if request.method == "POST":
		deployment_uuid = request.POST.get('deployment_uuid','')
		if deployment_uuid == '':
			# print 'deployment_uuid not present'
			JsonResponse({"status":"error","error_msg":'No deployment found'})

		con = get_redis_connection("default")
		pipeline = con.pipeline()

		# keys = con.keys('deployed:'+user_uuid+':*:'+deployment_uuid)
		keys = get_deployment_keys({"user_uuid":user_uuid,"deployment_uuid":deployment_uuid,"status":0,"expiration_time":{"$gte":datetime.datetime.now()}})
		if len(keys)>0:
			redis_key = keys[0]
		else:
			redis_key = None

		try:
			# holdings = models.HoldingsForAlgorithm.objects.get(deployment_uuid=deployment_uuid,user_uuid=user_uuid)
			#print holdings,dir(holdings.position),'....' ,holdings.position.keys(),type(holdings['position']['qty'])
			# if holdings['position']['qty']!=0:
			# 	return JsonResponse({"status":"error","error_msg":'Cancel the open order from Orderbook to stop the algo'})
			# try:
			# 	open_order = models.BrokerOrder.objects.get(deployment_uuid=deployment_uuid,user_uuid=user_uuid,order_status={})
			# 	print open_order.order_id,open_order.order_status
			# 	if open_order:
			# 		# res = ams_helper.cancel_order(user_uuid,open_order.order_payload['exchange'],open_order.order_payload['account_name'],open_order.order_id,open_order.order_payload['tradingsymbol'],'')
			# 		# if res is None:
			# 		msg = 'Cancel the open order from Orderbook to stop the algo'
			# 		# else:
			# 		return JsonResponse({"status":"error","error_msg":msg})
			# except:
			# 	print traceback.format_exc()
			if redis_key:
				pipeline.delete(redis_key)
				pipeline.expire(redis_key,1)
				pipeline.publish(settings.ENV+'-deployment_channel','DEL:'+redis_key)
				del_keys =  con.keys(user_uuid+':'+deployment_uuid+':PRICETRIGGER:*:IR1:*')
				# print 'del_keys---------',del_keys,user_uuid+':'+deployment_uuid+':PRICETRIGGER:*:IR1*'
				if len(del_keys)==1:
					pipeline.delete(del_keys[0])

			if deployment_uuid!='':
				# key_prefix_deployed = 'deployed:'+user_uuid+':*:'+deployment_uuid
				key_prefix_price_trigger = user_uuid+':'+deployment_uuid+':PRICETRIGGER:*'
				# deployment_key = con.keys(key_prefix_deployed)
				deployment_key = keys #get_deployment_keys({"user_uuid":user_uuid,"deployment_uuid":deployment_uuid})
				for k in deployment_key:
					pipeline.delete(k)
				price_trigger_key = con.keys(key_prefix_price_trigger)
				for k in price_trigger_key:
					pipeline.delete(k)

			deployed_algo = models.DeployedAlgorithm.objects.get(deployment_uuid=deployment_uuid,user_uuid=user_uuid)
			deployed_algo.status = -1
			deployed_algo.expiration_time = datetime.datetime.now()

			order_stop_log = models.OrderLog(
						user_uuid=user_uuid,
						algo_uuid=deployed_algo.algo_uuid,
						deployment_uuid=deployment_uuid,
						log_tag="Force stopped",
						log_message="Algo stopped by you"
						)

			deployed_algo.save()
			order_stop_log.save()
			pipeline.execute()
			return JsonResponse({"status":"success"})
		except:
			print traceback.format_exc()
			return JsonResponse({"status":"error","error_msg":'Unkown error, try again'})
			# action_type = algo_obj['action_type']
			# trigger_price = price_data
			# trigger_time = float(unix_time)
			# exch_seg = exch_seg
			# seg = event['seg']
			# sym = event['sym']
			# broker = algo_object['broker']
			# quantity = algo_obj['quantity']
			# notification_time = datetime.datetime.now().isoformat()
			# notification_msg = 'Strategy forced stopped!'
			# notification_payload = {'notification-type':'order-state','notification_msg':notification_msg,'action_type':action_type,
			# 'trigger_time':int(trigger_time),
			# 'trigger_price':price_data,
			# 'seg':seg,'sym':sym,'quantity':quantity,'broker':broker,'notification_time':notification_time,
			# 'user_uuid':algo_obj['user_uuid'],
			# 'algo_uuid':algo_obj['algo_uuid'],
			# 'algo_name':algo_obj['algo_name'],
			# 'deployment_uuid':algo_object['deployment_uuid']
			# }
			# notification_payload = json.dumps(notification_data)
			# pipeline.publish('dev'+'-notification','DEL:'+redis_key)r.publish('dev-notification',notification_payload)
	
	return JsonResponse({"status":"error","error_msg":'unkown'})

@override_with_ams
def exit_position_now_force_stop(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error"})
	if request.method == "POST":
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
			return JsonResponse({"status":"error"})

		access_token = request.session.get('access_token','')
		public_token = request.session.get('public_token','')
		user_broker_id = request.session.get('user_broker_id','')

		if access_token=='' or public_token=='' or user_broker_id=='':
			print 'probably kite login popup'
			return JsonResponse({"status":"error"})

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
		response_json = json.loads(response.text)
		if response.status_code == 200:
			if response_json['status']=="success":
				#update holdings for algorithm using webhook 
				# holding = HoldingsForAlgorithm.objects.get(user_uuid=user_uuid,deployment_uuid=deployment_uuid)
				# holding.position[segment+'_'+symbol]['qty']=
				broker_order = models.BrokerOrder(user_uuid=user_uuid,
					deployment_uuid=deployment_uuid,
					algo_uuid=algo_uuid,
					# algo_name=algo_name,
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

				con = get_redis_connection("default")
				pipeline = con.pipeline()

				# keys = con.keys('deployed:'+user_uuid+':*:'+deployment_uuid)
				keys = get_deployment_keys({"user_uuid":user_uuid,"deployment_uuid":deployment_uuid})
				if len(keys)>0:
					redis_key = keys[0]
				else:
					redis_key = None

				try:
					if redis_key:
						algo_obj = con.get(redis_key)
						if algo_obj is not None:
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
						else:
							print(redis_key)
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
						# deployment_key = con.keys(key_prefix_deployed)
						deployment_key = keys#con.keys(key_prefix_deployed)
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
								log_message="Algo stopped by you"
								)
					deployed_algo.save()
					order_stop_log.save()
					pipeline.execute()
					return JsonResponse({'status':'success'})
				except:
					return JsonResponse({'status':'error'})
			else:
				return JsonResponse({'status':'error','order_response':response_json,'response_code':response.status_code})
		else:
			return JsonResponse({'status':'error','response_code':response.status_code,'error_msg':response_json.get("message","")})
		return JsonResponse({'status':'error'})

def order_book(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return redirect('login')

	if request.method=="GET":
		pass

	return render(request,'orderbook2.html',{})

def mobile_order_book(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return redirect('login')

	if request.method=="GET":
		pass

	return render(request,'mobile_orderbook.html',{})

@override_with_ams
def fetch_order_book(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({'status':'error','error':'auth'})

	if request.method=="GET":
		platform = request.GET.get('platform','streak').lower()
		if platform not in ['streak','all']:
			return JsonResponse({'status':'error','error':'unkown platform'})
		if platform == 'streak':
			orders = []
			headers = {}
			if settings.KITE_HEADER == True:
				headers = {"X-Kite-Version":"3"}
				auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
				headers["Authorization"] = "token {}".format(auth_header)
			response = requests.request("GET","https://api-partners.kite.trade/orders?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token','')),headers=headers)
			print "https://api-partners.kite.trade/orders?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token',''))
			if response.status_code == 200:
				response_json = json.loads(response.text)
				if response_json['status']=="success":
					orders = response_json['data']
					executed = []
					pending = []
					now = datetime.datetime.now()
					br_o = models.BrokerOrder.objects(user_uuid=user_uuid,created_at__gte = now.replace(hour=0,minute=0,second=0))
					br_order_depid = {}
					br_orders_list = []
					try:
						for b in br_o:
							br_orders_list.append(b.order_id)
							br_order_depid[b.order_id]=b["deployment_uuid"]
					except:
						print(traceback.format_exc())
						br_orders_list = [b.order_id for b in br_o]
						pass
					for o in orders:
						if (o['order_id'] in br_orders_list):
							if "DIRECT_" in br_order_depid.get(o['order_id'],""):
								o["order_tag"]="direct"
							else:
								o["order_tag"]="strategy"
							if o['status'] in ['COMPLETE','REJECTED','CANCELLED','CANCELLED AMO'] or 'CANCELLED' in o['status'] or 'REJECTED' in o['status']:
								o['user_uuid']=user_uuid
								executed.append(o)
							else:
								pending.append(o)
					return JsonResponse({"status":"success","orders":orders,'pending':pending,'executed':executed,'platform':platform})
			else:
				return JsonResponse({"status":"error","error":"response error",'error_msg':'Session expired, relogin required'})
			return JsonResponse({'status':'success'})
		if platform == 'all':
			try:
				orders = []
				headers = {}
				if settings.KITE_HEADER == True:
					headers = {"X-Kite-Version":"3"}
					auth_header = settings.KITE_API_KEY + ":" + request.session.get('access_token','')
					headers["Authorization"] = "token {}".format(auth_header)
				response = requests.request("GET","https://api-partners.kite.trade/orders?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token','')),headers=headers)
				# print("https://api-partners.kite.trade/orders?api_key={}&access_token={}".format(settings.KITE_API_KEY,request.session.get('access_token','')))
				if response.status_code == 200:
					response_json = json.loads(response.text)
					if response_json['status']=="success":
						orders = response_json['data']
						executed = []
						pending = []

						now = datetime.datetime.now()
						br_o = models.BrokerOrder.objects(user_uuid=user_uuid,created_at__gte = now.replace(hour=0,minute=0,second=0))
						br_order_depid = {}
						br_orders_list = []
						try:
							for b in br_o:
								br_orders_list.append(b.order_id)
								br_order_depid[b.order_id]=b["deployment_uuid"]
						except:
							print(traceback.format_exc())
							br_orders_list = [b.order_id for b in br_o]
							pass

						for o in orders:
							if (o['order_id'] in br_orders_list):
								if "DIRECT_" in br_order_depid.get(o['order_id']):
									o["order_tag"]="direct"
								else:
									o["order_tag"]="strategy"
							else:
								o["order_tag"]="kite"

							if o['status'] in ['COMPLETE','REJECTED','CANCELLED','CANCELLED AMO'] or 'CANCELLED' in o['status'] or 'REJECTED' in o['status']:
								o['user_uuid']=user_uuid
								executed.append(o)
							else:
								pending.append(o)
						return JsonResponse({"status":"success","orders":orders,'pending':pending,'executed':executed,'platform':platform})
				else:
					return JsonResponse({"status":"error","error":"response error",'error_msg':'Session expired, relogin required'})
			except:
				print(traceback.format_exc())		

	return JsonResponse({})
