#!/usr/bin/env python3
"""Publish at most one vetted receipt from drafts/queue.json at 08:00 Paris time."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import json
import re
import subprocess
import sys
import time
import urllib.request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
PARIS = ZoneInfo('Europe/Paris')
INDEX = ROOT / 'index.html'
MANIFEST = ROOT / 'drafts' / 'queue.json'


def git(*args: str) -> str:
    result = subprocess.run(['git', *args], cwd=ROOT, text=True,
                            capture_output=True, check=True, timeout=50)
    return result.stdout.strip()


def live_has_first(post_id: str) -> bool:
    request = urllib.request.Request(
        f'https://receipts.newslings.xyz/?queue={int(time.time())}',
        headers={'Cache-Control': 'no-cache', 'User-Agent': 'Receipts queue publisher'},
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            page = response.read().decode('utf-8')
        ids = re.findall(r'<article class="receipt" id="([^"]+)"', page)
        return ids.count(post_id) == 1 and ids[0] == post_id
    except (OSError, ValueError, IndexError):
        return False


def selected_entry(now: datetime, published: str) -> dict | None:
    entries = json.loads(MANIFEST.read_text())['queue']
    if not isinstance(entries, list):
        raise ValueError('queue must be a list')
    ids = [entry['id'] for entry in entries]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate IDs in queue')
    due = []
    for entry in entries:
        date = datetime.fromisoformat(entry['publish_at'])
        if date.tzinfo is None:
            raise ValueError(f"Missing timezone in {entry['id']}")
        if date <= now and f'id="{entry["id"]}"' not in published:
            due.append((date, entry))
    return sorted(due, key=lambda pair: pair[0])[0][1] if due else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='validate without writing')
    parser.add_argument('--run-due-now', action='store_true', help='manual catch-up after 08:00 local')
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    local = now.astimezone(PARIS)
    if not args.dry_run and not args.run_due_now and local.hour != 8:
        return  # cron ticks at both candidate UTC hours; only 08:00 Paris publishes
    if git('branch', '--show-current') != 'main':
        raise RuntimeError('Expected the main branch')
    if git('status', '--porcelain'):
        raise RuntimeError('Working tree is not clean; refusing to mix changes')
    git('fetch', 'origin', 'main')
    if args.dry_run:
        if git('rev-parse', 'HEAD') != git('rev-parse', 'origin/main'):
            raise RuntimeError('Local branch is not synced to origin/main')
    else:
        git('pull', '--ff-only', 'origin', 'main')
    html = INDEX.read_text()
    entry = selected_entry(now, html)
    if entry is None:
        if args.dry_run:
            print('DRY RUN PASS: queue is empty or has no due unpublished receipts')
        return  # no queued story means no Discord message
    post_id = entry['id']
    draft_path = (ROOT / entry['draft']).resolve()
    if not draft_path.is_relative_to(ROOT / 'drafts') or not draft_path.is_file():
        raise ValueError(f'Invalid draft path: {entry["draft"]}')
    draft = draft_path.read_text()
    if draft.count(f'id="{post_id}"') != 1 or draft.count('<article class="receipt"') != 1:
        raise ValueError(f'Invalid receipt markup: {post_id}')
    match = re.search(r'<summary>Sources \((\d+)\)</summary>\s*<ol>(.*?)</ol>', draft, re.S)
    if not match or int(match.group(1)) != match.group(2).count('<li>'):
        raise ValueError(f'Sources count mismatch: {post_id}')
    for asset in re.findall(r'<img[^>]+src="\./assets/([^\"]+)"', draft):
        if not (ROOT / 'assets' / asset).is_file():
            raise ValueError(f'Missing image: {asset}')
    marker = '    <article class="receipt" id="'
    if html.count(marker) < 1:
        raise RuntimeError('Feed insertion point missing')
    updated = html.replace(marker, draft + marker, 1)
    if updated.count(f'id="{post_id}"') != 1 or updated.count(marker) != html.count(marker) + 1:
        raise RuntimeError('Unexpected feed count after insertion')
    if args.dry_run:
        print(f'DRY RUN PASS: ready to publish {post_id}; clean/synced main, draft, sources, image verified')
        return
    INDEX.write_text(updated)
    git('diff', '--check')
    git('add', 'index.html')
    git('commit', '-m', f'Publish queued receipt {post_id}')
    git('push', 'origin', 'main')
    commit = git('rev-parse', '--short', 'HEAD')
    for _ in range(9):
        if live_has_first(post_id):
            print(f'Published and verified https://receipts.newslings.xyz/#{post_id} (commit {commit})')
            return
        time.sleep(10)
    raise RuntimeError(f'Pushed {commit} but live site not updated within 90 seconds; verify https://receipts.newslings.xyz/#{post_id}')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'Receipt queue publication failed: {exc}', file=sys.stderr)
        raise
