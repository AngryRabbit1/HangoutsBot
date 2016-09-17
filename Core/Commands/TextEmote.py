# -*- coding: utf-8 -*-

import hangups
import logging
from Core.Commands.Dispatcher import DispatcherSingleton
from ..Util.EmoteModels import Ascii_Emotes
from ..Util.UtilBot import db_updates_queue


log = logging.getLogger(__name__)


def get_emotes(emote_name):
    query = (Ascii_Emotes
        .select(Ascii_Emotes.emote_name, Ascii_Emotes.emote_string)
        .where((Ascii_Emotes.emote_name.contains(emote_name)))
        .order_by(Ascii_Emotes.emote_name)
        .dicts())
    return query


def em_exists(emote_name):
    query = (Ascii_Emotes
        .select(Ascii_Emotes.emote_pk)
        .where((Ascii_Emotes.emote_name == emote_name))
        .dicts())

    if query:
        return True
    else:
        return False


def em_add(bot, event, emote_name, emote_string):
    if em_exists(emote_name):
        bot.send_message(event.conv, 'Emote "{}" already exists.'.format(emote_name))
    elif len(emote_string) == 0:
        bot.send_message(event.conv, 'Emote string is empty.')
    elif len(emote_string) > 255:
        bot.send_message(event.conv, 'Emote string is longer than 255 characters.')
    else:
        new_emote = dict()
        new_emote[emote_name] = {
            'user_id': 0,
            'emote_name': emote_name,
            'emote_string': emote_string
            }
        db_updates_queue.put((Ascii_Emotes, new_emote))
        bot.send_message(event.conv, 'New emote "{}" added.'.format(emote_name))


def em_list(bot, event):
    emote_list = [e['emote_name'] for e in get_emotes('')]
    response = ', '.join(emote_list)

    segments = [hangups.ChatMessageSegment('Available Emotes:', is_bold=True),
                hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                hangups.ChatMessageSegment(response)]
    bot.send_message_segments(event.conv, segments)


@DispatcherSingleton.register
def em(bot, event, *args):
    """
    **em:**
    Usage: /em <emote name>: Respond with the specified emote.
    Usage: /em list: List available emotes.
    Usage: /em add <emote name> <emote string>: Add a new emote.
    """
    log.info('/em from {}: {}'.format(event.user.full_name, ' '.join(args)))
    
    if len(args) == 0:
        em_list(bot, event)
    elif str(args[0]).lower() == 'list':
        em_list(bot, event)
    elif str(args[0]).lower() == 'add':
        emote_name = args[1]
        emote_string = ' '.join(args[2:])
        em_add(bot, event, emote_name, emote_string)
    else:
        emote_name = ' '.join(args)
        emotes = get_emotes(emote_name)
        if len(emotes) == 1 and str(emotes[0]['emote_name']).lower() == emote_name.lower():
            bot.send_message(event.conv, emotes[0]['emote_string'])