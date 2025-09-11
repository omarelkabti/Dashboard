"""
Schema definitions and column mappings for PET Resource Allocation Dashboard
"""

import re

# Sentinel values for header detection
SENTINELS = {"Supervisor or Hiring Manager", "Resource or Rec/Offer", "L3 Org"}

# Column mappings from business headers to normalized names
HEADER_MAP = {
    "Supervisor or Hiring Manager": "manager",
    "Resource or Rec/Offer": "resource_raw",
    "Type": "type",
    "L3 Org": "l3_org",
    "VP Org": "vp_org",
    "Director Org": "director_org",
    "Total Workstream Allocation %": "total_workstream_allocation_pct",
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
    # Add more variants as needed
}

# Expected data types for validation
EXPECTED_DTYPES = {
    'manager': 'string',
    'resource_raw': 'string',
    'type': 'string',
    'l3_org': 'string',
    'vp_org': 'string',
    'director_org': 'string',
    'total_allocation_pct': 'numeric'
}

# Allocation status thresholds
ALLOCATION_THRESHOLDS = {
    'underallocated': 100,
    'overallocated': 100,
    'unassigned': 0
}

# Tolerance for allocation mismatch validation
ALLOCATION_TOLERANCE = 1.0

# File watching configuration
WATCH_PATTERN = r'PET Resource Allocation.*\.csv'
WATCH_INTERVAL_SECONDS = 300  # 5 minutes
MAX_BACKUP_FILES = 5
