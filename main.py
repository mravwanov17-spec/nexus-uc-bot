import telebot
from telebot import types
from flask import Flask
from threading import Thread

# Tokeningizni shu yerga yozing
TOKEN = '8944341939:AAHyYOgs8Tgbzn1EJunFuvjBue9irIMPTpA'
bot = telebot.TeleBot(TOKEN)
admin_id = "7654914240"

# Botni uyg'oq saqlash (Keep Alive)
app = Flask('')
@app.route('/')
def home():
    return "Bot ishlayapti!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# Mijozlar holatini saqlash
user_states = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("💎 UC Sotib olish"), types.KeyboardButton("ℹ️ Admin"))
    bot.send_message(message.chat.id, "<b>Assalomu alaykum! Nexus UC do'koniga xush kelibsiz!</b> 👋", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def text_handler(message):
    cid = message.chat.id
    if message.text == "💎 UC Sotib olish":
        markup = types.InlineKeyboardMarkup(row_width=2)
        paketlar = [
            ("30 UC", "buy_30"), ("60 UC", "buy_60"),
            ("325 UC", "buy_325"), ("660 UC", "buy_660"),
            ("1900 UC", "buy_1900"), ("3850 UC", "buy_3850")
        ]
        for text, callback in paketlar:
            markup.add(types.InlineKeyboardButton(text, callback_data=callback))
        bot.send_message(cid, "Paketni tanlang:", reply_markup=markup)
    
    elif message.text == "ℹ️ Admin":
        bot.send_message(cid, "Admin bilan bog'lanish: @nexus_admin1")
    
    # ID qabul qilish qismi
    elif cid in user_states and user_states[cid].get('step') == 'waiting_pubg_id':
        pubg_id = message.text
        uc_count = user_states[cid]['uc']
        bot.send_message(admin_id, f"💎 Yangi ID keldi!\n👤 Mijoz: @{message.from_user.username}\n🆔 PUBG ID: `{pubg_id}`\n📦 UC: {uc_count}", parse_mode="HTML")
        bot.send_message(cid, "✅ ID qabul qilindi. Admin tekshirmoqda...")
        user_states[cid]['step'] = None

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def callback_handler(call):
    cid = call.message.chat.id
    uc = call.data.split('_')[1]
    bot.send_message(cid, f"✅ Siz tanlagan: {uc} UC.\n💳 Karta: `9860 1678 0224 9174`\n\nTo'lov qilganingizdan so'ng chekni rasm ko'rinishida yuboring.")
    user_states[cid] = {'step': 'waiting_photo', 'uc': uc}

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    cid = message.chat.id
    if cid in user_states and user_states[cid].get('step') == 'waiting_photo':
        bot.send_message(cid, "✅ Chek qabul qilindi. ID ni yuboring:")
        user_states[cid]['step'] = 'waiting_pubg_id'
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"ok_{cid}"))
        bot.send_photo(admin_id, message.photo[-1].file_id, caption=f"🔔 Yangi chek! Mijoz: @{message.from_user.username}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('ok_'))
def admin_confirm(call):
    mijoz_id = call.data.split('_')[1]
    bot.send_message(mijoz_id, "✅ Chekingiz tasdiqlandi! Endi PUBG ID ni yuboring.")
    bot.edit_message_caption(caption=f"{call.message.caption}\n\n✅ Tasdiqlandi", chat_id=admin_id, message_id=call.message.message_id)

bot.polling(none_stop=True)
