import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone  # consolidated import
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import subprocess
import time
import os  # <-- Needed for shutdown marker
from docore_ai.init_engine import get_state

# Constants
CSV_PATH = "docoreai_log.csv"
# Find the project root relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # stays the same if show_app.py is in utils/
#CSV_PATH = os.path.join(BASE_DIR, "..", "docoreai_log.csv")
CSV_PATH = os.environ.get("DOCOREAI_USER_CWD", os.getcwd())
CSV_PATH = os.path.join(CSV_PATH, "docoreai_log.csv")

CSV_PATH = os.path.abspath(CSV_PATH)
CSV_PATH = os.path.join(os.path.dirname(__file__), "docoreai_log.csv")#29-Jul

LOGO_URL = "https://docoreai.com/wp-content/uploads/2025/05/cropped-DoCoreAI-Logo-1-300x100.png"
MAX_LOOKBACK_DAYS = 30
BUTTON_COLOR = "#F45A2A"
BACKGROUND_COLOR = "#f5f5f5"
ACCENT_COLOR = "#004cba"
TEXT_COLOR = "#f5f5f5"
HIGHLIGHT_COLOR = "#FFD700"  # Golden yellow

st.set_page_config(
    page_title="DoCoreAI Prompts Viewer",
    layout="wide",
)

# --- Custom CSS ---
# --- CSS ---
st.markdown("""
    <style>
    /* Change st.success background and text */
    .stAlert[data-testid="stAlert-success"] {
        background-color: #004cba !important; /* light green */
        color: #1c1c1c !important;
    }
    /* Change st.info background and text */
    .stAlert[data-testid="stAlert-info"] {
        background-color: #F45A2A !important; /* light blue */
        color: #1c1c1c !important;
    }
    </style>
""", unsafe_allow_html=True)

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
        st.markdown("<h2 style='margin-top:0'>Local Prompts Viewer (Beta)</h2>", unsafe_allow_html=True)
        st.markdown(
            "<p style='margin-top:0'>Analyze your local DoCoreAI logs. Records older than 30 days are automatically pruned.</p>"
            "<p><strong>We do not save your prompts on our server. </strong><br>These records are stored on your machine only. You are responsible for securing them locally.</p>",
            unsafe_allow_html=True
        )

# --- Sidebar Filters ---
st.sidebar.header("Search & Filter")

cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_LOOKBACK_DAYS)

try:
    df = pd.read_csv(CSV_PATH, parse_dates=['local_timestamp'])
except FileNotFoundError:
    st.error(f"CSV not found at {CSV_PATH}. Run some prompts first and check. If issue persists, this may be due to a write permission issue. Please contact info@docoreai.com for support")
    st.stop()

# Coerce timestamps and ensure UTC
df['local_timestamp'] = pd.to_datetime(df['local_timestamp'], errors='coerce')
if df['local_timestamp'].dt.tz is None:
    df['local_timestamp'] = df['local_timestamp'].dt.tz_localize('UTC', ambiguous='NaT', nonexistent='NaT')
else:
    df['local_timestamp'] = df['local_timestamp'].dt.tz_convert('UTC')

bad_rows = df[df['local_timestamp'].isna()]
if not bad_rows.empty:
    st.warning(f"⚠️ {len(bad_rows)} rows had invalid timestamps and were skipped:")
    st.dataframe(bad_rows[['client_prompt_id', 'local_timestamp']])

df = df.dropna(subset=['local_timestamp'])
df = df[df['local_timestamp'] >= cutoff]

# Permanently prune old records from CSV (UNCOMMENT to enable)
#df.to_csv(CSV_PATH, index=False)

if df.empty:
    st.error("No valid data recorded in CSV file (local) -  After installation / Last 30 days.")
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

state = get_state()
is_account_inactive = state.get("account_state") in ("activation_pending","inactive",)
if is_account_inactive:
    dprint("❌ Please verify your email & upgrade access")
    exit(1)

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

# --- Shutdown Button (added at the end) ---
#st.markdown("---")
#if st.button("Close View & Exit"):
#    st.warning("Shutting down the Telemetry Viewer...")
#    # --- Marker for parent wrapper to cleanly shutdown Streamlit ---
#    with open("shutdown.marker", "w") as f:
#        f.write("shutdown")
#    try:
#        st.stop()
#    except:
#        os._exit(0)