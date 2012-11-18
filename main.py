from subreddits import subreddits
import random
import re
import time
import praw

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
    if subreddit['subscribers'] > settings.MINIMUM_SUBSCRIBER_COUNT:
        serendipitous_subreddits.append(subreddit)

# Pick out the random subreddit to pull a link form
subreddit = random.choice(serendipitous_subreddits)
subreddit_slug = re.sub(r'http://www\.reddit\.com/r/([^/]+)/', r'\1',
                        subreddit['uri'])

# Get the top stories from that subreddit, and pick a random one
stories = list(r.get_subreddit(subreddit_slug)
                .get_hot(limit=settings.HOT_STORY_COUNT))
story = random.choice(stories)

# Submit our crosspost
submission = r.submit(settings.SUBREDDIT_NAME,
                     "%s [X-Post From /r/%s]" % (story.title, subreddit_slug),
                     url=story.url)

# Sleep for a while so that we can let the submission go through before we add
# our comment.
time.sleep(3)

# Submit our comment onto our own submission
submission.add_comment("[Original Submission by %s](%s) into /r/%s" %
                       story.author, story.permalink, subreddit_slug)
