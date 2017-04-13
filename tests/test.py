#!/usr/bin/env
# -*- coding: utf-8 -*-
import re
import cookielib
import urllib
import urllib2
import logging
import sys

import sched
import time
from datetime import datetime as dt
import datetime
import timeit

from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import freeze_support
from multiprocessing import cpu_count

try:
	import requests
	from bs4 import BeautifulSoup

except ImportError:
		print "\nPlease make sure you have BeautifulSoup and requests modules installed!\n"
		exit()

class MuniRegister(object):

	def __init__(self):
		super(MuniRegister, self).__init__()

	def registerLesson(self, url):
		print "[%s] Registered => %s" % (str(dt.now()), url)
		time.sleep(1)

	def __call__(self, x):
		return self.registerLesson(x)

if __name__ == "__main__":
	freeze_support()

	sa = MuniRegister()

	#get list of URLs which will be clicked
	regURLs = ['One', 'Two', 'Three']

	pool = ThreadPool(cpu_count())
	start = 0

	def threadPoolExecutor(param):
		global start
		start = timeit.default_timer()
		print param,"\n"
		results = pool.map(sa, param)
		pool.close()
		pool.join()

	#TIMER
	def now_str():
		t = dt.now().time()
		return t.strftime("%H:%M:%S")

	# Build a scheduler object that will look at absolute times
	scheduler = sched.scheduler(time.time, time.sleep)
	
	# Put task on queue. Format H, M, S
	daily_time = datetime.time(22, 17, 50)
	first_time = dt.combine(dt.now(), daily_time)
	print "%s -> cekam na %s\n" % (now_str(), daily_time)

	#start = timeit.default_timer()
	
	# time, priority, callable, *args
	scheduler.enterabs(time.mktime(first_time.timetuple()), 1, threadPoolExecutor, (regURLs,))
	scheduler.run()



	#time.sleep(3)

	stop = timeit.default_timer()
	print "\nTime elapsed: ", stop - start

