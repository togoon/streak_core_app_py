
__version__ = '0.0.1'

# This is the parsing libarary for the trading strategy
# This version is a simple approach to parsing with word split and tree flow approach for simplicity
# TODO, upcoming versions will utilize advanced techniches of tockenization and NLU's with entity extractions and syntactical graph formation
from parsing_hierarchy2 import *
import re

class MainParser():
	"""MainParser handles the high level strategy break down, to create a nested dict format of the english startegy
	Sample: input => strategy_str = '2 days moving average crosses/goes above 4 days moving average and prev close price/ltp goes above 200' 
			output => [
			{
				'operation_list':[
					{
					"operator":"moving_average",
					"params":{
						"period":['2','day'],
						"offset":[]
						}
					},
					{
					"operator":"moving_average",
					"params":{
						"period":['4','day']
						"offset":[]
						}
					}
				],
				'comparator':'above/>'
			},
			AND,
			{
				'operation_list':[
					{
					"operator":"price",
					"params":{
						"price_type":['close'/'ltp'],
						"offset":[]
						}
					},
					{
					"operator":"number",
					"params":{
						"value":200
						}
					}
				],
				'comparator':'above/>'
			},
			]"""
	def __init__(self, strategy_str):
		# super(MainParser, self).__init__()
		self.strategy_str = strategy_str.lower()
		self.str_to_parse = strategy_str
		self.functions_hierarchy = functions_dict
		self.comparator_hierarchy = comparator_dict
		self.str_and_list = []
		self.str_or_list = []
		self.str_chunks = []
		self.parsed_list = []
		self.indicator_str_all = []

	def handle_abrupt_ends(self):
		str_to_parse = self.str_to_parse
		self.str_to_parse = self.str_to_parse.replace(' .',' 0.')
		if str_to_parse.endswith(' and'):
			self.str_to_parse = self.str_to_parse.strip(' and')
			return True
		if str_to_parse.endswith(' or'):
			self.str_to_parse = self.str_to_parse.strip(' or')
			return True
						
		if str_to_parse.endswith(' above') or str_to_parse.endswith(' below') or str_to_parse.endswith(' crosses') or str_to_parse.endswith(' equals') or str_to_parse.endswith(' equal'):
			return True

		return False

	def parse_period_with_offset(self,var_str):
		params_reg_dict = {'period':[r"(\d*)\s*(day)",
								r"(\d*)\s*(min)",
								r"(\d*)\s*(intervals)",
								r"(\d*)\s*(candles)"],
						'offset':[r"(\d*)\s*(\w*)\s*ago",
								r"(\d*)\s*(\w*)\s*old",
								r"(\d*)\s*(\w*)\s*back",
								r"(yesterday)",
								r"(previous day)"]
						}

		offset = []

		for off in params_reg_dict['offset']:
			offset = re.findall(off,var_str)
			if offset!=[]:
				# if len(offset)<2:
				#	 offset = offset
				if type(offset[0])==type(()):	
					offset = list(offset[0])
				var_str = re.sub(off, '', var_str) # this removes the occurance of the offset
				break

		period = []

		for per in params_reg_dict['period']:
			period = re.findall(per,var_str)
			if period!=[]:
				period = list(period[0])
				var_str = re.sub(per, '', var_str)
				break

		# print period
		return {'offset':offset,'period':period}

	def parser_bracket(self,var_str,params_list):
		params_reg_dict = {'bracket':[r"\((.*?)\)"]
						}

		params = []

		for per in params_reg_dict['bracket']:
			p = re.findall(per,var_str)
			if p!='' and p!=[]:
				params = list(p[0].split(','))
				break
		response_dict = {}
		for i in range(len(params_list)):
			try:
				response_dict[params_list[i][0]]=params[i]
			except:
				response_dict[params_list[i][0]]=[]
		return response_dict

	def parse_offset(self,var_str):
		params_reg_dict = {'period':[r"(\d*)\s*(day)",
								r"(\d*)\s*(min)"],
						'offset':[r"(\d*)\s*(\w*)\s*ago",
								r"(\d*)\s*(\w*)\s*old",
								r"(\d*)\s*(\w*)\s*back",
								r"(yesterday)",
								r"(previous day)"]
						}

		offset = []

		for off in params_reg_dict['offset']:
			offset = re.findall(off,var_str)
			if offset!=[]:
				# print '++++++++++++++',var_str,off,offset
				if type(offset[0])==type(()):   
					offset = list(offset[0])
				var_str = re.sub(off, '', var_str) # this removes the occurance of the offset
				break

		# period = []

		# for per in params_reg_dict['period']:
		#	 period = re.findall(per,var_str)
		#	 if period!=[]:
		#		 period = list(period[0])
		#		 var_str = re.sub(per, '', var_str)
		#		 break

		return {'offset':offset
				# ,'period':period
				}

	def parse_offset_without_interval(self,var_str):
		value = re.findall(r'(\d+)',var_str)
		offset = []
		# print 'value-----',value
		if value!=[]:
			offset = value[0]
		return {'offset':offset
				# ,'period':period
				}

	def change_by_parser(self,var_str):
		reg = r'(\d+\.{0,1}\d{0,})'
		params = re.findall(reg,var_str)
		value = []
		range_ = []
		if len(params)==1:
			if('%' in var_str):
				return [params[0],'"%"']
			return [params[0],'"abs"']
		return [0,'"%"']

	def parse_range(self,var_str):
		# print ==>'***************',var_str
		params_reg_dict = {'value':[r"[^0-9]*(\d*(\.\d+)\s*(day)",
								r"[^0-9]*(\d*(\.\d+)\s*(min)"],
						'offset':[r"[^0-9]*(\d*(\.\d+)\s*(\w*)\s*ago",
								r"(\d*)\s*(\w*)\s*old",
								r"(\d*)\s*(\w*)\s*back",
								r"(yesterday)"]
						}
		offset = []
		# for off in params_reg_dict['offset']:
		# 	offset = re.findall(off,var_str)
		# 	if offset!=[]:
		# 		# if len(offset)<2:
		# 		#	 offset = offset
		# 		if type(offset[0])==type(()):	
		# 			offset = list(offset[0])
		# 		var_str = re.sub(off, '', var_str) # this removes the occurance of the offset
		# 		break
		period = []
		# for per in params_reg_dict['period']:
		# 	period = re.findall(per,var_str)
		# 	if period!=[]:
		# 		period = list(period[0])
		# 		var_str = re.sub(per, '', var_str)
		# 		break
		reg = r'(\d+\.{0,1}\d{0,})'
		params = re.findall(reg,var_str)
		value = []
		range_ = []
		if len(params)==2:
			value = [params[0]]
			range_ = [params[1]]
			if '%' in var_str:
				range_.append('%')
		# print period
		return {'value':value,'range':range_}

	def parse_bb(self,var_str):
		# 'upper_multiplier','lower_multiplier'
		params_reg_dict = {'period':[r"(\d*)\s*(day)",
								r"(\d*)\s*(min)"],
						'offset':[r"(\d*)\s*(\w*)\s*ago",
								r"(\d*)\s*(\w*)\s*old",
								r"(\d*)\s*(\w*)\s*back"
								r"(yesterday)"],
						# 'upper_multiplier':[r"with[^0-9]*(\d*)[^0-9]*(\d*)",
						# 					r"with upper [^0-9]*(\d*)\s*[^0-9]*(\d*)",
						# 					r"with upper [^0-9]*(\d*)\s*[^0-9]*(\d*)",
						# 					r"with multi[^0-9]*(\d*)\s*[^0-9]*(\d*)",
						# 					r"with multi[^0-9]*(\d*)\s*[^0-9]*(\d*)"
						# and low[^0-9]*(\d*(\.\d+)?$)
						# 					],
						'upper_multiplier':[r"[^0-9]*with[^0-9]*(\d*(\.\d+)?$)",
											r"[^0-9]*with upper [^0-9]*(\d*(\.\d+)?$)",
											r"[^0-9]*with upper [^0-9]*(\d*(\.\d+)?$)",
											r"[^0-9]*with multi[^0-9]*(\d*(\.\d+)?$)",
											],
						'lower_multiplier':[
											r"[^0-9]*and[^0-9]*(\d*(\.\d+)?$)",
											r"[^0-9]*and low[^0-9]*(\d*(\.\d+)?$)",
											]
						}

		offset = []

		for off in params_reg_dict['offset']:
			offset = re.findall(off,var_str)
			if offset!=[]:
				# if len(offset)<2:
				#	 offset = offset
				if type(offset[0])==type(()):	
					offset = list(offset[0])
				var_str = re.sub(off, '', var_str) # this removes the occurance of the offset
				break

		period = []

		for per in params_reg_dict['period']:
			period = re.findall(per,var_str)
			if period!=[]:
				period = list(period[0])
				var_str = re.sub(per, '', var_str)
				break

		upper_mul = 2.0

		for u in params_reg_dict['upper_multiplier']:
			mul = re.findall(per,var_str)
			if period!=[]:
				period = list(period[0])
				var_str = re.sub(per, '', var_str)
				break

		# print period
		return {'offset':offset,'period':period,'upper_multiplier':2,'lower_multiplier':2}

	def parse_value(self,var_str):
		value = re.findall(r'(-?\d*.?\d)',var_str)
		indicator_value = ''
		# print 'value-----',value
		if value!=[]:
			indicator_value = ''.join(value)# value[0]
		# print 'value-----',indicator_value
		return {'value':indicator_value}

	def parse_period(self,var_str):
		value = re.findall(r'(\d+)',var_str)
		period = 0
		# print 'value-----',value
		if value!=[]:
			period = value[0]
		return {'period':period}

	def parse_variable(self,var_str):
		# finding functions in the sub strings of the comparator
		functions_hierarchy = self.functions_hierarchy

		func_list = functions_hierarchy.keys()

		indicator_func = ''

		# freq = {
		# 		'moving_average':0.0,
		# 		'exponential_moving_average':0.0,
		# 		'RSI':0.0,
		# 		'MACD':0.0,
		# 		'OBV':0.0,
		# 		'ATR':0.0,
		# 		'UBB':0.0,
		# 		'MBB':0.0,
		# 		'LBB':0.0,
		# 		'volume':0.0,
		# 		'open':0.0,
		# 		'high':0.0,
		# 		'low':0.0,
		# 		'close':0.0,
		# 		'range':0.0
		# 		}

		for func in functions_hierarchy.keys():
			for indicator in functions_hierarchy[func]['must']:
				if indicator_func!='':
					break
				if indicator in var_str:
					m_not = False
					for must_not in functions_hierarchy[func]['mustnot']:
						if must_not in var_str:
							m_not = True
					# print 'indicator',indicator,func,indicator_func
					if m_not:
						continue 
					indicator_func = func
					break

		if indicator_func!='':
			if functions_hierarchy[indicator_func]['parser'] == 'parser_bracket':
				params_list = functions_hierarchy[indicator_func]['default_params']
				params = eval('self.'+functions_hierarchy[indicator_func]['parser']+'(var_str,params_list)')
			else:
				params = eval('self.'+functions_hierarchy[indicator_func]['parser']+'(var_str)')
		# print indicator_func,var_str
		if indicator_func == '': # try for getting numbers out
			params = self.parse_value(var_str)
			indicator_func = 'float'

		return {'indicator':indicator_func,'params':params}

	def parse_condition(self,condition):
		comparator = ''
		variable_split = []
		# finding the comparator and spilling the string at that
		for comp in self.comparator_hierarchy.keys():
			for c in self.comparator_hierarchy[comp]['must']:
				if c in condition:
					# print 'condition',c
					comparator = self.comparator_hierarchy[comp]['comparision']
					if(comparator in ['higher by','lower by']):
						variable_split = re.split(self.comparator_hierarchy[comp].get('split_regex',c),condition)
						comparator = re.findall(self.comparator_hierarchy[comp].get('split_regex',c),condition)[0]
						self.indicator_str_all.append([variable_split,comp])
						# print variable_split,condition,c
					else:
						variable_split = condition.split(c) # split condition at comparator to provide two objects
						self.indicator_str_all.append([variable_split,comp])
					# if comparator == 'self':

		#todo figgure out if more than one condition is present and then return an error if it is
					break

		# 			break 
		indicator_str = []
		# print 'comparator',condition,comparator
		if(len(variable_split)==0 and len(condition)>4):
			variable_split=[condition]
			comparator=''
			self.indicator_str_all.append([variable_split,None])

		# print '-------->',variable_split
		for var_str in variable_split:
			# print 'var_str',var_str
			indicator_str.append(self.parse_variable(var_str))

		# print 'variable_split',variable_split
		# print 'indicator_list',indicator_str
		# print 'indicator_str len',len(indicator_str)
		return {'indicator_list':indicator_str,'comparator':comparator}

	def get_str_to_parse(self): # use to get the spelling corrected string
		return self.str_to_parse

	def parse(self):

		self.parsed_list = []

		if self.handle_abrupt_ends():
			self.error_parsing = True
			self.error_message = 'Abrupt end in the when statement'

		# correct any speeling mistakes
		# self.correct_spellings()

		# regex_and = r"(.*)and(.*)"
		# regex_or = r"(.*)or(.*)"
		# and_substrings = re.findall(off,var_str)
		# if and_substrings!=[]:
		#	 and_substrings = list(and_substrings[0])

		str_to_parse = self.str_to_parse
		# self.str_to_parse = ''
		print('str_to_parse',str_to_parse)

		chunk = ''
		and_or_flag = False

		# print str_to_parse.split()
		for word in str_to_parse.split():
			if word not in ['and','or']:
				chunk += ' ' + word
			if word in ['and','or']:
				and_or_flag = True
				self.str_chunks.append(chunk)
				self.str_chunks.append(word)
				chunk = '' 

		# if not and_or_flag:
		self.str_chunks.append(chunk)
		chunk = ''

		# finding any and's or or's in the statement
		# if ' and ' in self.str_to_parse:# or ' or ' in self.str_to_parse:
		# 	self.str_and_list = self.str_to_parse.split(' and ')
		# else:
		# 	self.str_and_list = self.str_to_parse.split(' and ')

		# print 'chunks',self.str_chunks,str_to_parse.split()

		if self.str_chunks!=[]:
			for condition in self.str_chunks:
				# print 'condition',condition
				p = self.parse_condition(condition)
				# print p
				if condition in ['and','or']:
					p['condition'] = condition
				# pprint(p)
				# print 'parse_condition','condition=> ',self.str_chunks
				self.parsed_list.append(p)
		
		return self.parsed_list

