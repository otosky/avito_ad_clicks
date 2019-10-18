import sqlite3
import time

conn = sqlite3.connect('database.sqlite')
cursor = conn.cursor()
print("Opened database successfully")

basic = '''
-- add basic indices on User Page Visit Streams
CREATE INDEX AdID_Index ON VisitsStream(AdID);

CREATE INDEX AdID_Index2 ON PhoneRequestsStream(AdID);

-- set primary keys on trainSearchStream
ALTER TABLE trainSearchStream RENAME TO old_tss;
CREATE TABLE trainSearchStream
    (
    SearchID INTEGER,
    AdID INTEGER,
    Position INTEGER,
    ObjectType INTEGER,
    HistCTR REAL,
    IsClick INTEGER,
    PRIMARY KEY (SearchID, AdID)
    );
INSERT INTO trainSearchStream 
    SELECT * FROM old_tss;
DROP TABLE old_tss;

-- set primary key on SearchInfo
ALTER TABLE SearchInfo RENAME TO old_si;
CREATE TABLE SearchInfo
    (
    SearchID INTEGER PRIMARY KEY,
    SearchDate DATETIME,
    IPID INTEGER,
    UserID INTEGER,
    IsUserLoggedOn INTEGER,
    SearchQuery,
    LocationID INTEGER,
    CategoryID INTEGER,
    SearchParams
    );
INSERT INTO SearchInfo
    SELECT * FROM old_si;
DROP TABLE old_si;

-- set AdID index on trainSearchStream
CREATE INDEX AdID_Index_tss ON trainSearchStream(AdID, SearchID);
'''

search2 = '''
CREATE TABLE SearchInfo2
    (
    SearchID INTEGER PRIMARY KEY,
    SearchDate DATETIME,
    IPID INTEGER,
    UserID INTEGER,
    IsUserLoggedOn INTEGER,
    SearchQuery,
    LocationID INTEGER,
    CategoryID INTEGER,
    SearchParams
    );

INSERT INTO SearchInfo2
    SELECT * FROM SearchInfo
    WHERE SearchID NOT IN (
        SELECT SearchID 
        FROM TestSearchStream);

CREATE INDEX User_index ON SearchInfo2(UserID);
'''

last10days = '''
CREATE TABLE last10days AS

    SELECT * FROM SearchInfo2
    WHERE SearchDate > "2015-05-11 00:00:00.0"
    ORDER BY SearchDate DESC;

CREATE TABLE last10days_imp AS

    SELECT * FROM trainSearchStream
    WHERE SearchID IN (
    SELECT SearchID FROM last10days 
    ORDER BY SearchID ASC);

CREATE TABLE last10days_ads AS

    SELECT * FROM AdsInfo
    WHERE AdID IN (
    SELECT AdID FROM last10days_imp 
    ORDER BY AdID ASC);

CREATE TABLE last10days_merged AS

    SELECT i.*, a.*, s.*
    FROM last10days_imp i
    JOIN (
        SELECT * FROM last10days 
         ) s
    ON s.SearchID = i.SearchID
    JOIN last10days_ads a
    ON a.AdID = i.AdID;

CREATE TABLE hist_visits AS

    SELECT * FROM VisitsStream
    WHERE ViewDate > "2015-05-11 00:00:00.0"
    AND   UserID IN (
            SELECT UserID FROM last10days);
'''

train_val_split = '''
CREATE TABLE last_seven_searches AS

    SELECT last_seven.*
    FROM
        (SELECT UserID, SearchID, SearchDate,
                row_number() OVER 
                (PARTITION BY UserID ORDER BY SearchDate DESC) AS row_n
        FROM last10days) last_seven
    WHERE row_n <= 7;

CREATE TABLE hist_searches AS

    SELECT last_seven.*
    FROM
        (SELECT UserID, SearchID, SearchDate,
                row_number() OVER 
                (PARTITION BY UserID ORDER BY SearchDate DESC) AS row_n
        FROM last10days) last_seven
    WHERE row_n > 7;
'''

