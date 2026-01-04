import os, threading, asyncio, logging, datetime, json, pytz
import yfinance as yf
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# --- الإعدادات الأساسية (لا يمكن المساس بها) ---
logging.basicConfig(level=logging.INFO)
TOKEN = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = 6758877303
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

# ملفات النظام
MEMORY_FILE = "sovereign_memory.json"
LOG_FILE = "activity_log.json"
PRODUCT_LAB_FILE = "sovereign_lab.py" # مختبر تطوير المنتج

app = Flask(__name__)

def load_data(file):
    if os.path.exists(file):
        with open(file, 'r') as f: return json.load(f)
    return {}

def save_data(file, data):
    with open(file, 'w') as f: json.dump(data, f)

# --- محرك التطوير 24/7 (المراقب للمختبر) ---
async def continuous_development_cycle(application):
    while True:
        try:
            now_sweden = datetime.datetime.now(SWEDEN_TZ).strftime("%Y-%m-%d %H:%M:%S")
            logs = load_data(LOG_FILE)
            
            # فحص حالة المختبر
            lab_status = "Empty"
            if os.path.exists(PRODUCT_LAB_FILE) and os.path.getsize(PRODUCT_LAB_FILE) > 0:
                lab_status = "Active - New Product Feature Drafted"
            
            # فحص السوق (كمثال للبيانات الخارجية)
            msft_price = yf.Ticker("MSFT").info.get('regularMarketPrice', 'N/A')
            
            logs[now_sweden] = f"Market: MSFT @{msft_price} | Lab Status: {lab_status}"
            save_data(LOG_FILE, logs)
            
            logging.info(f"[{now_sweden}] Sovereign Lab Monitored.")
        except Exception as e:
            logging.error(f"Dev Cycle Error: {e}")
        await asyncio.sleep(3600)

# --- معالج الرسائل الذكي ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    
    user_text = update.message.text
    llm = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
    
    logs = load_data(LOG_FILE)
    last_activities = list(logs.items())[-3:]
    
    system_instruction = (
        f"أنت نظام تشغيل Empire OS المسؤول عن بناء 'المدير السيادي'. "
        f"توقيت السويد: {datetime.datetime.now(SWEDEN_TZ)}. "
        f"مهمتك: العمل في 'المختبر' فقط. ممنوع تعديل الكود الأساسي (app.py). "
        f"عندما يطلب هاني ميزة جديدة، اكتب كودها واقترحه عليه كمسودة ليقوم هو بوضعها في sovereign_lab.py. "
        f"آخر أنشطة المختبر: {last_activities}"
    )
    
    response = llm.invoke([
        SystemMessage(content=system_instruction),
        HumanMessage(content=user_text)
    ])
    
    await update.message.reply_text(response.content)

# --- تشغيل النظام ---
async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    await application.bot.delete_webhook(drop_pending_updates=True)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    asyncio.create_task(continuous_development_cycle(application))
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(1)

@app.route('/')
def home(): return "Empire OS v7.2: Product Lab Mode Active (Secure Control)"

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    asyncio.run(main())
