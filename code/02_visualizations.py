import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

#load merged panel
panel = pd.read_csv("../data/merged_panel.csv")

#user-defined functions
def classify_media_change(country_id, declined_list):
    """Classify country as declined or stable based on media freedom."""
    if country_id in declined_list:
        return "Media freedom declined"
    return "Media freedom stable or improved"

#visualization 1: Backsliding trajectory

#subset to 2000-2023 with the columns we need
df = panel[panel["year"].between(2000, 2023)][
    ["country_name", "country_text_id", "year", "v2mecenefm", "e_pelifeex"]
].dropna().copy()

#get each country's media censorship score at baseline (2000) and recent (2023)
baseline = df[df["year"] == 2000].set_index("country_text_id")["v2mecenefm"]
recent = df[df["year"] == 2023].set_index("country_text_id")["v2mecenefm"]
change = (recent - baseline).dropna()

#list comprehension: countries whose media freedom dropped by more than 0.5
declined = [c for c in change.index if change[c] < -0.5]

#apply our function to label each row as declined or stable
df["group"] = df["country_text_id"].apply(lambda x: classify_media_change(x, declined))

#groupby year and group to get average life expectancy per year
grouped = df.groupby(["year", "group"]).agg({"e_pelifeex": "mean"}).reset_index()

#plot the two trajectories
fig, ax = plt.subplots(figsize=(10, 6))
for group, color, style in [("Media freedom declined", "#e34a33", "--"),
                              ("Media freedom stable or improved", "#2c7fb8", "-")]:
    sub = grouped[grouped["group"] == group]
    ax.plot(sub["year"], sub["e_pelifeex"], color=color, linewidth=2.5, linestyle=style, label=group)

ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Average Life Expectancy (years)", fontsize=11)
ax.set_title("Do Countries That Lose Media Freedom Fall Behind in Health?", fontsize=13, fontweight="bold")
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("../output/backsliding.png", dpi=200, bbox_inches="tight")
plt.show()

#visualization 2: Faceted scatter: spending vs life expectancy by freedom

#get most recent health expenditure per country from the panel
recent_health = panel.dropna(subset=["health_exp_pc_usd"]).sort_values("year", ascending=False)
recent_health = recent_health.groupby("country_text_id").first().reset_index()
recent_health = recent_health[["country_text_id", "health_exp_pc_usd"]].rename(
    columns={"health_exp_pc_usd": "health_exp"})

#merge with 2023 governance data from the panel
df3 = panel[panel["year"] == 2023][
    ["country_text_id", "country_name", "v2x_freexp_altinf", "e_pelifeex"]
].merge(recent_health, on="country_text_id", how="left")
df3 = df3.dropna(subset=["health_exp", "e_pelifeex", "v2x_freexp_altinf"])
df3 = df3[df3["health_exp"] > 0]

#split countries into terciles of media freedom using pd.qcut
df3["freedom_group"] = pd.qcut(df3["v2x_freexp_altinf"], 3,
    labels=["Low Media Freedom", "Medium Media Freedom", "High Media Freedom"])

#create three side-by-side panels, one per freedom level
fig, axes = plt.subplots(1, 3, figsize=(16, 6), sharey=True, sharex=True)
colors = ["#e34a33", "#fdbb84", "#2c7fb8"]
groups = ["Low Media Freedom", "Medium Media Freedom", "High Media Freedom"]

#loop through each group and plot scatter + trend line
for i, (group, color) in enumerate(zip(groups, colors)):
    sub = df3[df3["freedom_group"] == group]
    axes[i].scatter(sub["health_exp"], sub["e_pelifeex"], c=color,
                     alpha=0.7, edgecolors="white", s=60)

    #fit trend line on log-transformed spending
    log_x = np.log10(sub["health_exp"])
    z = np.polyfit(log_x, sub["e_pelifeex"], 1)
    x_line = np.logspace(np.log10(sub["health_exp"].min()),
                          np.log10(sub["health_exp"].max()), 100)
    axes[i].plot(x_line, np.poly1d(z)(np.log10(x_line)), "--", color="black", linewidth=1.5)

    #label each panel with freedom score range and sample size
    lo = sub["v2x_freexp_altinf"].min()
    hi = sub["v2x_freexp_altinf"].max()
    axes[i].set_xscale("log")
    axes[i].set_title(f"{group}\n(score: {lo:.2f}\u2013{hi:.2f}, n={len(sub)})",
                       fontsize=11, fontweight="bold", color=color)
    axes[i].set_xlabel("Health Spending Per Capita, USD")
    axes[i].grid(True, alpha=0.3)

axes[0].set_ylabel("Life Expectancy (years)", fontsize=11)
fig.suptitle("Does Media Freedom Matter Beyond Health Spending?", fontsize=14, fontweight="bold")
plt.tight_layout(rect=[0, 0.08, 1, 0.95])
plt.savefig("../output/scatterplot.png", dpi=200, bbox_inches="tight")
plt.show()

#visualization 3: Interactive Plotly choropleth map

#get 2023 snapshot from the panel
df4 = panel[panel["year"] == 2023][["country_text_id", "country_name",
    "v2x_freexp_altinf", "v2mecenefm", "v2csreprss", "e_pelifeex"]].dropna(
    subset=["v2x_freexp_altinf"]).copy()

#build hover text showing all metrics for each country
hover = (df4["country_name"] +
    "<br>Free Expression: " + df4["v2x_freexp_altinf"].round(2).astype(str) +
    "<br>Media Censorship: " + df4["v2mecenefm"].round(1).astype(str) +
    "<br>Civil Society: " + df4["v2csreprss"].round(1).astype(str) +
    "<br>Life Expectancy: " + df4["e_pelifeex"].round(1).astype(str) + " yrs")

fig = go.Figure()

#define four metrics the user can toggle between via dropdown
metrics = [
    ("v2x_freexp_altinf", "Free Expression (0-1)", "RdYlGn", 0, 1),
    ("e_pelifeex", "Life Expectancy (years)", "YlGnBu", 50, 86),
    ("v2mecenefm", "Media Censorship (higher = freer)", "RdYlGn", -3.1, 3.5),
    ("v2csreprss", "Civil Society Freedom", "PuBuGn", -3.8, 3.2),
]

#add one choropleth trace per metric; only first is visible by default
for i, (col, label, cmap, zmin, zmax) in enumerate(metrics):
    fig.add_trace(go.Choropleth(
        locations=df4["country_text_id"],
        z=df4[col],
        text=hover,
        colorscale=cmap, zmin=zmin, zmax=zmax,
        colorbar=dict(title=label),
        hovertemplate="%{text}<extra></extra>",
        visible=(i == 0)
    ))

#dropdown buttons using list comprehension to toggle visibility
buttons = []
for i, (col, label, *_) in enumerate(metrics):
    vis = [j == i for j in range(len(metrics))]
    buttons.append(dict(label=label, method="update",
        args=[{"visible": vis}, {"title": f"{label} Across Countries (2023)"}]))

#configure map layout with dropdown menu
fig.update_layout(
    updatemenus=[dict(buttons=buttons, direction="down",
        x=0.01, xanchor="left", y=1.08, yanchor="top",
        bgcolor="white", bordercolor="#ccc")],
    geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
    width=950, height=550,
    title=dict(text="Freedom of Expression Across Countries (2023)", x=0.5, y=0.98),
    margin=dict(t=120, b=10, l=10, r=10))

#save as interactive HTML file
fig.write_html("../output/democracy_health_map.html")
