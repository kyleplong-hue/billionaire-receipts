#!/usr/bin/env python3
"""Publish the approved Optimus draft once, no earlier than 09:00 Paris time."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ID = 'musk-optimus-timeline'
SITE = f'https://{(ROOT / "CNAME").read_text().strip()}'
URL = f'{SITE}/#{ID}'
RELEASE = datetime(2026, 10, 23, 9, 0, tzinfo=ZoneInfo('Europe/Paris'))
DRAFT = ROOT / 'drafts' / 'optimus-2026.html'
INDEX = ROOT / 'index.html'


def git(*args: str) -> str:
    result = subprocess.run(['git', *args], cwd=ROOT, text=True,
                            capture_output=True, check=True, timeout=50)
    return result.stdout.strip()


def live_contains_post() -> bool:
    request = urllib.request.Request(
        f'{SITE}/?release={int(time.time())}',
        headers={'Cache-Control': 'no-cache', 'User-Agent': 'Receipts scheduled publisher'},
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            page = response.read().decode('utf-8')
        return page.count(f'id="{ID}"') == 1 and page.index(f'id="{ID}"') < page.index('id="zuckerberg-privacy"')
    except (OSError, ValueError):
        return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if not args.dry_run and datetime.now(timezone.utc) < RELEASE.astimezone(timezone.utc):
        raise RuntimeError(f'Publication blocked before {RELEASE.isoformat()}')
    if git('branch', '--show-current') != 'main':
        raise RuntimeError('Expected the main branch')
    if git('status', '--porcelain'):
        raise RuntimeError('Working tree is not clean; refusing to mix unrelated changes')
    draft = DRAFT.read_text()
    if draft.count(f'id="{ID}"') != 1 or draft.count('<article class="receipt"') != 1:
        raise RuntimeError('Draft missing or duplicate post')
    if not (ROOT / 'assets' / 'teslarati-2024-optimus.webp').is_file():
        raise RuntimeError('Source image is missing')
    git('fetch', 'origin', 'main')
    if args.dry_run:
        if git('rev-parse', 'HEAD') != git('rev-parse', 'origin/main'):
            raise RuntimeError('Local branch is not synced to origin/main')
    else:
        git('pull', '--ff-only', 'origin', 'main')
    html = INDEX.read_text()
    if f'id="{ID}"' in html:
        if args.dry_run:
            raise RuntimeError('Draft is already published; dry-run is not applicable')
        if not live_contains_post():
            raise RuntimeError('Post is in source but not yet visible on the live site')
        print(f'Already published and verified: {URL}')
        return
    first = '    <article class="receipt" id="zuckerberg-privacy"'
    if html.count(first) != 1:
        raise RuntimeError('Unexpected feed order; needs editorial review before publishing')
    updated = html.replace(first, draft + first, 1)
    if updated.count(f'id="{ID}"') != 1 or updated.count('<article class="receipt"') != html.count('<article class="receipt"') + 1:
        raise RuntimeError('Unexpected post count after insertion')
    if args.dry_run:
        print('DRY RUN PASS: draft, image, clean/synced main, and insertion point verified; no files changed')
        return
    INDEX.write_text(updated)
    git('diff', '--check')
    git('add', 'index.html')
    git('commit', '-m', 'Publish Optimus delivery forecast receipt')
    git('push', 'origin', 'main')
    commit = git('rev-parse', '--short', 'HEAD')
    for _ in range(9):
        if live_contains_post():
            print(f'Published and verified {URL} (commit {commit})')
            return
        time.sleep(10)
    raise RuntimeError(f'Pushed commit {commit}, but live page did not reflect it within 90 seconds; verify {URL}')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'Scheduled receipt publication failed: {exc}', file=sys.stderr)
        raise
