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
