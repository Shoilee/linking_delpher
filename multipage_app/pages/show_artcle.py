import os
import json
import streamlit as st

st.set_page_config(
    page_title="Article Browser",
    page_icon="📄",
    layout="wide"
)

st.sidebar.success("Select a page above.")

st.title("Article Browser")

download_dir = st.session_state.get("download_dir", "../data")
FOLDER = os.path.join(download_dir, "DST")

if not os.path.isdir(FOLDER):
    st.error(f"No download folder found at {FOLDER}")
    st.stop()

page_size = 50
if "article_page" not in st.session_state:
    st.session_state["article_page"] = 0
if "selected_article" not in st.session_state:
    st.session_state["selected_article"] = None


def refresh_article_files():
    files = sorted(
        f for f in os.listdir(FOLDER)
        if f.lower().endswith(".json")
    )
    total_pages = max(1, (len(files) + page_size - 1) // page_size)

    if st.session_state["article_page"] >= total_pages:
        st.session_state["article_page"] = total_pages - 1

    if files:
        if st.session_state.get("selected_article") not in files:
            st.session_state["selected_article"] = files[0]
    else:
        st.session_state["selected_article"] = None

    return files, total_pages


files, total_pages = refresh_article_files()

if not files:
    st.info("No JSON files were found in the selected download folder.")
    st.stop()

start_idx = st.session_state["article_page"] * page_size
end_idx = start_idx + page_size
page_files = files[start_idx:end_idx]

left_col, right_col = st.columns([1, 2])

with left_col:
    st.subheader("Files")
    for filename in page_files:
        select_col, delete_col = st.columns([4, 1])
        with select_col:
            if st.button(
                filename,
                key=f"article_{filename}",
                use_container_width=True,
                type="secondary" if st.session_state.get("selected_article") != filename else "primary",
            ):
                st.session_state["selected_article"] = filename
        with delete_col:
            if st.button(
                "🗑",
                key=f"delete_{filename}",
                help=f"Delete {filename}",
                use_container_width=True,
            ):
                file_path = os.path.join(FOLDER, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                refresh_article_files()
                st.rerun()

    st.caption(f"Page {st.session_state['article_page'] + 1} of {total_pages}")
    prev_col, next_col = st.columns(2)
    with prev_col:
        if st.button("◀ Previous", disabled=st.session_state["article_page"] == 0):
            st.session_state["article_page"] = max(0, st.session_state["article_page"] - 1)
    with next_col:
        if st.button("Next ▶", disabled=st.session_state["article_page"] >= total_pages - 1):
            st.session_state["article_page"] = min(total_pages - 1, st.session_state["article_page"] + 1)

with right_col:
    selected = st.session_state.get("selected_article")
    if not selected:
        st.info("Select a file from the list to view its contents.")
    else:
        st.subheader(f"Contents of {selected}")
        file_path = os.path.join(FOLDER, selected)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        st.json(data)