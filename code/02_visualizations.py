import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
 
#paths: adjust these to wherever your files live
DATA_DIR  = os.path.expanduser("~/Desktop/QSS20-S26/public_data")
MERGED    = os.path.join(DATA_DIR, "merged_panel.csv")
VDEM      = os.path.join(DATA_DIR, "V-Dem-CY-Full+Others-v16.csv")  # raw V-Dem file (has polyarchy)
OUT_DIR   = os.path.expanduser("~/Desktop/QSS20-S26/figures")       # where the PNGs get written
os.makedirs(OUT_DIR, exist_ok=True)
 
#plot style, matches the rest of the site's charts
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.facecolor": "white", "font.family": "DejaVu Sans",
    "axes.edgecolor": "#444444", "axes.linewidth": 1.0,
})
BLUE, DBLUE, GRAY = "#2E6FE0", "#1B4FB0", "#9AA0A6"
DARK, FOOT        = "#222222", "#777777"
 
#load merged panel, restrict to 2000-2023, recode a life expectancy of 0 to missing
mp = pd.read_csv(MERGED)
mp = mp[(mp.year >= 2000) & (mp.year <= 2023)].copy()
mp.loc[mp.e_pelifeex == 0, "e_pelifeex"] = np.nan
 
#collapse to one row per country: period-average media freedom and life expectancy
cl = (mp.groupby("country_text_id")
        .agg(mf=("v2x_freexp_altinf", "mean"), le=("e_pelifeex", "mean"))
        .dropna())
cl["tier"] = pd.qcut(cl["mf"], 3, labels=["Low", "Medium", "High"])  # split countries into thirds by media freedom
le_low  = cl.loc[cl.tier == "Low",  "le"].mean()   # least-free third, avg life expectancy
le_high = cl.loc[cl.tier == "High", "le"].mean()   # freest third, avg life expectancy
slope, intercept = np.polyfit(cl["mf"], cl["le"], 1)  # best-fit line across countries
print(f"[chart 1] n={len(cl)}  least-free={le_low:.1f}  freest={le_high:.1f}  "
      f"gap={le_high - le_low:.1f}  slope(0->1)={slope:.1f}")
 
#visualization 1: the raw-gap hook (the ~8-year gap, before any controls)
fig, ax = plt.subplots(figsize=(11, 6.6), dpi=150)
colors = {"Low": GRAY, "Medium": "#7FA8EC", "High": BLUE}
for t in ["Low", "Medium", "High"]:                  # one scatter per media-freedom tier
    s = cl[cl.tier == t]
    ax.scatter(s["mf"], s["le"], s=46, color=colors[t], alpha=0.78,
               edgecolor="white", linewidth=0.6, zorder=3,
               label=f"{t} media freedom")
 
#dashed best-fit line
xs = np.linspace(cl["mf"].min(), cl["mf"].max(), 100)
ax.plot(xs, intercept + slope * xs, color=DARK, lw=2.0, ls="--", zorder=4, alpha=0.85)
 
#dotted lines at the two tier averages, plus a gap bracket in the right margin
for y, col in [(le_low, GRAY), (le_high, DBLUE)]:
    ax.axhline(y, color=col, lw=1.0, ls=":", alpha=0.55, zorder=1)
ax.annotate("", xy=(1.05, le_high), xytext=(1.05, le_low),
            arrowprops=dict(arrowstyle="<->", color=DARK, lw=1.7))
ax.text(1.075, (le_low + le_high) / 2, "\u2248 8-year\ngap",
        ha="left", va="center", fontsize=12, fontweight="bold", color=DARK)
ax.text(1.05, le_high + 1.4, "freest\nthird",     ha="center", va="bottom", fontsize=9, color=DBLUE)
ax.text(1.05, le_low  - 1.4, "least-free\nthird", ha="center", va="top",    fontsize=9, color=GRAY)
 
#titles, axes, styling
ax.set_title("Countries with a Freer Press Live About Eight Years Longer",
             fontsize=16.5, fontweight="bold", pad=16, color=DARK)
ax.set_xlabel("Media freedom  (V-Dem freedom of expression index, 0\u20131)", fontsize=12.5, color=DARK)
ax.set_ylabel("Life expectancy (years)", fontsize=12.5, color=DARK)
ax.set_xlim(-0.02, 1.16)
ax.set_xticks(np.arange(0, 1.01, 0.2))
ax.spines[["top", "right"]].set_visible(False)
ax.tick_params(labelsize=11)
ax.grid(axis="y", color="#E6E6E6", lw=0.8, zorder=0)
ax.legend(loc="upper left", fontsize=10.5, handletextpad=0.4,
          framealpha=0.9, facecolor="white", edgecolor="none")
fig.tight_layout(rect=[0, 0.05, 1, 1])
#footnote: this is the raw association, before controls
fig.text(0.02, 0.015, "Each point is one country (2000\u20132023 average). Raw cross-country "
         "association, before any controls \u2014 Findings 02\u201304 test what survives.",
         fontsize=9.5, color=FOOT)
