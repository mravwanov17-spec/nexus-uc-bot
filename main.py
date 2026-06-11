import telebot
from telebot import types
from flask import Flask
from threading import Thread

# 1. TOKEN va ADMIN ID ni bu yerga yozing
TOKEN = '8944341939:AAGb_gskjlHjYcrkULJmJg3TzPrVATYmFMc'
ADMIN_ID = 7654914240 

bot = telebot.TeleBot(TOKEN)
user_states = {} 

# Render uchun server (bot o'chib qolmasligi uchun)
app = Flask('')
@app.route('/')
def home():
    return "Bot ishlayapti!"
def run():
    app.run(host='0.0.0.0', port=8080)
Thread(target=run).start()

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("💎 UC Sotib olish"), types.KeyboardButton("ℹ️ Admin"))
    bot.send_message(message.chat.id, "Salom! NEXUS UC do'koniga xush kelibsiz.", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def text_handler(message):
    cid = message.chat.id
    if message.text == "💎 UC Sotib olish":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("60 UC - 15 000 so'm", callback_data="buy_60"))
        bot.send_message(cid, "Paketni tanlang:", reply_markup=markup)
    
    elif message.text == "ℹ️ Admin":
        bot.send_message(cid, "Admin: @nexus_admin1")

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def callback_handler(call):
    cid = call.message.chat.id
    uc = call.data.split('_')[1]
    
    # Karta raqamingizni shu yerga yozing
    bot.send_message(cid, f"✅ Siz {uc} UC tanladingiz.\n\n💳 Karta: `8600 1234 5678 9012`\n\nIltimos, pulni tashlang va **chekingizni rasm ko'rinishida yuboring.**")
    user_states[cid] = {'step': 'waiting_photo', 'uc': uc}

@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    cid = message.chat.id
    if cid in user_states and user_states[cid]['step'] == 'waiting_photo':
        bot.send_message(cid, "✅ Chekingiz qabul qilindi. Endi PUBG ID raqamingizni yozib yuboring:")
        user_states[cid]['step'] = 'waiting_id'
        user_states[cid]['photo'] = message.photo[-1].file_id

@bot.message_handler(content_types=['text'])
def id_handler(message):
    cid = message.chat.id
    if cid in user_states and user_states[cid]['step'] == 'waiting_id':
        uc = user_states[cid]['uc']
        photo = user_states[cid]['photo']
        pubg_id = message.text
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"ok_{cid}"))
        
        bot.send_photo(ADMIN_ID, photo, caption=f"🚨 YANGI BUYURTMA!\n📦 Paket: {uc} UC\n🆔 ID: {pubg_id}\n👤 Mijoz: @{message.from_user.username}", reply_markup=markup)
        bot.send_message(cid, "✅ Ma'lumotlaringiz adminga yuborildi. Kuting...")
        del user_states[cid]

@bot.callback_query_handler(func=lambda call: call.data.startswith('ok_'))
def admin_confirm(call):
    uid = int(call.data.split('_')[1])
    bot.send_message(uid, "✅ Admin to'lovingizni tasdiqladi! UC tez orada tushadi.")
    bot.edit_message_caption(caption="✅ Tasdiqlandi", chat_id=call.message.chat.id, message_id=call.message.message_id)

bot.infinity_polling()
