#!/usr/bin/env python3
"""
PET Resource Allocation Dashboard - Looker Studio Data Preparation
Processes your CSV files into Google Sheets format for Looker Studio
"""

import pandas as pd
import numpy as np
from pathlib import Path
import os
from datetime import datetime

# Import our ETL functions
from src.etl import process_pet_csv

def prepare_data_for_looker(csv_file_path, output_dir="looker_data"):
    """
    Process PET CSV data and create Looker Studio-ready files
    
    Args:
        csv_file_path: Path to your PET CSV file
        output_dir: Directory to save processed files
    """
    print("🔄 Processing PET data for Looker Studio...")
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Process the data using our ETL
    df, workstream_df = process_pet_csv(csv_file_path)
    
    print(f"✅ Processed {len(df)} resources and {len(workstream_df)} workstream assignments")
    
    # 1. Create main resources table
    resources_table = df[[
        'resource_name', 'manager', 'type', 'l3_org', 'vp_org', 'director_org',
        'total_allocation_pct', 'overallocated', 'underallocated', 'unassigned'
    ]].copy()
    
    # Add calculated fields for Looker
    resources_table['allocation_status'] = resources_table.apply(
        lambda row: 'Overallocated' if row['overallocated'] 
        else 'Underallocated' if row['underallocated']
        else 'Unassigned' if row['unassigned']
        else 'Properly Allocated', axis=1
    )
    
    resources_table['fte'] = resources_table['total_allocation_pct'] / 100
    resources_table['is_employee'] = resources_table['type'] == 'Employee'
    resources_table['is_contractor'] = resources_table['type'] == 'Contractor'
    
    # 2. Create workstream assignments table
    if len(workstream_df) > 0:
        workstreams_table = workstream_df[[
            'resource_name', 'workstream', 'allocation_pct', 'manager', 
            'type', 'l3_org', 'vp_org', 'director_org'
        ]].copy()
        
        workstreams_table['fte'] = workstreams_table['allocation_pct'] / 100
        workstreams_table['is_employee'] = workstreams_table['type'] == 'Employee'
        workstreams_table['is_contractor'] = workstreams_table['type'] == 'Contractor'
    else:
        workstreams_table = pd.DataFrame()
    
    # 3. Create summary metrics table
    summary_metrics = pd.DataFrame([{
        'metric_name': 'Total Resources',
        'metric_value': len(df),
        'metric_type': 'count'
    }, {
        'metric_name': 'Total FTE',
        'metric_value': df['total_allocation_pct'].sum() / 100,
        'metric_type': 'fte'
    }, {
        'metric_name': 'Employees',
        'metric_value': len(df[df['type'] == 'Employee']),
        'metric_type': 'count'
    }, {
        'metric_name': 'Contractors', 
        'metric_value': len(df[df['type'] == 'Contractor']),
        'metric_type': 'count'
    }, {
        'metric_name': 'Overallocated',
        'metric_value': df['overallocated'].sum(),
        'metric_type': 'count'
    }, {
        'metric_name': 'Underallocated',
        'metric_value': df['underallocated'].sum(),
        'metric_type': 'count'
    }, {
        'metric_name': 'Unassigned',
        'metric_value': df['unassigned'].sum(),
        'metric_type': 'count'
    }])
    
    # 4. Create workstream summary
    if len(workstream_df) > 0:
        workstream_summary = workstream_df.groupby('workstream').agg({
            'allocation_pct': 'sum',
            'resource_name': 'count'
        }).reset_index()
        workstream_summary.columns = ['workstream', 'total_fte_pct', 'resource_count']
        workstream_summary['total_fte'] = workstream_summary['total_fte_pct'] / 100
    else:
        workstream_summary = pd.DataFrame()
    
    # Save all tables
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save to CSV files (for upload to Google Sheets)
    resources_file = f"{output_dir}/pet_resources_{timestamp}.csv"
    resources_table.to_csv(resources_file, index=False)
    print(f"📊 Resources data: {resources_file}")
    
    if len(workstreams_table) > 0:
        workstreams_file = f"{output_dir}/pet_workstreams_{timestamp}.csv"
        workstreams_table.to_csv(workstreams_file, index=False)
        print(f"🎯 Workstreams data: {workstreams_file}")
    
    summary_file = f"{output_dir}/pet_summary_{timestamp}.csv"
    summary_metrics.to_csv(summary_file, index=False)
    print(f"📈 Summary metrics: {summary_file}")
    
    if len(workstream_summary) > 0:
        ws_summary_file = f"{output_dir}/pet_workstream_summary_{timestamp}.csv"
        workstream_summary.to_csv(ws_summary_file, index=False)
        print(f"📋 Workstream summary: {ws_summary_file}")
    
    print("\n✅ Data preparation completed!")
    print("\n📋 Next Steps for Looker Studio:")
    print("1. Upload the CSV files to Google Drive")
    print("2. Import each CSV into Google Sheets")
    print("3. Go to lookerstudio.google.com")
    print("4. Create new report and connect to your Google Sheets")
    print("5. Build charts using the prepared data")
    
    return {
        'resources_file': resources_file,
        'workstreams_file': workstreams_file if len(workstreams_table) > 0 else None,
        'summary_file': summary_file,
        'workstream_summary_file': ws_summary_file if len(workstream_summary) > 0 else None
    }

def create_sample_looker_data():
    """Create sample data to test Looker Studio setup"""
    print("🧪 Creating sample data for Looker Studio testing...")
    
    # Use the sample file
    sample_file = "data/PET_Resource_Allocation_Sample.csv"
    if not os.path.exists(sample_file):
        print("❌ Sample file not found. Please ensure you have data files available.")
        return None
    
    return prepare_data_for_looker(sample_file, "looker_sample_data")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        if os.path.exists(csv_file):
            prepare_data_for_looker(csv_file)
        else:
            print(f"❌ File not found: {csv_file}")
    else:
        # Process all CSV files in data directory
        data_dir = Path("data")
        csv_files = list(data_dir.glob("*.csv"))
        
        if csv_files:
            print(f"📁 Found {len(csv_files)} CSV files")
            for csv_file in csv_files:
                print(f"\n🔄 Processing: {csv_file}")
                try:
                    prepare_data_for_looker(str(csv_file))
                except Exception as e:
                    print(f"❌ Error processing {csv_file}: {e}")
        else:
            print("❌ No CSV files found in data directory")
            print("💡 Creating sample data instead...")
            create_sample_looker_data()
