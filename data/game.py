import random
import time
import sys

import pygame as pg
from pygame.locals import *

from data.globs import TARGET_SCORE, POINTS, WINDOW_WIDTH, WINDOW_HEIGHT,FPS
from data.globs import FONT, FONT2, BACKGROUND, screen, WHITE, DICE_SHEET
from data.objects import Button, ButtonSmall, Player, DiceRoll

SWITCHSCENE = USEREVENT
MOVE_DOWN = USEREVENT + 1


def post_event(event):
    pg.event.post(pg.event.Event(event))


class SceneManager:
    """Manages scenes and contains the main and event loop."""

    def __init__(self):
        self.fps_clock = pg.time.Clock()
        self.dt = self.fps_clock.tick()
        self.model = IntroModel()
        self.view = IntroView(self.model)
        self.game = IntroController(self.model)
        self.view.controller = self.game

        self.scene = 'intro'

    def run(self):
        while not self.game.done:
            self.handle_events()
            self.game.update(self.dt, self.fps_clock.get_fps())
            self.view.draw(screen, self.dt)
            self.dt = self.fps_clock.tick(FPS)
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
        players_human = self.model.players_human
        players_ai = self.model.players_ai
        self.view = View()
        self.game = Game(players_human, players_ai)
        self.view.controller = self.game

    def switchscene_intro(self):
        self.model = IntroModel()
        self.view = IntroView(self.model)
        self.game = IntroController(self.model)
        self.view.controller = self.game
        self.view.model = self.model


class Game:
    """Game controller class."""

    def __init__(self, players_human, players_ai):
        self.player_num = players_human + players_ai
        self.players = [Player('Player {}'.format(num), ai=False)
                        for num in range(1, players_human+1)]
        self.players.extend(Player('AI {}'.format(num), ai=True)
                            for num in range(1, players_ai+1))
        random.shuffle(self.players)
