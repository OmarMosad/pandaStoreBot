from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import nest_asyncio
import asyncio

# تفعيل nest_asyncio
nest_asyncio.apply()

# إعداد التوكن
TOKEN = os.environ.get("BOT_TOKEN")

# إنشاء التطبيقين
app = Flask(__name__)
application = ApplicationBuilder().token(TOKEN).build()

# دالة /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 افتح Panda Store", url="https://pandastores.onrender.com")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "مرحبًا بك في Panda Store 🐼✨!\nتقدر تشتري نجوم تيليجرام بكل سهولة من موقعنا الرسمي 🌟",
        reply_markup=reply_markup
    )

# إضافة هاندلر start
application.add_handler(CommandHandler("start", start))

# صفحة رئيسية للتأكد أن السيرفر شغال
@app.route("/")
def home():
    return "✅ Panda Bot is Running!"

# نقطة استقبال التحديثات عبر الويب هوك
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
async def webhook_handler():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
    return "ok", 200

# تشغيل التطبيق
if __name__ == "__main__":
    async def main():
        if not application._initialized:
            await application.initialize()
        if not application._running:
            await application.start()

        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

    asyncio.run(main())
