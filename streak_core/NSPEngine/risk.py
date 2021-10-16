from empyrical import (
    alpha_beta_aligned, # will be used wrt index
    annual_volatility,
    cum_returns,
    downside_risk,
    # information_ratio, # will be used wrt index
    max_drawdown,
    sharpe_ratio,
    sortino_ratio,
)

from portfolio import Portfolio
import numpy as np
#TODO add alpha and beta wrt to an index

class Risk(object):
	"""docstring for Risk"""
	def __init__(self,portfolio):
		# super(Risk, self).__init__()
		# self.arg = arg
		self.perfomance = 0.0
		self.net_pnl = 0.0
		self.volatility = 0.0
		self.sharpe = 0.0
		self.sortino = 0.0
		self.max_draw = 0.0
		self.win_rate = 0.0
		self.loss_rate = 0.0
		self.pnl = 0.0
		
		self.win_count = 0
		self.loss_count = 0

		self.max_win = 0.0
		self.max_loss = 0.0

		self.avg_win = 0.0
		self.avg_loss = 0.0

		# not being used now
		self._total_intraperiod_capital_change = 0.0
		self.cash_flow = 0.0 # to account for any dividends given
		
		self.cum_returns = 0.0
		self.downside_risk = 0.0

		self.portfolio = portfolio
		self.portfolio_value = portfolio.get_payout()
		self.orders_len = len(self.portfolio.orders)

		self.last_timestamp = None

	def add_win(self,data,pos,portfolio,returns,data_timestamp):
		self.win_count += 1
		if self.win_count+self.loss_count != 0:
			self.win_rate = float(self.win_count)/(self.win_count+self.loss_count)
			self.loss_rate = float(self.loss_count)/(self.win_count+self.loss_count)

		payout = portfolio.get_payout(data,pos+1)
		if(self.max_win < payout - self.portfolio_value):
			self.max_win = payout - self.portfolio_value

	def add_loss(self,data,pos,portfolio,returns,data_timestamp):
		self.loss_count += 1
		if self.win_count+self.loss_count != 0:
			self.win_rate = float(self.win_count)/(self.win_count+self.loss_count)
			self.loss_rate = float(self.loss_count)/(self.win_count+self.loss_count)

		payout = portfolio.get_payout(data,pos+1)
		
		if(self.max_loss > payout - self.portfolio_value):
			self.max_loss = payout - self.portfolio_value

	def add(self,data,pos,portfolio,returns,data_timestamp):
		# cal perfomance
		total_at_start = portfolio.initial_capital #+ portfolio.portfolio_value

		payout = portfolio.get_payout(data,pos) # returns the value of positions currently plus the capital in hand

		# ending_cash = portfolio.initial_capital + self.cash_flow + self._total_intraperiod_capital_change + payout
		ending_cash = self.cash_flow + self._total_intraperiod_capital_change + payout

		total_at_end = ending_cash

		# print 'total_at_start',total_at_start,'total_at_end',total_at_end,data_timestamp
		if total_at_start!=0:
			self.pnl = total_at_end - total_at_start
			self.perfomance = self.pnl/float(total_at_start)

		returns.set_value(data_timestamp,self.perfomance)
		
		self.volatility = annual_volatility(returns)
		self.sharpe = sharpe_ratio(returns)
		self.sortino = sortino_ratio(returns)
		self.max_draw = max_drawdown(returns)
		# self.cum_returns = cum_returns(returns)[-1]
		self.cum_returns = returns.cumsum().values[-1]
		self.downside_risk = downside_risk(returns)

		# if self.orders_len != len(portfolio.orders):
		# 	pay = portfolio.get_payout(data,pos+1)
		# 	self.orders_len = len(portfolio.orders)
		# 	if self.portfolio_value < pay:
		# 		self.win_count += 1
		# 		if(self.max_win < pay - self.portfolio_value):
		# 			self.max_win = pay - self.portfolio_value
		# 	elif self.portfolio_value > pay:
		# 		self.loss_count += 1
		# 		print 'Loss count',self.portfolio_value,loss_count,data_timestamp
		# 		if(self.max_loss > pay - self.portfolio_value):
		# 			self.max_loss = pay - self.portfolio_value
		
		# 	if self.win_count+self.loss_count != 0:
		# 		self.win_rate = float(self.win_count)/(self.win_count+self.loss_count)
		# 		self.loss_rate = float(self.loss_count)/(self.win_count+self.loss_count)

		self.portfolio_value = payout

		self.last_timestamp = data_timestamp

	def get_metrics(self):
		return {'pnl':self.pnl,
				'perfomance':self.perfomance,
				'volatility':self.volatility,
				'sharpe':self.sharpe,
				'sortino':self.sortino,
				'max_draw':self.max_draw,
				'cum_returns':self.cum_returns,
				'downside_risk':self.downside_risk,
				'win_rate':self.win_rate,
				'loss_rate':self.loss_rate,
				'win_count':self.win_count,
				'loss_count':self.loss_count,
				'max_win':self.max_win,
				'max_loss':self.max_loss,
				'portfolio_value':self.portfolio_value,
				'last_timestamp':self.last_timestamp
				}

