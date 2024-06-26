from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import google.generativeai as genai
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))
genai.configure(api_key = os.environ.get('API_KEY'))
model = genai.GenerativeModel('gemini-pro')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    gemini_response = get_gemini_response(message)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=gemini_response))

def get_gemini_response(user_message):
    response = model.generate_content(user_message)
    return response.text

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)