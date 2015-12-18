# PinkSlipper
PinkSlipper is a webapp designed for executive recruiters. It aggregates press releases relating to the hiring / firing of executives around the country and displays them in a simple intuitive UI. A custom Chain Conditional Random Field Model was built to semantically analyze text in each press release headline enabling Pinkslipper to filter the content on the site so it is relevant for an executive recruiter.

![Pinkslipper Logo](https://github.com/jscottcronin/PinkSlipper/blob/master/Images/Webapp_UI.png)

## Motivation
I met several executive recruiters who described a difficult problem in their industry. They are often contracted to find a new CEO, CFO, etc to run a company purchased through a PE shop. They have to close quickly, and it becomes difficult if their networks run dry. Furthermore, sources that currently exist such as LinkedIn, BizJournalNews, and Press Release sites do not yield effective results that one could act on. Therefore, I set out to build a simple intuitive UI that accomplished this goal, eliminating the hangups that plauge various alternatives.

## Data Collection
I scraped 10,000 articles from PR Newswire. An example article is below. For each article, I stored relevant information in a mongoDB including:

1. Headline
2. Time
3. Date
4. Location
5. Images
6. Body Text

![Press Release](https://github.com/jscottcronin/PinkSlipper/blob/master/Images/press_release_example.png)

## Feature Engineering
Goal was to predict the label for each word in a headline. Possible labels are:

1. Person
2. Organization
3. Position
4. Other

![Labelling](https://github.com/jscottcronin/PinkSlipper/blob/master/Images/headline_labels.png)

To accurately predict the correct label for each word in a headline, I used the following features:

1. Stanford's case insensitive POS tagger
2. Normalized Position in headline
3. Boolean for entire word being capitalized
4. Boolean for entire word being lowercased
5. POS tags of the two words prior and after

## Labelling Training Data
To build a supervised model, I manually labeled 550 headlines which contained around ~5000 total words. I built a webapp to simplify this process, allowing a scalable and crowdsourced approach to be taken.

## Modeling
I built a custom chain conditional random field (Chain-CRF) model to predict labels for each word. A CRF is a graphical model which stores features as nodes and connects those features via edges. The weights of the edges are learned through the algorithm such that accuracy is maximized. The inherent graphical nature of this model enables improved accuracy because the label for a given word is inherently affected by the labels of the words around it.

![Model Results](https://github.com/jscottcronin/PinkSlipper/blob/master/Images/model_results.png)

I used a 5-fold cross-validated approach for validating the model. Accuracy is defined by evaluating the number of correctly predicted labels against the total number of predicted labels.
 
![Model Comparison](https://github.com/jscottcronin/PinkSlipper/blob/master/Images/model_comparison.png)

Comparing my Chain-CRF (trained on 550 headlines) to Stanford's state-of-the-art NER (trained on 300,000 lines of text) demonstrates the success of my model. Stanford's model was able to better predict PERSON in a headline by 5%. My model predicted ORGANIZATION 13% better than Stanford's model.

All that said, Stanford's model was never designed to predict POSITION labels. This is the true reason a custom model is needed. My model ended up predicted POSITION with 80% accuracy. Thus for specialized applications, the efforts to build custom models are justified.


## Results  
The chain-CRF model predicted labels for each word with 75% accuracy. It predicted POSITION labels best at 80%, and outperformed any model currently available. The model was then saved, and all unlabelled, scraped articles were piped through it. Their predicted labels were then stored in a final mongoDB. A Flask / Bootstrap webapp was built to display articles in this final mongoDB. They would be loaded in, and simply filtered based on the words with POSITION tags.

An example video of the working app is below. Click on the image to check it out!

[![PinkSlipper Demo](http://img.youtube.com/vi/eVX4VQPxUX0/maxresdefault.jpg)](https://www.youtube.com/watch?v=eVX4VQPxUX0 "PinkSlipper Demo")

## Conclusion
A custom Chain-CRF was built to extract PERSON, ORGANIZATION, and POSITION information from press releases relating to the hiring / firing of executives. A webapp was built to display press releases for interested executive recruiters. The press release content is filtered on the POSITION tags of the articles to ensure it is only displaying content relevant to that specific recruiter.

## Tools Utilized

####Stack:

* python
* git
* markdown

####Debugging:

* ipdb

####Web Scraping:

* requests
* beautiful soup
* newspaper

####Databasing:

* pymongo
* mongodb

####Feature Engineering:

* NLTK
* Stanford POS Tagger
* Stanford NER Tagger (for comparison)
* regex

####Modeling:

* numpy
* pandas
* scikit learn
* pystruct
* json
* pickle

####Plotting:

* matplotlib
* seaborn
* plotly

####Web App:

* flask
* bootstrap
* pagination
* html
* css
