import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import plotly.graph_objects as go
 
#paths: adjust these to wherever your files live
DATA_DIR = os.path.expanduser("~/Desktop/QSS20-S26/public_data")
MERGED   = os.path.join(DATA_DIR, "merged_panel.csv")
OUT_DIR  = os.path.expanduser("~/Desktop/QSS20-S26/figures")
os.makedirs(OUT_DIR, exist_ok=True)
 
#shared plot style + palette for all the matplotlib charts
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.facecolor": "white", "font.family": "DejaVu Sans",
    "axes.edgecolor": "#444444", "axes.linewidth": 1.0,
})
BLUE, DBLUE, GRAY = "#2E6FE0", "#1B4FB0", "#9AA0A6"
DARK, FOOT        = "#222222", "#777777"
 
#load merged panel once, keep 2000-2023, recode life expectancy of 0 to missing
panel = pd.read_csv(MERGED)
panel = panel[(panel["year"] >= 2000) & (panel["year"] <= 2023)].copy()
panel.loc[panel["e_pelifeex"] == 0, "e_pelifeex"] = np.nan
 
#create logs if the merge didn't already include them
if "log_gdppc" not in panel.columns:
    panel["log_gdppc"] = np.where(panel["e_gdppc"] > 0, np.log(panel["e_gdppc"]), np.nan)
if "log_health_exp" not in panel.columns:
    panel["log_health_exp"] = np.where(
        panel["health_exp_pc_usd"] > 0, np.log(panel["health_exp_pc_usd"]), np.nan)
 
#merged_panel already includes v2x_polyarchy (added in the merging script)
 
#helper used by the dot plot and the forest plot
def get_coef_info(model, var_name):
    #extract coefficient, confidence interval, and p-value for a variable
    coef = model.params[var_name]
    ci_low, ci_high = model.conf_int().loc[var_name]
    pval = model.pvalues[var_name]
    return coef, ci_low, ci_high, pval
 
 
#visualization 1: raw-gap hook (the ~8-year gap, before any controls)
 
#collapse the panel to one row per country: its average media freedom and life expectancy
cl = (panel.groupby("country_text_id")
           .agg(mf=("v2x_freexp_altinf", "mean"), le=("e_pelifeex", "mean"))
           .dropna())
cl["tier"] = pd.qcut(cl["mf"], 3, labels=["Low", "Medium", "High"])   #thirds by media freedom
#average life expectancy in the least-free and freest thirds
le_low  = cl.loc[cl.tier == "Low",  "le"].mean()
le_high = cl.loc[cl.tier == "High", "le"].mean()
#straight-line fit of life expectancy on media freedom across the full 0 to 1 range
slope, intercept = np.polyfit(cl["mf"], cl["le"], 1)
#console check: country count, the two tier averages, the gap, and the slope
print(f"[viz 1] n={len(cl)}  least-free={le_low:.1f}  freest={le_high:.1f}  "
      f"gap={le_high - le_low:.1f}  slope(0->1)={slope:.1f}")
 
#set up the figure
fig, ax = plt.subplots(figsize=(11, 6.6), dpi=150)
#one color per press-freedom tier
colors = {"Low": GRAY, "Medium": "#7FA8EC", "High": BLUE}
#plot each tier as its own scatter so the legend separates them
for t in ["Low", "Medium", "High"]:
    s = cl[cl.tier == t]
    ax.scatter(s["mf"], s["le"], s=46, color=colors[t], alpha=0.78,
               edgecolor="white", linewidth=0.6, zorder=3, label=f"{t} media freedom")
#draw the fitted trend line over the observed range
xs = np.linspace(cl["mf"].min(), cl["mf"].max(), 100)
ax.plot(xs, intercept + slope * xs, color=DARK, lw=2.0, ls="--", zorder=4, alpha=0.85)
#faint dotted reference lines at the two tier averages
for y, col in [(le_low, GRAY), (le_high, DBLUE)]:
    ax.axhline(y, color=col, lw=1.0, ls=":", alpha=0.55, zorder=1)
