import os, threading, asyncio, logging
from flask import Flask, request, abort
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# --- إعدادات الفريق والهوية ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GK_KEY = os.environ.get("GROQ_API_KEY")
# ضع الرقم الذي تعتقد أنه صحيح هنا
MY_TELEGRAM_ID = 675887303 

# إعداد السجلات لمراقبة الأمان
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Empire OS: Security Shield Active</h1>"

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    user_id = update.effective_user.id
    user_text = update.message.text

    # --- نظام التحقق الذكي من الهوية ---
    if MY_TELEGRAM_ID and user_id != MY_TELEGRAM_ID:
        logger.warning(f"🚫 محاولة وصول من ID: {user_id}")
        # هذه الرسالة ستظهر لك لمرة واحدة لتصحيح الـ ID إذا كان خطأ
        await update.message.reply_text(f"⚠️ وصول مرفوض. رقم تعريفك الفعلي هو: {user_id}\nيرجى تحديثه في الكود لفتح القلعة.")
        return 

    try:
        # إعداد الذكاء الاصطناعي (Llama 3.3)
        llm = Chat
