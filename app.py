import os, threading, asyncio, logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import yfinance as yf

# إعداد السجلات لمراقبة الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = "6758877303"

app = Flask(__name__)

@app.route('/')
def home(): 
    return "<h1>Empire OS v2.1: Revenue System Active</h1>"

# وظيفة جلب بيانات السوق الحقيقية
def get_market_data(text):
    data_str = ""
    stocks = {"NVDA": "NVIDIA", "AAPL": "Apple", "MSFT": "Microsoft", "TSLA": "Tesla"}
    for ticker, name in stocks.items():
        if ticker in text.upper() or name.upper() in text.upper():
            try:
                stock = yf.Ticker(ticker)
                info = stock.fast_info
                price = info['last_price']
                change = info['year_to_date_return'] * 100
                data_str += f"\n- {name} ({ticker}): ${price:.2f} (YTD: {change:.2f}%)"
            except:
                continue
    return data_str

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update or not update.message or not update.message.text: return
    if str(update.effective_user.id) != MY_ID: return

    user_text = update.message.text
    # جلب بيانات حية إذا طلب المستخدم معلومة عن سهم
    live_data = get_market_data(user_text)

    try:
        llm = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
        
        system_prompt = f"""
        أنت العقل المدبر لنظام Empire OS. تعمل ككيان مزدوج:
        1. (المدير المالي): خبير في أفضل 100 شركة عالمياً.
        2. (سايبر): خبير أمن سيبراني يحمي العمليات.
        
        مهمتك الآن: تقديم نموذج (Demo) لمنتج 'Empire Guard: 100'.
        البيانات الحية المتاحة من السوق الآن: {live_data if live_data else 'لا يوجد سهم محدد في الطلب'}
        
        يجب أن يدمج ردك بين الفرصة المالية والفحص الأمني للمنصة (مثل Interactive Brokers) بأسلوب احترافي جداً يغري المشترك بالدفع.
        """
        
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_text)])
        await update.message.reply_text(response.content)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text(f"⚠️ تقرير تقني: النظام يواجه ضغطاً أو مشكلة في الربط. التفاصيل: {str(e)}")

def run_bot():
    # إعداد حلقة الأحداث بشكل صحيح لـ Render
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    # drop_pending_updates=True تحل مشكلة الـ Conflict عبر تجاهل الرسائل القديمة عند التشغيل
    application.run_polling(drop_pending_updates=True, stop_signals=None)

if __name__ == '__main__':
    # تشغيل البوت في خيط منفصل
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()
    
    # تشغيل سيرفر Flask
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
