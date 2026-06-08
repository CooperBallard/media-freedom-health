#imported by the numbered scripts in this folder so the plot style, panel
#loading, clustered regression call, and coefficient extraction are in one
#place instead of being copied into every script. 
 
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
 
#shared paths
DATA_DIR = "../data"
OUT_DIR  = "../output"
MERGED   = os.path.join(DATA_DIR, "merged_panel.csv")
 
#shared color palette
BLUE, DBLUE, GRAY = "#2E6FE0", "#1B4FB0", "#9AA0A6"
DARK, FOOT        = "#222222", "#777777"
 
 
def set_plot_style():
    #apply the shared matplotlib style used across all figure scripts
    plt.rcParams.update({
        "figure.facecolor": "white", "axes.facecolor": "white",
        "savefig.facecolor": "white", "font.family": "DejaVu Sans",
        "axes.edgecolor": "#444444", "axes.linewidth": 1.0,
    })
 
 
def ensure_output_dir():
    #make sure the output folder exists before saving a figure
    os.makedirs(OUT_DIR, exist_ok=True)
 
 
def load_panel():
    #load merged_panel.csv, keep 2000-2023, recode life expectancy of 0 to
    #missing, and create logs if the merge didn't already include them
    panel = pd.read_csv(MERGED)
    panel = panel[(panel["year"] >= 2000) & (panel["year"] <= 2023)].copy()
 
    #0 is a missing placeholder for life expectancy, not a real value
    panel.loc[panel["e_pelifeex"] == 0, "e_pelifeex"] = np.nan
 
    if "log_gdppc" not in panel.columns:
        panel["log_gdppc"] = np.where(
            panel["e_gdppc"] > 0, np.log(panel["e_gdppc"]), np.nan)
    if "log_health_exp" not in panel.columns:
        panel["log_health_exp"] = np.where(
            panel["health_exp_pc_usd"] > 0,
            np.log(panel["health_exp_pc_usd"]), np.nan)
 
    return panel
 
 
def cluster_ols(formula, data, cluster_col="country_text_id"):
    #fit OLS with standard errors clustered by country (the project default)
    return smf.ols(formula, data=data).fit(
        cov_type="cluster", cov_kwds={"groups": data[cluster_col]})
 
 
def get_coef_info(model, var_name):
    #extract coefficient, confidence interval, and p-value for a variable
    coef = model.params[var_name]
    ci_low, ci_high = model.conf_int().loc[var_name]
    pval = model.pvalues[var_name]
    return coef, ci_low, ci_high, pval
