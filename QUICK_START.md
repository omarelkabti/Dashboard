# 🚀 Quick Start - PET Resource Allocation Dashboard

## One-Command Setup

```bash
python3 start_dashboard.py
```

That's it! The dashboard will:
- ✅ Check your Python installation
- ✅ Install required packages automatically
- ✅ Verify your data files
- ✅ Start the dashboard
- ✅ Open your browser to http://localhost:8501

---

## Alternative Manual Setup (if needed)

### Step 1: Install Dependencies
```bash
pip3 install streamlit pandas plotly
```

### Step 2: Start Dashboard
```bash
streamlit run app.py
```

### Step 3: Open Browser
Go to: http://localhost:8501

---

## 📁 Required Files

Make sure you have:
- ✅ `app.py` (main dashboard)
- ✅ `src/etl.py` (data processing)
- ✅ `data/*.csv` (your PET data files)
- ✅ `requirements.txt` (dependencies)

---

## 🔄 Updating Data

To use new CSV files:
1. **Add new CSV** to the `data/` folder
2. **Refresh browser** page
3. Dashboard automatically uses the **most recent file**

---

## 🎯 Dashboard Features

Once running, you'll have access to:

### 📊 **Business Platform Services Focus**
- VP completion rates
- Supervisor team analysis
- Individual resource tracking

### 🔍 **Search & Filter**
- Global search across all data
- Filter by VP org, completion status
- Hierarchical drilldown (VP → Director → Supervisor → Individual)

### 📈 **Key Metrics**
- Workstream 1 completion tracking
- Resource allocation analysis
- Team performance insights

---

## 🛠 Troubleshooting

### "Command not found: python3"
Try: `python start_dashboard.py`

### "Module not found: streamlit"
Run: `pip3 install streamlit pandas plotly`

### "No CSV files found"
Add your PET Resource Allocation CSV files to the `data/` folder

### Dashboard won't load
1. Check terminal for error messages
2. Try: `streamlit run app.py --server.port 8502`
3. Open: http://localhost:8502

---

## 💡 Pro Tips

### Multiple Data Files
- Dashboard uses the **most recent** CSV file
- Keep historical files for trend analysis
- Name files with dates: `PET_Resource_Allocation_2025-09-10.csv`

### Performance
- Dashboard handles 1000+ resources easily
- Search is instant across all data
- Filters update in real-time

### Sharing
- Send teammates the URL: http://localhost:8501
- For external sharing, see `DEPLOYMENT_OPTIONS.md`

---

## 🎉 You're Ready!

Your dashboard includes:
- ✅ Real supervisor mapping (from CSV structure)
- ✅ Workstream 1 completion tracking
- ✅ Business Platform Services focus
- ✅ Interactive search and filters
- ✅ Hierarchical organizational analysis

**Questions?** Check the full documentation in the other `.md` files!
