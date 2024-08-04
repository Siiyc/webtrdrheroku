from flask import Flask, request, jsonify
from telegram import Bot
import aiohttp
import asyncio
import json

app = Flask(__name__)

# Ваш токен Telegram-бота и ID чата
TELEGRAM_TOKEN = '7179465730:AAEFcAad5AG0HWGTlCJ0e3fv0G6ZL-cQ3AA'
CHAT_ID = '427720816'

bot = Bot(token=TELEGRAM_TOKEN)

async def send_message_async(message):
    async with aiohttp.ClientSession() as session:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
        async with session.post(url, data=data) as response:
            return await response.text()

def format_message(data):
    # Извлечение данных из JSON
    alert_id = data.get('name', 'N/A')
    side = data.get('side', 'N/A').capitalize()
    continuation = data.get('continuation', 'N/A')
    base = data.get('base', 'N/A')
    
    # Обработка списка markets
    markets = data.get('markets', [])
    if markets:
        market = markets[0]  # Предполагаем, что интересует первый элемент
        exchange = market.get('exchange', 'N/A')
        symbol = market.get('symbol', 'N/A')
        price = market.get('price', 'N/A')
    else:
        exchange = 'N/A'
        symbol = 'N/A'
        price = 'N/A'

    # Создание форматированного сообщения
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

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    # Форматируем сообщение
    message = format_message(data)
    
    # Запускаем асинхронную функцию в синхронном контексте
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(send_message_async(message))
    loop.close()

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(debug=True)
