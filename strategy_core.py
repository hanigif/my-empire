import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

class StrategyCore:
    def __init__(self):
        # سحب المفاتيح من الخزنة
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.search_tool = DuckDuckGoSearchRun()
        
        # إعداد المحركات مع فحص التوفر
        self.programmer = ChatGroq(
            temperature=0, 
            model_name="llama-3.3-70b-versatile", 
            api_key=self.groq_key
        ) if self.groq_key else None
        
        self.legal_guardian = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro", 
            google_api_key=self.gemini_key
        ) if self.gemini_key else None

    def _fetch_reliable_info(self, topic):
        """البحث عن معلومات من مصادر سويدية موثوقة فقط 2026 (الهدف رقم 3)"""
        search_query = f"{topic} site:gov.se OR site:socialstyrelsen.se OR site:riksdagen.se 2026"
        try:
            return self.search_tool.run(search_query)
        except Exception as e:
            return f"فشل الاتصال بالإنترنت: {str(e)}"

    def fact_check_service(self, raw_info):
        """المدقق السيادي: فحص المعلومات وتنقيتها من الأخطاء عبر Gemini Pro"""
        if not self.legal_guardian: return raw_info
        verify_prompt = (
            f"بصفتك مدقق حقائق سيادي، راجع المعلومات التالية: \n{raw_info}\n"
            "استخرج فقط الحقائق المتوافقة مع معايير السويد 2026 واستبعد أي معلومة غير موثقة."
        )
        try:
            verified_data = self.legal_guardian.invoke([
                SystemMessage(content="أنت مدقق حقائق صارم. مهمتك تصفية المعلومات المغلوطة."),
                HumanMessage(content=verify_prompt)
            ])
            return verified_data.content
        except:
            return raw_info

    def consult_deepseek(self, task, context):
        """استشارة المبرمج مع نظام التبديل الآلي (Failover) عند حدوث Rate Limit"""
        prompt = f"المهمة: {task}\nالسياق المحدث: {context}\nاكتب الكود البرمجي اللازم بدقة."
        try:
            # المحاولة الأولى عبر Groq
            response = self.programmer.invoke(prompt)
            return response.content
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                # التبديل للطوارئ
                emergency_response = self.legal_guardian.invoke([
                    SystemMessage(content="أنت الآن Senior AI Developer. قم بإكمال المهمة البرمجية لأن المحرك الأول متوقف."),
                    HumanMessage(content=prompt)
                ])
                return f"(تم الإنتاج عبر المحرك الاحتياطي)\n\n{emergency_response.content}"
            return f"خطأ في الإنتاج: {str(e)}"

    def get_consensus(self, topic):
        """بروتوكول الإجماع السيادي الكامل (بحث - تدقيق - برمجة - فيتو قانوني)"""
        # 1. تحديث المعلومات من الإنترنت
        raw_info = self._fetch_reliable_info(topic)
        
        # 2. تدقيق الحقائق
        verified_context = self.fact_check_service(raw_info)
        
        # 3. توليد الكود التقني
        ds_opinion = self.consult_deepseek(topic, verified_context)
        
        # 4. مراجعة المحامي السويدي (VETO POWER)
        legal_review_prompt = f"""
        بصفتك المحامي الرسمي، راجع المهمة: {topic} والكود: {ds_opinion}
        هل يوافق معايير Socialstyrelsen و GDPR السويدية لعام 2026؟
        - ابدأ بـ 'REJECTED' إذا كان هناك أي خطر قانوني.
        - ابدأ بـ 'APPROVED' إذا كان آمناً.
        """
        legal_decision = self.legal_guardian.invoke([
            SystemMessage(content="أنت المحامي السيادي والمستشار القانوني في السويد."),
            HumanMessage(content=legal_review_prompt)
        ]).content

        # تفعيل الفيتو
        if "REJECTED" in legal_decision.upper():
            raise Exception(f"VETO_LEGAL: {legal_decision}")

        return {
            "Verified_Context": legal_decision,
            "DeepSeek_Logic": ds_opinion,
            "Status": "APPROVED"
        }
