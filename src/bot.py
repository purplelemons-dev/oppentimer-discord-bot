import discord
from timeit import default_timer as dt
from os import getenv


TOKEN = getenv("TOKEN")

intents = discord.Intents.all()


client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    print("--------------------")
    print(f"At: {dt()}")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if message.author.id == 756578226494767284:  # nate
        await message.reply("fuck you")


client.run(TOKEN)
