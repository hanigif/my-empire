import os
import logging
import datetime
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class StrategyCore:
    def __init__(self):
        # تنظيف المفاتيح
        self.groq_key = os.getenv("GROQ_API_KEY", "").strip()
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.search_tool = DuckDuckGoSearchRun()
        self.current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. المبرمج (Llama) - يعمل بنجاح بناءً على سجلاتك
        self.programmer = self._init_programmer()
            
        # 2. المحامي (Gemini) - التعديل الجذري هنا
        self.legal_guardian = self._init_legal_guardian()

    def _init_programmer(self):
        if self.groq_key:
            try:
                return ChatGroq(model_name="llama-3.3-70b-versatile", api_key=self.groq_key, temperature=0)
            except Exception as e:
                logging.error(f"❌ خطأ المبرمج: {e}")
        return None

    def _init_legal_guardian(self):
        """الحل النهائي: فرض الموديل بدون المعامل version لتجنب الـ Conflict"""
        if not self.gemini_key:
            return None
        
        # جرب المسارات الكاملة مباشرة داخل اسم الموديل
        variants = [
            "gemini-1.5-flash", 
            "gemini-1.5-pro"
        ]
        
        for model_name in variants:
            try:
                # التعديل: إزالة 'version' وإضافة 'models/' يدوياً لضمان المسار الصحيح
                model = ChatGoogleGenerativeAI(
                    model=f"models/{model_name}", 
                    google_api_key=self.gemini_key,
                    temperature=0,
                    # تحويل رسائل النظام لهيئة يفهمها الموديل القديم/المستقر
                    convert_system_message_to_human=True 
                )
                # اختبار Handshake
                model.invoke([HumanMessage(content="Test")])
                logging.info(f"⚖️ المحامي السيادي متصل بنجاح عبر: {model_name}")
                return model
            except Exception as e:
                logging.warning(f"⚠️ {model_name} لا يزال يرفض: {e}")
                continue
        return None

    def find_swedish_leads(self):
        """وظيفة البحث عن أهداف وصياغة رسالة مبيعات"""
        logging.info("🔍 جاري البحث عن شركات سويدية...")
        query = "Swedish companies data privacy issues 2026 news"
        try:
            raw_results = self.search_tool.run(query)
            # نستخدم المبرمج (Llama) للصياغة لأنه يعمل لديك بكفاءة
            prompt = f"بناءً على الأخبار: {raw_results}\nاستخرج اسم شركة سويدية حقيقية وصغ رسالة مبيعات لمنتج 'المدير السيادي'."
            return self.consult_deepseek("Sales Pitch", prompt)
        except Exception as e:
            return f"Error: {e}"

    def consult_deepseek(self, task, context):
        if not self.programmer: return "Programmer Offline"
        try:
            return self.programmer.invoke(f"{task}: {context}").content
        except Exception as e:
            return f"Execution Error: {e}"

    def fact_check_service(self, raw_info):
        if not self.legal_guardian: return raw_info
        try:
            return self.legal_guardian.invoke([HumanMessage(content=f"Verify this: {raw_info}")]).content
        except: return raw_info
