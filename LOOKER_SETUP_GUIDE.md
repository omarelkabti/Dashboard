# 📊 Looker Studio Dashboard Setup Guide

## Quick Start (15 minutes)

### Step 1: Export Data
```bash
python3 google_export.py
```
This creates optimized CSV files in the `exports/` folder.

### Step 2: Upload to Google Drive
1. **Create folder**: "PET Dashboard Data" in your Google Drive
2. **Upload** all files from `exports/` folder
3. **Share** folder with your team (Viewer access)

### Step 3: Create Looker Studio Dashboard
1. Go to [lookerstudio.google.com](https://lookerstudio.google.com)
2. **Create** → **Report**
3. **Add Data** → **Google Sheets** → Select your uploaded files

---

## 📋 Recommended Dashboard Layout

### Page 1: Executive Overview
**Charts to Create:**

#### 1. Key Metrics (Scorecard)
- **Data Source**: `Looker_Studio_Data.csv`
- **Metrics**: 
  - Total Resources: `COUNT(resource_name)`
  - WS1 Completion Rate: `COUNT(ws1_status = "Completed") / COUNT(resource_name) * 100`
  - Avg Allocation: `AVG(total_allocation_pct)`

#### 2. VP Organization Performance (Bar Chart)
- **X-Axis**: `vp_org`
- **Y-Axis**: `Completion Rate %`
- **Metric**: `COUNT(ws1_status = "Completed") / COUNT(resource_name) * 100`
- **Sort**: Descending by completion rate
- **Color**: Conditional formatting (Green >90%, Yellow 70-90%, Red <70%)

#### 3. Allocation Status Distribution (Pie Chart)
- **Dimension**: `allocation_status`
- **Metric**: `COUNT(resource_name)`

#### 4. Top Performing Supervisors (Table)
- **Dimensions**: `supervisor_clean`
- **Metrics**: 
  - Team Size: `COUNT(resource_name)`
  - Completed: `COUNT(ws1_status = "Completed")`
  - Rate: `COUNT(ws1_status = "Completed") / COUNT(resource_name) * 100`

### Page 2: Detailed Analysis
**Charts to Create:**

#### 1. Resource Details (Table)
- **Dimensions**: `resource_name`, `supervisor_clean`, `vp_org`, `ws1_status`
- **Metrics**: `total_allocation_pct`
- **Filters**: Add filters for VP Org, Supervisor, WS1 Status

#### 2. Allocation vs Completion (Scatter Plot)
- **X-Axis**: `total_allocation_pct`
- **Y-Axis**: `ws1_status` (converted to 0/1)
- **Color**: `vp_org`

---

## 🎨 Styling Recommendations

### Color Scheme (Intuit Brand)
- **Primary Blue**: #0052CC
- **Green (Completed)**: #00A86B
- **Red (Issues)**: #DE350B
- **Yellow (Warning)**: #FFAB00
- **Gray (Neutral)**: #626F86

### Conditional Formatting
```
Completion Rate:
• ≥90% = Green
• 70-89% = Yellow  
• <70% = Red

Allocation Status:
• Properly Allocated = Green
• Over/Under = Yellow
• Unassigned = Red
```

---

## 🔄 Data Refresh Setup

### Option A: Manual Weekly Update
1. Run `python3 google_export.py` weekly
2. Replace files in Google Drive
3. Looker Studio auto-refreshes

### Option B: Google Apps Script Automation
```javascript
// Google Apps Script to automate data refresh
function refreshDashboardData() {
  // This would connect to your data source
  // and update the Google Sheets automatically
  
  var spreadsheet = SpreadsheetApp.openById('YOUR_SHEET_ID');
  var sheet = spreadsheet.getSheetByName('BPS_Data');
  
  // Your data refresh logic here
  
  console.log('Dashboard data refreshed at: ' + new Date());
}

// Set up trigger to run weekly
function createTimeDrivenTriggers() {
  ScriptApp.newTrigger('refreshDashboardData')
    .timeBased()
    .everyWeeks(1)
    .onWeekDay(ScriptApp.WeekDay.MONDAY)
    .create();
}
```

---

## 📊 Advanced Features

### Interactive Filters
Add these filters to your dashboard:
- **Date Range**: For historical tracking
- **VP Organization**: Drill down by VP
- **Supervisor**: Filter by team lead
- **Completion Status**: Show completed/incomplete
- **Allocation Status**: Focus on issues

### Calculated Fields
Create these in Looker Studio:

#### Completion Rate by VP
```sql
COUNT(CASE WHEN ws1_status = "Completed" THEN resource_name END) / 
COUNT(resource_name) * 100
```

#### Performance Grade
```sql
CASE 
  WHEN Completion_Rate >= 90 THEN "Excellent"
  WHEN Completion_Rate >= 80 THEN "Good" 
  WHEN Completion_Rate >= 70 THEN "Needs Improvement"
  ELSE "Critical"
END
```

#### Team Size Category
```sql
CASE 
  WHEN Team_Size >= 30 THEN "Large Team (30+)"
  WHEN Team_Size >= 15 THEN "Medium Team (15-29)"
  ELSE "Small Team (<15)"
END
```

---

## 📱 Mobile Optimization

### Mobile-Friendly Design
- **Use scorecards** for key metrics
- **Simple bar charts** instead of complex visuals
- **Larger text** for readability
- **Vertical layout** for phone screens

### Mobile Dashboard Checklist
- [ ] Key metrics visible without scrolling
- [ ] Charts load quickly
- [ ] Filters are touch-friendly
- [ ] Text is readable on small screens

---

## 🔗 Sharing & Permissions

### Team Access Setup
1. **Dashboard URL**: Share the Looker Studio report URL
2. **View Access**: Team members need view access to Google Sheets
3. **Edit Access**: Only admins should have edit access to prevent accidental changes

### Embedding Options
- **Google Sites**: Embed dashboard in internal sites
- **Email Reports**: Schedule automated email reports
- **Google Slides**: Export charts for presentations

---

## 📈 Suggested Weekly Cadence

### Monday: Data Refresh
- Run export script
- Update Google Sheets
- Review dashboard for issues

### Wednesday: Team Review
- Share dashboard link in team meeting
- Discuss completion rates
- Identify action items

### Friday: Executive Summary
- Export key metrics for leadership
- Create slide deck if needed
- Plan next week's focus areas

---

## 🛠 Troubleshooting

### Common Issues & Solutions

#### "Data source not found"
- Check Google Sheets permissions
- Verify file hasn't been moved/deleted
- Re-link data source in Looker Studio

#### "Charts not updating"
- Refresh data in Looker Studio (⟳ button)
- Check if new data was uploaded to Google Sheets
- Verify calculated fields are correct

#### "Slow performance"
- Limit data to last 3-6 months
- Use filters to reduce dataset size
- Optimize calculated fields

---

## 🚀 Next Steps

1. **Create the dashboard** using this guide
2. **Share with team** and gather feedback
3. **Set up automated refresh** (weekly)
4. **Train team members** on dashboard usage
5. **Establish KPIs** and success metrics

**Questions?** Check the main `DEPLOYMENT_OPTIONS.md` for alternative approaches!
