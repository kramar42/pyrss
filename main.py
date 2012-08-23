
import feedparser
from urllib import urlretrieve


def main():
    get_rss('http://rss.cnn.com/rss/cnn_latest.rss')


def get_rss(rss):
    rss_name = rss.split('/')[-1]
    urlretrieve(rss, rss_name)

    feed = feedparser.parse(rss_name)
    print 'RSS Feed:', feed.feed.title
    print

    for entry in feed.entries:
        print entry.title, ':'
        print '\t', entry.link


if __name__ == '__main__':
    main()
