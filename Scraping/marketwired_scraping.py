from collections import defaultdict
import pymongo
import requests
from bs4 import BeautifulSoup
import numpy as np
import time


def get_pagemax(url):
    '''
    INPUT:  url - page from which article links are scraped
    OUTPUT: pagemax - total number of pages of articles
    '''
    soup = get_soup(url)
    page = soup.find(class_='PagerStatus')
    pagemax = int(page.text.split()[-1]) // 10 + 2
    return pagemax


def get_soup(url):
    '''
    INPUT:  url as a string
    OUTPUT: beautiful soup object
    '''
    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel ' +
              'Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, ' +
              'like Gecko) Chrome/46.0.2490.71 Safari/537.36'}
    r = requests.get(url, headers=header)
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup


def in_database(article, database):
    '''
    INPUT:  article - article title/headline as unicode string
            database - pymongo connection to db collection
    OUTPUT: Boolean specifying if article is in database
    '''
    if database.find({'_id': article}).count() > 0:
        return True
    else:
        return False


def labelled_as_training(article, database):
    '''
    INPUT:  article - article title/headline as unicode string
            database - pymongo connection to db collection
    OUTPUT: Boolean specifying if article has been labelled in database
    '''
    training_page = 'http://www.marketwired.com/refine-by?topic=MAC'
    if database.find({'_id': article}, {'source': training_page}).count() > 0:
        return True
    else:
        return False


def is_training(url):
    '''
    INPUT:  url as string
    OUTPUT: Boolean specifying if url is from training source or news source
    '''
    training_page = 'http://www.marketwired.com/refine-by?topic=MAC'
    if url == training_page:
        return True
    else:
        return False


def get_all_news(coll, url, urlbase):
    '''
    INPUT:  coll - pymongo object connection to db collection
            url - website as string to be scraped
            urlbase - website as string; used by concatenating with link
    OUTPUT: None - articles are saved to mongo db
    '''
    soup = get_soup(url)
    for article in soup.findAll(class_='news-item-news-room'):
        p = article.find(class_='news-story-news-room').findAll('p')
        if not in_database(p[0].text, coll):
            link = urlbase + p[0].find('a')['href']
            article_data = {'_id': p[0].text,
                            'link': link,
                            'source': url,
                            'page_soup': soup.prettify(),
                            'body_soup': get_soup(link).prettify()}
            coll.insert_one(article_data)
        elif is_training(url) and not labelled_as_training(p[0].text, coll):
            print 'is training, but not labelled as so --> Update'
            coll.update_one({'_id': p[0].text}, {'$set': {'source': url}})
        else:
            print 'is in db but either not training, or is properly labelled'
            print p[0].text


def randomize_time():
    '''
    INPUT:  None
    OUTPUT: None; this function delays scraping by distribution of time
    '''
    x = np.abs(np.random.normal(0, .1))
    time.sleep(x)


def main():
    '''
    INPUT:  None
    OUTPUT: None
    '''
    cli = pymongo.MongoClient()
    db = cli.pr
    coll = db.marketwired
    urlbase = 'http://www.marketwired.com'
    url = 'http://www.marketwired.com/news_room'
    print 'getting training news'
    get_all_news(coll, 'http://www.marketwired.com/' +
                 'refine-by?topic=MAC', urlbase)
    print 'getting all news'
    for page in xrange(1, get_pagemax(url)):
        print 'page: %i' %page
        randomize_time()
        pageurl = url + '?page=' + str(page)
        get_all_news(coll, pageurl, urlbase)
    cli.close()


if __name__ == '__main__':
    main()
