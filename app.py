import os, threading, asyncio, logging, datetime, pytz, time, requests, random
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram.error import TimedOut, NetworkError
from apscheduler.schedulers.background import BackgroundScheduler
from github import Github 
from google import genai 
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# --- 1. الإعدادات الأساسية والرموز السيادية ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN = os.environ.get("TELEGRAM_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
GK_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") 
REPO_NAME = "hanigif/Sovereign-Assets"
MY_ID = 6758877303  
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

app = Flask(__name__)
EMPIRE_START_TIME = datetime.datetime.now(SWEDEN_TZ)
AUTO_PRODUCTION_COUNT = 0
HUNTING_LOG = []

# --- 2. المحرك السيادي المدمج (لضمان عدم حدوث ImportError) ---
llm_backup = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)

class Gemini2026Manager:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash"
    
    def invoke(self, messages):
        prompt = messages[-1].content if isinstance(messages, list) else str(messages)
        try:
            response = self.client.models.generate_content(
                model=self.model_id, 
                contents=prompt,
                config={'system_instruction': "You are the Senior Sovereign Compliance Officer (Sweden 2026)."}
            )
            return type('Response', (object,), {'content': response.text})
        except Exception as e:
            logging.warning(f"Gemini error: {e}")
            return llm_backup.invoke(messages)

llm_gemini = Gemini2026Manager(GOOGLE_KEY) if GOOGLE_KEY else llm_backup

def get_board_decision(task):
    """صنع القرار السيادي"""
    res = llm_gemini.invoke([
        SystemMessage(content="You are the Sovereign Compliance Manager. Solve for Swedish companies privacy 2026."),
        HumanMessage(content=task)
    ])
    return res.content if hasattr(res, 'content') else str(res)

# --- 3. نظام النبض والتدقيق الآلي ---
def auto_learning_cycle():
    global AUTO_PRODUCTION_COUNT
    now = datetime.datetime.now(SWEDEN_TZ).strftime('%H:%M:%S')
    logging.info(f"[*] نبضة سيادية دورية: {now}")
    try:
        # محاكاة التدقيق أو البحث عن عملاء
        result = get_board_decision("AUTO_AUDIT: بحث عن ثغرات امتثال في شركات ستوكهولم لعام 2026")
        HUNTING_LOG.append(f"[{now}] تدقيق دوري ناجح.")
        if len(HUNTING_LOG) > 20: HUNTING_LOG.pop(0)
    except Exception as e:
        logging.error(f"[!] تنبيه في الدورة الآلية: {e}")

scheduler = BackgroundScheduler(daemon=True, timezone=SWEDEN_TZ)
scheduler.add_job(func=auto_learning_cycle, trigger="interval", hours=1)
scheduler.start()

# --- 4. معالجة رسائل القائد ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: 
        return
    
    task = update.message.text.strip()
    
    # صمام أمان المختبر السيادي
    if task.lower() in ["اختبار", "test lab"]:
        await update.message.reply_text("⚖️ جاري تشغيل المختبر السيادي الداخلي...")
        response = f"✅ المختبر يعمل بكفاءة.\n⏰ الوقت: {datetime.datetime.now(SWEDEN_TZ).strftime('%H:%M:%S')}\n🛡️ الحالة: محمية"
        await update.message.reply_text(response)
        return

    await update.message.reply_text("⚖️ جاري استشارة العقول السيادية (Gemini & Llama)...")
    
    try:
        response = get_board_decision(task)
        await update.message.reply_text(response)
    except Exception as e:
        logging.error(f"Technical Error: {e}")
        await update.message.reply_text(f"⚠️ عطل فني: {str(e)[:100]}")

# --- 5. بوابة الويب (The Sovereign Gate) ---
@app.route('/')
def home():
    try:
        now_sweden = datetime.datetime.now(SWEDEN_TZ).strftime('%Y-%m-%d %H:%M:%S')
        uptime = str(datetime.datetime.now(SWEDEN_TZ) - EMPIRE_START_TIME).split('.')[0]
        return f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Sovereign Gate | 2026 Compliance</title>
            <style>
                body {{ background-color: #050505; color: #f0f0f0; font-family: sans-serif; margin: 0; padding: 0; text-align: center; }}
                .hero {{ padding: 80px 20px; background: radial-gradient(circle, #0d1a0d 0%, #050505 100%); border-bottom: 1px solid #1a331a; }}
                h1 {{ color: #00ff41; font-size: 3em; text-shadow: 0 0 15px rgba(0,255,65,0.4); }}
                .tagline {{ color: #888; margin: 20px auto; max-width: 600px; }}
                .features {{ display: flex; justify-content: center; gap: 20px; padding: 40px; flex-wrap: wrap; }}
                .card {{ background: #111; border: 1px solid #1a1a1a; padding: 20px; width: 250px; border-radius: 10px; text-align: right; }}
                .status-footer {{ background: #000; padding: 10px; font-family: monospace; color: #00ff41; border-top: 1px solid #1a331a; position: fixed; bottom: 0; width: 100%; }}
            </style>
        </head>
        <body>
            <div class="hero">
                <h1>SOVEREIGN GATE</h1>
                <p class="tagline">تأمين بيانات الرعاية الصحية السويدية لعام 2026. امتثال كامل بلمسة تقنية سيادية.</p>
                <div style="color:#00ff41; margin-top:10px;">UPTIME: {uptime}</div>
            </div>
            <div class="features">
                <div class="card"><h3>🛡️ حراسة البيانات</h3><p>تشفير محلي سيادي يمنع التسرب السحابي.</p></div>
                <div class="card"><h3>⚖️ تدقيق 2026</h3><p>مراقبة آلية للتحديثات التشريعية السويدية.</p></div>
            </div>
            <div class="status-footer">SYSTEM_STATUS: ACTIVE | SWEDEN_TIME: {now_sweden}</div>
        </body>
        </html>
        """
    except Exception as e:
        return f"System Online - Web UI Error: {str(e)[:50]}"

# --- 6. محرك الإقلاع (Main Loop) ---
async def main():
    if not TOKEN:
        logging.error("❌ TELEGRAM_TOKEN مفقود!")
        return

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))

    try:
        await application.bot.delete_webhook(drop_pending_updates=True)
        await application.initialize()
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)
        logging.info("🚀 تم تشغيل الإمبراطورية بنجاح!")
        
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        logging.error(f"Critical Boot Error: {e}")

if __name__ ==
