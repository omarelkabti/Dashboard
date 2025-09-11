"""
ETL pipeline for PET Resource Allocation data with embedded header detection
Based on new-requirements.txt specification
"""

import pandas as pd
import re
import logging
from typing import Tuple, List, Dict, Any

logger = logging.getLogger(__name__)

# Define sentinel values for header detection
SENTINELS = {"Supervisor or Hiring Manager", "Resource or Rec/Offer", "L3 Org"}

# Regex patterns for workstream detection
WS_NAME_RE = re.compile(r"^\s*Workstream\s*(\d+)\s*$", re.I)
PCT_NAME_RE = re.compile(r"^\s*%+\s*(\d+)\s*$", re.I)

def _likely_header_row(row_vals) -> bool:
    """Check if a row likely contains header information"""
    vals = {str(v).strip() for v in row_vals if pd.notna(v)}
    return len(SENTINELS.intersection(vals)) >= 2

def read_with_embedded_header(csv_path: str) -> pd.DataFrame:
    """Read CSV with embedded header detection - handles two-header format"""
    # Read with first row as header to get technical names (Workstream 1, % 1, etc.)
    df = pd.read_csv(csv_path, header=0, dtype=str, keep_default_na=False)
    
    # The business headers are in the first data row
    if len(df) > 0:
        business_headers = df.iloc[0].tolist()
        
        # Create a combined header: use business header where available, technical header otherwise
        combined_headers = []
        for i, (tech_header, business_header) in enumerate(zip(df.columns, business_headers)):
            if business_header and business_header.strip() and business_header.strip() != 'nan':
                combined_headers.append(business_header.strip())
            else:
                combined_headers.append(tech_header)
        
        # Drop the business header row and apply new headers
        df = df.iloc[1:].copy()
        df.columns = combined_headers
    
    return df

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

def compute_total_allocation(df):
    """Compute total allocation with tolerance for missing Total column"""
    pairs = find_workstream_pairs(df.columns)
    if not pairs:
        df["computed_total_pct"] = 0.0
        df["total_allocation_pct"] = df.get("total_workstream_allocation_pct", pd.Series([None]*len(df)))
        return df

    comp = None
    for _, pct_col in pairs:
        col = pd.to_numeric(df[pct_col], errors="coerce")
        if col.dropna().between(0,1).mean() > 0.85:
            col = col * 100.0
        comp = col if comp is None else comp.add(col, fill_value=0)
    df["computed_total_pct"] = comp.fillna(0)
    canon = "Total Workstream Allocation %"
    if canon in df.columns:
        df["total_allocation_pct"] = pd.to_numeric(df[canon], errors="coerce").fillna(df["computed_total_pct"])
    else:
        df["total_allocation_pct"] = df["computed_total_pct"]
    return df

def detect_workstream1_completion(df):
    """Detect Workstream 1 completion status using 'Workstream Status Active' column"""
    df["workstream1_completed"] = False
    
    # Find the first "Workstream Status Active" column (should be for Workstream 1)
    for i, col in enumerate(df.columns):
        if str(col) == "Workstream Status Active":
            status_values = df.iloc[:, i].astype(str).str.strip().str.lower()
            df["workstream1_completed"] = status_values.isin(['y', 'yes', 'true', '1', 'active'])
            break
    
    return df

def load_latest_csv(csv_path: str) -> pd.DataFrame:
    """End-to-end CSV loader with header detection"""
    df = read_with_embedded_header(csv_path)
    
    # rename canonical business columns
    rename_map = {
        "Supervisor or Hiring Manager": "supervisor",
        "Resource or Rec/Offer": "resource_raw",
        "Type": "type",
        "L3 Org": "l3_org",
        "VP Org": "vp_org",
        "Director Org": "director_org",
        "Total Workstream Allocation %": "total_workstream_allocation_pct",
    }
    for k,v in rename_map.items():
        if k in df.columns:
            df = df.rename(columns={k: v})
        else:
            df[v] = ""

    # parse resource fields
    parsed = df["resource_raw"].apply(parse_employee)
    df[["employee_id","resource_name","resource_title"]] = pd.DataFrame(parsed.tolist(), index=df.index)

    # Parse pivot table structure: supervisor followed by their direct reports
    if "supervisor" in df.columns:
        current_supervisor = None
        
        # Reset index to ensure continuous indexing
        df = df.reset_index(drop=True)
        
        for idx in range(len(df)):
            supervisor_value = df.iloc[idx]["supervisor"]
            
            # If this row has a supervisor email, it's a supervisor header row
            if supervisor_value and supervisor_value != "":
                current_supervisor = supervisor_value
                # The supervisor row itself gets marked as "Self" (they supervise themselves)
                df.iloc[idx, df.columns.get_loc("supervisor")] = "Self"
            else:
                # This is a direct report row - assign the current supervisor
                if current_supervisor:
                    df.iloc[idx, df.columns.get_loc("supervisor")] = current_supervisor
                else:
                    df.iloc[idx, df.columns.get_loc("supervisor")] = "Unassigned"

    # totals and completion
    df = compute_total_allocation(df)
    df = detect_workstream1_completion(df)

    # Convert total_allocation_pct to numeric for comparisons
    df["total_allocation_pct"] = pd.to_numeric(df["total_allocation_pct"], errors='coerce').fillna(0)

    # flags
    df["overallocated"] = df["total_allocation_pct"] > 100.0
    df["underallocated"] = df["total_allocation_pct"] < 100.0
    df["unassigned"] = df["total_allocation_pct"] == 0.0
    return df

