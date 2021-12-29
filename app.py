import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

# dataframe data
from data import generate__dataframe


# dash instance
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

# app layout
app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1(
                    "Real Estate Dashboard", className="text-center text-primary mb-4"
                ),
                width=12,
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id="city-dpdn",
                            multi=False,
                            value="New-York_NY",
                            options=[
                                {"label": city, "value": city}
                                for city in (
                                    "New-York_NY",
                                    "Texas",
                                    "Georgia",
                                    "Michigan",
                                )
                            ],
                        ),
                        dcc.Graph(id="bar-fig", figure={}),
                    ],
                    xs=12,
                    sm=12,
                    md=12,
                    lg=6,
                    xl=6,
                ),
                dbc.Col(
                    dcc.Graph(id="bar-fig2", figure={}),
                    xs=12,
                    sm=12,
                    md=12,
                    lg=6,
                    xl=6,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id="bar-fig3", figure={}), xs=12, sm=12, md=12, lg=6, xl=6
                ),
                dbc.Col(
                    dcc.Graph(id="bar-fig4", figure={}),
                    xs=12,
                    sm=12,
                    md=12,
                    lg=6,
                    xl=6,
                ),
            ]
        ),
    ]
)

# Callbacks
@app.callback(
    [
        Output("bar-fig", "figure"),
        Output("bar-fig2", "figure"),
        Output("bar-fig3", "figure"),
        Output("bar-fig4", "figure"),
    ],
    [Input("city-dpdn", "value")],
)
def update_graph(city):
    df = generate__dataframe(city)
    bed_df = df[df["Beds"] <= 10]
    bed_nums = sorted(bed_df["Beds"].unique())
    bed_df = bed_df["Beds"].value_counts()
    bed_df = pd.DataFrame(bed_df)
    bed_df.reset_index(inplace=True)
    bed_df = bed_df.rename(columns={"index": "beds", "Beds": "count"})
    fig = px.bar(bed_df, x="beds", y="count", title="House Beds and Distribution Count")

    bath_nums = sorted(df["Baths"].unique())
    bath_df = df[df["Baths"] <= 10]
    bath_df = bath_df["Baths"].value_counts()
    bath_df = pd.DataFrame(bath_df)
    bath_df.reset_index(inplace=True)
    bath_df = bath_df.rename(columns={"index": "baths", "Baths": "count"})
    fig2 = px.bar(
        bath_df, x="baths", y="count", title="House Baths and Distribution Count"
    )

    bp_df = df.groupby("Beds")["Price"].mean()
    bp_df = pd.DataFrame(bp_df)
    bp_df.reset_index(inplace=True)
    bp_df.rename(columns={"Price": "average price"}, inplace=True)
    bp_df = bp_df[bp_df["Beds"] <= 10]
    fig3 = px.bar(
        bp_df, x="Beds", y="average price", title="House Beds and Average Price"
    )

    btp_df = df.groupby("Baths")["Price"].mean()
    btp_df = pd.DataFrame(btp_df)
    btp_df.reset_index(inplace=True)
    btp_df.rename(columns={"Price": "average price"}, inplace=True)
    btp_df = btp_df[btp_df["Baths"] <= 10]
    fig4 = px.bar(
        btp_df, x="Baths", y="average price", title="House Baths and Average Price"
    )

    return fig, fig2, fig3, fig4


if __name__ == "__main__":
    app.run_server(debug=True, port=8009)
