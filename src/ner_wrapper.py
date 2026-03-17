from flask import Flask, Response
import requests
import json

app = Flask(__name__)

@app.route('/')
def index():
    return 'Welcome to the NER wrapper API!'

def extract_ocr_text(response_json):
    docs = response_json.get("docs", [])
    if not docs:
        return ""

    first_doc = docs[0]
    return first_doc.get("ocr_text", "")

def check_ocr_quality(ocr_text):
    # handle error: missing target, HTTP errors, empty text
    if not ocr_text:
        return False
    if len(ocr_text) < 50:  # Example threshold for bad OCR
        return False
    # check (Zipf-ish heuristic) fraction of characters that are in abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.
    alpha_chars = sum(1 for c in ocr_text if c.isalpha())
    alpha_ratio = alpha_chars / len(ocr_text) if ocr_text else 0
    if alpha_ratio < 0.6:  # Example threshold for bad OCR
        return False
    return ocr_text 

@app.route("/dst_meta/<target_id>/ocr_text")
def get_text_from_framework(target_id:int):
    data_host = "http://127.0.0.1:5000/"
    url = f"{data_host}dst/{target_id}"

    response = requests.get(url, headers={"Accept": "application/json"}, timeout=5)

    if response.status_code != 200:
        print(f"Error fetching text: {response.text}")
        return None
    json_response = json.loads(response.content.decode('utf-8'))
    return extract_ocr_text(json_response)

if __name__ == '__main__':
    app.run(debug=True, port=5001)



# TODO: fetch the text from the framework app
# TODO: handle error: missing target, HTTP errors, empty text.
# TODO: Implement OCR sanity check (Zipf-ish heuristic)
# TODO: Call the actual NER engine
# TODO: Normalise NER results into required format; 
#           ners/tokens: list of unique entity strings [ "A", "B", "C", "D" ]. 
#           ner_extended: list of dicts like: {"text": "A", "type": "ORG", "start_pos": 10, "end_pos": 12}       
# TODO: Build and return the JSON response
        # {
        #   "ocr_bad": false,
        #   "ners": ["A", "B", "C", "D"],
        #   "ner_extended": [
        #     {"text": "A", "type": "ORG", "start_pos": 10, "end_pos": 12},
        #     ...
        #   ]
        # }
 