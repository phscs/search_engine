import urllib
import string

index = {}

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
