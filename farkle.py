#!/usr/bin/env python3

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

"""The dice game Farkle.

Roll 6 dice and choose a scoring combo. Then roll the remaining dice
or end the turn.

Author: Skorpio
License: MIT
"""


import random
from collections import OrderedDict
from operator import itemgetter

__version__ = '0.1.1'


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


def roll_dice(num):
    return ''.join(sorted(str(random.randint(1, 6)) for _ in range(num)))


def user_input(combos, chosen):
    while True:
        choice = input('>>> ').lower()
        possible_indices = (str(i+1) for i in range(len(combos)))
        if choice in possible_indices:
            return choice
        elif chosen and choice in ('r', 'e'):
            return choice


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


def play_turn(player, players, last_round, max_score):
    name = player['name']
    total_score = player['score']
    ai = player['ai']
    roll = roll_dice(6)
    score = 0
    max_score = max_score
    chosen = False
    while True:
        infos = name, score, total_score
        print('{} has score {} and {} banked.'.format(*infos))
        print('Dice:', roll if roll else 'Hot dice!')
        combos = [combo for combo in POINTS if combo in roll]
        if not combos and not chosen:
            print('xxxxxxxxxxxxx FARKLED xxxxxxxxxxxxx')
            score = 0
            break
        if not ai:
            for idx, c in enumerate(combos, 1):
                print('({}) Remove {} for {} points.'.format(
                    idx, c, POINTS[c]))
        if chosen and not ai:
            print('R to roll again.')
            print('E to end your turn.')
        if ai:
            keep_going = False
            if last_round:
                keep_going = last_round and max_score > total_score
            print(keep_going)
            print(max_score, total_score)

            choice = ai_input(
                combos,
                chosen,
                score,
                keep_going,
                dice_left=roll)
            print('{} chooses {}.'.format(name, choice))
        else:
            choice = user_input(combos, chosen)
        chosen = True
        if choice == 'e':
            break
        elif choice == 'r':
            chosen = False
            dice_left = len(roll) if roll else 6
            roll = roll_dice(dice_left)
            continue
        combo = combos[int(choice)-1]
        roll = roll.replace(combo, '', 1)
        score += POINTS[combo]
    return score


def play_round(players):
    """Every player plays a round, return True if last round."""
    last_round = False
    max_score = TARGET_SCORE
    if any(player['done'] for player in players):
        last_round = True
        max_score = get_max_score(players)
        print('='*11, 'Last round', '='*12)
        players = [player for player in players if not player['done']]
    for player in players:
        player['score'] += play_turn(player, players, last_round, max_score)
        if player['score'] >= TARGET_SCORE:
            player['done'] = True
            break
        print('-'*35)
    return last_round


def print_status(players):
    """Print total points of players."""
    print('='*13, 'Status', '='*14)
    for player in players:
        print('{name} has {score} points.'.format_map(player))
    print('='*35)


def input_to_int(message):
    while True:
        try:
            player_num = int(input(message))
        except ValueError:
            print('Incorrect input.')
            continue
        if player_num not in range(0, 100):
            print('Incorrect input.')
            continue
        return player_num


def get_max_score(players):
    return max(players, key=itemgetter('score'))['score']


def main():
    print('='*14, 'Farkle', '='*14, '\n')
    human_players = input_to_int('Enter number of human players: ')
    ai_players = input_to_int('Enter number of AI players: ')
    if not human_players and not ai_players:
        return None
    names = ['Mary', 'Bob', 'Ben', 'Eryn', 'John',
             'Ellen', 'Elizabeth', 'Jason']
    random.shuffle(names)
    players = []
    for num in range(1, human_players+1):
        name = input('Player {} enter your name: '.format(num))
        players.append({'ai': False, 'score': 0, 'name': name, 'done': False})
    for num in range(1, ai_players+1):
        name = names[num-1] if num < len(names) else num
        players.append({'ai': True, 'score': 0, 'name': name, 'done': False})

    print('The game begins.')
    game_over = False
    while not game_over:
        game_over = play_round(players)
        print_status(players)

    max_score = get_max_score(players)
    winners = [pl for pl in players if pl['score'] == max_score]
    for winner in winners:
        print('{name} is the winner with {score} points.'.format_map(winner))
    print('Game over.')


if __name__ == '__main__':
    main()
    input('Thank you for playing.')
