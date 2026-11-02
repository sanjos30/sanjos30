#!/usr/bin/env python3
"""Generate a self-hosted GitHub profile metrics SVG using GitHub's API."""
import datetime as dt
import html
import json
import os
import pathlib
import urllib.parse
import urllib.request

USER = os.environ.get('PROFILE_USERNAME', 'sanjos30')
TOKEN = os.environ.get('GITHUB_TOKEN', '')
OUT = pathlib.Path('assets/engineering-metrics.svg')
HEADERS = {'Accept': 'application/vnd.github+json', 'User-Agent': 'profile-metrics-builder', 'X-GitHub-Api-Version': '2022-11-28'}
if TOKEN:
    HEADERS['Authorization'] = f'Bearer {TOKEN}'


def request(url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, headers=HEADERS, data=data)
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.load(response)


def get_repos():
    repos = []
    for page in range(1, 5):
        batch = request(f'https://api.github.com/users/{urllib.parse.quote(USER)}/repos?type=owner&sort=pushed&per_page=100&page={page}')
        repos.extend(x for x in batch if not x.get('private') and not x.get('fork'))
        if len(batch) < 100:
            break
    return repos


def contribs():
    query = '''query($login: String!) { user(login: $login) { contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } } } } }'''
    data = request('https://api.github.com/graphql', {'query': query, 'variables': {'login': USER}})
    if data.get('errors'):
        raise RuntimeError(data['errors'])
    return data['data']['user']['contributionsCollection']['contributionCalendar']


def text(x, y, string, size=14, color='#cbd5e1', weight=400):
    return f'<text x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{html.escape(str(string))}</text>'


def main():
    if not TOKEN:
        raise RuntimeError('GITHUB_TOKEN is required for contribution metrics')
    repos = get_repos()
    calendar = contribs()
    today = dt.datetime.now(dt.timezone.utc)
    active = [r for r in repos if r.get('pushed_at') and (today - dt.datetime.fromisoformat(r['pushed_at'].replace('Z', '+00:00'))).days <= 90]
    recent = sorted(repos, key=lambda r: r.get('pushed_at') or '', reverse=True)[:4]
    # Language distribution represents bytes of code, not commit counts or developer proficiency.
    language_bytes = {}
    for repo in repos:
        for lang, count in request(repo['languages_url']).items():
            language_bytes[lang] = language_bytes.get(lang, 0) + count
    languages = sorted(language_bytes.items(), key=lambda kv: kv[1], reverse=True)[:5]
    total = sum(language_bytes.values()) or 1
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="480" viewBox="0 0 900 480" role="img" aria-label="GitHub engineering metrics">',
           '<rect width="900" height="480" rx="18" fill="#0d1424"/>',
           '<rect x="1" y="1" width="898" height="478" rx="18" fill="none" stroke="#26374e"/>',
           text(30, 42, 'ENGINEERING ACTIVITY', 18, '#f8fafc', 700),
           text(30, 65, f'@{USER}  •  Updated {today:%d %b %Y} UTC', 12, '#95a7c1')]
    metrics = [('CONTRIBUTIONS / 12 MO', calendar['totalContributions']), ('PUBLIC SOURCE REPOS', len(repos)), ('ACTIVE / 90 DAYS', len(active))]
    for i, (label, val) in enumerate(metrics):
        x = 30 + 285 * i
        svg.extend([f'<rect x="{x}" y="84" width="265" height="94" rx="10" fill="#152137"/>', text(x+15, 110, label, 11, '#94a3b8', 700), text(x+15, 155, f'{val:,}', 34, '#7dd3fc', 700)])
    svg.append(text(30, 211, 'TOP LANGUAGES  •  PUBLIC NON-FORK REPOS (BY CODE SIZE)', 12, '#dce6f3', 700))
    maxval = max([v for _, v in languages], default=1)
    for i, (lang, val) in enumerate(languages):
        y = 243 + i*38
        svg += [text(30, y, lang, 12, '#cbd5e1'), f'<rect x="145" y="{y-13}" width="230" height="13" rx="6" fill="#25344a"/>', f'<rect x="145" y="{y-13}" width="{230*val/maxval:.1f}" height="13" rx="6" fill="#38bdf8"/>', text(388, y, f'{val/total:.1%}', 12, '#94a3b8')]
    svg.append(text(490, 211, 'RECENTLY UPDATED PROJECTS', 12, '#dce6f3', 700))
    for i, r in enumerate(recent):
        y = 245+i*45
        pushed = (r.get('pushed_at') or '')[:10]
        svg += [text(490, y, r['name'][:36], 15, '#e2e8f0', 600), text(490, y+18, f'Last pushed: {pushed}', 11, '#94a3b8')]
    svg.append(text(30, 455, 'Contribution counts follow GitHub’s profile visibility settings. Repositories exclude forks.', 11, '#7e91ac'))
    svg.append('</svg>')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text('\n'.join(svg), encoding='utf-8')
    print(f'Generated {OUT}: {len(repos)} repositories, {calendar["totalContributions"]} contributions')


if __name__ == '__main__':
    main()
