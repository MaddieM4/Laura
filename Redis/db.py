import redis
import models
import logging

class DB:
	def __init__(self):
		self.redis = redis.Redis()
		self.redis.setnx("lrc/m/amount",0)

	def get_m_address(self, id):
		return "lrc/m/"+str(id)

	def save_message(self, message):
		if message.id==None:
			message.id = self.new_message_space()
		logging.info("Saving Message "+str(message.id))
		address = self.get_m_address(message.id)
		self.set(address, "author", message.author)
		self.set(address, "parent", message.parent)
		self.set(address, "text", message.text)
		return message.id

	def load_message(self, id):
		if not id:
			raise IndexError("Cannot attempt to read Message 0")
		logging.info("Loading Message "+str(id))
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

	def setsim(self, id1, id2, value):
		if id2>id1:
			return self.setsim(id2, id1)
		elif id2==id1:
			return True
		else:
			return self.redis.set("lrc/s/%d/%d"%(id1,id2), value)

	def get_parent(self, message):
		return self.load_message(message.parent)

	def new_message_space(self):
		r = self.redis.incr("lrc/m/amount")
		logging.info("New space allocated: "+str(r))
		return r

	def new_message(self, m):
		n = self.save_message(m)
		return Message(self,n)

	def set(self, address, property, value):
		return self.redis.set("%s:%s"%(address,property), value)

	def get(self, address, property):
		return self.redis.get("%s:%s"%(address,property))

	def flush(self):
		self.redis.flushall()

	@property
	def message_count(self):
		return int(self.redis.get("lrc/m/amount"))

	def __len__(self):
		return self.message_count

class Message:
	def __init__(self, db, id):
		self._message = db.load_message(id)
		self.db = db

	def run_sim(self):
		# store similarities for all IDs lower than this one
		for i in range(1,self.id):
			self.save_sim(i)

	def save_sim(self, id):
		other = self.db.load_message(id)
		self.db.setsim(self.id, id, self._message.similarity(other))

	def save(self):
		db.save_message(self._message)

	def load(self):
		self._message = self.db.load_message(self.id)

	def make_response(self):
		# For all other messages
		mark = models.Markov("")
		for i in range(1,len(self.db)):
			# grab parent
			logging.info("Loading mi where i="+str(i))
			mi = self.db.load_message(i)
			other = mi.parent
			own = self.id
			# initialization of values
			total = 0.0
			match = 0.0
			roleA = models.Role()
			roleB = models.Role()
			while other!=0 and own!=0:
				logging.info(other)
				_oth = self.db.load_message(other)
				_own = self.db.load_message(own)
				# check similarity
				sim = self.db.sim(other, own)*.8
				# weight by author and role
				if _oth.author == _own.author:
					sim += .1
				if roleA.insert(_oth.author)==roleB.insert(_own.author):
					sim += .1
				total += 1
				match += sim
				# set ids to parents
				other = _oth.parent
				own = _own.parent
			if not total:
				continue
			sim = match/total
			mark += mi.markov()*sim
		return mark.spit()

	@property
	def id(self):
		return self._message.id

	@property
	def parent(self):
		return Message(self.db, self._message.parent)
