REDDIT_LOGIN = ''
REDDIT_PASSWORD = ''
CLIENT_ID = ''
CLIENT_SECRET = ''

SUBREDDIT_NAME = ''

# Only pull random links from a subreddit who has at least this many
# subscribers. Too low and the subreddits may not be of real value yet. Too
# high and they aren't niche enough.
MINIMUM_SUBSCRIBER_COUNT = 1000

# When Serendipity pulls a link, it will take a random one from the top N
# stories so that it's not just the absolute-top link getting exposure.
HOT_STORY_COUNT = 5

VERSION = '1.3'
UA = 'Serendipity %s' % VERSION

BLACKLISTED_SUBREDDITS = frozenset([
    # Defaults
    'adviceanimals',
    'AskReddit',
    'aww',
    'bestof',
    'books',
    'earthporn',
    'explainlikeimfive',
    'funny',
    'gaming',
    'gifs',
    'IAmA',
    'movies',
    'music',
    'news',
    'pics',
    'science',
    'technology',
    'television',
    'todayilearned',
    'videos',
    'worldnews',
    'wtf',

    # Mod Requests
    'abrathatfits',
    'transtimelines',
    'firstimpression',
    'gonenatural',
    'subredditdrama',
    'suicidewatch',
])
