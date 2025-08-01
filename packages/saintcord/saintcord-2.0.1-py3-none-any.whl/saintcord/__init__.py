import asyncio
import discord
import time
import os
from discord.ext import commands
from discord.gateway import DiscordWebSocket

cooldown_messages = {}
message_timestamps = {}
group_cooldowns = {}
cooldown_store = {}

GLOBAL_COOLDOWN_MESSAGES = {
    "user": "{}: you are on cooldown, ends",
    "guild": "{}: this command is on cooldown, ends"
}

def group_cool(bucket_type, tries, seconds):
    def decorator(func):
        active_messages = {}
        async def wrapper(ctx, *args, **kwargs):
            key = f"{ctx.command.name}:{ctx.author.id if bucket_type == 'user' else ctx.guild.id if ctx.guild else ctx.author.id}"
            current_time = time.time()
            if key in group_cooldowns:
                elapsed = current_time - group_cooldowns[key]
                if elapsed < seconds:
                    if key not in active_messages:
                        cooldown_end = group_cooldowns[key] + seconds + 1
                        msg_template = GLOBAL_COOLDOWN_MESSAGES["guild"] if bucket_type == "guild" else GLOBAL_COOLDOWN_MESSAGES["user"]
                        embed = discord.Embed(description=f"> <:clock:1355214741374767114> {msg_template.format(ctx.author.mention)} <t:{int(cooldown_end)}:R>", color=0x2F3136)
                        cooldown_message = await ctx.send(embed=embed)
                        active_messages[key] = cooldown_message
                        await asyncio.sleep(2)
                        try:
                            await cooldown_message.delete()
                            del active_messages[key]
                        except discord.NotFound:
                            pass
                    return
            group_cooldowns[key] = current_time
            return await func(ctx, *args, **kwargs)
        return wrapper
    return decorator

def cool(bucket_type, tries, seconds, ignore=None, custom_messages=None):
    def decorator(func):
        active_messages = {}
        async def wrapper(ctx, *args, **kwargs):
            key = ctx.author.id if bucket_type == "user" else ctx.guild.id if ctx.guild else ctx.author.id
            command_key = f"{key}_{ctx.command.name}"
            if ignore and callable(ignore) and ignore(ctx):
                return await func(ctx, *args, **kwargs)
            current_time = time.time()
            if command_key in cooldown_store:
                elapsed_time = current_time - cooldown_store[command_key]['timestamp']
                if elapsed_time < seconds:
                    if command_key not in active_messages:
                        retry_after = seconds - elapsed_time
                        messages = custom_messages or GLOBAL_COOLDOWN_MESSAGES
                        msg_template = messages["guild"] if bucket_type == "guild" else messages["user"]
                        cooldown_end = cooldown_store[command_key]['timestamp'] + seconds + 1
                        embed = discord.Embed(description=f"> <:clock:1355214741374767114> {msg_template.format(ctx.author.mention)} <t:{int(cooldown_end)}:R>", color=0x2F3136)
                        cooldown_message = await ctx.send(embed=embed)
                        active_messages[command_key] = cooldown_message
                        await asyncio.sleep(2)
                        try:
                            await cooldown_message.delete()
                            del active_messages[command_key]
                        except discord.NotFound:
                            pass
                    return
                else:
                    del cooldown_store[command_key]
            result = await func(ctx, *args, **kwargs)
            cooldown_store[command_key] = {'timestamp': current_time}
            return result
        return wrapper
    return decorator

async def mobile_identify(self):
    payload = {
        "op": self.IDENTIFY,
        "d": {
            "token": self.token,
            "properties": {
                "$os": "Discord iOS",
                "$browser": "Discord iOS",
                "$device": "iOS",
                "$referrer": "",
                "$referring_domain": "",
            },
            "compress": True,
            "large_threshold": 250,
        },
    }
    if self.shard_id is not None and self.shard_count is not None:
        payload["d"]["shard"] = [self.shard_id, self.shard_count]
    state = self._connection
    if state._intents is not None:
        payload["d"]["intents"] = state._intents.value
    await self.call_hooks("before_identify", self.shard_id, initial=self._initial_identify)
    await self.send_as_json(payload)

DiscordWebSocket.identify = mobile_identify

class BucketType:
    user = "user"
    guild = "guild"

class Cooldown:
    def __init__(self, rate, per, type):
        self.rate = rate
        self.per = per
        self.type = type

class CommandOnCooldown(Exception):
    def __init__(self, retry_after, cooldown):
        self.retry_after = retry_after
        self.cooldown = cooldown

class Saint(commands.Bot):
    def __init__(self, prefix=",", blacklist=None):
        self.blacklist = blacklist
        self.processed_edits = {}
        intents = discord.Intents.all()
        super().__init__(command_prefix=prefix, intents=intents, case_insensitive=True, help_command=None)
        self.add_listener(self.on_command_error, 'on_command_error')
        self.add_listener(self.on_message_edit, 'on_message_edit')
    async def on_message_edit(self, before, after):
        if before.content == after.content:
            return
        if (after.edited_at.timestamp() - before.created_at.timestamp()) > 30:
            return
        edit_key = f"{after.channel.id}_{after.id}"
        if edit_key in self.processed_edits:
            return
        try:
            self.processed_edits[edit_key] = time.time()
            asyncio.create_task(self._clear_processed_edit(edit_key, 60))
            ctx = await self.get_context(after)
            if ctx.valid and ctx.command:
                await ctx.reinvoke()
        except Exception as e:
            print(f"Error processing edited message: {e}")
    async def _clear_processed_edit(self, key, delay):
        await asyncio.sleep(delay)
        if key in self.processed_edits:
            del self.processed_edits[key]
    async def on_ready(self):
        print(f"Bot is ready as {self.user}")
        await self.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name="🔗 discord.gg/saint"))
    async def process_commands(self, message):
        if self.blacklist and await self.blacklist(message.author):
            return
        await super().process_commands(message)
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            retry_after = error.retry_after
            embed = discord.Embed(description=f"> <:clock:1355214741374767114> {ctx.author.mention}: this command", color=0xFF0000)
            await ctx.send(embed=embed)
    def cmd(self, **kwargs):
        def decorator(func):
            cooldown = kwargs.pop('cool', None)
            if cooldown:
                amount, per, bucket = cooldown
                func = cool(bucket, amount, per)(func)
            command = commands.Command(func, **kwargs)
            self.add_command(command)
            return func
        return decorator

__all__ = ['Saint', 'cool', 'group_cool']
