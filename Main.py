import os
import logging
from Core.Bot import HangoutsBot
from Core.Util.UtilBot import get_args, init_database, db_updater
from threading import Thread


base_config = '''{
  "admins": ["YOUR-USER-ID-HERE"],
  "autoreplies_enabled": true,
  "autoreplies": [
    [["^@[\\\\w\\s]+\\\\++$"],"/karma {}"],
    [["^@[\\\\w\\\\s]+-+$"],"/karma {}"],
    [["bot", "robot", "Yo"], "/think {}"],
    [["^(https?:\\\\/\\\\/)?([\\\\da-z\\\\.-]+)\\\\.([a-z\\\\.]{2,6})([\\\\/\\\\w \\\\.-]*)*\\\\/?$"],"/_url_handle {}"],
    [["^@[\\\\w\\\\s]+$"], "/karma {}"],
    [["^@[\\\\w\\\\s]+\\\\++$"], "/_karma {}"],
    [["^@[\\\\w\\\\s]+-+$"], "/_karma {}",
  ],
  "development_mode": false,
  "commands_admin": ["hangouts", "reload", "quit", "config", "block", "record clear"],
  "commands_conversation_admin": ["leave", "echo", "block"]
  "commands_enabled": true,
  "forwarding_enabled": false,
  "rename_watching_enabled": true,
  "conversations": {
    "CONV-ID-HERE": {
      "autoreplies": [
        [["whistle", "bot", "whistlebot"], "/think {}"],
        [["trash"], "You're trash"]
      ],
      "forward_to": [
        "CONV1_ID"
      ]
    }
  }
}'''


if __name__ == "__main__":
    args = get_args()

    # setup logging
    logging.basicConfig(level=logging.INFO, format='[ %(asctime)s ][ %(name)s ][ %(levelname)s ] %(message)s')
    log = logging.getLogger(__name__)

    # setup database
    log.debug('Starting db-updater worker thread')
    db, db_updates_queue = init_database()
    t = Thread(target=db_updater, name='db-updater', args=(db, db_updates_queue))
    t.daemon = True
    t.start()

    # setup config
    # todo: switch to configargparse
    if os.path.isfile("config.json"):
        config_path = 'config.json'
        cookie_path = 'cookies.txt'
    elif os.path.isfile("Core" + os.sep + "config.json"):
        config_path = "Core" + os.sep + "config.json"
        cookie_path = "Core" + os.sep + "cookies.txt"
    else:
        log.warning("Error finding config.json file. Creating default config file config.json")
        config_path = "Core" + os.sep + "config.json"
        cookie_path = "Core" + os.sep + "cookies.txt"
        config_file = open(config_path, 'w+')
        config_file.writelines(base_config)
        config_file.close()

    # Shut up some of the logging cause of the spamming
    logging.getLogger('hangups.parsers').setLevel(logging.WARNING)
    logging.getLogger('hangups.http_utils').setLevel(logging.WARNING)
    logging.getLogger('hangups.conversation').setLevel(logging.WARNING)
    logging.getLogger('hangups.auth').setLevel(logging.WARNING)
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.WARNING)
    logging.getLogger('hangups.client').setLevel(logging.WARNING)
    logging.getLogger('hangups.channel').setLevel(logging.WARNING)
    logging.getLogger('root').setLevel(logging.WARNING)
    logging.getLogger('hangups.user').setLevel(logging.WARNING)
    logging.getLogger('root').setLevel(logging.WARNING)
    command_char = '/'

    # start the bot
    HangoutsBot(cookie_path, config_path, command_char=command_char).run()