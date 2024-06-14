import discord
from timeit import default_timer as dt
from os import getenv


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

        print(f"Finished init in: {st - dt():.2f}s")

    def run(self):
        super().run(getenv("TOKEN"))


client = Client()

GUILD = client.get_guild(1137187794398224394)


@client.tree.command(
    name="snipe", description="reveal the last message in chat that was deleted"
)
async def snipe(interaction: discord.Interaction):
    contents = client.last_message_content
    await interaction.response.send_message(
        content=f"```SENT: {client.last_message.created_at.strftime('%Y-%m-%d %H:%M:%S')}\nBY: {client.last_message.author}\n\nCONTENTS:\n{contents}```",
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

    if message.attachments:
        client.last_files = [await i.to_file() for i in message.attachments]
        client.last_files_deleted = False


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
