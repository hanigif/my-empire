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
# استخدام الوقت الرسمي للسويد كما طلبت في تعليماتك
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')
KNOWLEDGE_BASE_DIR = "knowledge_base"

if not os.path.exists(KNOWLEDGE_BASE_DIR):
    os.makedirs(KNOWLEDGE_BASE_DIR)

# --- إعداد العقول (تحديث الموديلات لعام 2026) ---

# CTO: استخدام Llama 3.3-70b وهو المحرك التقني الأقوى حالياً عبر Groq
llm_deepseek = ChatGroq(
    temperature=0.1, 
    model_name="llama-3.3-70b-versatile", 
    groq_api_key=GK_KEY
)

# COO: تحديث Gemini لتجنب خطأ 404 عبر استخدام المعرف الأحدث والمستقر
llm_gemini = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest", # تم التحديث لضمان التوافق مع API v1
    google_api_key=GOOGLE_KEY,
    convert_system_message_to_human=True # لضمان أعلى توافق مع رسائل النظام
)

search_tool = DuckDuckGoSearchRun()

def archive_learning(role, task, content):
    """أرشفة كل خطوة في قاعدة المعرفة - الحفاظ على التقدم كأساس لا يمس"""
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
    """تنسيق قرار مجلس الإدارة الرقمي للمدير السيادي"""
    try:
        # 1. البحث عن أحدث البيانات
        search_results = search_tool.run(task)
        
        # 2. تحليل CTO (الرؤية التقنية)
        cto_prompt = f"حلل تقنياً لعام 2026 الأدوات والفرص التالية: {search_results}"
        op1 = llm_deepseek.invoke([
            SystemMessage(content="أنت CTO خبير ومستشار تقني سيادي."), 
            HumanMessage(content=cto_prompt)
        ]).content
        
        # 3. تحليل COO (الرؤية الإدارية والربحية)
        coo_prompt
