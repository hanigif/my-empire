import os, threading, asyncio, logging, datetime, json, pytz
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# --- الإعدادات السيادية (أساس لا يُمس) ---
logging.basicConfig(level=logging.INFO)
TOKEN = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = 6758877303
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

app = Flask(__name__)

# --- دمج المختبر في دورة المراقبة المستمرة ---
async def continuous_monitor(application):
    while True:
        try:
            # استدعاء المختبر بهدوء كل ساعة لضمان التحسين المستمر
            from sovereign_lab import run_lab_test
            report = run_lab_test()
            logging.info(f"Sovereign Lab Report at {report['timestamp']}: {report['detail']}")
        except Exception as e:
            logging.error(f"Lab Access Error: {e}")
        await asyncio.sleep(3600) # فحص التقدم كل ساعة [cite: 2025-12-31]

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    
    llm = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
    
    # التعليمات السيادية للمدير [cite: 2026-01-04]
    system_instruction = (
        f"أنت المدير السيادي. الوقت الآن في السويد: {datetime.datetime.now(SWEDEN_TZ)}. "
        "مهمتك الوحيدة هي إدارة وتطوير شركة المدير السيادي للوصول لأفضل 100 شركة."
    )
    
    response = llm.invoke([SystemMessage(content=system_instruction), HumanMessage(content=update.message.text)])
    await update.message.reply_text(response.content)

async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    # تطهير الاتصالات القديمة لضمان عدم التعارض [cite: 2026-01-04]
    await application.bot.delete_webhook(drop_pending_updates=True)
    
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    # تشغيل مراقبة المختبر في الخلفية
    asyncio.create_task(continuous_monitor(application))
    
    await application.initialize()
    await application.start()
    
    # بدء سحب الرسائل مع تجاهل أي رسائل قديمة عالقة
    await application.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(1)

@app.route('/')
def home(): return "Sovereign Empire OS v7.2.2 - Lab Active"

if __name__ == '__main__':
    # تشغيل Flask في خيط منفصل لضمان بقاء السيرفر حياً 24/7
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    asyncio.run(main())
