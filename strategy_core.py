import os
import logging
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

# إعداد السجلات لمراقبة أداء المحامي والمبرمج
logging.basicConfig(level=logging.INFO)

class StrategyCore:
    def __init__(self):
        # سحب المفاتيح من الخزنة الرقمية في Render (تأكد من مطابقة الأسماء في Render)
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.search_tool = DuckDuckGoSearchRun()
        
        # 1. إعداد المبرمج الرقمي (Llama 3.3)
        try:
            if self.groq_key:
                self.programmer = ChatGroq(
                    temperature=0, 
                    model_name="llama-3.3-70b-versatile", 
                    api_key=self.groq_key
                )
            else:
                self.programmer = None
        except Exception as e:
            logging.error(f"❌ فشل تهيئة Groq: {e}")
            self.programmer = None
            
        # 2. إعداد المحامي والمدقق (Gemini) - بروتوكول التشغيل المحصن
        self.legal_guardian = self._initialize_gemini()

    def _initialize_gemini(self):
        """محاولة تهيئة الموديل بأكثر من صيغة لضمان تخطي خطأ 404 وتأكيد المفتاح"""
        if not self.gemini_key:
            logging.error("❌ GEMINI_API_KEY غير موجود في إعدادات البيئة!")
            return None
        
        # قائمة بالأسماء الممكنة للموديل لضمان التوافق مع تحديثات جوجل 2026
        model_variants = ["gemini-1.5-flash", "models/gemini-1.5-flash", "gemini-pro"]
        
        for model_name in model_variants:
            try:
                # محاولة إنشاء المحرك
                model = ChatGoogleGenerativeAI(
                    model=model_name, 
                    google_api_key=self.gemini_key.strip(), # تنظيف المفتاح من أي مسافات زائدة
                    temperature=0
                )
                # اختبار الاتصال الفعلي (Invoke Test)
                model.invoke([HumanMessage(content="Hello")])
                logging.info(f"✅ تم تفعيل المحامي الرقمي بنجاح: {model_name}")
                return model
            except Exception as e:
                logging.warning(f"⚠️ تجربة {model_name} فشلت: {e}")
                continue
        
        return None

    def _fetch_reliable_info(self, topic):
        """البحث عن معلومات من مصادر سويدية موثوقة فقط 2026 (الهدف رقم 3)"""
        search_query = f"{topic} site:gov.se OR site:socialstyrelsen.se OR site:riksdagen.se 2026"
        try:
            return self.search_tool.run(search_query)
        except Exception as e:
            return f"فشل الاتصال بالإنترنت لجلب البيانات الحية: {str(e)}"

    def fact_check_service(self, raw_info):
        """المدقق السيادي: فحص المعلومات وتنقيتها من الأخطاء (الهدف رقم 6)"""
        if not self.legal_guardian:
            return f"تحذير: المحرك القانوني غير متصل. البيانات الخام: {raw_info}"
        
        verify_prompt = (
            f"بصفتك مدقق حقائق سيادي، راجع المعلومات التالية: \n{raw_info}\n"
            "استخرج فقط الحقائق الصافية والمتوافقة مع معايير السويد 2026."
        )
        try:
            verified_data = self.legal_guardian.invoke([
                SystemMessage(content="أنت مدقق حقائق صارم."),
                HumanMessage(content=verify_prompt)
            ])
            return verified_data.content
        except Exception as e:
            logging.error(f"Fact check error: {e}")
            return f"بيانات خام (فشل التدقيق): {raw_info}"

    def consult_deepseek(self, task, context):
        """استشارة المبرمج الرقمي مع نظام التبديل الآلي (Failover) (الهدف رقم 9)"""
        prompt = f"المهمة: {task}\nالسياق المحدث: {context}\nاكتب الكود البرمجي اللازم."
        
        if not self.programmer:
            return self._emergency_programming(prompt)

        try:
            response = self.programmer.invoke(prompt)
            return response.content
        except Exception as e:
            if any(err in str(e
