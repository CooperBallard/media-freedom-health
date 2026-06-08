import os
import numpy as np
import matplotlib.pyplot as plt
from helpers import (set_plot_style, ensure_output_dir, load_panel,
                     OUT_DIR, BLUE, DBLUE, DARK, FOOT)
 
set_plot_style()
ensure_output_dir()
panel = load_panel()
 
 
#figure 3: press freedom vs democracy (nearly collinear, r ~ 0.90)
clv = (panel.groupby("country_text_id")
            .agg(mf=("v2x_freexp_altinf", "mean"), pol=("v2x_polyarchy", "mean"))
            .dropna())
r = clv["mf"].corr(clv["pol"])
print(f"[viz 3] n={len(clv)}  country-level r={r:.3f}  "
      f"(country-year r={panel['v2x_freexp_altinf'].corr(panel['v2x_polyarchy']):.3f})")
 
fig, ax = plt.subplots(figsize=(8.6, 7.6), dpi=150)
ax.scatter(clv["mf"], clv["pol"], s=42, color=BLUE, alpha=0.6,
           edgecolor="white", linewidth=0.5, zorder=3)
b1, b0 = np.polyfit(clv["mf"], clv["pol"], 1)   #best-fit line through the cloud
xs = np.linspace(0, 1, 100)
ax.plot(xs, b0 + b1 * xs, color=DBLUE, lw=2.0, zorder=4)
ax.text(0.05, 0.92, "r \u2248 0.90", transform=ax.transAxes, fontsize=23, fontweight="bold", color=DBLUE)
ax.text(0.05, 0.855, "very strongly correlated", transform=ax.transAxes, fontsize=12, color=FOOT)
ax.set_title("Press Freedom Cannot Be Separated from Democracy",
             fontsize=16.5, fontweight="bold", pad=16, color=DARK)
ax.set_xlabel("Media freedom  (freedom of expression index, 0\u20131)", fontsize=12.5, color=DARK)
ax.set_ylabel("Democracy  (electoral democracy index, 0\u20131)", fontsize=12.5, color=DARK)
ax.set_xlim(-0.02, 1.02)
ax.set_ylim(-0.02, 1.02)
ax.set_aspect("equal", adjustable="box")
ax.spines[["top", "right"]].set_visible(False)
ax.tick_params(labelsize=11)
ax.grid(color="#ECECEC", lw=0.8, zorder=0)
fig.tight_layout(rect=[0, 0.07, 1, 1])
fig.text(0.06, 0.02, "Each point is one country (2000\u20132023 average). Press freedom is one "
         "component of the broader democracy index, so the two cannot be told apart statistically.",
         fontsize=9.5, color=FOOT)
fig.savefig(os.path.join(OUT_DIR, "viz_freedom_democracy.png"), bbox_inches="tight")
print("saved viz_freedom_democracy.png")
