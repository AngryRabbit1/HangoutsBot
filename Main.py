import os
import logging
from Core.Bot import HangoutsBot


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
    # setup logging
    logging.basicConfig(level=logging.INFO, format='[ %(asctime)s ][ %(name)s ][ %(levelname)s ] %(message)s')
    log = logging.getLogger(__name__)

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

    # Shut up some of the logging
    logging.getLogger('hangups.parsers').setLevel(logging.WARNING)
    logging.getLogger('hangups.http_utils').setLevel(logging.WARNING)
    logging.getLogger('hangups.conversation').setLevel(logging.WARNING)
    command_char = '/'

    HangoutsBot(cookie_path, config_path, command_char=command_char).run()