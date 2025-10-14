
from __future__ import annotations
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, State, dash_table
from datetime import datetime

PRIMARY = "#4c00b0"
BG_DARK = "#0e0f17"
BG_PANEL = "#151826"
TEXT = "#e9e9f2"
SUBTEXT = "#b9bdd1"
BORDER = "rgba(255,255,255,0.08)"

# ---------- Fake static data (for demo) ----------
np.random.seed(7)
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

HIGHLIGHTS = [
    {"initials":"SC","name":"Dr. Sarah Chen (2019)","label":"Top Publication","ago":"2 days ago",
     "text":"Published breakthrough paper in Nature with oRCR of 3.8 (top 1%)."},
    {"initials":"EJ","name":"Dr. Emily Johnson (2020)","label":"Funding Success","ago":"1 week ago",
     "text":"Secured $12M Series A for Immuno‑Therapeutics startup."},
    {"initials":"JW","name":"Dr. James Washington (2018)","label":"NIH Award","ago":"2 weeks ago",
     "text":"Received $3.5M NIH R01 grant to expand research into novel approaches."}
]
COHORT = np.clip(np.random.normal(7.8, 1.2, 1245), 1.0, 9.9)

# ---------- UI helpers ----------
def panel(children, style=None):
    base = {
        "background": BG_PANEL,
        "border": f"1px solid {BORDER}",
        "borderRadius": "16px",
        "padding": "14px 16px",
        "boxShadow": "0 6px 18px rgba(0,0,0,0.25)",
    }
    if style: base.update(style)
    return html.Div(children, style=base)

def kpi(title, value, sub, delta="+0.0"):
    bar_width = 60
    try:
        if isinstance(value, str) and value.endswith("/10"):
            num = float(value.split(" ")[0])
            bar_width = int(min(100, max(8, num/10*100)))
        elif isinstance(value,(int,float)):
            bar_width = int(min(100, max(8, float(value)/10*100)))
    except Exception:
        pass
    return panel([
        html.Div(title, style={"fontSize":"12px","color":SUBTEXT}),
        html.Div(str(value), style={"fontSize":"28px","fontWeight":800,"color":PRIMARY}),
        html.Div(sub, style={"fontSize":"12px","color":SUBTEXT,"marginTop":"2px"}),
        html.Div([
            html.Div(style={"height":"6px","width":"100%","background":"#22263a","borderRadius":"6px"}, children=[
                html.Div(style={"height":"6px","width":f"{bar_width}%","background":PRIMARY,"borderRadius":"6px"})
            ]),
            html.Div(f"▲ {delta} from last year", style={"fontSize":"11px","color":SUBTEXT,"marginTop":"6px"})
        ])
    ], style={"minWidth":"220px"})

