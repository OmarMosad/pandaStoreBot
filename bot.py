import os
import asyncio
import nest_asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import requests

# تفعيل nest_asyncio
nest_asyncio.apply()

# توكن البوت ورابط الويب هوك
TOKEN = "7357184512:AAEzEFq2u0OESrgywa6g"
WEBHOOK_URL = "https://web-production-bdb7a.up.railway.app/"

# إنشاء تطبيق تيليجرام وفلاسك
application = ApplicationBuilder().token(TOKEN).build()
flask_app = Flask(__name__)

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # زر في الرسالة فقط
    inline_keyboard = [
        [InlineKeyboardButton("🚀 افتح Panda Store", url="https://pandastores.onrender.com")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)

    # كيبورد دائم تحت الرسالة
    reply_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("🚀 Start Shopping")],
            [KeyboardButton("❓ المساعدة")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

    # إرسال الرسالة بالزر الخارجي + الكيبورد
    await update.message.reply_text(
        "مرحبًا بك في Panda Store 🐼✨!\n"
        "تقدر تشتري نجوم تيليجرام بكل سهولة من موقعنا الرسمي 🌟",
        reply_markup=reply_markup
    )

    # إرسال الكيبورد الثابت بدون أي رسائل إضافية
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="",
        reply_markup=reply_keyboard
    )

# التعامل مع ضغط الأزرار العادية
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🚀 Start Shopping":
        # يعمل ريستارت (كأنه ضغط /start)
        await start(update, context)
    elif text == "❓ المساعدة":
        # يفتح لينك الشات الخاص بك
        await update.message.reply_text("تواصل مع الأدمن مباشرة: [اضغط هنا](https://t.me/OMAR_M_SHEHATA)", parse_mode="Markdown")

# تسجيل الأوامر
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("restart", start))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_buttons))

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
