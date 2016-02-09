import random

import pygame as pg
from pygame.locals import *

from data.globs import TARGET_SCORE, POINTS, WINDOW_WIDTH, WINDOW_HEIGHT,FPS
from data.globs import FONT, IMAGES, DICE_SHEET, BACKGROUND


class Die(pg.sprite.Sprite):

    def __init__(self, *sprite_groups):
        super().__init__(sprite_groups)
        self.sheet = DICE_SHEET
        self.state = 0
        self.frames = self.create_frames()
        self.current_image = self.frames[0]
        self.image = self.current_image
        self.rect = self.image.get_rect()
        self.num_map = {6: 0, 5: 1, 4: 2, 3: 3, 2: 4, 1: 5}

    def create_frames(self):
        frames = []
        for i in range(6):
            rect = pg.Rect((128*i, 0, 128, 128))
            image = self.sheet.subsurface(rect)
            frames.append(image)
        return frames

    @property
    def face(self):
        return self.image

    @face.setter
    def face(self, num):
        self.state = self.num_map[num]
        self.image = self.frames[self.state]

    def draw(self, surface, pos):
        surface.blit(self.current_image, pos)


def roll_dice(num):
    return ''.join(sorted(str(random.randint(1, 6)) for _ in range(num)))


def ai_input(combos, chosen, score, keep_going, dice_left):
    """AI's decision."""
    if combos:
        if score < 200 and len(dice_left) > 3 and chosen:
            return 'r'
        return combos.index(max(combos, key=lambda x: POINTS[x]))+1
    if not keep_going:
        if len(dice_left) < 3 and chosen or score >= 300 and chosen:
            return 'e'
    return 'r'


def get_max_score(players):
    return max(players, key=itemgetter('score'))['score']


class Player:

    def __init__(self, name):
        self.name = name
        self.score = 0


class Game:

    def __init__(self, player_num):
        self.player_num = player_num
        self.done = False
        self.fps_clock = pg.time.Clock()
        self.dt = self.fps_clock.tick()
        self.dice = pg.sprite.Group()
        self.roll = sorted(random.randint(1, 6) for _ in range(1, 7))
        for i in range(6):
            die = Die(self.dice)
            die.rect.topleft = (128*i, 128)
            die.face = self.roll[i]

    def run(self, screen):
        self.handle_events()
        self.run_logic()
        self.draw(screen)
        self.dt = self.fps_clock.tick(FPS)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            if event.type == pg.MOUSEBUTTONDOWN:
                # get button pressed
                # (button1, button2, button3,) = pg.mouse.get_pressed()
                if event.button == 1:
                    pass
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_a:
                    self.roll = roll_dice(6)
                    self.update_dice()
#             if event.type == pg.KEYUP:
#                 if event.key == pg.K_a:
#                     player.vel = (0, 0)

    def run_logic(self):
        pass

    def update_dice(self):
        for idx, die in enumerate(self.dice):
            die.face = int(self.roll[idx])

    def draw(self, screen):
#         screen.fill((60, 60, 90))
        screen.blit(BACKGROUND, (0, 0))
        txt = FONT.render("Choose dice", True, Color('springgreen1'))
        screen.blit(txt, (40, 60))
        txt = FONT.render("dt {} fps {}".format(
            self.dt, self.fps_clock), True, Color('springgreen1'))
        screen.blit(txt, (40, 90))
#         for i in range(1, 7):
#             screen.blit(IMAGES[i], ((i-1)*128, 128))
#             imgrect = IMAGES[i].get_rect()
#             imgrect.x = 128 * (i-1)
#             imgrect.y = 128
#             pg.draw.rect(screen, Color('springgreen1'), imgrect, 2)
#         for i, d in enumerate(self.die.frames):
#             screen.blit(d, (64, i * 128))
#         self.die.draw(screen, (64, 256))
        self.dice.draw(screen)

        pg.display.flip()