#double-headed arrow spanning the gap between the tiers, parked to the right of the data
ax.annotate("", xy=(1.05, le_high), xytext=(1.05, le_low),
            arrowprops=dict(arrowstyle="<->", color=DARK, lw=1.7))
#label the gap
ax.text(1.075, (le_low + le_high) / 2, "\u2248 8-year\ngap",
        ha="left", va="center", fontsize=12, fontweight="bold", color=DARK)
#label the freest and least-free thirds next to the arrow
ax.text(1.05, le_high + 1.4, "freest\nthird",     ha="center", va="bottom", fontsize=9, color=DBLUE)
ax.text(1.05, le_low  - 1.4, "least-free\nthird", ha="center", va="top",    fontsize=9, color=GRAY)
#title and axis labels
ax.set_title("Countries with a Freer Press Live About Eight Years Longer",
             fontsize=16.5, fontweight="bold", pad=16, color=DARK)
ax.set_xlabel("Media freedom  (V-Dem freedom of expression index, 0\u20131)", fontsize=12.5, color=DARK)
ax.set_ylabel("Life expectancy (years)", fontsize=12.5, color=DARK)
#extend the x-axis past 1 to leave room for the gap arrow and tier labels
ax.set_xlim(-0.02, 1.16)
ax.set_xticks(np.arange(0, 1.01, 0.2))
#drop the top and right borders for a cleaner look
ax.spines[["top", "right"]].set_visible(False)
ax.tick_params(labelsize=11)
#light horizontal gridlines only
ax.grid(axis="y", color="#E6E6E6", lw=0.8, zorder=0)
ax.legend(loc="upper left", fontsize=10.5, handletextpad=0.4,
          framealpha=0.9, facecolor="white", edgecolor="none")
#tighten the layout but reserve a strip at the bottom for the source note
fig.tight_layout(rect=[0, 0.05, 1, 1])
#source note under the figure
fig.text(0.02, 0.015, "Each point is one country (2000\u20132023 average). Raw cross-country "
         "association, before any controls \u2014 Findings 02\u201304 test what survives.",
         fontsize=9.5, color=FOOT)
#write the PNG to the output folder
fig.savefig(os.path.join(OUT_DIR, "viz_raw_gap.png"), bbox_inches="tight")
print("saved viz_raw_gap.png")
 
 
#visualization 2: progressive-controls dot plot for press freedom
#(add one control at a time, watch the coefficient shrink; year FE, clustered by country)
models = []
 
#model 1: media freedom alone
d1 = panel.dropna(subset=["e_pelifeex", "v2x_freexp_altinf"]).copy()
m1 = smf.ols("e_pelifeex ~ v2x_freexp_altinf + C(year)", data=d1).fit(
    cov_type="cluster", cov_kwds={"groups": d1["country_text_id"]})
models.append(("Media freedom alone", m1, d1))
 
#model 2: + GDP per capita
d2 = panel.dropna(subset=["e_pelifeex", "v2x_freexp_altinf", "log_gdppc"]).copy()
m2 = smf.ols("e_pelifeex ~ v2x_freexp_altinf + log_gdppc + C(year)", data=d2).fit(
    cov_type="cluster", cov_kwds={"groups": d2["country_text_id"]})
models.append(("+ GDP per capita", m2, d2))
 
#model 3: + health spending
d3 = panel.dropna(subset=["e_pelifeex", "v2x_freexp_altinf", "log_gdppc", "log_health_exp"]).copy()
m3 = smf.ols("e_pelifeex ~ v2x_freexp_altinf + log_gdppc + log_health_exp + C(year)", data=d3).fit(
    cov_type="cluster", cov_kwds={"groups": d3["country_text_id"]})
models.append(("+ health spending", m3, d3))
 
#model 4: + rule of law and civil society repression (v2csreprss; interpret its sign carefully)
d4 = panel.dropna(subset=["e_pelifeex", "v2x_freexp_altinf", "log_gdppc",
                          "log_health_exp", "e_wbgi_rle", "v2csreprss"]).copy()
m4 = smf.ols("e_pelifeex ~ v2x_freexp_altinf + log_gdppc + log_health_exp + e_wbgi_rle + v2csreprss + C(year)",
             data=d4).fit(cov_type="cluster", cov_kwds={"groups": d4["country_text_id"]})
