"""
Filter components for PET Resource Allocation Dashboard
Provides reusable filter widgets and filtering logic
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple

def create_filter_sidebar(people_df: pd.DataFrame, assignments_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Create the filter sidebar with all available filters

    Args:
        people_df: People DataFrame
        assignments_df: Assignments DataFrame

    Returns:
        Dictionary of applied filters
    """

    st.sidebar.header("🔍 Filters")

    filters = {}

    # Resource Type filter
    if 'type' in people_df.columns:
        type_options = sorted(people_df['type'].dropna().unique())
        filters['type'] = st.sidebar.multiselect(
            "Resource Type",
            options=type_options,
            default=[],
            help="Filter by employee type (Employee, Contractor, Req, etc.)"
        )

    # Manager filter
    if 'manager' in people_df.columns:
        manager_options = sorted(people_df['manager'].dropna().unique())
        filters['manager'] = st.sidebar.multiselect(
            "Manager",
            options=manager_options,
            default=[],
            help="Filter by direct manager"
        )

    # Org hierarchy filters
    org_filters = ['l3_org', 'vp_org', 'director_org']
    for org_level in org_filters:
        if org_level in people_df.columns:
            level_name = org_level.replace('_org', '').replace('_', ' ').title()
            options = sorted(people_df[org_level].dropna().unique())
            filters[org_level] = st.sidebar.multiselect(
                f"{level_name} Org",
                options=options,
                default=[],
                help=f"Filter by {level_name.lower()} organization"
            )

    # Workstream filter
    if not assignments_df.empty and 'workstream' in assignments_df.columns:
        workstream_options = sorted(assignments_df['workstream'].dropna().unique())
        filters['workstream'] = st.sidebar.multiselect(
            "Workstream",
            options=workstream_options,
            default=[],
            help="Filter by assigned workstreams"
        )

    # Allocation status filter
    allocation_options = []
    if 'overallocated' in people_df.columns and people_df['overallocated'].any():
        allocation_options.append("Overallocated (>100%)")
    if 'underallocated' in people_df.columns and people_df['underallocated'].any():
        allocation_options.append("Underallocated (<100%)")
    if 'unassigned' in people_df.columns and people_df['unassigned'].any():
        allocation_options.append("Unassigned (0%)")
    if 'allocation_mismatch' in people_df.columns and people_df['allocation_mismatch'].any():
        allocation_options.append("Allocation Mismatch")

    if allocation_options:
        filters['allocation_status'] = st.sidebar.multiselect(
            "Allocation Status",
            options=allocation_options,
            default=[],
            help="Filter by allocation status"
        )

    # Search box
    filters['search'] = st.sidebar.text_input(
        "Search",
        placeholder="Search by name, ID, or title...",
        help="Search across resource names, IDs, and titles"
    )

    # Clear filters button
    if st.sidebar.button("🗑️ Clear All Filters", type="secondary"):
        st.rerun()

    return filters

