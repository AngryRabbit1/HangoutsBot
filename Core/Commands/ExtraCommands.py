from fractions import Fraction
import json
import random
from urllib import parse, request
from bs4 import BeautifulSoup
import hangups
import requests
import logging
import re
from Core.Commands.Dispatcher import DispatcherSingleton
from Core.Util import UtilBot


log = logging.getLogger(__name__)


@DispatcherSingleton.register
def udefine(bot, event, *args):
    log.info('/udefine from {}: {}'.format(event.user.full_name, ' '.join(args)))
    if ''.join(args) == '?':
        segments = [hangups.ChatMessageSegment('Urbanly Define', is_bold=True),
                    hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                    hangups.ChatMessageSegment(
                        'Usage: /udefine <word to search for> <optional: definition number [defaults to 1st]>'),
                    hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                    hangups.ChatMessageSegment('Purpose: Define a word.')]
        bot.send_message_segments(event.conv, segments)
    else:
        api_host = 'http://urbanscraper.herokuapp.com/search/'
        num_requested = 0
        returnall = False
        if len(args) == 0:
            bot.send_message(event.conv, "Invalid usage of /udefine.")
            return
        else:
            if args[-1] == '*':
                args = args[:-1]
                returnall = True
            if args[-1].isdigit():
                # we subtract one here because def #1 is the 0 item in the list
                num_requested = int(args[-1]) - 1
                args = args[:-1]

            term = parse.quote('.'.join(args))
            response = requests.get(api_host + term)
            error_response = 'No definition found for \"{}\".'.format(' '.join(args))
            if response.status_code != 200:
                bot.send_message(event.conv, error_response)
            result = response.content.decode()
            result_list = json.loads(result)
            if len(result_list) == 0:
                bot.send_message(event.conv, error_response)
                return
            num_requested = min(num_requested, len(result_list) - 1)
            num_requested = max(0, num_requested)
            result = result_list[num_requested].get(
                'definition', error_response)
            if returnall:
                segments = []
                for string in result_list:
                    segments.append(hangups.ChatMessageSegment(string))
                    segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))
                bot.send_message_segments(event.conv, segments)
            else:
                segments = [hangups.ChatMessageSegment(' '.join(args), is_bold=True),
                            hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                            hangups.ChatMessageSegment(result + ' [{0} of {1}]'.format(
                                num_requested + 1, len(result_list)))]
                bot.send_message_segments(event.conv, segments)


@DispatcherSingleton.register
def flip(bot, event, *args):
    log.info('/flip from {}: {}'.format(event.user.full_name, ' '.join(args)))
    if ''.join(args) == '?':
        segments = [hangups.ChatMessageSegment('Flip', is_bold=True),
                    hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                    hangups.ChatMessageSegment('Usage: /flip <optional: number of times to flip>'),
                    hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                    hangups.ChatMessageSegment('Purpose: Flips a coin.')]
        bot.send_message_segments(event.conv, segments)
    else:
        times = 1
        if len(args) > 0 and args[-1].isdigit():
            times = int(args[-1]) if int(args[-1]) < 1000000 else 1000000
        heads, tails = 0, 0
        for x in range(0, times):
            n = random.randint(0, 1)
            if n == 1:
                heads += 1
            else:
                tails += 1
        if times == 1:
            bot.send_message(event.conv, "Heads!" if heads > tails else "Tails!")
        else:
            bot.send_message(event.conv,
                             "Winner: " + (
                                 "Heads!" if heads > tails else "Tails!" if tails > heads else "Tie!") + " Heads: " + str(
                                 heads) + " Tails: " + str(tails) + " Ratio: " + (str(
                                 Fraction(heads, tails)) if heads > 0 and tails > 0 else str(heads) + '/' + str(tails)))


