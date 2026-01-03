import os, threading, asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import yfinance as yf # أداة جلب بيانات السوق الحقيقية

TOKEN = "7987600648:AAFsGFuAqOandpZAwh1g1wia5zv6OutySdQ"
GK_KEY = os.environ.get("GROQ_API_KEY")
MY_ID = "6758877303"

app = Flask(__name__)

@app.route('/')
def home(): return "<h1>Empire OS v2.0: Active & Linked</h1>"

def get_stock_info(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.fast_info
        return f"السعر الحالي لـ {symbol}: ${data['last_price']:.2f}"
    except: return "تعذر جلب بيانات السوق حالياً."

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update or not update.message or not update.message.text: return
    if str(update.effective_user.id) != MY_ID: return

    user_text = update.message.text
    # محرك جلب البيانات الحية إذا ذكر سهم
    market_data = ""
    if "NVDA" in user_text.upper(): market_data = get_stock_info("NVDA")
    elif "AAPL" in user_text.upper(): market_data = get_stock_info("AAPL")

    try:
        llm = ChatGroq(temperature=0.2, model_name="llama-3.3-70b-versatile", groq_api_key=GK_KEY)
        system_prompt = f"""
        أنت نظام إدارة Empire OS. بصفتك (المدير المالي) و(سايبر).
        مهمتك الحالية: بناء منتج 'Empire Guard: 100'.
        المعطيات الحقيقية المتاحة حالياً: {market_data}
        يجب أن يكون ردك احترافياً، دقيقاً، وبالعربية. ادمج التحليل المالي مع الأمن السيبراني.
        """
        
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_text)])
        await update.message.reply_text(response.content)
    except Exception as e:
        await update.message.reply_text(f"⚠️ النظام يحتاج تحديث: {str(e)}")

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    application.run_polling(drop_pending_updates=True, stop_signals=None)

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
