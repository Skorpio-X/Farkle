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
DICE_SHEET = load(os.path.join('graphics', 'sheet', 'monti5.png'), alpha=True)
DICE_SHADOW = load(os.path.join('graphics', 'sheet', 'dice_shadow.png'), alpha=True)
for i in range(0, 5*128 + 1, 128):
    DICE_SHEET.blit(DICE_SHADOW, (i, 0))

# Split DICE_SHEET into several images.
# Need to invert dice num because the sheet starts with 6.
DICE_IMAGES = {}
for dice_num, i in zip(range(6, 0, -1), range(0, 5*128 + 1, 128)):
    rect = pg.Rect((i, 0, 128, 128))
    DICE_IMAGES[dice_num] = DICE_SHEET.subsurface(rect)

# BACKGROUND = load(os.path.join('graphics', 'background2blue.png'))
BACKGROUND = load(os.path.join('graphics', 'background2.png'))
BUTTON = load(os.path.join('graphics', 'Button.png'), alpha=True)
BUTTON2 = load(os.path.join('graphics', 'Button2.png'), alpha=True)
BUTTON3 = load(os.path.join('graphics', 'Button2.png'), alpha=True)

FONT = pg.font.Font(None, 30)
FONT2 = pg.font.Font(None, 46)
WHITE = Color('white')
GREEN = Color('springgreen1')
