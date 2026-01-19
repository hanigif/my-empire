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

# نظام التشفير السيادي
S_KEY = os.environ.get("SOVEREIGN_KEY")
if not S_KEY:
    S_KEY = Fernet.generate_key().decode()
    logging.warning(f"⚠️ Generated New Key: {S_KEY}")
cipher_suite = Fernet(S_KEY.encode())

app = Flask(__name__)

# --- 2. المحركات الذكية (Multi-Brain System) ---
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

def get_board_decision(task, sys_msg="You are the Senior Sovereign Compliance Manager 2026."):
    res = llm_gemini.invoke([SystemMessage(content=sys_msg), HumanMessage(content=task)])
    return res.content if hasattr(res, 'content') else str(res)

# --- 3. محرك التنفيذ (المنتج الرقمي) ---
def sovereign_vault_process(raw_data):
    clean_text = get_board_decision(
        f"Remove personal identities from this data: {raw_data}",
        sys_msg="You are a Data Sanitizer. Return ONLY the anonymized text."
    )
    encrypted = cipher_suite.encrypt(clean_text.encode())
    return encrypted.decode()

# --- 4. رادار الصيد (Intel Intelligence) ---
def deep_sovereign_hunting():
    try:
        query = "Swedish companies data privacy fines 2025 IMY compliance gap"
        raw_results = search_tool.run(query)
        analysis_prompt = f"Analyze and find ONE Swedish company to target from this: {raw_results[:1000]}"
        report = get_board_decision(analysis_prompt)
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={"chat_id": MY_ID, "text": f"🎯 **هدف سيادي جديد:**\n\n{report}"})
    except Exception as e:
        logging.error(f"Hunting Error: {e}")

scheduler = BackgroundScheduler(daemon=True, timezone=SWEDEN_TZ)
scheduler.add_job(func=deep_sovereign_hunting, trigger="interval", hours=3)
scheduler.start()

# --- 5. واجهة الويب والـ API ---
@app.route('/')
def home():
    now_sw = datetime.datetime.now(SWEDEN_TZ).strftime('%Y-%m-%d %H:%M:%S')
    return f"<h1>SOVEREIGN CORE v1.0</h1><p>Status: ACTIVE | Time: {now_sw}</p>"

@app.route('/api/v1/protect', methods=['POST'])
def protect_api():
    incoming = request.json.get("payload")
    if not incoming: return jsonify({"error": "Empty"}), 400
    try:
        protected = sovereign_vault_process(incoming)
        return jsonify({"status": "Sovereign Protected", "data": protected})
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- 6. معالجة الرسائل ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    task = update.message.text.strip()
    
    if task == "اصطاد":
        threading.Thread(target=deep_sovereign_hunting).start()
        await update.message.reply_text("⚖️ جاري تفعيل الرادار...")
        return

    response = get_board_decision(task)
    await update.message.reply_text(response)

# --- 7. محرك الإقلاع (The Core Launcher) ---
async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    await application.bot.delete_webhook(drop_pending_updates=True)
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    logging.info("🚀 الإمبراطورية تعمل!")
    while True: await asyncio.sleep(1)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, use_reloader=False), daemon=True).start()
    asyncio.run(main())
