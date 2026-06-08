import os
import pandas as pd
import matplotlib.pyplot as plt
from helpers import (set_plot_style, ensure_output_dir, load_panel,
                     cluster_ols, OUT_DIR)

set_plot_style()
ensure_output_dir()
panel = load_panel()


#figure 4: forest plot, press freedom vs democracy contrast
#all models: OLS, year fixed effects via C(year), SEs clustered by country
#each model drops missing rows only on the variables it uses, so sample sizes differ

#press freedom with wealth control (the comparison case, expected not significant)
d_pf = panel.dropna(subset=["e_pelifeex", "v2x_freexp_altinf", "log_gdppc"]).copy()
m_pf = cluster_ols("e_pelifeex ~ v2x_freexp_altinf + log_gdppc + C(year)", d_pf)

#democracy with wealth control
d_dem_wealth = panel.dropna(subset=["e_pelifeex", "v2x_polyarchy", "log_gdppc"]).copy()
m_dem_wealth = cluster_ols("e_pelifeex ~ v2x_polyarchy + log_gdppc + C(year)", d_dem_wealth)

#democracy with the full control set: wealth, rule of law, control of corruption
d_dem_full = panel.dropna(subset=["e_pelifeex", "v2x_polyarchy", "log_gdppc", "e_wbgi_rle", "e_wbgi_cce"]).copy()
m_dem_full = cluster_ols("e_pelifeex ~ v2x_polyarchy + log_gdppc + e_wbgi_rle + e_wbgi_cce + C(year)", d_dem_full)

#pull the coefficient, 95% CI, p-value, and n for one variable out of a fitted model
def coef_row(model, var, label):
    ci_low, ci_high = model.conf_int().loc[var]
    return {"label": label, "coef": model.params[var], "ci_low": ci_low,
            "ci_high": ci_high, "pval": model.pvalues[var], "n": int(model.nobs)}

#one row per bar in the forest plot, top to bottom
results = pd.DataFrame([
    coef_row(m_pf, "v2x_freexp_altinf", "Press freedom\n(+ wealth)"),
    coef_row(m_dem_wealth, "v2x_polyarchy", "Democracy\n(+ wealth)"),
    coef_row(m_dem_full, "v2x_polyarchy", "Democracy\n(+ wealth, rule of law,\ncorruption)"),
])
print(results)
print(f"\nSamples: press freedom+wealth n={int(m_pf.nobs)}, "
      f"democracy+wealth n={int(m_dem_wealth.nobs)}, democracy full n={int(m_dem_full.nobs)}")

fig, ax = plt.subplots(figsize=(11, 5))
#y positions: top bar is press freedom, bottom is the full democracy model
y_pos = [2, 1, 0]
for y, (_, row) in zip(y_pos, results.iterrows()):
    #blue if significant at 0.05, gray if not
    sig = row["pval"] < 0.05
    color = "#1f77b4" if sig else "#9aa0a6"
    #confidence interval as a horizontal line, point estimate as a dot
    ax.plot([row["ci_low"], row["ci_high"]], [y, y], color=color,
            linewidth=3, solid_capstyle="round", zorder=2)
    ax.plot(row["coef"], y, "o", color=color, markersize=13,
            markeredgecolor="white", markeredgewidth=2, zorder=3)
    #format the p-value text
    if row["pval"] < 0.001:
        p_text = "p < 0.001"
    else:
        p_text = f"p = {row['pval']:.3f}"
    #significant bars get the p-value in bold black, non-significant ones say so in gray
    if sig:
        label_text = f"{row['coef']:.1f} yrs  ({p_text})"
        text_color, weight = "black", "bold"
    else:
        label_text = f"{row['coef']:.1f} yrs  (not significant)"
        text_color, weight = "#666666", "normal"
    #move the label left a little so it sits just above the dot
    ax.text(row["coef"] - 1.55 if sig else row["coef"] - 1.35, y + 0.22, label_text,
            va="center", fontsize=12, fontweight=weight, color=text_color)
#dashed line at zero for the no-effect reference
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
#drop the box, keep only the bottom axis
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
#caption note under the plot
ax.text(0.5, -0.48, "Cross-country estimates, clustered by country. "
        "Press freedom's interval crosses zero.", fontsize=9, color="#888888")
plt.tight_layout()
#save to output/ at 300 dpi for the paper and website
fig.savefig(os.path.join(OUT_DIR, "viz_xc_contrast.png"), dpi=300, bbox_inches="tight")
print("saved viz_xc_contrast.png")
