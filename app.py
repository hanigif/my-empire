import os, threading, asyncio, logging, datetime, pytz, time, requests, random
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram.error import TimedOut, NetworkError
from apscheduler.schedulers.background import BackgroundScheduler
from github import Github 
from google import genai 
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

# --- 1. الإعدادات الأساسية ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN = os.environ.get("TELEGRAM_TOKEN")
GK_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") 
REPO_NAME = "hanigif/Sovereign-Assets"
MY_ID = 6758877303  
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

app = Flask(__name__)
EMPIRE_START_TIME = datetime.datetime.now(SWEDEN_TZ)
HUNTING_LOG = []

# --- 2. المحركات السيادية المدمجة (بدلاً من الملف الخارجي) ---
llm_backup = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
search_tool = DuckDuckGoSearchRun()

class Gemini2026Manager:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash"
    def invoke(self, messages):
        prompt = messages[-1].content if isinstance(messages, list) else str(messages)
        try:
            response = self.client.models.generate_content(model=self.model_id, contents=prompt)
            return type('Response', (object,), {'content': response.text})
        except: return llm_backup.invoke(messages)

llm_gemini = Gemini2026Manager(GOOGLE_KEY) if GOOGLE_KEY else llm_backup

def get_board_decision(task):
    res = llm_gemini.invoke([
        SystemMessage(content="You are the Sovereign Compliance Manager 2026. Focus on Swedish Law."),
        HumanMessage(content=task)
    ])
    return res.content if hasattr(res, 'content') else str(res)

# --- 3. نظام النبض والصيد الآلي ---
def auto_learning_cycle():
    now = datetime.datetime.now(SWEDEN_TZ).strftime('%H:%M:%S')
    logging.info(f"[*] نبضة سيادية دورية: {now}")
    try:
        # البحث عن شركة سويدية حقيقية تعاني من مشاكل بيانات
        sector = random.choice(["MedTech Stockholm", "Fintech Sweden"])
        raw_data = search_tool.run(f"Swedish {sector} companies 2026 GDPR privacy challenges")
        result = get_board_decision(f"Analyze this data and find one company to target: {raw_data[:1000]}")
        HUNTING_LOG.append(f"[{now}] تم فحص: {sector}")
        if len(HUNTING_LOG) > 10: HUNTING_LOG.pop(0)
    except Exception as e:
        logging.error(f"Auto Cycle Error: {e}")

scheduler = BackgroundScheduler(daemon=True, timezone=SWEDEN_TZ)
scheduler.add_job(func=auto_learning_cycle, trigger="interval", hours=1)
scheduler.start()

# --- 4. معالجة رسائل القائد ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    task = update.message.text.strip()
    
    if task.lower() in ["اختبار", "test lab"]:
        await update.message.reply_text("⚖️ جاري تشغيل المختبر السيادي... النظام مستقر.")
        return

    await update.message.reply_text("⚖️ جاري استشارة العقول السيادية...")
    try:
        response = get_board_decision(task)
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"⚠️ عطل فني: {str(e)[:50]}")

# --- 5. بوابة الويب (التصميم الاحترافي الذي اخترته) ---
@app.route('/')
def home():
    now_sw = datetime.datetime.now(SWEDEN_TZ).strftime('%Y-%m-%d %H:%M:%S')
    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>Sovereign Gate | 2026</title>
        <style>
            body {{ background: #050505; color: #f0f0f0; font-family: sans-serif; text-align: center; margin: 0; }}
            .hero {{ padding: 100px 20px; background: radial-gradient(circle, #0d1a0d 0%, #050505 100%); border-bottom: 1px solid #1a331a; }}
            h1 {{ color: #00ff41; font-size: 3.5em; text-shadow: 0 0 20px rgba(0,255,65,0.4); }}
            .card {{ background: #111; border: 1px solid #1a1a1a; padding: 20px; width: 280px; border-radius: 12px; display: inline-block; margin: 10px; vertical-align: top; }}
            .status-footer {{ background: #000; padding: 15px; color: #00ff41; position: fixed; bottom: 0; width: 100%; font-family: monospace; border-top: 1px solid #1a331a; }}
        </style>
    </head>
    <body>
        <div class="hero">
            <h1>SOVEREIGN GATE</h1>
            <p style="font-size:1.2em; color:#888;">تأمين بيانات الرعاية الصحية السويدية 2026. امتثال سيادي كامل.</p>
            <a href="https://t.me/Htestai" style="background:#00ff41; color:#000; padding:15px 30px; text-decoration:none; font-weight:bold; border-radius:5px;">دخول غرفة العمليات</a>
        </div>
        <div style="padding: 50px;">
            <div class="card"><h3>🛡️ حراسة البيانات</h3><p>تشفير محلي سيادي متوافق مع قوانين 2026.</p></div>
            <div class="card"><h3>⚖️ تدقيق آلي</h3><p>مراقبة حية للشركات السويدية وثغرات الامتثال.</p></div>
        </div>
        <div class="status-footer">SYSTEM_STATUS: ACTIVE | TIME: {now_sw}</div>
    </body>
    </html>
    """

# --- 6. محرك الإقلاع الصامد ---
async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    # محاولة التشغيل مع تخطي أخطاء الشبكة
    for i in range(3):
        try:
            await application.bot.delete_webhook(drop_pending_updates=True)
            await application.initialize()
            await application.start()
            await application.updater.start_polling(drop_pending_updates=True)
            logging.info("🚀 الإمبراطورية تعمل!")
            break
        except: 
            logging.warning("إعادة محاولة الاتصال...")
            await asyncio.sleep(5)
    
    while True: await asyncio.sleep(1)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, use_reloader=False), daemon=True).start()
    asyncio.run(main())
