import os, threading, asyncio, logging, time, requests
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import yfinance as yf

# إعداد السجلات لمتابعة حالة الاستيقاظ
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = "6758877303"
# ضع هنا رابط موقعك الذي حصلت عليه من Render
MY_URL = "https://your-app-name.onrender.com" 

app = Flask(__name__)

@app.route('/')
def home(): return "Empire OS: STATUS ACTIVE 24/7"

# وظيفة النبض الذاتي (تنبيه السيرفر كل 5 دقائق)
def keep_alive():
    while True:
        try:
            requests.get(MY_URL)
            logging.info("Pulse Sent: Empire OS is Awake.")
        except:
            logging.error("Pulse Failed: Website might be down.")
        time.sleep(300) # 300 ثانية = 5 دقائق

def get_multi_stock_data(text):
    data_str = ""
    stocks = {"MSFT": "Microsoft", "TSLA": "Tesla", "AMZN": "Amazon"}
    for ticker, name in stocks.items():
        try:
            stock = yf.Ticker(ticker)
            info = stock.fast_info
            data_str += f"\n- {name} ({ticker}): ${info['last_price']:.2f}"
        except: continue
    return data_str

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update or not update.message or not update.message.text: return
    if str(update.effective_user.id) != MY_ID: return

    user_text = update.message.text
    live_data = get_multi_stock_data(user_text)
    
    try:
        llm = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
        system_prompt = f"أنت نظام Empire OS. حلل هذه الشركات بناءً على البيانات: {live_data}. اختر الأفضل مالياً وأمنياً."
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_text)])
        await update.message.reply_text(response.content)
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطأ: {str(e)}")

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    # تشغيل البوت
    threading.Thread(target=run_bot, daemon=True).start()
    # تشغيل النبض الذاتي كل 5 دقائق
    threading.Thread(target=keep_alive, daemon=True).start()
    # تشغيل الموقع
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
