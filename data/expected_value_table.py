import itertools
from collections import OrderedDict
import json

# Contribution of davidnkyle

# Run this file to create a table of expected values at various game states. This information
# gets combined with specific information about a roll to come up with the best AI move.
# output is to expected_values.json. This only needs to be run once to create the json file in the first place.

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

df = {}


def exp_of_dice(dice, score, exp_dict):
    """
    analyzes the string dice role given to estimate the value of selecting dice for points versus re-rolling.
    """
    if score >= 10000:
        return score
    combos = [combo for combo in POINTS if combo in dice]
    if len(dice) == 6:
        raise ValueError('This function should only be called for 5 or fewer dice')
    dice_id = len(dice)
    if dice_id == 0: # if no dice are left then you will get a chance to roll all 6 again
        dice_id = 6
    max_exp = exp_dict[str(score)][str(dice_id)]
    for c in combos:
        new_exp = exp_of_dice(dice.replace(c, '', 1), score + POINTS[c], exp_dict)
        if new_exp > max_exp:
            max_exp = new_exp
    return max_exp


if __name__ == '__main__':
    # this runs all possible dice moves for each value in the table to derive probabilities of each dice/scoring event
    for score in reversed(range(0, 10000, 50)):
        print(score)
        df[str(score)] = dict()
        for num_dice in range(1, 7):
            exp = 0
            for dice_list in itertools.product(*[['1', '2', '3', '4', '5', '6'] for _ in range(num_dice)]):
                dice_list = list(dice_list)
                dice_list.sort()
                dice = ''.join(dice_list)
                combos = [combo for combo in POINTS if combo in dice]
                max_exp = 0
                for c in combos:
                    new_exp = exp_of_dice(dice.replace(c, '', 1), score + POINTS[c], df)
                    if new_exp > max_exp:
                        max_exp = new_exp
                exp += max_exp
            best_strategy = max(score, exp/(6**num_dice))
            df[str(score)][str(num_dice)] = int(best_strategy+0.5) # round to integer for clean output

    with open('expected_values.json', 'w') as f:
        json.dump(df, f, indent=4)


