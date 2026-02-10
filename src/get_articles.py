from flask import Flask, Response
import requests
import json

import xml.etree.ElementTree as ET

app = Flask(__name__)

# =============================
# EVENTS (SRC)
# =============================
event_set = ["Expeditie naar Bali", "Lombok oorlog", "Aceh oorlog", "2e expeditie naar nias", "Tapanahoni Expeditie"]

@app.route("/src/<event_nr>")
def show_src(event_nr):
    return f"this is event {event_set[int(event_nr)]}"

@app.route("/src_meta/<event_nr>")
def show_src_meta(event_nr):
    return f"this is event {event_set[int(event_nr)]}"

@app.route("/src_meta/<event_nr>/<prop>")
def show_src_meta_prop(event_nr, prop):
    know_props = "utc_date", "fulltext", "entities"
    if not prop in know_props:
        return ""
    return f"This is property {prop} of event {event}"

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