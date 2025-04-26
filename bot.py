from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os
import asyncio
import datetime

# إعداد
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# إنشاء Flask و Telegram Application
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

# دالة استقبال الأوردر من الويب
@app.route("/send_order", methods=["POST"])
def send_order():
    data = request.json
    username = data.get("username")
    stars = data.get("stars")
    created_at = data.get("createdAt", datetime.datetime.now().isoformat())

    if username and stars:
        date_text = datetime.datetime.fromisoformat(created_at).strftime("%Y-%m-%d %H:%M:%S")
        text = (
            f"🛒 طلب جديد:\n\n"
            f"👤 المستخدم: `@{username}`\n"
            f"⭐ عدد النجوم: {stars}\n"
            f"🗓️ تاريخ الطلب: {date_text}"
        )

        keyboard = [
            [InlineKeyboardButton("💳 دفع المستخدم", web_app=WebAppInfo(url="https://fragment.com/stars"))],
            [InlineKeyboardButton("✅ تم تنفيذ الطلب", callback_data=f"confirm_{username}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        asyncio.run(application.bot.send_message(
            chat_id=ADMIN_ID,
            text=text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        ))

    return "ok", 200

# دالة استقبال تأكيد تنفيذ الطلب
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("confirm_"):
        username = query.data.replace("confirm_", "")
        await query.message.delete()
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"✅ تم تنفيذ طلب @{username} وحذف الرسالة بنجاح."
        )

# هاندلرز البوت
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_callback))

# الويب هوك استقبال
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
async def webhook():
    if request.method == "POST":
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    return "ok", 200

# صفحة افتراضية
@app.route("/", methods=["GET"])
def home():
    return "✅ Panda Store Bot is Running!"

# تشغيل البوت والسيرفر مع بعض
async def run_bot():
    await application.initialize()
    await application.start()
    print("✅ Bot started...")

if __name__ == "__main__":
    # تشغيل التليجرام بوت
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())

    # تشغيل Flask
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
