import urllib

index = urllib.urlopen("index.html").read()

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

print get_links(index)