fig.savefig(os.path.join(OUT_DIR, "viz_raw_gap.png"), bbox_inches="tight")
print("saved viz_raw_gap.png")

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
from pathlib import Path
 
# load merged panel and keep the 2000-2023 window
DATA_DIR = Path("~/Desktop/QSS20-S26/public_data").expanduser()
panel = pd.read_csv(DATA_DIR / "merged_panel.csv")
panel = panel[(panel["year"] >= 2000) & (panel["year"] <= 2023)].copy()
 
# 0 is a missing placeholder for life expectancy, not a real value
panel.loc[panel["e_pelifeex"] == 0, "e_pelifeex"] = np.nan
 
# create log GDP and log health spending if not already present
# (income and spending have diminishing returns for health, so use logs)
if "log_gdppc" not in panel.columns:
    panel["log_gdppc"] = np.where(panel["e_gdppc"] > 0, np.log(panel["e_gdppc"]), np.nan)
 
if "log_health_exp" not in panel.columns:
    panel["log_health_exp"] = np.where(
        panel["health_exp_pc_usd"] > 0,
        np.log(panel["health_exp_pc_usd"]),
        np.nan,
    )
 
# pull coefficient, 95% CI, and p-value for one variable out of a fitted model
def get_coef_info(model, var_name):
    """Extract coefficient, confidence interval, and p-value for a variable."""
    coef = model.params[var_name]
    ci_low, ci_high = model.conf_int().loc[var_name]
    pval = model.pvalues[var_name]
    return coef, ci_low, ci_high, pval
 
 
# progressive control models: add one control at a time and watch the
# media-freedom coefficient shrink. all use year fixed effects and SEs
# clustered by country.
models = []
 
# model 1: media freedom alone
d1 = panel.dropna(subset=["e_pelifeex", "v2x_freexp_altinf"]).copy()
m1 = smf.ols(
    "e_pelifeex ~ v2x_freexp_altinf + C(year)",
    data=d1
).fit(cov_type="cluster", cov_kwds={"groups": d1["country_text_id"]})
models.append(("Media freedom alone", m1, d1))
 
# model 2: + GDP per capita (wealth)
d2 = panel.dropna(subset=["e_pelifeex", "v2x_freexp_altinf", "log_gdppc"]).copy()
m2 = smf.ols(
    "e_pelifeex ~ v2x_freexp_altinf + log_gdppc + C(year)",
    data=d2
).fit(cov_type="cluster", cov_kwds={"groups": d2["country_text_id"]})
models.append(("+ GDP per capita", m2, d2))
 
# model 3: + health spending
d3 = panel.dropna(
    subset=["e_pelifeex", "v2x_freexp_altinf", "log_gdppc", "log_health_exp"]
).copy()
m3 = smf.ols(
    "e_pelifeex ~ v2x_freexp_altinf + log_gdppc + log_health_exp + C(year)",
    data=d3
).fit(cov_type="cluster", cov_kwds={"groups": d3["country_text_id"]})
models.append(("+ health spending", m3, d3))
 
# model 4: + rule of law and civil society repression
# note: v2csreprss is civil society repression, so interpret its sign carefully
d4 = panel.dropna(
    subset=[
        "e_pelifeex",
        "v2x_freexp_altinf",
        "log_gdppc",
        "log_health_exp",
        "e_wbgi_rle",
        "v2csreprss",
    ]
).copy()
m4 = smf.ols(
    "e_pelifeex ~ v2x_freexp_altinf + log_gdppc + log_health_exp + e_wbgi_rle + v2csreprss + C(year)",
    data=d4
).fit(cov_type="cluster", cov_kwds={"groups": d4["country_text_id"]})
models.append(("+ rule of law & civil society", m4, d4))
 
 
# collect the media-freedom estimate from each model into one table
rows = []
for label, model, df in models:
    coef, ci_low, ci_high, pval = get_coef_info(model, "v2x_freexp_altinf")
    rows.append({
        "label": label,
        "coef": coef,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "pval": pval,
        "n": int(model.nobs),
        "countries": df["country_text_id"].nunique(),
    })
 
results = pd.DataFrame(rows)
print(results)
 
 
# dot plot: one row per model, dot = estimate, line = 95% CI
fig, ax = plt.subplots(figsize=(11, 5))
 
y_pos = list(range(len(results)))[::-1]   # top row = first model
 
