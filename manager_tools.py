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

def get_board_decision(task):
    """دورة الإنتاج السيادي المحدثة: خصوصية + تحليل ذكي"""
    try:
        # 1. البحث التقني المزدوج (خصوصية + تحليل طبي)
        search_query = f"Python AI X-ray analysis and PII scrubbing 2026 standards"
        search_results = search_tool.run(search_query)
        
        # 2. الـ CTO: إنتاج منطق المنتج (إضافة التحليل الذكي)
        cto_prompt = (f"بناءً على: {search_results}. اكتب كود Python (logic.py) لـ: {task}. "
                      f"يجب أن يتضمن الكود وظيفتين: 1. مسح بيانات المريض (Anonymization) "
                      f"2. وحدة ذكاء اصطناعي (محاكاة) لتحليل الصورة وإعطاء تقرير طبي أولي.")
        source_code = safe_invoke(llm_backup, [
            SystemMessage(content="أنت CTO خبير. اكتب كود Logic يجمع بين حماية الخصوصية والتحليل الطبي الذكي."), 
            HumanMessage(content=cto_prompt)
        ])
        
        # 3. مهندس الواجهات: دعم لوحة تحكم التحليل
        ui_prompt = (f"اكتب كود Streamlit (ui.py) للكود التالي: {source_code}. "
                      f"يجب أن تعرض الواجهة: الصورة الأصلية، الصورة المحمية، ونتائج التحليل الطبي الذكي بشكل احترافي.")
        ui_code = safe_invoke(llm_backup, [
            SystemMessage(content="أنت Frontend Developer. صمم لوحة تحكم طبية تعرض نتائج التحليل والخصوصية جنباً إلى جنب."),
            HumanMessage(content=ui_prompt)
        ])
        
        # 4. الـ COO: وثيقة البيع (القيمة المضافة المزدوجة)
        co_prompt = (f"صمم PRODUCT_OFFER.md لهذا المنتج. ركز على كيف يحل أزمة الخصوصية "
                      f"وفي نفس الوقت يوفر أداة تشخيص مساعدة للأطباء في السويد.")
        sales_strategy = safe_invoke(llm_gemini, [
            SystemMessage(content="أنت COO خبير. سوق للمنتج كحل 'سيادي' يجمع بين الأمان والذكاء."), 
            HumanMessage(content=co_prompt)
        ])
        
        # 5. التنفيذ والتأمين
        ts = datetime.datetime.now(SWEDEN_TZ).strftime("%H%M")
        code_fn, ui_fn, doc_fn = f"logic_{ts}.py", f"ui_{ts}.py", f"offer_{ts}.md"
        
        archive_and_save_production("TECH_LOGIC", code_fn, source_code)
        archive_and_save_production("FRONTEND_UI", ui_fn, ui_code)
        archive_and_save_production("SALES_DOC", doc_fn, sales_strategy)
        
        git_status_1 = export_to_github(code_fn, source_code, f"Logic & AI Asset: {ts}")
        git_status_2 = export_to_github(ui_fn, ui_code, f"UI AI-Dashboard: {ts}")
        git_status_3 = export_to_github(doc_fn, sales_strategy, f"Sales Strategy: {ts}")
        
        current_time = datetime.datetime.now(SWEDEN_TZ).strftime("%H:%M")
        
        return (f"🏛️ **تقرير خط الإنتاج المتكامل - النسخة الذكية ({current_time})**\n\n"
                f"🛡️ **حالة الخزنة (GitHub):**\n- {git_status_1}\n- {git_status_2}\n- {git_status_3}\n\n"
                f"🧠 **تحديث الذكاء:** تم دمج وحدة التحليل الطبي المستقلة داخل الأصول البرمجية.")

    except Exception as e:
        return f"❌ خطأ حرج في المحرك السيادي: {str(e)}"
