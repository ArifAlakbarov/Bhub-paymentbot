import os
from aiogram import Bot, Dispatcher, executor, types

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
PUBLIC_CHANNEL = os.getenv("PUBLIC_CHANNEL", "https://t.me/bbhub18")
PRIVATE_CHANNEL = os.getenv("PRIVATE_CHANNEL", "https://t.me/+6PXbnF9xaNgzMzky")
LEOBANK_CARD = os.getenv("LEOBANK_CARD", "4098584496156348")
KAPITALBANK_CARD = os.getenv("KAPITALBANK_CARD", "5239151747840174")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

users = {}

LANGS = ["az", "ru", "en"]

MESSAGES = {
    "start": {
        "az": f"Salam! Xoş gəlmisiniz.\nPublic kanalımız: {PUBLIC_CHANNEL}\nÖdəniş etmək üçün /pay yazın.",
        "ru": f"Здравствуйте! Добро пожаловать.\nНаш публичный канал: {PUBLIC_CHANNEL}\nДля оплаты напишите /pay.",
        "en": f"Hello! Welcome.\nOur public channel: {PUBLIC_CHANNEL}\nType /pay to get payment info."
    },
    "pay": {
        "az": f"Ödəniş məlumatları:\nLeobank: {LEOBANK_CARD}\nKapitalbank: {KAPITALBANK_CARD}\nÖdəniş qəbzini göndərin.",
        "ru": f"Платежные реквизиты:\nLeobank: {LEOBANK_CARD}\nKapitalbank: {KAPITALBANK_CARD}\nОтправьте чек оплаты.",
        "en": f"Payment details:\nLeobank: {LEOBANK_CARD}\nKapitalbank: {KAPITALBANK_CARD}\nSend your payment receipt."
    },
    "payment_received": {
        "az": "Ödənişiniz qeydə alındı, admin təsdiqini gözləyir.",
        "ru": "Ваш платеж зарегистрирован, ожидается подтверждение администратора.",
        "en": "Your payment has been recorded, awaiting admin confirmation."
    },
    "payment_confirmed": {
        "az": f"Təsdiq edildi! Private kanal linki: {PRIVATE_CHANNEL}",
        "ru": f"Подтверждено! Ссылка на приватный канал: {PRIVATE_CHANNEL}",
        "en": f"Confirmed! Private channel link: {PRIVATE_CHANNEL}"
    },
    "unknown_command": {
        "az": "Naməlum əmrdir.",
        "ru": "Неизвестная команда.",
        "en": "Unknown command."
    },
    "ask_name": {
        "az": "Adınızı daxil edin:",
        "ru": "Введите ваше имя:",
        "en": "Please enter your name:"
    }
}

def get_lang(text: str):
    # Sadə dil seçimi funksiyası, default az
    text = text.lower()
    if text in ["az", "azerbaijani", "azerbaijan"]:
        return "az"
    elif text in ["ru", "russian", "русский"]:
        return "ru"
    elif text in ["en", "english"]:
        return "en"
    return "az"

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    users[message.from_user.id] = {"lang": "az", "step": "ask_name"}
    await message.answer(MESSAGES["ask_name"]["az"])

@dp.message_handler(commands=["pay"])
async def pay_handler(message: types.Message):
    user = users.get(message.from_user.id, {"lang": "az"})
    lang = user.get("lang", "az")
    await message.answer(MESSAGES["pay"][lang])

@dp.message_handler(commands=["tesdiq"])
async def confirm_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("Siz admin deyilsiniz.")
        return
    args = message.get_args()
    if not args.isdigit():
        await message.reply("Zəhmət olmasa təsdiq üçün istifadəçi ID-ni yazın.")
        return
    user_id = int(args)
    try:
        await bot.send_message(user_id, MESSAGES["payment_confirmed"]["az"])
        await message.reply(f"{user_id} istifadəçisinə private kanal linki göndərildi.")
    except Exception as e:
        await message.reply(f"Xəta baş verdi: {e}")

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def photo_handler(message: types.Message):
    # Ödəniş çeki kimi şəkil qəbul edilir
    user_id = message.from_user.id
    await message.answer(MESSAGES["payment_received"]["az"])

    # Adminə şəkil və info göndər
    caption = f"Ödəniş çəkisi göndərildi.\nUsername: @{message.from_user.username}\nID: {user_id}"
    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption)

@dp.message_handler()
async def text_handler(message: types.Message):
    user = users.get(message.from_user.id, {"lang": "az"})
    if user.get("step") == "ask_name":
        name = message.text.strip()
        users[message.from_user.id]["name"] = name
        users[message.from_user.id]["step"] = None
        lang = get_lang(name)  # sadəcə nümunə üçün dil seçimi burada edilə bilər
        users[message.from_user.id]["lang"] = lang
        await message.answer(MESSAGES["start"][lang])
    else:
        await message.answer(MESSAGES["unknown_command"][user.get("lang", "az")])

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
