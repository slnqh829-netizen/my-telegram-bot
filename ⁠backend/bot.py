from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from downloader import extract_media
import os, re

TOKEN = os.getenv("BOT_TOKEN", "ضع_التوكن_هنا")

URL_PATTERN = re.compile(r'https?://[^\s]+')

user_settings = {}  # {user_id: {"quality": "4k"}}

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = [[
        InlineKeyboardButton("🎬 4K", callback_data="q_4k"),
        InlineKeyboardButton("📺 1080p", callback_data="q_1080p"),
        InlineKeyboardButton("📱 720p", callback_data="q_720p"),
    ]]
    await update.message.reply_text(
        "👋 *مرحباً بك في بوت التحميل الذكي*\n\n"
        "أرسل رابط فيديو/صورة من:\n"
        "• يوتيوب • تيك توك • إنستغرام • تويتر • فيسبوك\n\n"
        "⚙️ *اختر الجودة:*",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

async def quality_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    quality = q.data.split("_")[1]
    user_settings[uid] = {"quality": quality}
    await q.edit_message_text(f"✅ تم اختيار الجودة: *{quality}*\nأرسل الرابط الآن 🎯", parse_mode="Markdown")

async def handle_url(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    urls = URL_PATTERN.findall(text)
    if not urls:
        await update.message.reply_text("⚠️ أرسل رابط صحيح")
        return
    
    uid = update.from_user.id
    quality = user_settings.get(uid, {}).get("quality", "4k")
    
    msg = await update.message.reply_text("⏳ جاري التحميل بأعلى جودة...")
    result = await extract_media(urls[0], quality)
    
    if not result["success"]:
        await msg.edit_text(f"❌ فشل: {result['error']}")
        return
    
    file_size = os.path.getsize(result["file"]) / (1024*1024)
    await msg.edit_text(f"✅ تم! جودة: {result['resolution']}p | الحجم: {file_size:.1f}MB\n📤 جاري الرفع...")
    
    with open(result["file"], 'rb') as f:
        await update.message.reply_video(f, caption=f"🎬 {result['title'][:100]}")
    
    os.remove(result["file"])
    await msg.delete()

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(quality_callback, pattern="^q_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    print("🤖 البوت يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()
