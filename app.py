from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types, executor
import asyncio
import json
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
import logging

app = Flask(__name__)

# Настройки
TELEGRAM_TOKEN = '7179465730:AAEFcAad5AG0HWGTlCJ0e3fv0G6ZL-cQ3AA'
CHAT_IDS_FILE = 'chat_ids.json'

# Настройки бота
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# Настройки логирования
logging.basicConfig(level=logging.INFO)

# Настройки планировщика
scheduler = BackgroundScheduler()
scheduler.add_executor(ThreadPoolExecutor(10))
scheduler.start()

def load_chat_ids():
    try:
        if os.path.exists(CHAT_IDS_FILE) and os.path.getsize(CHAT_IDS_FILE) > 0:
            with open(CHAT_IDS_FILE, 'r') as f:
                return json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from {CHAT_IDS_FILE}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error while loading chat IDs: {e}")
    return []

def save_chat_ids(chat_ids):
    try:
        with open(CHAT_IDS_FILE, 'w') as f:
            json.dump(chat_ids, f)
    except Exception as e:
        logging.error(f"Unexpected error while saving chat IDs: {e}")

def format_message(data):
    alert_id = data.get('name', 'N/A')
    side = data.get('side', 'N/A').capitalize()
    continuation = data.get('continuation', 'N/A')
    base = data.get('base', 'N/A')
    
    markets = data.get('markets', [])
    if markets:
        market = markets[0]
        exchange = market.get('exchange', 'N/A')
        symbol = market.get('symbol', 'N/A')
        price = market.get('price', 'N/A')
    else:
        exchange = 'N/A'
        symbol = 'N/A'
        price = 'N/A'

    formatted_message = (
        f"**Alert ID:** {alert_id}\n"
        f"**Side:** {side} 🟢\n"
        f"**Continuation:** {continuation} minutes\n\n"
        f"**Market Information:**\n"
        f"   *Base:* {base}\n"
        f"   *Symbol:* {symbol}\n"
        f"   *Exchange:* {exchange}\n"
        f"   *Price:* {price}\n\n"
        f"{data.get('message', 'No additional message')}"
    )
    return formatted_message

async def send_message(chat_id, message):
    try:
        await bot.send_message(chat_id, message, parse_mode=types.ParseMode.MARKDOWN)
    except Exception as e:
        logging.error(f"Error sending message to chat {chat_id}: {e}")

async def async_update_chat_ids():
    try:
        updates = await bot.get_updates()
        chat_ids = load_chat_ids()
        new_chat_ids = set()
        
        for update in updates:
            if update.message and update.message.chat:
                chat_id = update.message.chat.id
                chat_type = update.message.chat.type
                if chat_id not in chat_ids and chat_type in ['group', 'supergroup']:
                    new_chat_ids.add(chat_id)
                    chat_ids.append(chat_id)
        
        if new_chat_ids:
            save_chat_ids(chat_ids)
    except Exception as e:
        logging.error(f"Error updating chat IDs: {e}")

def update_chat_ids():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_update_chat_ids())

@app.route('/', methods=['POST'])
async def webhook():
    data = await request.json
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    message = format_message(data)
    chat_ids = load_chat_ids()

    for chat_id in chat_ids:
        await send_message(chat_id, message)
    
    return jsonify({'status': 'success'}), 200

# Настроить обновление списка чатов каждую минуту
scheduler.add_job(update_chat_ids, 'interval', minutes=1)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
