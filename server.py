import zlib, collections, json, md5, random, time
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

PROTOCOL_VERSION = 2
MAX_SLOTS = 10
NAME = 'My Sexy Server!'
MOTD = 'Welcome to the Test server!'

USERS = {}
SLOTS = {}

def allocateSlot(): #Fairly proud of this little code here :)
	if SLOTS == {}: return 1
	ma = max(SLOTS.keys())
	mi = min(SLOTS.keys())
	for i in range(mi, ma):
		if i not in SLOTS.keys():
			return i
	return False

def userCount(): #Also damn proud of this :D
	return len([x for x in SLOTS.values() if x != None])

class User():
	def __init__(self, name, hash=None):
		self.name = name
		self.pos = [0, 0]
		self.hash = hash or self.genHash() #Unpythonic in a way...

	def genHash(self): #This is bullshit, ik
		self.hash = random.randint(11111, 99999)
		return self.hash

class RemoteClient(LineReceiver):
	def __init__(self, addr):
		self.addr = addr
		self.state = 'INIT'
		self.id = None
		self.lastGot = -1
		self.listen = True

	def kick(self, reason):
		self.send({'tag':'KICK', 'reason':reason})
		self.listen = False
		self.transport.loseConnection()

	def send(self, line):
		self.sendLine('\x02%s' % zlib.compress(json.dumps(line)))

	def connectionMade(self):
		if allocateSlot() == False:
			return self.send({'tag':'SERVER_FULL'})

	def connectionLost(self, reason):
		print 'Disconnected: %s' % reason
		if self.id != None: SLOTS[self.id] = None

	def lineReceived(self, line):
		if not self.listen: return
		if self.state == 'INIT': #Wrap these for speed
			if time.time()-self.lastGot <= 2: #.0009: #lame dos protection
				print 'Spamming?'
				self.kick('Detected spamming! (DOS?)')
			self.lastGot = time.time()
		try:
			if line.startswith('\x02'):
				line = json.loads(zlib.decompress(line[1:]))
			if line['tag'] in CLIENT_EVENTS.keys():
				CLIENT_EVENTS[line['tag']](self, line)
		except Exception, e:
		 	print 'Was not able to parse line! (%s)' % e
		print '%s: %s' % (self.id, line)

	def event_POS(self, packet): pass
		#@TODO Validate the pos first
		#USERS[self.id].pos = packet['pos']

	def event_ACTION(self, packet): pass
	def event_ENTACTION(self, packet): pass

	def event_HELLO(self, packet):
		self.send({'tag':'INFO', 'version':PROTOCOL_VERSION, 'name':NAME, 'maxclients':MAX_SLOTS, 'clients':userCount()})

	def event_JOINREQ(self, packet):
		def _s(): 
			self.send({'tag':'WELCOME', 'hash':USERS[packet['name']].genHash(), 'motd':MOTD})
			self.state = 'CONN'
			self.id = allocateSlot()
		 	SLOTS[self.id] = self
		if 'name' in packet.keys() and 'hash' in packet.keys():
			if packet['name'] not in USERS.keys() and packet['hash'] == None:
				print 'New user! Yay!'
				USERS[packet['name']] = User(packet['name'])
				_s()
			elif packet['name'] in USERS.keys() and packet['hash'] != None:
				if USERS[packet['name']].hash == packet['hash']:
					_s()
		self.kick('Bad JOIN_REQ')

class Host(Factory):
	def buildProtocol(self, addr):
		return RemoteClient(addr)

CLIENT_EVENTS = {
	'HELLO':RemoteClient.event_HELLO, #Sent to check the server version and stuff
	'JOIN_REQ':RemoteClient.event_JOINREQ,
	'PONG':None,
	'ACTION':RemoteClient.event_ACTION,
	'ENT_ACTION':RemoteClient.event_ENTACTION,
	'POS':RemoteClient.event_POS
}

reactor.listenTCP(27960, Host())
reactor.run()