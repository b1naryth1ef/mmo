import zlib, collections, json, md5, random, time, thread
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, task
from classes import ThreadSafe, HookException, SlotSystem

PROTOCOL_VERSION = 2
THREADING = True
MAX_SLOTS = 10
NAME = 'My Sexy Server!'
MOTD = 'Welcome to the Test server!'

USERS = {}
SLOTS = SlotSystem(MAX_SLOTS)
HOOKS = {}
Q = {}

def Hook(hook):
	def deco(func):
		if hook not in HOOKS.keys():
			HOOKS[hook] = func
			return func
		raise HookException('Hook %s already exsists' % hook)
	return deco

class User():
	def __init__(self, name, conn, hash=None):
		self.name = name
		self.conn = conn
		self.pos = [0, 0]
		

class RemoteClient(LineReceiver):
	def __init__(self, addr):
		self.addr = addr
		self.state = 'INIT'
		self.waitingForPong = False
		self.id = None
		self.listen = True

	def send(self, line):
		#print line
		self.sendLine('\x02%s' % zlib.compress(json.dumps(line)))

	def connectionMade(self): pass

	def connectionLost(self, reason):
		print 'Disconnected: %s' % reason
		if self.id != None: SLOTS[self.id] = None

	def lineReceived(self, line):
		if not self.listen: return		
		try:
			if line.startswith('\x02'):
				line = json.loads(zlib.decompress(line[1:]))
				if line['tag'] in HOOKS.keys():
					HOOKS[line['tag']](self, line)
		except Exception, e:
		 	print 'Was not able to parse line! (%s)' % e
		print '%s: %s' % (self.id, line)

	@Hook('POS')
	def event_POS(self, packet): pass
		#@TODO Validate the pos first
		#USERS[self.id].pos = packet['pos']

	@Hook('ACTION')
	def event_ACTION(self, packet): pass

	@Hook('ENT_ACTION')
	def event_ENTACTION(self, packet): pass

	@Hook('HELLO')
	def event_HELLO(self, packet):
		self.send({'tag':'INFO', 'version':PROTOCOL_VERSION, 'name':NAME, 'maxclients':MAX_SLOTS, 'clients':SLOTS.userCount()})

	@Hook('JOIN_REQ')
	def event_JOINREQ(self, packet):
		def _s(): 
			SLOTS.addUser(User(packet['name'], self))
			self.send({'tag':'WELCOME', 'hash':00000, 'motd':MOTD})
			self.state = 'CONN'
			self.task = task.LoopingCall(self.action_PING)
			self.task.start(300) #Ping request every 5 mins
		if 'name' in packet.keys() and 'hash' in packet.keys():
			if packet['name'] not in USERS.keys() and packet['hash'] == None:
				print 'New user! Yay!'
				return _s()
			elif packet['name'] in USERS.keys() and packet['hash'] != None:
				#if USERS[packet['name']].hash == packet['hash']:
				return _s()
		self.action_KICK('Bad JOIN_REQ')

	@Hook('PONG')
	def event_PONG(self, packet):
		print 'Got pong!'
		self.waitingForPong = False

	def action_PING(self):
		self.send({'tag':'PING'})
		self.waitingForPong = True
		reactor.callLater(5, self.hasPonged)

	def action_KICK(self, reason):
		self.send({'tag':'KICK', 'reason':reason})
		self.listen = False
		self.transport.loseConnection()

	def hasPonged(self):
		if self.waitingForPong is True:
			self.action_KICK('No Ping Response!')

class Host(Factory):
	def buildProtocol(self, addr):
		return RemoteClient(addr)

if __name__ == '__main__':
	reactor.listenTCP(27960, Host())
	reactor.run()