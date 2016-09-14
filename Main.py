import os
import logging


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

    try:
        import nltk
		# For Bots that have installed the nltk data in the root project dir.
        nltk.data.path.append("nltk_data")  

        # Keeps our words up to date for the URL summarizer.
        nltk.download("stopwords")
        nltk.download("punkt")
    except ImportError:
        log.info("nltk package is not installed. URL Summarizer will not work.")

    command_char = '/'

    from Core.Bot import HangoutsBot

    if os.path.isfile("config.json"):
        HangoutsBot("cookies.txt", "config.json", command_char=command_char).run()
    elif os.path.isfile("Core" + os.sep + "config.json"):
        HangoutsBot("Core" + os.sep + "cookies.txt", "Core" + os.sep + "config.json", command_char=command_char).run()
    else:
        log.warning("Error finding config.json file. Creating default config file config.json")
        config_file = open("config.json", 'w+')
        config_file.writelines(base_config)
        config_file.close()
        HangoutsBot("Core" + os.sep + "cookies.txt", "Core" + os.sep + "config.json", command_char=command_char).run()