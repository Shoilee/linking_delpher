from flask import Flask, Response
import requests
import json

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from utils import json_pretty_print

# CHANGE THIS BASED ON YOUR DESIRE
with open('example/events.json', 'r') as file:
    ALL_EVENTS = json.load(file)
COUCH_DB = "rinr-2026"

app = Flask(__name__)

@app.route('/')
def index():
    return 'Welcome to the linking delpher API!'

# =============================
# EVENTS (SRC)
# =============================
# event_set = ["Expeditie naar Bali", "Lombok oorlog", "Aceh oorlog", "2e expeditie naar nias", "Tapanahoni Expeditie"]

@app.route("/src/<event_nr>")
def show_src(event_nr):
    response = {"id" : "",
                "title" : "",
                "description" : "",
                "timeSpan_start" : "",
                "timeSpan_end" : ""}
    
    for key in response.keys():
        response[key] = ALL_EVENTS[int(event_nr)].get(key, "")
    response = Response(json.dumps(response),  mimetype='application/json')
    
    return response

def get_doc_ids_from_view(db_url, design_doc, view_name):
    """Get all document IDs from a specific CouchDB view."""
    view_url = f"{db_url}/_design/{design_doc}/_view/{view_name}"
    
    # Query the view to get all rows
    response = requests.get(view_url)
    if response.status_code != 200:
        print(f"View query failed: {response.text}")
        return []
    
    data = response.json()
    # Extract document IDs from each row
    doc_ids = [row['id'] for row in data['rows']]

    print(f"Found {len(doc_ids)} documents in view '{design_doc}/{view_name}'")
    return doc_ids

DB_URL = f'http://admin:123456@127.0.0.1:5984/{COUCH_DB}'
src_meta_set = get_doc_ids_from_view(DB_URL, 'view', 'event')

@app.route("/src_meta/<event_nr>")
def show_src_meta(event_nr):
    secelector = {"_id": f"{src_meta_set[int(event_nr)]}"}
    find_url = f"{DB_URL}/_find"
    response = requests.post(find_url, json={"selector": secelector}, headers={"Content-Type": "application/json"})
    json_respinse = json.loads(response.content.decode('utf-8'))
    # data = requests.get(f'http://resolver.kb.nl/resolve?urn={dst_set[int(paper_nr)]}:ocr')
    # root = ET.fromstring(data.content.decode('utf-8'))
    # for item in root.iter():
    #     if item.tag and item.text:
    #         if item.tag == prop:
    #             return item.text
    return json_respinse
    
@app.route("/src_meta/<event_nr>/<prop>")
def show_src_meta_prop(event_nr, prop):
    know_props = "utc_date", "fulltext", "entities", "title", "date_y", "date_m", "date_d", 
    if not prop in know_props:
        return f"No such prop: {prop}"
    
    secelector = {"_id": f"{src_meta_set[int(event_nr)]}"}
    find_url = f"{DB_URL}/_find"
    response = requests.post(find_url, json={"selector": secelector}, headers={"Content-Type": "application/json"})
    json_data = json.loads(response.content).get('docs')[0][prop]
    return f"This is property {prop} is: {json_data}"

# =============================
# PAPERS (DST)
# =============================

# dst_set = ["ddd:110579079:mpeg21:a0211", "ddd:110579079:mpeg21:a0212"]
dst_set = get_doc_ids_from_view(DB_URL, 'view', 'article_text')

# @app.route("/dst/<paper_nr>")
# def show_dst(paper_nr):
#     data = requests.get(f'http://resolver.kb.nl/resolve?urn={dst_set[int(paper_nr)]}:ocr')
#     response = Response(data.content, mimetype='application/xml')
#     return response

@app.route("/dst/<paper_nr>")
def show_dst_prop(paper_nr):
    secelector = {"_id": f"{dst_set[int(paper_nr)]}"}
    find_url = f"{DB_URL}/_find"
    response = requests.post(find_url, json={"selector": secelector, "fields": ["_id","_rev", "type", "ocr_text"]}, headers={"Content-Type": "application/json"})
    
    # data = requests.get(f'http://resolver.kb.nl/resolve?urn={dst_set[int(paper_nr)]}:ocr')
    # root = ET.fromstring(data.content.decode('utf-8'))
    # for item in root.iter():
    #     if item.tag and item.text:
    #         if item.tag == prop:
    #             return item.text
    return response.content.decode('utf-8')


def lookup_paper_publish_date(identifier):
    return '1912-01-01'

@app.route("/dst_meta/<paper_nr>")
def show_dst_meta(paper_nr):
    response = {"fulltext" : "",
                "title" : "",
                "pars": 0}

    data = requests.get(f'http://resolver.kb.nl/resolve?urn={dst_set[int(paper_nr)]}:ocr')
    root = ET.fromstring(data.content.decode('utf-8'))
    for item in root.iter():
        if item.tag and item.text:
            if item.tag == 'title':
                response['title'] = item.text
    response = Response(json.dumps(response),  mimetype='application/json')
    return response


@app.route("/dst_meta/<paper_nr>/<prop>")
def show_dst_meta_prop(paper_nr, prop):
    data = requests.get(f'http://localhost:5000/dst_meta/{paper_nr}').json()
    return data.get(prop)

if __name__ == '__main__':
    app.run(debug=True)