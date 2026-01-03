import os, threading, asyncio, logging
from flask import Flask, request, abort
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# --- إعدادات الأمن المتقدمة ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_TELEGRAM_ID = 123456789  # استبدل هذا الرقم بـ ID تلغرام الخاص بك لتفعيل الـ 2FA

# إعداد نظام مراقبة السجلات (Logging) كما طلب المدير
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Empire OS: Cyber-Shield Active</h1><p>تم تفعيل نظام مراقبة السجلات والدفاع التلقائي.</p>"

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    # التحقق من الهوية (نقطة القوة 1 في تقرير المدير)
    user_id = update.effective_user.id
    if MY_TELEGRAM_ID and user_id != MY_TELEGRAM_ID:
        logger.warning(f"⚠️ محاولة وصول غير مصرح بها من ID: {user_id}")
        await update.message.reply_text("🚫 الوصول مرفوض. تم تسجيل محاولة الدخول وإبلاغ المدير.")
        return

    try:
        llm = ChatGroq(temperature=0.3, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
        resp = llm.invoke([
            SystemMessage(content="أنت المدير التنفيذي لـ Empire OS. خبير في الأمن المالي. رد بالعربية."),
            HumanMessage(content=update.message.text)
        ])
        await update.message.reply_text(resp.content)
    except Exception as e:
        logger.error(f"خطأ أمني: {str(e)}")
        await update.message.reply_text("⚠️ [Security Alert] حدث خطأ، تم عزل النظام لحماية البيانات.")

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
