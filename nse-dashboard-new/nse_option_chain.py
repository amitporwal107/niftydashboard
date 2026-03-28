import pandas as pd
import os
import re
import sys

# =========================
# CONFIG
# =========================
DATA_FOLDER = "/app/nsedata"

# =========================
# EXTRACT DATE FROM FILENAME
# =========================
def extract_date(filename):
    match = re.search(r'\d{8}', filename)
    return match.group(0) if match else None

# =========================
# LOAD CSV FILES
# =========================
def load_data(file_path):
    """Load a single BhavCopy CSV file"""
    try:
        df = pd.read_csv(file_path)
        trade_date = extract_date(os.path.basename(file_path))
        df["TradeDate"] = trade_date
        return df
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

# =========================
# RENAME COLUMNS
# =========================
def rename_columns(df):
    return df.rename(columns={
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

# =========================
# FILTER NIFTY OPTIONS (IDO FIX)
# =========================
def filter_nifty(df):
    df["Symbol"] = df["Symbol"].astype(str).str.strip().str.upper()
    df["Instrument"] = df["Instrument"].astype(str).str.strip().str.upper()
    df["OptionType"] = df["OptionType"].astype(str).str.strip().str.upper()
    
    return df[
        (df["Symbol"] == "NIFTY") &
        (df["Instrument"] == "IDO") &
        (df["OptionType"].isin(["CE", "PE"]))
    ]

# =========================
# BUILD OPTION CHAIN (ALL EXPIRIES)
# =========================
def build_option_chain_all(df, trade_date=None):
    if trade_date:
        df = df[df["TradeDate"] == trade_date]
    
    expiries = sorted(df["Expiry"].dropna().unique())
    print(f"Processing {len(expiries)} expiries:", expiries)
    
    all_results = {}
    
    for expiry in expiries:
        print(f"\nProcessing Expiry: {expiry}")
        
        data = df[df["Expiry"] == expiry]
        
        ce = data[data["OptionType"] == "CE"]
        pe = data[data["OptionType"] == "PE"]
        
        # OUTER JOIN FIX (handles missing CE/PE)
        merged = pd.merge(
            ce,
            pe,
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
        
        all_results[expiry] = option_chain
    
    return all_results

# =========================
# MAIN
# =========================
def process_bhavcopy(input_file):
    """Process a BhavCopy file and generate expiry-wise CSV files"""
    print(f"Processing file: {input_file}")
    
    # Load data
    df = load_data(input_file)
    if df is None:
        return
    
    print(f"Total rows loaded: {len(df)}")
    
    # Rename columns
    df = rename_columns(df)
    
    # Debug
    print("Unique Symbols:", df["Symbol"].unique()[:10])
    print("Unique Instruments:", df["Instrument"].unique()[:10])
    
    # Filter NIFTY
    nifty = filter_nifty(df)
    print(f"NIFTY option rows: {len(nifty)}")
    
    if nifty.empty:
        print("ERROR: No NIFTY option data found")
        return
    
    print("Available TradeDates:", nifty["TradeDate"].unique())
    print("Available Expiries:", nifty["Expiry"].unique())
    
    # Build all expiry chains
    all_chains = build_option_chain_all(
        nifty,
        trade_date=nifty["TradeDate"].unique()[0]
    )
    
    # Save each expiry separately
    os.makedirs(DATA_FOLDER, exist_ok=True)
    
    for expiry, chain in all_chains.items():
        filename = f"NIFTY_{expiry}.csv".replace("-", "_")
        output_path = os.path.join(DATA_FOLDER, filename)
        chain.to_csv(output_path, index=False)
        print(f"✓ Saved: {output_path} ({len(chain)} rows)")
    
    print(f"\n✅ Successfully processed {len(all_chains)} expiry files")

# =========================
# RUN
# =========================
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        # Default to looking for BhavCopy in current directory
        input_file = "BhavCopy_NSE_FO_0_0_0_20260327_F_0000.csv"
    
    if not os.path.exists(input_file):
        print(f"ERROR: File not found: {input_file}")
        print("Usage: python nse_option_chain.py <path_to_bhavcopy.csv>")
        sys.exit(1)
    
    process_bhavcopy(input_file)
