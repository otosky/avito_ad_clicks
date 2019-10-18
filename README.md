# Predicting CTR on Avito Context Ads

## Overview

This is a series of notebooks for predicting click-through-rate (CTR) on Context
Ads from Avito.ru classifieds.  

## Requirements/Dependencies
Notebooks tested on an ancient 2012 MacBook Pro - 2.9 GHz Intel Core i7 / 16GB RAM

You'll want to have at least 200GB of free disk space.

Environment:
- python 3.7.3 
- scikit-learn 0.21.2
    - Probably the only hard-requirement: you'll need to have sklearn v.0.20
at the very least, since I utilize the `make_column_transformer` function.
- numpy 1.16.2
- pandas 0.24.2
- sqlite 3.27.2
- xgboost 0.90 - not necessary, but including version details for reference

## Data Source
The dataset comes from Kaggle: https://www.kaggle.com/c/avito-context-ad-clicks/data

The zip file you'll download comprises 8 relational tables, split amongst separate
.tsv files. They also included the tables packaged in a sqlite database.  *The code 
in this repo only references the SQLite database, so you can discard the tsv files
if you like.*

I would recommend, however, making a separate backup copy of the 
database.sqlite file, once you've uncompressed it, to spare you from potentially having 
to re-download/de-compress the dataset if the sqlite file gets corrupted somehow.

- Disk space usage of raw sqlite database: ~40GB
- Disk space usage of final sqlite database: ~171GB
- Disk space usage of pickle directory: ~1.5GB

#### Important!
My approach was to try and conserve in-memory use by creating many sub-tables in
SQLite, at the expense of disk-space. 

One issue with this is that it takes quite some time to generate these sub-tables.  We're talking HOURS here - 9.5 hours on my aging machine, YMMV.  

If watching paint dry is not your thing :nail_care:, I encourage you to run the 
`batch_create_tables.py` script to expedite this process.  Set it up in the background, or 
overnight, and it will build all the sub-tables for you.  *The commands are still 
in the notebooks so that you can follow along and understand the table schemas.*

In a terminal, `cd` to the directory where you cloned the repo and execute:
`python batch_create_tables.py`

## Notebook Structure

`1_eda_sql.ipynb` covers basic EDA using SQL on the dataset.

`2_split_data_baseline.ipynb` covers the general strategy for splitting the dataset
into training, validation, and test sets.  It also establishes a baseline Logistic Regression
model with just a handful of basic features.

`3_feature_engineering.ipynb` covers feature engineering and performs model validation on a 
more robust feature set.  Final evaluation on a hold-out test set is included, as well as,
code to create a submission to see how the model fares against the Kaggle leaderboard.

**Note:** this competition was from 2015 - so your submission won't be valid for any street-cred 
or :moneybag:.

## Results

Note final feature-set, model, time-diagnostics, and eval metric on hold-out
