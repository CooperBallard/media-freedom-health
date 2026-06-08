# Media Freedom and Population Health

**QSS 20 Final Project: Cooper Ballard, Dartmouth College**

**Live site:** https://cooperballard.github.io/media-freedom-health/

## Overview

Countries with freer presses tend to have longer-lived populations: in these data, the most press-free countries average roughly eight years more life expectancy than the least. This project asks whether that gap reflects press freedom itself, or whether it is explained by national wealth and by the broader democratic system that press freedom belongs to. Using a country-year panel of 179 countries (2000–2023), it stress-tests the raw association with progressively stronger controls and finds that press freedom carries no robust independent signal once income is accounted for, and that it cannot be statistically separated from overall democracy (the two correlate at about 0.90). What survives is a broader cross-country association between democratic governance and population health. These are observational, cross-country associations, not causal estimates.

## Data

| Dataset | Source | Key Variables |
|---------|--------|---------------|
| V-Dem Country-Year v16 | [V-Dem Institute](https://v-dem.net/data/the-v-dem-dataset/) | Freedom of expression / media freedom, electoral democracy (polyarchy), life expectancy, GDP per capita, rule of law, control of corruption |
| World Development Indicators | [World Bank](https://data.worldbank.org/indicator/SH.XPD.CHEX.PC.CD) | Health expenditure per capita (USD) |

The full V-Dem file is too large for GitHub; the World Bank file and the merged panel are included. See [`data/README.md`](data/README.md) for sources and download instructions.

## Repository Structure

- `code/` — Python scripts, run in numbered order (described in the Scripts section below)
  - `01_data_loading_and_merge.py`
  - `02_raw_gap.py`
  - `03_press_freedom_controls.py`
  - `04_press_freedom_democracy.py`
  - `05_full_comparison_plot.py`
  - `06_interactive_map.py`
  - `07_regression_analysis.py`
  - `08_summary_statistics.py`
  - `helpers.py` (shared functions imported by scripts 02–07 that are not run directly)
- `data/` — Data sources and the analysis-ready panel
  - `README.md` — sources and download links
  - `merged_panel.csv` — merged country-year panel (built by script 01, read by the rest)
  - `summary_statistics.csv` — Table 1 output from script 08
  - World Bank source file is included; the V-Dem file is too large for GitHub (see `data/README.md`)
- `output/` — Generated figures and the interactive map
  - `viz_raw_gap.png`
  - `viz_regression_dots.png`
  - `viz_freedom_democracy.png`
  - `viz_xc_contrast.png`
  - `democracy_health_map.html`
- `docs/` — Live project website (GitHub Pages): https://cooperballard.github.io/media-freedom-health/
- `Transcript.md` — full AI assistant transcript (the Agentic Analysis reflection is in the paper)

## Scripts

All scripts live in `code/` and read from `../data`. Run them in numbered order from inside the `code/` folder.

1. [`01_data_loading_and_merge.py`](code/01_data_loading_and_merge.py): Reads the raw V-Dem (`V-Dem-CY-Full+Others-v16.csv`) and World Bank health expenditure (`API_SH.XPD.CHEX.PC.CD_DS2_en_csv_v2_645.csv`) files, reshapes the World Bank data to long form, restricts both to 2000–2023, left-joins them into a country-year panel, recodes zero life-expectancy values as missing, log-transforms GDP and health spending, and prints row counts before and after the merge. Outputs `data/merged_panel.csv`.
2. [`02_raw_gap.py`](code/02_raw_gap.py): Reads `merged_panel.csv`. Produces Figure 1, the raw country-level scatter of media freedom against life expectancy showing the roughly eight-year gap before any controls. Outputs `output/viz_raw_gap.png`.
3. [`03_press_freedom_controls.py`](code/03_press_freedom_controls.py): Reads `merged_panel.csv`. Runs the progressive-controls regressions for media freedom (alone, then adding GDP, health spending, and rule of law plus civil society repression) with year fixed effects and standard errors clustered by country, and plots the shrinking coefficient. Produces Figure 2. Outputs `output/viz_regression_dots.png`.
4. [`04_press_freedom_democracy.py`](code/04_press_freedom_democracy.py): Reads `merged_panel.csv`. Produces Figure 3, the country-level scatter of media freedom against electoral democracy (r ≈ 0.90), showing the two are nearly collinear. Outputs `output/viz_freedom_democracy.png`.
5. [`05_full_comparison_plot.py`](code/05_full_comparison_plot.py): Reads `merged_panel.csv`. Estimates the cross-country contrast models (press freedom with wealth; democracy with wealth; democracy with wealth, rule of law, and control of corruption), clustered by country, and plots them side by side. Produces Figure 4. Outputs `output/viz_xc_contrast.png`.
6. [`06_interactive_map.py`](code/06_interactive_map.py): Reads `merged_panel.csv`. Builds an interactive Plotly choropleth of the 2023 snapshot with a dropdown to toggle between free expression, life expectancy, media censorship, and civil society freedom. Outputs `output/democracy_health_map.html`.
7. [`07_regression_analysis.py`](code/07_regression_analysis.py): Reads  `merged_panel.csv`. Runs and prints the regressions behind the paper: the cross-country media-freedom progressive-controls sequence, the cross-country democracy specifications, and the within-country two-way fixed-effects models with lagged democracy and lagged press freedom reported as sensitivity checks. Cross-country models use year fixed effects with standard errors clustered by country. Prints coefficients, p-values, and sample sizes. No file output as the numbers are reported in the paper.
8. [`08_summary_statistics.py`](code/08_summary_statistics.py): Reads `merged_panel.csv`. Builds Table 1 (N, mean, standard deviation, min, and max for the key variables) and prints panel coverage diagnostics (row and country counts, year span, and health-spending coverage). Outputs `data/summary_statistics.csv`.
9. [`helpers.py `](code/helpers.py): It holds the functions that the other scripts have in common, so the same setup does not have to be repeated in each file. set_plot_style applies the shared matplotlib styling. ensure_output_dir creates the output/ folder if it does not already exist. load_panel reads  `merged_panel.csv`, restricts it to the 2000–2023 window, recodes zero life-expectancy values as missing, and adds the log GDP and log health-spending columns if they are not already present. cluster_ols runs an OLS regression with year fixed effects and standard errors clustered by country. get_coef_info returns the coefficient, confidence interval, and p-value for a given variable from a fitted model. The module reads `merged_panel.csv` only through load_panel, and it does not write any files.

## Findings

Across countries, the most press-free countries average roughly eight years more life expectancy than the least, but that gap is largely an artifact of wealth: the media-freedom association shrinks from about eight years to roughly one and loses significance once GDP and health spending are controlled. Press freedom is also inseparable from overall democracy, with which it correlates at about 0.90, so it cannot be isolated as a predictor in its own right. On its own, with wealth controlled, press freedom is not statistically significant (about 2.8 years, p ≈ 0.09). Democracy, by contrast, holds up: about 4.7 more years of life expectancy across countries, even after controlling for wealth, rule of law, and control of corruption (p ≈ 0.02), with standard errors clustered by country. Within-country fixed-effects estimates point the same way but are not statistically distinguishable from zero once clustered. Press freedom looks more like a marker of broader democratic governance than an independent driver of population health.
