import discord
from timeit import default_timer as dt
from os import getenv
import random
import time

time.tzset()

# TODO: let this be dynamically generated and edited by the webiste
with open("wordlist.txt", "r") as f:
    wordlist = f.read().splitlines()


class Client(discord.Client):

    last_message: discord.Message = None
    last_message_content: str = ""
    last_files: list[discord.File] = []
    last_files_deleted: bool = False

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        st = dt()
        print("--------------------")

        self.GUILD = client.get_guild(1137187794398224394)
        self.SOLITARY_CATEGORY = discord.utils.get(
            self.GUILD.categories, name="solitary confinement"
        )
        self.JAIL_ROLE = discord.utils.get(self.GUILD.roles, name="jail time")

        print(f"Finished init in: {st - dt():.2f}s")

    def run(self):
        super().run(getenv("TOKEN"))


client = Client()


async def detect_words(message: discord.Message):
    for naughtyWord in wordlist:
        if naughtyWord in message.clean_content.lower():
            # solitary confinement logic here
            await message.delete()
            await message.author.add_roles(
                client.JAIL_ROLE, reason=f"Used the word {naughtyWord}"
            )

            userCell = await client.SOLITARY_CATEGORY.create_text_channel(
                name=f"{message.author.name}-cell"
            )

            timeInJail = abs(random.gauss(10.0, 3.0) * 60)

            await userCell.send(
                f"{message.author.mention}, you have been placed in solitary confinement for using the word ***{naughtyWord}***. Please remember to keep your dialogue clean. Thank you for your time. You will be released <t:{int(time.time() + timeInJail)}:R>"
            )

            time.sleep(timeInJail)

            await userCell.delete()

            await message.author.remove_roles(client.JAIL_ROLE, reason="Time served")

            return


@client.tree.command(
    name="snipe", description="reveal the last message in chat that was deleted"
)
async def snipe(interaction: discord.Interaction):
    contents = client.last_message_content
    await interaction.response.send_message(
        content=f"```SENT: {client.last_message.created_at.astimezone().strftime('%Y-%m-%d %H:%M:%S')}\nBY: {client.last_message.author}\nCONTENTS:\n{contents}```",
        files=client.last_files,
    )


@client.event
async def on_message(message: discord.Message):
    if (
        (message.author == client.user)
        or (message.author.bot)
        or (message.interaction == "application_command")
    ):
        return

    elif message.author.id == 756578226494767284:  # nate
        await message.reply("fuck you")

    elif message.author.id == 529505244615278605: # abbie
        now = time.localtime()
        if now.tm_hour == 11:
            message.reply(f"# shut the fuck up, you chink. go back to washing dishes")

    if message.attachments:
        client.last_files = [await i.to_file() for i in message.attachments]
        client.last_files_deleted = False

    # Detect words
    await detect_words(message)


@client.event
async def on_message_edit(message: discord.Message):
    if (
        (message.author == client.user)
        or (message.author.bot)
        or (message.interaction == "application_command")
    ):
        return

    await detect_words(message)


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


client.run()
