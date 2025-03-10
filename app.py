import logging
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackContext

# **Bot Token সেট করুন**  
TOKEN = "7305874644:AAEcpUBhpmmOrv0rE-0xTJsUSxsTmO5qZHw"
BASE_URL = "https://b15638c8-af87-4164-b831-414c185be4c8-00-3o5w0isf9c16d.pike.replit.dev"  # Flask সার্ভারের BASE URL
UPLOAD_URL = f"{BASE_URL}/photo"  # Flask API লিংক

# **লগিং সেটআপ করুন**
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# **Start Command**
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("👋 স্বাগতম! দয়া করে একটি ছবি পাঠান, আমি সেটি আপলোড করব।")

# **ছবি আপলোড হ্যান্ডলার**
async def handle_photo(update: Update, context: CallbackContext):
    photo = update.message.photo[-1]  # সর্বোচ্চ রেজোলিউশনের ছবি নিন
    file = await context.bot.get_file(photo.file_id)
    file_path = file.file_path

    # **ছবি টেম্প ফাইলে ডাউনলোড করুন**
    response = requests.get(file_path)
    if response.status_code == 200:
        files = {"file": ("image.jpg", response.content, "image/jpeg")}
        res = requests.post(UPLOAD_URL, files=files)

        if res.status_code == 200:
            data = res.json()
            final_url = f"{BASE_URL}{data['local_url']}"  # **BASE_URL + /uploads/... যোগ করা**
            await update.message.reply_text(f"✅ আপলোড সম্পন্ন!\n🔗 লিংক: {final_url}")
        else:
            await update.message.reply_text("❌ আপলোডে সমস্যা হয়েছে, পরে চেষ্টা করুন।")
    else:
        await update.message.reply_text("❌ ছবি ডাউনলোড করা যায়নি, দয়া করে আবার চেষ্টা করুন।")

# **বট চালু করুন**
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("🤖 বট চালু হয়েছে...")
    app.run_polling()

if __name__ == "__main__":
    main()
