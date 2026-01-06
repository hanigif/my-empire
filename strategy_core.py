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
        # سحب المفاتيح من الخزنة الرقمية في Render
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
            
        # 2. إعداد المحامي والمدقق (Gemini) - حل جذري لمشكلة الـ 404
        self.legal_guardian = self._initialize_gemini()

    def _initialize_gemini(self):
        """محاولة تهيئة الموديل بأكثر من صيغة لضمان تخطي خطأ 404"""
        if not self.gemini_key:
            return None
        
        # قائمة بالأسماء الممكنة للموديل حسب تحديثات Google 2026
        model_variants = ["gemini-1.5-flash", "models/gemini-1.5-flash", "gemini-pro"]
        
        for model_name in model_variants:
            try:
                model = ChatGoogleGenerativeAI(
                    model=model_name, 
                    google_api_key=self.gemini_key,
                    temperature=0
                )
                # اختبار الاتصال فوراً للتأكد من أن الموديل موجود (404 check)
                model.invoke([HumanMessage(content="test")])
                logging.info(f"✅ تم تفعيل المحامي الرقمي بنجاح باستخدام: {model_name}")
                return model
            except Exception as e:
                logging.warning(f"⚠️ فشل الاتصال بـ {model_name}: {e}")
                continue
        
        logging.error("❌ فشل تشغيل جميع محركات Gemini. تأكد من إعدادات المنطقة والمفتاح.")
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
            "استخرج فقط الحقائق الصافية والمتوافقة مع معايير السويد 2026. استبعد أي معلومة غير موثقة."
        )
        try:
            verified_data = self.legal_guardian.invoke([
                SystemMessage(content="أنت مدقق حقائق صارم. مهمتك تصفية المعلومات المغلوطة من الإنترنت."),
                HumanMessage(content=verify_prompt)
            ])
            return verified_data.content
        except Exception as e:
            logging.error(f"Fact check error: {e}")
            return f"بيانات خام (فشل التدقيق): {raw_info}"

    def consult_deepseek(self, task, context):
        """استشارة المبرمج الرقمي مع نظام التبديل الآلي (Failover) (الهدف رقم 9)"""
        prompt = f"المهمة: {task}\nالسياق المحدث والموثق قانونياً: {context}\nاكتب الكود البرمجي اللازم بدقة عالية."
        
        if not self.programmer:
            logging.warning("[!] المبرمج الأساسي غائب. تفعيل خطة الطوارئ...")
            return self._emergency_programming(prompt)

        try:
            response = self.programmer.invoke(prompt)
            return response.content
        except Exception as e:
            if any(err in str(e).lower() for err in ["429", "rate_limit", "500", "overloaded"]):
                logging.error("[!] عطل في Groq. تفعيل نظام التبديل الآلي لـ Gemini...")
                return self._emergency_programming(prompt)
            return f"خطأ حرج في الإنتاج البرمجي: {str(e)}"

    def _emergency_programming(self, prompt):
        """وظيفة الطوارئ البرمجية لضمان استمرارية العمل"""
        if not self.legal_guardian:
            return "فشل حرج: جميع المحركات (المبرمج والمحامي) خارج الخدمة."
        try:
            emergency_response = self.legal_guardian.invoke([
                SystemMessage(content="أنت الآن Senior AI Developer. قم بإكمال المهمة البرمجية نظراً لتعطل المحرك الأول."),
                HumanMessage(content=prompt)
            ])
            return f"⚠️ (تم الإنتاج عبر محرك الطوارئ الاحتياطي)\n\n{emergency_response.content}"
        except Exception as e:
            return f"فشل نظام الطوارئ أيضاً: {e}"

    def get_consensus(self, topic):
        """بروتوكول الإجماع السيادي الكامل (بحث - تدقيق - برمجة - مراجعة قانونية - فيتو)"""
        
        if not self.legal_guardian:
            raise Exception("VETO_LEGAL: المحرك القانوني غير مفعل. تأكد من GEMINI_API_KEY.")

        # 1. تحديث المعلومات من المصادر الرسمية السويدية
        raw_info = self._fetch_reliable_info(topic)
        
        # 2. تمرير المعلومات لمدقق الحقائق
        verified_context = self.fact_check_service(raw_info)
        
        # 3. طلب الكود من المبرمج بناءً على السياق المدقق
        ds_opinion = self.consult_deepseek(topic, verified_context)
        
        # 4. مراجعة المحامي السويدي النهائية (سلطة الفيتو المطلقة)
        legal_review_prompt = f"""
        بصفتك المحامي الرسمي للشركة وخبير القانون السويدي 2026:
        راجع المهمة التالية: {topic}
        والحل التقني المقترح: {ds_opinion}
        
        هل يوافق هذا معايير Socialstyrelsen و GDPR وقوانين خصوصية البيانات الصحية في السويد؟
        - إذا وجدت أي ثغرة أو مخالفة، ابدأ ردك بكلمة 'REJECTED' واشرح السبب.
        - إذا كان آمناً، ابدأ بكلمة 'APPROVED'.
        """
        
        try:
            legal_decision_resp = self.legal_guardian.invoke([
                SystemMessage(content="أنت المستشار القانوني السيادي. وظيفتك حماية الشركة من المخالفات القانونية."),
                HumanMessage(content=legal_review_prompt)
            ])
            legal_decision = legal_decision_resp.content

            if "REJECTED" in legal_decision.upper():
                raise Exception(f"VETO_LEGAL: المحامي رفض الإجراء. التفاصيل: {legal_decision}")

            return {
                "Verified_Context": legal_decision,
                "DeepSeek_Logic": ds_opinion,
                "Status": "APPROVED BY SOVEREIGN COUNCIL"
            }
        except Exception as e:
            if "VETO_LEGAL" in str(e): raise e
            raise Exception(f"عطل في محرك المراجعة القانونية: {e}")
