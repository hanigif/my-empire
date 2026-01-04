import os, threading, asyncio, logging, datetime
import yfinance as yf
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from googlesearch import search 

# --- 1. الإعدادات الأساسية (الأساس الذي لا يمس) ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
TOKEN = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = 6758877303
PORTFOLIO_FILE = "virtual_portfolio.txt"
TASKS_FILE = "smart_tasks.txt" # سجل مهام المشروع الجديد

app = Flask(__name__)

# قائمة الـ 100 شركة (توسيع تدريجي - نبدأ بـ 30 حالياً لضمان السرعة)
TOP_WATCHLIST = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "AVGO", "ASML", "COST",
    "NFLX", "ADBE", "AMD", "INTC", "PYPL", "V", "MA", "WMT", "JPM", "DIS",
    "CRM", "ORCL", "ABT", "PEP", "KO", "BAC", "COST", "CSCO", "AVGO", "TMO"
]

@app.route('/')
def home():
    return "Empire OS v6.7: Status ONLINE. Full Systems Integrated."

# --- 2. محرك البحث الذكي (مستمر ومتطور) ---
def get_stock_news(ticker):
    try:
        query = f"why is {ticker} stock price moving today 2026 analysis"
        results = []
        for j in search(query, num_results=2):
            results.append(j)
        return " | ".join(results) if results else "No recent specific news found."
    except Exception as e:
        logging.error(f"Search error for {ticker}: {e}")
        return "Search engine busy."

# --- 3. محرك الرادار المالي (محمي بالكامل) ---
async def executive_market_cycle(application):
    llm = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
    
    while True:
        try:
            now = datetime.datetime.now()
            report_entries = []
            
            for ticker in TOP_WATCHLIST:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="2d")
                if len(hist) < 2: continue
                
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change = ((current_price - prev_price) / prev_price) * 100
                
                # رادار التنبيه (حركة أكثر من 2%)
                if abs(change) >= 2.0:
                    news = get_stock_news(ticker)
                    
                    analysis_prompt = f"""
                    أنت المحلل المالي لشركة Empire OS. سهم {ticker} سعره {current_price:.2f} وتغير بـ {change:+.2f}%.
                    الأخبار المكتشفة: {news}
                    حلل باختصار: السبب، القرار، ونسبة الثقة.
                    """
                    ai_res = llm.invoke([HumanMessage(content=analysis_prompt)])
                    
                    entry = f"| {ticker} | {current_price:.2f} | {change:+.2f}% | {ai_res.content[:150]} |"
                    report_entries.append(entry)
                    
                    if "شراء" in ai_res.content or "BUY" in ai_res.content.upper():
                        with open(PORTFOLIO_FILE, "a", encoding="utf-8") as f:
                            f.write(f"{now.strftime('%Y-%m-%d %H:%M')}, {ticker}, {current_price:.2f}\n")

            if report_entries:
                header = "📊 **تقرير رادار السوق اللحظي**\n\n| سهم | سعر | تغير | تحليل Empire OS |\n|---|---|---|---|\n"
                await application.bot.send_message(chat_id=MY_ID, text=header + "\n".join(report_entries), parse_mode="Markdown")

        except Exception as e:
            logging.error(f"Market Cycle Error: {e}")
        
        await asyncio.sleep(7200) # فحص كل ساعتين

# --- 4. معالج الرسائل الذكي (يدير الاستثمار والمهام معاً) ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    
    query = update.message.text
    llm = ChatGroq(temperature=0.2, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
    
    # قسم إدارة المحفظة
    if "محفظة" in query.lower() or "portfolio" in query.lower():
        if os.path.exists(PORTFOLIO_FILE):
            with open(PORTFOLIO_FILE, "r", encoding="utf-8") as f:
                return await update.message.reply_text(f"📈 صفقاتنا:\n\n{f.read()}")
        return await update.message.reply_text("المحفظة فارغة.")

    # قسم إدارة مهام المشروع الجديد (من اجتماع اليوم)
    if query.startswith(("مهمة", "سجل", "إضافة")):
        with open(TASKS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now()}: {query}\n")
        response = llm.invoke([
            SystemMessage(content="أنت مدير مشاريع ذكي في شركة Empire OS. قمت بحفظ المهمة بنجاح."),
            HumanMessage(content=query)
        ])
        return await update.message.reply_text(f"📝 تمت إضافة المهمة لنواة المشروع:\n{response.content}")

    # الرد العام الذكي
    response = llm.invoke([
        SystemMessage(content="أنت Empire OS، النظام السيادي المتطور لهاني. هاني هو الرئيس التنفيذي."),
        HumanMessage(content=query)
    ])
    await update.message.reply_text(response.content)

# --- 5. التشغيل النهائي (حماية قصوى من التعارض) ---
async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    # الإجراء الأهم: تنظيف التلغرام قبل البدء لضمان عدم حدوث Conflict
    await application.bot.delete_webhook(drop_pending_updates=True)
    logging.info("Conflict Protection Active. System Ready.")

    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    # تشغيل الرادار المالي في الخلفية
    asyncio.create_task(executive_market_cycle(application))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    # تشغيل Flask لضمان بقاء Render مستيقظاً
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
