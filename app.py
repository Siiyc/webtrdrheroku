from flask import Flask, request, jsonify
from telegram import Bot
from telegram.ext import Application, CommandHandler, ContextTypes

app = Flask(__name__)

# Ваш токен Telegram-бота и ID чата
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
CHAT_ID = 'YOUR_CHAT_ID'

bot = Bot(token=TELEGRAM_TOKEN)

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    app.logger.info(f"Received webhook data: {data}")
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    # Обработка данных
    message = f"Received webhook data: {data}"
    
    # Используем асинхронный вызов
    async def send_message():
        await bot.send_message(chat_id=CHAT_ID, text=message)
    
    import asyncio
    asyncio.run(send_message())

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(debug=True)
