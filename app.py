import os, threading, asyncio, logging, datetime, json, pytz
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# --- الإعدادات السيادية (أساس لا يُمس) ---
logging.basicConfig(level=logging.INFO)
TOKEN = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = 6758877303
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

app = Flask(__name__)

# --- وظيفة معالجة الرسائل والربط مع المختبر ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    
    # 1. استدعاء تقرير المختبر (GitHub) فوراً
    lab_info = "جاري فحص المختبر..."
    try:
        from sovereign_lab import run_lab_test
        report = run_lab_test()
        lab_info = report['detail']
    except Exception as e:
        lab_info = f"تنبيه: تعذر جلب بيانات GitHub (السبب: {e})"

    # 2. إعداد المحرك (Llama 3.3)
    llm = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
    
    # 3. دمج البيانات الحقيقية في نظام التوجيه
    current_time = datetime.datetime.now(SWEDEN_TZ).strftime("%Y-%m-%d %H:%M:%S")
    system_instruction = (
        f"أنت المدير السيادي. الوقت الحالي في السويد: {current_time}.\n"
        f"بيانات المزامنة مع GitHub: {lab_info}.\n"
        "مهمتك: إدارة الشركة للوصول لأفضل 100 شركة. استخدم بيانات GitHub أعلاه للإجابة بدقة."
    )
    
    # 4. توليد الرد
    response = llm.invoke([
        SystemMessage(content=system_instruction), 
        HumanMessage(content=update.message.text)
    ])
    await update.message.reply_text(response.content)

# --- محرك التشغيل المستمر ---
async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    # تطهير الـ Webhook لضمان عدم التعارض
    await application.bot.delete_webhook(drop_pending_updates=True)
    
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    logging.info("Sovereign Manager is Live and Monitoring...")
    while True: await asyncio.sleep(1)

@app.route('/')
def home(): return "Sovereign Empire OS v7.2.2 - Lab Active"

if __name__ == '__main__':
    # تشغيل Flask في خيط منفصل لضمان بقاء السيرفر حياً
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    asyncio.run(main())
