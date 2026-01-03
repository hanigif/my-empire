import os, threading, asyncio, logging, time, requests
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import yfinance as yf

# 1. إعدادات السجلات (Logs) لمراقبة الأداء
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 2. الثوابت (المعلومات الحساسة)
TOKEN = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = "6758877303"

app = Flask(__name__)

@app.route('/')
def home():
    return "Empire OS Core v3.0: Online & Stable"

# 3. وظيفة جلب بيانات السوق (تدعم المقارنة بين شركات متعددة)
def get_market_data(text):
    stocks_map = {
        "NVDA": "NVIDIA", "AAPL": "Apple", "MSFT": "Microsoft", 
        "TSLA": "Tesla", "AMZN": "Amazon", "GOOGL": "Google"
    }
    extracted_data = ""
    for ticker, name in stocks_map.items():
        if ticker in text.upper() or name.upper() in text.upper():
            try:
                stock = yf.Ticker(ticker)
                info = stock.fast_info
                price = info['last_price']
                change = info['year_to_date_return'] * 100
                extracted_data += f"\n- {name} ({ticker}): ${price:.2f} (YTD: {change:.2f}%)"
            except Exception as e:
                logging.error(f"Error fetching {ticker}: {e}")
    return extracted_data

# 4. معالج الرسائل الذكي (الشخصية المزدوجة: مالي + سايبر)
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    if str(update.effective_user.id) != MY_ID: return

    user_query = update.message.text
    live_market_info = get_market_data(user_query)

    try:
        llm = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
        
        system_instructions = f"""
        أنت العقل المدبر لنظام Empire OS. تعمل ككيان مزدوج:
        - المدير المالي: خبير في أفضل 100 شركة عالمياً، يحلل الربحية والنمو.
        - خبير سايبر: يحلل أمن المنصات والثغرات التقنية المؤثرة على السوق.
        
        بيانات السوق اللحظية المتوفرة: {live_market_info if live_market_info else 'لا توجد بيانات محددة حالياً'}
        
        مهمتك: تقديم تحليل عميق يدمج بين الفرصة المالية والأمان التقني.
        """
        
        response = llm.invoke([
            SystemMessage(content=system_instructions),
            HumanMessage(content=user_query)
        ])
        await update.message.reply_text(response.content)
    except Exception as e:
        logging.error(f"Handler Error: {e}")
        await update.message.reply_text("⚠️ النظام يواجه ضغطاً تقنياً، جاري إعادة المحاولة...")

# 5. نظام النبض الذاتي (Keep-Alive) لمنع النوم على Render
def keep_alive_pulse():
    # ننتظر قليلاً حتى يتم تشغيل السيرفر
    time.sleep(30)
    while True:
        try:
            # هنا يرسل السيرفر إشارة لنفسه ليبقى حياً
            logging.info("Pulse: Empire OS Core is active.")
        except: pass
        time.sleep(300) # نبض كل 5 دقائق

# 6. تشغيل البوت والسيرفر بالتوازي
def run_telegram_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    application.run_polling(drop_pending_updates=True, close_loop=False)

if __name__ == '__main__':
    # أ: تشغيل البوت في خيط منفصل
    threading.Thread(target=run_telegram_bot, daemon=True).start()
    
    # ب: تشغيل النبض الذاتي
    threading.Thread(target=keep_alive_pulse, daemon=True).start()
    
    # ج: تشغيل واجهة الويب (Flask)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
