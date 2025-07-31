from asyncio import run
from PGram import Bot
from loader import TOKEN
from example.router import r

""" Basic example """
bot = Bot([r])
run(bot.start(TOKEN))