def create_hierarchical_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Create hierarchical summary for drilldown analysis"""
    summary_rows = []
    
    # Convert boolean columns to int for aggregation
    bool_cols = ['workstream1_completed', 'overallocated', 'underallocated', 'unassigned']
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].astype(int)
    
    # L3 Org level
    l3_summary = df.groupby('l3_org').agg({
        'total_allocation_pct': ['count', 'sum', 'mean'],
        'workstream1_completed': 'sum',
        'overallocated': 'sum',
        'underallocated': 'sum',
        'unassigned': 'sum'
    }).round(2)
    l3_summary.columns = ['resource_count', 'total_allocation_sum', 'avg_allocation', 
                         'ws1_completed_count', 'overallocated_count', 'underallocated_count', 'unassigned_count']
    l3_summary['level'] = 'L3 Org'
    l3_summary['entity'] = l3_summary.index
    l3_summary['parent'] = None
    summary_rows.append(l3_summary.reset_index(drop=True))
    
    # VP Org level
    vp_summary = df.groupby(['l3_org', 'vp_org']).agg({
        'total_allocation_pct': ['count', 'sum', 'mean'],
        'workstream1_completed': 'sum',
        'overallocated': 'sum',
        'underallocated': 'sum',
        'unassigned': 'sum'
    }).round(2)
    vp_summary.columns = ['resource_count', 'total_allocation_sum', 'avg_allocation', 
                         'ws1_completed_count', 'overallocated_count', 'underallocated_count', 'unassigned_count']
    vp_summary['level'] = 'VP Org'
    vp_summary['entity'] = vp_summary.index.get_level_values('vp_org')
    vp_summary['parent'] = vp_summary.index.get_level_values('l3_org')
    summary_rows.append(vp_summary.reset_index(drop=True))
    
    # Director level
    dir_summary = df.groupby(['l3_org', 'vp_org', 'director_org']).agg({
        'total_allocation_pct': ['count', 'sum', 'mean'],
        'workstream1_completed': 'sum',
        'overallocated': 'sum',
        'underallocated': 'sum',
        'unassigned': 'sum'
    }).round(2)
    dir_summary.columns = ['resource_count', 'total_allocation_sum', 'avg_allocation', 
                          'ws1_completed_count', 'overallocated_count', 'underallocated_count', 'unassigned_count']
    dir_summary['level'] = 'Director Org'
    dir_summary['entity'] = dir_summary.index.get_level_values('director_org')
    dir_summary['parent'] = dir_summary.index.get_level_values('vp_org')
    summary_rows.append(dir_summary.reset_index(drop=True))
    
    # Supervisor level (fixed from manager)
    if 'supervisor' in df.columns:
        supervisor_summary = df.groupby(['l3_org', 'vp_org', 'director_org', 'supervisor']).agg({
            'total_allocation_pct': ['count', 'sum', 'mean'],
            'workstream1_completed': 'sum',
            'overallocated': 'sum',
            'underallocated': 'sum',
            'unassigned': 'sum'
        }).round(2)
        supervisor_summary.columns = ['resource_count', 'total_allocation_sum', 'avg_allocation', 
                              'ws1_completed_count', 'overallocated_count', 'underallocated_count', 'unassigned_count']
        supervisor_summary['level'] = 'Supervisor'
        supervisor_summary['entity'] = supervisor_summary.index.get_level_values('supervisor')
        supervisor_summary['parent'] = supervisor_summary.index.get_level_values('director_org')
        summary_rows.append(supervisor_summary.reset_index(drop=True))
    
    # Combine all levels
    all_summary = pd.concat(summary_rows, ignore_index=True)
    all_summary['ws1_completion_rate'] = (all_summary['ws1_completed_count'] / all_summary['resource_count'] * 100).round(1)
    
    return all_summary

def process_pet_csv(file_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Process a PET CSV file through the complete ETL pipeline"""
    try:
        df = load_latest_csv(file_path)
        hierarchy_df = create_hierarchical_summary(df)
        
        logger.info(f"Processed {len(df)} resources")
        return df, hierarchy_df
        
    except Exception as e:
        logger.error(f"Error processing CSV {file_path}: {str(e)}")
        raise
