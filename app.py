import manager_tools
import os, threading, asyncio, logging, datetime, pytz
from flask import Flask, render_template
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from strategy_core import StrategyCore 
from web_architect import WebArchitect

logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TELEGRAM_TOKEN") 
MY_ID = 6758877303  
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

app = Flask(__name__)
strategy = StrategyCore() 
architect = WebArchitect()

architect.update_dashboard("v1.1-Sovereign-Legal-Shield")

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    
    status_msg = await update.message.reply_text("⚖️ جاري فحص الامتثال القانوني والتقني من قبل المحامي والمبرمج...")
    
    try:
        task = update.message.text
        # استدعاء الإجماع الذي يتضمن الآن "فحص المحامي"
        consensus = strategy.get_consensus(task)
        
        # إذا وافق المحامي:
        final_reply = (
            f"🏛️ **تقرير السيادة: موافقة قانونية**\n\n"
            f"⚖️ **موقف المحامي:** {consensus['Verified_Context'][:400]}...\n\n"
            f"⚙️ **الحل التقني:** تم اعتماده وأرشفته."
        )
        await update.message.reply_text(final_reply)
        threading.Thread(target=manager_tools.get_board_decision, args=(f"LEGAL_APPROVED: {task}",)).start()

    except Exception as e:
        # إذا رفض المحامي (الفيتو)
        if "VETO_LEGAL" in str(e):
            await update.message.reply_text(f"🚫 **فيتو قانوني عاجل!**\n\nتم إيقاف العملية لأنها تخالف القوانين السويدية.\n{str(e)}")
        else:
            logging.error(f"Error: {e}")
            await update.message.reply_text(f"⚠️ عطل فني: {str(e)[:100]}")

@app.route('/')
def home():
    try: return render_template('dashboard.html')
    except: return "Sovereign Portal Active."

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
    try: asyncio.run(main())
    except: pass
