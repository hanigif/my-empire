import os
import logging
import asyncio
from datetime import datetime
import pytz
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq

# --- الإعدادات الأساسية (The Foundation) ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# توقيت السويد الرسمي
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

app = Flask(__name__)

# إعداد الذكاء الاصطناعي (The Sovereign Brain)
llm = ChatGroq(
    temperature=0.3,
    model_name="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# --- منطق المدير السيادي (Sovereign Logic) ---
def get_sweden_time():
    return datetime.now(SWEDEN_TZ).strftime('%Y-%m-%d %H:%M:%S')

async def sovereign_decision_engine(user_input):
    """المحرك الذي يحول المدخلات إلى قرارات إدارية"""
    system_prompt = f"""
    أنت 'المدير السيادي'. هدفك الوحيد: الوصول لأفضل 100 شركة وتحقيق أعلى عائد.
    الوقت الحالي في السويد: {get_sweden_time()}
    القواعد: كن حاسماً، تحليلياً، وركز فقط على نمو المنتج والشركة.
    """
    try:
        response = llm.invoke([("system", system_prompt), ("human", user_input)])
        return response.content
    except Exception as e:
        return f"خطأ في محرك القرار: {str(e)}"

# --- معالجات تلغرام (Telegram Handlers) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = "تم تفعيل النواة السيادية. المدير جاهز للعمل.\nالهدف: أفضل 100 شركة."
    await update.message.reply_text(welcome_msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    # إشعار المدير بالعمل
    decision = await sovereign_decision_engine(user_text)
    await update.message.reply_text(decision)

# --- تشغيل البوت (The Core Engine) ---
async def run_bot():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("TELEGRAM_TOKEN missing!")
        return

    # بناء التطبيق مع نظام منع التضارب تلقائياً
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    logger.info("Sovereign Core is Pulse-Active...")

# --- مسارات Flask للـ Render ---
@app.route('/')
def home():
    return f"Sovereign Manager Active. Time in Sweden: {get_sweden_time()}"

if __name__ == "__main__":
    # تشغيل البوت في الخلفية
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    
    # تشغيل Flask
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
