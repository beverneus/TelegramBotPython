from config import BOT_TOKEN
import logging
import telegram
from telegram.ext import CommandHandler, Updater, CallbackContext
import time
import requests
DELAY = 6  # Hours
# Token is located in config.py

repeater = None
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher
job_queue = updater.job_queue

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - , %(message)s",
    level=logging.INFO)

# Define Functions

# Imports the bitcoin price from the coincap api


def getBitcoinPrice():
    response = requests.get('https://api.coincap.io/v2/assets/bitcoin/')
    response_json = response.json()
    # Convert the price to a floating point number
    return float(response_json['data']['priceUsd'])

# Message when the bot gets added


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="type /loop to start or /price to see the"
                             " current Bitcoin price")


# Make a new job to repeat bPrice every DELAY hours
def repeat(update, context: CallbackContext):
    global repeater
    try:
        if repeater.enabled is False:
            repeater.enabled = True
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text='Starting Bitcoin Price Alert, '
                                     'use /pause or /stop to pause or stop')
        elif repeater.enabled is True:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text='Bitcoin Price is already running!')
    except AttributeError:
        repeater = job_queue.run_repeating(PriceLoop, interval=DELAY*60*60,
                                           first=0,
                                           context=update.message.chat_id)
        print("Started")
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text='Starting Bitcoin Price Alert, '
                                      'use /pause to pause or \n/price to get'
                                      'the current price')


def pause(update: telegram.Update, context):
    repeater.enabled = False
    context.bot.send_message(chat_id=update.message.chat_id,
                             text='Paused Bitcoin Price, '
                                  'use /loop to start again')
    print("pause")


def TimePrice():
    price = round(getBitcoinPrice(), 2)
    timedate = time.strftime('[%H:%M/%d.%m.%Y]')
    return f"{timedate} : ${price}"
# Sends price every DELAY seconds


def PriceLoop(context):
    context.bot.send_message(chat_id=context.job.context,
                             text=TimePrice())


def price(context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=TimePrice())


# Define command handelers and add them to dispatcher
start_handeler = CommandHandler("start", start)
dispatcher.add_handler(start_handeler)
loop_handeler = CommandHandler("loop", repeat)
dispatcher.add_handler(loop_handeler)
pause_handeler = CommandHandler("pause", pause)
dispatcher.add_handler(pause_handeler)
price_handeler = CommandHandler("price", price)
dispatcher.add_handler(price_handeler)


# Start listening to commands
updater.start_polling()
