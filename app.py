import logging
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackContext

TOKEN = "7305874644:AAEcpUBhpmmOrv0rE-0xTJsUSxsTmO5qZHw"
BASE_URL = "https://photo-upload-production-cd8b.up.railway.app"
UPLOAD_URL = f"{BASE_URL}/photo"

# লগিং সেটআপ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)

# Start কমান্ড
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("👋 স্বাগতম! দয়া করে একটি ছবি পাঠান, আমি সেটি আপলোড করব।")

# ছবি হ্যান্ডলার
async def handle_photo(update: Update, context: CallbackContext):
    # প্রসেসিং মেসেজ পাঠানো
    processing_message = await update.message.reply_text("⚡ ছবিটি প্রসেস করা শুরু হয়েছে...")
    
    try:
        # ছবি ডাউনলোড
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        response = requests.get(file.file_path)
        
        if response.status_code != 200:
            raise Exception("Failed to download image")
        
        # ছবি আপলোড
        files = {"file": ("image.jpg", response.content, "image/jpeg")}
        res = requests.post(UPLOAD_URL, files=files)
        
        if res.status_code != 200:
            raise Exception("Failed to upload image")
        
        # লিংক তৈরি এবং মেসেজ ফরম্যাট
        data = res.json()
        final_url = f"{BASE_URL}{data['local_url']}"
        
        # MarkdownV2 ফরম্যাটে মেসেজ তৈরি (স্পেশাল ক্যারেক্টার এস্কেপ করা)
        safe_text = (
            "✅ আপলোড সম্পন্ন\\!\n"  # '!' কে এস্কেপ করা হয়েছে
            "🔗 লিংক: "
            f"`{final_url}`"  # ব্যাকটিকসের মধ্যে URL রাখা হয়েছে
        )
        
        # ফাইনাল মেসেজ পাঠানো
        await update.message.reply_text(
            safe_text,
            parse_mode="MarkdownV2"
        )
        
    except Exception as e:
        logging.error(f"Error: {e}")
        # এরর মেসেজ পাঠানো (এস্কেপ করা '!' সহ)
        await update.message.reply_text("❌ সমস্যা হয়েছে, পরে চেষ্টা করুন\\!", parse_mode="MarkdownV2")
        
    finally:
        # প্রসেসিং মেসেজ ডিলিট করা
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=processing_message.message_id
        )

# বট চালু করা
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("🤖 বট চালু হয়েছে...")
    app.run_polling()

if __name__ == "__main__":
    main()
