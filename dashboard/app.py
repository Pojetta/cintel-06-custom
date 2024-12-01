import faicons as fa
import plotly.express as px
from pathlib import Path

# Load data and compute static values
from shared import app_dir, tips
from shiny import reactive, render
from shiny.express import input, ui
from shinywidgets import render_plotly
import numpy as np

bill_rng = (min(tips.total_bill), max(tips.total_bill))

# Add page title and sidebar
ui.page_opts(title="Restaurant tipping", fillable=False)

with ui.sidebar(open="desktop"):

    ui.input_radio_buttons(
        "filter_days",
        "Filter Days",
        ["All", "Thur", "Fri", "Sat", "Sun"],  # Single radio button group for all filtering options
        selected="All",  # Default to "All" (show all days by default)
        inline=False,
    )

    ui.input_checkbox_group(
        "time",
        "Food service",
        ["Lunch", "Dinner"],
        selected=["Lunch", "Dinner"],
        inline=True,
    )

    ui.input_slider(
        "total_bill",
        "Bill amount",
        min=bill_rng[0],
        max=bill_rng[1],
        value=bill_rng,
        pre="$",
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
    with ui.card(full_screen=True, style="height: 300px;"):
        ui.card_header("Tips data", style="background-color: white;")

        @render.data_frame
        def table():
            return render.DataGrid(tips_data())

    with ui.card(full_screen=True, style="height: 300px;"):
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
            custom_colors = ["#7C1D6F", "#FAA476", "#B9257A", "#FCDE9C"]  # Custom color palette
            
            # Get the data
            df = tips_data()

            # Calculate a simple linear trendline
            trendline = np.polyfit(df["total_bill"], df["tip"], 1)  # First-degree polynomial (line)
            trend_fn = np.poly1d(trendline)

            # Create scatterplot
            fig = px.scatter(
                df,
                x="total_bill",
                y="tip",
                color_discrete_sequence=custom_colors,
                color=None if color == "none" else color,
            )

            # Add trendline to the plot
            fig.add_scatter(
                x=df["total_bill"],
                y=trend_fn(df["total_bill"]),
                mode="lines",
                line=dict(color="#B9257A"),  # Trendline color
                name="Trendline",
            )
            
            # Update the layout to adjust the legend
            fig.update_layout(
                legend=dict(
                    orientation="h",  # Horizontal legend layout
                    yanchor="bottom",  # Align legend to the bottom
                    y=1.02,  # Position above the plot
                    xanchor="center",  # Center align horizontally
                    x=0.5,  # Center of the plot
                    font=dict(size=10),  # Shrink font size
                    itemwidth=30,  # Compress legend item width
                ),
            )

            return fig



with ui.layout_columns():
        with ui.card(full_screen=True, style="height: 300px;"):
            ui.card_header("Tip Percentages", style="background-color: white;") 

            @render.image
            def image():
                # Get the path to the current directory
                dir = Path(__file__).resolve().parent

                # Create the image path and return it as an ImgData object
                img = {"src": str(dir / "ridgeplot_image.png"), "width": "100%", "style": "object-fit: contain;"}
                return img
         
# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------
# Reactive data filtering
@reactive.calc
def tips_data():
    # Get the selected day from the radio buttons
    selected_day = input.filter_days()  # Now this covers "All" and specific days

    # Determine filtering logic based on the selected option
    if selected_day == "All":
        idx3 = tips.day.isin(["Thur", "Fri", "Sat", "Sun"])  # Include all days
    else:
        idx3 = tips.day == selected_day  # Filter by the selected day

    # Additional filters (for bill and time)
    idx1 = tips.total_bill.between(input.total_bill()[0], input.total_bill()[1])
    idx2 = tips.time.isin(input.time())

    # Apply all filters and calculate tip percentage
    filtered = tips[idx1 & idx2 & idx3]
    filtered["tip_percentage"] = ((filtered.tip / filtered.total_bill) * 100).round(2)
    return filtered

@reactive.effect
@reactive.event(input.reset)
def reset_filters():
    # Reset the filters to their default values
    ui.update_slider("total_bill", value=bill_rng)
    ui.update_checkbox_group("time", selected=["Lunch", "Dinner"])
    ui.update_radio_buttons("filter_days", selected="All")  # Reset filter_option




