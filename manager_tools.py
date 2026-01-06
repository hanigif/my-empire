import os
import json
import datetime
import pytz
from github import Github 
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

# --- الإعدادات السيادية (2026) ---
GK_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") 
REPO_NAME = "hanigif/Sovereign-Assets"
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')
KNOWLEDGE_BASE_DIR = "knowledge_base"
PRODUCTION_DIR = "production_v1"

for folder in [KNOWLEDGE_BASE_DIR, PRODUCTION_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# --- إعداد العقول السيادية ---
llm_backup = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)

try:
    llm_gemini = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro", 
        google_api_key=GOOGLE_KEY,
        convert_system_message_to_human=True
    )
except Exception:
    llm_gemini = llm_backup 

search_tool = DuckDuckGoSearchRun()

def export_to_github(filename, content, commit_message):
    try:
        if not GITHUB_TOKEN: return "⚠️ GITHUB_TOKEN مفقود."
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        try:
            contents = repo.get_contents(filename)
            repo.update_file(contents.path, commit_message, content, contents.sha)
        except:
            repo.create_file(filename, commit_message, content)
        return f"✅ تم التأمين: {filename}"
    except Exception as e:
        return f"❌ فشل رفع {filename}: {str(e)}"

def archive_and_save_production(role, filename, content):
    file_path = os.path.join(PRODUCTION_DIR, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
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

def safe_invoke(llm, messages):
    try:
        return llm.invoke(messages).content
    except Exception as e:
        return llm_backup.invoke(messages).content

def get_auditor_review(logic, ui, task):
    """قسم الاختبار المستقل: مراجعة الجودة والتدقيق الطبي الصارم"""
    audit_prompt = (f"أنت مفتش جودة طبي مستقل (QA Auditor). راجع كود المنطق: {logic} وكود الواجهة: {ui}. "
                    f"للمهمة: {task}. ابحث عن: أخطاء طبية، عدم مطابقة للمعايير السويدية، ثغرات خصوصية. "
                    f"إذا وجدت خطأ طبياً حرجاً، ابدأ ردك فوراً بكلمة 'STOP_PRODUCTION'. "
                    f"قدم نصائح تقنية واضحة للتطوير في الدورة القادمة.")
    return safe_invoke(llm_gemini, [
        SystemMessage(content="أنت رئيس قسم الجودة المستقل. هدفك حماية سمعة القائد الطبية وضمان أعلى معايير الجودة."),
        HumanMessage(content=audit_prompt)
    ])

def get_board_decision(task):
    """محرك التطوير الذاتي: إنتاج، فحص، تحسين (3 دورات جودة)"""
    try:
        # 1. البحث في المعايير السويدية الحديثة
        search_query = f"Sweden AI medical software standards 2026 Patientdatalagen Socialstyrelsen"
        standards = search_tool.run(search_query)
        
        current_logic = ""
        current_ui = ""
        audit_report = ""
        iteration_history = ""

        # دورة التطوير الذاتي (3 دورات تحسين)
        for i in range(1, 4):
            # الـ CTO ينتج أو يحسن الكود بناءً على تقرير الاختبار السابق
            cto_prompt = (f"الدورة {i}: بناءً على معايير السويد: {standards}. "
                          f"المهمة: {task}. التاريخ والملاحظات: {iteration_history}. "
                          f"اكتب كود (logic.py) محسن، دقيق طبياً، ومؤمن بالكامل.")
            current_logic = safe_invoke(llm_backup, [
                SystemMessage(content="أنت Senior Medical Architect. وظيفتك تطوير كود طبي سيادي عالمي المستوى."),
                HumanMessage(content=cto_prompt)
            ])
            
            # إنتاج الواجهة
            ui_prompt = f"صمم واجهة Streamlit احترافية لهذا المنطق المطور: {current_logic}"
            current_ui = safe_invoke(llm_backup, [
                SystemMessage(content="أنت Frontend Developer طبي متخصص."),
                HumanMessage(content=ui_prompt)
            ])

            # قسم الاختبار يراجع نتاج الدورة
            audit_report = get_auditor_review(current_logic, current_ui, task)
            
            # إذا كان الكود ممتازاً طبياً ولا يحتاج تعديل جوهري، نخرج من الدورة
            if "STOP_PRODUCTION" not in audit_report:
                break
            
            # تحديث تاريخ الإخفاقات للدورة التالية ليتعلم النظام من خطئه
            iteration_history = f"فشل في الدورة {i}: {audit_report}"

        # التحقق النهائي من Kill Switch
        if "STOP_PRODUCTION" in audit_report:
            return (f"🛑 **توقف التطوير الذاتي - لم نصل للمعايير المطلوبة**\n\n"
                    f"حاول النظام تطوير نفسه 3 مرات وفشل في اجتياز اختبار الجودة الطبي:\n\n"
                    f"{audit_report}\n\n"
                    f"⚠️ تدخل القائد مطلوب لتعديل المتطلبات.")

        # الـ COO: استراتيجية البيع المبنية على "جودة التطوير الذاتي"
        co_prompt = f"صمم عرض بيع يركز على أن المنتج مر بـ 3 مراحل تحسين ذاتي ومطابق لمعايير: {standards}"
        sales_strategy = safe_invoke(llm_gemini, [
            SystemMessage(content="أنت COO خبير سوق."),
            HumanMessage(content=co_prompt)
        ])
        
        ts = datetime.datetime.now(SWEDEN_TZ).strftime("%H%M")
        code_fn, ui_fn, doc_fn = f"evolved_logic_{ts}.py", f"evolved_ui_{ts}.py", f"evolved_offer_{ts}.md"
        
        archive_and_save_production("TECH_LOGIC", code_fn, current_logic)
        archive_and_save_production("FRONTEND_UI", ui_fn, current_ui)
        archive_and_save_production("SALES_DOC", doc_fn, sales_strategy)
        
        git_1 = export_to_github(code_fn, current_logic, f"Evolved Logic V4.0 {ts}")
        git_2 = export_to_github(ui_fn, current_ui, f"Evolved UI V4.0 {ts}")
        git_3 = export_to_github(doc_fn, sales_strategy, f"Evolved Sales Strategy {ts}")
        
        return (f"🏛️ **تقرير التطوير الذاتي المعتمد ({ts})**\n\n"
                f"🛡️ **حالة الأصول:** تم رفع النسخة الأكثر نضجاً بعد دورات التحسين.\n"
                f"✅ **نتيجة الاختبار النهائي:**\n{audit_report[:500]}...")

    except Exception as e:
        return f"❌ فشل في محرك التطوير الذاتي: {str(e)}"
