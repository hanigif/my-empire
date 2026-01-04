import os
import logging
import asyncio
from datetime import datetime
import pytz
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq

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
    أنت 'المدير السيادي'. هدفه تطوير المنتج.
    توقيت السويد: {get_sweden_time()}
    """
    try:
        response = llm.invoke([("system", system_prompt), ("human", user_input)])
        return response.content
    except Exception as e:
        return f"خطأ: {str(e)}"

# معالجات التلغرام
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("النواة السيادية استقرت تماماً. أنا جاهز.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    decision = await sovereign_logic_engine(update.message.text)
    await update.message.reply_text(decision)

@app.route('/')
def home():
    return f"Sovereign Core Active. Sweden Time: {get_sweden_time()}"

# --- المحرك المدمج (The Unified Engine) ---
async def main():
    token = os.getenv("TELEGRAM_TOKEN")
    
    # بناء تطبيق التلغرام
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # تشغيل Flask بشكل غير متزامن داخل نفس الـ Loop
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config.bind = [f"0.0.0.0:{os.environ.get('PORT', '10000')}"]

    logger.info("Starting Unified Sovereign Engine...")
    
    # تشغيل البوت والسيرفر معاً
    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)
        
        # تشغيل سيرفر الويب
        await serve(app, config)
        
        await application.updater.stop()
        await application.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
