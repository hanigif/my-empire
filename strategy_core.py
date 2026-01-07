import os, logging, time, datetime
import pandas as pd
from google import genai
from google.genai import errors
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class StrategyCore:
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY", "").strip()
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.search_tool = DuckDuckGoSearchRun()
        
        self.programmer = self._init_groq()
        self.legal_guardian = self._init_gemini_2026()

    def _init_groq(self):
        try:
            return ChatGroq(model_name="llama-3.3-70b-versatile", api_key=self.groq_key)
        except: return None

    def _init_gemini_2026(self):
        """تهيئة مع نظام حماية من الزحام"""
        if not self.gemini_key: return None
        try:
            client = genai.Client(api_key=self.gemini_key)
            self.gen_client = client
            # اختبار صامت مع معالجة خطأ الزحام
            self.safe_generate("ping")
            logging.info("⚖️ المحامي السيادي جاهز (مع نظام الحماية من الزحام)")
            return True
        except Exception as e:
            logging.warning(f"⚠️ وضع Gemini الحالي: {e}")
            return None

    def safe_generate(self, prompt, retries=3):
        """وظيفة ذكية للتعامل مع خطأ 429 (Resource Exhausted)"""
        for i in range(retries):
            try:
                # محاولة الاتصال بـ 2.0 فلاش
                return self.gen_client.models.generate_content(
                    model="gemini-2.0-flash", 
                    contents=prompt
                ).text
            except Exception as e:
                if "429" in str(e):
                    wait = (i + 1) * 5
                    logging.info(f"⏳ زحام على الشبكة، سأنتظر {wait} ثانية...")
                    time.sleep(wait)
                else:
                    break
        return None

    def find_swedish_leads(self):
        """صيد الشركات السويدية باستخدام المحرك المتاح"""
        logging.info("🔍 جاري تنفيذ المسح السيادي...")
        try:
            query = "Swedish companies data privacy violations news 2026"
            results = self.search_tool.run(query)
            
            prompt = f"النتائج: {results}\nاستخرج شركة سويدية حقيقية وصغ رسالة مبيعات لمنتج 'المدير السيادي'."
            
            # محاولة استخدام Gemini أولاً للتدقيق القانوني
            response = self.safe_generate(prompt)
            
            # إذا فشل Gemini بسبب الزحام، استخدم Llama فوراً (الخطة ب)
            if not response and self.programmer:
                logging.info("🔄 تحويل المهمة للمبرمج (Llama) لتجاوز زحام جوجل.")
                response = self.programmer.invoke(prompt).content
                
            return response if response else "فشل في الحصول على بيانات حالياً."
        except Exception as e:
            return f"عطل فني: {e}"

    def fact_check_service(self, text):
        """التدقيق عبر Gemini أو Llama حسب المتاح"""
        verified = self.safe_generate(f"Verify: {text}")
        if not verified and self.programmer:
            return self.programmer.invoke(f"Fact check this: {text}").content
        return verified if verified else text
