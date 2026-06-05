# Data Sources

The full V-Dem source file is too large to host on GitHub, so download it from the link below. The World Bank health file and a pre-merged dataset (`merged_panel.csv`) are both included in this folder.

## Merged Dataset (included)
- **File:** `merged_panel.csv`
- **Description:** V-Dem governance indicators merged with World Bank health expenditure data
- **Coverage:** 2000–2024 (the paper restricts the analysis to 2000–2023)
- **Unit of analysis:** country-year (4,457 rows in the file; 4,278 in the 2000–2023 analysis sample)

## V-Dem Country-Year Full+Others (v16)
- **Source:** [V-Dem Institute](https://v-dem.net/data/the-v-dem-dataset/)
- **File:** `V-Dem-CY-Full+Others-v16.csv`
- **Coverage:** 170+ countries, 1900–2025
- **Key variables:** `v2x_freexp_altinf` (media freedom / freedom of expression index), `v2x_polyarchy` (electoral democracy index), `e_pelifeex` (life expectancy), `e_gdppc` (GDP per capita), `e_wbgi_rle` (rule of law), `e_wbgi_cce` (control of corruption), `v2csreprss` (civil society repression), `v2mecenefm` (media censorship), `v2meharjrn` (journalist harassment)

## World Bank World Development Indicators
- **Source:** [World Bank](https://data.worldbank.org/indicator/SH.XPD.CHEX.PC.CD)
- **Indicator:** Current health expenditure per capita, USD (`SH.XPD.CHEX.PC.CD`)
- **File:** `API_SH.XPD.CHEX.PC.CD_DS2_en_csv_v2_645.csv`
- **Coverage:** All countries, 2000–2023
