from django.shortcuts import render,redirect
from django.http import JsonResponse
from django_redis import get_redis_connection
import random
import uuid
import datetime
import traceback
from django.conf import settings
from coreapp import models


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
		return redirect('login')

	if request.method == "GET":
		
		algo_uuid = request.GET.get('algo_uuid','')
		if algo_uuid == '':
			return render(request,'algorithm.html',
					{'status':'success'
					})

		try:
			algo = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_uuid = algo_uuid,
					status = 0
					)
			return render(request,'algorithm.html',
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
			return render(request,'algorithm.html',
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

			return render(request,'algorithm.html',
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

	return render(request,'algorithm.html',
					{'status':'success'
					})

def submit_algorithm(request):
	"""
	Submit algorithm enables creating and updation of algorithm
	parameters
	----------
	request - This the django request object

	NOTE : This method can be made more efficient as it currently directly stores the entry logic and not the action, requires action parsing evey time
	"""
	if request.method == 'POST':
		user_uuid = request.session.get('user_uuid', '')
		user_is_auth = request.session.get('user_is_auth', False)

		if settings.ENV == "local" or settings.ENV == 'local1':
			user_uuid = '123'
			user_is_auth = True
		if not user_is_auth:
			return redirect('login')

		algo_uuid = request.POST.get('algo_uuid','')
		algo_name = request.POST.get('algo_name','').strip('<>/,{}')
		algo_desc = request.POST.get('algo_desc','').strip('<>/,{}')
		
		position_type = request.POST.get('position_type','')
		quantity = int(request.POST.get('position_qty',''))
		
		entry_logic = request.POST.get('entry_logic','')
		exit_logic = request.POST.get('exit_logic','')

		take_profit = request.POST.get('take_profit','0.0')
		stop_loss = request.POST.get('stop_loss','0.0')

		time_frame = request.POST.get('time_frame','day')
		cover_proportion = request.POST.get('cover_proportion',1)

		html_block = request.POST.get('html_block','')

		symbols = {}
		#TODO log UUID

		errors = []
		if take_profit == "":
			errors.append('Take profit not provided')
		elif stop_loss == "":
			errors.append('Stop loss not provided')

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
				action = Action(
					entry_logic = entry_logic,
					position_type = position_type,
					exit_logic = exit_logic
					)
				# temporarily updating in algorithm_tiem
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

				if not action.is_valid():
					errors.append('Action decoding error. \n{}\n{}'.format(action.get_entry_generator_error(),action.get_exit_generator_error()))
					return JsonResponse({'status':False,
										'error':errors
										})

				algorithm_item.algo_name = algo_name
				algorithm_item.algo_desc = algo_desc

				algorithm_item.user_uuid = user_uuid
				algorithm_item.algo_uuid = algo_uuid
				
				algorithm_item.entry_logic = entry_logic
				algorithm_item.exit_logic = exit_logic
				
				algorithm_item.position_type = action.position_type

				algorithm_item.quantity = strategy.quantity

				algorithm_item.take_profit = float(strategy.take_profit)
				algorithm_item.stop_loss = float(strategy.stop_loss)

				algorithm_item.html_block = html_block

				if algorithm_item.status == 1:
					algorithm_item.status = 2 # if algo was live, pause it

				try:
					algorithm_item.save(clean=False)
					# TODO handle deployment live state based on the database
					models.Backtest.objects(algo_uuid=algo_uuid,user_uuid=user_uuid).delete()
					request.session['algo_uuid'] = algo_uuid
					return JsonResponse({'status':'success','algo_uuid':algo_uuid})

				except Exception:
					# TODO log the error
					if settings.DEBUG:
						print(traceback.format_exc())

					return JsonResponse({'status':'error'})
			except models.Algorithm.DoesNotExist:
				# TODO log errors
				errors.append('Algo not found')
				return JsonResponse({
									'status':'error',
									'error':errors
									})

		if algo_uuid =='':
			try:
				algorithm_item = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_name = algo_name
					)
				if algorithm_item:
					errors.append('Strategy name already used, please use a different name.')
					return JsonResponse({'status':False,
								'errors':errors
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
		if not action.is_valid():
			# TODO log errors

			errors.append('Action decoding error. \n{}\n{}'.format(action.get_entry_generator_error,action.get_exit_generator_error))

			return JsonResponse({'status':False,
								'errors':errors
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

		algorithm_item = models.Algorithm(
								algo_name = algo_name,
								algo_desc = algo_desc,
								user_uuid = user_uuid,
								algo_uuid = algo_uuid,
								entry_logic = entry_logic,
								exit_logic = exit_logic,
								symbols = symbols, # symbols which are part of the stategy logic
								position_type = action.position_type,
								quantity = quantity,
								take_profit = take_profit,
								stop_loss = stop_loss,
								html_block = html_block
								)

		try:
			algorithm_item.save()
			# this sets the session variable so that on loading of any new page
			request.session['algo_uuid'] = algo_uuid # must be set so that we can identify wether an edit is being made or a new algo is being saved with the same name
			# print algo_uuid
			return JsonResponse({'status':'success','algo_uuid':algo_uuid})

		except:
			try:
				if request.session.get('algo_uuid',None):
					algorithm_item = models.Algorithm.objects(user_uuid=user_uuid,algo_name=algo_name).modify(upsert=True,
	                                      set__algo_desc=algo_desc,
	                                      set__entry_logic=entry_logic, 
	                                      set__exit_logic=exit_logic, 
	                                      set__symbols=symbols, 
	                                      set__position_type=action.position_type, 
	                                      set__quantity=quantity, 
	                                      set__take_profit=take_profit, 
	                                      set__stop_loss=stop_loss, 
	                                      set__html_block=html_block)

					algo_uuid = request.session.get('algo_uuid','')
					return JsonResponse({'status':'success','algo_uuid':algo_uuid})
				else:
					errors.append('You already have algo with same name exists')
					return JsonResponse({'status':'success','errors':errors})
			except:
				# TODO log error
				if settings.DEBUG:
					print traceback.format_exc()
				print "Some error",traceback.format_exc()

				return JsonResponse({'status':False,
									'errors':errors
									})

	else:
		print "wrong request type"
		return JsonResponse({'status':'error'})

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
			return render(request,'algorithm.html',
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
			
			return render(request,'algorithm.html',
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
			return JsonResponse({'status':'error','error':'Algo not present'})

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
			return JsonResponse({'status':'error','error':'Algo not present'})
	return JsonResponse({'status':'error','error':'Method not present'})

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
			return JsonResponse({'status':'error','error':'Algo not present'})

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
								html_block = algo.html_block
								)

			algorithm_item.save()
			return JsonResponse({'algo_uuid':cloned_algo_uuid,
							'status':'success'})

		except models.Algorithm.DoesNotExist:
			# TODO log error
			# if settings.DEBUG:
			print traceback.format_exc()
			return JsonResponse({'status':'error','error':'Algo not present'})
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
			return JsonResponse({'status':'error','error':'Algo not present'})
		try:
			algo = models.Algorithm.objects.get(
					user_uuid = user_uuid,
					algo_uuid = algo_uuid
					)
			algo.delete()
			return JsonResponse({'status':'success'})

		except models.Algorithm.DoesNotExist:
			# TODO log error
			# if settings.DEBUG:
			print traceback.format_exc()
			return JsonResponse({'status':'error','error':'Algo not present'})

	return JsonResponse({'status':'error'})