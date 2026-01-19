import os, threading, asyncio, logging, datetime, pytz, time, requests, random
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram.error import TimedOut, NetworkError
from apscheduler.schedulers.background import BackgroundScheduler
from google import genai 
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage
from cryptography.fernet import Fernet

# --- 1. الإعدادات الأساسية والسيادية ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN = os.environ.get("TELEGRAM_TOKEN")
GK_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY")
MY_ID = 6758877303  
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

# نظام التشفير (The Vault Key)
S_KEY = os.environ.get("SOVEREIGN_KEY")
if not S_KEY:
    S_KEY = Fernet.generate_key().decode()
    logging.warning(f"⚠️ تم توليد مفتاح تشفير جديد: {S_KEY}")
cipher_suite = Fernet(S_KEY.encode())

app = Flask(__name__)
EMPIRE_START_TIME = datetime.datetime.now(SWEDEN_TZ)

# --- 2. المحركات الذكية (Multi-Model Brain) ---
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
        except Exception as e:
            logging.error(f"Gemini Failure: {e}")
            return llm_backup.invoke(messages)

llm_gemini = Gemini2026Manager(GOOGLE_KEY) if GOOGLE_KEY else llm_backup

def get_board_decision(task, sys_msg="You are the Senior Sovereign Compliance Manager 2026. Target Swedish companies and solve their IMY/GDPR risks."):
    res = llm_gemini.invoke([SystemMessage(content=sys_msg), HumanMessage(content=task)])
    return res.content if hasattr(res, 'content') else str(res)

# --- 3. محرك التنفيذ (المنتج: التطهير والتشفير) ---
def sovereign_vault_process(raw_data):
    # تطهير البيانات بالذكاء الاصطناعي
    clean_text = get_board_decision(
        f"CRITICAL: Remove all personal identities (Names, IDs, Addresses) from this Swedish data: {raw_data}",
        sys_msg="You are a Data Sanitizer. Return ONLY the anonymized version of the data."
    )
    # تشفير البيانات السيادية
    encrypted = cipher_suite.encrypt(clean_text.encode())
    return encrypted.decode()

# --- 4. رادار الصيد الاستخباراتي (Targeting) ---
def deep_sovereign_hunting():
    now = datetime.datetime.now(SWEDEN_TZ).strftime('%H:%M')
    logging.info(f"[*] تفعيل الرادار السيادي: {now}")
    try:
        query = "Swedish companies IMY data privacy fines 2025 2026 compliance gap"
        raw_results = search_tool.run(query)
        analysis_prompt = f"""
        Analyze this search data: {raw_results[:1500]}
        1. Find ONE real Swedish company facing data risks.
        2. Detail Legal Vulnerability & Potential Fines.
        3. Professional Pitch in Swedish.
        """
        report = get_board_decision(analysis_prompt)
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={"chat_id": MY_ID, "text": f"🎯 **هدف سيادي مرصود!**\n\n{report}"})
    except Exception as e:
        logging.error(f"Hunting Error: {e}")

scheduler = BackgroundScheduler(daemon=True, timezone=SWEDEN_TZ)
scheduler.add_job(func=deep_sovereign_hunting, trigger="interval", hours=3)
scheduler.start()

