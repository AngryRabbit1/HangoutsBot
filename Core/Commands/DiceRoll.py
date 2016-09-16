import random
import hangups
from Core.Commands.Dispatcher import DispatcherSingleton
import logging


log = logging.getLogger(__name__)


@DispatcherSingleton.register
def roll(bot, event, *args):
    """
    **Roll:**
    Usage: /roll: Roll one 6 sided dice
    Usage: /roll <number>: Roll <number> dice with 6 sides
    Usage: /roll <number1>d<number2>: Roll <number1> dice with <number2> sides
    """
    log.info('/roll from {}: {}'.format(event.user.full_name, ' '.join(args)))
    dice_max = 100

    if len(args) <= 1:
        str_dice = ''
        str_sides = ''
        list_args = args if len(args) == 0 else args[0].split('d')

        if len(args) == 0:
            str_sides = 6
            str_dice = 1
        elif len(list_args) == 1:
            str_sides = 6
            str_dice = list_args[0]
        elif len(list_args) == 2:
            str_sides = list_args[1]
            if list_args[0] == '':
                str_dice = 1
            else:
                str_dice = list_args[0]
        else:
            response = 'Too many arguments sent.'
            bot.send_message(event.conv, response)
            return

        try:
            num_dice = int(str_dice)
            num_sides = int(str_sides)
        except:
            warn_text = 'Not a valid integer.'
            bot.send_message(event.conv, warn_text)
            return

        if num_dice > dice_max:
            response = "Can't roll more than 100 dice."

        elif num_sides == 1:
            response = "Can't roll a 1-sided dice."

        elif num_dice > 0 and num_sides > 0:
            random.seed()
            dice_rolls = [random.randint(1, num_sides) for i in range(num_dice)]
            dice_sum = sum(dice_rolls)
            roll_desc = '{}d{}'.format(num_dice, num_sides)

            if num_dice == 1:
                response = '{} rolled: {}'.format(roll_desc, str(dice_rolls[0]))
            else:
                response = '{} rolled: {} = {}'.format(roll_desc, ', '.join([str(i) for i in dice_rolls]), dice_sum)

        else:
            response = 'Numbers must be larger than 0.'

        bot.send_message(event.conv, response)

    else:
        response = 'Too many arguments sent.'
        bot.send_message(event.conv, response)
        return