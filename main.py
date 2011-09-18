from subreddits import subreddits
import random
import reddit
import re
import time

try:
    from settings import REDDIT_LOGIN, REDDIT_PASSWORD
except:
    print "Unable to pull settings from settings.py - make sure you create this file with two constances, REDDIT_LOGIN and REDDIT_PASSWORD."
    return

serendipitous_subreddits = []
for subreddit in subreddits:
    if subreddit['subscribers'] > 1000:
        serendipitous_subreddits.append(subreddit)
        
subreddit = random.choice(serendipitous_subreddits)

subreddit_slug = re.sub(r'http://www\.reddit\.com/r/([^/]+)/', r'\1', subreddit['uri'])


r = reddit.Reddit()
r.login(REDDIT_LOGIN,REDDIT_PASSWORD)
stories = r.get_subreddit(subreddit_slug).get_hot(limit=5)

story = random.choice(stories)

print(subreddit)
print(story)

print(story.__dict__)

submission = reddit.Submission({
        "title": "%s [X-Post From /r/%s]" % (story.__dict__['title'], subreddit_slug),
        "url": story.__dict__['url']
    }, r)

submission.subreddit = r.get_subreddit('serendipity')

print(submission.__dict__)

response = submission.submit();
print(response)

print(submission.__dict__)

comment_text = "[Original Submission by %s](%s) into [/r/%s](http://www.reddit.com/r/%s)" % (story.__dict__['author'], story.__dict__['permalink'], subreddit_slug, subreddit_slug)

print("sleeping")
time.sleep(3)
print("done sleeping")

print(submission.comment(comment_text))
