import pandas as pd
import numpy as np
from pathlib import Path
 
#load merged panel and keep the 2000-2023 window
DATA_DIR = Path("~/Desktop/QSS20-S26/public_data").expanduser()
panel = pd.read_csv(DATA_DIR / "merged_panel.csv")
panel = panel[(panel["year"] >= 2000) & (panel["year"] <= 2023)].copy()
 
#0 is a missing placeholder for life expectancy, not a real value
panel.loc[panel["e_pelifeex"] == 0, "e_pelifeex"] = np.nan
 
#log transforms (income and spending have diminishing returns for health)
panel["log_gdppc"] = np.where(panel["e_gdppc"] > 0, np.log(panel["e_gdppc"]), np.nan)
panel["log_health_exp"] = np.where(
    panel["health_exp_pc_usd"] > 0,
    np.log(panel["health_exp_pc_usd"]),
    np.nan
)
 
#panel diagnostics: row count, country count, year span, health-spending coverage
print("Panel diagnostics")
print(f"Rows: {len(panel):,}")
print(f"Countries: {panel['country_text_id'].nunique():,}")
print(f"Years: {panel['year'].min()}-{panel['year'].max()}")
print(
    f"Health expenditure coverage: "
    f"{panel['health_exp_pc_usd'].notna().sum():,} of {len(panel):,} rows "
    f"({panel['health_exp_pc_usd'].notna().mean() * 100:.1f}%)"
)
 
#variables to summarize, each mapped to a readable label for the table
summary_vars = {
    "e_pelifeex": "Life expectancy (years)",
    "v2x_freexp_altinf": "Media freedom (0-1)",
    "v2x_polyarchy": "Democracy (0-1)",
    "v2mecenefm": "Media censorship score",
    "v2meharjrn": "Journalist harassment score",
    "v2csreprss": "Civil society repression score",
    "health_exp_pc_usd": "Health spending per capita (USD)",
    "e_gdppc": "GDP per capita (thousands USD)",
    "e_wbgi_rle": "Rule of law score",
    "e_wbgi_cce": "Control of corruption score",
}
 
#build one row of N / mean / SD / min / max per variable (missing values dropped)
rows = []
for var, label in summary_vars.items():
    if var not in panel.columns:                 #skip and warn if a column is missing
        print(f"Warning: {var} not found in panel")
        continue
    col = panel[var].dropna()
    rows.append({
        "Variable": label,
        "N": len(col),
        "Mean": col.mean(),
        "SD": col.std(),
        "Min": col.min(),
        "Max": col.max(),
    })
 
summary_df = pd.DataFrame(rows)
 
#rounded, comma-formatted copy for display and export
summary_display = summary_df.copy()
for col in ["Mean", "SD", "Min", "Max"]:
    summary_display[col] = summary_display[col].round(2)
summary_display["N"] = summary_display["N"].map(lambda x: f"{x:,}")
 
print("\nTable 1. Summary statistics")
print(summary_display.to_string(index=False))
 
#save the table to CSV
OUT_PATH = DATA_DIR / "summary_statistics.csv"
summary_display.to_csv(OUT_PATH, index=False)
print(f"\nSaved summary statistics to: {OUT_PATH}")
