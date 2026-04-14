import argparse
import os, json
from xml.etree.ElementTree import indent
import requests
import xmltodict as xd
from get_article_by_ppn import filter_articles_by_id
import lxml.etree
from utils import extract_str

"""
Example queries:
# retunr articles related to the event "2e expeditie naar Nias"
https://jsru.kb.nl/sru/sru?version=1.2&operation=searchRetrieve&x-collection=DDD_artikel&maximumRecords=50&query="2e expeditie naar Nias"&recordSchema=ddd&x-fields=zones

https://www.wikidata.org/wiki/Wikidata:Database_download/n

https://jsru.kb.nl/sru/sru?version=1.2&operation=searchRetrieve&x-collection=DDD_artikel&recordSchema=indexing&startRecord=1&maximumRecords=50&query=(date within "1938 1939") AND Wilhelmina AND Elfstedentocht

https://jsru.kb.nl/sru/sru?query=ppna=45136599&version=1.2&operation=searchRetrieve&x-collection=DDD_artikel&recordSchema=indexing&startRecord=1&maximumRecords=50
"""

# retrieve the individual issue with the same PPN
URL = f'https://jsru.kb.nl/sru/sru?query=ppna=%s&version=1.2&operation=searchRetrieve&startRecord=1&maximumRecords=1&recordSchema=ddd&x-collection=DDD_krantnr&x-fields=ppna'
# e.g., https://jsru.kb.nl/sru/sru?query=ppna=832452025&version=1.2&operation=searchRetrieve&startRecord=1&maximumRecords=1&recordSchema=ddd&x-collection=DDD_krantnr&x-fields=ppna 

URL1 = f'https://jsru.kb.nl/sru/sru?query=ppna=%s&version=1.2&operation=searchRetrieve&startRecord=%s&maximumRecords=10&recordSchema=ddd&x-collection=DDD_krantnr&x-fields=ppna'

DIDL = 'https://services.kb.nl/mdo/oai?verb=GetRecord&identifier=%s&metadataPrefix=didl'

base_EVENT_BASED_URL = f"https://jsru.kb.nl/sru/sru?version=1.2&operation=searchRetrieve&x-collection=DDD_artikel&recordSchema=indexing&startRecord=1&maximumRecords=1&query=\"%s\" AND (date within \"%s %s\")"
# iter_EVENT_BASED_URL = f"https://jsru.kb.nl/sru/sru?version=1.2&operation=searchRetrieve&x-collection=DDD_artikel&recordSchema=indexing&startRecord=%s&maximumRecords=%s&query=\"%s\" AND (date within \"%s %s\")"
iter_EVENT_BASED_URL = f"https://jsru.kb.nl/sru/sru?version=1.2&operation=searchRetrieve&x-collection=DDD_artikel&startRecord=%s&maximumRecords=%s&query=\"%s\" AND (date within \"%s %s\")&recordSchema=ddd&x-fields=zones"


# /mdo/oai?
# https://services.kb.nl/mdo/oai?verb=GetRecord&identifier=KRANTEN:KBNRC01:KBNRC01:000028900:mpeg21&metadataPrefix=didl

prev_ppn = ''
prefix = ''

respbuff = []

# =============================
# remembers last 10 responses
# avoids repeating identical requests
# =============================
def resp_buff(url):
    global respbuff

    for item in respbuff:
        if url in item:
            return item.get(url)
    respbuff.append({url: ""})

    if len(respbuff) > 10:
        respbuff.reverse()
        respbuff.pop()
        respbuff.reverse()
    resp = requests.get(url)
    respbuff[-1] = {url: resp.content}
    return respbuff[-1].get(url)

