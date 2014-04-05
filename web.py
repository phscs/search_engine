import cherrypy
import search
import thread

thread.start_new_thread(search.crawl, ("http://en.wikipedia.org/wiki/George_Washington",))

form = "<form action='query' method='GET'> \
			query: <input type='text' name='search_string' autofocus> \
			relevance: <input type='number' name='rel'> \
			popularity: <input type='number' name = 'pop'> \
			<input type='submit' value='submit'> \
		</form>"

class SE(object):
	def index(self):
		html = "<html><body>" + form + "</body></html>"
		return html

	def query(self, search_string, rel, pop):
		html = "<html><body>" + form

		results = search.query(search_string, rel, pop)

		if results != ["No results found."]:
			html += "<ul>"
			for result in search.query(search_string, int(rel), int(pop)):
				url = result[0]
				score = str(result[1])
				html += "<li>[" + score + "] <a href='" + url + "'>" + url + "</a></li>"

			html += "</ul></body></html>"

		else:
			html += "<p>No results found.</p></body></html>"

		return html

	index.exposed = True
	query.exposed = True

cherrypy.quickstart(SE())