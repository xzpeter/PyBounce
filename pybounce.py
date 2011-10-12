"""
This is a bouncing ball application, by xzpeter
"""

import pygame, sys, math, random, time
from pygame.locals import *
 
# Define some colors
black    = (   0,   0,   0)
white    = ( 255, 255, 255)
green    = (   0, 255,   0)
blue     = (   0,   0, 255)
red      = ( 255,   0,   0)
yellow   = ( 255, 255,   0)
 
pygame.init()
  
# Set the height and width of the screen
width = 640
height = 480
size=[width, height]
screen=pygame.display.set_mode(size)
 
pygame.display.set_caption("PyBouncing")
 
# Used to manage how fast the screen updates
clock=pygame.time.Clock()

from pygamewrapper import *
fontfile = 'font/TEMPSITC.TTF'
font = FlashGreyFont(fontfile, 32)
score_font = pygame.font.Font(fontfile, 24)
info_font = pygame.font.Font(fontfile, 16)

wall_list = pygame.sprite.Group()
all_list = pygame.sprite.Group()
block_list = pygame.sprite.Group()

def log(msg):
    print msg
    file = open('bounce-log.txt', 'a')
    file.write('%s: %s\n'%(time.asctime(), msg))
    file.close()

def warn(msg):
    str = "WARNING: %s"%(msg)
    log(str)

class Wall(pygame.sprite.Sprite):
    """ a wall, start is the start point, size is width and height"""
    def __init__(self, start, size):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface(size).convert()
        rect = [0, 0]
        rect.extend(size)
        pygame.draw.rect(self.image, blue, rect)
        self.rect = self.image.get_rect()
        self.setPos(start)

    def setPos(self, pos):
        self.rect.x = pos[0]
        self.rect.y = pos[1]

class Player(pygame.sprite.Sprite):
    size = [10, 100]
    speed = 5
    com_thres = 3
    def __init__(self, start, keys, auto=0):
        """
        start is the start point of player, keys are (up,down) key pairs, auto to 1 if using COM
        index is the player index
        """
        pygame.sprite.Sprite.__init__(self)
        self.up, self.down = keys
        self.image = pygame.Surface(Player.size).convert()
        pygame.draw.rect(self.image, white, (0, 0, Player.size[0], Player.size[1]))
        self.rect = self.image.get_rect()
        self.setPos(start)
        self.setAuto(auto)
        self.chase_ball = 0

    def setAuto(self, val):
        if val:
            self.auto = 1
            # if using computer player, the block is yellow in color
            pygame.draw.rect(self.image, yellow, (0, 0, Player.size[0], Player.size[1]))
        else:
            self.auto = 0
            pygame.draw.rect(self.image, white, (0, 0, Player.size[0], Player.size[1]))
        
    def setPos(self, pos):
        self.rect.x = pos[0]-Player.size[0]/2
        self.rect.y = pos[1]-Player.size[1]/2

    def notifyCOM(self, rect):
        # TODO: here, Game() should notify COM about the ball
        if not self.auto:
            raise Exception, "Should not call notifyCOM() if not auto mode"
        self.ball_rect = rect
        self.chase_ball = 1

    def update(self):
        keys = pygame.key.get_pressed()
        oldy = self.rect.y
        if self.auto:
            if self.chase_ball:
                ball_y = self.ball_rect.y + self.ball_rect.height/2
                self_y = self.rect.y + self.rect.height/2
                if self_y > ball_y+Player.com_thres:
                    self.rect.y -= Player.speed
                elif self_y < ball_y-Player.com_thres:
                    self.rect.y += Player.speed
                self.chase_ball = 0
        else:
            if keys[self.up]:
                self.rect.y -= Player.speed
            elif keys[self.down]:
                self.rect.y += Player.speed

        # check collision
        if pygame.sprite.spritecollideany(self, wall_list):
            self.rect.y = oldy

