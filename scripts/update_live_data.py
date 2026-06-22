#!/usr/bin/env python3
"""Fetch daily public updates for the local elon-musk-live skill."""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import email.utils
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


DEFAULT_SKILL_ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "jiangyude-elon-musk-live-skill/0.1"
PUBLIC_WEB_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"


def now_taipei() -> dt.datetime:
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))


def read_json(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    tmp.replace(path)


def fetch_url(url: str, headers: dict[str, str] | None = None, timeout: int = 30) -> bytes:
    request_headers = {"User-Agent": USER_AGENT}
    if headers:
        request_headers.update(headers)
    req = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def stable_id(*parts: str) -> str:
    joined = "\n".join(part or "" for part in parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:24]


def parse_rfc_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return value
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc).isoformat()


def text_of(node: ET.Element, child: str) -> str:
    found = node.find(child)
    if found is None or found.text is None:
        return ""
    return html.unescape(found.text).strip()


def strip_html(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def infer_source_type(feed_tier: str, title: str, description: str) -> str:
    commentary_markers = (
        "opinion",
        "commentary",
        "analysis",
        "column",
        "editorial",
        "why ",
        "what ",
        "how ",
        "actually",
        "評論",
        "觀點",
        "專欄",
    )
    haystack = f"{title} {description}".lower()
    if any(marker in haystack for marker in commentary_markers):
        return "news_commentary"
    return feed_tier


def fetch_rss(feed: dict) -> tuple[list[dict], list[str]]:
    errors: list[str] = []
    items: list[dict] = []
    try:
        raw = fetch_url(feed["url"])
        root = ET.fromstring(raw)
    except (urllib.error.URLError, ET.ParseError, KeyError) as exc:
        return [], [f"{feed.get('id', 'rss')}: {exc}"]

    channel = root.find("channel")
    if channel is None:
        return [], [f"{feed.get('id', 'rss')}: missing channel"]

    for item in channel.findall("item"):
        title = text_of(item, "title")
        link = text_of(item, "link")
        published = parse_rfc_date(text_of(item, "pubDate"))
        description = strip_html(text_of(item, "description"))
        source_node = item.find("source")
        publisher = html.unescape(source_node.text).strip() if source_node is not None and source_node.text else ""
        item_id = stable_id(feed.get("id", ""), link, title, published or "")
        source_type = infer_source_type(feed.get("tier", "news_report"), title, description)
        items.append(
            {
                "id": item_id,
                "source_type": source_type,
                "source_id": feed.get("id"),
                "source_label": feed.get("label", feed.get("id")),
                "publisher": publisher,
                "title": title,
                "url": link,
                "published_at": published,
                "summary": description,
                "captured_at": now_taipei().isoformat(),
            }
        )
    return items, errors


def x_api_get(path: str, token: str, params: dict[str, str] | None = None) -> dict:
    query = urllib.parse.urlencode(params or {})
    url = f"https://api.twitter.com/2/{path}"
    if query:
        url = f"{url}?{query}"
    raw = fetch_url(url, headers={"Authorization": f"Bearer {token}"})
    return json.loads(raw.decode("utf-8"))


def fetch_x_posts(config: dict) -> tuple[list[dict], list[str]]:
    if not config.get("enabled", True):
        return [], ["x: disabled in config"]

    token = os.environ.get("X_BEARER_TOKEN")
    if not token:
        return [], ["x: skipped because X_BEARER_TOKEN is not set"]

    username = config.get("username", "elonmusk")
    max_results = str(config.get("max_results", 10))
    try:
        user_payload = x_api_get(
            f"users/by/username/{urllib.parse.quote(username)}",
            token,
            {"user.fields": "description,verified"},
        )
        user_id = user_payload["data"]["id"]
        tweets_payload = x_api_get(
            f"users/{user_id}/tweets",
            token,
            {
                "max_results": max_results,
                "tweet.fields": "created_at,public_metrics,referenced_tweets,entities",
                "exclude": "retweets",
            },
        )
    except (urllib.error.HTTPError, urllib.error.URLError, KeyError, json.JSONDecodeError) as exc:
        return [], [f"x: {exc}"]

    items: list[dict] = []
    for tweet in tweets_payload.get("data", []):
        tweet_id = tweet.get("id", "")
        url = f"https://x.com/{username}/status/{tweet_id}" if tweet_id else ""
        items.append(
            {
                "id": f"x-{tweet_id}",
                "source_type": "musk_direct",
                "source_id": "x-api-elonmusk",
                "source_label": f"X @{username}",
                "publisher": f"@{username}",
                "title": tweet.get("text", "").split("\n", 1)[0][:120],
                "url": url,
                "published_at": tweet.get("created_at"),
                "summary": tweet.get("text", ""),
                "public_metrics": tweet.get("public_metrics", {}),
                "captured_at": now_taipei().isoformat(),
            }
        )
    return items, []


def decode_x_tweet_id(encoded: str) -> str:
    padded = encoded + ("=" * (-len(encoded) % 4))
    decoded = base64.b64decode(padded).decode("utf-8", errors="replace")
    if decoded.startswith("Tweet:"):
        return decoded.split(":", 1)[1]
    return decoded


def fetch_x_public_profile(config: dict) -> tuple[list[dict], list[str]]:
    if not config.get("public_profile_enabled", True):
        return [], ["x_public: disabled in config"]

    username = config.get("username", "elonmusk")
    recent_days = int(config.get("public_profile_recent_days", 7))
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=recent_days)
    url = f"https://x.com/{urllib.parse.quote(username)}"

    try:
        raw = fetch_url(url, headers={"User-Agent": PUBLIC_WEB_USER_AGENT})
        page = raw.decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        return [], [f"x_public: {exc}"]

    pattern = re.compile(
        r"client:VHdlZXQ6([A-Za-z0-9+/=]+):details.*?full_text:\"((?:\\.|[^\"\\])*)\".*?created_at_ms:(\d+)",
        re.S,
    )
    by_tweet_id: dict[str, dict] = {}
    for match in pattern.finditer(page):
        try:
            tweet_id = decode_x_tweet_id(match.group(1))
            text = json.loads(f'"{match.group(2)}"')
            created_ms = int(match.group(3))
        except (ValueError, json.JSONDecodeError):
            continue
        created_at = dt.datetime.fromtimestamp(created_ms / 1000, tz=dt.timezone.utc)
        if created_at < cutoff:
            continue
        status_url = f"https://x.com/{username}/status/{tweet_id}"
        item = {
            "id": f"x-public-{tweet_id}-{created_ms}",
            "source_type": "musk_direct_public_web",
            "source_id": "x-public-elonmusk",
            "source_label": f"X public profile @{username}",
            "publisher": f"@{username}",
            "title": text.split("\n", 1)[0][:120],
            "url": status_url,
            "published_at": created_at.isoformat(),
            "summary": text,
            "capture_method": "best_effort_public_profile_html",
            "captured_at": now_taipei().isoformat(),
        }
        existing = by_tweet_id.get(tweet_id)
        if existing is None or len(item["summary"]) > len(existing.get("summary", "")):
            by_tweet_id[tweet_id] = item

    items = sorted(by_tweet_id.values(), key=lambda item: item.get("published_at", ""), reverse=True)
    if not items:
        return [], [f"x_public: no recent public posts parsed from {url}"]
    return items, []


