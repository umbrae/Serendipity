
/r/serendipity is a meta-subreddit meant to broaden the perspective of 
its subscribers. It takes a popular entry from a random subreddit and 
posts it every few hours. If you want to increase your exposure to niche 
subreddits, or just your perspective on things on the web in general, 
serendipity might help you do that. But it might not. It's a bot, after 
all.

## To Run

Serendipity requires a few packages, like
[PRAW](http://pypi.python.org/pypi/praw). You'll want to install the
`requirements.pip` dependencies into a virtualenv.

`build_subreddits.py` requires `lxml` as well, if you want to update
subreddits, which is not listed in requirements as it's a pain and
most people probably won't need it.

You'll likely want to stick these scripts in your cron, something to
the effect of:

```
0 */3 * * * python /path/to/serendipity/main.py # Post a serendipity link every 3 hours
0 0 1 */3 * python /path/to/serendipity/scripts/build_subreddits.py # Rebuild subreddits list every 3 months
```