aggregations = '''
CREATE TABLE hist_user_agg AS

    WITH historical_impressions AS (
        SELECT m.SearchID, AdID, UserID, IsClick, 
            IsContext, CategoryID CategoryID_s
        FROM last10days_merged m
        WHERE m.SearchID IN (
            SELECT SearchID 
            FROM hist_searches
                            )
    )

    SELECT a.UserID,
        user_total_searches,
        user_category_counts,
        user_total_clicks,
        user_total_impressions 

    FROM (  SELECT UserID,
                COUNT(SearchID) user_total_searches,
                COUNT(DISTINCT(CategoryID_s)) user_category_counts,
                SUM(IsClick) user_total_clicks
            FROM historical_impressions
            GROUP BY UserID
            ) AS a

    JOIN (  SELECT UserID,
                COUNT(AdID) user_total_impressions
            FROM historical_impressions
            WHERE IsContext = 1
            GROUP BY UserID 
            ) AS b
        ON a.UserID = b.UserID
    ORDER BY a.UserID;

CREATE TABLE hist_cat_agg_daily AS

    WITH hist_imp AS (
        SELECT m.SearchID, AdID, SearchDate, IsClick, 
            IsContext, Price, CategoryID CategoryID_s
        FROM last10days_merged m
    )

    SELECT a.CategoryID_s,
        a.search_date,
        cat_total_searches,
        cat_mean_price,
        cat_total_clicks,
        cat_total_impressions
            
    FROM (
        SELECT CategoryID_s,
            DATE(SearchDate) search_date,
            COUNT(DISTINCT(SearchID)) cat_total_searches,
            AVG(Price) cat_mean_price
        FROM hist_imp
        GROUP BY CategoryID_s, Date(SearchDate)
        ORDER BY CategoryID_s
        ) AS a
        
    JOIN (
        SELECT CategoryID_s, 
            DATE(SearchDate) search_date,
            SUM(IsClick) cat_total_clicks,
            COUNT(AdID) cat_total_impressions
        FROM hist_imp
        WHERE IsContext = 1
        GROUP BY CategoryID_s,  Date(SearchDate)
        ) AS b
    ON a.CategoryID_s = b.CategoryID_s
    AND a.search_date = b.search_date;

CREATE TABLE hist_ad_agg_daily AS

    WITH hist_imp AS (
    SELECT SearchID, SearchDate, AdID, Title, 
        IsClick, IsContext, CategoryID CategoryID_s
    FROM last10days_merged 
    )

    SELECT
        AdID,
        DATE(SearchDate) search_date,
        COUNT(SearchID) ad_total_impressions,
        SUM(IsClick) ad_total_clicks

    FROM hist_imp
    WHERE IsContext = 1
    GROUP BY AdID, Date(SearchDate)
    ORDER BY AdID;

CREATE TABLE hist_userAd_agg AS

    WITH hist_imp AS (
    SELECT m.SearchID, AdID, UserID, IsClick, 
        IsContext, CategoryID CategoryID_s
    FROM last10days_merged m
    WHERE m.SearchID IN (
        SELECT SearchID 
        FROM hist_searches
                        )
    )

    SELECT 
        UserID,
        AdID,
        COUNT(*) times_user_has_seen_ad
    FROM hist_imp

    WHERE IsContext = 1
    GROUP BY UserID, AdID
    ORDER BY UserID, AdID;

CREATE TABLE hist_visits_before_tr AS

    --selecting how many landing pages a given User has visited
    SELECT hv.UserID, 
           COUNT(hv.AdID) 'hist_user_total_visits'
    FROM hist_visits hv

    --join the last searchdate for each user prior to last 7 searches
    INNER JOIN (
        SELECT UserID, MAX(SearchDate) latest_search
        FROM hist_searches
        GROUP BY UserID) AS maxSD
    ON hv.UserID = maxSD.UserID

    --only count the landing page views that precede the user's last search
    WHERE hv.ViewDate < maxSD.latest_search
    GROUP BY hv.UserID;
'''

undersample = '''
CREATE TABLE unclicked_tss
    (
    SearchID INTEGER,
    AdID INTEGER,
    Position INTEGER,
    ObjectType INTEGER,
    HistCTR REAL,
    IsClick INTEGER,
    PRIMARY KEY (SearchID, AdID)
    );

INSERT INTO unclicked_tss 
    SELECT * FROM trainSearchStream
    WHERE IsClick=0;
    
CREATE TABLE just_context_tss
    (
    SearchID INTEGER,
    AdID INTEGER,
    Position INTEGER,
    ObjectType INTEGER,
    HistCTR REAL,
    IsClick INTEGER,
    PRIMARY KEY (SearchID, AdID)
    );

INSERT INTO just_context_tss 
    SELECT * FROM trainSearchStream
    WHERE IsClick=0 OR IsClick=1;
'''

