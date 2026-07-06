from aiogram import Router
from aiogram.types import Message


router = Router()



@router.message()
async def remove_service_messages(message: Message):

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