def append_jsonl(path: Path, items: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False, sort_keys=True))
            f.write("\n")


def markdown_escape(value: str | None) -> str:
    if not value:
        return ""
    return value.replace("\n", " ").strip()


def hot_score(item: dict) -> int:
    source_type = item.get("source_type", "")
    publisher = (item.get("publisher") or "").lower()
    title = (item.get("title") or "").lower()
    score = 0
    if source_type == "musk_direct":
        score += 100
    if source_type == "musk_direct_public_web":
        score += 90
    if source_type == "company_primary":
        score += 80
    if source_type == "news_report":
        score += 30
    if source_type == "news_commentary":
        score += 15
    priority_publishers = (
        "ap",
        "associated press",
        "reuters",
        "bloomberg",
        "cnbc",
        "the guardian",
        "the verge",
        "wired",
        "financial times",
        "wall street journal",
        "new york times",
        "washington post",
        "techcrunch",
    )
    if any(name in publisher for name in priority_publishers):
        score += 20
    topic_markers = (
        "xai",
        "grok",
        "tesla",
        "spacex",
        "starlink",
        "neuralink",
        "autopilot",
        "fsd",
        "ai",
        "trillion",
        "ipo",
    )
    score += sum(3 for marker in topic_markers if marker in title)
    return score


