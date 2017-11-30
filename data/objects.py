# The MIT License (MIT)
#
# Copyright (c) 2016 Skorpio
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import random

import pygame as pg
from pygame.locals import *

from data.globs import DICE_SHEET, FONT, FONT2, DICE_SHADOW, DICE_IMAGES
from data.globs import BUTTON2, BUTTON3, POINTS


def roll_dice(num):
    return [Die(n) for n in sorted(random.randint(1, 6) for _ in range(num))]


class Player(pg.sprite.Sprite):

    def __init__(self, name, ai):
        super().__init__()
        self.image = pg.Surface((20, 40))
        self.image.fill(Color('red'))
        self.rect = self.image.get_rect()
        self.score = 0
        self.name = name
        self.ai = ai
        self.chosen = False

    def move_down(self):
        # Used for testing MVC.
        self.rect.y += 30

    def choose_dice(self, dice, score):
        # TODO: Doesn't handle hot dice.
        if not dice:  # Hot dice. Test needed.
            return 'roll'
        string_dice = str(dice)
        max_combo = ''
        for combo in POINTS:
            if combo in string_dice:
                max_combo = combo
                break
        if max_combo:
            if score < 200 and len(dice) > 3 and self.chosen:
                self.chosen = False
                return 'roll'
            else:  # Choose dice.
                self.chosen = True
                selected_dice = []
                for char in max_combo:
                    for die in dice:
                        if int(char) == die.num and not die in selected_dice:
                            selected_dice.append(die)
                            break
                return selected_dice
        if len(dice) < 3 and self.chosen or score >= 300 and self.chosen:
            self.chosen = False
            return 'bank'
        return 'roll'

# From the text version of the game.
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
        


class Die(pg.sprite.Sprite):

    def __init__(self, num, *sprite_groups):
        super().__init__(sprite_groups)
        self.num = num
        self.image = DICE_IMAGES[num]
        self.rect = self.image.get_rect()

    def __str__(self):
        return str(self.num)
    
    def __lt__(self, other):
        return self.num < other.num
    
    def __gt__(self, other):
        return self.num > other.num


class DiceRoll(pg.sprite.Group):

    def __init__(self, num):
        super().__init__()
        dice = roll_dice(num)
        for die, x in zip(dice, range(20, 700, 128)):
            die.rect.topleft = x, 100
            self.add(die)

    def __str__(self):
        return ''.join(map(str, sorted(self.sprites())))


class Button(pg.sprite.Sprite):

    def __init__(self, pos=(0, 0), callback=None, text=''):
        super().__init__()
        self.image = BUTTON2.copy()
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.callback = callback
        if text:
            txt = FONT.render(text, True, Color('white'))
            self.image.blit(txt, (30, 27))

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and self.callback:
                self.callback()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class ButtonSmall(Button):

   def __init__(self, pos=(0, 0), callback=None, text=''):
        super().__init__(pos, callback, text)
        self.image = BUTTON3.copy()
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        if text:
            txt = FONT2.render(text, True, Color('white'))
            self.image.blit(txt, (27, 21))


class NewEvent:

    def __init__(self, type_):
        self.type = type_
