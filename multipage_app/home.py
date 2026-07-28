import streamlit as st
import datetime
import sys, os
import subprocess

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
if "download_dir" not in st.session_state:
    st.session_state["download_dir"] = "../data"

event_title = st.text_input("Enter your historical event title", st.session_state["histEvent_title"])
# use a real date default and pass session_state key via keyword to avoid positional-after-keyword error
default_date = datetime.date(1700, 1, 1)
event_startDate = st.date_input("Enter the (possible) event start date", value="1800-01-01", min_value="1600-01-01", max_value="1950-01-01")
event_endDate = st.date_input("Enter the (possible) event end date", value="1900-01-01", min_value="1600-01-01", max_value="1950-01-01")

download_dir = st.text_input("Relative path for download directory", st.session_state["download_dir"])

submit = st.button("Submit")
if submit:
    st.session_state["histEvent_title"] = event_title
    st.session_state["histEvent_startDate"] = event_startDate
    st.session_state["histEvent_endDate"] = event_endDate
    # persist chosen download directory
    st.session_state["download_dir"] = download_dir

    import subprocess
    try:
        # determine output directory (handle absolute or relative paths)
        user_dir = st.session_state.get("download_dir", "../data")
        out_dir = user_dir if os.path.isabs(user_dir) else os.path.join(os.getcwd(), user_dir)
        completed = subprocess.run(
            [
                sys.executable,
                "../src/get_article_by_event.py",
                "--title",
                st.session_state["histEvent_title"],
                "--date_y",
                str(st.session_state["histEvent_startDate"].year),
                "--out_dir",
                out_dir,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        st.text("Script output:\n" + (completed.stdout or "(no output)"))
        if completed.stderr:
            st.text("Script errors:\n" + completed.stderr)
        if completed.returncode == 0:
            st.session_state["download_success"] = True
            st.success("✅ Download successfully completed!")
            st.balloons()
            st.warning(f"Script exited with code {completed.returncode}")
        else:
            st.session_state["download_success"] = False
    except Exception as e:
        st.session_state["download_success"] = False
        st.error(f"Failed to run script: {e}")

if st.session_state.get("download_success", False):
    if st.button("Show downloaded articles", key="show_articles"):
        st.switch_page("pages/show_artcle.py")