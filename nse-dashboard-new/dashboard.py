import streamlit as st
st.set_page_config(layout="wide", page_title="NIFTY Options Analysis Dashboard")

import pandas as pd
import plotly.graph_objects as go
import os
import re
from datetime import datetime, timedelta

# =========================
# CONFIG
# =========================
DATA_FOLDER = "/app/nsedata"

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>
    /* Main theme colors matching mockup */
    .stApp {
        background-color: #f9fafb;
    }
    
    /* Header styling */
    .dashboard-header {
        background-color: white;
        padding: 1.5rem;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }
    
    /* Sidebar styling */
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
    
    /* Metric cards */
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
    
    /* Info badges */
    .info-badge {
        background-color: #fef3c7;
        color: #92400e;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    /* Buttons */
    div.stButton > button {
        border-radius: 0.375rem;
        font-weight: 500;
    }
    
    /* Remove streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background-color: white;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem;
        background-color: transparent;
        border-bottom: 2px solid transparent;
        color: #6b7280;
    }
    
    .stTabs [aria-selected="true"] {
        border-bottom-color: #3b82f6;
        color: #3b82f6;
        font-weight: 500;
    }
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
        
        # Extract expiry date from filename (NIFTY_2026_03_30.csv -> 2026-03-30)
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
    """Calculate ATM strike based on CE and PE LTP difference"""
    if df.empty:
        return 0
    df_copy = df.copy()
    df_copy["Diff"] = abs(df_copy["CE_LTP"] - df_copy["PE_LTP"])
    return int(df_copy.loc[df_copy["Diff"].idxmin(), "Strike"])

# =========================
# LOAD DATA
# =========================
expiry_data = load_all_expiry_data(DATA_FOLDER)

if not expiry_data:
    st.error("⚠️ No option data found. Please upload a BhavCopy CSV file and run the parser first.")
    st.code("python nse_option_chain.py BhavCopy_NSE_FO_XXXXXXXX_F_0000.csv")
    st.stop()

# Filter for current year
current_year = datetime.today().year
filtered_data = {
    exp: df for exp, df in expiry_data.items()
    if datetime.strptime(exp, "%Y-%m-%d").year == current_year
}

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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "OI Change",
    "Open Interest",
    "Multistrike OI",
    "Option OI vs Time",
    "Fut OI vs Time"
])

with tab2:  # Open Interest Tab (Main)
    col_sidebar, col_main = st.columns([1, 4])
    
    # =========================
    # LEFT SIDEBAR
    # =========================
    with col_sidebar:
        # NIFTY Search/Display
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">🔍 NIFTY 22819.60 <span style="color: #ef4444;">-2.09%</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Extract trade date from first expiry file if available
        trade_date = None
        if expiries:
            first_file = f"NIFTY_{expiries[0].replace('-', '_')}.csv"
            first_path = os.path.join(DATA_FOLDER, first_file)
            if os.path.exists(first_path):
                sample_df = pd.read_csv(first_path)
                if 'TradeDate' in sample_df.columns:
                    trade_date_str = str(sample_df['TradeDate'].iloc[0])
                    try:
                        trade_date = datetime.strptime(trade_date_str, "%Y%m%d")
                    except:
                        trade_date = datetime.today()
        
        if not trade_date:
            trade_date = datetime.today()
        
        # Date Display (showing trade date from data)
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">📅 Trade Date</div>', unsafe_allow_html=True)
        st.info(f"📅 {trade_date.strftime('%d %b %Y')}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Expiry Selection
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">Expiries Included</div>', unsafe_allow_html=True)
        
        selected_expiries = []
        today = datetime.today()
        
        for i, exp in enumerate(expiries[:6]):  # Show first 6 expiries
            exp_date = datetime.strptime(exp, "%Y-%m-%d")
            days = (exp_date - today).days
            
            is_weekly = days <= 7
            label = f"{exp_date.strftime('%d %b')} ({days}d)"
            if is_weekly:
                label += " 🔵"
            
            default_value = (i == 0)  # Select first expiry by default
            if st.checkbox(label, value=default_value, key=f"exp_{exp}"):
                selected_expiries.append(exp)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if not selected_expiries:
            st.warning("⚠️ Select at least one expiry")
            st.stop()
        
        # Combine selected expiries
        df = pd.concat([filtered_data[e] for e in selected_expiries])
        
        # Aggregate data
        df = df.groupby("Strike", as_index=False).agg({
            "CE_OI": "sum",
            "PE_OI": "sum",
            "CE_Chg_OI": "sum",
            "PE_Chg_OI": "sum",
            "CE_LTP": "mean",
            "PE_LTP": "mean",
            "CE_Volume": "sum",
            "PE_Volume": "sum"
        })
        
        df = df.sort_values("Strike")
        
        # Calculate ATM and Max Pain
        atm = calculate_atm(df)
        max_pain = int(calculate_max_pain(df))
        
        # Strike Range Filter
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">Strike Range</div>', unsafe_allow_html=True)
        
        min_strike = int(df["Strike"].min())
        max_strike = int(df["Strike"].max())
        
        default_min = max(min_strike, atm - 500)
        default_max = min(max_strike, atm + 500)
        
        strike_range = st.slider(
            "Range",
            min_value=min_strike,
            max_value=max_strike,
            value=(default_min, default_max),
            step=50,
            label_visibility="collapsed"
        )
        
        st.markdown('<p style="font-size: 0.75rem; color: #6b7280; margin-top: 0.5rem;">Strikes above and below ATM</p>', unsafe_allow_html=True)
        
        # ATM Proximity Buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Show All", use_container_width=True):
                strike_range = (min_strike, max_strike)
        with col2:
            if st.button("5", use_container_width=True):
                strike_range = (atm - 250, atm + 250)
        with col3:
            if st.button("10", use_container_width=True):
                strike_range = (atm - 500, atm + 500)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("15", use_container_width=True):
                strike_range = (atm - 750, atm + 750)
        with col2:
            if st.button("20", use_container_width=True):
                strike_range = (atm - 1000, atm + 1000)
        with col3:
            if st.button("25", use_container_width=True):
                strike_range = (atm - 1250, atm + 1250)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # How to use section
        with st.expander("❓ How to use this feature"):
            st.markdown("""
            1. **Select Expiries**: Choose one or more expiry dates
            2. **Adjust Strike Range**: Use slider or quick filters
            3. **ATM Filters**: Click 5, 10, 15, 20, or 25 for quick filtering
            4. **Analyze Charts**: View Put OI (green) vs Call OI (red)
            """)
    
    # Filter data by strike range
    df = df[
        (df["Strike"] >= strike_range[0]) &
        (df["Strike"] <= strike_range[1])
    ]
    
    # Calculate metrics
    support = int(df.loc[df["PE_OI"].idxmax(), "Strike"]) if len(df) > 0 else 0
    resistance = int(df.loc[df["CE_OI"].idxmax(), "Strike"]) if len(df) > 0 else 0
    
    total_pe = df["PE_OI"].sum()
    total_ce = df["CE_OI"].sum()
    pcr = round(total_pe / total_ce, 2) if total_ce else 0
    
    # =========================
    # MAIN CONTENT
    # =========================
    with col_main:
        # Show OI Change Toggle
        col_header1, col_header2 = st.columns([3, 1])
        with col_header1:
            chart_title = f"Open Interest on {trade_date.strftime('%a, %d %b')}"
            st.markdown(f'<h2 style="margin-bottom: 0;">{chart_title}</h2>', unsafe_allow_html=True)
            st.markdown('<a href="#" style="font-size: 0.875rem; color: #3b82f6;">How to read this?</a>', unsafe_allow_html=True)
        with col_header2:
            show_change = st.toggle("Show OI change", value=False)
            if show_change:
                st.markdown('<span class="info-badge">New</span>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Prepare chart data
        chart_df = df.copy()
        chart_df["Put OI"] = chart_df["PE_Chg_OI"] / 100000 if show_change else chart_df["PE_OI"] / 100000
        chart_df["Call OI"] = chart_df["CE_Chg_OI"] / 100000 if show_change else chart_df["CE_OI"] / 100000
        
        # Create chart
        fig = go.Figure()
        
        # Add bars
        fig.add_trace(go.Bar(
            x=chart_df["Strike"],
            y=chart_df["Put OI"],
            name="Put OI",
            marker_color="#10b981",  # Green from mockup
            hovertemplate='Strike: %{x}<br>Put OI: %{y:.2f}L<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            x=chart_df["Strike"],
            y=chart_df["Call OI"],
            name="Call OI",
            marker_color="#ef4444",  # Red from mockup
            hovertemplate='Strike: %{x}<br>Call OI: %{y:.2f}L<extra></extra>'
        ))
        
        # Add ATM line
        fig.add_vline(
            x=atm,
            line_dash="dash",
            line_color="#000",
            annotation_text=f"NIFTY {atm}",
            annotation_position="top"
        )
        
        # Update layout
        fig.update_layout(
            barmode='group',
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=450,
            xaxis=dict(
                title="Strike Price",
                gridcolor='#e5e7eb',
                showgrid=True
            ),
            yaxis=dict(
                title="Call / Put OI (Lakhs)",
                gridcolor='#e5e7eb',
                showgrid=True
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary Metrics
        st.markdown("---")
        st.markdown('<h3 style="margin-bottom: 1rem;">Summary Metrics</h3>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Call OI</div>
                <div class="metric-value">{(total_ce / 10000000):.2f}cr</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Put OI</div>
                <div class="metric-value">{(total_pe / 10000000):.2f}cr</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">PCR</div>
                <div class="metric-value">{pcr}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">NIFTY</div>
                <div class="metric-value">22819.6 <span style="color: #ef4444; font-size: 1rem;">-2.09%</span></div>
            </div>
            """, unsafe_allow_html=True)
        
        # Additional metrics
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("PCR", pcr)
        with col2:
            st.metric("ATM Strike", atm)
        with col3:
            st.metric("Support (Max Put OI)", support)
        with col4:
            st.metric("Resistance (Max Call OI)", resistance)
        
        # Market Bias
        if pcr > 1.2:
            st.success("🚀 Bullish Bias (PCR > 1.2)")
        elif pcr < 0.8:
            st.error("🔻 Bearish Bias (PCR < 0.8)")
        else:
            st.warning("⚖️ Sideways Market (0.8 ≤ PCR ≤ 1.2)")

# Other tabs
with tab1:
    st.info("🔄 OI Change view - Use the toggle in 'Open Interest' tab")

with tab3:
    st.info("📊 Multistrike OI view - Coming soon")

with tab4:
    st.info("📈 Option OI vs Time view - Coming soon")

with tab5:
    st.info("📉 Future OI vs Time view - Coming soon")

# =========================
# SIDEBAR - File Upload
# =========================
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📤 Upload BhavCopy")
    
    uploaded_file = st.file_uploader(
        "Upload NSE BhavCopy CSV",
        type=['csv'],
        help="Upload BhavCopy_NSE_FO CSV file"
    )
    
    if uploaded_file is not None:
        # Save uploaded file
        file_path = f"/tmp/{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Process button
        if st.button("🔄 Process BhavCopy", type="primary"):
            with st.spinner("Processing..."):
                import subprocess
                result = subprocess.run(
                    ["python", "/app/nse_option_chain.py", file_path],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    st.success("✅ BhavCopy processed successfully!")
                    st.info("🔄 Refreshing dashboard...")
                    st.rerun()
                else:
                    st.error("❌ Error processing file")
                    st.code(result.stderr)
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    **NIFTY Options Analysis Dashboard**
    
    - Real-time option chain analysis
    - Multiple expiry support
    - PCR calculation
    - ATM & Max Pain detection
    - Support/Resistance levels
    """)
