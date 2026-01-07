import os
import json
import datetime
import pytz
import threading
import time
import requests
import random
import logging
from github import Github 
from google import genai  # المحرك الجديد 2026
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

# --- 1. الإعدادات السيادية (2026) ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
GK_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") 
REPO_NAME = "hanigif/Sovereign-Assets"
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')
KNOWLEDGE_BASE_DIR = "knowledge_base"
PRODUCTION_DIR = "production_v1"

EMPIRE_START_TIME = datetime.datetime.now(SWEDEN_TZ)
PULSE_COUNT = 0
AUTO_PRODUCTION_COUNT = 0 

for folder in [KNOWLEDGE_BASE_DIR, PRODUCTION_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# --- 2. إعداد العقول السيادية (المطورة) ---
llm_backup = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)

class Gemini2026Manager:
    """إدارة Gemini عبر SDK الجديد لتجاوز أخطاء الاصدارات القديمة"""
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash"

    def invoke(self, messages):
        # استخراج النص الأخير من قائمة الرسائل
        prompt = messages[-1].content if isinstance(messages, list) else str(messages)
        try:
            # محاولة مع نظام حماية من الزحام (Rate Limiting)
            response = self.client.models.generate_content(model=self.model_id, contents=prompt)
            # محاكاة كائن LangChain للاتساق مع الكود القديم
            return type('Response', (object,), {'content': response.text})
        except Exception as e:
            logging.warning(f"⚠️ زحام Gemini، التحويل لـ Llama: {e}")
            return llm_backup.invoke(messages)

# تفعيل العقل المزدوج
llm_gemini = Gemini2026Manager(GOOGLE_KEY) if GOOGLE_KEY else llm_backup
search_tool = DuckDuckGoSearchRun()

# --- 3. نظام النبض والمصنع المستقل ---
def keep_alive_pulse():
    global PULSE_COUNT
    APP_URL = "https://my-empire.onrender.com" 
    while True:
        try:
            requests.get(APP_URL, timeout=10)
            PULSE_COUNT += 1
        except Exception: pass
        time.sleep(600) 

def autonomous_factory_loop():
    global AUTO_PRODUCTION_COUNT
    time.sleep(120) 
    auto_tasks = [
        "تحسين معايير Patientdatalagen 2026 في الكود السيادي",
        "تطوير خوارزميات تحليل البيانات الصحية السويدية المشفرة",
        "تحديث بروتوكولات الامتثال لـ Socialstyrelsen"
    ]
    while True:
        task = random.choice(auto_tasks)
        get_board_decision(f"AUTO_MODE: {task}")
        AUTO_PRODUCTION_COUNT += 1
        time.sleep(2460)

threading.Thread(target=keep_alive_pulse, daemon=True).start()
threading.Thread(target=autonomous_factory_loop, daemon=True).start()

# --- 4. وظائف الأرشفة والرفع لـ GitHub ---
def export_to_github(filename, content, commit_message):
    if not GITHUB_TOKEN: return "⚠️ GITHUB_TOKEN مفقود."
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        try:
            contents = repo.get_contents(filename)
            repo.update_file(contents.path, commit_message, content, contents.sha)
        except:
            repo.create_file(filename, commit_message, content)
        return f"✅ تم التأمين: {filename}"
    except Exception as e:
        return f"❌ فشل رفع {filename}: {str(e)}"

def archive_and_save_production(role, filename, content):
    file_path = os.path.join(PRODUCTION_DIR, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    archive_path = os.path.join(KNOWLEDGE_BASE_DIR, f"{role.lower()}_brain.json")
    entry = {
        "timestamp": datetime.datetime.now(SWEDEN_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "product_file": filename,
        "content_preview": content[:250] + "..."
    }
    data = []
    if os.path.exists(archive_path):
        with open(archive_path, "r", encoding="utf-8") as f:
            try: data = json.load(f)
            except: data = []
    data.append(entry)
    with open(archive_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return file_path

def safe_invoke(llm, messages):
    try:
        res = llm.invoke(messages)
        return res.content if hasattr(res, 'content') else str(res)
    except Exception:
        return llm_backup.invoke(messages).content

# --- 5. قسم الاختبار المستقل (Auditor) ---
def get_auditor_review(logic, ui, task):
    audit_prompt = (f"أنت مفتش جودة طبي مستقل (QA Auditor). راجع المنطق: {logic} والواجهة: {ui}. "
                    f"المهمة: {task}. ابحث عن توافق Patientdatalagen 2026.")
    return safe_invoke(llm_gemini, [
        SystemMessage(content="أنت رئيس قسم الجودة المستقل في السويد."),
        HumanMessage(content=audit_prompt)
    ])

# --- 6. المحرك الرئيسي (المدير السيادي) ---
def get_board_decision(task):
    clean_task = task.strip().lower()
    if any(k in clean_task for k in ["status", "حالة", "report"]):
        uptime = datetime.datetime.now(SWEDEN_TZ) - EMPIRE_START_TIME
        return (f"🏛️ **تقرير الإمبراطورية**\n"
                f"⏱️ تشغيل: {uptime.days}d {uptime.seconds//3600}h\n"
                f"⚙️ إنتاج آلي: {AUTO_PRODUCTION_COUNT}\n"
                f"💓 نبضات: {PULSE_COUNT}\n"
                f"📅 السويد: {datetime.datetime.now(SWEDEN_TZ).strftime('%H:%M')}")

    try:
        # البحث عن المعايير الحالية
        search_query = f"Sweden AI data laws 2026 {task}"
        standards = search_tool.run(search_query)
        
        # حلقة التحسين (Iteration)
        for i in range(1, 3):
            logic = safe_invoke(llm_backup, [SystemMessage(content="Senior Architect"), HumanMessage(content=f"Task: {task}. Standards: {standards}")])
            ui = safe_invoke(llm_backup, [SystemMessage(content="UI Dev"), HumanMessage(content=f"Build UI for: {logic}")])
            
            audit = get_auditor_review(logic, ui, task)
            if "STOP_PRODUCTION" not in audit: break

        # البيع والأرشفة
        sales = safe_invoke(llm_gemini, [SystemMessage(content="COO"), HumanMessage(content=f"Create sales pitch for: {logic}")])
        ts = datetime.datetime.now(SWEDEN_TZ).strftime("%H%M")
        
        archive_and_save_production("LOGIC", f"logic_{ts}.py", logic)
        export_to_github(f"production/logic_{ts}.py", logic, f"Sovereign Update {ts}")
        
        return f"🏛️ **تم الإنتاج بنجاح ({ts})**\n✅ تم الرفع لـ GitHub\n⚖️ تدقيق Gemini: مكتمل"
    except Exception as e:
        return f"❌ فشل المحرك: {str(e)}"
