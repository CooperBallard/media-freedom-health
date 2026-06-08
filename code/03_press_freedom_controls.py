import os
import pandas as pd
import matplotlib.pyplot as plt
from helpers import (set_plot_style, ensure_output_dir, load_panel,
                     cluster_ols, get_coef_info, OUT_DIR)
 
set_plot_style()
ensure_output_dir()
panel = load_panel()
 
 
#figure 2: progressive-controls dot plot for press freedom
#(add one control at a time, watch the coefficient shrink; year FE, clustered by country)
models = []
 
#model 1: media freedom alone
d1 = panel.dropna(subset=["e_pelifeex", "v2x_freexp_altinf"]).copy()
m1 = cluster_ols("e_pelifeex ~ v2x_freexp_altinf + C(year)", d1)
models.append(("Media freedom alone", m1, d1))
 
#model 2: + GDP per capita
d2 = panel.dropna(subset=["e_pelifeex", "v2x_freexp_altinf", "log_gdppc"]).copy()
m2 = cluster_ols("e_pelifeex ~ v2x_freexp_altinf + log_gdppc + C(year)", d2)
models.append(("+ GDP per capita", m2, d2))
 
#model 3: + health spending
d3 = panel.dropna(subset=["e_pelifeex", "v2x_freexp_altinf", "log_gdppc", "log_health_exp"]).copy()
m3 = cluster_ols("e_pelifeex ~ v2x_freexp_altinf + log_gdppc + log_health_exp + C(year)", d3)
models.append(("+ health spending", m3, d3))
 
#model 4: + rule of law and civil society repression (v2csreprss; interpret its sign carefully)
d4 = panel.dropna(subset=["e_pelifeex", "v2x_freexp_altinf", "log_gdppc",
                          "log_health_exp", "e_wbgi_rle", "v2csreprss"]).copy()
m4 = cluster_ols("e_pelifeex ~ v2x_freexp_altinf + log_gdppc + log_health_exp + e_wbgi_rle + v2csreprss + C(year)", d4)
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
    sig = row["pval"] < 0.05            #color blue only if significant at p<0.05
    color = "#1f77b4" if sig else "#c7c7c7"
    ax.plot([row["ci_low"], row["ci_high"]], [y, y], color=color,
            linewidth=3, solid_capstyle="round", zorder=2)
    ax.plot(row["coef"], y, "o", color=color, markersize=12,
            markeredgecolor="white", markeredgewidth=2, zorder=3)
    if row["pval"] < 0.01:
        p_text = "p<0.01"
    elif row["pval"] < 0.10:
        p_text = "p = 0.09, n.s."
    else:
        p_text = "not sig."
    ax.text(13.0, y, f"{row['coef']:.1f} yrs ({p_text})", va="center", fontsize=12,
            fontweight="bold" if sig else "normal",
            color="black" if sig else "#999999")
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
fig.savefig(os.path.join(OUT_DIR, "viz_regression_dots.png"), dpi=300, bbox_inches="tight")
print("saved viz_regression_dots.png")
