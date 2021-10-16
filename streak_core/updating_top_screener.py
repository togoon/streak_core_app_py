import csv 
import requests 
# import coreapp.view.screener as sc 
 
with open('popular_screener1.csv','rt')as f: 
  data = csv.reader(f) 
  for row in data: 
	url = "http://127.0.0.1/load_screener_to_archive/?id={}&secret=testing_initialization&tag={}".format(row[1],row[2]) 
	print row 
	response = requests.request("GET", url) 
	print response.text
	# break