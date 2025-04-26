import os
import asyncio
import nest_asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# تفعيل nest_asyncio
nest_asyncio.apply()

# بيئة العمل
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
MONGO_URI = os.getenv("MONGO_URI")  # حاطين اللينك كامل من .env

# إنشاء التطبيقات
app = Flask(__name__)
application = ApplicationBuilder().token(TOKEN).build()
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client.get_default_database()
orders_collection = db.get_collection("orders")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 افتح Panda Store", web_app=WebAppInfo(url="https://pandastores.onrender.com"))]
    ]
    await update.message.reply_text(
        "مرحبًا بك في Panda Store 🐼✨!\nتقدر تشتري نجوم تيليجرام بكل سهولة من موقعنا الرسمي 🌟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# تنفيذ الطلب بعد الضغط
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("confirm_"):
        username = query.data.replace("confirm_", "")
        await query.message.delete()
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"✅ تم تنفيذ طلب @{username} وحذف الرسالة بنجاح.")

# مراقبة الطلبات الجديدة
async def watch_orders():
    async with orders_collection.watch() as stream:
        async for change in stream:
            if change["operationType"] == "insert":
                full_doc = change["fullDocument"]
                username = full_doc.get("username")
                stars = full_doc.get("stars")
                created_at = full_doc.get("createdAt")
                
                if username and stars:
                    text = (
                        f"🛒 طلب جديد:\n\n"
                        f"👤 المستخدم: @{username}\n"
                        f"⭐ عدد النجوم: {stars}\n"
                        f"🗓 تاريخ الطلب: {created_at}"
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

# ربط الهاندلرز
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_callback))

# الصفحة الرئيسية
@app.route("/")
def home():
    return "✅ Panda Bot is Running!"

# تجهيز التطبيق
async def setup():
    await application.initialize()
    await application.start()
    asyncio.create_task(watch_orders())
    print("✅ Bot and DB Listener started!")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup())
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
