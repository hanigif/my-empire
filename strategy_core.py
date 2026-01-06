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
            
        # 2. إعداد المحامي والمدقق (Gemini)
        self.legal_guardian = self._initialize_gemini_with_failover()

    def _initialize_gemini_with_failover(self):
        """تجاوز خطأ 404 والربط بالمحرك المستقر"""
        if not self.gemini_key:
            logging.error("❌ مفتاح Gemini غائب.")
            return None
        
        clean_key = self.gemini_key.strip()
        variants = [
            "models/gemini-1.5-pro-latest", 
            "models/gemini-1.5-flash-latest",
            "gemini-1.5-pro",
            "gemini-pro"
        ]
        
        for model_path in variants:
            try:
                model = ChatGoogleGenerativeAI(
                    model=model_path, 
                    google_api_key=clean_key,
                    temperature=0,
                    convert_system_message_to_human=True 
                )
                model.invoke([HumanMessage(content="Sovereign Handshake")])
                logging.info(f"⚖️ تم الاتصال عبر: {model_path}")
                return model
            except Exception as e:
                logging.warning(f"⚠️ المسار {model_path} فشل: {e}")
                continue
        return None

    def _fetch_reliable_info(self, topic):
        """البحث عن معلومات من مصادر سويدية موثوقة لعام 2026"""
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
        """المدقق السيادي: تنقية البيانات من الأخطاء"""
        if not self.legal_guardian:
            return f"⚠️ بيانات غير مدققة قانونياً: {raw_info}"
        
        verify_prompt = (
            f"التوقيت الحالي: {self.current_time}\n"
            f"بصفتك مدقق حقائق سيادي في السويد، حلل ما يلي:\n{raw_info}\n"
            "المطلوب: استخراج القوانين السويدية لعام 2026 فقط."
        )
        try:
            verified_data = self.legal_guardian.invoke([
                SystemMessage(content="أنت مدقق حقائق صارم في السويد."),
                HumanMessage(content=verify_prompt)
            ])
            return verified_data.content
        except Exception as e:
            logging.error(f"❌ عطل في التدقيق: {e}")
            return f"بيانات خام: {raw_info}"

    def consult_deepseek(self, task, context):
        """استشارة المبرمج الرقمي (Llama)"""
        prompt = (f"المهمة: {task}\nالسياق القانوني: {context}\nاكتب الكود بأمان سويدي.")
        if not self.programmer:
            return self._emergency_programming(prompt)
        try:
            response = self.programmer.invoke(prompt)
            return response.content
        except Exception as e:
            logging.error(f"❌ عطل في المحرك الرئيسي، تفعيل الطوارئ: {e}")
            return self._emergency_programming(prompt)

    def _emergency_programming(self, prompt):
        """وظيفة الطوارئ عبر Gemini"""
        if not self.legal_guardian:
            return "فشل سيادي حرج: جميع المحركات خارج الخدمة."
        try:
            emergency_response = self.legal_guardian.invoke([
                SystemMessage(content="أنت الآن Senior Developer للطوارئ."),
                HumanMessage(content=prompt)
            ])
            return f"⚠️ (توليد طارئ)\n\n{emergency_response.content}"
        except Exception as e:
            return f"انهيار النظام: {e}"

    def get_consensus(self, topic):
        """بروتوكول الإجماع السيادي والفيتو المطلق"""
        logging.info(f"⚖️ بدء بروتوكول الإجماع: {topic}")
        if not self.legal_guardian:
            raise Exception("VETO_LEGAL: المحرك القانوني معطل.")

        raw_info = self._fetch_reliable_info(topic)
        verified_context = self.fact_check_service(raw_info)
        ds_opinion = self.consult_deepseek(topic, verified_context)
        
        legal_review_prompt = f"راجع المهمة: {topic}\nوالكود: {ds_opinion}\nابدأ بـ APPROVED أو REJECTED بناءً على قوانين 2026."
        
        try:
            legal_decision = self.legal_guardian.invoke([
                SystemMessage(content="أنت المستشار القانوني السيادي."),
                HumanMessage(content=legal_review_prompt)
            ]).content

            if "REJECTED" in legal_decision.upper():
                raise Exception(f"VETO_LEGAL: {legal_decision}")

            return {
                "Verified_Context": legal_decision,
                "DeepSeek_Logic": ds_opinion,
                "Status": "APPROVED BY SOVEREIGN COUNCIL",
                "Timestamp": self.current_time
            }
        except Exception as e:
            if "VETO_LEGAL" in str(e): raise e
            raise Exception(f"فشل المراجعة: {e}")
