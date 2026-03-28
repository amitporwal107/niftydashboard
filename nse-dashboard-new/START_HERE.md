# 📦 NIFTY Options Dashboard - Complete Package

## 🎉 Welcome!

This zip file contains the complete NIFTY Options Analysis Dashboard project.

---

## 📂 What's Inside:

### Core Files:
- `dashboard.py` - Main Streamlit application (544 lines)
- `nse_option_chain.py` - BhavCopy parser script (169 lines)
- `requirements.txt` - Python dependencies

### Deployment Files:
- `Dockerfile` - Docker container configuration
- `Procfile` - Heroku deployment file
- `runtime.txt` - Python version specification
- `deploy.sh` - Automated deployment script
- `.streamlit/config.toml` - Streamlit configuration

### Documentation:
- `README.md` - Main project documentation
- `DEPLOYMENT_GUIDE.md` - Comprehensive deployment guide
- `HOW_TO_USE.md` - User manual
- `UPLOAD_TO_GITHUB.md` - GitHub upload instructions
- `WHICH_APP_TO_USE.md` - App clarification
- `LICENSE` - MIT License

### Sample Data:
- `nsedata/` - 18 expiry CSV files (from 27 Mar 2026 BhavCopy)

---

## 🚀 Quick Start (3 Steps):

### 1. Extract the Zip File
```bash
unzip nifty-options-dashboard.zip
cd nifty-options-dashboard/
```

### 2. Install Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Run the Dashboard
```bash
streamlit run dashboard.py
```

**Access at:** http://localhost:8501

---

## 💡 First Time Using?

### Option A: Test Locally First
```bash
# Just run these 3 commands:
pip install streamlit plotly pandas
streamlit run dashboard.py
# Open: http://localhost:8501
```

### Option B: Deploy to Cloud (Free)
1. Upload to GitHub
2. Go to https://share.streamlit.io
3. Connect GitHub and select your repo
4. Set main file: `dashboard.py`
5. Deploy!

### Option C: Use Docker
```bash
docker build -t nifty-dashboard .
docker run -d -p 8501:8501 nifty-dashboard
# Access: http://localhost:8501
```

---

## 📊 What You Can Do:

✅ Upload NSE BhavCopy CSV files
✅ Analyze multiple expiry dates
✅ View Put vs Call Open Interest
✅ Calculate PCR, ATM, Max Pain
✅ Find Support & Resistance levels
✅ Filter by strike range
✅ Toggle OI vs OI Change view

---

## 📝 Sample Data Included:

The `nsedata/` folder contains processed data from:
- **Trade Date:** 27 Mar 2026
- **Expiries:** 18 different dates (30 Mar 2026 to 31 Dec 2030)
- **Strikes:** 158 strikes for nearest expiry

You can test the dashboard immediately with this data!

---

## 🔧 System Requirements:

- Python 3.11 or higher
- 2GB RAM (minimum)
- 100MB disk space
- Internet connection (for initial setup)

---

## 📖 Read This First:

**New Users:**
1. Start with `README.md` - Overview and features
2. Then `HOW_TO_USE.md` - Step-by-step usage guide

**Deploying to Cloud:**
3. Read `DEPLOYMENT_GUIDE.md` - All deployment options
4. Follow `UPLOAD_TO_GITHUB.md` - GitHub instructions

---

## 🆘 Troubleshooting:

**Can't run `streamlit run dashboard.py`?**
```bash
# Install Streamlit first:
pip install streamlit

# Or install everything:
pip install -r requirements.txt
```

**Port 8501 already in use?**
```bash
# Run on different port:
streamlit run dashboard.py --server.port 8502
```

**Need Python?**
- Download from: https://www.python.org/downloads/
- Install Python 3.11 or higher

---

## 📞 Support:

- GitHub: https://github.com/amitporwal107
- Email: (add your email if you want)

---

## 🎯 Next Steps:

1. ✅ Extract this zip
2. ✅ Run `pip install -r requirements.txt`
3. ✅ Run `streamlit run dashboard.py`
4. ✅ Upload your own BhavCopy CSV files
5. ✅ Deploy to cloud (optional)
6. ✅ Share with others!

---

## ⭐ Features:

- Real-time option chain analysis
- Multiple expiry support
- Professional visualizations
- PCR calculation
- ATM & Max Pain detection
- Support/Resistance levels
- Market bias indicator
- CSV upload & processing
- Mobile-friendly interface

---

## 📄 License:

MIT License - Free to use, modify, and distribute!

---

**Built with ❤️ for options traders**

*For detailed instructions, see README.md*
