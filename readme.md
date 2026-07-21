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
  - returns/stores the related newspaper issues (not that they are not the article, but the whole isssues)
- load articles to couchDB
  - load data `python src/load_data.py --article -i <input_dir>`
- [ ] automatically create database in couchDB and automatically create views
- show data
  - `src/show_data.py`
  - change global variable COUCH_DB for desired database

Things to discuss: 
- [x] why there is a gap in between DST / DST_XML
- [x] how can we increase event vs article results