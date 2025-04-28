import os
import asyncio
import nest_asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import requests

# تفعيل nest_asyncio
nest_asyncio.apply()

# توكن البوت ورابط الويب هوك
TOKEN = "7357184512:AAEzEFq2unKQ0oemjma3XsIF0OESrgywa6g"
WEBHOOK_URL = "https://web-production-bdb7a.up.railway.app/"

# إنشاء تطبيق تيليجرام وفلاسك
application = ApplicationBuilder().token(TOKEN).build()
flask_app = Flask(__name__)

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 افتح Panda Store", url="https://pandastores.onrender.com")],  # رابط عادي يفتح في المتصفح
        [InlineKeyboardButton("🚀 Start Shopping", callback_data="start_shopping")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "مرحبًا بك في Panda Store 🐼✨!\n"
        "تقدر تشتري نجوم تيليجرام بكل سهولة من موقعنا الرسمي 🌟",
        reply_markup=reply_markup
    )

# لما المستخدم يضغط على "Start Shopping"
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "start_shopping":
        await start(update, context)

# تسجيل أوامر البوت
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("restart", start))  # لو تحب تضيف أمر إعادة تشغيل عادي
application.add_handler(
    CallbackQueryHandler(button_handler)  # التعامل مع زرار "Start Shopping"
)

# الصفحة الرئيسية
@flask_app.route("/")
def home():
    return "✅ Panda Bot is Running!"

# استقبال التحديثات من تيليجرام
@flask_app.route("/webhook", methods=["POST"])
def webhook_handler():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.run(application.process_update(update))
    return "ok", 200

# إعداد الويب هوك
async def setup_webhook():
    set_webhook_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    webhook_data = {"url": f"{WEBHOOK_URL}/webhook"}
    response = requests.post(set_webhook_url, data=webhook_data)
    print("Webhook setup response:", response.json())

# بدء البوت والخادم
if __name__ == "__main__":
    async def main():
        if not application._initialized:
            await application.initialize()
        if not application._running:
            await application.start()
        await setup_webhook()
        flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

    asyncio.run(main())
