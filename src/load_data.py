import requests
import argparse
import json
from typing import Optional, Dict, Any, List
from utils import load_json_file, is_json_array

class CouchDBClient:
    def __init__(self, server_url: str, db_name: str, auth: Optional[tuple] = None):
        self.server_url = server_url.rstrip('/')
        self.db_name = db_name
        self.url = f'{self.server_url}/{self.db_name}'
        self.auth = auth
        self.headers = {'Content-Type': 'application/json'}
    
    def create_document(self, doc_type, doc: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a single document and return response data or None on error."""
        try:
            doc['type'] = doc_type
            response = requests.post(self.url, json=doc, headers=self.headers, auth=self.auth)
            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f'Error {response.status_code}: {response.text}')
                return None
        except requests.RequestException as e:
            print(f'Request failed: {e}')
            return None
    
    def bulk_create(self, doc_type, documents: List[Dict[str, Any]]) -> int:
        """Create multiple documents and return count of successes."""
        success_count = 0
        for doc in documents:
            if result := self.create_document(doc_type, doc):
                print(f'Success - ID: {result["id"]}, Rev: {result["rev"]}\n')
                success_count += 1
        return success_count


def main(input_file: str, doc_type: str):
    # Configuration
    CONFIG = {
        'server_url': 'http://localhost:5984',
        'db_name': 'rinr-2026',
        'auth': ('admin', '123456'),
        'input_file': input_file
    }
    
    # Load data
    data = load_json_file(CONFIG['input_file'])
    if not data:
        return
    
    # Initialize client
    client = CouchDBClient(
        server_url=CONFIG['server_url'],
        db_name=CONFIG['db_name'],
        auth=CONFIG['auth']
    )
    
    # Process based on data type
    if is_json_array(data):
        print(f'Uploading {len(data)} documents...\n')
        success_count = client.bulk_create(doc_type,data)
        print(f'Completed: {success_count}/{len(data)} documents uploaded')
    else:
        print('Uploading single document...\n')
        result = client.create_document(doc_type, data)
        if result:
            print(f'Success - ID: {result["id"]}, Rev: {result["rev"]}')

if __name__ == '__main__':
    TYPE_CONFIG = {
        'event': ('--event', 'Load event data into CouchDB'),
        'event_metadata': ('--event_metadata', 'Load event metadata into CouchDB'),
        'article': ('--article', 'Load news article data into CouchDB'),
        'article_metadata': ('--article_metadata', 'Load news article metadata into CouchDB')
    }

    parser = argparse.ArgumentParser(description='Load JSON data into CouchDB')
    parser.add_argument('-i', '--input_file', help='Path to the JSON file to load')

    # Add flags dynamically
    for doc_type, (arg, help_text) in TYPE_CONFIG.items():
        parser.add_argument(arg, help=help_text, action='store_true', dest=doc_type)

    args = parser.parse_args()

    # Find which type was specified
    doc_type = next((t for t, v in vars(args).items() if v and t in TYPE_CONFIG), None)
    if doc_type:
        input_file = args.input_file        
        if not input_file:
            print('Input file is required. Use -i or --input_file to specify the JSON file.')
        else:
            # print(f'Loading {doc_type} data from {input_file}...')
            main(input_file, doc_type)
    else:
        print('No data type specified. Use -e, -em, -a, or -am.')
