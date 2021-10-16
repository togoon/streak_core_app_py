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
from coreapp.views.utility import update_usage_util


def publication_action(request):
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
		return JsonResponse({"status":"error","error":"auth","error_msg":"auth"},status=401)

	if request.method!='POST':
		return JsonResponse({"status":"error","error":"Invalid method","error_msg":"Invalid method"},status=403)
	else:
		payload = request.POST



	interaction_type = payload.get("interaction_type","vote")
	publishing_uuid = payload.get("publishing_uuid","")
	element_type = payload.get("element_type","published_algo")
	interaction_action = payload.get("interaction_action","upvote")

	element_uuid = publishing_uuid

	if publishing_uuid == '':
		return JsonResponse({"status":"error","error":"Published algo for not found","error_msg":"Published algo for not found"})

	if interaction_type == 'vote':
		interaction = None
		element = None
		try:
			element = models.SubscribedAlgos.objects.get(user_uuid=user_uuid,publishing_uuid = element_uuid)

			published_algo = models.PublishedAlgos.objects.get(publishing_uuid = element_uuid)

			interaction = models.Interaction.objects.get(user_uuid=user_uuid,element_uuid=element_uuid,interaction_type=interaction_type)
			if interaction.interaction_action==interaction_action:
				return JsonResponse({"status":"error","error":"Already voted","error_msg":"Already voted"})
			else:
				interaction.interaction_action = interaction_action
			
			if interaction_action=="upvote":
				published_algo.upvotes = max(0,published_algo.upvotes + 1)
				published_algo.downvotes = max(0,published_algo.downvotes - 1)
			elif interaction_action=="downvote":
				published_algo.upvotes = max(0,published_algo.upvotes - 1)
				published_algo.downvotes = max(0,published_algo.downvotes + 1)
			published_algo.save()
			interaction.save()
			return JsonResponse({"status":"success","upvotes":published_algo.upvotes,"downvotes":published_algo.downvotes,"score":published_algo.score})
		except DoesNotExist:
			print(traceback.format_exc())
			if element is None:
				return JsonResponse({"status":"error","error":"You can only vote for after you have used it","error_msg":"You can only vote for after you have used it"})

			interaction_uuid = str(uuid.uuid4())
			interaction = models.Interaction(
				user_uuid=user_uuid,
				interaction_uuid=interaction_uuid,
				element_uuid=element_uuid,
				element_type=element_type,
				interaction_type=interaction_type,
				interaction_action = interaction_action,
				owner_uuid = element.user_uuid,
				)
			try:
				element = models.PublishedAlgos.objects.get(publishing_uuid = element_uuid)
				if interaction_action=="upvote":
					element.upvotes = max(0,element.upvotes + 1)
					element.downvotes = max(0,element.downvotes - 1)
				elif interaction_action=="downvote":
					element.upvotes = max(0,element.upvotes - 1)
					element.downvotes = max(0,element.downvotes + 1)
				element.save()
				interaction.save()
				# element = models.PublishedAlgos.objects.get(publishing_uuid = element_uuid)
				return JsonResponse({"status":"success","upvotes":element.upvotes,"downvotes":element.downvotes,"score":element.score})
			except DoesNotExist:
				return JsonResponse({"status":"error","error":"Published algo for not found","error_msg":"Published algo for not found"})
			except:
				print(traceback.format_exc())
		except:
			print(traceback.format_exc())
	return JsonResponse({"status":"error","error":"Unexpected error","error_msg":"Unexpected error"})