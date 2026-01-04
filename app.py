import os, threading, asyncio, logging, datetime, json, pytz
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
MEMORY_FILE = "sovereign_memory.json"
LOG_FILE = "activity_log.json"
SWEDEN_TZ = pytz.timezone('Europe/Stockholm') # توقيت السويد الرسمي

app = Flask(__name__)

# --- وظائف إدارة البيانات ---
def load_data(file):
    if os.path.exists(file):
        with open(file, 'r') as f: return json.load(f)
    return {}

def save_data(file, data):
    with open(file, 'w') as f: json.dump(data, f)

# --- محرك التطوير 24/7 (الواقعي) ---
async def continuous_development_cycle(application):
    while True:
        try:
            now_sweden = datetime.datetime.now(SWEDEN_TZ).strftime("%Y-%m-%d %H:%M:%S")
            logs = load_data(LOG_FILE)
            
            # هنا يجمع النظام "بيانات حقيقية" فقط
            # مثال: مراقبة سهم تقني أو خبر عن AI كمنافس للمنتج
            market_data = yf.Ticker("MSFT").info.get('regularMarketPrice', 'N/A') # مثال لمراقبة المنافسين
            
            logs[now_sweden] = f"Market Check: Microsoft Price {market_data}. Analyzing impact on 'Sovereign Manager'."
            save_data(LOG_FILE, logs)
            
            logging.info(f"[{now_sweden}] Activity Logged.")
        except Exception as e:
            logging.error(f"Dev Cycle Error: {e}")
        await asyncio.sleep(3600) # يعمل كل ساعة

# --- معالج الرسائل (بشخصية عملية صارمة) ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    
    user_text = update.message.text
    llm = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY) # تم تقليل الـ temperature لزيادة الدقة ومنع الهذيان
    
    memory = load_data(MEMORY_FILE)
    logs = load_data(LOG_FILE)
    last_activities = list(logs.items())[-5:] # آخر 5 أنشطة حقيقية
    
    system_instruction = (
        f"أنت نظام تشغيل Empire OS. هدفك الوحيد: بناء منتج 'المدير السيادي'. "
        f"التوقيت الحالي في السويد: {datetime.datetime.now(SWEDEN_TZ)}. "
        f"قواعد صارمة: 1. كن واقعياً وعملياً جداً. 2. ممنوع التطبيل أو ادعاء ميزات لم تبرمجها. "
        f"3. اعتمد على هذه الأنشطة الحقيقية المسجلة فقط: {last_activities}. "
        f"4. إذا سألك هاني ماذا فعلت، اذكر الأنشطة المسجلة بالوقت والتاريخ."
    )
    
    response = llm.invoke([
        SystemMessage(content=system_instruction),
        HumanMessage(content=user_text)
    ])
    
    # حفظ الدروس والخبرات
    if "سجل" in user_text:
        memory[str(datetime.datetime.now(SWEDEN_TZ))] = user_text
        save_data(MEMORY_FILE, memory)
        await update.message.reply_text("✅ تم تسجيل المعلومة في الذاكرة الدائمة.")
    else:
        await update.message.reply_text(response.content)

# --- التشغيل ---
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
def home(): return "Empire OS: Sovereign Manager Engine v7.1 (Sweden Time Active)"

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    asyncio.run(main())
