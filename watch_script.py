from tgtg import TgtgClient
from json import load
import requests
import schedule
import time
import os
import traceback
import json
import maya
import datetime
import inspect
from urllib.parse import quote
import random
import string

try:
    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.dirname(os.path.abspath(filename))
    # Load credentials from a file
    f = open(os.path.join(path, 'config.json'), mode='r+')
    config = load(f)
except FileNotFoundError:
    print("No files found for local credentials.")
    exit(1)
except:
    print("Unexpected error")
    print(traceback.format_exc())
    exit(1)

try:
    # Create the tgtg client with my credentials
    tgtg_client = TgtgClient(access_token=config['tgtg']['access_token'], refresh_token=config['tgtg']
                             ['refresh_token'], user_id=config['tgtg']['user_id'], cookie=config['tgtg']['cookie'])
except KeyError:
    # print(f"Failed to obtain TGTG credentials.\nRun \"python3 {sys.argv[0]} <your_email>\" to generate TGTG credentials.")
    # exit(1)
    try:
        email = input("Type your TooGoodToGo email address: ")
        client = TgtgClient(email=email)
        tgtg_creds = client.get_credentials()
        print(tgtg_creds)
        config['tgtg'] = tgtg_creds
        f.seek(0)
        json.dump(config, f, indent=4)
        f.truncate()
        tgtg_client = TgtgClient(access_token=config['tgtg']['access_token'], refresh_token=config['tgtg']
                                 ['refresh_token'], user_id=config['tgtg']['user_id'], cookie=config['tgtg']['cookie'])
    except:
        print(traceback.format_exc())
        exit(1)
except:
    print("Unexpected error")
    print(traceback.format_exc())
    exit(1)
try:
    bot_token = config['telegram']["bot_token"]
    if bot_token == "BOTTOKEN":
        raise KeyError
except KeyError:
    print(f"Failed to obtain Telegram bot token.\n Put it into config.json.")
    exit(1)
except:
    print(traceback.format_exc())
    exit(1)

try:
    bot_chatIDs = list(config['telegram']["bot_chatIDs"])
    if bot_chatIDs == []:
        # Get chat ID
        pin = ''.join(random.choice(string.digits) for x in range(6))
        print("Please type \"" + pin + "\" to the bot.")
        while bot_chatIDs == []:
            response = requests.get(
                'https://api.telegram.org/bot' + bot_token + '/getUpdates?limit=1&offset=-1')
            # print(response.json())
            if (response.json()['result'][0]['message']['text'] == pin):
                chatId = str(
                    response.json()['result'][0]['message']['chat']['id'])
                print("Your chat id:" + chatId)
                bot_chatIDs = [chatId]
                config['telegram']['bot_chatIDs'] = [chatId]
                f.seek(0)
                json.dump(config, f, indent=4)
                f.truncate()
            time.sleep(1)
except KeyError:
    print(f"Failed to obtain Telegram chat ID.")
    exit(1)
except:
    print(traceback.format_exc())
    exit(1)

try:
    f.close()
except:
    print(traceback.format_exc())
    exit(1)

# Init the favourites in stock list as a global variable
tgtg_in_stock = list()


def telegram_bot_sendtext(bot_message, only_to_admin=True):
    """
    Helper function: Send a message with the specified telegram bot.
    It can be specified if both users or only the admin receives the message
    Follow this article to figure out a specific chatID: https://medium.com/@ManHay_Hong/how-to-create-a-telegram-bot-and-send-messages-with-python-4cf314d9fa3e
    """
    if only_to_admin is True:
        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + \
            bot_chatIDs[0] + '&parse_mode=Markdown&text=' + quote(bot_message)
        response = requests.get(send_text)
    else:
        for chatId in bot_chatIDs:
            send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + \
                chatId + '&parse_mode=Markdown&text=' + quote(bot_message)
            response = requests.get(send_text)

    return response.json()


