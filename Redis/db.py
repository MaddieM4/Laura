import redis
import models

class DB:
	def __init__(self):
		self.redis = redis.Redis()
		self.redis.setnx("lrc/m/amount",0)

	def get_m_address(self, id):
		return "lrc/m/"+str(id)

	def save_message(self, message):
		if message.id==None:
			message.id = self.new_message_space()
		address = self.get_m_address(message.id)
		print self.set(address, "author", message.author)
		print self.set(address, "parent", message.parent)
		print self.set(address, "text", message.text)
		return message.id

	def load_message(self, id):
		address = self.get_m_address(id)
		author = self.get(address, "author")
		parent = self.get(address, "parent")
		text = self.get(address, "text")
		return models.Message(text, author, parent, id)

	def sim(self, id1, id2):
		''' Get a similarity out of storage '''
		if id2>id1:
			return self.sim(id2, id1)
		elif id2==id1:
			return 1.0
		else:
			return self.redis.get("lrc/s/%d/%d" % (id1, id2))

	def get_parent(self, message):
		return self.load_message(message.parent)

	def new_message_space(self):
		return self.redis.incr("lrc/m/amount")

	def set(self, address, property, value):
		return self.redis.set("%s:%s"%(address,property), value)

	def get(self, address, property):
		return self.redis.get("%s:%s"%(address,property))

	def flush(self):
		self.redis.flushall()

	@property
	def message_count(self):
		return self.redis.get("lrc/m/amount")
