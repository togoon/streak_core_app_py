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
import string
import json
import requests
from mongoengine import ValidationError,NotUniqueError
import os
from django.views.decorators.clickjacking import xframe_options_exempt
from coreapp.views.ams_helper import override_with_ams

def help(request):
	return render(request,'help.html',{})

def alerts(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	if user_uuid=='' or not user_is_auth:
		return redirect('home')
	return render(request,'alerts.html',{})

def trading_terms(request):
	return render(request,'trading_terms.html',{})

def app_trading_terms(request):
	return render(request,'app_trading_terms.html',{})

def terms(request):
	return render(request,'terms.html',{})

def backtest_webview(request):
	return render(request,'backtest_webview.html',{})

def app_terms(request):
	return render(request,'app_terms.html',{})

def disclosure(request):
	return render(request,'disclosure.html',{})

def app_disclosure(request):
	return render(request,'app_disclosure.html',{})

def privacy(request):
	return render(request,'privacy.html',{})

def app_privacy(request):
	return render(request,'app_privacy.html',{})

def milestones052018(request):
	return render(request,'milestones052018.html',{})

def milestones072018(request):
	return render(request,'milestones072018.html',{})

def backtest_graph(request):
	return render(request,'backtest_graph.html',{})

def chart(request):
	return render(request,'chart.html',{})

def mobile_landing(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	if user_uuid!='' and user_is_auth:
		return redirect('mobile_alerts')
	return render(request,'mobile_landing.html',{})

def lead_generation(request):
	print request.META.items()
	return render(request,'lead_generation.html',{})

def save_lead(request):
	if request.method!='POST':
		return JsonResponse({'status':'error','error':'method'})
	print(request.POST)
	full_name = request.POST.get('full_name','')
	if full_name.strip() == "":
		full_name = request.POST.get('name','')
	email = request.POST.get('email','')
	phone_number = request.POST.get('phone_number','');
	if(full_name!='' and email!='' and phone_number!=''):
		#stuff
		m = models.SignUpRequest(full_name=full_name,
							phone_number=phone_number,
							email=email)
		try:
			url = "https://signup.zerodha.com/api/partner/lead/register/"
			headers = {
			   'Content-Type': "application/json",
			}
			data = {
			    "name": full_name, # Name of the client. Required
			    "mobile": phone_number, # Client mobile number. Required
			    "email": email,      # Client email Required
			    "partner": "ZMPEWY",      # partner
			    "source": "https://www.streak.tech/signup/",      # Client email Required
			}
			response = requests.post(url, headers=headers, data=json.dumps(data))
			m.save()
			if(response.status_code==400):
				return JsonResponse({'status':'error','error':'inputs','msg':'Your account details already registered, try login with your Kite ID.'})

			print('Lead User registered',full_name,phone_number,email,response.status_code)
			return JsonResponse({'status':'success','msg':'Sign up successful, we will get in touch with you shortly'})
		except ValidationError:
			return JsonResponse({'status':'error','error':'inputs','msg':'Wrong phone number format'})
		except NotUniqueError:
			return JsonResponse({'status':'error','error':'inputs','msg':'Details already submitted'})
		except:
			return JsonResponse({'status':'error','error':'inputs','msg':'Unkown error, please try again'})

	else:
		return JsonResponse({'status':'error','error':'inputs','msg':'Incomplete inputs'})
	return JsonResponse({'status':'error','error':'inputs','msg':'Incomplete inputs'})

def save_profile_change(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth'})

	if request.method!='POST':
		return JsonResponse({'status':'error','error':'method'})

	full_name = request.POST.get('full_name','')
	email = request.POST.get('email','')
	phone_number = request.POST.get('phone_number','');

	date = request.POST.get('day','');
	month = request.POST.get('month','');
	year = request.POST.get('year','');
	street_address = request.POST.get('street_address','');
	country = request.POST.get('country','');
	if(phone_number!=''):
		#stuff
		try:
			u = models.UserProfile.objects.get(user_uuid=user_uuid)
			u.phone_number = phone_number
			u.addition_details = {'date':date,'month':month,'year':year,'country':country,'street_address':street_address}
			u.save()
			return JsonResponse({'status':'success'})
		except ValidationError:
			return JsonResponse({'status':'error','error':'inputs','msg':'Wrong phone number format'})
		except NotUniqueError:
			return JsonResponse({'status':'error','error':'inputs','msg':'Details already submitted'})
		except:
			print traceback.format_exc()
			return JsonResponse({'status':'error','error':'inputs','msg':'Unkown error, please try again'})

	else:
		return JsonResponse({'status':'error','error':'inputs','msg':'Incomplete inputs'})
	return JsonResponse({'status':'error','error':'inputs','msg':'Incomplete inputs'})

def whats_new(request):
	conn = get_redis_connection("default")
	content = conn.get('whats_new')
	try:
		resp = json.loads(content)
	except:
		resp = {
		'app':{
			'title':'',
			'title_img':'',
			'content':[
				{	'msg':'',
					'link':'',
					'img':''
				}
			],
			'tag':''
			},
		'site':{
			'title':'',
			'title_img':'',
			'content':[
				{	'msg':'',
					'link':'',
					'img':''
				}
			],
			'tag':''
			}
		}
	return JsonResponse(resp)

def whats_new2(request):
	conn = get_redis_connection("default")
	content = conn.get('whats_new2')
	try:
		resp = json.loads(content)
	except:
		resp = {'web': {'data': [],'img':''}, 'app': {'data': [],'img': ''}}
	return JsonResponse(resp)

@override_with_ams
def whats_new3(request):
	conn = get_redis_connection("default")
	content = conn.get('whats_new3')
	try:
		resp = json.loads(content)
	except:
		resp = {'web': {'data': [],'img':''}, 'app': {'data': [],'img': ''}}
	return JsonResponse(resp)

def fetch_total_backtest(request):
	conn = get_redis_connection("default")
	content = conn.get('streak_total_backtest_count')
	try:
		resp = {'status':'success','total_backtest_count':int(str(content))}
	except:
		resp = {'status':'success',
		'total_backtest_count':10208618
		}
	return JsonResponse(resp)

def fetch_total_backtest_days(request):
	conn = get_redis_connection("default")
	content = conn.get('streak_total_backtest_days')
	try:
		resp = {'status':'success','total_backtest_days':int(str(content))}
	except:
		resp = {
		'status':'success',
		'total_backtest_days':1771313649
		}
	return JsonResponse(resp)

def fetch_total_order_amount(request):
	conn = get_redis_connection("default")
	content = conn.get('streak_total_order_amount')
	try:
		resp = {'status':'success','total_order_amount':int(str(content))}
	except:
		resp = {'status':'success',
		'total_order_amount':17030423849
		}
	return JsonResponse(resp)

def fetch_total_index_metrics(request):
	conn = get_redis_connection("default")
	total_backtest_count = conn.get('streak_total_backtest_count')
	total_backtest_days = conn.get('streak_total_backtest_days')
	total_order_amount = conn.get('streak_total_order_amount')
	try:
		resp = {'status':'success',
		'total_backtest_count':int(str(total_backtest_count)),
		'total_backtest_days':int(str(total_backtest_days)),
		'total_order_amount':int(str(total_order_amount))}
	except:
		resp = {'status':'success',
		'total_backtest_count':5111111,
		'total_backtest_days':783093089,
		'total_order_amount':5324842087
		}
	return JsonResponse(resp)

js_parsing_tree = None 
with open(os.path.dirname(os.path.abspath(__file__))+'/../../coreapp/static/js_parsing_tree.json') as parsing_tree_file:	 
	js_parsing_tree = json.load(parsing_tree_file)
 
def fetch_parsing_tree(request): 
	user_uuid = request.session.get('user_uuid','') 
	user_is_auth = request.session.get('user_is_auth',False) 
	# if settings.DEBUG: 
	if settings.ENV == "local" or settings.ENV == 'local1': 
		user_uuid = '123' 
		user_is_auth = True 
	if not user_is_auth: 
		return JsonResponse({"status":"error","error":"auth"},status=401) 
	js_parsing_tree['status']='success'
	return JsonResponse(js_parsing_tree) 

js_parsing_tree2 = None 
with open(os.path.dirname(os.path.abspath(__file__))+'/../../coreapp/static/js_parsing_tree2.json') as parsing_tree_file2:	 
	js_parsing_tree2 = json.load(parsing_tree_file2)

def fetch_parsing_tree2(request): 
	user_uuid = request.session.get('user_uuid','') 
	user_is_auth = request.session.get('user_is_auth',False) 
	# if settings.DEBUG: 
	if settings.ENV == "local" or settings.ENV == 'local1': 
		user_uuid = '123' 
		user_is_auth = True 
	if not user_is_auth: 
		return JsonResponse({"status":"error","error":"auth"},status=401) 
	js_parsing_tree2['status']='success'
	return JsonResponse(js_parsing_tree2) 

def apple_app_site_association(request): 
	user_uuid = request.session.get('user_uuid','') 
	user_is_auth = request.session.get('user_is_auth',False) 
	# if settings.DEBUG: 
	if settings.ENV == "local" or settings.ENV == 'local1': 
		user_uuid = '123' 
		user_is_auth = True 
	# if not user_is_auth: 
	# 	return JsonResponse({"status":"error","error":"auth"},status=401) 
	resp = {
		"applinks": {
		"apps": [],
		"details": [
		 {
		   "appID": "W9TX2B2J74.tech.streak.trade",
		   "paths": [ "*" ]
		 }
		]
		}
	}

	return JsonResponse(resp)
 
def fetch_trainer_model(request): 
	user_uuid = request.session.get('user_uuid','') 
	user_is_auth = request.session.get('user_is_auth',False) 
	# if settings.DEBUG: 
	if settings.ENV == "local" or settings.ENV == 'local1': 
		user_uuid = '123' 
		user_is_auth = True 
	if not user_is_auth: 
		return JsonResponse({"status":"error","error":"auth"},status=401) 
	conn = get_redis_connection("default") 
	trainer_knowledgebase = conn.get('trainer_indicator_tree') 
	if trainer_knowledgebase==None: 
		trainer_knowledgebase = "{}" 
	return JsonResponse(json.loads(trainer_knowledgebase)) 

def fetch_sctrainer_model(request): 
	user_uuid = request.session.get('user_uuid','') 
	user_is_auth = request.session.get('user_is_auth',False) 
	# if settings.DEBUG: 
	# if settings.ENV == "local" or settings.ENV == 'local1': 
	# 	user_uuid = '123' 
	# 	user_is_auth = True 
	# if not user_is_auth: 
	# 	return JsonResponse({"status":"error","error":"auth"},status=401) 
	conn = get_redis_connection("default") 
	trainer_knowledgebase = conn.get('trainer_screener_indicator_tree') 
	if trainer_knowledgebase==None: 
		trainer_knowledgebase = "{}" 
	return JsonResponse(json.loads(trainer_knowledgebase)) 
	
def accept_terms(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth','error_msg':'auth'})

	if request.method=='POST':
		try:
			user = models.UserProfile.objects.get(user_uuid=user_uuid)
			user.terms_accepted = True
			user.save()
			request.session.pop('terms_accepted','')
			return JsonResponse({'status':'success'})

		except:
			return JsonResponse({'status':'error','error_msg':'User not found','error':'method'})
	return JsonResponse({'status':'error','error':'method','error':'method'})

@xframe_options_exempt
def fetch_terms_of_service(request):
	if request.GET.get("broker","zerodha")=="ab":
		return render(request,'terms_of_service_ab.html')
	return render(request,'terms_of_service.html')

def fetch_terms(request):
	user_uuid = request.session.get('user_uuid','')
	user_is_auth = request.session.get('user_is_auth',False)
	# if settings.DEBUG:
	if settings.ENV == "local" or settings.ENV == 'local1':
		user_uuid = '123'
		user_is_auth = True
	if not user_is_auth:
		return JsonResponse({"status":"error",'error-type':'auth','error_msg':'auth'})

	if request.method!='GET':
		return JsonResponse({'status':'error','error':'method','error':'method'})

	terms_heading = "Agreement / Terms of Use, Risk Disclosure Statement, and Disclaimers"
	terms = """INTRODUCTION
Welcome to Streak.tech, an extension to Kite - Zerodha's exchange approved trading platform.
Streak.tech is provided by Streak AI Technologies Pvt. Ltd, a web-based platform to create, backtest and deploy trading algorithms.
AGREEMENT / Terms of USE.
These Terms of Use constitute a legally binding agreement between Streak AI Technologies Pvt. Ltd. provider of streak.tech, "us" or "we" and you ("you"), the individual logging in through Zerodha's Kite account, sets forth the terms and conditions that govern your use of Streak.tech (the "Site" or " Mobile App" Together referred as Platform) and/or any related services (the "Services") accessed through the Streak platform.
We refer to these Terms of Use as the "Agreement." We may update or amend these Terms of Use from time to time by posting such updates or amendments to the Site. Your use of the Site after we post any such updates or amendments will constitute your agreement to those updates or amendments.
THIS AGREEMENT REQUIRES THE USE OF ARBITRATION ON AN INDIVIDUAL BASIS TO RESOLVE DISPUTES, RATHER THAN JURY TRIALS OR CLASS ACTIONS, AND ALSO LIMITS THE REMEDIES AVAILABLE TO YOU IN THE EVENT OF A DISPUTE.
PLEASE CAREFULLY READ THESE TERMS OF USE BEFORE ACCESSING THE SITE OR USING ANY OF THE SERVICES. IF YOU DO NOT WISH TO BE BOUND BY THESE TERMS AND CONDITIONS OR IF YOU CANNOT REMAIN IN COMPLIANCE WITH SUCH TERMS AND CONDITIONS, YOU MAY NOT ACCESS THE SITE OR USE ANY OF THE SERVICES AND SHOULD IMMEDIATELY CEASE SUCH ACCESS AND USE.
 
1. Use of Services.
Unless otherwise specified, Streak AI Technologies Pvt. Ltd. grants to you a non-exclusive and non-transferable limited right and license to access the Site streak.tech or the mobile android app. which is an extension to Kite - Zerodha's exchange approved trading platform. The users of this platform need to have opened a trading and demat account in zerodha. The Services provided on this platform ( steak.tech ) is for your personal use only, provided that you agree with and comply fully with the provisions of this Agreement. Certain features of the Site or Services are available only to users who register with streak.tech via Zerodha's Kite account. The complete customer facing features of streak.tech is available only by paying a premium depending on the plans available.
You acknowledge and understand that we provide tools and infrastructure designed to allow you to create, backtest, and deploy your algorithms and algorithmic trading strategies live in the market.
To be clear, we do not provide any trading algorithms or trading strategies, rather the tools to create them and the data with which you can test and use them. You can create your own algorithms or use algorithms made available on the Site to modify them as per your needs.
Sample algo feature : Users can check the sample algos provided on the dashboard to understand the working of indicators and how to use them. Streak is not promoting any stock or indicator, this is just a sample which user on his/her own accord is responsible if used	and which results in any profits/losses occurred after deploying sample algos in the market.
2. Accounts, Passwords and Security.
To become a registered user, you must login by providing Streak.tech your Zerodha Kite login credentials. We are eligible to know your current, complete and accurate personal identifiable information, including, without limitation, your real name and the email address through which we can correspond with you and the telephone number, as prompted by the applicable registration form. You further agree to keep any registration information you provide to Streak AI Technologies Pvt. Ltd. current, complete and accurate.
FURTHERMORE, YOU ARE ENTIRELY RESPONSIBLE FOR ANY AND ALL ACTIVITIES AND CONDUCT, WHETHER BY YOU OR ANYONE ELSE, THAT ARE CONDUCTED THROUGH YOUR ACCOUNT. We may hold you liable for any losses incurred by Streak AI Technologies Pvt. Ltd. or any other party due to someone else's use of your account or password. You agree to notify Streak AI Technologies Pvt. Ltd. by writing to support@streak.tech immediately upon your becoming aware of any unauthorized use of your account or any other breach of security involving your account. Streak AI Technologies Pvt. Ltd. will not be liable for any loss that you or any other party may incur as a result of someone else's use of your password or account, either with or without your knowledge.
3. Prohibited Activities.
We use the term "Content" to mean entire or partial algorithms, trading strategies, data transformations, data analysis and manipulation functions, tools, software, data, databases, text, messages, images, graphics, video files, audio files, ideas or any other information and materials. We use the term "Shared Content" to mean the Content (other than third party data) that we, you, or other Registered Users of Streak AI Technologies Pvt. Ltd. post in publicly accessible areas of the Site and Services. Third party data is subject to the terms and conditions of the provider of such data. Other than as provided at the end of this Section in respect of Shared Content, you acknowledge and agree that you will NOT:
i. Copy, modify, publish, transmit, distribute, transfer or sell, create derivative works of, or in any way exploit, any of the Content accessible through the Site not submitted or provided by you, including by use of any robot, spider, scraper, scripting, deep link or other similar automated data gathering or extraction tools, program, algorithm or methodology, unless you obtain Streak AI Technologies Pvt. Ltd.'s prior written consent; use the Site or Services to advertise, market, sell, or otherwise promote any commercial enterprise that you own, are employed by or are otherwise compensated by, either directly or indirectly; use any engine, software, tool, agent or other device or mechanism to navigate or search the Site, other than the search engines and agents available through the Service and other than generally available third party web browsers; copy, reverse engineer, reverse assemble, otherwise attempt to discover the source code, distribute, transmit, display, perform, reproduce, publish, license, create derivative works from, transfer or sell any information, software, products or services obtained through the Site or the Services; access the Site or use the Services by any means other than through Streak AI Technologies Pvt. Ltd.-provided or approved interfaces; transmit any Content that is unlawful, harmful, threatening, abusive, harassing, tortious, defamatory, vulgar, obscene, libelous, or otherwise objectionable or which may invade another's right of privacy or publicity;
ii. post or transmit any material that contains a virus, worm, Trojan horse, or any other contaminating or destructive feature; post or transmit information protected under any law, agreement or fiduciary relationship, including but not limited to proprietary or confidential information of others; use any of the Site's or Service's communications features in a manner that adversely affects the availability of its resources to other users; post or transmit any unsolicited advertising, promotional materials, "junk mail", "spam," "chain letters," "pyramid schemes" or any other form of solicitation or any non-resume information such as opinions or notices, commercial or otherwise; access or use the Site or Services to intentionally or unintentionally violate any applicable local, state, national or international law, including, but not limited to, regulations promulgated under any such law; upload or transmit any material that infringes, violates or misappropriate any patent, trademark, service mark, trade secret, copyright or other proprietary rights of any third party or violates a third party's right of privacy or publicity; manipulate or otherwise display or obstruct portions of the Site and/or the Services by using framing or similar navigational technology; register, subscribe, attempt to register, attempt to subscribe, unsubscribe, or attempt to unsubscribe, any party for any Streak AI Technologies Pvt. Ltd. product or Service if you are not expressly authorized by such party to do so;
iii. use the Site and/or the Services for any purpose that is unlawful or prohibited by these terms and conditions; use the Site or the Services in any manner that could damage, disable, overburden or impair Streak AI Technologies Pvt. Ltd.'s servers or networks, or interfere with any other user's use and enjoyment of the Site and/or the Services; attempt to gain unauthorized access to any of the Site, Services, accounts, computer systems or networks connected to Streak AI Technologies Pvt. Ltd. through hacking, password mining, brute force	or any other means; obtain or attempt to obtain any Content through any means not intentionally made available as Shared Content through the Site or the Services; or knowingly provide any Content that is false or inaccurate or will become false or inaccurate at any time.
iv. use of any third party services/software/mechanisms/tool/plugins/code injections on Streak website/app or other Streak services.
4. Investment Disclaimer.
You acknowledge and understand that the Services of Streak AI Technologies Pvt. Ltd. (Streak.tech) are not intended to supply investment, financial, tax or legal advice. The Services are not investment advice and any observations concerning any security, trading algorithm or investment strategy provided in the Services is not a recommendation to buy, sell or hold such investment or security or to make any other investment decisions. We offer no advice regarding the nature, potential value, risk or suitability of any particular investment strategy, trading algorithm, transaction, security or investment. You acknowledge and agree that any use of the Services, any decisions made in reliance on the Services, including any trading or investment decisions or strategies, are made at your own risk. If investment, trading or other professional advice is required, the services of a competent, licensed professional should be sought. No employee, agent or representative of Streak AI Technologies Pvt. Ltd. is authorized to provide any such advice pursuant to this Agreement, and any such advice, if given, is in violation of Streak AI Technologies Pvt. Ltd.'s policies, and unauthorized and hence should not be relied upon.
You are Solely Responsible for Input, Correctness, and Accuracy. The quality of the product's analysis and optimization depends on the user's inputs. After deployment, alerts have been made available in the product to ease and expedite your entry of the position, and you, as user of the system, are solely responsible for ensuring the quality of all its inputs. As such, you must carefully review all input parameters in all ways necessary to ensure their accuracy and fidelity. While there are other factors governing analysis and optimization accuracy, the quality of the product outputs depends on the accuracy of your inputs. The trades generated by the Service may increase beyond what is practical to execute, due to broker execution limits and the difficulties in executing a complex trade in an all-or-none fashion. Moreover, once the trade is executed, the management of a complex trade becomes more difficult than is normally the case. Another factor is that you may not be authorized to execute all contract types found in the solutions generated. Streak AI Technologies Pvt. Ltd. makes no representation that a solution generated by the Service can be executed and effectively monitored and managed in practice. It is entirely your responsibility to assess the appropriateness, suitability, and practicality of the solutions generated by the optimizer. It is your responsibility to ensure the trade is executable and manageable, and appropriate for your needs.
5. Cancellation Policy: Streak.tech
Subscription fee once paid is non-refundable. The billing cycle is one month which we consider as 30 days.
You will be able to cancel the monthly subscription to streak.tech by clicking on "Cancel subscription" in your billing section.
Once you cancel your subscription, you will be able to use the platform till the current billing cycle that you have been charged for. For example, if you have subscribed on the 1st of Jan 2018, you will be able to use the platform till 30 Jan 2018 and the next billing date is 31 Jan 2018. If for any reason, you decide to cancel the subscription on 19 Jan 2018 you will still be able to use the platform till 30 Jan 2018 and you will not be billed on 31 Jan 2018. As a policy we do not refund subscription fee once paid.
We bill on the first day of the billing cycle at 00:00 hours. In order to avoid getting charged for the next billing period, you need to cancel at least one day before the next billing date. All prices inclusive of taxes.
6. Intellectual property and Trademark
The Website www.streak.tech, its general structure, its create, backtest, and deploy features, as well as text, animated or non-animated images, know-how, drawings, graphics, as well as the look and feel of the site and the features of zero coding, algo trade without coding are and shall remain the exclusive property of Streak AI Technologies Pvt Ltd. You are only entitled to view information for your private use only. You may not reproduce, by any means, or process, in whole or in part, distribute, publish, transmit, create derivative works based on, modify or sell any such materials contained on the site. Any total or partial representation of this site by any process without the express authorization of the operator of the Website is prohibited and legal action will be enforced punishable by law.
Streak.tech is a patent pending technology in the US. Streak is a trademarked word in India by Streak AI Technologies Pvt Ltd. The operator of the Website Streak.tech is a patent pending technology in the US. Streak is a trademarked word in India by Streak AI technologies pvt ltd.
7. Backtesting and data.
Backtesting results are hypothetical and are simulated on historical data. The performance results have certain inherent limitations. Unlike the results shown in an actual performance record, these results do not represent actual trading. These trades have not actually been executed, these results may have under-or over-compensated for the impact especially when we have lack of liquidity in the market or news driven events or any other conditions. Simulated or hypothetical trading algos in general are also subject to the fact that they are designed with the benefit of hindsight. No representation is being made that any account will or is likely to achieve profits or losses similar to those backtested.
In addition, hypothetical trading does not involve financial risk, and no hypothetical trading record can completely account for the impact of financial risk in actual trading. For example, the ability to withstand losses or to adhere to a particular trading Algos in spite of trading losses are material points which can also adversely affect actual trading results. There are numerous other factors related to the markets in general or to the implementation of any specific Algos trading which cannot be fully accounted for in the preparation of hypothetical performance results and all of which can adversely affect actual trading results.
Chart data is subjected to minor variations from market time to post market times due to standard data adjustments.
8. Electronic Communications.
You acknowledge and understand that (a) we can only give you the benefits of accessing the Site and using the Services by conducting business through the Internet, and therefore we need you to consent to our giving you Communications (defined below) electronically, and (b) this Section informs you of your rights when receiving Communications from us electronically. For contractual purposes, you: (i) consent to receive communications from us in an electronic form and (ii) agree that all terms and conditions, agreements, notices, documents, disclosures, and other communications ("Communications") that we provide to you electronically satisfy any legal requirement that such Communications would satisfy if they were in writing. Your consent to receive Communications and do business electronically, and our agreement to do so, applies to all of your interactions and transactions with us. The foregoing does not affect your non-waivable rights.
9. Indemnification.
You agree to indemnify, defend, and hold Zerodha, the exchange (National Stock Exchange), Streak AI Technologies Pvt. Ltd the owner of streak.tech, and its subsidiaries, affiliates, officers, directors, agents, co-branders, sponsors, distributors, or other partners, employees, and representatives harmless from and against any and all claims, demands, actions, causes of action, damages, losses, costs or expenses (including reasonable attorneys' fees and disbursements) which arise or relate, directly or indirectly, out of, from or to (i) your breach of this Agreement or violation of any applicable law or regulation, (ii) any allegation that any materials that you submit to Streak AI Technologies Pvt. Ltd. infringe, misappropriate, or otherwise violate the copyright, trade secret, trademark or other intellectual property rights, or any other rights of a third party, or (iii) access or use of the Site and/or the Services by you or anyone using your Streak AI Technologies Pvt. Ltd. account. This Section shall survive in the event this Agreement is terminated for any reason.
10. Limitation of Liability.
YOU ACKNOWLEDGE AND AGREE THAT WE ARE ONLY WILLING TO PROVIDE ACCESS TO THE SITE AND TO PROVIDE THE SERVICES IF YOU AGREE TO CERTAIN LIMITATIONS OF OUR LIABILITY TO YOU AND TO THIRD PARTIES. NEITHER STREAK AI TECHNOLOGIES PVT. LTD. NOR ITS DIRECTORS, OFFICERS, EMPLOYEES, CONTRACTORS, AGENTS OR SPONSORS ARE RESPONSIBLE OR LIABLE TO YOU OR ANYONE ELSE FOR ANY LOSS OR INJURY OR ANY INDIRECT, INCIDENTAL, CONSEQUENTIAL, SPECIAL, EXEMPLARY, PUNITIVE OR OTHER DAMAGES UNDER ANY CONTRACT, NEGLIGENCE, STRICT LIABILITY OR OTHER THEORY ARISING OUT OF OR RELATING IN ANY WAY TO (I) THE USE OF, DELAYS IN OPERATION, TRANSMISSION OR RESPONSE OF, OR INABILITY TO USE THE SITE OR THE SERVICES; (II) ANY CONTENT CONTAINED ON THE SITES AND/OR THE SERVICES; (III) STATEMENTS OR CONDUCT POSTED OR MADE PUBLICLY AVAILABLE ON THE SITES AND/OR THE SERVICES; (IV) ANY PRODUCT OR SERVICE PURCHASED OR OBTAINED THROUGH THE SITES; (V) ANY ACTION TAKEN IN RESPONSE TO OR AS A RESULT OF ANY INFORMATION AVAILABLE ON THE SITES OR THE SERVICES; (VI) ANY DAMAGE CAUSED BY MISTAKES, INACCURACIES, OMISSIONS, ERRORS, INTERRUPTIONS OR LOSS OF ACCESS TO, DELETION OF, FAILURE TO STORE, FAILURE TO BACK UP, OR ALTERATION OF ANY CONTENT ON THE SITES OR THE SERVICES, OR (VII) ANY OTHER FAILURE OF PERFORMANCE OF THE SITE OR SERVICES OR OTHER MATTER RELATING TO THE SITE AND/OR THE SERVICES, IN EACH CASE WHETHER OR NOT CAUSED BY EVENTS BEYOND THE CONTROL OF OUR DIRECTORS, OFFICERS, EMPLOYEES, CONTRACTORS, AGENTS OR SPONSORS, INCLUDING, BUT NOT LIMITED TO, ACTS OF NATURE, COMMUNICATIONS LINE FAILURE, THEFT, DESTRUCTION, OR UNAUTHORIZED ACCESS TO THE SITE OR SERVICES OR CONTENT STORED THEREIN. IN NO EVENT SHALL STREAK AI TECHNOLOGIES PVT. LTD.'S TOTAL LIABILITY TO YOU FOR ANY AND ALL DAMAGES, LOSSES, AND CAUSES OF ACTION (WHETHER IN CONTRACT, TORT, STATUTORY, OR OTHERWISE) EXCEED ONE RUPEE ( RS 1.00). SOME JURISDICTIONS DO NOT ALLOW THE EXCLUSION OF CERTAIN WARRANTIES OR THE LIMITATION OR EXCLUSION OF CERTAIN TYPES OF LIABILITY. ACCORDINGLY, SOME OF THE ABOVE LIMITATIONS AND DISCLAIMERS MAY NOT APPLY TO YOU. TO THE EXTENT THAT WE MAY NOT, AS A MATTER OF APPLICABLE LAW, DISCLAIM ANY IMPLIED WARRANTY OR LIMIT LIABILITIES, THE SCOPE AND DURATION OF SUCH WARRANTY AND THE EXTENT OF OUR LIABILITY WILL BE THE MINIMUM PERMITTED UNDER SUCH APPLICABLE LAW.
11. Force majeure.
Streak AI Technologies Pvt Ltd shall not be responsible for delay or default in the performance of their obligations due to contingencies beyond their control, such as (including but not limited to) losses caused directly or indirectly by exchange or market rulings, suspension of trading, fire, flood, civil commotion, earthquake, war, strikes, failure of the systems, failure of the internet links or government/regulatory action.
12. Use of Internet.
The Client is aware and acknowledges that trading over the internet involves many uncertain factors and complex hardware, software, systems, communication lines, peripherals, etc., which are susceptible to interruptions and dislocations; and the Online Trading Service of Streak.tech may at any time be unavailable without further notice. Upon clicking on buy/sell on the order window, based on client's network speed, a network latency can be experienced, and any rapid clicks on the buy/sell button through same or different windows can lead to multiple order placements. Clients take full responsibility on making sure the actions on the notifications are their own actions and are fully aware of their positions and algo status when on the buy/sell button. Streak.tech and Zerodha do not make any representation or warranty that the Online Trading Service of Zerodha or Streak.tech will be available to the Client at all times without any interruption. The Client agrees that he shall not have any claim against the Exchange or Zerodha or Streak.tech or Streak AI technologies pvt ltd on account of any suspension, interruption, non-availability or malfunctioning of the Online Trading System or Service of Zerodha or the Exchange's service or systems for any reason whatsoever.
DISCLAIMERS 
 
Browser Notification:
The first time you login to Streak website, the web browser asks your permission to allow browser notification. Please allow the notification, else you won't be getting any alerts on your system when the algo condition is met.
Sample Algos : Users can check the sample algos provided on the dashboard to understand the working of indicators and how to use them. Streak is not responsible for any profits/losses occurred after deploying sample algos in the market
Algo alerts : Once the algo is live and an alert is generated based on the conditions in the algo, our systems attempt to deliver the alert to the user over the internet. By using this service, the user acknowledges they understand that the alerts' delivery is dependent on many factors such as the internet connection of the user, location, time of the day, server load, data availability etc. 
We recommend	users to be logged in to streak.tech, keep it open in their browser and maintain a fast uninterrupted internet connection to their devices to see the best alerts delivery. 
 
Streak relies on third party services for market data eg.	Kite ( Zerodha Trading Platform ) for ticks, OHLCV etc. If these services are down due to unforeseen circumstances or experience a down time due to various technical / non technical issues, Streak might not be able to generate and deliver the actionable alerts on time or at all.
 
Once a signal is generated, we try to send this signal to the user's device over the internet. The delivery of these alerts are subject to network conditions of the user, internet services and technical issues. 
Accurate and complete real-time price data is critical for the success of algorithmic trading. Our service providers or systems that provide data could experience failures, errors, lag, and latency which could result in missing, incorrect, or stale market data leading to no/wrong signals(alert) while triggering an alert.
All actionable order alerts are read-only market order alerts, where with a single click the user can send the order to the exchange. The actionable order alerts are made read-only in order to obtain consistency in the deployed and backtest results and to avoid any drastic increase in risk. If on any scrip / instruments such as Stock, Futures, Currency Futures etc., there is high volatility due to news based or non news based or any speculative events / positions, Streak is not responsible for higher slippages. You understand that volatility is the nature of the market. 
Upon clicking on buy/sell on the order window, based on users network speed, a network latency can be experienced and any rapid clicks on the buy/sell button through same or different windows can lead to multiple order placements. Users take full responsibility on making sure the actions on the notifications are their own actions and are fully aware of their positions and algo status when clicking on the buy/sell button.
Algo deployment cycle or Algo Cycle:
 
The algo cycle : Entry and respective exit of an algo is defined as an algo cycle.
Once an algo is deployed, the stocks are periodically tracked based on the conditions in the algo. The periodicity with which the market is tracked is the same as the candle interval selected by the user while backtesting the algo and shown in the algo summary before deployment. An algo's ideal life cycle and the tree of events that can occur during an algo's life cycle, called an "algo cycle", has been explained below: 
1. Waits for the first entry event as per the entry condition in the deployed section. 
2. Once the entry event occurs, a entry signal (buy/sell) is triggered and an actionable alert is sent to the user. 
3. The user can choose to act on the alert by clicking buy/sell or choose to ignore the alert and cancel it (canceling from the notification window will terminate the algo). 
4. If the user has clicked on buy/sell in the alert, a market order is sent to the exchange (NSE). 
5. The order will either be successfully placed by the exchange or it might get rejected due to reasons such as insufficient capital, etc. If the order gets rejected by the exchange, the algo gets terminated. Streak does not verify the margin requirement, Kite determines the margin requirement as all orders are placed on Kite.
 
6. After the successful placement of an order,	the algo immediately triggers an SL-M order. This is a STOP LOSS order which the user can place or cancel. Canceling this order will NOT terminate the algo and your positions will be open and if your Stop Loss is triggered later , then a notification is sent again to the user. ( If you have already placed the SL-M order then if the SL hits first then this order will get executed and position is closed)
 
7. The algo continues to track the stock waiting for the exit signal (SL or TP) or exit condition. Based on the entry price and the SL and TP percentages entered by the user, the SL and TP prices are calculated which are displayed to the user in the Deployed Page Subsection ENTERED .
 
8. When the SL/TP price occurs or if the exit condition is met, whichever occurs first, an actionable notification is sent to the user again. The user can then chose to act on it by clicking buy/sell or choose to ignore the alert and cancel it (cancel will terminate the algo). Note : If you cancel the SL or TP alert from the notification / alerts page the algo gets terminated. However, if you cancel the notification or alert from the order log in deployed page, the algo is not terminated.
 
9. If the user has clicked on buy/sell in the alert, a market order is sent to the exchange (NSE) and the algo's life cycle is now complete.
10. The "algo cycle" sequence defined above is an ideal sequence and is subject to market conditions and user behaviour. Based on the user's action or market conditions, the sequence might not completely occur in the same way as it is intended to, since this sequence may have been interrupted due to various reasons such as, the user stopping the algo, order rejection by the exchange, network lag, network error etc. 
11. For both intraday and overnight algos, the algo cycle has to be defined by the user during deployment. Depending on the number of algo cycles, the algo moves to a 'complete' state and is stopped. 
12. Margins are not blocked till the user acts on the actionable alerts (buy/sell) and the order is sent to the exchange. 
13.The algo can be stopped by the user at any time in the life cycle of the algo by clicking on the "Stop" button. If the algo has not entered a position, it will be directly stopped otherwise the user will be presented with an option to either stop the algo by keeping the positions open or to exit positions at market and stop the algo. The algo will no longer be tracked and no further alerts will be sent to the user for the respective algo. 
14. In cases where the user stops the algo and chooses to keep positions open, the responsibility of closing any and all positions is solely on the user, and user will get no alerts for that deployed instrument once the algo is stopped. 
15. For order type MIS, all algos will be stopped at 3:20 PM (4:30 PM for currency futures) and the open positions, if any, will be squared off by the respective broker (example, Zerodha) before market close and charges for closure by kite is applied
 
16. All actionable order alerts sent to the user can be used only once and will be active for only 5 minutes after which the alert expires in the notification/ alerts section. However, these alerts are actionable in the order log section of the Deployed Page.
 
17. All actionable alert orders are market orders and users can expect price variation from the price at which the alert was triggered to the price at which the the order is placed. Slippages are expected to occur.
 
18. If the user's order is rejected due to various reasons such as shortage of funds, circuit limit hit, no liquidity in market, etc, the algo will be stopped and no further alerts will be sent for that algo. This is done in order to avoid unnecessary tracking of instruments where the order placement failed. However, the user can deploy the algo again and take action on any new alerts that get generated.
Currency futures You can create, backtest and deploy currency futures in Streak. Each quantity corresponds to 1 lot size ie, 1000. MIS algos will be stopped at 4:30 PM and open positions, if any will be squared off.
Use of Cookies
A cookie is a small data file, often including an anonymous unique identifier that is sent from a website's computer and stored on your computer's hard drive. Use of cookies is common on the Internet. A web site can send its own cookie to your browser if your browser's preferences allow it, but (to protect your privacy) your browser permits a web site to access only the cookies it has already sent to you, not the cookies sent to you by other sites. You can configure your browser to accept all cookies, reject all cookies, or notify you when a cookie is sent. (Each browser is different, so check the "Help" menu of your browser to learn how to change your cookie preferences.) You can reset your browser to refuse all cookies or indicate when a cookie is being sent. But if you refuse cookies, some parts of the Site will not function properly and may not provide services or information you have requested. For example, without cookies, we will not be able to provide you with searches that you have asked us to save.
Our hosting services maintains its systems in accordance with reasonable industry standards to reasonably secure the information of its customers, such as using SSL encryption in certain places to prevent eavesdropping, and employing up-to-date software on the server. However, no data transmission over the Internet can be guaranteed to be 100% secure. "Perfect security" does not exist on the Internet, and you use the Site at your own risk.
Cookies Policy
The use of this website is governed by the general terms of usage of websites. In addition, Streak AI Technologies Pvt. Ltd. (Streak.tech) retains all proprietary rights over the intellectual property and information made available to the user through this website.
Streak AI Technologies Pvt. Ltd. (Streak.tech) recognizes all copyrights associated with its products and services. However, Streak AI Technologies Pvt. Ltd. (Streak.tech) does not warrant the accuracy, completeness or reliability of the information or content contained herein and made available to the user; nor will Streak AI Technologies Pvt. Ltd. (Streak.tech) be made liable for any losses incurred or investments made or other decisions taken/not taken based on the representations made or information provided hereunder.
Most browsers have an option for turning off the cookie feature, which will prevent your browser from accepting new cookies, as well as (depending on the sophistication of your browser software) allowing you to decide on acceptance of each new cookie in a variety of ways. We strongly recommend that you leave cookies active for the session on Streak.tech, because they enable you to take advantage the most attractive features of our Services.
Notifications/alerts
Push and locally scheduled notifications can provide people with timely information and provide them with the ability to take appropriate actions in response.
Email Communications
We may receive a confirmation when you open an email from us. We use this confirmation to improve our customer service.
Aggregate Information
We collect statistical information about how both unregistered and registered users, collectively, use the Services ("Aggregate Information"). Some of this information is derived from Personal Information. This statistical information is not Personal Information and cannot be tied back to you, your Account or your web browser.
IP Address Information
While we collect and store IP address information, that information is not made public. We do at times, however, share this information with our partners, service providers and other persons with whom we conduct business, and as otherwise specified in this Privacy Policy.
Information required by our app
In order to ensure proper functionality of our product on the mobile platform, the mobile application that you download from App Stores such as Google Play Store requires you to grant certain permissions for your device. This is to ensure a smooth and seamless mobile experience on your devices and these permissions may vary for different devices and OS models/versions. Some of the permissions required by our mobile applications include but are not limited to the following:
(i)android.permission.INTERNET to access internet via the app
(ii)android.permission.ACCESS_NETWORK_STATE to read internet state to check whether the user is connected to internet or not
(iii)android.permission.SYSTEM_ALERT_WINDOW to display a window on top of other apps
(iv)android.permission.WRITE_EXTERNAL_STORAGE to save user preferences and the app state to storage
(v)android.permission.READ_EXTERNAL_STORAGE to read back user preference and app state from storage
(vi)android.permission.READ_PHONE_STATE to read current cellular network information
(vii)android.permission.VIBRATE to initiate phone vibration when an alert is received by the application
Email Communications with Us
As part of the Services, you may occasionally receive email and other communications from us, such as communications relating to your Account or new features or promotional activities related to Streak.tech
Information Shared with Our Agents
We employ and contract with people and other entities that perform certain tasks on our behalf and who are under our control (our "Agents"). We may need to share Personal Information with our Agents in order to provide products or services to you. Unless we tell you differently, our Agents do not have any right to use Personal Information or other information we share with them beyond what is necessary to assist us. You hereby consent to our sharing of Personal Information with our Agents.
Information Disclosed Pursuant to Business Transfers
In some cases, we may choose to buy or sell assets. In these types of transactions, user information is typically one of the transferred business assets. Moreover, if we, or substantially all of our assets, were acquired, or if we go out of business or enter bankruptcy, user information would be one of the assets that is transferred or acquired by a third party. You acknowledge that such transfers may occur, and that any acquirer of us or our assets may continue to use your Personal Information as set forth in this policy all the data might be used for commercial purpose, etc.
Information Disclosed for Our Protection and the Protection of Others
We also reserve the right to access, read, preserve, and disclose any information as it reasonably believes is necessary to (i) satisfy any applicable law, regulation, legal process or governmental request, (ii) enforce the Terms of Service, including investigation of potential violations thereof, (iii) detect, prevent, or otherwise address fraud, security or technical issues, (iv) respond to user support requests, or (v) protect our rights, property or safety, our users and the public. This includes exchanging information with other companies and organizations for fraud protection and spam/malware prevention. 
 
Risk Disclosure Statement
INTRODUCTION
Welcome to Streak.tech, an extension to Kite - Zerodha's exchange approved trading platform. Streak.tech is provided by Streak AI Technologies Pvt. Ltd, a web-based platform to create, backtest and deploy trading algorithms.
 
Create is a process to input entry and exit conditions involving technical indicators, stop loss percentage, take profit percentage, instrument, quantity of stocks etc and form a trading strategy, hereafter referred to as "trading algo" or "algo" or "algorithms".
 
Backtesting is the process of testing a trading strategy on relevant historical data to ensure its viability before the trader risks any actual capital. A trader can simulate the trading of a strategy over an appropriate period of time and analyze the results for the levels of profitability and risk. Streak AI Technologies Pvt. Ltd. (Streak.tech) strives to give you accurate information on your trading strategies and your algorithms, however methodology covers the PROCESS AND ASSUMPTIONS THAT ARE MADE DURING CALCULATING THE RESULTS OF THE ALGO(ALGORITHM) DURING BACKTEST AND THE DATA SHOWN AFTER DEPLOYMENT.
 
In addition to the services that allow you to create and backtest a trading algo (algorithms), Streak.tech is an extension to Kite - Zerodha's exchange approved trading platform that allows you to engage in live trading through deployment feature in the platform.
 
Using Streak AI Technologies Pvt. Ltd. (Streak.tech)'s Services, including its deploy services, presents several different types of risk. We have summarized these below. You should read and understand these risks before you use any of Streak AI Technologies Pvt. Ltd. (Streak.tech)'s services.
RISKS
We as Streak, do not provide auto trading services. Any use of third party services or softwares on Streak to avail additional functionality, may cause your Streak platform to malfunction, alter expected outcomes and cause problems. As per our terms of use, we strongly suggest to avoid usasge of any third party softwares or plugins along with Streak platform (website and mobile applications).
The risks that can arise from using Streak AI Technologies Pvt. Ltd. (Streak.tech)'s Site and Services fall into three broad categories:
1. Risks inherent generally in using Internet-based technology;
2. Risks inherent in creating, backtesting, and deploying trading algorithms; and
3. Risks inherent in engaging in live algorithmic trading.
ANY PERMUTATION OR COMBINATION OF THE OCCURRENCE OF THE POTENTIAL EVENTS THAT DEFINE THE RISKS DESCRIBED IN THIS DISCLOSURE STATEMENTS CAN LEAD TO A TOTAL OR PARTIAL LOSS OF OPERABILITY, RESPONSIVENESS, FUNCTIONALITY, AND FEATURES THAT COULD MATERIALLY AND ADVERSELY AFFECT YOUR USE OF WWW.STREAK.TECH OR STREAK.ZERODHA.COM.
Risks of Using Internet-based Technology - Generally
The Internet-related technological risks arising from using Streak AI Technologies Pvt. Ltd. (Streak.tech)'s Site and Services to write, test, analyze, and run trading algorithms and related trading strategies fall into three categories: (a) risks related to Streak AI Technologies Pvt. Ltd. (Streak.tech)'s software; (b) risks related to Streak AI Technologies Pvt. Ltd. (Streak.tech)'s computing and communications infrastructure; and (c) risks related to your software, hardware, and Internet connectivity. It is your obligation to thoroughly and appropriately test any trading algorithm before you deploy it and to continually monitor the operation of any deployed trading algorithm to ensure it is running properly and in compliance with any applicable rules.
 
a. Streak AI Technologies Pvt. Ltd. (Streak.tech)'s software/ code might fail to work properly.
i. All software is subject to inadvertent programming errors and bugs embedded in the code comprising that software. Any of these errors and bugs can cause the software in which they are located to fail or not work properly. The applications software used to operate Streak AI Technologies Pvt. Ltd. (Streak.tech)'s Site and Services depends is subject to this risk. Despite testing and on-going monitoring and maintenance, inadvertent errors and bugs may still cause a failure inStreak AI Technologies Pvt. Ltd. (Streak.tech)'s applications software.
ii. We may update or revise our applications software in ways that cause some of its functionality or features to be lost or diminished. Any such loss or diminution could make Streak AI Technologies Pvt. Ltd. (Streak.tech) less valuable to you, cause certain functions and features in your algorithms to fail, and require you to change your algorithms and related trading strategies.
b.Streak AI Technologies Pvt. Ltd. (Streak.tech)'s computing and communications infrastructure may fail.
The operation of Streak AI Technologies Pvt. Ltd. (Streak.tech)'s Site and Services depend heavily on our infrastructure of computing and communications systems. The operation of this infrastructure is subject to several risks:
i. Any or all of the systems comprising our infrastructure could entirely or partially fail, function erratically, or function very slowly (thereby leading to latency, i.e., delays in receipt of and response to user requests).
ii. We may inadvertently cause a systems failure during planned or unplanned system maintenance.
iii. We may undertake software upgrades, either planned or unplanned, that take longer to implement or that causes your computer system or Internet connectivity to fail.
iv. We may change or remove functions and features whose change or removal causes your system to fail, function erratically, or function very slowly.
 
c. Your computer system and your Internet connectivity may fail.
Any of the components of your computer system and/or your Internet connectivity could fail entirely, function erratically, or function very slowly. The result of any of these occurrences could make it difficult or impossible for you to access the Streak AI Technologies Pvt. Ltd. (Streak.tech) Site or use the Streak AI Technologies Pvt. Ltd. (Streak.tech) Services.
You may incur losses (or fail to gain profits) while trading securities. You should discuss the risks of trading with the broker-dealer where you maintain an account or other investment professional. Streak AI Technologies Pvt. Ltd. (Streak.tech) provides you only with trading technology and can provide no investment, financial, regulatory, tax or legal advice.
Risks in Create, Backtest, and Deploying Algos (Algorithms)
Creating, backtesting, and deploying computer-based trading algorithms is subject to several risks, any of which can cause your algorithms to not function as you had intended or fail to achieve one or more of the objectives of your algorithms. Algorithmic trading is rapidly changing as a practice and as an industry. Models of markets used to write and test trading algorithms are inherently limited and often fail to perform as expected. In addition, trading algorithms are implemented in software programming code, and no matter how well designed and thoroughly tested, any such code can have logical errors and bugs that cause the algorithms to malfunction or suggest trades that, if executed, would result in losses. It is your obligation to thoroughly and appropriately test any trading algorithm before you deploy it and to continually monitor the operation of any deployed trading algorithm to ensure it is running properly and in compliance with any applicable rules
a. Your algorithm may be designed on the basis of an incorrect understanding of technical indicators which may not work as expected.
b. Your algorithm may contain logical errors in the way you understand the indicators and comparators.
c. Errors may exist in the data used for testing your algorithm or the applicable model of the market.
d. Your algorithm might appear to succeed in a backtesting environment using historical data, but fail when using live data.
e. Your algorithm might appear to succeed with some data sources, but fail when using other data sources in our system.
f. Your algorithm may not achieve the returns you anticipate. There are no guarantees, or even expectations, that can be made about the future behavior of an algorithm.
Risks of Engaging in Live Algorithmic Trading and Related Strategies
Streak AI Technologies Pvt. Ltd. Streak.tech and Zerodha allows you to engage in live trading. Engaging in live trading subjects you to (a) the risks associated with trading generally, and (b) the risks associated with live algorithmic trading using Streak AI Technologies Pvt. Ltd. (Streak.tech).
THE OCCURRENCE OF ANY OF THE EVENTS ASSOCIATED WITH THESE RISKS, ALONE OR IN COMBINATION WITH ANY OF THE OTHER RISKS DESCRIBED IN THIS DISCLOSURE STATEMENT, COULD RESULT IN THE LOSS OF ALL OF THE MONEY YOU HAVE DEPOSITED IN THE BROKERAGE ACCOUNT YOU USE FOR LIVE TRADING BASED ON THE ALGORITHMS YOU WRITE, TEST, AND RUN ON Streak AI Technologies Pvt. Ltd. (Streak.tech). LOSSES CAN HAPPEN MORE QUICKLY WHEN USING ALGORITHMIC TRADING THAN OTHER FORMS OF TRADING. YOU SHOULD DISCUSS WITH AN INVESTMENT PROFESSIONAL THE RISKS OF TRADING IN GENERAL AND ALGORITHMIC TRADING IN PARTICULAR. YOU USE ANY ALGORITHM IN LIVE TRADING AT YOUR OWN RISK AND IT IS YOUR OBLIGATION TO THOROUGHLY AND APPROPRIATELY TEST ANY TRADING ALGORITHM BEFORE YOU DEPLOY IT AND TO CONTINUALLY MONITOR THE OPERATION OF ANY DEPLOYED TRADING ALGORITHM TO ENSURE IT IS RUNNING PROPERLY AND IN COMPLIANCE WITH ANY APPLICABLE RULES.
Certain Risks of Live Algorithmic Trading
In addition to all of the risks described above, live algorithmic trading is subject to the following types of types of risk:
i. Backtesting Cannot Assure Actual Results.
It is not possible for a computer model to truly predict what might have happened if an algorithm-based trading strategy was in play in a live trading environment. For example, the implementation of such a strategy can itself have an impact on the market, and the model may fail to account for real-life factors that impact the model. Moreover, the model may fail to account for execution costs including broker commissions, fees, and trading slippage.
 
A promising model result does not necessarily predict a successful strategy. Execution of the algorithm and the performance of that code may prove to be impossible in a live trading environment. Changes in various market factors not foreseen in a model can change, causing a strategy to fail. A backtest might be over-fitted to past data, and fail when the strategy is applied to new, live data. Orders that were executed correctly in the backtesting environment may be disallowed or rejected because of various reasons eg: margin requirement , illiquid stocks etc causing the algorithm to fail or otherwise not perform as expected. Attempts to create, exit, or cancel orders might fail, or might result in unexpected outcomes. Moreover, your algorithm might not handle market conditions that cannot be reasonably anticipated, i.e., a "flash crash" or an exchange outage. These market conditions, by definition, will not have been tested.
ii. The relevant market might fail or behave unexpectedly.
Market centers in which you seeking to implement your trading strategy may fail or behave incorrectly because of technical reasons relating to infrastructure, connectivity, and similar factors.
Your algorithm might suffer from adverse market conditions. Those conditions can include lack of liquidity, and abrupt and unwarranted price swings. Also possible are late market openings, early market closings, market chaos, and mid-day trading pauses, and other such disruptive events.
iii. Your broker may experience failures in its infrastructure, fail to execute your orders in a correct or timely fashion or reject your orders.
Streak.tech infrastructure on which you are running your algorithm might fail. In addition, even if Streak.tech infrastructure or your broker's infrastructure and API are working correctly, the orders may get rejected in error or by design, incorrectly execute orders, or induce errors through unexpected behavior (such as returning messages out of sequence, incorrectly acknowledging orders, or posting incorrect execution reports). If at all, any losses arise from these risks, Streak AI Technologies Pvt. Ltd. (Streak.tech) bears no responsibility for this.
iv. The system you use for generating trading orders, communicating those orders to your broker, and receiving queries and trading results from your broker may fail or not function in a correct or timely manner.
Latency (i.e., delays) within and between your system, as well as those of your broker and the market in which you seeking to affect trades, might cause orders, corrections, and cancels to be placed or not placed in ways that are not desired. You may receive incorrect information, or be unable to get information, about your orders, your positions, or market conditions. Incorrect actions may be taken, or correct actions may not be taken, because of inaccurate or missing information. In addition, you may be unable to terminate or edit your algorithm.
v. Time lag at various point in live trading might cause unexpected behavior.
The time lag between the actionable alert generation time, the time at which you receive the actionable alert, and the time at which you take action on the alert, can cause a delayed order placement in the market, lead to cancellations, and cause you loss (or fail to gain profits) and may deliver unanticipated results vastly different from the backtest results.
vi. The systems of third parties in addition to those of the provider from which we obtain various services, your broker, and the applicable securities market may fail or malfunction.
Algorithmic trading depends on the availability of various services from third parties in addition to your service provider and your broker. These, for example, include providers of data services, computational services, and network connectivity. The operations of these third parties are beyond all of our reasonable control. Regardless of the reason for any failure by your broker, the market in which you seek to have trades executed, or these other third parties, we will not have any liability for any such failure.
Accurate and complete real-time price data is critical for the success of algorithmic trading. The systems of these data providers could experience failures, errors, and latency, which could result in missing, incorrect, or stale market data.
vii. Malicious and criminal activities might cause your algorithms and strategy to fail or your brokerage account to be compromised.
All computers and networks are subject to malicious "hacking" attacks and criminal activities designed to misappropriate intellectual property, compromise personally identifiable information, steal funds, or any combination of such purposes. These attacks might be attacks on a target of opportunity or specifically targeted. Each of the various systems described above that are necessary for you to engage in live algorithmic trading is subject to such attack. Any such attack could cause the system so attacked to function improperly or not at all and could result in the misappropriation of your intellectual property, the compromise of your personally identifiable information and personal financial information, the theft of your funds and can cause your algo be misbehave, malfunction or behave erratically.

	"""
	return JsonResponse({'status':'success','terms':terms,"terms_heading":terms_heading})
