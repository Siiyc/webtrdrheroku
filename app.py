from flask import Flask, request, jsonify
from telegram import Bot

app = Flask(__name__)

# Ваш токен Telegram-бота и ID чата
TELEGRAM_TOKEN = '7179465730:AAEFcAad5AG0HWGTlCJ0e3fv0G6ZL-cQ3AA'
CHAT_ID = '427720816'

bot = Bot(token=TELEGRAM_TOKEN)

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400
    bot.send_message(chat_id=CHAT_ID, text="Test message")
    # Обработка данных
    message = f"Received webhook data: {data}"
    bot.send_message(chat_id=CHAT_ID, text=message)

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(debug=True)
