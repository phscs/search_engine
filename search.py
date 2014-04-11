import urllib
import string
import pickledb
import urlparse

max_crawls = 1000

db = pickledb.load("db.db", False)
db.dcreate("index")
db.dcreate("popularity_index")

"""
db.dadd("index", (key, value))		>> adds key-value pair to dictionary
db.dgetall("index")					>> returns entire dictionary
db.dget("index", key)				>> returns value for key
db.pop("index", key)				>> removes key-value pair from dictionary

db.deldb()							>> clears out database
db.dump()							>> writes the database to disk
"""

def get_links(source):
	links = []
	link_temp = ""
	collecting_characters = False

	for i in range(0, len(source)):
		character = source[i]

		if source[i-6 : i] == 'href="' or source[i-6 : i] == "href='":
			collecting_characters = True

		if collecting_characters:
			if character == '"' or character == "'":
				collecting_characters = False
				links.append(link_temp)
				link_temp = ""
			else:
				try:
					link_temp += character.decode("utf-8")
				except:
					pass

	return links

def get_keywords(source):
	collecting_characters = False
	collected_characters = ""

	for i in range(0, len(source)):
		character = source[i]

		if character == "<":
			collecting_characters = False
		elif character == ">":
			collecting_characters = True
		elif collecting_characters:
			if character in string.punctuation or character in ["\r","\n","\t"]:
				collected_characters += u" "
			else:
				try:
					collected_characters += character.lower().decode("utf-8")
				except:
					pass

	keywords = collected_characters.split(" ")

	while "" in keywords:
		keywords.remove("")

	for word in keywords:
		if word in keywords[keywords.index(word)+1:]:
			keywords.remove(word)

	return keywords

def add_to_index(url, keywords):
	index = db.dgetall("index")

	for keyword in keywords:
		if keyword not in index:
			value = [[url, 0]]
			db.dadd("index", (keyword, value))

		else:
			url_already_in_entry = False

			for entry in index[keyword]:
				if url == entry[0]:
					url_already_in_entry = True

			if not url_already_in_entry:
				urls = index[keyword]
				urls.append([url, 0])
				db.dadd("index", (keyword, urls))

def crawl(seed_page_url):
		urls_to_crawl = [seed_page_url]
		urls_already_crawled = []
		crawls = 0

		while len(urls_to_crawl) > 0 and crawls < max_crawls:
			try:
				url = urls_to_crawl[0]
				source = urllib.urlopen(url).read()
				print "crawling " + url

				print "getting keywords..."
				keywords = get_keywords(source)

				print "adding to index..."
				add_to_index(url, keywords)

				print "upranking relevance..."
				uprank_relevance(keywords, source, url)

				print "getting links..."
				links = get_links(source)

				print "upranking popularity..."
				for link in links:
					parsed_link = urlparse.urlparse(link)

					if link[0:2] == "//":
						link = "http:" + link
					elif link[0] == "/" and link[1] != "/":
						parsed_url = urlparse.urlparse(url)
						url_domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_url)
						link = url_domain + link

					uprank_popularity(link)

					if link != url and link not in urls_already_crawled and link not in urls_to_crawl:
						urls_to_crawl.append(link)

			except Exception, e:
				print str(e)

			print "writing to disk..."
			db.dump()
			urls_to_crawl.remove(url)
			urls_already_crawled.append(url)
			crawls += 1

		print "crawl finished."

def uprank_popularity(url):
	popularity_index = db.dgetall("popularity_index")

	if url in popularity_index:
		rank = db.dget("popularity_index", url) + 1
		db.dadd("popularity_index", (url, rank))
	else:
		db.dadd("popularity_index", (url, 1))

def uprank_relevance(keywords, source, url):
	try:
		source = source.decode("utf-8").lower()
	except:
		pass

	for keyword in keywords:
		urls = db.dget("index", keyword)

		for entry in urls:
			if entry[0] == url:
				entry[1] = source.count(keyword)

		db.dadd("index", (keyword, urls))

def query(search_string, rel, pop):
	sanitized_search_string = ""

	for character in search_string:
		if character not in string.punctuation:
			sanitized_search_string += character.lower()

	keywords = sanitized_search_string.split(" ")

	index = db.dgetall("index")
	results = []

	for keyword in keywords:
		if keyword in index:
			results.append(index[keyword])

	if (len(results) != 0):
		urls = []

		for i in range(0, len(results)):
			entry = results[i]
			for url in entry:
				in_other_entries = True
				for other_entry in (results[:i] + results[i+1:]):
					if url not in other_entry:
						in_other_entries = False
				if in_other_entries and url not in urls:
					urls.append(url)

		sorted_urls = sort(urls, rel, pop)

		return sorted_urls

	else:
		return ["No results found."]

def sort(urls, relevance_weight, popularity_weight):
	popularity_index = db.dgetall("popularity_index")
	scored_urls = []

	for url in urls:
		score = 0

		try:
			score = relevance_weight * url[1] + popularity_weight * popularity_index[url[0]]
		except:
			pass

		scored_urls.append([url[0], score])

	sorted_urls = [scored_urls[0]]

	for url in scored_urls:
		for i in range(0, len(sorted_urls)):
			sorted_url = sorted_urls[i]
			if url[1] > sorted_url[1] and url not in sorted_urls:
				sorted_urls.insert(i, url)

		if url not in sorted_urls:
			sorted_urls.append(url)

	return sorted_urls
