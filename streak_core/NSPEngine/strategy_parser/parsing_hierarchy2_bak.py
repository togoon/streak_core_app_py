functions_dict = {
					'sma':
						{'must':['dma','daily moving average','simple moving average','moving average','average','sma','simple mean'],
						'params':['period','offset'],# a list to maintain order
						'external_params':['offset'],
						'display':'simple moving average',
						'parser':'parse_period_with_offset',
						'func':'SMA',
						'default_params':[('period','[20,"day"]'),('offset','[0,"day"]')],
						'params_limits':{'period':[2,3],
										'offset':[0,10]
										},# a dict for lookup
						'type':'overlap',
						'parent_tag':'ti'
						},
					'ema':
						{'must':['ema','exponential','exponential moving average','exponential moving','exponential ma'],
						'params':['period','offset'],
						'display':'exponential moving average',
						'parser':'parse_period_with_offset',
						'func':'EMA',
						'default_params':[('period','[20,"day"]'),('offset','[0,"day"]')]
						},
					
					'volume':
						{'must':['volume'],
						'params':['offset'],
						'parser':'parse_offset',
						'func':'ohlcv_comparision',
						'default_params':[('item',"'volume'"),('offset','0'),('value','None')]
						},
					'open':
						{'must':['open'],
						'params':['offset'],
						'parser':'parse_offset',
						'func':'ohlcv_comparision',
						'default_params':[('item',"'open'"),('offset','0'),('value','None')]
						},
					'high':
						{'must':['high'],
						'params':['offset'],
						'parser':'parse_offset',
						'func':'ohlcv_comparision',
						'default_params':[('item',"'high'"),('offset','0'),('value','None')]
						},
					'low':
						{'must':['low'],
						'parser':'parse_offset',
						'params':['offset'],
						'func':'ohlcv_comparision',
						'default_params':[('item',"'low'"),('offset','0'),('value','None')]
						},
					'close':
						{'must':['close'],
						'parser':'parse_offset',
						'params':['offset'],
						'func':'ohlcv_comparision',
						'default_params':[('item',"'close'"),('offset','0'),('value','None')]
						},
					'price':
						{'must':['price','last traded price','last traded value','trading price','ltp'],
						'parser':'parse_offset',
						'params':['offset'],
						'func':'ohlcv_comparision',
						'default_params':[('item',"'ltp'"),('offset','0'),('value','None')]
						},
					'rsi':
						{'must':['rsi','relative strength index','relative strength'],
						'params':['period','offset'],
						'parser':'parse_period_with_offset',
						'func':'RSI',
						'default_params':[('period','[15,"day"]'),('offset','[0,"day"]')]
						},
					'macd':
						{'must':['macd'],
						'params':['period','offset'],
						'parser':'parse_period_with_offset',
						'func':'RSI',
						'default_params':[('offset','[0,"day"]'),('fast_period','[12,"day"]'),('slow','[26,"day"]'),('signal_period','[9,"day"]'),]
						},
					'obv':
						{'must':['obv ',' obv'],
						'params':['period','offset'],
						'parser':'parse_period_with_offset',
						'func':'OBV',
						'default_params':[('period','[15,"day"]'),('offset','[0,"day"]')]
						},
					'atr':
						{'must':['atr ',' atr'],
						'params':['period','offset'],
						'parser':'parse_period_with_offset',
						'func':'ATR',
						'default_params':[('period','[14,"day"]'),('offset','[0,"day"]')]
						},
					'aroon_up':
						{'must':['aroon-up ',' aroon-up'],
						'params':['period','offset'],
						'parser':'parse_period_with_offset',
						'func':'AROON_UP',
						'default_params':[('period','[14,"day"]'),('offset','[0,"day"]')]
						},
					'aroon_down':
						{'must':['aroon-down','aroon-down('],
						'params':['period','offset'],
						'parser':'parse_period_with_offset',
						'func':'AROON_DOWN',
						'default_params':[('period','[14,"day"]'),('offset','[0,"day"]')]
						},
					'ubb':
						{'must':['upper bollinger band','ubb','upper bollinger'],
						'params':['period','offset','upper_multiplier','lower_multiplier'],
						'parser':'parse_bb',
						'func':'UBB',
						'default_params':[('period','[15,"day"]'),('offset','[0,"day"]'),('upper_multiplier','[2]'),('lower_multiplier','[2]')]
						},
					'mbb':
						{'must':['middle bollinger band','mbb','upper bollinger'],
						'params':['period','offset','upper_multiplier','lower_multiplier'],
						'parser':'parse_bb',
						'func':'MBB',
						'default_params':[('period','[15,"day"]'),('offset','[0,"day"]'),('upper_multiplier','[2]'),('lower_multiplier','[2]')]
						},
					'lbb':
						{'must':['lower bollinger band','lbb','lower bollinger','low bollinger'],
						'params':['period','offset','upper_multiplier','lower_multiplier'],
						'parser':'parse_bb',
						'func':'LBB',
						'default_params':[('period','[15,"day"]'),('offset','[0,"day"]'),('upper_multiplier','[2]'),('lower_multiplier','[2]')]
						},
					'range':
						{'must':['range','slippage','region'],
						'params':['value','range'],
						'parser':'parse_range',
						'func':'inrange',
						'default_params':[('value','0'),('range','[0.5,"%"]')]
						},
					'float':
						{
						'must':['float'],
						'params':'',
						'parser':'',
						'func':'custom_float',
						'default_params':[('value','0')]
						}
					}
comparator_dict = {
					'above equal':
					{'must':['greater than equal','greater than equal to'],
					'must_not':['equal'],
					'comparision':' >= '
					}
					,
					'below equal':{'must':['less than equal','less than equal to'],
						'must_not':['equal'],
						'comparision':' <= '
						}	
					,
					'above':
						{'must':['greater than','goes above','above','crosses','higher than','breaches','over'],
						'must_not':['equal'],
						'comparision':' > '
						}
					,
					'below':{'must':['less than','lesser than','goes below','below','lower than','under','falls below'],
						'must_not':['equal'],
						'comparision':' < '
						},
					'at':{'must':['@'],
						'must_not':['equal'],
						'comparision':' at '
						}
					}

default_param_mapping = {
			'yesterday':"['1','day']",
			'previous day':"['1','day']"
		}