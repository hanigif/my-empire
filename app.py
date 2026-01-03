import os, threading, asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# إحضار المفاتيح
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GK_KEY = os.environ.get("GROQ_API_KEY")

# الرقم الصحيح كما ظهر في رسالتك
MY_TELEGRAM_ID = 6758877303 

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Empire OS: Identity Control Center</h1>"

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    # تحويل كلاهما إلى نص لضمان التطابق 100%
    user_id = str(update.effective_user.id)
    allowed_id = str(MY_TELEGRAM_ID)

    # التحقق المرن والجازم
    if allowed_id and user_id != allowed_id:
        await update.message.reply_text(f"⚠️ الوصول محصور للمدير فقط. رقمك الحالي: {user_id}")
        return

    try:
        llm = ChatGroq(temperature=0.3, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
        
        user_text = update.message.text
        if any(word in user_text.lower() for word in ["أمن", "حماية", "اختراق", "تأمين", "ثغرة"]):
            system_prompt = "أنت (سايبر) خبير أمن المعلومات في Empire OS. رد بحزم وتقنية وبالعربية."
        else:
            system_prompt = "أنت المدير التنفيذي لـ Empire OS. خبير مالي في أفضل 100 شركة. رد باحترافية وبالعربية."

        resp = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_text)
        ])
        await update.message.reply_text(resp.content)
    except Exception as e:
        await update.message.reply_text(f"⚠️ مشكلة فنية: {str(e)}")

def run_bot():
    if not TOKEN: return
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    bot_app.run_polling(drop_pending_updates=True, close_loop=False, stop_signals=None)

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
