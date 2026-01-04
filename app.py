import os
import logging
import threading
from datetime import datetime
import pytz
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq

# 1. الإعدادات الأساسية
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

app = Flask(__name__)

# 2. إعداد المحرك الذهني (Groq)
GK_KEY = os.environ.get("GROQ_API_KEY")
llm = ChatGroq(
    temperature=0.3, 
    model_name="llama-3.3-70b-versatile", 
    groq_api_key=GK_KEY
)

def get_sweden_time():
    return datetime.now(SWEDEN_TZ).strftime('%Y-%m-%d %H:%M:%S')

# 3. معالج الرسائل (الذي تواصلت معه في تلغرام بنجاح)
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    
    user_text = update.message.text
    system_instruction = f"أنت المدير السيادي. الوقت الآن في السويد: {get_sweden_time()}. هدفك تطوير منتجك."
    
    try:
        response = llm.invoke([("system", system_instruction), ("human", user_text)])
        await update.message.reply_text(response.content)
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("عذراً مدير، هناك مشكلة في الربط.")

# 4. تشغيل التلغرام (polling)
def run_telegram_bot():
    # تأكد من وضع التوكن الخاص بك هنا أو في Environment Variables
    TOKEN = os.environ.get("TELEGRAM_TOKEN") 
    application = ApplicationBuilder().token(TOKEN).build()
    
    # إضافة المعالج
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    logger.info("Bot is starting...")
    application.run_polling(drop_pending_updates=True)

# 5. مسار Flask لإبقاء Render نشطاً
@app.route('/')
def home():
    return f"Sovereign Manager Active. Sweden Time: {get_sweden_time()}"

if __name__ == '__main__':
    # تشغيل البوت في خيط منفصل (هذا هو السر في بقاء التلغرام شغال)
    threading.Thread(target=run_telegram_bot, daemon=True).start()
    
    # تشغيل Flask
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