@DispatcherSingleton.register
def quote(bot, event, *args):
    log.info('/quote from {}: {}'.format(event.user.full_name, ' '.join(args)))
    if ''.join(args) == '?':
        segments = [hangups.ChatMessageSegment('Quote', is_bold=True),
                    hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                    hangups.ChatMessageSegment(
                        'Usage: /quote <optional: terms to search for> <optional: number of quote to show>'),
                    hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                    hangups.ChatMessageSegment('Purpose: Shows a quote.')]
        bot.send_message_segments(event.conv, segments)
    else:
        USER_ID = "3696"
        DEV_ID = "ZWBWJjlb5ImJiwqV"
        QUERY_TYPE = "RANDOM"
        fetch = 0
        if len(args) > 0 and args[-1].isdigit():
            fetch = int(args[-1])
            args = args[:-1]
        query = '+'.join(args)
        if len(query) > 0:
            QUERY_TYPE = "SEARCH"
        url = "http://www.stands4.com/services/v2/quotes.php?uid=" + USER_ID + "&tokenid=" + DEV_ID + "&searchtype=" + QUERY_TYPE + "&query=" + query
        soup = BeautifulSoup(request.urlopen(url))
        if QUERY_TYPE == "SEARCH":
            children = list(soup.results.children)
            numQuotes = len(children)
            if numQuotes == 0:
                bot.send_message(event.conv, "Unable to find quote.")
                return

            if fetch > numQuotes - 1:
                fetch = numQuotes
            elif fetch < 1:
                fetch = 1
            bot.send_message(event.conv, "\"" +
                             children[fetch - 1].quote.text + "\"" + ' - ' + children[
                                 fetch - 1].author.text + ' [' + str(
                fetch) + ' of ' + str(numQuotes) + ']')
        else:
            bot.send_message(event.conv, "\"" + soup.quote.text + "\"" + ' -' + soup.author.text)


@DispatcherSingleton.register
def define(bot, event, *args):
    """
    **Define:**
    Usage: /define <word to search for> <optional: definition number [defaults to 1] OR * to show all definitions>
    Usage: /define <word to search for> <start index and end index in form of int:int (e.g., /define test 1:3)>
    Purpose: Show definitions for a word.
    """
    log.info('/define from {}: {}'.format(event.user.full_name, ' '.join(args)))
    if args[-1].isdigit():
        definition, length = UtilBot.define(' '.join(args[0:-1]), num=int(args[-1]))
        segments = [hangups.ChatMessageSegment(' '.join(args[0:-1]).title(), is_bold=True),
                    hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                    hangups.ChatMessageSegment(
                        definition.replace('\n', ''))]
        bot.send_message_segments(event.conv, segments)
    elif args[-1] == '*':
        args = list(args)
        args[-1] = '1:*'
    if ':' in args[-1]:
        start, end = re.split(':', args[-1])
        try:
            start = int(start)
        except ValueError:
            start = 1
        display_all = False
        if end == '*':
            end = 100
            display_all = True
        else:
            try:
                end = int(end)
            except ValueError:
                end = 3
        if start < 1:
            start = 1
        if start > end:
            end, start = start, end
        if start == end:
            end += 1
        if len(args) <= 1:
            bot.send_message(event.conv, "Invalid usage for /define.")
            return
        query = ' '.join(args[:-1])
        definition_segments = [hangups.ChatMessageSegment(query.title(), is_bold=True),
                               hangups.ChatMessageSegment('', segment_type=hangups.SegmentType.LINE_BREAK)]
        if start < end:
            x = start
            while x <= end:
                definition, length = UtilBot.define(query, num=x)
                definition_segments.append(hangups.ChatMessageSegment(definition))
                if x != end:
                    definition_segments.append(
                        hangups.ChatMessageSegment('', segment_type=hangups.SegmentType.LINE_BREAK))
                    definition_segments.append(
                        hangups.ChatMessageSegment('', segment_type=hangups.SegmentType.LINE_BREAK))
                if end > length:
                    end = length
                if display_all:
                    end = length
                    display_all = False
                x += 1
            bot.send_message_segments(event.conv, definition_segments)
        return
    else:
        args = list(args)
        args.append("1:3")
        define(bot, event, *args)
        return


