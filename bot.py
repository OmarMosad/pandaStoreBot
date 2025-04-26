from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os
import asyncio
import datetime
import nest_asyncio
import httpx  # اضفناها

# تفعيل nest_asyncio
nest_asyncio.apply()

# إعدادات
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# إنشاء التطبيق
app = Flask(__name__)

# إنشاء Client مخصص
client = httpx.AsyncClient(
    limits=httpx.Limits(max_connections=100),  # عدد اتصالات أكتر
    timeout=httpx.Timeout(10.0)  # وقت انتظار معقول
)

# بناء التطبيق مع client مخصص
application = ApplicationBuilder().token(TOKEN).client(client).build()

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

# استقبال طلبات الأوردر
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
            f"👤 المستخدم: @{username}\n"
            f"⭐ عدد النجوم: {stars}\n"
            f"🗓 تاريخ الطلب: {date_text}"
        )

        asyncio.create_task(application.bot.send_message(
            chat_id=ADMIN_ID,
            text=text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 دفع المستخدم", web_app=WebAppInfo(url="https://fragment.com/stars"))],
                [InlineKeyboardButton("✅ تم تنفيذ الطلب", callback_data=f"confirm_{username}")]
            ])
        ))

    return "ok", 200

# تأكيد تنفيذ الطلب
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("confirm_"):
        username = query.data.replace("confirm_", "")
        await query.message.delete()
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"✅ تم تنفيذ طلب @{username} وحذف الرسالة بنجاح.")

# تسجيل الهاندلرز
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

async def setup_application():
    print("⏳ Initializing the bot...")
    await application.initialize()
    await application.start()
    print("✅ Bot initialized and started!")

if __name__ == "__main__":
    # نعمل لوب ونشغل البوت قبل سيرفر Flask
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup_application())

    # بعدين نشغل السيرفر
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
