import random
import hangups
import logging
from Core.Commands.Dispatcher import DispatcherSingleton


log = logging.getLogger(__name__)


_magic_responses = (
    'It is certain',
    'It is decidedly so',
    'Without a doubt',
    'Yes, definitely',
    'You may rely on it',
    'As I see it, yes',
    'Most likely',
    'Outlook good',
    'Yes',
    'Signs point to yes',
    "That's an affirmative",
    'Probably, yeah',
    'Sources say yes',
    'Probably not',
    "That's a negative",
    "Don't count on it",
    'My reply is no',
    'My sources say no',
    'Outlook not so good',
    'Very doubtful',
    'Bite my shiny metal ass'
    )


@DispatcherSingleton.register
def ball(bot, event, *args):
    """
    **Ball:**
    Usage: /ball <question>: Ask the Magic 8-ball a question.
    """
    log.info('/ball from {}: {}'.format(event.user.full_name, ' '.join(args)))
    global _magic_responses
    if len(args) == 0:
        response = "You didn't ask a question."
    else:
        random.seed()
        response = _magic_responses[random.randint(1, len(_magic_responses)) - 1]

    bot.send_message(event.conv, response)