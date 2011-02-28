import models
import db

class Laura:
	def __init__(self):
		self.db = db.DB()

	def push(self, text, author=None, parent=None):
		# Push a message, return the ID
		extra = {}
		if author:
			extra['author'] = author
		if parent:
			extra['parent'] = parent
		m = models.Message(text, **extra)
		supermessage = self.db.new_message(m)
		supermessage.run_sim()
		return supermessage.id

	def pull(self, target):
		# Pull a response
		M = self.db.Message(self.db, target)
		return M.make_response()

	def read(self, target):
		m = self.db.load_message(target)
		s =  "{"
		s += "\n\t'Author':'%s'" % str(m.author)
		s += "\n\t'Parent':'%s'" % m.parent
		s += "\n\t'Message':'%s'" % m.text
		s += "\n}"
		return s

	def flush(self):
		# Flush the DB
		self.db.flush()

	def count(self):
		return len(self.db)
