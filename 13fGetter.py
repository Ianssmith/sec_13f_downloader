from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from downloader import Downloader
import pandas as pd
import os
import re



baseurl = "https://www.sec.gov"
userAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"

#initialize robotparser
import robotexclusionrulesparser
rp = robotexclusionrulesparser.RobotExclusionRulesParser()

#parse robots file
#import robotparser -(python2)
#rp = robotparser.RobotFileParser() -(python2)
rp.user_agent = userAgent
rp.fetch = baseurl+"/robots.txt"
#rp.read() -(python2)

landing = "https://www.sec.gov/edgar/searchedgar/companysearch.html"

#myTest = ["0001035674","0001079114","0001061768","0001067983","0001061165","0001029160","0000904571","0001166559"]
#landing = "https://en.wikipedia.org/wiki/42_(number)"
D = Downloader()

#controller
def crawl(start):
#def crawl(start, symbol):
	landPage = D(start)
	if landPage['code'] >= 400:
		print("Could not retrieve requested page: "+landPage['code'])
		shtml = None
	else:
		soup = BeautifulSoup(landPage['html'],"html5lib")
		form = soup.find(id='fast-search')
		form_action = form['action']
		form_fields = form.find_all('input')#,value=re.compile("(?!Search).*"))
		search = {}
		for el in form_fields:
			try:
				search[el['name']] = el['value']
			except:
				print("please enter Ticker or CIK number: ")
				symbol = input()
				search['CIK'] = symbol
				print("Documents are searched by the 100, how many hundreds should we look back? ")
				numQs = int(input())
				#numQs = 2
		for x in range(numQs):
			startQ = str(x*100)
			endQ = str((x+1)*100)
			search['start'] = startQ
			search['count'] = endQ
			#searchRange = "&start="+startQ+"&count="+endQ
			shtml = D(baseurl+form_action,search)
			profileSoup = BeautifulSoup(shtml['html'],"html5lib")
			dirName = profileSoup.find('span', class_='companyName').contents[0]
			if not os.path.exists(dirName):
				os.makedirs(dirName)
			tables = profileSoup.find_all('table')
			rows = tables[2].tbody.find_all('tr')
			docPages = []
			dates = []
			for i in rows:
				if "13F" in i.contents[1].string:
					docPages.append(BeautifulSoup(D(baseurl + i.contents[1].find_next_sibling('td').find('a').get('href'))['html'],"html5lib"))
					dates.append(i.contents[1].find_next_siblings('td')[2].get_text()+"_"+search['CIK'])

			#dataDict = {}
			for i,page in enumerate(docPages):
				getDocs(page,dirName, dates[i])

				#pathName = dirName+"/"+dates[i]+".xml"
				#dataDict[dates[i]] = getDocs(page,pathName, dirName)
				#dataDict[dates[i]] = getDocs(page,dirName, dates[i])
				#print(len(xfilenames))

			print("length of files and dates v")
			print(len(docPages))
			print(len(xfiles))
			print(len(dates))
			for k,name in enumerate(xfiles):
				if k < len(dates):
					parseXMLdoc(name, dirName, dates[k])

	#dataPanel = pd.Panel(dataDict)

xfiles = []

#downloads xml files
regXML = re.compile('.*(?<!doc)\.xml$')
def getDocs(soupObj,direcName,date):
	for link in soupObj.find_all('a', href=regXML):
		path = link.get('href')
		fn = direcName+"/"+date+".xml"
		data = D(baseurl+path, doctype='xml',filename=fn)
		if data[0] not in xfiles:
			xfiles.append(data[0])


cleanUrl = re.compile('{http.*}')

#parses xmlfiles to tsv files
def parseXMLdoc(filename,dr,dt):
	tsvdir = dr+"/tsvFiles"
	if not os.path.exists(tsvdir):
		os.makedirs(tsvdir)

	tsvFileName = "/"+dt+".tsv"
	tree=ET.parse(filename)
	root = tree.getroot()
	cols = []
	for j, infotable in enumerate(root):
		data = {}
		for subEl in infotable:
			if len(subEl) == 0:
				data[cleanUrl.sub('',subEl.tag)] = cleanUrl.sub('',subEl.text)
			else:
				data[cleanUrl.sub('',subEl.tag)] = []
				for m in subEl:
					data[cleanUrl.sub('',subEl.tag)].append("["+cleanUrl.sub('',m.tag)+","+cleanUrl.sub('',m.text)+"]")#subEl.text
		cols.append(data)
	df = pd.DataFrame(cols)
	#print(df.head())
	df.to_csv(tsvdir+tsvFileName, sep="\t")
	return df


#for z in myTest:
	#crawl(landing,z)

crawl(landing)

