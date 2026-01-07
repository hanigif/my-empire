import os, logging, datetime
import pandas as pd
import plotly.express as px
from google import genai 
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class StrategyCore:
    def __init__(self):
        # 1. تنظيف المفاتيح
        self.groq_key = os.getenv("GROQ_API_KEY", "").strip()
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.search_tool = DuckDuckGoSearchRun()
        
        # 2. تهيئة المحركات (المبرمج والمحامي)
        self.programmer = self._init_groq()
        self.legal_guardian = self._init_gemini_2026()
        
        # 3. قاعدة بيانات الشركات (Pandas)
        self.leads_df = pd.DataFrame(columns=['Company', 'Status', 'Risk_Level', 'Pitch'])

    def _init_groq(self):
        if self.groq_key:
            return ChatGroq(model_name="llama-3.3-70b-versatile", api_key=self.groq_key)
        return None

    def _init_gemini_2026(self):
        """تجاوز الـ 404 نهائياً عبر SDK 2026 الجديد"""
        if not self.gemini_key: return None
        try:
            client = genai.Client(api_key=self.gemini_key)
            # تجربة الاتصال بموديل مستقر
            client.models.generate_content(model="gemini-2.0-flash", contents="ping")
            self.gen_client = client
            logging.info("⚖️ المحامي السيادي متصل بنجاح.")
            return True
        except Exception as e:
            logging.error(f"⚠️ فشل Gemini: {e}")
            return None

    def find_swedish_leads(self):
        """البحث، التحليل باستخدام Pandas، وصياغة العرض"""
        logging.info("🔍 جاري تنفيذ المسح السيادي للسوق السويدي...")
        try:
            # البحث عن أخبار الامتثال والخصوصية في السويد
            query = "Swedish companies data breach GDPR 2025 2026"
            raw_results = self.search_tool.run(query)
            
            # نطلب من المبرمج استخراج البيانات بشكل منظم
            extraction_prompt = f"من النتائج التالية: {raw_results}. استخرج أسماء 3 شركات سويدية حقيقية واذكر مستوى خطر الخصوصية (High/Medium)."
            
            raw_list = self.programmer.invoke(extraction_prompt).content
            
            # هنا نقوم بدمج الرسالة التسويقية لمنتج "المدير السيادي"
            pitch_prompt = f"صغ رسالة بيع احترافية لشركة سويدية تعاني من مشاكل خصوصية: {raw_list}"
            final_pitch = self.programmer.invoke(pitch_prompt).content
            
            return final_pitch
        except Exception as e:
            return f"عطل في معالجة البيانات: {e}"

    def generate_risk_chart(self):
        """إنتاج رسم بياني لمستويات الخطر (اختياري للتقارير)"""
        # مثال لاستخدام Plotly
        data = {'Category': ['Privacy Risk', 'Compliance', 'Security'], 'Score': [85, 70, 90]}
        df = pd.DataFrame(data)
        fig = px.bar(df, x='Category', y='Score', title="Sovereign Risk Analysis")
        return fig.to_json()
