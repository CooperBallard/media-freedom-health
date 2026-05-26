import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

#load data
vdem = pd.read_csv("~/Desktop/QSS20-S26/public_data/V-Dem-CY-Full+Others-v16.csv", low_memory=False)
wb = pd.read_csv("~/Desktop/QSS20-S26/public_data/healthdata.csv", skiprows=4)

#user-defined functions
def classify_media_change(country_id, declined_list):
    """Classify country as declined or stable based on media freedom."""
    if country_id in declined_list:
        return "Media freedom declined"
    return "Media freedom stable or improved"

def compute_residuals(df, x_col, y_col):
    """Regress y on x and return residuals."""
    z = np.polyfit(df[x_col], df[y_col], 1)
    return df[y_col] - np.poly1d(z)(df[x_col])

#visualization 1: backsliding trajectory

#subset V-Dem to 2000-2023 with the columns we need
df = vdem[vdem["year"].between(2000, 2023)][
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
plt.savefig("viz_backsliding.png", dpi=200, bbox_inches="tight")
plt.show()

#visualization 2: Faceted scatter: spending vs life expectancy by freedom
#get most recent health expenditure (try 2022, fall back to 2021, then 2020)
wb["health_exp"] = wb["2022"].fillna(wb["2021"]).fillna(wb["2020"])
wb_clean = wb[["Country Code", "health_exp"]].rename(columns={"Country Code": "country_text_id"})

#merge V-Dem governance data with World Bank spending data for 2023
df3 = vdem[vdem["year"] == 2023][
    ["country_text_id", "country_name", "v2x_freexp_altinf", "e_pelifeex"]
].merge(wb_clean, on="country_text_id", how="left")
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
plt.savefig("viz_faceted_spending.png", dpi=200, bbox_inches="tight")
plt.show()

#visualization 3 Interactive Plotly choropleth map
df4 = vdem[vdem["year"] == 2023][["country_text_id", "country_name",
    "v2x_freexp_altinf", "v2mecenefm", "v2csreprss", "e_pelifeex"]].dropna(
    subset=["v2x_freexp_altinf"]).copy()

#build hover text using string concatenation
hover = (df4["country_name"] +    "<br>Free Expression: " + df4["v2x_freexp_altinf"].round(2).astype(str) +
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
fig.write_html("democracy_health_map.html")
print("Saved interactive map to democracy_health_map.html")
