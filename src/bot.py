import discord
from timeit import default_timer as dt
from os import getenv


class Client(discord.Client):

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        print("--------------------")

        print(f"Finished init at: {dt()}")

    def run(self):
        super().run(getenv("TOKEN"))


client = Client()

GUILD = client.get_guild(1137187794398224394)


@client.tree.command(name="ping", description="Pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!", ephemeral=True)


@client.event
async def on_message(message: discord.Message):
    if (message.author == client.user) or (message.author.bot) or (message.interaction == "application_command"):
        return

    if message.author.id == 756578226494767284:  # nate
        await message.reply("fuck you")


client.run()
