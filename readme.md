It's pointers all the way down..

SRC is what is, but must be addressable from your framework,

SRC_meta is the enriched and parsed SRC so we have distinct properties, we store this in NOSQL,
         since we do not have a uniform idea what kind of fields we will attach, we want
         max flexibiliry per record and iteration,
         so our db-schema does not hold us back from adding new fields on the fly.

DST is the list of newspapers that are within your target SRU-query (all of them).

DST_meta is the enriched and parsed DST (newspaper) same as before with parsed an distinct properties,
         and like before stored in NOSQL backend. 
         Make this lazy loading, when you first requests dst_meta/1 it has to fetch the initial data from dst,
         do the processings / ner / date_formatting ect., store results and display,
         next time just show stored result.


ENT is a copy of wikidata entities, so we can reference to this from both sides,
    full dump of .nl avail, also handy if we can address this from our own framework.

ENT_meta is where we have the parsed per record info.

==

  SRC_meta (event) has entries from ENT

  http://framework/src/1 (Just the event)
  http://framework/src_meta/1 (Event + seperated in properties, enrichment (e.g. links to ENT) on the fly, or prefered stored).


  DST_meta (newspaper_article) has enries from ENT
  http://framework/dst/1 (Just a newspaper, fulltext)
  http://framework/dst_meta/1 (Nespapers sperated in properties, enrichment (e.g. links to ENT) on the fly, or prefered stored).
  http://framework/dst_meta/1/fulltext (Nespapers sperated in properties, enrichment (e.g. links to ENT) on the fly, or prefered stored).
  http://framework/dst_meta/1/entities_raw (Nespapers sperated in properties, enrichment (e.g. links to ENT) on the fly, or prefered stored).
  http://framework/dst_meta/1/entities_linked (Nespapers sperated in properties, enrichment (e.g. links to ENT) on the fly, or prefered stored).

  At this point we can make a disambig search index.

  We start just indexing all src_meta and dst_meta in seperate indexes (Solr or Elasticserch),
   as well as ENT itself.

 And the final stage the disambig software can now traverse each event in de db, and use the indexes to make matches or at least come up with a nice candidate list.


==


SRC -> Events  / 1 /  Example: "Zes de Elfstedentocht, Op 30 januari 1940 werd de zesde Elfstedentocht verreden.  Afgelastingen Oorspronkelijk zou de zesde Elfstedentocht op 21 december 1939 verreden worden. Het ijs was goed, en het leek er ook niet op dat het snel ging dooien. De sneeuwval was echter zo hevig dat de tocht verschillende keren moest worden uitgesteld. Een plan om werklozen als werkverschaffing te laten schoonmaken kreeg weinig weerklank in Den Haag. Toen men eindelijk dankzij een donatie van Koningin Wilhelmina het tweehonderd kilometer lange traject sneeuwvrij gemaakt had, zette de dooi plotseling in. Toen in het nieuwe jaar de vorst opnieuw inzette, werd de organisatie voor de tocht alweer snel op touw gezet. Op 15 januari zouden de Elfstedenschaatsers van start gaan, ware het niet dat de dooi opnieuw roet in het eten gooide. Uiteindelijk kon de Tocht der Tochten op 30 januari toch doorgaan. 21 december 1939 "

SRC_meta -> Events / parsed,
            and addressable and enriched (if needed).

            1 / Example:
                full_text: "Op 30 januari 1940 werd de zesde Elfstedentocht verreden.  Afgelastingen Oorspronkelijk zou de zesde Elfstedentocht op 21 december 1939 verreden worden. Het ijs was goed, en het leek er ook niet op dat het snel ging dooien. De sneeuwval was echter zo hevig dat de tocht verschillende keren moest worden uitgesteld. Een plan om werklozen als werkverschaffing te laten schoonmaken kreeg weinig weerklank in Den Haag. Toen men eindelijk dankzij een donatie van Koningin Wilhelmina het tweehonderd kilometer lange traject sneeuwvrij gemaakt had, zette de dooi plotseling in. Toen in het nieuwe jaar de vorst opnieuw inzette, werd de organisatie voor de tocht alweer snel op touw gezet. Op 15 januari zouden de Elfstedenschaatsers van start gaan, ware het niet dat de dooi opnieuw roet in het eten gooide. Uiteindelijk kon de Tocht der Tochten op 30 januari toch doorgaan."
                title: "Zesde Elfstedentocht"
                date_m: 01
                date_y: 1939
                date_d: 21
                UTC_DATE: 1939-01-21:00:00:00Z
                entities: set(Q150747, Q???) 


DST is just a huge Python3 set (A single list) with all identifiers that are potential targets.

DST -> Papers / 1 / [ MMUTRA04:253396087:mpeg21:a00029 , kdsaksad, dsasad] [0,1]


                full_text: "<text> <title>Er is nog niet veel leven in de scheepvaart</title> <p> Doch het begint langzaam te komen Waal, Oude Maas en Dordtsche Kil worden opengebroken Waterweg Rotterdam en Amsterdam is open </p> <p> 
                <dc:date>1938/12/25 00:00:00</dc:date>
                    <dc:identifier>
                    http://resolver.kb.nl/resolve?urn=ddd:110579079:mpeg21:a0211:ocr
                </dc:identifier>
                <dc:publisher>Dagblad De Telegraaf</dc:publisher>
                <dc:source>KB C 98</dc:source>
                <dc:title>
                REEDS 600 DEELNEMERS VOOR DEN ELFSTEDENTOCHT. Friesland valt van de eene verbazing in de andere.
                </dc:title>
                <dc:type>artikel</dc:type>
                <dcx:DelpherPublicationDate>Wed Nov 20 01:00:00 CET 2013</dcx:DelpherPublicationDate>
                <dcx:issued>1893</dcx:issued>  


