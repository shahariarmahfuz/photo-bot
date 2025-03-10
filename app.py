import logging
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackContext, ConversationHandler

TOKEN = "7305874644:AAEcpUBhpmmOrv0rE-0xTJsUSxsTmO5qZHw"
BASE_URL = "https://nekos-photo.onrender.com"
UPLOAD_URL = f"{BASE_URL}/photo"
API_URL = "https://nekofilx.onrender.com/photo"

# কনভারসেশন স্টেটস
ANIME_NUMBER, IMG_RATIO_2_3_PHOTO, IMG_RATIO_16_9_PHOTO = range(3)

# লগিং সেটআপ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Start কমান্ড
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("👋 *স্বাগতম\\!* এখানে আপনি `/add` কমান্ড এর মাধ্যমে এনিমি পেজের থাম্বনেইল আপলোড করতে পারবেন।", parse_mode="MarkdownV2")

# ------------------ /add কমান্ড হ্যান্ডলার -------------------
async def add_command(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("📟 *এনিমির নাম্বার দিন:*", parse_mode="MarkdownV2")
    return ANIME_NUMBER

async def get_anime_number(update: Update, context: CallbackContext) -> int:
    context.user_data["anime"] = update.message.text
    await update.message.reply_text("🖼 *2:3 থাম্বনেইলের ছবি দিন:*", parse_mode="MarkdownV2")
    return IMG_RATIO_2_3_PHOTO

async def get_img_ratio_2_3_photo(update: Update, context: CallbackContext) -> int:
    processing_message_2_3 = await update.message.reply_text("⚡ *2:3 থাম্বনেইল আপলোড করা হচ্ছে\\.\\.\\.*", parse_mode="MarkdownV2")
    try:
        photo_2_3 = update.message.photo[-1]
        file_2_3 = await context.bot.get_file(photo_2_3.file_id)
        response_2_3 = requests.get(file_2_3.file_path)

        if response_2_3.status_code != 200:
            raise Exception("Failed to download 2:3 image")

        files_2_3 = {"file": ("image_2_3.jpg", response_2_3.content, "image/jpeg")}
        res_2_3 = requests.post(UPLOAD_URL, files=files_2_3)

        if res_2_3.status_code != 200:
            raise Exception("Failed to upload 2:3 image")

        data_2_3 = res_2_3.json()
        context.user_data["img"] = f"{BASE_URL}{data_2_3['local_url']}"
        await update.message.reply_text("🎬 *16:9 থাম্বনেইলের ছবি দিন:*", parse_mode="MarkdownV2")

    except Exception as e:
        logging.error(f"Error uploading 2:3 image: {e}")
        await update.message.reply_text("❌ *2:3 থাম্বনেইল আপলোডে সমস্যা হয়েছে, আবার চেষ্টা করুন\\!*", parse_mode="MarkdownV2")
        return ConversationHandler.END

    finally:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_message_2_3.message_id)
    return IMG_RATIO_16_9_PHOTO


async def get_img_ratio_16_9_photo(update: Update, context: CallbackContext) -> int:
    processing_message_16_9 = await update.message.reply_text("⚡ *16:9 থাম্বনেইল আপলোড করা হচ্ছে\\.\\.\\.*", parse_mode="MarkdownV2")
    try:
        photo_16_9 = update.message.photo[-1]
        file_16_9 = await context.bot.get_file(photo_16_9.file_id)
        response_16_9 = requests.get(file_16_9.file_path)

        if response_16_9.status_code != 200:
            raise Exception("Failed to download 16:9 image")

        files_16_9 = {"file": ("image_16_9.jpg", response_16_9.content, "image/jpeg")}
        res_16_9 = requests.post(UPLOAD_URL, files=files_16_9)

        if res_16_9.status_code != 200:
            raise Exception("Failed to upload 16:9 image")

        data_16_9 = res_16_9.json()
        context.user_data["anime_img"] = f"{BASE_URL}{data_16_9['local_url']}"

        anime = context.user_data.get("anime", "").strip()
        img = context.user_data.get("img", "").strip()
        anime_img = context.user_data.get("anime_img", "").strip()

        params = {
            "anime": anime,
            "img": img,
            "anime_img": anime_img,
        }
        api_response = requests.get(API_URL, params=params)
        api_response.raise_for_status()
        api_data = api_response.json()

        if api_data.get("status") == "success":
            message = (
                "✅ *সফলভাবে আপডেট করা হয়েছে\\!* \n\n"
                f"🔗 *[এনিমি পেজ ফটো]({api_data['anime_page_photo']})* \n"
                f"📸 *[2:3 থাম্বনেইল]({img})* \n"
                f"🎬 *[16:9 থাম্বনেইল]({anime_img})* \n"
                f"📝 *মেসেজ:* `{api_data['message']}`"
            )
        else:
            message = f"❌ *ত্রুটি:* `{api_data.get('message', 'অজানা ত্রুটি')}`"

    except Exception as e:
        logging.error(f"API Error: {str(e)}")
        message = "⚠️ *সার্ভারে সমস্যা হয়েছে, পরে চেষ্টা করুন\\!*"

    finally:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_message_16_9.message_id)

    await update.message.reply_text(message, parse_mode="MarkdownV2", disable_web_page_preview=True)
    return ConversationHandler.END

# বট চালু করা
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    # নরমাল আপলোড হ্যান্ডলার রিমুভ করা হয়েছে
    # app.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, handle_photo))

    app.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("add", add_command)],
            states={
                ANIME_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_anime_number)],
                IMG_RATIO_2_3_PHOTO: [MessageHandler(filters.PHOTO & ~filters.COMMAND, get_img_ratio_2_3_photo)],
                IMG_RATIO_16_9_PHOTO: [MessageHandler(filters.PHOTO & ~filters.COMMAND, get_img_ratio_16_9_photo)],
            },
            fallbacks=[],
        )
    )

    print("🤖 *বট চালু হয়েছে...*")
    app.run_polling()

if __name__ == "__main__":
    main()
