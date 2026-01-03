import os, threading, asyncio, logging
from flask import Flask, request, abort
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# --- إعدادات الفريق والهوية ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_TELEGRAM_ID = 675887303 # ضع هنا الـ ID الخاص بك الذي حصلت عليه من @userinfobot

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Empire OS: Elite Security Team Active</h1>"

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    user_id = update.effective_user.id
    user_text = update.message.text

    # فحص الهوية الصارم
    if MY_TELEGRAM_ID and user_id != MY_TELEGRAM_ID:
        logger.warning(f"🚫 محاولة اختراق من ID: {user_id}")
        return # لا يرد البوت على الغرباء نهائياً

    try:
        llm = ChatGroq(temperature=0.2, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
        
        # توجيه الطلب للموظف المناسب
        if any(word in user_text.lower() for word in ["أمن", "حماية", "اختراق", "تأمين", "ثغرة", "security"]):
            system_prompt = (
                "أنت (خبير أمن المعلومات - CISO) في Empire OS. مهمتك حماية النظام من الاختراق، "
                "إجراء اختبارات اختراق دورية، وتشفير البيانات. ردك يجب أن يكون تقنياً وحازماً وبالعربية."
            )
        else:
            system_prompt = (
                "أنت المدير التنفيذي لـ Empire OS. خبير مالي تركز على أعلى عائد من أفضل 100 شركة. "
                "لديك فريق أمني يحميك. رد بالعربية."
            )

        resp = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_text)
        ])
        await update.message.reply_text(resp.content)

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        await update.message.reply_text("⚠️ النظام في وضع الصيانة الأمنية حالياً.")

def run_bot():
    if not TOKEN: return
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    bot_app.run_polling(close_loop=False, stop_signals=None)

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

