import os
import asyncio
import nest_asyncio
import requests
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# تفعيل nest_asyncio
nest_asyncio.apply()

# التوكن والهوك
TOKEN = "7357184512:AAEzEFq2unKQ0oemjma3XsIF0OESrgywa6g"
WEBHOOK_URL = "https://web-production-bdb7a.up.railway.app"  # لينك الموقع بتاعك

# إنشاء بوت تيليجرام
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

# إضافة الهاندلر
application.add_handler(CommandHandler("start", start))

# إنشاء سيرفر Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Panda Bot is Running!"

@app.route('/webhook', methods=['POST'])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok", 200

# تهيئة الويب هوك
async def setup_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    webhook_url = f"{WEBHOOK_URL}/webhook"
    data = {"url": webhook_url}
    response = requests.post(url, data=data)
    print("Webhook setup response:", response.json())

# تشغيل كل حاجة
async def main():
    await application.initialize()
    await application.start()
    await setup_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    asyncio.run(main())
