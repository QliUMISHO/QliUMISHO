from __future__ import annotations

import html
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


API_BASE = "http://divergence.nyarchlinux.moe/api"
ROOT = Path(__file__).resolve().parents[1]
DIVERGENCE_SVG = ROOT / "worldline-divergence.svg"
NEWS_SVG = ROOT / "worldline-news.svg"
NEWS_COUNT = 3


def fetch_json(path: str, params: dict | None = None) -> dict:
    url = f"{API_BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "worldline-profile-updater/1.0",
            "Accept": "application/json",
        },
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def compact(text: str) -> str:
    return " ".join(text.split())


def truncate(text: str, limit: int) -> str:
    text = compact(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def fmt_divergence(value: object) -> str:
    try:
        return f"{float(value):.6f}"
    except (TypeError, ValueError):
        return "-"


def fmt_impact(value: object) -> str:
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return "-"


def render_divergence_svg(divergence_value: str, updated_at: str) -> str:
    return f"""<svg width="724" height="156" viewBox="0 0 724 156" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .pixel {{
        font-family: "Lucida Console", "Courier New", monospace;
        letter-spacing: 0.5px;
        shape-rendering: crispEdges;
        text-rendering: geometricPrecision;
      }}
      .frame {{
        fill: #161b22;
        stroke: #30363d;
        stroke-width: 1.5;
      }}
      .panel {{
        fill: #0d1117;
        stroke: #30363d;
        stroke-width: 1.2;
      }}
      .title {{
        font-size: 18px;
        font-weight: bold;
        fill: #c9d1d9;
      }}
      .muted {{
        font-size: 13px;
        font-weight: bold;
        fill: #8b949e;
      }}
      .value {{
        font-size: 36px;
        font-weight: bold;
        fill: #58a6ff;
      }}
      .accent {{
        fill: #58a6ff;
      }}
      .chip {{
        fill: #161b22;
        stroke: #30363d;
        stroke-width: 1;
      }}
      .chip-text {{
        font-size: 12px;
        font-weight: bold;
        fill: #c9d1d9;
      }}
    </style>
  </defs>

  <rect x="1" y="1" width="722" height="154" rx="10" class="frame"/>
  <rect x="16" y="16" width="692" height="124" rx="8" class="panel"/>

  <text x="32" y="40" class="pixel title">WORLDLINE DIVERGENCE</text>
  <rect x="32" y="48" width="660" height="3" rx="1.5" class="accent"/>

  <text x="32" y="76" class="pixel muted">CURRENT VALUE</text>
  <text x="32" y="118" class="pixel value">{esc(divergence_value)}</text>

  <rect x="534" y="70" width="158" height="28" rx="6" class="chip"/>
  <text x="613" y="88" text-anchor="middle" class="pixel chip-text">STEINS;GATE</text>

  <text x="32" y="132" class="pixel muted">LAST UPDATE {esc(updated_at)}</text>
</svg>
"""


def render_news_svg(articles: list[dict], updated_at: str) -> str:
    rows = []
    row_y = [48, 102, 156]

    padded = articles[:NEWS_COUNT]
    while len(padded) < NEWS_COUNT:
        padded.append(
            {
                "title": "No article available",
                "field": "-",
                "impact": "-",
                "divergence": "-",
            }
        )

    for idx, article in enumerate(padded, start=1):
        y = row_y[idx - 1]
        title = truncate(str(article.get("title", "Untitled")), 54)
        field = truncate(str(article.get("field", "-")), 12)
        impact = fmt_impact(article.get("impact"))
        divergence = fmt_divergence(article.get("divergence"))

        rows.append(
            f"""
  <rect x="24" y="{y}" width="676" height="40" rx="6" class="row"/>
  <text x="40" y="{y + 15}" class="pixel item-title">{esc(title)}</text>
  <text x="40" y="{y + 31}" class="pixel item-meta">FIELD {esc(field)}  |  IMPACT {esc(impact)}  |  DIV {esc(divergence)}</text>
  <text x="682" y="{y + 16}" text-anchor="end" class="pixel index">{idx:02d}</text>"""
        )

    return f"""<svg width="724" height="224" viewBox="0 0 724 224" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .pixel {{
        font-family: "Lucida Console", "Courier New", monospace;
        letter-spacing: 0.5px;
        shape-rendering: crispEdges;
        text-rendering: geometricPrecision;
      }}
      .frame {{
        fill: #161b22;
        stroke: #30363d;
        stroke-width: 1.5;
      }}
      .panel {{
        fill: #0d1117;
        stroke: #30363d;
        stroke-width: 1.2;
      }}
      .row {{
        fill: #161b22;
        stroke: #30363d;
        stroke-width: 1;
      }}
      .title {{
        font-size: 18px;
        font-weight: bold;
        fill: #c9d1d9;
      }}
      .item-title {{
        font-size: 14px;
        font-weight: bold;
        fill: #c9d1d9;
      }}
      .item-meta {{
        font-size: 11px;
        font-weight: bold;
        fill: #8b949e;
      }}
      .index {{
        font-size: 14px;
        font-weight: bold;
        fill: #58a6ff;
      }}
      .foot {{
        font-size: 11px;
        font-weight: bold;
        fill: #8b949e;
      }}
      .accent {{
        fill: #58a6ff;
      }}
    </style>
  </defs>

  <rect x="1" y="1" width="722" height="222" rx="10" class="frame"/>
  <rect x="16" y="16" width="692" height="192" rx="8" class="panel"/>

  <text x="32" y="34" class="pixel title">LATEST WORLDLINE NEWS</text>
  <rect x="32" y="40" width="660" height="3" rx="1.5" class="accent"/>{''.join(rows)}

  <text x="32" y="196" class="pixel foot">LAST UPDATE {esc(updated_at)}</text>
</svg>
"""


def main() -> None:
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    divergence_payload = fetch_json("/divergence")
    news_payload = fetch_json("/news", {"page": 1, "per_page": NEWS_COUNT})

    divergence_value = fmt_divergence(divergence_payload.get("divergence"))
    articles = news_payload.get("articles", [])

    DIVERGENCE_SVG.write_text(
        render_divergence_svg(divergence_value, now_utc),
        encoding="utf-8",
    )
    NEWS_SVG.write_text(
        render_news_svg(articles, now_utc),
        encoding="utf-8",
    )

    print(f"Updated {DIVERGENCE_SVG.name} and {NEWS_SVG.name}")


if __name__ == "__main__":
    main()
