import redis
from sanitizer import sanitize

class Message:
	def __init__(self, text, author="noone@example", parent=0):
		self.text = sanitize(text)
		self.author = author
		self.parent = parent

	def markov(self):
		result = {}
		for i in self.text.split():
			
