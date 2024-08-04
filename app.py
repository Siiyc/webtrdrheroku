from flask import Flask, request, jsonify
from telegram import Bot
import aiohttp
import asyncio
import json
import os
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

TELEGRAM_TOKEN = '7179465730:AAEFcAad5AG0HWGTlCJ0e3fv0G6ZL-cQ3AA'
CHAT_IDS_FILE = 'chat_ids.json'

bot = Bot(token=TELEGRAM_TOKEN)

scheduler = BackgroundScheduler()
scheduler.start()

# Функция для загрузки ID чатов из файла
def load_chat_ids():
    if os.path.exists(CHAT_IDS_FILE):
        with open(CHAT_IDS_FILE, 'r') as f:
            return json.load(f)
    return []

# Функция для сохранения ID чатов в файл
def save_chat_ids(chat_ids):
    with open(CHAT_IDS_FILE, 'w') as f:
        json.dump(chat_ids, f)

# Функция для отправки сообщений
async def send_message_async(chat_id, message):
    async with aiohttp.ClientSession() as session:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}
        async with session.post(url, data=data) as response:
            return await response.text()

# Форматирование сообщения
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
        f"**Side:** {side}\n"
        f"**Continuation:** {continuation} minutes\n\n"
        f"**Market Information:**\n"
        f"   *Base:* {base}\n"
        f"   *Symbol:* {symbol}\n"
        f"   *Exchange:* {exchange}\n"
        f"   *Price:* {price}\n\n"
        f"{data.get('message', 'No additional message')}"
    )
    return formatted_message

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    message = format_message(data)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    chat_ids = load_chat_ids()
    results = []
    for chat_id in chat_ids:
        result = loop.run_until_complete(send_message_async(chat_id, message))
        results.append(result)
    
    loop.close()

    return jsonify({'status': 'success', 'results': results}), 200

def update_chat_ids():
    updates = bot.get_updates()
    chat_ids = load_chat_ids()
    new_chat_ids = set()
    
    for update in updates:
        if update.message and update.message.chat:
            chat_id = update.message.chat_id
            chat_type = update.message.chat.type
            if chat_id not in chat_ids and chat_type in ['group', 'supergroup']:
                new_chat_ids.add(chat_id)
                chat_ids.append(chat_id)
    
    if new_chat_ids:
        save_chat_ids(chat_ids)

# Запуск функции обновления чатов каждую минуту
scheduler.add_job(update_chat_ids, 'interval', minutes=1)

if __name__ == '__main__':
    app.run(debug=True)
