
import os
from lxml import etree
import xmltodict, json
import requests

def get_all_articles(root):
    articles_xml = root.findall('.//didl:Item[@ddd:article_id]', 
                                namespaces={
                                    'didl': 'urn:mpeg:mpeg21:2002:02-DIDL-NS', 
                                    'ddd': 'http://www.kb.nl/namespaces/ddd'
                                    }
                                )  
    # print(f"Found {len(articles_xml)} articles in the XML.")
    return articles_xml

def get_article_text(identifier):
    URI = f"http://resolver.kb.nl/resolve?urn={identifier}:ocr"
    print(f"Retrieving OCR text for identifier: {identifier}")
    req = requests.get(URI)
    if req.status_code == 200:
        root = etree.fromstring(req.text.encode('utf-8'))
        text_children = list(root)
        clean_xml_string = (''.join([etree.tostring(child, pretty_print=True).decode('utf-8') for child in text_children]))
        return clean_xml_string
    else:
        print(f"Failed to retrieve OCR text for identifier: {identifier}, status code: {req.status_code}")

if __name__ == '__main__':
    OUTPUT_DIR = 'data/DST'
    xml = etree.parse('data/DST_XML/ddd_000014853_mpeg21.xml')
    root = xml.getroot()
    
    articles_xml = get_all_articles(root)
    print(f"Processing {len(articles_xml)} articles...")

    for article in articles_xml:
        article_id = article.get('{http://www.kb.nl/namespaces/ddd}article_id')
        print(f"Processing article ID: {article_id}")

        text = get_article_text(article_id)
        
        xml_bytes = etree.tostring(article)        
        data = xmltodict.parse(xml_bytes)["didl:Item"]      

        # Add the retrieved OCR text to the data dictionary
        data['ocr_text'] = text

        output_path = f'{OUTPUT_DIR}/{article_id.replace(":", "_")}.json'
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
    