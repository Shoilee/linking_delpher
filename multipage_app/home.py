import streamlit as st
import datetime

st.set_page_config(
    page_title="Trace The Past",
    page_icon="⎋",
)

st.title("Trace The Past")
st.sidebar.success("Select a page above.")

if "histEvent_title" not in st.session_state:
    st.session_state["histEvent_title"] = ""
# date_input manages its own session_state when given a key; provide sensible defaults
if "histEvent_startDate" not in st.session_state:
    st.session_state["histEvent_startDate"] = None
if "histEvent_endDate" not in st.session_state:
    st.session_state["histEvent_endDate"] = None

event_title = st.text_input("Enter your event title", st.session_state["histEvent_title"])
# use a real date default and pass session_state key via keyword to avoid positional-after-keyword error
default_date = datetime.date(1700, 1, 1)
event_startDate = st.date_input("Enter the (possible) event start date", value="1600-01-01", min_value="1600-01-01", max_value="1950-01-01")
event_endDate = st.date_input("Enter the (possible) event end date", value="1900-01-01", min_value="1600-01-01", max_value="1950-01-01")

submit = st.button("Submit")
if submit:
    st.session_state["histEvent_title"] = event_title
    st.session_state["histEvent_startDate"] = event_startDate
    st.session_state["histEvent_endDate"] = event_endDate