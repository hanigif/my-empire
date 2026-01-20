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
import trafilatura

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

# --- 2. قاعدة البيانات والذاكرة ---
def init_db():
    conn = sqlite3.connect('sovereign.db')
    c = conn.cursor()
    # إنشاء الجدول الأساسي إذا لم يكن موجوداً
    c.execute('''CREATE TABLE IF NOT EXISTS targets 
                 (id INTEGER PRIMARY KEY, company TEXT, country TEXT, fine TEXT, date TEXT, status TEXT)''')
    
    # فحص إذا كان عمود status موجوداً بالفعل، وإذا لم يوجد يتم إضافته
    c.execute("PRAGMA table_info(targets)")
    columns = [column[1] for column in c.fetchall()]
    if 'status' not in columns:
        c.execute("ALTER TABLE targets ADD COLUMN status TEXT DEFAULT 'Scouted'")
        
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
    
    pdf.set_font("Arial", 'B', 50)
    pdf.set_text_color(240, 240, 240)
    pdf.rotate(45, 105, 155)
    pdf.text(30, 190, "CONFIDENTIAL - SOVEREIGN")
    pdf.rotate(0)
    
    pdf.ln(25)
    pdf.set_text_color(30, 41, 59)
    
    for line in analysis_data.split('\n'):
        if ':' in line:
            title, content = line.split(':', 1)
            pdf.set_font("Arial", 'B', 11)
            pdf.set_fill_color(241, 245, 249)
            pdf.cell(0, 8, title.strip().upper(), ln=True, fill=True)
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(0, 6, content.strip().encode('latin-1', 'replace').decode('latin-1'))
            pdf.ln(2)
            
    file_name = f"Sovereign_Executive_Report_{int(time.time())}.pdf"
    pdf.output(file_name)
    return file_name

# --- 5. رادار الصيد والتدقيق (The Mission) ---
def deep_hunting_mission(sector="Logistics"):
    try:
        query = f"Swedish mid-sized {sector} transport companies privacy leaks NIS2 compliance 2026"
        raw_data = search_tool.run(query)
        
        mission_prompt = f"""
        TASK: ACT AS A SWEDISH CYBER-LEGAL AUDITOR (IMY SPECIALIST).
        DATA SOURCE: {raw_data[:2500]}

        1. FOCUS: Find a REAL Swedish mid-sized Logistics/Transport company (local names in Gothenburg/Stockholm).
        2. PREDICTIVE AUDIT: Analyze digital presence for NIS2 failures (24h reporting, EU data residency).
        3. FINANCIAL WOUND: Calculate potential fine (4% of revenue) in SEK.
        4. SOVEREIGN SHIELD: Explain how our 'Sovereign Agent' solves this.
        5. THE PITCH (Swedish): Professional CEO message starting with: "VIKTIGT: Bristande efterlevnad av NIS2-direktivet identifierad för [Company Name]"
        
        Format the output: TARGET, COUNTRY, WOUND, SHIELD, PITCH.
        """
        
        analysis = ai_engine.ask(mission_prompt, "Senior Swedish Data Auditor & NIS2 Expert")
        
        comp = "Unknown Target"
        try:
            lines = analysis.split('\n')
            target_line = [l for l in lines if "TARGET" in l.upper()][0]
            comp = target_line.split(':')[1].strip()
            
            conn = sqlite3.connect('sovereign.db')
            conn.cursor().execute("INSERT INTO targets (company, date) VALUES (?, ?)", 
                                (comp, str(datetime.datetime.now(SWEDEN_TZ))))
            conn.commit()
            conn.close()
        except Exception as db_e:
            logging.error(f"Database Save Error: {db_e}")

        pdf_path = create_rich_report(analysis)
        
        url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
        with open(pdf_path, "rb") as f:
            requests.post(url, data={
                "chat_id": MY_ID, 
                "caption": f"🚨 رادار السيادة: تم اصطياد هدف حقيقي!\n🏢 الشركة: {comp}\n🎯 القطاع: {sector}"
            }, files={"document": f})
        
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            
    except Exception as e:
        logging.error(f"Hunting Error: {e}")

