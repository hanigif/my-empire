import os, threading, asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# إحضار المفاتيح من البيئة
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GK_KEY = os.environ.get("GROQ_API_KEY")

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Empire OS: Active</h1><p>المدير يعمل الآن بنظام التوافق مع السيرفر.</p>"

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    try:
        # استشارة المدير (Groq)
        llm = ChatGroq(temperature=0.3, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
        resp = llm.invoke([
            SystemMessage(content="أنت المدير التنفيذي لـ Empire OS. هدفك أعلى عائد من أفضل 100 شركة. رد بالعربية."),
            HumanMessage(content=update.message.text)
        ])
        await update.message.reply_text(resp.content)
    except Exception as e:
        await update.message.reply_text(f"⚠️ عذراً، واجهت مشكلة في التحليل: {str(e)}")

def run_bot():
    if not TOKEN: return
    
    # إعداد حلقة الأحداث (Event Loop)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # بناء البوت
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    print("🤖 [Empire OS] البوت يبدأ الآن في وضع التوافق...")
    
    # الحل السحري: تعطيل إشارات النظام ليعمل في خيط خلفي
    bot_app.run_polling(close_loop=False, stop_signals=None)

if __name__ == '__main__':
    # تشغيل البوت في خيط خلفي
    threading.Thread(target=run_bot, daemon=True).start()
    
    # تشغيل واجهة الويب
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
