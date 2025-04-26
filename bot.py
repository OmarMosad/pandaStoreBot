import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# إعدادات
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# إنشاء التطبيق Flask
app = Flask(__name__)

# إنشاء تطبيق تيليجرام
telegram_app: Application = ApplicationBuilder().token(TOKEN).build()

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

# دالة معالجة الكول باك
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("confirm_"):
        username = query.data.replace("confirm_", "")
        await query.message.delete()
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"✅ تم تنفيذ طلب @{username} وحذف الرسالة بنجاح.")

# إضافة الهاندلرز
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(handle_callback))

# إعداد بوت تيليجرام في الخلفية
async def telegram_bot_runner():
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()  # خلي البوت شغال عادي بدون مشاكل

# استقبال التحديثات Webhook من تليجرام
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    await telegram_app.process_update(update)
    return "ok", 200

# الصفحة الرئيسية للتأكد ان السيرفر شغال
@app.route("/", methods=["GET"])
def home():
    return "✅ Panda Bot is running!"

# تشغيل كل حاجة لما السيرفر يشتغل
def run():
    loop = asyncio.get_event_loop()
    loop.create_task(telegram_bot_runner())
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

if __name__ == "__main__":
    run()
