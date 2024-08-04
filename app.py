from flask import Flask, request, jsonify
from telegram import Bot
import aiohttp
import asyncio

app = Flask(__name__)

# Ваш токен Telegram-бота и ID чата
TELEGRAM_TOKEN = '7179465730:AAEFcAad5AG0HWGTlCJ0e3fv0G6ZL-cQ3AA'
CHAT_ID = '427720816'

bot = Bot(token=TELEGRAM_TOKEN)

async def send_message_async(message):
    async with aiohttp.ClientSession() as session:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {'chat_id': CHAT_ID, 'text': message}
        async with session.post(url, data=data) as response:
            return await response.text()

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    app.logger.info(f"Received webhook data: {data}")
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    # Обработка данных
    message = f"Received webhook data: {data}"
    
    # Запускаем асинхронную функцию в синхронном контексте
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(send_message_async(message))
    loop.close()

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(debug=True)
