from __future__ import division
from datetime import datetime
from collections import Counter
from operator import attrgetter
import flesch_kincaid
import praw

try:
    import settings
except:
    exit("Unable to pull settings from settings.py.\n" +
         "Make sure you create this file as a copy of settings.template.py.")

def avg(l):
    """ Return the average of a list. Uses future division. """
    return sum(l) / len(l)

def _add_first_unique(top, story_type, stories):
    """ Given a dict top, and a key story_type, find a story in stories that
        does not already exist in top and add it at the position k. Alters
        top in-place. Raises ValueError if all stories in `stories` are
        already within `top`.
    """
    for story in stories:
        if story.id in [s.id for s in top.values()]:
            continue
        top[story_type] = story
        return
    raise ValueError("All stories already exist in top_list")

class SubredditStats(object):
    LINKS_LIMIT = 200
    COMMENTS_LIMIT = 200

    def __init__(self, slug, r=None):
        self.slug = slug
        if not r:
            r = praw.Reddit(user_agent=settings.UA)
            r.login(settings.REDDIT_LOGIN, settings.REDDIT_PASSWORD)
        self.r = r
        self.sr = self.r.get_subreddit(self.slug)
        self._cached_hot = None
        self._cached_comments = None
        self._domain_counter = None

    @property
    def cached_hot(self):
        """ Get the top N hot links for stats purposes. Cache it, because we'll
            be iterating over it quite a few times.
        """
        if self._cached_hot is None:
            self._cached_hot = list(self.sr.get_hot(limit=self.LINKS_LIMIT))
        return self._cached_hot

    @property
    def cached_comments(self):
        """ Get the most recent N comments for stats purposes. Cache it,
            because we'll be iterating over it quite a few times.
        """
        if self._cached_comments is None:
            self._cached_comments = list(self.sr.get_comments(limit=self.COMMENTS_LIMIT))
        return self._cached_comments

    @property
    def domain_counter(self):
        if self._domain_counter is None:
            domains = Counter()
            for link in self.cached_hot:
                d = 'imgur.com' if link.domain == 'i.imgur.com' else link.domain
                domains[d] += 1
            self._domain_counter = domains
        return self._domain_counter

    def get_overview(self):
        mods = [u.name for u in self.sr.get_moderators()]

        return {
            "subscribers": self.sr.subscribers,
            "create_date": datetime.fromtimestamp(self.sr.created),
            "mods": mods
        }

    def get_domain_breakdown(self, num=10):
        total_count = sum(self.domain_counter.values())
        breakdown = []
        for domain, count in self.domain_counter.most_common(num):
            breakdown.append((domain, count/total_count))
        return breakdown

    def get_avg_ratio(self):
        return avg([l.ups / (l.ups + l.downs) for l in self.cached_hot])

    def get_avg_score(self):
        return avg([l.score for l in self.cached_hot])

    def get_avg_over_18(self):
        return avg([1 if l.over_18 else 0 for l in self.cached_hot])

    def get_avg_num_comments(self):
        return avg([l.num_comments for l in self.cached_hot])

    def get_avg_comment_length(self):
        return avg([len(c.body.split()) for c in self.cached_comments])

    def get_avg_reading_level(self):
        reading_levels = []
        for c in self.cached_comments:
            if not c.body:
                continue
            try:
                reading_level = flesch_kincaid.grade_level(c.body)
                reading_levels.append(reading_level)
            except:
                continue

        if len(reading_levels) == 0:
            return 0
        
        return avg(reading_levels)

    def get_top_links(self):
        top = {}
        _add_first_unique(top, 'all_time', self.sr.get_top_from_all(limit=1))
        _add_first_unique(top, 'month', self.sr.get_top_from_month(limit=2))
        _add_first_unique(top, 'week', self.sr.get_top_from_week(limit=3))

        return top
