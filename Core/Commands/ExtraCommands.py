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
            bot.send_message(event.conv, "Winner: " + ("Heads!" if heads > tails else "Tails!" if tails > heads else "Tie!") + " Heads: " + str(heads) + " Tails: " + str(tails))


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
        soup = BeautifulSoup(request.urlopen(url), "html.parser")
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