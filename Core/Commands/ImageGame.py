# -*- coding: utf-8 -*-

import logging
import hangups
from Core.Commands.Dispatcher import DispatcherSingleton
import random
from .ImageSearch import send_image


log = logging.getLogger(__name__)
headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0"}

random_for = (
    'cat',
    'cats',
    'kitty',
    'dog',
    'puppy'
    )

# 0 = no game in progress, 1 = new game started, waiting for players to join, 2+ = player (n-1)'s turn to guess
game_state = 0
main_conv = None
main_conv_id = None
# 0 = player id, 1 = player name, 2 = player conv, 3 = player guess
players = []


def join_game(bot, event, user):
    global players
    user_id = user.id_.chat_id
    user_name = user.full_name
    convs = bot.list_conversations()

    for p in players:
        if p[0] == user_id:
            bot.send_message(p[2], '{}, you are already in the game.'.format(user_name))
            return

    conv_found = False
    for c in convs:
        users = c.users
        if len(users) == 2:
            if users[0].id_.chat_id == user_id or users[1].id_.chat_id == user_id:
                conv_found = True
                break

    if conv_found:
        players.append([user_id, user_name, c, ''])
        bot.send_message(event.conv, '{} has joined the game.'.format(user_name))
        bot.send_message(c, 'You have joined the game. You will use this chat to send your guess when it is your turn. Please keep this chat open until the game is finished.')
    else:
        bot.send_message(event.conv, 'No private chat found. Please start a private chat and try joining again.')


