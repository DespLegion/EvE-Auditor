import discord

from config import dbconf

from src.core.db_operations import DBOperations
from src.commands.planetary_tax.tax_message import TaxMessage
from src.moduls.custom_logger import CustomLogger


custom_logger = CustomLogger(logger_name=__name__, log_level='error', logfile_name='commands.log')
period_modal_logger = custom_logger.create_logger()

db_operations = DBOperations(dbconf)
tax_msg = TaxMessage()


class PeriodTaxModal(discord.ui.Modal, title="Planetary Tax"):
    period_start = discord.ui.TextInput(
        label="Period start date",
        style=discord.TextStyle.short,
        placeholder="Date format: YYYY.MM.DD",
        max_length=10,
        required=True
    )
    period_end = discord.ui.TextInput(
        label="Period end date",
        style=discord.TextStyle.short,
        placeholder="Date format: YYYY.MM.DD",
        max_length=10,
        required=True
    )
    system = discord.ui.TextInput(
        label="Ingame System name",
        style=discord.TextStyle.short,
        placeholder="System name",
        max_length=10,
        required=False
    )
    character = discord.ui.TextInput(
        label="Ingame Character name",
        style=discord.TextStyle.short,
        placeholder="Character name",
        required=False
    )

    plot_type = discord.ui.TextInput(
        label="Plot Type (Bar as default)",
        style=discord.TextStyle.short,
        placeholder="Bar or Pie",
        max_length=3,
        min_length=3,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        if self.plot_type.value == "":
            f_plot_type = None
        else:
            f_plot_type = self.plot_type.value

        if self.system.value == "":
            f_system = None
        else:
            f_system = self.system.value

        if self.character.value == "":
            f_character = None
        else:
            f_character = self.character.value

        if f_plot_type is None or f_plot_type == "Bar" or f_plot_type == "Pie":
            res = db_operations.get_period_planetary_tax(
                period_start=self.period_start.value,
                period_end=self.period_end.value,
                system_name=f_system,
                character_name=f_character
            )

            if res['status']:
                try:
                    tax_message = await tax_msg.create_tax_message(
                        db_tax_data=res['data'],
                        plot_type=f_plot_type,
                        period=True,
                        system_name=f_system,
                        char_name=f_character,
                    )

                    await interaction.response.send_message(
                        embed=tax_message["embed"],
                        file=tax_message["plot_img"],
                        view=tax_message["view"]
                    )
                    period_modal_logger.info(f"Modal send successful")
                except Exception as err:
                    period_modal_logger.error(f"Error sending Modal message: {err}")

            else:
                try:
                    period_modal_logger.info(f"Modal bad database request send")
                    await interaction.response.send_message(f"{res['data']}", ephemeral=True)
                except Exception as err:
                    period_modal_logger.error(f"Modal bad database request send error: {err}")
        else:
            try:
                period_modal_logger.info(f"Modal unknown plot type")
                await interaction.response.send_message(
                    f"Unknown plot type. Plot type must be Bar or Pie (If empty - Bar uses as default).",
                    ephemeral=True
                )
            except Exception as err:
                period_modal_logger.error(f"Modal unknown plot type message send error: {err}")
