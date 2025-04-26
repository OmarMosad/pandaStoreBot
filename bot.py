from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os
import asyncio

# إعدادات
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# إنشاء التطبيق
app = Flask(__name__)
application = ApplicationBuilder().token(TOKEN).build()

# دالة /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 افتح Panda Store", web_app=WebAppInfo(url="https://pandastores.onrender.com"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "مرحبًا بك في Panda Store 🐼✨!\nتقدر تشتري نجوم تيليجرام بكل سهولة من موقعنا الرسمي 🌟",
        reply_markup=reply_markup
    )

# تأكيد تنفيذ الطلب
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("confirm_"):
        username = query.data.replace("confirm_", "")
        await query.message.delete()
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"✅ تم تنفيذ طلب @{username} وحذف الرسالة بنجاح.")

# إضافة الهاندلرز
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_callback))

# استقبال التحديثات Webhook
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
async def webhook_handler():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok", 200

# الصفحة الافتراضية
@app.route("/")
def home():
    return "✅ Panda Bot is Running!"

# دالة تجهيز التطبيق
async def setup_application():
    print("⏳ Initializing the bot...")
    await application.initialize()
    await application.start()
    print("✅ Bot initialized and started!")

# تجهيز التطبيق أول ما السيرفر يبدأ
@app.before_first_request
def before_first_request():
    loop = asyncio.get_event_loop()
    loop.create_task(setup_application())

# تشغيل السيرفر لو محلي
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
