import os
import json
import datetime
import pytz
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

# --- الإعدادات الأساسية ---
GK_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY")
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')
KNOWLEDGE_BASE_DIR = "knowledge_base"

if not os.path.exists(KNOWLEDGE_BASE_DIR):
    os.makedirs(KNOWLEDGE_BASE_DIR)

# --- إعداد العقول السيادية ---
# CTO: DeepSeek (عبر Groq باستخدام Llama 3.3 المحدث)
llm_deepseek = ChatGroq(
    temperature=0.1, 
    model_name="llama-3.3-70b-versatile", 
    groq_api_key=GK_KEY
)

# COO: Gemini (الإدارة والربحية)
llm_gemini = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", 
    google_api_key=GOOGLE_KEY
)

search_tool = DuckDuckGoSearchRun()

def archive_learning(role, task, content):
    """حفظ النتائج في ملفات JSON منظمة"""
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
            except:
                data = []
    
    data.append(entry)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_board_decision(task):
    """تنسيق العمل بين العقول وأرشفة النتائج مع التلخيص التنفيذي"""
    try:
        # 1. البحث عن المعلومات
        search_results = search_tool.run(task)
        
        # 2. استشارة الـ CTO (الجانب التقني)
        cto_prompt = f"بصفتك CTO، حلل هذه النتائج تقنياً واستخرج أفضل الأدوات البرمجية لعام 2026: {search_results}"
        op1 = llm_deepseek.invoke([SystemMessage(content="أنت كبير المسؤولين التقنيين (CTO)."), HumanMessage(content=cto_prompt)]).content
        
        # 3. استشارة الـ COO (الجانب الإداري والمالي)
        coo_prompt = f"بصفتك COO، حلل هذه النتائج لاستخراج نموذج ربحية (Monetization) وخطة عمل: {search_results}"
        op2 = llm_gemini.invoke([SystemMessage(content="أنت كبير مسؤولي العمليات (COO)."), HumanMessage(content=coo_prompt)]).content
        
        # 4. التلخيص التنفيذي (المدير السيادي)
        summary_prompt = f"لدينا تقرير تقني: {op1[:500]} وتقرير مالي: {op2[:500]}. صغ ملخصاً تنفيذياً في 3-4 أسطر يحدد الخطوة القادمة للشركة."
        executive_summary = llm_gemini.invoke([SystemMessage(content="أنت المدير التنفيذي السيادي."), HumanMessage(content=summary_prompt)]).content
        
        # 5. الأرشفة
        archive_learning("CTO", task, op1)
        archive_learning("COO", task, op2)
        archive_learning("MANAGER", f"Summary_{task}", executive_summary)
        
        return (f"🏛️ **ملخص الساعة السيادي**:\n\n"
                f"🎯 **الخلاصة:** {executive_summary}\n\n"
                f"🛠️ **تقنياً (CTO):** {op1[:250]}...\n\n"
                f"💰 **مالياً (COO):** {op2[:250]}...\n\n"
                f"📁 تم حفظ التفاصيل كاملة في قاعدة المعرفة.")
                
    except Exception as e:
        return f"❌ خطأ في النظام السيادي: {str(e)}"
