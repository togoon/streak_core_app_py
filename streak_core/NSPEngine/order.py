import sys
sys.path.append('./dist-packages/')

__version__ = '0.0.1'

from action import Action

# validate use of mathcing parsing library versions versions
import strategy_parser as sp
assert __version__ == sp.__version__

from position import Position
import math 

POS_TYPE = {'':None,'BUY':1,'SELL':-1,'HOLD':0}

class Order():
	"""Class for abstracting Orders"""
	def __init__(self,transaction_type,qty,sym,exch,commission,fixed_commission=True,price_data = None,available_capital=0.0,available_positions=0,slippage=None):
		# super(Order, self).__init__()
		self.transaction_type = transaction_type
		self.qty = qty
		self.sym = sym 
		self.exch = exch
		self.commission = commission
		self.fixed_commission = fixed_commission
		self.slippage = slippage

		self.average_price = None # must be caluclated by slippage, for now qty* price_data['close']

		self.price_data = price_data

		self.start_capital = available_capital

		self.available_positions = available_positions

		self.position = None

		self.create_position()

		self.order_status = None

	def create_position(self):
		# TODO add, slippage affect here , and create postion with partial order sized or varying prices
		position_size = self.qty*self.price_data['close']
		self.position = Position(qty = self.qty, 
									price = self.price_data['close'], 
									size = self.qty*self.price_data['close'], # can be replaced with slippage function to get new price eg: slippage.get_price(qty,price,slip_factor)
									average_price = float(position_size)/self.price_data['close'],
									sym = self.sym , 
									exch = self.exch,
									start_time=self.price_data.name, 
									stop_time=self.price_data.name,  # must also be given by slippage model
									status = 1, # opening the position
									pos_type = self.transaction_type
									)

		self.average_price = float(position_size)/self.price_data['close']

	def success(self):
		# if self.sym not in supported_sym:
		# 	return False
		# TODO , add check to see if portfolio.curr_position will become negative in any case by placing the order and avoid that.
		# TODO check for commission as well to see if they take the value negative
		# print 'self.transaction_type',self.transaction_type,'\nself.start_capital',self.start_capital,'\nself.price_data["close"] * self.qty',self.price_data['close'] * self.qty,'\nself.available_positions',self.available_positions
		if self.transaction_type == 1 and self.start_capital < self.price_data['close'] * self.qty and self.available_positions >= 0:
			# Trying to buy more than the value at hand
			# self.order_status = '1'
			# print self.start_capital,self.price_data['close'] * self.qty
			return False

		if self.transaction_type == -1:
			"""
			TODO, allow shorting positions, add features of margins, free cash
			"""
			if self.available_positions < self.qty:
				if self.start_capital < self.price_data['close'] * math.fabs(self.available_positions-self.qty):
					# trying to short more than the value at hand
					# self.order_status = '2'
					return False

			# if self.start_capital < self.price_data['close'] * self.qty and:
			# 	# trying to short more than the value at hand
			# 	return False
			# if self.available_positions < self.qty:
			# # Trying to close more than the open positions
			# 	return False

		return True

	def get_order_dict(self):
		return {
			'transaction_type':self.transaction_type,
			'qty':self.qty,
			'sym':self.sym,
			'exch':self.exch,
			'commission':self.commission,
			'fixed_commission':self.fixed_commission,
			'slippage':self.slippage,
			'average_price':self.average_price,
			'price_data':self.price_data,
			'start_capital':self.start_capital,
			'available_capital_postions':self.available_positions,
		}
	
	def load_orders(self,order_data):
		self.transaction_type = order_data['transaction_type']
		self.qty = order_data['qty']
		self.sym = order_data['sym']
		self.exch = order_data['exch']
		self.commission = order_data['commission']
		self.fixed_commission = order_data['fixed_commission']
		self.slippage = order_data['slippage']
		self.average_price = order_data['average_price']
		self.price_data = order_data['price_data']
		self.start_capital = order_data['start_capital']
		self.available_positions = order_data['available_positions']
