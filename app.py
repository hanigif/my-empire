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
AUTO_PRODUCTION_COUNT = 0
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
            response = self.client.models.generate_content(
                model=self.model_id, 
                contents=prompt,
                config={'system_instruction': "You are the Senior Sovereign Compliance Officer (Sweden 2026)."}
            )
            return type('Response', (object,), {'content': response.text})
        except Exception as e:
            logging.error(f"Gemini Error: {e}")
            return llm_backup.invoke(messages)

llm_gemini = Gemini2026Manager(GOOGLE_KEY) if GOOGLE_KEY else llm_backup

def get_board_decision(task):
    res = llm_gemini.invoke([
        SystemMessage(content="You are the Sovereign Compliance Manager. Solve for Swedish companies privacy 2026."),
        HumanMessage(content=task)
    ])
    return res.content if hasattr(res, 'content') else str(res)

# --- 3. نظام الصيد التلقائي ---
def auto_hunting_cycle():
    global AUTO_PRODUCTION_COUNT
    now = datetime.datetime.now(SWEDEN_TZ).strftime('%H:%M')
    try:
        sector = random.choice(["E-health Stockholm", "Fintech Sweden", "MedTech Uppsala"])
        raw_search = search_tool.run(f"Companies in {sector} facing GDPR or AI compliance issues 2026")
        
        report = get_board_decision(f"Based on this: {raw_search[:1500]}. Write a professional audit for one real company found. Language: Swedish.")
        
        HUNTING_LOG.append(f"[{now}] 🎯 صيد: {sector}")
        AUTO_PRODUCTION_COUNT += 1
        
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={"chat_id": MY_ID, "text": f"🎯 **صيد سيادي جديد!**\nتم تحليل قطاع {sector} بنجاح."})
    except Exception as e:
        logging.error(f"Hunting error: {e}")

scheduler = BackgroundScheduler(daemon=True, timezone=SWEDEN_TZ)
scheduler.add_job(func=auto_hunting_cycle, trigger="interval", hours=2)
scheduler.start()

# --- 4. واجهة الويب (The Sovereign Gate) ---
@app.route('/')
def home():
    now_sw = datetime.datetime.now(SWEDEN_TZ).strftime('%Y-%m-%d %H:%M:%S')
    uptime = str(datetime.datetime.now(SWEDEN_TZ) - EMPIRE_START_TIME).split('.')[0]
    logs = "<br>".join(HUNTING_LOG[-5:])
    return f"""
    <html><body style='background:#050505;color:#00ff41;font-family:monospace;padding:50px;'>
    <h1>SOVEREIGN GATE ACTIVE</h1><hr>
    <p>TIME: {now_sw}</p>
    <p>UPTIME: {uptime}</p>
    <p>ASSETS PRODUCED: {AUTO_PRODUCTION_COUNT}</p>
    <h3>RECENT LOGS:</h3>
    <div style='color:#888;'>{logs}</div>
    </body></html>
    """

# --- 5. معالج الرسائل ---
async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == MY_ID:
        response = get_board_decision(update.message.text)
        await update.message.reply_text(response)

# --- 6. التشغيل الرئيسي ---
async def main():
    if not TOKEN:
        print("Error: TELEGRAM_TOKEN not found!")
        return
    
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_response))
    
    await application.bot.delete_webhook(drop_pending_updates=True)
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, use_reloader=False), daemon=True).start()
    
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("System Shutdown.")
