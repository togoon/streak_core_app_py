import sys
sys.path.append('./dist-packages/')

__version__ = '0.0.1'

from action import Action

from position import Position
import math
import traceback

class Portfolio(object):
	"""class for Portfolio"""
	def __init__(self, user='',initial_capital = 100000.00,initial_postitions_value = 0.0):
		# super(Portfolio, self).__init__()
		self.initial_capital = initial_capital
		self.initial_postitions_value = initial_postitions_value 
		self.positions = dict()
		self.orders = list()
		# Position()
		self.sym_in_portfolio = list()
		self.curr_capital = self.initial_capital
		
		# self.portfolio_value = initial_postitions_value
		self.portfolio_value = self.initial_capital + initial_postitions_value

	# add position to portfolio
	def add_order(self,order):
		if order.success():
			self.orders.append(order)

			# if not self.portfolio_value < 10000000000000:
			# 	print '******',self.initial_capital,self.portfolio_value,self.curr_capital,order.position.size

			commission = 0.0
			if order.fixed_commission:
				commission = order.commission
			else:
				commission = order.commission * order.qty

			# self.curr_capital = self.curr_capital - (order.position.size) - commission
			order_instrument = '_'.join([order.exch,order.sym])
			if order_instrument not in self.positions.keys():
				self.curr_capital = self.curr_capital - (order.position.size) - commission
				# print '0',self.curr_capital
			else:
				if self.positions[order_instrument]['qty'] >= 0 and order.transaction_type == 1:
					# adding more shares
					self.curr_capital = self.curr_capital - (order.position.size) - commission
					# print '1',self.curr_capital

				elif self.positions[order_instrument]['qty'] < 0 and order.transaction_type == -1:
					# adding more short positions
					self.curr_capital = self.curr_capital - order.position.size - commission
					# print '2',self.curr_capital

				elif self.positions[order_instrument]['qty'] >= 0 and order.transaction_type == -1:
					# closeing exiting buy positions
					self.curr_capital = self.curr_capital + min(math.fabs(self.positions[order_instrument]['qty']),order.position.qty) * order.position.price + max(0,order.position.qty-self.positions[order_instrument]['qty'])*-1*order.position.price - commission
					# adding the sold posititon size min(math.fabs(self.positions[order_instrument]['qty']),order.position.qty) * order.position.price
					# deduction of addition shorts max(0,order.position.qty-self.positions[order_instrument]['qty'])*-1*order.position.price
					# print '3',self.curr_capital

				elif self.positions[order_instrument]['qty'] < 0 and order.transaction_type == 1:
					diff = max(0,self.positions[order_instrument]['qty'] + order.position.qty)
					price = self.positions[order_instrument]['pos_value']/math.fabs(float(self.positions[order_instrument]['qty']))
					self.curr_capital = self.curr_capital - diff * order.position.price + price*min(math.fabs(self.positions[order_instrument]['qty']),order.position.qty) + (price - order.position.price)*min(order.position.qty,math.fabs(self.positions[order_instrument]['qty'])) - commission
					# substracing the extra buys position size - diff * order.position.price
					# base position value + price*min(math.fabs(self.positions[order.sym]['qty']),order.position.qty)
					# gains or loss due to the price difference + (price - order.position.price)*min(order.position.qty,math.fabs(self.positions[order.sym]['qty']))
					# print '4',self.curr_capital,diff * order.position.price,price*min(math.fabs(self.positions[order_instrument]['qty']),order.position.qty),(price - order.position.price)*min(order.position.qty,math.fabs(self.positions[order_instrument]['qty'])),math.fabs(self.positions[order_instrument]['qty']),order.position.qty

			if order_instrument in self.positions.keys():
				try:
					total_qty = self.positions[order_instrument]['qty']+order.qty*order.transaction_type
					if total_qty == 0.0:
						self.positions[order_instrument]['average_price'] = 0.0
					else:
						self.positions[order_instrument]['average_price'] = self.positions[order_instrument]['qty']*self.positions[order_instrument]['average_price'] + order.average_price*order.qty*order.transaction_type/float(total_qty)
				except:
					self.positions[order_instrument]['average_price'] = 0.0

				self.positions[order_instrument]['last_updated'] = order.position.stop_time

				self.positions[order_instrument]['qty'] += order.qty*order.transaction_type
				
				self.positions[order_instrument]['pos_value'] = math.fabs(self.positions[order_instrument]['qty'])*order.position.price

			else:
				self.positions[order_instrument] = {'sym':order.sym,
													'exch':order.exch
													}

				if order.transaction_type == 1: # buying more shares
					self.positions[order_instrument]['average_price'] = \
						order.average_price*order.qty*order.transaction_type/float(order.qty)*order.transaction_type

					self.positions[order_instrument]['last_updated'] = order.position.stop_time

					self.positions[order_instrument]['qty'] = order.qty*order.transaction_type

					self.positions[order_instrument]['pos_value'] = math.fabs(self.positions[order_instrument]['qty'])*order.position.price

				elif order.transaction_type == -1: # shorting shares
					self.positions[order_instrument]['average_price'] = \
						order.average_price*order.qty*order.transaction_type/float(order.qty)*order.transaction_type

					self.positions[order_instrument]['last_updated'] = order.position.stop_time

					self.positions[order_instrument]['qty'] = order.qty*order.transaction_type

					self.positions[order_instrument]['pos_value'] = math.fabs(self.positions[order_instrument]['qty'])*order.position.price

			# self.portfolio_value = self.curr_capital + order.position.size
			# if not self.portfolio_value < 10000000000000:
			# 	print '******',self.initial_capital,self.portfolio_value,self.curr_capital,order.position.size

	def remove_order(self,order):
		pass
		
	def get_position_qty(self,sym): #TODO, add exch_sym for lookup
		# print self.positions.keys()
		if sym in self.positions.keys():
			return self.positions[sym]['qty']
		return 0

	def get_position_value(self,sym):
		# print self.positions.keys()
		if sym in self.positions.keys():
			return self.positions[sym]['pos_value']
		return 0

	def get_position(self,sym):
		# print self.positions.keys()
		if sym in self.positions.keys():
			return self.positions[sym]
		return None

	def get_payout(self,data=None,data_pos=-1):
		"""
		Calculates the portfolios net payout
		parameters
		----------
		data : complete data panel having all the data object,
		data_pos : iteration position
		"""
		if data is None:
			return self.portfolio_value

		payout = 0.0
		for order_instrument in self.positions.keys():
			try:
				# stock_curr_value = data.minor_xs(order_instrument).iloc[data_pos].close
				# speed optimisation of 50%
				stock_curr_value = data.minor_xs(order_instrument).iat[data_pos,0] #close = 0
				payout += math.fabs(self.positions[order_instrument]['qty']) * stock_curr_value
				# print self.positions[sym]['qty']
				if self.positions[order_instrument]['qty'] < 0:
					payout += (self.positions[order_instrument]['pos_value'] - stock_curr_value*math.fabs(self.positions[order_instrument]['qty']))*2.0
					# print '&&&&&&&&',self.positions[sym]['pos_value'] - stock_curr_value*math.fabs(self.positions[sym]['qty']),payout
					# (stock_curr_value - order.position.price)*min(order.position.qty,math.fabs(self.positions[order.sym]['qty']))
			except:
				print traceback.format_exc()
			# if not stock_curr_value < 10000000000000:
			# 	print self.portfolio_value,self.curr_capital,payout,order_instrument,self.positions[order_instrument]['qty'],stock_curr_value,data_pos,'........',len(data.minor_xs(order_instrument))
			# 	print '~~~~~~~~',data.minor_xs(order_instrument).iat[data_pos,0]
			# 	print '~~~~~~~~',data.minor_xs(order_instrument).iloc[data_pos-1].close
			# 	print '<><><><>',data.minor_xs(order_instrument).iloc[data_pos-1].name.strftime('%s')
			# 	print '~~~~~~~~',data.minor_xs(order_instrument).iloc[data_pos].name.strftime('%s')
			# 	print '!!!!!!!!',data.minor_xs(order_instrument).iloc[data_pos]
			# 	print '~~~~~~~~',data.minor_xs(order_instrument).iloc[data_pos+1].close
			# 	print '><><><><',data.minor_xs(order_instrument).iloc[data_pos+1].name.strftime('%s')

		payout += self.curr_capital

		self.portfolio_value = payout
		# if not payout < 10000000000000:
		# 	print self.portfolio_value,self.curr_capital,payout
		return payout

	def get_portforlio(self):
		portfolio = {}
		portfolio['initial_capital'] = self.initial_capital
		portfolio['positions'] = self.positions
		portfolio['orders'] = [o.get_order_dict() for o in self.orders]
		portfolio['sym_in_portfolio'] = self.positions.keys()
		portfolio['curr_capital'] = self.curr_capital
		portfolio['portfolio_value'] = self.portfolio_value

		return portfolio

	def load_protfolio(self,portfolio_data):
		self.initial_capital = portfolio_data['initial_capital']
		self.positions = portfolio_data['positions']
		self.orders = []
		for o in portfolio_data['orders']:
			order_obj = Order(o.get('transaction_type',0),o.get('qty',0),o.get('sym',''),o.get('exch',''),o.get('commission',0.0),o.get('fixed_commission',False),o.get(price_data,None),o.get(available_capital,0.0),o.get(available_positions,0),o.get(slippage,None))
			self.orders.append(order_obj)
		self.curr_capital = portfolio_data['curr_capital']
		self.portfolio_value = portfolio_data['portfolio_value']