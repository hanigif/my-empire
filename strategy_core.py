import os
import logging
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
        
        # إعداد المبرمج (Groq)
        try:
            self.programmer = ChatGroq(
                temperature=0, 
                model_name="llama-3.3-70b-versatile", 
                api_key=self.groq_key
            ) if self.groq_key else None
        except Exception as e:
            logging.error(f"Error initializing Groq: {e}")
            self.programmer = None
            
        # إعداد المحامي (Gemini) مع حل مشكلة الـ 404
        try:
            # تم التغيير إلى gemini-1.5-flash لضمان التوفر المستمر وتجنب خطأ 404
            self.legal_guardian = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash", 
                google_api_key=self.gemini_key
            ) if self.gemini_key else None
        except Exception as e:
            logging.error(f"Error initializing Gemini: {e}")
            self.legal_guardian = None

    def _fetch_reliable_info(self, topic):
        """البحث عن معلومات من مصادر سويدية موثوقة فقط 2026"""
        search_query = f"{topic} site:gov.se OR site:socialstyrelsen.se OR site:riksdagen.se 2026"
        try:
            return self.search_tool.run(search_query)
        except Exception as e:
            return f"فشل الاتصال بالإنترنت: {str(e)}"

    def fact_check_service(self, raw_info):
        """المدقق السيادي: فحص المعلومات وتنقيتها"""
        if not self.legal_guardian: 
            return "تحذير: المحرك القانوني غير متصل."
        
        verify_prompt = (
            f"بصفتك مدقق حقائق سيادي، راجع المعلومات التالية: \n{raw_info}\n"
            "استخرج فقط الحقائق المتوافقة مع معايير السويد 2026."
        )
        try:
            verified_data = self.legal_guardian.invoke([
                SystemMessage(content="أنت مدقق حقائق صارم."),
                HumanMessage(content=verify_prompt)
            ])
            return verified_data.content
        except Exception as e:
            logging.error(f"Fact check error: {e}")
            return raw_info

    def consult_deepseek(self, task, context):
        """استشارة المبرمج مع نظام التبديل الآلي"""
        prompt = f"المهمة: {task}\nالسياق: {context}\nاكتب الكود البرمجي."
        
        if not self.programmer:
            if self.legal_guardian:
                return self._emergency_programming(prompt)
            return "خطأ: المحركات غير متوفرة."

        try:
            response = self.programmer.invoke(prompt)
            return response.content
        except Exception as e:
            if ("429" in str(e) or "rate_limit" in str(e).lower()) and self.legal_guardian:
                return self._emergency_programming(prompt)
            return f"خطأ في الإنتاج البرمجي: {str(e)}"

    def _emergency_programming(self, prompt):
        """وظيفة الطوارئ للتبديل إلى Gemini"""
        try:
            emergency_response = self.legal_guardian.invoke([
                SystemMessage(content="أنت الآن Senior AI Developer."),
                HumanMessage(content=prompt)
            ])
            return f"(تم الإنتاج عبر المحرك الاحتياطي)\n\n{emergency_response.content}"
        except Exception as e:
            return f"فشل محرك الطوارئ أيضاً: {e}"

    def get_consensus(self, topic):
        """بروتوكول الإجماع السيادي الكامل"""
        
        if not self.legal_guardian:
            raise Exception("VETO_LEGAL: المحرك القانوني غير مفعل. تأكد من GEMINI_API_KEY.")

        # 1. بحث وتدقيق
        raw_info = self._fetch_reliable_info(topic)
        verified_context = self.fact_check_service(raw_info)
        
        # 2. برمجة
        ds_opinion = self.consult_deepseek(topic, verified_context)
        
        # 3.
