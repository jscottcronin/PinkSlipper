from collections import defaultdict
import pymongo
import requests
from bs4 import BeautifulSoup
import numpy as np
import time


def get_soup(url):
    '''
    INPUT:  url as string from where to scrape
    OUTPUT: soup as BeautifulSoup Object for given url
    '''
    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel ' +
              'Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, ' +
              'like Gecko) Chrome/46.0.2490.71 Safari/537.36'}
    r = requests.get(url, headers=header)
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup


def in_database(article, database):
    '''
    INPUT:  article - article headline as string
            database - pymongo object connection to mongodb
    OUTPUT: Boolean if article is in database
    '''
    if database.find({'_id': article}).count() > 0:
        return True
    else:
        return False


def labelled_as_training(article, database):
    '''
    INPUT:  article - article headline as string
            database - pymongo object connection to mongodb
    OUTPUT: Boolean if article is labelled as training data in db
    '''
    training_page = 'http://www.prnewswire.com/news-releases/' + \
                    'general-business-latest-news/personnel-announcements-list/' + \
                    '?page=1&pagesize=1'
    if database.find({'_id': article}, {'source': training_page}).count() > 0:
        return True
    else:
        return False


def is_training(url):
    '''
    INPUT:  url as string
    OUTPUT: Boolean if url points to training data page
    '''
    training_page = 'http://www.prnewswire.com/news-releases/' + \
                    'general-business-latest-news/personnel-announcements-list/' + \
                    '?page=1&pagesize=1'
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
    for article in soup.find_all(class_='list-links'):
        title = article.li.a['title']
        print title
        if not in_database(title, coll):
            randomize_time()
            print 'adding to db'
            print '---------------------'
            link = article.li.a['href']
            article_data = {'_id': title,
                            'link': link,
                            'source': url.rsplit('/', 2)[1],
                            'page_soup': soup.prettify(),
                            'body_soup': get_soup(link).prettify()}
            coll.insert_one(article_data)
        else:
            print 'already in db'
            print '---------------------'


def randomize_time():
    '''
    INPUT:  None
    OUTPUT: None; this function delays scraping by distribution of time
    '''
    x = np.abs(np.random.normal(0, 1))
    time.sleep(x)


def main():
    cli = pymongo.MongoClient()
    db = cli.pr
    coll = db.prnewswire

    urlbase = 'http://www.prnewswire.com'
    url = 'http://www.prnewswire.com/news-releases/' + \
          'english-releases/?page=1&pagesize=2000'
    url_training = 'http://www.prnewswire.com/news-releases/' + \
                   'general-business-latest-news/personnel-announcements-list/' + \
                   '?page=1&pagesize=2000'
    print 'starting w training'
    get_all_news(coll, url_training, urlbase)
    print 'ended w training'
    get_all_news(coll, url, urlbase)
    cli.close()


if __name__ == '__main__':
    main()
