import logging
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackContext

TOKEN = "7305874644:AAEcpUBhpmmOrv0rE-0xTJsUSxsTmO5qZHw"
BASE_URL = "https://b15638c8-af87-4164-b831-414c185be4c8-00-3o5w0isf9c16d.pike.replit.dev"
UPLOAD_URL = f"{BASE_URL}/photo"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("👋 স্বাগতম! দয়া করে একটি ছবি পাঠান, আমি সেটি আপলোড করব।")

async def handle_photo(update: Update, context: CallbackContext):
    # প্রসেসিং মেসেজ পাঠানো এবং স্টোর করা
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
        markdown_link = f"`{final_url}`"
        
        # ফাইনাল মেসেজ পাঠানো
        await update.message.reply_text(
            f"✅ আপলোড সম্পন্ন!\n🔗 লিংক: {markdown_link}",
            parse_mode="MarkdownV2"
        )
        
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("❌ সমস্যা হয়েছে, পরে চেষ্টা করুন!")
        
    finally:
        # প্রসেসিং মেসেজ ডিলিট
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=processing_message.message_id
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("🤖 বট চালু হয়েছে...")
    app.run_polling()

if __name__ == "__main__":
    main()
