import discord
from src.moduls.formatters import tax_str_formatter


class PaginationView(discord.ui.View):
    def __init__(self, data, max_key, total_entries, space, total_label, period_dates=None, total_tax=0):
        super().__init__()
        self.data = data
        self.current_page = 1
        self.sep = 10
        self.total_tax = total_tax
        self.period_dates = period_dates
        self.max_key = max_key
        self.space = space
        self.total_entries = total_entries
        self.total_label = total_label

    async def send(self, interaction):
        self.message = await interaction.followup.send(view=self)
        await self.update_message(self.data[:self.sep])

    def create_mess(self, data):
        tax_str = tax_str_formatter(
            tax_data=data,
            period_dates=self.period_dates,
            total_tax=self.total_tax,
            space=self.space,
            max_key=self.max_key,
            total_entries=self.total_entries,
            total_label=self.total_label
        )
        footer = f"Page {self.current_page} of {int(len(self.data) / self.sep) + 1}"
        return f"```{tax_str[0]}```\n```{tax_str[1]}```\n```{footer}```"

    async def update_message(self, data):
        self.update_buttons()
        await self.message.edit(content=self.create_mess(data), view=self)

    def update_buttons(self):
        if self.current_page == 1:
            self.f_page_b.disabled = True
            self.p_page_b.disabled = True
            self.f_page_b.style = discord.ButtonStyle.grey
            self.p_page_b.style = discord.ButtonStyle.grey
        else:
            self.f_page_b.disabled = False
            self.p_page_b.disabled = False
            self.f_page_b.style = discord.ButtonStyle.primary
            self.p_page_b.style = discord.ButtonStyle.primary

        if self.current_page == int(len(self.data) / self.sep) + 1:
            self.n_page_b.disabled = True
            self.l_page_b.disabled = True
            self.n_page_b.style = discord.ButtonStyle.grey
            self.l_page_b.style = discord.ButtonStyle.grey
        else:
            self.n_page_b.disabled = False
            self.l_page_b.disabled = False
            self.n_page_b.style = discord.ButtonStyle.primary
            self.l_page_b.style = discord.ButtonStyle.primary

    @discord.ui.button(label="<<", style=discord.ButtonStyle.primary)
    async def f_page_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = 1
        until_item = self.current_page * self.sep
        await self.update_message(self.data[:until_item])

    @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
    async def p_page_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 1
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(self.data[from_item:until_item])

    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def n_page_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 1
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(self.data[from_item:until_item])

    @discord.ui.button(label=">>", style=discord.ButtonStyle.primary)
    async def l_page_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = int(len(self.data) / self.sep) + 1
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(self.data[from_item:])
