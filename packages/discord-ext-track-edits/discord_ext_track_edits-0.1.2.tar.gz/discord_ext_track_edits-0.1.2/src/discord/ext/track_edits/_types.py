from typing import TypeVar, Union

from discord.ext import commands

BotT = TypeVar("BotT", bound=Union[commands.Bot, commands.AutoShardedBot], covariant=True)
