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
    """تقرير مجلس الإدارة الكامل مع الأرشفة"""
    search_results = sovereign_search(task)
    op1 = consult_deepseek(f"حلل هذه البيانات تقنياً لشركتنا: {search_results}")
    op2 = consult_gemini(f"حلل هذه البيانات استراتيجياً لشركتنا: {search_results}")
    
    # أرشفة تلقائية للتعلم
    archive_learning("CTO", task, op1)
    archive_learning("COO", task, op2)
    
    return (f"📊 تقرير مجلس الإدارة (السيادة):\n\n"
            f"👤 CTO (DeepSeek):\n{op1[:500]}...\n\n"
            f"👤 COO (Gemini):\n{op2[:500]}...\n\n"
            f"📥 تم حفظ هذه الجلسة في قاعدة المعرفة الذاتية.")
