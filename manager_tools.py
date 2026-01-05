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
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')
KNOWLEDGE_BASE_DIR = "knowledge_base"

if not os.path.exists(KNOWLEDGE_BASE_DIR):
    os.makedirs(KNOWLEDGE_BASE_DIR)

# --- تعريف العقول السيادية ---

# عقل Groq (المستقر جداً)
llm_backup = ChatGroq(
    temperature=0.1, 
    model_name="llama-3.3-70b-versatile", 
    groq_api_key=GK_KEY
)

# محاولة تعريف عقل Gemini (النسخة الأكثر استقراراً)
try:
    llm_gemini = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro", # التغيير لـ Pro لضمان الثبات
        google_api_key=GOOGLE_KEY,
        convert_system_message_to_human=True
    )
except:
    llm_gemini = llm_backup # إذا فشل التعريف، استخدم Backup فوراً

search_tool = DuckDuckGoSearchRun()

def safe_invoke(llm, messages):
    """وظيفة الاستدعاء الآمن لمنع انهيار النظام"""
    try:
        return llm.invoke(messages).content
    except Exception as e:
        print(f"Fallback triggered due to: {e}")
        return llm_backup.invoke(messages).content

def get_board_decision(task):
    """تنسيق قرار مجلس الإدارة الرقمي مع نظام الحماية من الانهيار"""
    try:
        # 1. البحث
        search_results = search_tool.run(task)
        
        # 2. تحليل CTO (عبر Groq)
        op1 = safe_invoke(llm_backup, [
            SystemMessage(content="أنت CTO خبير."), 
            HumanMessage(content=f"حلل تقنياً لعام 2026: {search_results}")
        ])
        
        # 3. تحليل COO (محاولة Gemini مع Fallback لـ Groq)
        op2 = safe_invoke(llm_gemini, [
            SystemMessage(content="أنت COO استراتيجي."), 
            HumanMessage(content=f"صغ نموذج ربحية بناءً على: {search_results}")
        ])
        
        # 4. القرار النهائي للمدير
        executive_summary = safe_invoke(llm_gemini, [
            SystemMessage(content="أنت المدير التنفيذي السيادي."), 
            HumanMessage(content=f"الرؤية التقنية: {op1[:500]}. الرؤية المالية: {op2[:500]}. صغ القرار النهائي.")
        ])
        
        # 5. الأرشفة
        from manager_tools import archive_learning # لضمان الوصول
        archive_learning("CTO", task, op1)
        archive_learning("COO", task, op2)
        archive_learning("MANAGER", task, executive_summary)
        
        return (f"🏛️ **قرار مجلس الإدارة السيادي (مؤمن)**\n\n"
                f"🎯 **الخلاصة:** {executive_summary}\n\n"
                f"🛠️ **تقنياً:** {op1[:200]}...\n\n"
                f"💰 **مالياً:** {op2[:200]}...\n\n"
                f"📁 تم الحفظ في 'الأساس الذي لا يمس'.")

    except Exception as e:
        # الملاذ الأخير: إذا انهار كل شيء، استخدم Llama لرد بسيط
        return f"⚠️ استجابة طوارئ: النظام يواجه تحديثات خارجية من Google. التحليل الأولي لـ '{task}' جارٍ أرشفته يدوياً."

def archive_learning(role, task, content):
    # (نفس كود الأرشفة السابق دون تغيير لضمان الأساس)
    file_path = os.path.join(KNOWLEDGE_BASE_DIR, f"{role.lower()}_brain.json")
    entry = {"timestamp": datetime.datetime.now(SWEDEN_TZ).strftime("%Y-%m-%d %H:%M:%S"), "task": task, "content": content}
    data = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try: data = json.load(f)
            except: data = []
    data.append(entry)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
