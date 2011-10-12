import pygame
from pygame.locals import *

class FlashGreyFont(pygame.font.Font):
    def __init__(self, file, size):
        pygame.font.Font.__init__(self, file, size)
        self.max = 240
        self.min = 50 
        self.step = 7 
        self.grey = self.max
        self.inc = -1

    def change(self):
        self.grey += self.inc * self.step
        if self.grey < self.min:
            self.inc = 1
        elif self.grey > self.max:
            self.inc = -1

    def setGrey(self, val):
        if val > self.max:
            self.grey = self.max
        elif val < self.min:
            self.grey = self.min
        else:
            self.grey = val

    def render(self, msg):
        i = self.grey
        color = (i,i,i)
        return pygame.font.Font.render(self, msg, True, color)
