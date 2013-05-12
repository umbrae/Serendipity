from subreddits import subreddits
import random
import time
import praw
from datetime import datetime, timedelta

try:
    import settings
except:
    exit("Unable to pull settings from settings.py.\n" +
         "Make sure you create this file as a copy of settings.template.py.")

r = praw.Reddit(user_agent='Serendipity %s' % settings.VERSION)
r.login(settings.REDDIT_LOGIN, settings.REDDIT_PASSWORD)

# Pull all of the subreddits from subreddits.py that fit our criteria.
serendipitous_subreddits = []
for subreddit in subreddits:
    slug = subreddit['uri'].strip('/').split('/')[-1].lower()
    if (subreddit['subscribers'] > settings.MINIMUM_SUBSCRIBER_COUNT and
        slug not in settings.DEFAULT_SUBREDDITS):
            serendipitous_subreddits.append(subreddit)

story = None
while story is None:
    # Pick out the random subreddit to pull a link form
    subreddit = random.choice(serendipitous_subreddits)
    subreddit_slug = subreddit['uri'].strip('/').split('/')[-1]
    
    # Get the top stories from that subreddit, and pick a random one
    stories = list(r.get_subreddit(subreddit_slug)
                    .get_hot(limit=settings.HOT_STORY_COUNT))
    story = random.choice(stories)

    # Ignore stories from bots, or that are older than 30 days.
    submission_date = datetime.utcfromtimestamp(story.created_utc)
    submission_age = datetime.utcnow() - submission_date
    if story.author.name.lower().endswith('bot') or submission_age.days > 30:
        story = None
        continue        

# Submit our crosspost
submission = r.submit(settings.SUBREDDIT_NAME,
                     "%s [X-Post From /r/%s]" % (story.title, subreddit_slug),
                     url=story.url)

# If it was a NSFW submission, mark the crosspost also
if story.over_18:
    submission.mark_as_nsfw()

# Submit our comment onto our own submission
submission.add_comment("[Original Submission by %s](%s) into /r/%s" %
                       (story.author, story.permalink, subreddit_slug))

feature_comment_text = ("This submission has been randomly featured in "
                        "/r/serendipity, a bot-driven subreddit discovery "
                        "engine. More here: %s" % submission.permalink)
story.add_comment(feature_comment_text)
