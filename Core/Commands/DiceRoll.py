import random
import hangups
from Core.Commands.Dispatcher import DispatcherSingleton
import logging
import re


log = logging.getLogger(__name__)
dice_max = 100


@DispatcherSingleton.register
def roll(bot, event, *args):
    """
    **Roll:**
    Usage: /roll: Roll one 6 sided dice
    Usage: /roll <number>: Roll <number> dice with 6 sides
    Usage: /roll <number1>d<number2>: Roll <number1> dice with <number2> sides
    Usage: /roll <number1>d<number2>+<number3>: Roll <number1> dice with <number2> sides and add <number3>
    """
    log.info('/roll from {}: {}'.format(event.user.full_name, ' '.join(args)))
    global dice_max

    user = ' '.join(args)
    p1 = re.compile('^\s*(\d+)\s*\+?\s*(\d*)\s*$', re.IGNORECASE)
    p2 = re.compile('^\s*d\s*(\d+)\s*\+?\s*(\d*)\s*$', re.IGNORECASE)
    p3 = re.compile('^\s*(\d+)\s*d\s*(\d+)\s*\+?\s*(\d*)\s*$', re.IGNORECASE)
    s1 = p1.search(user)
    s2 = p2.search(user)
    s3 = p3.search(user)

    if len(args) == 0:
        num_dice = 1
        num_sides = 6
        num_add = 0
    elif s1:
        num_dice = int(s1.group(1))
        num_sides = 6
        num_add = 0 if s1.group(2) == '' else int(s1.group(2))
    elif s2:
        num_dice = 1
        num_sides = int(s2.group(1))
        num_add = 0 if s2.group(2) == '' else int(s2.group(2))
    elif s3:
        num_dice = int(s3.group(1))
        num_sides = int(s3.group(2))
        num_add = 0 if s3.group(3) == '' else int(s3.group(3))
    else:
        return

    num_dice = num_dice if num_dice <= dice_max else 0
    dice_rolls = roll_dice(num_dice, num_sides)
    dice_sum = sum(dice_rolls) + num_add
    if num_add == 0:
        roll_desc = '{}d{}'.format(num_dice, num_sides)
    else:
        roll_desc = '{}d{}+{}'.format(num_dice, num_sides, num_add)

    response = '{} rolled: {} = {}'.format(roll_desc, ', '.join([str(i) for i in dice_rolls]), dice_sum)
    bot.send_message(event.conv, response)


def roll_dice(num_dice, num_sides):
    random.seed()
    dice_rolls = [random.randint(1, num_sides) for i in range(num_dice)]
    return dice_rolls