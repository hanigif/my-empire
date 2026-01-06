import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

class StrategyCore:
    def __init__(self):
        # سحب المفاتيح من الخزنة الرقمية
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.search_tool = DuckDuckGoSearchRun()
        
        # 1. المبرمج الرقمي (Llama 3.3 عبر Groq) - للأكواد المعقدة
        self.programmer = ChatGroq(
            temperature=0, 
            model_name="llama-3.3-70b-versatile", 
            api_key=self.groq_key
        ) if self.groq_key else None
        
        # 2. المحامي والمحلل الاستراتيجي (Gemini 1.5 Pro) - للتدقيق والقانون السويدي
        self.legal_guardian = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro", 
            google_api_key=self.gemini_key
        ) if self.gemini_key else None

    def _fetch_live_laws(self, topic):
        """البحث الحي عن القوانين السويدية 2026 (الهدف رقم 3)"""
        search_query = f"{topic} Swedish healthcare data law 2026 site:socialstyrelsen.se OR site:gov.se"
        try:
            return self.search_tool.run(search_query)
        except Exception as e:
            return f"فشل البحث المباشر، الاعتماد على المعايير المحفوظة. الخطأ: {e}"

    def get_consensus(self, task):
        """بروتوكول الإجماع السيادي: بحث -> برمجة -> تدقيق قانوني -> قرار"""
        
        # المرحلة 1: جمع البيانات القانونية الحية
        raw_context = self._fetch_live_laws(task)

        # المرحلة 2: توليد الحل التقني (مع نظام التبديل الآلي في حال تعطل Groq)
        initial_logic = ""
        try:
            # المحاولة عبر المبرمج الأساسي (Groq)
            prompt = f"المهمة: {task}\nالسياق القانوني المكتشف: {raw_context}\nصمم الحل البرمجي المتوافق."
            initial_logic = self.programmer.invoke(prompt).content
        except Exception as e:
            # التبديل الآلي للمحرك الاحتياطي (Gemini) في حال حدوث Rate Limit (429)
            if "429" in str(e) or "rate_limit" in str(e).lower():
                emergency_prompt = f"إشعار طوارئ: المحرك الأول متوقف. قم بدور المبرمج والمحلل للمهمة: {task}\nالسياق: {raw_context}"
                initial_logic = self.legal_guardian.invoke(emergency_prompt).content
            else:
                initial_logic = f"خطأ تقني في التوليد: {e}"

        # المرحلة 3: مراجعة المحامي السويدي (VETO POWER) - إلزامية
        legal_review_prompt = f"""
        بصفتك المحامي الرسمي وخبير الامتثال السويدي لعام 2026:
        المهمة المطلوبة: {task}
        الحل التقني المقترح: {initial_logic}
        
        المطلوب منك:
        1. إذا كان الحل يخالف أي قانون سويدي أو معايير Socialstyrelsen، ابدأ ردك بكلمة 'REJECTED' فوراً مع ذكر السبب.
        2. إذا كان متوافقاً تماماً، ابدأ بكلمة 'APPROVED' مع توضيح المند الرقابي الذي يدعم الموافقة.
        """
        
        try:
            legal_decision = self.legal_guardian.invoke([
                SystemMessage(content="أنت المحامي السيادي والمستشار القانوني الأول للشركة في السويد."),
                HumanMessage(content=legal_review_prompt)
            ]).content
        except Exception as e:
            legal_decision = f"REJECTED: تعذر الحصول على موافقة المحامي بسبب عطل في محرك التدقيق: {e}"

        # المرحلة 4: تفعيل نظام الفيتو (الذي طلبه القائد)
        if "REJECTED" in legal_decision.upper():
            # إطلاق الاستثناء الذي سيلتقطه app.py لإرسال التنبيه لتلغرام
            raise Exception(f"VETO_LEGAL: المحامي رفض الإجراء. التفاصيل: {legal_decision}")

        # المرحلة 5: النتيجة النهائية في حال الموافقة
        return {
            "Verified_Context": legal_decision,
            "DeepSeek_Logic": initial_logic,
            "Status": "APPROVED"
        }
