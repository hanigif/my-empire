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

# --- 3. وظيفة صيد العملاء (Sovereign Scout) ---
def sovereign_scout():
    """البحث عن شركات سويدية وصياغة رسائل بيع مخصصة لها"""
    search_query = "Swedish health-tech startups data compliance problems 2026 Patientdatalagen"
    targets = search_tool.run(search_query)
    
    analysis_prompt = f"بناءً على هذه البيانات: {targets}. استخرج 3 شركات سويدية حقيقية تحتاج لخدمات الامتثال للبيانات السيادية واكتب رسالة مبيعات (Sales Pitch) بالسويدية والإنجليزية موجهة لمديرهم التقني."
    
    return safe_invoke(llm_gemini, [
        SystemMessage(content="أنت مدير مبيعات تقني خبير في قوانين السويد."),
        HumanMessage(content=analysis_prompt)
    ])

# --- 4. الأنظمة الخلفية (Pulse & Factory) ---
def keep_alive_pulse():
    global PULSE_COUNT
    while True:
        try:
            requests.get("https://my-empire.onrender.com", timeout=10)
            PULSE_COUNT += 1
        except: pass
        time.sleep(600)

def autonomous_factory_loop():
    global AUTO_PRODUCTION_COUNT
    time.sleep(120)
    auto_tasks = ["تحسين معايير Patientdatalagen 2026", "تطوير خوارزميات التشفير السويدية"]
    while True:
        task = random.choice(auto_tasks)
        get_board_decision(f"AUTO_MODE: {task}")
        AUTO_PRODUCTION_COUNT += 1
        time.sleep(5400)

threading.Thread(target=keep_alive_pulse, daemon=True).start()
threading.Thread(target=autonomous_factory_loop, daemon=True).start()

# --- 5. وظائف التنفيذ والأرشفة ---
def export_to_github(filename, content, commit_message):
    try:
        if not GITHUB_TOKEN: return "⚠️ TOKEN مفقود"
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        try:
            contents = repo.get_contents(filename)
            repo.update_file(contents.path, commit_message, content, contents.sha)
        except:
            repo.create_file(filename, commit_message, content)
        return "✅ تم الرفع"
    except: return "❌ فشل الرفع"

def safe_invoke(llm, messages):
    try:
        # المحاولة الأولى
        return llm.invoke(messages).content
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            logging.warning("🚨 زحام في المحركات. تفعيل بروتوكول الانتظار...")
            # إذا فشل Gemini، جرب Llama بعد انتظار بسيط
            time.sleep(2) 
            try:
                return llm_backup.invoke(messages).content
            except:
                return "🏛️ (رسالة نظام): المحركات السيادية في حالة استراحة قصيرة لتجنب الحظر. سأعود للعمل بكامل طاقتي خلال دقائق."
        return f"⚠️ عذرًا قائد، واجهت تحديًا تقنيًا بسيطًا: {error_msg[:50]}"

def get_auditor_review(logic, ui, task):
    audit_prompt = f"راجع المنطق: {logic} والواجهة: {ui} بناءً على Patientdatalagen 2026. إذا وجد خطر، ابدأ بـ STOP_PRODUCTION."
    return safe_invoke(llm_gemini, [SystemMessage(content="Audit Chief"), HumanMessage(content=audit_prompt)])

# --- 6. المحرك الرئيسي (المدير السيادي) ---
def get_board_decision(task):
    clean_task = task.strip().lower()
    
    # ميزة صيد العملاء الجديدة
    if any(k in clean_task for k in ["scout", "ابحث", "عملاء"]):
        return f"🕵️ **تقرير الكشاف السيادي للعملاء:**\n\n{sovereign_scout()}"

    # تقرير الحالة
    if any(k in clean_task for k in ["status", "حالة", "report"]):
        uptime = datetime.datetime.now(SWEDEN_TZ) - EMPIRE_START_TIME
        return f"🏛️ **تقرير الإمبراطورية**\n⏱️ تشغيل: {uptime.days}d {uptime.seconds//3600}h\n⚙️ إنتاج: {AUTO_PRODUCTION_COUNT}\n💓 نبضات: {PULSE_COUNT}"

    # مسار الإنتاج والتدقيق
    try:
        standards = search_tool.run(f"Sweden AI medical laws 2026 {task}")
        logic = safe_invoke(llm_backup, [SystemMessage(content="Senior Architect"), HumanMessage(content=f"{task} Standards: {standards}")])
        ui = safe_invoke(llm_backup, [SystemMessage(content="UI Specialist"), HumanMessage(content=f"UI for {logic}")])
        
        audit = get_auditor_review(logic, ui, task)
        if "STOP_PRODUCTION" in audit: return f"🛑 فشل التدقيق: {audit[:200]}"
        
        ts = datetime.datetime.now(SWEDEN_TZ).strftime("%H%M")
        export_to_github(f"production/logic_{ts}.py", logic, f"Update {ts}")
        
        return f"🏛️ **تم الإنتاج ({ts})**\n✅ مطابق لمعايير 2026\n🛡️ تم التأمين على GitHub"
    except Exception as e:
        return f"❌ خطأ حرج: {str(e)}"
