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

# --- 2. المحركات السيادية (تعدد العقول) ---
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
            logging.warning(f"Gemini error: {e}")
            return llm_backup.invoke(messages)

llm_gemini = Gemini2026Manager(GOOGLE_KEY) if GOOGLE_KEY else llm_backup

def get_board_decision(task):
    res = llm_gemini.invoke([
        SystemMessage(content="You are the Sovereign Compliance Manager. Analyze strictly for Swedish laws 2026."),
        HumanMessage(content=task)
    ])
    return res.content if hasattr(res, 'content') else str(res)

# --- 3. وظيفة التصدير لـ GitHub ---
def export_asset_to_github(content, filename):
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        ts = datetime.datetime.now(SWEDEN_TZ).strftime("%Y-%m-%d %H:%M")
        repo.create_file(f"assets/{filename}", f"Sovereign Asset {ts}", content)
        return True
    except Exception as e:
        logging.error(f"GitHub Export Error: {e}")
        return False

# --- 4. نظام الصيد والتعلم الآلي (Autonomous Hunting) ---
def auto_hunting_cycle():
    global AUTO_PRODUCTION_COUNT
    now_ts = datetime.datetime.now(SWEDEN_TZ).strftime('%H:%M')
    logging.info(f"[*] جولة الصيد السيادي بدأت: {now_ts}")
    
    sectors = ["MedTech Stockholm", "Fintech Gothenburg", "E-health Sweden"]
    target_sector = random.choice(sectors)
    
    try:
        # البحث عن شركات حقيقية تواجه مشاكل امتثال
        raw_data = search_tool.run(f"Innovative {target_sector} companies 2026 data privacy challenges")
        
        prompt = f"Based on this data: {raw_data[:2000]}. Identify ONE real company and write a 'Sovereign Compliance Audit' in SWEDISH. Focus on 2026 laws."
        result = get_board_decision(prompt)
        
        filename = f"Audit_{target_sector.replace(' ', '_')}_{now_ts.replace(':', '')}.md"
        if export_asset_to_github(result, filename):
            AUTO_PRODUCTION_COUNT += 1
            HUNTING_LOG.append(f"[{now_ts}] صيد ناجح: {target_sector}")
            # إرسال تنبيه للقائد
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          json={"chat_id": MY_ID, "text": f"🎯 **صيد سيادي جديد!**\n📂 تم فحص قطاع: {target_sector}\n📄 الملف: {filename}"})
    except Exception as e:
        logging.error(f"Hunting Cycle Error: {e}")

# المجدول الزمني (كل ساعتين جولة صيد)
scheduler = BackgroundScheduler(daemon=True, timezone=SWEDEN_TZ)
scheduler.add_job(func=auto_hunting_cycle, trigger="interval", hours=2)
scheduler.start()

# --- 5. معالجة رسائل القائد ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    task = update.message.text.strip()
    
    if task.lower() in ["اختبار", "test"]:
        await update.message.reply_text("⚖️ المختبر يعمل بكفاءة. النظام السيادي مستقر.")
        return

    await update.message.reply_text("⚖️ جاري استشارة العقول السيادية...")
    response = get_board_decision(task)
    await update.message.reply_text(response)

# --- 6. بوابة الويب (Sovereign Gate) ---
@app.route('/')
def home():
    uptime = str(datetime.datetime.now(SWEDEN_TZ) - EMPIRE_START_TIME).split('.')[0]
    return {
        "status": "SOVEREIGN_SYSTEM_ACTIVE",
        "produced_assets": AUTO_PRODUCTION_COUNT,
        "uptime": uptime,
        "sweden_time": datetime.datetime.now(SWEDEN_TZ).strftime('%Y-%m-%d %H:%M:%S'),
        "recent_activity": HUNTING_LOG[-5:]
    }

# --- 7. محرك الإقلاع ---
async def main_bot():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    await application.bot.delete_webhook(drop_pending_updates=True)
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(1)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, use_reloader=False), daemon=True).start()
    try:
        asyncio.run(main_bot())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Shutdown.")
