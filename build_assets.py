"""Build the profile's SVG graphics (banner, section headers, project cards).

Edit the text in BANNER, HEADERS and CARDS below, then run:

    python build_assets.py

Chart thumbnails are read from the sibling project folders and embedded in the
card SVGs, because GitHub will not load external images inside an SVG.
"""

import base64
import io
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image

ROOT = Path(__file__).parent
PROJECTS = ROOT.parent
OUT = ROOT / "assets"

# Palette: light mint
BG = "#F2FBF8"
BORDER = "#D5F2E8"
ACCENT = "#0F766E"
INK = "#0F2E2A"
MUTED = "#4B6B66"
CHIP_BG = "#DDF6EE"
CHIP_INK = "#0F5F57"
LIGHT = "#99E2CB"
MID = "#5ECBA8"
FONT = "Inter, 'Segoe UI', system-ui, -apple-system, Helvetica, Arial, sans-serif"

BANNER = {
    "eyebrow": "JOSH  ·  DATA ANALYST PORTFOLIO",
    "title": "Data analysis portfolio",
    # Wraps automatically (up to 4 lines).
    "intro": (
        "This is a collection of my data analysis projects in Excel, Python, SQL and Power BI "
        "as well as my AI-made projects. Each one starts with a question or problem, works "
        "through the data, and explains what was found."
    ),
    "tools": ["Excel", "Python", "SQL", "Power BI"],
}

HEADERS = {
    "featured": "Featured projects",
    "ai-builds": "AI-built projects",
}

# image: chart path (shown in full, centred) or None to draw a placeholder chart
CARDS = {
    "odds": {
        "eyebrow": "PYTHON  ·  STATISTICS",
        "title": "Premier League Odds Calibration",
        "text": "Are bookmaker odds honest? Almost exactly, but home wins turn out slightly under-priced.",
        "chips": ["Python", "pandas", "SciPy"],
        "image": PROJECTS / "PLOddsAnalysis/images/calibration-home-wins.png",
    },
    "sales": {
        "eyebrow": "EXCEL  ·  BUSINESS ANALYSIS",
        "title": "Sales Analysis",
        "text": "Which sales reps actually make the company money? Profit, margin and performance by rep, month and year.",
        "chips": ["Excel", "Power Query", "PivotTables"],
        "image": PROJECTS / "SalesReps/TotalProfitPerRep.png",
    },
    "energy": {
        "eyebrow": "EXCEL  ·  FORECASTING",
        "title": "Energy Forecasting Accuracy",
        "text": "How close do NESO's day-ahead forecasts get to real UK electricity demand?",
        "chips": ["Excel"],
        "status": "In progress",
        "image": None,
    },
    "next": {
        "eyebrow": "COMING NEXT",
        "title": "SQL and Power BI",
        "text": "Two new projects in progress to round out the portfolio across all four tools.",
        "chips": ["SQL", "Power BI", "DAX"],
        "status": "Planned",
        "image": None,
    },
}


