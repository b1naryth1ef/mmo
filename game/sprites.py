import pygame
from pygame.locals import *
from utils import loadImage

class ZombieSprite(): pass

class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, player):
        pygame.sprite.Sprite.__init__(self)
        self.dir = 1 #-1 left, 1 right
        self.image, self.rect = loadImage('mega.png')
        self.player = player
        self.bounds = (10, 8, 52, 56)
        self.char = self.image.subsurface(self.bounds)
        self.char_rect = self.char.get_rect()

    def flip(self):
        self.dir = self.dir*-1
        self.char = pygame.transform.flip(self.char, True, False)

    def display(self, screen):
        screen.blit(self.char, self.player.pos)