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
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

# --- 1. الإعدادات السيادية (2026) ---
logging.basicConfig(level=logging.INFO)
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

# --- 2. إعداد العقول السيادية ---
llm_backup = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)

try:
    llm_gemini = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro", 
        google_api_key=GOOGLE_KEY,
        convert_system_message_to_human=True
    )
except Exception:
    llm_gemini = llm_backup 

search_tool = DuckDuckGoSearchRun()

# --- 3. أدوات الاستخبارات والمبيعات (Sovereign Scout) ---

def sovereign_scout():
    """وظيفة البحث عن شركات سويدية وصياغة رسائل بيع مخصصة لها"""
    logging.info("🕵️ جاري تشغيل 'الكشاف السيادي' للبحث عن أهداف...")
    
    # البحث عن شركات في قطاعات حساسة بالسويد
    search_query = "Swedish health tech or fintech startups needing Patientdatalagen compliance 2026"
    raw_targets = search_tool.run(search_query)
    
    analysis_prompt = f"""
    بناءً على نتائج البحث: {raw_targets}
    1. استخرج أسماء 3 شركات سويدية حقيقية (Real Swedish Companies).
    2. صغ رسالة بيع (Sales Pitch) احترافية باللغة السويدية موجهة لمدير التقنية (CTO).
    3. الرسالة يجب أن تعرض حل مشكلة الامتثال للبيانات الحساسة باستخدام نظامنا السيادي.
    """
    
    # استخدام Gemini لصياغة الرسائل الاحترافية
    return safe_invoke(llm_gemini, [
        SystemMessage(content="أنت مدير مبيعات تقني خبير في السوق السويدي."),
        HumanMessage(content=analysis_prompt)
    ])

# --- 4. الأنظمة الخلفية (Pulse & Factory) ---

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
    auto_tasks = ["تحسين معايير Patientdatalagen 2026", "تحديث بروتوكولات الامتثال"]
    while True:
        task = random.choice(auto_tasks)
        get_board_decision(f"AUTO_MODE: {task}")
        AUTO_PRODUCTION_COUNT += 1
        time.sleep(2460)

threading.Thread(target=keep_alive_pulse, daemon=True).start()
threading.Thread(target=autonomous_factory_loop, daemon=True).start()

# --- 5. وظائف التنفيذ والأرشفة ---

def export_to_github(filename, content, commit_message):
    try:
        if not GITHUB_TOKEN: return "⚠️ GITHUB_TOKEN مفقود."
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        try:
            contents = repo.get_contents(filename)
            repo.update_file(contents.path, commit_message, content, contents.sha)
        except:
            repo.create_file(filename, commit_message, content)
        return "✅ Success"
    except: return "❌ Fail"

def safe_invoke(llm, messages):
    try:
        return llm.invoke(messages).content
    except Exception as e:
        # إذا كان هناك خطأ في المحرك (مثل 429)، حاول استخدام البديل
        logging.error(f"Error in LLM: {e}")
        return "⚠️ المحرك مشغول حالياً."

# --- 6. المحرك الرئيسي (المعدل ليشمل البحث عن الشركات) ---

def get_board_decision(task):
    clean_task = task.strip().lower()
    
    # استجابة لطلب البحث عن عملاء
    if "scout" in clean_task or "ابحث" in clean_task:
        return f"🏛️ **تقرير الكشاف السيادي للعملاء المستهدفين**\n\n{sovereign_scout()}"

    if any(k in clean_task for k in ["status", "حالة"]):
        uptime = datetime.datetime.now(SWEDEN_TZ) - EMPIRE_START_TIME
        return f"🏛️ وقت التشغيل: {uptime.days}d {uptime.seconds//3600}h\n⚙️ دورات الإنتاج: {AUTO_PRODUCTION_COUNT}"

    # مسار الإنتاج العادي (كما هو في الكود السابق)
    try:
        standards = search_tool.run(f"Sweden AI laws 2026 {task}")
        logic = safe_invoke(llm_backup, [SystemMessage(content="Architect"), HumanMessage(content=task)])
        
        ts = datetime.datetime.now(SWEDEN_TZ).strftime("%H%M")
        export_to_github(f"production/logic_{ts}.py", logic, f"Update {ts}")
        
        return f"✅ تم الإنتاج والرفع لـ GitHub (ID: {ts})"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"
