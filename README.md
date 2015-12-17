# PinkSlipper
A webapp designed for executive recruiters. Pinkslipper aggregates press releases relating to the hiring / firing of executives around the country and displays them in a simple intuitive UI. A custom Chain Conditional Random Field Model was built to semantically analyze text in press release headlines enabling Pinkslipper to filter the content on the site so it is relevant for an executive recruiter.

![Pinkslipper Logo](https://github.com/jscottcronin/PinkSlipper/blob/master/Images/Webapp_UI.png)

## Motivation
I met several executive recruiters who described a difficult problem in their industry. They are often contracted to find a new CEO, CFO, etc to run a company purchased through a PE shop. They have to close quickly, and it becomes difficult if their networks run dry. Furthermore, sources that currently exist such as LinkedIn, BizJournalNews, and Press Release sites do not yield quick results that one could act on. Therefore, I set out to build a simple intuitive UI that accomplished this goal, eliminating the hangups that plauge alternatives.

## Data Collection
I scraped 10,000 articles from PR Newswire. An example article is below. For each article, I stored relevant information in a MongoDB including:

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

To accurately predict the correct label for each word in a headline, I used the following features for each headline word:

1. Stanford's case insensitive POS tagger
2. Normalized Position in headline
3. Boolean for entire word being capitalized
4. Boolean for entire word being lowercased
5. POS tags of the two words prior and after

## Modeling
![Model Results](https://github.com/jscottcronin/PinkSlipper/blob/master/Images/model_results.png)

![Model Comparison](https://github.com/jscottcronin/PinkSlipper/blob/master/Images/model_comparison.png)
## Results
PinkSlipper - Using Chain CRF machine learning models to conditionally classify text in press release headlines relating to the hiring / firing of individuals 
