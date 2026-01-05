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

if not os.path.exists(KNOWLEDGE_BASE_DIR):
    os.makedirs(KNOWLEDGE_BASE_DIR)

# --- إعداد العقول لعام 2026 (تم الإصلاح) ---
# عقل التحليل التقني
llm_deepseek = ChatGroq(
    temperature=0.1, 
    model_name="llama-3.3-70b-versatile", 
    groq_api_key=GK_KEY
)

# عقل الاستراتيجية المالية - المسار الكامل لضمان عدم حدوث 404
llm_gemini = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash", 
    google_api_key=GOOGLE_KEY,
    convert_system_message_to_human=True
)

search_tool = DuckDuckGoSearchRun()

def archive_learning(role, task, content):
    """أرشفة البيانات في قاعدة المعرفة - الأساس الذي لا يمس"""
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
        # 1. البحث باستخدام أدوات البحث السيادية
        search_results = search_tool.run(task)
        
        # 2. تحليل CTO
        cto_prompt = f"حلل تقنياً لعام 2026 الأدوات والفرص التالية: {search_results}"
        op1 = llm_deepseek.invoke([
            SystemMessage(content="أنت CTO خبير ومستشار تقني سيادي."), 
            HumanMessage(content=cto_prompt)
        ]).content
        
        # 3. تحليل COO
        coo_prompt = f"صغ نموذج ربحية وخطة عمل بناءً على المعطيات: {search_results}"
        op2 = llm_gemini.invoke([
            SystemMessage(content="أنت COO استراتيجي ومحلل مالي للفرص الربحية."), 
            HumanMessage(content=coo_prompt)
        ]).content
        
        # 4. تلخيص المدير التنفيذي السيادي
        summary_prompt = (
            f"بناءً على التقارير التالية:\n"
            f"الرؤية التقنية: {op1[:600]}\n"
            f"الرؤية المالية: {op2[:600]}\n"
            f"صغ القرار النهائي بلهجة قوية، سيادية، ومباشرة للقائد."
        )
        executive_summary = llm_gemini.invoke([
            SystemMessage(content="أنت المدير التنفيذي السيادي والقائد الفعلي للشركة."), 
            HumanMessage(content=summary_prompt)
        ]).content
        
        # 5. الأرشفة في "الأساس الذي لا يمس"
        archive_learning("CTO", task, op1)
        archive_learning("COO", task, op2)
        archive_learning("MANAGER", task, executive_summary)
        
        current_time = datetime.datetime.now(SWEDEN_TZ).strftime("%H:%M")
        
        # التنسيق النهائي للرد
        res = (f"🏛️ **قرار مجلس الإدارة السيادي ({current_time})**\n\n"
               f"🎯 **الخلاصة:** {executive_summary}\n\n"
               f"🛠️ **تقنياً (CTO):** {op1[:250]}...\n\n"
               f"💰 **مالياً (COO):** {op2[:250]}...\n\n"
               f"📁 تم التحديث بنجاح في قاعدة المعرفة السيادية.")
        return res

    except Exception as e:
        # تسجيل الخطأ بوضوح لتسهيل المتابعة
        return f"❌ خطأ في النظام: {str(e)}"
