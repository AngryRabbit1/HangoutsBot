import logging
import hangups
from hangups.ui.utils import get_conv_name
from Core.Commands.Dispatcher import DispatcherSingleton
from Core.Util import UtilBot


log = logging.getLogger(__name__)


@DispatcherSingleton.register_unknown
def unknown_command(bot, event, *args):
	pass


@DispatcherSingleton.register
def help(bot, event, command=None, *args):
    valid_user_commands = []
    for command_test in sorted(DispatcherSingleton.commands.keys()):
        if UtilBot.check_if_can_run_command(bot, event, command_test):
            valid_user_commands.append(command_test)
    docstring = """
    **Current Implemented Commands:**
    {}
    Use: /<command name> ? or /help <command name> to find more information about the command.
    """.format(', '.join(valid_user_commands))
    if command == '?' or command is None:
        bot.send_message_segments(event.conv, UtilBot.text_to_segments(docstring))
    else:
        if command in DispatcherSingleton.commands.keys():
            func = DispatcherSingleton.commands[command]
            if func.__doc__:
                bot.send_message_segments(event.conv, UtilBot.text_to_segments(func.__doc__))
            else:  # Compatibility purposes for the old way of showing help text.
                args = ['?']
                func(bot, event, *args)


@DispatcherSingleton.register_hidden
def rename(bot, event, *args):
    """
    **Rename:**
    Usage: /rename <new title>
    Purpose: Changes the chat title of the room.
    """
    yield from bot._client.setchatname(event.conv_id, ' '.join(args))


@DispatcherSingleton.register_hidden
def users(bot, event, *args):
    """
    **Users:**
    Usage: /users
    Purpose: Lists all users in the current conversations.
    """
    segments = [hangups.ChatMessageSegment('Users: '.format(len(event.conv.users)),
                                           is_bold=True),
                hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK)]
    for user in sorted(event.conv.users, key=lambda x: x.full_name.split()[-1]):
        link = 'https://plus.google.com/u/0/{}/about'.format(user.id_.chat_id)
        segments.append(hangups.ChatMessageSegment(user.full_name, hangups.SegmentType.LINK,
                                                   link_target=link))
        if user.emails:
            segments.append(hangups.ChatMessageSegment(' ('))
            segments.append(hangups.ChatMessageSegment(user.emails[0], hangups.SegmentType.LINK,
                                                       link_target='mailto:{}'.format(user.emails[0])))
            segments.append(hangups.ChatMessageSegment(')'))

        segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))
    bot.send_message_segments(event.conv, segments)


@DispatcherSingleton.register_hidden
def user(bot, event, username, *args):
    """
    **User:**
    Usage: /user <user name>
    Purpose: Lists information about the specified user in the current chat.
    """
    username_lower = username.strip().lower()
    segments = [hangups.ChatMessageSegment('User: "{}":'.format(username),
                                           is_bold=True),
                hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK)]
    for u in sorted(event.conv.users, key=lambda x: x.full_name.split()[-1]):
        if username_lower not in u.full_name.lower():
            continue

        link = 'https://plus.google.com/u/0/{}/about'.format(u.id_.chat_id)
        segments.append(hangups.ChatMessageSegment(u.full_name, hangups.SegmentType.LINK,
                                                   link_target=link))
        if u.emails:
            segments.append(hangups.ChatMessageSegment(' ('))
            segments.append(hangups.ChatMessageSegment(u.emails[0], hangups.SegmentType.LINK,
                                                       link_target='mailto:{}'.format(u.emails[0])))
            segments.append(hangups.ChatMessageSegment(')'))
        segments.append(hangups.ChatMessageSegment(' ... {}'.format(u.id_.chat_id)))
        segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))
    if len(segments) > 2:
        bot.send_message_segments(event.conv, segments)
    else:
        bot.send_message(event.conv, 'No user "%s" in current conversation.' % username)


@DispatcherSingleton.register
def leave(bot, event, conversation=None, *args):
    """
    **Leave:**
    Usage: /leave
    **Purpose: Leaves the chat room.**
    """
    convs = []
    if not conversation:
        convs.append(event.conv)
    else:
        conversation = conversation.strip().lower()
        for c in bot.list_conversations():
            if conversation in get_conv_name(c, truncate=True).lower():
                convs.append(c)

    for c in convs:
        yield from c.send_message([
            hangups.ChatMessageSegment('I\'ll be back!')
        ])
        yield from bot._conv_list.leave_conversation(c.id_)


@DispatcherSingleton.register
def mute(bot, event, *args):
    """
    **Mute:**
    Usage: /mute
    Purposes: Mutes all autoreplies and commands.
    """
    try:
        bot.config['conversations'][event.conv_id]['autoreplies_enabled'] = False
        bot.config['conversations'][event.conv_id]['commands_enabled'] = False
    except KeyError:
        bot.config['conversation'][event.conv_id] = {}
        bot.config['conversation'][event.conv_id]['autoreplies_enabled'] = False
        bot.config['conversations'][event.conv_id]['commands_enabled'] = False
    bot.config.save()
    bot.send_message(event.conv, "Bot has been muted. Use /unmute to resume.")


@DispatcherSingleton.register
def unmute(bot, event, *args):
    """
    **Unmute:**
    Usage: /unmute
    Purpose: Unmutes all autoreplies and commands.
    """
    if ''.join(args) == '?':
        segments = [hangups.ChatMessageSegment('Unmute', is_bold=True),
                    hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                    hangups.ChatMessageSegment('Usage: /unmute'),
                    hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                    hangups.ChatMessageSegment('Purpose: Unmutes all non-command replies.')]
        bot.send_message_segments(event.conv, segments)
    else:
        try:
            bot.config['conversations'][event.conv_id]['autoreplies_enabled'] = True
            bot.config['conversations'][event.conv_id]['commands_enabled'] = True
        except KeyError:
            bot.config['conversations'][event.conv_id] = {}
            bot.config['conversations'][event.conv_id]['autoreplies_enabled'] = True
            bot.config['conversations'][event.conv_id]['commands_enabled'] = True
        bot.config.save()
        bot.send_message(event.conv, "Bot has been unmuted.")