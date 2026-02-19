from flask import Flask, Response
import requests
import json

import xml.etree.ElementTree as ET
from datetime import datetime, timezone


with open('data/sample_events.json', 'r') as file:
    ALL_EVENTS = json.load(file)

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


def make_utc_date(year, month, day):
    dt = datetime(int(year), int(month), int(day), tzinfo=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def literal_to_d_m_y(date_literal):
    # Example: "1940-01-21" -> (1940, 1, 21)
    year, month, day = date_literal.split("-")
    return int(year), int(month), int(day)

def create_meta_data(event):
    year, month, day = literal_to_d_m_y(event.get("timeSpan_start", "") if event.get("timeSpan_start", "") else (0,0,0))
    # NOTE: we are only using the start date for the meta data, but we could also use the end date if needed
    meta_data = {
        "fulltext": event.get("description", ""),
        "title": event.get("title", ""),
        "date_y": year,
        "date_m": month,
        "date_d": day,
        "UTC_DATE": make_utc_date(year, month, day),
        "entities": set()
    }
    return meta_data

@app.route("/src_meta/<event_nr>")
def show_src_meta(event_nr):
    return f"{create_meta_data(ALL_EVENTS[int(event_nr)])}"
    
@app.route("/src_meta/<event_nr>/<prop>")
def show_src_meta_prop(event_nr, prop):
    know_props = "utc_date", "fulltext", "entities", "title", "date_y", "date_m", "date_d", 
    if not prop in know_props:
        return ""
    return f"This is property {prop} is: {create_meta_data(ALL_EVENTS[int(event_nr)])[prop]}"

# =============================
# PAPERS (DST)
# =============================
dst_set = ["ddd:110579079:mpeg21:a0211", "ddd:110579079:mpeg21:a0212"]

@app.route("/dst/<paper_nr>")
def show_dst(paper_nr):
    data = requests.get(f'http://resolver.kb.nl/resolve?urn={dst_set[int(paper_nr)]}:ocr')
    response = Response(data.content, mimetype='application/xml')
    return response


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