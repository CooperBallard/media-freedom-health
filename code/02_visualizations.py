#visualization 2: forest plot for the press freedom vs democracy contrast

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
from pathlib import Path
 
#load merged panel (one row per country-year) and keep 2000-2023
DATA_DIR = Path("~/Desktop/QSS20-S26/public_data").expanduser()
panel = pd.read_csv(DATA_DIR / "merged_panel.csv")
panel = panel[(panel["year"] >= 2000) & (panel["year"] <= 2023)].copy()
 
#0 is a missing placeholder, not a real life expectancy
panel.loc[panel["e_pelifeex"] == 0, "e_pelifeex"] = np.nan
 
#log GDP: income has diminishing returns for health
if "log_gdppc" not in panel.columns:
    panel["log_gdppc"] = np.where(panel["e_gdppc"] > 0, np.log(panel["e_gdppc"]), np.nan)
 
#all three models: OLS, year fixed effects via C(year), SEs clustered by country
 
#model 1: press freedom + wealth
d_pf = panel.dropna(
    subset=["e_pelifeex", "v2x_freexp_altinf", "log_gdppc"]
).copy()
m_pf = smf.ols(
    "e_pelifeex ~ v2x_freexp_altinf + log_gdppc + C(year)",
    data=d_pf
).fit(
    cov_type="cluster",
    cov_kwds={"groups": d_pf["country_text_id"]}
)
 
#model 2: democracy + wealth
d_dem_wealth = panel.dropna(
    subset=["e_pelifeex", "v2x_polyarchy", "log_gdppc"]
).copy()
m_dem_wealth = smf.ols(
    "e_pelifeex ~ v2x_polyarchy + log_gdppc + C(year)",
    data=d_dem_wealth
).fit(
    cov_type="cluster",
    cov_kwds={"groups": d_dem_wealth["country_text_id"]}
)
 
#model 3: democracy + wealth + rule of law + corruption (the one that survives)
d_dem_full = panel.dropna(
    subset=["e_pelifeex", "v2x_polyarchy", "log_gdppc", "e_wbgi_rle", "e_wbgi_cce"]
).copy()
m_dem_full = smf.ols(
    "e_pelifeex ~ v2x_polyarchy + log_gdppc + e_wbgi_rle + e_wbgi_cce + C(year)",
    data=d_dem_full
).fit(
    cov_type="cluster",
    cov_kwds={"groups": d_dem_full["country_text_id"]}
)
 
#pull coef, 95% CI, p-value, and N for one predictor (one plot row)
def coef_row(model, var, label):
    ci_low, ci_high = model.conf_int().loc[var]
    return {
        "label": label,
        "coef": model.params[var],
        "ci_low": ci_low,
        "ci_high": ci_high,
        "pval": model.pvalues[var],
        "n": int(model.nobs),
    }
 
results = pd.DataFrame([
    coef_row(m_pf, "v2x_freexp_altinf", "Press freedom\n(+ wealth)"),
    coef_row(m_dem_wealth, "v2x_polyarchy", "Democracy\n(+ wealth)"),
    coef_row(m_dem_full, "v2x_polyarchy", "Democracy\n(+ wealth, rule of law,\ncorruption)"),
])
 
print(results)
 
print("\nSample sizes:")
print("Press freedom + wealth:",
      int(m_pf.nobs), "obs,",
      d_pf["country_text_id"].nunique(), "countries")
print("Democracy + wealth:",
      int(m_dem_wealth.nobs), "obs,",
      d_dem_wealth["country_text_id"].nunique(), "countries")
print("Democracy full:",
      int(m_dem_full.nobs), "obs,",
      d_dem_full["country_text_id"].nunique(), "countries")
 
#forest plot: dot = estimate, line = 95% CI, blue = significant, grey = not
fig, ax = plt.subplots(figsize=(11, 5))
y_pos = [2, 1, 0]
 
for y, (_, row) in zip(y_pos, results.iterrows()):
    sig = row["pval"] < 0.05
    color = "#1f77b4" if sig else "#9aa0a6"
 
    #95% CI line
    ax.plot(
        [row["ci_low"], row["ci_high"]],
        [y, y],
        color=color,
        linewidth=3,
        solid_capstyle="round",
        zorder=2,
    )
    #point estimate
    ax.plot(
        row["coef"],
        y,
        "o",
        color=color,
        markersize=13,
        markeredgecolor="white",
        markeredgewidth=2,
        zorder=3,
    )
 
    if row["pval"] < 0.001:
        p_text = "p < 0.001"
    else:
        p_text = f"p = {row['pval']:.3f}"
 
    if sig:
        label_text = f"{row['coef']:.1f} yrs  ({p_text})"
        text_color = "black"
        weight = "bold"
    else:
        label_text = f"{row['coef']:.1f} yrs  (not significant)"
        text_color = "#666666"
        weight = "normal"
 
    ax.text(
        row["coef"] - 1.55 if sig else row["coef"] - 1.35,
        y + 0.22,
        label_text,
        va="center",
        fontsize=12,
        fontweight=weight,
        color=text_color,
    )
 
