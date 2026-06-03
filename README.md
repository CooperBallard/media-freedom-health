# Media Freedom and Population Health

**QSS 20 Final Project — Cooper Ballard, Dartmouth College**

## Overview

Countries with freer presses tend to have longer-lived populations: in these data, the most press-free countries average roughly eight years more life expectancy than the least. This project asks whether that gap reflects press freedom itself, or whether it is explained by national wealth and by the broader democratic system that press freedom belongs to. Using a country-year panel of 179 countries (2000–2023), it stress-tests the raw association with progressively stronger controls and finds that press freedom carries no robust independent signal once income is accounted for, and that it cannot be statistically separated from overall democracy (the two correlate at about 0.90). What survives is a broader cross-country association between democratic governance and population health. These are observational, cross-country associations, not causal estimates.

## Data

| Dataset | Source | Key Variables |
|---------|--------|---------------|
| V-Dem Country-Year v16 | [V-Dem Institute](https://v-dem.net/data/the-v-dem-dataset/) | Freedom of expression / media freedom, electoral democracy (polyarchy), life expectancy, GDP per capita, rule of law, control of corruption |
| World Development Indicators | [World Bank](https://data.worldbank.org/indicator/SH.XPD.CHEX.PC.CD) | Health expenditure per capita (USD) |

Raw data files are too large for GitHub. See [`data/README.md`](data/README.md) for download instructions.

## Repository Structure

- `code/` — Python scripts for data processing and analysis
  - `01_data_loading_and_merge.py`
  - `02_visualizations.py`
  - `03_regression_analysis.py`
  - `04_summary_statistcs.py`
- `data/` — Data download instructions (raw files too large for GitHub)
  - `README.md`
- `output/` — Generated figures
  - `viz_raw_gap.png`
  - `viz_regression_dots.png`
  - `viz_freedom_democracy.png`
  - `viz_xc_contrast.png`
  - `democracy_health_map.html`

## Scripts

1. **`01_data_loading_and_merge.py`** — Loads V-Dem and World Bank health expenditure data, merges into a country-year panel (2000–2023), recodes zero life-expectancy values as missing, and log-transforms GDP and health spending.
2. **`02_visualizations.py`** — Produces the four figures: the raw media-freedom vs life-expectancy gap, the progressive-controls coefficient plot, the media-freedom vs democracy scatter (r ≈ 0.90), and the cross-country contrast of press freedom vs democracy.
3. **`03_regression_analysis.py`** — Runs cross-country regressions with standard errors clustered by country: the progressive-controls sequence for media freedom, and the democracy specifications adding wealth, rule of law, and control of corruption. Also estimates within-country fixed-effects models as a sensitivity check.

## Findings

Across countries, the most press-free countries average roughly eight years more life expectancy than the least, but that gap is largely an artifact of wealth: the media-freedom association shrinks from about eight years to roughly one and loses significance once GDP and health spending are controlled. Press freedom is also inseparable from overall democracy, with which it correlates at about 0.90, so it cannot be isolated as a predictor in its own right. On its own, with wealth controlled, press freedom is only marginal and not statistically significant (about 2.8 years, p ≈ 0.09). Democracy, by contrast, holds up: about 4.7 more years of life expectancy across countries, even after controlling for wealth, rule of law, and control of corruption (p ≈ 0.02), with standard errors clustered by country. Within-country fixed-effects estimates point the same way but are not statistically distinguishable from zero once clustered. Press freedom looks more like a marker of broader democratic governance than an independent driver of population health.
