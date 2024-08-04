from flask import Flask, request, jsonify
import os
import logging
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.json
        # Обработка полученных данныхgit
        logger.info('Received webhook data: %s', data)
        print(data)  # Вывод данных в консоль
        return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