# --- 5. بوابة الويب المتطورة (Web Interface & API) ---
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
            .hero {{ padding: 80px 20px; background: radial-gradient(circle, #0d1a0d 0%, #050505 100%); border-bottom: 1px solid #1a331a; }}
            h1 {{ color: #00ff41; font-size: 3.5em; text-shadow: 0 0 20px rgba(0,255,65,0.4); }}
            .status-footer {{ background: #000; padding: 15px; color: #00ff41; position: fixed; bottom: 0; width: 100%; font-family: monospace; border-top: 1px solid #1a331a; }}
        </style>
    </head>
    <body>
        <div class="hero">
            <h1>SOVEREIGN GATE v1.0</h1>
            <p style="color:#888;">نظام رصد الامتثال وتشفير البيانات السيادية السويدية 2026.</p>
        </div>
        <div style="padding: 20px;">
            <p>Vault Status: <span style="color:#00ff41;">SECURED (AES-256)</span></p>
            <p>Jurisdiction: Stockholm, Sweden</p>
        </div>
        <div class="status-footer">SYSTEM_STATUS: ACTIVE | RADAR: SCANNING | {now_sw}</div>
    </body>
    </html>
    """

@app.route('/api/v1/protect', methods=['POST'])
def protect_api():
    incoming = request.json.get("payload")
    if not incoming: return jsonify({"error": "Empty payload"}), 400
    try:
        protected = sovereign_vault_process(incoming)
        return jsonify({"{'status': 'Sovereign Protected', 'vault_id': 'SW-2026', 'data': protected}"})
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- 6. معالجة رسائل القائد والتحكم في البوت ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    task = update.message.text.strip()
    
    if task == "اصطاد":
        threading.Thread(target=deep_sovereign_hunting).start()
        await update.message.reply_text("⚖️ جاري تفعيل الرادار السيادي للبحث عن الأهداف...")
        return

    await update.message.reply_text("⚖️ جاري استشارة العقول السيادية...")
    response = get_board_decision(task)
    await update.message.reply_text(response)

# --- 7. محرك الإقلاع المرن (Auto-Recovery) ---
async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    while True:
        try:
            await application.bot.delete_webhook(drop_pending_updates=True)
            await application.initialize()
            await application.start()
            await application.updater.start_polling(drop_pending_updates=True)
            logging.info("🚀 الإمبراطورية تعمل بكامل طاقتها!")
            break
        except Exception as e:
            logging.error(f"Restarting due to error: {e}")
            await asyncio.sleep(10)
    
    while True: await asyncio.sleep(1)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, use_reloader=False), daemon=True).start()
    asyncio.run(main())import os, threading, asyncio, logging, datetime, pytz, time, requests, random
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram.error import TimedOut, NetworkError
from apscheduler.schedulers.background import BackgroundScheduler
from google import genai 
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

# --- 1. الإعدادات الأساسية ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN = os.environ.get("TELEGRAM_TOKEN")
GK_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY")
MY_ID = 6758877303  
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

app = Flask(__name__)
EMPIRE_START_TIME = datetime.datetime.now(SWEDEN_TZ)
HUNTING_LOG = []

# --- 2. المحركات الذكية ---
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
        SystemMessage(content="You are the Senior Sovereign Compliance Manager 2026. Your goal is to identify Swedish companies facing massive IMY fines and provide a high-ticket solution."),
        HumanMessage(content=task)
    ])
    return res.content if hasattr(res, 'content') else str(res)

# --- 3. محرك الصيد الاستخباراتي (Targeting & Fines) ---
def deep_sovereign_hunting():
    now = datetime.datetime.now(SWEDEN_TZ).strftime('%H:%M')
    logging.info(f"[*] تفعيل الرادار للبحث عن الشركات المتضررة: {now}")
    try:
        # البحث عن شركات سويدية تعاني من ثغرات قانونية حقيقية
        query = "Swedish companies data privacy fines 2025 2026 IMY Schrems III compliance gap"
        raw_results = search_tool.run(query)
        
        analysis_prompt = f"""
        Analyze this: {raw_results[:1500]}
        Find ONE real Swedish company (Private or Tech) facing major data compliance risks.
        Provide:
        1. Company Name.
        2. Legal Vulnerability (Detailed).
        3. Potential Fine/Loss.
        4. Proposed Solution (Sovereign Manager).
        5. Professional Pitch in Swedish.
        Language: Arabic for analysis, Swedish for the pitch.
        """
        
        report = get_board_decision(analysis_prompt)
        
        # إرسال التقرير فوراً للقائد
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={"chat_id": MY_ID, "text": f"🎯 **هدف سيادي مرصود!**\n\n{report}"})
        
        HUNTING_LOG.append(f"[{now}] تم رصد هدف متضرر")
    except Exception as e:
        logging.error(f"Hunting Error: {e}")

scheduler = BackgroundScheduler(daemon=True, timezone=SWEDEN_TZ)
# البحث التلقائي كل 3 ساعات
scheduler.add_job(func=deep_sovereign_hunting, trigger="interval", hours=3)
scheduler.start()

# --- 4. معالجة رسائل القائد ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    task = update.message.text.strip()
    
    if task == "اصطاد":
        await update.message.reply_text("⚖️ جاري تشغيل الرادار السيادي للبحث عن أكثر الشركات تضرراً...")
        threading.Thread(target=deep_sovereign_hunting).start()
        return
    
    if task.lower() in ["اختبار", "test lab"]:
        await update.message.reply_text("⚖️ المختبر السيادي مستقر وجاهز.")
        return

    await update.message.reply_text("⚖️ جاري استشارة العقول السيادية...")
    try:
        response = get_board_decision(task)
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"⚠️ عطل فني: {str(e)[:50]}")

# --- 5. بوابة الويب (التصميم الخاص بك) ---
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
            <p style="font-size:1.2em; color:#888;">نظام رصد الامتثال والبيانات السيادية السويدية 2026.</p>
            <a href="https://t.me/Htestai" style="background:#00ff41; color:#000; padding:15px 30px; text-decoration:none; font-weight:bold; border-radius:5px;">دخول غرفة العمليات</a>
        </div>
        <div style="padding: 50px;">
            <div class="card"><h3>🎯 رادار الأهداف</h3><p>البحث عن الشركات المتضررة من قوانين البيانات الجديدة.</p></div>
            <div class="card"><h3>⚖️ حلول 2026</h3><p>تشفير سيادي يمنع الغرامات المليونية لـ IMY.</p></div>
        </div>
        <div class="status-footer">SYSTEM_STATUS: ACTIVE | RADAR: SCANNING | {now_sw}</div>
    </body>
    </html>
    """

# --- 6. محرك الإقلاع ---
async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    for i in range(3):
        try:
            await application.bot.delete_webhook(drop_pending_updates=True)
            await application.initialize()
            await application.start()
            await application.updater.start_polling(drop_pending_updates=True)
            logging.info("🚀 الإمبراطورية تعمل!")
            break
        except: 
            await asyncio.sleep(5)
    
    while True: await asyncio.sleep(1)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, use_reloader=False), daemon=True).start()
    asyncio.run(main())

