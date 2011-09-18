#!/usr/bin/env python
# Requires lxml 2.0.3 and httplib2.  Public domain.

# Derived from subreddit scraper here: http://pastie.org/pastes/804537

first_uri = 'http://www.reddit.com/reddits/'

import httplib2
import urlparse
import lxml.html.soupparser
import json

def get_page(uri):
    print 'Processing %s' % uri
    http = httplib2.Http()
    response, content = http.request(uri)
    return lxml.html.soupparser.fromstring(content)

def fetch_reddits():
    reddit_list = []
    current_uri = first_uri
    while True:
        page = get_page(current_uri)
        reddits = page.xpath('//div[contains(@class, \'subreddit\')]')
        for reddit in reddits:
            info = reddit.xpath('descendant::a[@class=\'title\']')[0]
            name = info.text or info.attrib['href']
            uri = urlparse.urljoin(current_uri, info.attrib['href'])
            try:
                description = reddit.xpath('descendant::p[@class=\'description\']/text()')[0]
            except:
                description = None
            try:
                subscribers = reddit.xpath('.//span[@class=\'score unvoted\']/span[@class=\'number\']/text()')[0].split()[0].replace(',','')
            except IndexError:
                subscribers = -1
            is_nsfw = bool(len(reddit.xpath('.//img[@title=\'over18\']')) > 0)
            reddit_list.append(
                {
                    "name": name,
                    "uri": uri,
                    "description": description,
                    "subscribers": int(subscribers),
                    "is_nsfw": is_nsfw
                }
            )
        try:
            print "Processed %s reddits." % len(reddit_list)
            next_link = page.xpath('//p[@class=\'nextprev\']/a[contains(text(),\'next\')]')[0]
            current_uri = urlparse.urljoin(current_uri, next_link.attrib['href'])
        except:
            break
        break
    return reddit_list

if __name__ == '__main__':
    reddits = fetch_reddits()
    reddits.sort(key=lambda reddit: reddit["subscribers"])
    reddits.reverse()

    print json.dumps(reddits)