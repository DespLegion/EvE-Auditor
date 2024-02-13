import discord
from discord.ui import View, Button
import heapq

from src.moduls.plot_generator import CreatePlotByteImg
from src.views.pagination_view import PaginationView

from src.moduls.custom_logger import CustomLogger


custom_logger = CustomLogger(logger_name=__name__, log_level='error', logfile_name='commands.log')
tax_mess_logger = custom_logger.create_logger()

create_plot = CreatePlotByteImg(global_style='dark_background')


class TaxMessage:
    def __init__(self, names_to_display_c: int = 5):
        self.names_to_display_c = names_to_display_c
        self.x_label_name = ""

    async def create_tax_message(self, db_tax_data, plot_type, system_name=False, period=False, char_name=False):
        try:
            total_tax = 0
            total_entries = 0
            tax_in_names = {}

            period_dates = [
                db_tax_data[0][1].date(),
                db_tax_data[int(len(db_tax_data)) - 1][1].date()
            ]

            for tax_row in db_tax_data:
                total_tax += int(tax_row[0])
                total_entries += 1

                if system_name and not char_name:
                    name = str(tax_row[2])  # char names
                elif system_name and char_name:
                    reason = str(tax_row[2]).split()  # planets
                    name = reason[4]
                else:
                    reason = str(tax_row[2]).split()  # systems
                    name = reason[3]

                if name in tax_in_names:
                    tax_in_names[name] += int(tax_row[0])
                else:
                    tax_in_names[name] = int(tax_row[0])

            sorted_tax_dict = {}
            for k in sorted(tax_in_names, key=tax_in_names.get, reverse=True):
                sorted_tax_dict[k] = tax_in_names[k]

            if len(sorted_tax_dict) > 6:
                tax_for_plot = await self.reformat_big_tax(sorted_tax_dict)
            else:
                tax_for_plot = sorted_tax_dict

            if system_name and not char_name:
                self.x_label_name = "Characters"
            elif system_name and char_name:
                self.x_label_name = "Planets"
            else:
                self.x_label_name = "Systems"

            plot_title = "Planetary Tax Graph"
            if period:
                plot_title += f"\n{period_dates[0]} - {period_dates[1]}"
                if char_name:
                    plot_title += f"\nFor {char_name}"
                if system_name:
                    plot_title += f" In {system_name}"

            plot_byte_img = await create_plot.get_plot_universal_img(
                plot_type=plot_type,
                data_dict=tax_for_plot,
                title=plot_title,
                x_label=self.x_label_name,
                y_axis_visible=False
            )

            plot_img = discord.File(plot_byte_img, filename="p_tax_graph.png")

            tax_view = await self.tax_view_generator(
                period_dates=period_dates,
                total_entries=total_entries,
                total_tax=total_tax,
                system_name=system_name,
                period=period,
                char_name=char_name,
                plot_img=plot_img,
                tax_in_names=sorted_tax_dict
            )
            tax_mess_logger.info(f"Tax view created")
            return tax_view
        except Exception as err:
            tax_mess_logger.error(f"Tax view creation error: {err}")

    async def reformat_big_tax(self, tax_dict):
        short_tax_dict = {}
        other_tax_names = {}
        names_to_display = heapq.nlargest(self.names_to_display_c, tax_dict, key=tax_dict.get)
        other_names_count = len(tax_dict) - len(names_to_display)
        for tax_name, tax in tax_dict.items():
            if tax_name in names_to_display:
                short_tax_dict[tax_name] = tax
            else:
                if f'Other {other_names_count}' in other_tax_names:
                    other_tax_names[f'Other {other_names_count}'] += tax
                else:
                    other_tax_names[f'Other {other_names_count}'] = tax
        else:
            short_tax_dict[f'Other {other_names_count}'] = other_tax_names[f'Other {other_names_count}']
        return short_tax_dict

    async def tax_view_generator(
            self,
            period_dates,
            total_entries,
            total_tax,
            system_name,
            period,
            char_name,
            plot_img,
            tax_in_names
    ):
        embed = discord.Embed(
            title='Planetary Tax',
            description='',
            color=0x00FF00
        )
        if period:
            embed.add_field(name='Period', value=f'{period_dates[0]} - {period_dates[1]}', inline=False)
        if system_name:
            embed.add_field(name='System', value=f'{system_name}', inline=False)
        if char_name:
            embed.add_field(name='Character', value=f'{char_name}', inline=False)
        embed.add_field(name='Total Entries', value=f'{total_entries}', inline=False)
        embed.add_field(name='Total Tax', value=f"{format(total_tax, ',').replace(',', '.')}  isk", inline=False)
        embed.set_image(
            url="attachment://p_tax_graph.png"
        )

        button = Button(label="More info", style=discord.ButtonStyle.primary)

        async def more_info_callback(inter: discord.Interaction):
            await inter.response.edit_message(embed=embed, view=None)
            p_list = []
            l_key = max(map(len, tax_in_names)) + 3
            l_value = len(str(max(tax_in_names.values())))
            space = ""
            for _ in range(l_value + l_key + 15):
                space += "-"
            for l_sys, l_taxs in tax_in_names.items():
                first_part_len = l_key - len(l_sys)
                for _ in range(first_part_len):
                    l_sys += " "
                str_element = f"|  {l_sys}  | {format(l_taxs, ',').replace(',', '.')} isk"
                line_end = len(space) - len(str_element)
                line_end_symbol = ""
                for _ in range(line_end - 1):
                    line_end_symbol += " "
                else:
                    line_end_symbol += "|"
                p_list.append(f"{str_element}{line_end_symbol}\n{'|' + space[1:-1] + '|'}\n")
            pag_view = PaginationView(
                data=p_list,
                total_tax=format(total_tax, ',').replace(',', '.'),
                period_dates=period_dates,
                max_key=l_key,
                space=space,
                total_entries=len(tax_in_names),
                total_label=self.x_label_name
            )
            tax_mess_logger.info(f"Tax More Info used by {inter.user}")
            await pag_view.send(inter)

        button.callback = more_info_callback
        view = View()
        view.add_item(button)

        return {"embed": embed, "plot_img": plot_img, "view": view}
