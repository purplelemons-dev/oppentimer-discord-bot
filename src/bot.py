import discord
from timeit import default_timer as dt
from os import getenv
import random
import time
import asyncio
import json
from data_classes import *
from requests import get as req_get

time.tzset()

# TODO: let this be dynamically generated and edited by the webiste
with open("wordlist.txt", "r") as f:
    wordlist = f.read().splitlines()


with open("data/userinfo.json", "r") as f:
    userinfo: dict[int, UserInfo] = json.load(f)

with open("data/roles.json", "r") as f:
    roles: ReactionRoles = json.load(f)


def get_digits(text: str) -> int:
    return int("".join(filter(str.isdigit, text)))


class Client(discord.Client):

    class channels:
        solitary: discord.CategoryChannel = None
        botLogs: discord.TextChannel = None
        hangouts: discord.TextChannel = None
        oppentimer_channel: discord.TextChannel = None

    class roles:
        jail: discord.Role = None

    last_message: discord.Message = None
    last_message_content: str = ""
    last_files: list[discord.File] = []
    last_files_deleted: bool = False
    voice_client: discord.VoiceClient = None

    has_loaded: bool = False

    def __init__(self, *args, **kwargs):
        intents = discord.Intents.all()
        super().__init__(intents=intents, *args, **kwargs)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        await super().setup_hook()

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        print("--------------------")
        st = dt()

        self.GUILD = client.get_guild(1137187794398224394)
        self.channels.solitary = discord.utils.get(
            self.GUILD.categories, name="solitary confinement"
        )
        self.channels.botLogs = self.get_channel(1251302290875220038)
        self.channels.hangouts = self.get_channel(1137187795736211549)
        self.channels.oppentimer_channel = self.get_channel(1137187795736211549)

        self.roles.jail = self.GUILD.get_role(1251026269835886613)

        for user in self.GUILD.members:
            if user.id not in userinfo:
                userinfo[user.id] = {"messageCount": 0}

        finishTime = dt() - st
        self.has_loaded = True
        print(f"Finished init in: {finishTime:.2f}s")

        await self.channels.botLogs.send(f"Bot booted in {finishTime:.2f}s")

        # main loop
        while True:
            with open("data/userinfo.json", "w") as f:
                json.dump(userinfo, f, default=lambda x: x.__dict__, indent=4)

            with open("data/roles.json", "w") as f:
                json.dump(roles, f, default=lambda x: x.__dict__, indent=4)

            await asyncio.sleep(1)

    def run(self):
        super().run(getenv("TOKEN"))


client = Client(max_messages=10000)


async def detect_words(message: discord.Message):
    if client.roles.jail in message.author.roles:
        print(f"{message.author.display_name} is in jail, not checking for words")
        return False

    for naughtyWord in wordlist:
        if naughtyWord in message.clean_content.lower():
            # solitary confinement logic here
            await message.delete()
            await message.author.add_roles(
                client.roles.jail, reason=f"Used the word {naughtyWord}"
            )

            userCell = await client.channels.solitary.create_text_channel(
                name=f"{message.author.name}-cell"
            )

            timeInJail = abs(random.gauss(10.0, 3.0) * 60)

            await userCell.send(
                f"{message.author.mention}, you have been placed in solitary confinement for using the word ***{naughtyWord}***. Please remember to keep your dialogue clean. Thank you for your time. You will be released <t:{int(time.time() + timeInJail)}:R>"
            )

            await client.channels.botLogs.send(
                f"{message.author.name} has been placed in solitary confinement for using the word ***{naughtyWord}*** and will be released <t:{int(time.time() + timeInJail)}:R>"
            )

            await asyncio.sleep(timeInJail)

            await userCell.delete()

            await message.author.remove_roles(client.roles.jail, reason="Time served")

            return True

    return False


