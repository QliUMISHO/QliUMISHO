import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, '..');
const outputSvg = path.join(repoRoot, 'assets', 'worldline-card.svg');
const outputJson = path.join(repoRoot, 'data', 'worldline.json');

const API_BASE_CANDIDATES = [
  process.env.WORLDLINE_API_BASE,
  'https://divergence.nyarchlinux.moe/api',
  'http://divergence.nyarchlinux.moe/api',
].filter(Boolean).map((v) => v.replace(/\/+$/, ''));

function escapeXml(value = '') {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

function truncate(text, max = 78) {
  const clean = String(text || '').replace(/\s+/g, ' ').trim();
  if (clean.length <= max) return clean;
  return `${clean.slice(0, Math.max(0, max - 1)).trimEnd()}…`;
}

function wrapText(text, maxCharsPerLine = 52, maxLines = 2) {
  const words = String(text || '').replace(/\s+/g, ' ').trim().split(' ');
  const lines = [];
  let current = '';

  for (const word of words) {
    if (!word) continue;
    const next = current ? `${current} ${word}` : word;
    if (next.length <= maxCharsPerLine) {
      current = next;
      continue;
    }
    if (current) lines.push(current);
    current = word;
    if (lines.length === maxLines - 1) break;
  }

  if (lines.length < maxLines && current) lines.push(current);
  if (lines.length > maxLines) lines.length = maxLines;

  const original = String(text || '').replace(/\s+/g, ' ').trim();
  const joined = lines.join(' ');
  if (original.length > joined.length && lines.length) {
    lines[lines.length - 1] = truncate(lines[lines.length - 1], maxCharsPerLine);
  }
  return lines;
}

async function fetchJson(url) {
  const response = await fetch(url, {
    headers: {
      'user-agent': 'worldline-profile-card/1.0 (+https://github.com)',
      'accept': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status} for ${url}`);
  }

  return response.json();
}

function normalizeNews(items) {
  return (Array.isArray(items) ? items : [])
    .map((item) => ({
      title: String(item?.title || '').trim(),
      description: String(item?.description || '').trim(),
      field: String(item?.field || 'UNKNOWN').trim().toUpperCase(),
      impact: Number(item?.impact ?? 0),
      divergence: item?.divergence ?? null,
      independent_divergence: item?.independent_divergence ?? null,
    }))
    .filter((item) => item.title)
    .sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact));
}

function loadPreviousData() {
  if (!fs.existsSync(outputJson)) return null;
  try {
    return JSON.parse(fs.readFileSync(outputJson, 'utf8'));
  } catch {
    return null;
  }
}

async function loadLiveData() {
  let lastError;
  for (const base of API_BASE_CANDIDATES) {
    try {
      const [divergenceResult, newsResult] = await Promise.all([
        fetchJson(`${base}/divergence`),
        fetchJson(`${base}/news?page=1&per_page=100`),
      ]);

      const topNews = normalizeNews(newsResult?.articles).slice(0, 3);
      const divergence = Number(divergenceResult?.divergence ?? NaN);

      if (!Number.isFinite(divergence)) {
        throw new Error(`Invalid divergence payload from ${base}`);
      }

      return {
        status: 'ok',
        stale: false,
        api_base: base,
        fetched_at: new Date().toISOString(),
        divergence,
        total_articles_considered: Array.isArray(newsResult?.articles) ? newsResult.articles.length : 0,
        top_news: topNews,
      };
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError || new Error('Failed to reach any API base candidate.');
}

function withFallback(liveData, previousData) {
  if (liveData) return liveData;

  if (previousData) {
    return {
      ...previousData,
      status: 'stale',
      stale: true,
      fetched_at: previousData.fetched_at || new Date().toISOString(),
    };
  }

  return {
    status: 'unavailable',
    stale: true,
    api_base: API_BASE_CANDIDATES[0] || 'https://divergence.nyarchlinux.moe/api',
    fetched_at: new Date().toISOString(),
    divergence: null,
    total_articles_considered: 0,
    top_news: [
      {
        title: 'No live API data yet',
        description: 'Run this workflow in your repository to populate the card with real worldline data.',
        field: 'BOOT',
        impact: 0,
      },
      {
        title: 'Divergence meter API unreachable from the local generator',
        description: 'The GitHub Action is ready and will render the real feed when it runs on GitHub.',
        field: 'NET',
        impact: 0,
      },
      {
        title: 'This placeholder SVG will be replaced automatically',
        description: 'The first successful scheduled or manual run writes the live top-impact news list.',
        field: 'SYNC',
        impact: 0,
      },
    ],
  };
}

function fieldColor(field) {
  const map = {
    ALPHA: '#7ee787',
    BETA: '#79c0ff',
    GAMMA: '#ff7b72',
    DELTA: '#d2a8ff',
    OMEGA: '#ffa657',
    BOOT: '#f2cc60',
    NET: '#ff7b72',
    SYNC: '#79c0ff',
  };
  return map[field] || '#9e6eff';
}

function buildNewsBlock(article, index) {
  const y = 170 + index * 64;
  const badgeColor = fieldColor(article.field);
  const titleLines = wrapText(article.title, 48, 2);
  const description = truncate(article.description || 'No description provided by the API.', 74);
  const impactLabel = Number.isFinite(article.impact) ? article.impact.toFixed(3) : '0.000';

  const titleTspans = titleLines
    .map((line, i) => `<tspan x="386" dy="${i === 0 ? 0 : 18}">${escapeXml(line)}</tspan>`)
    .join('');

  return `
    <rect x="356" y="${y - 28}" width="584" height="54" rx="16" fill="#ffffff" fill-opacity="0.04" stroke="#ffffff" stroke-opacity="0.07"/>
    <rect x="376" y="${y - 14}" width="56" height="24" rx="12" fill="${badgeColor}" fill-opacity="0.16" stroke="${badgeColor}" stroke-opacity="0.55"/>
    <text x="404" y="${y + 2}" fill="${badgeColor}" font-family="Segoe UI, Inter, Arial, sans-serif" font-size="11" text-anchor="middle" font-weight="700">${escapeXml(article.field)}</text>
    <text x="450" y="${y + 2}" fill="#f0f6fc" font-family="Segoe UI, Inter, Arial, sans-serif" font-size="13" font-weight="700">Impact ${escapeXml(impactLabel)}</text>
    <text x="386" y="${y + 24}" fill="#8b949e" font-family="Segoe UI, Inter, Arial, sans-serif" font-size="11">${escapeXml(description)}</text>
    <text x="386" y="${y - 2}" fill="#e6edf3" font-family="Segoe UI, Inter, Arial, sans-serif" font-size="13" font-weight="600">${titleTspans}</text>
  `;
}

function renderSvg(data) {
  const divergenceText = Number.isFinite(data.divergence) ? data.divergence.toFixed(6) : '—.—————';
  const statusText = data.status === 'ok' ? 'LIVE' : data.status === 'stale' ? 'STALE CACHE' : 'WAITING FOR FIRST RUN';
  const statusColor = data.status === 'ok' ? '#7ee787' : data.status === 'stale' ? '#f2cc60' : '#79c0ff';
  const statusWidth = Math.max(132, Math.min(250, statusText.length * 7 + 34));
  const fetched = new Date(data.fetched_at);
  const timestamp = Number.isNaN(fetched.getTime())
    ? 'Updated: unknown'
    : `Updated: ${fetched.toISOString().replace('T', ' ').replace(/\.\d+Z$/, ' UTC')}`;

  const newsBlocks = (data.top_news || []).slice(0, 3).map(buildNewsBlock).join('\n');

  return `<?xml version="1.0" encoding="UTF-8"?>
<svg width="980" height="380" viewBox="0 0 980 380" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
  <title id="title">Worldline status card</title>
  <desc id="desc">Dynamic GitHub profile card showing the latest divergence value and the top three highest-impact news items from the Divergence Meter API.</desc>
  <defs>
    <linearGradient id="bg" x1="40" y1="20" x2="940" y2="360" gradientUnits="userSpaceOnUse">
      <stop stop-color="#0d1117"/>
      <stop offset="1" stop-color="#111827"/>
    </linearGradient>
    <linearGradient id="accent" x1="40" y1="20" x2="320" y2="320" gradientUnits="userSpaceOnUse">
      <stop stop-color="#9e6eff"/>
      <stop offset="1" stop-color="#58a6ff"/>
    </linearGradient>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="10" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <rect x="10" y="10" width="960" height="360" rx="28" fill="url(#bg)" stroke="#ffffff" stroke-opacity="0.08"/>
  <circle cx="180" cy="120" r="110" fill="url(#accent)" fill-opacity="0.10" filter="url(#glow)"/>
  <circle cx="910" cy="58" r="40" fill="#58a6ff" fill-opacity="0.06"/>
  <circle cx="845" cy="320" r="68" fill="#9e6eff" fill-opacity="0.05"/>

  <text x="40" y="54" fill="#f0f6fc" font-family="Segoe UI, Inter, Arial, sans-serif" font-size="26" font-weight="700">Worldline Status</text>
  <text x="40" y="78" fill="#8b949e" font-family="Segoe UI, Inter, Arial, sans-serif" font-size="13">Divergence Meter API • Top 3 news by impact</text>

  <rect x="40" y="98" width="${statusWidth}" height="28" rx="14" fill="${statusColor}" fill-opacity="0.14" stroke="${statusColor}" stroke-opacity="0.45"/>
  <text x="${40 + statusWidth / 2}" y="116" fill="${statusColor}" font-family="Segoe UI, Inter, Arial, sans-serif" font-size="12" font-weight="700" text-anchor="middle">${escapeXml(statusText)}</text>

  <text x="40" y="164" fill="#8b949e" font-family="Segoe UI, Inter, Arial, sans-serif" font-size="12" letter-spacing="1.8">CURRENT DIVERGENCE</text>
  <text x="40" y="234" fill="#e6edf3" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="52" font-weight="700">${escapeXml(divergenceText)}</text>
  <text x="40" y="266" fill="#8b949e" font-family="Segoe UI, Inter, Arial, sans-serif" font-size="13">${escapeXml(timestamp)}</text>
  <text x="40" y="292" fill="#8b949e" font-family="Segoe UI, Inter, Arial, sans-serif" font-size="13">Source base: ${escapeXml(data.api_base || 'unknown')}</text>
  <text x="40" y="318" fill="#8b949e" font-family="Segoe UI, Inter, Arial, sans-serif" font-size="13">Articles scanned this run: ${escapeXml(data.total_articles_considered ?? 0)}</text>

  <line x1="336" y1="44" x2="336" y2="336" stroke="#ffffff" stroke-opacity="0.08"/>
  <text x="356" y="54" fill="#f0f6fc" font-family="Segoe UI, Inter, Arial, sans-serif" font-size="20" font-weight="700">Top Impact News</text>
  <text x="356" y="78" fill="#8b949e" font-family="Segoe UI, Inter, Arial, sans-serif" font-size="13">Highest absolute impact from <tspan font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">/api/news</tspan></text>

  ${newsBlocks}

  <rect x="40" y="338" width="900" height="1" fill="#ffffff" fill-opacity="0.08"/>
  <text x="40" y="356" fill="#6e7681" font-family="Segoe UI, Inter, Arial, sans-serif" font-size="11">Generated for GitHub README • Commit this SVG and embed it directly in your profile repository README.</text>
</svg>`;
}

async function main() {
  const previousData = loadPreviousData();
  let liveData = null;
  let errorMessage = null;

  try {
    liveData = await loadLiveData();
  } catch (error) {
    errorMessage = error instanceof Error ? error.message : String(error);
  }

  const data = withFallback(liveData, previousData);
  if (errorMessage) data.last_error = errorMessage;

  fs.mkdirSync(path.dirname(outputJson), { recursive: true });
  fs.mkdirSync(path.dirname(outputSvg), { recursive: true });
  fs.writeFileSync(outputJson, JSON.stringify(data, null, 2) + '\n');
  fs.writeFileSync(outputSvg, renderSvg(data));

  console.log(`SVG written to ${outputSvg}`);
  console.log(`Data written to ${outputJson}`);
  if (errorMessage) console.warn(`Live fetch warning: ${errorMessage}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
