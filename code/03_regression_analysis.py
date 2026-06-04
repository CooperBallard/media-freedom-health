import os
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
 
#full path to your merged_panel.csv (it lives in public_data, not data)
PANEL = "/Users/cooperballard/Desktop/QSS20-S26/public_data/merged_panel.csv"
 
#load merged panel from the merging script (script 01)
panel = pd.read_csv(PANEL)
 
#keep the study window (drops any stray 2024 rows so it matches the paper)
panel = panel[(panel["year"] >= 2000) & (panel["year"] <= 2023)].copy()
 
#create log GDP if the merge didn't already include it
if "log_gdppc" not in panel.columns:
    panel["log_gdppc"] = np.where(panel["e_gdppc"] > 0, np.log(panel["e_gdppc"]), np.nan)
 
#0 is a missing placeholder for life expectancy, not a real value
panel.loc[panel["e_pelifeex"] == 0, "e_pelifeex"] = np.nan
 
#cross-country press freedom models (year FE, clustered by country)
#each model drops only on the variables IT uses, so simpler models keep more rows (matches the paper)
f1d = panel.dropna(subset=["e_pelifeex", "v2x_freexp_altinf"]).copy()
f1 = smf.ols("e_pelifeex ~ v2x_freexp_altinf + C(year)", data=f1d).fit(
    cov_type="cluster", cov_kwds={"groups": f1d["country_text_id"]})
print(f"Press freedom alone:        coef={f1.params['v2x_freexp_altinf']:.3f}, p={f1.pvalues['v2x_freexp_altinf']:.4f}, n={int(f1.nobs)}")
 
f2d = panel.dropna(subset=["e_pelifeex", "v2x_freexp_altinf", "log_gdppc"]).copy()
f2 = smf.ols("e_pelifeex ~ v2x_freexp_altinf + log_gdppc + C(year)", data=f2d).fit(
    cov_type="cluster", cov_kwds={"groups": f2d["country_text_id"]})
print(f"+ wealth:                   coef={f2.params['v2x_freexp_altinf']:.3f}, p={f2.pvalues['v2x_freexp_altinf']:.4f}, n={int(f2.nobs)}")
 
f3d = panel.dropna(subset=["e_pelifeex", "v2x_freexp_altinf", "log_gdppc", "e_wbgi_rle", "e_wbgi_cce"]).copy()
f3 = smf.ols("e_pelifeex ~ v2x_freexp_altinf + log_gdppc + e_wbgi_rle + e_wbgi_cce + C(year)", data=f3d).fit(
    cov_type="cluster", cov_kwds={"groups": f3d["country_text_id"]})
print(f"+ rule of law & corruption: coef={f3.params['v2x_freexp_altinf']:.3f}, p={f3.pvalues['v2x_freexp_altinf']:.4f}, n={int(f3.nobs)}")
 
#cross-country democracy models (main result; year FE, clustered by country)
p1d = panel.dropna(subset=["e_pelifeex", "v2x_polyarchy"]).copy()
p1 = smf.ols("e_pelifeex ~ v2x_polyarchy + C(year)", data=p1d).fit(
    cov_type="cluster", cov_kwds={"groups": p1d["country_text_id"]})
print(f"\nDemocracy alone:            coef={p1.params['v2x_polyarchy']:.3f}, p={p1.pvalues['v2x_polyarchy']:.4f}, n={int(p1.nobs)}")
 
p2d = panel.dropna(subset=["e_pelifeex", "v2x_polyarchy", "log_gdppc"]).copy()
p2 = smf.ols("e_pelifeex ~ v2x_polyarchy + log_gdppc + C(year)", data=p2d).fit(
    cov_type="cluster", cov_kwds={"groups": p2d["country_text_id"]})
print(f"+ wealth:                   coef={p2.params['v2x_polyarchy']:.3f}, p={p2.pvalues['v2x_polyarchy']:.4f}, n={int(p2.nobs)}")
 
p3d = panel.dropna(subset=["e_pelifeex", "v2x_polyarchy", "log_gdppc", "e_wbgi_rle", "e_wbgi_cce"]).copy()
p3 = smf.ols("e_pelifeex ~ v2x_polyarchy + log_gdppc + e_wbgi_rle + e_wbgi_cce + C(year)", data=p3d).fit(
    cov_type="cluster", cov_kwds={"groups": p3d["country_text_id"]})
print(f"+ rule of law & corruption: coef={p3.params['v2x_polyarchy']:.3f}, p={p3.pvalues['v2x_polyarchy']:.4f}, n={int(p3.nobs)}")