def apply_filters(people_df: pd.DataFrame, assignments_df: pd.DataFrame, filters: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Apply filters to the dataframes

    Args:
        people_df: People DataFrame
        assignments_df: Assignments DataFrame
        filters: Dictionary of applied filters

    Returns:
        Tuple of filtered (people_df, assignments_df)
    """

    filtered_people = people_df.copy()
    filtered_assignments = assignments_df.copy()

    # Apply type filter
    if filters.get('type'):
        filtered_people = filtered_people[filtered_people['type'].isin(filters['type'])]

    # Apply manager filter
    if filters.get('manager'):
        filtered_people = filtered_people[filtered_people['manager'].isin(filters['manager'])]

    # Apply org hierarchy filters
    org_filters = ['l3_org', 'vp_org', 'director_org']
    for org_level in org_filters:
        if filters.get(org_level):
            filtered_people = filtered_people[filtered_people[org_level].isin(filters[org_level])]

    # Apply workstream filter
    if filters.get('workstream'):
        # Filter assignments by workstream
        filtered_assignments = filtered_assignments[filtered_assignments['workstream'].isin(filters['workstream'])]

        # Filter people to only those with assignments in the selected workstreams
        people_with_assignments = filtered_assignments['employee_id'].unique()
        filtered_people = filtered_people[
            filtered_people['employee_id'].isin(people_with_assignments) |
            filtered_people['employee_id'].isna()  # Include people without IDs if they match other filters
        ]

    # Apply allocation status filters
    allocation_status_filters = filters.get('allocation_status', [])
    if allocation_status_filters:
        status_mask = pd.Series([False] * len(filtered_people), index=filtered_people.index)

        if "Overallocated (>100%)" in allocation_status_filters:
            status_mask |= filtered_people['overallocated'].fillna(False)
        if "Underallocated (<100%)" in allocation_status_filters:
            status_mask |= filtered_people['underallocated'].fillna(False)
        if "Unassigned (0%)" in allocation_status_filters:
            status_mask |= filtered_people['unassigned'].fillna(False)
        if "Allocation Mismatch" in allocation_status_filters:
            status_mask |= filtered_people['allocation_mismatch'].fillna(False)

        filtered_people = filtered_people[status_mask]

    # Apply search filter
    search_term = filters.get('search', '').strip()
    if search_term:
        search_mask = pd.Series([False] * len(filtered_people), index=filtered_people.index)

        # Search in resource name, title, and employee ID
        search_cols = ['resource_name', 'resource_title']
        for col in search_cols:
            if col in filtered_people.columns:
                search_mask |= filtered_people[col].fillna('').str.lower().str.contains(search_term.lower())

        # Search in employee ID
        if 'employee_id' in filtered_people.columns:
            search_mask |= filtered_people['employee_id'].fillna('').str.lower().str.contains(search_term.lower())

        filtered_people = filtered_people[search_mask]

    # Filter assignments to only include people that passed the people filter
    if not filtered_people.empty:
        valid_employee_ids = filtered_people['employee_id'].dropna().unique()
        if len(valid_employee_ids) > 0:
            filtered_assignments = filtered_assignments[
                filtered_assignments['employee_id'].isin(valid_employee_ids)
            ]

    return filtered_people, filtered_assignments

def get_filter_summary(filters: Dict[str, Any]) -> str:
    """
    Generate a summary of applied filters

    Args:
        filters: Dictionary of applied filters

    Returns:
        Summary string
    """
    active_filters = []

    for key, value in filters.items():
        if key == 'search':
            if value and value.strip():
                active_filters.append(f"Search: '{value}'")
        elif isinstance(value, list) and value:
            if key == 'allocation_status':
                active_filters.append(f"{key.replace('_', ' ').title()}: {', '.join(value)}")
            else:
                active_filters.append(f"{key.replace('_', ' ').title()}: {len(value)} selected")

    if not active_filters:
        return "No filters applied"

    return f"Filters: {', '.join(active_filters)}"

def create_filter_chips(filters: Dict[str, Any]) -> None:
    """
    Display active filters as removable chips

    Args:
        filters: Dictionary of applied filters
    """
    active_filters = []

    for key, value in filters.items():
        if key == 'search' and value and value.strip():
            active_filters.append((f"Search: '{value}'", key))
        elif isinstance(value, list) and value:
            for item in value:
                display_name = f"{key.replace('_', ' ').title()}: {item}"
                active_filters.append((display_name, f"{key}:{item}"))

    if active_filters:
        st.write("**Active Filters:**")
        cols = st.columns(min(len(active_filters), 4))

        for i, (display_name, filter_id) in enumerate(active_filters):
            col_idx = i % 4
            with cols[col_idx]:
                if st.button(f"❌ {display_name}", key=f"remove_{filter_id}"):
                    # Remove this filter (would need to be handled by parent component)
                    pass
