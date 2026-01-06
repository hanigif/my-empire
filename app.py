import manager_tools
import os, threading, asyncio, logging, datetime, pytz
from flask import Flask, render_template # أضفنا render_template
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from strategy_core import StrategyCore 
from web_architect import WebArchitect # استدعاء مسؤول الواجهة

# --- الإعدادات السيادية ---
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TELEGRAM_TOKEN") 
MY_ID = 6758877303  
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

app = Flask(__name__)
strategy = StrategyCore() 
architect = WebArchitect() # تعيين مسؤول الواجهة

# إنشاء واجهة الموقع فور تشغيل النظام
architect.update_dashboard("v1.0-Sovereign-Portal")

# --- وظيفة التعلم الذاتي الآلية ---
def auto_learning_cycle():
    now = datetime.datetime.now(SWEDEN_TZ).strftime('%H:%M:%S')
    logging.info(f"[*] نبضة سيادية جديدة: {now}")
    task = "تحديث بروتوكولات الأمان السيادي لعام 2026"
    try:
        consensus = strategy.get_consensus(task)
        manager_tools.get_board_decision(f"AUTO_ARCHIVE: {task} | Context: {consensus['Verified_Context'][:100]}")
        logging.info(f"[✓] تم التحديث بنجاح.")
    except Exception as e:
        logging.error(f"[!] خطأ في الدورة: {e}")

scheduler = BackgroundScheduler(daemon=True, timezone=SWEDEN_TZ)
scheduler.add_job(func=auto_learning_cycle, trigger="interval", hours=1)
scheduler.start()

# --- معالجة الرسائل من القائد ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    
    await update.message.reply_text("⏳ جاري البحث وتدقيق الحقائق عبر المحرك السيادي...")
    
    try:
        task = update.message.text
        consensus = strategy.get_consensus(task)
        
        verified_info = consensus.get("Verified_Context", "لا توجد بيانات")
        logic_result = consensus.get("DeepSeek_Logic", "تعذر الإنتاج")

        final_reply = (
            f"🏛️ **تقرير الإمبراطورية السيادية**\n\n"
            f"📋 **التدقيق:** {verified_info[:300]}...\n\n"
            f"⚙️ **القرار التقني:**\n{logic_result[:500]}...\n\n"
            f"🛡️ **الحالة:** تم التحديث في بوابة العميل و GitHub."
        )
        await update.message.reply_text(final_reply)
        threading.Thread(target=manager_tools.get_board_decision, args=(f"LOG: {task}",)).start()

    except Exception as e:
        logging.error(f"❌ خطأ: {e}")
        await update.message.reply_text(f"❌ عطل تقني: {str(e)[:100]}")

# --- محرك واجهة الويب (المنتج الملموس) ---
@app.route('/')
def home(): 
    # عرض لوحة التحكم الاحترافية بدلاً من النص البسيط
    try:
        return render_template('dashboard.html')
    except:
        now_sweden = datetime.datetime.now(SWEDEN_TZ).strftime('%Y-%m-%d %H:%M:%S')
        return f"🏛️ Sovereign Portal Active. Sweden Time: {now_sweden}"

# --- المحرك الأساسي للبوت ---
async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    await application.bot.delete_webhook(drop_pending_updates=True)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(1)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port), daemon=True).start()
    try:
        asyncio.run(main())
    except:
        logging.info("Stopped.")