DST_papers_meta -> Papers / parsed, and addressable and enriched.

DST_papers_meta / 1 /  fulltext: 
                        Er is nog niet veel leven in de scheepvaart Doch het begint langzaam te komen Waal, Oude Maas en Dordtsche Kil worden opengebroken Waterweg Rotterdam en Amsterdam is open ...
                       title: Er is nog niet veel leven in de scheepvaart.

                 1 / paragraph_1: Doch het begint langzaam...
                 1 / utc_date: 1939-01-21:00:00:00z
                 1 / publisher: "Dagblad De Telegraaf"
                 1 / entities: [Q150747, ...]
                 1 / entities_raw:  


===

Tue Feb 17 09:35:55 AM CET 2026

Thoughts on expanding and making it work,

A) 


Getting the dst-set / newspaper id's complete, 

U can use PPN's to get complete newspaper-titles. I've added some example code,
still needs some work for your goals, but it uses PPN's as identifiers for complete
newspaper-titles.

You can iter over SRU results using the startRecord parameter,
(so the first request is just fetching the expexed nr of results (maxrecords=1),
and then in a loop fetch all identifiers and dates (maxrecords=10), store them on disk.




B)

build a second Flask app, this time it will be a NER-wrapper,
before passing text to the actual NER-engine, do a quick sanity check,
so the response of the app will be something like:

ocr_bad: Flase
ners: [A, B, C, D]
ner_extended: [ {"A", type: ORG, start_pos, end_pos}, {"B", .. ]


We'll re-use the http://framework/ url's as request parameters to the http://ner/ app,  
in this form: http://ner/?target=dst_meta/1/fulltext, and get our response.

(Use the python3 lib - requests for this, and to get a quick measure on how 'correct' an OCR is,
some hacky rudementary implementation of a zipf's law will do..

so how manny of the total char as a percentage of the text are in:
>>> string.ascii_letters
'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
?


C)

Start implementing the cache-mechanism in the http://framework app,
we'll use NOSQL-couchdb for this.  https://couchdb.apache.org/

This might look like overkill for what we are doing,
but we'll use only 1% of the whole package,
so you only have to understand the verry basics of the CouchDB-engine,
for we'll only use it as a 'dumb-cache' system,
so we do not have to write complex nosql-queries,

just get the basics up and running, add, delete and mutate (a value) in a document.

So we can use this to store the results of the more 'expensive' operations, like NER-results.



D)

Start exploring the wiki-data set, we'll use this as a gazetter later on to match our NER's, 
well store the records in SOLR later, but first look at the set a bit more in depth,
to see if we can make a pre-selection of things we want and things we want to ignore.

To work with wiki-data dumps is quite the task, since the compressed +/- 300 MB json dumps,
are not easy to work with and, is not quite in the form we want it to be,
since it's auto-generated semi-structured data, we'll have to be carefull with assumptions and look at the data itself.

(there are things like IS_PLACE, IS_HISTORICAL_PLACE, IS_PERSON expressed as Q-facts,
we can ignore most of the entires, but some need special treatment, 
for example, I'm unsure how re-direction pages are handled in wikidata,
and they do contain alternative labels for exising entities..
https://nl.wikipedia.org/wiki/Best_(doorverwijspagina)


some code for this could look like this:




*/


https://www.wikidata.org/wiki/Wikidata:Database_download/nl

https://jsru.kb.nl/sru/sru?version=1.2&operation=searchRetrieve&x-collection=DDD_artikel&recordSchema=indexing&startRecord=1&maximumRecords=50&query=(date within "1938 1939") AND Wilhelmina AND Elfstedentocht

https://jsru.kb.nl/sru/sru?query=ppna=45136599&version=1.2&operation=searchRetrieve&x-collection=DDD_artikel&recordSchema=indexing&startRecord=1&maximumRecords=50

*/
                    
```pyhton                
import os, sys, time
import requests
import lxml.etree



URL = f'https://jsru.kb.nl/sru/sru?query=ppna=%s&version=1.2&operation=searchRetrieve&startRecord=1&maximumRecords=1&recordSchema=ddd&x-collection=DDD_krantnr&x-fields=ppna'


URL1 = f'https://jsru.kb.nl/sru/sru?query=ppna=%s&version=1.2&operation=searchRetrieve&startRecord=%s&maximumRecords=10&recordSchema=ddd&x-collection=DDD_krantnr&x-fields=ppna'

DIDL = 'https://services.kb.nl/mdo/oai?verb=GetRecord&identifier=%s&metadataPrefix=didl'

# /mdo/oai?
# https://services.kb.nl/mdo/oai?verb=GetRecord&identifier=KRANTEN:KBNRC01:KBNRC01:000028900:mpeg21&metadataPrefix=didl

prev_ppn = ''
prefix = ''

respbuff = []

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
            #print(prefix, i.text)
            identifier = i.text.split('=')[-1]
            get_didl(prefix, identifier, ppn)


with open('506_PPNA.txt', 'r') as fh:
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
```