#zero line: CIs that cross it aren't distinguishable from no association
ax.axvline(0, color="#555555", linestyle="--", linewidth=1.2)
 
ax.set_yticks(y_pos)
ax.set_yticklabels(results["label"], fontsize=12)
ax.set_xlabel("Association with life expectancy (years)", fontsize=13)
ax.set_title(
    "Democracy Predicts Life Expectancy; Press Freedom Does Not",
    fontsize=16,
    fontweight="bold",
    pad=15,
)
ax.set_xlim(-2, 10)
ax.set_ylim(-0.6, 2.6)
ax.xaxis.grid(True, alpha=0.2)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
 
#method note + takeaway, inside the plot
ax.text(
    0.5,
    -0.48,
    "Cross-country estimates, clustered by country. Press freedom's interval crosses zero.",
    fontsize=9,
    color="#888888",
)
 
plt.tight_layout()
OUT_PATH = DATA_DIR / "viz_xc_contrast.png"
plt.savefig(OUT_PATH, dpi=300, bbox_inches="tight")
plt.show()

#visualization 3: Interactive Plotly choropleth map

import plotly.graph_objects as go
#get 2023 snapshot from the panel
df1 = panel[panel["year"] == 2023][["country_text_id", "country_name",
    "v2x_freexp_altinf", "v2mecenefm", "v2csreprss", "e_pelifeex"]].dropna(
    subset=["v2x_freexp_altinf"]).copy()

#build hover text showing all metrics for each country
hover = (df4["country_name"] +
    "<br>Free Expression: " + df4["v2x_freexp_altinf"].round(2).astype(str) +
    "<br>Media Censorship: " + df4["v2mecenefm"].round(1).astype(str) +
    "<br>Civil Society: " + df4["v2csreprss"].round(1).astype(str) +
    "<br>Life Expectancy: " + df4["e_pelifeex"].round(1).astype(str) + " yrs")

#define four metrics the user can toggle between via dropdown
metrics = [
    ("v2x_freexp_altinf", "Free Expression (0-1)",            "RdYlGn", 0,    1),
    ("e_pelifeex",        "Life Expectancy (years)",          "RdYlGn", 50,   86),
    ("v2mecenefm",        "Media Censorship (higher = freer)", "RdYlGn", -3.1, 3.5),
    ("v2csreprss",        "Civil Society Freedom",            "RdYlGn", -3.8, 3.2),
]

#add one choropleth trace per metric; only first is visible by default

fig = go.Figure()
for i, (col, label, scale, zmin, zmax) in enumerate(metrics):
    sub = df1.dropna(subset=[col])              #drop missing for this metric
    fig.add_trace(go.Choropleth(
        locations=sub["country_text_id"],       #ISO-3 codes
        locationmode="ISO-3",                    #tells Plotly these are countries
        z=sub[col],                              #the value that sets the color
        text=sub["country_name"],               #shows up on hover
        colorscale=scale, zmin=zmin, zmax=zmax,  #straight from your tuple
        colorbar_title=label,
        visible=(i == 0),                        #only the FIRST layer starts visible
        hovertemplate="<b>%{text}</b><br>" + label + ": %{z}<extra></extra>",
    ))

#dropdown buttons using list comprehension to toggle visibility
buttons = [
    dict(label=label, method="update",
         args=[{"visible": [j == i for j in range(len(metrics))]},  #show only layer i
               {"title": label}])                                   #update the title too
    for i, (col, label, *rest) in enumerate(metrics)
]

#configure map layout with dropdown menu
fig.update_layout(
    updatemenus=[dict(buttons=buttons, direction="down",
        x=0.01, xanchor="left", y=1.08, yanchor="top",
        bgcolor="white", bordercolor="#ccc")],
    geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
    width=950, height=550,
    title=dict(text="Freedom of Expression Across Countries (2023)", x=0.5, y=0.98),
    margin=dict(t=120, b=10, l=10, r=10))

#save as interactive HTML file
import os
os.makedirs("docs", exist_ok=True)
fig.write_html("docs/democracy_health_map.html")
