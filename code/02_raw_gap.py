import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from helpers import (set_plot_style, ensure_output_dir, load_panel,
                     OUT_DIR, BLUE, DBLUE, GRAY, DARK, FOOT)
 
set_plot_style()
ensure_output_dir()
panel = load_panel()
 
 
#figure 1: raw-gap hook (the ~8-year gap, before any controls)
 
#collapse the panel to one row per country: its average media freedom and life expectancy
cl = (panel.groupby("country_text_id")
           .agg(mf=("v2x_freexp_altinf", "mean"), le=("e_pelifeex", "mean"))
           .dropna())
cl["tier"] = pd.qcut(cl["mf"], 3, labels=["Low", "Medium", "High"])   #thirds by media freedom
#average life expectancy in the least-free and freest thirds
le_low  = cl.loc[cl.tier == "Low",  "le"].mean()
le_high = cl.loc[cl.tier == "High", "le"].mean()
#straight-line fit of life expectancy on media freedom across the full 0 to 1 range
slope, intercept = np.polyfit(cl["mf"], cl["le"], 1)
#console check: country count, the two tier averages, the gap, and the slope
print(f"[viz 1] n={len(cl)}  least-free={le_low:.1f}  freest={le_high:.1f}  "
      f"gap={le_high - le_low:.1f}  slope(0->1)={slope:.1f}")
 
#set up the figure
fig, ax = plt.subplots(figsize=(11, 6.6), dpi=150)
#one color per press-freedom tier
colors = {"Low": GRAY, "Medium": "#7FA8EC", "High": BLUE}
#plot each tier as its own scatter so the legend separates them
for t in ["Low", "Medium", "High"]:
    s = cl[cl.tier == t]
    ax.scatter(s["mf"], s["le"], s=46, color=colors[t], alpha=0.78,
               edgecolor="white", linewidth=0.6, zorder=3, label=f"{t} media freedom")
#draw the fitted trend line over the observed range
xs = np.linspace(cl["mf"].min(), cl["mf"].max(), 100)
ax.plot(xs, intercept + slope * xs, color=DARK, lw=2.0, ls="--", zorder=4, alpha=0.85)
#faint dotted reference lines at the two tier averages
for y, col in [(le_low, GRAY), (le_high, DBLUE)]:
    ax.axhline(y, color=col, lw=1.0, ls=":", alpha=0.55, zorder=1)
#double-headed arrow spanning the gap between the tiers, parked to the right of the data
ax.annotate("", xy=(1.05, le_high), xytext=(1.05, le_low),
            arrowprops=dict(arrowstyle="<->", color=DARK, lw=1.7))
#label the gap
ax.text(1.075, (le_low + le_high) / 2, "\u2248 8-year\ngap",
        ha="left", va="center", fontsize=12, fontweight="bold", color=DARK)
#label the freest and least-free thirds next to the arrow
ax.text(1.05, le_high + 1.4, "freest\nthird",     ha="center", va="bottom", fontsize=9, color=DBLUE)
ax.text(1.05, le_low  - 1.4, "least-free\nthird", ha="center", va="top",    fontsize=9, color=GRAY)
#title and axis labels
ax.set_title("Countries with a Freer Press Live About Eight Years Longer",
             fontsize=16.5, fontweight="bold", pad=16, color=DARK)
ax.set_xlabel("Media freedom  (V-Dem freedom of expression index, 0\u20131)", fontsize=12.5, color=DARK)
ax.set_ylabel("Life expectancy (years)", fontsize=12.5, color=DARK)
#extend the x-axis past 1 to leave room for the gap arrow and tier labels
ax.set_xlim(-0.02, 1.16)
ax.set_xticks(np.arange(0, 1.01, 0.2))
#drop the top and right borders for a cleaner look
ax.spines[["top", "right"]].set_visible(False)
ax.tick_params(labelsize=11)
#light horizontal gridlines only
ax.grid(axis="y", color="#E6E6E6", lw=0.8, zorder=0)
ax.legend(loc="upper left", fontsize=10.5, handletextpad=0.4,
          framealpha=0.9, facecolor="white", edgecolor="none")
#tighten the layout but reserve a strip at the bottom for the source note
fig.tight_layout(rect=[0, 0.05, 1, 1])
#source note under the figure
fig.text(0.02, 0.015, "Each point is one country (2000\u20132023 average). Raw cross-country "
         "association, before any controls; later models test whether this gap survives "
         "adjustment for wealth and democracy.",
         fontsize=9.5, color=FOOT)
#write the PNG to the output folder
fig.savefig(os.path.join(OUT_DIR, "viz_raw_gap.png"), bbox_inches="tight")
print("saved viz_raw_gap.png")
