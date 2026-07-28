import xmltodict as xd
import json
import os
import requests
from utils import extract_str


# TODO: you can update the query strategy
base_EVENT_BASED_URL = f"https://jsru.kb.nl/sru/sru?version=1.2&operation=searchRetrieve&x-collection=DDD_artikel&recordSchema=indexing&startRecord=1&maximumRecords=1&query=(content all \"%s\") AND (date within \"%s %s\")"
# iter_EVENT_BASED_URL = f"https://jsru.kb.nl/sru/sru?version=1.2&operation=searchRetrieve&x-collection=DDD_artikel&recordSchema=indexing&startRecord=%s&maximumRecords=%s&query=\"%s\" AND (date within \"%s %s\")"
iter_EVENT_BASED_URL = f"https://jsru.kb.nl/sru/sru?version=1.2&operation=searchRetrieve&x-collection=DDD_artikel&startRecord=%s&maximumRecords=%s&query=(content all \"%s\") AND (date within \"%s %s\")&recordSchema=ddd&x-fields=zones"

def parse_resp_events(response, event, folder):
    data = xd.parse(response.content, xml_attribs=False)
    raw_records = data['srw:searchRetrieveResponse']['srw:records']['srw:record']
    if not isinstance(raw_records, list):
        raw_records = [raw_records]
   
    # print(f"raw_records: {len(raw_records)} for response: {response.url}")

    # THIS IS TEMPORARY
    dir = os.getcwd()
    dir = os.path(dir, "folder")
    
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


import pandas as pd

import requests
import lxml.etree

def get_article_by_event(event:json, dir):
    title = event.get("title", "")
    date_y = event.get("date_y", "")
    # print(f"Title: {title}, Fulltext: {fulltext}, Date: {date_y}")

    base_url = base_EVENT_BASED_URL % (title, date_y, date_y+10)
    print(f"Fetching articles for event: {title} with base URL: {base_url}")

    resp = requests.get(base_url)
    data = lxml.etree.fromstring(resp.content)
    total_nr_results = 0
    for i in data.iter():
        if i.tag == '{http://www.loc.gov/zing/srw/}numberOfRecords':
            total_nr_results = int(i.text)
            break
    print(f"Total results: {total_nr_results} for event: {title}")

    if total_nr_results == 0:
        print(f"No results found for event: {title}")
        return
    
    inv = 10 if total_nr_results > 10 else total_nr_results

    result_dicts = []
    for start in range(1, total_nr_results+1, inv):
        paged_url = iter_EVENT_BASED_URL % (start, inv, title, date_y, date_y+10)
        # print(f"Fetching articles for event: {title} with paged URL: {paged_url}")
        paged_resp = requests.get(paged_url)
        parse_resp_events(paged_resp, event, folder=dir)

    # # convert list of dicts to dataframe
    # df = pd.DataFrame(result_dicts)
    # df.to_csv(f"{title.replace(' ', '_')}_articles.csv", index=False)
    