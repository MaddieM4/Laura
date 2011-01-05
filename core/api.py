from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import dbtools
import models
import logging
import md5

class Insert(webapp.RequestHandler):
	def post(self):
		# Post variables
		parent = self.request.get('parent')
		text   = self.request.get('text')
		author = self.request.get('author')
		resurl = self.request.get('responseurl')
		if resurl:
			logging.info('Starting response fingerprint')
			f = dbtools.start_fingerprint(text, author, parent)
			r = dbtools.start_response_fingerprint(f, resurl)
		else:
			logging.info('Starting regular fingerprint')
			f = dbtools.start_fingerprint(text, author, parent)
			r = None
		logging.debug(f)
		logging.debug(r)
		self.response.out.write("{'inserted':'%s'" % str(f.key()))
		if r:
			self.response.out.write(",'response':'%s'" % str(r.key()))
		self.response.out.write('}')

class Cancel(webapp.RequestHandler):
	def post(self):
		key = self.response.get('key')
		dbtools.cancel(models.fromkey(key))
		db.write('success')

class RenderForm(webapp.RequestHandler):
	def get(self):
		messages = ""
		for i in models.Fingerprint.all().filter('parentprint =',None):
			messages += self.ftable(i)
		self.response.out.write(''' 
			<html>
			<head>
				<title>Manually Insert</title>
				<style>
					li.building {color:green}
				</style>
			</head>
			<body>
				<form method="post" action="/api/insert">
					Parent: <input name="parent"/><br/>
					Author: <input name="author"/><br/>
					Text Content: <textarea name="text"></textarea><br/>
					Response URL: <input name="responseurl"/><br/>
					<input type="submit"/><br/>
				</form>
				<ul>%s</ul>
			</body>
			</html>'''
			% messages
		)

	def ftable(self, fingerprint):
		children = fingerprint.fingerprint_set
		r = "<li class='%s'><ul><li>%s</li><li>%s</li><li>%s</li><ul>" % (
				fingerprint.state,
				str(fingerprint.key()),
				fingerprint.author,
				fingerprint.fulltext)
		for i in children:
			r += self.ftable(i)
		r += "</ul></ul></li>"
		return r

class Display(webapp.RequestHandler):
	def get(self):
		self.response.out.write(''' 
			<html>
			<head>
				<title>Datastore</title>
				<style>
					table, table * {border:1px solid rgb(50,50,50)}
				</style>
			</head>
			<body>''')
		self.tabulate(models.Fingerprint, "Fingerprints")
		self.tabulate(models.WordChain, "WordChains")
		self.tabulate(models.WordResult, "WordResults")
		self.tabulate(models.Similarity, "Similarities")
		self.response.out.write("</body></html>")

	def tabulate(self, type, ttext):
		props = type.properties()
		self.response.out.write("<br/>"+ttext+":<br/><table><tr><th>Key</th>")
		for p in props:
			self.response.out.write("<th>"+str(p)+"</th>")
		for x in type.all():
			self.response.out.write("</tr><tr>")
			self.response.out.write("<td>"+self.split(str(x.key()))+"</td>")
			for p in props:
				self.response.out.write("<td>"+str(getattr(x,p))+"</td>")
		self.response.out.write("</tr></table>")

	def split(self, text):
		result = ""
		for i in range(len(text)):
			result += text[i]
			if (i+2) % 10 == 1:
				result += "\n"
		return result

class Purge(webapp.RequestHandler):
	def get(self):
		models.purge()
		self.response.out.write("Purge completed")

def main():
    run_wsgi_app(webapp.WSGIApplication([
        ('/api/insert', Insert),
        ('/api/cancel', Cancel),
	('/api/form', RenderForm),
	('/api/display', Display),
	('/api/purge', Purge)
    ]))

if __name__ == '__main__':
    main()
