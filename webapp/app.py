from flask import Flask
import flask
import pandas as pd
from collections import defaultdict
import pymongo

DF = None

app = Flask(__name__)
app.config.from_object(__name__)
app._static_folder = 'static'

# query string for flask to parse page info -- request.args.get('page', 1)
@app.route('/')
def index():
    # title, img, date_loc, summary = get_one()
    return flask.render_template('index.html')

def get_one(df=DF):
    i = 0
    title = df.ix[i,:]['_id']
    img = df.ix[i,:]['img']
    date_loc = df.ix[i,:]['date'] + ' -- ' + df.ix[i,:]['location'].rstrip(',')
    summary = df.ix[i,:]['text'][:250] + '...'
    return title, img, date_loc, summary

if __name__ == '__main__':
    cli = pymongo.MongoClient()
    db = cli.pr
    cursor = db.pr_realtime.find()
    DF = pd.DataFrame(list(cursor))
    cli.close()
    app.run(host='0.0.0.0', port=8080, debug=True)