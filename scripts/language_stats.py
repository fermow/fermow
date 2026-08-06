import os
import urllib.request
import json
from collections import Counter
from datetime import datetime, timezone

import matplotlib.pyplot as plt


TOKEN = os.environ["PROFILE_STATS_TOKEN"]
USERNAME = "fermow"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "fermow-profile-stats",
}


def api_get(url):
    request = urllib.request.Request(url, headers=HEADERS)

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode())


# --------------------------------------------------
# Get ALL owned repositories
# Public + Private
# --------------------------------------------------

repos = []

page = 1

while True:

    url = (
        "https://api.github.com/user/repos"
        "?visibility=all"
        "&affiliation=owner"
        "&per_page=100"
        f"&page={page}"
    )

    data = api_get(url)

    if not data:
        break

    repos.extend(data)

    if len(data) < 100:
        break

    page += 1


# --------------------------------------------------
# Repository statistics
# --------------------------------------------------

public_repos = 0
private_repos = 0

language_bytes = Counter()

included_repos = 0


for repo in repos:

    # Fork ها را حساب نکن؛ چون کد اصلی متعلق به تو نیست
    if repo.get("fork"):
        continue

    included_repos += 1

    if repo.get("private"):
        private_repos += 1
    else:
        public_repos += 1

    languages = api_get(repo["languages_url"])

    for language, byte_count in languages.items():
        language_bytes[language] += byte_count


# --------------------------------------------------
# Calculate percentages
# --------------------------------------------------

total_bytes = sum(language_bytes.values())

languages_sorted = sorted(
    language_bytes.items(),
    key=lambda item: item[1],
    reverse=True,
)

names = [item[0] for item in languages_sorted]
values = [item[1] for item in languages_sorted]

percentages = [
    value / total_bytes * 100
    for value in values
] if total_bytes else []


# --------------------------------------------------
# Generate chart
# --------------------------------------------------

BG = "#0d1117"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
BLUE = "#58a6ff"

fig_height = max(6.2, 4.8 + len(names) * 0.18)

fig, ax = plt.subplots(
    figsize=(12, fig_height),
    facecolor=BG,
)

ax.set_facecolor(BG)


# Colors
cmap = plt.colormaps["tab20"]

colors = [
    cmap(i % 20)
    for i in range(len(names))
]


if values:

    wedges, _ = ax.pie(
        values,
        startangle=90,
        counterclock=False,
        colors=colors,
        wedgeprops={
            "width": 0.32,
            "edgecolor": BG,
            "linewidth": 2,
        },
    )

    # Center text
    ax.text(
        0,
        0.10,
        f"{len(names)}",
        ha="center",
        va="center",
        fontsize=30,
        fontweight="bold",
        color="white",
    )

    ax.text(
        0,
        -0.10,
        "LANGUAGES",
        ha="center",
        va="center",
        fontsize=10,
        color=MUTED,
    )


# --------------------------------------------------
# Legend
# --------------------------------------------------

legend_labels = [
    f"{name}   {percentage:.1f}%"
    for name, percentage in zip(names, percentages)
]

if values:

    legend = ax.legend(
        wedges,
        legend_labels,
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=False,
        fontsize=10,
        labelspacing=1.0,
    )

    for text in legend.get_texts():
        text.set_color(TEXT)


# --------------------------------------------------
# Titles
# --------------------------------------------------

fig.text(
    0.06,
    0.95,
    "LANGUAGE UNIVERSE",
    fontsize=21,
    fontweight="bold",
    color="white",
)

fig.text(
    0.06,
    0.915,
    "Public + Private GitHub repositories",
    fontsize=11,
    color=MUTED,
)


# --------------------------------------------------
# Statistics
# --------------------------------------------------

fig.text(
    0.06,
    0.83,
    str(included_repos),
    fontsize=23,
    fontweight="bold",
    color=BLUE,
)

fig.text(
    0.06,
    0.795,
    "TOTAL REPOS",
    fontsize=9,
    color=MUTED,
)


fig.text(
    0.20,
    0.83,
    str(public_repos),
    fontsize=23,
    fontweight="bold",
    color=BLUE,
)

fig.text(
    0.20,
    0.795,
    "PUBLIC",
    fontsize=9,
    color=MUTED,
)


fig.text(
    0.32,
    0.83,
    str(private_repos),
    fontsize=23,
    fontweight="bold",
    color=BLUE,
)

fig.text(
    0.32,
    0.795,
    "PRIVATE",
    fontsize=9,
    color=MUTED,
)


fig.text(
    0.44,
    0.83,
    str(len(names)),
    fontsize=23,
    fontweight="bold",
    color=BLUE,
)

fig.text(
    0.44,
    0.795,
    "LANGUAGES",
    fontsize=9,
    color=MUTED,
)


updated = datetime.now(timezone.utc).strftime("%d %b %Y")

fig.text(
    0.06,
    0.035,
    f"Generated automatically from GitHub API • Updated {updated}",
    fontsize=8,
    color=MUTED,
)


ax.axis("equal")

plt.subplots_adjust(
    left=0.05,
    right=0.72,
    top=0.78,
    bottom=0.08,
)


# --------------------------------------------------
# Save
# --------------------------------------------------

os.makedirs("assets", exist_ok=True)

plt.savefig(
    "assets/languages.svg",
    format="svg",
    facecolor=BG,
    bbox_inches="tight",
)

plt.close()

print(
    f"Generated stats from {included_repos} repositories "
    f"({public_repos} public / {private_repos} private)"
)
