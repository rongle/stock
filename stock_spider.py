import urllib.request
import urllib.error
import pymysql
import queue
import time
import threading
from threading import Timer
from flask import Flask, render_template
from lxml import etree
import sys
from middlewares import USER_AGENTS
import random

sys.setrecursionlimit(1000000) 

app = Flask(__name__)

stock_CodeUrl = 'http://quote.eastmoney.com/stocklist.html'
institutiongrade_url = 'http://stockpage.10jqka.com.cn/'

q = queue.Queue()

def connect_mysql():
	db = pymysql.connect(host='localhost', user='root', passwd='root', db='stock',charset='utf8')
	cursor = db.cursor()
	return db, cursor

def get_request(url, num_retries=20):

	try:
		req = urllib.request.Request(url, headers={'User-Agent': random.sample(USER_AGENTS, 1)})
		html = urllib.request.urlopen(req).read()
	except urllib.error.URLError as e:
		print('Request error:', e.reason)
		html = None
		if num_retries > 0:
			if hasattr(e, 'code') and 500 <= e.code < 600:
				return get_request(url, num_retries-1)
	except urllib.error.HTTPError as e:
		print('Request error:', e.reason)
		return get_request(url, num_retries=20)
	text = etree.HTML(html)
	return text
	

def get_allstock(url):
	code_name = {}
	str = get_request(url)
	stocks = str.xpath('//*[@id="quotesearch"]/ul/li/a[@target="_blank"]/text()')	
	for stock in stocks:
		stock_name = stock.split('(')[0]
		stock_code = stock.split('(')[1].split(')')[0]	
		if stock_code[0] == '6' or stock_code[0] == '3' or stock_code[0] == '0':
			q.put(stock_code)
			print(stock_code)
			code_name[stock_code] = stock_name
	return code_name	


def get_stockgrade():
	db, cursor = connect_mysql()
	code_name = get_allstock(stock_CodeUrl)
	sql = 'insert into stock_grade (stock_name, stock_code, grade_institution, grade_date, grade_content) values (%s, %s, %s, %s, %s)'
	cursor.execute('delete from stock_grade')
	while not q.empty():
		stock_code = q.get()
		url = institutiongrade_url + stock_code
		str = get_request(url)
		institution = str.xpath('//table[@class="table-jg"]/tbody/tr[2]/td[1]/text()')
		date = str.xpath('//table[@class="table-jg"]/tbody/tr[2]/td[2]/text()')
		content = str.xpath('//table[@class="table-jg"]/tbody/tr[2]/td[3]/text()')
		if len(institution):
			grade_institution = institution[0].strip()
		else:
			grade_institution = '0'
		if len(date):
			grade_date = date[0].strip()
		else:
			grade_date = '0'
		if len(content):
			grade_content = content[0].strip()
		else:
			grade_content = '0'						
		param = (code_name[stock_code], stock_code, grade_institution, grade_date, grade_content)
		print(code_name[stock_code], stock_code, grade_institution, grade_date, grade_content)
		cursor.execute(sql, param)
		db.commit()	
	db.close()

if __name__ == '__main__':
	# get_stockgrade()
	Timer(3600, get_stockgrade()).start()  
	#get_stockgrade()