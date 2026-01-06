import manager_tools
import os, threading, asyncio, logging, datetime, pytz
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from strategy_core import StrategyCore  # العقل الجديد المحدث

# --- الإعدادات السيادية ---
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TELEGRAM_TOKEN") 
GK_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
MY_ID = 6758877303  # هويتك السيادية
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

app = Flask(__name__)
strategy = StrategyCore() # تفعيل العقل المحدث

# --- وظيفة التعلم الذاتي الآلية (تنبض كل ساعة) ---
def auto_learning_cycle():
    """هذه الوظيفة تعمل في الخلفية لضمان استمرارية عمل الشركة بناءً على حقائق مدققة"""
    now = datetime.datetime.now(SWEDEN_TZ).strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"[*] بدء دورة التعلم الآلية - توقيت السويد: {now}")
    
    # المهمة الاستراتيجية للدورة الآلية (تم تحديثها لتكون أكثر دقة)
    task = "تطوير بروتوكولات الخصوصية السيادية لعام 2026 بناءً على أحدث قوانين السويد"
    
    try:
        # استخدام العقل الجديد للبحث والتدقيق قبل اتخاذ القرار
        consensus = strategy.get_consensus(task)
        # تمرير القرار للمدير السيادي للأرشفة والرفع لـ GitHub
        manager_tools.get_board_decision(f"AUTO_TASK: {task} | Context: {consensus['Verified_Context']}")
        logging.info(f"[✓] اكتملت دورة التعلم الموثقة وتمت الأرشفة بنجاح.")
    except Exception as e:
        logging.error(f"[!] خطأ في دورة التعلم: {e}")

# --- إعداد المجدول السيادي ---
scheduler = BackgroundScheduler(daemon=True, timezone=SWEDEN_TZ)
# يمكنك تعديل hours=1 إلى دقائق إذا أردت تسريع الإنتاج (مثلاً 0.68 ساعة لتعادل 41 دقيقة)
scheduler.add_job(func=auto_learning_cycle, trigger="interval", hours=1)
scheduler.start()

# --- معالجة الرسائل الواردة من القائد ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: 
        return
    
    status_msg = await update.message.reply_text("⏳ القائد يتحدث.. جاري استشارة مجلس الإدارة، تدقيق الحقائق، وأرشفة البيانات...")
    
    try:
        task = update.message.text
        # استدعاء العقل الجديد للحصول على إجماع مدقق
        consensus = strategy.get_consensus(task)
        
        # تحويل النتيجة للمدير السيادي للقيام بالعمليات التقنية (GitHub)
        response_text = manager_tools.get_board_decision(f"COMMAND: {task} | Context: {consensus['Verified_Context']}")
        
        # إضافة لمحة من التدقيق في الرد النهائي للقائد
        final_reply = f"{response_text}\n\n📋 **ملخص التدقيق:** {consensus['Verified_Context'][:200]}..."
        await update.message.reply_text(final_reply)
        
    except Exception as e:
        error_msg = f"❌ خطأ سيادي: {str(e)}"
        logging.error(error_msg)
        await update.message.reply_text("عذراً سيدي، واجه المحرك التقني صعوبة في تدقيق المعلومات. تم تسجيل الخطأ.")

# --- المحرك الأساسي للبوت ---
async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    await application.bot.delete_webhook(drop_pending_updates=True)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    logging.info("[-] البوت نشط الآن ومسلح بالعقل المدقق.")
    while True:
        await asyncio.sleep(1)

# --- واجهة الويب ---
@app.route('/')
def home(): 
    now_sweden = datetime.datetime.now(SWEDEN_TZ).strftime('%Y-%m-%d %H:%M:%S')
    return f"🏛️ Sovereign Empire OS - Verified Brain Active. <br>Sweden Time: {now_sweden}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    flask_thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=port), 
        daemon=True
    )
    flask_thread.start()
    
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("[!] تم إيقاف النظام السيادي يدوياً.")
