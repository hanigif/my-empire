import os, json, datetime, pytz, threading, time, requests, random, logging
from github import Github 
from google import genai 
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage
from flask import Flask

# --- 1. الإعدادات الأساسية ---
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

GK_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") 
REPO_NAME = "hanigif/Sovereign-Assets"
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

EMPIRE_START_TIME = datetime.datetime.now(SWEDEN_TZ)
AUTO_PRODUCTION_COUNT = 0 
HUNTING_LOG = [] 

# --- 2. المحركات السيادية (تعدد العقول) ---
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
                config={'system_instruction': "You are the Senior Sovereign Compliance Officer (Sweden 2026). Analyze strictly for Swedish data laws."}
            )
            return type('Response', (object,), {'content': response.text})
        except Exception as e:
            logging.warning(f"Gemini error: {e}")
            return llm_backup.invoke(messages)

llm_gemini = Gemini2026Manager(GOOGLE_KEY) if GOOGLE_KEY else llm_backup
search_tool = DuckDuckGoSearchRun()

# --- 3. الوظائف التشغيلية ---
def send_telegram_message(message):
    try:
        token = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
        chat_id = "6168694801"
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                      json={"chat_id": chat_id, "text": message}, timeout=10)
    except: pass

def export_to_github(filename, content, commit_message):
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        try:
            contents = repo.get_contents(filename)
            repo.update_file(contents.path, commit_message, content, contents.sha)
        except:
            repo.create_file(filename, commit_message, content)
        return True
    except Exception as e:
        logging.error(f"GitHub Error: {e}")
        return False

# --- 4. مصنع الصيد الذكي (The Aggressive Factory) ---
def autonomous_factory_loop():
    global AUTO_PRODUCTION_COUNT, HUNTING_LOG
    time.sleep(25) # انتظار استقرار السيرفر
    
    targets = [
        "Stockholm MedTech AI privacy", 
        "Swedish fintech cross-border data", 
        "Gothenburg SaaS sensitive data 2026",
        "Private healthcare Sweden digital compliance"
    ]
    
    while True:
        try:
            sector = random.choice(targets)
            ts_now = datetime.datetime.now(SWEDEN_TZ).strftime("%H:%M")
            
            # إدارة سجل النشاط
            if len(HUNTING_LOG) > 50: HUNTING_LOG.pop(0)
            HUNTING_LOG.append(f"[{ts_now}] Hunting in {sector}...")

            # --- التعديل المدمج: ضمان جودة البيانات ---
            raw_leads = search_tool.run(f"Top innovative {sector} companies 2026 Sweden")
            
            if not raw_leads or len(raw_leads) < 50:
                logging.warning(f"[{ts_now}] بيانات البحث غير كافية لقطاع {sector}، إعادة المحاولة...")
                time.sleep(300)
                continue
            # ---------------------------------------

            ts_file = datetime.datetime.now(SWEDEN_TZ).strftime("%Y%m%d_%H%M")
            prompt = (
                f"Identify ONE real Swedish company from: {raw_leads}. "
                f"1. Create a Technical & Legal Roadmap in PROFESSIONAL SWEDISH. "
                f"2. Write a high-stakes Sales Pitch to their CTO. "
                f"Focus on Sovereign-Shield solutions and 2026 Swedish data laws."
            )
            
            result = llm_gemini.invoke([HumanMessage(content=prompt)]).content
            
            filename = f"assets/Sovereign_Asset_{ts_file}.md"
            if export_to_github(filename, result, f"Asset Creation {ts_file}"):
                AUTO_PRODUCTION_COUNT += 1
                send_telegram_message(f"🎯 **صيد سيادي ناجح!**\n📂 الملف: {filename}\n🇸🇪 القطاع: {sector}")
                HUNTING_LOG.append(f"[{ts_now}] Created asset for {sector}")
            
        except Exception as e:
            logging.error(f"Loop Error: {e}")
            time.sleep(600)
        
        # وقت الانتظار بين الجولات (ساعتين + عشوائي)
        time.sleep(7200 + random.randint(1, 900))

# --- 5. واجهة التحكم (Dashboard) ---
@app.route('/')
def home():
    uptime = datetime.datetime.now(SWEDEN_TZ) - EMPIRE_START_TIME
    return {
        "Status": "Active",
        "Assets_Produced": AUTO_PRODUCTION_COUNT,
        "Uptime": str(uptime),
        "Sweden_Time": datetime.datetime.now(SWEDEN_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "Intelligence_Feed": HUNTING_LOG[-10:] 
    }

if __name__ == "__main__":
    threading.Thread(target=autonomous_factory_loop, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
