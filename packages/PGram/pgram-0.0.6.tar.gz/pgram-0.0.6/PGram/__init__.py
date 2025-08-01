from aiogram import Bot as BaseBot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.base import BaseSession
from aiogram.enums import UpdateType
from tortoise.backends.asyncpg import AsyncpgDBClient


class Bot:
    dp: Dispatcher
    store: object
    cn: AsyncpgDBClient
    bot: BaseBot
    au: list[UpdateType] = [
        UpdateType.MESSAGE,
        UpdateType.EDITED_MESSAGE,
        UpdateType.CHANNEL_POST,
        UpdateType.EDITED_CHANNEL_POST,
        UpdateType.BUSINESS_CONNECTION,
        UpdateType.BUSINESS_MESSAGE,
        UpdateType.EDITED_BUSINESS_MESSAGE,
        UpdateType.DELETED_BUSINESS_MESSAGES,
        UpdateType.MESSAGE_REACTION,
        UpdateType.MESSAGE_REACTION_COUNT,
        UpdateType.INLINE_QUERY,
        UpdateType.CHOSEN_INLINE_RESULT,
        UpdateType.CALLBACK_QUERY,
        UpdateType.SHIPPING_QUERY,
        UpdateType.PRE_CHECKOUT_QUERY,
        UpdateType.PURCHASED_PAID_MEDIA,
        UpdateType.POLL,
        UpdateType.POLL_ANSWER,
        UpdateType.MY_CHAT_MEMBER,
        UpdateType.CHAT_MEMBER,
        UpdateType.CHAT_JOIN_REQUEST,
        UpdateType.CHAT_BOOST,
        UpdateType.REMOVED_CHAT_BOOST,
    ]

    def __init__(
        self,
        routers: list[Router] = None,
        store: object = None,
        au: list[UpdateType] = None,
        default: DefaultBotProperties = None,
    ) -> None:
        self.store = store
        self.dp = Dispatcher(name="disp", store=store)
        self.dp.include_routers(*routers)
        self.dp.shutdown.register(self.stop)
        if au:
            self.au = au
        self.default = default

    async def start(
        self,
        token: str,
        cn: AsyncpgDBClient = None,
        wh_host: str = None,
        # app_host: str = None,  # todo: app
        session: BaseSession = None,
    ):
        self.cn = cn
        # self.app_host = app_host
        self.bot = BaseBot(token, session, self.default)
        webhook_info = await self.bot.get_webhook_info()
        if not wh_host:
            """ START POLLING """
            if webhook_info.url:
                await self.bot.delete_webhook(True)
            await self.dp.start_polling(self.bot, polling_timeout=300, allowed_updates=self.au)
        elif (wh_url := wh_host + "/public/wh") != webhook_info.url:
            """ WEBHOOK SETUP """
            await self.bot.set_webhook(
                url=wh_url,
                drop_pending_updates=True,
                allowed_updates=self.au,
                secret_token=self.bot.token.split(":")[1],
                request_timeout=300,
            )
        return self

    async def stop(self) -> None:
        """CLOSE BOT SESSION"""
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.bot.session.close()
