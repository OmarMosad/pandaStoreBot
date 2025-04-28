import os
import asyncio
import nest_asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests

# تفعيل nest_asyncio لتجنب تعارض مع Flask
nest_asyncio.apply()

# التوكن الخاص بالبوت
TOKEN = "7357184512:AAEzEFq2unKQ0oemjma3XsIF0OESrgywa6g"

# رابط الويب هوك
WEBHOOK_URL = "https://your-railway-app-url.up.railway.app"

# إنشاء تطبيق Flask
app = Flask(__name__)

# بناء تطبيق تيليجرام
application = ApplicationBuilder().token(TOKEN).build()

# كود أمر /start
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

# الصفحة الرئيسية
@app.route("/")
def home():
    return "✅ Panda Bot is Running!"

# ويب هوك ريسيفر
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook_handler():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.create_task(application.process_update(update))
    return "ok", 200

# وظيفة إعداد الويب هوك تلقائي
async def setup_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    webhook_url = f"{WEBHOOK_URL}/webhook/{TOKEN}"
    data = {"url": webhook_url}
    response = requests.post(url, data=data)
    print("Webhook setup response:", response.json())

# تشغيل كل شيء
if __name__ == "__main__":
    async def main():
        if not application._initialized:
            await application.initialize()
        if not application._running:
            await application.start()

        # إعداد الويب هوك تلقائي
        await setup_webhook()

        # تشغيل Flask
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

    asyncio.run(main())
