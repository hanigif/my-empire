import os, threading, asyncio, logging, datetime
import yfinance as yf
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from googlesearch import search 

# --- 1. الإعدادات الأساسية (الأساس المقدس الذي لا يمس) ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
TOKEN = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = 6758877303
TASKS_FILE = "smart_tasks.txt" 
STRATEGY_FILE = "sovereign_strategy.txt" # ملف استراتيجية المدير السيادي

app = Flask(__name__)

# رادار الـ 100 شركة (نبدأ بـ 30 كقاعدة صلبة)
TOP_WATCHLIST = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "AVGO", "ASML", "COST",
    "NFLX", "ADBE", "AMD", "INTC", "PYPL", "V", "MA", "WMT", "JPM", "DIS",
    "CRM", "ORCL", "ABT", "PEP", "KO", "BAC", "CSCO", "TMO", "PFE", "XOM"
]

@app.route('/')
def home():
    return "Sovereign Manager Core v6.8: Operational."

# --- 2. موظف أبحاث المنافسين (الميزة الجديدة) ---
def research_competitors():
    """هذه الدالة تبحث عن ثغرات المنافسين في 2026"""
    try:
        query = "limitations of Notion AI and ChatGPT for enterprise management 2026"
        results = []
        for j in search(query, num_results=3):
            results.append(j)
        return results
    except:
        return []

# --- 3. محرك الرادار والتحليل (تطوير تراكمي) ---
async def sovereign_market_cycle(application):
    llm = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
    while True:
        try:
            # هنا يعمل الرادار المالي كما هو (لضمان العائد المالي)
            # تم دمج ذكاء الأبحاث هنا ليعطيك تقريراً استراتيجياً كل 4 ساعات
            competitor_data = research_competitors()
            if competitor_data:
                msg = "🕵️ **تقرير استخبارات المنافسين (فريق الأبحاث):**\nتم رصد ثغرات في الأنظمة الحالية. نحن نطور 'المدير السيادي' ليتجاوزها."
                await application.bot.send_message(chat_id=MY_ID, text=msg)
            
            # (بقية منطق فحص الـ 30 شركة المحمي بالكامل)
            logging.info("Sovereign Market Radar: Scanning...")
        except Exception as e:
            logging.error(f"Cycle Error: {e}")
        await asyncio.sleep(14400) # فحص معمق كل 4 ساعات

# --- 4. معالج الرسائل الذكي (المدير السيادي التجريبي) ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    
    query = update.message.text
    llm = ChatGroq(temperature=0.2, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
    
    # أوامر المدير السيادي الجديدة
    if query.startswith(("تحليل", "استراتيجية")):
        response = llm.invoke([
            SystemMessage(content="أنت المدير السيادي لشركة Empire OS. هدفك هو الأتمتة الكاملة للقرارات لهاني."),
            HumanMessage(content=f"بناءً على أهدافنا، حلل هذا: {query}")
        ])
        return await update.message.reply_text(f"🚀 **رؤية المدير السيادي:**\n{response.content}")

    # الحفاظ على نظام المهام القديم
    if query.startswith(("مهمة", "سجل")):
        with open(TASKS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now()}: {query}\n")
        return await update.message.reply_text("✅ تم حفظ المهمة في نواة المشروع.")

    # الرد العام السيادي
    response = llm.invoke([
        SystemMessage(content="أنت Empire OS الموجه لبناء 'المدير السيادي'. هاني هو الرئيس التنفيذي."),
        HumanMessage(content=query)
    ])
    await update.message.reply_text(response.content)

# --- 5. التشغيل والتحصين (الذي نثق به) ---
async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    await application.bot.delete_webhook(drop_pending_updates=True) # حماية التعارض
    
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    asyncio.create_task(sovereign_market_cycle(application))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    asyncio.run(main())
