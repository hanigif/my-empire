import os, threading, asyncio, logging, datetime, json
import yfinance as yf
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# --- الإعدادات الفنية ---
logging.basicConfig(level=logging.INFO)
TOKEN = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = 6758877303
MEMORY_FILE = "sovereign_memory.json" # ملف الذاكرة الاستراتيجية

app = Flask(__name__)

# --- 1. نظام الذاكرة السيادية (لعدم النسيان) ---
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f: return json.load(f)
    return {"vision": "Building The Sovereign Manager", "learned_lessons": [], "last_update": ""}

def save_memory(data):
    data["last_update"] = str(datetime.datetime.now())
    with open(MEMORY_FILE, 'w') as f: json.dump(data, f)

# --- 2. محرك التطوير 24/7 (الموظف الذي لا ينام) ---
async def continuous_development_cycle(application):
    while True:
        try:
            # هنا يقوم البوت بمراجعة الأهداف وتطويرها تلقائياً
            mem = load_memory()
            logging.info("24/7 Engine: Reviewing market and strategy...")
            
            # مثال: تحديث تلقائي للرادار (هنا يمكن إضافة خوارزميات البحث)
            # سنقوم بإرسال إشعار لك فقط في حال وجدنا "فرصة ذهبية" أو "تهديداً تقنياً"
            
        except Exception as e:
            logging.error(f"Dev Cycle Error: {e}")
        await asyncio.sleep(3600) # يعمل كل ساعة بدقة متناهية

# --- 3. معالج الرسائل المطور (بصلاحيات المدير السيادي) ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    
    user_text = update.message.text
    llm = ChatGroq(temperature=0.3, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
    
    memory = load_memory()
    
    # الرد بهوية المدير السيادي مع استرجاع الذاكرة
    response = llm.invoke([
        SystemMessage(content=f"أنت المدير السيادي لشركة Empire OS. هدفك الوحيد: {memory['vision']}. أنت تعمل 24/7 لتطوير النظام لهاني."),
        HumanMessage(content=user_text)
    ])
    
    # حفظ ما تعلمه البوت من المحادثة
    if "تعلم" in user_text or "سجل" in user_text:
        memory["learned_lessons"].append(user_text)
        save_memory(memory)
        await update.message.reply_text("✅ تم إدخال هذه الخبرة في ذاكرتي الدائمة لضمان التطوير المستمر.")
    else:
        await update.message.reply_text(response.content)

# --- 4. التشغيل الآمن ---
async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    await application.bot.delete_webhook(drop_pending_updates=True)
    
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    # تشغيل محرك التطوير 24/7 كـ Task منفصل
    asyncio.create_task(continuous_development_cycle(application))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(1)

@app.route('/')
def home(): return "Empire OS: Sovereign Manager is Active 24/7"

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    asyncio.run(main())
