# import all modules
from config import BOT_TOKEN
import logging
import telegram
from telegram.ext import CommandHandler, Updater, CallbackContext
import time
import requests
DELAY = 6  # Hours
# Token is located in config.py


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
                             text="Thank you for purchasing my bot,"
                             " type '/price' to start")

# Sends price every DELAY seconds


def bPrice(context: CallbackContext):
    price = round(getBitcoinPrice(), 2)
    timedate = time.strftime('[%H:%M/%d.%m.%Y]')
    context.bot.send_message(chat_id=context.job.context,
                             text=f"{timedate} : {price}")


def repeat(update: telegram.Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text='Starting Bitcoin Price Alert')
    repeater = job_queue.run_repeating(bPrice, interval=10, first=0,
                                       context=update.message.chat_id)


# Define command handelers and add them to dispatcher
start_handeler = CommandHandler("start", start)
dispatcher.add_handler(start_handeler)
loop_handeler = CommandHandler("price", repeat)
dispatcher.add_handler(loop_handeler)

# Start listening to commands
updater.start_polling()
