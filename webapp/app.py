from flask import Flask, request, redirect, url_for
import flask
from flask.ext.paginate import Pagination
import pandas as pd
import numpy as np
from collections import defaultdict
import pymongo
import re


DF = None
DF_SUBSET = None
PAGES = None
app = Flask(__name__)
app.config.from_object(__name__)


def get_positions(label):
    lst = sorted([(k, v['word']) for k, v in label.iteritems() \
                  if v['model'] == 'POSITION'], key=lambda(p,w): p)
    s = ' '.join([word.upper() for (pos, word) in lst])
    s = ' '.join(re.findall(r'[a-zA-Z]+', s))
    s = re.findall(r"CHIEF [A-Z]+ OFFICER|\bC.O[S' ]", s)
    positions = ['C' + p.split()[1][0] + 'O' \
                 if len(p.split())>1 else p[:3] for p in s]
    return positions


def preprocess(df):
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values('date', ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['date_loc'] = df['date'].astype(str) + ' -- ' + \
                     df['location'].map(lambda x: x.rstrip(','))
    df['summary_250'] = df['text'].map(lambda x: x[:250] + '...')
    s = df['label'].map(get_positions).apply(pd.Series).stack().sum(level=0)
    df = pd.concat([df, pd.get_dummies(s)], axis=1)
    return df


@app.route('/reset')
def reset():
    global PAGES, DF_SUBSET, DF
    DF_SUBSET = DF
    PAGES = len(DF_SUBSET)
    return redirect(url_for('index'))


@app.route('/<int:index>')
def page(index):
    global DF_SUBSET
    article = DF_SUBSET.iloc[index].to_dict()
    text = article['text'].replace(u'\n', '<br>')
    return flask.render_template('page.html', article=article, text=text)


@app.route('/', methods=['GET', 'POST'])
def index():
    global DF_SUBSET, PAGES, DF
    if request.method == 'POST':
        filtr = request.form.getlist('checkboxes')
        if len(filtr) != 0:
            DF_SUBSET = DF[(DF[filtr] == 1).stack().sum(level=0)] \
                        .reset_index(drop=True)
        else:
            DF_SUBSET = DF
        page = 1
        PAGES = len(DF_SUBSET)
    else:
        page = int(request.args.get('page', 1))
    i_end = page * 10
    i_start = i_end - 10
    articles = DF_SUBSET[i_start:i_end].to_dict('index')
    pagination = Pagination(page=page, total=PAGES, css_framework='foundation')
    return flask.render_template('index.html', articles=articles, pagination=pagination)


if __name__ == '__main__':
    cli = pymongo.MongoClient()
    db = cli.pr
    cursor = db.pr_realtime.find()
    df = pd.DataFrame(list(cursor))
    cli.close()

    DF = preprocess(df)
    DF_SUBSET = DF
    PAGES = len(DF_SUBSET)  
    app.run(host='0.0.0.0', port=8080, debug=True)
