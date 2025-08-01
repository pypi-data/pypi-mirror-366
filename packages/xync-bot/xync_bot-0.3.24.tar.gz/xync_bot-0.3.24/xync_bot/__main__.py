import logging
from asyncio import run

from PGram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import UpdateType
from x_model import init_db

from xync_bot.routers.main.handler import mr
from xync_bot.routers.cond import cr
from xync_bot.routers.pay.handler import pr
from xync_bot.routers import last
from xync_bot.routers.pay.dep import Store

au = [
    UpdateType.MESSAGE,
    UpdateType.CALLBACK_QUERY,
    UpdateType.CHAT_MEMBER,
    UpdateType.MY_CHAT_MEMBER,
]  # , UpdateType.CHAT_JOIN_REQUEST
bot = Bot([cr, pr, mr, last], Store(), au, default=DefaultBotProperties(parse_mode="HTML"))

if __name__ == "__main__":
    from xync_bot.loader import TOKEN, TORM

    logging.basicConfig(level=logging.INFO)

    async def main() -> None:
        cn = await init_db(TORM)
        bot.dp.workflow_data["store"].glob = await Store.Global()  # todo: refact store loading
        await bot.start(
            TOKEN,
            cn,
        )

    run(main())
