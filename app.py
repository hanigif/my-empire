import os
import logging
from datetime import datetime
import pytz
from flask import Flask
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq

# 1. الإعدادات واللوغز
logging.basicConfig(level=logging.INFO)
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')
app = Flask(__name__)

# 2. محرك الذكاء الاصطناعي (Groq)
llm = ChatGroq(
    temperature=0.3,
    model_name="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

def get_sweden_time():
    return datetime.now(SWEDEN_TZ).strftime('%Y-%m-%d %H:%M:%S')

# 3. منطق المدير السيادي
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    system_prompt = f"أنت 'المدير السيادي'. هدفك تطوير منتجك. توقيت السويد: {get_sweden_time()}"
    
    try:
        response = llm.invoke([("system", system_prompt), ("human", user_text)])
        await update.message.reply_text(response.content)
    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("النواة السيادية تعمل. أنا جاهز يا مدير.")

# 4. وظيفة تشغيل البوت
def run_bot():
    token = os.getenv("TELEGRAM_TOKEN")
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling(drop_pending_updates=True)

# 5. مسار Flask لـ Render
@app.route('/')
def home():
    return f"Sovereign Manager Active. Time: {get_sweden_time()}"

if __name__ == "__main__":
    # تشغيل البوت في خيط منفصل ببساطة كما كنا نفعل
    threading.Thread(target=run_bot, daemon=True).start()
    # تشغيل Flask
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
