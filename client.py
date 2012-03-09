import socket, zlib, thread, json, time

PROTOCOL_VERSION = 2

HOST = 'localhost'
PORT = 1338
PREFIX = {'start':'\x02', 'end':'\r\n'}
HOOKS = {}

def Hook(hook):
	def deco(func):
		if hook not in HOOKS.keys():
			HOOKS[hook] = func
			return func
		raise HookException('Hook %s already exsists' % hook)
	return deco

class Client():
	def __init__(self, data=('localhost', 27960)):
		self.host, self.port = data
		self.c = None
		self.connected = False
		#self.queue = collections.deque()
		self.serverInfo = {}
		self.state = 'DISCONNECTED'

		self.name = 'Jeffery'
		self.hash = None
		self.alive = False
		self.cid = -1

		self.SERVER_EVENTS = {
		'PING':self.event_PING,
		'WELCOME':self.event_WELCOME,
		'KICK':self.event_KICK,
		}

	def connect(self):
		if self.alive is False:
			try:
				self.c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.c.connect((self.host, self.port))
				self.write({'tag': 'HELLO'})
				self.state = 'JOINING'
				self.connected = True
				self.c.settimeout(10)
				self.parse(self.read())
			except:
				return (False, 'Error with connecting... (Internet problems?)')
			finally:
				self.c.settimeout(None)
			self.loop()

	def action_JOINREQ(self):
		self.write({'tag':'JOIN_REQ', 'name':self.name, 'hash':self.hash})

	def disconnect(self): pass

	def write(self, line):
		self.c.send('%s%s%s' % (PREFIX['start'], zlib.compress(json.dumps(line)), PREFIX['end']))

	def parse(self, line):
		if line:
			if line['tag'] in HOOKS.keys():
					HOOKS[line['tag']](self, line)

	def read(self, a=2048):
		line = self.c.recv(a)
		if line:
			for line in line.split('\r\n'):
				if line.startswith('\x02'):
					return json.loads(zlib.decompress(line[1:]))
				
	def loop(self):
		while self.connected:
			self.parse(self.read())

	@Hook('INFO')
	def event_INFO(self, E):
		if self.state == 'JOINING' and type(E) == dict:
			self.serverInfo = E
			del self.serverInfo['tag']
			if self.serverInfo['maxclients'] <= self.serverInfo['clients']:
				return (False, 'Server is full!')
			elif self.serverInfo['version'] != PROTOCOL_VERSION:
				return (False, 'Server version mismatch!')
			else:
				self.action_JOINREQ()

	@Hook('PING')
	def event_PING(self, E):
		print 'Writing ping'
		self.write({'tag':'PONG', 'time':time.time()})

	@Hook('WELCOME')
	def event_WELCOME(self, E):
		if self.state == 'JOINING' and type(E) == dict:
			self.hash = E['hash']
			self.serverInfo['motd'] = E['motd']
			self.state = 'JOINED'
			self.event_PING(None)
			print 'Joined Server!'

	@Hook('KICK')
	def event_KICK(self, E):
		print 'Got kicked! for %s' % E['reason']
		self.connected = False
		self.disconnect()
