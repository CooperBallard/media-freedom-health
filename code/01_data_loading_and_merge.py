import pandas as pd
import numpy as np

#user-defined function to reshape World Bank wide-to-long

def reshape_wb_data(wb_raw):
    """Reshape World Bank data from wide format (years as columns) to long format."""
    year_cols = [c for c in wb_raw.columns if c.isdigit()]
    wb_long = wb_raw.melt(
        id_vars=["Country Code"],
        value_vars=year_cols,
        var_name="year",
        value_name="health_exp_pc_usd",
    )
    wb_long["year"] = wb_long["year"].astype(int)
    wb_long = wb_long.rename(columns={"Country Code": "country_text_id"})
    wb_long = wb_long.dropna(subset=["health_exp_pc_usd"])
    return wb_long


#Load V-Dem data
vdem_raw = pd.read_csv("~/Desktop/QSS20-S26/public_data/V-Dem-CY-Full+Others-v16.csv", low_memory=False)

# List comprehension style: columns we want to keep
VDEM_COLS = [
    "country_name", "country_text_id", "year",
    "v2mecenefm",           #government media censorship
    "v2meslfcen",           #media self-censorship
    "v2meharjrn",           #harassment of journalists
    "v2csreprss",           #civil society repression
    "v2x_freexp_altinf",    #freedom of expression index (0-1)
    "e_gdppc",              #GDP per capita
    "e_pop",                #population
    "e_pelifeex",           #life expectancy
    "e_wbgi_rle",           #rule of law
    "e_wbgi_cce",           #control of corruption
]
vdem = vdem_raw[VDEM_COLS].copy()

#Boolean filter to subset to analysis window
vdem = vdem[(vdem["year"] >= 2000) & (vdem["year"] <= 2024)]
print(f"V-Dem: {vdem.shape}")

#load and reshape World Bank health expenditure data
wb_raw = pd.read_csv("~/Desktop/QSS20-S26/public_data/healthdata.csv", skiprows=4)
wb_long = reshape_wb_data(wb_raw)
print(f"World Bank: {wb_long.shape}")

#merge on country code and year
panel = vdem.merge(wb_long, on=["country_text_id", "year"], how="left")

#apply lambda to log-transform skewed variables
panel["log_gdppc"] = panel["e_gdppc"].apply(lambda x: np.log(x) if x > 0 else np.nan)
panel["log_health_exp"] = panel["health_exp_pc_usd"].apply(lambda x: np.log(x) if x > 0 else np.nan)

print(f"Merged panel: {panel.shape}")
print(f"Health expenditure coverage: {panel['health_exp_pc_usd'].notna().sum()} of {len(panel)} rows")

#save
panel.to_csv("~/Desktop/QSS20-S26/public_data/merged_panel.csv", index=False)
print("Saved merged_panel.csv")
