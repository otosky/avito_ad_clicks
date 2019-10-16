# Predicting CTR on Avito Context Ads

## Overview

Note blog posts for long-form reading

## Requirements/Dependencies and Data Source 
Note laptop specifications - expected disk usage
Note Python versions and packages


The dataset comes from Kaggle: https://www.kaggle.com/c/avito-context-ad-clicks/data

The zip file you'll download comprises 8 relational tables, split amongst separate
.tsv files. They also included the tables packaged in a sqlite database.  The code 
in this repo only references the SQLite database, so you can discard the tsv files
if you like.  I would recommend, however, making a separate backup copy of the 
database.sqlite file, once you've uncompressed it, to spare you from potentially having 
to re-download/de-compress the dataset if the sqlite file gets corrupted somehow.

Note disk space usage of raw sqlite database
Note final disk usage of sqlite database
Note disk space usage of pickle directory

#### Important!
My approach was to try and conserve in-memory use by creating many sub-tables in
SQLite, at the expense of disk-space. One issue with this is that it takes 
quite some time to generate these sub-tables.  We're talking HOURS here.  If watching
paint dry is not your thing, I encourage you to run the create_tables.py script to 
expedite this process.  Set it up in the background or overnight and it will build all the 
sub-tables for you.  The commands are still in the notebooks so that you can follow
along and understand the table schemas.

In a terminal, `cd` to the directory where blah.py is contained and execute:
`python blah.py`

## Notebook Structure


## Results

Note final feature-set, model, time-diagnostics, and eval metric on hold-out