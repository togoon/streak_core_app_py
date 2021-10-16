import traceback
import ujson
from django.http import JsonResponse

class CustomMiddleware:

	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		response = self.get_response(request)
		response['Access-Control-Allow-Credentials'] = True
		# print('origin',request.META.get('HTTP_REFERER',''))
		# if("https://api.streak.tech" == request.META.get('HTTP_REFERER','')):
		# 		# response['X-Frame-Options']="ALLOW FROM https://streak.ninja"
		# 		response.pop('X-Frame-Options')
		# if("https://api.streak.ninja" == request.META.get('HTTP_REFERER','')):
		# 		response['X-Frame-Options']="ALLOW FROM https://streak.ninja"
		return response


class CustomMiddlewareHeaderGenerator:

	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		#response = self.get_response(request)
		#print request.META.items()
		try:
			# print request.POST.items()
			pass
		except:
			print traceback.format_exc()
			pass
		try:
			correct_origin = "https://api.streak.tech"
			if('HTTP_COOKIE' in request.META.keys()):
				request.META['HTTP_COOKIE']+=';'+request.META.get('HTTP_AUTHORIZATION','')
			else:
				request.META['HTTP_COOKIE']=request.META.get('HTTP_AUTHORIZATION','')

			if('HTTP_COOKIE' in request.META.keys()):
				request.META['HTTP_COOKIE']+=';'+request.META.get('HTTP_COOKIE1','')
			else:
				request.META['HTTP_COOKIE']=request.META.get('HTTP_COOKIE1','')
			# print request.META.items()
			if('http://localhost:3000' in request.META.get('HTTP_REFERER','')) or ('http://localhost:3000' in request.META.get('HTTP_ORIGIN','')):
				request.META['X-REFERER_LOCAL'] = True
				request.META['HTTP_REFERER'] = correct_origin
			if('https://streak.tech' in request.META.get('HTTP_REFERER','')):
				request.META['HTTP_REFERER'] = correct_origin
			if('https://streak.zerodha.com' in request.META.get('HTTP_REFERER','')):
				request.META['HTTP_REFERER'] = correct_origin
			if('https://streak.angelbroking.com' in request.META.get('HTTP_REFERER','')):
				request.META['HTTP_REFERER'] = correct_origin
			if('https://r.streak.ninja' in request.META.get('HTTP_REFERER','')):
				request.META['HTTP_REFERER'] = correct_origin
			if('https://r.streak.tech' in request.META.get('HTTP_REFERER','')):
				request.META['HTTP_REFERER'] = correct_origin
			if('https://streakv3.zerodha.com' in request.META.get('HTTP_REFERER','')):
				request.META['HTTP_REFERER'] = correct_origin
			if('https://v3.streak.ninja' in request.META.get('HTTP_REFERER','')):
				request.META['HTTP_REFERER'] = correct_origin
			if('https://5paisa.streak.ninja' in request.META.get('HTTP_REFERER','')):
				request.META['HTTP_REFERER'] = correct_origin
			if('https://ab.streak.ninja' in request.META.get('HTTP_REFERER','')):
				request.META['HTTP_REFERER'] = correct_origin
			if('https://streak.5paisa.com' in request.META.get('HTTP_REFERER','')):
				request.META['HTTP_REFERER'] = correct_origin
			if('https://web.streak.ninja' in request.META.get('HTTP_REFERER','')):
				request.META['HTTP_REFERER'] = correct_origin
			if('https://web.streak.tech' in request.META.get('HTTP_REFERER','')):
				request.META['HTTP_REFERER'] = correct_origin

			if('chrome-extension://' in request.META.get('HTTP_ORIGIN','')):
				request.META['HTTP_REFERER'] = correct_origin

			# if request.method == 'OPTIONS':
			# 	resp = JsonResponse({'status': 'success'}, status=200)
			# 	resp["Access-Control-Allow-Credentials"] = "true" 
			# 	resp["Access-Control-Allow-Origin"] = "*"
			# 	resp["Access-Control-Allow-Headers"] = "*" 
			# 	resp["Access-Control-Allow-Methods"] = "*" 
			# 	return resp
		except:
			print traceback.format_exc()
			pass
		response = self.get_response(request)
		# print request.META.items()
		return response