def topnav():
    return html.Div([
        html.Div([
            html.Div("sofea", style={"fontWeight":900,"letterSpacing":"0.08em","textTransform":"uppercase"}),
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
    ], style={"display":"flex","justifyContent":"space-between","alignItems":"center","padding":"14px 18px","position":"sticky","top":0,"zIndex":9,"background":BG_DARK,"borderBottom":f"2px solid {PRIMARY}"})

def sidebar_filters():
    return panel([
        html.Div("Filters", style={"fontWeight":800,"marginBottom":"10px"}),
        html.Div([html.Label("Foundation", style={"fontSize":"12px","color":SUBTEXT}), dcc.Dropdown(options=[{"label":"Damon Runyon","value":"DR"}], value="DR")], style={"marginBottom":"8px"}),
        html.Div([html.Label("Award Year", style={"fontSize":"12px","color":SUBTEXT}), dcc.Checklist(options=["2023","2022","2021"], value=["2023","2022","2021"])], style={"marginBottom":"8px"}),
        html.Div([html.Label("Field of Study", style={"fontSize":"12px","color":SUBTEXT}), dcc.RadioItems(options=["All Fields","Oncology","Neuroscience","Immunology"], value="All Fields")], style={"marginBottom":"8px"}),
        html.Button("Reset Filters")
    ])

def histogram_component():
    fig = px.histogram(COHORT, nbins=9)
    fig.update_layout(
        title="SOFEA Score Distribution",
        xaxis_title="SOFEA Score Range",
        yaxis_title="Number of awardees",
        paper_bgcolor=BG_PANEL, plot_bgcolor=BG_PANEL, font_color=TEXT,
        margin=dict(l=10,r=10,t=40,b=10),
    )
    fig.update_traces(marker_color=PRIMARY)
    return dcc.Graph(figure=fig, config={"displayModeBar": False})

def recent_highlights():
    items = []
    for h in HIGHLIGHTS:
        items.append(panel([
            html.Div([
                html.Div(h["initials"], style={"width":"36px","height":"36px","borderRadius":"999px","background":"#232741","display":"grid","placeItems":"center","fontWeight":700}),
                html.Div([
                    html.Div(h["name"], style={"fontWeight":700}),
                    html.Div(h["text"], style={"color":SUBTEXT,"fontSize":"13px"}),
                    html.Div(h["label"] + " • " + h["ago"], style={"color":PRIMARY,"fontSize":"12px","marginTop":"4px"})
                ], style={"display":"grid","gap":"2px"})
            ], style={"display":"grid","gridTemplateColumns":"40px 1fr","gap":"10px","alignItems":"center"})
        ]))
    return html.Div(items, style={"display":"grid","gap":"10px"})

def sofea_score_bar():
    top_df = DF.sort_values("SOFEA", ascending=False)
    fig = px.bar(top_df, x="Scientist", y="SOFEA", title="Top SOFEA — click a bar to drill down")
    fig.update_layout(paper_bgcolor=BG_PANEL, plot_bgcolor=BG_PANEL, font_color=TEXT, margin=dict(l=10,r=10,t=40,b=10))
    fig.update_traces(marker_color=PRIMARY)
    return dcc.Graph(id="scores", figure=fig, config={"displayModeBar": False})

# ---------- Pages ----------
def page_overview():
    return html.Div([
        topnav(),
        html.Div([
            html.Div(sidebar_filters(), style={"width":"260px"}),
            html.Div([
                html.Div("Overview", style={"fontSize":"22px","fontWeight":800,"marginBottom":"10px"}),
                html.Div([
                    kpi("Avg SOFEA Score", "8.7 /10", "STD: ±1.2", "+0.5"),
                    kpi("Avg UQS (Academic)", "7.9 /10", "Based on 1,245 papers", "+0.3"),
                    kpi("Avg TA‑EIS (Economic)", "6.4 /10", "Based on 187 ventures", "+1.2"),
                    kpi("Avg Years Since Award", "4.3 years", "Range: 0.5–12 years", "+0.2"),
                ], style={"display":"grid","gridTemplateColumns":"repeat(4, minmax(220px,1fr))","gap":"14px"}),
                panel([histogram_component()]) ,
                html.Div([
                    kpi("% with oRCR > 1", "78%", "Industry avg: 52%", "+3%"),
                    kpi("% with NIH grants > $1M", "42%", "Industry avg: 23%", "+5%"),
                    kpi("% of companies founded", "15%", "Industry avg: 8%", "+2%"),
                    kpi("Total capital raised", "$1.2B", "Avg per venture: $8.7M", "+$320M"),
                ], style={"display":"grid","gridTemplateColumns":"repeat(4, minmax(220px,1fr))","gap":"14px","marginTop":"10px"}),
                panel([
                    html.Div("Impact Story", style={"fontWeight":800,"marginBottom":"6px"}),
                    html.Div("Your funding powers discoveries that translate into real‑world outcomes — high‑impact publications, NIH grants, startups, and therapies reaching patients.", style={"color":SUBTEXT})
                ], style={"marginTop":"12px"}),
                panel([sofea_score_bar()]),
                html.Div("Recent Highlights", style={"fontWeight":800,"marginTop":"12px","marginBottom":"8px"}),
                recent_highlights(),
            ], style={"flex":"1","display":"grid","gap":"12px"}),
        ], style={"display":"grid","gridTemplateColumns":"260px 1fr","gap":"14px","padding":"14px"})
    ], style={"background":BG_DARK,"color":TEXT,"minHeight":"100vh"})

def page_bucket(title, metric_col):
    fig = px.bar(DF.sort_values(metric_col, ascending=False), x="Scientist", y=metric_col, title=f"{title} — Awardees")
    fig.update_layout(paper_bgcolor=BG_PANEL, plot_bgcolor=BG_PANEL, font_color=TEXT, margin=dict(l=10,r=10,t=40,b=10))
    fig.update_traces(marker_color=PRIMARY)
    table = dash_table.DataTable(
        data=DF[["Scientist","Field","Award_Year",metric_col]].to_dict("records"),
        columns=[{"name":c,"id":c} for c in ["Scientist","Field","Award_Year",metric_col]],
        style_table={"overflowX":"auto"},
        style_header={"backgroundColor":"#1b1f33","fontWeight":"700"},
        style_cell={"backgroundColor":BG_PANEL,"color":TEXT,"border":f"1px solid {BORDER}","padding":"8px"}
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
    ], style={"background":BG_DARK,"color":TEXT,"minHeight":"100vh"})

def page_explorer():
    table = dash_table.DataTable(
        id="explorer-table",
        data=DF.to_dict("records"),
        columns=[{"name":c,"id":c} for c in DF.columns],
        row_selectable="single",
        style_table={"overflowX":"auto"},
        style_header={"backgroundColor":"#1b1f33","fontWeight":"700"},
        style_cell={"backgroundColor":BG_PANEL,"color":TEXT,"border":f"1px solid {BORDER}","padding":"8px"},
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
    ], style={"background":BG_DARK,"color":TEXT,"minHeight":"100vh"})