def write_daily_digest(path: Path, date_key: str, items: list[dict], errors: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    by_type: dict[str, list[dict]] = {}
    for item in items:
        by_type.setdefault(item.get("source_type", "unknown"), []).append(item)

    lines = [
        f"# Elon Musk live daily digest {date_key}",
        "",
        f"更新時間：{now_taipei().strftime('%Y-%m-%d %H:%M %Z')}",
        "",
        "## 摘要",
        "",
        f"- 新增項目：{len(items)}",
        f"- 來源類型：{', '.join(sorted(by_type)) if by_type else '無新增'}",
        f"- 錯誤或略過：{len(errors)}",
        "",
    ]

    hot_items = sorted(items, key=hot_score, reverse=True)[:10]
    lines.extend(["## 熱門候選", ""])
    if hot_items:
        for item in hot_items:
            title = markdown_escape(item.get("title")) or "(no title)"
            url = item.get("url") or ""
            publisher = markdown_escape(item.get("publisher"))
            source_type = item.get("source_type", "")
            score = hot_score(item)
            if url:
                lines.append(f"- [{title}]({url})")
            else:
                lines.append(f"- {title}")
            lines.append(f"  分數：{score}；來源類型：{source_type}；來源：{publisher or item.get('source_label', '')}")
        lines.append("")
    else:
        lines.extend(["- 無新增熱門候選", ""])

    for source_type in sorted(by_type):
        lines.append(f"## {source_type}")
        lines.append("")
        for item in by_type[source_type]:
            title = markdown_escape(item.get("title")) or "(no title)"
            url = item.get("url") or ""
            publisher = markdown_escape(item.get("publisher"))
            published = item.get("published_at") or ""
            summary = markdown_escape(item.get("summary"))
            if url:
                lines.append(f"- [{title}]({url})")
            else:
                lines.append(f"- {title}")
            lines.append(f"  來源：{publisher or item.get('source_label', '')}；時間：{published}")
            if summary and summary != title:
                lines.append(f"  摘要：{summary[:300]}")
        lines.append("")

    lines.extend(
        [
            "## 錯誤或略過",
            "",
        ]
    )
    if errors:
        lines.extend(f"- {error}" for error in errors)
    else:
        lines.append("- 無")

    lines.extend(
        [
            "",
            "## 正式技能包更新判斷",
            "",
            "本日資料先進 daily digest。若要改 `SKILL.md`，請依 `references/promotion-gate.md` 審查。",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Update elon-musk-live public source data.")
    parser.add_argument("--skill-root", default=str(DEFAULT_SKILL_ROOT), help="Path to elon-musk-live skill root.")
    parser.add_argument("--date", default=now_taipei().strftime("%Y-%m-%d"), help="Date key for output files.")
    parser.add_argument("--max-new", type=int, default=40, help="Maximum new items to write in one run.")
    args = parser.parse_args()

    skill_root = Path(args.skill_root).expanduser().resolve()
    live_root = skill_root / "references" / "live-data"
    config_path = skill_root / "references" / "source-config.json"
    seen_path = live_root / "state" / "seen-ids.json"
    last_run_path = live_root / "state" / "last-run.json"
    raw_path = live_root / "raw" / f"{args.date}.jsonl"
    digest_path = live_root / "daily" / f"{args.date} daily-digest.md"
    log_path = live_root / "logs" / f"{args.date}.log"

    config = read_json(config_path, {})
    seen = set(read_json(seen_path, []))
    errors: list[str] = []
    collected: list[dict] = []

    x_config = config.get("x", {})
    x_public_items, x_public_errors = fetch_x_public_profile(x_config)
    collected.extend(x_public_items)
    errors.extend(x_public_errors)

    x_items, x_errors = fetch_x_posts(x_config)
    collected.extend(x_items)
    errors.extend(x_errors)

    for feed in config.get("rss_feeds", []):
        feed_items, feed_errors = fetch_rss(feed)
        collected.extend(feed_items)
        errors.extend(feed_errors)

    new_items: list[dict] = []
    for item in collected:
        item_id = item.get("id")
        if not item_id or item_id in seen:
            continue
        new_items.append(item)
        seen.add(item_id)
        if len(new_items) >= args.max_new:
            break

    append_jsonl(raw_path, new_items)
    write_daily_digest(digest_path, args.date, new_items, errors)
    write_json(seen_path, sorted(seen)[-5000:])
    write_json(
        last_run_path,
        {
            "ran_at": now_taipei().isoformat(),
            "date": args.date,
            "new_items": len(new_items),
            "errors": errors,
            "raw_path": str(raw_path),
            "digest_path": str(digest_path),
        },
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        f"ran_at={now_taipei().isoformat()}\nnew_items={len(new_items)}\nerrors={json.dumps(errors, ensure_ascii=False)}\n",
        encoding="utf-8",
    )

    print(f"new_items={len(new_items)}")
    print(f"digest={digest_path}")
    if errors:
        print(f"errors={len(errors)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
