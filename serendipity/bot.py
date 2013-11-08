# -*- coding: utf-8 -*- 
from __future__ import unicode_literals
from .subreddits import subreddits
from .stats import SubredditStats
import ago
import random
import praw
from datetime import datetime

try:
    import settings
except:
    exit("Unable to pull settings from settings.py.\n" +
         "Make sure you create this file as a copy of settings.template.py.")

def link_display(s):
    """ Given a story, format it nicely with markdown """
    author_name = s.author.name if s.author else "Unknown"
    return "[%s (%d points by /u/%s)](%s)" % (s.title, s.score, author_name,
                                              s.permalink)

def domain_display(d):
    """ Given a domain from `get_domain_breakdown`, format with markdown """
    return "%s **(%0.f%%)**" % (d["domain"], d["percent"]*100.0)

class SerendipityException(Exception):
    pass

class SerendipityBot(object):
    def __init__(self, dry_run=False, verbose=False, force_subreddit=False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.force_subreddit = force_subreddit
        self.slug = None
        self.chosen_subreddit = None
        self.chosen_story = None
        self.story = None
        self.summary = None
        self.stats = None

        self._setup_praw()

    def _dbg(self, s):
        """ Print this string if verbose mode is enabled. """
        if self.verbose:
            print(s)

    def _setup_praw(self):
        """ Set up our praw client. Uses settings file for credentials. """
        self.r = praw.Reddit(user_agent=settings.UA)
        self.r.login(settings.REDDIT_LOGIN, settings.REDDIT_PASSWORD)
        self.r.config.decode_html_entities = True

    def _choose_subreddit(self):
        """ Choose a random subreddit out of our subreddits list.

        If `force_subreddit` was specified, use that instead.
        """
        if self.force_subreddit is not None:
            self.slug = self.force_subreddit
        else:
            subreddit = random.choice(subreddits)
            self.slug = subreddit['uri'].strip('/').split('/')[-1]

        self.chosen_subreddit = self.r.get_subreddit(self.slug)
        self.stats = SubredditStats(self.slug, self.r)
 
    def _choose_story(self):
        """ Choose the story to highlight from the chosen subreddit.

        A chosen story must be < 30 days old and we do a little checking to make
        sure we're not featuring a bot.
        """
        if not self.chosen_subreddit:
            self._choose_subreddit()

        stories = list(self.chosen_subreddit
                           .get_hot(limit=settings.HOT_STORY_COUNT))
        while len(stories) > 0:
            story = random.choice(stories)

            # Ignore stories from bots, or that are older than 30 days.
            story_date = datetime.utcfromtimestamp(story.created_utc)
            story_age = datetime.utcnow() - story_date
            is_bot = story.author.name.lower().endswith('bot')

            if is_bot or story_age.days > 30:
                self._dbg("Following story is ineligible, skipping: “%s”" %
                          link_display(story))
                stories.remove(story)
                continue
            else:
                self.chosen_story = story
                return

        if self.force_subreddit:
            raise SerendipityException("No worthy stories found in forced sub "
                                       "/r/%s." % self.slug)

        self._dbg("Exhausted all top stories in /r/%s, choosing new " 
                  "subreddit." % self.slug)
        self._choose_subreddit()
        return self._choose_story()

    def _generate_summary(self):
        """ The subreddit summary is posted as a comment to the crosspost.

        Makes use of stats to do most of the heavy lifting, just reads the
        template and formats for the most part.
        """
        self._dbg("Generating summary for crosspost “%s” in /r/%s" %
                  (self.chosen_story.title, self.slug))

        overview = self.stats.get_overview()
        top_links = self.stats.get_top_links()
        domain_breakdown = self.stats.get_domain_breakdown(3)
        top_domains = ', '.join([domain_display(d) for d in domain_breakdown])
        age = ago.human(overview['create_date'], precision=1, past_tense='{}')
        subscribers_per_mod = overview['subscribers'] / len(overview['mods'])

        with open("templates/summary.tpl") as f:
            summary_tpl = f.read()
            summary = summary_tpl.format(
                story_author = self.chosen_story.author,
                story_permalink = self.chosen_story.permalink,
                domain = self.slug,
                age = age,
                subscribers = overview['subscribers'],
                num_mods = len(overview['mods']),
                subscribers_per_mod = subscribers_per_mod,
                top_domains = top_domains,
                avg_ratio = self.stats.get_avg_ratio(),
                avg_over_18 = self.stats.get_avg_over_18(),
                avg_karma = self.stats.get_avg_score(),
                avg_num_comments = self.stats.get_avg_num_comments(),
                all_time_top_display = link_display(top_links['all_time']),
                month_top_display = link_display(top_links['month']),
                week_top_display = link_display(top_links['week']),
                avg_comment_length = self.stats.get_avg_comment_length(),
                avg_reading_level = self.stats.get_avg_reading_level()
            )

            self._dbg("Summary:\n%s" % summary)
            self.summary = summary

    def _submit_post(self):
        self._dbg("Submitting serendipity post.")

        title = "%s [X-Post From /r/%s]" % (self.chosen_story.title,
                                            self.slug)
        self.story = self.r.submit(settings.SUBREDDIT_NAME, title,
                                   url=self.chosen_story.url)

        # If it was a NSFW submission, mark the crosspost also
        if self.chosen_story.over_18:
            self.story.mark_as_nsfw()

    def _submit_summary(self):
        self._dbg("Submitting subreddit summary.")

        if not self.summary:
            self._generate_summary()

        self.story.add_comment(self.summary)

    def _submit_cross_comment(self):
        self._dbg("Submitting cross comment.")

        feature_text = ("This submission has been randomly featured in "
                        "/r/serendipity, a bot-driven subreddit discovery "
                        "engine. More here: %s" % self.story.permalink)

        self.chosen_story.add_comment(feature_text)

    def run(self):
        self._choose_subreddit()
        self._choose_story()

        # Generate summary before submitting story so that if summary generation
        # fails we don't submit the post. Also useful for dry runs.
        self._generate_summary()

        if self.dry_run:
            print "Dry run, skipping submission"
        else:
            self._submit_post()
            self._submit_summary()
            self._submit_cross_comment()
