import os, threading, asyncio, logging, datetime, pytz
from flask import Flask, render_template
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler

# استيراد الوظيفة المحركة من الكود المدمج الجديد
from strategy_core import get_board_decision 

# --- الإعدادات السيادية ---
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TELEGRAM_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
MY_ID = 6758877303  
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

app = Flask(__name__)

# --- وظيفة التعلم والتدقيق الآلية (النبض الدوري) ---
def auto_learning_cycle():
    now = datetime.datetime.now(SWEDEN_TZ).strftime('%H:%M:%S')
    logging.info(f"[*] نبضة سيادية دورية: {now}")
    task = "تدقيق أحدث ثغرات الامتثال في المشافي السويدية لعام 2026"
    try:
        # استخدام المحرك المدمج الجديد مباشرة
        result = get_board_decision(f"AUTO_AUDIT: {task}")
        logging.info(f"[-] نتيجة الدورة: {result[:100]}...")
    except Exception as e:
        logging.error(f"[!] تنبيه في الدورة الآلية: {e}")

# المجدول الزمني
scheduler = BackgroundScheduler(daemon=True, timezone=SWEDEN_TZ)
scheduler.add_job(func=auto_learning_cycle, trigger="interval", hours=1)
scheduler.start()

# --- معالجة أوامر القائد ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    
    await update.message.reply_text("⚖️ جاري استشارة المحامي والمبرمج السيادي (نظام 2026)...")
    
    try:
        task = update.message.text
        # استدعاء المحرك المدمج الذي يحتوي على Gemini و Llama معاً
        response = get_board_decision(task)
        await update.message.reply_text(response)

    except Exception as e:
        logging.error(f"Technical Error: {e}")
        await update.message.reply_text(f"⚠️ عطل فني في المحرك: {str(e)[:100]}")

# --- بوابة الويب (المنتج الملموس) ---
@app.route('/')
def home():
    # استدعاء حالة الإمبراطورية لعرضها على الصفحة الرئيسية
    status_report = get_board_decision("status")
    return f"<pre>{status_report}</pre>"

# --- إقلاع النظام ---
async def main():
    if not TOKEN:
        logging.error("❌ TELEGRAM_TOKEN مفقود!")
        return

    application = ApplicationBuilder().token(TOKEN).build()
    await application.bot.delete_webhook(drop_pending_updates=True)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    logging.info("[-] النظام السيادي يعمل بكامل طاقته القانونية والتقنية.")
    while True: await asyncio.sleep(1)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    # تشغيل Flask في ثريد منفصل
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, use_reloader=False), daemon=True).start()
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("System Shutdown.")
