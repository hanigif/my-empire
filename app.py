import os, threading, asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# إحضار المفاتيح
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_TELEGRAM_ID = 675887303 

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Empire OS: Online</h1><p>تم حل مشكلة التضارب بنجاح.</p>"

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    user_id = update.effective_user.id
    if MY_TELEGRAM_ID and user_id != MY_TELEGRAM_ID:
        await update.message.reply_text(f"⚠️ الوصول محصور للمدير فقط. رقمك: {user_id}")
        return

    try:
        llm = ChatGroq(temperature=0.3, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
        resp = llm.invoke([
            SystemMessage(content="أنت المدير التنفيذي لـ Empire OS. هدفك أعلى عائد من أفضل 100 شركة. رد بالعربية."),
            HumanMessage(content=update.message.text)
        ])
        await update.message.reply_text(resp.content)
    except Exception as e:
        await update.message.reply_text(f"⚠️ مشكلة فنية: {str(e)}")

def run_bot():
    if not TOKEN: return
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # بناء البوت مع ميزة مسح التحديثات العالقة
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    print("🚀 جاري تنظيف الاتصالات القديمة وبدء البوت...")
    
    # الحل البرمجي لـ Conflict: مسح أي اتصال قديم (drop_pending_updates)
    bot_app.run_polling(drop_pending_updates=True, close_loop=False, stop_signals=None)

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
