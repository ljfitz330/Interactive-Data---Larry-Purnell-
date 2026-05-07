# Dash dashboard for the 2024 Gen Z voting project.
from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "vote01_2024_e.csv"

BLUE = "#0B4F9C"
RED = "#D84A4A"
GRAY = "#8A8F98"
WHITE = "#FFFFFF"
PAGE_BG = "#F5F7FA"
TEXT = "#1F2A37"
MUTED = "#6B7280"
BORDER = "#DDE5EF"

STATUS_COLORS = {
    "Registered": BLUE,
    "Not registered": "#9AD7FF",
    "Voted": BLUE,
    "Did not vote": RED,
    "No response": GRAY,
}

GENDER_COLORS = {
    "Female": RED,
    "Male": BLUE
}

def load_data():
    vote = pd.read_csv(DATA_PATH)
    vote = vote.rename(columns={
        "sex": "Sex",
        "age": "Age_Group",
        "tot_pop": "Total_Population",
        "us_cit_tot_pop": "Citizen_Population",
        "us_cit_rep_reg_num": "Registered_Number",
        "us_cit_rep_reg_pct": "Registered_Percent",
        "us_cit_rep_nr_num": "Not_Registered_Number",
        "us_cit_rep_nr_pct": "Not_Registered_Percent",
        "us_cit_nr_num": "No_Response_Registration_Number",
        "us_cit_nr_pct": "No_Response_Registration_Percent",
        "us_cit_vote_yes_num": "Voted_Number",
        "us_cit_vote_yes_pct": "Voted_Percent",
        "us_cit_vote_no_num": "Did_Not_Vote_Number",
        "us_cit_vote_no_pct": "Did_Not_Vote_Percent",
        "us_cit_vote_nr_num": "No_Response_Vote_Number",
        "us_cit_vote_nr_pct": "No_Response_Vote_Percent",
        "us_tot_rep_reg_pct": "Overall_Registration_Percent",
        "us_tot_rep_vote_yes_pct": "Overall_Vote_Percent",
    })

    count_columns = [
        "Total_Population",
        "Citizen_Population",
        "Registered_Number",
        "Not_Registered_Number",
        "No_Response_Registration_Number",
        "Voted_Number",
        "Did_Not_Vote_Number",
        "No_Response_Vote_Number",
    ]
    percent_columns = [
        "Registered_Percent",
        "Not_Registered_Percent",
        "No_Response_Registration_Percent",
        "Voted_Percent",
        "Did_Not_Vote_Percent",
        "No_Response_Vote_Percent",
        "Overall_Registration_Percent",
        "Overall_Vote_Percent",
    ]

    for column in count_columns:
        vote[column] = (
            vote[column]
            .astype(str)
            .str.replace(",", "", regex=False)
            .pipe(pd.to_numeric, errors="coerce")
        )

    for column in percent_columns:
        vote[column] = pd.to_numeric(vote[column], errors="coerce")

    vote["Is_Exact_Age"] = vote["Age_Group"].str.match(r"^\d+ years$", na=False)
    vote["Age_Number"] = pd.to_numeric(vote["Age_Group"].str.extract(r"^(\d+)")[0], errors="coerce")
    return vote


vote_2024 = load_data()

gen_z = vote_2024[
    (vote_2024["Sex"] == "BOTH SEXES")
    & (vote_2024["Is_Exact_Age"])
    & (vote_2024["Age_Number"].between(18, 29))
].copy()
gen_z["Age_Number"] = gen_z["Age_Number"].astype(int)
gen_z = gen_z.sort_values("Age_Number")

gen_z_by_gender = vote_2024[
    (vote_2024["Sex"].isin(["FEMALE", "MALE"]))
    & (vote_2024["Is_Exact_Age"])
    & (vote_2024["Age_Number"].between(18, 29))
].copy()
gen_z_by_gender["Age_Number"] = gen_z_by_gender["Age_Number"].astype(int)
gen_z_by_gender["Gender"] = gen_z_by_gender["Sex"].str.title()
gen_z_by_gender = gen_z_by_gender.sort_values(["Age_Number", "Gender"])

