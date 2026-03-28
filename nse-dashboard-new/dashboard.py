import streamlit as st
st.set_page_config(layout="wide", page_title="NIFTY Options Analysis Dashboard")

import pandas as pd
import plotly.graph_objects as go
import os
import re
from datetime import datetime, timedelta
import glob

# =========================
# CONFIG
# =========================
# Get script directory for cross-platform compatibility
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
DATA_FOLDER = os.path.join(SCRIPT_DIR, "nsedata")

# Ensure data folder exists
os.makedirs(DATA_FOLDER, exist_ok=True)

# =========================
# AUTO-PARSE BHAVCOPY FILES
# =========================
def auto_parse_bhavcopy():
    """Automatically parse any BhavCopy files found in nsedata folder"""
    # Look for BhavCopy files
    bhavcopy_pattern = os.path.join(DATA_FOLDER, "BhavCopy_*.csv")
    bhavcopy_files = glob.glob(bhavcopy_pattern)
    
    if not bhavcopy_files:
        return False, "No BhavCopy files found"
    
    # Check if already parsed (look for NIFTY_*.csv files)
    nifty_pattern = os.path.join(DATA_FOLDER, "NIFTY_*.csv")
    nifty_files = glob.glob(nifty_pattern)
    
    if nifty_files:
        return False, f"Already parsed. Found {len(nifty_files)} expiry files"
    
    # Parse the first BhavCopy file found
    bhavcopy_file = bhavcopy_files[0]
    
    try:
        # Read BhavCopy
        df = pd.read_csv(bhavcopy_file)
        
        # Extract date from filename
        filename = os.path.basename(bhavcopy_file)
        date_match = re.search(r'\d{8}', filename)
        trade_date = date_match.group(0) if date_match else None
        
        # Rename columns
        df = df.rename(columns={
            "TckrSymb": "Symbol",
            "FinInstrmTp": "Instrument",
            "XpryDt": "Expiry",
            "StrkPric": "Strike",
            "OptnTp": "OptionType",
            "OpnIntrst": "OI",
            "ChngInOpnIntrst": "OI_Change",
            "TtlTradgVol": "Volume",
            "LastPric": "LTP"
        })
        
        # Clean and filter
        df["Symbol"] = df["Symbol"].astype(str).str.strip().str.upper()
        df["Instrument"] = df["Instrument"].astype(str).str.strip().str.upper()
        df["OptionType"] = df["OptionType"].astype(str).str.strip().str.upper()
        
        # Filter NIFTY options
        nifty = df[
            (df["Symbol"] == "NIFTY") &
            (df["Instrument"] == "IDO") &
            (df["OptionType"].isin(["CE", "PE"]))
        ]
        
        if nifty.empty:
            return False, "No NIFTY option data found in BhavCopy"
        
        nifty["TradeDate"] = trade_date
        
        # Get unique expiries
        expiries = sorted(nifty["Expiry"].dropna().unique())
        
        # Create individual expiry files
        files_created = 0
        for expiry in expiries:
            data = nifty[nifty["Expiry"] == expiry]
            
            ce = data[data["OptionType"] == "CE"]
            pe = data[data["OptionType"] == "PE"]
            
            # Merge CE and PE data
            merged = pd.merge(
                ce, pe,
                on=["Strike", "Expiry", "TradeDate"],
                how="outer",
                suffixes=("_CE", "_PE")
            ).fillna(0)
            
            option_chain = pd.DataFrame({
                "TradeDate": merged["TradeDate"],
                "Expiry": merged["Expiry"],
                "Strike": merged["Strike"],
                "CE_OI": merged.get("OI_CE", 0),
                "CE_Chg_OI": merged.get("OI_Change_CE", 0),
                "CE_Volume": merged.get("Volume_CE", 0),
                "CE_LTP": merged.get("LTP_CE", 0),
                "PE_OI": merged.get("OI_PE", 0),
                "PE_Chg_OI": merged.get("OI_Change_PE", 0),
                "PE_Volume": merged.get("Volume_PE", 0),
                "PE_LTP": merged.get("LTP_PE", 0),
            }).sort_values(by="Strike")
            
            # Save to CSV
            filename = f"NIFTY_{expiry}.csv".replace("-", "_")
            output_path = os.path.join(DATA_FOLDER, filename)
            option_chain.to_csv(output_path, index=False)
            files_created += 1
        
        return True, f"Parsed {files_created} expiries from {os.path.basename(bhavcopy_file)}"
        
    except Exception as e:
        return False, f"Error parsing BhavCopy: {str(e)}"

