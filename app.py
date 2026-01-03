import os, threading, asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# إعدادات الوصول (تأكد أن هذه القيم مطابقة لحسابك)
TOKEN = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_TELEGRAM_ID = "6758877303" 

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Empire OS: Online & Secure</h1>"

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    user_id = str(update.effective_user.id)
    
    # التحقق من الهوية (المدير فقط)
    if user_id != MY_TELEGRAM_ID:
        await update.message.reply_text(f"⚠️ وصول مرفوض. النظام محمي لمدير واحد فقط.")
        return

    try:
        # إعداد الذكاء الاصطناعي
        llm = ChatGroq(temperature=0.3, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
        user_text = update.message.text

        # التبديل الذكي بين المدير وسايبر
        if any(word in user_text.lower() for word in ["أمن", "حماية", "اختراق", "تأمين", "سايبر"]):
            system_msg = "أنت (سايبر) المسؤول الأمني لـ Empire OS. رد بلهجة تقنية حازمة وبالعربية."
        else:
            system_msg = "أنت المدير التنفيذي لـ Empire OS. خبير مالي في أفضل 100 شركة. رد باحترافية وبالعربية."

        response = llm.invoke([
            SystemMessage(content=system_msg),
            HumanMessage(content=user_text)
        ])
        await update.message.reply_text(response.content)
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في المعالجة: {str(e)}")

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # بناء البوت مع ميزة مسح التحديثات القديمة (تنظيف الـ Conflict)
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    print("🚀 Empire OS: جاري التشغيل والتحقق من الهوية...")
    bot_app.run_polling(drop_pending_updates=True, close_loop=False, stop_signals=None)

if __name__ == '__main__':
    # تشغيل البوت في خلفية السيرفر
    threading.Thread(target=run_bot, daemon=True).start()
    # تشغيل سيرفر ويب Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
