import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# === SOZLAMALAR ===
BOT_TOKEN = "8944341939:AAFt7QP-TsrKpvPLCeX7QFl3fET2x_gcklQ"
ADMIN_ID = 7654914240

# UC narxlari (miqdor: narx so'mda)
UC_PRICES = {
    "60 UC": 13_000,
    "325 UC": 60_000,
    "660 UC": 110_000,
    "1800 UC": 380_000,
    "3850 UC": 780_000,
    "8100 UC": 1_550_000,
}

# To'lov rekvizitlari
PAYMENT_CARD = "8600 1234 5678 9012"
PAYMENT_NAME = "Ismoil Karimov"

# Holat kodlari
SELECT_UC, ENTER_PLAYER_ID, CONFIRM_ORDER, WAIT_PAYMENT = range(4)

# Buyurtmalar saqlash (xotirada, keyinchalik DB ga o'tkazish mumkin)
orders = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# === BOSHLASH ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 UC sotib olish", callback_data="buy_uc")],
        [InlineKeyboardButton("📋 Mening buyurtmalarim", callback_data="my_orders")],
        [InlineKeyboardButton("📞 Qo'llab-quvvatlash", callback_data="support")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎮 *PUBG UC Do'koniga Xush Kelibsiz!*\n\n"
        "Tez va ishonchli UC yetkazib berish xizmati.\n"
        "Quyidagi tugmalardan birini tanlang:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


# === UC TANLASH ===
async def buy_uc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = []
    for uc, price in UC_PRICES.items():
        keyboard.append([InlineKeyboardButton(
            f"💎 {uc} — {price:,} so'm", callback_data=f"uc_{uc}"
        )])
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_main")])

    await query.edit_message_text(
        "💎 *UC miqdorini tanlang:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return SELECT_UC


async def select_uc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uc_choice = query.data.replace("uc_", "")
    context.user_data["uc"] = uc_choice
    context.user_data["price"] = UC_PRICES[uc_choice]

    await query.edit_message_text(
        f"✅ Siz *{uc_choice}* tanladingiz.\n\n"
        f"Endi PUBG *Player ID* raqamingizni kiriting:\n\n"
        f"_(Player ID ni PUBG o'yinida Profil > ID belgisidan topishingiz mumkin)_",
        parse_mode="Markdown"
    )
    return ENTER_PLAYER_ID


# === PLAYER ID KIRITISH ===
async def enter_player_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player_id = update.message.text.strip()

    if not player_id.isdigit():
        await update.message.reply_text(
            "❌ Player ID faqat raqamlardan iborat bo'lishi kerak. Qaytadan kiriting:"
        )
        return ENTER_PLAYER_ID

    context.user_data["player_id"] = player_id
    uc = context.user_data["uc"]
    price = context.user_data["price"]

    keyboard = [
        [InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm_order")],
        [InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_order")],
    ]

    await update.message.reply_text(
        f"📋 *Buyurtmangizni tasdiqlang:*\n\n"
        f"💎 UC miqdori: *{uc}*\n"
        f"🎮 Player ID: *{player_id}*\n"
        f"💰 Narxi: *{price:,} so'm*\n\n"
        f"Ma'lumotlar to'g'rimi?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return CONFIRM_ORDER


# === TASDIQLASH ===
async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    uc = context.user_data["uc"]
    price = context.user_data["price"]
    player_id = context.user_data["player_id"]

    # Buyurtma ID yaratish
    order_id = f"ORD{user.id}{len(orders)+1:04d}"
    orders[order_id] = {
        "user_id": user.id,
        "username": user.username,
        "uc": uc,
        "price": price,
        "player_id": player_id,
        "status": "To'lov kutilmoqda"
    }
    context.user_data["order_id"] = order_id

    await query.edit_message_text(
        f"💳 *To'lov Ma'lumotlari:*\n\n"
        f"🏦 Karta raqami: `{PAYMENT_CARD}`\n"
        f"👤 Karta egasi: *{PAYMENT_NAME}*\n"
        f"💰 To'lov summasi: *{price:,} so'm*\n\n"
        f"📌 Buyurtma ID: `{order_id}`\n\n"
        f"⚠️ To'lovni amalga oshirgandan so'ng, "
        f"to'lov chekini (screenshot) shu yerga yuboring.",
        parse_mode="Markdown"
    )

    # Adminga xabar
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🔔 *Yangi buyurtma!*\n\n"
             f"📌 ID: `{order_id}`\n"
             f"👤 Foydalanuvchi: @{user.username} ({user.id})\n"
             f"💎 UC: {uc}\n"
             f"🎮 Player ID: {player_id}\n"
             f"💰 Narx: {price:,} so'm\n"
             f"📊 Holat: To'lov kutilmoqda",
        parse_mode="Markdown"
    )
    return WAIT_PAYMENT


# === CHEK QABUL QILISH ===
async def receive_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    order_id = context.user_data.get("order_id", "Noma'lum")

    if orders.get(order_id):
        orders[order_id]["status"] = "Chek tekshirilmoqda"

    # Chekni adminga yuborish
    caption = (
        f"🧾 *To'lov cheki keldi!*\n\n"
        f"📌 Buyurtma ID: `{order_id}`\n"
        f"👤 @{user.username} ({user.id})\n"
        f"💎 UC: {orders.get(order_id, {}).get('uc', '-')}\n"
        f"🎮 Player ID: {orders.get(order_id, {}).get('player_id', '-')}"
    )

    if update.message.photo:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=caption,
            parse_mode="Markdown"
        )
    elif update.message.document:
        await context.bot.send_document(
            chat_id=ADMIN_ID,
            document=update.message.document.file_id,
            caption=caption,
            parse_mode="Markdown"
        )

    await update.message.reply_text(
        "✅ *Chekingiz qabul qilindi!*\n\n"
        f"📌 Buyurtma ID: `{order_id}`\n\n"
        "⏳ Admin tomonidan tekshirilgandan so'ng, "
        "UC hisobingizga o'tkaziladi (odatda 2 daqiqa).\n\n"
        "Savol bo'lsa: /support",
        parse_mode="Markdown"
    )
    return ConversationHandler.END


# === MENING BUYURTMALARIM ===
async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    user_orders = {k: v for k, v in orders.items() if v["user_id"] == user_id}

    if not user_orders:
        await query.edit_message_text(
            "📋 Sizda hali buyurtma yo'q.\n\n/start — Bosh menu",
            parse_mode="Markdown"
        )
        return

    text = "📋 *Sizning buyurtmalaringiz:*\n\n"
    for oid, o in list(user_orders.items())[-5:]:
        text += f"📌 `{oid}`\n💎 {o['uc']} | 💰 {o['price']:,} so'm | 📊 {o['status']}\n\n"

    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back_main")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


# === QOLLAB-QUVVATLASH ===
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back_main")]]
    await query.edit_message_text(
        "📞 *Qo'llab-quvvatlash:*\n\n"
        "Muammo yoki savollar uchun adminga murojaat qiling:\n"
        "👤 @nexus_admin1"
        "Ish vaqti: 24/7",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# === BOSH MENUGA QAYTISH ===
async def back_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🎮 UC sotib olish", callback_data="buy_uc")],
        [InlineKeyboardButton("📋 Mening buyurtmalarim", callback_data="my_orders")],
        [InlineKeyboardButton("📞 Qo'llab-quvvatlash", callback_data="support")],
    ]
    await query.edit_message_text(
        "🎮 *PUBG UC Do'koniga Xush Kelibsiz!*\n\n"
        "Tez va ishonchli UC yetkazib berish xizmati.\n"
        "Quyidagi tugmalardan birini tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ Buyurtma bekor qilindi. /start — Bosh menu")
    return ConversationHandler.END


# === ADMIN: BUYURTMANI TASDIQLASH ===
async def admin_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    args = context.args
    if not args:
        await update.message.reply_text("Foydalanish: /approve ORDER_ID")
        return

    order_id = args[0]
    if order_id not in orders:
        await update.message.reply_text("❌ Buyurtma topilmadi.")
        return

    orders[order_id]["status"] = "✅ Bajarildi"
    user_id = orders[order_id]["user_id"]
    uc = orders[order_id]["uc"]

    await context.bot.send_message(
        chat_id=user_id,
        text=f"🎉 *Tabriklaymiz!*\n\n"
             f"Buyurtma `{order_id}` bajarildi.\n"
             f"💎 *{uc}* hisobingizga o'tkazildi!\n\n"
             f"PUBG ga kiring va UC ni tekshiring. 🎮",
        parse_mode="Markdown"
    )
    await update.message.reply_text(f"✅ {order_id} tasdiqlandi va foydalanuvchiga xabar yuborildi.")


# === MAIN ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(buy_uc, pattern="^buy_uc$")],
        states={
            SELECT_UC: [CallbackQueryHandler(select_uc, pattern="^uc_")],
            ENTER_PLAYER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_player_id)],
            CONFIRM_ORDER: [
                CallbackQueryHandler(confirm_order, pattern="^confirm_order$"),
                CallbackQueryHandler(cancel_order, pattern="^cancel_order$"),
            ],
            WAIT_PAYMENT: [
                MessageHandler(filters.PHOTO | filters.Document.ALL, receive_receipt)
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("approve", admin_approve))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(my_orders, pattern="^my_orders$"))
    app.add_handler(CallbackQueryHandler(support, pattern="^support$"))
    app.add_handler(CallbackQueryHandler(back_main, pattern="^back_main$"))

    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
