import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

class StrategyCore:
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.search_tool = DuckDuckGoSearchRun()
        
        # المبرمج الأساسي
        self.programmer = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile", api_key=self.groq_key) if self.groq_key else None
        # المحامي والمحلل الاستراتيجي (Gemini Pro)
        self.legal_guardian = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=self.gemini_key) if self.gemini_key else None

    def _fetch_reliable_info(self, topic):
        search_query = f"{topic} Sweden healthcare law 2026 site:socialstyrelsen.se OR site:gov.se"
        try:
            return self.search_tool.run(search_query)
        except:
            return "تعذر جلب بيانات حية، الاعتماد على القاعدة المعرفية 2026."

    def get_consensus(self, topic):
        # 1. البحث والتدقيق
        raw_info = self._fetch_reliable_info(topic)
        
        # 2. استشارة المبرمج (المسودة التقنية)
        prompt = f"المهمة: {topic}\nالسياق القانوني: {raw_info}\nاكتب الحل التقني المبدئي."
        try:
            initial_logic = self.programmer.invoke(prompt).content
        except:
            initial_logic = self.legal_guardian.invoke(f"Developer Mode: {prompt}").content

        # 3. مراجعة المحامي الرقمي (VETO POWER)
        legal_prompt = f"""
        بصفتك المحامي الرسمي للشركة وخبير القانون السويدي 2026:
        راجع هذا الإجراء: {topic} 
        وهذا الكود: {initial_logic}
        هل يوافق معايير Socialstyrelsen و GDPR السويدية؟
        - إذا كان مخالفاً، ابدأ بكلمة 'REJECTED' واذكر السبب بدقة.
        - إذا كان موافقاً، ابدأ بكلمة 'APPROVED' مع شرح بسيط للمزايا القانونية.
        """
        legal_opinion = self.legal_guardian.invoke([SystemMessage(content="أنت المحامي السيادي."), HumanMessage(content=legal_prompt)]).content

        # نظام الفيتو
        if "REJECTED" in legal_opinion.upper():
            raise Exception(f"VETO_LEGAL: المحامي رفض الإجراء. السبب: {legal_opinion}")

        return {
            "Verified_Context": legal_opinion, # رأي المحامي
            "DeepSeek_Logic": initial_logic,   # الكود التقني
            "Status": "APPROVED"
        }
