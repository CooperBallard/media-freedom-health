import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

#user-defined function to extract regression results
def get_coef_info(model, var_name):
    """Extract coefficient, confidence interval, and p-value for a variable."""
    coef = model.params[var_name]
    ci = model.conf_int().loc[var_name]
    pval = model.pvalues[var_name]
    return {"coef": coef, "ci_low": ci[0], "ci_high": ci[1], "pval": pval}

#load merged panel from script 01
panel = pd.read_csv("./data/merged_panel.csv")

#apply lambda for log transforms
panel["log_gdppc"] = panel["e_gdppc"].apply(lambda x: np.log(x) if x > 0 else np.nan)
panel["log_health_exp"] = panel["health_exp_pc_usd"].apply(lambda x: np.log(x) if x > 0 else np.nan)

#drop rows missing key regression variables
df = panel.dropna(subset=["e_pelifeex", "v2x_freexp_altinf", "log_gdppc", "log_health_exp"])
print(f"Regression sample: {len(df)} country-years")

#four OLS model specifications (clustered standard errors)

#model 1: media freedom alone
m1 = smf.ols("e_pelifeex ~ v2x_freexp_altinf", data=df).fit(
    cov_type="cluster", cov_kwds={"groups": df["country_text_id"]})

#model 2: add GDP per capita
m2 = smf.ols("e_pelifeex ~ v2x_freexp_altinf + log_gdppc", data=df).fit(
    cov_type="cluster", cov_kwds={"groups": df["country_text_id"]})

#model 3: add health spending
m3 = smf.ols("e_pelifeex ~ v2x_freexp_altinf + log_gdppc + log_health_exp", data=df).fit(
    cov_type="cluster", cov_kwds={"groups": df["country_text_id"]})

#model 4: add rule of law and civil society repression
df_full = df.dropna(subset=["e_wbgi_rle", "v2csreprss"])
m4 = smf.ols("e_pelifeex ~ v2x_freexp_altinf + log_gdppc + log_health_exp + e_wbgi_rle + v2csreprss",
    data=df_full).fit(cov_type="cluster", cov_kwds={"groups": df_full["country_text_id"]})

#extract results using function + list comprehension
models = [m1, m2, m3, m4]
labels = [
    "Media freedom alone",
    "+ GDP per capita",
    "+ health spending",
    "+ rule of law & civil society",
]

#list comprehension to pull coefficient info from each model
results = [get_coef_info(m, "v2x_freexp_altinf") for m in models]

#print summary
for label, r in zip(labels, results):
    sig = "***" if r["pval"] < 0.01 else ("*" if r["pval"] < 0.1 else "ns")
    print(f"{label:45s}  coef={r['coef']:6.2f}  p={r['pval']:.3f}  {sig}")

#coefficient dot plot
fig, ax = plt.subplots(figsize=(10, 4.5))
y_pos = list(range(len(models) - 1, -1, -1))

for i, (r, y, label) in enumerate(zip(results, y_pos, labels)):
    #blue if significant, gray if not
    significant = r["pval"] < 0.1
    color = "#2c7fb8" if significant else "#cccccc"

    #confidence interval line
    ax.plot([r["ci_low"], r["ci_high"]], [y, y], color=color,
            linewidth=2.5, solid_capstyle="round")
    #coefficient dot
    ax.plot(r["coef"], y, "o", color=color, markersize=10,
            markeredgecolor="white", markeredgewidth=1.5)

    #label with significance level
    sig_label = " (p<0.01)" if r["pval"] < 0.01 else (
        " (p<0.1)" if r["pval"] < 0.1 else " (not sig.)")
    ax.text(14, y, f"{r['coef']:.1f} yrs{sig_label}", va="center", fontsize=10,
            fontweight="bold" if significant else "normal",
            color="black" if significant else "#999999")

#red dashed line at zero effect
ax.axvline(x=0, color="#e34a33", linestyle="--", linewidth=1.2)
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=10)
ax.set_xlabel("Effect of media freedom on life expectancy (years)", fontsize=11)
ax.set_title("Does Media Freedom Predict Life Expectancy\nAfter Ruling Out Alternative Explanations?",
             fontsize=13, fontweight="bold")
ax.grid(True, axis="x", alpha=0.2)
plt.tight_layout()
plt.savefig("../output/regression.png", dpi=200, bbox_inches="tight")
plt.show()
