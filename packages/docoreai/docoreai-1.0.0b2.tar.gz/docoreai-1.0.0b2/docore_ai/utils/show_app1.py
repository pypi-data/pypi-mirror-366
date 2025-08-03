import os
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import subprocess
import time

# Constants
CSV_PATH = "docoreai_log.csv"
LOGO_URL = "https://docoreai.com/wp-content/uploads/2025/05/cropped-DoCoreAI-Logo-1-300x100.png"
MAX_LOOKBACK_DAYS = 30
BUTTON_COLOR = "#f45827"
BACKGROUND_COLOR = "#f5f5f5"
ACCENT_COLOR = "#277ef7"
TEXT_COLOR = "#f5f5f5"
HIGHLIGHT_COLOR = "#FFD700"  # Golden yellow

st.set_page_config(
    page_title="DoCoreAI Telemetry Viewer",
    layout="wide",
)

# --- Custom CSS ---
st.markdown(f"""
    <style>
    body .main .block-container {{
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_COLOR};
        max-width: 1400px;
        padding: 2rem;
    }}
    h1, h2, h3, h4, h5, h6 {{ color: {TEXT_COLOR}; margin-bottom: 0.5rem; }}
    p, .stMarkdown {{ color: {TEXT_COLOR}; font-size: 1rem; margin-bottom: 1rem; }}
    .stButton>button {{
        background-color: {BUTTON_COLOR} !important;
        color: white !important;
        border-radius: 0.5rem;
        padding: 0.6rem 1.2rem;
    }}
    input[type="date"] {{
        color: {HIGHLIGHT_COLOR} !important;
    }}
    .ag-theme-streamlit {{
        --ag-header-background-color: {ACCENT_COLOR};
        --ag-header-foreground-color: white;
        --ag-row-hover-color: {BUTTON_COLOR}22;
    }}
    </style>
""", unsafe_allow_html=True)

# --- Header with Branding ---
with st.container():
    cols = st.columns([1, 5])
    with cols[0]:
        try:
            resp = requests.get(LOGO_URL, timeout=3)
            if resp.status_code == 200:
                st.image(LOGO_URL, use_container_width=True)
            else:
                st.markdown("<h1><strong>DoCoreAI</strong></h1>", unsafe_allow_html=True)
        except Exception:
            st.markdown("<h1><strong>DoCoreAI</strong></h1>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown("<h2 style='margin-top:0'>Local Telemetry Viewer (Beta)</h2>", unsafe_allow_html=True)
        st.markdown(
            "<p style='margin-top:0'>Analyze your local DoCoreAI logs. Records older than 30 days are automatically pruned.</p>"
            "<p>We do not save your prompts on our server. These records are stored on your machine only. You are responsible for securing them locally.</p>",
            unsafe_allow_html=True
        )

# --- Sidebar Filters ---
st.sidebar.header("Search & Filter")

#cutoff = datetime.utcnow() - timedelta(days=MAX_LOOKBACK_DAYS) old code
cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_LOOKBACK_DAYS)


try:
    df = pd.read_csv(CSV_PATH, parse_dates=['local_timestamp'])
except FileNotFoundError:
    st.error(f"CSV not found at {CSV_PATH}. Run some prompts first.")
    st.stop()

# Coerce timestamps
df['local_timestamp'] = pd.to_datetime(df['local_timestamp'], errors='coerce')
bad_rows = df[df['local_timestamp'].isna()]
if not bad_rows.empty:
    st.warning(f"⚠️ {len(bad_rows)} rows had invalid timestamps and were skipped:")
    st.dataframe(bad_rows[['client_prompt_id', 'local_timestamp']])

df = df.dropna(subset=['local_timestamp'])
df = df[df['local_timestamp'] >= cutoff]

if df.empty:
    st.error("No valid telemetry data in the last 30 days.")
    st.stop()

# --- Single Date Filter ---
max_date = df['local_timestamp'].dt.date.max()
selected_date = st.sidebar.date_input(
    "Select Date",
    value=max_date,
    min_value=max_date - timedelta(days=MAX_LOOKBACK_DAYS),
    max_value=max_date
)
df = df[df['local_timestamp'].dt.date == selected_date]

# --- Other Filters ---
client_id = st.sidebar.text_input("Client Prompt ID")
if client_id:
    df = df[df['client_prompt_id'].astype(str).str.contains(client_id)]

user_id = st.sidebar.text_input("User ID")
if user_id:
    df = df[df['user_id'].astype(str).str.contains(user_id)]

models = ["Any"] + sorted(df['model_name'].dropna().unique().tolist())
model_select = st.sidebar.selectbox("Model Name", models)
if model_select != "Any":
    df = df[df['model_name'] == model_select]

success_only = st.sidebar.checkbox("Only Successful Runs")
if success_only:
    df = df[df['success'] == 1]

st.sidebar.markdown("---")
export_csv = df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    "Export Filtered Data",
    data=export_csv,
    file_name="telemetry_filtered.csv",
    mime='text/csv'
)

# --- Main Content ---
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("Telemetry Records")
st.caption(f"{len(df)} records on {selected_date}")

if not df.empty:
    st.write("✅ Click a row in the table to view its Prompt and Response below.")

    # AgGrid setup
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_selection('single', use_checkbox=True)
    gb.configure_default_column(
    groupable=True,
    value=True,
    enableRowGroup=True,
    editable=False,
    resizable=True,
    #wrapText=True,
    autoHeight=True,
    flex=1
)    
    gb.configure_grid_options(domLayout='autoHeight')
    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=500,
        theme="streamlit",
        fit_columns_on_grid_load=True
    )
    selected_df = pd.DataFrame(grid_response['selected_rows'])
    if not selected_df.empty:
        row = selected_df.iloc[0]
        st.success(f"✅ Selected Record: Client ID {row.get('client_prompt_id', '')}")
        st.markdown("**Prompt:**")
        st.code(row.get('user_message', ''), language='markdown')
        st.markdown("**Response:**")
        st.code(row.get('response', ''), language='markdown')
    else:
        st.info("ℹ️ Select a row in the table above to view details.")
else:
    st.warning("No records match your filters.")
# --- Shutdown Button ---
st.markdown("---")
if st.button("❌ Close View / Shutdown"):
    st.warning("Shutting down the Telemetry Viewer...")
    st.stop()
    os._exit(0)    
