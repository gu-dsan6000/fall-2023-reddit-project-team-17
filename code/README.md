# DSAN 6000 Project Code Folder

This document details the various scripts and notebooks created to complete this project. This code is composed of 3 primary sections: `project-eda`, `project-nlp`, and `project-ml`, along with some secondary sections such as `filtering-jobs` and `starter-code`. These will each be detailed and explained below:

## Primary Section 1: `project_eda`

This folder contains all of the notebooks and scripts that comprise the Exploratory Data Analysis (EDA) portion of our project, excluding data acquisition which is performed in the `filtering_jobs` section. Within the `project-eda` folder are the following files (sorted alphabetically):

* `engagement_sentiment_corr.ipynb`:

* `project-eda-aita-texts.ipynb`: This notebook consists of an initial exploration of the data from a preliminary subset of the overall Reddit data set to the 12 subreddits of interest. Multiple plots are created in this section of the notebook including a bar chart showing the counts of valid text posts from each of the 12 subreddits and a scatterplot comparing the mean post scores and number of comments per valid post. Additionally, there is an initial exploration r/AmItheAsshole in relation to the flair prediction task. The data are subsetted to this subreddit and the number of occurrences of each of these flairs is visualized in a bar chart and treemap as can be seen in the `EDA` section of the website.

* `project-eda-exploratory-vis.ipynb`: Within this notebook is the code that generates some exploratory visualizations relating to the NSFW-related portion of our analysis and the subreddit engagement portion of our analysis.

* `project-eda-exploratory.ipynb`: This notebook contains the loading, processing, cleaning, and visualization of the Reddit data related to the exploratory analysis of NSFW posts and various measures of user engagement with posts. Within this notebook we create a new variable relevant to user engagement called `interaction_score` which is composed of post's score and number of comments each accompanied by weights. Additionally, we employed a temporal analysis in the notebook and created new variables associated with the day/month that a given Reddit post was created. Finally, we created some visualizations, of which some are displayed on our project website. Data used to generate the table related to the correlation coefficients associated with the user engagement of posts by subreddit are also saved in this notebook, and presented in a tabular format on the project website.

* `project-eda-predicting-subreddits-vis.ipynb`: In this notebook an Altair plot concerning the number of user engagements (number of comments plus post score) per month which is presented on the project website. Additionally the data used to create this plot can be found in the `data/eda-data` folder.

* `project-eda-predicting-subreddits.ipynb`: Within this notebook we perform some initial exploratory analysis relating to the comments and submissions of all 12 subreddits of interest along with the creation of dummy variables relating to the number of posts that are "valid" (that is to say, not deleted or removed). Additionally, these comments and submissions data are grouped by time frame and then saved to the `data/eda-data` directory.

* `topic_trends.ipynb`: The business ideas relating to topic summarization and visualization are generated in this notebook. A grouped matplotlib bar chart presented on the project website is also generated within this notebook wherein numerous new variables were created based on the topic occurrences by subreddit.

## Primary Section 2: `project-nlp`

* `flairs-nlp.ipynb`: This notebook contains the application of a sentiment model to the subset of data pertaining to `r/AmItheAsshole`. Additionally, we created visualizations and tables that are presented in the `NLP` section of the project website. We also analyzed the sentiment model with respect to the number of engagements (as the number of comments) by assigned flair in this notebook.

* `project-nlp-posts-and-books-generate.ipynb`: Victor fill this in

* `project-nlp-posts-and-books-vis.ipynb`: Victor fill this in

* `project-nlp-predicting-subreddits-cv.ipynb`: This notebook includes a sentiment analysis of the posts in the 12 subreddits of interest and the application of spark-NLP's CountVectorizer to all valid (i.e., non-empty) text posts from all subreddits of interest. The application of NLP techniques are performed in two iterations: one specific to `r/relationship_advice` and one related to all subreddits of interest to generate data for use in the `ML` portion of this project. The NLP processing techniques used in this notebook derive from johnsnowlabs' `spark-nlp` in the form of a pipeline. The CountVectorized form of the valid text posts were saved to the project bucket on AWS.

* `project-nlp-predicting-subreddits-vis.ipynb`: Contains visualizations related to the sentiment analysis performed in `project-nlp-predicting-subreddits-cv.ipynb` and associated tables.

* `project-nlp-predicting-subreddits.ipynb`: This notebook is specific to the business goals concerning `r/relationship_advice` and involves the application of regular expressions to find the ages and genders mentioned in the titles and bodies of text posts. Upon application of these NLP techniques to all valid `r/relationship_advice` posts, they were saved to the project bucket on AWS.

* `topics-nlp.ipynb`: This notebook contains the NLP processing of and subsequent analysis of posts in `r/NoStupidQuestions` with respect to the topics covered in both their submissions and comments.

## Primary Section 3: `project-ml`

* `project-ml-aita-flair-prediction-viz.ipynb`: In this notebook, visualizations of model performance are generated based on the Random Forest models constructed and fitted in the notebook `project-ml-aita-flair-prediction.ipynb`. Two bar charts and four confusion matrices are created and then subsequently saved in the `website-source/img/ml-plots` folder.

* `project-ml-aita-flair-prediction.ipynb`: In this notebook, multiple random forest models are applied to posts from `r/AmItheAsshole` created in 2022. These are generated using various predictors and several performance metrics (accuracy , f1, recall, precision) are calculated and saved into the `data/ml-data` directory along with confusion matrices.

* `project-ml-predicting-subreddits-vis.ipynb`: Within this notebook, several visualizations concerning the random forest models generated in `project-ml-predicting-subreddits.ipynb` are constructed. These are saved off and presented on the project website.

* `project-ml-predicting-subreddits.ipynb`: Various predictors and sampling techniques were applied to all "valid" (non-empty) posts of the 12 subreddits of interest created in 2022 to construct random forest models. Various performance metrics were calculated and confusion matrices constructed, all of which were saved to the `data/ml-data` directory.

* `project-nlp-posts-and-books-model.ipynb`: Victor fill this in

* `project-nlp-posts-and-books-use-trained.ipynb`: Victor fill this in

* `topic-summarization-and-sentiment.ipynb`: ROUGE scores associated with the summarization model established in `topic_summarization.ipynb` are calculated and then visualized (in the form of a violin plot)

* `topic_summarization.ipynb`: 

## Secondary Section 1: `filtering-jobs`

This folder contains the notebook `filtering-jobs.ipynb` and accompanying script `process.py`. The former is where the data acquisition for this project occurred. In this notebook, a script that accesses the overall Reddit dataset, filters for the 12 subreddits of interest, and saves the resulting parquet files in an Amazon S3 bucket on Alex Pattarini's AWS account. The script that serves as the basis for these jobs is the `process.py` script, which is automatically created when running the `filtering-jobs.ipynb` notebook.

## Secondary Section 2: `starter-jobs`

This section contains the starter code provided to us by Professors Marck Vaisman, Abhijit Dasgupta, Amit Arora, and Anderson Monken. These files aided us in creating in both the data acquisition performed in the `filtering-jobs` section and the data processing/analysis performed in other sections.