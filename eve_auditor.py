import discord
from discord.ext import commands

from config import conf

from src.commands.service.service_commands import ServiceCommands
from src.commands.planetary_tax import PlanetaryTaxCommands
from src.moduls.custom_logger import CustomLogger


custom_logger = CustomLogger(logger_name=__name__, log_level='info', logfile_name='main.log')
main_logger = custom_logger.create_logger()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=conf['prefix'], intents=intents)


@bot.event
async def on_connect():
    main_logger.info(f"Connected to Server - {bot.guilds[0].name} ({bot.guilds[0].id})")


@bot.event
async def on_ready():
    main_logger.info(f"Logged as {bot.user.name} on Server - {bot.guilds[0].name} ({bot.guilds[0].id})")
    try:
        await bot.add_cog(ServiceCommands(bot))
        await bot.add_cog(PlanetaryTaxCommands(bot))
        main_logger.info(f"Cogs loaded successfully")
    except Exception as error:
        main_logger.error(f"Cogs not loaded! {error}")
    try:
        await bot.tree.sync()
        main_logger.info(f"Commands tree sync successfully")
    except Exception as error:
        main_logger.error(f"Problem while syncing commands tree! {error}")

bot.run(conf['token'])
