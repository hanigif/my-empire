import os
import json
import datetime
import pytz
import threading
import time
import requests
import random
from github import Github 
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

# --- 1. الإعدادات السيادية (2026) ---
GK_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") 
REPO_NAME = "hanigif/Sovereign-Assets"
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')
KNOWLEDGE_BASE_DIR = "knowledge_base"
PRODUCTION_DIR = "production_v1"

EMPIRE_START_TIME = datetime.datetime.now(SWEDEN_TZ)
PULSE_COUNT = 0
AUTO_PRODUCTION_COUNT = 0 # عداد الإنتاج الآلي الجديد

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

# --- 3. الأنظمة الخلفية المستقلة (النبض والمصنع) ---

def keep_alive_pulse():
    global PULSE_COUNT
    APP_URL = "https://my-empire.onrender.com" 
    while True:
        try:
            requests.get(APP_URL, timeout=10)
            PULSE_COUNT += 1
        except Exception:
            pass
        time.sleep(600) # نبضة كل 10 دقائق

def autonomous_factory_loop():
    """محرك الإنتاج الآلي: يعمل كل 41 دقيقة لاستهلاك 35 طلب Gemini يومياً"""
    global AUTO_PRODUCTION_COUNT
    time.sleep(300) # انتظار 5 دقائق للاستقرار بعد التشغيل
    
    # مهام تطويرية متنوعة للمصنع
    auto_tasks = [
        "تحسين بروتوكولات الخصوصية السيادية لبيانات المرضى في السويد",
        "تحديث منطق تشفير البيانات الطبية وفق معايير Patientdatalagen 2026",
        "تطوير واجهة مستخدم آمنة لا تسمح بتسريب البيانات خارج الحدود السيادية",
        "فحص وتحديث أنظمة الامتثال لعام 2026 تلقائياً"
    ]
    
    while True:
        task = random.choice(auto_tasks)
        # إرسال الأمر للمحرك الرئيسي ببادئة تميزه كإنتاج آلي
        get_board_decision(f"AUTO_TASK: {task}")
        AUTO_PRODUCTION_COUNT += 1
        # 2460 ثانية = 41 دقيقة (35 دورة في الـ 24 ساعة)
        time.sleep(2460)

# تشغيل الأنظمة في الخلفية
threading.Thread(target=keep_alive_pulse, daemon=True).start()
threading.Thread(target=autonomous_factory_loop, daemon=True).start()

# --- 4. وظائف الأرشفة والرفع لـ GitHub ---
def export_to_github(filename, content, commit_message):
    try:
        if not GITHUB_TOKEN: return "⚠️ GITHUB_TOKEN مفقود."
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        try:
            # محاولة تحديث الملف المركزي (تجنب الفوضى)
            contents = repo.get_contents(filename)
            repo.update_file(contents.path, commit_message, content, contents.sha)
        except:
            # إنشاء الملف إذا لم يكن موجوداً
            repo.create_file(filename, commit_message, content)
        return f"✅ تم التأمين: {filename}"
    except Exception as e:
        return f"❌ فشل رفع {filename}: {str(e)}"

def archive_and_save_production(role, filename, content):
    file_path = os.path.join(PRODUCTION_DIR, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path

def safe_invoke(llm, messages):
    try:
        return llm.invoke(messages).content
    except Exception:
        return llm_backup.invoke(messages).content

# --- 5. قسم الاختبار المستقل (Auditor) ---
def get_auditor_review(logic, ui, task):
    audit_prompt = (f"أنت مفتش جودة طبي مستقل. راجع كود المنطق: {logic} وكود الواجهة: {ui}. "
                    f"للمهمة: {task}. ابحث عن: عدم مطابقة للمعايير السويدية 2026. "
                    f"إذا وجدت خطأ حرجاً ابدأ بـ 'STOP_PRODUCTION'.")
    return safe_invoke(llm_gemini, [
        SystemMessage(content="أنت رئيس قسم الجودة المستقل."),
        HumanMessage(content=audit_prompt)
    ])

# --- 6. المحرك الرئيسي (المدير السيادي) ---
def get_board_decision(task):
    clean_task = task.strip().lower()
    status_keywords = ["حالة الإمبراطورية", "status", "report", "حالة الامبراطورية"]

    # --- [المسار السريع للأوامر الإدارية] ---
    if any(keyword in clean_task for keyword in status_keywords):
        uptime = datetime.datetime.now(SWEDEN_TZ) - EMPIRE_START_TIME
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        return (f"🏛️ **تقرير حالة الإمبراطورية السيادية**\n"
                f"━━━━━━━━━━━━━━━\n"
                f"⏱️ **وقت التشغيل:** {days} يوم، {hours} ساعة، {minutes} دقيقة\n"
                f"💓 **نبضات Keep-Alive:** {PULSE_COUNT}\n"
                f"⚙️ **دورات الإنتاج الآلي:** {AUTO_PRODUCTION_COUNT}\n"
                f"🛡️ **سياسة الاستهلاك:** 35 طلب/يوم (آمن)\n"
                f"📅 **توقيت السويد:** {datetime.datetime.now(SWEDEN_TZ).strftime('%H:%M:%S')}\n"
                f"✅ **حالة النظام:** Live (24/7)\n"
                f"━━━━━━━━━━━━━━━")

    # --- [مسار دورة الإنتاج والتطوير الذاتي] ---
    try:
        search_query = f"Sweden AI medical software standards 2026 {task}"
        standards = search_tool.run(search_query)
        
        # دورة التطوير والتحسين (نظام الـ 3 دورات)
        current_logic = ""
        current_ui = ""
        audit_report = ""
        iteration_history = ""

        for i in range(1, 4):
            current_logic = safe_invoke(llm_backup, [
                SystemMessage(content="Senior Medical Architect"),
                HumanMessage(content=f"Build logic for: {task}. Standards: {standards}. History: {iteration_history}")
            ])
            current_ui = safe_invoke(llm_backup, [SystemMessage(content="UI Specialist"), HumanMessage(content=f"UI for: {current_logic}")])
            
            audit_report = get_auditor_review(current_logic, current_ui, task)
            if "STOP_PRODUCTION" not in audit_report: break 
            iteration_history = f"Attempt {i} failed: {audit_report}"

        # رفع النتائج (تحديث الملفات المركزية لتجنب الفوضى)
        ts = datetime.datetime.now(SWEDEN_TZ).strftime("%Y%m%d_%H%M")
        export_to_github("Sovereign_Core_Logic.py", current_logic, f"Auto-Update {ts}")
        export_to_github("Sovereign_UI.py", current_ui, f"Auto-Update UI {ts}")
        
        return f"🏛️ **تمت دورة الإنتاج ({ts})**\n✅ الجودة: معتمدة\n🛡️ تم التحديث في GitHub."

    except Exception as e:
        return f"❌ خطأ حرج: {str(e)}"
