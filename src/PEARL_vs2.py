from dotenv import load_dotenv
from telegram import Update
import os
import requests
import json
from PIL import Image
from telegram.ext import CommandHandler, MessageHandler, Updater, ConversationHandler
from telegram.ext import Filters as filters
from telegram import Update, ForceReply

user_name = '@dsxservicosbot'
 
load_dotenv()
# Define the states for the conversation handler
MESSAGE, RESPONSE = range(2)

class TelegramBot():
    def __init__(self):
        TOKEN = os.getenv("API_KEY")
        self.url = f"https://api.telegram.org/bot{TOKEN}/"
        self.conv_handler = ConversationHandler(
            entry_points=[CommandHandler('send_message', self.send_message)],
            states={
                MESSAGE: [MessageHandler(filters.text, self.get_message)],
                RESPONSE: [MessageHandler(filters.text, self.send_response)]
            },
            fallbacks=[]
        )

    def start(self):
        print("Inicializando bot...")
        updater = Updater(token=os.getenv("API_KEY"), use_context=True)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(self.conv_handler)
        updater.start_polling()

    def send_message(self, update, context):
        context.user_data['chat_id'] = update.message.chat_id
        update.message.reply_text('Qual mensagem você deseja enviar?')
        return MESSAGE

    def get_message(self, update, context):
        context.user_data['message'] = update.message.text
        update.message.reply_text('Para qual chat você deseja enviar essa mensagem?')
        return RESPONSE

    def send_response(self, update, context):
        chat_id = context.user_data['chat_id']
        message = context.user_data['message']
        response = update.message.text
        sent_message = context.bot.send_message(chat_id=chat_id, text=message)
        context.user_data['sent_message_id'] = sent_message.message_id
        context.user_data['response_chat_id'] = update.message.chat_id
        update.message.reply_text('Mensagem enviada. Aguardando resposta...')
        return ConversationHandler.END

    def forward_response(self, update, context):
        response_chat_id = context.user_data['response_chat_id']
        sent_message_id = context.user_data['sent_message_id']
        response = update.message.text
        context.bot.send_message(chat_id=response_chat_id, text=response, reply_to_message_id=sent_message_id)