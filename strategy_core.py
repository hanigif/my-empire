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
        # سحب المفاتيح من الخزنة الرقمية
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.search_tool = DuckDuckGoSearchRun()
        
        # توقيت السويد الرسمي للعمليات السيادية
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
            
        # 2. إعداد المحامي والمدقق (Gemini) - بروتوكول التشغيل المحصن ضد 404
        self.legal_guardian = self._initialize_gemini_with_failover()

    def _initialize_gemini_with_failover(self):
        """تحديث سيادي: إجبار السيرفر على استخدام المسارات المطلقة وتجاوز خطأ v1beta"""
        if not self.gemini_key:
            logging.error("❌ مفتاح Gemini غائب عن إعدادات الرندر.")
            return None
        
        clean_key = self.gemini_key.strip()
        
        # المسارات المطلقة هي المفتاح لتجاوز خطأ 404 في بيئات الاستضافة مثل Render
        variants = [
            "models/gemini-1.5-pro-latest", 
            "models/gemini-1.5-flash-latest",
            "gemini-1.5-pro",
            "gemini-pro"
        ]
        
        for model_path in variants:
            try:
                # إعداد المحرك مع التوافق القسري (Forced Compatibility)
                model = ChatGoogleGenerativeAI(
                    model=model_path, 
                    google_api_key=clean_key,
                    temperature=0,
                    # تحويل رسائل النظام لرسائل مستخدم لضمان قبول السيرفر للطلب وتجنب البروتوكولات القديمة
                    convert_system_message_to_human=True 
                )
                # اختبار الاتصال الفعلي (Handshake)
                model.invoke([HumanMessage(content="Sovereign Handshake")])
                logging.info(f"⚖️ المحامي الرقمي اخترق الحاجز التقني عبر: {model_path}")
                return model
            except Exception as e:
                logging.warning(f"⚠️ تجربة المسار {model_path} فشلت: {e}")
                continue
        
        return None

    def _fetch_reliable_info(self, topic):
        """البحث عن معلومات من مصادر سويدية موثوقة فقط 2026 (الهدف رقم
