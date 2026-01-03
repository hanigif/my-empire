import os, threading, asyncio, logging, time
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import yfinance as yf

# --- إعدادات النظام الأساسية ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = "6758877303"

app = Flask(__name__)

@app.route('/')
def home():
    return "Empire OS v3.2: Full Power Core Online"

# --- محرك البيانات المالي (الرادار) ---
def fetch_comprehensive_data(text):
    """جلب بيانات مالية تفصيلية لأهم الشركات عند ذكرها"""
    tickers = {
        "NVDA": "NVIDIA", "TSLA": "Tesla", "MSFT": "Microsoft",
        "AAPL": "Apple", "AMZN": "Amazon", "GOOGL": "Google",
        "META": "Meta", "ASML": "ASML"
    }
    report = ""
    for ticker, name in tickers.items():
        if ticker in text.upper() or name.upper() in text.upper():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="5d")
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change = ((current_price - prev_price) / prev_price) * 100
                
                report += f"\n- {name} ({ticker}): ${current_price:.2f} ({change:+.2f}% اليوم)"
            except: continue
    return report

# --- معالج الرسائل (العقل المدبر) ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    if str(update.effective_user.id) != MY_ID: return

    user_query = update.message.text
    market_context = fetch_comprehensive_data(user_query)

    try:
        # استخدام أعلى نموذج متاح للتحليل
        llm = ChatGroq(temperature=0.2, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
        
        system_logic = f"""
        أنت الكيان التقني المالي "Empire OS". 
        قواعدك الصارمة:
        1. التحليل المالي: اعتمد على البيانات الحقيقية المرفقة {market_context if market_context else 'لا توجد بيانات لحظية حالياً'}.
        2. الرؤية الأمنية: حلل أي مخاطر سيبرانية أو جيوسياسية قد تؤثر على الشركات المذكورة.
        3. الهدف: تحقيق أعلى عائد للمدير (Hani) وتنبيهه للفرص فوراً.
        4. الأسلوب: ردود احترافية، مقتضبة، وعميقة.
        """
        
        response = llm.invoke([
            SystemMessage(content=system_logic),
            HumanMessage(content=user_query)
        ])
        await update.message.reply_text(response.content)
    except Exception as e:
        logging.error(f"Logic Error: {e}")
        await update.message.reply_text("⚠️ خلل في معالجة البيانات، جاري إعادة تشغيل المحرك...")

# --- أنظمة البقاء (Keep-Alive) ---
def keep_alive_pulse():
    while True:
        # نبض داخلي للسجلات
        logging.info("Pulse: Empire OS Core Heartbeat...")
        time.sleep(300)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, use_reloader=False)

# --- نقطة الانطلاق الرئيسية ---
if __name__ == '__main__':
    # 1. تشغيل واجهة الويب والنبض في خيوط خلفية
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=keep_alive_pulse, daemon=True).start()
    
    # 2. تشغيل البوت في الخيط الرئيسي لضمان الاستقرار التام
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    logging.info("Empire OS System Initiated...")
    application.run_polling(drop_pending_updates=True)
