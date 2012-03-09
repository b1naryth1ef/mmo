import time

#--Exceptions--#
class HookException(Exception): pass
class ThreadSafeException(Exception): pass

#--Server Classes--#
class SlotSystem():
	def __init__(self, slots):
		self._s = dict([(i, None) for i in range(1, slots+1)])
		self.slots = slots
		self.lock = ThreadSafe()

	def it(self):
		return [i for i in self._s if self._s[i] == None]

	def getFreeSlot(self):
		a = self.it()
		if len(a) > 0:
			return min(a)
		else:
			return False

	def userCount(self):
		return self.slots - len(self.it())

	def addUser(self, user):
		with self.lock:
			s = self.getFreeSlot()
			self._s[s] = user
			return s

	def rmvUser(self, slot):
		with self.lock:
			self._s[slot] = None
			return True

	def __getitem__(self, attr):
		return self._s[attr]

#--Global Classes--#
class ThreadSafe():
	def __init__(self):
		self.locked = False

	def __enter__(self):
		if self.locked:
			for i in range(0, 3):
				time.sleep(5)
				if not self.locked:
					return getLock()
			raise ThreadSafeException('Could not get thread lock...')
		else:
			self.locked = True

	def __exit__(self, exc_type, exc_value, traceback):
		if self.locked:
			self.locked = False

class User():
	def __init__(self, name, conn):
		self.name = name
		self.alias = name
		self.conn = conn
		self.pos = [1, 1]
		self.methods = USER_METHODS

	def setPos(self, pos):
		self.pos = pos or [1, 1]

	def getPos(self, null):
		return self.pos

	def setName(self, name):
		print name
		self.alias = name or self.name

	def getName(self, null):
		return self.alias

USER_METHODS = {
'setPos':User.setPos, 
'getPos':User.getPos, 
'setName':User.setName, 
'getName':User.getName}