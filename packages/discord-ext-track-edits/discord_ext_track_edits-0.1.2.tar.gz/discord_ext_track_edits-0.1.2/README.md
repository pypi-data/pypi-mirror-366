# discord-ext-track-edits

A [discord.py](https://github.com/Rapptz/discord.py) extension that implements
edit tracking for prefix commands, inspired by [poise](https://github.com/serenity-rs/poise):
- When user edits their message, automatically update bot response
- When user deletes their message, automatically delete corresponding
bot response, if it exists.

## Usage

The extension contains an `EditTrackerCog` and an `EditTrackableContext`. They must
be used together for edit tracking to work.

Responses will be tracked only when you explicitly `.reply()` to the invocation message.

```python
from datetime import timedelta
from typing import Type, Union
from typing_extensions import override

import discord
from discord.ext import commands
from discord.ext.track_edits import EditTrackerCog, EditTrackableContext

class Bot(commands.Bot):
    async def setup_hook(self) -> None:
        await self.add_cog(
            EditTrackerCog(
                self,
                max_duration=timedelta(minutes=5),
                execute_untracked_edits=True,
                ignore_edits_if_not_yet_responded=False,
            ),
        )

    @override
    async def get_context(
        self,
        origin: Union[discord.Message, discord.Interaction],
        *,
        cls: Type[EditTrackableContext] = EditTrackableContext,
    ) -> EditTrackableContext:
        return await super().get_context(origin, cls=cls)

# your usual bot setup code here
```

## Cog options
- `max_duration`: How long to track bot responses for. If set to `None`, bot
responses will be tracked indefinitely until the process is shut down.
(default: 5 minutes)
- `execute_untracked_edits`: Whether to execute a command that was previously
untracked, for example, when the user makes a typo and edits it into a valid
invocation. (default: `True`)
- `ignore_edits_if_not_yet_responded`: Whether to ignore edits on messages
that have not been responded to. This happens if the edits happens before the
command has sent a response, or if the command does not respond at all.
(default: `False`)

## Command options
Command options are supplied through the `extras` dictionary:

```python
@commands.command(extras={"invoke_on_edit": False})
async def cmd(ctx):
    ...
```

- `invoke_on_edit`: Whether to rerun the command if an existing invocation
message is edited (default: `True`)
- `track_deletion`: Whether to delete the bot response if an existing invocation
message is deleted (default: `True`)
- `reuse_response`: Whether to post subsequent responses as edits to the original
response (default: `True`)