gen_z_gender_voted = (
    gen_z_by_gender
    .groupby("Gender", as_index=False)["Voted_Number"]
    .sum()
)

gen_z_total_citizens = gen_z["Citizen_Population"].sum()
gen_z_registered = gen_z["Registered_Number"].sum()
gen_z_not_registered = gen_z["Not_Registered_Number"].sum()
gen_z_voted = gen_z["Voted_Number"].sum()
gen_z_did_not_vote = gen_z["Did_Not_Vote_Number"].sum()
gen_z_no_response = gen_z["No_Response_Vote_Number"].sum()

gen_z_registered_pct = gen_z_registered / gen_z_total_citizens * 100
gen_z_voted_pct = gen_z_voted / gen_z_total_citizens * 100
gen_z_did_not_vote_pct = gen_z_did_not_vote / gen_z_total_citizens * 100
gen_z_no_response_pct = gen_z_no_response / gen_z_total_citizens * 100

gen_z_status = pd.DataFrame({
    "Voting_Status": ["Voted", "Did not vote", "No response"],
    "People_Thousands": [gen_z_voted, gen_z_did_not_vote, gen_z_no_response],
    "Percent": [gen_z_voted_pct, gen_z_did_not_vote_pct, gen_z_no_response_pct],
})

gen_z_status_by_age = gen_z.melt(
    id_vars=["Age_Number"],
    value_vars=["Voted_Percent", "Did_Not_Vote_Percent", "No_Response_Vote_Percent"],
    var_name="Voting_Status",
    value_name="Percent",
)
gen_z_status_by_age["Voting_Status"] = gen_z_status_by_age["Voting_Status"].map({
    "Voted_Percent": "Voted",
    "Did_Not_Vote_Percent": "Did not vote",
    "No_Response_Vote_Percent": "No response",
})

fig_turnout_line = px.line(
    gen_z,
    x="Age_Number",
    y="Voted_Percent",
    markers=True,
    title="Gen Z Voting Turnout by Exact Age",
    labels={"Age_Number": "Age", "Voted_Percent": "Voting rate"},
)
fig_turnout_line.update_traces(
    line=dict(color=BLUE, width=3),
    marker=dict(size=9, color=RED, line=dict(color=WHITE, width=1)),
    text=gen_z["Voted_Percent"],
    texttemplate="%{text:.1f}%",
    textposition="top center",
)
fig_turnout_line.update_layout(yaxis_ticksuffix="%", yaxis_range=[0, 70], xaxis=dict(dtick=1), showlegend=False)

fig_status_bar = px.bar(
    gen_z_status_by_age,
    x="Age_Number",
    y="Percent",
    color="Voting_Status",
    barmode="group",
    title="Gen Z Voting Status Percent by Age",
    labels={"Age_Number": "Age", "Percent": "Percent", "Voting_Status": "Voting status"},
    color_discrete_map=STATUS_COLORS,
)
fig_status_bar.update_layout(yaxis_ticksuffix="%", xaxis=dict(dtick=1), legend_title_text="Voting status")

fig_status_pie = px.pie(
    gen_z_status,
    names="Voting_Status",
    values="People_Thousands",
    title="Gen Z Voting Status Share, Ages 18-29",
    hole=0.38,
    color="Voting_Status",
    color_discrete_map=STATUS_COLORS,
)
fig_status_pie.update_traces(
    textinfo="label+percent",
    hovertemplate="%{label}<br>People: %{value:,.0f} thousand<br>Share: %{percent}<extra></extra>",
)

fig_gender_line = px.line(
    gen_z_by_gender,
    x="Age_Number",
    y="Voted_Percent",
    color="Gender",
    markers=True,
    title="Gen Z Male vs Female Voting Rates by Age",
    labels={"Age_Number": "Age", "Voted_Percent": "Voting rate", "Gender": "Gender"},
    color_discrete_map=GENDER_COLORS,
)
fig_gender_line.update_traces(line=dict(width=3), marker=dict(size=8))
fig_gender_line.update_layout(yaxis_ticksuffix="%", yaxis_range=[0, 75], xaxis=dict(dtick=1), hovermode="x unified")