#         for player in self.players:
#             player.score = 1000
        self.player_index = 0
        self.player = self.players[self.player_index]
        self.score = 0
        self.done = False
        self.dice = DiceRoll(6)
        self.dice_left = len(self.dice)
        self.selected_dice = []
        self.farkled = False
        self.can_bank = False
        self.can_roll = False
        self.last_round = False
        self.game_over = False
        self.max_score = 3000
        self.high_score = 0
        self.winner = None
        self.last_round_counter = self.player_num

        self.button_add = Button(pos=(WINDOW_WIDTH/100*4, WINDOW_HEIGHT/12*5),
                                 callback=self.add_score, text='Add score')
        self.button_roll = Button(pos=(WINDOW_WIDTH/100*4, WINDOW_HEIGHT/12*7),
                                  callback=self.roll, text='Roll')
        self.button_bank = Button(pos=(WINDOW_WIDTH/100*4, WINDOW_HEIGHT/12*9),
                                  callback=self.bank, text='Bank')
        self.buttons = [self.button_add, self.button_roll, self.button_bank]

    def handle_events(self, event):
        if event.type == pg.QUIT:
            self.done = True
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.farkled:
                    self.farkled = False
                    self.roll()
                no_collisions = True
                for die in self.dice:
                    collided = die.rect.collidepoint(event.pos)
                    # Deselect one die.
                    if collided and die in self.selected_dice:
                        idx = self.selected_dice.index(die)
                        del self.selected_dice[idx]
                        no_collisions = False
                    # Select one die.
                    elif collided:
                        self.selected_dice.append(die)
                        no_collisions = False
                # Deselect all.
                clicked_button = self.button_add.rect.collidepoint(event.pos)
                if no_collisions and not clicked_button:
                    self.selected_dice = []

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                post_event(SWITCHSCENE)
            if event.key == pg.K_RETURN:
                self.add_score()
            if event.key == pg.K_a:
                self.roll()
            if event.key == pg.K_f:
                print(self.dice)
        for button in self.buttons:
            button.handle_event(event)

    def update(self, dt, fps):
        self.dt = dt
        self.fps = fps
        if self.last_round and self.last_round_counter <= 0 and not self.game_over:
            self.set_game_over()

        # AI turn.
        if self.player.ai:
            # TODO: sleep delays the game.
            # TODO: AI skips player farkle.
            time.sleep(1)
            ai_decision = self.player.choose_dice(self.dice, self.score)
            if ai_decision == 'roll':
                print('ai roll')
                self.roll()
            elif ai_decision == 'bank':
                print('ai bank')
                self.bank()
            else:  # score
                print('ai score')
                self.selected_dice = ai_decision
                self.add_score()

    def roll(self):
        if self.can_roll:
            self.dice = DiceRoll(self.dice_left)
            self.selected_dice = []
            print('Dice roll:', self.dice)
            string_dice = str(self.dice)
            self.farkled = not any(combo in string_dice for combo in POINTS)
            if self.farkled:
                print('Farkled')
                self.next_player()
            else:
                self.can_roll = False
                self.can_bank = False

    def next_player(self):
        self.can_roll = True
        self.dice_left = 6
        self.score = 0
        self.player_index = (self.player_index + 1) % self.player_num
        self.player = self.players[self.player_index]
        if self.winner == self.player:
            self.player_index = (self.player_index + 1) % self.player_num
            self.player = self.players[self.player_index]
        if self.last_round:
            self.last_round_counter -= 1

    def add_score(self):
        """Add selected dice to self.score."""
        selected = ''.join(map(str, sorted(self.selected_dice)))
        print('selected', selected)
        print('dice', self.selected_dice)
        print('Dice before remove:', self.dice)
        try:
            print(POINTS[selected])
            self.score += POINTS[selected]
        except KeyError:
            print('Not a valid combo.')
        else:
            self.dice.remove(self.selected_dice)
            print('Dice after remove:', self.dice)
            self.can_roll = True
            self.can_bank = True
        self.selected_dice = []
        self.dice_left = len(self.dice)
        if self.dice_left == 0:
            self.dice_left = 6

    def bank(self):
        if self.can_bank:
            self.player.score += self.score
            if self.player.score >= self.max_score and not self.last_round:
                self.last_round = True
                self.high_score = self.player.score
                self.winner = self.player
                print('Last round')
            self.high_score = max(p.score for p in self.players)
            self.score = 0
            self.next_player()
            self.can_bank = False
            self.dice.empty()

    def set_game_over(self):
        self.game_over = True
        self.can_roll = False
        self.can_bank = False
        self.winner = [player for player in self.players
                       if player.score == self.high_score]
        print('Game over')


class View:

    def __init__(self):
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT

    def draw(self, screen, dt):
        screen.blit(BACKGROUND, (0, 0))

#         fps_txt = FONT.render('dt {} fps {:.2f}'.format(
#             dt, self.controller.fps), True, WHITE)
#         screen.blit(fps_txt, (WINDOW_WIDTH/100*70, self.height/10))

        score_txt = 'Score {}'.format(self.controller.score)
        score_font = FONT.render(score_txt, True, WHITE)
        screen.blit(score_font, (WINDOW_WIDTH/100*40, WINDOW_HEIGHT/12*5.3))

        total_score = 'Total score {}'.format(self.controller.player.score)
        tot_score = FONT.render(total_score, True, WHITE)
        screen.blit(tot_score, (WINDOW_WIDTH/100*40, WINDOW_HEIGHT/12*7.3))

        high_score = 'High score {}'.format(self.controller.high_score)
        high_score2 = FONT.render(high_score, True, WHITE)
        screen.blit(high_score2, (WINDOW_WIDTH/100*40, WINDOW_HEIGHT/12*9.3))

        self.controller.dice.draw(screen)
        for die in self.controller.selected_dice:
            pg.draw.rect(screen, (100, 200, 56), die.rect, 2)
        for button in self.controller.buttons:
            button.draw(screen)

        if self.controller.farkled:
            farkled = FONT.render('--- FARKLED ---', True, pg.Color('red'))
            screen.blit(farkled, (WINDOW_WIDTH/100*30, WINDOW_HEIGHT/12*3))

        player = "{}'s turn.".format(self.controller.player.name)
        txt = FONT.render(player, True, WHITE)
        screen.blit(txt, (WINDOW_WIDTH/100*4, self.height/10))

        if self.controller.last_round:
            last = FONT2.render('Last round!', True, WHITE)
            screen.blit(last, (WINDOW_WIDTH/100*4, self.height/22))

        if self.controller.game_over:
            winner = ', '.join(str(player.name) for player in self.controller.winner)
            game_over_txt = 'GAME OVER - The winner is {}'.format(winner)
            game_over = FONT2.render(game_over_txt, True, WHITE)
            screen.blit(game_over, (WINDOW_WIDTH/100*4, WINDOW_HEIGHT/10*9))

        pg.display.flip()

    def handle_events(self, event):
        pass


