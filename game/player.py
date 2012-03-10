from sprites import PlayerSprite
import time

class Player(object):
    def __init__(self, name, game):
        self.name = name
        self.pos = [50, 50]
        self.do_blit = False
        self.game = game
        self.surf = game.SCREEN

        self.lastMove = 99999999999

        self.velo_def = [0, 0]
        self.velo_x = 0
        self.velo_y = 0

        self.sprite = PlayerSprite(self)

        self.moving = [False, False, False, False]

    def tick(self):
        if self.do_blit:
            self.game.reDraw = True
            self.sprite.display(self.surf.screen)
            #self.surface.screen.blit(self.image, self.pos)
            self.do_blit = False
       # print self.lastMove - time.time()
        if True in self.moving and abs(self.lastMove - time.time()) >= .08:
            self.lastMove = time.time()
            if self.moving[0]: self.move(x=-1)
            if self.moving[1]: self.move(x=1)#down
            if self.moving[2]: self.move(y=-1)#left
            if self.moving[3]: self.move(y=1)#right

    def move(self, x=0, y=0):
        self.pos[1]+=x*10
        self.pos[0]+=y*10
        self.do_blit = True
        if y < 0 and self.sprite.dir == 1:
            self.sprite.flip()
        elif y > 0 and self.sprite.dir == -1:
            self.sprite.flip()