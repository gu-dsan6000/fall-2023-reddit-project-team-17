# DSAN 6000 Project Code Folder

This document details the various scripts and notebooks created to complete this project. This code is composed of 3 primary sections: `project-eda`, `project-nlp`, and `project-ml`, along with some secondary sections such as `filtering-jobs` and `starter-code`. These will each be detailed and explained below:

## Primary Section 1: `project_eda`

This folder contains all of the notebooks and scripts that comprise the Exploratory Data Analysis (EDA) portion of our project, excluding data acquisition which is performed in the `filtering_jobs` section. Within the `project-eda` folder are the following files (sorted alphabetically):

* `project-eda-aita-texts.ipynb`: This notebook consists of an initial exploration of the data from a preliminary subset of the overall Reddit data set to the 12 subreddits of interest. Multiple plots are created in this section of the notebook including a bar chart showing the counts of valid text posts from each of the 12 subreddits and a scatterplot comparing the mean post scores and number of comments per valid post. Additionally, there is an initial exploration r/AmItheAsshole in relation to the flair prediction task. The data are subsetted to this subreddit and the number of occurrences of each of these flairs is visualized in a bar chart and treemap as can be seen in the `EDA` section of the website.

* `project-eda-exploratory-vis.ipynb`: 

* `project-eda-exploratory.ipynb`:

* `project-eda-predicting-subreddits-vis.ipynb`:

* `project-eda-predicting-subreddits.ipynb`:

## Primary Section 2: `project-nlp`

## Primary Section 3: `project-ml`

## Secondary Section 1: `filtering-jobs`

This folder contains the notebook `filtering-jobs.ipynb` and accompanying script `process.py`. The former is where the data acquisition for this project occurred. In this notebook, a script that access the overall Reddit dataset, filters for the 12 subreddits of interest, and saves the resulting parquet files in an Amazon S3 bucket on Alex Pattarini's AWS account. The script that serves as the basis for these jobs is the `process.py` script, which is automatically created when running the `filtering-jobs.ipynb` notebook.

## Secondary Section 2: `starter-jobs`

This section contains the starter code given to us by Professor Marck Vaisman, Abhijit Dasgupta, Amit Arora, and Anderson Monken. These files aided us in creating in both the data acquisition performed in the `filtering-jobs` section and the data processing/analysis performed in other sections.