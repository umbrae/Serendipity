# -*- coding: utf-8 -*- 
from subreddits import subreddits
import ago
import random
import praw
from datetime import datetime
from stats import SubredditStats

try:
    import settings
except:
    exit("Unable to pull settings from settings.py.\n" +
         "Make sure you create this file as a copy of settings.template.py.")

def link_display(s):
    return "[%s (%d points by /u/%s)](%s)" % (s.title, s.score, s.author.name,
                                              s.permalink)

def domain_display(d):
    return "%s **(%0.f%%)**" % (d[0], d[1]*100.0)

def summary_comment_text(story, subreddit, r):
    subreddit_slug = subreddit['uri'].strip('/').split('/')[-1]
    stats = SubredditStats(subreddit_slug, r)
    overview = stats.get_overview()
    domain_breakdown = stats.get_domain_breakdown(3)
    top_links = stats.get_top_links()

    summary_tpl = """
**[Original Submission by /u/{story_author}]({story_permalink})** into /r/{domain}

---

# Subreddit Overview
* A community for: **{age}**
* # of subscribers: **{subscribers:,}**
* # of mods: **{num_mods:,}**
* Subscribers per mod: **{subscribers_per_mod:,}**

# Popular Posts Summary
* Top domains: {top_domains}
* Average ups/downs ratio: **{avg_ratio:0.2%}**
* % NSFW: **{avg_over_18:0.0%}**
* Average Score: **{avg_karma:0.0f}**

# Discussion Summary
* Average Comment Length: **~{avg_comment_length:0.0f}** words per comment
* Flesch-Kincaid Reading Level: **{avg_reading_level:0.0f}**
* Comments per post: **~{avg_num_comments:0.0f}**

# A sampling of top posts:
* Top all time: {all_time_top_display}
* Top this month: {month_top_display}
* Top this week: {week_top_display}

## **[Subscribe at /r/{domain}](/r/{domain})**   
    """

    summary = summary_tpl.format(
        story_author = story.author,
        story_permalink = story.permalink,
        domain = subreddit_slug,
        age = ago.human(overview['create_date'], precision=1, past_tense='{}'),
        subscribers = overview['subscribers'],
        num_mods = len(overview['mods']),
        subscribers_per_mod = overview['subscribers'] / len(overview['mods']),
        top_domains = ', '.join([domain_display(d) for d in domain_breakdown]),
        avg_ratio = stats.get_avg_ratio(),
        avg_over_18 = stats.get_avg_over_18(),
        avg_karma = stats.get_avg_score(),
        avg_num_comments = stats.get_avg_num_comments(),
        all_time_top_display = link_display(top_links['all_time']),
        month_top_display = link_display(top_links['month']),
        week_top_display = link_display(top_links['week']),
        avg_comment_length = stats.get_avg_comment_length(),
        avg_reading_level = stats.get_avg_reading_level()
    )

    return summary

def generate_serendipitous_subreddits(subreddits):
    """ Pull all of the subreddits from subreddits.py that fit our criteria.
        TODO: Just build this on build_subreddits.
    """
    serendipitous_subreddits = []
    for subreddit in subreddits:
        slug = subreddit['uri'].strip('/').split('/')[-1].lower()
        if (subreddit['subscribers'] > settings.MINIMUM_SUBSCRIBER_COUNT and
            slug not in settings.BLACKLISTED_SUBREDDITS):
                serendipitous_subreddits.append(subreddit)
    return serendipitous_subreddits

def pick_submission(subreddits, r):
    subreddit = None
    story = None
    while story is None:
        # Pick out the random subreddit to pull a link form
        subreddit = random.choice(subreddits)
        subreddit_slug = subreddit['uri'].strip('/').split('/')[-1]
        
        # Get the top stories from that subreddit, and pick a random one
        stories = list(r.get_subreddit(subreddit_slug)
                        .get_hot(limit=settings.HOT_STORY_COUNT))
        story = random.choice(stories)

        # Ignore stories from bots, or that are older than 30 days.
        submission_date = datetime.utcfromtimestamp(story.created_utc)
        submission_age = datetime.utcnow() - submission_date
        if (story.author.name.lower().endswith('bot') or
            submission_age.days > 30):
            story = None
            continue        
    
    return (subreddit, story)

def get_feature_comment_text(submission):
    return ("This submission has been randomly featured in /r/serendipity, a "
            "bot-driven subreddit discovery engine. More here: %s" %
            submission.permalink)

def main():
    r = praw.Reddit(user_agent=settings.UA)
    r.login(settings.REDDIT_LOGIN, settings.REDDIT_PASSWORD)
    r.config.decode_html_entities = True

    serendipitous_subreddits = generate_serendipitous_subreddits(subreddits)

    subreddit, story = pick_submission(serendipitous_subreddits, r)
    subreddit_slug = subreddit['uri'].strip('/').split('/')[-1]

    # Submit our crosspost
    submission = r.submit(settings.SUBREDDIT_NAME,
                         "%s [X-Post From /r/%s]" % (story.title, subreddit_slug),
                         url=story.url)

    # If it was a NSFW submission, mark the crosspost also
    if story.over_18:
        submission.mark_as_nsfw()

    comment_text = summary_comment_text(story, subreddit, r)

    # Submit our comment onto our own submission
    submission.add_comment(comment_text)

    feature_comment_text = get_feature_comment_text(submission)
    story.add_comment(feature_comment_text)


if __name__ == "__main__":
    main()
