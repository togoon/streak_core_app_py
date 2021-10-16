class Position(object):
	"""class for Position"""

	POS_STATUS = {'':None,'OPEN':1,'CLOSE':0}
	POS_TYPE = {'':None,'BUY':1,'SELL':-1,'HOLD':0}

	def __init__(self, qty = 0, price = 0.0, size = 0.0, average_price = 0.0, sym = '' , exch = '',start_time=None, stop_time=None, status= None,pos_type = None):
		# super(Position, self).__init__()
		self.qty = qty
		self.price = price # price of each stock
		self.size = size # total size of the position , price * qty
		self.average_price = average_price
		self.sym = sym
		self.start_time = None
		self.stop_time = None
		self.status = status#elf.POS_STATUS[status]
		self.pos_type = pos_type#self.POS_TYPE[pos_type]

	def close_position(close_time):
		self.close_time = close_time
		self.status = POS_STATUS['CLOSE']

	def get_status():
		return self.statusut