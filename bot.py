import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from pytonapi import AsyncTonapi

API_TOKEN = '7871008510:AAEWx-kAigP8kzS1H2Ga11qhgsLQoIFCT6s'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Ссылка на manifest.json, размещённый на GitHub
MANIFEST_URL = "https://raw.githubusercontent.com/VakuumJava/tonconntestbot/main/manifest.json"
TONAPI_KEY = 'AEI4Z5YW7Q3OFMIAAAALOFGBCP6LCCNC4LKSWFTQKK4HLKOTARHPWSIA4G57OPDKONU4PWQ'  # Вставьте сюда ваш API-ключ от tonapi.io

tonapi = AsyncTonapi(api_key=TONAPI_KEY)

# Словарь для хранения адресов пользователей (лучше использовать БД)
user_wallets = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Для подключения TON-кошелька отправь /connect")

@dp.message(Command("connect"))
async def connect(message: types.Message):
    tonkeeper_web = f"https://app.tonkeeper.com/ton-connect?manifestUrl={MANIFEST_URL}"
    tonconnect_deeplink = f"tonconnect://ton-connect?manifestUrl={MANIFEST_URL}"
    await message.answer(
        (
            "*Подключение кошелька через TonConnect:*\n\n"
            f"[Открыть Tonkeeper Web]({tonkeeper_web})\n\n"
            "Для мобильных кошельков скопируйте или отсканируйте QR-код с этой ссылкой:\n"
            f"`{tonconnect_deeplink}`"
        ),
        parse_mode="Markdown"
    )

@dp.message(lambda m: m.text and m.text.startswith('ton://'))
async def save_wallet(message: types.Message):
    # Здесь должна быть логика парсинга адреса из ton:// ссылки, если потребуется
    await message.answer(f"Кошелек успешно подключен! (ton:// ссылка получена)")

@dp.message(Command("balance"))
async def balance(message: types.Message):
    address = user_wallets.get(message.from_user.id)
    if not address:
        await message.answer("Сначала подключите кошелек через /connect")
        return
    # Получаем информацию о кошельке через tonapi
    info = await tonapi.accounts.get_info(address)
    # Для отладки: печатаем структуру info
    print(f"DEBUG: info = {info}")
    balance = 0
    if hasattr(info, 'balance'):
        bal = info.balance
        if isinstance(bal, (int, float)):
            balance = bal / 1e9
        elif isinstance(bal, dict) and 'coins' in bal:
            balance = int(bal['coins']) / 1e9
    elif isinstance(info, dict) and 'balance' in info:
        balance = int(info['balance']) / 1e9
    await message.answer(f"Ваш баланс: {balance} TON")

@dp.message(Command("deposit"))
async def deposit(message: types.Message):
    address = user_wallets.get(message.from_user.id)
    if not address:
        await message.answer("Сначала подключите кошелек через /connect")
        return
    await message.answer(f"Для пополнения переведите TON на адрес: {address}")

@dp.message(Command("withdraw"))
async def withdraw(message: types.Message):
    address = user_wallets.get(message.from_user.id)
    if not address:
        await message.answer("Сначала подключите кошелек через /connect")
        return
    await message.answer("Введите сумму и адрес для вывода в формате:\n<адрес> <сумма>")

@dp.message(lambda m: m.text and len(m.text.split()) == 2 and m.text.split()[1].replace('.', '', 1).isdigit())
async def process_withdraw(message: types.Message):
    address = user_wallets.get(message.from_user.id)
    if not address:
        await message.answer("Сначала подключите кошелек через /connect")
        return
    to_address, amount = message.text.split()
    # Здесь должна быть логика отправки TON через TonConnect
    await message.answer(f"Запрос на вывод {amount} TON на адрес {to_address} отправлен!")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
