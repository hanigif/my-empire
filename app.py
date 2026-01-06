import manager_tools
import os, threading, asyncio, logging, datetime, pytz
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from strategy_core import StrategyCore 

# --- الإعدادات السيادية ---
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TELEGRAM_TOKEN") 
MY_ID = 6758877303  
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

app = Flask(__name__)
strategy = StrategyCore() 

# --- وظيفة التعلم الذاتي الآلية ---
def auto_learning_cycle():
    now = datetime.datetime.now(SWEDEN_TZ).strftime('%H:%M:%S')
    logging.info(f"[*] نبضة سيادية جديدة: {now}")
    task = "تحديث بروتوكولات الأمان السيادي لعام 2026"
    try:
        # نحصل على الإجماع من العقل المحدث (الذي يملك نظام التبديل الآلي)
        consensus = strategy.get_consensus(task)
        # نرسل النتيجة الجاهزة فقط للأرشفة لضمان عدم استهلاك توكنات Groq مجدداً
        manager_tools.get_board_decision(f"AUTO_ARCHIVE: {task} | Context: {consensus['Verified_Context'][:100]}")
        logging.info(f"[✓] تم التحديث الذاتي بنجاح.")
    except Exception as e:
        logging.error(f"[!] خطأ في الدورة: {e}")

scheduler = BackgroundScheduler(daemon=True, timezone=SWEDEN_TZ)
scheduler.add_job(func=auto_learning_cycle, trigger="interval", hours=1)
scheduler.start()

# --- معالجة الرسائل من القائد ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    
    # إشعار البدء الذكي
    status_msg = await update.message.reply_text("⏳ جاري البحث في المصادر السويدية وتفعيل نظام التبديل الآلي...")
    
    try:
        task = update.message.text
        # 1. العقل الجديد يقوم بالبحث والتدقيق والبرمجة (مع Failover لـ Gemini)
        consensus = strategy.get_consensus(task)
        
        # 2. استخراج المخرجات
        verified_info = consensus.get("Verified_Context", "لا توجد بيانات محدثة")
        logic_result = consensus.get("DeepSeek_Logic", "تعذر إنتاج الكود")
        strategy_result = consensus.get("Gemini_Strategy", "تحليل استراتيجي غير متوفر")

        # 3. إبلاغ القائد بالنتيجة فوراً (قبل الأرشفة لضمان السرعة)
        # نستخدم النص الناتج من العقل المحدث مباشرة
        final_reply = (
            f"🏛️ **تقرير الإمبراطورية السيادية**\n\n"
            f"📋 **التدقيق (2026):** {verified_info[:300]}...\n\n"
            f"⚙️ **القرار التقني:**\n{logic_result[:500]}...\n\n"
            f"🛡️ **الحالة:** تم الإنتاج وتخطي قيود الحصة اليومية بنجاح."
        )
        await update.message.reply_text(final_reply)

        # 4. الأرشفة في الخلفية (GitHub) دون إزعاج القائد بالانتظار
        threading.Thread(target=manager_tools.get_board_decision, args=(f"LOG: {task}",)).start()

    except Exception as e:
        logging.error(f"❌ خطأ: {e}")
        # إذا كان الخطأ متعلق بالـ Rate Limit رغم نظام التبديل
        if "429" in str(e):
            await update.message.reply_text("⚠️ النظام تحت ضغط عالٍ، لكن المحرك الاحتياطي يعمل. يرجى إعادة المحاولة خلال دقيقة.")
        else:
            await update.message.reply_text(f"❌ عطل تقني: {str(e)[:100]}")

# --- بقية المحرك (main & Flask) ---
async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    await application.bot.delete_webhook(drop_pending_updates=True)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(1)

@app.route('/')
def home(): return f"🏛️ Sovereign Empire - Verified & Fail-Safe Active. {datetime.datetime.now(SWEDEN_TZ)}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port), daemon=True).start()
    try: asyncio.run(main())
    except: logging.info("Stopped.")
