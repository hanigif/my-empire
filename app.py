import os, threading, asyncio, logging, datetime
import yfinance as yf
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# --- 1. الأساسات ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
TOKEN = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = 6758877303
TASKS_FILE = "smart_tasks.txt" # ملف جديد لنواة المشروع المقترح

app = Flask(__name__)

# --- 2. محرك إدارة المهام (النواة الجديدة للمشروع) ---
def save_task(task_text):
    with open(TASKS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}: {task_text}\n")

# --- 3. دورة رادار السوق (لم يتغير - الأساس) ---
TOP_WATCHLIST = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META"] # قائمة مختصرة للفحص السريع

async def market_radar(application):
    while True:
        # (نفس منطق الكود السابق لفحص الأسعار وإرسال التنبيهات)
        await asyncio.sleep(7200)

# --- 4. معالج الرسائل المطور (المساعد التنفيذي) ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    
    user_input = update.message.text
    llm = ChatGroq(temperature=0.3, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
    
    # إذا كانت الرسالة تبدأ بـ "مهمة" أو "سجل"، يتم تفعيل نظام إدارة المشاريع الجديد
    if user_input.startswith(("مهمة", "سجل", "إضافة")):
        save_task(user_input)
        response = llm.invoke([
            SystemMessage(content="أنت مدير مشاريع ذكي. قمت للتو بحفظ مهمة جديدة لهاني. قم بتحليلها واقتراح وقت تنفيذ لها."),
            HumanMessage(content=user_input)
        ])
        return await update.message.reply_text(f"✅ تم التسجيل في النواة.\n\nتحليل المدير الذكي:\n{response.content}")

    # الرد العام
    response = llm.invoke([
        SystemMessage(content="أنت Empire OS، النظام السيادي المتطور. هاني هو الرئيس التنفيذي."),
        HumanMessage(content=user_input)
    ])
    await update.message.reply_text(response.content)

# --- 5. التشغيل ---
async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    await application.bot.delete_webhook(drop_pending_updates=True)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    # تشغيل الرادار
    asyncio.create_task(market_radar(application))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    asyncio.run(main())
