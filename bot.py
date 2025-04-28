import os
import asyncio
import nest_asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests

nest_asyncio.apply()

TOKEN = "التوكن بتاعك هنا"
WEBHOOK_URL = "رابط الموقع بتاعك هنا"  # مثلاً https://اسمك.railway.app

flask_app = Flask(__name__)
application = ApplicationBuilder().token(TOKEN).build()

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 افتح Panda Store", web_app=WebAppInfo(url="https://pandastores.onrender.com"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "مرحبًا بك في Panda Store 🐼✨!\nتقدر تشتري نجوم تيليجرام بكل سهولة من موقعنا الرسمي 🌟",
        reply_markup=reply_markup
    )

application.add_handler(CommandHandler("start", start))

# الصفحة الرئيسية
@flask_app.route("/")
def home():
    return "✅ Panda Bot is Running!"

# استقبال التحديثات
@flask_app.route("/webhook", methods=["POST"])
def webhook_handler():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(application.process_update(update))
    return "ok", 200

# تهيئة الويب هوك
async def setup_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    webhook_url = f"{WEBHOOK_URL}/webhook"
    data = {"url": webhook_url}
    response = requests.post(url, data=data)
    print("Webhook setup response:", response.json())

if __name__ == "__main__":
    async def main():
        if not application._initialized:
            await application.initialize()
        if not application._running:
            await application.start()
        await setup_webhook()
        flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

    asyncio.run(main())