class EvalGenerator():
	"""Use the parsed Dict to create executable functions and dynamic test of validations"""
	def __init__(self,str_to_parse):
		# super(WhenParser, self).__init__()
		# self.arg = arg
		self.str_to_parse = str_to_parse.lower()
		self.indicator_mapping = functions_dict

		self.param_mapping = default_param_mapping

		self.main_parser = MainParser(self.str_to_parse)
		self.parsed_list = None # parsed conditional list
		self.parsed_eval = None
		self.parse_error = None

	def get_eval(self):
		main = self.generate_eval()
		return self.parsed_eval

	def get_eval_error(self):
		return self.parse_error

	def generate_eval(self): 
		'''
		Generates executable code for python eval
		output => eval_string
		'''
		if not self.parsed_list:
			self.parsed_list = self.main_parser.parse()
		main = ''
		error = None
		indicator_function_list = []
		logical_op_list = [] # hold the list of all the AND and OR's in sequnce
		comparator_list = [] # hold the list of comparators like above and below

		for item in self.parsed_list:
			comparator = item['comparator']

			if comparator!='':
				comparator_list.append(comparator)

			if len(item['indicator_list']) == 0:
				# check if the item is empty logical element
				if 'condition' in item.keys():
					logical_op_list.append("".join(item['condition'].split()))

			if len(item['indicator_list']) == 1 :
				error='No logic found'

			if len(item['indicator_list']) == 2 :
				# this block handles a balanced two sided condition
				for indicator_item in item['indicator_list']:
					temp = '' # hold the eval string temporarily
					indicator = indicator_item['indicator']#[0]
					# print item
					mapped_function = self.indicator_mapping[indicator]
					mapped_function_name = mapped_function['func']
					params = mapped_function['default_params']
					# print 'mapped_function_name',mapped_function_name
					# print 'indicator',indicator
					temp += mapped_function_name+'('
					# print '+++',temp

					for p in params:
						# print indicator_item['params'][p[0]]
						temp += p[0]+'='
						if p[0] in indicator_item['params'].keys():
							if len(indicator_item['params'][p[0]]) > 0:
								temp += self.param_mapping.get(str(indicator_item['params'][p[0]][0]),str(indicator_item['params'][p[0]]))
							else:
								# temp += str(indicator_item['params'][p[0]])
								temp += str(p[1]) # putting default param
						else:
							temp += str(p[1]) # putting default param
						temp += ','
					# temp = temp[:-1]
					temp += 'action_data=action_data,iter_position=pos)'
					indicator_function_list.append(temp)

		if len(comparator_list)*2 > len(indicator_function_list):
			error = 'Extra above or below conditions'

		elif len(comparator_list)*2 < len(indicator_function_list):
			error = 'Missing above or below conditions'
		elif len(logical_op_list) <  len(comparator_list)-1 and len(logical_op_list) != 0:
			error = 'Missing and/or'
		elif len(logical_op_list) > len(comparator_list)-1 and len(logical_op_list) != 0:
			# print  '...................................'
			error = 'Extra and/or'

		if not error:
			for i in range(0,len(comparator_list)):
				# print '.......',comparator_list[i],'.......'
				if comparator_list[i] == ' at ':
					# especial handling of the comparator item
					reg = r'(\d+\.{0,1}\d{0,})'
					params = re.findall(reg,indicator_function_list[i*2+1])
					value = '"nan"'
					range_ = []
					# print len(params),params,indicator_function_list
					if len(params)==2:
						value = params[0]
						range_ = [params[1]]
						# print value,range_
						if '%' in indicator_function_list[i*2+1]:
							range_.append('"%"')
					main += 'inrange('+indicator_function_list[i*2]+','+value+',['+','.join(range_)+'])'
				else:
					if(comparator_list[i] in ["crosses>"]):
						main += comparator_hierarchy[comparator_list[i]]+'('+indicator_function_list[i*2]+',',indicator_function_list[i*2+1]+',iter_pos)'
					else:
						main += indicator_function_list[i*2]+' '
						main += comparator_list[i]
						main += indicator_function_list[i*2+1]+' '

				try:
					if logical_op_list!=[]:
						main += ' ' + logical_op_list[i] + ' '
				except:
					pass

		# print main
		# print comparator_list
		# print logical_op_list
		# print indicator_function_list
		# print error
		# print len(comparator),len(indicator_function_list)
		# print self.parsed_list
		self.parsed_eval = main
		self.parse_error = error
		# ==>print main
		return main

