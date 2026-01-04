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
    temperature=0.2, # درجة حرارة منخفضة لقرار أكثر دقة وسيادية
    model_name="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

def get_sweden_time():
    return datetime.now(SWEDEN_TZ).strftime('%Y-%m-%d %H:%M:%S')

async def sovereign_logic_engine(user_input):
    """هذا هو قلب المنتج الذي سنطوره تدريجياً"""
    system_prompt = f"""
    أنت 'المدير السيادي' (Sovereign Manager). 
    هدفنا الحالي: بناء وتطوير منتج "المدير السيادي" ككيان ذكي متكامل.
    الوقت الحالي في السويد: {get_sweden_time()}
    القواعد: كن استراتيجياً، فكر كقائد منتج، ولا تشتت نفسك بأهداف جانبية.
    """
    try:
        response = llm.invoke([("system", system_prompt), ("human", user_input)])
        return response.content
    except Exception as e:
        return f"عذراً مدير، حدث خطأ في محرك القرار: {str(e)}"

# معالجات التلغرام
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("النواة السيادية نشطة. منتج 'المدير السيادي' جاهز للتطوير.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    decision = await sovereign_logic_engine(update.message.text)
    await update.message.reply_text(decision)

# تشغيل المحرك
async def run_bot():
    token = os.getenv("TELEGRAM_TOKEN")
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True) # أهم سطر لمنع الـ Conflict
    logger.info("Sovereign Manager is Live...")

@app.route('/')
def home():
    return f"Sovereign Core Active. Sweden Time: {get_sweden_time()}"

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
