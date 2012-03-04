import zlib, collections, json, md5, random
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

PROTOCOL_VERSION = 1
MAX_SLOTS = 10
NAME = 'My Sexy Server!'

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
		self.hash = hash or self.genHash() #Unpythonic in a way...

	def genHash(self): #This is bullshit, ik
		self.hash = random.randint(11111, 99999)
		return self.hash

class RemoteClient(LineReceiver):
	def __init__(self, addr):
		self.addr = addr
		self.state = 'INIT'
		self.id = None

	def send(self, line, header='\x01'):
		if header != '\x00':
			line = zlib.compress(line)
		self.sendLine('%s%s' % (header, line))

	def connectionMade(self):
		if allocateSlot() == False:
			return self.sendLine('\x00SERVER_FULL')

	def connectionLost(self, reason):
		print 'Disconnected: %s' % reason
		if self.id != None: SLOTS[self.id] = None

	def lineReceived(self, line):
		newline = None
		try:
			if line.startswith(('\x01', '\x02')): #@TODO unpack JSON stuff here (copy the client read)
				newline = zlib.decompress(line[1:]).strip()
				if line.startswith('\x02'):
					newline = json.loads(newline)
					if newline['tag'] in CLIENT_EVENTS.keys():
						CLIENT_EVENTS[newline['tag']](self, newline)
			elif line[1:] in CLIENT_EVENTS.keys():
				CLIENT_EVENTS[line[1:]](self, line[1:])
		 except Exception, e:
		 	print 'Was not able to parse line! (%s)' % e
		print '%s: %s' % (self.id, newline or line)

	def event_HELLO(self, packet):
		self.send(json.dumps({'tag':'INFO', 'version':PROTOCOL_VERSION, 'name':NAME, 'maxclients':MAX_SLOTS, 'clients':userCount()}), '\x02')

	def event_JOINREQ(self, packet):
		def _s(): 
			self.send(json.dumps({'tag':'WELCOME', 'hash':USERS[packet['name']].genHash(), 'motd':'Lalalalal!'}), '\x02')
			self.id = slot
		 	SLOTS[slot] = self
		if 'name' in packet.keys() and 'hash' in packet.keys():
			if packet['name'] not in USERS.keys() and packet['hash'] == None:
				print 'New user! Yay!'
				USERS[packet['name']] = User(packet['name'])
				_s()
			elif packet['name'] in USERS.keys() and packet['hash'] != None:
				if USERS[packet['name']].hash == packet['hash']:
					_s()
		self.send('KICK')
		#self.loseConnection() idk how to shutdown a connection with twisted...

class Host(Factory):
	def buildProtocol(self, addr):
		return RemoteClient(addr)

CLIENT_EVENTS = {
	'HELLO':RemoteClient.event_HELLO, #Sent to check the server version and stuff
	'JOIN_REQ':RemoteClient.event_JOINREQ,
	'AUTH':None,
	'PONG':None,
}

reactor.listenTCP(27960, Host())
reactor.run()