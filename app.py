import pymysql
import time
import threading
from flask import Flask, render_template
import sys


sys.setrecursionlimit(1000000) 

app = Flask(__name__)


def connect_mysql():
	db = pymysql.connect(host='localhost', user='root', passwd='root', db='stock',charset='utf8')
	cursor = db.cursor()
	return db, cursor

def query_stock():
	db, cursor = connect_mysql()
	sql = 'select * from stock_grade order by grade_date DESC limit 100'
	cursor.execute(sql)
	result = ''
	for l in cursor.fetchall():
		result += '<tr><td>' + l[0] + '</td><td>' + l[1] + '</td><td>' + l[2] + '</td><td>' + l[3] + '</td><td>' + l[4] + '</td></tr>'
	return result


@app.route('/')
def index():
	return render_template('index.html')

@app.route('/query', methods=['GET'])
def get_stockgrade():
	return query_stock()


if(__name__ == '__main__'):
	#get_stockgrade()
	#print(query_stock())
	app.run()