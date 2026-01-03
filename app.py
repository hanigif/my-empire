import os, threading, asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# إحضار المفاتيح
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GK_KEY = os.environ.get("GROQ_API_KEY")

app = Flask(__name__)

@app.route('/')
def home():
    return f"Status: Server is Active. Bot Token Present: {bool(TOKEN)}"

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # المدير يرد فوراً لتأكيد العمل
    await update.message.reply_text("✅ المدير استلم رسالتك، جاري الربط مع Groq...")
    try:
        llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
        resp = llm.invoke([SystemMessage(content="أنت مدير مالي"), HumanMessage(content=update.message.text)])
        await update.message.reply_text(resp.content)
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في Groq: {str(e)}")

def run_bot():
    if not TOKEN:
        print("❌ خطأ حرج: TELEGRAM_TOKEN غير موجود!")
        return
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    print("🤖 البوت بدأ بالعمل الآن...")
    bot_app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
