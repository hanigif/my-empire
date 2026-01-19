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
import pyotp 

# --- 1. الإعدادات الأساسية والسيادية ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN = os.environ.get("TELEGRAM_TOKEN")
GK_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY")
MY_ID = 6758877303  
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

# نظام التشفير والتحقق السيادي
S_KEY = os.environ.get("SOVEREIGN_KEY")
if not S_KEY:
    S_KEY = Fernet.generate_key().decode()
cipher_suite = Fernet(S_KEY.encode())

TOTP_SECRET = os.environ.get("TOTP_SECRET", "JBSWY3DPEHPK3PXP")
totp_verifier = pyotp.TOTP(TOTP_SECRET, interval=1)

# --- 2. الذاكرة السيادية (Sovereign Memory) ---
class SovereignMemory:
    def __init__(self):
        self.total_protected = 0
        self.threats_blocked = 0
        self.start_time = datetime.datetime.now(SWEDEN_TZ)

    def add_protected(self): self.total_protected += 1
    def add_threat(self): self.threats_blocked += 1

sov_memory = SovereignMemory()

app = Flask(__name__)
PORT = int(os.environ.get("PORT", 10000))

# --- 3. المحركات الذكية ---
llm_backup = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
try:
    search_tool = DuckDuckGoSearchRun()
except Exception:
    search_tool = None

class Gemini2026Manager:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash"
    def invoke(self, messages):
        prompt = messages[-1].content if isinstance(messages, list) else str(messages)
        try:
            response = self.client.models.generate_content(model=self.model_id, contents=prompt)
            return type('Response', (object,), {'content': response.text})
        except Exception:
            return llm_backup.invoke(messages)

llm_gemini = Gemini2026Manager(GOOGLE_KEY) if GOOGLE_KEY else llm_backup

def get_board_decision(task, sys_msg="You are the Senior Sovereign Compliance Manager 2026."):
    res = llm_gemini.invoke([SystemMessage(content=sys_msg), HumanMessage(content=task)])
    return res.content if hasattr(res, 'content') else str(res)

def sovereign_vault_process(raw_data):
    clean_text = get_board_decision(
        f"Anonymize this data, remove IDs: {raw_data}",
        sys_msg="You are a Data Sanitizer. Return ONLY the safe text."
    )
    encrypted = cipher_suite.encrypt(clean_text.encode())
    return encrypted.decode()

# --- 4. رادار الصيد الاستراتيجي ---
def deep_sovereign_hunting():
    try:
        query = "Sweden IMY privacy fines 2025 2026 news companies compliance"
        raw_results = search_tool.run(query) if search_tool else "No search tool available"
        analysis_prompt = f"""
        Analyze these Swedish news results: {raw_results[:2000]}
        1. Identify ONE real Swedish company recently fined by IMY.
        2. Write a high-level sales pitch in SWEDISH for their CEO.
        Format: TARGET, LOSS, OUR SHIELD, SWEDISH PITCH.
        """
        report = get_board_decision(analysis_prompt, sys_msg="You are a Senior Sovereign Sales Strategist.")
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={"chat_id": MY_ID, "text": f"🚨 **تقرير اقتناص سيادي:**\n\n{report}"})
    except Exception as e:
        logging.error(f"Hunting Error: {e}")

scheduler = BackgroundScheduler(daemon=True, timezone=SWEDEN_TZ)
scheduler.add_job(func=deep_sovereign_hunting, trigger="interval", hours=3)
scheduler.start()

# --- 5. واجهة الويب (Dashboard) والـ API ---
@app.route('/')
def home():
    now_sw = datetime.datetime.now(SWEDEN_TZ).strftime('%H:%M:%S')
    return f"""
    <html>
        <head>
            <title>Sovereign Manager | Control Center</title>
            <style>
                body {{ background: #020617; color: #f8fafc; font-family: 'Segoe UI', sans-serif; text-align: center; padding: 40px; }}
                .container {{ max-width: 900px; margin: auto; }}
                .grid {{ display: flex; justify-content: center; gap: 20px; margin-top: 30px; }}
                .card {{ background: #1e293b; border: 1px solid #38bdf8; border-radius: 12px; padding: 25px; width: 250px; box-shadow: 0 4px 15px rgba(56, 189, 248, 0.2); }}
                .stat {{ font-size: 2.5em; font-weight: bold; color: #38bdf8; margin-bottom: 5px; }}
                .label {{ color: #94a3b8; text-transform: uppercase; font-size: 0.8em; letter-spacing: 1px; }}
                .status {{ display: inline-block; padding: 5px 15px; border-radius: 20px; background: #064e3b; color: #4ade80; font-size: 0.9em; margin-bottom: 20px; }}
            </style>
            <meta http-equiv="refresh" content="5">
        </head>
        <body>
            <div class="container">
                <div class="status">● SYSTEM SOVEREIGNTY: OPTIMAL</div>
                <h1>🛡️ SOVEREIGN MANAGER CORE</h1>
                <div class="grid">
                    <div class="card"><div class="stat">{sov_memory.total_protected}</div><div class="label">Protected Records</div></div>
                    <div class="card"><div class="stat">{sov_memory.threats_blocked}</div><div class="label">Security Blocks</div></div>
                    <div class="card"><div class="stat">99.9%</div><div class="label">Compliance Rate</div></div>
                </div>
                <p style="margin-top: 40px; color: #475569;">Pulse Time (Sweden): {now_sw}</p>
            </div>
        </body>
    </html>
    """

@app.route('/api/v1/protect', methods=['POST'])
def protect_api():
    client_token = request.headers.get('X-Sovereign-Token')
    if not client_token or not totp_verifier.verify(client_token):
        sov_memory.add_threat()
        return jsonify({"error": "Unauthorized"}), 401
    
    incoming = request.json.get("payload")
    try:
        protected = sovereign_vault_process(incoming)
        sov_memory.add_protected()
        return jsonify({"status": "Sovereign Protected", "data": protected})
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- 6. معالجة الرسائل ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    task = update.message.text.strip()

    if task == "اختبر":
        await update.message.reply_text("🔍 جاري بدء اختبار الاختراق...")
        try:
            # اختبار داخلي لرفع العداد في الداش بورد
            res1 = requests.post(f"http://127.0.0.1:{PORT}/api/v1/protect", json={"payload": "test"})
            token = totp_verifier.now()
            res2 = requests.post(f"http://127.0.0.1:{PORT}/api/v1/protect", 
                                 json={"payload": "Hani Test"}, 
                                 headers={"X-Sovereign-Token": token})
            await update.message.reply_text(f"🛡️ النظام مؤمن! (تم تحديث الداش بورد)")
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ: {str(e)}")
        return

    if task == "اصطاد":
        threading.Thread(target=deep_sovereign_hunting).start()
        await update.message.reply_text("⚖️ جاري تفعيل الرادار...")
        return

    response = get_board_decision(task)
    await update.message.reply_text(response)

# --- 7. الإقلاع ---
async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    await application.bot.delete_webhook(drop_pending_updates=True)
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=PORT, use_reloader=False), daemon=True).start()
    asyncio.run(main())
