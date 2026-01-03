import os, threading, asyncio, logging, time, datetime
import yfinance as yf
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# --- الإعدادات الفنية ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
TOKEN = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = 6758877303
LEARNING_FILE = "empire_intelligence.txt"

app = Flask(__name__)

# قائمة الـ 100 شركة (عينة تمثيلية يمكن توسيعها)
TOP_100 = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "AVGO", "ASML", "COST", "NFLX", "ADBE", "AMD", "INTC", "PYPL"]

@app.route('/')
def home():
    size = os.path.getsize(LEARNING_FILE) if os.path.exists(LEARNING_FILE) else 0
    return f"Empire OS v5.0: Status ACTIVE. Knowledge Base: {size} bytes. System is learning..."

# --- 1. محرك التحليل والتعلم الذاتي ---
async def learn_and_analyze(application):
    """هذه الدورة تعمل وأنت نائم لجمع المعلومات وتحليل الفرص"""
    llm = ChatGroq(temperature=0.2, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
    
    while True:
        try:
            now = datetime.datetime.now()
            logging.info(f"Starting learning cycle at {now}")
            
            summary_report = "--- تقرير الفرص المكتشفة ---\n"
            found_opportunity = False

            for ticker in TOP_100:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="5d")
                if hist.empty: continue
                
                # حساب تقني سريع (RSI مبسط)
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change = ((current_price - prev_price) / prev_price) * 100
                
                # معايير التنبيه: حركة قوية أو وصول لنقطة شراء
                if abs(change) > 2.5: 
                    found_opportunity = True
                    analysis_prompt = f"حلل حركة سهم {ticker} السعرية الحالية (${current_price:.2f}, تغير {change:.2f}%). هل هذه فرصة شراء أم بيع بناءً على استراتيجيات النمو لعام 2026؟ اجعل الرد قصيراً واحترافياً للبيع كاستشارة."
                    ai_opinion = llm.invoke([HumanMessage(content=analysis_prompt)])
                    
                    report_entry = f"📍 {ticker}: ${current_price:.2f} ({change:+.2f}%)\n💡 AI: {ai_opinion.content}\n"
                    summary_report += report_entry
                    
                    # حفظ في ذاكرة النظام
                    with open(LEARNING_FILE, "a", encoding="utf-8") as f:
                        f.write(f"[{now}] {report_entry}\n")

            if found_opportunity:
                await application.bot.send_message(chat_id=MY_ID, text=f"🚀 هاني، اكتشفت فرصاً أثناء مراقبتي للسوق:\n\n{summary_report}")

            # تعلم عام عن السوق (محاكاة قراءة الكتب والتقارير)
            learning_prompt = "اكتب دراسة حالة قصيرة عن أفضل استراتيجية تداول لشركات التكنولوجيا في 2026 لتعزيز أرباح المحفظة بنسبة 20%."
            knowledge = llm.invoke([HumanMessage(content=learning_prompt)])
            with open(LEARNING_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n[KNOWLEDGE_{now}] {knowledge.content}\n")

        except Exception as e:
            logging.error(f"Error in learning cycle: {e}")
        
        await asyncio.sleep(3600) # كرر العملية كل ساعة

# --- 2. معالج الرسائل الذكي ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: return
    
    llm = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
    query = update.message.text
    
    # استحضار الذاكرة
    memory = ""
    if os.path.exists(LEARNING_FILE):
        with open(LEARNING_FILE, "r", encoding="utf-8") as f:
            memory = "".join(f.readlines()[-15:]) # آخر 15 سطر معلومات

    system_msg = f"أنت Empire OS، كيان استثماري متطور. هاني هو المدير. استخدم معلوماتك المحدثة: {memory}"
    response = llm.invoke([SystemMessage(content=system_msg), HumanMessage(content=query)])
    await update.message.reply_text(response.content)

# --- 3. تشغيل النظام ومنع التضارب (Anti-Conflict) ---
def run_flask():
    app.run(host='0.0.0.0', port=10000)

async def main():
    # بناء التطبيق مع نظام معالجة الأخطاء
    application = ApplicationBuilder().token(TOKEN).build()
    
    # إضافة المعالجات
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    # تشغيل دورة التعلم في الخلفية
    asyncio.create_task(learn_and_analyze(application))
    
    # بدء البوت مع تنظيف أي جلسات قديمة لمنع خطأ 409
    logging.info("Starting Empire OS v5.0...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True) # حذف أي رسائل قديمة متراكمة
    
    # ابقاء النظام يعمل
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    # تشغيل Flask في خيط منفصل
    threading.Thread(target=run_flask, daemon=True).start()
    
    # تشغيل المحرك الرئيسي
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
