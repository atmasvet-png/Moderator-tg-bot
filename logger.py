from config import LOG_CHAT_ID


async def send_log(bot, text):

    await bot.send_message(
        LOG_CHAT_ID,
        text
    )
