from subreddits import subreddits
import random
import reddit
import re
import time

try:
    import settings
except:
    exit("Unable to pull settings from settings.py.\n" + 
         "Make sure you create this file as a copy of settings.template.py.")

# Pull all of the subreddits from subreddits.py that fit our criteria.
serendipitous_subreddits = [s for s in subreddits if s['subscribers'] > settings.MINIMUM_SUBSCRIBER_COUNT]
# for subreddit in subreddits:
#     if subreddit['subscribers'] > settings.MINIMUM_SUBSCRIBER_COUNT:
#         serendipitous_subreddits.append(subreddit)

# Pick out the random subreddit to pull a link form    
subreddit      = random.choice(serendipitous_subreddits)
subreddit_slug = re.sub(r'http://www\.reddit\.com/r/([^/]+)/', r'\1', subreddit['uri'])

# Get the top stories from that subreddit, and pick a random one
r = reddit.Reddit()
r.login(settings.REDDIT_LOGIN, settings.REDDIT_PASSWORD)
stories = r.get_subreddit(subreddit_slug).get_hot(limit=settings.HOT_STORY_COUNT)
story   = random.choice(stories)

# Build our submission
submission = reddit.Submission({
    "title": "%s [X-Post From /r/%s]" % (story.title, subreddit_slug),
    "url": story.url
}, r)
submission.subreddit = r.get_subreddit(settings.SUBREDDIT_NAME)

# Send it off to reddit
response = submission.submit();

# Sleep for a while so that we can let the submission go through before we add
# our comment.
time.sleep(3)

comment_text = (
    ("[Original Submission by %(author)s](%(permalink)s) into " + 
    "[/r/%(subreddit_slug)s](http://www.reddit.com/r/%(subreddit_slug)s)") %
    {
        "author": story.author,
        "permalink": story.permalink,
        "subreddit_slug": subreddit_slug
    }
)

submission.comment(comment_text)
