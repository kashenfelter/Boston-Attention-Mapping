################################################################################
# Module that connects to Globe API and to Globe FTP data sources
# Gets latest data
################################################################################
import simplejson 
import json
import urllib2
from DBManager import DBManager
import utils
import ConfigParser
from datetime import date, timedelta


def fetchLatestArticlesFromAPI(conn):
	print conn

	db = conn.db

	APP_ROOT_DIR=utils.getAppRootDir()
	config = ConfigParser.ConfigParser()
	config.read(APP_ROOT_DIR + 'python/globe.config')

	max_num_articles=config.getint('boston_globe','max_num_articles')
	articles_at_a_time=config.getint('boston_globe','articles_at_a_time')
	api_fields=config.get('boston_globe','api_fields')
	
	lastArticleDate=""
	results = db.view('globe/last_article_date')
	for row in results:       
	 	lastArticleDate = row['value']
	
	if (lastArticleDate ==""):
		lastArticleDate = "20100101"
	today = date.today()
	todayStr = today.strftime('%Y%m%d')

	size = 0
	allArticles = []
	while size<max_num_articles:
		req = urllib2.Request(	"http://50.17.92.83/s?key=catherine&bq=printpublicationdate:" + 
								lastArticleDate +".."+todayStr+"&return-fields="+
								api_fields+
								"&size="+str(articles_at_a_time)+"&"+
								"start="+str(size)+
								"&rank=printpublicationdate")
		print req.get_full_url()
		opener = urllib2.build_opener()
		f = opener.open(req)

		try:
			data = simplejson.load(f)
		except:
			print "JSONDecodeError\nEither there was no data found or some other parsy thing happened"
			break

		print str(data["hits"]["found"]) + " articles found"

		conn.db_metadata["total_articles_available"] = data["hits"]["found"]


		if max_num_articles > int(data["hits"]["found"]):
			max_num_articles = data["hits"]["found"]
			print "Resetting max articles to " + str(data["hits"]["found"])
		
		allArticles.extend(data["hits"]["hit"])
		
		if len(allArticles) == 0:
			break
		size += articles_at_a_time

	return allArticles

def fetchLatestFullTextFromFTP(db):
	# go to file system, grab latest, return results
	return ""