fig_gender_pie = px.pie(
    gen_z_gender_voted,
    names="Gender",
    values="Voted_Number",
    title="Gen Z Voters by Gender",
    hole=0.38,
    color="Gender",
    color_discrete_map=GENDER_COLORS,
)
fig_gender_pie.update_traces(
    textinfo="label+percent",
    hovertemplate="Gender: %{label}<br>Voters: %{value:,.0f} thousand<br>Share: %{percent}<extra></extra>",
)
fig_gender_pie.update_layout(legend_title_text="Gender")

for figure in [fig_turnout_line, fig_status_bar, fig_status_pie, fig_gender_line, fig_gender_pie]:
    figure.update_layout(
        template="plotly_white",
        title_x=0.02,
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(family="Arial", color=TEXT),
        margin=dict(l=48, r=24, t=64, b=54),
    )


def percent_tile(label, value, note, accent):
    return html.Div(
        className="percent-tile",
        style={"borderTopColor": accent},
        children=[
            html.Div(label, className="tile-label"),
            html.Div(f"{value:.1f}%", className="tile-value", style={"color": accent}),
            html.Div(note, className="tile-note"),
        ],
    )


def graph_panel(figure):
    return html.Div(
        className="graph-panel",
        children=dcc.Graph(figure=figure, config={"displayModeBar": False}),
    )


app = Dash(__name__)
server = app.server

app.layout = html.Div(
    className="page",
    children=[
        html.Div(
            className="header",
            children=[
                html.H1("Gen Z Voting Dashboard"),
                html.P("2024 Census voting data for ages 18-29, with key percentages shown above the charts."),
            ],
        ),
        html.Div(
            className="percent-grid",
            children=[
                percent_tile("Registered", gen_z_registered_pct, "Share of Gen Z citizens registered", BLUE),
                percent_tile("Voted", gen_z_voted_pct, "Share of Gen Z citizens who voted", BLUE),
                percent_tile("Did not vote", gen_z_did_not_vote_pct, "Share of Gen Z citizens who did not vote", RED),
                percent_tile("No response", gen_z_no_response_pct, "No voting response recorded", GRAY),
            ],
        ),
        html.Div(
            className="graph-grid two-column",
            children=[graph_panel(fig_turnout_line), graph_panel(fig_status_pie)],
        ),
        html.Div(
            className="graph-grid one-column",
            children=[graph_panel(fig_status_bar)],
        ),
        html.Div(
            className="graph-grid two-column",
            children=[graph_panel(fig_gender_line), graph_panel(fig_gender_pie)],
        ),
    ],
)

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Gen Z Voting Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            body { margin: 0; background: #F5F7FA; }
            .page { max-width: 1180px; margin: 0 auto; padding: 28px; font-family: Arial, sans-serif; color: #1F2A37; }
            .header { margin-bottom: 20px; }
            .header h1 { margin: 0 0 8px; color: #0B4F9C; font-size: 34px; }
            .header p { margin: 0; color: #6B7280; line-height: 1.45; }
            .percent-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin: 22px 0; }
            .percent-tile { background: #FFFFFF; border: 1px solid #DDE5EF; border-top: 5px solid #0B4F9C; border-radius: 8px; padding: 16px; }
            .tile-label { color: #4B5563; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0; }
            .tile-value { font-size: 34px; font-weight: 800; margin-top: 6px; }
            .tile-note { color: #6B7280; font-size: 12px; line-height: 1.35; margin-top: 4px; }
            .graph-grid { display: grid; gap: 16px; margin-bottom: 16px; }
            .two-column { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .one-column { grid-template-columns: 1fr; }
            .graph-panel { background: #FFFFFF; border: 1px solid #DDE5EF; border-radius: 8px; padding: 8px; }
            @media (max-width: 850px) {
                .page { padding: 18px; }
                .percent-grid, .two-column { grid-template-columns: 1fr; }
                .header h1 { font-size: 28px; }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050)
