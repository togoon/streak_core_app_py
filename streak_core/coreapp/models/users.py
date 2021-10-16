from __future__ import unicode_literals

from mongoengine import *
import datetime
import hashlib
from django.utils import timezone
import random
import string
import os,base64

class UserProfile(Document):
	"""Schema for User profile"""
	user_uuid = StringField(max_length=500, required=True)
	first_name = StringField(max_length=100, required=True)
	last_name = StringField(max_length=100, required=True)

	phone_regex = r'^\+?1?\d{9,15}$'
	phone_number = StringField(max_length=15)
	# phone_number = StringField(regex=phone_regex,max_length=15)
	email = StringField(max_length=50, required=True, unique=True)

	password = StringField(max_length=100,required=True)#,unique=True)
	status = IntField(default=0)
	user_broker_id = StringField(max_length=20)
	
	last_ip = StringField(max_length=40,default='')
	brower_cookie = StringField(max_length=200,default='')
	country = StringField(max_length=5,default='')
	country_code = StringField(max_length=5,default='')

	first_login = BooleanField(default=True)

	terms_accepted = BooleanField(default=False)
	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)
	last_login = DateTimeField(required=False,default=datetime.datetime.now) 
	additional_details = DictField(default={})
	publisher = BooleanField(default=False)
	
	first_broker = StringField(default="zerodha")
	# broker_account_type = StringField(default="B2C")
	# brokers_list = ListField(default=[])
	# onboarding 
	onboarding = DictField(default={'status':'beginner',# beginner intermediate pro expert
									'first_algo':False,
									'first_2fa':False,
									'first_account_added':False})
	login_count = IntField(default=0)
	publisher = BooleanField(default=False)
	user_credits = FloatField(default=0)
	# publisher_name = StringField(default="",max_length=50)
	# publisher_bio = StringField(default="",max_length=500)
	profile_basic_complete = BooleanField(default=False)

	ref_id = StringField(max_length=50, required=True,default="")
	short_link = StringField(max_length=100, required=True,default="")
	
	total_credits = FloatField(default=0)
	used_credits = FloatField(default=0)
	available_credits = FloatField(default=0)
	otp_secret = StringField(max_length=20,default='')
	verification_status = BooleanField(default=False)

	def __unicode__(self):
		return self.email

	def check_password(self,raw_password):
		import hashlib

		hsh_passwd = self.password

		salt = ''

		print hashlib.sha1(raw_password).hexdigest()
		if hsh_passwd == hashlib.sha1(raw_password).hexdigest():
			return True
		return False

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(UserProfile,self).save(*args, **kwargs)

class DirectUserProfile(Document):
	"""Schema for User profile"""
	user_uuid = StringField(max_length=500, required=True)
	user_id = StringField(max_length=500, required=True,default="") # user_id
	first_name = StringField(max_length=50, required=False,default="")
	last_name = StringField(max_length=50, required=False,default="")

	phone_regex = r'^\+?1?[\d+-]{9,15}$'
	phone_number = StringField(max_length=15,required=False,default="")
	# phone_number = StringField(regex=phone_regex,max_length=15)
	email = StringField(max_length=50, required=True, unique=True)

	password = StringField(max_length=100,required=False)#,unique=True)
	status = IntField(default=0)
	user_broker_id = StringField(max_length=20,required=False)
	
	last_ip = StringField(max_length=40,default='')
	brower_cookie = StringField(max_length=200,default='')
	verification_status = BooleanField(default=False)
	terms_accepted = BooleanField(default=False)
	first_login = BooleanField(default=True)
	otp_secret = StringField(max_length=20,default='')
	addition_details = DictField(default={})
	country = StringField(max_length=5,default='')
	country_code = StringField(max_length=5,default='')

	# onboarding 
	onboarding = DictField(default={'status':'beginner',# beginner intermediate pro expert
									'first_algo':False,
									'first_2fa':False,
									'first_account_added':False})
	login_count = IntField(default=0)
	publisher = BooleanField(default=False)
	user_credits = FloatField(default=0)
	# publisher_name = StringField(default="",max_length=50)
	# publisher_bio = StringField(default="",max_length=500)
	profile_basic_complete = BooleanField(default=False)

	ref_id = StringField(max_length=50, required=True,default="")
	short_link = StringField(max_length=100, required=True,default="")
	
	total_credits = FloatField(default=0)
	used_credits = FloatField(default=0)
	available_credits = FloatField(default=0)

	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	meta = {
		'indexes': [
			{'fields': ('user_uuid','user_broker_id','email')}
		]
	}

	def __unicode__(self):
		return self.email

	def check_password(self,raw_password):
		import hashlib

		hsh_passwd = self.password

		salt = ''

		return hsh_passwd==hashlib.sha1(raw_password).hexdigest()
		if hsh_passwd == hashlib.sha1(raw_password).hexdigest():
			# print ';reutlkjdlkasjldkj',True
			return True
		return False

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(DirectUserProfile,self).save(*args, **kwargs)

