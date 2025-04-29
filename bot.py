import os
import asyncio
import nest_asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
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
    inline_keyboard = [
        [InlineKeyboardButton("🚀 افتح Panda Store", url="https://pandastores.onrender.com")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)

    reply_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("❓المساعدة")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

    await update.message.reply_text(
        "مرحبًا بك في Panda Store 🐼✨!\n"
        "تقدر تشتري نجوم تيليجرام بكل سهولة من موقعنا الرسمي 🌟",
        reply_markup=reply_markup
    )

    # إرسال الكيبورد السُفلي فقط بدون رسالة
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="\u200b",  # حرف مخفي يمنع الكراش
        reply_markup=reply_keyboard
    )

# عندما يضغط المستخدم على زر المساعدة
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "إذا كنت بحاجة للمساعدة، يمكنك التواصل مع المدير عبر تيليجرام: @OMAR_M_SHEHATA"
    )

# تسجيل الأوامر
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("restart", start))

# التعامل مع زر المساعدة
application.add_handler(CommandHandler("help", help))

# صفحة التشغيل
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
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    data = {"url": f"{WEBHOOK_URL}/webhook"}
    response = requests.post(url, data=data)
    print("Webhook setup response:", response.json())

# بدء التطبيق
if __name__ == "__main__":
    async def main():
        if not application._initialized:
            await application.initialize()
        if not application._running:
            await application.start()
        await setup_webhook()
        flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

    asyncio.run(main())