class Risk2():
	"""docstring for Risk"""
	def __init__(self,portfolio):
		# super(Risk, self).__init__()
		# self.arg = arg
		self.perfomance = 0.0
		self.net_pnl = 0.0
		self.volatility = 0.0
		self.sharpe = 0.0
		self.sortino = 0.0
		self.max_draw = 0.0
		self.win_rate = 0.0
		self.loss_rate = 0.0
		self.pnl = 0.0
		
		self.win_count = 0
		self.loss_count = 0

		self.max_win = 0.0
		self.max_loss = 0.0

		self.avg_win = 0.0
		self.avg_loss = 0.0

		# not being used now
		self._total_intraperiod_capital_change = 0.0
		self.cash_flow = 0.0 # to account for any dividends given
		
		self.cum_returns = 0.0
		self.downside_risk = 0.0

		self.portfolio = portfolio
		self.portfolio_value = portfolio.get_payout()
		self.orders_len = len(self.portfolio.orders)

		self.last_timestamp = None

		self.period_high = 0.0
		self.period_low = 0.0
		self.period_return = 0.0
		self.period_volatility = 0.0

	def add_win(self,data,pos,portfolio,returns,data_timestamp):
		self.win_count += 1
		if self.win_count+self.loss_count != 0:
			self.win_rate = float(self.win_count)/(self.win_count+self.loss_count)
			self.loss_rate = float(self.loss_count)/(self.win_count+self.loss_count)

		# prev_portfolio = self.portfolio_value
		# payout = portfolio.get_payout(data,pos+1)
		# # print payout - prev_portfolio
		# if(self.max_win < payout - prev_portfolio):
		# 	self.max_win = payout - prev_portfolio

	def add_loss(self,data,pos,portfolio,returns,data_timestamp):
		self.loss_count += 1
		if self.win_count+self.loss_count != 0:
			self.win_rate = float(self.win_count)/(self.win_count+self.loss_count)
			self.loss_rate = float(self.loss_count)/(self.win_count+self.loss_count)

		# prev_portfolio = self.portfolio_value
		# payout = portfolio.get_payout(data,pos+1)
		# # print payout - prev_portfolio
		# if(self.max_loss > payout - self.portfolio_value):
		# 	self.max_loss = payout - self.portfolio_value

	def add(self,data,pos,portfolio,returns,data_timestamp):
		# cal perfomance
		total_at_start = portfolio.initial_capital #+ portfolio.portfolio_value

		payout = portfolio.get_payout(data,pos) # returns the value of positions currently plus the capital in hand

		# ending_cash = portfolio.initial_capital + self.cash_flow + self._total_intraperiod_capital_change + payout
		ending_cash = self.cash_flow + self._total_intraperiod_capital_change + payout

		total_at_end = ending_cash

		# print 'total_at_start',total_at_start,'total_at_end',total_at_end,data_timestamp
		if total_at_start!=0:
			self.pnl = total_at_end - total_at_start
			self.perfomance = self.pnl/float(total_at_start)

		returns.append(self.perfomance)
		returns_arr = np.array(returns)
		self.volatility = annual_volatility(returns_arr)
		self.sharpe = sharpe_ratio(returns_arr)
		self.sortino = sortino_ratio(returns_arr)
		self.max_draw = max_drawdown(returns_arr)
		# self.cum_returns = cum_returns(returns)[-1]
		self.cum_returns = returns_arr.cumsum()[-1]
		self.downside_risk = downside_risk(returns_arr)

		# if self.orders_len != len(portfolio.orders):
		# 	pay = portfolio.get_payout(data,pos+1)
		# 	self.orders_len = len(portfolio.orders)
		# 	if self.portfolio_value < pay:
		# 		self.win_count += 1
		# 		if(self.max_win < pay - self.portfolio_value):
		# 			self.max_win = pay - self.portfolio_value
		# 	elif self.portfolio_value > pay:
		# 		self.loss_count += 1
		# 		print 'Loss count',self.portfolio_value,loss_count,data_timestamp
		# 		if(self.max_loss > pay - self.portfolio_value):
		# 			self.max_loss = pay - self.portfolio_value
		
		# 	if self.win_count+self.loss_count != 0:
		# 		self.win_rate = float(self.win_count)/(self.win_count+self.loss_count)
		# 		self.loss_rate = float(self.loss_count)/(self.win_count+self.loss_count)

		self.portfolio_value = payout

		self.last_timestamp = data_timestamp

	def add2(self,data,pos,portfolio,returns,data_timestamp):
		# cal perfomance
		pos = pos+1 # because order is always placed at next close 
		total_at_start = portfolio.initial_capital #+ portfolio.portfolio_value

		payout = portfolio.get_payout(data,pos) # returns the value of positions currently plus the capital in hand

		# ending_cash = portfolio.initial_capital + self.cash_flow + self._total_intraperiod_capital_change + payout
		ending_cash = self.cash_flow + self._total_intraperiod_capital_change + payout

		total_at_end = ending_cash
		
		# print 'total_at_start',total_at_start,'total_at_end',total_at_end,data_timestamp
		if total_at_start!=0:
			self.pnl = total_at_end - total_at_start
			self.perfomance = self.pnl/float(total_at_start)

		returns.append(self.perfomance)
		# returns_arr = np.array(returns)
		# self.volatility = annual_volatility(returns_arr)
		# self.sharpe = sharpe_ratio(returns_arr)
		# self.sortino = sortino_ratio(returns_arr)
		# self.max_draw = max_drawdown(returns_arr)
		# # self.cum_returns = cum_returns(returns)[-1]
		# self.cum_returns = returns_arr.cumsum()[-1]
		# self.downside_risk = downside_risk(returns_arr)

		# if self.orders_len != len(portfolio.orders):
		# 	pay = portfolio.get_payout(data,pos+1)
		# 	self.orders_len = len(portfolio.orders)
		# 	if self.portfolio_value < pay:
		# 		self.win_count += 1
		# 		if(self.max_win < pay - self.portfolio_value):
		# 			self.max_win = pay - self.portfolio_value
		# 	elif self.portfolio_value > pay:
		# 		self.loss_count += 1
		# 		print 'Loss count',self.portfolio_value,loss_count,data_timestamp
		# 		if(self.max_loss > pay - self.portfolio_value):
		# 			self.max_loss = pay - self.portfolio_value
		
		# 	if self.win_count+self.loss_count != 0:
		# 		self.win_rate = float(self.win_count)/(self.win_count+self.loss_count)
		# 		self.loss_rate = float(self.loss_count)/(self.win_count+self.loss_count)
		self.portfolio_value = payout

		self.last_timestamp = data_timestamp

	def cal_final_metrics(self,data,pos,portfolio,returns,data_timestamp):
		returns_arr = np.array(returns)
		self.volatility = annual_volatility(returns_arr)
		self.sharpe = sharpe_ratio(returns_arr)
		self.sortino = sortino_ratio(returns_arr)
		self.max_draw = max_drawdown(returns_arr)
		# self.cum_returns = cum_returns(returns)[-1]
		try:
			self.cum_returns = returns_arr.cumsum()[-1]
		except:
			self.cum_returns = 0
		self.downside_risk = downside_risk(returns_arr)
		# self.max_win = max(0,max(self.pnl))
		# self.max_loss = min(0,min(self.pnl))
		self.period_high = max(data.high)
		self.period_low = min(data.low)
		self.period_return = (data.iloc[pos].close-data.iloc[0].close)/data.iloc[0].close*100
		self.period_volatility = 0

	def get_metrics(self):
		return {'pnl':self.pnl,
				'perfomance':self.perfomance,
				# high computation cost associatedwith the below
				# 'volatility':self.volatility,
				# 'sharpe':self.sharpe,
				# 'sortino':self.sortino,
				# 'max_draw':self.max_draw,
				# 'cum_returns':self.cum_returns,
				# 'downside_risk':self.downside_risk,
				'win_rate':self.win_rate,
				'loss_rate':self.loss_rate,
				'win_count':self.win_count,
				'loss_count':self.loss_count,
				# 'max_win':self.max_win,
				# 'max_loss':self.max_loss,
				'portfolio_value':self.portfolio_value,
				'last_timestamp':self.last_timestamp
				}

	def get_all_metrics(self):
		return {'pnl':self.pnl,
				'perfomance':self.perfomance,
				# high computation cost associated with the below
				'volatility':self.volatility,
				'sharpe':self.sharpe,
				'sortino':self.sortino,
				'max_draw':self.max_draw,
				'cum_returns':self.cum_returns,
				'downside_risk':self.downside_risk,
				'win_rate':self.win_rate,
				'loss_rate':self.loss_rate,
				'win_count':self.win_count,
				'loss_count':self.loss_count,
				# 'max_win':self.max_win,
				# 'max_loss':self.max_loss,
				'portfolio_value':self.portfolio_value,
				'last_timestamp':self.last_timestamp,
				'period_high':self.period_high,
				'period_low':self.period_low,
				'period_return':self.period_return,
				'period_volatility':self.period_volatility
				}