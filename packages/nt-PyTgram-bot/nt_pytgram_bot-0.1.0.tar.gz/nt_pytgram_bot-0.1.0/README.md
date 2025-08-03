# PyTgram_bot

# Updater -- telegram serviriga borib bir qancha updateni olib keladi qisqa qilib aytganda oxirgi updatelarni olib keladi

# Dispatcher -- updater ustida amal bajaradi

# Handler -- xabar kelsa hal qilish 

# Types - Message, MyChatMember

# nt_PyTgram_bot 

`nt_PyTgram_bot` — bu `python-telegram-bot` kutubxonasi asosida Telegram botlar yaratishni soddalashtirish uchun yozilgan modul.

## Xususiyatlar

- Telegram API bilan oddiy interfeys
- Botga xabarlar va komandalarni yozish oson
- Moslashtirilgan `Updater`, `Handler` funksiyalari

## O'rnatish

```bash
pip install nt_PyTgram_bot

##  Foydalanish misoli

```python
from PyTgram_bot.updater import Updater
from PyTgram_bot.handler import MessageHandler
from PyTgram_bot.message_types import Update
import requests
from config import TOKEN

def handle_message(update: Update):
    chat_id = update.message['from']['id']
    text = update.message['text']

    requests.get(
        url=f'https://api.telegram.org/bot{TOKEN}/sendMessage',
        params={
            'chat_id': chat_id,
            'text': f"Siz yubordingiz: {text}"
        }
    )

updater = Updater(TOKEN)
updater.dispatcher.add_handler(MessageHandler(handle_message))
updater.start_polling()



