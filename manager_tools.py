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

# 2. عقل Gemini (المحرك الأساسي - مع معالجة الأخطاء)
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
    """تنسيق قرار مجلس الإدارة: ابتكار منتجات لقطاع الصحة الرقمي (HealthTech)"""
    try:
        # 1. البحث عن مشاكل الخصوصية والامتثال في القطاع الصحي 2026
        # نركز البحث على السويد وأوروبا (AI Act & GDPR)
        search_query = (
            f"HealthTech Sweden AI compliance issues 2026 - "
            f"patient data privacy gaps in private clinics - AI Act healthcare impact"
        )
        search_results = search_tool.run(search_query)
        
        # 2. تحليل CTO (عبر Llama/Groq) - ابتكار الحل التقني
        cto_prompt = (
            f"بناءً على مشاكل الخصوصية الطبية: {search_results}. "
            f"صمم 'وكيل امتثال سيادي' (Sovereign Compliance Agent) يقوم بتجهيل بيانات المرضى (Anonymization) "
            f"قبل معالجتها بأي ذكاء اصطناعي. ركز على كود يمكن بيعه كبراءة اختراع أو SaaS."
        )
        op1 = safe_invoke(llm_backup, [
            SystemMessage(content="أنت CTO خبير في الأمن السيبراني الطبي والامتثال الرقمي لعام 2026."), 
            HumanMessage(content=cto_prompt)
        ])
        
        # 3. تحليل COO (عبر Gemini) - استراتيجية الربح والبيع
        coo_prompt = (
            f"الحل التقني: {op1[:500]}. "
            f"صغ نموذج ربحية لبيعه للعيادات والمستشفيات الخاصة في السويد. "
            f"كم السعر المتوقع؟ وكيف نضمن تسابق الشركات لشرائه لتجنب غرامات AI Act؟"
        )
        op2 = safe_invoke(llm_gemini, [
            SystemMessage(content="أنت COO استراتيجي متخصص في تطوير أعمال الـ HealthTech والاشتراكات عالية القيمة."), 
            HumanMessage(content=coo_prompt)
        ])
        
        # 4. تلخيص المدير السيادي (القرار النهائي والمنتج للبيع)
        summary_prompt = (
            f"الرؤية التقنية: {op1[:500]}. الرؤية المالية: {op2[:500]}. "
            f"صغ المنتج النهائي الذي سأقوم ببيعه لشركات الصحة."
        )
        executive_summary = safe_invoke(llm_gemini, [
            SystemMessage(content="أنت المدير التنفيذي السيادي. هدفك تحويل المشاكل التقنية إلى منتجات غالية الثمن."), 
            HumanMessage(content=summary_prompt)
        ])
        
        # 5. الأرشفة السيادية المحدثة
        archive_learning("CTO_TECH", task, op1)
        archive_learning("COO_BUSINESS", task, op2)
        archive_learning("SOVEREIGN_MANAGER", task, executive_summary)
        
        current_time = datetime.datetime.now(SWEDEN_TZ).strftime("%H:%M")
        return (f"🏛️ **قرار مجلس الإدارة السيادي (قطاع الصحة 2026)**\n\n"
                f"🎯 **المنتج المبتكر للبيع:** {executive_summary}\n\n"
                f"🛠️ **القيمة التقنية:** {op1[:250]}...\n\n"
                f"💰 **خطة تحقيق الدخل:** {op2[:250]}...\n\n"
                f"📁 تم التحديث بنجاح (نظام الحماية والهدف الطبي نشط).")

    except Exception as e:
        return f"❌ خطأ حرج في النظام السيادي: {str(e)}"
