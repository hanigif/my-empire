import os
import json
import datetime
import pytz
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

# --- الإعدادات السيادية (2026) ---
# استخدام الوقت الرسمي السويدي لسهولة المتابعة
GK_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')
KNOWLEDGE_BASE_DIR = "knowledge_base"
PRODUCTION_DIR = "production_v1"

# تأمين وجود المجلدات (الأساس الذي لا يمس)
for folder in [KNOWLEDGE_BASE_DIR, PRODUCTION_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# --- إعداد العقول السيادية (الإنتاجية) ---
# عقل Groq (كبير المهندسين - CTO)
llm_backup = ChatGroq(
    temperature=0.1, 
    model_name="llama-3.3-70b-versatile", 
    groq_api_key=GK_KEY
)

# عقل Gemini (خبير الاستراتيجية - COO)
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
    """استدعاء ذكي مع نظام تبديل آلي في حال فشل Gemini"""
    try:
        return llm.invoke(messages).content
    except Exception as e:
        print(f"⚠️ تحويل للمحرك الاحتياطي: {str(e)}")
        return llm_backup.invoke(messages).content

def archive_and_save_production(role, filename, content):
    """حفظ الكود المنتج كملكية فكرية وأرشفته في قاعدة المعرفة"""
    # 1. حفظ الملف الفعلي في مجلد الإنتاج
    file_path = os.path.join(PRODUCTION_DIR, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    # 2. الأرشفة في سجلات العقل (الأساس التاريخي)
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
    """دورة الإنتاج السيادي: تحويل الأفكار إلى أصول برمجية وخطط بيع"""
    try:
        # 1. البحث عن المعايير البرمجية لعام 2026
        search_query = f"Python implementation PII scrubbing Differential Privacy standards 2026"
        search_results = search_tool.run(search_query)
        
        # 2. مهندس الإنتاج (CTO): كتابة الكود المصدري (الملكية الفكرية)
        cto_prompt = (
            f"بناءً على: {search_results}. اكتب كود Python احترافي وكامل لوحدة 'Sovereign Anonymizer'. "
            f"المهمة المطلوبة: {task}. "
            f"يجب أن يتضمن الكود منطقاً حقيقياً لتجهيل البيانات وتشفيرها. "
            f"هذا الكود هو منتجنا، اجعله جاهزاً للاستخدام (Production-ready)."
        )
        source_code = safe_invoke(llm_backup, [
            SystemMessage(content="أنت كبير مهندسي برمجيات (CTO). اكتب كوداً مصدرياً نظيفاً فقط جاهزاً للبيع."), 
            HumanMessage(content=cto_prompt)
        ])
        
        # 3. مدير الاستراتيجية (COO): صياغة ملف البيع والقيمة المضافة
        coo_prompt = (
            f"الكود المنتج هو: {source_code[:500]}. صمم ملف PRODUCT_OFFER.md "
            f"يشرح للشركات السويدية كيف يحميهم هذا الكود قانونياً وفق قوانين AI Act 2026."
        )
        sales_strategy = safe_invoke(llm_gemini, [
            SystemMessage(content="أنت خبير نمو واستراتيجيات مبيعات تقنية (COO)."), 
            HumanMessage(content=coo_prompt)
        ])
        
        # 4. تنفيذ الإنتاج وحفظ الملفات
        # تسمية الملفات بناءً على وقت الإنتاج لضمان عدم التكرار
        timestamp_str = datetime.datetime.now(SWEDEN_TZ).strftime("%H%M")
        code_file = archive_and_save_production("TECH_SPECS", f"logic_{timestamp_str}.py", source_code)
        readme_file = archive_and_save_production("SALES_STRATEGY", f"offer_{timestamp_str}.md", sales_strategy)
        
        current_time = datetime.datetime.now(SWEDEN_TZ).strftime("%H:%M")
        
        return (f"🏛️ **تم تشغيل خط الإنتاج السيادي ({current_time})**\n\n"
                f"✅ **الملكية الفكرية:** تم توليد `{code_file}`\n"
                f"✅ **مستندات البيع:** تم تجهيز `{readme_file}`\n\n"
                f"🎯 **ملخص المدير:** لقد انتقلنا من مرحلة التخطيط إلى الإنتاج الفعلي. "
                f"الملفات محفوظة في `{PRODUCTION_DIR}` وهي أصولك البرمجية الجاهزة للتسويق.")

    except Exception as e:
        return f"❌ خطأ حرج في دورة الإنتاج: {str(e)}"
