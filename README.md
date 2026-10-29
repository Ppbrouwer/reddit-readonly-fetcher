# reddit-readonly-fetcher

A small, personal, **read-only** script that counts how often stock tickers are
mentioned in public posts on a few finance subreddits (r/wallstreetbets,
r/stocks, r/investing, r/options), for off-platform research on retail attention.

## What it does
- Authenticates with application-only OAuth (client ID + secret, no user login) and sets PRAW to `read_only`.
- Fetches `/new` and `/hot` listings (up to 100 posts each) per subreddit, about 8 listing requests per run.
- Runs about once each weekday evening, plus occasional checks: roughly 100–200 requests a day, well under Reddit's rate limits.
- Outputs aggregate ticker counts and one example post link per ticker.

## What it never does
- No posting, commenting, voting, messaging, or bot account.
- No storage of usernames or private data.
- No AI model training on Reddit content.

## Setup
```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export REDDIT_CLIENT_ID=...        # never commit these
export REDDIT_CLIENT_SECRET=...
export REDDIT_USER_AGENT="script:reddit-readonly-fetcher:v0.1 (by /u/Rocket_Pocket_6)"
python fetch_mentions.py            # all tickers
python fetch_mentions.py NVDA,TSLA  # only these
```

Credentials come from environment variables only and are never stored in this repo.
