import os, sys, time
import requests
import lxml.etree


# retrieve the individual issue with the same PPN
URL = f'https://jsru.kb.nl/sru/sru?query=ppna=%s&version=1.2&operation=searchRetrieve&startRecord=1&maximumRecords=1&recordSchema=ddd&x-collection=DDD_krantnr&x-fields=ppna'
# e.g., https://jsru.kb.nl/sru/sru?query=ppna=832452025&version=1.2&operation=searchRetrieve&startRecord=1&maximumRecords=1&recordSchema=ddd&x-collection=DDD_krantnr&x-fields=ppna 

URL1 = f'https://jsru.kb.nl/sru/sru?query=ppna=%s&version=1.2&operation=searchRetrieve&startRecord=%s&maximumRecords=10&recordSchema=ddd&x-collection=DDD_krantnr&x-fields=ppna'

DIDL = 'https://services.kb.nl/mdo/oai?verb=GetRecord&identifier=%s&metadataPrefix=didl'

EVENT_BASED_URL = f"https://jsru.kb.nl/sru/sru?version=1.2&operation=searchRetrieve&x-collection=DDD_artikel&recordSchema=indexing&startRecord=1&maximumRecords=50&query=\"%s\" AND (date within \"%s %s\")"


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

def get_didl(dentifier):
    # TODO: store the retrieved didl in a local folder to avoid repeating identical requests
    return
    # url = DIDL % (prefix + identifier)
    # # e.g., url= https://services.kb.nl/mdo/oai?verb=GetRecord&identifier=DDD:ddd:010905171:mpeg21&metadataPrefix=didl

    # fname = 'data' + os.sep + identifier + '.xml'
    # fname = fname.replace(':', '_')

    # if not os.path.isfile(fname):
    #     resp = requests.get(url)
    #     # print(resp.content.decode('utf-8'))
    #     with open(fname, 'w') as fh:
    #         fh.write(resp.content.decode('utf-8'))

def get_didl(prefix, identifier, ppn):
    url = DIDL % (prefix + identifier)
    # e.g., url= https://services.kb.nl/mdo/oai?verb=GetRecord&identifier=DDD:ddd:010905171:mpeg21&metadataPrefix=didl

    if not os.path.isdir(ppn):
        os.mkdir(ppn)

    fname = ppn + os.sep + identifier + '.xml'
    fname = fname.replace(':', '_')

    if not os.path.isfile(fname):
        resp = requests.get(url)
        # print(resp.content.decode('utf-8'))
        with open(fname, 'w') as fh:
            fh.write(resp.content.decode('utf-8'))


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

event_set = [{"title": "expeditie naar bali", "fulltext": "Description of event 1", "date_y": 1906},
                {"title": "Expeditie naar Nias", "fulltext": "Description of event 2", "date_y": 1863},
                {"title": "Tapanahoni Expeditie", "fulltext": "Description of event 3", "date_y": 1904}]

def parse_resp_events(instr):
    data = lxml.etree.fromstring(instr)
    for i in data.iter():
        if i.tag == '{http://www.loc.gov/zing/srw/}numberOfRecords':
            total_nr_results = int(i.text)
            break
    # print(f"Total number of results: {total_nr_results}")

    # TODO: handle pagination if total_nr_results > 10
    for i in data.iter():
        if i.tag == '{http://purl.org/dc/elements/1.1/}identifier':
            identifier = i.text.split('=')[-1] # e.g., ddd:010905171:mpeg21
            # print(f"Identifier: {identifier}")
            get_didl(identifier)

def get_article_by_event(event_set):
    for event in event_set:
        title = event.get("title", "")
        fulltext = event.get("fulltext", "")
        date_y = event.get("date_y", "")
        # print(f"Title: {title}, Fulltext: {fulltext}, Date: {date_y}")
        url = EVENT_BASED_URL % (title, date_y-10, date_y+10)
        # print(url)
        
        resp = requests.get(url)
        parse_resp_events(resp.content)
        return

if __name__ == "__main__":
    # get_article_by_event(event_set)
    get_articles_by_ppn()