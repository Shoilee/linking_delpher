import os, json
import requests
import lxml.etree

"""
Example queries:
https://www.wikidata.org/wiki/Wikidata:Database_download/nl

https://jsru.kb.nl/sru/sru?version=1.2&operation=searchRetrieve&x-collection=DDD_artikel&recordSchema=indexing&startRecord=1&maximumRecords=50&query=(date within "1938 1939") AND Wilhelmina AND Elfstedentocht

https://jsru.kb.nl/sru/sru?query=ppna=45136599&version=1.2&operation=searchRetrieve&x-collection=DDD_artikel&recordSchema=indexing&startRecord=1&maximumRecords=50
"""


OUTPUT_DIR="example/DST"

# retrieve the individual issue with the same PPN
URL = f'https://jsru.kb.nl/sru/sru?query=ppna=%s&version=1.2&operation=searchRetrieve&startRecord=1&maximumRecords=1&recordSchema=ddd&x-collection=DDD_krantnr&x-fields=ppna'
# e.g., https://jsru.kb.nl/sru/sru?query=ppna=832452025&version=1.2&operation=searchRetrieve&startRecord=1&maximumRecords=1&recordSchema=ddd&x-collection=DDD_krantnr&x-fields=ppna 

URL1 = f'https://jsru.kb.nl/sru/sru?query=ppna=%s&version=1.2&operation=searchRetrieve&startRecord=%s&maximumRecords=10&recordSchema=ddd&x-collection=DDD_krantnr&x-fields=ppna'

DIDL = 'https://services.kb.nl/mdo/oai?verb=GetRecord&identifier=%s&metadataPrefix=didl'

base_EVENT_BASED_URL = f"https://jsru.kb.nl/sru/sru?version=1.2&operation=searchRetrieve&x-collection=DDD_artikel&recordSchema=indexing&startRecord=1&maximumRecords=1&query=\"%s\" AND (date within \"%s %s\")"
iter_EVENT_BASED_URL = f"https://jsru.kb.nl/sru/sru?version=1.2&operation=searchRetrieve&x-collection=DDD_artikel&recordSchema=indexing&startRecord=%s&maximumRecords=10&query=\"%s\" AND (date within \"%s %s\")"


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

# def get_didl(prefix, identifier):
#     if not prefix == 'DDD:':
#         prefix = 'KRANTEN:'+prefix
    
#     url = DIDL % (prefix + identifier)
#     print(f"Fetching DIDL for identifier: {identifier} with url: {url}")
#     # TODO: add prefix to identifier, e.g., ddd:010905171:mpeg21; Note that, anything accept for ddl has prefix KRANTEN: append prefix.
#     # TODO: go back to page metadata
#     # e.g., https://services.kb.nl/mdo/oai?verb=GetRecord&identifier=KRANTEN:MMKB19:MMKB19:003518056:mpeg21&metadataPrefix=didl
#     # TODO: store the page metadata in a separate file, not the article metadata
#     # url = DIDL % (prefix + identifier)
#     # # e.g., url= https://services.kb.nl/mdo/oai?verb=GetRecord&identifier=DDD:ddd:010905171:mpeg21&metadataPrefix=didl

#     # fname = 'data' + os.sep + identifier + '.xml'
#     # fname = fname.replace(':', '_')

#     # if not os.path.isfile(fname):
#     #     resp = requests.get(url)
#     #     # print(resp.content.decode('utf-8'))
#     #     with open(fname, 'w') as fh:
#     #         fh.write(resp.content.decode('utf-8'))
#     return

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


def filter_articles_by_id(xml_content, current_article_id):
    """
    Process OAI-PMH/DIDL response to keep only didl:Item with 
    matching ddd:article_id = current_article_id
    """
    
    # Define namespaces from your file
    namespaces = {
        'didl': 'urn:mpeg:mpeg21:2002:02-DIDL-NS',
        'ddd': 'http://www.kb.nl/namespaces/ddd',
    }
    
    # Parse the XML (handles large 346KB file)
    parser = lxml.etree.XMLParser(recover=True, remove_blank_text=True)
    root = lxml.etree.fromstring(xml_content, parser)
    
    # Count before filtering
    all_items = root.xpath('.//didl:Item', namespaces=namespaces)
    
    # Find and remove non-matching articles
    items_to_remove = []
    for item in all_items:
        # Check if item has ddd:article_id attribute
        article_id = item.get('{http://www.kb.nl/namespaces/ddd}article_id')
        
        if article_id:
            article_id = article_id.split(':')[-1]  # Extract the last part after the last colon
            if article_id != current_article_id:
                items_to_remove.append(item)
            
    # Remove non-matching items
    for item in items_to_remove:
        parent = item.getparent()
        if parent is not None:
            parent.remove(item)
    
    # Pretty print result
    filtered_xml = lxml.etree.tostring(
        root,
        pretty_print=True,
        encoding='unicode'
    )
    
    return filtered_xml


