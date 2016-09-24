import random
import hangups
import logging
from Core.Commands.Dispatcher import DispatcherSingleton


log = logging.getLogger(__name__)


_canned_responses = (
    'As the prophecy foretold.',
    'But at what cost?',
    'So let it be written; so let it be done.',
    'So... it has come to this.',
    "That's just what they would've said",
    'Is this why fate brought us together?',
    '... just like in my dream ...',
    'And thus, I die.',
    'Be that as it may, still may it be as it may be.',
    'There is no escape from destiny.',
    "Wise words by wise men write wise deeds in wise pen.",
    'In *this* economy?',
    '... and then the wolves came.'
    )


@DispatcherSingleton.register
def canned(bot, event, *args):
    """
    **Canned:**
    Usage: /canned: Response that works for anything.
    """
    log.info('/canned from {}: {}'.format(event.user.full_name, ' '.join(args)))
    global _canned_responses
    random.seed()
    response = _canned_responses[random.randint(1, len(_canned_responses)) - 1]
    bot.send_message(event.conv, response)