import socket, zlib, thread, json, time, collections
from classes import User

PROTOCOL_VERSION = 3

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
		self.user = User('Jeffery', self)
		self.Q = collections.deque()

		self.serverInfo = {}
		self.last_packets = {'pos':-1}
		self.last_sent = {'pos':[-1, -1]}

		self.state = 'DISCONNECTED'
		self.c = None
		self.id = None
		self.connected = False

	def connect(self):
		if self.connected is False:
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
			thread.start_new_thread(self.readLoop, ())
			self.consumerLoop()

	def action_JOINREQ(self):
		self.write({'tag':'JOIN_REQ', 'name':self.user.name, 'hash':self.hash})

	def disconnect(self):
		self.connected = False

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
				
	def readLoop(self):
		while self.connected:
			self.Q.append(self.read())

	def consumerLoop(self):
		while self.connected:
			while len(self.Q) > 0:
				self.parse(self.Q.popleft())
			if time.time() - self.last_packets['pos'] >= 5 and self.user.pos != self.last_sent['pos']: #send pos packet at least every 5 seconds
				self.action_POS
				self.last_packets['pos'] = time.time()
			time.sleep(.1)

	@Hook('INFO')
	def event_INFO(self, E):
		if self.state == 'JOINING' and type(E) == dict:
			self.serverInfo = E
			del self.serverInfo['tag']
			if self.serverInfo['maxclients'] <= self.serverInfo['clients']:
				print 'Server is full!'
			elif self.serverInfo['version'] != PROTOCOL_VERSION:
				print 'Protocol mismatch (Server is %s, we are %s)' % (self.serverInfo['version'], PROTOCOL_VERSION)
			else:
				return self.action_JOINREQ()
			self.disconnect()

	@Hook('PING')
	def event_PING(self, E): action_PONG()

	def action_PONG(self):
		self.write({'tag':'PONG', 'time':time.time()})

	@Hook('WELCOME')
	def event_WELCOME(self, E):
		if self.state == 'JOINING' and type(E) == dict:
			self.hash = E['hash']
			self.serverInfo['motd'] = E['motd']
			self.id = E['id']
			self.state = 'JOINED'
			self.action_PONG()
			self.action_POS()
			print 'Joined Server!'

	@Hook('KICK')
	def event_KICK(self, E):
		print 'Got kicked! for %s' % E['reason']
		self.disconnect()

	@Hook('ACTION')
	def event_ACTION(self, E):
		if E['action'] in self.user.methods:
			self.user.methods[E['action']](self.user, *E['data'])

	@Hook('ENT_ACTION')
	def event_ENTACTION(self, E): pass

	@Hook('POS')
	def event_POS(self, E):
		if self.E['id'] == self.id:
			self.pos = self.E['pos']
		else: pass #find the user, update

	def action_POS(self):
		self.write({'tag':'POS', 'pos':self.user.pos, 'id':self.id})

if __name__ == '__main__':
	c = Client()
	c.connect()
