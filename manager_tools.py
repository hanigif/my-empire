import os
import json
import datetime
import pytz
from github import Github 
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

# --- الإعدادات السيادية (2026) ---
GK_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") 
REPO_NAME = "hanigif/Sovereign-Assets"
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')
KNOWLEDGE_BASE_DIR = "knowledge_base"
PRODUCTION_DIR = "production_v1"

for folder in [KNOWLEDGE_BASE_DIR, PRODUCTION_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# --- إعداد العقول السيادية ---
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
    except Exception as e:
        return llm_backup.invoke(messages).content

def get_auditor_review(logic, ui, task):
    """قسم الاختبار المستقل: مراجعة الجودة والتدقيق الطبي"""
    audit_prompt = (f"أنت مفتش جودة طبي مستقل (QA Auditor). راجع كود المنطق: {logic} وكود الواجهة: {ui}. "
                    f"للمهمة: {task}. ابحث عن: أخطاء طبية، ثغرات خصوصية، أو ضعف في الواجهة. "
                    f"إذا وجدت خطأ طبياً حرجاً أو معلومة مغلوطة، ابدأ ردك فوراً بكلمة 'STOP_PRODUCTION'. "
                    f"قدم تقريراً مفصلاً بنقاط الضعف.")
    return safe_invoke(llm_gemini, [
        SystemMessage(content="أنت رئيس قسم الجودة المستقل. لا تجامل الفريق. هدفك حماية سمعة القائد الطبية."),
        HumanMessage(content=audit_prompt)
    ])

def get_board_decision(task):
    """دورة الإنتاج السيادية المحدثة مع قسم الاختبار والتحكم القائد"""
    try:
        # 1. البحث التقني
        search_query = f"Emergency AI medical standards 2026 ECG Xray CT"
        search_results = search_tool.run(search_query)
        
        # 2. الـ CTO: إنتاج المنطق
        cto_prompt = (f"استخدم {search_results}. اكتب كود (logic.py) لـ {task}. "
                      f"يجب أن يشمل معالجة الكسور، الجلطات، والنزيف مع نظام Triage.")
        source_code = safe_invoke(llm_backup, [
            SystemMessage(content="أنت CTO. اكتب كود منطق طبي سيادي مع تشفير PII."),
            HumanMessage(content=cto_prompt)
        ])
        
        # 3. Frontend: إنتاج الواجهة
        ui_prompt = f"اكتب كود Streamlit (ui.py) للكود التالي: {source_code}. واجهة طوارئ احترافية."
        ui_code = safe_invoke(llm_backup, [
            SystemMessage(content="أنت Frontend Developer. صمم واجهة لوحة تحكم طوارئ (Dashboard)."),
            HumanMessage(content=ui_prompt)
        ])
        
        # 4. قسم الاختبار (Independent QA) - الخطوة الفاصلة
        audit_report = get_auditor_review(source_code, ui_code, task)
        
        # 5. بروتوكول الإيقاف الطارئ (Kill Switch)
        if "STOP_PRODUCTION" in audit_report:
            return (f"🛑 **بروتوكول الإيقاف الطارئ (STOP_PRODUCTION)**\n\n"
                    f"تم تجميد الرفع بسبب مخاطر جودة رصدها قسم الاختبار:\n\n"
                    f"{audit_report}\n\n"
                    f"⚠️ لا يمكن الاستمرار دون تدخل القائد لتصحيح المسار.")

        # 6. الـ COO: استراتيجية البيع (فقط في حال اجتياز الاختبار)
        co_prompt = f"صمم عرض بيع (OFFER.md) بناءً على الكود المعتمد وجودة الاختبار: {audit_report}"
        sales_strategy = safe_invoke(llm_gemini, [
            SystemMessage(content="أنت COO خبير سوق."),
            HumanMessage(content=co_prompt)
        ])
        
        # 7. التوقيت والتأمين
        ts = datetime.datetime.now(SWEDEN_TZ).strftime("%H%M")
        code_fn, ui_fn, doc_fn = f"logic_{ts}.py", f"ui_{ts}.py", f"offer_{ts}.md"
        
        archive_and_save_production("TECH_LOGIC", code_fn, source_code)
        archive_and_save_production("FRONTEND_UI", ui_fn, ui_code)
        archive_and_save_production("SALES_DOC", doc_fn, sales_strategy)
        
        git_1 = export_to_github(code_fn, source_code, f"Verified Logic {ts}")
        git_2 = export_to_github(ui_fn, ui_code, f"Verified UI {ts}")
        git_3 = export_to_github(doc_fn, sales_strategy, f"Sales Strategy {ts}")
        
        return (f"🏛️ **تقرير الإنتاج السيادي المعتمد ({ts})**\n\n"
                f"🛡️ **حالة GitHub:**\n- {git_1}\n- {git_2}\n- {git_3}\n\n"
                f"✅ **تقرير الجودة المستقل:**\n{audit_report[:400]}...")

    except Exception as e:
        return f"❌ خطأ حرج: {str(e)}"
