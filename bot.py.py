import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiohttp import web

# Bot tokeningiz va yopiq guruhingiz ID raqamini shu yerga yozing
TOKEN = "8979824672:AAEJZ3CHylCvNcoaUHdOt_mmxfcroVWpQk0"
GROUP_ID = -1003919402335  # Епиқ гуруҳингизнинг ID рақами
WEB_APP_URL = "https://karjabov-baxtiyor.vercel.app"  # Vercel'dagi Mini App havolangiz

bot = Bot(token=TOKEN)
dp = Dispatcher()

# A'zolikni tekshiruvchi funksiya
async def check_membership(user_id: int, bot: Bot) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=GROUP_ID, user_id=user_id)
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            return True
    except Exception:
        pass
    return False

# /start buyrug'i kelganda ishlaydigan funksiya
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    
    is_member = await check_membership(user_id, bot)
    
    if is_member:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📝 Testlarni boshlash", web_app=WebAppInfo(url=WEB_APP_URL))]
            ]
        )
        await message.answer(
            "Xush kelibsiz, Baxtiyor Karjabov Demo testlar portaliga! Testlarni ishlash uchun quyidagi tugmani bosing:",
            reply_markup=keyboard
        )
    else:
        await message.answer(
            "❌ Kechirasiz, siz bizning yopiq guruhimiz a'zosi emassiz.\n\n"
            "Testlarni ishlash uchun avval yopiq guruhimizga qo'shiling!"
        )

# Web Service uchun soxta server (Render bepul ishlashi uchun talab qilinadi)
async def handle(request):
    return web.Response(text="Bot ishlayapti!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    import os
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# Bot va serverni birgalikda ishga tushirish
async def main():
    logging.basicConfig(level=logging.INFO)
    print("Bot va veb-server ishga tushdi...")
    
    # Veb-server va botni bir vaqtning o'zida (fon rejimida) ishga tushiramiz
    await asyncio.gather(
        web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())