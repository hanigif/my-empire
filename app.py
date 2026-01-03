import os, threading, asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# إعدادات ثابتة
TOKEN = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_TELEGRAM_ID = "6758877303" 

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Empire OS: Core Active</h1>"

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update or not update.message or not update.message.text: return
    user_id = str(update.effective_user.id)

    if user_id != MY_TELEGRAM_ID:
        await update.message.reply_text("⚠️ الوصول للمدير فقط.")
        return

    try:
        llm = ChatGroq(temperature=0.3, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
        user_text = update.message.text

        if any(word in user_text.lower() for word in ["أمن", "حماية", "اختراق", "سايبر"]):
            system_msg = "أنت (سايبر) المسؤول الأمني لـ Empire OS. رد بلهجة تقنية حازمة وبالعربية."
        else:
            system_msg = "أنت المدير التنفيذي لـ Empire OS. خبير مالي في أفضل 100 شركة. رد باحترافية وبالعربية."

        response = llm.invoke([SystemMessage(content=system_msg), HumanMessage(content=user_text)])
        await update.message.reply_text(response.content)
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")

def run_bot_forever():
    # إنشاء حلقة أحداث جديدة وتثبيتها لهذا الخيط
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # بناء التطبيق مع إيقاف ميزة إشارات التوقف لتجنب تضاربها مع Flask
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    print("🚀 جاري بدء تشغيل البوت...")
    # استخدام سياق التشغيل المتوافق
    application.run_polling(drop_pending_updates=True, stop_signals=None)

if __name__ == '__main__':
    # تشغيل البوت في خيط منفصل
    t = threading.Thread(target=run_bot_forever, daemon=True)
    t.start()
    
    # تشغيل Flask
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
