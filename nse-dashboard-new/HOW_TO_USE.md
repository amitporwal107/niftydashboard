# 🎯 How to Upload and Process BhavCopy CSV

## ✅ Updated Dashboard Features

The dashboard now includes **automatic CSV processing** when you upload a file!

## 📤 Step-by-Step Guide:

### Step 1: Access the Dashboard
- Dashboard URL: **http://localhost:8502**
- Or access via the preview URL provided by your environment

### Step 2: Upload BhavCopy CSV

1. Look for the **"📤 Upload BhavCopy"** section in the **left sidebar**
2. Click **"Browse files"** or drag and drop your CSV file
3. Select your BhavCopy file (format: `BhavCopy_NSE_FO_0_0_0_YYYYMMDD_F_0000.csv`)

### Step 3: Process the File

After uploading, you'll see a **"🔄 Process BhavCopy"** button:
1. Click the **"Process BhavCopy"** button
2. Wait for processing (you'll see a spinner)
3. Dashboard will show "✅ BhavCopy processed successfully!"
4. Dashboard will automatically refresh with new data

### Step 4: Analyze Your Data

Once processed, you can:
- ✅ Select multiple expiries from the **"Expiries Included"** section
- ✅ Adjust the **Strike Range** slider
- ✅ Use **ATM proximity buttons** (Show All, 5, 10, 15, 20, 25)
- ✅ Toggle **"Show OI change"** to view OI changes instead of absolute values
- ✅ View all the **Summary Metrics** (PCR, ATM, Support, Resistance)

## 🔧 What Happens Behind the Scenes

When you click "Process BhavCopy":
1. CSV is saved temporarily
2. Parser script (`nse_option_chain.py`) runs automatically
3. BhavCopy is converted to individual expiry files:
   - `NIFTY_2026_03_30.csv`
   - `NIFTY_2026_04_07.csv`
   - etc.
4. Files are saved in `/app/nsedata/`
5. Dashboard reloads and shows the new data

## 📊 Dashboard Features

### Left Sidebar:
- **NIFTY Display**: Current price and % change
- **Trade Date**: Automatically extracted from CSV
- **Expiries Included**: Checkboxes for multiple expiry selection
  - Shows days remaining until expiry
  - Blue badge (🔵) for weekly expiries
- **Strike Range**: Slider to filter strikes
- **ATM Proximity**: Quick filter buttons (5, 10, 15, 20, 25 strikes)

### Main Chart:
- **Green Bars**: Put OI (Open Interest)
- **Red Bars**: Call OI (Open Interest)
- **Dashed Line**: ATM (At The Money) strike
- **Toggle**: Switch between absolute OI and OI changes

### Summary Metrics:
- **Total Call OI**: Sum of all Call Open Interest
- **Total Put OI**: Sum of all Put Open Interest
- **PCR**: Put-Call Ratio (Total Put OI / Total Call OI)
- **NIFTY**: Current index price
- **ATM Strike**: Strike where CE LTP ≈ PE LTP
- **Support**: Strike with maximum Put OI
- **Resistance**: Strike with maximum Call OI
- **Market Bias**: 
  - 🚀 Bullish if PCR > 1.2
  - 🔻 Bearish if PCR < 0.8
  - ⚖️ Sideways if 0.8 ≤ PCR ≤ 1.2

## 🐛 Troubleshooting

### Issue: "No option data found"
**Solution**: Upload a BhavCopy CSV and click "Process BhavCopy"

### Issue: "No expiries showing"
**Solution**: Make sure the CSV was processed successfully. Check for success message.

### Issue: "All dates disabled in calendar"
**Note**: The calendar is currently for display only. The trade date is automatically extracted from your CSV data.

## 📝 Data Format

Your BhavCopy CSV should have these columns:
- `TckrSymb`: Ticker Symbol (e.g., NIFTY)
- `FinInstrmTp`: Instrument Type (IDO for index options)
- `XpryDt`: Expiry Date
- `StrkPric`: Strike Price
- `OptnTp`: Option Type (CE/PE)
- `OpnIntrst`: Open Interest
- `ChngInOpnIntrst`: Change in Open Interest
- `TtlTradgVol`: Total Trading Volume
- `LastPric`: Last Traded Price

## 🎨 Color Scheme

- **Put OI**: #10b981 (Green) - Indicates bullish sentiment
- **Call OI**: #ef4444 (Red) - Indicates bearish sentiment
- **Background**: #f9fafb (Light Gray)
- **Accents**: #3b82f6 (Blue)

## 📂 File Locations

- **Dashboard**: `/app/dashboard.py`
- **Parser**: `/app/nse_option_chain.py`
- **Data Folder**: `/app/nsedata/`
- **Sample CSV**: `/app/BhavCopy_NSE_FO_0_0_0_20260327_F_0000.csv`

---

**Need Help?** Expand the **"❓ How to use this feature"** section in the dashboard sidebar!