def telegram_bot_sendimage(image_url, image_caption=None, button_links=None):
    """
    For sending an image in Telegram, that can also be accompanied by an image caption
    """
    # Prepare the url for an telegram API call to send a photo

    for chatId in bot_chatIDs:
        send_text = 'https://api.telegram.org/bot' + bot_token + \
        '/sendPhoto?chat_id=' + chatId + '&photo=' + image_url

        if button_links != None:
            button_links_text = '{"inline_keyboard":[['
            for item in button_links:
                button_links_text += '{"text":"' + \
                    item['text'] + '","url":"' + item['url'] + '"}'
            button_links_text += ']]}'
            send_text += '&reply_markup=' + quote(button_links_text)

        # If the argument gets passed, at a caption to the image
        if image_caption != None:
            send_text += '&parse_mode=Markdown&caption=' + quote(image_caption)

        response = requests.get(send_text)

    return response.json()


def telegram_bot_delete_message(message_id):
    """
    For deleting a Telegram message
    """
    for chatId in bot_chatIDs:
        send_text = 'https://api.telegram.org/bot' + bot_token + \
            '/deleteMessage?chat_id=' + chatId + \
            '&message_id=' + str(message_id)
        response = requests.get(send_text)
    return response.json()


def parse_tgtg_api(api_result):
    """
    For fideling out the few important information out of the api response
    """
    result = list()
    # Go through all stores, that are returned with the api
    for store in api_result:
        current_item = dict()
        current_item['id'] = store['item']['item_id']
        current_item['store_name'] = store['store']['store_name']
        current_item['items_available'] = store['items_available']
        if current_item['items_available'] == 0:
            result.append(current_item)
            continue
        current_item['description'] = store['item']['description']
        current_item['category_picture'] = store['item']['cover_picture']['current_url']
        current_item['price_including_taxes'] = str(store['item']['price_including_taxes']['minor_units'])[:-(store['item']['price_including_taxes']['decimals'])] + "." + str(
            store['item']['price_including_taxes']['minor_units'])[-(store['item']['price_including_taxes']['decimals']):]+store['item']['price_including_taxes']['code']
        current_item['value_including_taxes'] = str(store['item']['value_including_taxes']['minor_units'])[:-(store['item']['value_including_taxes']['decimals'])] + "." + str(
            store['item']['value_including_taxes']['minor_units'])[-(store['item']['value_including_taxes']['decimals']):]+store['item']['value_including_taxes']['code']

        # added metdata
        current_item['store_branch'] = store['store']['branch']
        current_item['store'] = store['store']

        try:
            localPickupStart = datetime.datetime.strptime(
                store['pickup_interval']['start'], '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=datetime.timezone.utc).astimezone()
            localPickupEnd = datetime.datetime.strptime(
                store['pickup_interval']['end'], '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=datetime.timezone.utc).astimezone()
            current_item['pickup_start'] = maya.parse(localPickupStart).slang_date(locale="de"
            ).capitalize() + " " + localPickupStart.strftime('%H:%M')
            current_item['pickup_end'] = maya.parse(localPickupEnd).slang_date(locale="de"
            ).capitalize() + " " + localPickupEnd.strftime('%H:%M')
        except KeyError:
            current_item['pickup_start'] = None
            current_item['pickup_end'] = None
        try:
            current_item['rating'] = round(
                store['item']['average_overall_rating']['average_overall_rating'], 2)
        except KeyError:
            current_item['rating'] = None
        result.append(current_item)
    return result


def toogoodtogo():
    """
    Retrieves the data from tgtg API and selects the message to send.
    """

    # Get the global variable of items in stock
    global tgtg_in_stock

    # Get all favorite items
    # api_response = tgtg_client.get_items(
    #     favorites_only=True,
    #     latitude=config['location']['lat'],
    #     longitude=config['location']['long'],
    #     radius=config['location']['range'],
    #     page_size=300
    # )
    api_response = tgtg_client.get_items()

    parsed_api = parse_tgtg_api(api_response)

    # Go through all favourite items and compare the stock
    for item in parsed_api:
        try:
            old_stock = [stock['items_available']
                         for stock in tgtg_in_stock if stock['id'] == item['id']][0]
        except IndexError:
            old_stock = 0
        try:
            item['msg_id'] = [stock['msg_id']
                              for stock in tgtg_in_stock if stock['id'] == item['id']][0]
        except:
            pass

        new_stock = item['items_available']

        # Check, if the stock has changed. Send a message if so.
        if new_stock != old_stock:
            # Check if the stock was replenished, send an encouraging image message
            if old_stock == 0 and new_stock > 0:

                message = f"🍽 Es gibt {new_stock} neue Magic bags bei [{item['store_name']}](https://share.toogoodtogo.com/item/{item['id']}) in {item['store_branch']}\n\n"\
                    f"_{item['description']}_\n\n"\
                    # f"💰 *{item['price_including_taxes']}*/{item['value_including_taxes']}\n"
                message += f"💰 {item['price_including_taxes']}\n"
                if 'rating' in item:
                    message += f"⭐️ {item['rating']} / 5\n"
                if 'pickup_start' and 'pickup_end' in item:
                    # message += f"⏰ {item['pickup_start']} - {item['pickup_end']}\n"
                    message += f"⏰ {item['pickup_start']} - {item['pickup_end']}\n"
                message += f"📍  [{item['store']['store_location']['address']['address_line']}](https://maps.google.com/?q={item['store']['store_location']['location']['latitude']},{item['store']['store_location']['location']['longitude']})\n"
                # message += f"ℹ️ [Jetzt reservieren](https://share.toogoodtogo.com/item/{item['id']})"

                button_links = [
                    {
                        "text": "Jetzt reservieren",
                        "url": f"https://share.toogoodtogo.com/item/{item['id']}"
                    }
                ]

                tg = telegram_bot_sendimage(
                    item['category_picture'], message, button_links)
                try:
                    item['msg_id'] = tg['result']['message_id']
                except:
                    print(json.dumps(tg))
                    print(item['category_picture'])
                    print(message)
                    print(traceback.format_exc())
            elif old_stock > new_stock and new_stock != 0:
                # customer feedback: This message is not needed
                pass
                # Prepare a generic string, but with the important info
                # message = f" 📉 Decrease from {old_stock} to {new_stock} available goodie bags at {[item['store_name'] for item in new_api_result if item['item_id'] == item_id][0]}."
                # telegram_bot_sendtext(message, False)
            elif old_stock > new_stock and new_stock == 0:
                # message = f" ⭕ Sold out! There are no more goodie bags available at {item['store_name']}."
                # telegram_bot_sendtext(message, False)
                try:
                    tg = telegram_bot_delete_message(
                        [stock['msg_id'] for stock in tgtg_in_stock if stock['id'] == item['id']][0])
                except:
                    print(
                        f"Failed to remove message for item id: {item['id']}")
                    print(traceback.format_exc())
            else:
                # Prepare a generic string, but with the important info
                message = f"Die Anzahl der vorrätigen Magic Bags änderte sich von {old_stock} auf {new_stock} bei [{item['store_name']}](https://share.toogoodtogo.com/item/{item['id']})."
                telegram_bot_sendtext(message, False)

    # Reset the global information with the newest fetch
    tgtg_in_stock = parsed_api

    # Print out some maintenance info in the terminal
    print(f"TGTG: API run at {time.ctime(time.time())} successful.")
    # for item in parsed_api:
    #     print(f"{item['store_name']}({item['id']}): {item['items_available']}")


def still_alive():
    """
    This function gets called every 24 hours and sends a 'still alive' message to the admin.
    """
    message = f"Current time: {time.ctime(time.time())}. The bot is still running. "
    telegram_bot_sendtext(message)


def refresh():
    """
    Function that gets called via schedule every 1 minute.
    Retrieves the data from services APIs and selects the messages to send.
    """
    try:
        toogoodtogo()
    except:
        print(traceback.format_exc())
        telegram_bot_sendtext("Error occured: \n```" +
                              str(traceback.format_exc()) + "```")


# Use schedule to set up a recurrent checking
schedule.every(1).minutes.do(refresh)
schedule.every(24).hours.do(still_alive)

# Description of the service, that gets send once
telegram_bot_sendtext("The bot script has started successfully. The bot checks every 1 minute, if there is something new at TooGoodToGo. Every 24 hours, the bots sends a \"still alive\" message.")
refresh()
while True:
    # run_pending
    schedule.run_pending()
    time.sleep(1)
