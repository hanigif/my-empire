import os
import logging
import datetime
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage

# إعداد السجلات لمراقبة الأداء السيادي
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class StrategyCore:
    def __init__(self):
        """تهيئة النخبة: استدعاء المحركات مع معالجة الأخطاء المتقدمة"""
        # تنظيف المفاتيح لضمان عدم وجود مسافات خفية
        self.groq_key = os.getenv("GROQ_API_KEY", "").strip()
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.search_tool = DuckDuckGoSearchRun()
        
        # توقيت السويد الرسمي للعمليات
        self.current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. إعداد المبرمج الرقمي (Llama 3.3)
        self.programmer = self._init_programmer()
            
        # 2. إعداد المحامي والمدقق (Gemini) - الحل النهائي للـ 404
        self.legal_guardian = self._init_legal_guardian()

    def _init_programmer(self):
        try:
            if self.groq_key:
                model = ChatGroq(
                    temperature=0, 
                    model_name="llama-3.3-70b-versatile", 
                    api_key=self.groq_key
                )
                logging.info("✅ المبرمج الرقمي جاهز للعمل.")
                return model
        except Exception as e:
            logging.error(f"❌ عطل في تهيئة المبرمج: {e}")
        return None

    def _init_legal_guardian(self):
        """كسر حصار الـ 404 عبر فرض إصدار v1 المستقر صراحة"""
        if not self.gemini_key:
            logging.error("❌ مفتاح Gemini غائب.")
            return None
        
        # القائمة الذهبية للموديلات المستقرة
        variants = ["gemini-1.5-pro", "gemini-1.5-flash"]
        
        for model_name in variants:
            try:
                # تحديد version="v1" يحل مشكلة الـ 404 في Render/2026
                model = ChatGoogleGenerativeAI(
                    model=model_name, 
                    google_api_key=self.gemini_key,
                    temperature=0,
                    version="v1", 
                    convert_system_message_to_human=True 
                )
                # اختبار القوة (Handshake)
                model.invoke([HumanMessage(content="Sovereign Handshake")])
                logging.info(f"⚖️ المحامي الرقمي اخترق الحصار بنجاح عبر: {model_name}")
                return model
            except Exception as e:
                logging.warning(f"⚠️ المسار {model_name} لا يزال يرفض: {e}")
                continue
        return None

    def find_swedish_leads(self):
        """البحث عن شركات سويدية حقيقية وصياغة رسالة بيع مستهدفة"""
        logging.info("🔍 جاري اصطياد أهداف تجارية في السويد...")
        query = "Swedish companies data privacy breach news 2025 2026"
        
        try:
            raw_results = self.search_tool.run(query)
            lead_prompt = (
                f"بناءً على الأخبار التالية: {raw_results}\n"
                "1. استخرج اسم شركة سويدية حقيقية واحدة تعاني من مشاكل في امتثال البيانات.\n"
                "2. صغ رسالة بيع (Pitch) احترافية جداً موجهة لمدير التقنية لديهم (CTO).\n"
                "3. اعرض 'المدير السيادي' كحل جذري لضمان الخصوصية الكاملة."
            )
            return self.consult_deepseek("صياغة عرض مبيعات سيادي", lead_prompt)
        except Exception as e:
            return f"عطل في البحث عن عملاء: {e}"

    def fact_check_service(self, raw_info):
        """المدقق السيادي: تنقية البيانات من الأخطاء"""
        if not self.legal_guardian:
            return f"⚠️ بيانات غير مدققة: {raw_info}"
        
        verify_prompt = (
            f"بصفتك مدقق حقائق سيادي في السويد لعام 2026، راجع المعلومات التالية:\n{raw_info}\n"
            "المطلوب: التأكد من مطابقتها للقوانين السويدية الحالية."
        )
        try:
            verified = self.legal_guardian.invoke([
                SystemMessage(content="أنت مدقق حقائق سيادي صارم."),
                HumanMessage(content=verify_prompt)
            ])
            return verified.content
        except Exception as e:
            logging.error(f"❌ عطل في التدقيق: {e}")
            return raw_info

    def consult_deepseek(self, task, context):
        """استشارة المبرمج الرقمي (Llama)"""
        prompt = f"المهمة: {task}\nالسياق القانوني والبيئي: {context}\nالنتيجة المطلوبة: كود أو نص سيادي احترافي."
        
        if not self.programmer:
            return self._emergency_response(prompt)
            
        try:
            response = self.programmer.invoke(prompt)
            return response.content
        except Exception as e:
            logging.error(f"❌ عطل في المحرك الرئيسي، تفعيل الطوارئ: {e}")
            return self._emergency_response(prompt)

    def _emergency_response(self, prompt):
        """وظيفة الطوارئ في حال تعطل أحد المحركات"""
        if not self.legal_guardian:
            return "فشل سيادي حرج: جميع المحركات خارج الخدمة."
        try:
            emergency = self.legal_guardian.invoke([
                SystemMessage(content="أنت الآن Senior Developer للطوارئ."),
                HumanMessage(content=prompt)
            ])
            return f"⚠️ (توليد طارئ عبر المحامي)\n\n{emergency.content}"
        except Exception as e:
            return f"انهيار النظام: {e}"

    def get_consensus(self, topic):
        """بروتوكول الإجماع السيادي والفيتو"""
        logging.info(f"⚖️ بدء بروتوكول الإجماع: {topic}")
        
        if not self.legal_guardian:
            raise Exception("VETO_LEGAL: المحامي معطل.")

        raw_info = self.search_tool.run(f"{topic} Sweden 2026")
        verified_context = self.fact_check_service(raw_info)
        logic_output = self.consult_deepseek(topic, verified_context)
        
        # المراجعة النهائية
        review = self.legal_guardian.invoke([
            SystemMessage(content="أنت المستشار القانوني السيادي. أجب بـ APPROVED أو REJECTED مع السبب."),
            HumanMessage(content=f"راجع المخرج التالي: {logic_output}")
        ]).content

        if "REJECTED" in review.upper():
            raise Exception(f"VETO_LEGAL: تم رفض العملية. السبب: {review}")

        return {
            "Status": "APPROVED",
            "Result": logic_output,
            "Legal_Review": review,
            "Timestamp": self.current_time
        }