# =========================
# CREATE SAMPLE DATA IF NEEDED
# =========================
def create_sample_data():
    """Create minimal sample data for demonstration"""
    # Check if any data exists
    try:
        existing_files = [f for f in os.listdir(DATA_FOLDER) if f.startswith("NIFTY_") and f.endswith('.csv')]
    except:
        existing_files = []
    
    if len(existing_files) == 0:
        sample_data = {
            'TradeDate': ['20260327'] * 20,
            'Expiry': ['2026-03-30'] * 20,
            'Strike': [22200, 22250, 22300, 22350, 22400, 22450, 22500, 22550, 22600, 22650, 
                      22700, 22750, 22800, 22850, 22900, 22950, 23000, 23050, 23100, 23150],
            'CE_OI': [50000, 75000, 100000, 150000, 200000, 250000, 300000, 350000, 300000, 250000,
                     200000, 150000, 100000, 75000, 50000, 40000, 30000, 20000, 15000, 10000],
            'PE_OI': [10000, 15000, 20000, 30000, 40000, 50000, 75000, 100000, 150000, 200000,
                     250000, 300000, 350000, 300000, 250000, 200000, 150000, 100000, 75000, 50000],
            'CE_Chg_OI': [1000, 1500, 2000, 3000, 4000, 5000, 6000, 7000, 6000, 5000,
                         4000, 3000, 2000, 1500, 1000, 800, 600, 400, 300, 200],
            'PE_Chg_OI': [200, 300, 400, 600, 800, 1000, 1500, 2000, 3000, 4000,
                         5000, 6000, 7000, 6000, 5000, 4000, 3000, 2000, 1500, 1000],
            'CE_Volume': [5000, 7000, 9000, 11000, 13000, 15000, 17000, 19000, 17000, 15000,
                         13000, 11000, 9000, 7000, 5000, 4000, 3000, 2000, 1500, 1000],
            'PE_Volume': [1000, 1500, 2000, 3000, 4000, 5000, 7000, 9000, 11000, 13000,
                         15000, 17000, 19000, 17000, 15000, 13000, 11000, 9000, 7000, 5000],
            'CE_LTP': [220, 180, 150, 120, 95, 75, 60, 48, 38, 30,
                      24, 19, 15, 12, 9, 7, 5, 4, 3, 2],
            'PE_LTP': [2, 3, 4, 5, 7, 9, 12, 15, 19, 24,
                      30, 38, 48, 60, 75, 95, 120, 150, 180, 220]
        }
        
        df = pd.DataFrame(sample_data)
        sample_file = os.path.join(DATA_FOLDER, 'NIFTY_2026_03_30.csv')
        df.to_csv(sample_file, index=False)
        return True
    return False

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>
    .stApp { background-color: #f9fafb; }
    .dashboard-header {
        background-color: white;
        padding: 1.5rem;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }
    .sidebar-section {
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .sidebar-title {
        font-size: 0.875rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 0.75rem;
    }
    .metric-card {
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
    }
    .metric-label {
        font-size: 0.875rem;
        color: #6b7280;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #111827;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =========================
# LOAD DATA FUNCTIONS
# =========================
@st.cache_data
def load_all_expiry_data(folder):
    """Load all NIFTY expiry CSV files"""
    data = {}
    
    if not os.path.exists(folder):
        return data
    
    for file in os.listdir(folder):
        if not file.startswith("NIFTY_") or not file.endswith(".csv"):
            continue
        
        # Extract expiry date from filename
        match = re.search(r'NIFTY_(\d{4})_(\d{2})_(\d{2})\.csv', file)
        if match:
            expiry_date = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
            df = pd.read_csv(os.path.join(folder, file))
            data[expiry_date] = df
    
    return data

def calculate_max_pain(df):
    """Calculate max pain strike price"""
    strikes = df["Strike"].unique()
    pain = {}
    
    for strike in strikes:
        ce_pain = ((df["Strike"] - strike).clip(lower=0) * df["CE_OI"]).sum()
        pe_pain = ((strike - df["Strike"]).clip(lower=0) * df["PE_OI"]).sum()
        pain[strike] = ce_pain + pe_pain
    
    return min(pain, key=pain.get) if pain else 0

def calculate_atm(df):
    """Calculate ATM strike"""
    if df.empty:
        return 0
    df_copy = df.copy()
    df_copy["Diff"] = abs(df_copy["CE_LTP"] - df_copy["PE_LTP"])
    return int(df_copy.loc[df_copy["Diff"].idxmin(), "Strike"])

# =========================
# STARTUP: AUTO-PARSE BHAVCOPY
# =========================
with st.spinner("Checking for BhavCopy files..."):
    parsed, message = auto_parse_bhavcopy()
    if parsed:
        st.success(f"✅ {message}")

# =========================
# LOAD DATA
# =========================
sample_created = create_sample_data()

expiry_data = load_all_expiry_data(DATA_FOLDER)

if not expiry_data:
    st.error("⚠️ No option data found.")
    st.info("""
    **To get started:**
    
    1. Place your BhavCopy CSV file in the `nsedata` folder
       - Format: `BhavCopy_NSE_FO_0_0_0_YYYYMMDD_F_0000.csv`
    
    2. Refresh the page (press F5)
    
    3. The dashboard will automatically parse the file and create expiry data
    
    **Or download BhavCopy from:**
    - NSE India: https://www.nseindia.com
    - Reports → Archives → F&O Bhavcopy
    """)
    st.stop()
else:
    if sample_created:
        st.info("📊 **Demo Mode:** Using sample data. Place BhavCopy file in `nsedata` folder for real data.")

# Filter for current year
current_year = datetime.today().year
filtered_data = {exp: df for exp, df in expiry_data.items() if datetime.strptime(exp, "%Y-%m-%d").year == current_year}
if not filtered_data:
    filtered_data = expiry_data

expiries = sorted(filtered_data.keys())

# =========================
# HEADER
# =========================
st.markdown('<div class="dashboard-header"><h1 style="margin:0;">🚀 NIFTY Options Analysis Dashboard</h1></div>', unsafe_allow_html=True)

# =========================
# TABS
# =========================
tab1, tab2 = st.tabs(["Open Interest", "OI Change"])

with tab2:
    st.info("🔄 Use the toggle in 'Open Interest' tab to view OI changes")

with tab1:
    col_sidebar, col_main = st.columns([1, 4])
    
    with col_sidebar:
        # NIFTY Display
        st.subheader("🔍 NIFTY Index")
        st.metric("Price", "22,819.60", "-2.09%", delta_color="inverse")
        
        st.markdown("---")
        
        # Trade date
        st.subheader("📅 Trade Date")
        if expiries:
            first_file = f"NIFTY_{expiries[0].replace('-', '_')}.csv"
            first_path = os.path.join(DATA_FOLDER, first_file)
            if os.path.exists(first_path):
                sample_df = pd.read_csv(first_path)
                if 'TradeDate' in sample_df.columns:
                    trade_date_str = str(sample_df['TradeDate'].iloc[0])
                    try:
                        trade_date = datetime.strptime(trade_date_str, "%Y%m%d")
                        st.info(f"📅 {trade_date.strftime('%d %b %Y')}")
                    except:
                        st.info("📅 Date from data")
        
        st.markdown("---")
        
        # Expiries
        st.subheader("Expiries Included")
        
        selected_expiries = []
        today = datetime.today()
        
        for i, exp in enumerate(expiries[:6]):
            exp_date = datetime.strptime(exp, "%Y-%m-%d")
            days = (exp_date - today).days
            is_weekly = days <= 7
            
            # Create simple label without emoji
            label = f"{exp_date.strftime('%d %b %Y')} ({days} days)"
            
            # Show checkbox
            default_value = (i == 0)
            checked = st.checkbox(label, value=default_value, key=f"exp_{exp}")
            
            if checked:
                selected_expiries.append(exp)
        
        st.markdown("---")
        
        if not selected_expiries:
            st.warning("⚠️ Select at least one expiry")
            st.stop()
        
        # Combine data
        df = pd.concat([filtered_data[e] for e in selected_expiries])
        df = df.groupby("Strike", as_index=False).agg({
            "CE_OI": "sum", "PE_OI": "sum",
            "CE_Chg_OI": "sum", "PE_Chg_OI": "sum",
            "CE_LTP": "mean", "PE_LTP": "mean",
            "CE_Volume": "sum", "PE_Volume": "sum"
        }).sort_values("Strike")
        
        atm = calculate_atm(df)
        max_pain = int(calculate_max_pain(df))
        
        # Strike Range
        st.subheader("Strike Range")
        
        min_strike = int(df["Strike"].min())
        max_strike = int(df["Strike"].max())
        default_min = max(min_strike, atm - 500)
        default_max = min(max_strike, atm + 500)
        
        strike_range = st.slider("Range", min_value=min_strike, max_value=max_strike,
                                value=(default_min, default_max), step=50, label_visibility="collapsed")
        
        st.caption("Quick filters - Strikes around ATM:")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("All", use_container_width=True): 
                strike_range = (min_strike, max_strike)
        with col2:
            if st.button("±10", use_container_width=True): 
                strike_range = (atm - 500, atm + 500)
        with col3:
            if st.button("±20", use_container_width=True): 
                strike_range = (atm - 1000, atm + 1000)
    
    # Filter data
    df = df[(df["Strike"] >= strike_range[0]) & (df["Strike"] <= strike_range[1])]
    
    support = int(df.loc[df["PE_OI"].idxmax(), "Strike"]) if len(df) > 0 else 0
    resistance = int(df.loc[df["CE_OI"].idxmax(), "Strike"]) if len(df) > 0 else 0
    total_pe = df["PE_OI"].sum()
    total_ce = df["CE_OI"].sum()
    pcr = round(total_pe / total_ce, 2) if total_ce else 0
    
    with col_main:
        col_header1, col_header2 = st.columns([3, 1])
        with col_header1:
            st.markdown('<h2>Open Interest</h2>', unsafe_allow_html=True)
        with col_header2:
            show_change = st.toggle("Show OI change", value=False)
        
        st.markdown("---")
        
        # Chart
        chart_df = df.copy()
        chart_df["Put OI"] = (chart_df["PE_Chg_OI"] if show_change else chart_df["PE_OI"]) / 100000
        chart_df["Call OI"] = (chart_df["CE_Chg_OI"] if show_change else chart_df["CE_OI"]) / 100000
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=chart_df["Strike"], y=chart_df["Put OI"], name="Put OI", marker_color="#10b981"))
        fig.add_trace(go.Bar(x=chart_df["Strike"], y=chart_df["Call OI"], name="Call OI", marker_color="#ef4444"))
        fig.add_vline(x=atm, line_dash="dash", line_color="#000", annotation_text=f"ATM {atm}")
        
        fig.update_layout(barmode='group', plot_bgcolor='white', paper_bgcolor='white', height=450,
                         xaxis=dict(title="Strike Price", gridcolor='#e5e7eb'),
                         yaxis=dict(title="OI (Lakhs)", gridcolor='#e5e7eb'),
                         legend=dict(orientation="h", yanchor="bottom", y=-0.2))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Metrics
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Call OI", f"{(total_ce / 10000000):.2f}cr")
        with col2:
            st.metric("Total Put OI", f"{(total_pe / 10000000):.2f}cr")
        with col3:
            st.metric("PCR", pcr)
        with col4:
            st.metric("ATM Strike", atm)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Support", support)
        with col2:
            st.metric("Resistance", resistance)
        with col3:
            st.metric("Max Pain", max_pain)
        
        if pcr > 1.2:
            st.success("🚀 Bullish Bias (PCR > 1.2)")
        elif pcr < 0.8:
            st.error("🔻 Bearish Bias (PCR < 0.8)")
        else:
            st.warning("⚖️ Sideways Market")
