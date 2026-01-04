import os
import logging
import threading
import asyncio
from datetime import datetime
import pytz
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq

# إعداد اللوغز
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# توقيت السويد
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

app = Flask(__name__)

# إعداد محرك الذكاء الاصطناعي
llm = ChatGroq(
    temperature=0.3,
    model_name="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

def get_sweden_time():
    return datetime.now(SWEDEN_TZ).strftime('%Y-%m-%d %H:%M:%S')

# --- منطق الاستجابة ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    system_prompt = f"""
    أنت 'المدير السيادي'. هدفه بناء وتطوير منتجه الخاص للوصول للقمة.
    توقيت السويد الحالي: {get_sweden_time()}
    أجب بوضوح واحترافية كمدير استراتيجي.
    """
    try:
        response = llm.invoke([("system", system_prompt), ("human", user_text)])
        await update.message.reply_text(response.content)
    except Exception as e:
        logger.error(f"Error in LLM: {e}")
        await update.message.reply_text("عذراً، واجهت مشكلة في معالجة الطلب.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"مرحباً بك يا مدير. النواة السيادية تعمل بنجاح.\nالتوقيت: {get_sweden_time()}")

# --- تشغيل البوت ---
def run_telegram_bot():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("No TELEGRAM_TOKEN found!")
        return

    # إنشاء تطبيق التلغرام
    application = Application.builder().token(token).build()

    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting bot polling...")
    # تشغيل البولينج
    application.run_polling(drop_pending_updates=True)

# --- مسارات Flask ---
@app.route('/')
def index():
    return f"Sovereign Manager is Online. Sweden Time: {get_sweden_time()}"

@app.route('/health')
def health():
    return "OK", 200

if __name__ == "__main__":
    # تشغيل التلغرام في خيط منفصل (Thread) لضمان عدم توقف Flask
    threading.Thread(target=run_telegram_bot, daemon=True).start()
    
    # تشغيل Flask على المنفذ المطلوب
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
