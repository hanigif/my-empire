import os
import logging
import datetime
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

# إعداد السجلات لمراقبة أداء المحامي والمبرمج
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class StrategyCore:
    def __init__(self):
        """تهيئة النخبة: استدعاء المحركات مع نظام الحماية الثلاثي"""
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.search_tool = DuckDuckGoSearchRun()
        
        # توقيت السويد الرسمي
        self.current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. إعداد المبرمج الرقمي (Llama 3.3)
        try:
            if self.groq_key:
                self.programmer = ChatGroq(
                    temperature=0, 
                    model_name="llama-3.3-70b-versatile", 
                    api_key=self.groq_key
                )
                logging.info("✅ المبرمج الرقمي جاهز للعمل.")
            else:
                self.programmer = None
        except Exception as e:
            logging.error(f"❌ عطل في تهيئة المبرمج: {e}")
            self.programmer = None
            
        # 2. إعداد المحامي والمدقق (Gemini)
        self.legal_guardian = self._initialize_gemini_with_failover()

    def _initialize_gemini_with_failover(self):
        """تجاوز خطأ 404 عبر فرض المسارات الكاملة"""
        if not self.gemini_key:
            logging.error("❌ مفتاح Gemini غائب.")
            return None
        
        clean_key = self.gemini_key.strip()
        variants = [
            "models/gemini-1.5-pro",
            "models/gemini-1.5-flash",
            "models/gemini-pro"
        ]
        
        for model_path in variants:
            try:
                model = ChatGoogleGenerativeAI(
                    model=model_path, 
                    google_api_key=clean_key,
                    temperature=0,
                    convert_system_message_to_human=True 
                )
                model.invoke([HumanMessage(content="Sovereign Handshake")])
                logging.info(f"⚖️ المحامي الرقمي متصل عبر: {model_path}")
                return model
            except Exception as e:
                logging.warning(f"⚠️ المسار {model_path} رفض: {e}")
                continue
        return None

    def find_swedish_leads(self):
        """وظيفة Sovereign Manager: البحث عن أهداف وصياغة رسائل مبيعات"""
        logging.info("🔍 جاري اصطياد أهداف تجارية في السويد...")
        query = "Swedish companies data breach GDPR 2025 2026 news"
        try:
            raw_results = self.search_tool.run(query)
            lead_prompt = (
                f"بناءً على الأخبار: {raw_results}\n"
                "استخرج اسم شركة سويدية حقيقية، وصغ رسالة مبيعات لمنتج 'المدير السيادي' لحل مشاكل الخصوصية."
            )
            return self.consult_deepseek("صياغة عرض بيع سيادي", lead_prompt)
        except Exception as e:
            return f"فشل البحث عن عملاء: {e}"

    def fact_check_service(self, raw_info):
        """المدقق السيادي: تنقية البيانات"""
        if not self.legal_guardian:
            return f"بيانات خام: {raw_info}"
        try:
            verified = self.legal_guardian.invoke([
                SystemMessage(content="أنت مدقق حقائق سويدي."),
                HumanMessage(content=f"حلل بدقة قوانين 2026: {raw_info}")
            ])
            return verified.content
        except Exception as e:
            logging.error(f"❌ خطأ تدقيق: {e}")
            return raw_info

    def consult_deepseek(self, task, context):
        """استشارة المبرمج الرقمي"""
        prompt = f"المهمة: {task}\nالسياق: {context}"
        if not self.programmer:
            return "المبرمج غير متاح حالياً."
        try:
            return self.programmer.invoke(prompt).content
        except Exception as e:
            logging.error(f"❌ خطأ برمجي: {e}")
            return "فشل تنفيذ المهمة البرمجية."
