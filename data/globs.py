import os
from collections import OrderedDict

import pygame as pg
from pygame.locals import *


pg.init()


def load(path, alpha=False):
    if not alpha:
        return pg.image.load(path).convert()
    else:
        return pg.image.load(path).convert_alpha()
    

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pg.display.set_caption('Farkle')

TARGET_SCORE = 10000
POINTS = OrderedDict((
    ('111', 1000),
    ('666', 600),
    ('555', 500),
    ('444', 400),
    ('333', 300),
    ('222', 200),
    ('1', 100),
    ('5', 50),
    ))

FPS = 30

IMAGES = {}
for i in range(1, 7):
    IMAGES[i] = load(os.path.join('graphics', 'dice{}.png'.format(i)), alpha=True)

sheet = load(os.path.join('graphics', 'sheet', 'monti3.png'), alpha=True)
# DICE_IMAGES = {}
# for i in range(0, 257, 128):
#     s = pg.Surface((128, 128), pg.SRCALPHA, 32).convert_alpha()
#     for j in range(0, 385, 128):
#         s.blit(
DICE_SHEET = load(os.path.join('graphics', 'sheet', 'monti5.png'), alpha=True)
# BACKGROUND = load(os.path.join('graphics', 'background2blue.png'))
BACKGROUND = load(os.path.join('graphics', 'background2.png'))
BUTTON = load(os.path.join('graphics', 'Button.png'), alpha=True)
    
FONT = pg.font.Font(None, 30)
GREEN = Color('springgreen1')
