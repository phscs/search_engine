import urllib
import string

index = {}
popularity_index = {}

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
			link_temp += character

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
				collected_characters += " "
			else:
				collected_characters += character.lower()

	keywords = collected_characters.split(" ")

	while "" in keywords:
		keywords.remove("")

	for word in keywords:
		if word in keywords[keywords.index(word)+1:]:
			keywords.remove(word)

	return keywords

def add_to_index(url, keywords):
    for keyword in keywords:
		if keyword not in index:
			index[keyword] = [[url, 0]]

		else:
			url_already_in_entry = False

			for entry in index[keyword]:
				if url == entry[0]:
					url_already_in_entry = True

			if not url_already_in_entry:
				index[keyword].append([rank, 0])
		
def crawl(seed_page_url):
        urls_to_crawl = [seed_page_url]
        urls_already_crawled = []
        crawls = 0

        while len(urls_to_crawl) > 0 and crawls < 50:
            url = urls_to_crawl[0]
            source = urllib.urlopen(url).read()

            keywords = get_keywords(source)
            add_to_index(url, keywords)

            links = get_links(source)

            for link in links:
                uprank_popularity(link)
                if link != url and link not in urls_already_crawled:
                    urls_to_crawl.append(link)

            urls_to_crawl.remove(url)
            urls_already_crawled.append(url)

            crawls += 1

def uprank_popularity(url):
    if url in popularity_index:
        popularity_index[url] += 1
    else:
        popularity_index[url] = 1

def uprank_relevance(keyword, url):
    if keyword in index:
        for entry in index[keyword]:
            if url == entry[0]:
                entry[1] += 1

def query(search_string):
	sanitized_search_string = ""

	for character in search_string:
		if character not in string.punctuation:
			sanitized_search_string += character.lower()

	keywords = sanitized_search_string.split(" ")

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

		sorted_urls = sort(urls)

		return sorted_urls
	
	else:
		return ["No results found."]

def sort(urls):
	relevance_weight = 1
	popularity_weight = 1

	scored_urls = []

	for url in urls:
		score = 0

		try:
			score = url[1] + popularity_index{url[0]}
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
