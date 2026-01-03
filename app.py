import os, threading, asyncio, logging, time, datetime
import yfinance as yf
import pandas as pd
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# --- الإعدادات اللوجستية ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
TOKEN = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = 6758877303

app = Flask(__name__)

# قاعدة بيانات الـ 100 شركة وأرشيف التعلم
S_P_100 = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK-B", "V", "JNJ", "WMT", "JPM", "MA", "PG", "UNH"] # يمكن إكمالها لـ 100
LEARNING_LOG = "empire_knowledge.txt"

@app.route('/')
def home():
    return f"Empire OS v4.0: Autonomous Learning Engine Online. Knowledge size: {os.path.getsize(LEARNING_LOG) if os.path.exists(LEARNING_LOG) else 0} bytes"

# --- 1. وظيفة التعلم الذاتي والبحث (تشتغل وأنت نائم) ---
async def autonomous_learning_cycle(application):
    while True:
        current_hour = datetime.datetime.now().hour
        logging.info(f"Autonomous Cycle: System is studying market trends... (Hour: {current_hour})")
        
        study_topic = "Advanced Stock Analysis & Cybersecurity Risks in 2026"
        llm = ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
        
        try:
            # محاكاة البحث والتعلم (يمكن ربطها بـ API بحث مستقبلاً)
            learning_prompt = f"البحث في أحدث استراتيجيات الاستثمار لعام 2026 لشركات الـ S&P 100 وتلخيص أهم 5 نصائح لبيعها كمنتج توصيات."
            summary = llm.invoke([HumanMessage(content=learning_prompt)])
            
            with open(LEARNING_LOG, "a", encoding="utf-8") as f:
                f.write(f"\n--- Study Session {datetime.datetime.now()} ---\n{summary.content}\n")
            
            # إذا كانت الساعة 7 صباحاً، أرسل تقرير الصباح للمدير
            if current_hour == 7:
                await application.bot.send_message(chat_id=MY_ID, text="🌅 صباح الخير مدير هاني. لقد أتممت دورة التعلم الليلي. إليك ملخص الفرص الجاهزة للبيع اليوم...")
        
        except Exception as e:
            logging.error(f"Learning Error: {e}")
        
        await asyncio.sleep(7200) # دورة كل ساعتين

# --- 2. رادار صيد الصفقات (المنتج المالي) ---
def analyze_opportunity(ticker):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1mo")
        # حساب بسيط لمؤشر القوة النسبية (RSI) لاكتشاف فرص الشراء
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_price = df['Close'].iloc[-1]
        change = ((current_price - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
        
        status = "HOLD"
        if rsi.iloc[-1] < 30: status = "BUY (Oversold)"
        elif rsi.iloc[-1] > 70: status = "SELL (Overbought)"
        
        return f"📍 {ticker}: ${current_price:.2f} | RSI: {rsi.iloc[-1]:.1f} | Action: {status}", (status != "HOLD")
    except: return None, False

async def operational_radar(application):
    while True:
        for ticker in S_P_100:
            report, is_urgent = analyze_opportunity(ticker)
            if is_urgent:
                await application.bot.send_message(chat_id=MY_ID, text=f"💰 فرصة ذهبية مكتشفة:\n{report}")
        await asyncio.sleep(3600)

# --- 3. معالج الرسائل (الواجهة الاحترافية) ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != MY_ID: return
    
    user_msg = update.message.text
    llm = ChatGroq(temperature=0.3, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
    
    # قراءة ما تعلمه النظام للرد بدقة
    context_data = ""
    if os.path.exists(LEARNING_LOG):
        with open(LEARNING_LOG, "r", encoding="utf-8") as f:
            context_data = f.readlines()[-20:] # آخر 20 سطر مما تعلمه
    
    response = llm.invoke([
        SystemMessage(content=f"أنت Empire OS. استخدم ما تعلمته لتقديم رد احترافي جاهز للبيع كاستشارة مالية: {context_data}"),
        HumanMessage(content=user_msg)
    ])
    await update.message.reply_text(response.content)

# --- نظام التشغيل المتوازي ---
def run_background_loop(application):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # تشغيل الرادار والتعلم معاً
    loop.create_task(autonomous_learning_cycle(application))
    loop.create_task(operational_radar(application))
    loop.run_forever()

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000, use_reloader=False), daemon=True).start()
    
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    threading.Thread(target=run_background_loop, args=(application,), daemon=True).start()
    
    logging.info("Empire OS v4.0 Global Deployment Successful.")
    application.run_polling()
