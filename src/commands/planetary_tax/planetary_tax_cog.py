import discord
from discord import app_commands
from discord.ext import commands

from src.core.db_operations import DBOperations
from src.moduls.plot_generator import CreatePlotByteImg
from src.views.period_modal_view import PeriodTaxModal
from src.commands.planetary_tax.tax_message import TaxMessage

from config import dbconf

from src.moduls.custom_logger import CustomLogger


custom_logger = CustomLogger(logger_name=__name__, log_level='error', logfile_name='commands.log')
commands_logger = custom_logger.create_logger()

db_operations = DBOperations(dbconf)
create_plot = CreatePlotByteImg(global_style='dark_background')
tax_msg = TaxMessage()


class PlanetaryTaxCommands(commands.GroupCog, group_name="planet_tax"):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        commands_logger.info(f"Planetary Tax Commands Cog is loaded")

    @app_commands.command(
        name="total",
        description="Show total Planetary Tax"
    )
    @app_commands.choices(
        plot_type=[
            app_commands.Choice(name="Bar", value="bar"),
            app_commands.Choice(name="Pie", value="pie"),
        ]
    )
    @app_commands.rename(plot_type="plot")
    @app_commands.describe(plot_type="Select type of plot")
    async def total_tax(self, interaction: discord.Interaction, plot_type: str = "bar"):
        commands_logger.info(
            f"total_tax command used by {interaction.user} on server id: {interaction.guild_id}"
        )

        db_q_all = db_operations.get_all_planetary_tax()

        if db_q_all['status']:
            try:
                tax_message = await tax_msg.create_tax_message(db_tax_data=db_q_all['data'], plot_type=plot_type)

                await interaction.response.send_message(
                    embed=tax_message["embed"],
                    file=tax_message["plot_img"],
                    view=tax_message["view"]
                )
                commands_logger.info(f"total_tax command completed")
            except Exception as error:
                commands_logger.error(f"total_tax command error: {error}")
        else:
            try:
                await interaction.response.send_message(f"{db_q_all['data']}")
                commands_logger.info(f"total_tax send err message completed")
            except Exception as error:
                commands_logger.error(f"total_tax send err message error: {error}")

    @app_commands.command(
        name="period",
        description="Show total Planetary Tax"
    )
    async def period_tax(self, interaction: discord.Interaction):
        commands_logger.info(
            f"period_tax command used by {interaction.user} on server id: {interaction.guild_id}"
        )
        try:
            await interaction.response.send_modal(PeriodTaxModal())
            commands_logger.info(f"period_tax send message completed")
        except Exception as error:
            commands_logger.error(f"period_tax send message error: {error}")


def setup(bot):
    bot.add_cog(PlanetaryTaxCommands(bot))
