#!/usr/bin/env python3
import json, math, subprocess

USER = "fermow"
EXCLUDE = {"html", "css"}
CHART = "profile-langs.svg"


def gh_api(path: str) -> json:
    return json.loads(subprocess.check_output(["gh", "api", path]))


def count_languages() -> dict:
    counts = {}
    for r in gh_api(f"/users/{USER}/repos?per_page=100"):
        if r.get("fork") or r.get("private"):
            continue
        try:
            data = gh_api(f"/repos/{USER}/{r['name']}/languages")
        except subprocess.CalledProcessError:
            continue
        # dominant language of this repo = one "vote"
        if not data:
            continue
        top = max(data, key=data.get).lower()
        if top not in EXCLUDE:
            counts[top] = counts.get(top, 0) + 1
    return counts


NAMES = {
    "typescript": "TypeScript", "javascript": "JavaScript", "python": "Python",
    "go": "Go", "jupyter notebook": "Jupyter Notebook", "java": "Java",
    "c++": "C++", "shell": "Shell", "c": "C", "rust": "Rust",
}
COLORS = {
    "typescript": "#3178C6", "python": "#3776AB", "javascript": "#F7DF1E",
    "go": "#00ADD8", "jupyter notebook": "#F37626", "java": "#E76F00",
    "c++": "#f34b7d", "shell": "#89e051", "c": "#555555",
}


def render(counts: dict) -> None:
    total = sum(counts.values())
    if not total:
        raise SystemExit("no usable language data")
    items = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:6]
    cx, cy, r = 150, 145, 112
    C = 2 * math.pi * r
    parts, leg = [], []
    cum, ly = 0.0, cy - (len(items) - 1) * 13 - 24
    lx = cx + r + 82
    for key, count in items:
        arc = C * count / total
        color = COLORS.get(key, "#8b5cf6")
        parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" '
            f'stroke-width="48" stroke-dasharray="{arc:.1f} {C - arc:.1f}" '
            f'stroke-dashoffset="{-cum:.1f}" transform="rotate(-90 {cx} {cy})"/>'
        )
        cum += arc
        pct = round(count / total * 100, 1)
        leg.append(
            f'<rect x="{lx}" y="{ly - 9}" width="14" height="14" rx="3" fill="{color}"/>'
            f'<text x="{lx + 24}" y="{ly + 1}" font-size="15" fill="#d1d5db">{NAMES.get(key, key)}</text>'
            f'<text x="{lx + 150}" y="{ly + 1}" font-size="15" fill="#c4b5fd" text-anchor="end">{pct:.0f}%</text>'
        )
        ly += 27
    W, H = lx + 158, cy * 2 + 24
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="Segoe UI, Arial, sans-serif">'
        f'<rect width="100%" height="100%" fill="#0d1117"/>'
        + "".join(parts)
        + f'<text x="{cx}" y="{cy - 8}" text-anchor="middle" font-size="20" font-weight="600" fill="#e5e7eb">@{USER}</text>'
        + f'<text x="{cx}" y="{cy + 16}" text-anchor="middle" font-size="14" fill="#9ca3af">public repos · per-repo</text>'
        + "".join(leg)
        + "</svg>"
    )
    with open(CHART, "w") as fh:
        fh.write(svg)
    summary = ", ".join(f"{NAMES.get(k, k)} {round(v / total * 100)}%" for k, v in items)
    print(f"ok: {summary}")


if __name__ == "__main__":
    render(count_languages())