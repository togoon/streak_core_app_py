from mongoengine import *
import datetime
from django.utils import timezone

class Screener(Document):
	"""Schema for Algorithm"""
	user_uuid = StringField(max_length=500, required=True)
	screener_uuid = StringField(max_length=500, required=True,unique=True)
	screener_name = StringField(max_length=500, required=True)
	screener_first_name = StringField(max_length=500, default="")
	screener_desc = StringField(max_length=500, required=True)

	screener_logic = StringField(max_length=50000, required=True)
	# exit_logic = StringField(max_length=5000, required=True)
	time_frame = StringField(max_length=10,default='hour')

	universe = StringField(max_length=500)

	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	screener_state = DictField(required=False)
	screener_result = ListField(required=False)
	status = IntField(default=0, required=False) #status => 0=created, 1=Live,
	chart_type = StringField(max_length=20,default='candlestick',required=False)
	owner = StringField(max_length=20,default='',required=False)
	
	sample = BooleanField(default=False)
	predefined = BooleanField(default=False)
	basket_name = StringField(max_length=100,default="")
	basket_symbols = ListField(default=[])
	tags = ListField(StringField())

	complete = BooleanField(default=True) 
	percent_complete = IntField(default=100)

	meta = {
    'indexes': [
        {'fields': ('user_uuid','screener_uuid'), 'unique': True}
    	]
	}

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(Screener, self).save(*args, **kwargs)

class ScreenerAlert(Document):
	user_uuid = StringField(max_length=500, required=True)
	screener_uuid = StringField(max_length=500, required=True)
	alert_uuid = StringField(max_length=500, required=True,unique=True)
	status = IntField(default=0, required=False)
	screener_logic = StringField(max_length=6000, required=True)
	chart_type = StringField(max_length=20,default='candlestick',required=False)
	universe = StringField(max_length=500)
	time_frame = StringField(max_length=10,default='hour')
	periodicity = StringField(max_length=10,default='hour')
	screener_name = StringField(max_length=500, required=True)
	new_symbols = ListField(required=False)
	results = ListField(required=False)
	basket_name = StringField(max_length=100,default="")
	basket_symbols = ListField(default=[])
	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(ScreenerAlert, self).save(*args, **kwargs)