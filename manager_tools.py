import os
import json
from datetime import datetime

# مسارات ملفات التعلم
KNOWLEDGE_DIR = "knowledge_base"
os.makedirs(KNOWLEDGE_DIR, exist_ok=True)

def archive_knowledge(role, data):
    """حفظ ما تعلمه المساعد في ملفه الخاص"""
    filename = os.path.join(KNOWLEDGE_DIR, f"{role.lower()}_learning.json")
    
    # تجهيز المعلومة الجديدة
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "knowledge_unit": data
    }
    
    # قراءة الملف الحالي أو إنشاء قائمة جديدة
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = []
    
    history.append(entry)
    
    # حفظ البيانات
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)
    
    return f"✅ تم أرشفة المعرفة في سجل الـ {role}"
