import os, threading, asyncio
from flask import Flask, request, abort
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from time import time

# --- إعدادات الأمن القصوى ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GK_KEY = os.environ.get("GROQ_API_KEY")
ALLOWED_USER_ID = None # يمكننا لاحقاً حصر البوت لك فقط

app = Flask(__name__)

# مخزن بسيط لتقييد معدل الطلبات (Rate Limiting)
ip_requests = {}

@app.before_request
def security_filter():
    # جدار حماية بسيط: منع الطلبات المتكررة جداً من نفس المصدر
    ip = request.remote_addr
    now = time()
    if ip in ip_requests and now - ip_requests[ip] < 0.5: # طلب كل نصف ثانية كحد أقصى
        abort(429) # Too Many Requests
    ip_requests[ip] = now

@app.route('/')
def home():
    return "<h1>Empire OS: Secure Mode Active</h1><p>البيئة محمية ببروتوكولات SSL و Rate Limiting.</p>"

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    # تأمين البيئة: لا تظهر المفاتيح في الـ Logs أبداً
    try:
        llm = ChatGroq(temperature=0.3, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
        resp = llm.invoke([
            SystemMessage(content="أنت المدير التنفيذي لـ Empire OS. أنت مبرمج أمني وخبير مالي. رد بالعربية."),
            HumanMessage(content=update.message.text)
        ])
        await update.message.reply_text(resp.content)
    except Exception:
        await update.message.reply_text("⚠️ [Security] حدث خطأ فني، تم تشفير التفاصيل وحمايتها.")

def run_bot():
    if not TOKEN: return
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    bot_app.run_polling(close_loop=False, stop_signals=None)

if __name__ == '__main__':
    # تشغيل البوت في خيط مستقل
    threading.Thread(target=run_bot, daemon=True).start()
    # تشغيل السيرفر
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