def svg(width: int, height: int, body: str) -> str:
    """Wrap SVG body markup in a root element with the shared font."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">\n'
        f"<style>text {{ font-family: {FONT}; white-space: pre; }}</style>\n{body}\n</svg>\n"
    )


def embed_png(path: Path, width: int) -> str:
    """Shrink a chart image to `width`, returning a base64 JPEG data URI."""
    img = Image.open(path).convert("RGB")
    img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=85, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def chips(items: list[str], x: int, y: int, size: int = 14) -> str:
    """Render a row of rounded tool chips starting at (x, y), with text at `size` px."""
    out = []
    h = round(size * 2.15)
    for item in items:
        w = round(len(item) * size * 0.62 + 2 * size)
        out.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{CHIP_BG}"/>'
            f'<text x="{x + w / 2}" y="{y + round(h * 0.67)}" font-size="{size}" fill="{CHIP_INK}" '
            f'text-anchor="middle">{escape(item)}</text>'
        )
        x += w + round(size * 0.6)
    return "".join(out)


def placeholder_chart(key: str) -> str:
    """Draw a simple mint chart for cards without a real thumbnail yet."""
    if key == "energy":  # forecast vs actual lines
        actual = "60,190 120,150 180,165 240,110 300,125 360,80 420,100 480,70 540,90"
        forecast = "60,180 120,160 180,150 240,125 300,115 360,95 420,90 480,85 540,80"
        return (
            f'<polyline points="{forecast}" fill="none" stroke="{LIGHT}" stroke-width="4" stroke-dasharray="10 8"/>'
            f'<polyline points="{actual}" fill="none" stroke="{ACCENT}" stroke-width="4" stroke-linejoin="round"/>'
        )
    heights = [70, 110, 90, 150, 120, 170]
    return "".join(
        f'<rect x="{80 + i * 78}" y="{230 - h}" width="48" height="{h}" rx="6" fill="{MID if i % 2 else LIGHT}"/>'
        for i, h in enumerate(heights)
    )


THUMB_H = 300  # thumbnail height; tall enough to show a whole chart
DY = THUMB_H - 230  # how far the text block sits below the original 230px layout


def build_card(key: str, card: dict) -> str:
    """Build one 600-wide project card SVG with the chart shown in full."""
    height = 460 + DY
    parts = [
        f'<rect x="1" y="1" width="598" height="{height - 2}" rx="20" fill="#FFFFFF" stroke="{BORDER}" stroke-width="2"/>',
        f'<clipPath id="thumb"><rect x="20" y="20" width="560" height="{THUMB_H}" rx="12"/></clipPath>',
        f'<rect x="20" y="20" width="560" height="{THUMB_H}" rx="12" fill="{BG}"/>',
    ]
    if card["image"]:
        uri = embed_png(card["image"], width=1120)
        parts.append(
            f'<rect x="20" y="20" width="560" height="{THUMB_H}" fill="#FFFFFF" clip-path="url(#thumb)"/>'
            f'<image href="{uri}" x="28" y="28" width="544" height="{THUMB_H - 16}" preserveAspectRatio="xMidYMid meet"/>'
        )
    else:
        parts.append(f'<g clip-path="url(#thumb)"><g transform="translate(0,{DY // 2})">{placeholder_chart(key)}</g></g>')
    if status := card.get("status"):
        w = round(len(status) * 8 + 28)
        parts.append(
            f'<rect x="{564 - w}" y="36" width="{w}" height="28" rx="14" fill="{ACCENT}"/>'
            f'<text x="{564 - w / 2}" y="55" font-size="13" fill="#FFFFFF" text-anchor="middle">{escape(status)}</text>'
        )
    parts.append(
        f'<text x="24" y="{286 + DY}" font-size="13" font-weight="600" fill="{ACCENT}" letter-spacing="1">{escape(card["eyebrow"])}</text>'
        f'<text x="24" y="{320 + DY}" font-size="26" font-weight="600" fill="{INK}">{escape(card["title"])}</text>'
    )
    for i, line in enumerate(textwrap.wrap(card["text"], 54)[:2]):
        parts.append(f'<text x="24" y="{352 + DY + i * 24}" font-size="17" fill="{MUTED}">{escape(line)}</text>')
    parts.append(chips(card["chips"], 24, 404 + DY))
    return svg(600, height, "".join(parts))


def build_banner() -> str:
    """Build the hero banner: title, intro paragraph and tool chips. Height fits the intro."""
    lines = textwrap.wrap(BANNER["intro"], 90)[:4]
    chips_y = 246 + len(lines) * 38
    height = chips_y + 44 + 56
    parts = [
        '<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="1.3" fill="{BORDER}"/></pattern>',
        f'<rect x="1" y="1" width="1198" height="{height - 2}" rx="28" fill="{BG}" stroke="{BORDER}" stroke-width="2"/>',
        '<rect x="860" y="2" width="336" height="150" rx="26" fill="url(#dots)"/>',
        f'<text x="72" y="96" font-size="18" font-weight="600" fill="{ACCENT}" letter-spacing="3">{escape(BANNER["eyebrow"])}</text>',
        f'<text x="69" y="162" font-size="58" font-weight="700" fill="{INK}">{escape(BANNER["title"])}</text>',
        f'<rect x="72" y="186" width="64" height="6" rx="3" fill="{MID}"/>',
    ]
    for i, line in enumerate(lines):
        parts.append(f'<text x="72" y="{240 + i * 38}" font-size="25" fill="{MUTED}">{escape(line)}</text>')
    parts.append(chips(BANNER["tools"], 72, chips_y, size=20))
    return svg(1200, height, "".join(parts))


def build_header(title: str) -> str:
    """Build a 1200x84 solid section header pill."""
    return svg(
        1200,
        84,
        f'<rect x="0" y="0" width="1200" height="84" rx="42" fill="{ACCENT}"/>'
        f'<circle cx="46" cy="42" r="9" fill="{LIGHT}"/>'
        f'<text x="72" y="54" font-size="34" font-weight="700" fill="#FFFFFF">{escape(title)}</text>',
    )


def main() -> None:
    """Write every SVG into assets/."""
    OUT.mkdir(exist_ok=True)
    (OUT / "banner.svg").write_text(build_banner(), encoding="utf-8")
    for key, title in HEADERS.items():
        (OUT / f"header-{key}.svg").write_text(build_header(title), encoding="utf-8")
    for key, card in CARDS.items():
        (OUT / f"card-{key}.svg").write_text(build_card(key, card), encoding="utf-8")
    print("Wrote", ", ".join(sorted(p.name for p in OUT.glob("*.svg"))))


if __name__ == "__main__":
    main()
