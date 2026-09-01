import telebot
from telebot import types

# =========================================================
# RB SENSI STORE BOT
# =========================================================
# 1) Put your BotFather token below.
# 2) Keep qr.jpg in the same folder as this file.
# 3) Install: pip install pyTelegramBotAPI
# 4) Run: python bot.py
# =========================================================

TOKEN = "8952232562:AAELo2nZmSKMP2rm0fkk91lQLDM2ZXV6-Y4"
ADMIN_ID = 6874112056
QR_IMAGE = "qr.jpg"

bot = telebot.TeleBot(TOKEN)

# ---------------- PACKS ----------------
PACKS = {
    "₹199 Basic": {
        "price": 199,
        "features": "1 Device + Basic Premium Sensitivity + User Friendly Settings",
    },
    "₹299 Pro": {
        "price": 299,
        "features": "1 Device + Advanced Sensitivity + DPI & Control Settings",
    },
    "₹450 Elite": {
        "price": 450,
        "features": "Device-Specific Premium Sensitivity + Advanced Configuration + Extra Tweaks",
    },
    "₹590 Ultimate": {
        "price": 590,
        "features": "Full Premium Pack + All Settings Unlocked + Priority Support",
    },
}

# Edit these lists if you want different brands/models.
BRANDS = {
    "Samsung": ["4GB", "6GB", "8GB"],
    "Redmi": ["4GB", "6GB", "8GB"],
    "Realme": ["4GB", "6GB", "8GB"],
    "Poco": ["4GB", "6GB", "8GB"],
    "Vivo": ["4GB", "6GB", "8GB"],
}

# Per-user temporary order data.
users = {}

# ---------------- KEYBOARD HELPERS ----------------
def keyboard(buttons, columns=2):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    row = []
    for i, text in enumerate(buttons, 1):
        row.append(types.KeyboardButton(text))
        if i % columns == 0:
            kb.row(*row)
            row = []
    if row:
        kb.row(*row)
    return kb


def main_keyboard():
    return keyboard(["🎁 Free Sensitivity", "💎 Premium Sensitivity"], 1)


def send_qr(chat_id, pack_name):
    pack = PACKS[pack_name]
    caption = (
        f"💎 *{pack_name}*\n"
        f"💰 Price: ₹{pack['price']}\n"
        f"📦 Features: {pack['features']}\n\n"
        "👇 Scan the QR and make the payment.\n"
        "📷 After payment, send the *payment screenshot* here.\n\n"
        "⚠️ Your order will be delivered after admin verification."
    )
    with open(QR_IMAGE, "rb") as photo:
        bot.send_photo(chat_id, photo, caption=caption, parse_mode="Markdown")


def reset_user(chat_id):
    users.pop(chat_id, None)


# ---------------- /START ----------------
@bot.message_handler(commands=["start"])
def start(message):
    users[message.chat.id] = {"step": "home"}
    bot.send_message(
        message.chat.id,
        "🤖 *Welcome to RB Sensi Store!*\n\n"
        "🎁 Free Sensitivity — free pack\n"
        "💎 Premium Sensitivity — paid device-specific packs\n\n"
        "Select an option below:",
        reply_markup=main_keyboard(),
        parse_mode="Markdown",
    )


# ---------------- FREE SENSI ----------------
@bot.message_handler(func=lambda m: m.text == "🎁 Free Sensitivity")
def free_sensi(message):
    users[message.chat.id] = {"step": "home"}
    # Replace this fixed text with your actual free sensitivity.
    bot.send_message(
        message.chat.id,
        "🎁 *FREE SENSITIVITY*\n\n"
        "Sensitivity: YOUR_FIXED_FREE_SENSI_HERE\n\n"
        "Use the buttons below to continue.",
        reply_markup=main_keyboard(),
        parse_mode="Markdown",
    )


