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
    bot.send_message(message.chat.id, "<b>Assalomu alaykum! Nexus UC do'koniga xush kelibsiz!</b> 👋", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def text_handler(message):
    cid = message.chat.id
    if message.text == "💎 UC Sotib olish":
        markup = types.InlineKeyboardMarkup(row_width=2)
        # Yangilangan paketlar narxlari
        paketlar = [
            ("30 UC - 6 500 so'm", "buy_30"), 
            ("60 UC - 12 500 so'm", "buy_60"),
            ("325 UC - 60 000 so'm", "buy_325"), 
            ("660 UC - 117 000 so'm", "buy_660"),
            ("1900 UC - 290 000 so'm", "buy_1900"),
            ("3850 UC - 580 000 so'm", "buy_3850")
        ]
        for text, callback in paketlar:
            markup.add(types.InlineKeyboardButton(text, callback_data=callback))
        bot.send_message(cid, "Paketni tanlang:", reply_markup=markup)
    
    elif message.text == "ℹ️ Admin":
        bot.send_message(cid, "Admin bilan bog'lanish: @nexus_admin1")
    
    # ID qabul qilish
    elif cid in user_states and user_states[cid].get('step') == 'waiting_pubg_id':
        pubg_id = message.text
        user_states[cid]['step'] = 'waiting_admin_done'
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ UC tashlandi", callback_data=f"done_{cid}"))
        markup.add(types.InlineKeyboardButton("❌ Bekor qilish", callback_data=f"fake_{cid}"))
        
        caption = f"💎 Yangi ID keldi!\n👤 Mijoz: @{message.from_user.username}\nPUBG ID: `{pubg_id}`\nUC: {user_states[cid]['uc']}"
        bot.send_message(admin_id, caption, parse_mode="HTML", reply_markup=markup)
        bot.send_message(cid, "⏳ ID qabul qilindi. Admin UC tashlashini kuting.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def callback_handler(call):
    cid = call.message.chat.id
    uc = call.data.split('_')[1]
    bot.send_message(cid, f"✅ Siz tanlagan paket: {uc} UC.\n💳 Karta: `9860 1678 0224 9174`\n👤 ISM: U/M\n\nChek yuboring.")
    user_states[cid] = {'step': 'waiting_photo', 'uc': uc}

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    cid = message.chat.id
    if cid in user_states and user_states[cid].get('step') == 'waiting_photo':
        bot.send_message(cid, "✅ Chekingiz adminga yuborildi. 10 sekund ichida tekshiriladi.")
        caption = f"🔔 Yangi buyurtma!\n👤 User: @{message.from_user.username}\n🆔 ID: `{cid}`\n💎 UC: {user_states[cid]['uc']}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"ok_{cid}"))
        markup.add(types.InlineKeyboardButton("❌ Feyk", callback_data=f"fake_{cid}"))
        bot.send_photo(admin_id, message.photo[-1].file_id, caption=caption, reply_markup=markup)
        user_states[cid]['step'] = 'waiting_admin_check'

@bot.callback_query_handler(func=lambda call: call.data.startswith(('ok_', 'fake_')))
def admin_decision(call):
    action, mijoz_id = call.data.split('_')
    mijoz_id = int(mijoz_id)
    if action == 'ok':
        bot.send_message(mijoz_id, "✅ Chekingiz tasdiqlandi! PUBG ID raqamingizni yuboring.")
        user_states[mijoz_id]['step'] = 'waiting_pubg_id'
        bot.edit_message_caption(caption=f"{call.message.caption}\n\nStatus: TASDIQLANDI", chat_id=admin_id, message_id=call.message.message_id)
    elif action == 'fake':
        bot.send_message(mijoz_id, "❌ Chekingiz feyk deb topildi!")
        bot.edit_message_caption(caption=f"{call.message.caption}\n\nStatus: FEYK", chat_id=admin_id, message_id=call.message.message_id)
        user_states[mijoz_id]['step'] = 'finished'

@bot.callback_query_handler(func=lambda call: call.data.startswith(('done_', 'fake_')))
def final_decision(call):
    action, mijoz_id = call.data.split('_')
    mijoz_id = int(mijoz_id)
    if action == 'done':
        bot.send_message(mijoz_id, "✅ Buyurtmangiz bajarildi! UC hisobingizga tushdi.")
        bot.edit_message_text(text=f"{call.message.text}\n\n✅ Holat: BAJARILDI", chat_id=admin_id, message_id=call.message.message_id)
    elif action == 'fake':
        bot.send_message(mijoz_id, "❌ Buyurtmangiz bekor qilindi.")
        bot.edit_message_text(text=f"{call.message.text}\n\n❌ Holat: BEKOR QILINDI", chat_id=admin_id, message_id=call.message.message_id)

bot.polling(none_stop=True)