def create_event_metadata_list(COUCH_DB):
    def get_doc_ids_from_view(db_url, design_doc, view_name):
        """Get all document IDs from a specific CouchDB view."""
        view_url = f"{db_url}/_design/{design_doc}/_view/{view_name}"
        # print(f"Querying CouchDB view at: {view_url}")
        
        # Query the view to get all rows
        response = requests.get(view_url)
        if response.status_code != 200:
            print(f"View query failed: {response.text}")
            return []
        
        data = response.json()
        # Extract document IDs from each row
        events_list = [row for row in data['rows']]
       
        events_meta_list = []
        for event in events_list:
            secelector = {"_id": f"{event['id']}"}
            find_url = f"{DB_URL}/_find"
            response = requests.post(find_url, json={"selector": secelector}, headers={"Content-Type": "application/json"})
            json_respinse = json.loads(response.content.decode('utf-8'))
            events_meta_list.append(json_respinse.get('docs')[0])
        return events_meta_list

    DB_URL = f'http://admin:123456@127.0.0.1:5984/{COUCH_DB}'
    src_meta_set = get_doc_ids_from_view(DB_URL, 'view', 'event')

    return src_meta_set

# event_set = [{"title": "expeditie naar bali", "fulltext": "Description of event 1", "date_y": 1906},
#                 {"title": "Expeditie naar Nias", "fulltext": "Description of event 2", "date_y": 1863},
#                 {"title": "Tapanahoni Expeditie", "fulltext": "Description of event 3", "date_y": 1904}]

def parse_resp_events(response, event, dir):
    data = xd.parse(response.content, xml_attribs=False)
    raw_records = data['srw:searchRetrieveResponse']['srw:records']['srw:record']
    if not isinstance(raw_records, list):
        raw_records = [raw_records]
   
    # print(f"raw_records: {len(raw_records)} for response: {response.url}")

    for record in raw_records:
        record_data = record['srw:recordData']
        # Load zones as json
        record_data['zones'] = json.loads(record_data['zones'])
        # Get OCR (text content of response)
        ocr_url = record_data['dc:identifier']
        with requests.get(ocr_url) as ocr_response:
            record_data['ocr'] = ocr_response.text
        record_data['event_id'] = event.get('id', '')
        record_data['event_title'] = event.get('title', '')

        identifier = "_".join(extract_str(record_data['dc:identifier'], '?urn=').split(':')[:-1])  # Extract identifier and remove 'ddd:' prefix
        filename = os.path.join(dir, 'DST', identifier + '.json')

        # print(f"{type(record_data)} for record_data type, {filename} for filename")

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(record_data, f, indent=2, ensure_ascii=False)


def get_article_by_event(event_set, OUTPUT_DIR):
    for event in event_set:
        title = event.get("title", "")
        fulltext = event.get("fulltext", "")
        date_y = event.get("date_y", "")
        # print(f"Title: {title}, Fulltext: {fulltext}, Date: {date_y}")

        base_url = base_EVENT_BASED_URL % (title, date_y-10, date_y+10)

        resp = requests.get(base_url)
        data = lxml.etree.fromstring(resp.content)
        total_nr_results = 0
        for i in data.iter():
            if i.tag == '{http://www.loc.gov/zing/srw/}numberOfRecords':
                total_nr_results = int(i.text)
                break
        print(f"Total results: {total_nr_results} for event: {title}")

        if total_nr_results == 0:
            continue
        inv = 100 if total_nr_results > 100 else total_nr_results
        for start in range(1, total_nr_results+1, inv):
            paged_url = iter_EVENT_BASED_URL % (start, inv, title, date_y-10, date_y+10)
            # print(f"Fetching articles for event: {title} with paged URL: {paged_url}")
            paged_resp = requests.get(paged_url)
            parse_resp_events(paged_resp, event, OUTPUT_DIR)

if __name__ == "__main__":
    arguments = argparse.ArgumentParser()
    arguments.add_argument('-db', '--database', help='CouchDB URL', required=False)
    arguments.add_argument('-o', '--output_path', help='Path to the JSON file to save', required=True)
    args = arguments.parse_args()
    COUCH_DB = args.database if args.database else "rinr-2026"
    OUTPUT_DIR = args.output_path
    print(f"Using CouchDB database: {COUCH_DB}")
    print(f"Output directory: {OUTPUT_DIR}")


    ALL_EVENTS = create_event_metadata_list(COUCH_DB)
    
    get_article_by_event(ALL_EVENTS, OUTPUT_DIR=OUTPUT_DIR)
    # get_articles_by_ppn()