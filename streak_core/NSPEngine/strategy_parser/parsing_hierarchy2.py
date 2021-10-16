functions_dict = {
					'sma':
						{'must':['dma','daily moving average','simple moving average','sma','simple mean'],'mustnot':['stochastic','pivot'],
						'params':['period','offset'],# a list to maintain order
						'external_params':['offset'],
						'display':'simple moving average',
						'parser':'parse_period',
						'func':'SMA',
						'default_params':[('period','[20,"day"]'),('offset','[0,"day"]')],
						'params_limits':{'period':[2,3],
										'offset':[0,10]
										},# a dict for lookup
						'type':'overlap',
						'parent_tag':'ti'
						},
					'ema':
						{'must':['ema'],'mustnot':['tema', 'dema', 'tma', 'sma', 'triple', 'double', 'simple', 'triangular','stochastic'],
						'params':['period','offset'],
						'display':'exponential moving average',
						'parser':'parse_period',
						'func':'EMA',
						'default_params':[('period','[20,"day"]'),('offset','[0,"day"]')]
						},
					'wma':
						{'must':['wma'],'mustnot':[],
						'params':['period','offset'],
						'display':'weighted moving average',
						'parser':'parse_period',
						'func':'WMA',
						'default_params':[('period','[50,"day"]'),('offset','[0,"day"]')]
						},
					'tma':
						{'must':['tma'],'mustnot':['triple', 'triple exponential', 'exponential', 'simple'],
						'params':['period','offset'],
						'display':'triangular moving average',
						'parser':'parse_period',
						'func':'TMA',
						'default_params':[('period','[50,"day"]'),('offset','[0,"day"]')]
						},
					'tema':
						{'must':['tema'],'mustnot':['tma', 'triangular', 'simple', 'double'],
						'params':['period','offset'],
						'display':'triple exponential moving average',
						'parser':'parse_period',
						'func':'TEMA',
						'default_params':[('period','[50,"day"]'),('offset','[0,"day"]')]
						},
					'dema':
						{'must':['dema'],'mustnot':['tma', 'triangular', 'simple', 'triple'],
						'params':['period','offset'],
						'display':'double exponential moving average',
						'parser':'parse_period',
						'func':'DEMA',
						'default_params':[('period','[50,"day"]'),('offset','[0,"day"]')]
						},
					'volume':
						{'must':['volume'],'mustnot':['prev','opening range','moving average'],
						'params':['offset'],
						'parser':'parse_offset',
						'func':'ohlcv_comparision',
						'default_params':[('item',"'volume'"),('offset','0'),('value','None')]
						},
					'open':
						{'must':['open'],'mustnot':['prev','opening range','moving average','trend int','rsi','bollinger bandwidth','atr bands'],
						'params':['offset'],
						'parser':'parse_offset',
						'func':'ohlcv_comparision',
						'default_params':[('item',"'open'"),('offset','0'),('value','None')]
						},
					'high':
						{'must':['high'],'mustnot':['prev','opening range','moving average','trend int','rsi','period high','bollinger bandwidth','atr bands'],
						'params':['offset'],
						'parser':'parse_offset',
						'func':'ohlcv_comparision',
						'default_params':[('item',"'high'"),('offset','0'),('value','None')]
						},
					'low':
						{'must':['low'],'mustnot':['prev','below','slow','opening range','moving average','trend int','rsi','period low','bollinger bandwidth','atr bands'],
						'parser':'parse_offset',
						'params':['offset'],
						'func':'ohlcv_comparision',
						'default_params':[('item',"'low'"),('offset','0'),('value','None')]
						},
					'close':
						{'must':['close'],'mustnot':['prev','opening range','moving average','trend int','rsi','bollinger bandwidth','atr bands'],
						'parser':'parse_offset',
						'params':['offset'],
						'func':'ohlcv_comparision',
						'default_params':[('item',"'close'"),('offset','0'),('value','None')]
						},
					'prev_open':
						{'must':['prev open','previous open'],'mustnot':['high','low','close','prev n','opening range','moving average','trend int','rsi','bollinger bandwidth'],
						'params':['offset'],
						'parser':'parse_offset',
						'func':'ohlcv_comparision',
						'default_params':[('item',"'prev_open'"),('offset','1'),('value','None')]
						},
					'prev_high':
						{'must':['prev high','previous high'],'mustnot':['open','low','close','prev n','opening range','moving average','trend int','rsi','bollinger bandwidth'],
						'params':['offset'],
						'parser':'parse_offset',
						'func':'ohlcv_comparision',
						'default_params':[('item',"'prev_high'"),('offset','1'),('value','None')]
						},
					'prev_low':
						{'must':['prev low','previous low'],'mustnot':['high','open','close','prev n','opening range','moving average','trend int','rsi','bollinger bandwidth'],
						'parser':'parse_offset',
						'params':['offset'],
						'func':'ohlcv_comparision',
						'default_params':[('item',"'prev_low'"),('offset','1'),('value','None')]
						},
					'prev_close':
						{'must':['prev close','previous close'],'mustnot':['high','low','open','prev n','opening range','moving average','trend int','rsi','bollinger bandwidth'],
						'parser':'parse_offset',
						'params':['offset'],
						'func':'ohlcv_comparision',
						'default_params':[('item',"'prev_close'"),('offset',"'1'"),('value','None')]
						},
					'prev_n':
						{'must':['prev n'],'mustnot':['opening range','moving average','trend int'],
						'parser':'parser_bracket',
						'params':['field','offset','candle'],
						'func':'prev_n',
						'default_params':[('field',"'close'"),('offset',"-1"),('candle',"'min'")]
						},
					'price':
						{'must':['price','last traded price','last traded value','trading price','ltp'],'mustnot':[],
						'parser':'parse_offset',
						'params':['offset'],
						'func':'ohlcv_comparision',
						'default_params':[('item',"'ltp'"),('offset','0'),('value','None')]
						},
					'rsi':
						{'must':['rsi','relative strength index','relative strength'],'mustnot':['stochastic','ma','moving average'],
						'params':['period','offset'],
						'parser':'parse_period',
						'func':'RSI',
						'default_params':[('period','[14,"day"]'),('offset','[0,"day"]')]
						},
					'mom':
						{'must':['mom','momentum indicator'],'mustnot':['stochastic','stoch'],
						'params':['period','offset'],
						'parser':'parse_period',
						'func':'MOM',
						'default_params':[('period','[14,"day"]'),('offset','[0,"day"]')]
						},
					'cmo':
						{'must':['cmo','Chande momentum oscillator'],'mustnot':['stochastic','stoch','mom','indicator'],
						'params':['period','offset'],
						'parser':'parse_period',
						'func':'CMO',
						'default_params':[('period','[9,"day"]'),('offset','[0,"day"]')]
						},
					'ultimate_oscillator':
						{'must':['ultimate oscillator'],'mustnot':['stochastic','stoch','mom','indicator'],
						'params':['cycle_1','cycle_2','cycle_3','offset'],
						'parser':'parser_bracket',
						'func':'ULTIMATE_OSCILLATOR',
						'default_params':[('cycle_1','7'),('cycle_2','14'),('cycle_3','28'),('offset','0')]
						},
					'proc':
						{'must':['proc','Price rate of change'],'mustnot':[],
						'params':['period','offset'],
						'parser':'parse_period',
						'func':'PROC',
						'default_params':[('period','[14,"day"]'),('offset','[0,"day"]')]
						},
					'trix':
						{'must':['trix','TRIX'],'mustnot':[],
						'params':['period','offset'],
						'parser':'parse_period',
						'func':'TRIX',
						'default_params':[('period','[14,"day"]'),('offset','[0,"day"]')]
						},
					'stoch_momentum_slowk':
						{'must':['stoch momentum slowk','stochastic momentum index','stochastics momentum', 'stochastic momentum'],'mustnot':[],
						'params':['fastk_period','slowk_period','slowk_matype', 'slowd_period', 'slowd_matype'],
						'parser':'parser_bracket',
						'func':'STOCH_MOMENTUM_SLOWK',
						'default_params':[('fastk_period','[5,"day"]'),('slowk_period','[3,"day"]'),('slowk_matype','[0,"day"]'),('slowd_period','[3,"day"]'),('slowd_matype','[0,"day"]')],
						},
					'ichimoku':
						{'must':['ichimoku'],'mustnot':[],
						'params':['conversion_line_period','base_line_period','leading_span_b_period', 'lagging_span_period', 'line', 'cloud_shift','offset'],
						'parser':'parser_bracket',
						'func':'ichimoku',
						'default_params':[('conversion_line_period','[9,"day"]'),('base_line_period','[26"day"]'),('leading_span_b_period','[52,"day"]'),('lagging_span_period','[26,"day"]'),('line','"conversion line"'),('cloud_shift','"yes"'),('offset','[0,"day"]')],
						},
					'macd':
						{'must':['macd'],'mustnot':['macd signal','macd histogram'],
						'params':['fast_period','slow_period','signal_period','offset'],
						'parser':'parser_bracket',
						'func':'MACD',
						'default_params':[('fast_period','[12,"day"]'),('slow_period','[26,"day"]'),('signal_period','[9,"day"]'),('offset','[0,"day"]')]
						},
					'macd_signal':
						{'must':['macd signal'],'mustnot':[],
						'params':['fast_period','slow_period','signal_period','offset'],
						'parser':'parser_bracket',
						'func':'MACD_SIGNAL',
						'default_params':[('fast_period','[12,"day"]'),('slow_period','[26,"day"]'),('signal_period','[9,"day"]'),('offset','[0,"day"]')]
						},
					'macd_histogram':
						{'must':['macd histogram'],'mustnot':[],
						'params':['fast_period','slow_period','signal_period','offset'],
						'parser':'parser_bracket',
						'func':'MACD_HIST',
						'default_params':[('fast_period','[12,"day"]'),('slow_period','[26,"day"]'),('signal_period','[9,"day"]'),('offset','[0,"day"]')]
						},
					'parabolic_sar':
						{'must':['parabolic sar','psar'],'mustnot':[],
						'params':['acceleration_factor','acceleration_maximum','offset'],
						'parser':'parser_bracket',
						'func':'PSAR',
						'default_params':[('acceleration_factor','[0.02,"day"]'),('acceleration_maximum','[0.2,"day"]'),('offset','[0,"day"]')]
						},
					'obv':
						{'must':['obv ',' obv'],'mustnot':[],
						'params':['period','offset'],
						'parser':'parser_bracket',
						'func':'OBV',
						'default_params':[('offset','0')]
						},
					'tr':
						{'must':['tr','true range'],'mustnot':['atr', 'natr', 'average','normalised','normalized','trix','supertrend','trend int','stochastic mtm','triangular','triple','tri','star'],
						'parser':'parse_offset',
						'params':['offset'],
						'func':'TR',
						'default_params':[('offset','[0,"day"]')]
						},
					'atr':
						{'must':['atr ',' atr','average true range'],'mustnot':['bands top','bands bottom','normalised','normalized','trix','trend int'],
						'params':['period','offset'],
						'parser':'parse_period',
						'func':'ATR',
						'default_params':[('period','[14,"day"]'),('offset','[0,"day"]')]
						},
					'natr':
						{'must':['natr ',' natr','natr','normalised average true range', 'normalized average true range'],'mustnot':['bands top','bands bottom', 'average','trix','trend int'],
						'params':['period','offset'],
						'parser':'parse_period',
						'func':'NATR',
						'default_params':[('period','[14,"day"]'),('offset','[0,"day"]')]
						},
					'atr_bands_top':
						{'must':['atr bands top'],'mustnot':['bands bottom'],
						'params':['period','offset'],
						'parser':'parser_bracket',
						'func':'ATR_BAND_TOP',
						'default_params':[('period','[5,"day"]'),('shift','[3]'),('field','["close"]'),('offset','[0,"day"]')]
						},
					'atr_bands_bottom':
						{'must':['atr bands bottom'],'mustnot':['bands top'],
						'params':['period','offset'],
						'parser':'parser_bracket',
						'func':'ATR_BAND_BOTTOM',
						'default_params':[('period','[5,"day"]'),('shift','[3]'),('field','["close"]'),('offset','[0,"day"]')]
						},
					'supertrend':
						{'must':['supertrend'],'mustnot':[],
						'params':['period','multiplier','offset'],
						'parser':'parser_bracket',
						'func':'SUPERTREND',
						'default_params':[('period','[7,"day"]'),('multiplier','[3]'),('offset','0')]
						},
					'ehler_fisher':
						{'must':['ehlerfisher'],'mustnot':[],
						'params':['line','period', 'offset'],
						'parser':'parser_bracket',
						'func':'EHLER_FISHER',
						'default_params':[('line','"EF"'),('period','10'),('offset','0')],
						},
					'adx':
						{'must':['adx ',' adx'],'mustnot':[],
						'params':['period','offset'],
						'parser':'parser_bracket',
						'func':'ADX',
						'default_params':[('period','[14,"day"]'),('smoothing_period','[14,"day"]'),('offset','[0,"day"]')]
						},
					'plus_di':
						{'must':['+di','plus di'],'mustnot':[],
						'params':['period','offset'],
						'parser':'parser_bracket',
						'func':'PLUS_DI',
						'default_params':[('period','[14,"day"]'),('smoothing_period','[14,"day"]'),('offset','[0,"day"]')]
						},
					'minus_di':
						{'must':['-di','minus di'],'mustnot':[],
						'params':['period','offset'],
						'parser':'parser_bracket',
						'func':'MINUS_DI',
						'default_params':[('period','[14,"day"]'),('smoothing_period','[14,"day"]'),('offset','[0,"day"]')]
						},
					'cci':
						{'must':['cci ','commodity channel index'],'mustnot':[],
						'params':['period','offset'],
						'parser':'parse_period',
						'func':'CCI',
						'default_params':[('period','[20,"day"]'),('offset','[0,"day"]')]
						},
					'mfi':
						{'must':['mfi ','money flow index'],'mustnot':[],
						'params':['period','offset'],
						'parser':'parse_period',
						'func':'MFI',
						'default_params':[('period','[20,"day"]'),('offset','[0,"day"]')]
						},
					'willr':
						{'must':['williams %r',"william %r"],'mustnot':[],
						'params':['period','offset'],
						'parser':'parse_period',
						'func':'WILLR',
						'default_params':[('period','[14,"day"]'),('offset','[0,"day"]')]
						},
					'aroon_up':
						{'must':['aroon-up ',' aroon-up'],'mustnot':[],
						'params':['period','offset'],
						'parser':'parse_period',
						'func':'AROON_UP',
						'default_params':[('period','[14,"day"]'),('offset','[0,"day"]')]
						},
					'aroon_down':
						{'must':['aroon-down','aroon-down('],'mustnot':[],
						'params':['period','offset'],
						'parser':'parse_period',
						'func':'AROON_DOWN',
						'default_params':[('period','[14,"day"]'),('offset','[0,"day"]')]
						},
					'aroon_oscillator':
						{'must':['aroon oscillator','aroon oscillator'],'mustnot':[],
						'params':['period','offset'],
						'parser':'parse_period',
						'func':'AROON_OSCILLATOR',
						'default_params':[('period','[14,"day"]'),('offset','[0,"day"]')]
						},
					'ubb':
						{'must':['upper bollinger band','ubb','upper bollinger'],'mustnot':['bandwidth'],
						'params':['period','offset','upper_multiplier','lower_multiplier','offset'],
						'parser':'parser_bracket',
						'func':'UBB',
						'default_params':[('period','[20,"day"]'),('standard_deviations','[2,""]'),('offset','[0,"day"]')]
						},
					'mbb':
						{'must':['middle bollinger band','mbb','upper bollinger'],'mustnot':['bandwidth'],
						'params':['period','offset','upper_multiplier','lower_multiplier','offset'],
						'parser':'parser_bracket',
						'func':'MBB',
						'default_params':[('period','[20,"day"]'),('standard_deviations','[2,""]'),('offset','[0,"day"]')]
						},
					'lbb':
						{'must':['lower bollinger band','lbb','lower bollinger','low bollinger'],'mustnot':['bandwidth'],
						'params':['period','offset','upper_multiplier','lower_multiplier','offset'],
						'parser':'parser_bracket',
						'func':'LBB',
						'default_params':[('period','[20,"day"]'),('standard_deviations','[2,""]'),('offset','[0,"day"]')]
						},
					'bollinger_bandwidth':
						{'must':['bollinger bandwidth'],'mustnot':[],
						'params':['field','period','standard_deviations','offset'],
						'parser':'parser_bracket',
						'func':'BOLLINGER_BANDWIDTH',
						'default_params':[('field',"'close'"),('period','20'),('standard_deviations','20'),('offset','0')]
						},
					'range':
						{'must':['range','slippage','region'],'mustnot':['average','atr', 'tr', 'true'],
						'params':['value','range'],
						'parser':'parse_range',
						'func':'inrange',
						'default_params':[('value','0'),('range','[0.5,"%"]')]
						},
					'float':
						{
						'must':['float'],'mustnot':[],
						'params':'',
						'parser':'',
						'func':'custom_float',
						'default_params':[('value','0')]
						},
					'spinningtop':
						{'must':['spinningtop','Spinningtop'],'mustnot':[],
						'params':['trend','offset'],
						'parser':'parser_bracket',
						'func':'SPINNINGTOP',
						'default_params':[('trend','"bullish"'),('offset','[0,"day"]')]
						},
					'engulfing':
						{'must':['engulfing','Engulfing'],'mustnot':[],
						'params':['trend','offset'],
						'parser':'parser_bracket',
						'func':'ENGULFING',
						'default_params':[('trend','"bullish"'),('offset','[0,"day"]')]
						},
					'kicking':
						{'must':['engulfing','Engulfing'],'mustnot':[],
						'params':['trend','offset'],
						'parser':'parser_bracket',
						'func':'KICKING',
						'default_params':[('trend','"bullish"'),('offset','[0,"day"]')]
						},
					'morning_star':
						{'must':['morning star','Morning Star'],'mustnot':['doji','doji star','morning doji star'],
						'params':['trend','penetration','offset'],
						'parser':'parser_bracket',
						'func':'MORNING_STAR',
						'default_params':[('trend','"bullish"'),('penetration','"0.3"'),('offset','[0,"day"]')]
						},
					'doji_star':
						{'must':['doji star'],'mustnot':['morning','morning doji star'],
						'params':['trend','offset'],
						'parser':'parser_bracket',
						'func':'DOJI_STAR',
						'default_params':[('trend','"bullish"'),('offset','[0,"day"]')]
						},
					'homing_pigeon':
						{'must':['homing pigeon'],'mustnot':['doji','morning'],
						'params':['trend','offset'],
						'parser':'parser_bracket',
						'func':'HOMING_PIGEON',
						'default_params':[('trend','"bullish"'),('offset','[0,"day"]')]
						},
					'morning_doji_star':
						{'must':['morning doji star'],'mustnot':[],
						'params':['trend','penetration','offset'],
						'parser':'parser_bracket',
						'func':'MORNING_DOJI_STAR',
						'default_params':[('trend','"bullish"'),('penetration','"0.3"'),('offset','[0,"day"]')]
						},
					'three_white_soldiers':
						{'must':['three white soldiers'],'mustnot':[],
						'params':['trend','offset'],
						'parser':'parser_bracket',
						'func':'THREE_WHITE_SOLDIERS',
						'default_params':[('trend','"bullish"'),('offset','[0,"day"]')]
						},
					'abandoned_baby':
						{'must':['abandoned baby'],'mustnot':[],
						'params':['trend','offset'],
						'parser':'parser_bracket',
						'func':'ABANDONED_BABY',
						'default_params':[('trend','"bullish"'),('penetration','"0.3"'),('offset','[0,"day"]')]
						},
					'tri_star':
						{'must':['tri star'],'mustnot':[],
						'params':['trend','offset'],
						'parser':'parser_bracket',
						'func':'TRI_STAR',
						'default_params':[('trend','"bullish"'),('offset','[0,"day"]')]
						},
					'advance_block':
						{'must':['advance block'],'mustnot':[],
						'params':['trend','offset'],
						'parser':'parser_bracket',
						'func':'ADVANCE_BLOCK',
						'default_params':[('trend','"bullish"'),('offset','[0,"day"]')]
						},
					'side_3_gaps':
						{'must':['side 3 gaps'],'mustnot':[],
						'params':['trend','offset'],
						'parser':'parser_bracket',
						'func':'SIDE_GAP_3_METHODS',
						'default_params':[('trend','"bullish"'),('offset','[0,"day"]')]
						},
					'conceal_baby_swallow':
						{'must':['conceal baby swallow'],'mustnot':[],
						'params':['trend','offset'],
						'parser':'parser_bracket',
						'func':'CONCEAL_BABY_SWALL',
						'default_params':[('trend','"bullish"'),('offset','[0,"day"]')]
						},
					'stick_sandwich':
						{'must':['stick sandwich'],'mustnot':[],
						'params':['trend','offset'],
						'parser':'parser_bracket',
						'func':'STICK_SANDWICH',
						'default_params':[('trend','"bullish"'),('offset','[0,"day"]')]
						},
					'narrow_range':
						{'must':['narrow range'],'mustnot':[],
						'params':['period','candle','trend','offset'],
						'parser':'parser_bracket',
						'func':'narrow_range',
						'default_params':[('period',7),('candle',"'day'"),('offset',-1)]
						},
					'stochastic':
						{'must':['stochastic','Stochastic'],'mustnot':['stochastic momentum',"stochastic mtm",'stochastic rsi'],
						'params':['period','k','smoothen','offset'],
						'parser':'parser_bracket',
						'func':'STOCHASTIC',
						'default_params':[('period','"14"'),('k','"Fast"'),('smoothen','"True"'),('offset','[0,"day"]')]
						},
					'stochastic_rsi':
						{'must':['stochastic rsi'],'mustnot':['stochastic momentum',"stochastic mtm"],
						'params':['period','candle','k','fastk_period','fastd_period','offset'],
						'parser':'parser_bracket',
						'func':'STOCHASTIC_RSI',
						'default_params':[('period','"14"'),('candle','"close"'),('k','"Fast"'),('fastk_period','3'),('fastd_period','3'),('offset','[0,"day"]')]
						},
					'stochastic_mtm':
						{'must':['stochastic mtm'],'mustnot':[],
						'params':['k','k_period','k_smoothening_period','k_double_smoothening_period','d_period','d_ma_type','offset'],
						'parser':'parser_bracket',
						'func':'STOCHASTIC_MOMENTUM_INDEX',
						'default_params':[('k','"%k"'),('k_period','10'),('k_smoothening_period','3'),('k_double_smoothening_period','3'),('d_period','10'),('d_ma_type','"EMA"'),('offset','[0,"day"]')]
						},
					'alligator':
						{'must':['alligator'],'mustnot':[],
						'params':['signal','jaw_period','jaw_offset','teeth_period','teeth_offset','lips_period','lips_offset','offset'],
						'parser':'parser_bracket',
						'func':'alligator',
						'default_params':[('signal','jaw'),('jaw_period','13'),('jaw_offset','8'),('teeth_period','8'),('teeth_offset','5'),('lips_period','5'),('lips_offset','3'),('offset','0')]
						},
					'pivot_points':
						{'must':['pivot point'],'mustnot':[],
						'params':['signal','ptype','continous'],
						'parser':'parser_bracket',
						'func':'pivot_points',
						'default_params':[('signal','"pp"'),('ptype','standard'),('continous','"No"')]
						},
					'opening_range':
						{'must':['opening range'],'mustnot':[],
						'params':['field','Range'],
						'parser':'parser_bracket',
						'func':'opening_range',
						'default_params':[('field',"'high'"),('Range','"15min"')]
						},
					'coppock_curve':
						{'must':['coppock curve'],'mustnot':[],
						'params':['field','short_roc','long_roc','period','offset'],
						'parser':'parser_bracket',
						'func':'COPPOCK_CURVE',
						'default_params':[('field',"'close'"),('short_roc',11),('long_roc',14),('period',10),('offset',0)]
						},
					'moving_average':
						{'must':['moving average'],'mustnot':['rsi'],
						'params':['period','field','Type','offset'],
						'parser':'parser_bracket',
						'func':'moving_average',
						'default_params':[('period',20),('field',"'close'"),('Type','"simple"'),('offset',0)]
						},
					'rsi_moving_average':
						{'must':['rsi moving average','rsi ma'],'mustnot':[],
						'params':['rsi_period','field','Type','period','offset'],
						'parser':'parser_bracket',
						'func':'rsi_moving_average',
						'default_params':[('rsi_period',14),('field',"'close'"),('Type','"simple"'),('period',20),('offset',0)]
						},
					'trend_intensity_index':
						{'must':['trend int'],'mustnot':[],
						'params':['field','Type','period','signal_period','offset'],
						'parser':'parser_bracket',
						'func':'trend_intensity_index',
						'default_params':[('field',"'close'"),('Type','"tii"'),('period',14),('signal_period',9),('offset',0)]
						},
					'choppiness_index':
						{'must':['choppiness index'],'mustnot':[],
						'params':['period','offset'],
						'parser':'parser_bracket',
						'func':'choppiness_index',
						'default_params':[('period',14),('offset',0)]
						},
					'volume_profile':
						{'must':['volume profile'],'mustnot':[],
						'params':['field','VA_pct','row_size','offset','period'],
						'parser':'parser_bracket',
						'func':'volume_profile',
						'default_params':[('field',"'POC'"),('VA_pct',70),('row_size',24),('offset',-1),('period','"day"')]
						},
					'vortex_indicator':
						{'must':['vortex'],'mustnot':[],
						'params':['period','signal','offset'],
						'parser':'parser_bracket',
						'func':'vortex',
						'default_params':[('period',14),('signal','+vi'),('offset',0)]
						},
					'vwap':
						{'must':['vwap'],'mustnot':[],
						'params':['offset'],
						'parser':'parser_bracket',
						'func':'vwap',
						'default_params':[('offset',0)]
						}
					}
