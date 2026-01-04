import os
import json
from datetime import datetime
from duckduckgo_search import DDGS
from langchain_groq import ChatGroq

# 1. إعدادات الأمان والبيئة
GROQ_KEY = os.getenv("GROQ_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# 2. إعدادات المجلدات (الذاكرة المؤسسية)
WORK_ZONE = "work_zone"
KNOWLEDGE_BASE = "knowledge_base"
os.makedirs(WORK_ZONE, exist_ok=True)
os.makedirs(KNOWLEDGE_BASE, exist_ok=True)

AI_STAFF_FILE = os.path.join(WORK_ZONE, "ai_staff.json")

# --- وظائف الاتصال بالعقول الرقمية ---

def consult_deepseek(prompt):
    """استشارة CTO (DeepSeek)"""
    if not GROQ_KEY: return "خطأ: مفتاح GROQ مفقود"
    try:
        llm = ChatGroq(temperature=0.1, model_name="deepseek-r1-distill-llama-70b", api_key=GROQ_KEY)
        return llm.invoke(prompt).content
    except Exception as e:
        return f"خطأ تقني في DeepSeek: {str(e)}"

def consult_gemini(prompt):
    """استشارة COO (Gemini/Llama)"""
    if not GROQ_KEY: return "خطأ: مفتاح GROQ مفقود"
    try:
        llm = ChatGroq(temperature=0.3, model_name="llama-3.3-70b-versatile", api_key=GROQ_KEY)
        return llm.invoke(f"بصفتك مساعد استراتيجي، حلل: {prompt}").content
    except Exception as e:
        return f"خطأ تقني في Gemini: {str(e)}"

# --- وظائف التعلم والأرشفة (الجديدة) ---

def archive_learning(role, unit_name, content):
    """حفظ ما تم تعلمه في قاعدة المعرفة"""
    filename = os.path.join(KNOWLEDGE_BASE, f"{role.lower()}_brain.json")
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "topic": unit_name,
        "details": content
    }
    
    data = []
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    
    data.append(entry)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return f"✅ تم حفظ 'وحدة معرفة' جديدة في سجل {role}"

# --- وظائف البحث المتقدم ---

def sovereign_search(query):
    """البحث في الإنترنت لخدمة التعلم الذاتي"""
    try:
        with DDGS() as ddgs:
            return [r for r in ddgs.text(query, max_results=5)]
    except Exception as e:
        return f"خطأ في البحث: {str(e)}"

def get_board_decision(task):
    """تقرير مجلس الإدارة مع التلخيص الذكي والأرشفة"""
    # 1. البحث والتقصي
    search_results = sovereign_search(task)
    
    # 2. استشارة العقول
    op1 = consult_deepseek(f"بصفتك CTO، استخرج أهم 3 أدوات تقنية من هذه النتائج وكيفية تطبيقها: {search_results}")
    op2 = consult_gemini(f"بصفتك COO، استخرج نموذج الربح الأنسب لهذه التقنيات: {search_results}")
    
    # 3. وظيفة التلخيص السيادي (الجديدة)
    # المدير هنا يجمع الآراء ويصيغ خلاصة لك
    summary_prompt = f"لدينا تقرير تقني من CTO: {op1[:500]} وتقرير إداري من COO: {op2[:500]}. ادمجهما في ملخص تنفيذي واحد من 4 أسطر فقط يوضح الخطوة القادمة للشركة."
    executive_summary = consult_gemini(summary_prompt) # Gemini يتولى الصياغة النهائية
    
    # 4. الأرشفة الذكية
    archive_learning("CTO", task, op1)
    archive_learning("COO", task, op2)
    archive_learning("MANAGER", f"Summary_{task}", executive_summary)
    
    return (f"🏛️ **ملخص الساعة السيادي**:\n\n"
            f"🎯 **الخلاصة:** {executive_summary}\n\n"
            f"🛠️ **تقنياً (CTO):** {op1[:200]}...\n"
            f"💰 **مالياً (COO):** {op2[:200]}...\n\n"
            f"📁 تم حفظ التفاصيل كاملة في قاعدة المعرفة.")
