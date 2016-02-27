import random
import sys

import pygame as pg
from pygame.locals import *

from data.globs import TARGET_SCORE, POINTS, WINDOW_WIDTH, WINDOW_HEIGHT,FPS
from data.globs import FONT, IMAGES, DICE_SHEET, BACKGROUND, screen, GREEN, BUTTON


SWITCHSCENE = USEREVENT
MOVE_DOWN = USEREVENT + 1


def post_event(event):
    pg.event.post(pg.event.Event(event))

class Die(pg.sprite.Sprite):

    def __init__(self, *sprite_groups):
        super().__init__(sprite_groups)
        self.sheet = DICE_SHEET
        self.state = 0
        self.frames = self.create_frames()
        self.current_image = self.frames[0]
        self.image = self.current_image
        self.rect = self.image.get_rect()
        # TODO: Shouldn't be necessary to convert the dice
        # nums with this mapping.
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


class SceneManager:
    """Manages scenes and contains the main and event loop."""

    def __init__(self):
        self.scenes = []
        view = View()
        self.game = Game(player_num=3)
        view.controller = self.game
        self.scenes.append(self.game)
        self.scenes.append(view)

        self.model = IntroModel()
        self.view = IntroView(self.model)
        self.game = IntroController(self.model)
        self.view.controller = self.game

        self.scene = 'intro'

    def run(self):
        while not self.game.done:
            self.handle_events()
            self.view.draw()
        pg.quit()
        sys.exit()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == SWITCHSCENE:
                if self.scene == 'intro':
                    self.scene = 'game'
                    self.switchscene()
                elif self.scene == 'game':
                    self.scene = 'intro'
                    self.switchscene_intro()
            self.game.handle_events(event)
            self.view.handle_events(event)
            self.model.handle_events(event)

    def switchscene(self):
        self.view = View()
        self.game = Game(player_num=3)
        self.view.controller = self.game

    def switchscene_intro(self):
        self.view = IntroView()
        self.game = IntroController()
        self.view.controller = self.game
        self.model = IntroModel()
        self.view.model = self.model


class Game:
    """Game controller class."""

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

    def run(self):
        self.dt = self.fps_clock.tick(FPS)

    def handle_events(self, event):
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
            if event.key == pg.K_s:
                pg.event.post(pg.event.Event(SWITCHSCENE))
#             if event.type == pg.KEYUP:
#                 if event.key == pg.K_a:
#                     player.vel = (0, 0)

    def update_dice(self):
        for idx, die in enumerate(self.dice):
            die.face = int(self.roll[idx])


class View:

    def __init__(self):
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT

    def draw(self):
        screen.blit(BACKGROUND, (0, 0))
        txt = FONT.render("Choose dice", True, GREEN)
        screen.blit(txt, (self.width/10, self.height/10))
        txt = FONT.render("dt {} fps {}".format(
            self.controller.dt, self.controller.fps_clock), True, GREEN)
        screen.blit(txt, (self.width/10, self.height/7))
        self.controller.dice.draw(screen)

        pg.display.flip()

    def handle_events(self, event):
        pass

class Button(pg.sprite.Sprite):

    def __init__(self, pos=(0, 0), callback=None, text=None):
        super().__init__()
        self.image = BUTTON
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.topleft = self.pos
        self.callback = callback
        self.text = text
        if self.text:
            txt = FONT.render(self.text, True, Color('white'))
            self.image.blit(txt, (50, 50))

    def handle_event(self, event):
        collided = self.rect.collidepoint(event.pos)
        if hasattr(event, 'pos') and collided and self.callback:
            self.callback()

    def draw(self, screen):
        screen.blit(self.image, self.pos)


class NewEvent:

    def __init__(self, type_):
        self.type = type_


class Player(pg.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.image = pg.Surface((20, 40))
        self.image.fill(Color('red'))
        self.rect = self.image.get_rect()

    def move_down(self):
        self.rect.y += 30


class IntroModel:

    def __init__(self):
        self.sprites = pg.sprite.Group()
        self.player = Player()
        self.player.rect.topleft = 300, 100
        self.button = Button((WINDOW_WIDTH//10*3, WINDOW_HEIGHT//10*3),
                             text='Start game')
        self.sprites.add(self.player, self.button)


class IntroController:

    def __init__(self, model):
        self.done = False
        self.human_players = 0
        self.ai_players = 0
        self.model = model

    def handle_events(self, event):
        if event.type == pg.QUIT:
            self.done = True
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_s:
                post_event(MOVE_DOWN)
        if event.type == MOVE_DOWN:
            self.player.rect.y += 30
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and self.button.rect.collidepoint(event.pos):
                new_event = pg.event.Event(SWITCHSCENE)
                print('mouse click', event.pos)
                pg.event.post(new_event)


class IntroView:

    def __init__(self, model):
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.model = model

    def draw(self):
        screen.blit(BACKGROUND, (0, 0))
        txt = FONT.render("Choose players", True, GREEN)
        screen.blit(txt, (self.width//8, self.height//8))
        self.model.sprites.draw(screen)
        pg.display.flip()

    def handle_events(self, event):
        pass
