# main.py

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from config import BOT_TOKEN, ADMIN_ID

from database import (
    init_db,
    add_warning,
    get_warnings,
    clear_warnings
)

from filters import (
    contains_bad_words,
    has_link
)

from antiflood import check_flood
from logger import send_log



bot = Bot(
    token=BOT_TOKEN
)

dp = Dispatcher()



# =========================
# Удаление системных сообщений
# =========================

@dp.message()
async def delete_service_messages(message: Message):

    if message.new_chat_members:
        await message.delete()
        return


    if message.left_chat_member:
        await message.delete()
        return


    if message.new_chat_photo:
        await message.delete()
        return


    if message.delete_chat_photo:
        await message.delete()
        return


    if message.new_chat_title:
        await message.delete()
        return


    if message.pinned_message:
        await message.delete()
        return



# =========================
# Главная модерация
# =========================

@dp.message()
async def moderation(message: Message):


    if message.from_user.is_bot:
        return


    user_id = message.from_user.id

    text = message.text



    # ---- Антифлуд ----

    if check_flood(user_id):

        await message.delete()


        await message.chat.restrict(
            user_id=user_id,
            permissions={
                "can_send_messages": False
            },
            until_date=300
        )


        await send_log(
            bot,
            f"🚨 Антифлуд\n"
            f"Пользователь: {message.from_user.full_name}\n"
            f"ID: {user_id}\n"
            f"Мут: 5 минут"
        )

        return



    # ---- Запрещённые ссылки ----

    if has_link(text):

        await message.delete()


        await send_log(
            bot,
            f"🔗 Удалена ссылка\n"
            f"Пользователь: {message.from_user.full_name}"
        )

        return



    # ---- Запрещённые слова ----

    if contains_bad_words(text):

        await message.delete()


        await add_warning(user_id)


        warns = await get_warnings(user_id)



        await message.answer(
            f"⚠️ Нарушение!\n"
            f"Пользователь: {message.from_user.full_name}\n"
            f"Предупреждение {warns}/3"
        )


        await send_log(
            bot,
            f"⚠️ Нарушение\n"
            f"Пользователь: {message.from_user.full_name}\n"
            f"Предупреждений: {warns}"
        )



        if warns >= 3:

            await message.chat.ban(
                user_id=user_id
            )


            await message.answer(
                "🚫 Пользователь заблокирован"
            )


            await send_log(
                bot,
                f"🚫 Бан\n"
                f"{message.from_user.full_name}"
            )


        return





# =========================
# Бан командой
# =========================

@dp.message(Command("ban"))
async def ban_command(message: Message):


    if message.from_user.id != ADMIN_ID:
        return



    if not message.reply_to_message:

        await message.answer(
            "Используй команду ответом на сообщение"
        )

        return



    user_id = message.reply_to_message.from_user.id


    await message.chat.ban(
        user_id=user_id
    )


    await message.answer(
        "🚫 Пользователь заблокирован"
    )


    await send_log(
        bot,
        f"🚫 Ручной бан\n"
        f"Админ: {message.from_user.full_name}\n"
        f"Пользователь ID: {user_id}"
    )





# =========================
# Очистить предупреждения
# =========================

@dp.message(Command("clearwarn"))
async def clear_warn(message: Message):


    if message.from_user.id != ADMIN_ID:
        return



    if not message.reply_to_message:

        await message.answer(
            "Ответь на сообщение пользователя"
        )

        return



    user_id = message.reply_to_message.from_user.id


    await clear_warnings(user_id)


    await message.answer(
        "✅ Предупреждения очищены"
    )



# =========================
# Запуск
# =========================

async def main():

    await init_db()


    print(
        "🤖 Moderator bot started"
    )


    await dp.start_polling(bot)




if __name__ == "__main__":

    asyncio.run(main())
