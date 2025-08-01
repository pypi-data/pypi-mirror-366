import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Generic, Optional

from typing_extensions import override

import discord
from discord.ext import commands, tasks
from discord.utils import MISSING  # pyright: ignore[reportAny]

from ._lock import AsyncRWLock
from ._types import BotT

_logger = logging.getLogger(__name__)


@dataclass
class CachedInvocation:
    user_message: discord.Message
    bot_response: Optional[discord.Message]
    track_deletion: bool


class EditTrackerCog(commands.Cog, Generic[BotT]):
    """A cog handling automatic edit tracking. When user edits or delete their message,
    the bot will automatically update its response.

    Attributes
    ----------
    bot: Union[`commands.Bot`, `commands.AutoShardedBot`]
        The bot that this cog is being added to.
    max_duration: Optional[`datetime.timedelta`]
        How long to track bot responses for. If set to `None`, bot responses will be
        tracked indefinitely until the process is shut down.
    execute_untracked_edits: `bool`
        Whether to execute a command that was previously untracked, for example, when the
        user makes a typo and edits it into a valid invocation.
    ignore_edits_if_not_yet_responded: `bool`
        Whether to ignore edits on messages that have not been responded to. This happens
        if the edits happens before the command has sent a response, or if the command
        does not respond at all.

    """

    def __init__(
        self,
        bot: BotT,
        *,
        max_duration: Optional[timedelta] = MISSING,
        execute_untracked_edits: bool = True,
        ignore_edits_if_not_yet_responded: bool = False,
    ) -> None:
        self.bot: BotT = bot

        if max_duration is MISSING:
            self.max_duration: Optional[timedelta] = timedelta(minutes=5)
        else:
            self.max_duration = max_duration

        self.execute_untracked_edits: bool = execute_untracked_edits
        self.ignore_edits_if_not_yet_responded: bool = ignore_edits_if_not_yet_responded

        self._cache: dict[int, CachedInvocation] = {}
        self._lock: AsyncRWLock = AsyncRWLock()

    @override
    async def cog_load(self) -> None:
        if (max_duration := self.max_duration) is not None:
            self.purge_cache.change_interval(seconds=max_duration.total_seconds())
            _ = self.purge_cache.start()

    @override
    async def cog_unload(self) -> None:
        self.purge_cache.stop()

    @tasks.loop(name="discord-ext-track-edits-purge-cache")
    async def purge_cache(self):
        """
        Forget all messages that are older than the tracker's `max_duration`.
        The cog will automatically do this periodically.
        """
        if (max_duration := self.max_duration) is None:
            return

        _logger.debug("purging edit tracker cache")

        async with self._lock.write():
            # create a shallow copy of the current cache so we can safely delete
            # items from the actual cache, since modifying a collection while
            # iterating through it in Python gives a RuntimeError
            for user_message_id, invocation in self._cache.copy().items():
                last_updated = (
                    invocation.user_message.edited_at
                    or invocation.user_message.created_at
                )

                if datetime.now(timezone.utc) - last_updated > max_duration:
                    del self._cache[user_message_id]

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        async with self._lock.write():
            invocation = self._cache.get(payload.message_id)

            if invocation is not None:
                if (
                    self.ignore_edits_if_not_yet_responded
                    and invocation.bot_response is None
                ):
                    return

                if payload.data.get("content", MISSING) is MISSING:
                    return

                invocation.user_message = payload.message
            elif (
                # ignore untracked edits if we have not responded to them,
                # or if the original message is too old (to prevent abuse),
                # or if we don't want to execute untracked edits at all
                self.ignore_edits_if_not_yet_responded
                or (
                    self.max_duration is not None
                    and datetime.now(timezone.utc) - payload.message.created_at
                    > self.max_duration
                )
                or not self.execute_untracked_edits
            ):
                return

        ctx = await self.bot.get_context(payload.message)

        if ctx.command is not None and not ctx.command.extras.get("invoke_on_edit", True):
            return

        await self.bot.invoke(ctx)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        async with self._lock.write():
            if (invocation := self._cache.pop(payload.message_id, None)) is None:
                return

            if not invocation.track_deletion or invocation.bot_response is None:
                return

        try:
            await invocation.bot_response.delete()
        except Exception as e:
            _logger.exception("failed to delete bot response", exc_info=e)

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context[BotT]):
        # this should never happen because this event is only dispatched on valid commands
        if ctx.command is None:
            return

        # we need to track whenever commands are running to prevent infinite loops
        # when the command tries to edit its invocation message
        async with self._lock.write():
            if ctx.message.id not in self._cache:
                self._cache[ctx.message.id] = CachedInvocation(
                    ctx.message,
                    None,
                    track_deletion=bool(ctx.command.extras.get("track_deletion", True)),  # pyright: ignore[reportAny]
                )

    async def get_bot_response(self, user_message_id: int):
        """
        Find the corresponding bot respond for a user message ID, if it exists and
        is cached.
        """
        async with self._lock.read():
            if (invocation := self._cache.get(user_message_id)) is None:
                return None

            return invocation.bot_response

    async def set_bot_response(
        self,
        user_message: discord.Message,
        bot_response: discord.Message,
        *,
        track_deletion: bool,
    ):
        """
        Notify the tracker that the given `user_message` should be associated with the
        given `bot_response`. This overwrites any previously associated bot response.
        """
        async with self._lock.write():
            if (invocation := self._cache.get(user_message.id)) is not None:
                invocation.bot_response = bot_response
                invocation.track_deletion = track_deletion
            else:
                self._cache[user_message.id] = CachedInvocation(
                    user_message, bot_response, track_deletion
                )