class EvalGenerator2():
	"""Use the parsed Dict to create executable functions and dynamic test of validations"""
	def __init__(self,str_to_parse):
		# super(WhenParser, self).__init__()
		# self.arg = arg
		self.str_to_parse = str_to_parse.lower()
		self.indicator_mapping = functions_dict

		self.param_mapping = default_param_mapping

		for mappings in self.param_mapping.keys():
			if mappings in self.str_to_parse:
				self.str_to_parse = self.str_to_parse.replace(mappings,self.param_mapping[mappings])

		self.main_parser = MainParser(self.str_to_parse)
		self.parsed_list = None # parsed conditional list
		self.parsed_eval = None
		self.parse_error = None
		self.cal_df_eval = None

	def get_eval(self):
		main = self.generate_eval()
		return self.parsed_eval

	def get_eval_error(self):
		return self.parse_error

	def generate_eval(self): 
		'''
		Generates executable code for python eval
		output => eval_string
		'''
		if not self.parsed_list:
			self.parsed_list = self.main_parser.parse()

		df_eval = [] # data frame shorts hand name list
		self.cal_df_eval = {} # data frame calculation eval code
		# df_run_eval = []
	#	 temp_forming_list = []
		main = ''
		error = None
		
		comparator_list = []
		logical_op_list = []
		# print 'self.parsed_list',self.parsed_list
		# print 'self.parsed_list`-`-`-`-`-`-',self.parsed_list
		exceptions_dict = {'min':"'min'",'3min':"'3min'",'5min':"'5min'",'10min':"'10min'",'15min':"'15min'",'30min':"'30min'",'45min':"'45min'",'hour':"'hour'",'day':"'day'",'week':"'week'",'open':"'open'",'high':"'high'",'low':"'low'",'close':"'close'",'volume':"'volume'",'ema':"'ema'",'sma':"'sma'",'%k':"'%k'",'%d':"'%d'",'r1':"'r1'",'r2':"'r2'",'r3':"'r3'",'pp':"'pp'",'s1':"'s1'",'s2':"'s2'",'s3':"'s3'",'standard':"'standard'",'fibonacci':"'fibonacci'",'simple':"'simple'",'exponential':"'exponential'",'weighted':"'weighted'",'triple':"'triple'",'triangular':"'triangular'",'double':"'double'",'hull':"'hull'",'kaufman':"'kaufman'",'tii':"'tii'",'signal':"'signal'","":'0','+vi':"'+vi'",'-vi':"'-vi'",'jaw':"'jaw'",'teeth':"'teeth'",'lips':"'lips'",'ef':'"ef"','trigger':'"trigger"','val':'"val"','vah':'"vah"','poc':'"poc"','bt':'"bt"','plow':'"plow"','phigh':'"phigh"','conversion line':'"conversion_line"','base line':'"base_line"','leading span a':'"leading_span_a"','leading span b':'"leading_span_b"','lagging span':'"lagging_span"','yes':'"yes"','no':'"no"'}

		for item in self.parsed_list:
			
			# indicator list, for parsing the individual indicators and their associated functions
			comparator = item['comparator']
			if comparator!='':
				comparator_list.append(comparator)
			elif comparator=='' and len(item['indicator_list'])==1 and 'condition' not in item.keys():
				comparator_list.append('single line')
			if len(item['indicator_list']) == 0:
				# check if the item is empty logical element
				if 'condition' in item.keys():
					logical_op_list.append("".join(item['condition'].split()))

			if len(item['indicator_list']) == 1:
				indicator_item = item['indicator_list'][0]
				temp = ''
				# if not in 
				indicator_function = functions_dict.get(indicator_item['indicator'],None)
				ti = indicator_item['indicator']
				# print ti
				if indicator_function != None:
					indicator_func = indicator_function['func']
					temp += indicator_func +'('
					params = ''
					for p in indicator_function['default_params']:
						original_val = str(indicator_item['params'].get(
								p[0], #['20', 'min']
								p[1]  # default as default_value ['20', 'day']
								))
						# params += p[0]+'='+str(indicator_item['params'].get(
						# 	p[0], #['20', 'min']
						# 	p[1]  # default as default_value ['20', 'day']
						# 	))+','
						params += p[0]+'='+exceptions_dict.get(original_val,original_val)+','
						if type(indicator_item['params'].get(p[0],None)) == type([]):
							params_suffix = '_'.join(indicator_item['params'][p[0]])
							if params_suffix!='':
								ti += '_' + params_suffix
						elif indicator_item['params'].get(p[0],None) != None:
							ti += '_'+indicator_item['params'][p[0]].replace('.','__').replace('-','___')
					temp += params[:-1] + ',action_data=data_frame)' #SMA(period=['20', 'min'],offset=[],action_data=data_frame)
					temp += ','
				
				if indicator_item['indicator'] not in ['float','range','open','high','low','close','volume','price']:# this will filter out and fundamental indicators and any stocks preser in the strategy, TODO append stock into a new list for stocks and a new list for fundamentals
					temp_eval_to_append = ti+'[iter_pos]'
					# print 'temp_eval_to_append',temp_eval_to_append
					df_eval.append('action_data.'+temp_eval_to_append) 
					self.cal_df_eval[ti] = temp[:-1]
					# print df_eval
				elif indicator_item['indicator'] in ['open','high','low','close','volume','price']:# this will add OHLC for calc only when there an addition param like offset
					if ti == 'price' or ti == 'ltp':
						ti = 'close'
					temp_eval_to_append = ti+'[iter_pos]'
					df_eval.append('action_data.'+temp_eval_to_append) 
					if '_' in ti:
						self.cal_df_eval[ti] = temp[:-1]
				else:
					df_eval.append(temp[:-1])
			if len(item['indicator_list']) == 2:
				exceptions_dict = {'min':"'min'",'3min':"'3min'",'5min':"'5min'",'10min':"'10min'",'15min':"'15min'",'30min':"'30min'",'45min':"'45min'",'hour':"'hour'",'day':"'day'",'week':"'week'",'open':"'open'",'high':"'high'",'low':"'low'",'close':"'close'",'volume':"'volume'",'ema':"'ema'",'sma':"'sma'",'%k':"'%k'",'%d':"'%d'",'r1':"'r1'",'r2':"'r2'",'r3':"'r3'",'pp':"'pp'",'s1':"'s1'",'s2':"'s2'",'s3':"'s3'",'standard':"'standard'",'fibonacci':"'fibonacci'",'simple':"'simple'",'exponential':"'exponential'",'weighted':"'weighted'",'triple':"'triple'",'triangular':"'triangular'",'double':"'double'",'hull':"'hull'",'kaufman':"'kaufman'",'tii':"'tii'",'signal':"'signal'","":'0','+vi':"'+vi'",'-vi':"'-vi'",'jaw':"'jaw'",'teeth':"'teeth'",'lips':"'lips'",'ef':'"ef"','trigger':'"trigger"','val':'"val"','vah':'"vah"','poc':'"poc"','bt':'"bt"','plow':'"plow"','phigh':'"phigh"','conversion line':'"conversion line"','base line':'"base line"','leading span a':'"leading span a"','leading span b':'"leading span b"','lagging span':'"lagging span"','yes':'"yes"','no':'"no"'} 
				for indicator_item in item['indicator_list']:
					temp = ''
					# if not in 
					indicator_function = functions_dict.get(indicator_item['indicator'],None)
					ti = indicator_item['indicator']
					# print ti
					if indicator_function != None:
						indicator_func = indicator_function['func']
						temp += indicator_func +'('
						params = ''
						for p in indicator_function['default_params']:
							original_val = str(indicator_item['params'].get(
								p[0], #['20', 'min']
								p[1]  # default as default_value ['20', 'day']
								))
							params += p[0]+'='+exceptions_dict.get(original_val,original_val)+','
							if type(indicator_item['params'].get(p[0],None)) == type([]):
								params_suffix = '_'.join(indicator_item['params'][p[0]])
								if params_suffix!='':
									ti += '_' + params_suffix.replace('%','percentage')
							elif indicator_item['params'].get(p[0],None) != None:
								ti += '_'+indicator_item['params'][p[0]].replace('.','__').replace('-','___').replace('+','plus').replace('%','percentage').replace(' ','')
						temp += params[:-1] + ',action_data=data_frame)' #SMA(period=['20', 'min'],offset=[],action_data=data_frame)
						temp += ','
					
					if indicator_item['indicator'] not in ['float','range','open','high','low','close','volume','price']:# this will filter out and fundamental indicators and any stocks preser in the strategy, TODO append stock into a new list for stocks and a new list for fundamentals
						temp_eval_to_append = ti+'[iter_pos]'
						# print 'temp_eval_to_append',temp_eval_to_append
						df_eval.append('action_data.'+temp_eval_to_append) 
						self.cal_df_eval[ti] = temp[:-1]
						# print df_eval
					elif indicator_item['indicator'] in ['open','high','low','close','volume','price']:# this will add OHLC for calc only when there an addition param like offset
						if ti == 'price' or ti == 'ltp':
							ti = 'close'
						temp_eval_to_append = ti+'[iter_pos]'
						df_eval.append('action_data.'+temp_eval_to_append) 
						if '_' in ti:
							self.cal_df_eval[ti] = temp[:-1]
					else:
						df_eval.append(temp[:-1])
	#				 temp_forming_list.append(temp[:-1])
					# print self.cal_df_eval

		# print len(comparator_list)*2,len(df_eval),len(logical_op_list)

		len_comparator_list = len(comparator_list)
		len_df_eval = len(df_eval)

		single_line_count = comparator_list.count('single line')
		if 'single line' in comparator_list:
			len_comparator_list = len_comparator_list - 0.5*single_line_count
		# add some sanity check here
		# print len_comparator_list*2,len(df_eval),len(logical_op_list)
		if len_comparator_list*2 > len(df_eval):
			error = 'Extra above or below conditions'
		elif len_comparator_list*2 < len(df_eval):
			error = 'Missing above or below conditions'
		elif len(logical_op_list) <  len(comparator_list)-1 and len(logical_op_list) != 0:
			error = 'Missing and/or'
		elif len(logical_op_list) > len(comparator_list)-1 and len(logical_op_list) != 0:
			error = 'Extra and/or'

		# print error
		# print 'comparator_list...',comparator_list,logical_op_list,df_eval
		# if no error then form the strategy string
		j = 0
		for i in range(0,len(comparator_list)):
			# print i,comparator_list[i],main
			if comparator_list[i] == ' at ':
				# especial handling of the comparator item
				reg = r'(\d+\.{0,1}\d{0,})'
				params = re.findall(reg,df_eval[j+1])
				value = '"nan"'
				range_ = []
				# print len(params),params,df_eval
				if len(params)==2:
					value = params[0]
					range_ = [params[1]]
					# print value,range_
					if '%' in df_eval[j+1]:
						range_.append('"%"')
				main += 'inrange('+df_eval[j]+','+value+',['+','.join(range_)+'])'
				j+=2
			elif comparator_list[i] == 'single line':
				main += df_eval[j]
				j+=1
			else:
				# print(comparator_list[i].strip()+' ...')
				if(comparator_list[i].strip() in ["crosses above","crosses below"]):
					custom_comparision = self.main_parser.comparator_hierarchy[comparator_list[i].strip()]['func']+'('+df_eval[j]+','+df_eval[j+1]+',pos,iter_pos)'
					# print()
					# print('.....',main)
					main += custom_comparision.replace('[iter_pos]','')
				elif("higher by" in comparator_list[i].strip()):
					comp_param = self.main_parser.change_by_parser(comparator_list[i].strip())
					custom_comparision = self.main_parser.comparator_hierarchy["higher by"]['func']+'('+df_eval[j]+','+df_eval[j+1]+','+','.join(comp_param)+',pos,iter_pos)'
					# print()
					# print('.....',main)
					main += custom_comparision.replace('[iter_pos]','')
				elif("lower by" in comparator_list[i].strip()):
					comp_param = self.main_parser.change_by_parser(comparator_list[i].strip())
					custom_comparision = self.main_parser.comparator_hierarchy["lower by"]['func']+'('+df_eval[j]+','+df_eval[j+1]+','+','.join(comp_param)+',pos,iter_pos)'
					# print()
					# print('.....',main)
					main += custom_comparision.replace('[iter_pos]','')
				else:
					# print i,comparator_list[i],i*2-i%2
					main += df_eval[j]+' '
					main += comparator_list[i]
					main += df_eval[j+1]+' '
				j+=2
			try:
				if logical_op_list!=[]:
					main += ' ' + logical_op_list[i] + ' '
			except:
				pass

		# if(len(comparator_list)==0 and len(df_eval)==1):
		# 	main = df_eval[0]
		# print '---------------'
		# print df_eval
		# print self.cal_df_eval
		# print '\n\n'
		# print logical_op_list
		# print comparator_list
		# print '---------------'
		# print error
		self.parsed_eval = main
		self.parse_error = error
		# ==>print main
		return main
