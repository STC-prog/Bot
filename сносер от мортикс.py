import logging
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Настройка логирования
logging.basicConfig(level=logging.ERROR)

# Конфигурация бота
TOKEN = "7781461583:AAF5GBghbRH3YnIbBCNWktM011SjDuTkAeQ"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Аккаунты Gmail (App Passwords)
senders = {
    'zlotema12@gmail.com': 'xxie yzkz wdyk ugxm',
    'maybelox231@gmail.com': 'auov fern blju utwf',
    'andeybirum@gmail.com': 'ouho uujv htlm rwaz',
    'faverokstandof@gmail.com': 'nrsg kchi etta uuzh',
    'faveroktt@gmail.com': 'dywo rgle jjwl hhbq',
    'mksmksergeev@gmail.com': 'ycmw rqii rcbd isfd',
    'maksimafanacefish@gmail.com': 'hdpn tbfp acwv jyro'
}

# Получатели жалоб
receivers = ['sms@telegram.org', 'dmca@telegram.org', 'abuse@telegram.org']

# Состояния FSM
class ComplaintState(StatesGroup):
    complaint_type = State()
    username = State()
    telegram_id = State()
    reason = State()
    count = State()

# Клавиатура
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("/complaint"), KeyboardButton("ℹ О проекте"))

# Команды
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("🚀 Бот для жалоб в Telegram. Используй /complaint", reply_markup=keyboard)

@dp.message_handler(commands=["complaint"])
async def complaint(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📌 Через чат", "🚀 Быстрый снос")
    await message.answer("Выберите тип жалобы:", reply_markup=markup)
    await ComplaintState.complaint_type.set()

# Обработчики состояний
@dp.message_handler(state=ComplaintState.complaint_type)
async def process_type(message: types.Message, state: FSMContext):
    if message.text not in ["📌 Через чат", "🚀 Быстрый снос"]:
        return await message.answer("❌ Выберите вариант из клавиатуры!")
    await state.update_data(complaint_type=message.text)
    await message.answer("Введите username нарушителя (без @):")
    await ComplaintState.username.set()

@dp.message_handler(state=ComplaintState.username)
async def process_username(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text.strip())
    await message.answer("Введите Telegram ID:")
    await ComplaintState.telegram_id.set()

@dp.message_handler(state=ComplaintState.telegram_id)
async def process_id(message: types.Message, state: FSMContext):
    await state.update_data(telegram_id=message.text.strip())
    await message.answer("📝 Опишите причину жалобы:")
    await ComplaintState.reason.set()

@dp.message_handler(state=ComplaintState.reason)
async def process_reason(message: types.Message, state: FSMContext):
    await state.update_data(reason=message.text.strip())
    await message.answer("🔢 Введите количество жалоб для отправки:")
    await ComplaintState.count.set()

@dp.message_handler(state=ComplaintState.count)
async def process_count(message: types.Message, state: FSMContext):
    try:
        count = int(message.text)
        if count < 1: raise ValueError
    except:
        return await message.answer("❌ Введите число больше 0!")

    data = await state.get_data()
    complaint_text = f"""
    Жалоба на пользователя:
    👤 Юзернейм: {data['username']}
    🔖 ID: {data['telegram_id']}
    📌 Причина: {data['reason']}
    """

    success = 0
    errors = []
    
    # Отправка писем
    for _ in range(count):
        for email, password in senders.items():
            for receiver in receivers:
                try:
                    result = send_gmail(receiver, email, password, "Жалоба", complaint_text)
                    if "Успешно" in result: success += 1
                except Exception as e:
                    errors.append(str(e))
                if success >= count: break
            if success >= count: break
        if success >= count: break

    await message.answer(f"""
    ✅ Отправлено жалоб: {success}
    ❌ Ошибок: {len(errors)}
    """)
    await state.finish()

# Функция отправки через Gmail
def send_gmail(receiver, sender_email, sender_password, subject, body):
    try:
        # Проверка подключения
        socket.create_connection(("smtp.gmail.com", 587), timeout=5)
        
        # Формирование письма
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Отправка
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver, msg.as_string())
        return "Успешно"
    except Exception as e:
        return f"Ошибка: {str(e)}"

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)