import os, threading, asyncio, logging, datetime, json, pytz
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# --- الإعدادات السيادية ---
logging.basicConfig(level=logging.INFO)
TOKEN = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = 6758877303
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

LOG_FILE = "activity_log.json"
PRODUCT_LAB_FILE = "sovereign_lab.py"

app = Flask(__name__)

# --- وظائف البيانات ---
def load_data(file):
    if os.path.exists(file):
        with open(file, 'r') as f: return json.load(f)
    return {}

def save_data(file, data):
    with open(file, 'w') as f: json.dump(data, f)

# --- محرك الرقابة المستمر ---
async def continuous_monitor(application):
    while True:
        try:
            now = datetime.datetime.now(SWEDEN_TZ).strftime("%H:%M:%S")
            logs = load_data(LOG_FILE)
            lab_active = "Active" if os.path.exists(PRODUCT_LAB_FILE) else "Ready"
            logs[now] = f"Status: {lab_active} | System: Secure"
            save_data(LOG_FILE, logs)
        except: pass
        await asyncio.sleep(3600)

# --- معالج الرسائل الذكي ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    
    llm = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
    
    system_instruction = (
        f"أنت المدير السيادي. وقت السويد: {datetime.datetime.now(SWEDEN_TZ)}. "
        "مهمتك تطوير منتج 'المدير السيادي' داخل sovereign_lab.py فقط."
    )
    
    response = llm.invoke([SystemMessage(content=system_instruction), HumanMessage(content=update.message.text)])
    await update.message.reply_text(response.content)

# --- التشغيل النهائي (حل التعارض) ---
async def main():
    # 1. إنشاء التطبيق
    application = ApplicationBuilder().token(TOKEN).build()
    
    # 2. تنظيف قسري لأي جلسات قديمة (Force Close)
    logging.info("Attempting to close old sessions...")
    await application.bot.delete_webhook(drop_pending_updates=True)
    await asyncio.sleep(2) # انتظار التأكيد من خوادم تلغرام
    
    # 3. إضافة المعالجات
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    # 4. تشغيل المراقبة
    asyncio.create_task(continuous_monitor(application))
    
    # 5. بدء التشغيل مع التنبيه عند النجاح
    await application.initialize()
    await application.start()
    
    # إرسال رسالة تأكيد لك بمجرد أن يفتح "عينه"
    await application.bot.send_message(chat_id=MY_ID, text="✅ Empire OS v7.2.2: أنا متصل الآن والسيطرة كاملة. المختبر جاهز.")
    
    await application.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(1)

@app.route('/')
def home(): return "Sovereign Lab v7.2.2 Online"

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    asyncio.run(main())
