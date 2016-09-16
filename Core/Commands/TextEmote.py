# -*- coding: utf-8 -*-

import hangups
import logging
from Core.Commands.Dispatcher import DispatcherSingleton


log = logging.getLogger(__name__)

_text_emotes = {
    'shrug': u'¯\_(ツ)_/¯',
    'tableflip': u'(╯°□°）╯︵ ┻━┻',
    'happy': u'ヽ(´▽`)/',
    'tablefix': u'┬──┬ ノ( ゜-゜ノ)',
    'monocle': u'( ಠ ͜ʖರೃ)',
    'angry': u'(╬ ಠ益ಠ)',
    'lenny': u'( ͡° ͜ʖ ͡°)',
    'fight': u'(ง ͠° ͟ل͜ ͡°)ง',
    'gimme': u'(づ｡◕‿◕｡)づ'
    }


@DispatcherSingleton.register
def em(bot, event, *args):
    """
    **em:**
    Usage: /em <emote name>: Respond with the specified emote.
    """
    log.info('/em from {}: {}'.format(event.user.full_name, ' '.join(args)))
    global _text_emotes
    target = ' '.join(args)
    if target in _text_emotes:
        bot.send_message(event.conv, _text_emotes[target])


@DispatcherSingleton.register
def emlist(bot, event, *args):
    """
    **emlist:**
    Usage: /emlist
    Purpose: Get a list of emotes.
    """
    log.info('/emlist from {}: {}'.format(event.user.full_name, ' '.join(args)))
    global _text_emotes
    response = ', '.join(sorted(list(_text_emotes.keys())))
    segments = [hangups.ChatMessageSegment('Available Emotes:', is_bold=True),
                hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                hangups.ChatMessageSegment(response)]
    bot.send_message_segments(event.conv, segments)