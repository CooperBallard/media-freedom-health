import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path("../data")

VDEM_PATH = DATA_DIR / "V-Dem-CY-Full+Others-v16.csv"
WB_PATH   = DATA_DIR / "API_SH.XPD.CHEX.PC.CD_DS2_en_csv_v2_645.csv"
OUT_PATH  = DATA_DIR / "merged_panel.csv"

#this is a helper function to reshape World Bank data from wide format, where years are columns to long format with one country-year per row.
def reshape_wb_data(wb_raw): 
 
    year_cols = [c for c in wb_raw.columns if str(c).isdigit()]

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


#load V-Dem data
vdem_raw = pd.read_csv(VDEM_PATH, low_memory=False)

VDEM_COLS = [
    "country_name",
    "country_text_id",
    "year",
    "v2mecenefm",          #government media censorship
    "v2meslfcen",          #media self-censorship
    "v2meharjrn",          #harassment of journalists
    "v2csreprss",          #civil society repression
    "v2x_freexp_altinf",   #freedom of expression / alternative information index
    "v2x_polyarchy",       #electoral democracy index
    "e_gdppc",             #GDP per capita
    "e_pop",               #population
    "e_pelifeex",          #life expectancy
    "e_wbgi_rle",          #rule of law
    "e_wbgi_cce",          #control of corruption
]

vdem = vdem_raw[VDEM_COLS].copy()

# Restrict to final project analysis window: 2000–2023
vdem = vdem[(vdem["year"] >= 2000) & (vdem["year"] <= 2023)].copy()

print("\nV-Dem after year filter")
print("Rows:", len(vdem))
print("Countries:", vdem["country_text_id"].nunique())
print("Years:", vdem["year"].min(), "-", vdem["year"].max())


#load and reshape World Bank health expenditure data
wb_raw = pd.read_csv(WB_PATH, skiprows=4)
wb_long = reshape_wb_data(wb_raw)

#restrict World Bank data to same analysis window
wb_long = wb_long[(wb_long["year"] >= 2000) & (wb_long["year"] <= 2023)].copy()

print("\nWorld Bank health expenditure after reshape")
print("Rows:", len(wb_long))
print("Countries:", wb_long["country_text_id"].nunique())
print("Years:", wb_long["year"].min(), "-", wb_long["year"].max())

#merge V-Dem + World Bank
panel = vdem.merge(
    wb_long,
    on=["country_text_id", "year"],
    how="left",
    validate="one_to_one",
)

print("\nMerged panel")
print("Rows:", len(panel))
print("Countries:", panel["country_text_id"].nunique())
print("Years:", panel["year"].min(), "-", panel["year"].max())
print(
    "Health expenditure coverage:",
    panel["health_exp_pc_usd"].notna().sum(),
    "of",
    len(panel),
    "rows",
)
print(
    "Health expenditure coverage percent:",
    round(panel["health_exp_pc_usd"].notna().mean() * 100, 1),
    "%",
)

#clean and transform variables

#life expectancy coded as 0 means missing, not true zero
panel.loc[panel["e_pelifeex"] == 0, "e_pelifeex"] = np.nan

#log-transform skewed variables
panel["log_gdppc"] = np.where(
    panel["e_gdppc"] > 0,
    np.log(panel["e_gdppc"]),
    np.nan,
)

panel["log_health_exp"] = np.where(
    panel["health_exp_pc_usd"] > 0,
    np.log(panel["health_exp_pc_usd"]),
    np.nan,
)


#final diagnostics
key_vars = [
    "e_pelifeex",
    "v2x_freexp_altinf",
    "v2x_polyarchy",
    "log_gdppc",
    "log_health_exp",
    "e_wbgi_rle",
    "e_wbgi_cce",
]

print("\nMissingness in key variables")
print(panel[key_vars].isna().sum().sort_values(ascending=False))

print("\nFinal merged_panel diagnostics")
print("Rows:", len(panel))
print("Countries:", panel["country_text_id"].nunique())
print("Years:", panel["year"].min(), "-", panel["year"].max())



#save corrected merged panel
panel.to_csv(OUT_PATH, index=False)
print(f"\nSaved corrected merged panel to: {OUT_PATH}")
