import pygame
from pygame.locals import *
from library import PygameScreen, Fadeable
from player import Player
import os, sys, time

key_map = {
	K_w:(-1, 0),
	K_a:(0, -1),
	K_s:(1, 0),
	K_d:(0, 1)
}

# class Char():
# 	def __init__(self, name, game, img, ):
# 		self.pos = [0, 0]
# 		self.name = name
# 		self.surface = game.SCREEN
# 		self.image = img
# 		self.game = game
# 		self.do_blit = False

# 	def tick(self):
# 		if self.do_blit:
# 			self.game.reDraw = True
# 			self.surface.screen.blit(self.image, self.pos)
# 			self.do_blit = False

# 	def move(self, x=0, y=0):
# 		self.pos[1]+=x*10
# 		self.pos[0]+=y*10
# 		print self.pos
# 		self.do_blit = True

class Game():
	def __init__(self, windowsize=(50, 50), fullscreen=False):
		self.winsize = windowsize
		self.fullscreen = fullscreen
		self._tickables = {}

		self.reDraw = False
		self.doLoop = True
		self.doTick = True
		self.doRender = False
		self.FPS = 15 #Doesnt need to be high, we're text based ffs!
		self.CLOCK = pygame.time.Clock()
		#self.SCREEN = self._win = pygcurse.PygcurseWindow(*self.winsize, fullscreen=self.fullscreen)
		self.SCREEN = PygameScreen('Main', title='PyMMO').load()
		#self.CLIENT = client.Client()

		#img = pygame.image.load(os.path.join('data', 'images', 'test_char.jpeg'))
		#img.convert_alpha()
		self.char = Player('Joey', self)
		self.char.do_blit = True
		self._tickables[self.char.name] = self.char

	def tick(self):
		self.CLOCK.tick(self.FPS)

	def render(self):
		pygame.display.flip() 
		self.reDraw = False

	def loop(self):
		while True:
			self.SCREEN.screen.fill((0,0,0))
			for ticky in self._tickables.values():
				ticky.tick()
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					if event.key in key_map:
						if event.key == K_w: 
							self.char.move(x=-1)
							self.char.moving[0] = True
						elif event.key == K_s:
							self.char.move(x=1)
							self.char.moving[1] = True
						elif event.key == K_a: 
							self.char.move(y=-1)
							self.char.moving[2] = True
						elif event.key == K_d: 
							self.char.move(y=1)
							self.char.moving[3] = True
				elif event.type == pygame.KEYUP:
					if event.key == K_w: 
						self.char.moving[0] = False
					elif event.key == K_s:
						self.char.moving[1] = False
					elif event.key == K_a: 
						self.char.moving[2] = False
					elif event.key == K_d: 
						self.char.moving[3] = False

				elif event.type == pygame.QUIT:
					sys.exit()
			if self.reDraw:
				self.render()
			self.tick()

g = Game()
g.render()
g.loop()