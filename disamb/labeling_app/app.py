import streamlit as st
import pandas as pd
import datetime
from pathlib import Path

st.set_page_config(page_title="Entity Resolution Labeler", layout="wide")

# ==========================================
# 1. Initialize Session State
# ==========================================
if 'df' not in st.session_state:
    st.session_state.df = None
    st.session_state.blocks = []
    st.session_state.current_idx = 0
    st.session_state.reviewed_blocks = set()
    st.session_state.original_filename = "data.csv"

# ==========================================
# 2. Sidebar: File Upload & Export
# ==========================================
with st.sidebar:
    st.header("File Operations")
    uploaded_file = st.file_uploader("Upload candidates CSV", type=["csv"])
    
    if uploaded_file is not None and st.session_state.df is None:
        # Load the dataframe
        df = pd.read_csv(uploaded_file)
        
        # Ensure is_match column exists and is boolean
        if 'is_match' not in df.columns:
            df['is_match'] = False
        else:
            df['is_match'] = df['is_match'].fillna(False).astype(bool)

        # Ensure annotated column exists and is boolean.
        if 'annotated' not in df.columns:
            df['annotated'] = False
        else:
            df['annotated'] = df['annotated'].fillna(False).astype(bool)
            
        st.session_state.df = df
        st.session_state.blocks = df['name_id'].unique().tolist()
        st.session_state.current_idx = 0
        st.session_state.original_filename = uploaded_file.name
        
        # Infer already reviewed blocks from annotation state.
        labeled_ids = df[df['annotated'] == True]['name_id'].unique()
        st.session_state.reviewed_blocks.update(labeled_ids)
        st.rerun()

    # Save / Export Button
    if st.session_state.df is not None:
        st.divider()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = Path(st.session_state.original_filename).stem
        export_name = f"{base_name}_labeled_{timestamp}.csv"
        
        csv_data = st.session_state.df.to_csv(index=False)
        st.download_button(
            label="💾 Save Labeled File",
            data=csv_data,
            file_name=export_name,
            mime="text/csv",
            type="primary"
        )
        
        st.progress((len(st.session_state.reviewed_blocks) / len(st.session_state.blocks)) if len(st.session_state.blocks) > 0 else 0)
        st.caption(f"Reviewed {len(st.session_state.reviewed_blocks)} out of {len(st.session_state.blocks)} blocks")

# ==========================================
# 3. Main Labeling UI
# ==========================================
if st.session_state.df is not None:
    # Basic state variables
    blocks = st.session_state.blocks
    curr_idx = st.session_state.current_idx
    current_name_id = blocks[curr_idx]
    
    # Filter dataframe to the current block (keep index intact for updating later)
    mask = st.session_state.df['name_id'] == current_name_id
    block_df = st.session_state.df[mask]
    
    # Get the actual name for display purposes
    current_name = block_df['name'].iloc[0] if not block_df.empty else "Unknown"
    is_block_annotated = bool(block_df['annotated'].all()) if 'annotated' in block_df.columns and not block_df.empty else False
    status_badge = "Annotated" if is_block_annotated else "Skipped / Unannotated"

    st.title(f"Labeling Block: {curr_idx + 1} / {len(blocks)}")
    st.caption(f"Block status: **{status_badge}**")
    
    # -- Jump to ID controls --
    col_jump1, col_jump2 = st.columns([1, 4])
    with col_jump1:
        st.info(f"**Current name_id:**\n\n {current_name_id}")
    with col_jump2:
        jump_input = st.text_input("Jump to a specific name_id:", key="jump_input")
        if st.button("Go"):
            # Try to match data types (int vs string)
            target_id = jump_input
            if len(blocks) > 0 and isinstance(blocks[0], (int, float)):
                try: target_id = type(blocks[0])(jump_input)
                except ValueError: pass
                
            if target_id in blocks:
                st.session_state.current_idx = blocks.index(target_id)
                st.rerun()
            else:
                st.error("name_id not found in dataset.")

    st.subheader(f"Query Name: `{current_name}`")
    
    # -- Data Editor for the block --
    # Disable editing for all columns EXCEPT 'is_match'
    disabled_cols = [col for col in block_df.columns if col != 'is_match']
    
    column_order_start = ['is_match', 'name', 'candidate']
    column_order = column_order_start + [col for col in block_df.columns if col not in column_order_start]

    edited_block = st.data_editor(
        block_df,
        column_config={
            "is_match": st.column_config.CheckboxColumn("Is Match?", default=False)
        },
        disabled=disabled_cols,
        column_order=column_order,
        height="content",
        use_container_width=True,
        hide_index=True,
        key=f"editor_{current_name_id}" # Prevents weird caching issues between blocks
    )

    # -- Navigation & Action Functions --
    def save_current_state():
        st.session_state.df.update(edited_block)
        st.session_state.df.loc[mask, 'annotated'] = True
        st.session_state.df['annotated'] = st.session_state.df['annotated'].fillna(False).astype(bool)
        st.session_state.reviewed_blocks.add(current_name_id)

    def skip_current_example():
        st.session_state.df.update(edited_block)
        st.session_state.df.loc[mask, 'annotated'] = False
        st.session_state.df['annotated'] = st.session_state.df['annotated'].fillna(False).astype(bool)
        st.session_state.reviewed_blocks.add(current_name_id)

    def find_next_unlabeled(direction="forward"):
        step = 1 if direction == "forward" else -1
        idx = st.session_state.current_idx + step
        while 0 <= idx < len(blocks):
            if blocks[idx] not in st.session_state.reviewed_blocks:
                return idx
            idx += step
        return st.session_state.current_idx # Stay put if none found

    # -- Navigation Buttons --
    st.divider()
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

    with col1:
        if st.button("⏮️ Prev", use_container_width=True):
            if curr_idx > 0:
                st.session_state.current_idx -= 1
                st.rerun()

    with col2:
        if st.button("💾 Prev & Save", use_container_width=True, type="primary"):
            save_current_state()
            if curr_idx > 0:
                st.session_state.current_idx -= 1
                st.rerun()

    with col3:
        if st.button("💾 Next & Save", use_container_width=True, type="primary"):
            save_current_state()
            if curr_idx < len(blocks) - 1:
                st.session_state.current_idx += 1
                st.rerun()

    with col4:
        if st.button("Next ⏭️", use_container_width=True):
            if curr_idx < len(blocks) - 1:
                st.session_state.current_idx += 1
                st.rerun()

    with col5:
        if st.button("Prev Unlabeled", use_container_width=True):
            st.session_state.current_idx = find_next_unlabeled("backward")
            st.rerun()

    with col6:
        if st.button("Next Unlabeled", use_container_width=True):
            st.session_state.current_idx = find_next_unlabeled("forward")
            st.rerun()

    with col7:
        if st.button("Skip Example", use_container_width=True):
            skip_current_example()
            if curr_idx < len(blocks) - 1:
                st.session_state.current_idx += 1
            st.rerun()

else:
    st.info("👈 Please upload a CSV file in the sidebar to begin labeling.")