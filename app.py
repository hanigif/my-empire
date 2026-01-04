import os, threading, asyncio, logging, datetime
import yfinance as yf
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from googlesearch import search  # يحتاج تثبيت: pip install googlesearch-python

# --- الإعدادات الفنية ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
TOKEN = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = 6758877303
INTEL_FILE = "empire_intel_v6.txt"
PORTFOLIO_FILE = "virtual_portfolio.txt"

app = Flask(__name__)

# قائمة الـ 100 شركة (توسيع القائمة)
TOP_100 = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "AVGO", "ASML", "COST", "NFLX", "ADBE", "AMD", "INTC", "PYPL", "V", "MA", "WMT", "JPM", "DIS"]

@app.route('/')
def home():
    return "Empire OS v6.0: Executive System Active. Monitoring Markets & News."

# --- 1. وظيفة البحث عن الأخبار (الذكاء الاستقصائي) ---
def get_stock_news(ticker):
    try:
        query = f"why is {ticker} stock moving today 2026 news"
        results = list(search(query, num_results=3))
        return "\n".join(results)
    except:
        return "No recent news found via search."

# --- 2. محرك التحليل والتعلم (The Executive Cycle) ---
async def executive_cycle(application):
    llm = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
    
    while True:
        try:
            now = datetime.datetime.now()
            report_data = []
            
            for ticker in TOP_100:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="2d")
                if len(hist) < 2: continue
                
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change = ((current_price - prev_price) / prev_price) * 100
                
                # رادار الفرص (حركة > 2.0%)
                if abs(change) >= 2.0:
                    news = get_stock_news(ticker)
                    analysis_prompt = f"""
                    حلل سهم {ticker} بالسعر {current_price:.2f} وتغير {change:.2f}%.
                    الأخبار المتاحة: {news}
                    المطلوب: 
                    1. سبب الحركة.
                    2. قرار (شراء/بيع/انتظار).
                    3. درجة ثقة من 100.
                    4. نص الاستشارة الاحترافي للبيع.
                    اجعل الرد بصيغة JSON مختصرة.
                    """
                    ai_res = llm.invoke([HumanMessage(content=analysis_prompt)])
                    
                    entry = f"| {ticker} | {current_price:.2f} | {change:+.2f}% | {ai_res.content[:150]}... |"
                    report_data.append(entry)
                    
                    # تسجيل في المحفظة الوهمية إذا كانت التوصية شراء
                    if "شراء" in ai_res.content or "BUY" in ai_res.content.upper():
                        with open(PORTFOLIO_FILE, "a") as pf:
                            pf.write(f"{now.date()}, {ticker}, {current_price:.2f}\n")

            if report_data:
                header = "📊 **تقرير النخبة لفرص السوق**\n\n| الشركة | السعر | التغير | التحليل الموجز |\n| :--- | :--- | :--- | :--- |\n"
                full_msg = header + "\n".join(report_data)
                await application.bot.send_message(chat_id=MY_ID, text=full_msg, parse_mode="Markdown")

        except Exception as e:
            logging.error(f"Executive Cycle Error: {e}")
        
        await asyncio.sleep(7200) # فحص كل ساعتين لتجنب الحظر

# --- 3. معالج الرسائل الذكي ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != MY_ID: return
    
    query = update.message.text
    llm = ChatGroq(temperature=0.2, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
    
    if "أرباح" in query or "portfolio" in query.lower():
        if os.path.exists(PORTFOLIO_FILE):
            with open(PORTFOLIO_FILE, "r") as f:
                data = f.read()
            await update.message.reply_text(f"📈 سجل المشتريات الوهمية لتتبع الأرباح:\n{data}")
        else:
            await update.message.reply_text("لا يوجد صفقات مسجلة بعد.")
        return

    # الرد العادي مع سياق الذاكرة
    response = llm.invoke([SystemMessage(content="أنت Empire OS المساعد التنفيذي لهاني."), HumanMessage(content=query)])
    await update.message.reply_text(response.content)

async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    asyncio.create_task(executive_cycle(application))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    while True: await asyncio.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    asyncio.run(main())
