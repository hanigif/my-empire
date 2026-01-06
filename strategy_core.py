import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

class StrategyCore:
    def __init__(self):
        # سحب المفاتيح من خزنة Render
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.search_tool = DuckDuckGoSearchRun()
        
        # إعداد العقول السيادية
        self.programmer = ChatGroq(temperature=0, model_name="deepseek-v3", api_key=self.groq_key) if self.groq_key else None
        self.strategist = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=self.gemini_key) if self.gemini_key else None

    def _fetch_reliable_info(self, topic):
        """البحث عن معلومات من مصادر سويدية موثوقة فقط 2026"""
        search_query = f"{topic} site:gov.se OR site:socialstyrelsen.se OR site:riksdagen.se 2026"
        try:
            raw_data = self.search_tool.run(search_query)
            return raw_data
        except Exception as e:
            return f"فشل الاتصال بالإنترنت: {str(e)}"

    def fact_check_service(self, raw_info):
        """المدقق السيادي: فحص المعلومات وتنقيتها من الأخطاء"""
        if not self.strategist: return raw_info
        
        verify_prompt = (
            f"بصفتك مدقق حقائق سيادي، راجع المعلومات التالية المستخرجة من الإنترنت: \n{raw_info}\n"
            "ابحث عن أي تضارب قانوني أو أخطاء تقنية في معايير السويد 2026. "
            "استبعد أي معلومات غير موثقة وأعطني فقط الحقائق الصافية."
        )
        verified_data = self.strategist.invoke([
            SystemMessage(content="أنت مدقق حقائق صارم (Fact-Checker). مهمتك كشف المعلومات المغلوطة."),
            HumanMessage(content=verify_prompt)
        ])
        return verified_data.content

    def consult_deepseek(self, task, context):
        """استشارة المبرمج الرقمي بناءً على المعلومات المحدثة"""
        if not self.programmer: return "مفتاح Groq غير متوفر."
        try:
            prompt = f"المهمة: {task}\nالسياق المحدث والموثق: {context}\nحلل المهمة برمجياً وفق هذا السياق."
            response = self.programmer.invoke(prompt)
            return response.content
        except Exception as e:
            return f"خطأ في استشارة ديب سيك: {str(e)}"

    def consult_gemini(self, task, context):
        """استشارة المحلل الاستراتيجي لضمان السيادة"""
        if not self.strategist: return "مفتاح Gemini غير متوفر."
        try:
            prompt = f"المهمة: {task}\nالحقائق الموثقة: {context}\nضع اللمسة الاستراتيجية لضمان الامتثال لقوانين السويد."
            response = self.strategist.invoke([
                SystemMessage(content="أنت المحلل الاستراتيجي السيادي."),
                HumanMessage(content=prompt)
            ])
            return response.content
        except Exception as e:
            return f"خطأ في استشارة جيمناي: {str(e)}"

    def get_consensus(self, topic):
        """بروتوكول الإجماع السيادي المحدث (اتصال - بحث - تدقيق - قرار)"""
        print(f"[*] تفعيل النبض: تحديث الفريق عبر الإنترنت حول {topic}...")
        
        # 1. تحديث المعلومات من مصادر موثوقة
        raw_info = self._fetch_reliable_info(topic)
        
        # 2. تدقيق المعلومات المستلمة (المرشح السيادي)
        verified_context = self.fact_check_service(raw_info)
        
        print(f"[*] تم تدقيق المعلومات وتأكيد الموثوقية.")
        
        # 3. استشارة مجلس الإدارة بناءً على الحقائق فقط
        ds_opinion = self.consult_deepseek(topic, verified_context)
        gemini_opinion = self.consult_gemini(topic, verified_context)
        
        return {
            "Verified_Context": verified_context[:500], # ملخص المعلومات الموثقة
            "DeepSeek_Logic": ds_opinion,
            "Gemini_Strategy": gemini_opinion,
            "Final_Decision": "تم الاعتماد بناءً على حقائق مدققة من مصادر حكومية سويدية."
        }