@client.tree.command(name="test", description="test")
async def test(ctx: discord.Interaction, target: discord.User):
    class View(discord.ui.View):
        @discord.ui.button(label="test1", style=discord.ButtonStyle.primary, emoji="👍")
        async def test1(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await interaction.response.send_message(
                "You pressed button 1!", ephemeral=True
            )

        @discord.ui.button(label="test2", style=discord.ButtonStyle.primary, emoji="👎")
        async def test2(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await interaction.response.send_message(
                "You pressed button 2!", ephemeral=True
            )

    await ctx.response.send_message(
        embed=discord.Embed(
            title="Test",
            description=f"Test command for {target.mention}",
            color=discord.Color.gold(),
        ),
        view=View(),
    )


@client.tree.command(
    name="snipe", description="reveal the last message in chat that was deleted"
)
async def snipe(ctx: discord.Interaction):
    contents = client.last_message_content
    await ctx.response.send_message(
        content=f"```SENT: {client.last_message.created_at.astimezone().strftime('%Y-%m-%d %H:%M:%S')}\nBY: {client.last_message.author}\nCONTENTS:\n{contents}```",
        files=client.last_files,
    )


@client.tree.command(
    name="role_selector",
    description="Sends a message in current channel with a role selector menu",
)
async def role_selector(ctx: discord.Interaction, roles: str):

    print(roles)
    roleObjs = [
        discord.utils.get(client.GUILD.roles, id=get_digits(role.strip()))
        for role in roles.split(",")
    ]
    print(roleObjs)

    embed = discord.Embed(
        title="Role Selector",
        description="React to this message to get the roles you want",
        color=discord.Color.blurple(),
    )

    # add a button for each role
    for role in roleObjs:
        embed.add_field(
            name=role.name,
            value=f"React with {role.mention} to get the {role.name} role",
            inline=False,
        )

    await ctx.response.send_message(embed=embed)


@client.tree.command(
    name="set_role_emoji", description="Set the emoji for a role in the role selector"
)
async def set_role_emoji(ctx: discord.Interaction, role: str, emoji: str):
    roleObj = discord.utils.get(client.GUILD.roles, id=get_digits(role))
    await ctx.response.send_message(
        content=f"Set the emoji for the role {roleObj.name} to {emoji}"
    )


@client.tree.command(name="join", description="Join the voice channel you are in")
async def join(ctx: discord.Interaction):
    channel: discord.VoiceChannel = ctx.user.voice.channel
    print(f"User {ctx.user} joined #{channel.name}")

    client.voice_client = await channel.connect()
    await ctx.response.send_message("Joined")


@client.tree.command(name="leave", description="Leave the voice channel")
async def leave(ctx: discord.Interaction):
    await client.voice_client.disconnect()
    await ctx.response.send_message("Left")


@client.tree.command(
    name="minecraft", description="See how many people are on the minecraft server"
)
async def minecraft(ctx: discord.Interaction):
    MC_IP = getenv("MCSERVER")
    players = req_get(f"https://api.mcsrvstat.us/3/{MC_IP}").json()["players"]
    try:
        playerList = ":\n- " + "\n- ".join(i["name"] for i in players["list"])
    except KeyError:
        playerList = "."
    await ctx.response.send_message(
        f"There are {players['online']}/{players['max']} players on the server{playerList}"
    )


@client.event
async def on_message(message: discord.Message):
    if (
        (message.author == client.user)
        or (message.author.bot)
        or (message.interaction == "application_command")
    ):
        return

    elif (message.author.id == 756578226494767284) and (
        message.channel.id
        in {
            i.id for i in {client.channels.hangouts, client.channels.oppentimer_channel}
        }
    ):  # nate
        await message.reply("fuck you")

    elif message.author.id == 529505244615278605:  # abbie
        now = time.localtime()
        if now.tm_hour == 11:
            await message.reply(
                f"# shut the fuck up, you chink. go back to washing dishes"
            )

    if message.attachments:
        client.last_files = [await i.to_file() for i in message.attachments]
        client.last_files_deleted = False

    # Detect words
    if not await detect_words(message):
        if message.author.id not in userinfo:
            userinfo[message.author.id] = {}
        try:
            userinfo[message.author.id]["messageCount"] += 1
        except KeyError:
            userinfo[message.author.id]["messageCount"] = 1


@client.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if (
        (after.author == client.user)
        or (after.author.bot)
        or (after.interaction == "application_command")
    ):
        return

    await detect_words(after)


@client.event
async def on_message_delete(message: discord.Message):
    if (
        (message.author == client.user)
        or (message.author.bot)
        or (message.interaction == "application_command")
    ):
        return
    client.last_message = message

    client.last_message_content = client.last_message.clean_content
    client.last_files_deleted = True
