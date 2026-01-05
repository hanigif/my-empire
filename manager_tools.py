import os
import json
import datetime
import pytz
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

# --- الإعدادات السيادية (2026) ---
GK_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')
KNOWLEDGE_BASE_DIR = "knowledge_base"
PRODUCTION_DIR = "production_v1"

# إنشاء المجلدات الأساسية إذا لم توجد
for folder in [KNOWLEDGE_BASE_DIR, PRODUCTION_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# --- إعداد العقول السيادية (الإنتاجية) ---
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

def safe_invoke(llm, messages):
    """استدعاء ذكي مع نظام تبديل آلي"""
    try:
        return llm.invoke(messages).content
    except Exception as e:
        print(f"⚠️ تحويل للمحرك الاحتياطي: {str(e)}")
        return llm_backup.invoke(messages).content

def archive_and_save_code(role, filename, content):
    """حفظ الكود المنتج كملكية فكرية مستقلة وأرشفة المهمة"""
    # 1. حفظ الكود كملف قابل للتشغيل
    file_path = os.path.join(PRODUCTION_DIR, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    # 2. أرشفة العملية في قاعدة المعرفة (الأساس الذي لا يمس)
    archive_path = os.path.join(KNOWLEDGE_BASE_DIR, f"{role.lower()}_brain.json")
    entry = {
        "timestamp": datetime.datetime.now(SWEDEN_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "file_generated": filename,
        "content_preview": content[:200]
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
    """دورة الإنتاج السيادي: توليد كود المنتج وخطط البيع"""
    try:
        # 1. البحث عن أحدث تقنيات التجهيل البرمجية 2026
        search_query = f"Python implementation Differential Privacy healthcare PII scrubbing 2026"
        search_results = search_tool.run(search_query)
        
        # 2. مهندس الإنتاج (CTO) - كتابة كود المحرك الخاص بك
        cto_prompt = (
            f"بناءً على التقنيات: {search_results}. اكتب كود بايثون كامل واحترافي لوحدة 'Sovereign Anonymizer'. "
            f"يجب أن يتضمن الكود وظائف مسح البيانات الشخصية (PII) وتشفيرها قبل خروجها للـ AI. "
            f"أريد كوداً نظيفاً (Clean Code) يمكن بيعه كمنتج مستقل."
        )
        source_code = safe_invoke(llm_backup, [
            SystemMessage(content="أنت كبير مهندسي برمجيات. وظيفتك كتابة كود بايثون فعلي وجاهز للإنتاج فقط."), 
            HumanMessage(content=cto_prompt)
        ])
        
        # 3. مدير الاستراتيجية (COO) - صياغة ملف البيع (README)
        coo_prompt = (
            f"الكود المنتج هو: {source_code[:500]}. صمم عرض القيمة (Value Proposition) "
            f"وملف README.md احترافي بالإنجليزية يوضح للشركات كيف يحميهم هذا الكود قانونياً."
        )
        sales_strategy = safe_invoke(llm_gemini, [
            SystemMessage(content="أنت خبير نمو وبيع تقني (Growth Hacker)."), 
            HumanMessage(content=coo_prompt)
        ])
        
        # 4. حفظ الإنتاج (تحويل التنظير إلى ملفات)
        code_file = archive_and_save_code("TECH_SPECS", "sovereign_logic.py", source_code)
        readme_file = archive_and_save_code("SALES_STRATEGY", "PRODUCT_OFFER.md", sales_strategy)
        
        current_time = datetime.datetime.now(SWEDEN_TZ).strftime("%H:%M")
        return (f"🏛️ **تم تشغيل خط الإنتاج السيادي ({current_time})**\n\n"
                f"🛠️ **المنتج البرمجي:** تم إنشاء `{code_file}` بنجاح.\n"
                f"📜 **مستندات البيع:** تم إنشاء `{readme_file}`.\n\n"
                f"🎯 **ملخص المدير:** هذا الكود هو ملكيتك الفكرية. لقد قمنا ببرمجة نظام التجهيل "
                f"بدلاً من مجرد التخطيط له. الملفات جاهزة للتسليم للعملاء.")

    except Exception as e:
        return f"❌ خطأ حرج في خط الإنتاج: {str(e)}"
