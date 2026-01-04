import os
import json
from datetime import datetime
from duckduckgo_search import DDGS
from langchain_groq import ChatGroq

# --- التعديل الأمني السيادي ---
# الكود الآن يبحث عن المفاتيح في "خزنة" النظام ولا يظهرها للعلن
GROQ_KEY = os.getenv("GROQ_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

WORK_ZONE = "work_zone"
AI_STAFF_FILE = os.path.join(WORK_ZONE, "ai_staff.json")

def consult_deepseek(prompt):
    """استشارة DeepSeek بأمان"""
    if not GROQ_KEY:
        return "خطأ: مفتاح GROQ غير معرف في إعدادات Render"
    try:
        llm = ChatGroq(temperature=0.2, model_name="deepseek-r1-distill-llama-70b", api_key=GROQ_KEY)
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"خطأ تقني: {str(e)}"

def consult_gemini(prompt):
    """استشارة العقل الثاني بأمان"""
    if not GROQ_KEY:
        return "خطأ: مفتاح GROQ غير معرف"
    try:
        # نستخدم موديل Llama 3.3 كمساعد استراتيجي حالياً
        llm = ChatGroq(temperature=0.4, model_name="llama-3.3-70b-versatile", api_key=GROQ_KEY)
        response = llm.invoke(f"بصفتك مساعد استراتيجي، حلل: {prompt}")
        return response.content
    except Exception as e:
        return f"خطأ تقني: {str(e)}"

def get_board_decision(task):
    """تقرير مجلس الإدارة"""
    opinion_1 = consult_deepseek(f"تحليل تقني لـ: {task}")
    opinion_2 = consult_gemini(f"تحليل استراتيجي لـ: {task}")
    
    return (f"📊 تقرير السيادة:\n\n"
            f"👤 DeepSeek:\n{opinion_1[:300]}...\n\n"
            f"👤 Gemini (Assistant):\n{opinion_2[:300]}...\n\n"
            f"✅ القرار: جاري التنفيذ.")
