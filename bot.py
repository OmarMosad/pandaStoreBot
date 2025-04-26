# bot.py
import os
import asyncio
import datetime
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from motor.motor_asyncio import AsyncIOMotorClient
import nest_asyncio

# تفعيل nest_asyncio عشان نستخدم Flask مع asyncio
nest_asyncio.apply()

# إعدادات
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
MONGO_URI = os.getenv("MONGO_URI")

# إنشاء التطبيق
app = Flask(__name__)
application = ApplicationBuilder().token(TOKEN).build()

# اتصال بقاعدة بيانات MongoDB
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client.get_database()  # بياخد الداتابيز اللي موجودة في رابط الاتصال
orders_collection = db.orders  # اسم الكوليكشن بتاع الأوردرات (غيره لو عندك اسم تاني)

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

# دالة لمراقبة الطلبات الجديدة في قاعدة البيانات
async def monitor_orders():
    print("🔎 بدأ مراقبة الطلبات الجديدة في MongoDB...")
    pipeline = [{'$match': {'operationType': 'insert'}}]  # نرصد بس الإضافات الجديدة
    async with orders_collection.watch(pipeline) as stream:
        async for change in stream:
            order = change['fullDocument']
            username = order.get('username')
            stars = order.get('stars')
            created_at = order.get('createdAt', datetime.datetime.now().isoformat())

            if username and stars:
                date_text = datetime.datetime.fromisoformat(created_at).strftime("%Y-%m-%d %H:%M:%S")
                text = (
                    f"🛒 طلب جديد:\n\n"
                    f"👤 المستخدم: @{username}\n"
                    f"⭐ عدد النجوم: {stars}\n"
                    f"🗓 تاريخ الطلب: {date_text}"
                )
                await application.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=text,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("💳 دفع المستخدم", web_app=WebAppInfo(url="https://fragment.com/stars"))],
                        [InlineKeyboardButton("✅ تم تنفيذ الطلب", callback_data=f"confirm_{username}")]
                    ])
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

# صفحة رئيسية للاطمئنان أن البوت شغال
@app.route("/")
def home():
    return "✅ Panda Bot is Running and Monitoring MongoDB!"

# دالة تجهيز التطبيق
async def setup_application():
    print("⏳ Initializing the bot...")
    await application.initialize()
    await application.start()
    print("✅ Bot initialized and started!")
    asyncio.create_task(monitor_orders())  # نبدأ مراقبة الطلبات بعد بدء البوت

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup_application())
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
