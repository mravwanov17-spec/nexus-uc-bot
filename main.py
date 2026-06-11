import telebot
from telebot import types

TOKEN = '8944341939:AAHyYOgs8Tgbzn1EJunFuvjBue9irIMPTpA'
bot = telebot.TeleBot(TOKEN)
admin_id = "7654914240"

user_states = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("💎 UC Sotib olish"), types.KeyboardButton("ℹ️ Admin"))
    welcome_text = "<b>Assalomu alaykum! Nexus UC do'koniga xush kelibsiz!</b> 👋"
    bot.send_message(message.chat.id, welcome_text, parse_mode="HTML", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def text_handler(message):
    cid = message.chat.id
    if message.text == "💎 UC Sotib olish":
        markup = types.InlineKeyboardMarkup(row_width=2)
        paketlar = [
            ("60 UC - 12 000 so'm", "buy_60"), ("120 UC - 26 000 so'm", "buy_120"),
            ("180 UC - 39 000 so'm", "buy_180"), ("325 UC - 60 000 so'm", "buy_325"),
            ("385 UC - 73 000 so'm", "buy_385"), ("445 UC - 86 000 so'm", "buy_445"),
            ("660 UC - 117 000 so'm", "buy_660"), ("720 UC - 130 000 so'm", "buy_720"),
            ("780 UC - 143 000 so'm", "buy_780"), ("985 UC - 177 000 so'm", "buy_985"),
            ("1320 UC - 234 000 so'm", "buy_1320"), ("1800 UC - 300 000 so'm", "buy_1800")
        ]
        for text, callback in paketlar:
            markup.add(types.InlineKeyboardButton(text, callback_data=callback))
        bot.send_message(cid, "Paketni tanlang:", reply_markup=markup)
    elif message.text == "ℹ️ Admin":
        bot.send_message(cid, "Admin: @nexus_admin1")

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def callback_handler(call):
    cid = call.message.chat.id
    uc = call.data.split('_')[1]
    narxlar = {"60": "12 000", "120": "26 000", "180": "39 000", "325": "60 000", "385": "73 000", "445": "86 000", "660": "117 000", "720": "130 000", "780": "143 000", "985": "177 000", "1320": "234 000", "1800": "300 000"}
    
    bot.send_message(cid, f"✅ {uc} UC tanladingiz.\n\n💳 Karta: `9860 1678 0224 9174`\n👤 ISM: U/M\n\nChek yuboring.")
    user_states[cid] = {'step': 'waiting_photo', 'uc': uc, 'narx': narxlar.get(uc)}

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    cid = message.chat.id
    if cid in user_states and user_states[cid]['step'] == 'waiting_photo':
        bot.send_message(cid, "✅ Chekingiz adminga yuborildi.")
        caption = f"🔔 Yangi buyurtma!\n👤 User: @{message.from_user.username}\n🆔 ID: `{cid}`\n💎 UC: {user_states[cid]['uc']}\n💰 Narx: {user_states[cid]['narx']}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_{cid}"))
        bot.send_photo(admin_id, message.photo[-1].file_id, caption=caption, reply_markup=markup)
        user_states[cid]['step'] = 'waiting_admin_check'

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_'))
def approve_handler(call):
    mijoz_id = call.data.split('_')[1]
    bot.send_message(mijoz_id, "✅ Chekingiz tasdiqlandi! PUBG ID yuboring.")
    bot.answer_callback_query(call.id, "Mijozga xabar ketdi.")

bot.polling(none_stop=True)
