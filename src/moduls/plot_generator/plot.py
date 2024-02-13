import matplotlib.pyplot as plt
from io import BytesIO
from typing import Optional

from src.moduls.formatters import isk_formatter
from src.moduls.custom_logger import CustomLogger


custom_logger = CustomLogger(logger_name=__name__, log_level='error', logfile_name='commands.log')
plot_logger = custom_logger.create_logger()


class CreatePlotByteImg:
    def __init__(self, global_style: str = 'seaborn-whitegrid', global_dpi: int = 300, global_format: str = 'png'):
        self.global_style = global_style
        self.global_dpi = global_dpi
        self.global_format = global_format

    def add_labels(self, x, y, plot):
        yl = list(y)
        for i in range(len(x)):
            plot.text(i, yl[i] // 2, isk_formatter(yl[i]), ha='center')

    async def get_plot_universal_img(
            self,
            data_dict: dict,
            plot_type: Optional[str] = "bar",
            title: Optional[str] = None,
            x_label: Optional[str] = None,
            y_label: Optional[str] = None,
            x_axis_visible: bool = True,
            y_axis_visible: bool = True
    ):
        if plot_type is None:
            plot_type = "bar"
        plot_type = plot_type.lower()
        try:
            if plot_type == "bar":
                plot_bar_img = await self.get_plot_bar_img(
                    data_dict=data_dict,
                    title=title,
                    x_label=x_label,
                    y_label=y_label,
                    x_axis_visible=x_axis_visible,
                    y_axis_visible=y_axis_visible
                )
                plot_logger.info(f"Plot bar img generated")
                return plot_bar_img
            elif plot_type == "pie":
                plot_pie_img = await self.get_plot_pie_img(data_dict=data_dict, title=title)
                plot_logger.info(f"Plot pie img generated")
                return plot_pie_img
            else:
                raise Exception("Unknown plot type")
        except Exception as err:
            plot_logger.info(f"Error while plot creating: {err}")

    async def get_plot_bar_img(
            self,
            data_dict: dict,
            title: str = None,
            x_label: str = None,
            y_label: str = None,
            x_axis_visible: bool = True,
            y_axis_visible: bool = True
    ):
        img_bites = BytesIO()

        plt.style.use(self.global_style)

        names_dict = []

        for key in data_dict.keys():
            f_key = key.split(" ")
            names_dict.append(
                "\n".join(f_key)
            )

        x = names_dict
        y = data_dict.values()

        f = plt.gca()
        if not x_axis_visible:
            f.axes.get_xaxis().set_visible(False)
            f.axes.xaxis.set_ticklabels([])
        if not y_axis_visible:
            f.axes.get_yaxis().set_visible(False)
            f.axes.yaxis.set_ticklabels([])

        plt.subplots_adjust(bottom=0.2, left=0.024, right=0.98)

        plt.bar(x, y, color='green')

        self.add_labels(x, y, plot=plt)

        if title:
            plt.title(title)
        if x_label:
            plt.xlabel(x_label)
        if y_label:
            plt.ylabel(y_label)

        plt.savefig(img_bites, format=self.global_format, dpi=self.global_dpi)
        plt.close()
        img_bites.seek(0)
        return img_bites

    async def get_plot_pie_img(self, data_dict: dict, title: str = None):
        img_bites = BytesIO()
        plt.style.use(self.global_style)

        x = data_dict.keys()
        y = data_dict.values()

        _, _, autotexs = plt.pie(y, labels=x, autopct='%1.1f%%')
        for autotex in autotexs:
            autotex.set_color('black')

        if title:
            plt.title(title)

        plt.savefig(img_bites, format=self.global_format, dpi=self.global_dpi)
        plt.close()
        img_bites.seek(0)
        return img_bites