# ---------------- PREMIUM START ----------------
@bot.message_handler(func=lambda m: m.text == "💎 Premium Sensitivity")
def premium_start(message):
    users[message.chat.id] = {"step": "brand"}
    bot.send_message(
        message.chat.id,
        "📱 Select your *Brand*:",
        reply_markup=keyboard(list(BRANDS.keys()), 2),
        parse_mode="Markdown",
    )


# ---------------- BRAND ----------------
@bot.message_handler(
    func=lambda m: users.get(m.chat.id, {}).get("step") == "brand"
)
def brand_selected(message):
    if message.text not in BRANDS:
        bot.send_message(
            message.chat.id,
            "⚠️ Click the right button ✅",
        )
        return

    users[message.chat.id].update({
        "brand": message.text,
        "step": "ram",
    })

    bot.send_message(
        message.chat.id,
        f"📱 Brand: *{message.text}*\n\nSelect your *RAM*:",
        reply_markup=keyboard(BRANDS[message.text], 3),
        parse_mode="Markdown",
    )


# ---------------- RAM ----------------
@bot.message_handler(
    func=lambda m: users.get(m.chat.id, {}).get("step") == "ram"
)
def ram_selected(message):
    data = users[message.chat.id]
    if message.text not in BRANDS.get(data.get("brand"), []):
        bot.send_message(message.chat.id, "⚠️ Click the right button ✅")
        return

    data.update({
        "ram": message.text,
        "step": "device",
    })

    devices = [
        "My device is not listed",
        "Enter my device manually",
    ]

    bot.send_message(
        message.chat.id,
        f"🧠 RAM: *{message.text}*\n\n"
        "Enter your exact device model.\n"
        "You can type the model name manually.",
        reply_markup=keyboard(devices, 1),
        parse_mode="Markdown",
    )


# ---------------- DEVICE ----------------
@bot.message_handler(
    func=lambda m: users.get(m.chat.id, {}).get("step") == "device"
)
def device_selected(message):
    data = users[message.chat.id]

    if message.text == "My device is not listed":
        bot.send_message(
            message.chat.id,
            "✍️ Please type your exact device model name:",
        )
        return

    if message.text == "Enter my device manually":
        bot.send_message(
            message.chat.id,
            "✍️ Please type your exact device model name:",
        )
        return

    data.update({
        "device": message.text,
        "step": "pack",
    })

    bot.send_message(
        message.chat.id,
        "💎 Select your Premium Pack:",
        reply_markup=keyboard(list(PACKS.keys()), 1),
    )


# ---------------- PACK ----------------
@bot.message_handler(
    func=lambda m: users.get(m.chat.id, {}).get("step") == "pack"
)
def pack_selected(message):
    data = users[message.chat.id]

    if message.text not in PACKS:
        bot.send_message(message.chat.id, "⚠️ Click the right button ✅")
        return

    data.update({
        "pack": message.text,
        "step": "waiting_payment",
    })

    pack = PACKS[message.text]
    bot.send_message(
        message.chat.id,
        f"✅ *Order Selected*\n\n"
        f"📱 Brand: {data['brand']}\n"
        f"🧠 RAM: {data['ram']}\n"
        f"📲 Device: {data['device']}\n"
        f"💎 Pack: {message.text}\n"
        f"💰 Price: ₹{pack['price']}",
        parse_mode="Markdown",
    )

    send_qr(message.chat.id, message.text)