class IntroModel:

    def __init__(self):
        self.sprites = pg.sprite.Group()
        # Used a sprite to test MVC.
#         self.player = Player(1)
#         self.player.rect.topleft = 300, 100
        self.button = Button(
            pos=(WINDOW_WIDTH//10*3, WINDOW_HEIGHT//10*6),
            text='Start game')
        self.button_incr = ButtonSmall(
            pos=(WINDOW_WIDTH//10*3, WINDOW_HEIGHT//10*2),
            callback=self.increase_human_players,
            text='+')
        self.button_decr = ButtonSmall(
            pos=(WINDOW_WIDTH//10*4, WINDOW_HEIGHT//10*2),
            callback=self.decrease_human_players,
            text='-')
        self.button_incr_ai = ButtonSmall(
            pos=(WINDOW_WIDTH//10*3, WINDOW_HEIGHT//10*4),
            callback=self.increase_ai_players,
            text='+')
        self.button_decr_ai = ButtonSmall(
            pos=(WINDOW_WIDTH//10*4, WINDOW_HEIGHT//10*4),
            callback=self.decrease_ai_players,
            text='-')

        buttons = (self.button,
                   self.button_incr,
                   self.button_decr,
                   self.button_incr,
                   self.button_incr_ai,
                   self.button_decr_ai)

        for button in buttons:
            self.sprites.add(button)

        self.players_human = 1
        self.players_ai = 2

    def handle_events(self, event):
        if event.type == MOVE_DOWN:
            print(event)
            self.player.rect.y += 30
        for sprite in self.sprites:
            sprite.handle_event(event)

    def increase_human_players(self):
        if self.players_human < 10:
            self.players_human += 1

    def decrease_human_players(self):
        if self.players_human > 0:
            self.players_human -= 1

    def increase_ai_players(self):
        if self.players_ai < 10:
            self.players_ai += 1

    def decrease_ai_players(self):
        if self.players_ai > 0:
            self.players_ai -= 1


class IntroController:

    def __init__(self, model):
        self.done = False
        self.model = model

    def handle_events(self, event):
        if event.type == pg.QUIT:
            self.done = True
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_s:
                post_event(MOVE_DOWN)
        if event.type == pg.MOUSEBUTTONDOWN:
            collided = self.model.button.rect.collidepoint(event.pos)
            if event.button == 1 and collided:
                post_event(SWITCHSCENE)

    def update(self, dt, fps):
        pass


class IntroView:

    def __init__(self, model):
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.model = model

    def draw(self, screen, dt):
        screen.blit(BACKGROUND, (0, 0))
        txt = FONT2.render('--- FARKLE ---', True, WHITE)
        screen.blit(txt, (self.width//2-150, self.height//100*5))
        
        txt = FONT.render('Human players {}'.format(self.model.players_human),
                           True, WHITE)
        screen.blit(txt, (self.width//100*53, self.height//100*23))
        
        txt = FONT.render('Computer players {}'.format(self.model.players_ai),
                           True, WHITE)
        screen.blit(txt, (self.width//100*53, self.height//100*43))
        self.model.sprites.draw(screen)
#         screen.blit(DICE_SHEET, (10, 300))
        pg.display.flip()

    def handle_events(self, event):
        pass
