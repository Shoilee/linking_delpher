
import os
from lxml import etree
import xmltodict, json

def get_all_articles(root):
    articles_xml = root.findall('.//didl:Item[@ddd:article_id]', 
                                namespaces={
                                    'didl': 'urn:mpeg:mpeg21:2002:02-DIDL-NS', 
                                    'ddd': 'http://www.kb.nl/namespaces/ddd'
                                    }
                                )  
    # print(f"Found {len(articles_xml)} articles in the XML.")
    return articles_xml

if __name__ == '__main__':
    OUTPUT_DIR = 'data/DST'
    xml = etree.parse('data/DST_XML/ddd_000014853_mpeg21.xml')
    root = xml.getroot()
    
    articles_xml = get_all_articles(root)
    print(f"Processing {len(articles_xml)} articles...")

    for article in articles_xml:
        article_id = article.get('{http://www.kb.nl/namespaces/ddd}article_id')
        print(f"Processing article ID: {article_id}")
        
        xml_bytes = etree.tostring(article)        
        data = xmltodict.parse(xml_bytes)["didl:Item"]      
        
        # TODO: Add article OCRED text to data dict here

        output_path = f'{OUTPUT_DIR}/{article_id.replace(":", "_")}.json'
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
    