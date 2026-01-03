import os
import threading
import asyncio
from flask import Flask
import yfinance as yf
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# إعدادات الهوية
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

app = Flask(__name__)

# إعداد الذكاء الاصطناعي
if GROQ_API_KEY:
    llm = ChatGroq(temperature=0.3, model_name="llama-3.3-70b-versatile", groq_api_key=GROQ_API_KEY)
else:
    llm = None

@app.route('/')
def index():
    return "<h1>Empire OS: Online & Secure</h1><p>المدير التنفيذي قيد العمل في الخلفية...</p>"

@app.route('/health')
def health():
    return "OK", 200

# منطق البوت
async def process_ai_response(user_input):
    if not llm: return "المفتاح مفقود!"
    messages = [SystemMessage(content="أنت المدير التنفيذي لـ Empire OS. رد بالعربية."), HumanMessage(content=user_input)]
    return llm.invoke(messages).content

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        answer = await process_ai_response(update.message.text)
        await update.message.reply_text(answer)

def run_telegram_bot():
    if not TELEGRAM_TOKEN: return
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app_bot.run_polling(drop_pending_updates=True)

# التشغيل الذكي
if __name__ == '__main__':
    # تشغيل البوت أولاً في خيط مستقل
    threading.Thread(target=run_telegram_bot, daemon=True).start()
    
    # تشغيل Flask مع تحديد البورت بدقة لـ Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
