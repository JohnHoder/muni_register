#!/usr/bin/env
# -*- coding: utf-8 -*-
import re
import cookielib
import urllib
import urllib2
import logging
import sys

import collections

import sched
import time
from datetime import datetime as dt
import datetime
import timeit

#Spawn threads or processes?
#from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool as ThreadPool
from multiprocessing import freeze_support
from multiprocessing import cpu_count

from config import username, password, studium, fakulta, season

try:
	import requests
	from bs4 import BeautifulSoup

except ImportError:
		print "\nPlease make sure you have BeautifulSoup and requests modules installed!\n"
		exit()

DEBUG = False

if DEBUG == True:
	try:
		import http.client as http_client
	except ImportError:
		# Python 2
		import httplib as http_client

	http_client.HTTPConnection.debuglevel = 1

	# You must initialize logging, otherwise you'll not see debug output.
	logging.basicConfig()
	logging.getLogger().setLevel(logging.DEBUG)
	requests_log = logging.getLogger("requests.packages.urllib3")
	requests_log.setLevel(logging.DEBUG)
	requests_log.propagate = True


class MuniRegister(object):

	def __init__(self, username, password, season, fakulta, studium):
		super(MuniRegister, self).__init__()
		self.username = username
		self.password = password

		self.season = season
		self.fakulta = fakulta
		self.studium = studium

		self.session = requests.Session()

		self.dictLessonsNameToID = collections.OrderedDict()

	def getTextOnly(self, soupedHtml):
		# kill all script and style elements
		for script in soupedHtml(["script", "style"]):
			script.extract()    # rip it out
		# get text
		text = soupedHtml.get_text(separator=' ')
		# break into lines and remove leading and trailing space on each
		lines = (line.strip() for line in text.splitlines())
		# break multi-headlines into a line each
		chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
		# drop blank lines
		text = '\n'.join(chunk for chunk in chunks if chunk)

		return (text)

	def login(self):
		url_login2 = 'https://muni.islogin.cz/login/34pu97005hst6XKaJ9yCzkdS'

		print "\n"
		print "######################################################"

		header2={
				"Host" : "muni.islogin.cz",
				"User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0",
				"Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
				"Accept-Language" : "en-US,en;q=0.5",
				"Accept-Encoding" : "gzip, deflate, br",
				"Referer" : "https://muni.islogin.cz/login/34pu97005hst6XKaJ9yCzkdS",
				"Upgrade-Insecure-Requests" : "1",
				"Connection" : "close",
				"Content-Type" : "application/x-www-form-urlencoded",
				}

		get_params = {}

		res = self.session.get(url_login2, params=get_params, headers=header2, allow_redirects=False)

		redir_loc = res.headers['Location']
		print res.status_code, res.reason, " => ", redir_loc

		print "######################################################"

		redir1 = self.session.get(redir_loc, allow_redirects=False)
		print "Session [iscreds]:", redir1.cookies['iscreds']
		session1 = redir1.cookies['iscreds']
		redir_loc = redir1.headers['Location']
		print redir1.status_code, redir1.reason, " => ", redir_loc

		print "######################################################"

		redir2 = self.session.get(redir_loc, allow_redirects=False)
		print "Session [islogincreds]:", redir2.cookies['islogincreds']
		session2 = redir2.cookies['islogincreds']
		print redir2.url
		print redir2.status_code, redir2.reason

		print "######################################################"

		cookies = dict(iscreds=session1, islogincreds=session2)

		payload = {
					"akce" : "login",
					"credential_0" : self.username,
					"credential_1" : self.password,
					"submit" : "P%C5%99ihl%C3%A1sit+se",
					"uloz" : "uloz"
					}

		header3={
				"Host" : "muni.islogin.cz",
				"User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0",
				"Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
				"Accept-Language" : "en-US,en;q=0.5",
				"Accept-Encoding" : "gzip, deflate, br",
				"Referer" : redir2.url,
				"Cookie" : "islogincreds=" + session2 + "",
				"Connection" : "keep-alive",
				"Upgrade-Insecure-Requests" : "1",
				}

		res3 = self.session.post(redir2.url, params=get_params, data=payload, headers=header3, allow_redirects=False)

		print "######################################################"

		url_we_out_there = "https://is.muni.cz/auth/"

		redir2 = self.session.get(url_we_out_there, allow_redirects=False)
		if("administrativa" in redir2.text):
			print "~We logged in, boyyy!"
		else:
			print "NOT LOGGED IN ???"
		#print redir2.text

		print "######################################################"
		print "######################################################"
		print "\n\n"

	def loadDataFromFile(self, filename):
		mydata = collections.OrderedDict()

		with open(filename) as f:
			for line in f:
				#print line
				datum = line.strip().split(' ')
				mydata[datum[0]] = datum[1]

		#print mydata
		return mydata
		
	def processData(self, dictOfLessons):

		internalLessonDict = collections.OrderedDict()

		url_faecher = ("https://is.muni.cz/auth/student/zapis?studium=%s;obdobi=%s") % (self.studium, self.season)

		header={
				"User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0",
				"Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
				"Accept-Language" : "en-US,en;q=0.5",
				"Accept-Encoding" : "gzip, deflate, br",
				"Referer" : "https://is.muni.cz/auth/student/?studium=%s;lvs=p" % (self.studium),
				}

		#IS SOMETHING WRONG HERE? 10% chance the program will crash here
		
		statuscode = 0
		while statuscode != requests.codes.ok:  #send request three times and let's hope at least one of them will be successful
			try:
				#print x+1
				web_faecher = self.session.get(url_faecher, headers=header, allow_redirects=True)
				web_faecher.encoding = 'utf-8'
				statuscode = web_faecher.status_code
				print "Cteni registrovanych predmetu OK -> ", web_faecher.status_code, "\n"
				#print web_faecher.text[0:50]
				#file = open("output.html","w")
				#file.write(str(web_faecher.text.encode('utf8')))
				#file.close()
				#time.sleep(1)
			except requests.exceptions.RequestException as e:
				print("WEIRD -> ", e)
				pass
			except:
				print("Unexpected error:", sys.exc_info()[0])
				pass

		soup = BeautifulSoup(web_faecher.text, "lxml")
		#soup.prettify()
		#print soup

		for lesson in dictOfLessons:
			lesson_id = ""
			elems = soup(text=re.compile(r"" + lesson + ""))
			if elems != [] and elems[0].parent['class'][0] == "okno":
				sub = elems[0].parent.parent.parent
				page = sub.find('a', text=re.compile(ur'zvolit(.*)', re.DOTALL), attrs={'href': re.compile(ur'' + '../seminare/student?' + '(.*)'), 'class' : 'maybe'})
				page2 = sub.find('a', text=re.compile(ur'změnit(.*)', re.DOTALL), attrs={'href': re.compile(ur'' + '../seminare/student?' + '(.*)')})
				if page != None:
					print "[%s] byl pridan k casovanemu zapisu" % (lesson)
					#print page
					lesson_id = re.findall(r'\d+', page['href'])[3]
				else:
					if page2 != None:
						print "[%s] jiz ma zvolenou seminarni skupinu" % (lesson)
						#print "\n" , page2
						continue
			else:
				print "[%s] neni registrovan!" % (lesson)
				continue

			#Assign lesson_id to study group
			internalLessonDict[lesson_id] = dictOfLessons[lesson]

			#Assign lessonName to lessonID
			self.dictLessonsNameToID[lesson] = lesson_id

		#print internalLessonDict
		print "######################################################"
		print "\n"
		return internalLessonDict

	def prepareRegistrationURLs(self, dictOfLessons, dictOfInternalLessons):

		#print dictOfLessons
		#print dictOfInternalLessons

		listOfRegURLs = []

		header1={
				"User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0",
				"Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
				"Accept-Language" : "en-US,en;q=0.5",
				"Accept-Encoding" : "gzip, deflate, br",
				"Referer" : "https://is.muni.cz/auth/student/zapis?studium=%s;obdobi=%s" % (self.studium, self.season),
				}

		for (lesson_id, lessonGroup), (lessonName, lessonID) in zip(dictOfInternalLessons.items(), self.dictLessonsNameToID.items()):
			url_fach = "https://is.muni.cz/auth/seminare/student?fakulta=%s;obdobi=%s;studium=%s;akce=podrob;predmet=%s" % (self.fakulta, self.season, self.studium, lesson_id)

			#print "###"
			#print lesson_id, lessonGroup
			#print lessonName, lessonID
			#print "###"

			res = self.session.get(url_fach, headers=header1, allow_redirects=False)
			#res.encoding = 'utf-8'
			soupx = BeautifulSoup(res.text, "lxml")

			elems = soupx.find('h5', text=re.compile(u'' + lessonName + '/' + lessonGroup))

			try:
				sub = elems.parent.parent.parent
			except Exception, e:
				print "Skupina nebyla nalezena -> ", e
				continue
				
			page = sub.find('a', text=re.compile(ur'zkusit se přihlásit(.*)', re.DOTALL))
			regurl = page['href']
			reg_id = (re.findall('(?<=prihlasit\=)\d+', regurl))[0]

			url_reg = "https://is.muni.cz/auth/seminare/student?fakulta=%s;obdobi=%s;studium=%s;predmet=%s;prihlasit=%s;akce=podrob;provest=1;stopwindow=1;design=m" % (self.fakulta, self.season, self.studium, lesson_id, reg_id)

			listOfRegURLs.append(url_reg)

		#print listOfRegURLs
		return listOfRegURLs

	def registerLesson(self, url):

		lesson_id = (re.findall('(?<=predmet\=)\d+', url))[0]

		header2={
				"User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0",
				"Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
				"Accept-Language" : "en-US,en;q=0.5",
				"Accept-Encoding" : "gzip, deflate, br",
				"Referer" : "https://is.muni.cz/auth/seminare/student?fakulta=%s;obdobi=%s;studium=%s;akce=podrob;predmet=%s" % (self.fakulta, self.season, self.studium, lesson_id),
				}

		#Here we come
		reg_res = self.session.get(url, headers=header2, allow_redirects=False)
		reg_res.encoding = 'utf-8'
		bsoup = BeautifulSoup(reg_res.text, "lxml")
		#print soup
		#find = soup(text=re.compile(r"" + "zdurazneni varovani" + ""))
		message = bsoup.find("div", {"class": re.compile(ur'zdurazneni(.*)', re.DOTALL)}).contents
		#print "[%s / %s] -> %s" % (lessonName, lessonGroup, self.getTextOnly(message[0]))
		print "[%s] [%s] -> %s" % (str(dt.now()), lesson_id, self.getTextOnly(message[0]))

	def __call__(self, x):
		return self.registerLesson(x)


if __name__ == "__main__":
	freeze_support()
	
	filename = "seminars.txt"

	sa = MuniRegister(username, password, season, fakulta, studium)
	sa.login()

	userData = sa.loadDataFromFile(filename)

	processedData = sa.processData(userData)

	#get list of URLs which will be clicked
	regURLs = sa.prepareRegistrationURLs(userData, processedData)

	pool = ThreadPool(cpu_count())
	start = 0

	def threadPoolExecutor(param):
		global start
		start = timeit.default_timer()

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
	daily_time = datetime.time(17, 0, 0)
	first_time = dt.combine(dt.now(), daily_time)
	print "%s -> cekam na %s\n" % (now_str(), daily_time)

	# time, priority, callable, *args
	scheduler.enterabs(time.mktime(first_time.timetuple()), 1, threadPoolExecutor, (regURLs,))
	scheduler.run()

	stop = timeit.default_timer()
	print "\nTime elapsed for registration: ", stop - start, " seconds"