def page_detail(scientist: str):
    row = DF[DF["Scientist"]==scientist]
    if row.empty:
        return html.Div([topnav(), html.Div("Scientist not found", style={"padding":"24px"})], style={"background":BG_DARK,"color":TEXT,"minHeight":"100vh"})
    r = row.iloc[0]
    df_break = pd.DataFrame({"Bucket":["AIS","EIS","HIS","SIS"],"Score":[r["AIS"],r["EIS"],r["HIS"],r["SIS"]]})
    fig_break = px.bar(df_break, x="Bucket", y="Score", title=f"Bucket Breakdown — {scientist}")
    fig_break.update_layout(paper_bgcolor=BG_PANEL, plot_bgcolor=BG_PANEL, font_color=TEXT, margin=dict(l=10,r=10,t=40,b=10))
    fig_break.update_traces(marker_color=PRIMARY)
    tyears = list(range(int(r["First_Publication_Year"]), int(r["Award_Year"]) + 4))
    timeline_df = pd.DataFrame({
        "Year": tyears,
        "Publications": np.random.poisson(1.2, len(tyears)).cumsum(),
        "Grants": np.clip(np.random.poisson(0.6, len(tyears)).cumsum(), 0, None),
    })
    fig_timeline = px.line(timeline_df, x="Year", y=["Publications","Grants"], title="Career Timeline (mock)")
    fig_timeline.update_layout(paper_bgcolor=BG_PANEL, plot_bgcolor=BG_PANEL, font_color=TEXT, margin=dict(l=10,r=10,t=40,b=10))

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
                html.Div([
                    kpi("SOFEA Score", f"{r['SOFEA']}", "Composite", "+0.1"),
                    kpi("AIS", f"{int(r['AIS'])}", "Academic Impact", "+2"),
                    kpi("EIS", f"{int(r['EIS'])}", "Economic Impact", "+1"),
                    kpi("HIS", f"{int(r['HIS'])}", "Health Impact", "+1"),
                    kpi("SIS", f"{int(r['SIS'])}", "Social Impact", "+0"),
                ], style={"display":"grid","gridTemplateColumns":"repeat(5, minmax(200px,1fr))","gap":"12px"}),
                panel([dcc.Graph(figure=fig_break, config={"displayModeBar": False})]),
                panel([dcc.Graph(figure=fig_timeline, config={"displayModeBar": False})]),
                panel([
                    html.Div("Publications (mock table)", style={"fontWeight":800,"marginBottom":"6px"}),
                    dash_table.DataTable(
                        data=pd.DataFrame({
                            "Year":[int(r["First_Publication_Year"]) + i for i in range(5)],
                            "Journal":["Nature","Cancer Cell","Cell Reports","PNAS","Science Advances"],
                            "oRCR": np.round(np.random.uniform(0.8,4.1,5),2)
                        }).to_dict("records"),
                        columns=[{"name":c,"id":c} for c in ["Year","Journal","oRCR"]],
                        style_table={"overflowX":"auto"},
                        style_header={"backgroundColor":"#1b1f33","fontWeight":"700"},
                        style_cell={"backgroundColor":BG_PANEL,"color":TEXT,"border":f"1px solid {BORDER}","padding":"8px"}
                    )
                ])
            ], style={"flex":"1","display":"grid","gap":"12px"}),
        ], style={"display":"grid","gridTemplateColumns":"260px 1fr","gap":"14px","padding":"14px"})
    ], style={"background":BG_DARK,"color":TEXT,"minHeight":"100vh"})

# ---------- App & routing ----------
app = Dash(__name__, suppress_callback_exceptions=True, title="SOFEA — Mockup")
server = app.server
app.layout = html.Div([dcc.Location(id="url"), html.Div(id="router")])

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

@app.callback(Output("url","href"), Input("scores","clickData"), prevent_initial_call=True)
def bar_click(cd):
    if not cd: return dash.no_update
    name = cd["points"][0]["x"]
    return f"/detail/{name}"

app.index_string = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>SOFEA — Mockup</title>
<style>
  html,body,#root {{ height:100%; margin:0; }}
  * {{ box-sizing:border-box; font-family: ui-sans-serif, -apple-system, Segoe UI, Roboto, Helvetica, Arial; }}
  a.navlink {{ color:{TEXT}; text-decoration:none; padding:6px 8px; border-radius:10px; }}
  a.navlink:hover {{ background:{PRIMARY}; color:white; }}
  button {{ background:{PRIMARY}; color:white; border:none; padding:8px 10px; border-radius:12px; font-weight:700; cursor:pointer; }}
</style>
</head>
<body style='background:{BG_DARK}; color:{TEXT};'>
  <div id='root'>{{app_entry}}</div>
  {{config}} {{scripts}} {{renderer}}
</body>
</html>
"""

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)
