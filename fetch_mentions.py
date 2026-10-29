"""Read-only Reddit ticker-mention counter.

Reads public posts from a few finance subreddits with application-only OAuth
(no user login) and counts ticker mentions. Never posts, comments, votes or
messages. Stores only aggregate counts and a few example post links.
"""
import collections
import datetime as dt
import json
import os
import re
import sys

import praw  # PRAW in read-only mode

SUBREDDITS = ["wallstreetbets", "stocks", "investing", "options"]
LIMIT_PER_LISTING = 100  # /new and /hot per subreddit -> ~8 listing calls per run
TICKER_RE = re.compile(r"(?<![A-Za-z])\$?([A-Z]{2,5})(?![A-Za-z])")
STOPWORDS = {"THE", "AND", "FOR", "YOLO", "DD", "CEO", "IPO", "ETF", "USA", "EPS",
             "ATH", "IMO", "GDP", "FED", "CPI", "DTE", "OTM", "ITM", "WSB", "LOL"}


def reddit_client() -> praw.Reddit:
    r = praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        user_agent=os.environ.get(
            "REDDIT_USER_AGENT",
            "script:reddit-readonly-fetcher:v0.1 (by /u/Rocket_Pocket_6)",
        ),
    )
    r.read_only = True
    return r


def count_mentions(watch: set[str] | None = None) -> dict:
    r = reddit_client()
    counts: dict[str, collections.Counter] = {}
    examples: dict[str, str] = {}
    for sub in SUBREDDITS:
        c = collections.Counter()
        seen = set()
        sr = r.subreddit(sub)
        for listing in (sr.new(limit=LIMIT_PER_LISTING), sr.hot(limit=LIMIT_PER_LISTING)):
            for post in listing:
                if post.id in seen:
                    continue
                seen.add(post.id)
                text = f"{post.title} {post.selftext or ''}"
                found = {t for t in TICKER_RE.findall(text) if t not in STOPWORDS}
                if watch is not None:
                    found &= watch
                for t in found:
                    c[t] += 1
                    examples.setdefault(t, f"https://www.reddit.com{post.permalink}")
        counts[sub] = c
    total = collections.Counter()
    for c in counts.values():
        total.update(c)
    return {
        "fetched_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "subreddits": SUBREDDITS,
        "total": dict(total.most_common()),
        "by_subreddit": {s: dict(c.most_common()) for s, c in counts.items()},
        "example_post": examples,
    }


if __name__ == "__main__":
    watch = set(sys.argv[1].split(",")) if len(sys.argv) > 1 else None
    print(json.dumps(count_mentions(watch), indent=2))
