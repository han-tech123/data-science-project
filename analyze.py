"""Reproduce two descriptive charts for the Palmer Penguins portfolio project.

Run from this repository's root: python3 analyze.py
Only Python's standard library is required.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "penguins.csv"
FIGURES = ROOT / "figures"
COLORS = {"Adelie": "#237A91", "Chinstrap": "#DC6B45", "Gentoo": "#7359A6"}


def svg_start(width: int, height: int, title: str, description: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title>',
        f'<desc id="desc">{escape(description)}</desc>',
        f'<rect width="{width}" height="{height}" fill="#F7F9FC"/>',
    ]


def txt(x: float, y: float, value: str, size: int = 16, color: str = "#17324D", anchor: str = "start", weight: str = "normal") -> str:
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, sans-serif" '
            f'font-size="{size}" fill="{color}" text-anchor="{anchor}" '
            f'font-weight="{weight}">{escape(value)}</text>')


def save_svg(name: str, lines: list[str]) -> None:
    FIGURES.mkdir(exist_ok=True)
    (FIGURES / name).write_text("\n".join(lines + ["</svg>", ""]), encoding="utf-8")


def load_rows() -> list[dict[str, str]]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 344, "Unexpected source row count"
    assert {row["species"] for row in rows} == set(COLORS), "Unexpected species"
    return rows


def mass_chart(rows: list[dict[str, str]]) -> None:
    masses: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        if row["body_mass_g"] not in ("", "NA"):
            masses[row["species"]].append(float(row["body_mass_g"]))
    lines = svg_start(900, 450, "Average body mass by species",
                      "Horizontal bars show mean body mass in grams. Thin whiskers show plus or minus one standard deviation. Gentoo has the highest mean.")
    lines += [txt(40, 52, "Average body mass by species", 26, weight="bold"),
              txt(40, 82, "Palmer Penguins • measured birds only; whiskers = ±1 standard deviation", 15, "#52677B")]
    x0, scale = 175, 0.105
    for tick in range(0, 7000, 1000):
        x = x0 + tick * scale
        lines.append(f'<line x1="{x:.1f}" y1="112" x2="{x:.1f}" y2="357" stroke="#D9E2EB"/>')
        lines.append(txt(x, 383, f"{tick:,}", 13, "#52677B", "middle"))
    for i, species in enumerate(COLORS):
        vals = masses[species]
        avg, sd = mean(vals), stdev(vals)
        y = 143 + i * 78
        lines.append(txt(154, y + 25, species, 18, anchor="end", weight="bold"))
        lines.append(f'<rect x="{x0}" y="{y}" width="{avg * scale:.1f}" height="39" rx="5" fill="{COLORS[species]}"/>')
        whisker_x1, whisker_x2 = x0 + (avg - sd) * scale, x0 + (avg + sd) * scale
        lines.append(f'<line x1="{whisker_x1:.1f}" y1="{y + 19}" x2="{whisker_x2:.1f}" y2="{y + 19}" stroke="#17324D" stroke-width="3"/>')
        for x in [whisker_x1, whisker_x2]:
            lines.append(f'<line x1="{x:.1f}" y1="{y + 12}" x2="{x:.1f}" y2="{y + 26}" stroke="#17324D" stroke-width="3"/>')
        lines.append(txt(810, y + 57, f"{avg:,.0f} g  (n={len(vals)})", 14, "#17324D", "end"))
    lines.append(txt(505, 414, "Body mass (grams)", 15, "#52677B", "middle"))
    save_svg("mean_body_mass.svg", lines)
    for species in COLORS:
        vals = masses[species]
        print(f"{species}: mean body mass {mean(vals):.1f} g; n={len(vals)}; SD={stdev(vals):.1f} g")


def scatter_chart(rows: list[dict[str, str]]) -> None:
    points = [(row["species"], float(row["bill_length_mm"]), float(row["body_mass_g"]))
              for row in rows if row["bill_length_mm"] not in ("", "NA")
              and row["body_mass_g"] not in ("", "NA")]
    lines = svg_start(900, 570, "Bill length and body mass by species",
                      "Scatter plot of individual penguins, with bill length in millimeters on the horizontal axis and body mass in grams on the vertical axis. Colors identify species.")
    lines += [txt(40, 52, "Bill length and body mass", 26, weight="bold"),
              txt(40, 82, f"{len(points)} birds with both measurements • each dot is one bird", 15, "#52677B")]
    left, top, right, bottom = 105, 125, 805, 455
    xmap = lambda v: left + (v - 30) / 30 * (right - left)
    ymap = lambda v: bottom - (v - 2500) / 4000 * (bottom - top)
    for tick in range(30, 61, 5):
        x = xmap(tick)
        lines.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" stroke="#D9E2EB"/>')
        lines.append(txt(x, 482, str(tick), 13, "#52677B", "middle"))
    for tick in range(2500, 6501, 1000):
        y = ymap(tick)
        lines.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#D9E2EB"/>')
        lines.append(txt(87, y + 5, f"{tick:,}", 13, "#52677B", "end"))
    for species, bill, mass in points:
        lines.append(f'<circle cx="{xmap(bill):.1f}" cy="{ymap(mass):.1f}" r="4.3" fill="{COLORS[species]}" fill-opacity="0.63"/>')
    lines.append(txt(455, 518, "Bill length (mm)", 15, "#52677B", "middle"))
    lines.append('<text x="24" y="290" transform="rotate(-90 24 290)" font-family="Arial, sans-serif" font-size="15" fill="#52677B" text-anchor="middle">Body mass (g)</text>')
    for i, species in enumerate(COLORS):
        x = 420 + i * 135
        lines.append(f'<circle cx="{x}" cy="545" r="6" fill="{COLORS[species]}"/>')
        lines.append(txt(x + 13, 550, species, 14))
    save_svg("bill_length_vs_mass.svg", lines)
    print(f"Scatter plot: {len(points)} complete observations")


if __name__ == "__main__":
    data = load_rows()
    mass_chart(data)
    scatter_chart(data)
