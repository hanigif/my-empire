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
            
        # 2. إعداد المحامي والمدقق (Gemini) - تم حل مشكلة 404 هنا
        try:
            if self.gemini_key:
                # نستخدم gemini-1.5-flash كاسم أساسي لأنه الأكثر استقراراً في 2026
                self.legal_guardian = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash", 
                    google_api_key=self.gemini_key
                )
            else:
                self.legal_guardian = None
        except Exception as e:
            logging.error(f"❌ فشل تهيئة Gemini: {e}")
            self.legal_guardian = None

    def _fetch_reliable_info(self, topic):
        """البحث عن معلومات من مصادر سويدية موثوقة فقط 2026 (الهدف رقم 3)"""
        # نركز البحث على الهيئات الحكومية السويدية لضمان السيادة
        search_query = f"{topic} site:gov.se OR site:socialstyrelsen.se OR site:riksdagen.se 2026"
        try:
            return self.search_tool.run(search_query)
        except Exception as e:
            return f"فشل الاتصال بالإنترنت لجلب البيانات الحية: {str(e)}"

    def fact_check_service(self, raw_info):
        """المدقق السيادي: فحص المعلومات وتنقيتها من الأخطاء (الهدف رقم 6)"""
        if not self.legal_guardian:
            return "تحذير: المحرك القانوني غير متصل. البيانات غير مدققة."
        
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
        
        # منع خطأ NoneType قبل الاستدعاء
        if not self.programmer:
            logging.warning("[!] المبرمج الأساسي غائب. تفعيل خطة الطوارئ...")
            return self._emergency_programming(prompt)

        try:
            # المحاولة الأولى عبر Groq (الأداء الأعلى)
            response = self.programmer.invoke(prompt)
            return response.content
        except Exception as e:
            # التبديل الآلي في حال تجاوز حدود الطلبات أو أي عطل
            if "429" in str(e) or "rate_limit" in str(e).lower() or "500" in str(e):
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
        
        # 1. التأكد من أن "المحامي" جاهز للعمل (لا يمكن المضي قدماً بدونه)
        if not self.legal_guardian:
            raise Exception("VETO_LEGAL: المحرك القانوني غير مفعل. تأكد من GEMINI_API_KEY.")

        # 2. تحديث المعلومات من المصادر الرسمية السويدية
        raw_info = self._fetch_reliable_info(topic)
        
        # 3. تمرير المعلومات لمدقق الحقائق
        verified_context = self.fact_check_service(raw_info)
        
        # 4. طلب الكود من المبرمج بناءً على السياق المدقق
        ds_opinion = self.consult_deepseek(topic, verified_context)
        
        # 5. مراجعة المحامي السويدي النهائية (سلطة الفيتو المطلقة)
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
                SystemMessage(content="أنت المستشار القانوني السيادي. وظيفتك حماية الشركة من أي مخالفة قانونية سويدية."),
                HumanMessage(content=legal_review_prompt)
            ])
            legal_decision = legal_decision_resp.content

            # 6. تفعيل نظام الفيتو الذي طلبه القائد
            if "REJECTED" in legal_decision.upper():
                raise Exception(f"VETO_LEGAL: المحامي رفض الإجراء. التفاصيل: {legal_decision}")

            # 7. النجاح: إعادة التقرير المتكامل
            return {
                "Verified_Context": legal_decision,
                "DeepSeek_Logic": ds_opinion,
                "Status": "APPROVED BY SOVEREIGN COUNCIL"
            }
        except Exception as e:
            if "VETO_LEGAL" in str(e): raise e
            raise Exception(f"عطل في محرك المراجعة القانونية: {e}")
