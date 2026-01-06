import manager_tools
import os, threading, asyncio, logging, datetime, pytz
from flask import Flask, render_template
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from strategy_core import StrategyCore 
from web_architect import WebArchitect

# --- الإعدادات السيادية ---
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TELEGRAM_TOKEN") 
MY_ID = 6758877303  
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

app = Flask(__name__)
strategy = StrategyCore() 
architect = WebArchitect()

# تفعيل بوابة العميل فور التشغيل
architect.update_dashboard("v1.2-Legal-Shield-Active")

# --- وظيفة التعلم والتدقيق الآلية (النبض الدوري) ---
def auto_learning_cycle():
    now = datetime.datetime.now(SWEDEN_TZ).strftime('%H:%M:%S')
    logging.info(f"[*] نبضة سيادية دورية: {now}")
    task = "تدقيق أحدث ثغرات الامتثال في المشافي السويدية لعام 2026"
    try:
        # هنا المحامي والمبرمج يعملان تلقائياً في الخلفية
        consensus = strategy.get_consensus(task)
        manager_tools.get_board_decision(f"AUTO_AUDIT: {task} | Result: {consensus['Status']}")
    except Exception as e:
        logging.error(f"[!] تنبيه في الدورة الآلية: {e}")

# المجدول الزمني (الهدف رقم 3 ورقم 6)
scheduler = BackgroundScheduler(daemon=True, timezone=SWEDEN_TZ)
scheduler.add_job(func=auto_learning_cycle, trigger="interval", hours=1)
scheduler.start()

# --- معالجة أوامر القائد (نظام الفيتو) ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    
    await update.message.reply_text("⚖️ جاري استشارة المحامي والمبرمج للتحقق من الامتثال السويدي...")
    
    try:
        task = update.message.text
        # استدعاء العقل (الذي يضم الآن نظام الـ VETO)
        consensus = strategy.get_consensus(task)
        
        # رد النجاح في حال موافقة المحامي
        final_reply = (
            f"🏛️ **تقرير السيادة الرقمية**\n\n"
            f"⚖️ **رأي المحامي السويدي:** {consensus['Verified_Context'][:400]}...\n\n"
            f"⚙️ **القرار التقني:** تم اعتماد البروتوكول وأرشفته بنجاح."
        )
        await update.message.reply_text(final_reply)
        
        # الأرشفة في GitHub
        threading.Thread(target=manager_tools.get_board_decision, args=(f"APPROVED_TASK: {task}",)).start()

    except Exception as e:
        # التقاط فيتو المحامي وإبلاغ القائد فوراً كما طلبت
        error_str = str(e)
        if "VETO_LEGAL" in error_str:
            await update.message.reply_text(f"🚫 **إيقاف طوارئ قانوني!**\n\nالمحامي رفض الإجراء لمخالفته القوانين.\n\n{error_str}")
        else:
            logging.error(f"Technical Error: {e}")
            await update.message.reply_text(f"⚠️ عطل فني في المحرك: {error_str[:100]}")

# --- بوابة الويب (المنتج الملموس) ---
@app.route('/')
def home():
    try:
        return render_template('dashboard.html')
    except:
        return f"🏛️ Sovereign Portal Active. Time: {datetime.datetime.now(SWEDEN_TZ)}"

# --- إقلاع النظام ---
async def main():
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
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port), daemon=True).start()
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("System Shutdown.")
