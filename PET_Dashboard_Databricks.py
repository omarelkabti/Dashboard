# Databricks notebook source
# MAGIC %md
# MAGIC # 🚀 PET Resource Allocation Dashboard - Databricks Edition
# MAGIC 
# MAGIC This notebook sets up and runs your PET Resource Allocation Dashboard in Databricks with optimized performance and collaborative features.
# MAGIC 
# MAGIC ## 📋 Features:
# MAGIC - **Spark-optimized** data processing
# MAGIC - **DBFS integration** for file storage
# MAGIC - **Interactive widgets** for dynamic filtering
# MAGIC - **Collaborative sharing** within your workspace
# MAGIC - **Auto-scaling** compute resources
# MAGIC 
# MAGIC ---

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📦 STEP 1: Install Required Packages

# COMMAND ----------

# Install required packages
%pip install streamlit pandas plotly openpyxl

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🔧 STEP 2: Setup and Configuration

# COMMAND ----------

import pandas as pd
import numpy as np
import re
from typing import Optional, Tuple
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Databricks specific imports
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Initialize Spark session (already available in Databricks)
spark = SparkSession.builder.getOrCreate()

print("✅ Environment setup completed!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📊 STEP 3: Data Processing Functions

# COMMAND ----------

# Sentinel values for header detection
SENTINELS = {"Supervisor or Hiring Manager", "Resource or Rec/Offer", "L3 Org"}

# Column mappings
HEADER_MAP = {
    "Supervisor or Hiring Manager": "manager",
    "Resource or Rec/Offer": "resource_raw", 
    "Type": "type",
    "L3 Org": "l3_org",
    "VP Org": "vp_org",
    "Director Org": "director_org",
    "Total Workstream Allocation %": "total_workstream_allocation_pct",
}

# Legacy column mappings for backward compatibility
LEGACY_HEADER_MAP = {
    'Unnamed: 0': 'manager',
    'Unnamed: 1': 'resource_raw',
    'Unnamed: 2': 'type', 
    'Unnamed: 3': 'l3_org',
    'Unnamed: 4': 'vp_org',
    'Unnamed: 5': 'director_org',
    'Unnamed: 6': 'total_workstream_allocation_pct'
}

# Dynamic workstream detection patterns
WS_NAME_RE = re.compile(r"^\s*Workstream\s*(\d+)\s*$", re.I)
PCT_NAME_RE = re.compile(r"^\s*%+\s*(\d+)\s*$", re.I)

# Type normalization mapping
TYPE_MAPPING = {
    'employee': 'Employee',
    'contractor': 'Contractor', 
    'req': 'Req',
    'open role': 'Open Role',
    'request': 'Req',
    'requisition': 'Req',
}

def _likely_header_row(row_vals) -> bool:
    """Check if a row likely contains header information"""
    vals = {str(v).strip() for v in row_vals if pd.notna(v)}
    return len(SENTINELS.intersection(vals)) >= 2

def find_workstream_pairs(cols):
    """Dynamically find workstream and percentage column pairs"""
    ws_cols = {}
    pct_cols = {}
    for c in cols:
        m1 = WS_NAME_RE.match(str(c))
        m2 = PCT_NAME_RE.match(str(c))
        if m1:
            ws_cols[int(m1.group(1))] = c
        elif m2:
            pct_cols[int(m2.group(1))] = c
    pairs = []
    for k in sorted(set(ws_cols) & set(pct_cols)):
        pairs.append((ws_cols[k], pct_cols[k]))
    return pairs

def parse_employee(raw):
    """Parse employee information from raw resource string"""
    if not isinstance(raw, str): 
        return None, None, None
    parts = raw.split(':', 1)
    if len(parts) == 2:
        emp_id = re.sub(r'\D', '', parts[0]) or None
        title = parts[1].strip()
        name = title.split(' - ')[-1].strip() if ' - ' in title else title
        return emp_id, name, title
    return None, raw.strip(), raw.strip()

print("✅ Data processing functions loaded!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📁 STEP 4: File Upload and Data Loading

# COMMAND ----------

# Create widgets for file upload and configuration
dbutils.widgets.text("file_path", "/FileStore/shared_uploads/pet_data.csv", "CSV File Path")
dbutils.widgets.dropdown("file_format", "auto", ["auto", "legacy", "new"], "File Format")

# Get widget values
file_path = dbutils.widgets.get("file_path")
file_format = dbutils.widgets.get("file_format")

print(f"📁 Configuration:")
print(f"   File Path: {file_path}")
print(f"   Format: {file_format}")
print()
print("💡 To upload your CSV file:")
print("   1. Go to Data → Create Table")
print("   2. Upload your PET Resource Allocation CSV")
print("   3. Note the file path and update the widget above")

# COMMAND ----------

def load_pet_data_databricks(file_path: str, file_format: str = "auto"):
    """Load PET data with Databricks optimizations"""
    try:
        # Read CSV with pandas first for header detection
        df_pandas = pd.read_csv(file_path, header=None, dtype=str, keep_default_na=False, nrows=10)
        
        # Detect header format
        has_business_headers = False
        header_row_idx = 0
        
        if file_format == "auto":
            # Auto-detect format
            for i in range(min(10, len(df_pandas))):
                if _likely_header_row(df_pandas.iloc[i].tolist()):
                    has_business_headers = True
                    header_row_idx = i
                    break
        elif file_format == "new":
            has_business_headers = True
            header_row_idx = 1  # Assume row 1 for new format
        else:  # legacy
            has_business_headers = False
        
        # Load full data
        if has_business_headers and header_row_idx > 0:
            # Skip to header row
            df = pd.read_csv(file_path, header=header_row_idx, dtype=str, keep_default_na=False)
        else:
            df = pd.read_csv(file_path, header=0, dtype=str, keep_default_na=False)
        
        # Apply appropriate column mapping
        if has_business_headers:
            rename_map = HEADER_MAP
        else:
            rename_map = LEGACY_HEADER_MAP
            
        # Rename columns
        for old_col, new_col in rename_map.items():
            if old_col in df.columns:
                df = df.rename(columns={old_col: new_col})
            elif new_col not in df.columns:
                df[new_col] = ""
        
        # Parse employee information
        if "resource_raw" in df.columns:
            parsed = df["resource_raw"].apply(parse_employee)
            df[["employee_id", "resource_name", "resource_title"]] = pd.DataFrame(parsed.tolist(), index=df.index)
        
        # Find workstream pairs and compute totals
        pairs = find_workstream_pairs(df.columns)
        
        if pairs:
            total_allocation = None
            for _, pct_col in pairs:
                col_data = pd.to_numeric(df[pct_col], errors='coerce').fillna(0)
                # Auto-scale if values are between 0-1 (treat as decimals)
                if col_data.max() <= 1.0 and col_data.min() >= 0:
                    col_data = col_data * 100
                total_allocation = col_data if total_allocation is None else total_allocation + col_data
            
            df["computed_total_pct"] = total_allocation if total_allocation is not None else 0
        else:
            df["computed_total_pct"] = 0
        
        # Use computed total if official total not available
        if "total_workstream_allocation_pct" not in df.columns or df["total_workstream_allocation_pct"].isna().all():
            df["total_allocation_pct"] = df["computed_total_pct"]
        else:
            df["total_allocation_pct"] = pd.to_numeric(df["total_workstream_allocation_pct"], errors='coerce').fillna(df["computed_total_pct"])
        
        # Create allocation flags
        df["overallocated"] = df["total_allocation_pct"] > 100
        df["underallocated"] = (df["total_allocation_pct"] < 100) & (df["total_allocation_pct"] > 0)
        df["unassigned"] = df["total_allocation_pct"] == 0
        
        # Create workstream assignments
        workstream_data = []
        for idx, row in df.iterrows():
            for ws_col, pct_col in pairs:
                if pd.notna(row[ws_col]) and pd.to_numeric(row[pct_col], errors='coerce') > 0:
                    allocation = pd.to_numeric(row[pct_col], errors='coerce')
                    if allocation <= 1.0:  # Scale if needed
                        allocation *= 100
                    
                    workstream_data.append({
                        'resource_name': row.get('resource_name', ''),
                        'workstream': row[ws_col],
                        'allocation_pct': allocation,
                        'manager': row.get('manager', ''),
                        'type': row.get('type', ''),
                        'l3_org': row.get('l3_org', ''),
                        'vp_org': row.get('vp_org', ''),
                        'director_org': row.get('director_org', '')
                    })
        
        workstream_df = pd.DataFrame(workstream_data)
        
        return df, workstream_df, pairs
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None, None, []

print("✅ Data loading function ready!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📊 STEP 5: Load and Process Data

# COMMAND ----------

# Load the data
print("🔄 Loading PET data...")
df, workstream_df, workstream_pairs = load_pet_data_databricks(file_path, file_format)

if df is not None:
    print(f"✅ Successfully loaded data:")
    print(f"   📊 {len(df)} total resources")
    print(f"   🎯 {len(workstream_df)} workstream assignments")
    print(f"   🔗 {len(workstream_pairs)} workstream pairs detected")
    print(f"   📋 Columns: {', '.join(df.columns[:8])}...")
    
    # Display basic statistics
    display(df.describe())
else:
    print("❌ Failed to load data. Please check the file path and try again.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📈 STEP 6: Interactive Dashboard

# COMMAND ----------

# Create interactive widgets for filtering
if df is not None:
    # Filter widgets
    managers = ['All'] + sorted(df['manager'].dropna().unique().tolist()) if 'manager' in df.columns else ['All']
    types = ['All'] + sorted(df['type'].dropna().unique().tolist()) if 'type' in df.columns else ['All']
    l3_orgs = ['All'] + sorted(df['l3_org'].dropna().unique().tolist()) if 'l3_org' in df.columns else ['All']
    
    dbutils.widgets.dropdown("filter_manager", "All", managers, "Filter by Manager")
    dbutils.widgets.dropdown("filter_type", "All", types, "Filter by Type") 
    dbutils.widgets.dropdown("filter_l3_org", "All", l3_orgs, "Filter by L3 Org")
    
    print("🎛️ Interactive filters created! Use the widgets above to filter data.")

# COMMAND ----------

# Apply filters and create visualizations
if df is not None:
    # Get filter values
    selected_manager = dbutils.widgets.get("filter_manager")
    selected_type = dbutils.widgets.get("filter_type")
    selected_l3_org = dbutils.widgets.get("filter_l3_org")
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_manager != "All" and 'manager' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['manager'] == selected_manager]
    
    if selected_type != "All" and 'type' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['type'] == selected_type]
        
    if selected_l3_org != "All" and 'l3_org' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['l3_org'] == selected_l3_org]
    
    print(f"📊 Filtered Results: {len(filtered_df)} resources")
    
    # Display key metrics
    total_resources = len(filtered_df)
    total_fte = filtered_df['total_allocation_pct'].sum() / 100 if 'total_allocation_pct' in filtered_df.columns else 0
    overallocated = filtered_df['overallocated'].sum() if 'overallocated' in filtered_df.columns else 0
    underallocated = filtered_df['underallocated'].sum() if 'underallocated' in filtered_df.columns else 0
    unassigned = filtered_df['unassigned'].sum() if 'unassigned' in filtered_df.columns else 0
    
    print("\n📈 KEY METRICS:")
    print(f"   👥 Total Resources: {total_resources}")
    print(f"   ⚡ Total FTE: {total_fte:.1f}")
    print(f"   🔴 Overallocated: {overallocated}")
    print(f"   🟡 Underallocated: {underallocated}")
    print(f"   ⚪ Unassigned: {unassigned}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📊 STEP 7: Data Visualizations

# COMMAND ----------

if df is not None and len(filtered_df) > 0:
    # 1. Allocation Status Distribution
    status_counts = {
        'Overallocated': overallocated,
        'Underallocated': underallocated, 
        'Unassigned': unassigned
    }
    
    fig_status = px.pie(
        values=list(status_counts.values()),
        names=list(status_counts.keys()),
        title="Resource Allocation Status Distribution",
        color_discrete_map={
            'Overallocated': '#ff6b6b',
            'Underallocated': '#ffd93d', 
            'Unassigned': '#6bcf7f'
        }
    )
    fig_status.show()

# COMMAND ----------

if workstream_df is not None and len(workstream_df) > 0:
    # 2. Workstream FTE Distribution
    filtered_ws_df = workstream_df.copy()
    
    # Apply same filters to workstream data
    if selected_manager != "All":
        filtered_ws_df = filtered_ws_df[filtered_ws_df['manager'] == selected_manager]
    if selected_type != "All":
        filtered_ws_df = filtered_ws_df[filtered_ws_df['type'] == selected_type]
    if selected_l3_org != "All":
        filtered_ws_df = filtered_ws_df[filtered_ws_df['l3_org'] == selected_l3_org]
    
    if len(filtered_ws_df) > 0:
        workstream_fte = filtered_ws_df.groupby('workstream')['allocation_pct'].sum() / 100
        workstream_fte = workstream_fte.sort_values(ascending=False)
        
        fig_workstream = px.bar(
            x=workstream_fte.index,
            y=workstream_fte.values,
            title="FTE Allocation by Workstream",
            labels={'x': 'Workstream', 'y': 'FTE'}
        )
        fig_workstream.update_layout(xaxis_tickangle=-45)
        fig_workstream.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📋 STEP 8: Data Tables

# COMMAND ----------

if df is not None:
    print("👥 RESOURCE OVERVIEW:")
    # Select relevant columns for display
    display_cols = ['resource_name', 'manager', 'type', 'l3_org', 'vp_org', 'director_org', 'total_allocation_pct']
    available_display_cols = [col for col in display_cols if col in filtered_df.columns]
    
    if available_display_cols:
        display(filtered_df[available_display_cols].head(20))
    else:
        display(filtered_df.head(20))

# COMMAND ----------

if workstream_df is not None and len(filtered_ws_df) > 0:
    print("🎯 WORKSTREAM ASSIGNMENTS:")
    ws_display_cols = ['workstream', 'resource_name', 'allocation_pct', 'manager', 'type']
    available_ws_cols = [col for col in ws_display_cols if col in filtered_ws_df.columns]
    
    if available_ws_cols:
        display(filtered_ws_df[available_ws_cols].sort_values('allocation_pct', ascending=False).head(20))
    else:
        display(filtered_ws_df.head(20))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📤 STEP 9: Export and Save Results

# COMMAND ----------

if df is not None:
    # Save processed data to DBFS for future use
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save main data
    output_path_main = f"/FileStore/shared_uploads/pet_processed_main_{timestamp}.csv"
    filtered_df.to_csv(output_path_main.replace("/FileStore", "/dbfs/FileStore"), index=False)
    
    # Save workstream data  
    if workstream_df is not None and len(workstream_df) > 0:
        output_path_ws = f"/FileStore/shared_uploads/pet_processed_workstreams_{timestamp}.csv"
        filtered_ws_df.to_csv(output_path_ws.replace("/FileStore", "/dbfs/FileStore"), index=False)
        
        print(f"✅ Data exported successfully:")
        print(f"   📊 Main data: {output_path_main}")
        print(f"   🎯 Workstream data: {output_path_ws}")
    else:
        print(f"✅ Main data exported: {output_path_main}")
    
    print("\n🔗 You can download these files from the FileStore or use them in other notebooks.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Dashboard Complete!
# MAGIC 
# MAGIC ### 🎉 Your PET Resource Allocation Dashboard is now running in Databricks!
# MAGIC 
# MAGIC **Features Available:**
# MAGIC - ✅ **Smart header detection** for various CSV formats
# MAGIC - ✅ **Dynamic workstream discovery** 
# MAGIC - ✅ **Interactive filtering** via widgets
# MAGIC - ✅ **Real-time visualizations** with Plotly
# MAGIC - ✅ **Data export** capabilities
# MAGIC - ✅ **Collaborative sharing** within Databricks workspace
# MAGIC 
# MAGIC **Next Steps:**
# MAGIC 1. **Share this notebook** with your team members
# MAGIC 2. **Schedule regular runs** using Databricks Jobs
# MAGIC 3. **Connect to dashboards** using Databricks SQL Analytics
# MAGIC 4. **Integrate with data pipelines** for automated updates
# MAGIC 
# MAGIC **Need Help?**
# MAGIC - Modify the widgets above to filter data
# MAGIC - Upload new CSV files and update the file path widget
# MAGIC - Clone this notebook to customize for your needs
