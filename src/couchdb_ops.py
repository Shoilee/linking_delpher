import requests
import argparse



def delete_all_by_type(db_url, doc_type):
    """Delete all documents where type == doc_type using Mango query + bulk delete."""
    
    # Step 1: Find all documents with matching type (use selector for efficiency)
    selector = {"type": f"{doc_type}"}  # Matches docs where 'type' field equals doc_type

    # Matches docs missing the 'type' field entirely
    # selector = {"type": {
    #         "$exists": False  
    #     }} 
    find_url = f"{db_url}/_find"
    
    response = requests.post(find_url, json={"selector": selector, "fields": ["_id","_rev"]}, headers={"Content-Type": "application/json"})
    if response.status_code != 200:
        print(f"Query failed: {response.text}")
        return
    
    docs = response.json().get('docs', [])
    print(f"Found {len(docs)} documents to delete")
    
    if not docs:
        print("No documents found")
        return
    
    # Step 2: Prepare bulk update docs with _deleted: true
    bulk_docs = [{"_id": d["_id"], "_rev": d["_rev"], "_deleted": True} for d in docs]
    
    # TODO: for some reason it only deletes 25 documents, even though there are more than 25 documents with type type. Maybe we need to do it in batches of 25?
    # Step 3: Bulk delete (logical delete)
    bulk_url = f"{db_url}/_bulk_docs"
    bulk_response = requests.post(bulk_url, json={"docs": bulk_docs})
    
    if bulk_response.status_code in [201, 202]:
        results = bulk_response.json()
        ok_count = sum(1 for r in results if r.get('ok'))
        print(f"Successfully deleted {ok_count}/{len(bulk_docs)} documents")
    else:
        print(f"Bulk delete failed: {bulk_response.text}")

if __name__ == '__main__':
    arguments = argparse.ArgumentParser()
    arguments.add_argument('-db', '--database', help='CouchDB URL', required=False)
    arguments.add_argument('-t', '--type', help='Document type to delete, e.g., "event" or "article"', required=True)
    args = arguments.parse_args()

    COUCH_DB = args.database if args.database else "rinr-2026"
    DOC_TYPE = args.type 

    DB_URL = f'http://admin:123456@localhost:5984/{COUCH_DB}'
    # auth = ('admin', '123456')  # CouchDB credentials
    delete_all_by_type(DB_URL, DOC_TYPE)
