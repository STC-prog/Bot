from telebot import TeleBot, types

API_TOKEN = '7768303949:AAFUHHzGfJAwnKGVfeuuxhlZ6ZX6wWn514I'
ADMIN_ID = 1903849541
bot = TeleBot(API_TOKEN)

pending_responses = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Здравствуйте! Отправьте ваш вопрос, и администратор ответит вам в ближайшее время.")

@bot.message_handler(func=lambda message: message.chat.id != ADMIN_ID)
def forward_to_admin(message):
    user_id = message.chat.id
    text = message.text
    markup = types.InlineKeyboardMarkup()
    reply_button = types.InlineKeyboardButton("Ответить", callback_data=f"reply_{user_id}")
    markup.add(reply_button)
    bot.send_message(ADMIN_ID, f"Сообщение от пользователя {user_id}: {text}", reply_markup=markup)
    bot.send_message(user_id, "Ваше сообщение отправлено администратору.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def ask_for_reply(call):
    user_id = call.data.split("_")[1]
    pending_responses[call.from_user.id] = user_id
    bot.send_message(call.from_user.id, "Введите ответ на сообщение пользователя:")

@bot.message_handler(func=lambda message: message.from_user.id in pending_responses)
def send_reply_to_user(message):
    user_id = pending_responses.pop(message.from_user.id)
    reply_text = message.text
    bot.send_message(user_id, f"Ответ от администратора: {reply_text}")
    bot.send_message(message.from_user.id, "Ответ отправлен пользователю.")

bot.polling()