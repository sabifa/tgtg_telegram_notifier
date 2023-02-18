# tgtg_telegram_notifier
## Bot for [Too good to go](https://toogoodtogo.com)
Forked from: https://github.com/kacpi2442/am_bot

Changes:
- Only TGTG support
- uses inline_keyboard parameter for fancy telegram buttons
- only queries favorite shops
- uses german datetime format
- adds shop address to message
- allows to provide multiple chat ids for telegram bot (to send to multiple clients)

## Solution
Here is a screenshot:
![Telegram Screenshot](/result_screenshot.png "Telegram bot with notifications")

#### Tgtg API
There is a library wrapped around the API of the tgtg-app. You can find the library and a short documentation [here.](https://pypi.org/project/tgtg/)

#### Telegram bot
I used Telegram as the service to notify me, because they are quite supportive for adding your own bots to the platform and provide a rich API. [This article](https://medium.com/@ManHay_Hong/how-to-create-a-telegram-bot-and-send-messages-with-python-4cf314d9fa3e) provides a quick introduction into sending Telegram messages with python.

### Usage:
#### Install required libraries:
```pip install -r requirements.txt```
#### Create config file:
```cp config.example.json config.json```
#### Edit config file:
- Insert your bot token (you can get it from [@BotFather](https://t.me/BotFather))
#### Run the script:
```python3  watch_script.py```

 On the first run the script will ask for your tgtg email address to get the needed API keys, and it will ask you to authorize your Telegram account by sending 6 digit pin to the bot.

### Azure Linux VM
- create a Virtual Machine, Image "Ubuntu 18.04 Linux LTS with Docker - x64 Gen1"

with docker (make sure to rebuild after changing config.json):
- sudo docker build -t tgtg_notifier .
- sudo docker run -e PYTHONUNBUFFERED=1 tgtg_notifier

later to attach to running container and view logs:
- docker container logs CONTAINER -f

alternative:
- sudo apt install python-pip
- sudo add-apt-repository ppa:deadsnakes/ppa
- sudo apt-get update
- sudo apt-get install python3.8
- python3.8 -m pip install -r requirements.txt
- python3.8 watch_script.py