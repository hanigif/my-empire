import manager_tools
import os, threading, asyncio, logging, datetime, pytz
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler

# --- الإعدادات السيادية ---
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TELEGRAM_TOKEN") 
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = 6758877303  # هويتك السيادية
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

app = Flask(__name__)

# --- وظيفة التعلم الذاتي الآلية (تنبض كل ساعة) ---
def auto_learning_cycle():
    """هذه الوظيفة تعمل في الخلفية كل ساعة لضمان استمرارية عمل الشركة"""
    now = datetime.datetime.now(SWEDEN_TZ).strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"[*] بدء دورة التعلم الآلية - توقيت السويد: {now}")
    
    # المهمة الاستراتيجية للدورة الآلية
    task = "تحليل أحدث فرص الاستثمار والتقنيات السيادية لعام 2026 ونماذج الربح المستقلة"
    
    # استدعاء المدير السيادي للبحث والأرشفة والتحليل
    # النتائج ستُحفظ تلقائياً في الـ Knowledge Base عبر manager_tools
    manager_tools.get_board_decision(task)
    logging.info(f"[✓] اكتملت دورة التعلم وتمت الأرشفة بنجاح.")

# --- إعداد المجدول السيادي ---
scheduler = BackgroundScheduler(daemon=True)
# إضافة الوظيفة لتعمل كل ساعة (60 دقيقة)
scheduler.add_job(func=auto_learning_cycle, trigger="interval", hours=1)
scheduler.start()

# --- معالجة الرسائل الواردة من القائد ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: 
        return
    
    # إشعار البدء
    await update.message.reply_text("⏳ القائد يتحدث.. جاري استشارة مجلس الإدارة وأرشفة البيانات...")
    
    # استخدام المحلل الاستراتيجي من manager_tools مباشرة لضمان الأرشفة والبحث والتحليل
    # هذا يضمن أن كل رسالة ترسلها تتحول إلى "معرفة" محفوظة
    response_text = manager_tools.get_board_decision(update.message.text)
    
    await update.message.reply_text(response_text)

# --- المحرك الأساسي للبوت ---
async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    # تنظيف التحديثات المعلقة لضمان بداية نظيفة
    await application.bot.delete_webhook(drop_pending_updates=True)
    
    # معالجة النصوص فقط من القائد
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    logging.info("[-] البوت نشط الآن وجاهز للأوامر السيادية.")
    
    # الحفاظ على تشغيل الحلقة البرمجية
    while True:
        await asyncio.sleep(1)

# --- واجهة الويب (لضمان عمل UptimeRobot و Render) ---
@app.route('/')
def home(): 
    return f"🏛️ Sovereign Empire OS - Active. <br>Sweden Time: {datetime.datetime.now(SWEDEN_TZ).strftime('%Y-%m-%d %H:%M:%S')}"

# --- نقطة الانطلاق ---
if __name__ == '__main__':
    # تشغيل Flask في Thread منفصل لخدمة الـ Webhook و UptimeRobot
    flask_thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), 
        daemon=True
    )
    flask_thread.start()
    
    # تشغيل محرك التلغرام الأساسي
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("[!] تم إيقاف النظام السيادي يدوياً.")
