"""Farkle with GUI."""

import pygame as pg
from pygame.locals import *
import sys

from data.game import Player, Game
from data.globs import screen

__version__ = '0.0.3'


def main():
    game = Game(3)
    while not game.done:
        game.run(screen)
    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()
