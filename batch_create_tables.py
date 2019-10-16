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

aggregations = '''
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

if __name__ == 'main':
    start = time.time()

    duration = time.time() - start
    duration = round(duration / 60 / 60, 4)
    print(f'Total time taken = {duration} hours')
    pass