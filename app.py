import manager_tools
import os, threading, asyncio, logging, datetime, pytz
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from apscheduler.schedulers.background import BackgroundScheduler

# --- الإعدادات السيادية ---
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TELEGRAM_TOKEN") 
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = 6758877303
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

app = Flask(__name__)

# --- وظيفة التعلم الذاتي الآلية (تنبض كل ساعة) ---
def auto_learning_cycle():
    """هذه الوظيفة تعمل في الخلفية كل ساعة"""
    now = datetime.datetime.now(SWEDEN_TZ).strftime('%H:%M')
    logging.info(f"[*] بدء دورة التعلم الآلية - توقيت السويد: {now}")
    # تنفيذ المهمة عبر المساعدين في ملف manager_tools
    task = "أفضل نماذج أعمال AI Agents وتقنيات الاستقلالية لعام 2026"
    manager_tools.get_board_decision(task)

# إعداد المجدول
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(func=auto_learning_cycle, trigger="interval", hours=1)
scheduler.start()

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: 
        return
    
    # استخدام المحلل الاستراتيجي من manager_tools مباشرة لضمان الأرشفة
    response_text = manager_tools.get_board_decision(update.message.text)
    await update.message.reply_text(response_text)

async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    await application.bot.delete_webhook(drop_pending_updates=True)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    while True:
        await asyncio.sleep(1)

@app.route('/')
def home(): 
    return f"Sovereign Empire OS - Active. Sweden Time: {datetime.datetime.now(SWEDEN_TZ)}"

if __name__ == '__main__':
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True)
    flask_thread.start()
    asyncio.run(main())