def technical_vulnerability_scan(domain):
    """فحص تقني حقيقي لاكتشاف تسريب البيانات للسيرفرات الأمريكية"""
    target_url = domain if domain.startswith("http") else f"https://{domain}"
    leaks = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (SovereignAudit/1.0)'}
        response = requests.get(target_url, timeout=10, headers=headers)
        content = response.text.lower()
        
        if "google-analytics.com" in content or "googletagmanager.com" in content:
            leaks.append("Google Analytics (Detected: Unauthorized US Data Flow)")
        if "facebook.net/en_us/fbevents.js" in content:
            leaks.append("Facebook Pixel (Detected: Direct PII Leak to Meta US)")
        if "hotjar.com" in content:
            leaks.append("Hotjar (Detected: Session Recording on External Servers)")
            
        return leaks
    except Exception as e:
        return [f"Scan Error: {str(e)}"]

# دمج الفحص في عملية التدقيق الحي
def real_time_compliance_audit(domain):
    tech_leaks = technical_vulnerability_scan(domain)
    leaks_found = "\n".join(tech_leaks) if tech_leaks else "No direct technical leaks found."

    downloaded = trafilatura.fetch_url(f"{domain}/privacy-policy") or trafilatura.fetch_url(domain)
    web_text = trafilatura.extract(downloaded) if downloaded else "No content"
    
    audit_prompt = f"""
    ANALYSIS TASK: Conduct a CRITICAL Legal & Technical audit.
    DOMAIN: {domain}
    TECHNICAL LEAKS DETECTED: {leaks_found}
    SOURCE TEXT: {web_text[:3000]}
    
    INSTRUCTIONS:
    1. PROVE THE VIOLATION: Use the detected technical leaks to cite specific NIS2/GDPR breaches.
    2. THE FINE: Calculate the fine based on 4% of their revenue (use SEK).
    3. THE SOLUTION: Pitch our 'Sovereign Proxy' that fixes these SPECIFIC leaks.
    4. LANGUAGE: Arabic for me, but the PITCH in Swedish.
    """
    return ai_engine.ask(audit_prompt, "Senior Swedish Data Auditor")

# --- 6. واجهة الويب (Dashboard) ---
app = Flask(__name__)

