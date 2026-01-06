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
        """نظام تشغيل المحامي بأكثر من مسار لضمان تخطي خطأ 404 NOT FOUND"""
        if not self.gemini_key:
            logging.error("❌ مفتاح Gemini غائب عن إعدادات الرندر.")
            return None
        
        clean_key = self.gemini_key.strip()
        # تجربة المسارات الثلاثة الممكنة للموديل (حل جذري لمشكلة الـ 404)
        variants = ["models/gemini-1.5-flash", "gemini-1.5-flash", "models/gemini-pro"]
        
        for model_path in variants:
            try:
                model = ChatGoogleGenerativeAI(
                    model=model_path, 
                    google_api_key=clean_key,
                    temperature=0
                )
                # اختبار الاتصال الفعلي للتأكد من وجود الموديل في هذا المسار
                model.invoke([HumanMessage(content="test")])
                logging.info(f"⚖️ المحامي الرقمي اتصل بنجاح عبر المسار: {model_path}")
                return model
            except Exception as e:
                if "404" in str(e):
                    logging.warning(f"⚠️ المسار {model_path} غير موجود (404)، جاري تجربة البديل...")
                    continue
                logging.error(f"❌ خطأ في {model_path}: {e}")
                continue
        
        return None

    def _fetch_reliable_info(self, topic):
        """البحث عن معلومات من مصادر سويدية موثوقة فقط 2026 (الهدف رقم 3)"""
        logging.info(f"🌐 جاري البحث السيادي عن: {topic}")
        search_query = (
            f"{topic} site:gov.se OR site:socialstyrelsen.se OR "
            f"site:riksdagen.se OR site:1177.se 2026"
        )
        try:
            results = self.search_tool.run(search_query)
            return results if results else "لم يتم العثور على تحديثات قانونية جديدة."
        except Exception as e:
            return f"عطل في الاتصال بمصادر البيانات: {str(e)}"

    def fact_check_service(self, raw_info):
        """المدقق السيادي: تنقية البيانات من الأخطاء والبروباغندا (الهدف رقم 6)"""
        if not self.legal_guardian:
            return f"⚠️ بيانات غير مدققة قانونياً: {raw_info}"
        
        verify_prompt = (
            f"التوقيت الحالي: {self.current_time}\n"
            f"بصفتك مدقق حقائق سيادي في السويد، قم بتحليل المعلومات التالية:\n{raw_info}\n"
            "المطلوب: استخراج القوانين السويدية الفعلية لعام 2026 وحذف أي افتراضات غير دقيقة."
        )
        try:
            verified_data = self.legal_guardian.invoke([
                SystemMessage(content="أنت مدقق حقائق صارم تعمل لدى الحكومة السويدية."),
                HumanMessage(content=verify_prompt)
            ])
            return verified_data.content
        except Exception as e:
            logging.error(f"❌ عطل في التدقيق: {e}")
            return f"بيانات خام (تعذر التدقيق): {raw_info}"

    def consult_deepseek(self, task, context):
        """استشارة المبرمج الرقمي مع نظام التبديل الآلي (الهدف رقم 9)"""
        prompt = (
            f"المهمة المطلوبة: {task}\n"
            f"السياق القانوني المعتمد: {context}\n"
            "قم بكتابة الكود البرمجي مع مراعاة أعلى معايير الأمان السويدية."
        )
        
        if not self.programmer:
            logging.warning("⚠️ المبرمج الأساسي غائب. تفعيل خطة الطوارئ...")
            return self._emergency_programming(prompt)

        try:
            response = self.programmer.invoke(prompt)
            return response.content
        except Exception as e:
            if any(err in str(e).lower() for err in ["429", "rate_limit", "500", "overloaded"]):
                logging.error("❌ عطل في المحرك الرئيسي. التبديل للمحرك الاحتياطي...")
                return self._emergency_programming(prompt)
            return f"خطأ حرج في الإنتاج البرمجي: {str(e)}"

    def _emergency_programming(self, prompt):
        """وظيفة الطوارئ البرمجية: Gemini يتحول لمبرمج عند غياب Llama"""
        if not self.legal_guardian:
            return "فشل سيادي حرج: جميع المحركات خارج الخدمة."
        try:
            emergency_response = self.legal_guardian.invoke([
                SystemMessage(content="أنت الآن Senior AI Developer مخصص لحالات الطوارئ."),
                HumanMessage(content=prompt)
            ])
            return f"⚠️ (توليد طارئ عبر المحرك الاحتياطي)\n\n{emergency_response.content}"
        except Exception as e:
            return f"انهيار كامل لنظام الإنتاج: {e}"

    def get_consensus(self, topic):
        """بروتوكول الإجماع السيادي الكامل (الفيتو المطلق)"""
        logging.info(f"⚖️ بدء بروتوكول الإجماع للمهمة: {topic}")
        
        if not self.legal_guardian:
            raise Exception("VETO_LEGAL: المحرك القانوني غير مفعل. تأكد من تفعيل GEMINI_API_KEY في الرندر وعمل Clear Cache and Deploy.")

        # 1. البحث
        raw_info = self._fetch_reliable_info(topic)
        
        # 2. التدقيق
        verified_context = self.fact_check_service(raw_info)
        
        # 3. البرمجة
        ds_opinion = self.consult_deepseek(topic, verified_context)
        
        # 4. المراجعة والفيتو
        legal_review_prompt = f"""
        بصفتك المحامي الرسمي، راجع المهمة: {topic} 
        والكود المقترح من المبرمج: {ds_opinion}
        بناءً على قوانين السويد لعام 2026:
        - ابدأ بـ 'REJECTED' للمخالفة.
        - ابدأ بـ 'APPROVED' للأمان.
        """
        
        try:
            legal_decision_resp = self.legal_guardian.invoke([
                SystemMessage(content="أنت المستشار القانوني السيادي السويدي."),
                HumanMessage(content=legal_review_prompt)
            ])
            legal_decision = legal_decision_resp.content

            if "REJECTED" in legal_decision.upper():
                logging.error(f"🛑 فيتو قانوني: {legal_decision}")
                raise Exception(f"VETO_LEGAL: {legal_decision}")

            return {
                "Verified_Context": legal_decision,
                "DeepSeek_Logic": ds_opinion,
                "Status": "APPROVED BY SOVEREIGN COUNCIL",
                "Timestamp": self.current_time
            }
        except Exception as e:
            if "VETO_LEGAL" in str(e): raise e
            raise Exception(f"فشل في إتمام المراجعة القانونية: {e}")

# نهاية الكود السيادي المحدث - الإصدار 2.1.1 (2026)