@DispatcherSingleton.register
def vote(bot, event, set_vote=None, *args):
    """**Vote:**
    Usage: /vote <subject to vote on>
    Usage: /vote <yea|yes|for|nay|no|against (used to cast a vote)>
    Usage: /vote cancel
    Usage: /vote abstain
    Usage: /vote start <subject to vote on>
    Usage: /vote start admin (used to start a vote for a new conversation admin)
    """

    log.info('/vote from {}: {}'.format(event.user.full_name, ' '.join(args)))
    # Abstains user from voting.
    if set_vote is not None and set_vote.lower() == 'abstain':
        if UtilBot.is_vote_started(event.conv_id):
            bot.send_message(event.conv, 'User {} has abstained from voting.'.format(event.user.full_name))
            if UtilBot.abstain_voter(event.conv_id, event.user.full_name):
                bot.send_message(event.conv, "The vote has ended because all voters have abstained.")
                return
        else:
            bot.send_message(event.conv, 'No vote currently in process to abstain from.')
            return

        # Check if the vote has ended
        vote_result = UtilBot.check_if_vote_finished(event.conv_id)
        if vote_result is not None:
            if vote_result != 0:
                bot.send_message(event.conv,
                                 'In the matter of: "' + UtilBot.get_vote_subject(event.conv_id) + '", the ' + (
                                     'Yeas' if vote_result > 0 else 'Nays') + ' have it.')
            else:
                bot.send_message(event.conv, "The vote ended in a tie in the matter of: {}".format(
                    UtilBot.get_vote_subject(event.conv_id)))
            UtilBot.end_vote(event.conv_id)
        return

    # Cancels the vote
    if set_vote is not None and set_vote.lower() == "cancel":
        if UtilBot.is_vote_started(event.conv_id):
            bot.send_message(event.conv, 'Vote "{}" cancelled.'.format(UtilBot.get_vote_subject(event.conv_id)))
            UtilBot.end_vote(event.conv_id)
        else:
            bot.send_message(event.conv, 'No vote currently started.')
        return

    # Starts a new vote
    if not UtilBot.is_vote_started(event.conv_id) and set_vote == "start":
        vote_subject = ' '.join(args)
        vote_callback = None

        # TODO Refactor this into a more easily extensible system.
        if vote_subject.lower().strip() == "admin":  # For the special Conversation Admin case.

            vote_subject = '{} for Conversation Admin for chat {}'.format(event.user.full_name,
                                                                          get_conv_name(event.conv))

            def set_conv_admin(won):
                if won:
                    try:
                        bot.config["conversations"][event.conv_id]["conversation_admin"] = event.user.id_[0]
                    except (KeyError, TypeError):
                        bot.config["conversations"][event.conv_id] = {}
                        bot.config["conversations"][event.conv_id]["admin"] = event.user.id_[0]
                    bot.config.save()

            vote_callback = set_conv_admin

        UtilBot.set_vote_subject(event.conv_id, vote_subject)
        UtilBot.init_new_vote(event.conv_id, event.conv.users)
        if vote_callback is not None:
            UtilBot.set_vote_callback(event.conv_id, vote_callback)
        bot.send_message(event.conv, "Vote started for subject: " + vote_subject)
        return

    # Cast a vote.
    if set_vote is not None and UtilBot.is_vote_started(event.conv_id):
        if UtilBot.can_user_vote(event.conv_id, event.user):
            set_vote = set_vote.lower()
            if set_vote == "true" or set_vote == "yes" or set_vote == "yea" or set_vote == "for" or set_vote == "yay" or set_vote == "aye":
                UtilBot.set_vote(event.conv_id, event.user.full_name, True)
            elif set_vote == "false" or set_vote == "no" or set_vote == "nay" or set_vote == "against":
                UtilBot.set_vote(event.conv_id, event.user.full_name, False)
            else:
                bot.send_message(event.conv,
                                 "{}, you did not enter a valid vote parameter.".format(event.user.full_name))
                return

            # Check if the vote has ended
            vote_result = UtilBot.check_if_vote_finished(event.conv_id)
            if vote_result is not None:
                if vote_result != 0:
                    bot.send_message(event.conv,
                                     'In the matter of: "' + UtilBot.get_vote_subject(event.conv_id) + '", the ' + (
                                         'Yeas' if vote_result > 0 else 'Nays') + ' have it.')
                else:
                    bot.send_message(event.conv, "The vote ended in a tie in the matter of: {}".format(
                        UtilBot.get_vote_subject(event.conv_id)))
                UtilBot.end_vote(event.conv_id, vote_result)
            return
        else:
            bot.send_message(event.conv_id, 'User {} is not allowed to vote.'.format(event.user.full_name))
            return

    # Check the status of a vote.
    if UtilBot.is_vote_started(event.conv_id):
        status = UtilBot.get_vote_status(event.conv_id)
        if len(status) > 1:
            bot.send_message_segments(event.conv, UtilBot.text_to_segments('\n'.join(status)))
        else:
            bot.send_message(event.conv, "No vote currently started.")
    else:
        bot.send_message(event.conv, "No vote currently started.")