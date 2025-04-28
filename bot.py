import os
import asyncio
import nest_asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests

# تفعيل nest_asyncio
nest_asyncio.apply()

# التوكن والهوك
TOKEN = "7357184512:AAEzEFq2unKQ0oemjma3XsIF0OESrgywa6g"
WEBHOOK_URL = "https://web-production-bdb7a.up.railway.app"  # لينك Railway بتاعك

# إنشاء تطبيق Flask
flask_app = Flask(__name__)

# إنشاء تطبيق تيليجرام
application = ApplicationBuilder().token(TOKEN).build()

# أمر start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 افتح Panda Store", web_app=WebAppInfo(url="https://pandastores.onrender.com"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "مرحبًا بك في Panda Store 🐼✨!\nتقدر تشتري نجوم تيليجرام بكل سهولة من موقعنا الرسمي 🌟",
        reply_markup=reply_markup
    )

# إضافة أمر /start
application.add_handler(CommandHandler("start", start))

# الصفحة الرئيسية
@flask_app.route("/")
def home():
    return "✅ Panda Bot is Running!"

# استقبال التحديثات من تيليجرام
@flask_app.route("/webhook", methods=["POST"])
def webhook_handler():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.create_task(application.process_update(update))
    return "ok", 200

# تهيئة الويب هوك تلقائيًا
async def setup_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    webhook_url = f"{WEBHOOK_URL}/webhook"
    data = {"url": webhook_url}
    response = requests.post(url, data=data)
    print("Webhook setup response:", response.json())

# تشغيل كل حاجة
if __name__ == "__main__":
    async def main():
        if not application._initialized:
            await application.initialize()
        if not application._running:
            await application.start()
        await setup_webhook()

    asyncio.run(main())