models.append(("+ rule of law & civil society", m4, d4))
 
#collect the media-freedom estimate from each model
rows = []
for label, model, df in models:
    coef, ci_low, ci_high, pval = get_coef_info(model, "v2x_freexp_altinf")
    rows.append({"label": label, "coef": coef, "ci_low": ci_low, "ci_high": ci_high,
                 "pval": pval, "n": int(model.nobs), "countries": df["country_text_id"].nunique()})
results = pd.DataFrame(rows)
print(results)
 
fig, ax = plt.subplots(figsize=(11, 5))
y_pos = list(range(len(results)))[::-1]   #top row = first model
for y, (_, row) in zip(y_pos, results.iterrows()):
    marginal = row["pval"] < 0.10            #color blue if at least marginally significant
    color = "#1f77b4" if marginal else "#c7c7c7"
    ax.plot([row["ci_low"], row["ci_high"]], [y, y], color=color,
            linewidth=3, solid_capstyle="round", zorder=2)
    ax.plot(row["coef"], y, "o", color=color, markersize=12,
            markeredgecolor="white", markeredgewidth=2, zorder=3)
    if row["pval"] < 0.01:
        p_text = "p<0.01"
    elif row["pval"] < 0.10:
        p_text = "p<0.1"
    else:
        p_text = "not sig."
    ax.text(13.0, y, f"{row['coef']:.1f} yrs ({p_text})", va="center", fontsize=12,
            fontweight="bold" if marginal else "normal",
            color="black" if marginal else "#999999")
ax.axvline(0, color="red", linestyle="--", linewidth=1.2, alpha=0.8)
ax.set_yticks(y_pos)
ax.set_yticklabels(results["label"], fontsize=12)
ax.set_xlabel("Effect of media freedom on life expectancy (years)", fontsize=13)
ax.set_title("Does Media Freedom Predict Life Expectancy\nAfter Ruling Out Alternative Explanations?",
             fontsize=16, fontweight="bold", pad=15)
ax.set_xlim(-4.5, 15)
ax.set_ylim(-0.5, len(results) - 0.5)
ax.xaxis.grid(True, alpha=0.2)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
plt.tight_layout()
fig.savefig(os.path.join(DATA_DIR, "viz_regression_dots.png"), dpi=300, bbox_inches="tight")
print("saved viz_regression_dots.png")
 
 
#visualization 3: press freedom vs democracy (nearly collinear, r ~ 0.90)
clv = (panel.groupby("country_text_id")
            .agg(mf=("v2x_freexp_altinf", "mean"), pol=("v2x_polyarchy", "mean"))
            .dropna())
r = clv["mf"].corr(clv["pol"])
print(f"[viz 3] n={len(clv)}  country-level r={r:.3f}  "
      f"(country-year r={panel['v2x_freexp_altinf'].corr(panel['v2x_polyarchy']):.3f})")
 
fig, ax = plt.subplots(figsize=(8.6, 7.6), dpi=150)
ax.scatter(clv["mf"], clv["pol"], s=42, color=BLUE, alpha=0.6,
           edgecolor="white", linewidth=0.5, zorder=3)
b1, b0 = np.polyfit(clv["mf"], clv["pol"], 1)   #best-fit line through the cloud
xs = np.linspace(0, 1, 100)
ax.plot(xs, b0 + b1 * xs, color=DBLUE, lw=2.0, zorder=4)
ax.text(0.05, 0.92, "r \u2248 0.90", transform=ax.transAxes, fontsize=23, fontweight="bold", color=DBLUE)
ax.text(0.05, 0.855, "nearly perfectly correlated", transform=ax.transAxes, fontsize=12, color=FOOT)
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
 
 
#visualization 4: forest plot, press freedom vs democracy contrast
#all models: OLS, year fixed effects via C(year), SEs clustered by country
d_pf = panel.dropna(subset=["e_pelifeex", "v2x_freexp_altinf", "log_gdppc"]).copy()
m_pf = smf.ols("e_pelifeex ~ v2x_freexp_altinf + log_gdppc + C(year)", data=d_pf).fit(
    cov_type="cluster", cov_kwds={"groups": d_pf["country_text_id"]})
 
