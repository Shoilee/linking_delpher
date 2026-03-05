import requests
import json



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
    DB_URL = 'http://admin:123456@localhost:5984/rinr-2026'  # Replace with your CouchDB URL and DB name
    # auth = ('admin', '123456')  # CouchDB credentials
    delete_all_by_type(DB_URL, 'event')
