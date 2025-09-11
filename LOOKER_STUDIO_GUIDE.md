# 🎯 PET Dashboard - Google Looker Studio Setup Guide

## 🌟 Why Looker Studio for Your Team?

- **🆓 Completely Free** - No subscription costs
- **🤝 Perfect Team Sharing** - Uses Google accounts (like Google Docs)
- **📱 Mobile Access** - Works on phones/tablets
- **🔄 Auto-Refresh** - Data updates automatically
- **🎨 Professional Charts** - Beautiful, interactive visualizations
- **🔗 Easy Links** - Share via URL or embed in websites

## 🚀 Quick Setup (15 Minutes)

### Step 1: Prepare Your Data
```bash
# Run this to convert your CSV to Looker-friendly format
python3 Looker_Studio_Setup.py

# This creates 4 optimized files:
# - pet_resources_*.csv (main data)
# - pet_workstreams_*.csv (workstream assignments) 
# - pet_summary_*.csv (key metrics)
# - pet_workstream_summary_*.csv (workstream totals)
```

### Step 2: Upload to Google Sheets
1. **Upload CSVs to Google Drive**
   - Go to [Google Drive](https://drive.google.com)
   - Upload the 4 CSV files from `looker_data/` folder

2. **Convert to Google Sheets**
   - Right-click each CSV → "Open with" → "Google Sheets"
   - Click "Import" to convert to Sheets format
   - Rename sheets to: "PET Resources", "PET Workstreams", "PET Summary", "Workstream Summary"

### Step 3: Create Looker Studio Dashboard
1. **Go to Looker Studio**
   - Visit [lookerstudio.google.com](https://lookerstudio.google.com)
   - Click "Create" → "Report"

2. **Connect Data Sources**
   - Click "Add Data" → "Google Sheets"
   - Select your 4 converted sheets
   - Click "Add to Report"

### Step 4: Build Your Dashboard

## 📊 Recommended Dashboard Layout

### Page 1: Executive Overview
**Top Row - Key Metrics (Scorecards)**
- Total Resources: `SUM(resource_count)` from Summary table
- Total FTE: `SUM(total_fte)` from Resources table  
- Employees: `COUNT(is_employee=TRUE)` from Resources table
- Contractors: `COUNT(is_contractor=TRUE)` from Resources table

**Second Row - Allocation Status**
- **Pie Chart**: `allocation_status` from Resources table
- **Bar Chart**: Count by `type` (Employee/Contractor/Req)

**Third Row - Organization Breakdown**
- **Stacked Bar**: `l3_org` with `allocation_status` breakdown
- **Table**: Top managers by resource count

### Page 2: Workstream Analysis
**Top Section**
- **Bar Chart**: `workstream` vs `total_fte` from Workstream Summary
- **Metric**: Total Active Workstreams

**Bottom Section**
- **Table**: Detailed workstream assignments from Workstreams table
- **Filters**: Manager, Organization, Resource Type

### Page 3: Resource Details
- **Table**: Complete resource list from Resources table
- **Advanced Filters**: All fields available
- **Download Option**: Enable data export

## 🎨 Chart Configuration Guide

### Key Metrics (Scorecards)
```
Chart Type: Scorecard
Data Source: PET Summary
Metric: metric_value
Dimension: metric_name
Filter: metric_name = "Total Resources" (etc.)
```

### Allocation Status Pie Chart
```
Chart Type: Pie Chart  
Data Source: PET Resources
Dimension: allocation_status
Metric: COUNT(resource_name)
Colors: 
  - Overallocated: #ff6b6b (red)
  - Underallocated: #ffd93d (yellow) 
  - Properly Allocated: #6bcf7f (green)
  - Unassigned: #9ca3af (gray)
```

### Workstream FTE Bar Chart
```
Chart Type: Column Chart
Data Source: Workstream Summary  
Dimension: workstream
Metric: total_fte
Sort: total_fte DESC
```

### Resource Details Table
```
Chart Type: Table
Data Source: PET Resources
Dimensions: resource_name, manager, type, l3_org, allocation_status
Metrics: fte, total_allocation_pct
```

## 🎛️ Adding Filters

### Date Range Filter
- **Type**: Date Range Control
- **Data Source**: Any (will apply to all charts)
- **Default**: Last 30 days

### Organization Filter
- **Type**: Drop-down List
- **Data Source**: PET Resources
- **Control Field**: l3_org
- **Allow Multiple**: Yes

### Manager Filter  
- **Type**: Drop-down List
- **Data Source**: PET Resources
- **Control Field**: manager
- **Allow Multiple**: Yes

### Resource Type Filter
- **Type**: Drop-down List  
- **Data Source**: PET Resources
- **Control Field**: type
- **Allow Multiple**: Yes

## 📱 Sharing Your Dashboard

### Option 1: Share by Link
1. Click "Share" in top-right
2. Set permissions:
   - **Viewer**: Can see dashboard only
   - **Editor**: Can modify dashboard
3. Copy link and send to team

### Option 2: Email Sharing
1. Click "Share" → "Invite people"
2. Enter email addresses
3. Set permission level
4. Add message and send

### Option 3: Embed in Website
1. Click "Share" → "Embed"
2. Copy embed code
3. Paste in your website/wiki

## 🔄 Auto-Refresh Setup

### Method 1: Google Sheets Auto-Import
```javascript
// In Google Sheets, use Apps Script to auto-import from Drive
function autoImportCSV() {
  // Script to automatically import updated CSV files
  // Runs on schedule (hourly/daily)
}
```

### Method 2: Manual Refresh
- Upload new CSV files to Drive
- Replace data in existing Google Sheets
- Looker Studio updates automatically

## 💡 Pro Tips

### Performance Optimization
- **Use Extracts**: For large datasets (>100k rows)
- **Aggregate Data**: Pre-calculate summaries when possible
- **Limit Date Ranges**: Use default filters to reduce data load

### Design Best Practices
- **Consistent Colors**: Use your company brand colors
- **Clear Labels**: Add descriptive chart titles
- **Mobile-Friendly**: Test on phone screens
- **Progressive Disclosure**: Use drill-down charts

### Collaboration
- **Template Dashboards**: Create reusable templates
- **Comment System**: Use Looker's commenting for feedback
- **Version Control**: Make copies before major changes

## 🔧 Troubleshooting

### Common Issues

**❌ "Data source not found"**
- ✅ Ensure Google Sheets are in same Google account
- ✅ Check sharing permissions on sheets

**❌ "Charts not updating"**  
- ✅ Refresh data source (Data → Refresh data)
- ✅ Check if Google Sheets have new data

**❌ "Slow loading dashboards"**
- ✅ Add date range filters
- ✅ Reduce number of charts per page
- ✅ Use data extracts for large datasets

**❌ "Sharing not working"**
- ✅ Check if recipients have Google accounts
- ✅ Verify Google Sheets permissions
- ✅ Use "Anyone with link" for easier sharing

## 📈 Advanced Features

### Calculated Fields
Create custom metrics directly in Looker:

**FTE Utilization Rate**
```
SUM(fte) / COUNT(resource_name)
```

**Over-allocation Rate**  
```
COUNT(CASE WHEN overallocated = true THEN resource_name END) / COUNT(resource_name)
```

**Top Workstreams**
```
RANK(SUM(total_fte), SUM(total_fte) DESC)
```

### Drill-Down Reports
- **Org → Team → Individual**: Click org to see teams, teams to see people
- **Workstream → Resources**: Click workstream to see assigned people
- **Manager → Direct Reports**: Click manager to see their team

## ✅ Success Checklist

- [ ] Data processed with `Looker_Studio_Setup.py`
- [ ] 4 CSV files uploaded to Google Drive  
- [ ] CSV files converted to Google Sheets
- [ ] Looker Studio report created
- [ ] Data sources connected
- [ ] Key metrics scorecards added
- [ ] Allocation status pie chart created
- [ ] Workstream analysis charts built
- [ ] Filters configured
- [ ] Dashboard shared with team
- [ ] Mobile view tested
- [ ] Auto-refresh method chosen

**🎉 Your team dashboard is now live and shareable!**

## 🆘 Need Help?

- **Looker Studio Help**: [support.google.com/looker-studio](https://support.google.com/looker-studio)
- **Google Sheets Help**: [support.google.com/sheets](https://support.google.com/sheets)
- **Video Tutorials**: Search "Looker Studio tutorial" on YouTube
