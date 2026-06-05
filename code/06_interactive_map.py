import os
import pandas as pd
import plotly.graph_objects as go
 
#paths
DATA_DIR = "../data"
MERGED   = os.path.join(DATA_DIR, "merged_panel.csv")
 
#load merged panel, keep 2000-2023
panel = pd.read_csv(MERGED)
panel = panel[(panel["year"] >= 2000) & (panel["year"] <= 2023)].copy()
 
 
#interactive map (HTML): Plotly choropleth, 2023 snapshot, toggle between metrics
df1 = panel[panel["year"] == 2023][["country_text_id", "country_name",
        "v2x_freexp_altinf", "v2mecenefm", "v2csreprss", "e_pelifeex"]].dropna(
        subset=["v2x_freexp_altinf"]).copy()
 
#four metrics the user can toggle between via dropdown
metrics = [
    ("v2x_freexp_altinf", "Free Expression (0-1)",             "RdYlGn", 0,    1),
    ("e_pelifeex",        "Life Expectancy (years)",           "RdYlGn", 50,   86),
    ("v2mecenefm",        "Media Censorship (higher = freer)", "RdYlGn", -3.1, 3.5),
    ("v2csreprss",        "Civil Society Freedom",             "RdYlGn", -3.8, 3.2),
]
 
#one choropleth trace per metric; only the first is visible by default
fig = go.Figure()
for i, (col, label, scale, zmin, zmax) in enumerate(metrics):
    sub = df1.dropna(subset=[col])
    fig.add_trace(go.Choropleth(
        locations=sub["country_text_id"], locationmode="ISO-3", z=sub[col],
        text=sub["country_name"], colorscale=scale, zmin=zmin, zmax=zmax,
        colorbar_title=label, visible=(i == 0),
        hovertemplate="<b>%{text}</b><br>" + label + ": %{z}<extra></extra>"))
 
#dropdown buttons: show only the selected layer and update the title
buttons = [
    dict(label=label, method="update",
         args=[{"visible": [j == i for j in range(len(metrics))]}, {"title": label}])
    for i, (col, label, *rest) in enumerate(metrics)
]
 
fig.update_layout(
    updatemenus=[dict(buttons=buttons, direction="down", x=0.01, xanchor="left",
                      y=1.08, yanchor="top", bgcolor="white", bordercolor="#ccc")],
    geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
    width=950, height=550,
    title=dict(text="Freedom of Expression Across Countries (2023)", x=0.5, y=0.98),
    margin=dict(t=120, b=10, l=10, r=10))
 
os.makedirs("../docs", exist_ok=True)
fig.write_html("../docs/democracy_health_map.html")
print("saved ../docs/democracy_health_map.html")
