import logging
from flask import Flask, request, jsonify
from telegram import Bot
import aiohttp
import asyncio
import json

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Ваш токен Telegram-бота и ID чата
TELEGRAM_TOKEN = '7179465730:AAEFcAad5AG0HWGTlCJ0e3fv0G6ZL-cQ3AA'
CHAT_ID = '427720816'

bot = Bot(token=TELEGRAM_TOKEN)

async def send_message_async(message, file_path=None):
    async with aiohttp.ClientSession() as session:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
        data = {'chat_id': CHAT_ID, 'caption': message, 'parse_mode': 'Markdown'}
        files = {'document': open(file_path, 'rb')} if file_path else None
        async with session.post(url, data=data, files=files) as response:
            return await response.text()

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

    custom_message = data.get('message', 'No additional message')

    formatted_message = (
        f"**Alert ID:** {alert_id}\n"
        f"**Side:** {side}\n"
        f"**Continuation:** {continuation} minutes\n\n"
        f"**Market Information:**\n"
        f"   *Base:* {base}\n"
        f"   *Symbol:* {symbol}\n"
        f"   *Exchange:* {exchange}\n"
        f"   *Price:* {price}\n\n"
        f"**Custom Message:** {custom_message}"
    )
    return formatted_message

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    # Логируем полученные данные
    logging.info(f"Received JSON data: {json.dumps(data, indent=4)}")

    message = format_message(data)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Запись данных во временный файл
    with open('received_data.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

    result = loop.run_until_complete(send_message_async(message, 'received_data.json'))
    loop.close()

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(debug=True)
