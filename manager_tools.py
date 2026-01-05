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

# --- إعداد العقول السيادية مع نظام الحماية ---

# 1. عقل Groq (المستقر جداً - الصمام الاحتياطي)
llm_backup = ChatGroq(
    temperature=0.1, 
    model_name="llama-3.3-70b-versatile", 
    groq_api_key=GK_KEY
)

# 2. عقل Gemini (المحرك الأساسي)
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
    """استدعاء ذكي: إذا فشل المحرك الأساسي، ينتقل للاحتياطي فوراً"""
    try:
        return llm.invoke(messages).content
    except Exception as e:
        print(f"⚠️ تنبيه: تم تفعيل المحرك الاحتياطي بسبب: {str(e)}")
        return llm_backup.invoke(messages).content

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
            try: data = json.load(f)
            except: data = []
    data.append(entry)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_board_decision(task):
    """تنسيق قرار مجلس الإدارة: الهندسة التقنية واستراتيجية البيع لقطاع الصحة 2026"""
    try:
        # 1. البحث عن المعايير التقنية الصارمة للامتثال الطبي 2026
        search_query = (
            f"Technical standards for medical data anonymization 2026 - "
            f"Differential Privacy in healthcare AI Europe - AI Act compliance automated auditing"
        )
        search_results = search_tool.run(search_query)
        
        # 2. تحليل CTO (عبر Llama/Groq) - التصميم الهيكلي للمنتج
        cto_prompt = (
            f"بناءً على المعايير: {search_results}. صمم الهيكل الهندسي لـ 'وكيل الامتثال السيادي'. "
            f"حدد خوارزميات التجهيل (مثل Differential Privacy) وكيفية بناء نظام الـ Audit Log "
            f"الذي يثبت قانونياً أن البيانات لم تتسرب للذكاء الاصطناعي."
        )
        op1 = safe_invoke(llm_backup, [
            SystemMessage(content="أنت كبير مهندسي برمجيات (Lead Architect) متخصص في أنظمة الأمان الطبية والامتثال القانوني."), 
            HumanMessage(content=cto_prompt)
        ])
        
        # 3. تحليل COO (عبر Gemini) - تحويل التقنية إلى 'عرض لا يرفض'
        coo_prompt = (
            f"التصميم التقني: {op1[:500]}. صمم 'وعد القيمة' (Value Proposition) لمدراء المستشفيات. "
            f"كيف نستخدم ميزة 'إثبات الامتثال الفوري' لبيعه بأعلى سعر وتجاوز المنافسين؟ "
            f"حدد باقات السعر لعام 2026 لخدمة الـ SaaS الطبية."
        )
        op2 = safe_invoke(llm_gemini, [
            SystemMessage(content="أنت خبير استراتيجيات بيع (Growth Hacker) في قطاع الـ HealthTech الأوروبي."), 
            HumanMessage(content=coo_prompt)
        ])
        
        # 4. تلخيص المدير السيادي (القرار النهائي)
        executive_summary = safe_invoke(llm_gemini, [
            SystemMessage(content="أنت المدير التنفيذي السيادي. وظيفتك صياغة العرض الفني والمالي النهائي الذي سيباع للشركات."), 
            HumanMessage(content=f"الهندسة: {op1[:400]}. استراتيجية البيع: {op2[:400]}. صغ العرض النهائي للعملاء.")
        ])
        
        # 5. الأرشفة السيادية المحدثة
        archive_learning("TECH_SPECS", task, op1)
        archive_learning("SALES_STRATEGY", task, op2)
        archive_learning("FINAL_OFFER", task, executive_summary)
        
        current_time = datetime.datetime.now(SWEDEN_TZ).strftime("%H:%M")
        return (f"🏛️ **قرار مجلس الإدارة السيادي - الهندسة والبيع ({current_time})**\n\n"
                f"🎯 **العرض النهائي (غير قابل للرفض):** {executive_summary}\n\n"
                f"🛠️ **المواصفات الهندسية للمحرك:** {op1[:300]}...\n\n"
                f"📜 **نظام إثبات الامتثال:** {op2[:300]}...\n\n"
                f"📁 تم حفظ المخططات الهندسية في 'الأساس الذي لا يمس'.")

    except Exception as e:
        return f"❌ خطأ حرج في الدورة الهندسية: {str(e)}"
