import os, threading, asyncio, logging, datetime, pytz
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram.error import TimedOut, NetworkError
from apscheduler.schedulers.background import BackgroundScheduler

# استيراد المحرك السيادي المطور
from strategy_core import get_board_decision 

# --- 1. الإعدادات الأساسية ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
TOKEN = os.environ.get("TELEGRAM_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
MY_ID = 6758877303  
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

app = Flask(__name__)

# --- 2. نظام النبض والتدقيق الآلي ---
def auto_learning_cycle():
    now = datetime.datetime.now(SWEDEN_TZ).strftime('%H:%M:%S')
    logging.info(f"[*] نبضة سيادية دورية: {now}")
    try:
        # البحث التلقائي عن عملاء أو ثغرات لضمان تحديث المنتج
        result = get_board_decision("AUTO_AUDIT: تدقيق امتثال 2026")
        logging.info(f"[-] نتيجة الدورة: {result[:100]}...")
    except Exception as e:
        logging.error(f"[!] تنبيه في الدورة الآلية: {e}")

# تشغيل المجدول
scheduler = BackgroundScheduler(daemon=True, timezone=SWEDEN_TZ)
scheduler.add_job(func=auto_learning_cycle, trigger="interval", hours=1)
scheduler.start()

# --- 3. معالجة رسائل القائد ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: 
        return
    
    await update.message.reply_text("⚖️ جاري استشارة العقول السيادية (Gemini & Llama)...")
    
    try:
        task = update.message.text
        # استدعاء المحرك الذي يحتوي على وظيفة الـ Scout والإنتاج
        response = get_board_decision(task)
        await update.message.reply_text(response)
    except Exception as e:
        logging.error(f"Technical Error: {e}")
        await update.message.reply_text(f"⚠️ عطل فني: {str(e)[:100]}")

# --- 4. بوابة الويب (لوحة التحكم) ---
@app.route('/')
def home():
    try:
        # عرض حالة الإمبراطورية على الويب
        status_report = get_board_decision("status")
        return f"<html><body style='font-family:monospace; background:#0f0f0f; color:#00ff00; padding:20px;'><pre>{status_report}</pre></body></html>"
    except:
        return "Sovereign System: Online"

# --- 5. محرك الإقلاع (مع نظام إعادة المحاولة الصارم) ---
async def main():
    if not TOKEN:
        logging.error("❌ TELEGRAM_TOKEN مفقود!")
        return

    # بناء التطبيق مرة واحدة خارج الحلقة
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))

    max_retries = 5
    retry_delay = 5  # ثوانٍ

    for attempt in range(max_retries):
        try:
            logging.info(f"🔄 محاولة بدء تشغيل النظام ({attempt + 1}/{max_retries})...")
            
            # بروتوكول الصمود لتجاوز أخطاء الشبكة في Render
            await application.bot.delete_webhook(drop_pending_updates=True)
            await application.initialize()
            await application.start()
            await application.updater.start_polling(drop_pending_updates=True)
            
            logging.info("🚀 تم تشغيل الإمبراطورية بنجاح وتجاوز عوائق الشبكة!")
            break 
        except (TimedOut, NetworkError) as e:
            if attempt < max_retries - 1:
                logging.warning(f"⚠️ مهلة اتصال (Timeout). إعادة المحاولة خلال {retry_delay} ثوانٍ...")
                await asyncio.sleep(retry_delay)
            else:
                logging.error("🚨 فشلت جميع محاولات الاتصال بالسيرفرات الخارجية.")
                raise e

    # الحفاظ على التشغيل
    while True:
        await asyncio.sleep(1)

# --- 6. التشغيل النهائي ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    # تشغيل Flask للويب في الخلفية
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, use_reloader=False), daemon=True).start()
    
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("System Shutdown.")