class UserFunds(Document):
	user_uuid = StringField(max_length=500, required=True)
	funds_object = DictField(default={})
	created_at = DateTimeField(default=datetime.datetime.now)
	updated_at = DateTimeField(default=datetime.datetime.now)

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(UserFunds,self).save(*args, **kwargs)

	# def update_one(self, *args, **kwargs):
	# 	if not self.created_at:
	# 		self.created_at = datetime.datetime.now()
	# 	self.updated_at = datetime.datetime.now()
	# 	return super(UserFunds,self).save(*args, **kwargs)

class UserDeviceToken(Document):
	user_uuid = StringField(max_length=500, required=True)
	device_tokens = DictField(default={'android':[],'ios':[],'web':[]})

	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(UserDeviceToken,self).save(*args, **kwargs)
		

class UserActivity(Document):
	user_uuid = StringField(max_length=500, required=True,unique=True)
	login_count = IntField(default=0)

	algorithms = IntField(default=0)
	backtests = IntField(default=0)
	screeners = IntField(default=0)
	orders = IntField(default=0)
	deployments = IntField(default=0)
	notifications = IntField(default=0)
	alerts = IntField(default=0)
	profile_pic_changed = IntField(default=0)
	phone_number_added = IntField(default=0)
	trial_count = IntField(default=0)
	shares = IntField(default=0)
	referrals = IntField(default=0)
	subscriptions = IntField(default=0)
	subscription_validity = DateTimeField()
	subscription_type = IntField(default=0)
	subscription_period = StringField(default="0")
	demo_requested = IntField(default=0)
	demo_request_date = DateTimeField()
	demo_schedule_date = DateTimeField()
	
	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(UserActivity,self).save(*args, **kwargs)

class UserSessionLog(Document):
	user_uuid = StringField(max_length=500, required=True)
	login_count = IntField(default=0)
	login_ip = StringField(default="")
	device = StringField(default="")
	login_time = DateTimeField(default=datetime.datetime.now)

	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		self.last_login_time = datetime.datetime.now()
		self.login_count = self.login_count + 1
		return super(UserSessionLog,self).save(*args, **kwargs)
		
class UserVerification(Document):
	"""Schema for User verification"""
	user_uuid = StringField(max_length=500, required=True)
	activation_key = StringField(max_length=40, blank=True)
	otp_key = StringField(max_length=6,blank=True)
	used = BooleanField(default=True)
	key_expires = DateTimeField(default=timezone.now)

	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(UserVerification,self).save(*args, **kwargs)

class DirectUserEmailVerification(Document):
	"""Schema for User verification"""
	user_uuid = StringField(max_length=500, required=True)
	activation_key = StringField(max_length=100, blank=True)
	otp_key = StringField(max_length=4,blank=True)
	salt = StringField(max_length=5,blank=True)
	used = BooleanField(default=True)
	key_expires = DateTimeField(default=timezone.now)

	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(DirectUserEmailVerification,self).save(*args, **kwargs)

class DirectPasswordReset(Document):
	"""docstring for DirectPasswordReset"""
	user_uuid = StringField(max_length=500, required=True)
	activation_key = StringField(max_length=100, blank=True)
	salt = StringField(max_length=5,blank=True)
	otp_key = StringField(max_length=4,blank=True)
	used = BooleanField(default=True)
	key_expires = DateTimeField(default=timezone.now)

	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(DirectPasswordReset,self).save(*args, **kwargs)
		
class ExchangeAccount(Document):
	user_uuid = StringField(max_length=500, required=True)
	account_service_name = StringField(max_length=200,default='')# exchnage or wallet names

	account_type = StringField(max_length=20,default='exch')

	account_name = StringField(max_length=200,default='')
	
	api_key = StringField(max_length=200,default='')
	api_secret = StringField(max_length=200,default='')
	passphrase = StringField(max_length=200,default='')
	
	public_key = StringField(max_length=200,default='')
	
	account_type = StringField(max_length=20,default='')
	
	# OAuth params
	access_token = StringField(max_length=200,default='')
	public_token = StringField(max_length=200,default='')
	refresh_token = StringField(max_length=200,default='')
	
	user_broker_id = StringField(max_length=20,default='')
	params_being_used = StringField(max_length=20,required=True,default='')

	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	meta = {
		'indexes': [
			{'fields': ('user_uuid','account_service_name')}
		]
	}

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(ExchangeAccount,self).save(*args, **kwargs)

class BrokerSession(Document):
	user_uuid = StringField(max_length=500, required=True)
	access_token = StringField(max_length=200)
	public_token = StringField(max_length=200)
	refresh_token = StringField(max_length=200,default='')
	user_broker_id = StringField(max_length=20)

	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(BrokerSession,self).save(*args, **kwargs)

