import os
import asyncio
import nest_asyncio
import requests
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

# تفعيل nest_asyncio
nest_asyncio.apply()

# التوكن ورابط الموقع
TOKEN = "7357184512:AAEzEFq2unKQ0oemjma3XsIF0OESrgywa6g"
WEBHOOK_URL = "https://web-production-bdb7a.up.railway.app"

# إنشاء Flask app
flask_app = Flask(__name__)

# إنشاء تيليجرام app
telegram_app = Application.builder().token(TOKEN).build()

# دالة أمر start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 افتح Panda Store", web_app=WebAppInfo(url="https://pandastores.onrender.com"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "مرحبًا بك في Panda Store 🐼✨!\nتقدر تشتري نجوم تيليجرام بكل سهولة من موقعنا الرسمي 🌟",
        reply_markup=reply_markup
    )

# إضافة أمر start
telegram_app.add_handler(CommandHandler("start", start))

# استقبال التحديثات من تيليجرام
@flask_app.route(f"/webhook/{TOKEN}", methods=["POST"])
async def webhook():
    if request.method == "POST":
        data = request.get_json(force=True)
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)
    return "ok", 200

# الصفحة الرئيسية
@flask_app.route("/")
def home():
    return "✅ Panda Bot is Running!"

# تفعيل الويب هوك
async def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    webhook_url = f"{WEBHOOK_URL}/webhook/{TOKEN}"
    res = requests.post(url, data={"url": webhook_url})
    print("Webhook set response:", res.text)

# تشغيل التطبيق
if __name__ == "__main__":
    async def main():
        await set_webhook()
        await telegram_app.initialize()
        await telegram_app.start()
        flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

    asyncio.run(main())
