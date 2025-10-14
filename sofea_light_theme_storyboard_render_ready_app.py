"""
SOFEA — Light‑Theme Storyboard (Render‑Ready)

Purpose
-------
High‑fidelity mockup matching the storyboard flow with static data:
Overview → AIS → EIS → HIS → SIS → Awardee Explorer → Scientist Detail.

Design
------
• Light theme, #4c00b0 accents, no photos.
• Animated Impact Highlights strip on Overview.
• Click logic for drilldowns.

How to run
----------
$ pip install -r requirements.txt
$ python app.py
# open http://127.0.0.1:8050

Render
------
• Start command: gunicorn app:server
• runtime.txt: 3.11.9
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from datetime import datetime
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, State, dash_table, callback_context

PRIMARY = "#4c00b0"
BG = "#faf9ff"  # subtle warm light
PANEL = "#ffffff"
TEXT = "#1e1b2e"
SUBTEXT = "#605a78"
BORDER = "#ece7ff"

# ---------------------------
# Static Fake Data (presentation quality)
# ---------------------------
np.random.seed(11)
SCIENTISTS = [
    "Dr. Sarah Chen", "Dr. Emily Johnson", "Dr. James Washington",
    "Dr. Diego Rossi", "Dr. Elena Park", "Dr. Farah Khan",
    "Dr. Miguel Alvarez", "Dr. Priya Sharma", "Dr. Noah Lee", "Dr. Lila Patel",
]
award_year = np.random.choice([2018,2019,2020,2021,2022,2023], size=len(SCIENTISTS))
first_pub = award_year - np.random.choice([2,3,4,5,6], size=len(SCIENTISTS))
sofea = np.clip(np.random.normal(7.9, 0.8, len(SCIENTISTS)), 5.2, 9.6)
AIS = np.clip(np.random.normal(32, 6, len(SCIENTISTS)), 18, 48)
EIS = np.clip(np.random.normal(18, 5, len(SCIENTISTS)), 6, 30)
HIS = np.clip(np.random.normal(20, 3, len(SCIENTISTS)), 12, 26)
SIS = np.clip(np.random.normal(9, 2, len(SCIENTISTS)), 4, 14)
nih_grants = np.random.choice([1,2,3,4], size=len(SCIENTISTS), p=[0.35,0.4,0.2,0.05])
companies = np.random.choice([0,1,2], size=len(SCIENTISTS), p=[0.7,0.25,0.05])
capital = (companies * np.random.choice([3.5,8.7,12.1], size=len(SCIENTISTS)))

DF = pd.DataFrame({
    "Scientist": SCIENTISTS,
    "Award_Year": award_year,
    "First_Publication_Year": first_pub,
    "SOFEA": np.round(sofea,1),
    "AIS": AIS.astype(int),
    "EIS": EIS.astype(int),
    "HIS": HIS.astype(int),
    "SIS": SIS.astype(int),
    "NIH_Grants": nih_grants,
    "Companies": companies,
    "Capital_M_USD": np.round(capital,1),
    "Field": np.random.choice(["Oncology","Neuroscience","Immunology"], size=len(SCIENTISTS))
})
DF["Years_Since_Award"] = datetime.now().year - DF["Award_Year"]

COHORT = np.clip(np.random.normal(7.8, 1.2, 1245), 1.0, 9.9)

IMPACT_HIGHLIGHTS = [
    "1,245 awardees supported",
    "$1.2B capital raised",
    "6 FDA‑approved therapies",
    "78% above national oRCR",
    "42% in leadership roles",
]

# ---------------------------
# UI helpers
# ---------------------------

def panel(children, style=None):
    base = {
        "background": PANEL,
        "border": f"1px solid {BORDER}",
        "borderRadius": "16px",
        "padding": "14px 16px",
        "boxShadow": "0 6px 18px rgba(0,0,0,0.06)",
    }
    if style: base.update(style)
    return html.Div(children, style=base)


def kpi(title, value, sub, delta=None):
    bar_width = 60
    try:
        if isinstance(value, str) and value.endswith("/10"):
            num = float(value.split(" ")[0])
            bar_width = int(min(100, max(8, num/10*100)))
        elif isinstance(value,(int,float)):
            bar_width = int(min(100, max(8, float(value)/10*100)))
    except Exception:
        pass
    bar = html.Div(style={"height":"6px","width":"100%","background":"#efeaff","borderRadius":"6px"}, children=[
        html.Div(style={"height":"6px","width":f"{bar_width}%","background":PRIMARY,"borderRadius":"6px"})
    ])
    delta_el = html.Div(delta, style={"fontSize":"11px","color":SUBTEXT,"marginTop":"6px"}) if delta else None
    return panel([
        html.Div(title, style={"fontSize":"12px","color":SUBTEXT}),
        html.Div(str(value), style={"fontSize":"28px","fontWeight":800,"color":PRIMARY}),
        html.Div(sub, style={"fontSize":"12px","color":SUBTEXT,"marginTop":"2px"}),
        bar,
        delta_el
    ], style={"minWidth":"220px"})


def topnav():
    return html.Div([
        html.Div([
            html.Div("SOFEA", style={"fontWeight":900,"letterSpacing":"0.08em","textTransform":"uppercase", "color":PRIMARY}),
            html.Div("Damon Runyon Impact", style={"color":SUBTEXT,"fontSize":"12px"})
        ]),
        html.Div([
            dcc.Link("Overview", href="/", className="navlink"),
            dcc.Link("Academic Impact", href="/ais", className="navlink"),
            dcc.Link("Economic Impact", href="/eis", className="navlink"),
            dcc.Link("Health Impact", href="/his", className="navlink"),
            dcc.Link("Social Impact", href="/sis", className="navlink"),
            dcc.Link("Awardee Explorer", href="/explorer", className="navlink")
        ], style={"display":"flex","gap":"18px","alignItems":"center"})
    ], style={"display":"flex","justifyContent":"space-between","alignItems":"center","padding":"14px 18px","position":"sticky","top":0,"zIndex":9,"background":BG,"borderBottom":f"2px solid {PRIMARY}"})


def histogram_component():
    fig = px.histogram(COHORT, nbins=9)
    fig.update_layout(
        title="SOFEA Score Distribution",
        xaxis_title="SOFEA Score Range",
        yaxis_title="Number of awardees",
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font_color=TEXT,
        margin=dict(l=10,r=10,t=40,b=10),
    )
    fig.update_traces(marker_color=PRIMARY)
    return dcc.Graph(figure=fig, config={"displayModeBar": False})


def sidebar_filters():
    return panel([
        html.Div("Filters", style={"fontWeight":800,"marginBottom":"10px"}),
        html.Div([html.Label("Foundation", style={"fontSize":"12px","color":SUBTEXT}), dcc.Dropdown(options=[{"label":"Damon Runyon","value":"DR"}], value="DR")], style={"marginBottom":"8px"}),
        html.Div([html.Label("Award Year", style={"fontSize":"12px","color":SUBTEXT}), dcc.Checklist(options=["2023","2022","2021"], value=["2023","2022","2021"])], style={"marginBottom":"8px"}),
        html.Div([html.Label("Field of Study", style={"fontSize":"12px","color":SUBTEXT}), dcc.RadioItems(options=["All Fields","Oncology","Neuroscience","Immunology"], value="All Fields")], style={"marginBottom":"8px"}),
        html.Button("Reset Filters")
    ])


# ---------------------------
# Pages
# ---------------------------

def page_overview():
    # Animated highlights: rotate every 2.5s
    return html.Div([
        topnav(),
        dcc.Interval(id="hi-interval", interval=2500, n_intervals=0),
        dcc.Store(id="hi-index", data=0),
        html.Div([
            html.Div(sidebar_filters(), style={"width":"260px"}),
            html.Div([
                html.Div("Overview", style={"fontSize":"22px","fontWeight":800,"marginBottom":"10px"}),

                # KPI Row
                html.Div([
                    kpi("Academic Impact (AIS)", "8.1 /10", "Citations & quality", "+0.3"),
                    kpi("Economic Impact (EIS)", "6.6 /10", "Ventures & capital", "+1.1"),
                    kpi("Health Impact (HIS)", "7.2 /10", "Trials & therapies", "+0.5"),
                    kpi("Social Impact (SIS)", "6.9 /10", "Leadership & outreach", "+0.2"),
                ], style={"display":"grid","gridTemplateColumns":"repeat(4, minmax(220px,1fr))","gap":"14px"}),

                # Animated Impact Highlights strip
                panel([
                    html.Div("Impact Highlights", style={"fontWeight":800,"marginBottom":"6px"}),
                    html.Div(id="impact-headline", style={"fontSize":"18px","fontWeight":700,"color":TEXT})
                ]),

                panel([histogram_component()]),

                # Secondary KPIs (text-only callouts)
                html.Div([
                    kpi("% with oRCR > 1", "78%", "Above field norm"),
                    kpi("% with NIH grants > $1M", "42%", "Depth of support"),
                    kpi("% who founded companies", "15%", "Entrepreneurial reach"),
                    kpi("Total capital raised", "$1.2B", "All ventures"),
                ], style={"display":"grid","gridTemplateColumns":"repeat(4, minmax(220px,1fr))","gap":"14px"}),

                # Top SOFEA bars (clickable)
                panel([sofea_score_bar()]),

                # Recent Highlights (text‑only)
                panel([
                    html.Div("Recent Highlights", style={"fontWeight":800,"marginBottom":"6px"}),
                    html.Ul([
                        html.Li("FDA approval announced for awardee‑linked therapy (Q3 2024)"),
                        html.Li("Awardee‑founded biotech closes Series C at $180M"),
                        html.Li("Multi‑center Phase II trial launches in immuno‑oncology"),
                    ], style={"margin":"0", "paddingLeft":"18px", "color":SUBTEXT})
                ])
            ], style={"flex":"1","display":"grid","gap":"12px"}),
        ], style={"display":"grid","gridTemplateColumns":"260px 1fr","gap":"14px","padding":"14px"})
    ], style={"background":BG,"color":TEXT,"minHeight":"100vh"})


def page_bucket(title, metric_col):
    fig = px.bar(DF.sort_values(metric_col, ascending=False), x="Scientist", y=metric_col, title=f"{title} — Awardees")
    fig.update_layout(paper_bgcolor=PANEL, plot_bgcolor=PANEL, font_color=TEXT, margin=dict(l=10,r=10,t=40,b=10))
    fig.update_traces(marker_color=PRIMARY)
    table = dash_table.DataTable(
        data=DF[["Scientist","Field","Award_Year",metric_col]].to_dict("records"),
        columns=[{"name":c,"id":c} for c in ["Scientist","Field","Award_Year",metric_col]],
        style_table={"overflowX":"auto"},
        style_header={"backgroundColor":"#f4f0ff","fontWeight":"700","color":TEXT},
        style_cell={"backgroundColor":PANEL,"color":TEXT,"border":f"1px solid {BORDER}","padding":"8px"}
    )
    return html.Div([
        topnav(),
        html.Div([
            html.Div(sidebar_filters(), style={"width":"260px"}),
            html.Div([
                html.Div(title, style={"fontSize":"22px","fontWeight":800,"marginBottom":"10px"}),
                panel([dcc.Graph(figure=fig, config={"displayModeBar": False})]),
                panel([table])
            ], style={"flex":"1","display":"grid","gap":"12px"}),
        ], style={"display":"grid","gridTemplateColumns":"260px 1fr","gap":"14px","padding":"14px"})
    ], style={"background":BG,"color":TEXT,"minHeight":"100vh"})


def page_explorer():
    table = dash_table.DataTable(
        id="explorer-table",
        data=DF.to_dict("records"),
        columns=[{"name":c,"id":c} for c in DF.columns],
        row_selectable="single",
        style_table={"overflowX":"auto"},
        style_header={"backgroundColor":"#f4f0ff","fontWeight":"700","color":TEXT},
        style_cell={"backgroundColor":PANEL,"color":TEXT,"border":f"1px solid {BORDER}","padding":"8px"},
        page_size=10
    )
    return html.Div([
        topnav(),
        html.Div([
            html.Div(sidebar_filters(), style={"width":"260px"}),
            html.Div([
                html.Div("Awardee Explorer", style={"fontSize":"22px","fontWeight":800,"marginBottom":"10px"}),
                panel([table])
            ], style={"flex":"1","display":"grid","gap":"12px"}),
        ], style={"display":"grid","gridTemplateColumns":"260px 1fr","gap":"14px","padding":"14px"})
    ], style={"background":BG,"color":TEXT,"minHeight":"100vh"})


def page_detail(scientist: str):
    row = DF[DF["Scientist"]==scientist]
    if row.empty:
        return html.Div([topnav(), html.Div("Scientist not found", style={"padding":"24px"})], style={"background":BG,"color":TEXT,"minHeight":"100vh"})
    r = row.iloc[0]

    # Breakdown chart
    df_break = pd.DataFrame({"Bucket":["AIS","EIS","HIS","SIS"],"Score":[r["AIS"],r["EIS"],r["HIS"],r["SIS"]]})
    fig_break = px.bar(df_break, x="Bucket", y="Score", title=f"Bucket Breakdown — {scientist}")
    fig_break.update_layout(paper_bgcolor=PANEL, plot_bgcolor=PANEL, font_color=TEXT, margin=dict(l=10,r=10,t=40,b=10))
    fig_break.update_traces(marker_color=PRIMARY)

    # Timeline (mock publications & grants)
    tyears = list(range(int(r["First_Publication_Year"]), int(r["Award_Year"]) + 4))
    timeline_df = pd.DataFrame({
        "Year": tyears,
        "Publications": np.random.poisson(1.2, len(tyears)).cumsum(),
        "Grants": np.clip(np.random.poisson(0.6, len(tyears)).cumsum(), 0, None),
    })
    fig_timeline = px.line(timeline_df, x="Year", y=["Publications","Grants"], title="Career Timeline (mock)")
    fig_timeline.update_layout(paper_bgcolor=PANEL, plot_bgcolor=PANEL, font_color=TEXT, margin=dict(l=10,r=10,t=40,b=10))

    # Detail tables
    pubs_table = dash_table.DataTable(
        data=pd.DataFrame({
            "Year":[int(r["First_Publication_Year"]) + i for i in range(5)],
            "Journal":["Nature","Cancer Cell","Cell Reports","PNAS","Science Advances"],
            "oRCR": np.round(np.random.uniform(0.8,4.1,5),2)
        }).to_dict("records"),
        columns=[{"name":c,"id":c} for c in ["Year","Journal","oRCR"]],
        style_table={"overflowX":"auto"},
        style_header={"backgroundColor":"#f4f0ff","fontWeight":"700","color":TEXT},
        style_cell={"backgroundColor":PANEL,"color":TEXT,"border":f"1px solid {BORDER}","padding":"8px"}
    )

    grants_table = dash_table.DataTable(
        data=pd.DataFrame({
            "Year":[int(r["Award_Year"]) + i for i in range(3)],
            "Agency":["NIH R01","NCI","SBIR"],
            "Amount_USD":[3500000, 1200000, 500000]
        }).to_dict("records"),
        columns=[{"name":c,"id":c} for c in ["Year","Agency","Amount_USD"]],
        style_table={"overflowX":"auto"},
        style_header={"backgroundColor":"#f4f0ff","fontWeight":"700","color":TEXT},
        style_cell={"backgroundColor":PANEL,"color":TEXT,"border":f"1px solid {BORDER}","padding":"8px"}
    )

    ventures_table = dash_table.DataTable(
        data=pd.DataFrame({
            "Company":["OncoNovaX","ImmuneBridge"],
            "Stage":["Series B","Series A"],
            "Raised_USD_M":[88, 24]
        }).to_dict("records"),
        columns=[{"name":c,"id":c} for c in ["Company","Stage","Raised_USD_M"]],
        style_table={"overflowX":"auto"},
        style_header={"backgroundColor":"#f4f0ff","fontWeight":"700","color":TEXT},
        style_cell={"backgroundColor":PANEL,"color":TEXT,"border":f"1px solid {BORDER}","padding":"8px"}
    )

    return html.Div([
        topnav(),
        html.Div([
            html.Div(sidebar_filters(), style={"width":"260px"}),
            html.Div([
                html.Div([
                    html.Div([
                        html.Div(scientist, style={"fontSize":"24px","fontWeight":900}),
                        html.Div(f"Field: {r['Field']} • Award Year: {int(r['Award_Year'])}", style={"color":SUBTEXT}),
                    ]),
                    dcc.Link("← Back to Overview", href="/", style={"color":PRIMARY,"textDecoration":"none","fontWeight":700})
                ], style={"display":"flex","justifyContent":"space-between","alignItems":"baseline","marginBottom":"10px"}),

                # KPI mini row (no bars here to save space)
                html.Div([
                    kpi("SOFEA Score", f"{r['SOFEA']}", "Composite"),
                    kpi("AIS", f"{int(r['AIS'])}", "Academic"),
                    kpi("EIS", f"{int(r['EIS'])}", "Economic"),
                    kpi("HIS", f"{int(r['HIS'])}", "Health"),
                    kpi("SIS", f"{int(r['SIS'])}", "Social"),
                ], style={"display":"grid","gridTemplateColumns":"repeat(5, minmax(200px,1fr))","gap":"12px"}),

                panel([dcc.Graph(figure=fig_break, config={"displayModeBar": False})]),
                panel([dcc.Graph(figure=fig_timeline, config={"displayModeBar": False})]),

                panel([
                    html.Div("Publications", style={"fontWeight":800,"marginBottom":"6px"}),
                    pubs_table
                ]),
                panel([
                    html.Div("Grants", style={"fontWeight":800,"marginBottom":"6px"}),
                    grants_table
                ]),
                panel([
                    html.Div("Ventures", style={"fontWeight":800,"marginBottom":"6px"}),
                    ventures_table
                ]),
            ], style={"flex":"1","display":"grid","gap":"12px"}),
        ], style={"display":"grid","gridTemplateColumns":"260px 1fr","gap":"14px","padding":"14px"})
    ], style={"background":BG,"color":TEXT,"minHeight":"100vh"})


def sofea_score_bar():
    top_df = DF.sort_values("SOFEA", ascending=False)
    fig = px.bar(top_df, x="Scientist", y="SOFEA", title="Top SOFEA — click a bar to drill down")
    fig.update_layout(paper_bgcolor=PANEL, plot_bgcolor=PANEL, font_color=TEXT, margin=dict(l=10,r=10,t=40,b=10))
    fig.update_traces(marker_color=PRIMARY)
    return dcc.Graph(id="scores", figure=fig, config={"displayModeBar": False})

# ---------------------------
# App + Routing
# ---------------------------
app = Dash(__name__, suppress_callback_exceptions=True, title="SOFEA — Storyboard")
server = app.server

app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div(id="router")
])

@app.callback(Output("router","children"), Input("url","pathname"))
def route(path):
    if path is None or path == "/":
        return page_overview()
    if path.startswith("/detail/"):
        name = path.split("/detail/")[-1].replace("%20"," ")
        return page_detail(name)
    if path == "/ais":
        return page_bucket("Academic Impact (AIS)", "AIS")
    if path == "/eis":
        return page_bucket("Economic Impact (EIS)", "EIS")
    if path == "/his":
        return page_bucket("Health Impact (HIS)", "HIS")
    if path == "/sis":
        return page_bucket("Social Impact (SIS)", "SIS")
    if path == "/explorer":
        return page_explorer()
    return page_overview()

# bar → detail
@app.callback(Output("url","href"), Input("scores","clickData"), prevent_initial_call=True)
def bar_click(cd):
    if not cd: return dash.no_update
    name = cd["points"][0]["x"]
    return f"/detail/{name}"

# Animated highlights logic
@app.callback(Output("impact-headline","children"), Output("hi-index","data"), Input("hi-interval","n_intervals"), State("hi-index","data"))
def rotate_highlights(n, idx):
    i = (idx + 1) % len(IMPACT_HIGHLIGHTS)
    return IMPACT_HIGHLIGHTS[i], i

# Minimal CSS for nav links / body
app.index_string = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>SOFEA — Storyboard</title>
<style>
  html,body,#root {{ height:100%; margin:0; background:{BG}; color:{TEXT}; }}
  * {{ box-sizing:border-box; font-family: Inter, ui-sans-serif, -apple-system, Segoe UI, Roboto, Helvetica, Arial; }}
  a.navlink {{ color:{TEXT}; text-decoration:none; padding:6px 8px; border-radius:10px; }}
  a.navlink:hover {{ background:{PRIMARY}; color:white; }}
  button {{ background:{PRIMARY}; color:white; border:none; padding:8px 10px; border-radius:12px; font-weight:700; cursor:pointer; }}
</style>
</head>
<body>
  <div id='root'>{{app_entry}}</div>
  {{config}} {{scripts}} {{renderer}}
</body>
</html>
"""

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)
