from datetime import datetime, timezone
import json
import os
from utils import json_pretty_print
from load_data import main as load_eventmeta2DB


def make_utc_date(year, month, day):
    dt = datetime(int(year), int(month), int(day), tzinfo=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def literal_to_d_m_y(date_literal):
    # Example: "1940-01-21" -> (1940, 1, 21)
    year, month, day = date_literal.split("-")
    return int(year), int(month), int(day)

def create_meta_data(event):
    start_date = event.get("timeSpan_start", "")

    # NOTE: start_date is required!!!
    if not isinstance(start_date, str):
        return "NO START DATE FOUND!"
    year, month, day = literal_to_d_m_y(start_date)
    # NOTE: we are only using the start date for the meta data, but we could also use the end date if needed
    meta_data = {
        "id": event.get("id", ""),
        "title": event.get("title", ""),
        "timeSpan_start": event.get("timeSpan_start", ""),
        "timeSpan_end": event.get("timeSpan_start", ""),
        "date_y": year,
        "date_m": month,
        "date_d": day,
        "UTC_DATE": make_utc_date(year, month, day),
        "fulltext": event.get("description", ""),
        "entities": []
    }
    return meta_data

if __name__ == '__main__':
    COUCH_DB = "rinr-2026-example"
    

    DIRECTORY = 'example'
    with open(os.path.join(DIRECTORY, 'events.json'), 'r') as file:
        ALL_EVENTS = json.load(file)

    for event in ALL_EVENTS:
        # TODO: load to couch_db
        # store in a json file

        file_path = os.path.join(DIRECTORY, 'events_meta_temp.json')
        with open(file_path, 'w+') as file:
            data = create_meta_data(event)
            json_dumps_str = json.dumps(data, indent=4)
            file.write(json_dumps_str)
    


