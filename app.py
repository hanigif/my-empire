import os, threading, asyncio, logging, datetime, pytz
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram.error import TimedOut, NetworkError
from apscheduler.schedulers.background import BackgroundScheduler

# استيراد المحرك السيادي المطور
from strategy_core import get_board_decision 

# --- 1. الإعدادات الأساسية ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
TOKEN = os.environ.get("TELEGRAM_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
MY_ID = 6758877303  
SWEDEN_TZ = pytz.timezone('Europe/Stockholm')

app = Flask(__name__)

# --- 2. نظام النبض والتدقيق الآلي ---
def auto_learning_cycle():
    now = datetime.datetime.now(SWEDEN_TZ).strftime('%H:%M:%S')
    logging.info(f"[*] نبضة سيادية دورية: {now}")
    try:
        # البحث التلقائي عن عملاء أو ثغرات لضمان تحديث المنتج
        result = get_board_decision("AUTO_AUDIT: تدقيق امتثال 2026")
        logging.info(f"[-] نتيجة الدورة: {result[:100]}...")
    except Exception as e:
        logging.error(f"[!] تنبيه في الدورة الآلية: {e}")

# تشغيل المجدول
scheduler = BackgroundScheduler(daemon=True, timezone=SWEDEN_TZ)
scheduler.add_job(func=auto_learning_cycle, trigger="interval", hours=1)
scheduler.start()

# --- 3. معالجة رسائل القائد ---
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_user.id != MY_ID: 
        return
    
    await update.message.reply_text("⚖️ جاري استشارة العقول السيادية (Gemini & Llama)...")
    
    try:
        task = update.message.text
        # استدعاء المحرك الذي يحتوي على وظيفة الـ Scout والإنتاج
        response = get_board_decision(task)
        await update.message.reply_text(response)
    except Exception as e:
        logging.error(f"Technical Error: {e}")
        await update.message.reply_text(f"⚠️ عطل فني: {str(e)[:100]}")

# --- 4. بوابة الويب (الواجهة التجارية السيادية) ---
@app.route('/')
def home():
    try:
        now_sweden = datetime.datetime.now(SWEDEN_TZ).strftime('%Y-%m-%d %H:%M:%S')
        # تصميم واجهة احترافية لبيع المنتج (The Sovereign Gate) للشركات السويدية
        return f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Sovereign Gate | حلول الامتثال السيادي</title>
            <style>
                body {{ background-color: #050505; color: #f0f0f0; font-family: 'Segoe UI', Tahoma, Geneva, sans-serif; margin: 0; padding: 0; text-align: center; }}
                .hero {{ padding: 100px 20px; background: radial-gradient(circle, #0d1a0d 0%, #050505 100%); border-bottom: 1px solid #1a331a; }}
                h1 {{ color: #00ff41; font-size: 3.5em; margin: 0; text-shadow: 0 0 20px rgba(0,255,65,0.4); font-weight: 900; }}
                .tagline {{ font-size: 1.4em; color: #888; max-width: 800px; margin: 20px auto; line-height: 1.6; }}
                .cta-button {{ background: #00ff41; color: #000; padding: 18px 40px; font-weight: bold; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 30px; transition: 0.3s; font-size: 1.1em; }}
                .cta-button:hover {{ background: #fff; box-shadow: 0 0 30px #00ff41; transform: translateY(-3px); }}
                .features {{ display: flex; justify-content: center; gap: 30px; padding: 70px 20px; flex-wrap: wrap; background: #080808; }}
                .card {{ background: #111; border: 1px solid #1a1a1a; padding: 30px; width: 280px; border-radius: 12px; transition: 0.3s; text-align: right; }}
                .card:hover {{ border-color: #00ff41; background: #151515; }}
                .card h3 {{ color: #00ff41; margin-top: 0; font-size: 1.5em; }}
                .card p {{ color: #aaa; line-height: 1.5; }}
                .status-footer {{ background: #000; padding: 15px; font-family: monospace; font-size: 0.85em; color: #00ff41; border-top: 1px solid #1a331a; position: fixed; bottom: 0; width: 100%; }}
            </style>
        </head>
        <body>
            <div class="hero">
                <h1>SOVEREIGN GATE</h1>
                <p class="tagline">نؤمن بيانات الرعاية الصحية السويدية لعام 2026. امتثال كامل لـ Patientdatalagen بلمسة تقنية سيادية تضمن أمنك القانوني.</p>
                <a href="https://t.me/your_bot_username" class="cta-button">تواصل مع المحرك السيادي</a>
            </div>
            
            <div class="features">
                <div class="card">
                    <h3>🛡️ حراسة البيانات</h3>
                    <p>تشفير محلي سيادي يمنع تسرب البيانات الحساسة إلى السحابات العالمية دون غطاء قانوني كامل.</p>
                </div>
                <div class="card">
                    <h3>⚖️ تدقيق 2026</h3>
                    <p>نظام ذكاء اصطناعي يراقب التحديثات التشريعية السويدية ويعدل بروتوكولات التشفير تلقائياً.</p>
                </div>
                <div class="card">
                    <h3>📜 تقارير الامتثال</h3>
                    <p>توليد تقارير براءة ذمة قانونية دورية جاهزة للتقديم لهيئات الرقابة والتدقيق السويدية.</p>
                </div>
            </div>

            <div class="status-footer">
                SYSTEM_STATUS: ACTIVE | COMPLIANCE_LEVEL: 100% | SWEDEN_TIME: {now_sweden}
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"Sovereign System Online - Web UI Error: {str(e)[:50]}"

# --- 5. محرك الإقلاع (مع نظام إعادة المحاولة الصارم) ---
async def main():
    if not TOKEN:
        logging.error("❌ TELEGRAM_TOKEN مفقود!")
        return

    # بناء التطبيق مرة واحدة خارج الحلقة
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))

    max_retries = 5
    retry_delay = 5  # ثوانٍ

    for attempt in range(max_retries):
        try:
            logging.info(f"🔄 محاولة بدء تشغيل النظام ({attempt + 1}/{max_retries})...")
            
            # بروتوكول الصمود لتجاوز أخطاء الشبكة في Render
            await application.bot.delete_webhook(drop_pending_updates=True)
            await application.initialize()
            await application.start()
            await application.updater.start_polling(drop_pending_updates=True)
            
            logging.info("🚀 تم تشغيل الإمبراطورية بنجاح وتجاوز عوائق الشبكة!")
            break 
        except (TimedOut, NetworkError) as e:
            if attempt < max_retries - 1:
                logging.warning(f"⚠️ مهلة اتصال (Timeout). إعادة المحاولة خلال {retry_delay} ثوانٍ...")
                await asyncio.sleep(retry_delay)
            else:
                logging.error("🚨 فشلت جميع محاولات الاتصال بالسيرفرات الخارجية.")
                raise e

    # الحفاظ على التشغيل
    while True:
        await asyncio.sleep(1)

# --- 6. التشغيل النهائي ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    # تشغيل Flask للويب في الخلفية
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, use_reloader=False), daemon=True).start()
    
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("System Shutdown.")
