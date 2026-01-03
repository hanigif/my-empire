import os
import threading
import asyncio
from flask import Flask
import yfinance as yf
import plotly.express as px
import plotly.io as pio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# ==========================================
# إعدادات الهوية (سحب آمن من إعدادات السيرفر)
# ==========================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

app = Flask(__name__)

# إعداد ذكاء المدير التنفيذي (Llama 3.3)
# يتم تفعيله فقط إذا كانت المفاتيح موجودة
if GROQ_API_KEY:
    llm = ChatGroq(
        temperature=0.3, 
        model_name="llama-3.3-70b-versatile", 
        groq_api_key=GROQ_API_KEY
    )
else:
    llm = None

# --- واجهة الموقع (لوحة تحكم الإمبراطورية) ---
@app.route('/')
def index():
    try:
        # مراقبة عمالقة السوق كعينة للـ 100 شركة
        tickers = ["NVDA", "AAPL", "MSFT", "AMZN", "TSLA"]
        df = yf.download(tickers, period="1d", interval="5m")['Close']
        fig = px.line(df, title="Empire OS: Strategic Assets Pulse (Top 100 Watchlist)")
        fig.update_layout(template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a")
        graph_html = pio.to_html(fig, full_html=False)
        
        return f"""
        <body style='background:#0f172a; color:white; font-family:sans-serif; text-align:center; padding: 40px;'>
            <h1 style='color:#38bdf8; font-size: 2.5em;'>Empire Financial OS - v1.1</h1>
            <p style='color:#94a3b8;'>نظام الإمبراطورية المالي يعمل الآن. المدير والوكلاء متصلون عبر تلغرام.</p>
            <div style='margin:30px auto; width:95%; border-radius:15px; overflow:hidden; border:1px solid #334155; box-shadow: 0 10px 30px rgba(0,0,0,0.5);'>
                {graph_html}
            </div>
            <div style='margin-top:20px; color:#10b981;'>الحالة: متصل وآمن (Secret Scanning Protected) ✅</div>
        </body>
        """
    except Exception as e:
        return f"<body style='background:#0f172a; color:white;'><h1>Empire OS Live</h1><p>جاري المزامنة... {str(e)}</p></body>"

# --- منطق ذكاء المدير التنفيذي (AI Logic) ---
async def process_ai_response(user_input):
    if not llm:
        return "⚠️ عذراً، مفتاح GROQ_API_KEY غير مفعّل في إعدادات السيرفر."
    
    system_prompt = """
    أنت المدير التنفيذي (CEO) لنظام Empire OS. 
    استراتيجيتك: التركيز على أفضل 100 شركة لتحقيق أعلى عائد.
    لديك فريق وكلاء (المحلل، المبرمج، خبير المخاطر).
    رد باللغة العربية بأسلوب استراتيجي، مالي، واحترافي.
    """
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_input)]
    response = llm.invoke(messages)
    return response.content

# --- تعامل البوت مع رسائل تلغرام ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_text = update.message.text
    
    temp_msg = await update.message.reply_text("🔎 المدير التنفيذي يتشاور مع فريق الوكلاء...")
    
    try:
        answer = await process_ai_response(user_text)
        await context.bot.edit_message_text(chat_id=chat_id, message_id=temp_msg.message_id, text=answer)
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطأ فني: {str(e)}")

def run_telegram_bot():
    if not TELEGRAM_TOKEN:
        print("❌ فشل تشغيل البوت: TELEGRAM_TOKEN غير موجود!")
        return

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("🤖 [Empire System] البوت يعمل الآن في الخلفية...")
    application.run_polling()

# --- بدء تشغيل النظام ---
if __name__ == '__main__':
    # 1. إطلاق البوت في خيط خلفي
    t = threading.Thread(target=run_telegram_bot, daemon=True)
    t.start()
    
    # 2. إطلاق الموقع (Flask)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
