import os
import logging
import asyncio
from datetime import datetime
import pytz
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
import threading

# إعدادات التوقيت واللوغز
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

app = Flask(__name__)

# المحرك الذهني للمنتج (Groq AI)
llm = ChatGroq(
    temperature=0.2,
    model_name="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

def get_sweden_time():
    return datetime.now(SWEDEN_TZ).strftime('%Y-%m-%d %H:%M:%S')

async def sovereign_logic_engine(user_input):
    system_prompt = f"""
    أنت 'المدير السيادي'. 
    هدفك: بناء وتطوير منتج 'المدير السيادي' ككيان ذكي.
    الوقت في السويد: {get_sweden_time()}
    """
    try:
        response = llm.invoke([("system", system_prompt), ("human", user_input)])
        return response.content
    except Exception as e:
        return f"خطأ: {str(e)}"

# معالجات التلغرام
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("النواة السيادية نشطة. بانتظار أوامرك يا مدير.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    decision = await sovereign_logic_engine(update.message.text)
    await update.message.reply_text(decision)

# دالة تشغيل البوت (النسخة المستقرة)
def run_telegram_bot():
    token = os.getenv("TELEGRAM_TOKEN")
    # إنشاء حلقة أحداث جديدة لهذا الخيط (Thread)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Starting Telegram Bot Polling...")
    # استخدام run_polling الذي يتعامل مع الحلقة داخلياً بشكل أفضل
    application.run_polling(drop_pending_updates=True)

@app.route('/')
def home():
    return f"Sovereign Core Active. Sweden Time: {get_sweden_time()}"

if __name__ == "__main__":
    # تشغيل البوت في خيط منفصل (Background Thread)
    # هذا يضمن أن Flask لا يعطل البوت والعكس صحيح
    bot_thread = threading.Thread(target=run_telegram_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # تشغيل Flask على الخيط الرئيسي
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
