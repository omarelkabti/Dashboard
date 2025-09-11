# PET Resource Allocation Dashboard - Deployment Options for Intuit

## Overview
Your dashboard is currently running locally. Here are several options to deploy it for your team at Intuit.

## Option 1: 🥇 **Streamlit Cloud (Recommended)**

### Why This is Best:
- **Free hosting** for internal dashboards
- **Direct GitHub integration** - updates automatically
- **Easy sharing** via URL
- **Maintains all functionality** (search, filters, drilldown)

### Setup Steps:
1. **Create GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial dashboard commit"
   git remote add origin https://github.com/your-username/pet-dashboard.git
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Deploy from your repository
   - Share the URL with your team

3. **Update Data**
   - Replace CSV files in `/data` folder
   - Push to GitHub → auto-deploys

---

## Option 2: 📊 **Google Sheets + Looker Studio Integration**

### For Teams Preferring Google Ecosystem

#### Step A: Export to Google Sheets
```python
# Run this script to export dashboard data to Google Sheets format
import sys
sys.path.append('src')
from etl import process_pet_csv
import pandas as pd

# Process your data
people_df, hierarchy_df = process_pet_csv('data/PET Resource Allocation (11).csv')

# Export for Google Sheets
people_df.to_csv('exports/bps_resources.csv', index=False)
hierarchy_df.to_csv('exports/bps_hierarchy.csv', index=False)

# Create summary for Looker
summary = people_df.groupby(['vp_org', 'supervisor']).agg({
    'workstream1_completed': ['sum', 'count'],
    'total_allocation_pct': 'mean'
}).round(2)
summary.to_csv('exports/bps_summary.csv')
```

#### Step B: Looker Studio Dashboard
1. **Upload CSVs to Google Drive**
2. **Create Looker Studio Report**
   - Connect to Google Sheets data
   - Create charts for:
     - VP completion rates
     - Supervisor team sizes
     - Workstream 1 completion tracking
3. **Share with team**

---

## Option 3: 🐳 **Docker + Internal Hosting**

### For IT-Managed Deployment

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

#### Deploy Commands
```bash
# Build image
docker build -t pet-dashboard .

# Run container
docker run -p 8501:8501 pet-dashboard
```

---

## Option 4: 📑 **Google Slides Reporting**

### For Executive Presentations

#### Auto-Generate Slides
```python
# Create executive summary for slides
def create_executive_summary():
    people_df, _ = process_pet_csv('data/PET Resource Allocation (11).csv')
    bps_df = people_df[people_df['l3_org'] == 'Business Platform Services (Kashi Kakarla)']
    
    summary = {
        'total_resources': len(bps_df),
        'ws1_completion_rate': f"{bps_df['workstream1_completed'].sum() / len(bps_df) * 100:.1f}%",
        'top_performing_vp': bps_df.groupby('vp_org')['workstream1_completed'].mean().idxmax(),
        'completion_by_vp': bps_df.groupby('vp_org')['workstream1_completed'].mean() * 100
    }
    return summary

# Export summary
summary = create_executive_summary()
print("Executive Summary for Google Slides:")
print(f"• Total BPS Resources: {summary['total_resources']}")
print(f"• Workstream 1 Completion: {summary['ws1_completion_rate']}")
print(f"• Top Performing VP: {summary['top_performing_vp']}")
```

---

## Option 5: 💾 **Shared Google Drive Folder**

### For Simple File Sharing

#### Setup Shared Folder Structure
```
📁 PET Dashboard (Shared Drive)
├── 📁 Data
│   ├── PET Resource Allocation (11).csv
│   └── PET Resource Allocation (12).csv (next week)
├── 📁 Reports
│   ├── BPS_Weekly_Report.csv
│   └── VP_Completion_Summary.csv
├── 📁 Dashboard Files
│   ├── app.py
│   ├── requirements.txt
│   └── src/
└── 📄 Setup_Instructions.md
```

#### Automated Reporting Script
```python
# weekly_report.py - Run this weekly to update reports
def generate_weekly_report():
    people_df, hierarchy_df = process_pet_csv('latest_data.csv')
    
    # BPS summary report
    bps_report = people_df[people_df['l3_org'] == 'Business Platform Services (Kashi Kakarla)']
    bps_summary = bps_report.groupby('vp_org').agg({
        'workstream1_completed': ['sum', 'count'],
        'total_allocation_pct': 'mean'
    })
    
    # Save to shared drive
    bps_summary.to_csv('shared_drive/Reports/BPS_Weekly_Report.csv')
    
    print("✅ Weekly report generated and saved to shared drive")
```

---

## 🎯 **Recommendation: Streamlit Cloud**

### Why Streamlit Cloud is Best for Your Use Case:

1. **Zero Infrastructure** - No IT setup needed
2. **Real-time Updates** - Upload new CSV → instant refresh
3. **Full Functionality** - Keeps all search, filter, and drilldown features
4. **Easy Sharing** - Just send URL to team
5. **Version Control** - GitHub integration for change tracking

### Quick Start (15 minutes):
1. Push code to GitHub
2. Deploy on Streamlit Cloud
3. Share URL with team
4. Update data by uploading new CSVs

---

## 📊 **Data Update Workflows**

### For Any Deployment Option:

#### Weekly Data Updates
```bash
# 1. Export new data from your source system
# 2. Replace files in data/ folder
# 3. Dashboard auto-updates (Streamlit Cloud) or run refresh script
```

#### Monthly Reports
```python
# Generate monthly summary for stakeholders
def monthly_stakeholder_report():
    # Create executive summary
    # Export to Google Sheets
    # Send email with Looker Studio link
```

---

## 🔒 **Security Considerations**

- **Streamlit Cloud**: Private repos for sensitive data
- **Google Sheets**: Proper sharing permissions
- **Docker**: Internal network deployment
- **Data Anonymization**: Remove sensitive employee info if needed

---

## 🚀 **Next Steps**

1. **Choose deployment method** based on team preference
2. **Set up automated data pipeline** for weekly updates
3. **Train team** on dashboard usage
4. **Establish reporting cadence** (weekly/monthly reviews)

Would you like me to help you set up any of these deployment options?
