import logging
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackContext, ConversationHandler

TOKEN = "7305874644:AAEcpUBhpmmOrv0rE-0xTJsUSxsTmO5qZHw"
BASE_URL = "https://photo-upload-production-cd8b.up.railway.app"
UPLOAD_URL = f"{BASE_URL}/photo"
API_URL = "https://nekofilx.onrender.com/photo"

# কনভারসেশন স্টেটস
ANIME_NUMBER, IMG_RATIO_2_3, IMG_RATIO_16_9 = range(3)

# লগিং সেটআপ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)

# Start কমান্ড
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("👋 *স্বাগতম\\!* দয়া করে একটি ছবি পাঠান, আমি সেটি আপলোড করব।", parse_mode="MarkdownV2")

# ছবি হ্যান্ডলার
async def handle_photo(update: Update, context: CallbackContext):
    processing_message = await update.message.reply_text("⚡ *ছবিটি প্রসেস করা শুরু হয়েছে\\.\\.\\.*", parse_mode="MarkdownV2")

    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        response = requests.get(file.file_path)

        if response.status_code != 200:
            raise Exception("Failed to download image")

        files = {"file": ("image.jpg", response.content, "image/jpeg")}
        res = requests.post(UPLOAD_URL, files=files)

        if res.status_code != 200:
            raise Exception("Failed to upload image")

        data = res.json()
        final_url = f"{BASE_URL}{data['local_url']}"

        safe_text = (
            "✅ *আপলোড সম্পন্ন\\!* \n"
            "🔗 *লিংক:* \n"
            f"`{final_url}`"
        )

        await update.message.reply_text(safe_text, parse_mode="MarkdownV2")

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("❌ *সমস্যা হয়েছে, পরে চেষ্টা করুন\\!*", parse_mode="MarkdownV2")

    finally:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_message.message_id)

# ------------------ /add কমান্ড হ্যান্ডলার -------------------
async def add_command(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("📟 *এনিমির নাম্বার দিন:*", parse_mode="MarkdownV2")
    return ANIME_NUMBER

async def get_anime_number(update: Update, context: CallbackContext) -> int:
    context.user_data["anime"] = update.message.text
    await update.message.reply_text("🖼 *2:3 থাম্বনেইলের লিংক দিন:*", parse_mode="MarkdownV2")
    return IMG_RATIO_2_3

async def get_img_ratio_2_3(update: Update, context: CallbackContext) -> int:
    context.user_data["img"] = update.message.text
    await update.message.reply_text("🎬 *16:9 থাম্বনেইলের লিংক দিন:*", parse_mode="MarkdownV2")
    return IMG_RATIO_16_9

async def get_img_ratio_16_9(update: Update, context: CallbackContext) -> int:
    context.user_data["anime_img"] = update.message.text

    anime = context.user_data.get("anime", "").strip()
    img = context.user_data.get("img", "").strip()
    anime_img = context.user_data.get("anime_img", "").strip()

    try:
        params = {
            "anime": anime,
            "img": img,
            "anime_img": anime_img,
        }
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "success":
            message = (
                "✅ *সফলভাবে আপডেট করা হয়েছে\\!* \n\n"
                f"🔗 *[এনিমি পেজ ফটো]({data['anime_page_photo']})* \n"
                f"📸 *[ইমেজ লিংক]({data['image']})* \n"
                f"📝 *মেসেজ:* `{data['message']}`"
            )
        else:
            message = f"❌ *ত্রুটি:* `{data.get('message', 'অজানা ত্রুটি')}`"

    except Exception as e:
        logging.error(f"API Error: {str(e)}")
        message = "⚠️ *সার্ভারে সমস্যা হয়েছে, পরে চেষ্টা করুন\\!*"

    await update.message.reply_text(message, parse_mode="MarkdownV2")
    return ConversationHandler.END

# বট চালু করা
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    app.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("add", add_command)],
            states={
                ANIME_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_anime_number)],
                IMG_RATIO_2_3: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_img_ratio_2_3)],
                IMG_RATIO_16_9: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_img_ratio_16_9)],
            },
            fallbacks=[],
        )
    )

    print("🤖 *বট চালু হয়েছে...*")
    app.run_polling()

if __name__ == "__main__":
    main()
