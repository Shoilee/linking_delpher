import argparse
import json
import os
import requests
import xmltodict as xd
import lxml.etree
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

    out_dir = os.path.join(folder, "DST")
    os.makedirs(out_dir, exist_ok=True)

    for record in raw_records:
        record_data = record['srw:recordData']
        record_data['zones'] = json.loads(record_data['zones'])
        ocr_url = record_data['dc:identifier']
        with requests.get(ocr_url) as ocr_response:
            record_data['ocr'] = ocr_response.text

        record_data['event_id'] = event.get('id', '')
        record_data['event_title'] = event.get('title', '')

        identifier = "_".join(extract_str(record_data['dc:identifier'], '?urn=').split(':')[:-1])
        filename = os.path.join(out_dir, identifier + '.json')

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(record_data, f, indent=2, ensure_ascii=False)

def get_article_by_event(event, out_dir):
    title = event.get("title", "")
    date_y = int(event.get("date_y", 0))

    base_url = base_EVENT_BASED_URL % (title, date_y, date_y + 10)
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

    for start in range(1, total_nr_results + 1, inv):
        paged_url = iter_EVENT_BASED_URL % (start, inv, title, date_y, date_y + 10)
        paged_resp = requests.get(paged_url)
        parse_resp_events(paged_resp, event, folder=out_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--date_y", type=int, required=True)
    parser.add_argument("--event_id", default="")
    parser.add_argument("--out_dir", required=True)
    args = parser.parse_args()

    event = {
        "title": args.title,
        "date_y": args.date_y,
        "id": args.event_id,
    }

    get_article_by_event(event, args.out_dir)