import os
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
 
#full path to your merged_panel.csv (it lives in public_data, not data)
PANEL = "/Users/cooperballard/Desktop/QSS20-S26/public_data/merged_panel.csv"
 
#if that path is not found, search a few common folders and use the first match
if not os.path.exists(PANEL):
    for base in [os.path.expanduser("~/Desktop"), os.path.expanduser("~/Documents"),
                 os.getcwd(), os.path.expanduser("~")]:
        hits = [os.path.join(r, "merged_panel.csv") for r, _, fs in os.walk(base)
                if "merged_panel.csv" in fs]
        if hits:
            PANEL = hits[0]
            print("found panel at:", PANEL)
            break
 
#load merged panel from the merging script (script 01)
panel = pd.read_csv(PANEL)
 
#keep the study window (drops any stray 2024 rows so it matches the paper)
panel = panel[(panel["year"] >= 2000) & (panel["year"] <= 2023)].copy()
 
#create log GDP if the merge didn't already include it
if "log_gdppc" not in panel.columns:
    panel["log_gdppc"] = np.where(panel["e_gdppc"] > 0, np.log(panel["e_gdppc"]), np.nan)
 
#0 is a missing placeholder for life expectancy, not a real value
panel.loc[panel["e_pelifeex"] == 0, "e_pelifeex"] = np.nan
 
#fit one model on its own complete-case sample
#we only drop rows for variables this model actually uses, so simpler models keep more rows
def fit(key, controls):
    rhs = [key] + controls
    sub = panel.dropna(subset=["e_pelifeex"] + rhs).copy()   #complete cases for THIS model
    formula = "e_pelifeex ~ " + " + ".join(rhs) + " + C(year)"
    m = smf.ols(formula, data=sub).fit(                      #cluster groups come from the same subset
        cov_type="cluster", cov_kwds={"groups": sub["country_text_id"]})
    return m, key
 
#cross-country press freedom models (year FE, clustered by country)
for label, ctrls in [("Press freedom alone",        []),
                     ("+ wealth",                   ["log_gdppc"]),
                     ("+ rule of law & corruption", ["log_gdppc", "e_wbgi_rle", "e_wbgi_cce"])]:
    m, key = fit("v2x_freexp_altinf", ctrls)
    print(f"{label:28s} coef={m.params[key]:.3f}, p={m.pvalues[key]:.4f}, n={int(m.nobs)}")
 
print()
 
#cross-country democracy models (main result; year FE, clustered by country)
for label, ctrls in [("Democracy alone",            []),
                     ("+ wealth",                   ["log_gdppc"]),
                     ("+ rule of law & corruption", ["log_gdppc", "e_wbgi_rle", "e_wbgi_cce"])]:
    m, key = fit("v2x_polyarchy", ctrls)
    print(f"{label:28s} coef={m.params[key]:.3f}, p={m.pvalues[key]:.4f}, n={int(m.nobs)}")