comparator_dict = {
					'above equal':
					{'must':['greater than equal','greater than equal to'],'mustnot':[],
					'must_not':['equal'],
					'comparision':' >= '
					}
					,
					'below equal':{'must':['less than equal','less than equal to'],'mustnot':[],
						'must_not':['equal'],
						'comparision':' <= '
						}	
					,
					'above':
						{'must':['greater than','goes above','higher than','breaches','over'],
						'must_not':['equal','crosses above','crosses'],
						'comparision':' > '
						}
					,
					'crosses above':
						{'must':['crosses above'],
						'must_not':['equal'],
						'comparision':' crosses above ',
						'func':'crosses_above'
						}
					,
					'crosses below':
						{'must':['crosses below'],
						'must_not':['equal'],
						'comparision':' crosses below ',
						'func':'crosses_below'
						}
					,
					'equal to':
						{'must':['equal to'],'mustnot':['above','below','higher','lower'],
						'must_not':['above','below','higher','lower'],
						'comparision':' == '
						}
					,
					'below':{'must':['less than','lesser than','goes below','lower than','under','falls below'],'mustnot':[],
						'must_not':['equal','crosses below'],
						'comparision':' < '
						},
					'at':{'must':['@'],'mustnot':[],
						'must_not':['equal'],
						'comparision':' at '
						}
						,
					'higher by':{'must':['higher by'],'mustnot':[],
						'must_not':['equal'],
						'comparision':'higher by',
						'parser':'change_by_parser',
						'func':'higher_by',
						'syntax':'higher_by(<1>,<2>,<3>)',
						'split_regex':'higher by \d+\.{0,1}\d{0,}.*than'
						},
					'lower by':{'must':['lower by'],'mustnot':[],
						'must_not':['equal'],
						'comparision':'lower by',
						'parser':'change_by_parser',
						'func':'lower_by',
						'syntax':'higher_by(<1>,<2>,<3>)',
						'split_regex':'lower by \d+\.{0,1}\d{0,}.*than'
						}
					}

default_param_mapping = {
			'yesterday':"['1','day']",
			'previous day':"['1','day']"
		}