import os
import json
from datetime import datetime
from duckduckgo_search import DDGS

# --- إعداد بيئة العمل السيادية ---
WORK_ZONE = "work_zone"
MEMORY_FILE = os.path.join(WORK_ZONE, "memory.json")

if not os.path.exists(WORK_ZONE):
    os.makedirs(WORK_ZONE)

# --- وظيفة البحث في الإنترنت (العين) ---
def sovereign_search(query):
    """البحث في الإنترنت وجلب نتائج حقيقية 2026"""
    print(f"[*] جاري البحث عن: {query}")
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=5)]
            return results
    except Exception as e:
        return f"خطأ في الاتصال بالإنترنت: {str(e)}"

# --- وظيفة الذاكرة المستديمة (العقل) ---
def update_memory(category, data):
    """تخزين المعلومات الجديدة في ذاكرة الشركة"""
    memory = {}
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            memory = json.load(f)
    
    if category not in memory:
        memory[category] = []
    
    # إضافة البيانات مع ختم الوقت السويدي
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "content": data
    }
    memory[category].append(entry)
    
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(memory, f, ensure_ascii=False, indent=4)
    return "تم الحفظ في الذاكرة السيادية."

# --- وظيفة التعلم الذاتي (الاستقلالية المقيدة) ---
def autonomous_agent_logic(objective):
    """هذا هو المحرك الذي سيعمل 24/7"""
    # 1. البحث
    search_results = sovereign_search(f"site:.se {objective}")
    
    # 2. التخزين
    update_memory("market_research", search_results)
    
    return f"تم إنهاء جولة البحث بنجاح. النتائج محفوظة في {MEMORY_FILE}"