@DispatcherSingleton.register
def imggame(bot, event, *args):
    """
    **Imggame (in progress, should work, might be buggy):**
    Usage: /imggame rules: Send rules about the image game.
    Usage: /imggame new: Start a new game. Only one game can be active at one time.
    Usage: /imggame join: Join the game. You must have started a private chat with the bot first.
    Usage: /imggame start: Start the game once all players have joined.
    Usage: /imggame <guess>: Send your guess about previous image. Only do this in the private chat.
    Usage: /imggame stop: Prematurely end a game.
    """
    log.info('/imggame from {}: {}'.format(event.user.full_name, ' '.join(args)))
    global game_state
    global main_conv
    global main_conv_id
    global players

    if len(args) == 0:
        pass

    # send rules text
    elif args[0].lower() == 'rules' and len(args) == 1:
        segments = [hangups.ChatMessageSegment('Image Game Rules', is_bold=True),
                    hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                    hangups.ChatMessageSegment('A randomly chosen player will send an /imggame <search term> command in a private chat to the bot.'),
                    hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                    hangups.ChatMessageSegment('The result of that search will be sent to the main chat.'),
                    hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                    hangups.ChatMessageSegment('Once all players have made a guess, the full list of search terms will be printed.')]
        bot.send_message_segments(event.conv, segments)

    # begin a new game
    elif args[0].lower() == 'new' and len(args) == 1:
        if game_state == 0:
            game_state = 1
            main_conv = event.conv
            main_conv_id = event.conv_id
            bot.send_message(event.conv, 'Image Game started, use "/imggame join" to participate. You must have a private chat open with the bot first.')
            join_game(bot, event, event.user)
        elif game_state == 1:
            if event.conv_id == main_conv_id:
                bot.send_message(event.conv, 'There is a game in progress. Use "/imggame join" to participate. You must have a private chat open with the bot first.')
            else:
                bot.send_message(event.conv, 'There is a game in progress in another chat.')
        elif game_state > 1:
            if event.conv_id == main_conv_id:
                bot.send_message(event.conv, 'There is a game in progress.')
            else:
                bot.send_message(event.conv, 'There is a game in progress in another chat.')
        else:
            log.error('Uncaught scenario in image game.')

    # join a player to a game in progress
    elif args[0].lower() == 'join' and len(args) == 1:
        if game_state == 0:
            bot.send_message(event.conv, 'There is no game in progress. Use "/imggame new" to begin a game.')
        elif game_state == 1:
            if event.conv_id == main_conv_id:
                join_game(bot, event, event.user)
            else:
                bot.send_message(event.conv, 'There is a game in progress in another chat.')
        elif game_state > 1:
            if event.conv_id == main_conv_id:
                bot.send_message(event.conv, 'There is a game in progress.')
            else:
                bot.send_message(event.conv, 'There is a game in progress in another chat.')
        else:
            log.error('Uncaught scenario in image game.')

    # start a game with the current players
    elif args[0].lower() == 'start' and len(args) == 1:
        if game_state == 0:
            bot.send_message(event.conv, 'There is no game in progress. Use "/imggame new" to begin a game.')
        elif game_state == 1:
            if event.conv_id == main_conv_id:
                if len(players) >= 2:
                    game_state = 2
                    players.sort(key=lambda x: random.random())
                    bot.send_message(event.conv, "The game is afoot. The first player is {}. Send your search term in the private chat.".format(players[game_state - 2][1]))
                    bot.send_message(players[game_state - 2][2], 'You are the first player. Use "/imggame <search term>" to submit the first image.')
                else:
                    bot.send_message(event.conv, "Can't start a game with less than 2 players.")
            else:
                bot.send_message(event.conv, 'There is a game in progress in another chat.')
        elif game_state > 1:
            if event.conv_id == main_conv_id:
                bot.send_message(event.conv, 'There is a game in progress.')
            else:
                bot.send_message(event.conv, 'There is a game in progress in another chat.')
        else:
            log.error('Uncaught scenario in image game.')

    # prematurely end a game and reset game state
    elif args[0].lower() == 'stop' and len(args) == 1:
        if game_state == 0:
            bot.send_message(event.conv, 'There is no game in progress. Use "/imggame new" to begin a game.')
        elif game_state >= 1:
            if event.conv_id == main_conv_id:
                segments = [hangups.ChatMessageSegment('Game has been stopped before the end:', is_bold=True)]
                for p in players:
                    segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))
                    segments.append(hangups.ChatMessageSegment('{}: {}'.format(p[1], p[3])))
                bot.send_message_segments(main_conv, segments)
                game_state = 0
                main_conv = None
                main_conv_id = None
                players = []
            else:
                bot.send_message(event.conv, 'There is a game in progress in another chat.')
        else:
            log.error('Uncaught scenario in image game.')

    # process user guess
    else:
        if game_state == 0:
            bot.send_message(event.conv, 'There is no game in progress. Use "/imggame new" to begin a game.')
        elif game_state == 1:
            if event.conv_id == main_conv_id:
                bot.send_message(event.conv, 'The game has not started yet. Use "imggame start" to start the game now.')
            else:
                bot.send_message(event.conv, 'There is a game in progress in another chat.')
        elif game_state > 1:
            if players[game_state - 2][0] == event.user.id_.chat_id:
                if players[game_state - 2][2].id_ == event.conv_id:
                    global headers
                    global random_for

                    query = ' '.join(args)
                    if query.lower() in random_for:
                        random.seed()
                        first = random.randint(2, 1000000)
                    else:
                        first = 2

                    if game_state == 2:
                        success = yield from send_image(bot, main_conv, "Guess made by {}.".format(players[game_state - 2][1]), players[game_state - 2][2], first, query)
                    else:
                        success = yield from send_image(bot, main_conv, "First image submitted by {}.".format(players[game_state - 2][1]), players[game_state - 2][2], first, query)

                    if success:
                        players[game_state - 2][3] = query
                        if len(players) <= game_state - 1:
                            segments = [hangups.ChatMessageSegment('Game has ended:', is_bold=True)]
                            for p in players:
                                segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))
                                segments.append(hangups.ChatMessageSegment('{}: {}'.format(p[1], p[3])))

                            bot.send_message_segments(main_conv, segments)
                            game_state = 0
                            main_conv = None
                            main_conv_id = None
                            players = []
                        else:
                            game_state += 1
                            bot.send_message(main_conv, 'Next player is {}.'.format(players[game_state - 2][1]))
                            bot.send_message(players[game_state - 2][2], 'It is your turn. Use "/imggame <search term>" to submit a guess on the previous image.'.format(players[game_state - 2][1]))
                else:
                    bot.send_message(event.conv, 'You must send your guess in the private chat.')
            else:
                bot.send_message(event.conv, 'You are not the active player.')
        else:
            log.error('Uncaught scenario in image game.')