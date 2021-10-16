__version__ = '0.0.1'

from action import Action

class Strategy():
	"""docstring for Strategy
		Strategy class abstracts the strategy object functionality.
		These include:
			- human readable strategy string
			- eval code generation
			- position type
			- position quantity(In future should be able to take weighted mapping for symbols to the quantity or portfolio size), also figure out a way to to implement portfolio theory
			- take profit and stop loss elements
			- cover position strategy
			- cover proportion
			
		Parameters
		----------
		strategy_name : UUID, string like type
						Name of the strategy, mostly going to be the UUID
		action : Action object 
				 holding the eval code of entry and exit and human readable format of the algorithm, initial assumption in this version is that, each strategy can house only a SINGLE ACTION, later versions will be able to handle multiple actions under same strategy
			
		symbols : [], expected format = [(EXCH1,SYM1),(EXCH2,SYM2)]
			
		quantity : Integer 
				   Number of stocks/contracts to be taken in a single order, in future should be able to take weighted mapping for symbols to the quantity or portfolio size), also figure out a way to to implement portfolio theory
			
		take_profit : (Float value,'%'/'dt') like tuple 
					  Take profit tuple of type as float and string
		stop_loss : (Float value,'%'/'dt') like tuple 
					Stoploss tuple of type as float and string
		cover_proportion : Float, optional
						   1.0, used to specify the position size while taking a stoploss
	"""
	def __init__(self, strategy_name,action=None,symbols=[],quantity=0,take_profit=(None,'%'),stop_loss=(None,'%'),time_frame='day',cover_proportion=1.0):
		# super(Strategy, self).__init__()
		self.strategy_name = strategy_name
		self.action = action

		self.symbols = symbols #TODO this will contain the symbols which are part of the strategy
		self.quantity = quantity
		self.take_profit = take_profit
		self.stop_loss = stop_loss
		self.time_frame = time_frame # this will be used to fetch candle stick type of data
		self.cover_proportion = cover_proportion
		# house keeping attributes
		self.sanity_msg = []
		self.sanity = True

		self.refresh_type = time_frame # this is the time frame after which strategy needs to be checked. If it contains at price, or higher than a value then it must be a tick type, else a time_frame specified by in the strategy

	def validate_sanity(self):
		# validate sanity of strategy before running
		if self.stop_loss[0] <= 0.0:
			self.sanity_msg.append('Stop loss cannot be less than equal to 0')
			self.sanity = False

		if self.take_profit[0] <= 0.0:
			self.sanity_msg.append('Take profit cannot be less than equal to 0')
			self.sanity = False

		if not self.action.eval_generated:
			#cehck for any error during eval code generation
			self.sanity_msg+=self.action.eval_error_list

		return self.sanity

	def get_action(self):
		return self.action
