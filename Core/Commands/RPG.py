# -*- coding: utf-8 -*-

import hangups
import logging
from Core.Commands.Dispatcher import DispatcherSingleton
from ..Util.EmoteModels import Ascii_Emotes
from ..Util.UtilBot import db_updates_queue
from .DiceRoll import roll_dice


log = logging.getLogger(__name__)


@DispatcherSingleton.register
def fireball(bot, event, *args):
    """
    **Fireball:**
    Usage: /fireball <user name>: Attack the user with a fireball.
    """
    log.info('/fireball from {}: {}'.format(event.user.full_name, ' '.join(args)))

    dice_results = roll_dice(8, 6)
    damage = sum(dice_results)

    if len(args) == 0:
        bot.send_message(event.conv, '{} fireballed themself in the face for {} damage.'.format(event.user.full_name, damage))
    else:
        target = ' '.join(args)
        if target.lower() == event.user.full_name.lower():
            bot.send_message(event.conv, '{} fireballed themself in the face for {} damage.'.format(event.user.full_name, damage))
            return

        target_found = False
        for user in event.conv.users:
            if target.lower() == user.full_name.lower():
                target_found = True
                break

        if target_found:
            bot.send_message(event.conv, '{} fireballed {} for {} damage.'.format(event.user.full_name, user.full_name, damage))
        else:
            bot.send_message(event.conv, 'Fireball could not find {} and rebounded on {} for {} damage.'.format(target, event.user.full_name, damage))