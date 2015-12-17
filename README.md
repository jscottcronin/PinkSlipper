# PinkSlipper
![Pinkslipper Logo](https://github.com/jscottcronin/PinkSlipper/blob/master/Images/logo_356x200.png)

A webapp designed for executive recruiters. Pinkslipper aggregates press releases relating to the hiring / firing of executives around the country and displays them in a simple intuitive UI. A custom Chain Conditional Random Field Model was built to semantically analyze text in press release headlines enabling Pinkslipper to filter the content on the site so it is relevant for an executive recruiter.

![Pinkslipper Logo](https://github.com/jscottcronin/PinkSlipper/blob/master/Images/Webapp_UI.png)

## Motivation
I met several executive recruiters who described a difficult problem in their industry. They are often contracted to find a new CEO, CFO, etc to run a company purchased through a PE shop. They have to close quickly, and it becomes difficult if their networks run dry. Furthermore, sources that currently exist such as LinkedIn, BizJournalNews, and Press Release sites do not yield quick results that one could act on. Therefore, I set out to build a simple intuitive UI that accomplished this goal, eliminating the hangups that plauge alternatives.

## Data Collection
I scraped 10,000 articles from PR Newswire and stored the data in a MongoDB. Articles looked like:

![Press Release](https://github.com/jscottcronin/PinkSlipper/blob/master/Images/press_release_example.png)

## Feature Engineering
Goal was to predict the label for each word in a headline. Possible labels are:

1. Person
2. Organization
3. Position
4. Other

![Labelling](https://github.com/jscottcronin/PinkSlipper/blob/master/Images/headline_labels.png)


PinkSlipper - Using Chain CRF machine learning models to conditionally classify text in press release headlines relating to the hiring / firing of individuals 
