import os, threading, asyncio, logging, datetime, pytz, time, requests, sqlite3, json, random
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram.error import TimedOut, NetworkError
from apscheduler.schedulers.background import BackgroundScheduler
from google import genai 
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage
from cryptography.fernet import Fernet
import pyotp 
from fpdf import FPDF
import qrcode

# --- 1. الإعدادات الأساسية والسيادية ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN = os.environ.get("TELEGRAM_TOKEN")
GK_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY")
MY_ID = 6758877303  
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

S_KEY = os.environ.get("SOVEREIGN_KEY", Fernet.generate_key().decode())
cipher_suite = Fernet(S_KEY.encode())

TOTP_SECRET = os.environ.get("TOTP_SECRET", "JBSWY3DPEHPK3PXP")
totp_verifier = pyotp.TOTP(TOTP_SECRET, interval=1)

# --- 2. قاعدة البيانات والذاكرة (Sovereign DB & Memory) ---
def init_db():
    conn = sqlite3.connect('sovereign.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS targets 
                 (id INTEGER PRIMARY KEY, company TEXT, country TEXT, fine TEXT, date TEXT)''')
    conn.commit()
    conn.close()

init_db()

class SovereignMemory:
    def __init__(self):
        self.total_protected = 0
        self.threats_blocked = 0
        self.start_time = datetime.datetime.now(SWEDEN_TZ)
    def add_protected(self): self.total_protected += 1
    def add_threat(self): self.threats_blocked += 1

sov_memory = SovereignMemory()

# --- 3. المحركات الذكية (AI Engines) ---
llm_backup = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
search_tool = DuckDuckGoSearchRun()

class SovereignAI:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash"
    
    def ask(self, prompt, system_msg="You are the Sovereign Manager."):
        try:
            res = self.client.models.generate_content(
                model=self.model_id, 
                contents=f"System: {system_msg}\nUser: {prompt}"
            )
            return res.text
        except:
            res = llm_backup.invoke([SystemMessage(content=system_msg), HumanMessage(content=prompt)])
            return res.content

ai_engine = SovereignAI(GOOGLE_KEY)

# --- 4. محرك التقارير الاستراتيجي (Sovereign PDF) ---
class SovereignPDF(FPDF):
    def header(self):
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 35, 'F')
        self.set_font("Arial", 'B', 20)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, "SOVEREIGN STRATEGIC AUDIT", ln=True, align='C')
        self.set_font("Arial", 'I', 10)
        self.cell(0, 5, "Confidential Intelligence Report", ln=True, align='C')

    def footer(self):
        self.set_y(-25)
        self.set_font("Arial", 'I', 8)
        self.set_text_color(100)
        self.cell(0, 10, f"Sovereign Manager Core 2026 | Page {self.page_no()}", align='C')

def create_rich_report(analysis_data):
    pdf = SovereignPDF()
    pdf.add_page()
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(30, 41, 59)
    
    sections = analysis_data.split('\n\n')
    for section in sections:
        if ':' in section:
            title, content = section.split(':', 1)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, title.strip().upper(), ln=True)
            pdf.set_font("Arial", '', 11)
            pdf.multi_cell(0, 7, content.strip().encode('latin-1', 'replace').decode('latin-1'))
            pdf.ln(5)
    
    file_name = f"Sovereign_Audit_{int(time.time())}.pdf"
    pdf.output(file_name)
    return file_name

# --- 5. رادار الصيد (The Hunter Mission) ---
def deep_hunting_mission(sector="General"):
    try:
        query = f"latest GDPR fines 2025 2026 {sector} companies Europe Swedish news"
        raw_data = search_tool.run(query)
        
        mission_prompt = f"""
        Based on this data: {raw_data[:2500]}
        1. Identify a NEW real company recently fined (Prefer Swedish if available).
        2. Analyze the 'Financial Wound' (Fine amount vs impact).
        3. Craft a 'Sovereign Shield' solution.
        4. Write a professional CEO Pitch in the company's local language.
        Format: TARGET, COUNTRY, WOUND, SHIELD, PITCH.
        """
        
        analysis = ai_engine.ask(mission_prompt, "Senior Sovereign Strategist")
        
        # حفظ في قاعدة البيانات
        try:
            lines = analysis.split('\n')
            comp = [l for l in lines if "TARGET" in l][0].split(':')[1].strip()
            conn = sqlite3.connect('sovereign.db')
            conn.cursor().execute("INSERT INTO targets (company, date) VALUES (?, ?)", (comp, str(datetime.datetime.now(SWEDEN_TZ))))
            conn.commit()
            conn.close()
        except: pass

        pdf_path = create_rich_report(analysis)
        
        url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
        with open(pdf_path, "rb") as f:
            requests.post(url, data={"chat_id": MY_ID, "caption": f"🚨 رادار السيادة: تم اصطياد هدف في قطاع {sector}"}, files={"document": f})
        os.remove(pdf_path)
    except Exception as e:
        logging.error(f"Hunting Error: {e}")

# --- 6. واجهة الويب والـ API ---
app = Flask(__name__)

@app.route('/')
def dashboard():
    conn = sqlite3.connect('sovereign.db')
    targets_count = conn.cursor().execute("SELECT count(*) FROM targets").fetchone()[0]
    conn.close()
    now_sw = datetime.datetime.now(SWEDEN_TZ).strftime('%H:%M:%S')
    return f"""
    <body style='background:#0f172a; color:white; font-family:sans-serif; text-align:center; padding:50px;'>
        <h1 style='color:#38bdf8;'>🛡️ SOVEREIGN CONTROL CENTER</h1>
        <div style='display:flex; justify-content:center; gap:20px; margin:30px 0;'>
            <div style='background:#1e293b; padding:20px; border-radius:10px; border:1px solid #38bdf8; width:200px;'>
                <h3>Targets Captured</h3>
                <h2 style='font-size:3em; color:#38bdf8;'>{targets_count}</h2>
            </div>
            <div style='background:#1e293b; padding:20px; border-radius:10px; border:1px solid #4ade80; width:200px;'>
                <h3>Protected Records</h3>
                <h2 style='font-size:3em; color:#4ade80;'>{sov_memory.total_protected}</h2>
            </div>
        </div>
        <p>System Status: <span style='color:#4ade80;'>ACTIVE</span> | Pulse: {now_sw}</p>
    </body>
    """

# --- 7. معالجة الرسائل والتشغيل ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    text = update.message.text.strip()
    
    if text == "اصطاد":
        await update.message.reply_text("⚖️ الرادار يعمل.. جاري مسح الأسواق...")
        threading.Thread(target=deep_hunting_mission).start()
    elif text.startswith("قطاع"):
        sector = text.split(" ")[1] if " " in text else "General"
        await update.message.reply_text(f"🎯 توجيه الرادار نحو قطاع: {sector}")
        threading.Thread(target=deep_hunting_mission, args=(sector,)).start()
    else:
        response = ai_engine.ask(text)
        await update.message.reply_text(response)

async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    scheduler = BackgroundScheduler(daemon=True, timezone=SWEDEN_TZ)
    scheduler.add_job(func=deep_hunting_mission, trigger="interval", hours=3)
    scheduler.start()

    await application.bot.delete_webhook(drop_pending_updates=True)
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000, use_reloader=False), daemon=True).start()
    asyncio.run(main())
