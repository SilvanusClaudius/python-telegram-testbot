#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import random
import csv
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

import logging
import mysql.connector

#Connecting to database
mydb = mysql.connector.connect(
	host = "localhost",
	user = "USER",
	passwd ="PASSWORD",
	database ="allquestions"
	)

cursor = mydb.cursor()
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSETOPIC, MATERIALS, THERMO, OTHERS, ROUTE, NAMETHATFEATURE = range(6)

randnum = random.randint(1,26)	
state = 0
chosen_question = []

def start(bot, update):

    reply_keyboard = [['Thermodynamics', 'NameThatFeature', 'Others']]
    update.message.reply_text(
        'Hi! My name is Jen Yang Bot. I am a bona fide professor! Select a topic to start. '
        'Type in anything to start. A random question will appear.' 
        'I am not programmed to check for answers, so I will just respond to whatever you type in. Send /cancel to stop talking to me.\n\n'
        'Let us GOOO!',)
    update.message.reply_photo(photo='https://telegram.org/img/t_logo.png',
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    

    return CHOOSETOPIC

def topic(bot, update):
    if update.message.text == 'NameThatFeature':
        global state
        state = 1
        update.message.reply_text('You have chosen NameThatFeature', reply_markup=ReplyKeyboardRemove())
        #update.message.reply_photo(photo='https://upload.wikimedia.org/wikipedia/commons/a/af/Tux.png')
        cursor.execute("SELECT * FROM namethatfeature ORDER BY RAND() LIMIT 1")
        global chosen_question
        chosen_question = cursor.fetchone()
        update.message.reply_text('You have chosen question ' + str(chosen_question[0]))
        if str(chosen_question[1]) != 'NA':
            update.message.reply_photo(photo=str(chosen_question[1]))
        update.message.reply_text(str(chosen_question[2]))
        return ROUTE
        
    elif update.message.text == 'Thermodynamics':
        update.message.reply_text('You have chosen Thermo. Question bank is still being created. Name That Feature is currently the only fully functional section. Send /end to stop talking', reply_markup=ReplyKeyboardRemove())
        return THERMO
    else:
        update.message.reply_text('You have chosen something else. No questions yet. Please choose Name That Feature next time. Send /end to stop talking', reply_markup=ReplyKeyboardRemove())
        return OTHERS

def router(bot,update):
    if state == 1:
        update.message.reply_text('The answer is: ' + str(chosen_question[3]))
        if str(chosen_question[4]) != 'NA':
            update.message.reply_photo(photo=str(chosen_question[4]))
        update.message.reply_text('Type in anything for the next question. Send /end to stop talking. Next question...')
        return NAMETHATFEATURE 
    else:
        return ConversationHandler.END
        
def name_that_feature(bot,update):
    cursor.execute("SELECT * FROM namethatfeature ORDER BY RAND() LIMIT 1")
    global chosen_question
    chosen_question = cursor.fetchone()
    update.message.reply_text('You have chosen question ' + str(chosen_question[0]))
    if str(chosen_question[1]) != 'NA':
        update.message.reply_photo(photo=str(chosen_question[1]))
    update.message.reply_text(str(chosen_question[2]))
    return ROUTE
    
def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! Why would you cancel on me I have no idea. I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("TOKEN")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
	
    # Add conversation handler with the states GENDER, PHOTO, LOCATION
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSETOPIC: [MessageHandler(Filters.regex('^(NameThatFeature|Thermodynamics|Others)$'), topic), CommandHandler('end', cancel)],
            ROUTE:[MessageHandler(Filters.text, router), CommandHandler('end', cancel)],
            THERMO:[CommandHandler('end', cancel)],
            NAMETHATFEATURE:[MessageHandler(Filters.text, name_that_feature), CommandHandler('end', cancel)],
            OTHERS:[CommandHandler('end', cancel)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling(poll_interval = 1.0)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()