class UserSubscription(Document):
	user_uuid = StringField(max_length=100,required=True,unique=True)
	user_broker_id = StringField(max_length=100,default='')
	subscription_uuid = StringField(max_length=100,required=True,unique=True)
	subscription_type = IntField(default=0)
	# 0 = Free trial
	# 1 = Monthly paid subscription
	subscription_product = StringField(default="free")
	# subscription product can be of type free trial or Monthly subscription
	subscription_plan = StringField(default="free")
	subscription_price = FloatField(default=0)
	subscription_tax = FloatField(default=0)
	subscription_total_price = FloatField(default=0)
	# subscription_total = FloatField(default=0)
	# subscription product can be of type free trial plan or Monthly subscription plan
	subscription_validity = DateTimeField(required=True)
	latest_subscription_id = StringField(max_length=100)
	subscription_instance = StringField(default="first")
	# can be trial, first, autorenewal, restart 
	subscription_active = BooleanField(default=False)
	# if subscription is active, then autorenewal is true
	renew_plan = StringField(default="")
	renew_plan_type = IntField(default=-1)

	subscription_period = StringField(default="1")
	payment_uuid = StringField(max_length=100,default="")

	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	# meta = {
	# 	'indexes': [
	# 		{'fields': ('user_uuid')}
	# 	]
	# }

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(UserSubscription,self).save(*args, **kwargs)

class UserSubscriptionLog(Document):
	user_uuid = StringField(max_length=100,required=True)
	subscription_uuid = StringField(max_length=100,required=True)
	subscription_log_uuid = StringField(max_length=100,required=True)
	user_broker_id = StringField(max_length=100,default='')
	subscription_type = IntField(default=-1)
	subscription_product = StringField(default="free")
	subscription_plan = StringField(default="free")
	subscription_instance = StringField(default="first")
	# can be first, autorenewal, restart 
	subscription_payment_method = StringField(default="zerodha")
	subscription_period = StringField(default="1")
	payment_uuid = StringField(max_length=100,default="")
	subscription_price = FloatField(default=0)
	subscription_tax = FloatField(default=0)
	subscription_total_price = FloatField(default=0)
	subscription_promotion = StringField(default='')
	subscription_start = DateTimeField(required=True)
	subscription_stop = DateTimeField(required=True)
	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	meta = {
		'indexes': [
			{'fields': ('user_uuid','subscription_uuid')}
		]
	}

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(UserSubscriptionLog,self).save(*args, **kwargs)

class UserSubscriptionPayment(Document):
	user_uuid = StringField(max_length=100,required=True)
	subscription_uuid = StringField(max_length=100,required=True)
	# subscription_log_uuid = StringField(max_length=100,required=True,default='')
	payment_uuid = StringField(max_length=100,required=True)
	user_broker_id = StringField(max_length=100,default='')
	# can be first, autorenewal, restart 
	subscription_payment_method = StringField(default="") # payment gateway name
	subscription_payment_type = StringField(default="") # order / subscription
	subscription_response = DictField(default={})
	subscription = DictField(default={})
	payment_data = DictField(default={})
	customer = DictField(default={})
	payment_status = IntField(default=0)
	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	meta = {
		'indexes': [
			{'fields': ('user_uuid','user_broker_id','subscription_uuid')}
		]
	}

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(UserSubscriptionPayment,self).save(*args, **kwargs)

class SignUpRequest(Document):
	"""docstring for SignUpRequest"""
	full_name = StringField(max_length=100,required=True,default='')
	phone_regex = r'^\+?1?\d{9,15}$'
	phone_number = StringField(max_length=15,default='',unique=True)
	# phone_number = StringField(regex=phone_regex,max_length=15)
	email = StringField(max_length=50,required=True)
	allowed = BooleanField(max_length=50, required=True,default=False)
	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(SignUpRequest,self).save(*args, **kwargs)

class UserFeedback(Document):
	user_uuid = StringField(max_length=100,required=True)
	reason = StringField(max_length=200,default="")
	note = StringField(max_length=500,default="")
	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(UserFeedback,self).save(*args, **kwargs)

class ReferralUsers(Document):
	"""docstring for ClassName"""
	ref_id = StringField(max_length=50, required=True)

	user_uuid = StringField(max_length=100,required=True,unique=True)
	email = StringField(max_length=50, required=True, unique=True)
	ref_uuid = StringField(max_length=100,required=True, unique=True) # referral uuid
	ref_first_name = StringField(max_length=50, required=False,default="")
	ref_last_name = StringField(max_length=50, required=False,default="")
	ref_source = StringField(max_length=25, required=False,default="")
	ref_device = StringField(max_length=25, required=False,default="")
	ref_status = IntField(default=0)
	referral_rewards = ListField(default=[])
	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(ReferralUsers,self).save(*args, **kwargs)

class ReferralRewards(Document):
	"""docstring for ReferralRewards"""
	ref_id = StringField(max_length=50, required=True)
	
	user_uuid = StringField(max_length=100,required=True)
	ref_code = StringField(max_length=50, required=True,unique=True)
	status = IntField(default=0)
	claimed = BooleanField(default=False)
	claimed_msg = StringField(default='')
	claimed_desc = StringField(default='')
	credit_type = IntField(default=0)
	credits = FloatField(default=0)

	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(ReferralRewards,self).save(*args, **kwargs)
		
class DirectUserSyncContacts(Document):
	"""docstring for DirectUserSyncContacts"""
	user_uuid = StringField(max_length=100,required=True,unique=True)
	contacts_list = ListField(default=[])
	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(DirectUserSyncContacts,self).save(*args, **kwargs)