d_dem_wealth = panel.dropna(subset=["e_pelifeex", "v2x_polyarchy", "log_gdppc"]).copy()
m_dem_wealth = smf.ols("e_pelifeex ~ v2x_polyarchy + log_gdppc + C(year)", data=d_dem_wealth).fit(
    cov_type="cluster", cov_kwds={"groups": d_dem_wealth["country_text_id"]})
 
d_dem_full = panel.dropna(subset=["e_pelifeex", "v2x_polyarchy", "log_gdppc", "e_wbgi_rle", "e_wbgi_cce"]).copy()
m_dem_full = smf.ols("e_pelifeex ~ v2x_polyarchy + log_gdppc + e_wbgi_rle + e_wbgi_cce + C(year)",
                     data=d_dem_full).fit(cov_type="cluster", cov_kwds={"groups": d_dem_full["country_text_id"]})
 
def coef_row(model, var, label):
    ci_low, ci_high = model.conf_int().loc[var]
    return {"label": label, "coef": model.params[var], "ci_low": ci_low,
            "ci_high": ci_high, "pval": model.pvalues[var], "n": int(model.nobs)}
 
results = pd.DataFrame([
    coef_row(m_pf, "v2x_freexp_altinf", "Press freedom\n(+ wealth)"),
    coef_row(m_dem_wealth, "v2x_polyarchy", "Democracy\n(+ wealth)"),
    coef_row(m_dem_full, "v2x_polyarchy", "Democracy\n(+ wealth, rule of law,\ncorruption)"),
])
print(results)
print(f"\nSamples: press freedom+wealth n={int(m_pf.nobs)}, "
      f"democracy+wealth n={int(m_dem_wealth.nobs)}, democracy full n={int(m_dem_full.nobs)}")
 
fig, ax = plt.subplots(figsize=(11, 5))
y_pos = [2, 1, 0]
for y, (_, row) in zip(y_pos, results.iterrows()):
    sig = row["pval"] < 0.05
    color = "#1f77b4" if sig else "#9aa0a6"
    ax.plot([row["ci_low"], row["ci_high"]], [y, y], color=color,
            linewidth=3, solid_capstyle="round", zorder=2)
    ax.plot(row["coef"], y, "o", color=color, markersize=13,
            markeredgecolor="white", markeredgewidth=2, zorder=3)
    if row["pval"] < 0.001:
        p_text = "p < 0.001"
    else:
        p_text = f"p = {row['pval']:.3f}"
    if sig:
        label_text = f"{row['coef']:.1f} yrs  ({p_text})"
        text_color, weight = "black", "bold"
    else:
        label_text = f"{row['coef']:.1f} yrs  (not significant)"
        text_color, weight = "#666666", "normal"
    ax.text(row["coef"] - 1.55 if sig else row["coef"] - 1.35, y + 0.22, label_text,
            va="center", fontsize=12, fontweight=weight, color=text_color)
ax.axvline(0, color="#555555", linestyle="--", linewidth=1.2)
ax.set_yticks(y_pos)
ax.set_yticklabels(results["label"], fontsize=12)
ax.set_xlabel("Association with life expectancy (years)", fontsize=13)
ax.set_title("Democracy Predicts Life Expectancy; Press Freedom Does Not",
             fontsize=16, fontweight="bold", pad=15)
ax.set_xlim(-2, 10)
ax.set_ylim(-0.6, 2.6)
ax.xaxis.grid(True, alpha=0.2)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.text(0.5, -0.48, "Cross-country estimates, clustered by country. "
        "Press freedom's interval crosses zero.", fontsize=9, color="#888888")
plt.tight_layout()
fig.savefig(os.path.join(DATA_DIR, "viz_xc_contrast.png"), dpi=300, bbox_inches="tight")
print("saved viz_xc_contrast.png")
 
 
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
 
os.makedirs("docs", exist_ok=True)
fig.write_html("docs/democracy_health_map.html")
print("saved docs/democracy_health_map.html")