def get_didl(prefix, identifier, article_id, ppn=None):
    if not prefix == 'DDD':
        prefix = 'KRANTEN:'+prefix
    url = DIDL % (prefix +':'+identifier)
    # print(f"Fetching DIDL for identifier: {identifier} with url: {url}")
    
    # e.g., url= https://services.kb.nl/mdo/oai?verb=GetRecord&identifier=DDD:ddd:010905171:mpeg21&metadataPrefix=didl
    #            https://services.kb.nl/mdo/oai?verb=GetRecord&identifier=MMKB19:MMKB19:000691071:mpeg21&metadataPrefix=didl

    if ppn and not os.path.isdir(ppn):
        os.mkdir(os.path.join(OUTPUT_DIR, ppn))

    fname = OUTPUT_DIR +os.sep+ ppn + os.sep + identifier + '.xml' if ppn is not None else OUTPUT_DIR + os.sep + identifier + '.xml'
    fname = fname.replace(':', '_')
    
    if not os.path.isfile(fname):
        resp = requests.get(url)
        filtered_xml = filter_articles_by_id(resp.content.decode('utf-8'), article_id)
        
        # print(resp.content.decode('utf-8'))
        with open(fname, 'w') as fh:
            fh.write(filtered_xml)


def parse_resp_ppns(instr, ppn):
    global prev_ppn
    global prefix
    new_ppn = False

    if not ppn == prev_ppn:
        print('!!!ppn')
        prev_ppn = ppn
        new_ppn = True

    data = lxml.etree.fromstring(instr)
    for i in data.iter():
        # metadata key for each issue
        if i.tag == '{http://www.kb.nl/ddd}metadataKey':
            if new_ppn:
                resp = requests.get(i.text)
                nurl = resp.url # e.g., https://services.kb.nl/mdo/oai?verb=GetRecord&identifier=DDD:ddd:010905171:mpeg21&metadataPrefix=didl
                prefix = nurl.split('=')[2].split('&')[0].replace(i.text.split('=')[-1], '')
            # print(prefix, i.text)
            identifier = i.text.split('=')[-1] # e.g., ddd:010905171:mpeg21
            get_didl(prefix, identifier, ppn)


def get_articles_by_ppn(ppn_filepath='data/sample_PPNA.txt'):
    with open(ppn_filepath, 'r') as fh:
        data = fh.read()
        for line in data.split('\n'):
            data = resp_buff(URL % line.strip())
            ppn = line.strip()
            data = lxml.etree.fromstring(data)
            for i in data.iter():
                if str(i.tag) == '{http://www.loc.gov/zing/srw/}numberOfRecords':
                    total_nr_results = int(i.text)
                    break
        
            for i in range(1, total_nr_results + 1, 10):
                url = URL1 % (ppn, i)
                resp = resp_buff(url) # requests.get(url)
                parse_resp_ppns(resp, ppn)


def parse_resp_events(instr):
    data = lxml.etree.fromstring(instr)
    
    for i in data.iter():
        if i.tag == '{http://purl.org/dc/elements/1.1/}identifier':
            identifier = i.text.split('=')[-1].split(':')[:-1] # e.g., ddd:010905171:mpeg21:a0002
            prefix = identifier[0].upper()  
            article_identifier = identifier[-1] # e.g., a0002

            # here we are moving to page from article metadata, 
                # so we need to fetch the page metadata using the identifier of the article, 
                # which is the same as the identifier of the page metadata except for the last part 
                # (e.g., a0002 -> mpeg21)
            identifier = ':'.join(identifier[:-1]) # e.g., ddd:010905171:mpeg21
            # print(f"Identifier: {identifier}")
            get_didl(prefix, identifier, article_identifier)

def get_article_by_event(event_set):
    for event in event_set:
        title = event.get("title", "")
        fulltext = event.get("fulltext", "")
        date_y = event.get("date_y", "")
        print(f"Title: {title}, Fulltext: {fulltext}, Date: {date_y}")

        base_url = base_EVENT_BASED_URL % (title, date_y-10, date_y+10)

        resp = requests.get(base_url)
        data = lxml.etree.fromstring(resp.content)
        total_nr_results = 0
        for i in data.iter():
            if i.tag == '{http://www.loc.gov/zing/srw/}numberOfRecords':
                total_nr_results = int(i.text)
                break
        print(f"Total results: {total_nr_results} for event: {title}")

        for start in range(1, total_nr_results+1, 10):
            paged_url = iter_EVENT_BASED_URL % (start, title, date_y-10, date_y+10)
            # print(paged_url)
            paged_resp = requests.get(paged_url)
            parse_resp_events(paged_resp.content)

if __name__ == "__main__":
    COUCH_DB = "rinr-2026-example"
    ALL_EVENTS = create_event_metadata_list(COUCH_DB)
    
    get_article_by_event(ALL_EVENTS)
    # get_articles_by_ppn()