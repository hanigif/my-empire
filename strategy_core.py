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

# --- 1. الإعدادات السيادية ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
GK_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") 
REPO_NAME = "hanigif/Sovereign-Assets"
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')
PRODUCTION_DIR = "production"

EMPIRE_START_TIME = datetime.datetime.now(SWEDEN_TZ)
PULSE_COUNT = 0
AUTO_PRODUCTION_COUNT = 0 

if not os.path.exists(PRODUCTION_DIR):
    os.makedirs(PRODUCTION_DIR)

# --- 2. العقول السيادية ---
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
        except: return llm_backup.invoke(messages)

llm_gemini = Gemini2026Manager(GOOGLE_KEY) if GOOGLE_KEY else llm_backup
search_tool = DuckDuckGoSearchRun()

# --- 3. نظام الإشعارات والمصنع ---
def send_telegram_message(message):
    try:
        token = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
        chat_id = "6168694801"
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                      json={"chat_id": chat_id, "text": message}, timeout=10)
    except: pass

def autonomous_factory_loop():
    global AUTO_PRODUCTION_COUNT
    time.sleep(30)
    targets = ["Private Health Tech Stockholm", "Digital Mental Health Sweden", "Swedish FinTech Privacy"]
    
    while True:
        try:
            sector = random.choice(targets)
            send_telegram_message(f"🔎 بدأت جولة صيد في قطاع: {sector}")
            
            # البحث عن أهداف
            raw_leads = search_tool.run(f"list of {sector} companies Sweden 2026")
            
            # صناعة الحل
            prompt = f"Target leads: {raw_leads}. Choose one real Swedish company. Write a professional Sales Pitch in SWEDISH for their CTO about 'Sovereign Data Compliance'. Focus on preventing AI data leaks."
            result = get_board_decision(prompt)
            
            # الحفظ والرفع
            ts = datetime.datetime.now(SWEDEN_TZ).strftime("%H%M")
            filename = f"pitch_{ts}.txt"
            
            with open(os.path.join(PRODUCTION_DIR, filename), "w", encoding="utf-8") as f:
                f.write(result)
            
            export_to_github(f"production/{filename}", result, f"New Lead {ts}")
            AUTO_PRODUCTION_COUNT += 1
            send_telegram_message(f"🎯 صيد ثمين! تم إنشاء عرض للشركة بنجاح.\nالملف: {filename}")
            
        except Exception as e:
            logging.error(f"Error: {e}")
            time.sleep(600)
        time.sleep(3600)

# --- 4. العمليات التقنية ---
def export_to_github(filename, content, commit_message):
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        try:
            contents = repo.get_contents(filename)
            repo.update_file(contents.path, commit_message, content, contents.sha)
        except:
            repo.create_file(filename, commit_message, content)
    except: pass

def get_board_decision(task):
    if any(k in task.lower() for k in ["status", "حالة"]):
        uptime = datetime.datetime.now(SWEDEN_TZ) - EMPIRE_START_TIME
        return (f"🏛️ **تقرير الإمبراطورية**\n⏱️ تشغيل: {uptime.days}d {uptime.seconds//3600}h\n"
                f"⚙️ إنتاج آلي: {AUTO_PRODUCTION_COUNT}\n📅 السويد: {datetime.datetime.now(SWEDEN_TZ).strftime('%H:%M')}")

    # محرك التفكير
    res = llm_gemini.invoke([HumanMessage(content=task)])
    return res.content if hasattr(res, 'content') else str(res)

class SovereignLab:
    def run_stress_test(self):
        return f"🚀 الحالة: الإمبراطورية جاهزة للصيد. وقت السويد: {datetime.datetime.now(SWEDEN_TZ)}"
