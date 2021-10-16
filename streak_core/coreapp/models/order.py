from mongoengine import *
import datetime
from django.utils import timezone

class DeployedAlgorithm(Document):
	"""DeployedAlgo stores the deployed algos"""
	user_uuid =  StringField(max_length=500, required=True)
	algo_uuid = StringField(max_length=500, required=True)
	algo_name = StringField(max_length=500)
	algo_obj = DictField(default={}) 
	deployment_uuid = StringField(max_length=500, required=True,unique=True)#,db_field='id')
	segment_symbol = StringField(max_length=200, required=True)
	segment = StringField(max_length=50, required=True)
	symbol = StringField(max_length=200, required=True)
	deployment_time = DateTimeField()
	account_name = StringField(max_length=50,default='')
	exchange = StringField(max_length=50,default='')
	order_type = StringField(max_length=50,default='')
	broker = StringField(max_length=50,default='')
	expiration_time = DateTimeField()
	frequency = IntField(default=0)
	live_period = IntField(default=0)
	deployment_type = StringField(max_length=50,default='')
	created_at = DateTimeField() 
	updated_at = DateTimeField(default=datetime.datetime.now)
	status = IntField(default=0) # 0 = live , 1 = completed, -1 = force stopped
	explore_algo = BooleanField(default=False)

	meta = {
    'indexes': [
        {'fields': ('user_uuid','deployment_uuid', 'algo_uuid', 'segment_symbol', 'status'), 'unique': True}
    	],
	}

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(DeployedAlgorithm, self).save(*args, **kwargs)

class PositionsOfInstrument(Document):
	"""PositionsForAlgorithm, holds consodilated quantitites"""
	user_uuid = StringField(max_length=100, required=True)
	symbol = StringField(max_length=200, required=True)
	segment = StringField(max_length=50, required=True)
	exch = StringField(max_length=10, required=True)
	quantity = FloatField(default=0)
	avg_price = FloatField(default=0.0)
	buy_value = FloatField(default=0.0)
	sell_value = FloatField(default=0.0)
	pnl = FloatField(default=0.0)
	product = StringField(max_length=5)
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
		return super(PositionsOfInstrument, self).save(*args, **kwargs)

class HoldingsForAlgorithm(Document):
	"""HoldingsForAlgorithm stores current size of the algorithm"""
	user_uuid = StringField(max_length=500, required=True)
	algo_uuid = StringField(max_length=500, required=True)
	algo_name = StringField(max_length=500)
	segment = StringField(max_length=50, required=True)
	exchange = StringField(max_length=50, required=True,default='')
	product = StringField(max_length=5,required=True,default="MIS")
	algo_reference = ReferenceField(DeployedAlgorithm,reverse_delete_rule=CASCADE,required=True)
	symbol = StringField(max_length=200, required=True)
	deployment_uuid = StringField(max_length=500, required=True,unique=True)
	deployment_type = StringField(max_length=50,default='')
	position = DictField(default={}) 
	""" {qty:100,last_order_average_price:210,"product=MIS",
  	"validity=DAY"
	} """
	pnl = DictField(default={})
	explore_algo = BooleanField(default=False)
	""" {
	seg_sym:{final_pnl:100,returns:0.50}
	} """
	explore_algo = BooleanField(default=False)
	created_at = DateTimeField() 
	updated_at = DateTimeField(default=datetime.datetime.now)
	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(HoldingsForAlgorithm, self).save(*args, **kwargs)

class AlgorithmPerformance(Document):
	"""Algorithm Performace for deplyed algorithms"""
	user_uuid =  StringField(max_length=500, required=True)
	algo_uuid = StringField(max_length=500, required=True)
	deployment_uuid = StringField(max_length=500, required=True)
	segment_symbol = StringField(max_length=200, required=True)
	trigger_price = FloatField()
	avg_price = FloatField()
	quantity = FloatField()
	filled_quantity = FloatField()

	created_at = DateTimeField() 
	updated_at = DateTimeField(default=datetime.datetime.now)
	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(OrderLog, self).save(*args, **kwargs)

class OrderLog(Document):
	"""	Orders log storage"""
	user_uuid =  StringField(max_length=500, required=True)
	algo_uuid = StringField(max_length=500, required=True)
	deployment_uuid = StringField(max_length=500, required=True)
	deployment_type = StringField(max_length=50,default='')
	log_tag = StringField(max_length=50,required=True)
	log_message =  StringField(max_length=5000, required=True)
	extra_msg =  StringField(max_length=150, required=False)
	extra_reason =  StringField(max_length=250, required=False)
	notification_data = DictField(default={})
	created_at = DateTimeField() 
	updated_at = DateTimeField(default=datetime.datetime.now)
	explore_algo = BooleanField(default=False)
	
	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(OrderLog, self).save(*args, **kwargs)

class BrokerOrder(Document):
	"""	Orders log storage"""
	user_uuid =  StringField(max_length=500, required=True)
	algo_uuid =  StringField(max_length=500)
	algo_name =  StringField(max_length=500)
	deployment_uuid = StringField(max_length=500, required=True)
	order_id = StringField(max_length=50,required=True)
	status = StringField(default='',required=False)
	order_payload = DictField(default={})
	order_status = DictField(default={})
	created_at = DateTimeField() 
	updated_at = DateTimeField(default=datetime.datetime.now)

	meta = {
		'indexes': [
			{'fields': ('user_uuid','algo_uuid','deployment_uuid','order_id')}
		]
	}

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(BrokerOrder, self).save(*args, **kwargs)