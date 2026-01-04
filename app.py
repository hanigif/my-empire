import manager_tools
import os, threading, asyncio, logging, datetime, pytz
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# --- الإعدادات السيادية ---
logging.basicConfig(level=logging.INFO)
# يفضل دائماً سحب التوكن من Environment Variables لأمان مشروعك
TOKEN = os.environ.get("TELEGRAM_TOKEN") 
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = 6758877303
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

app = Flask(__name__)

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # حماية سيادية: الرد فقط على صاحب الشركة
    if not update.message or update.effective_user.id != MY_ID: 
        return
    
    llm = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
    
    system_instruction = (
        f"أنت المدير السيادي. الوقت الآن في السويد: {datetime.datetime.now(SWEDEN_TZ).strftime('%Y-%m-%d %H:%M:%S')}. "
        "مهمتك هي إدارة وتطوير الشركة. لديك الآن أدوات خارجية (Internet Search & Memory) "
        "موجودة في ملف manager_tools. يمكنك طلب تنفيذها عند الحاجة."
    )
    
    try:
        response = llm.invoke([SystemMessage(content=system_instruction), HumanMessage(content=update.message.text)])
        await update.message.reply_text(response.content)
    except Exception as e:
        logging.error(f"LLM Error: {e}")

async def main():
    # بناء تطبيق التلغرام مع تعطيل إشارات النظام لتجنب خطأ الـ Thread
    application = ApplicationBuilder().token(TOKEN).build()
    
    # تطهير الاتصالات القديمة
    await application.bot.delete_webhook(drop_pending_updates=True)
    
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    await application.initialize()
    await application.start()
    
    # سحب الرسائل
    await application.updater.start_polling(drop_pending_updates=True)
    
    # الحفاظ على الحلقة نشطة
    while True:
        await asyncio.sleep(1)

@app.route('/')
def home(): 
    return f"Sovereign Empire OS - Active. Sweden Time: {datetime.datetime.now(SWEDEN_TZ)}"

if __name__ == '__main__':
    # السر هنا: تشغيل Flask في خيط منفصل (Daemon)
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True)
    flask_thread.start()
    
    # تشغيل التلغرام في الخيط الرئيسي (Main Thread) لحل مشكلة ValueError
    asyncio.run(main())


