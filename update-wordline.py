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

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "github-profile-worldline-updater/1.0",
            "Accept": "application/json",
        },
    )

    with urllib.request.urlopen(req, timeout=20) as response:
        body = response.read().decode("utf-8")
        return json.loads(body)


def esc(text: object) -> str:
    return html.escape(str(text), quote=True)


def truncate(text: str, limit: int) -> str:
    clean = " ".join(text.split())
    return clean if len(clean) <= limit else clean[: limit - 1] + "…"


def fmt_impact(value: object) -> str:
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return "-"


def fmt_divergence(value: object) -> str:
    try:
        return f"{float(value):.6f}"
    except (TypeError, ValueError):
        return str(value)


def render_divergence_svg(divergence_value: str, updated_at: str) -> str:
    return f"""<svg width="724" height="148" viewBox="0 0 724 148" xmlns="http://www.w3.org/2000/svg">
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
        font-size: 34px;
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

  <rect x="1" y="1" width="722" height="146" rx="10" class="frame"/>
  <rect x="16" y="16" width="692" height="116" rx="8" class="panel"/>

  <text x="32" y="40" class="pixel title">WORLDLINE DIVERGENCE</text>
  <rect x="32" y="50" width="660" height="3" rx="1.5" class="accent"/>

  <text x="32" y="74" class="pixel muted">CURRENT VALUE</text>
  <text x="32" y="114" class="pixel value">{esc(divergence_value)}</text>

  <rect x="544" y="76" width="148" height="24" rx="6" class="chip"/>
  <text x="618" y="92" text-anchor="middle" class="pixel chip-text">STEINS;GATE</text>

  <text x="32" y="126" class="pixel muted">LAST UPDATE {esc(updated_at)}</text>
</svg>
"""


def render_news_svg(articles: list[dict], updated_at: str) -> str:
    rows = []
    row_y = [44, 92, 140]

    padded_articles = articles[:NEWS_COUNT]
    while len(padded_articles) < NEWS_COUNT:
        padded_articles.append(
            {
                "title": "No article available",
                "field": "-",
                "impact": "-",
                "divergence": "-",
            }
        )

    for index, article in enumerate(padded_articles):
        y = row_y[index]
        title = truncate(str(article.get("title", "Untitled")), 52)
        field = truncate(str(article.get("field", "-")), 12)
        impact = fmt_impact(article.get("impact"))
        divergence = fmt_divergence(article.get("divergence", "-"))

        rows.append(
            f"""
  <rect x="24" y="{y}" width="676" height="38" rx="6" class="row"/>
  <text x="40" y="{y + 15}" class="pixel item-title">{esc(title)}</text>
  <text x="40" y="{y + 30}" class="pixel item-meta">FIELD {esc(field)}  |  IMPACT {esc(impact)}  |  DIV {esc(divergence)}</text>
  <text x="682" y="{y + 15}" text-anchor="end" class="pixel index">{index + 1:02d}</text>
"""
        )

    return f"""<svg width="724" height="196" viewBox="0 0 724 196" xmlns="http://www.w3.org/2000/svg">
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

  <rect x="1" y="1" width="722" height="194" rx="10" class="frame"/>
  <rect x="16" y="16" width="692" height="164" rx="8" class="panel"/>

  <text x="32" y="34" class="pixel title">LATEST WORLDLINE NEWS</text>
  <rect x="32" y="40" width="660" height="3" rx="1.5" class="accent"/>
  {''.join(rows)}
  <text x="32" y="170" class="pixel foot">LAST UPDATE {esc(updated_at)}</text>
</svg>
"""


def main() -> None:
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    divergence_data = fetch_json("/divergence")
    news_data = fetch_json("/news", {"page": 1, "per_page": NEWS_COUNT})

    divergence_value = fmt_divergence(divergence_data.get("divergence", "-"))
    articles = news_data.get("articles", [])

    DIVERGENCE_SVG.write_text(
        render_divergence_svg(divergence_value, now_utc),
        encoding="utf-8",
    )
    NEWS_SVG.write_text(
        render_news_svg(articles, now_utc),
        encoding="utf-8",
    )

    print("Updated:", DIVERGENCE_SVG.name, NEWS_SVG.name)


if __name__ == "__main__":
    main()
