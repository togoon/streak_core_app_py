from mongoengine import *
import datetime
from django.utils import timezone

class Algorithm(Document):
	"""Schema for Algorithm"""
	user_uuid = StringField(max_length=500, required=True)
	algo_uuid = StringField(max_length=500, required=True,unique=True)
	algo_name = StringField(max_length=500, required=True)
	algo_fist_name = StringField(max_length=500, default="") 
	algo_desc = StringField(max_length=500, required=True)

	entry_logic = StringField(max_length=7000, required=True)
	exit_logic = StringField(max_length=7000, required=True)
	time_frame = StringField(max_length=10,default='hour')

	symbols = DictField(max_length=5000)

	position_type = IntField(min_value=None, max_value=1)
	quantity = FloatField(min_value=-10000000, max_value=10000000)

	take_profit = FloatField(max_length=0.0, min_value=0.0, required=True)
	stop_loss = FloatField(max_length=0.0, min_value=0.0, required=True)
	html_block = StringField(max_length=50000, required=True)

	min_candle_freq = IntField(max_value=1000,default=1000)
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
	create_plus = BooleanField(default=False)
	daily_strategy_cycle = StringField(max_length=20,default='-',required=False)
	max_allocation = StringField(max_length=20,default='',required=False)
	tpsl_type = StringField(max_length=20,default='pct',required=False)
	position_sizing_type = StringField(max_length=20,default='-',required=False)

	owner = StringField(max_length=500, default='', required=False)
	sample = BooleanField(default=False)

	complete = BooleanField(default=True) 
	percent_complete = IntField(default=100)
	
	meta = {
    'indexes': [
        {'fields': ('user_uuid', 'algo_name','algo_uuid'), 'unique': True}
    	]
	}

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(Algorithm, self).save(*args, **kwargs)
		