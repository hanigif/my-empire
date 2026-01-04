import os, threading, asyncio, logging, datetime, json, pytz
import yfinance as yf
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# --- الإعدادات (ثابتة) ---
logging.basicConfig(level=logging.INFO)
TOKEN = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = 6758877303
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

# الملفات
MEMORY_FILE = "sovereign_memory.json"
LOG_FILE = "activity_log.json"
PRODUCT_LAB_FILE = "sovereign_lab.py"

app = Flask(__name__)

def load_data(file):
    if os.path.exists(file):
        with open(file, 'r') as f: return json.load(f)
    return {}

def save_data(file, data):
    with open(file, 'w') as f: json.dump(data, f)

# --- محرك الرقابة 24/7 ---
async def continuous_development_cycle(application):
    while True:
        try:
            now_sweden = datetime.datetime.now(SWEDEN_TZ).strftime("%H:%M:%S")
            logs = load_data(LOG_FILE)
            lab_status = "Active" if os.path.exists(PRODUCT_LAB_FILE) else "Empty"
            logs[now_sweden] = f"Sovereign Lab: {lab_status} | System: Online"
            save_data(LOG_FILE, logs)
            logging.info(f"Monitor Logged at {now_sweden}")
        except Exception as e:
            logging.error(f"Cycle Error: {e}")
        await asyncio.sleep(3600)

# --- معالج الرسائل ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    
    user_text = update.message.text
    llm = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
    
    system_instruction = (
        f"أنت المدير السيادي داخل Empire OS. وقت السويد الآن: {datetime.datetime.now(SWEDEN_TZ)}. "
        f"صلاحياتك محصورة في 'المختبر' (sovereign_lab.py). "
        "مهمتك اقتراح حلول تقنية وإدارية لهاني، وعند الاتفاق على كود، تطلب منه وضعه في المختبر."
    )
    
    response = llm.invoke([SystemMessage(content=system_instruction), HumanMessage(content=user_text)])
    await update.message.reply_text(response.content)

# --- التشغيل الرئيسي ---
async def main():
    # منع التصادم عبر حذف الـ Webhook وتنظيف الجلسات القديمة
    application = ApplicationBuilder().token(TOKEN).build()
    await application.bot.delete_webhook(drop_pending_updates=True)
    
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    # تشغيل دورة الرقابة
    asyncio.create_task(continuous_development_cycle(application))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    logging.info("Empire OS v7.2.1 Started Successfully")
    while True: await asyncio.sleep(1)

@app.route('/')
def home(): return "Sovereign Control Active"

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    asyncio.run(main())
