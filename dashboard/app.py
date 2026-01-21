import streamlit as st
import pandas as pd
import glob
import os
import subprocess
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="VSA Daily Dashboard", layout="wide")

# --- CUSTOM CSS FOR "WOW" FACTOR ---
st.markdown("""
    <style>
    .big-font { font-size:20px !important; }
    h1 { color: #4F8BF9; }
    h2 { color: #FF4B4B; }
    .status-box { padding: 10px; border-radius: 5px; background-color: #f0f2f6; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🚀 VSA Agentic Screener Dashboard")
st.markdown("Daily analysis of Volume Spread Analysis signals, highlighting high-confidence Smart Money setups.")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Controls")
if st.sidebar.button("🔄 Pull Latest Data (Git Pull)"):
    with st.spinner("Pulling latest reports from GitHub..."):
        try:
            # Assumes running from root of repo or dashboard dir
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            result = subprocess.run(["git", "pull"], cwd=root_dir, capture_output=True, text=True)
            if result.returncode == 0:
                st.sidebar.success("Updated successfully!")
            else:
                st.sidebar.error(f"Git pull failed: {result.stderr}")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

# --- DATA LOADING ---
@st.cache_data(ttl=300) # Cache for 5 mins
def load_latest_report():
    # Reports are in ../reports/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report_dir = os.path.join(base_dir, "reports")
    
    csv_files = glob.glob(os.path.join(report_dir, "REPORT_*.csv"))
    if not csv_files:
        return None, None
    
    # Sort by date (filename)
    latest_file = max(csv_files, key=os.path.getctime)
    df = pd.read_csv(latest_file)
    return df, os.path.basename(latest_file)

df, filename = load_latest_report()

# --- AGGRID HELPER ---
def show_aggrid(df, key):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)
    # Enable Enterprise to get 'Set' filters (Excel-style dropdowns)
    # Note: This may show a console warning about license key, acceptable for local personal use.
    gb.configure_default_column(editable=False, groupable=True, filterable=True, sortable=True, resizable=True)
    
    # Configure specific columns for Set Filtering (Dropdowns)
    categorical_cols = ['Ticker', 'Priority', 'Action', 'Monthly_Context', 'Weekly_Context', 'Weekly_Signal']
    for col in categorical_cols:
        if col in df.columns:
            gb.configure_column(col, filter="agSetColumnFilter")
            
    gb.configure_column("Current_Price", type=["numericColumn", "numberColumnFilter"], precision=2)
    
    gridOptions = gb.build()
    
    grid_response = AgGrid(
        df, 
        gridOptions=gridOptions, 
        width='100%',
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=True, # REQUIRED for 'Set' filter
        key=key
    )
    return grid_response

if df is None:
    st.error("No reports found in `reports/` directory. Please run the screener or git pull.")
else:
    st.markdown(f"### 📅 Report: `{filename}`")
    
    # --- FILTERING ---
    high_conf_df = df[df['Priority'].isin(['VERY_HIGH', 'HIGH'])]
    
    if high_conf_df.empty:
        st.warning("No High Confidence setups found for today.")
    else:
        # Split Longs vs Shorts
        longs = high_conf_df[high_conf_df['Verdict'] == 'BULLISH_SETUP']
        shorts = high_conf_df[high_conf_df['Verdict'] == 'BEARISH_SETUP']

        # --- SHORTS ---
        st.markdown("## 📉 Sell / Short Setups")
        if not shorts.empty:
            st.info(f"Found {len(shorts)} High-Confidence Short opportunities. Use column headers to filter.")
            display_cols = ['Ticker', 'Current_Price', 'Priority', 'Action', 'Monthly_Context', 'Weekly_Context', 'Weekly_Anchor_Date', 'Weekly_Signal']
            shorts_display = shorts[display_cols].copy()
            
            # Show AgGrid
            grid_shorts = show_aggrid(shorts_display, key="shorts_grid")
            
            # Get filtered data if user filtered in grid (AgGrid returns the state)
            # However, for the simple text list below, we might just loop through the original or the filtered result.
            # Using grid_response['data'] gives back the data in the grid.
            filtered_shorts = grid_shorts['data']
            
            with st.expander("🕵️ Smart Money Analysis (Shorts)"):
                # Convert back to dataframe to iterrows easily if it's a dict/list
                if isinstance(filtered_shorts, pd.DataFrame):
                    iter_shorts = filtered_shorts
                else:
                    iter_shorts = pd.DataFrame(filtered_shorts)

                if not iter_shorts.empty:
                    for index, row in iter_shorts.iterrows():
                        st.markdown(f"**{row['Ticker']}**: {row['Priority']}. **{row['Weekly_Signal']}** on {row['Weekly_Anchor_Date']}.")
        else:
            st.markdown("*No high-confidence short setups.*")

        # --- LONGS ---
        st.markdown("## 📈 Buy / Long Setups")
        if not longs.empty:
            st.success(f"Found {len(longs)} High-Confidence Long opportunities. Use column headers to filter.")
            display_cols = ['Ticker', 'Current_Price', 'Priority', 'Action', 'Monthly_Context', 'Weekly_Context', 'Weekly_Anchor_Date', 'Weekly_Signal']
            longs_display = longs[display_cols].copy()
            
            # Show AgGrid
            grid_longs = show_aggrid(longs_display, key="longs_grid")
            filtered_longs = grid_longs['data']
            
            with st.expander("🕵️ Smart Money Analysis (Longs)"):
                if isinstance(filtered_longs, pd.DataFrame):
                    iter_longs = filtered_longs
                else:
                    iter_longs = pd.DataFrame(filtered_longs)
                    
                if not iter_longs.empty:
                    for index, row in iter_longs.iterrows():
                        st.markdown(f"**{row['Ticker']}**: {row['Priority']}. **{row['Weekly_Signal']}** on {row['Weekly_Anchor_Date']}.")
        else:
            st.markdown("*No high-confidence long setups.*")

    # --- ALL TRADES EXPANDER ---
    with st.expander("📂 View All Data (Raw)"):
        show_aggrid(df, key="main_grid")
