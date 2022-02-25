import discord
from discord.ext import commands
import music
from online import online
import os

cogs = [music]

client = commands.Bot(command_prefix='-', intents = discord.Intents.all())
client.remove_command('help')

for i in range(len(cogs)):
    cogs[i].setup(client)

online()
client.run(os.environ.get("TOKEN"))