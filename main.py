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
# Удаление служебных сообщений
# =========================

@dp.message()
async def delete_service_messages(message: Message):

    if (
        message.new_chat_members
        or message.left_chat_member
        or message.new_chat_photo
        or message.delete_chat_photo
        or message.new_chat_title
        or message.pinned_message
    ):

        await message.delete()
        return



# =========================
# Модерация сообщений
# =========================

@dp.message()
async def moderation(message: Message):

    if message.from_user.is_bot:
        return


    user_id = message.from_user.id
    text = message.text



    # Антифлуд

    if check_flood(user_id):

        await message.delete()


        await message.chat.restrict(
            user_id=user_id,
            permissions={
                "can_send_messages": False
            },
            until_date=600
        )


        await send_log(
            bot,
            f"🚨 Флуд\n"
            f"{message.from_user.full_name}\n"
            f"Мут 10 минут"
        )

        return



    # Ссылки

    if has_link(text):

        await message.delete()


        await send_log(
            bot,
            f"🔗 Удалена ссылка\n"
            f"{message.from_user.full_name}"
        )

        return



    # Запрещённые слова

    if contains_bad_words(text):

        await message.delete()


        await add_warning(user_id)

        warns = await get_warnings(user_id)


        await message.answer(
            f"⚠️ Нарушение\n"
            f"{message.from_user.full_name}\n"
            f"Предупреждение {warns}/3"
        )


        await send_log(
            bot,
            f"⚠️ Нарушение\n"
            f"{message.from_user.full_name}\n"
            f"Варнов: {warns}"
        )


        if warns >= 3:

            await message.chat.ban(
                user_id=user_id
            )


            await message.answer(
                "🚫 Пользователь заблокирован"
            )


        return




# =========================
# Бан
# =========================

@dp.message(Command("ban"))
async def ban_user(message: Message):

    if message.from_user.id != ADMIN_ID:
        return


    if not message.reply_to_message:

        await message.answer(
            "Ответь на сообщение пользователя"
        )

        return


    user_id = message.reply_to_message.from_user.id


    await message.chat.ban(
        user_id=user_id
    )


    await message.answer(
        "🚫 Пользователь заблокирован"
    )



# =========================
# Мут
# =========================

@dp.message(Command("mute"))
async def mute_user(message: Message):

    if message.from_user.id != ADMIN_ID:
        return


    if not message.reply_to_message:

        await message.answer(
            "Ответь на сообщение пользователя"
        )

        return



    user_id = message.reply_to_message.from_user.id


    await message.chat.restrict(
        user_id=user_id,
        permissions={
            "can_send_messages": False
        },
        until_date=600
    )


    await message.answer(
        "🔇 Мут 10 минут"
    )



# =========================
# Размут
# =========================

@dp.message(Command("unmute"))
async def unmute_user(message: Message):

    if message.from_user.id != ADMIN_ID:
        return


    if not message.reply_to_message:

        await message.answer(
            "Ответь на сообщение пользователя"
        )

        return



    user_id = message.reply_to_message.from_user.id


    await message.chat.restrict(
        user_id=user_id,
        permissions={
            "can_send_messages": True,
            "can_send_media_messages": True,
            "can_send_other_messages": True,
            "can_add_web_page_previews": True
        }
    )


    await message.answer(
        "🔊 Мут снят"
    )



# =========================
# Очистка предупреждений
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

    print("🤖 Moderator bot started")

    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())
