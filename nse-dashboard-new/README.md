# 🚀 NIFTY Options Analysis Dashboard

A professional, real-time options analysis dashboard for NIFTY index options trading. Built with Streamlit and Python.

![Dashboard](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## ✨ Features

- 📊 **Real-time Option Chain Analysis** - Visualize Put and Call Open Interest
- 📈 **Multiple Expiry Support** - Analyze multiple expiry dates simultaneously
- 🎯 **Smart Calculations** - Auto-calculate ATM, Max Pain, PCR, Support & Resistance
- 📤 **CSV Upload** - Upload NSE BhavCopy files directly through the dashboard
- 🔄 **Auto-Processing** - Automatic parsing and processing of uploaded data
- 🎨 **Professional UI** - Clean, modern interface with color-coded charts
- ⚡ **Real-time Filtering** - Strike range slider and ATM proximity filters
- 📱 **Responsive Design** - Works on desktop and mobile devices

## 🎯 Key Metrics Displayed

- **PCR (Put-Call Ratio)** - Market sentiment indicator
- **ATM Strike** - At-The-Money strike price detection
- **Support Level** - Strike with maximum Put OI
- **Resistance Level** - Strike with maximum Call OI
- **Max Pain** - Price point with maximum option writer pain
- **Market Bias** - Bullish/Bearish/Sideways indicator based on PCR

## 📸 Screenshots

### Main Dashboard
- Multi-tab interface (OI Change, Open Interest, Multistrike OI, etc.)
- Green bars for Put OI, Red bars for Call OI
- Dashed line marking ATM strike
- Summary metrics panel

### Features
- **Left Sidebar**: NIFTY price, Date, Expiry selection, Strike range filters
- **Main Chart**: Professional Plotly bar charts with interactive tooltips
- **Summary Panel**: Total Call/Put OI, PCR, NIFTY price, Support/Resistance

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip or conda

### Installation

```bash
# Clone the repository
git clone https://github.com/amitporwal107/nifty-options-dashboard.git
cd nifty-options-dashboard

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run dashboard.py
```

Access the dashboard at: **http://localhost:8501**

## 📦 Project Structure

```
nifty-options-dashboard/
├── dashboard.py              # Main Streamlit application
├── nse_option_chain.py       # BhavCopy parser script
├── nsedata/                  # Data directory (CSV files)
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker configuration
├── deploy.sh                 # Auto-deployment script
├── .streamlit/
│   └── config.toml          # Streamlit configuration
└── README.md                 # This file
```

## 💾 Data Format

The dashboard accepts NSE BhavCopy CSV files with the following format:

**Required Columns:**
- `TckrSymb` - Ticker Symbol (NIFTY)
- `FinInstrmTp` - Instrument Type (IDO for index options)
- `XpryDt` - Expiry Date
- `StrkPric` - Strike Price
- `OptnTp` - Option Type (CE/PE)
- `OpnIntrst` - Open Interest
- `ChngInOpnIntrst` - Change in Open Interest
- `TtlTradgVol` - Total Trading Volume
- `LastPric` - Last Traded Price

**Sample filename:** `BhavCopy_NSE_FO_0_0_0_20260327_F_0000.csv`

## 📤 How to Use

1. **Upload BhavCopy CSV**
   - Click "Browse files" in the sidebar
   - Select your NSE BhavCopy CSV file
   - Click "🔄 Process BhavCopy"

2. **Select Expiries**
   - Check the expiry dates you want to analyze
   - Dashboard shows days remaining and marks weekly expiries

3. **Adjust Strike Range**
   - Use the slider for custom range
   - Or click ATM proximity buttons (5, 10, 15, 20, 25)

4. **Analyze Data**
   - View the chart (Green=Put OI, Red=Call OI)
   - Check summary metrics below the chart
   - Toggle "Show OI change" to view OI changes

## 🐳 Docker Deployment

```bash
# Build image
docker build -t nifty-dashboard .

# Run container
docker run -d -p 8501:8501 \
  -v $(pwd)/nsedata:/app/nsedata \
  --name nifty-dashboard \
  nifty-dashboard
```

## 🌐 Cloud Deployment

### Streamlit Cloud (Free)
1. Push this repo to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository
5. Set main file: `dashboard.py`
6. Deploy!

### Heroku
```bash
heroku create nifty-dashboard
git push heroku main
```

### AWS EC2 / DigitalOcean
See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

## 🔧 Configuration

Edit `.streamlit/config.toml` to customize:

```toml
[server]
maxUploadSize = 200  # Max CSV upload size in MB
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

## 📊 Technical Details

### Technologies Used
- **Streamlit** - Web framework
- **Plotly** - Interactive charts
- **Pandas** - Data processing
- **Python 3.11** - Core language

### Data Processing
1. Upload BhavCopy CSV
2. Parse and filter NIFTY options (IDO instrument)
3. Separate CE (Call) and PE (Put) data
4. Perform outer join to handle missing strikes
5. Calculate metrics (ATM, PCR, Max Pain, etc.)
6. Store as individual expiry CSV files
7. Display in interactive dashboard

### Calculations

**ATM Strike:**
```python
df["Diff"] = abs(df["CE_LTP"] - df["PE_LTP"])
atm = df.loc[df["Diff"].idxmin(), "Strike"]
```

**PCR (Put-Call Ratio):**
```python
pcr = total_put_oi / total_call_oi
```

**Max Pain:**
```python
for strike in strikes:
    ce_pain = sum((df["Strike"] - strike).clip(lower=0) * df["CE_OI"])
    pe_pain = sum((strike - df["Strike"]).clip(lower=0) * df["PE_OI"])
    total_pain = ce_pain + pe_pain
max_pain = strike with minimum total_pain
```

## 🎨 Color Scheme

- **Put OI**: `#10b981` (Green) - Bullish sentiment
- **Call OI**: `#ef4444` (Red) - Bearish sentiment
- **Background**: `#f9fafb` (Light Gray)
- **Accents**: `#3b82f6` (Blue)

## 📈 Market Bias Indicators

- **Bullish**: PCR > 1.2 (More puts than calls)
- **Bearish**: PCR < 0.8 (More calls than puts)
- **Sideways**: 0.8 ≤ PCR ≤ 1.2

## 🔒 Security

- No hardcoded credentials
- Environment-based configuration
- CORS protection (can be enabled)
- File upload validation

## 📝 Development

### Setup Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
streamlit run dashboard.py
```

### Adding New Features

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 🐛 Troubleshooting

**Issue: Port already in use**
```bash
# Find and kill the process
lsof -i :8501
kill -9 <PID>
```

**Issue: Large CSV files failing**
- Increase upload size in `.streamlit/config.toml`
- Set `maxUploadSize = 200` (or higher)

**Issue: Data not loading**
- Ensure CSV format matches NSE BhavCopy format
- Check if file has NIFTY options data (IDO instrument)
- Verify file naming convention

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Amit Porwal**
- GitHub: [@amitporwal107](https://github.com/amitporwal107)

## 🙏 Acknowledgments

- NSE (National Stock Exchange of India) for providing BhavCopy data
- Streamlit for the amazing framework
- Plotly for interactive visualizations

## 📞 Support

For support, please open an issue in the GitHub repository or contact the author.

---

**⭐ If you find this project helpful, please consider giving it a star!**

---

## 🔗 Links

- [Streamlit Documentation](https://docs.streamlit.io/)
- [NSE India](https://www.nseindia.com/)
- [Plotly Python](https://plotly.com/python/)

---

**Built with ❤️ for options traders**
