# Media Freedom and Population Health

**QSS 20 Final Project — Cooper Ballard, Dartmouth College**

## Overview

Do declines in media freedom and civil society lead to worse health outcomes, even when health spending stays the same? This project uses country-year panel data from 170+ countries (2000–2024) to test whether nondistributive dimensions of democratic governance predict changes in life expectancy independently of government health expenditure.

## Data

| Dataset | Source | Key Variables |
|---------|--------|---------------|
| V-Dem Country-Year v16 | [V-Dem Institute](https://v-dem.net/data/the-v-dem-dataset/) | Media censorship, journalist harassment, civil society repression, freedom of expression index, GDP per capita, life expectancy, rule of law |
| World Development Indicators | [World Bank](https://data.worldbank.org/indicator/SH.XPD.CHEX.PC.CD) | Health expenditure per capita (USD) |

Raw data files are too large for GitHub. See [`data/README.md`](data/README.md) for download instructions.

## Repository Structure

- `code/` — Python scripts for data processing and analysis
  - `01_data_loading_and_merge.py`
  - `02_visualizations.py`
  - `03_regression_analysis.py`
- `data/` — Data download instructions (raw files too large for GitHub)
  - `README.md`
- `output/` — Generated figures
  - `viz_backsliding.png`
  - `viz_residualized_scatter.png`
  - `viz_spending_freedom.png`

## Scripts

1. **`01_data_loading_and_merge.py`** — Loads V-Dem and World Bank health expenditure data, merges into a country-year panel.
2. **`02_visualizations.py`** — Produces exploratory plots: backsliding trajectory comparison, health spending vs life expectancy by freedom level, and faceted version by tercile.
3. **`03_regression_analysis.py`** — Runs four OLS specifications progressively adding controls to test whether media freedom predicts life expectancy.

## Preliminary Findings

Countries that experienced significant declines in media freedom show lower life expectancy gains than countries with stable media freedom. The association between media freedom and life expectancy persists after controlling for GDP, though it weakens when rule of law is added, suggesting governance quality may operate through multiple correlated channels.
