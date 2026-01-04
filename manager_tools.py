import os
import json
import datetime
import pytz
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

# --- الإعدادات السيادية ---
GK_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY")
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')
KNOWLEDGE_BASE_DIR = "knowledge_base"

if not os.path.exists(KNOWLEDGE_BASE_DIR):
    os.makedirs(KNOWLEDGE_BASE_DIR)

# --- إعداد العقول (تحديث الموديلات لعام 2026) ---
# CTO: تم استبدال الموديل الموقوف بـ Llama 3.3 الأحدث والأقوى
llm_deepseek = ChatGroq(
    temperature=0.1, 
    model_name="llama-3.3-70b-versatile", 
    groq_api_key=GK_KEY
)

# COO: Gemini 1.5 Flash للسرعة والذكاء الإداري
llm_gemini = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", 
    google_api_key=GOOGLE_KEY
)

search_tool = DuckDuckGoSearchRun()

def archive_learning(role, task, content):
    """أرشفة كل خطوة في قاعدة المعرفة"""
    date_str = datetime.datetime.now(SWEDEN_TZ).strftime("%Y-%m-%d")
    file_path = os.path.join(KNOWLEDGE_BASE_DIR, f"{role.lower()}_brain.json")
    
    entry = {
        "timestamp": datetime.datetime.now(SWEDEN_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "task": task,
        "content": content
    }
    
    data = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except: data = []
    
    data.append(entry)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_board_decision(task):
    """تنسيق قرار مجلس الإدارة الرقمي"""
    try:
        # البحث
        search_results = search_tool.run(task)
        
        # تحليل CTO
        cto_prompt = f"حلل تقنياً لعام 2026 الأدوات والفرص التالية: {search_results}"
        op1 = llm_deepseek.invoke([SystemMessage(content="أنت CTO خبير."), HumanMessage(content=cto_prompt)]).content
        
        # تحليل COO
        coo_prompt = f"صغ نموذج ربحية وخطة عمل بناءً على: {search_results}"
        op2 = llm_gemini.invoke([SystemMessage(content="أنت COO استراتيجي."), HumanMessage(content=coo_prompt)]).content
        
        # تلخيص المدير (السيادي)
        summary_prompt = f"لدينا رؤية تقنية: {op1[:500]} ورؤية مالية: {op2[:500]}. اعطِ ملخصاً تنفيذياً في 4 أسطر."
        executive_summary = llm_gemini.invoke([SystemMessage(content="أنت المدير التنفيذي."), HumanMessage(content=summary_prompt)]).content
        
        # الأرشفة
        archive_learning("CTO", task, op1)
        archive_learning("COO", task, op2)
        archive_learning("MANAGER", task, executive_summary)
        
        return (f"🏛️ **ملخص الساعة السيادي**:\n\n"
                f"🎯 **الخلاصة:** {executive_summary}\n\n"
                f"🛠️ **تقنياً (CTO):** {op1[:300]}...\n\n"
                f"💰 **مالياً (COO):** {op2[:300]}...\n\n"
                f"📁 تم الأرشفة بنجاح.")
    except Exception as e:
        return f"❌ فشل في معالجة الطلب: {str(e)}"
