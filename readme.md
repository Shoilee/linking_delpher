This is KB RinR-2026 Project. 

For project update see the [wiki](https://github.com/Shoilee/linking_delpher/wiki)


### Data Processing
- Create Event Metadata and load it to couchDB
  - `python src/process_events.py`
  - Starts with CouchDB database name and directory to operate on 
- Get Article
  - `src/get_articles.py`
  - starts with the CouchDB database name
  - harvest the events metadata list from the dataase
  - query for the articles related to events (i.e., event title string match and publication year+/- 10 yrs)
  - [ ] clarify how the SRU match was performed
  - returns/stores the related newspaper issues (not that they are not the article, but the whole isssues)
  - Note that, at this point we are not only harvesting articles that are only relavent to events, but also all other articles from the same issue. 
- load articles to couchDB
  - Convert xml `src/create_article_docs.py`
  - load data `python src/load_data.py --article -i <input_dir>`
- [ ] automatically create database in couchDB and automatically create views
- show data
  - `src/show_data.py`
  - change global variable COUCH_DB for desired database

Things to discuss: 
- [ ] why there is a gap in between DST / DST_XML
- [ ] how can we increase event vs article results