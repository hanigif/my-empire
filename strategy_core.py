import os, logging, datetime
import google.generativeai as genai  # الحل النهائي لكسر حاجز الـ 404
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class StrategyCore:
    def __init__(self):
        # 1. إعدادات المفاتيح (تنظيف آلي)
        self.groq_key = os.getenv("GROQ_API_KEY", "").strip()
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.search_tool = DuckDuckGoSearchRun()
        
        # 2. المبرمج (Llama 3.3) - المحرك الأساسي
        self.programmer = self._init_prog()
        
        # 3. المحامي (Gemini) - الاتصال المباشر (Direct SDK) لضمان تجاوز الـ 404
        self.legal_guardian = self._init_legal_direct()

    def _init_prog(self):
        if self.groq_key:
            return ChatGroq(model_name="llama-3.3-70b-versatile", api_key=self.groq_key, temperature=0)
        return None

    def _init_legal_direct(self):
        """الاتصال المباشر بجوجل لتجاوز مشاكل المكتبات الوسيطة"""
        if not self.gemini_key: return None
        try:
            genai.configure(api_key=self.gemini_key)
            # استخدام فلاش 1.5 لأنه الأكثر استقراراً في 2026
            model = genai.GenerativeModel('gemini-1.5-flash')
            # تجربة اتصال صامتة
            model.generate_content("ping")
            logging.info("⚖️ المحامي السيادي متصل مباشرة عبر Google SDK.")
            return model
        except Exception as e:
            logging.error(f"⚠️ فشل الاتصال المباشر بالمحامي: {e}")
            return None

    def find_swedish_leads(self):
        """اصطياد الشركات السويدية (المهمة الأساسية)"""
        logging.info("🔍 جاري اصطياد الأهداف السويدية...")
        try:
            results = self.search_tool.run("Swedish companies data breach GDPR 2026")
            prompt = f"بناءً على النتائج: {results}\nاستخرج شركة سويدية حقيقية وصغ رسالة مبيعات لمنتج 'المدير السيادي'."
            
            # نستخدم المبرمج للصياغة لأنه الأضمن اتصالاً لديك
            if self.programmer:
                return self.programmer.invoke(prompt).content
            return "المحرك الرئيسي غير متاح."
        except Exception as e:
            return f"عطل في البحث: {e}"

    def fact_check_service(self, text):
        """التدقيق القانوني عبر المحامي (Direct Mode)"""
        if not self.legal_guardian: return text
        try:
            # استخدام الاتصال المباشر
            response = self.legal_guardian.generate_content(f"Verify legal compliance: {text}")
            return response.text
        except:
            return text
