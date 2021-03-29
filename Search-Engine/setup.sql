
-------- Create Table --------

CREATE TABLE indexer (
	keys TEXT,
	value TEXT
);

-------- Load Data from Txt ---------
 
COPY indexer
FROM 'C:\Users\imaia\Desktop\CS121\HW#3\ANALYST\indexes.csv'
(FORMAT CSV, HEADER false)
;