class Ball(pygame.sprite.Sprite):
    r = 10
    speed = 10
    acc = 1.0005
    # this is the max angle when ball hits player
    bounce_angle_max = math.pi*3/8

    def __init__(self, start):
        pygame.sprite.Sprite.__init__(self)
        r = Ball.r
        self.image = pygame.Surface([r*2, r*2]).convert()
        self.image.fill(black)
        self.image.set_colorkey(black)
        pygame.draw.circle(self.image, white, [r, r], r)
        self.rect = self.image.get_rect()
        self.setPos(start)
        self.acc = Ball.acc

        # ball speed init
        self.angle = (random.random()-0.5)*2*math.pi/4
        if random.randrange(2):
            self.angle = math.pi - self.angle
        self.speed = Ball.speed
        # either direction

    def setPos(self, pos):
        self.rect.x = pos[0]-Ball.r
        self.rect.y = pos[1]-Ball.r

    def goRight(self):
        # python % can work with floats! wow
        if self.vx > 0:
            return True
        else:
            return False

    def hitByPlayer(self, thing):
        """check the thing!"""
        if not isinstance(thing, Player):
            return False
        return True

    def fixAngleByPlayer(self, thing):
        """fix angle if hitting a player, else return false"""
        # check the ball direction, if going right, flip angle at last
        if self.goRight():
            flip = 1
        else:
            flip = 0
        ball_y = self.rect.y+self.rect.height/2
        player_y = thing.rect.y+thing.rect.height/2
        ratio = 1.0*(ball_y-player_y)/(self.rect.height+thing.rect.height)*2
        # ratio check: should not be needed, just be safe
        if ratio > 1 or ratio < -1:
            warn("ratio not right! (%f)" % ratio)
            if ratio > 1:
                ratio = 1
            else:
                ratio = -1
        angle = Ball.bounce_angle_max * ratio
        self.angle = flip and math.pi-angle or angle

    def update(self):
        # calc speed in both axes
        self.speed *= self.acc
        self.vx = self.speed*math.cos(self.angle)
        self.vy = self.speed*math.sin(self.angle)

        oldx = self.rect.x
        oldy = self.rect.y
        
        # update x

        try:
            self.rect.x = oldx + self.vx
        except:
            warn("oldx: %d, selv.vx: %d, plus=%d" % (oldx, self.vx, oldx, self.vx))
            raise Exception

        thing = pygame.sprite.spritecollideany(self, block_list)
        if thing:
            self.rect.x = oldx
            if self.hitByPlayer(thing):
                self.fixAngleByPlayer(thing)
            else:
                self.angle = math.pi - self.angle

        # update y
        self.rect.y = oldy + self.vy
        thing = pygame.sprite.spritecollideany(self, block_list)
        if thing:
            self.rect.y = oldy
            if self.hitByPlayer(thing):
                self.fixAngleByPlayer(thing)
            else:
                self.angle = -self.angle

PLAYER1, PLAYER2, DUAL = range(3)

