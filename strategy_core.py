import os
from langchain_groq import ChatGroq
# ملاحظة: سنستخدم مكتبة قوقل الرسمية أو LangChain للربط

class StrategyCore:
    def __init__(self):
        # سحب المفاتيح من خزنة Render التي أعددناها
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        
    def consult_deepseek(self, task):
        """استشارة المبرمج الرقمي (عبر Groq)"""
        if not self.groq_key: return "مفتاح Groq غير متوفر."
        try:
            llm = ChatGroq(temperature=0, model_name="deepseek-v3", api_key=self.groq_key)
            response = llm.invoke(f"كخبير برمجة، حلل هذه المهمة: {task}")
            return response.content
        except Exception as e:
            return f"خطأ في استشارة ديب سيك: {str(e)}"

    def consult_gemini(self, data):
        """استشارة المحلل الاستراتيجي (Gemini)"""
        # هنا سنضيف كود الربط بجيمناي فور وضعك للمفتاح
        return f"تم استلام البيانات للتحليل عبر جيمناي: {data[:50]}..."

    def get_consensus(self, topic):
        """بروتوكول الاستشارة الجماعية"""
        print(f"[*] بدء اجتماع مجلس الإدارة حول: {topic}")
        ds_opinion = self.consult_deepseek(topic)
        # هنا يمكن إضافة آراء البقية
        return {
            "DeepSeek_Opinion": ds_opinion,
            "Final_Decision": "قيد التحليل الجماعي..."
        }