@app.route('/')
def dashboard():
    conn = sqlite3.connect('sovereign.db')
    # جلب آخر 10 أهداف مع كامل بياناتهم
    targets = conn.execute("SELECT company, country, fine, date, status FROM targets ORDER BY id DESC LIMIT 10").fetchall()
    targets_count = conn.execute("SELECT count(*) FROM targets").fetchone()[0]
    # جلب عدد الحلول التي أُرسلت فعلياً
    solutions_sent = conn.execute("SELECT count(*) FROM targets WHERE status = 'Solution Sent'").fetchone()[0]
    conn.close()
    
    now_sw = datetime.datetime.now(SWEDEN_TZ).strftime('%Y-%m-%d %H:%M:%S')
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8"><title>Sovereign Manager | Control Center</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background-color: #020617; color: #f8fafc; }}
            .cyber-card {{ background: rgba(30, 41, 59, 0.5); border: 1px solid #38bdf8; backdrop-filter: blur(10px); }}
            .status-glow-sent {{ color: #4ade80; text-shadow: 0 0 10px rgba(74, 222, 128, 0.5); }}
            .status-glow-scouted {{ color: #fbbf24; text-shadow: 0 0 10px rgba(251, 191, 36, 0.5); }}
        </style>
    </head>
    <body class="p-8">
        <div class="max-w-6xl mx-auto">
            <div class="flex justify-between items-center border-b border-slate-700 pb-6 mb-8">
                <div>
                    <h1 class="text-3xl font-bold text-sky-400">🛡️ SOVEREIGN MANAGER CORE</h1>
                    <p class="text-slate-400 text-sm">Sovereign Data Compliance Lead Generation</p>
                </div>
                <p class="font-mono text-sky-300 text-right">{now_sw}<br><span class="text-xs text-slate-500 font-sans">Stockholm, Sweden</span></p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div class="cyber-card p-6 rounded-xl text-center">
                    <h3 class="text-slate-400 text-sm mb-2">TARGETS SCOUTED</h3>
                    <p class="text-5xl font-black text-sky-400">{targets_count}</p>
                </div>
                <div class="cyber-card p-6 rounded-xl text-center">
                    <h3 class="text-slate-400 text-sm mb-2">SOLUTIONS DELIVERED</h3>
                    <p class="text-5xl font-black text-emerald-400">{solutions_sent}</p>
                </div>
                <div class="cyber-card p-6 rounded-xl text-center">
                    <h3 class="text-slate-400 text-sm mb-2">PII PROTECTED</h3>
                    <p class="text-5xl font-black text-amber-400">ACTIVE</p>
                </div>
            </div>

            <div class="cyber-card rounded-xl overflow-hidden shadow-2xl">
                <table class="w-full text-left">
                    <thead class="bg-slate-900/80 text-sky-400">
                        <tr>
                            <th class="p-4">COMPANY ENTITY</th>
                            <th class="p-4">COMPLIANCE STATUS</th>
                            <th class="p-4">DISCOVERY DATE</th>
                        </tr>
                    </thead>
                    <tbody>
                        {" ".join([f'''
                        <tr class="border-b border-slate-800 hover:bg-slate-800/30 transition-colors">
                            <td class="p-4 font-semibold">{t[0]}</td>
                            <td class="p-4">
                                <span class="{"status-glow-sent" if t[4] == 'Solution Sent' else "status-glow-scouted"}">
                                    ● {t[4] if t[4] else 'Scouted'}
                                </span>
                            </td>
                            <td class="p-4 text-slate-400 text-sm">{t[3]}</td>
                        </tr>''' for t in targets])}
                    </tbody>
                </table>
            </div>
            
            <div class="mt-6 text-center text-slate-600 text-xs">
                &copy; 2026 Sovereign Data Agent | Sweden Compliance Operation
            </div>
        </div>
    </body>
    </html>
    """

# --- 7. معالجة الرسائل والتشغيل (Telegram & Scheduler) ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    text = update.message.text.strip()
    
    if text == "اصطاد":
        await update.message.reply_text("⚖️ الرادار يعمل.. جاري مسح الأسواق السويدية...")
        threading.Thread(target=deep_hunting_mission).start()

    elif text.startswith("حل"):
        company_name = text.replace("حل ", "").strip()
        await update.message.reply_text(f"📦 جاري تحضير حقيبة 'Sovereign Proxy' لشركة {company_name}...")
        
        # طلب نص بيع مختصر وواضح لتجنب التعقيد
        pitch_prompt = f"Write a professional CEO-level pitch for {company_name}. Focus on how SovereignProxy.py solves NIS2 compliance. Keep it under 800 characters. Language: Swedish."
        pitch = ai_engine.ask(pitch_prompt, "Swedish B2B Sales Expert")
        
        if os.path.exists("SovereignProxy.py"):
            try:
                # 1. إرسال رسالة البيع كنص عادي أولاً لتجنب أخطاء Markdown والطول
                await update.message.reply_text(f"🚀 عرض الحل لـ {company_name}:\n\n{pitch}")
                
                # 2. إرسال الملف بشكل مستقل بعدها مباشرة
                with open("SovereignProxy.py", "rb") as f:
                    await context.bot.send_document(
                        chat_id=MY_ID, 
                        document=f, 
                        caption=f"SovereignProxy.py technical file for {company_name}"
                    )
                
                # تحديث حالة الهدف في قاعدة البيانات
                conn = sqlite3.connect('sovereign.db')
                conn.execute("UPDATE targets SET status = 'Solution Sent' WHERE company LIKE ?", (f"%{company_name}%",))
                conn.commit()
                conn.close()
            except Exception as e:
                await update.message.reply_text(f"❌ خطأ تقني أثناء الإرسال: {str(e)}")
        else:
            await update.message.reply_text("❌ خطأ: ملف SovereignProxy.py غير موجود في المجلد الرئيسي.")

    elif text.startswith("فحص"):
        domain = text.split(" ")[1] if " " in text else None
        if domain:
            await update.message.reply_text(f"🔍 جاري فحص الامتثال لـ {domain}...")
            report = real_time_compliance_audit(domain)
            await update.message.reply_text(report)
    
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
    await application.updater.start_polling()
    while True: await asyncio.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000, use_reloader=False), daemon=True).start()
    asyncio.run(main())





