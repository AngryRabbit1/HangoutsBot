from bisect import bisect_left
from datetime import datetime, timedelta
import os
from urllib import request
from bs4 import BeautifulSoup, Tag
import re
import hangups
import configargparse
from peewee import MySQLDatabase, InsertQuery
from queue import Queue
import logging
import time


log = logging.getLogger(__name__)
_url_regex = r"^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$"


def memoize(function):
    memo = {}

    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            rv = function(*args)
            memo[args] = rv
            return rv
    return wrapper


@memoize
def get_args():
    configpath = os.path.join(os.path.dirname(__file__), '../config.ini')
    parser = configargparse.ArgParser(default_config_files=[configpath])

    parser.add_argument('--db-name', help='Name of the database to be used')
    parser.add_argument('--db-user', help='Username for the database')
    parser.add_argument('--db-pass', help='Password for the database')
    parser.add_argument('--db-host', help='IP or hostname for the database')
    parser.add_argument('--db-port', help='Port for the database', type=int, default=3306)

    args = parser.parse_args()
    return args


args = get_args()
db_updates_queue = Queue()
db = MySQLDatabase(args.db_name, user=args.db_user, password=args.db_pass, host=args.db_host, port=args.db_port)


def init_database():
    log.info('Connecting to MySQL database on %s:%i', args.db_host, args.db_port)
    global db
    global db_updates_queue

    while True:
        try:
            db.connect()
            break
        except Exception as e:
            log.warning('%s... Retrying', e)
            time.sleep(1)

    db.close()
    return [db, db_updates_queue]


def db_updater(db, db_updates_queue):
    # The forever loop
    while True:
        try:
            # Loop the queue
            while True:
                # Connect to the database
                while True:
                    try:
                        db.connect()
                        break
                    except Exception as e:
                        log.warning('%s... Retrying', e)
                        time.sleep(1)
                # Process queue
                model, data = db_updates_queue.get()
                bulk_upsert(model, data)
                db_updates_queue.task_done()
                db.close()

                if db_updates_queue.qsize() > 50:
                    log.warning("DB queue is > 50 (@%d); try increasing --db-threads", db_updates_queue.qsize())

        except Exception as e:
            log.exception('Exception in db_updater: %s', e)


def bulk_upsert(cls, data):
    while True:
        try:
            InsertQuery(cls, rows=data.values()).upsert().execute()
        except Exception as e:
            log.warning('%s... Retrying', e)
            continue

        break


def is_user_conv_admin(bot, user_info, conv_id=None):
    if isinstance(user_info, hangups.ConversationEvent):
        user_id = user_info.user_id
        conv_id = user_info.conversation_id
    elif isinstance(user_info, str):
        user_id = user_info
    elif isinstance(user_info, hangups.user.User):
        user_id = user_info.user_id[0]
    elif isinstance(user_info, hangups.user.UserID):
        user_id = user_info[0]

    if conv_id is None:
        raise ValueError("conv_id can not be None.")

    if user_id is None:
        raise ValueError("user_info can not be null")

    conv_admin_list = bot.get_config_suboption(conv_id, 'conversation_admin')
    return conv_admin_list and user_id in conv_admin_list


def is_user_admin(bot, user_info, conv_id=None):
    user_id = None
    if isinstance(user_info, hangups.ConversationEvent):
        user_id = user_info.user_id
        conv_id = user_info.conversation_id
    elif isinstance(user_info, str):
        user_id = user_info
    elif isinstance(user_info, hangups.user.User):
        user_id = user_info.user_id[0]
    elif isinstance(user_info, hangups.user.UserID):
        user_id = user_info[0]

    if conv_id is None:
        raise ValueError("conv_id can not be None.")

    if user_id is None:
        raise ValueError("user_info does not contain valid User information.")

    admins_list = bot.get_config_suboption(conv_id, 'admins')
    return admins_list and user_id in admins_list


def check_if_can_run_command(bot, event, command):
    commands_admin_list = bot.get_config_suboption(event.conv_id, 'commands_admin')
    commands_conv_admin_list = bot.get_config_suboption(event.conv_id, 'commands_conversation_admin')
    admins_list = bot.get_config_suboption(event.conv_id, 'admins')
    conv_admin = bot.get_config_suboption(event.conv_id, 'conversation_admin')


    # Check if this is a conversation admin command.
    if commands_conv_admin_list and (command in commands_conv_admin_list):
        if (admins_list and event.user_id[0] not in admins_list) \
                and (conv_admin and event.user_id[0] != conv_admin):
            return False

    # Check if this is a admin-only command.
    if commands_admin_list and (command in commands_admin_list):
        if not admins_list or event.user_id[0] not in admins_list:
            return False
    return True


def find_private_conversation(conv_list, user_id, default=None):
    for conv_id in conv_list._conv_dict.keys():
        current_conv = conv_list.get(conv_id)
        if len(current_conv.users) == 2:

            # Just in case the bot has a reference to a conversation it isn't actually in anymore.
            if not (current_conv.users[0].is_self or current_conv.users[1].is_self):
                continue

            # Is the user in this conversation?
            if user_id in [user.id_ for user in current_conv.users]:
                return current_conv
    return default


def define(word, num=1):
    if num < 1:
        num = 1
    try:
        url = "http://wordnetweb.princeton.edu/perl/webwn?s=" + word + "&sub=Search+WordNet&o2=&o0=&o8=1&o1=1&o7=&o5=&o9=&o6=&o3=&o4=&h=0000000000"
    except Exception as e:
        print(e)
        return 'Couldn\'t download definition.'
    try:
        soup = BeautifulSoup(request.urlopen(url))
    except:
        return "Network Error: Couldn't download definition.", 0
    if soup.ul is not None:
        definitions = [x.text for x in list(soup.ul) if isinstance(x, Tag) and x.text != '\n' and x.text != '']
        if len(definitions) >= num:
            return (definitions[num - 1] + '[' + str(num) + ' of ' + str(len(definitions)) + ']')[
                   3:].capitalize(), len(definitions)
    return "Couldn\'t find definition.", 0


# Uses basic markdown syntax for italics and bold.
def text_to_segments(text):
    if not text:
        return []

    # Replace two consecutive spaces with space and non-breakable space, strip of leading/trailing spaces,
    # then split text to lines
    lines = [x.strip() for x in text.replace('  ', ' \xa0').splitlines()]

    # Generate line segments
    segments = []
    for line in lines[:-1]:
        if line:
            if line[:2] == '**' and line[-2:] == '**':
                line = line[2:-2]
                segments.append(hangups.ChatMessageSegment(line, is_bold=True))
            elif line[0] == '*' and line[-1] == '*':
                line = line[1:-1]
                segments.append(hangups.ChatMessageSegment(line, is_italic=True))
            else:
                segments.append(hangups.ChatMessageSegment(line))
            segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))
    if lines[-1]:
        segments.append(hangups.ChatMessageSegment(lines[-1]))

    return segments