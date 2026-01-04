import os, threading, asyncio, logging, datetime
import yfinance as yf
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from googlesearch import search 

# --- 1. الإعدادات الأساسية ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
TOKEN = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = 6758877303
PORTFOLIO_FILE = "virtual_portfolio.txt"

app = Flask(__name__)

# قائمة الـ 20 شركة الأهم للتركيز (أساس الـ 100 شركة)
TOP_WATCHLIST = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "AVGO", "ASML", "COST", "NFLX", "ADBE", "AMD", "INTC", "PYPL", "V", "MA", "WMT", "JPM", "DIS"]

@app.route('/')
def home():
    return "Empire OS v6.2: Status ONLINE. Monitoring Market Opportunities..."

# --- 2. محرك البحث الذكي عن أخبار الأسهم ---
def get_stock_news(ticker):
    try:
        # البحث عن سبب الحركة في جوجل لعام 2026
        query = f"why is {ticker} stock price moving today 2026 analysis"
        results = []
        for j in search(query, num_results=2):
            results.append(j)
        return " | ".join(results) if results else "No recent specific news found."
    except Exception as e:
        logging.error(f"Search error for {ticker}: {e}")
        return "Search engine temporarily busy."

# --- 3. محرك التحليل التنفيذي (Executive Cycle) ---
async def executive_cycle(application):
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
                    أنت محلل مالي في 2026. سهم {ticker} سعره الآن {current_price:.2f} وتغير بـ {change:+.2f}%.
                    الأخبار المكتشفة: {news}
                    حلل باختصار:
                    1. ما سبب الحركة؟
                    2. هل هي فرصة (شراء/بيع)؟
                    3. درجة الثقة (0-100).
                    اجعل الرد في سطرين فقط للاحترافية.
                    """
                    ai_res = llm.invoke([HumanMessage(content=analysis_prompt)])
                    
                    # تنسيق الجدول
                    entry = f"| {ticker} | {current_price:.2f} | {change:+.2f}% | {ai_res.content[:150]} |"
                    report_entries.append(entry)
                    
                    # حفظ الصفقات "الوهمية" لتتبع الأرباح
                    if "شراء" in ai_res.content or "BUY" in ai_res.content.upper():
                        with open(PORTFOLIO_FILE, "a", encoding="utf-8") as f:
                            f.write(f"{now.strftime('%Y-%m-%d')}, {ticker}, {current_price:.2f}\n")

            if report_entries:
                table_header = "📊 **تقرير النخبة: تحركات السوق الكبرى**\n\n| سهم | سعر | تغير | تحليل Empire OS |\n|---|---|---|---|\n"
                full_report = table_header + "\n".join(report_entries)
                await application.bot.send_message(chat_id=MY_ID, text=full_report, parse_mode="Markdown")

        except Exception as e:
            logging.error(f"Error in cycle: {e}")
        
        # الانتظار لمدة ساعتين قبل الفحص التالي
        await asyncio.sleep(7200)

# --- 4. معالج الرسائل المباشرة ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    
    query = update.message.text
    llm = ChatGroq(temperature=0.2, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
    
    if "أرباح" in query or "portfolio" in query.lower():
        if os.path.exists(PORTFOLIO_FILE):
            with open(PORTFOLIO_FILE, "r", encoding="utf-8") as f:
                data = f.read()
            return await update.message.reply_text(f"📈 سجل صفقاتنا حتى الآن:\n\n{data}")
        return await update.message.reply_text("المحفظة فارغة حالياً.")

    response = llm.invoke([
        SystemMessage(content="أنت Empire OS، النظام الذكي المملوك لهاني. وظيفتك إدارة الاستثمارات وتقديم نصائح دقيقة."),
        HumanMessage(content=query)
    ])
    await update.message.reply_text(response.content)

# --- 5. التشغيل النهائي ---
async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    # تنظيف الاتصالات القديمة
    await application.bot.delete_webhook(drop_pending_updates=True)
    logging.info("Telegram connection cleaned and ready.")

    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    asyncio.create_task(executive_cycle(application))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    # تشغيل Flask بشكل سليم مع إغلاق الأقواس
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
