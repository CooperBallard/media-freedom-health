import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
 
#load merged panel from the merging script (script 01)
panel = pd.read_csv("../data/merged_panel.csv")
 
#keep the study window (drops any stray 2024 rows so it matches the paper)
panel = panel[(panel["year"] >= 2000) & (panel["year"] <= 2023)].copy()
 
#create log GDP if the merge didn't already include it
if "log_gdppc" not in panel.columns:
    panel["log_gdppc"] = np.where(panel["e_gdppc"] > 0, np.log(panel["e_gdppc"]), np.nan)
 
#0 is a missing placeholder for life expectancy, not a real value
panel.loc[panel["e_pelifeex"] == 0, "e_pelifeex"] = np.nan
 
#cross-country press freedom models (year FE, clustered by country)
dpf = panel.dropna(subset=["e_pelifeex", "v2x_freexp_altinf", "log_gdppc", "e_wbgi_rle", "e_wbgi_cce"]).copy()
 
f1 = smf.ols("e_pelifeex ~ v2x_freexp_altinf + C(year)", data=dpf).fit(
    cov_type="cluster", cov_kwds={"groups": dpf["country_text_id"]})
print(f"Press freedom alone:        coef={f1.params['v2x_freexp_altinf']:.3f}, p={f1.pvalues['v2x_freexp_altinf']:.4f}")
 
f2 = smf.ols("e_pelifeex ~ v2x_freexp_altinf + log_gdppc + C(year)", data=dpf).fit(
    cov_type="cluster", cov_kwds={"groups": dpf["country_text_id"]})
print(f"+ wealth:                   coef={f2.params['v2x_freexp_altinf']:.3f}, p={f2.pvalues['v2x_freexp_altinf']:.4f}")
 
f3 = smf.ols("e_pelifeex ~ v2x_freexp_altinf + log_gdppc + e_wbgi_rle + e_wbgi_cce + C(year)", data=dpf).fit(
    cov_type="cluster", cov_kwds={"groups": dpf["country_text_id"]})
print(f"+ rule of law & corruption: coef={f3.params['v2x_freexp_altinf']:.3f}, p={f3.pvalues['v2x_freexp_altinf']:.4f}")
print(f"n = {int(f3.nobs)}")
 
#cross-country democracy models (main result; same sample, year FE, clustered)
d = panel.dropna(subset=["e_pelifeex", "v2x_polyarchy", "log_gdppc", "e_wbgi_rle", "e_wbgi_cce"]).copy()
 
p1 = smf.ols("e_pelifeex ~ v2x_polyarchy + C(year)", data=d).fit(
    cov_type="cluster", cov_kwds={"groups": d["country_text_id"]})
print(f"\nDemocracy alone:            coef={p1.params['v2x_polyarchy']:.3f}, p={p1.pvalues['v2x_polyarchy']:.4f}")
 
p2 = smf.ols("e_pelifeex ~ v2x_polyarchy + log_gdppc + C(year)", data=d).fit(
    cov_type="cluster", cov_kwds={"groups": d["country_text_id"]})
print(f"+ wealth:                   coef={p2.params['v2x_polyarchy']:.3f}, p={p2.pvalues['v2x_polyarchy']:.4f}")
 
p3 = smf.ols("e_pelifeex ~ v2x_polyarchy + log_gdppc + e_wbgi_rle + e_wbgi_cce + C(year)", data=d).fit(
    cov_type="cluster", cov_kwds={"groups": d["country_text_id"]})
print(f"+ rule of law & corruption: coef={p3.params['v2x_polyarchy']:.3f}, p={p3.pvalues['v2x_polyarchy']:.4f}")
print(f"n = {int(p3.nobs)}")
