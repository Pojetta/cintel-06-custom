import faicons as fa
import plotly.express as px

# Load data and compute static values
from shared import app_dir, tips
from shiny import reactive, render
from shiny.express import input, ui
from shinywidgets import render_plotly

bill_rng = (min(tips.total_bill), max(tips.total_bill))

# Add page title and sidebar
ui.page_opts(title="Restaurant tipping", fillable=False)

with ui.sidebar(open="closed",style="background-color: #FCDE9C;"):
    ui.input_slider(
        "total_bill",
        "Bill amount",
        min=bill_rng[0],
        max=bill_rng[1],
        value=bill_rng,
        pre="$",
    )
    ui.input_checkbox_group(
        "time",
        "Food service",
        ["Lunch", "Dinner"],
        selected=["Lunch", "Dinner"],
        inline=True,
    )
    ui.input_action_button("reset", "Reset filter")

# Add main content
ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "wallet": fa.icon_svg("wallet"),
    "currency-dollar": fa.icon_svg("dollar-sign"),
    "ellipsis": fa.icon_svg("ellipsis"),
}

with ui.layout_columns(fill=False):
    with ui.value_box(showcase=ICONS["user"], theme=ui.value_box_theme(fg="white", bg="#7C1D6F")):
        "Total tippers"

        @render.express
        def total_tippers():
            tips_data().shape[0]

    with ui.value_box(showcase=ICONS["wallet"], theme=ui.value_box_theme(fg="white", bg="#B9257A")):
        "Average tip"

        @render.express
        def average_tip():
            d = tips_data()
            if d.shape[0] > 0:
                perc = d.tip / d.total_bill
                f"{perc.mean():.1%}"


    with ui.value_box(showcase=ICONS["currency-dollar"], theme=ui.value_box_theme(fg="white", bg="#FAA476")):
        "Average bill"

        @render.express
        def average_bill():
            d = tips_data()  # Get the filtered data
            if d.shape[0] > 0:
                bill = d.total_bill.mean()  # Calculate the average bill
                f"${bill:.2f}"  # The function will output this value without returning it


with ui.layout_columns(col_widths=[6, 6, 12]):
    with ui.card(full_screen=True):
        ui.card_header("Tips data", style="background-color: white;")

        @render.data_frame
        def table():
            return render.DataGrid(tips_data())

    with ui.card(full_screen=True):
        with ui.card_header(class_="d-flex justify-content-between align-items-center", style="background-color: white;"):
            "Total bill vs tip"
            with ui.popover(title="Add a color variable", placement="top"):
                ICONS["ellipsis"]
                ui.input_radio_buttons(
                    "scatter_color",
                    None,
                    ["none", "sex", "day", "time"],
                    inline=True,
                )

        @render_plotly
        def scatterplot():
            color = input.scatter_color()
            return px.scatter(
                tips_data(),
                x="total_bill",
                y="tip",
                color_discrete_sequence=["#7C1D6F"],
                color=None if color == "none" else color,
                trendline="lowess",
            )

    with ui.card(full_screen=True):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "Tip percentages"
            with ui.popover(title="Add a color variable"):
                ICONS["ellipsis"]
                ui.input_radio_buttons(
                    "tip_perc_y",
                    "Split by:",
                    ["sex", "day", "time"],
                    selected="day",
                    inline=True,
                )

        @render_plotly
        def tip_perc():
            from ridgeplot import ridgeplot

            # Calculate the 'percent' as tip / total_bill
            dat = tips_data()
            dat["percent"] = dat.tip / dat.total_bill  # Tip percentage as a ratio

            # Get the variable to split by (e.g., sex, day, time)
            yvar = input.tip_perc_y()
            uvals = dat[yvar].unique()  # Get the unique values for the chosen split variable

            # Prepare the samples for the ridge plot, splitting by the selected variable
            samples = [[dat.percent[dat[yvar] == val]] for val in uvals]

            # Create the ridge plot
            plt = ridgeplot(
                samples=samples,
                labels=uvals,
                bandwidth=0.01,
                colorscale="sunsetdark",  # Default color scale
                colormode="row-index",  # Color based on row index
            )

            # Update the layout of the plot (e.g., legend placement)
            plt.update_layout(
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5
                )
            )

            return plt



# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------

@reactive.calc
def tips_data():
    bill = input.total_bill()
    idx1 = tips.total_bill.between(bill[0], bill[1])
    idx2 = tips.time.isin(input.time())
    filtered = tips[idx1 & idx2]
    filtered["tip_percentage"] = ((filtered.tip / filtered.total_bill) * 100).round(2)  # Rounding to 2 decimal places
    return filtered

@reactive.effect
@reactive.event(input.reset)
def _():
    ui.update_slider("total_bill", value=bill_rng)
    ui.update_checkbox_group("time", selected=["Lunch", "Dinner"])
