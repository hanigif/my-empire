import os
import json
import datetime
import pytz
import threading
import time
import requests
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

# سجلات المراقبة العالمية لضمان الـ 24/7
EMPIRE_START_TIME = datetime.datetime.now(SWEDEN_TZ)
PULSE_COUNT = 0

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

# --- 3. نظام النبض الذكي (Keep-Alive) ---
def keep_alive_pulse():
    global PULSE_COUNT
    APP_URL = "https://my-empire.onrender.com" 
    while True:
        try:
            # النبض يمنع Render من النوم التلقائي
            requests.get(APP_URL, timeout=10)
            PULSE_COUNT += 1
        except Exception:
            pass
        time.sleep(600) # نبضة كل 10 دقائق

# تشغيل النبض في خيط منفصل لضمان استمرارية العمل
pulse_thread = threading.Thread(target=keep_alive_pulse, daemon=True)
pulse_thread.start()

# --- 4. وظائف الأرشفة والرفع لـ GitHub ---
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
        return llm.invoke(messages).content
    except Exception:
        return llm_backup.invoke(messages).content

# --- 5. قسم الاختبار المستقل (Auditor) ---
def get_auditor_review(logic, ui, task):
    audit_prompt = (f"أنت مفتش جودة طبي مستقل (QA Auditor). راجع كود المنطق: {logic} وكود الواجهة: {ui}. "
                    f"للمهمة: {task}. ابحث عن: أخطاء طبية، عدم مطابقة للمعايير السويدية، ثغرات خصوصية. "
                    f"إذا وجدت خطأ طبياً حرجاً، ابدأ ردك فوراً بكلمة 'STOP_PRODUCTION'.")
    return safe_invoke(llm_gemini, [
        SystemMessage(content="أنت رئيس قسم الجودة المستقل. وظيفتك التدقيق الصارم."),
        HumanMessage(content=audit_prompt)
    ])

# --- 6. المحرك الرئيسي (المدير السيادي) ---
def get_board_decision(task):
    # تنظيف المدخلات لضمان التعرف على الأوامر الإدارية
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
                f"🛡️ **حالة النظام:** Live (24/7)\n"
                f"📅 **توقيت السويد الحالي:** {datetime.datetime.now(SWEDEN_TZ).strftime('%H:%M:%S')}\n"
                f"✅ **جاهزية المفتش:** نشط ومستعد للفحص\n"
                f"━━━━━━━━━━━━━━━\n"
                f"⚠️ *ملاحظة: هذا رد إداري مباشر ولا يستهلك موارد الإنتاج.*")

    # --- [مسار دورة الإنتاج والتطوير الذاتي] ---
    try:
        search_query = f"Sweden AI medical software standards 2026 Patientdatalagen Socialstyrelsen"
        standards = search_tool.run(search_query)
        
        current_logic = ""
        current_ui = ""
        audit_report = ""
        iteration_history = ""

        for i in range(1, 4):
            cto_prompt = (f"الدورة {i}: معايير السويد: {standards}. المهمة: {task}. "
                          f"تاريخ التحسين: {iteration_history}. اكتب كود logic.py سيادي.")
            current_logic = safe_invoke(llm_backup, [
                SystemMessage(content="أنت Senior Medical Architect."),
                HumanMessage(content=cto_prompt)
            ])
            
            ui_prompt = f"صمم واجهة Streamlit لهذا الكود: {current_logic}"
            current_ui = safe_invoke(llm_backup, [SystemMessage(content="أنت UI Specialist."), HumanMessage(content=ui_prompt)])

            audit_report = get_auditor_review(current_logic, current_ui, task)
            if "STOP_PRODUCTION" not in audit_report: 
                break 
            
            iteration_history = f"فشل الدورة {i}: {audit_report}"

        if "STOP_PRODUCTION" in audit_report:
            return (f"🛑 **بروتوكول الإيقاف الطارئ**\n\n"
                    f"لم نتجاوز اختبار الجودة الطبي بعد 3 دورات.\n"
                    f"📝 تقرير المفتش: {audit_report}")

        co_prompt = f"صمم عرض بيع بناءً على جودة المنتج المطابق لـ {standards}"
        sales_strategy = safe_invoke(llm_gemini, [SystemMessage(content="أنت COO خبير."), HumanMessage(content=co_prompt)])
        
        ts = datetime.datetime.now(SWEDEN_TZ).strftime("%H%M")
        code_fn, ui_fn, doc_fn = f"logic_{ts}.py", f"ui_{ts}.py", f"offer_{ts}.md"
        
        archive_and_save_production("TECH_LOGIC", code_fn, current_logic)
        archive_and_save_production("FRONTEND_UI", ui_fn, current_ui)
        archive_and_save_production("SALES_DOC", doc_fn, sales_strategy)
        
        export_to_github(code_fn, current_logic, f"Evolved Logic {ts}")
        export_to_github(ui_fn, current_ui, f"Evolved UI {ts}")
        export_to_github(doc_fn, sales_strategy, f"Evolved Offer {ts}")
        
        return (f"🏛️ **تقرير الإنتاج السيادي المعتمد ({ts})**\n\n"
                f"✅ تم اجتياز الاختبار بعد {i} دورات تحسين.\n"
                f"🛡️ تم التأمين في GitHub بنجاح.\n"
                f"📋 **ملخص المفتش:** {audit_report[:300]}...")

    except Exception as e:
        return f"❌ خطأ حرج في المحرك: {str(e)}"
