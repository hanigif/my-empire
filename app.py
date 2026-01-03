import os, threading, asyncio, logging, time, requests
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import yfinance as yf

# 1. إعدادات السجلات
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = "6758877303"

app = Flask(__name__)

@app.route('/')
def home():
    return "Empire OS Core v3.1: Stable & Connected"

# 2. وظيفة جلب بيانات السوق
def get_market_data(text):
    stocks_map = {
        "NVDA": "NVIDIA", "AAPL": "Apple", "MSFT": "Microsoft", 
        "TSLA": "Tesla", "AMZN": "Amazon", "GOOGL": "Google"
    }
    extracted_data = ""
    for ticker, name in stocks_map.items():
        if ticker in text.upper() or name.upper() in text.upper():
            try:
                stock = yf.Ticker(ticker)
                info = stock.fast_info
                price = info['last_price']
                extracted_data += f"\n- {name} ({ticker}): ${price:.2f}"
            except: continue
    return extracted_data

# 3. معالج الرسائل
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    if str(update.effective_user.id) != MY_ID: return

    user_query = update.message.text
    live_market_info = get_market_data(user_query)

    try:
        llm = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
        system_instructions = f"أنت Empire OS. حلل مالياً وتقنياً بناءً على: {live_market_info}"
        response = llm.invoke([SystemMessage(content=system_instructions), HumanMessage(content=user_query)])
        await update.message.reply_text(response.content)
    except Exception as e:
        logging.error(f"Error: {e}")

# 4. وظيفة النبض الذاتي
def keep_alive_pulse():
    time.sleep(30)
    while True:
        logging.info("Pulse: Empire OS is Alive.")
        time.sleep(300)

# 5. تشغيل Flask في خيط منفصل
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, use_reloader=False)

if __name__ == '__main__':
    # تشغيل Flask في الخلفية
    threading.Thread(target=run_flask, daemon=True).start()
    
    # تشغيل النبض في الخلفية
    threading.Thread(target=keep_alive_pulse, daemon=True).start()
    
    # تشغيل تلغرام في الخيط الرئيسي (Main Thread) لحل المشكلة
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    logging.info("Starting Empire OS Telegram Bot...")
    application.run_polling(drop_pending_updates=True)