for y, (_, row) in zip(y_pos, results.iterrows()):
    sig = row["pval"] < 0.05
    marginal = row["pval"] < 0.10            # color blue if at least marginally significant
 
    color = "#1f77b4" if marginal else "#c7c7c7"
 
    # 95% CI line
    ax.plot(
        [row["ci_low"], row["ci_high"]],
        [y, y],
        color=color,
        linewidth=3,
        solid_capstyle="round",
        zorder=2,
    )
    # point estimate
    ax.plot(
        row["coef"],
        y,
        "o",
        color=color,
        markersize=12,
        markeredgecolor="white",
        markeredgewidth=2,
        zorder=3,
    )
 
    # significance label text
    if row["pval"] < 0.01:
        p_text = "p<0.01"
    elif row["pval"] < 0.10:
        p_text = "p<0.1"
    else:
        p_text = "not sig."
 
    ax.text(
        13.0,
        y,
        f"{row['coef']:.1f} yrs ({p_text})",
        va="center",
        fontsize=12,
        fontweight="bold" if marginal else "normal",
        color="black" if marginal else "#999999",
    )
 
# dashed line at zero: estimates whose CI crosses it aren't distinguishable from no effect
ax.axvline(0, color="red", linestyle="--", linewidth=1.2, alpha=0.8)
 
ax.set_yticks(y_pos)
ax.set_yticklabels(results["label"], fontsize=12)
ax.set_xlabel("Effect of media freedom on life expectancy (years)", fontsize=13)
ax.set_title(
    "Does Media Freedom Predict Life Expectancy\nAfter Ruling Out Alternative Explanations?",
    fontsize=16,
    fontweight="bold",
    pad=15,
)
 
ax.set_xlim(-4.5, 15)
ax.set_ylim(-0.5, len(results) - 0.5)
ax.xaxis.grid(True, alpha=0.2)
ax.set_axisbelow(True)
 
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
 
plt.tight_layout()
 
# save the figure
OUT_PATH = DATA_DIR / "viz_regression_dots.png"
plt.savefig(OUT_PATH, dpi=300, bbox_inches="tight")
plt.show()
 
print(f"Saved figure to: {OUT_PATH}")
 
#visualization 2: press freedom vs democracy (they are nearly collinear, r ~ 0.90)
#polyarchy is not in merged_panel, so pull it from the raw V-Dem file
v = pd.read_csv(VDEM, usecols=["country_text_id", "year",
                               "v2x_freexp_altinf", "v2x_polyarchy"])
v = v[(v.year >= 2000) & (v.year <= 2023)]
v = v[v.country_text_id.isin(mp.country_text_id.unique())].dropna(
        subset=["v2x_freexp_altinf", "v2x_polyarchy"])
#one row per country, then correlate the two indices
clv = v.groupby("country_text_id").agg(mf=("v2x_freexp_altinf", "mean"),
                                       pol=("v2x_polyarchy", "mean"))
r = clv["mf"].corr(clv["pol"])
print(f"[chart 3] n={len(clv)}  country-level r={r:.3f}  "
      f"(country-year r={v['v2x_freexp_altinf'].corr(v['v2x_polyarchy']):.3f})")
 
fig, ax = plt.subplots(figsize=(8.6, 7.6), dpi=150)
ax.scatter(clv["mf"], clv["pol"], s=42, color=BLUE, alpha=0.6,
           edgecolor="white", linewidth=0.5, zorder=3)
b1, b0 = np.polyfit(clv["mf"], clv["pol"], 1)   #best-fit line through the cloud
xs = np.linspace(0, 1, 100)
ax.plot(xs, b0 + b1 * xs, color=DBLUE, lw=2.0, zorder=4)
 
#big r annotation in the corner
ax.text(0.05, 0.92, "r \u2248 0.90", transform=ax.transAxes,
        fontsize=23, fontweight="bold", color=DBLUE)
ax.text(0.05, 0.855, "nearly perfectly correlated", transform=ax.transAxes,
        fontsize=12, color=FOOT)
 
#titles, axes, styling (square aspect since both axes are 0-1 indices)
ax.set_title("Press Freedom Cannot Be Separated from Democracy",
             fontsize=16.5, fontweight="bold", pad=16, color=DARK)
ax.set_xlabel("Media freedom  (freedom of expression index, 0\u20131)", fontsize=12.5, color=DARK)
ax.set_ylabel("Democracy  (electoral democracy index, 0\u20131)", fontsize=12.5, color=DARK)
ax.set_xlim(-0.02, 1.02)
ax.set_ylim(-0.02, 1.02)
ax.set_aspect("equal", adjustable="box")
ax.spines[["top", "right"]].set_visible(False)
ax.tick_params(labelsize=11)
ax.grid(color="#ECECEC", lw=0.8, zorder=0)
fig.tight_layout(rect=[0, 0.07, 1, 1])
fig.text(0.06, 0.02, "Each point is one country (2000\u20132023 average). Press freedom is one "
         "component of the broader democracy index, so the two cannot be told apart statistically.",
         fontsize=9.5, color=FOOT)
fig.savefig(os.path.join(OUT_DIR, "viz_freedom_democracy.png"), bbox_inches="tight")
print("saved viz_freedom_democracy.png")



#visualization 3: forest plot for the press freedom vs democracy contrast
import statsmodels.formula.api as smf
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
