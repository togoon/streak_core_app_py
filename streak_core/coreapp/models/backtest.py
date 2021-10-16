from mongoengine import *
import datetime
from django.utils import timezone

class Backtest(Document):
	"""Schema for Backtest"""
	user_uuid = StringField(max_length=500, required=True)
	algo_uuid = StringField(max_length=500, required=True)
	seg_sym = StringField(max_length=500, required=True)
	backtest_result = DictField(required=True)
	algo_obj = DictField()
	runtime = FloatField()
	updated_time = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)
	
	meta = {
		'indexes': [
			{'fields': ('user_uuid', 'algo_uuid')}
		]
	}

	def save(self, *args, **kwargs):
		# if not self.created_at:
		# 	self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(Backtest, self).save(*args, **kwargs)

class BacktestMeta(Document):
	"""Schema for Backtest"""
	user_uuid = StringField(max_length=500, required=True)
	algo_uuid = StringField(max_length=500, required=True)
	seg_sym = StringField(max_length=500, required=True)
	backtest_result = DictField(required=True)
	algo_obj = DictField()
	runtime = FloatField()
	updated_time = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)
	backtest_result_meta = DictField(required=False,default={})
	
	meta = {
		'indexes': [
			{'fields': ('user_uuid', 'algo_uuid')}
		]
	}

	def save(self, *args, **kwargs):
		# if not self.created_at:
		# 	self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(BacktestMeta, self).save(*args, **kwargs)

class ShareableBacktest(Document):
	"""Schema for Backtest"""
	backtest_share_uuid = StringField(max_length=500, required=True)
	user_uuid = StringField(max_length=500, required=True)
	algo_uuid = StringField(max_length=500, required=True)
	seg_sym = StringField(max_length=500, required=True)
	backtest_result = DictField(required=True)
	algo_obj = DictField()
	runtime = FloatField()
	updated_time = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)
	public = StringField(default='') # if no blankc then its public
	
	meta = {
		'indexes': [
			{'fields': ('user_uuid', 'algo_uuid')}
		]
	}

	def save(self, *args, **kwargs):
		# if not self.created_at:
		# 	self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(ShareableBacktest, self).save(*args, **kwargs)

class OrderLogBacktest(Document):
	"""Schema for Backtest"""
	user_uuid = StringField(max_length=500, required=True)
	algo_uuid = StringField(max_length=500, required=True)
	deployment_uuid = StringField(max_length=500, required=True, unique=True)
	backtest_result = DictField(required=True)
	algo_obj = DictField()
	updated_time = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	meta = {
		'indexes': [
			{'fields': ('user_uuid', 'algo_uuid')}
		]
	}
	
	def save(self, *args, **kwargs):
		# if not self.created_at:
		# 	self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(OrderLogBacktest, self).save(*args, **kwargs)