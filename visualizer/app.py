## A basic streamlit app for visualizing NER results, using spacy_streamlit

import streamlit as st
import spacy
from spacy.tokens import Span
import spacy_streamlit
from spacy_streamlit import visualize_ner, visualize_spans

from pathlib import Path
import io
import ast

import pandas as pd

# Get file path of the current script
FILE_PATH = Path(__file__).resolve()

st.session_state['nlp'] = spacy.blank("nl")
# st.session_state['nlp'].add_pipe("ner")

default_labels = ["PER", "LOC", "ORG"]
default_colors = {
    "PER": "#7aecec",
    "LOC": "#22c705",
    "ORG": "#feca74",
}

# On the side bar should be an upload button for a csv file with 'filename', 'paragraph', 
# 'person', 'geographic location', 'organization'
# It has one line per paragraph, with the filename indicating the source document. 
# The entity columns contain lists of entities found in the paragraph.

example_csv = """filename,paragraph,person,geographic location,organization
MMHCO01_000065498_mpeg21_a0001.json,De heer van Meeuwen bespreekt de klagten over de aansluiting der treinen en de verzwaring vau den Waaldijk.,"[{'start': 0, 'end': 19, 'text': 'De heer van Meeuwen', 'label': 'persoon', 'score': 0.971204936504364}]","[{'start': 98, 'end': 106, 'text': 'Waaldijk', 'label': 'locatie', 'score': 0.5981191396713257}]",[]
"""

def create_doc(row):

    nlp = st.session_state['nlp']
    text = row['paragraph']

    doc = nlp(text)

    # Create single list with all entities and their labels
    input_spans = row[st.session_state['entity_cols']].explode().dropna().to_list()

    # Convert start and end character offsets to token offsets (i.e. token indices)
    output_spans = []
    labels = set()
    for span in input_spans:
        label = span['label'][:3].upper()
        labels.add(label)

        token_span = doc.char_span(span['start'], span['end'], label=label)
        output_spans.append(token_span)

    # doc.spans["sc"] = output_spans
    doc.ents = output_spans

    if not labels:
        labels = default_labels
    st.session_state['ner_labels'] = list(labels)

    return doc



st.title("NER Visualization")


with st.sidebar:
    st.title("NER Visualizer")
    st.markdown(
        """
        This is a simple app for visualizing Named Entity Recognition (NER) results.
        Upload a CSV file with the following columns:
        - filename: The source document filename
        - paragraph: The text of the paragraph
        - person: List of person entities found in the paragraph
        - geographic location: List of geographic location entities found in the paragraph
        - organization: List of organization entities found in the paragraph
        """
    )
    # Add dropdown list with csv files in the data folder
    csv_files = FILE_PATH.parent / "data"
    csv_files = csv_files.glob("*.csv")
    selected_file = st.selectbox("Select a CSV file from the data folder", [f.name for f in csv_files])
    if selected_file:
        st.session_state['df'] = pd.read_csv(FILE_PATH.parent / "data" / selected_file, encoding="utf-8-sig")

    else:
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded_file is not None:
            st.session_state['df']  = pd.read_csv(uploaded_file, encoding="utf-8-sig")
            # Save the uploaded file to the data folder
            with open(FILE_PATH.parent / "data" / uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())
        else:
            st.info("Using example data. Upload your own CSV to visualize your NER results.")
            st.session_state['df']  = pd.read_csv(io.StringIO(example_csv))


    # Add option to select the entity columns
    non_entity_cols = ['filename', 'paragraph']
    entity_options = [col for col in st.session_state['df'].columns.tolist() if col not in non_entity_cols]
    st.session_state['entity_cols'] = st.multiselect(
        "Select entity columns", 
        options=entity_options, 
        default=entity_options
        )
    
    st.session_state['df'][st.session_state['entity_cols']] = st.session_state['df'][st.session_state['entity_cols']].map(ast.literal_eval)



# # Initialize selected row index once
# if "row_index" not in st.session_state:
#     st.session_state["row_index"] = 0 # int(st.session_state["df"].index[0])

# # Keep row_index valid when dataframe changes
# max_index = len(st.session_state["df"]) - 1
# st.session_state["row_index"] = max(0, min(st.session_state["row_index"], max_index))

# # Selectbox uses the same state key
# st.selectbox(
#     "Select a row to visualize",
#     st.session_state["df"].index,
#     key="row_index",
#     format_func=lambda x: str(x) + ": " + st.session_state["df"].loc[x, "paragraph"][:70] + " [...]",
# )

# # Navigation controls all update the same key
# col1, col2, col3 = st.columns(3)

# with col1:
#     if st.button("Previous") and st.session_state["row_index"] > 0:
#         st.session_state["row_index"] -= 1
#         st.rerun()

# with col2:
#     if st.button("Next") and st.session_state["row_index"] < max_index:
#         st.session_state["row_index"] += 1
#         st.rerun()

# with col3:
#     jump_index = st.number_input(
#         "Jump to row index",
#         min_value=0,
#         max_value=max_index,
#         value=int(st.session_state["row_index"]),
#         step=1,
#     )
#     st.session_state["row_index"] = int(jump_index)

#     row_index = st.selectbox(
#         "Select a row to visualize",
#         st.session_state["df"].index,
#         index=int(st.session_state["row_index"]),
#         format_func=lambda x: str(x) + ": " + st.session_state["df"].loc[x, "paragraph"][:70] + " [...]",
#     )

if "selected_row" not in st.session_state:
    row_index = 0
    st.session_state["row_index"] = int(row_index)
    st.session_state["selected_row"] = st.session_state["df"].loc[st.session_state["row_index"]]
# Add dropdown to select a row from the dataframe, with the paragraph as the label



doc = create_doc(st.session_state['selected_row'])
visualize_ner(
    doc, 
    labels=st.session_state['ner_labels'], 
    show_table=True, 
    # title="NER Visualization"
    colors=default_colors
    
)


row_index = st.selectbox(
    "Select a row to visualize", 
    st.session_state['df'].index, 
    format_func=lambda x: str(x) + ": " + st.session_state['df'].loc[x, "paragraph"][:70] + " [...]"
    )


st.session_state['selected_row'] = st.session_state['df'].loc[row_index] 


# visualize_spans(
#     doc,
#     spans_key="sc",
# )