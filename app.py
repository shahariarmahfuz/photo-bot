import logging
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackContext, ConversationHandler

TOKEN = "7305874644:AAEcpUBhpmmOrv0rE-0xTJsUSxsTmO5qZHw"
BASE_URL = "https://nekos-photo.onrender.com"
UPLOAD_URL = f"{BASE_URL}/photo"
API_URL = "https://nekofilx.onrender.com/photo"

# কনভারসেশন স্টেটস
ANIME_NUMBER, IMG_RATIO_2_3, IMG_RATIO_16_9 = range(3)

# লগ সেটআপ
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# ------------------ Start কমান্ড -------------------
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("👋 *স্বাগতম! দয়া করে একটি ছবি পাঠান, আমি সেটি আপলোড করব।*", parse_mode="MarkdownV2")

# ------------------ নরমাল ছবি আপলোড হ্যান্ডলার -------------------
async def handle_photo(update: Update, context: CallbackContext):
    """নরমাল ছবি আপলোড করার জন্য ফাংশন (এটি অপরিবর্তিত)"""
    processing_message = await update.message.reply_text("⚡ *ছবিটি প্রসেস করা হচ্ছে...*", parse_mode="MarkdownV2")

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

        safe_text = f"✅ *আপলোড সম্পন্ন!* \n🔗 *লিংক:* \n`{final_url}`"
        await update.message.reply_text(safe_text, parse_mode="MarkdownV2")

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("❌ *সমস্যা হয়েছে, পরে চেষ্টা করুন!*", parse_mode="MarkdownV2")

    finally:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_message.message_id)

# ------------------ ছবি আপলোড ফাংশন -------------------
async def upload_photo(photo, context):
    """ছবি আপলোড করে সার্ভার থেকে লিংক ফেরত দেয়"""
    try:
        file = await context.bot.get_file(photo.file_id)
        response = requests.get(file.file_path)

        if response.status_code != 200:
            raise Exception("Failed to download image")

        files = {"file": ("image.jpg", response.content, "image/jpeg")}
        res = requests.post(UPLOAD_URL, files=files)

        if res.status_code != 200:
            raise Exception("Failed to upload image")

        data = res.json()
        return f"{BASE_URL}{data['local_url']}"  # আপলোড হওয়া ছবির লিংক ফেরত দেওয়া
    except Exception as e:
        logging.error(f"Upload Error: {e}")
        return None

# ------------------ /add কমান্ড হ্যান্ডলার -------------------
async def add_command(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("📟 *এনিমির নাম্বার দিন:*", parse_mode="MarkdownV2")
    return ANIME_NUMBER

async def get_anime_number(update: Update, context: CallbackContext) -> int:
    context.user_data["anime"] = update.message.text
    await update.message.reply_text("📸 *এখন 2:3 অনুপাতের ছবি পাঠান:*", parse_mode="MarkdownV2")
    return IMG_RATIO_2_3

async def get_img_ratio_2_3(update: Update, context: CallbackContext) -> int:
    """2:3 ছবিটি আপলোড করা হবে"""
    if not update.message.photo:
        await update.message.reply_text("❌ দয়া করে একটি ছবি পাঠান!", parse_mode="MarkdownV2")
        return IMG_RATIO_2_3

    processing_message = await update.message.reply_text("⏳ *ছবি আপলোড হচ্ছে...*", parse_mode="MarkdownV2")
    img_url = await upload_photo(update.message.photo[-1], context)
    
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_message.message_id)

    if not img_url:
        await update.message.reply_text("❌ *ছবি আপলোড করতে ব্যর্থ হয়েছে, আবার চেষ্টা করুন!*", parse_mode="MarkdownV2")
        return IMG_RATIO_2_3

    context.user_data["img"] = img_url
    await update.message.reply_text("📸 *এখন 16:9 অনুপাতের ছবি পাঠান:*", parse_mode="MarkdownV2")
    return IMG_RATIO_16_9

async def get_img_ratio_16_9(update: Update, context: CallbackContext) -> int:
    """16:9 ছবিটি আপলোড করা হবে"""
    if not update.message.photo:
        await update.message.reply_text("❌ দয়া করে একটি ছবি পাঠান!", parse_mode="MarkdownV2")
        return IMG_RATIO_16_9

    processing_message = await update.message.reply_text("⏳ *ছবি আপলোড হচ্ছে...*", parse_mode="MarkdownV2")
    anime_img_url = await upload_photo(update.message.photo[-1], context)
    
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_message.message_id)

    if not anime_img_url:
        await update.message.reply_text("❌ *ছবি আপলোড করতে ব্যর্থ হয়েছে, আবার চেষ্টা করুন!*", parse_mode="MarkdownV2")
        return IMG_RATIO_16_9

    context.user_data["anime_img"] = anime_img_url

    # API-তে রিকোয়েস্ট পাঠানো
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
                "✅ *সফলভাবে আপডেট করা হয়েছে!* \n\n"
                f"🔗 *[এনিমি পেজ ফটো]({data['anime_page_photo']})* \n"
                f"📸 *[ইমেজ লিংক]({data['image']})* \n"
                f"📝 *মেসেজ:* `{data['message']}`"
            )
        else:
            message = f"❌ *ত্রুটি:* `{data.get('message', 'অজানা ত্রুটি')}`"

    except Exception as e:
        logging.error(f"API Error: {str(e)}")
        message = "⚠️ *সার্ভারে সমস্যা হয়েছে, পরে চেষ্টা করুন!*"

    await update.message.reply_text(message, parse_mode="MarkdownV2")
    return ConversationHandler.END

# বট চালু করা
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))  # নরমাল আপলোড

    app.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("add", add_command)],
            states={
                ANIME_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_anime_number)],
                IMG_RATIO_2_3: [MessageHandler(filters.PHOTO, get_img_ratio_2_3)],
                IMG_RATIO_16_9: [MessageHandler(filters.PHOTO, get_img_ratio_16_9)],
            },
            fallbacks=[],
        )
    )

    print("🤖 *বট চালু হয়েছে...*")
    app.run_polling()

if __name__ == "__main__":
    main()
