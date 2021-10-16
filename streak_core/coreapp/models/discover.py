from mongoengine import *
import datetime
from django.utils import timezone

class PublisherBio(Document):
	user_uuid = StringField(max_length=500,required=True,unique=True)
	publisher_name = StringField(max_length=500,required=True,default="",unique=True)
	publisher_bio = StringField(max_length=50000,required=True,default="")
	publisher_img_url = StringField(max_length=50000,required=True,default="")
	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)
	def save(self, *args, **kwargs):
		if not self.created_at:
				self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(SubscribedAlgosLog, self).save(*args, **kwargs)

class PublishedAlgos(Document):
	"""Schema for Algorithm"""
	user_uuid = StringField(max_length=500, required=True)
	algo_uuid = StringField(max_length=500, required=True)
	publishing_uuid = StringField(max_length=500, required=True,unique=True)
	algo_name = StringField(max_length=500, required=True)
	algo_desc = StringField(max_length=50000, required=True)

	entry_logic = StringField(max_length=50000, required=True)
	exit_logic = StringField(max_length=50000, required=True)
	time_frame = StringField(max_length=10,default='hour')

	symbols = DictField(max_length=5000)

	position_type = IntField(min_value=None, max_value=1)
	quantity = FloatField(min_value=-10000000, max_value=10000000)

	take_profit = FloatField(max_length=0.0, min_value=0.0, required=True)
	stop_loss = FloatField(max_length=0.0, min_value=0.0, required=True)
	# html_block = StringField(max_length=50000, required=True)

	min_candle_freq = IntField(max_value=1000)
	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)
	algo_state = DictField(required=False)
	algo_calc = DictField(required=False)
	status = IntField(default=0, required=False) #status => 0=created, 1=Live,
	holding_type = StringField(max_length=10,default='CNC')
	trade_time_given = StringField(default="False",required=False)
	trading_start_time = StringField(max_length=10,default='',required=False)
	trading_stop_time = StringField(max_length=10,default='',required=False)
	chart_type = StringField(max_length=20,default='candlestick',required=False)
	owner = StringField(max_length=20,default='',required=False)
	sample = BooleanField(default=False)
	create_plus = BooleanField(default=False)

	publish_status = IntField(min_value=None, max_value=2,default=0)#0 = sbumited for review, 1 published,-1 unpublished,2 featured 
	published = BooleanField(default=False)
	public = BooleanField(default=True)# True if conditions are public
	subscription_price = DictField(default={})# if {} = then free to use
	min_subscription_duration = IntField(default=30)# if {} = then free to use
	algo_obj = DictField()
	tagged_class = StringField(default="misc")
	upvotes = IntField(default=0)
	downvotes = IntField(default=0)
	score = IntField(default=0)
	total_views = IntField(default=0)


	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(PublishedAlgos, self).save(*args, **kwargs)

class PublishedBacktests(Document):
	"""Schema for Algorithm"""
	user_uuid = StringField(max_length=500, required=True)
	algo_uuid = StringField(max_length=500, required=True)
	publishing_uuid = StringField(max_length=500, required=True)
	seg_sym = StringField(max_length=500, required=True)
	backtest_result = DictField(required=True)
	algo_obj = DictField()
	runtime = FloatField()
	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)
	access_type = StringField(max_length=10, required=False,default='')

	

	def save(self, *args, **kwargs):
		# if not self.created_at:
		# 	self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(PublishedBacktests, self).save(*args, **kwargs)

class PublishedBacktestsMeta(Document):
	"""Schema for Algorithm"""
	user_uuid = StringField(max_length=500, required=True)
	algo_uuid = StringField(max_length=500, required=True)
	publishing_uuid = StringField(max_length=500, required=True)
	seg_sym = StringField(max_length=500, required=True)
	backtest_result = DictField(required=True)
	algo_obj = DictField()
	runtime = FloatField()
	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)
	access_type = StringField(max_length=10, required=False,default='')
	backtest_result_meta = DictField(required=False,default={})
	

	def save(self, *args, **kwargs):
		# if not self.created_at:
		# 	self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(PublishedBacktestsMeta, self).save(*args, **kwargs)

class SubscribedAlgos(Document):
	user_uuid = StringField(max_length=500, required=True)
	algo_uuid = StringField(max_length=500, required=True)
	publishing_uuid = StringField(max_length=500, required=True)
	algo_subscription_uuid = StringField(max_length=500, required=True,unique=True)
	algo_name = StringField(max_length=500, required=True)
	algo_desc = StringField(max_length=50000, required=True)
	subscription_date = DateTimeField(required=True)
	subscription_expiry = DateTimeField()
	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)
	algo_obj = DictField()
	subscription_active = BooleanField(default=True)
	subscription_status = IntField(default=0)
	public = BooleanField(default=False)# True if conditions are public
	# meta = {
	# 	'indexes': [
	# 		{'fields': ('user_uuid', 'algo_uuid','publishing_uuid')}
	# 	]
	# }

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(SubscribedAlgos, self).save(*args, **kwargs)

class SubscribeAlgoBacktest(Document):
	user_uuid = StringField(max_length=500, required=True)
	algo_uuid = StringField(max_length=500, required=True)
	publishing_uuid = StringField(max_length=500, required=True)
	algo_subscription_uuid = StringField(max_length=500, required=True)
	seg_sym = StringField(max_length=500, required=True)
	backtest_result = DictField(required=True)
	algo_obj = DictField()
	runtime = FloatField()
	updated_time = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)
	

	def save(self, *args, **kwargs):
		# if not self.created_at:
		# 	self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(SubscribeAlgoBacktest, self).save(*args, **kwargs)

class SubscribedAlgosLog(Document):
	user_uuid = StringField(max_length=500, required=True)
	algo_uuid = StringField(max_length=500, required=True)
	publishing_uuid = StringField(max_length=500, required=True)
	algo_subscription_uuid = StringField(max_length=500, required=True)
	algo_name = StringField(max_length=500, required=True)
	algo_desc = StringField(max_length=50000, required=True)
	subscription_date = DateTimeField(required=True)
	subscription_expiry = DateTimeField()
	subscription_status = IntField(default=0)
	payment_intent = DictField(default={})
	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	# meta = {
	# 	'indexes': [
	# 		{'fields': ('user_uuid', 'algo_uuid','publishing_uuid')}
	# 	]
	# }

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(SubscribedAlgosLog, self).save(*args, **kwargs)