class Game():

    # game status
    INIT, RUNNING, DONE = range(3)
    # game mode
    SINGLE_GAME, DUAL_GAME = range(2)

    players = (("Player 1", "COM"), ("Player 1", "Player 2"))
    score_rect = [[30, 30], [width-150, 30]]

    def __init__(self):

        # by default, runs the single game mode
        self.mode = Game.SINGLE_GAME
        self.player = Game.players[self.mode]

        self.status = Game.INIT
        self.winner = "None"
        self.score = [0, 0]
        self.totalWin = DUAL

        # upper wall
        wall = Wall((0,0),(width,10))
        all_list.add(wall)
        wall_list.add(wall)
        block_list.add(wall)

        # downside wall
        wall = Wall((0,height-10),(width, 10))
        all_list.add(wall)
        wall_list.add(wall)
        block_list.add(wall)

        # player 1
        self.player1 = player = Player((10, height/2), (K_a, K_z))
        all_list.add(player)
        block_list.add(player)

        # player 2
        self.player2 = player = Player((width-10, height/2), (K_UP, K_DOWN))
        all_list.add(player)
        block_list.add(player)
        self.setMode(self.mode)

    def showMsg(self, msg):
        font.change()
        wordsur = font.render(msg)
        rect = wordsur.get_rect()
        screen.blit(wordsur, (width/2-rect.width/2, height/2-rect.height/2))

    def showScore(self):
        # display scores for players
        color = (white, white)
        for i in range(2):
            score_sur = score_font.render("%s: %d"%(self.player[i], self.score[i]), True, color[i])
            screen.blit(score_sur, Game.score_rect[i])

    def showInfo(self):
        # display howto at startup
        sur = info_font.render('Player 1:A/Z,Player 2:UP/DOWN', True, yellow)
        rect = sur.get_rect()
        screen.blit(sur, [width/2-rect.width/2, height-50-rect.height/2])
        sur = info_font.render('Game mode switch:B', True, yellow)
        rect = sur.get_rect()
        screen.blit(sur, [width/2-rect.width/2, height-30-rect.height/2])

    def setMode(self, mode):
        if mode == Game.SINGLE_GAME:
            self.mode = Game.SINGLE_GAME
            log("game in Single Mode")
            self.player2.setAuto(1)
        elif mode == Game.DUAL_GAME:
            self.mode = Game.DUAL_GAME
            log("game in Dual Mode")
            self.player2.setAuto(0)
        self.player = Game.players[self.mode]

    def toggleMode(self):
        if self.mode == Game.DUAL_GAME:
            self.setMode(Game.SINGLE_GAME)
        else:
            self.setMode(Game.DUAL_GAME)

    def run(self):

        space = 0

        # handle events
        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.event.post(pygame.event.Event(QUIT))
                elif event.key == K_SPACE:
                    space = 1
                elif event.key == K_b:
                    # toggle computer mode
                    self.toggleMode()
                elif event.key == K_p and 'ball' in dir(self):
                    self.ball.acc += 0.01
                    log("acc: "+str(self.ball.acc))

        # handle game status
        if self.status == Game.INIT:
            self.showMsg('Space to start, ESC to quit...')
            self.showInfo()
            keys = pygame.key.get_pressed()
            if space:
                game.createBall()
                game.status = Game.RUNNING

        elif self.status == Game.RUNNING:
            # notify work
            if self.mode == Game.SINGLE_GAME:
                self.player2.notifyCOM(self.ball.rect)
            x = self.ball.rect.x
            if x < 0 or x > width:
                if x < 0:
                    winner = PLAYER2
                else:
                    winner = PLAYER1
                self.winner = self.player[winner]
                self.score[winner] += 1
                self.status = Game.DONE
                if self.score[PLAYER1] > self.score[PLAYER2]:
                    self.totalWin = PLAYER1
                elif self.score[PLAYER1] < self.score[PLAYER2]:
                    self.totalWin = PLAYER2
                else:
                    self.totalWin = DUAL
                self.removeBall()

        elif self.status == Game.DONE:
            self.showMsg("%s win!"%self.winner+" Space for next turn...")
            keys = pygame.key.get_pressed()
            if space:
                self.status = Game.INIT

        self.showScore()

    def createBall(self):
        # the ball
        if 'ball' not in dir(self):
            self.ball = ball = Ball((width/2, height/2))
            all_list.add(ball)
        else:
            warn('createBall() failed since there is a ball!')

    def removeBall(self):
        if 'ball' in dir(self):
            # we should both remove ball in the all_list and self params
            all_list.remove(self.ball)
            del self.ball
        else:
            warn("removeBall() failed since there is no ball!")

game = Game()

log('starting game...')

# -------- Main Program Loop -----------
while True:
 
    # Set the screen background
    screen.fill(black)

    all_list.update()
    all_list.draw(screen)

    game.run()
 
    # Limit to 20 frames per second
    clock.tick(30)
 
    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

