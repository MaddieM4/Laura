from sanitizer import sanitize, output
import random

class Message:
	''' A message in the database. '''
	def __init__(self, text, author="noone@example", parent=0, id=None):
		self.text = sanitize(text)
		self.author = author
		self.parent = parent
		self.id = id

	@property
	def has_id(self):
		return self.id != None

	def markov(self):
		return Markov(self.text)

	def similarity(self, other):
		s = self.markov().similarity(other.markov())*0.8
		if self.author == other.author:
			s += .1
		if self.author == other.author:
			s += .1		

class Markov(dict):
	def __init__(self, text, length):
		words = text.split()
		for i in range(1,length):
			for x in range(len(words)):
				local = words[x:x+i]
				if len(local) == i:
					self.incr(local)
		self.maxkeylen = length

	def incr(self, chain):
		if tuple(chain) in self:
			self[tuple(chain)] += 1
		else:
			self[tuple(chain)] = 1

	def spit(self, chain = []):
		if chain == []:
			chain = ['--start*']
		# get weight of all possibilities
		poss, total = self.poss(chain)
		# pick one at random
		chain += self.randposs(poss, total)
		if chain[-1:] == "--end*":
			return output(" ".join(chain))
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
		total = 0
		match = 0
		for i in mine:
			if i in yours:
				matched = mine[i] + yours[i]
				total += matched
				match += match
				del yours[i]
			else:
				total += mine[i]
		for i in yours:
			total += yours[i]
		return match/total

	def singles(self):
		results = {}
		for i in self:
			if len(i) == 1:
				results[i[0]] = self[i]
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
