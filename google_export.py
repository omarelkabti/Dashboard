"""
Export PET Dashboard data to Google-friendly formats
Run this script to prepare data for Google Sheets, Looker Studio, etc.
"""

import sys
import os
sys.path.append('src')
from etl import process_pet_csv
import pandas as pd
from datetime import datetime

def create_exports_directory():
    """Create exports directory if it doesn't exist"""
    if not os.path.exists('exports'):
        os.makedirs('exports')

def export_for_google_sheets():
    """Export data in formats optimized for Google Sheets"""
    print("🔄 Processing data for Google Sheets export...")
    
    # Process the latest CSV
    csv_files = [f for f in os.listdir('data') if f.endswith('.csv')]
    if not csv_files:
        print("❌ No CSV files found in data directory")
        return
    
    latest_file = max([f"data/{f}" for f in csv_files], key=os.path.getmtime)
    print(f"📁 Using file: {latest_file}")
    
    people_df, hierarchy_df = process_pet_csv(latest_file)
    
    # Filter for Business Platform Services
    bps_df = people_df[people_df['l3_org'] == 'Business Platform Services (Kashi Kakarla)']
    
    # Export 1: Full BPS Resource Data
    bps_export = bps_df[[
        'resource_name', 'supervisor', 'director_org', 'vp_org',
        'total_allocation_pct', 'workstream1_completed', 'type'
    ]].copy()
    
    bps_export['workstream1_completed'] = bps_export['workstream1_completed'].map({
        True: 'Completed', False: 'Not Completed'
    })
    
    bps_export.to_csv('exports/BPS_Resources.csv', index=False)
    print(f"✅ Exported {len(bps_export)} BPS resources to exports/BPS_Resources.csv")
    
    # Export 2: VP Summary for Leadership
    vp_summary = bps_df.groupby('vp_org').agg({
        'workstream1_completed': ['sum', 'count'],
        'total_allocation_pct': 'mean'
    }).round(2)
    
    vp_summary.columns = ['WS1_Completed', 'Total_Resources', 'Avg_Allocation_Pct']
    vp_summary['Completion_Rate_Pct'] = (vp_summary['WS1_Completed'] / vp_summary['Total_Resources'] * 100).round(1)
    vp_summary['VP_Organization'] = vp_summary.index
    
    vp_summary = vp_summary[['VP_Organization', 'Total_Resources', 'WS1_Completed', 'Completion_Rate_Pct', 'Avg_Allocation_Pct']]
    vp_summary.to_csv('exports/VP_Summary.csv', index=False)
    print(f"✅ Exported VP summary to exports/VP_Summary.csv")
    
    # Export 3: Supervisor Teams for Management
    supervisor_summary = bps_df.groupby('supervisor').agg({
        'workstream1_completed': ['sum', 'count'],
        'total_allocation_pct': 'mean'
    }).round(2)
    
    supervisor_summary.columns = ['WS1_Completed', 'Team_Size', 'Avg_Allocation_Pct']
    supervisor_summary['Completion_Rate_Pct'] = (supervisor_summary['WS1_Completed'] / supervisor_summary['Team_Size'] * 100).round(1)
    supervisor_summary['Supervisor_Email'] = supervisor_summary.index
    
    # Filter out 'Self' and 'Unassigned'
    supervisor_summary = supervisor_summary[
        ~supervisor_summary['Supervisor_Email'].isin(['Self', 'Unassigned'])
    ]
    
    supervisor_summary = supervisor_summary[['Supervisor_Email', 'Team_Size', 'WS1_Completed', 'Completion_Rate_Pct', 'Avg_Allocation_Pct']]
    supervisor_summary = supervisor_summary.sort_values('Completion_Rate_Pct', ascending=False)
    supervisor_summary.to_csv('exports/Supervisor_Teams.csv', index=False)
    print(f"✅ Exported supervisor teams to exports/Supervisor_Teams.csv")
    
    return bps_export, vp_summary, supervisor_summary

