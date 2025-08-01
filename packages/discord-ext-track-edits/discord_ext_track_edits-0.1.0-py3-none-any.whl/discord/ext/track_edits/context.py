# pyright: reportAny=false, reportExplicitAny=false
from typing import Any, Generic, Optional

from typing_extensions import override

import discord
from discord.ext import commands
from discord.utils import MISSING

from ._types import BotT
from .cog import EditTrackerCog


class EditTrackableContext(Generic[BotT], commands.Context[BotT]):
    @override
    async def reply(
        self,
        content: Optional[str] = None,
        **kwargs: Any,
    ) -> discord.Message:
        # edit tracking doesn't make sense for slash commands since the invocation can
        # never change
        if self.interaction is not None or self.command is None:
            return await super().reply(content, **kwargs)

        edit_tracker = self.bot.get_cog("EditTrackerCog")

        if isinstance(edit_tracker, EditTrackerCog) and self.command.extras.get(
            "reuse_response", True
        ):
            existing_response = await edit_tracker.get_bot_response(self.message.id)
        else:
            existing_response = None

        if existing_response is not None:
            file = kwargs.get("file", MISSING)
            files = kwargs.get("files", MISSING)
            embed = kwargs.get("embed", MISSING)
            embeds = kwargs.get("embeds", MISSING)
            mention_author = kwargs.get("mention_author")
            allowed_mentions = kwargs.get("allowed_mentions")

            if file is not MISSING and files is not MISSING:
                raise TypeError("Cannot mix file and files keyword arguments.")
            if embed is not MISSING and embeds is not MISSING:
                raise TypeError("Cannot mix embed and embeds keyword arguments.")

            # We want to act as if the reply is brand new, hence all of these different
            # defaults; if we set attachments to MISSING when no files are specified,
            # the attachments from the previous message are persisted.
            if files is not MISSING:
                attachments = files
            elif file is not MISSING:
                attachments = [file]
            else:
                attachments = []

            # same idea here; if we set embeds to MISSING the embeds from the old message
            # will be preserved.
            # if embed is not MISSING else if embeds is *also* MISSING
            # since we already checked that embed/embeds cannot both be existing
            if embed is not MISSING:
                embeds = [embed]
            elif embeds is MISSING:
                embeds = []

            if mention_author is not None:
                if allowed_mentions is None:
                    allowed_mentions = discord.AllowedMentions()

                allowed_mentions.replied_user = mention_author

            bot_response = await existing_response.edit(
                content=content or "",
                embeds=embeds,
                attachments=attachments,
                suppress=kwargs.get("suppress_embeds", False),
                delete_after=kwargs.get("delete_after"),
                allowed_mentions=allowed_mentions,
                view=kwargs.get("view"),
            )
        else:
            bot_response = await super().reply(content, **kwargs)

        if isinstance(edit_tracker, EditTrackerCog):
            await edit_tracker.set_bot_response(
                self.message,
                bot_response,
                track_deletion=self.command.extras.get("track_deletion", True),
            )

        return bot_response
