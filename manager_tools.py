import os
import json
import datetime
import pytz
from github import Github  # إضافة مكتبة الخزنة
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

# --- الإعدادات السيادية (2026) ---
GK_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")  # المفتاح المبرمج في Render
REPO_NAME = "YOUR_USERNAME/Sovereign-Assets" # استبدل YOUR_USERNAME باسم حسابك
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')
KNOWLEDGE_BASE_DIR = "knowledge_base"
PRODUCTION_DIR = "production_v1"

# تأمين وجود المجلدات (الأساس الذي لا يمس)
for folder in [KNOWLEDGE_BASE_DIR, PRODUCTION_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# --- إعداد العقول السيادية ---
llm_backup = ChatGroq(
    temperature=0.1, 
    model_name="llama-3.3-70b-versatile", 
    groq_api_key=GK_KEY
)

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
    """تأمين المنتج في خزنة GitHub الخاصة كملكية فكرية"""
    try:
        if not GITHUB_TOKEN:
            return "⚠️ تنبيه: GITHUB_TOKEN غير مفقود، تم الحفظ محلياً فقط."
        
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        
        try:
            # تحديث الملف إذا كان موجوداً
            contents = repo.get_contents(filename)
            repo.update_file(contents.path, commit_message, content, contents.sha)
        except:
            # إنشاء ملف جديد
            repo.create_file(filename, commit_message, content)
        return f"✅ تم التأمين في الخزنة (GitHub): {filename}"
    except Exception as e:
        return f"❌ فشل رفع الخزنة: {str(e)}"

def archive_and_save_production(role, filename, content):
    """حفظ الكود المنتج كملكية فكرية وأرشفته في قاعدة المعرفة المحلية"""
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

def get_board_decision(task):
    """دورة الإنتاج السيادي: تحويل المهام إلى أصول رقمية محمية"""
    try:
        # 1. البحث عن المعايير السيادية لعام 2026
        search_query = f"Python PII scrubbing Differential Privacy standards 2026"
        search_results = search_tool.run(search_query)
        
        # 2. الـ CTO: إنتاج الكود (الملكية الفكرية)
        cto_prompt = (
            f"بناءً على: {search_results}. اكتب كود Python احترافي وكامل لوحدة 'Sovereign Anonymizer'. "
            f"المهمة: {task}. الكود منتج للبيع، اجعله نظيفاً وقابلاً للتوسع."
        )
        source_code = safe_invoke(llm_backup, [
            SystemMessage(content="أنت CTO. اكتب كوداً مصدرياً جاهزاً للإنتاج والبيع فقط."), 
            HumanMessage(content=cto_prompt)
        ])
        
        # 3. الـ COO: إنتاج وثيقة البيع
        co_prompt = (f"صمم ملف PRODUCT_OFFER.md للكود التالي: {source_code[:400]}. "
                     f"ركز على قيمة الامتثال والسيادة للشركات الكبرى.")
        sales_strategy = safe_invoke(llm_gemini, [
            SystemMessage(content="أنت COO خبير في بيع التكنولوجيا في السويد."), 
            HumanMessage(content=co_prompt)
        ])
        
        # 4. التنفيذ: الحفظ المحلي + التأمين في الخزنة العالمية
        timestamp = datetime.datetime.now(SWEDEN_TZ).strftime("%H%M")
        code_fn, doc_fn = f"logic_{timestamp}.py", f"offer_{timestamp}.md"
        
        # الحفظ المحلي (الأساس)
        archive_and_save_production("TECH_SPECS", code_fn, source_code)
        archive_and_save_production("SALES_STRATEGY", doc_fn, sales_strategy)
        
        # التأمين في GitHub (الخزنة)
        git_status_code = export_to_github(code_fn, source_code, f"Asset Production: {code_fn}")
        git_status_doc = export_to_github(doc_fn, sales_strategy, f"Sales Strategy: {doc_fn}")
        
        current_time = datetime.datetime.now(SWEDEN_TZ).strftime("%H:%M")
        
        return (f"🏛️ **تقرير خط الإنتاج السيادي ({current_time})**\n\n"
                f"🛡️ **حالة الخزنة:**\n- {git_status_code}\n- {git_status_doc}\n\n"
                f"🎯 **ملخص:** تم تحويل المهمة إلى أصل رقمي محفوظ محلياً ومؤمن في مستودعك الخاص.")

    except Exception as e:
        return f"❌ خطأ حرج في دورة الإنتاج: {str(e)}"

def safe_invoke(llm, messages):
    try:
        return llm.invoke(messages).content
    except Exception as e:
        return llm_backup.invoke(messages).content