def create_looker_studio_data():
    """Create optimized dataset for Looker Studio"""
    print("🔄 Creating Looker Studio dataset...")
    
    csv_files = [f for f in os.listdir('data') if f.endswith('.csv')]
    latest_file = max([f"data/{f}" for f in csv_files], key=os.path.getmtime)
    
    people_df, _ = process_pet_csv(latest_file)
    bps_df = people_df[people_df['l3_org'] == 'Business Platform Services (Kashi Kakarla)']
    
    # Create flat dataset optimized for Looker Studio
    looker_data = bps_df[[
        'resource_name', 'supervisor', 'director_org', 'vp_org', 'l3_org',
        'total_allocation_pct', 'workstream1_completed', 'type',
        'overallocated', 'underallocated', 'unassigned'
    ]].copy()
    
    # Add calculated fields for Looker
    looker_data['ws1_status'] = looker_data['workstream1_completed'].map({
        True: 'Completed', False: 'Not Completed'
    })
    
    looker_data['allocation_status'] = 'Properly Allocated'
    looker_data.loc[looker_data['overallocated'] == True, 'allocation_status'] = 'Overallocated'
    looker_data.loc[looker_data['underallocated'] == True, 'allocation_status'] = 'Underallocated'
    looker_data.loc[looker_data['unassigned'] == True, 'allocation_status'] = 'Unassigned'
    
    # Add date for time series
    looker_data['report_date'] = datetime.now().strftime('%Y-%m-%d')
    
    # Clean supervisor names for display
    looker_data['supervisor_clean'] = looker_data['supervisor'].apply(
        lambda x: x.split('@')[0].replace('_', ' ').title() if '@' in str(x) else str(x)
    )
    
    looker_data.to_csv('exports/Looker_Studio_Data.csv', index=False)
    print(f"✅ Exported Looker Studio dataset to exports/Looker_Studio_Data.csv")
    
    return looker_data

def create_executive_summary():
    """Create executive summary for Google Slides/Docs"""
    print("🔄 Creating executive summary...")
    
    csv_files = [f for f in os.listdir('data') if f.endswith('.csv')]
    latest_file = max([f"data/{f}" for f in csv_files], key=os.path.getmtime)
    
    people_df, _ = process_pet_csv(latest_file)
    bps_df = people_df[people_df['l3_org'] == 'Business Platform Services (Kashi Kakarla)']
    
    # Calculate key metrics
    total_resources = len(bps_df)
    ws1_completed = bps_df['workstream1_completed'].sum()
    completion_rate = (ws1_completed / total_resources * 100)
    
    # VP performance
    vp_performance = bps_df.groupby('vp_org')['workstream1_completed'].agg(['sum', 'count'])
    vp_performance['rate'] = (vp_performance['sum'] / vp_performance['count'] * 100).round(1)
    top_vp = vp_performance.loc[vp_performance['rate'].idxmax()]
    
    # Supervisor performance
    supervisor_performance = bps_df[~bps_df['supervisor'].isin(['Self', 'Unassigned'])].groupby('supervisor')['workstream1_completed'].agg(['sum', 'count'])
    supervisor_performance['rate'] = (supervisor_performance['sum'] / supervisor_performance['count'] * 100).round(1)
    top_supervisor = supervisor_performance.loc[supervisor_performance['rate'].idxmax()]
    
    # Create summary text
    summary = f"""
# Business Platform Services - Workstream 1 Completion Summary
**Report Date:** {datetime.now().strftime('%B %d, %Y')}

## 🎯 Key Metrics
- **Total Resources:** {total_resources:,}
- **Workstream 1 Completion:** {ws1_completed}/{total_resources} ({completion_rate:.1f}%)
- **Top Performing VP Org:** {top_vp.name} ({top_vp['rate']:.1f}% completion)
- **Top Performing Supervisor:** {top_supervisor.name.split('@')[0].replace('_', ' ').title()} ({top_supervisor['rate']:.1f}% completion)

## 📊 VP Organization Performance
{vp_performance.sort_values('rate', ascending=False).to_string()}

## 🚨 Action Items
- Focus on VP orgs with <80% completion rate
- Recognize top performing supervisors
- Address unassigned resources: {bps_df[bps_df['supervisor'] == 'Unassigned'].shape[0]} resources

## 📈 Weekly Trends
- Upload this data to Google Sheets for trend tracking
- Set up Looker Studio dashboard for real-time monitoring
    """
    
    with open('exports/Executive_Summary.md', 'w') as f:
        f.write(summary)
    
    print("✅ Created executive summary in exports/Executive_Summary.md")
    return summary

def main():
    """Run all export functions"""
    print("🚀 Starting PET Dashboard data export for Google ecosystem...")
    
    create_exports_directory()
    
    # Run exports
    bps_data, vp_summary, supervisor_teams = export_for_google_sheets()
    looker_data = create_looker_studio_data()
    exec_summary = create_executive_summary()
    
    print("\n" + "="*60)
    print("✅ ALL EXPORTS COMPLETED!")
    print("="*60)
    print("📁 Files created in exports/ directory:")
    print("   • BPS_Resources.csv (for Google Sheets)")
    print("   • VP_Summary.csv (for leadership dashboards)")
    print("   • Supervisor_Teams.csv (for management reports)")
    print("   • Looker_Studio_Data.csv (for Looker Studio)")
    print("   • Executive_Summary.md (for Google Docs/Slides)")
    print("\n🔄 Next steps:")
    print("   1. Upload CSV files to Google Drive")
    print("   2. Create Looker Studio dashboard")
    print("   3. Share links with your team")
    print("   4. Schedule weekly runs of this script")

if __name__ == "__main__":
    main()
