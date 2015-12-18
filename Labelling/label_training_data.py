from flask import Flask
import flask
import pandas as pd
from collections import defaultdict
import pymongo


app = Flask(__name__)
app.config.from_object(__name__)
app._static_folder = 'static'
DF = None
DB = None
INDEX = None
TITLE = None


def save_to_db(form, title, db=DB):
    '''
    PURPOSE:    Triggered from submit button on form.
                Saves training labels for words in article
                headline in mongodb
    INPUT:      form (html form) - fields are correct labels
                title (str) - headline of article
                db (pymongo obj) - conn to mongodb
    OUTPUT:     None
    '''
    labels = defaultdict(list)
    for position, word in enumerate(title.split()):
        word = word.replace('.', '[dot]')
        word = word.replace('$', '[dol]')
        labels[word].append({'position': position,
                             'label': 'other',
                             'POS': ''})
    for item in form:
        if form[item] != '' and item != 'horf':
            for word in form[item].split():
                word = word.replace('.', '[dot]')
                word = word.replace('$', '[dol]')
                for label in labels[word.strip()]:
                    label['label'] = item

    _id = {'_id': title}
    update = {'$set': {'labels': labels,
                       'horf': form['horf']}}
    DB.pr_train.update_one(_id, update)


@app.route('/')
def index():
    '''
    PURPOSE:    Initial site to specify document index
                of where to begin labelling training data
    INPUT:      None
    OUTPUT:     html (str) - html to input dcoument index
    '''
    return '''
        <form action="/label" method='POST' >
            <input type="text" name="index" />
            <input type="submit" />
        </form>
        '''


@app.route('/label', methods=['POST', 'GET'])
def label():
    '''
    PURPOSE:    load article title from mongodb. When a POST request
                is made on the form, the labelled words are stored back
                in the mongodb
    INPUT:  None
    OUTPUT: html (flask html obj) - rendered label.html
    '''
    global INDEX
    global TITLE
    if flask.request.method == 'POST' and INDEX == None:
        INDEX = int(flask.request.form['index'])
    elif flask.request.method == 'POST':
        save_to_db(flask.request.form, TITLE)
    title = DF['_id'].values[INDEX]
    TITLE = title
    INDEX += 1
    return flask.render_template('label.html', text=title, index=INDEX-1)


if __name__ == '__main__':
    cli = pymongo.MongoClient()
    DB = cli.pr
    cursor = DB.pr_train.find({'labels': {'$exists': False}})
    DF =  pd.DataFrame(list(cursor))
    app.run(host='0.0.0.0', port=8080, debug=True)
    cli.close()
