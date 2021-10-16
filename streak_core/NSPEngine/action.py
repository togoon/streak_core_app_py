__version__ = '0.0.1'

import strategy_parser as sp

# validate use of mathcing parsing library versions versions
assert __version__ == sp.__version__

class BaseAction():
	"""
	BaseAction class is the basic action format
	Its input is a action_string, this base action class is designed to use same underlying class to build both action class and alerts
	"""

	# POS_TYPE = {'':None,'BUY':1,'SELL':-1,'HOLD':0}

	WHEN_TYPE = {'ENTRY':1,'EXIT':-1}

	def __init__(self, entry_logic,exit_logic=''):
		# super(Action,self).__init__()
		self.entry_logic = entry_logic
		self.exit_logic = exit_logic

		self.entry_eval_generator = sp.EvalGenerator2(entry_logic) 
		self.entry_eval = None
		
		self.exit_given = False
		self.exit_eval_generator = None
		self.exit_eval = None

		if exit_logic!='':
			self.exit_eval_generator = sp.EvalGenerator2(exit_logic) 
			self.exit_given = True

		self.eval_generated = False
		self.eval_error_list = []
		self.eval_error = False

	def is_valid(self):
		if self.entry_eval_generator.get_eval_error()!=None:
			return False

		return True 

	def generate_eval(self):
		self.entry_eval = self.entry_eval_generator.get_eval()
		if not self.entry_eval:
			self.eval_error_list.append(['entry logic error',self.entry_eval_generator.get_eval_error()])
			self.eval_error = True
		
		if self.exit_eval:
			self.exit_eval = self.exit_eval_generator.get_eval()
			if not self.exit_eval:
				self.eval_error_list.append(['exit logic error',self.entry_eval_generator.get_eval_error()])
				self.eval_error = True

		if self.eval_error:
			return False
		
		if self.entry_eval:
			self.entry_eval_prev = self.entry_eval.replace('iter_pos','iter_pos-1')
			self.entry_eval_next = self.entry_eval.replace('iter_pos','iter_pos+1')

		if self.exit_eval:
			self.exit_eval_prev = self.exit_eval.replace('iter_pos','iter_pos-1')
			self.exit_eval_next = self.exit_eval.replace('iter_pos','iter_pos+1')
		
		self.eval_generated = True
		return True

	def get_entry_generator_error(self):
		return self.entry_eval_generator.parse_error

	def get_exit_generator_error(self):
		if self.exit_eval:
			return self.exit_eval_generator.parse_error
		return None

	def get_as_dict(self):
		return {
		'entry_eval':self.entry_eval,
		'entry_eval_prev':self.entry_eval_prev  if self.entry_eval else '',
		'entry_eval_next':self.entry_eval_next if self.entry_eval else '',
		'exit_eval':self.exit_eval,
		'exit_eval_prev':self.exit_eval_prev if self.exit_eval else '',
		'exit_eval_next':self.exit_eval_next if self.exit_eval else '',
		'is_valid':self.is_valid(),
		'exit_given':self.exit_given,
		'entry_cal_df_eval':self.entry_eval_generator.cal_df_eval  if self.entry_eval else {},
		'exit_cal_df_eval':self.exit_eval_generator.cal_df_eval  if self.exit_eval else {}
		}

class Action(BaseAction):

	POS_TYPE = {'':None,'BUY':1,'SELL':-1,'HOLD':0}

	def __init__(self,entry_logic,position_type,exit_logic=''):
		BaseAction.__init__(self,entry_logic,exit_logic)
		BaseAction.generate_eval(self)
		#TODO add other attributes apecific to actions
		if not isinstance(position_type,int):
			self.position_type = self.POS_TYPE[position_type.upper()]