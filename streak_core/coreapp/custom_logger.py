import time                                                                                                             
import datetime                                                                                                         
import re                                                                                                               
import dateutil                                                                                                         
import dateutil.parser                                                                                                  
                                                                                                                        
def parse_line(logger, line):                                                                                           
    data = re.split("\s\[.*?\]\s", line)                                                                                
    # datadog|mahesh|warning|candle_formation|Candle for token 779521 formed                                            
    p = data[1].split("|")                                                                                              
    if p[0] == "datadog":                                                                                               
        date_string = data[0]                                                                                           
        # 2017-11-22 09:14:05+0000                                                                                      
        date = dateutil.parser.parse(date_string)                                                                       
        #date = date.astimezone(dateutil.tz.tzutc())                                                                    
        timestamp = int(date.strftime("%s"))                                                                            
        user = p[1]                                                                                                     
        text = p[4]                                                                                                     
        event_type = p[3]                                                                                               
        alert_type = p[2]                                                                                               
        return {"msg_title": user,                                                                                      
                "timestamp": timestamp,                                                                                 
                "msg_text": text,                                                                                       
                "priority": "normal",                                                                                   
                "alert_type": alert_type,                                                                               
                "aggregation_key": user                                                                                 
                }                                                                                                       
    else:                                                                                                               
        return None