kaggle = '''
CREATE TABLE test_merged AS

SELECT i.*, s.*, a.*
FROM testSearchStream i
JOIN SearchInfo s
    ON s.SearchID = i.SearchID
JOIN AdsInfo a
    ON a.AdID = i.AdID
WHERE ObjectType = 3;
'''

scripts = {'basic':basic,
           'search2':search2,
           'last10days':last10days,
           'train_val_split':train_val_split,
           'aggregations':aggregations,
           'undersample':undersample,
           'kaggle':kaggle}

def create_undersampled_table():
    s = time.time()
    # get row shape of unclicked trainSearchStream
    q = '''
    SELECT MAX(rowid) FROM unclicked_tss
    '''
    cursor.execute(q)
    max_rows = cursor.fetchone()
    
    # get number of total clicks in trainSearchStream
    q = '''
    SELECT COUNT(*) FROM just_context_tss
    WHERE IsClick=1;
    '''
    cursor.execute(q)
    total_clicks = cursor.fetchone()

    # undersample non-clicks to clicks at 10:1 ratio
    np.random.seed(666)
    random_rows = np.random.choice(max_rows[0], total_clicks[0]*10, replace=False).tolist()
    # sort the row_ids for faster sql querying
    random_rows = sorted(random_rows)
    # annoyingly, SQLite can only handle 1000 parameters to a query,
    # so you have to perform the query in 1000-row chunks :(
    partitions = len(random_rows) // 1000

    # create schema for undersampled table
    undersampling = '''
    CREATE TABLE undersampled_tss
        (
        SearchID INTEGER,
        AdID INTEGER,
        Position INTEGER,
        ObjectType INTEGER,
        HistCTR REAL,
        IsClick INTEGER,
        PRIMARY KEY (SearchID, AdID)
        );
    '''
    cursor.executescript(undersampling)

    # loop through number of partitions and insert non-clicks to 
    # undersampled table in 1000-row chunks
    for i in range(partitions):

        q = '''
        INSERT INTO undersampled_tss
            SELECT * 
            FROM unclicked_tss
            WHERE rowid IN ({});
        '''.format(', '.join(['?' for _ in range(1000)]))
        start = 1000 * i
        cursor.execute(q, tuple(random_rows[start:start+1000]))
        conn.commit()

    # remainder from last partition 
    # (remember that partitions was calculated with '//' so it was rounded down)
    remainder = random_rows[partitions*1000:]
    q = '''
        INSERT INTO undersampled_tss
            SELECT * 
            FROM unclicked_tss
            WHERE rowid IN ({});
        '''.format(', '.join(['?' for _ in range(len(remainder))]))
    cursor.execute(q, tuple(random_rows[start+1000:]))
    conn.commit()
    f = time.time()


    # insert all clicks into undersampled table
    q = '''
    INSERT INTO undersampled_tss
        SELECT * FROM just_context_tss
        WHERE IsClick = 1;
    '''
    cursor.executescript(q)

    # log execution time and print
    duration = (f - s) / 60
    print(f'Finished "{script_key}" in {round(duration, 2)} min')

def create_table(script_key, cur=cursor, scripts=scripts):

    # log start time and print status
    s = time.time()
    print(f'Creating {script_key} table(s)')
    
    # execute the script
    cur.executescript(scripts[script_key])
    
    # log finish time and print status
    f = time.time()
    duration = (f - s) / 60
    print(f'Finished "{script_key}" in {round(duration, 2)} min')

if __name__ == "__main__":
    # start timer
    start = time.time()
    print('Starting Batch Job')
    # create all tables / function will print individual execution times FYI
    create_table('basic')
    create_table('search2')
    create_table('last10days')
    create_table('train_val_split')
    create_table('aggregations')
    create_table('undersample')
    create_table('kaggle')
    create_undersampled_table()
    # end timer, convert duration to hours
    duration = time.time() - start
    duration = round(duration / 60 / 60, 2)
    # print total execution time
    print('ALL DONE!')
    print(f'Total time taken = {duration} hours')
    