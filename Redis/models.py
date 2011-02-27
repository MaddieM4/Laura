import sanitizer
import random
import logging

class Message:
	''' A message in the database. '''
	def __init__(self, text, author="noone@example", parent=0, id=None):
		self.text = sanitizer.filter(text)
		self.author = author
		self.parent = int(parent)
		self.id = id
		self.cachedMarkov = None

	@property
	def has_id(self):
		return self.id != None

	def markov(self):
		if self.cachedMarkov == None:
			self.cachedMarkov = Markov(self.text)
		return self.cachedMarkov

	def similarity(self, other):
		s = self.markov().similarity(other.markov())
		logging.info("Models.Message similarity = "+str(s))
		return s

class Markov(dict):
	def __init__(self, text, length=8):
		words = text.split()
		logging.info(text)
		for i in range(1,length):
			for x in range(len(words)):
				local = words[x:x+i]
				if len(local) == i:
					self.incr(local)
		self.maxkeylen = length

	def incr(self, chain, amount=1):
		tup = tuple(chain)
		if tup in self:
			self[tup] += amount
		else:
			self[tup] = amount
		#logging.info("self["+str(tup)+"] = " +str(self[tup]))

	def spit(self, chain = []):
		if chain == []:
			chain = ['--start*']
		# get weight of all possibilities
		poss, total = self.poss(chain)
		if total == 0:
			return "Not enough parental data to construct sentences."
		# pick one at random
		chain.append(self.randposs(poss, total))
		if chain[-1:] == "--end*":
			return sanitizer.output(" ".join(chain))
		else:
			return self.spit(chain)

	def randposs(self, poss, total):
		meter = random.random() * total
		for i in poss:
			meter -= poss[i]
			if meter <= 0:
				return i

	def similarity(self, other):
		mine = self.singles()
		yours = other.singles()
		total = 0.0
		match = 0.0
		for i in mine:
			if i in yours:
				#logging.info(i)
				matched = mine[i] + yours[i]
				total += matched
				match += matched
				del yours[i]
			else:
				total += mine[i]
		for i in yours:
			total += yours[i]
		logging.info("%s/%s" %(str(match),str(total)))
		return match/total

	def singles(self):
		results = {}
		for i in self:
			if len(i) == 1:
				results[i[0]] = self[i]
		#logging.info(results)
		return results

	def poss(self, chain):
		all = {}
		total = 0
		for i in self:
			if len(i) == 1:
				continue
			if chain[-(len(i)-1):] == i[:-1]:
				# A match
				target = i[-1:]
				total += 1
				if target in all:
					all[target] += 1
				else:
					all[target] = 1
		return all, total

	def __iadd__(self, other):
		for i in other:
			self.incr(i, other[i])

	def __mul__(self, amount):
		result = {}
		for i in self:
			result[i] = self[i]*amount
		return result

class Role:
	def __init__(self):
		self.authors = []
		self.roles = []

	def insert(self, author):
		if author in self.authors:
			role = self.authors.index(author)
		else:
			self.authors.append(author)
			role = len(self.authors)-1
		self.roles.append(role)
		return role