# ---------------- PAYMENT SCREENSHOT ----------------
@bot.message_handler(content_types=["photo"])
def payment_screenshot(message):
    data = users.get(message.chat.id)

    if not data or data.get("step") != "waiting_payment":
        bot.send_message(
            message.chat.id,
            "⚠️ Please select a Premium Pack first.",
            reply_markup=main_keyboard(),
        )
        return

    data["step"] = "verification"
    data["screenshot_message_id"] = message.message_id

    # Send screenshot to admin.
    caption = (
        "🧾 *NEW PAYMENT VERIFICATION*\n\n"
        f"👤 User ID: `{message.chat.id}`\n"
        f"📱 Brand: {data['brand']}\n"
        f"🧠 RAM: {data['ram']}\n"
        f"📲 Device: {data['device']}\n"
        f"💎 Pack: {data['pack']}\n"
        f"💰 Amount: ₹{PACKS[data['pack']]['price']}\n\n"
        "Choose an action below."
    )

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(
            "✅ Approve", callback_data=f"approve:{message.chat.id}"
        ),
        types.InlineKeyboardButton(
            "❌ Reject", callback_data=f"reject:{message.chat.id}"
        ),
    )

    # Forward the actual screenshot first, then attach admin controls to a text message.
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.send_message(
        ADMIN_ID,
        caption,
        reply_markup=markup,
        parse_mode="Markdown",
    )

    bot.send_message(
        message.chat.id,
        "🕐 Payment screenshot received.\n\n"
        "✅ Admin verification pending. Please wait.",
    )


# ---------------- ADMIN APPROVE / REJECT ----------------
@bot.callback_query_handler(func=lambda call: call.data.startswith(("approve:", "reject:")))
def admin_action(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Not authorized.")
        return

    action, user_id_text = call.data.split(":", 1)
    user_id = int(user_id_text)
    data = users.get(user_id)

    if not data:
        bot.answer_callback_query(call.id, "Order data not found.")
        return

    if action == "approve":
        data["step"] = "approved"

        bot.send_message(
            user_id,
            "✅ *PAYMENT APPROVED*\n\n"
            f"💎 Pack: {data['pack']}\n"
            f"📱 Device: {data['device']}\n\n"
            "🎉 Your Premium Sensi is approved.\n"
            "Admin will send your Premium Details shortly.",
            parse_mode="Markdown",
        )

        bot.edit_message_reply_markup(
            ADMIN_ID,
            call.message.message_id,
            reply_markup=None,
        )
        bot.send_message(
            ADMIN_ID,
            f"✅ Approved order for User ID {user_id}."
        )
        bot.answer_callback_query(call.id, "Payment approved.")

    else:
        data["step"] = "rejected"

        bot.send_message(
            user_id,
            "❌ *PAYMENT REJECTED*\n\n"
            "The payment screenshot could not be verified.\n"
            "Please make the payment again and send a clear screenshot.",
            parse_mode="Markdown",
        )

        bot.edit_message_reply_markup(
            ADMIN_ID,
            call.message.message_id,
            reply_markup=None,
        )
        bot.send_message(
            ADMIN_ID,
            f"❌ Rejected order for User ID {user_id}."
        )
        bot.answer_callback_query(call.id, "Payment rejected.")


# ---------------- ADMIN DELIVERY ----------------
@bot.message_handler(commands=["send"])
def admin_send(message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.reply_to(
            message,
            "Usage:\n/send USER_ID Your premium sensi/details here"
        )
        return

    try:
        user_id = int(parts[1])
    except ValueError:
        bot.reply_to(message, "Invalid User ID.")
        return

    details = parts[2]
    data = users.get(user_id)

    if not data or data.get("step") != "approved":
        bot.reply_to(
            message,
            "User not found or payment is not approved yet."
        )
        return

    bot.send_message(
        user_id,
        "🎁 *YOUR PREMIUM SENSI*\n\n"
        f"📱 Device: {data['device']}\n"
        f"💎 Pack: {data['pack']}\n\n"
        f"{details}\n\n"
        "🙏 Thank you for choosing RB Sensi Store!",
        parse_mode="Markdown",
    )

    data["step"] = "delivered"
    bot.reply_to(message, "✅ Premium details delivered to customer.")


# ---------------- RANDOM TEXT / FALLBACK ----------------
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.send_message(
        message.chat.id,
        "⚠️ Click the right button ✅",
        reply_markup=main_keyboard(),
    )


# ---------------- RUN ----------------
if __name__ == "__main__":
    print("RB Sensi Store Bot is running...")
    bot.infinity_polling(skip_pending=True)
