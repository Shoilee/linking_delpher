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


### Network Visual 

- [disamb/disambiguation_embedding_faiss_v1.ipynb] does the similar person name matching. (output --> similar_names.json). 
- [src/create_network_graph.py] convert the given json file into st_link_analysis analysis style. (output --> graph_output.json)
- [src/similar_person_vis.py] creates a network visual which shows network of similar person (inspection or annotation module).
- [src/assign_person_uri.py] assign person uri based on graph_output.json. (output --> graph_output.json) 
- TODO: network of persons with articles

