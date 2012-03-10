import pygame
from pygame.locals import *
import sys, os
def loadImage(name, alpha=False):
    path = os.path.join('data', 'images', name)
    try:
        image = pygame.image.load(path)
    except:
        print 'Can\'t load image %s!' % name
    if alpha: image = image.alpha_conver()
    else: image = image.convert()
    return image, image.get_rect()