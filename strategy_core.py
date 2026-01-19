import os
import json
import datetime
import pytz
import threading
import time
import requests
import random
import logging
from github import Github 
from google import genai 
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage
from flask import Flask

# --- 1. الإعدادات الأساسية ---
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

GK_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") 
REPO_NAME = "hanigif/Sovereign-Assets"
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

EMPIRE_START_TIME = datetime.datetime.now(SWEDEN_TZ)
AUTO_PRODUCTION_COUNT = 0 

# --- 2. المحركات الذكية ---
llm_backup = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)

class Gemini2026Manager:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash"
    
    def invoke(self, messages):
        prompt = messages[-1].content if isinstance(messages, list) else str(messages)
        try:
            response = self.client.models.generate_content(model=self.model_id, contents=prompt)
            return type('Response', (object,), {'content': response.text})
        except Exception as e:
            logging.warning(f"Gemini error: {e}")
            return llm_backup.invoke(messages)

llm_gemini = Gemini2026Manager(GOOGLE_KEY) if GOOGLE_KEY else llm_backup
search_tool = DuckDuckGoSearchRun()

# --- 3. الوظائف التشغيلية ---
def send_telegram_message(message):
    try:
        token = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
        chat_id = "6168694801"
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                      json={"chat_id": chat_id, "text": message}, timeout=10)
    except: pass

def get_board_decision(task):
    """صنع القرار السيادي"""
    res = llm_gemini.invoke([
        SystemMessage(content="You are the Sovereign Compliance Manager. You find real Swedish companies and create professional data-sovereignty solutions (2026)."),
        HumanMessage(content=task)
    ])
    return res.content if hasattr(res, 'content') else str(res)

def export_to_github(filename, content, commit_message):
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        # التأكد من وجود المجلد أو حفظه في المسار المتاح
        try:
            contents = repo.get_contents(filename)
            repo.update_file(contents.path, commit_message, content, contents.sha)
        except:
            repo.create_file(filename, commit_message, content)
        return True
    except Exception as e:
        logging.error(f"GitHub Error: {e}")
        return False

def autonomous_factory_loop():
    """مصنع الصيد الآلي"""
    global AUTO_PRODUCTION_COUNT
    time.sleep(20) # انتظار استقرار السيرفر
    
    targets = [
        "Stockholm Private Health providers", 
        "Swedish insurance companies data storage", 
        "Government contractors Sweden AI privacy"
    ]
    
    while True:
        try:
            sector = random.choice(targets)
            logging.info(f"Hunting in sector: {sector}")
            
            # بحث عن شركات حقيقية
            raw_leads = search_tool.run(f"List of {sector} companies 2026 Sweden")
            
            ts = datetime.datetime.now(SWEDEN_TZ).strftime("%Y%m%d_%H%M")
            prompt = (f"Analyze these Swedish leads: {raw_leads}. "
                      f"Identify ONE real company. Write a high-level Sales Pitch in SWEDISH. "
                      f"Focus on Sovereign AI and keeping data inside Sweden to comply with 2026 laws.")
            
            result = get_board_decision(prompt)
            # حفظ في مجلد 'reports' لضمان التنظيم
            filename = f"reports/Sovereign_Analysis_{ts}.md"
            
            if export_to_github(filename, result, f"Sovereign Asset Created: {ts}"):
                AUTO_PRODUCTION_COUNT += 1
                send_telegram_message(f"🎯 **صيد سيادي جديد!**\n📂 الملف: {filename}\n🇸🇪 الوقت: {ts}")
            
        except Exception as e:
            logging.error(f"Factory Loop Error: {e}")
            time.sleep(300) # انتظار 5 دقائق في حال الفشل قبل المحاولة مجدداً
        
        # الانتظار لمدة ساعتين + دقائق عشوائية لمنع كشف البوت
        wait_time = 7200 + random.randint(1, 600)
        time.sleep(wait_time)

# --- 4. واجهة التحكم والتشغيل ---
@app.route('/')
def home():
    uptime = datetime.datetime.now(SWEDEN_TZ) - EMPIRE_START_TIME
    return {
        "status": "Empire is Live",
        "assets_produced": AUTO_PRODUCTION_COUNT,
        "uptime": str(uptime),
        "current_time_sweden": datetime.datetime.now(SWEDEN_TZ).strftime("%Y-%m-%d %H:%M")
    }

if __name__ == "__main__":
    # بدء خيط الصيد في الخلفية
    threading.Thread(target=autonomous_factory_loop, daemon=True).start()
    
    # تشغيل خادم الويب (Port 10000 هو الافتراضي لـ Render)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
