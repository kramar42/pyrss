
import feedparser


def main():
    url = 'http://habrahabr.ru/rss'
    feed = feedparser.parse(url)

    for entry in feed.entries:
        print entry.description

    #    print feed.feed.title
    #    for article in feed.entries:
    #        print article.title
        #print article.link.split('/')[-2]


if __name__ == '__main__':
    main()
