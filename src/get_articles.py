import os, sys, time
import requests
import lxml.etree


# retrieve the individual issue with the same PPN
URL = f'https://jsru.kb.nl/sru/sru?query=ppna=%s&version=1.2&operation=searchRetrieve&startRecord=1&maximumRecords=1&recordSchema=ddd&x-collection=DDD_krantnr&x-fields=ppna'
# e.g., https://jsru.kb.nl/sru/sru?query=ppna=832452025&version=1.2&operation=searchRetrieve&startRecord=1&maximumRecords=1&recordSchema=ddd&x-collection=DDD_krantnr&x-fields=ppna 

URL1 = f'https://jsru.kb.nl/sru/sru?query=ppna=%s&version=1.2&operation=searchRetrieve&startRecord=%s&maximumRecords=10&recordSchema=ddd&x-collection=DDD_krantnr&x-fields=ppna'

DIDL = 'https://services.kb.nl/mdo/oai?verb=GetRecord&identifier=%s&metadataPrefix=didl'

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


def get_didl(prefix, identifier, ppn):
    url = DIDL % (prefix + identifier)

    if not os.path.isdir(ppn):
        os.mkdir(ppn)

    fname = ppn + os.sep + identifier + '.xml'
    fname = fname.replace(':', '_')


    if not os.path.isfile(fname):
        resp = requests.get(url)
        print(resp.content.decode('utf-8'))
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
        if i.tag == '{http://www.kb.nl/ddd}metadataKey':
            if new_ppn:
                resp = requests.get(i.text)
                nurl = resp.url 
                prefix = nurl.split('=')[2].split('&')[0].replace(i.text.split('=')[-1], '')
            # print(prefix, i.text)
            identifier = i.text.split('=')[-1]
            get_didl(prefix, identifier, ppn)


if __name__ == "__main__":
    with open('../data/sample_PPNA.txt', 'r') as fh:
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