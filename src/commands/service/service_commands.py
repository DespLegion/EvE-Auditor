import discord
from discord import app_commands
from discord.ext import commands

from config import dbconf

from src.core.db_operations import DBOperations
from src.moduls.custom_logger import CustomLogger


custom_logger = CustomLogger(logger_name=__name__, log_level='error', logfile_name='commands.log')
s_commands_logger = custom_logger.create_logger()


db_operations = DBOperations(dbconf)


class ServiceCommands(commands.GroupCog, group_name="service"):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        s_commands_logger.info(f"Service Commands Cog is loaded")

    @app_commands.command(
        name="check_db",
        description="Check connection to database and show version of MySQL database"
    )
    async def check_db(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            v = db_operations.check_connection()
            if v['status']:
                await interaction.followup.send(f"Connection is Fine.\nMysql v: {v['data'][0]}")
            else:
                await interaction.followup.send(f"{v['data']}")
            s_commands_logger.info(f"Service Commands send message successfully")
        except Exception as err:
            s_commands_logger.error(f"Service Commands send message error: {err}")


def setup(bot):
    bot.add_cog(ServiceCommands(bot))
