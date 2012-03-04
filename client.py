import socket, zlib, thread, json, collections, time

PROTOCOL_VERSION = 1

HOST = 'localhost'
PORT = 1338
PREFIX = {'start':'', 'end':'\r\n'}

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((HOST, PORT))
# s.send('\x01'+zlib.compress('Very very very long message about lots of things that are very very important *&#(${}:ASD<>XCBM#?'))

class Client():
	def __init__(self, data=('localhost', 27960)):
		self.host, self.port = data
		self.c = None
		self.queue = collections.deque()
		self.serverInfo = {}

		self.name = 'Jeffery'
		self.hash = None
		self.alive = False
		self.cid = -1

		self.SERVER_EVENTS = {
		'PING':self.event_PING,
		'SERVER_FULL':self.event_FULL,
		'WELCOME':self.event_WELCOME,
		'KICK':self.event_KICK,
		}

	def connect(self):
		if self.alive is False:
			try:
				self.c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.c.connect((self.host, self.port))
				self.write('\x00HELLO')
			except:
				return (False, 'Error with connecting... (Internet problems?)')
			try:
				self.c.settimeout(10) #Wait ten seconds
				hello = self.read()
			except Exception, e:
				return (False, 'Server did not respond to HELLO request... %s' % e)
			finally:
				self.c.settimeout(None)
			try:
				if type(hello) == dict:
					if hello['tag'] == 'INFO':
						self.serverInfo = hello
						del self.serverInfo['tag']
						if self.serverInfo['maxclients'] <= self.serverInfo['clients']:
							return (False, 'Server is full!')
						elif self.serverInfo['version'] != PROTOCOL_VERSION:
							return (False, 'Server version mismatch!')
						else:
							self.send_joinReq()
							r = self.read()
							print type(r)
							if type(r) == dict:
								if r['tag'] == 'WELCOME':
									self.hash = r['hash']
									self.serverInfo['motd'] = r['motd']
									return (True, 'Joined Server!')
			except Exception, e: 
				print e
			return (False, 'Error doing shit with the server!')

	def send_joinReq(self):
		self.write('\x02'+zlib.compress(json.dumps({'tag':'JOIN_REQ', 'name':self.name, 'hash':self.hash})))

	def disconnect(self): pass
	def write(self, line):
		self.c.send('%s%s%s' % (PREFIX['start'], line, PREFIX['end']))
	def read(self, a=1024):
		line = self.c.recv(a)
		if line:
			if line.startswith('\x00'):
				return line[1:].strip()
			elif line.startswith(('\x01', '\x02')):
				newline = zlib.decompress(line[1:])
				if line.startswith('\x02'):
					return dict(json.loads(newline))
				return newline
				
	def parse(self, line): pass
	def event_FULL(self, E): pass
	def event_LOGIN(self, E): pass
	def event_PING(self, E): pass
	def event_WELCOME(self, E): pass
	def event_KICK(self, E):
		print 'Got kicked!'
		self.disconnect()
