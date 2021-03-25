# ICS-Search-Engine
 
# 1.	Introduction
The main goal of this project was to replicate the search engine of my own university’s search engine on their main website under my school of ICS. In order to do this, I first had to build a web crawler in order to scrape all of the current pages related to the school of ICS’s website and store them. Then, build a search engine from the ground up that is capable of handling thousands of documents or Web pages. The details of both the Web crawler and search engine will be explained in detail below. 

# 2.	Acknowledgements
Before we continue, I would like to thank my professor Martins for providing my inspiration for this project, as well as provide much of the Web crawler. 

# 3.	The Web Crawler
The purpose of the Web crawler was to collect all of the important URLs related to the School of ICS on my university’s website. In total my crawler scraped roughly under 2000 Web pages. Below is the list of URL domains my crawler scraped. 

•	. ics.uci.edu
•	. cs.uci.edu
•	. informatics.uci.edu
•	. stat.uci.edu
•	today.uci.edu/department/information_computer_sciences

Additionally, the scraper crawled a caching server in order to receive the URLs rather than scraping the actual school’s website itself. This was so I would not disturb the actual school’s network.

# 3.1.	 Behavioral Requirements 
The crawler was set with a certain list of behavior requirements. A few of which can be found below with the addition of how each of these requirements were met. There were many other requirements that my crawler had to obey, but these were the most important.
•	Honor the politeness delay for each site.
Each thread of the Web crawler was delayed 0.5 seconds after each download. 
•	Crawl all pages with high textual information content.
Pages were avoided if that page had a low token frequency. 
•	Detect and avoid infinite traps as well as sets of similar pages with no information.
Using Simhash fingerprinting from the token frequencies of each Web page.
•	Detect and avoid dead URLs that return a 200 status but no data.
The HTTP response status was evaluated, and the page was avoided if the page contained low textual information content. 
•	Detect and avoid crawling very large files, especially if they have low information value.
Each page was avoided if the content size of the page was above 50,000 kilobytes. 

# 3.2.	 Flow
Below is a simple explanation of how the crawler works. 
&#8594;	The crawler receives a cache host and port from the spacetime servers and instantiates the config. 
&#8594;	It then launches a crawler, which creates a Frontier and Worker(s). 
&#8594;	When the crawler is started, workers are created that pick up a non-downloaded link from the frontier, download it from our cache server, and then pass the response to the scraper function. 
&#8594;	The links that are received by the scraper is added to the list of non-downloaded links in the frontier and the URL that was downloaded is marked as complete. 
&#8594;	The cycle continues until there are no more URLs to be downloaded in the frontier.
The URL’s HTML collected by the scraper were then stored in folders corresponding to their domains.

# 4.	Inverted Indexer
Now that I had collected all of the HTML files related to the School of ICS, I used an inverted indexer to map the tokens of the HTML documents to their corresponding postings. Each post contained the document name and the frequency of that token in the document. The tokens and postings were stored in a PostgreSQL database. This was so that the retrieval process was much faster than using a text, or csv file. The indexer had a total of roughly 11,000 tokens and took around 20 minutes to run. 

# 4.1.	Flow
Below is a simple explanation of how the inverted indexer works. 
&#8594;	The indexer reads an individual HTML file and tokenizes it.
&#8594;	Then removes all stop words and uses Porter stemming for better textual matches.
&#8594;	Bold words and headings in the HTML are weighted to be more important.
&#8594;	The tokens and post are inserted into the PostgreSQL database.
&#8594;	The cycle continues until all of the HTML files are processed and stored.

# 5.	Search Engine
The search engine is used in order to return the five most relevant URLs given the query provided by the user along with the execution time. The execution time of the search is always done in under two seconds.

# 5.1.	 Page Ranking
In order to effectively rank the pages given the user’s query I used tf-idf and cosine similarity. Tf-idf was used in order to measure the importance of tokens in text of each document. Then those scores were used in order to calculate the cosine similarity between the documents tf-idf scores and the query. 

# 5.2.	 Flow
Below is a simple explanation of how the search engine works. 

&#8594;	 The program prompts the user for a query.
&#8594;	 The query terms are stemmed using Porter stemming.
&#8594;	 The postings of the query terms are then extracted from the PostgreSQL database.
&#8594;	 The pages are then ranked using the ranking described above in 5.2.
&#8594;	 Lastly, the five most relevant page URLs are then outputted along with the execution time of the search.

