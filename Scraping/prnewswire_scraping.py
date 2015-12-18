from collections import defaultdict
import pymongo
import requests
from bs4 import BeautifulSoup
import numpy as np
import time


def get_soup(url):
    '''
    PURPOSE:    return soup object for any url
    INPUT:      url (str) -  url of site to scrape
    OUTPUT:     soup (beautiful soup object) - soup for given url
    '''
    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel ' +
              'Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, ' +
              'like Gecko) Chrome/46.0.2490.71 Safari/537.36'}
    r = requests.get(url, headers=header)
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup


def in_database(article, database):
    '''
    PURPOSE:    check if article is in given database
    INPUT:      article (str) - article headline
                database (pymongo obj) - connection to mongodb
    OUTPUT:     boolean -  True if article is in database
    '''
    if database.find({'_id': article}).count() > 0:
        return True
    else:
        return False


def labelled_as_training(article, database):
    '''
    PURPOSE:    check if article is labelled for training models
                in database
    INPUT:      article (str) - article headline
                database (pymongo obj) - connection to mongodb
    OUTPUT:     boolean - True if article is labelled as training in db
    '''
    training_page = 'http://www.prnewswire.com/news-releases/' + \
                    'general-business-latest-news/' + \
                    '\personnel-announcements-list/?page=1&pagesize=1'
    if database.find({'_id': article}, {'source': training_page}).count() > 0:
        return True
    else:
        return False


def is_training(url):
    '''
    PURPOSE:    check if url contains articles for training the model
    INPUT:      url (str) - url for site with articles
    OUTPUT:     boolean -  True if url contains articles for training model
    '''
    training_page = 'http://www.prnewswire.com/news-releases/' + \
                    'general-business-latest-news/' + \
                    'personnel-announcements-list/?page=1&pagesize=1'
    if url == training_page:
        return True
    else:
        return False


def get_all_news(coll, url, urlbase):
    '''
    PURPOSE:    Add articles to mongodb. Keys in db are article headlines.
                Store link, source_page, page_soup, and body_soup in db.
    INPUT:      coll (pymongo obj) - connection to db collection
                url (str) - url of site for scraping
                urlbase (str) - concatenate base with link to get full url
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
    PURPOSE:    delay random time between consecutive url requests
    INPUT:      None
    OUTPUT:     None
    '''
    x = np.abs(np.random.normal(0, 1))
    time.sleep(x)


def main():
    '''
    PURPOSE:    scrape articles from PR Newswire and save into mongodb
    INPUT:      None
    OUTPUT:     None
    '''
    cli = pymongo.MongoClient()
    db = cli.pr
    coll = db.prnewswire

    urlbase = 'http://www.prnewswire.com'
    url = 'http://www.prnewswire.com/news-releases/' + \
          'english-releases/?page=1&pagesize=2000'
    url_training = 'http://www.prnewswire.com/news-releases/' + \
                   'general-business-latest-news/' + \
                   'personnel-announcements-list/?page=1&pagesize=2000'
    print 'starting w training'
    get_all_news(coll, url_training, urlbase)
    print 'ended w training'
    get_all_news(coll, url, urlbase)
    cli.close()


if __name__ == '__main__':
    main()
