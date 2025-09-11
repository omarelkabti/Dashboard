"""
Organization mapping view for PET Resource Allocation Dashboard
Displays resources in table/tree format with drill-down capabilities
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
import json

def create_org_view(people_df: pd.DataFrame, assignments_df: pd.DataFrame) -> None:
    """
    Create the organization mapping view

    Args:
        people_df: People DataFrame
        assignments_df: Assignments DataFrame
    """

    st.header("🏢 Organization Mapping")

    if people_df.empty:
        st.info("No data available. Please upload a PET CSV file.")
        return

    # View toggle
    view_mode = st.radio(
        "View Mode",
        ["Table View", "Tree View"],
        horizontal=True,
        help="Switch between table and hierarchical tree view"
    )

    if view_mode == "Table View":
        create_org_table_view(people_df, assignments_df)
    else:
        create_org_tree_view(people_df, assignments_df)

def create_org_table_view(people_df: pd.DataFrame, assignments_df: pd.DataFrame) -> None:
    """
    Create table view of organization data

    Args:
        people_df: People DataFrame
        assignments_df: Assignments DataFrame
    """

    # Select columns to display
    display_cols = [
        'resource_name', 'type', 'manager', 'director_org', 'vp_org', 'l3_org',
        'total_allocation_pct', 'overallocated', 'underallocated', 'unassigned'
    ]

    # Filter to available columns
    available_cols = [col for col in display_cols if col in people_df.columns]
    display_df = people_df[available_cols].copy()

    # Format columns
    if 'total_allocation_pct' in display_df.columns:
        display_df['total_allocation_pct'] = display_df['total_allocation_pct'].round(1)

    # Rename columns for display
    column_names = {
        'resource_name': 'Resource',
        'type': 'Type',
        'manager': 'Manager',
        'director_org': 'Director Org',
        'vp_org': 'VP Org',
        'l3_org': 'L3 Org',
        'total_allocation_pct': 'Total Allocation %',
        'overallocated': 'Overallocated',
        'underallocated': 'Underallocated',
        'unassigned': 'Unassigned'
    }
    display_df = display_df.rename(columns=column_names)

    # Add selection column for drill-down
    display_df.insert(0, 'Select', False)

    # Display table with selection
    edited_df = st.data_editor(
        display_df,
        column_config={
            "Select": st.column_config.CheckboxColumn(
                "Select",
                help="Select to view resource details",
                default=False,
            ),
            "Total Allocation %": st.column_config.NumberColumn(
                "Total Allocation %",
                format="%.1f%%",
            ),
            "Overallocated": st.column_config.CheckboxColumn(
                "Overallocated",
                help="Total allocation > 100%",
                disabled=True
            ),
            "Underallocated": st.column_config.CheckboxColumn(
                "Underallocated",
                help="Total allocation < 100%",
                disabled=True
            ),
            "Unassigned": st.column_config.CheckboxColumn(
                "Unassigned",
                help="Total allocation = 0%",
                disabled=True
            ),
        },
        disabled=["Resource", "Type", "Manager", "Director Org", "VP Org", "L3 Org", "Total Allocation %", "Overallocated", "Underallocated", "Unassigned"],
        hide_index=True,
        use_container_width=True
    )

    # Show selected resource details
    selected_rows = edited_df[edited_df['Select']]
    if not selected_rows.empty:
        selected_resource = selected_rows.iloc[0]['Resource']
        show_resource_drawer(selected_resource, people_df, assignments_df)

def create_org_tree_view(people_df: pd.DataFrame, assignments_df: pd.DataFrame) -> None:
    """
    Create hierarchical tree view of organization data

    Args:
        people_df: People DataFrame
        assignments_df: Assignments DataFrame
    """

    # Build hierarchical structure
    hierarchy_levels = ['l3_org', 'vp_org', 'director_org', 'manager']

    # Filter to available levels
    available_levels = [level for level in hierarchy_levels if level in people_df.columns]

    if not available_levels:
        st.warning("No organizational hierarchy data available for tree view.")
        return

    # Create tree structure
    tree_data = build_org_tree(people_df, available_levels)

    # Display tree
    display_org_tree(tree_data, people_df, assignments_df)

def build_org_tree(people_df: pd.DataFrame, hierarchy_levels: list) -> Dict[str, Any]:
    """
    Build hierarchical tree structure from people data

    Args:
        people_df: People DataFrame
        hierarchy_levels: List of hierarchy levels to include

    Returns:
        Nested dictionary representing the org tree
    """

    tree = {}

    for _, person in people_df.iterrows():
        current_node = tree

        # Navigate/create path through hierarchy
        for level in hierarchy_levels:
            level_value = person.get(level, 'Unknown')
            if pd.isna(level_value):
                level_value = '(unknown)'

            if level_value not in current_node:
                current_node[level_value] = {'_count': 0, '_fte': 0.0}

            current_node = current_node[level_value]

        # Add person at leaf level
        emp_id = person.get('employee_id', person.get('resource_name', 'Unknown'))
        current_node[emp_id] = {
            'name': person.get('resource_name', 'Unknown'),
            'type': person.get('type', 'Unknown'),
            'allocation_pct': person.get('total_allocation_pct', 0),
            'workstreams': get_person_workstreams(emp_id, assignments_df)
        }

        # Update counts up the tree
        update_tree_counts(tree, hierarchy_levels, person)

    return tree

def update_tree_counts(tree: Dict[str, Any], hierarchy_levels: list, person: pd.Series) -> None:
    """Update counts and FTE in tree structure"""
    current_node = tree

    for level in hierarchy_levels:
        level_value = person.get(level, 'Unknown')
        if pd.isna(level_value):
            level_value = '(unknown)'

        if level_value in current_node:
            current_node[level_value]['_count'] += 1
            current_node[level_value]['_fte'] += person.get('total_allocation_pct', 0) / 100.0

        current_node = current_node[level_value]

def get_person_workstreams(employee_id: str, assignments_df: pd.DataFrame) -> list:
    """Get workstream assignments for a person"""
    if assignments_df.empty or not employee_id:
        return []

    person_assignments = assignments_df[assignments_df['employee_id'] == employee_id]
    return person_assignments[['workstream', 'allocation_pct']].to_dict('records')

def display_org_tree(tree_data: Dict[str, Any], people_df: pd.DataFrame, assignments_df: pd.DataFrame, prefix: str = "", level: int = 0) -> None:
    """
    Display the organizational tree with expandable nodes

    Args:
        tree_data: Tree structure dictionary
        people_df: People DataFrame
        assignments_df: Assignments DataFrame
        prefix: Current path prefix for keys
        level: Current hierarchy level
    """

    for key, value in tree_data.items():
        if key.startswith('_'):
            continue  # Skip metadata keys

        # Create unique key for this node
        node_key = f"{prefix}_{key}_{level}"

        # Check if this is a leaf node (person)
        if isinstance(value, dict) and 'name' in value:
            # This is a person node
            person_info = value
            workstreams = person_info.get('workstreams', [])

            # Create expandable row for person
            with st.expander(f"👤 {person_info['name']} ({person_info['type']}) - {person_info['allocation_pct']:.1f}%", expanded=False):
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.write(f"**Type:** {person_info['type']}")
                    st.write(f"**Allocation:** {person_info['allocation_pct']:.1f}%")

                with col2:
                    if workstreams:
                        st.write("**Workstreams:**")
                        for ws in workstreams:
                            st.write(f"• {ws['workstream']}: {ws['allocation_pct']:.1f}%")
                    else:
                        st.write("*No workstream assignments*")

                if st.button("View Full Details", key=f"details_{node_key}"):
                    show_resource_drawer(person_info['name'], people_df, assignments_df)
        else:
            # This is an org node
            count = value.get('_count', 0)
            fte = value.get('_fte', 0.0)

            # Create expandable org node
            with st.expander(f"🏢 {key} ({count} resources, {fte:.1f} FTE)", expanded=False):
                display_org_tree(value, people_df, assignments_df, node_key, level + 1)

def show_resource_drawer(resource_name: str, people_df: pd.DataFrame, assignments_df: pd.DataFrame) -> None:
    """
    Show detailed resource information in a drawer/sidebar

    Args:
        resource_name: Name of the resource to show
        people_df: People DataFrame
        assignments_df: Assignments DataFrame
    """

    # Find the resource
    resource_row = people_df[people_df['resource_name'] == resource_name]
    if resource_row.empty:
        st.error(f"Resource '{resource_name}' not found.")
        return

    resource = resource_row.iloc[0]

    st.header(f"👤 {resource_name}")

    # Basic information
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Basic Information")
        st.write(f"**Employee ID:** {resource.get('employee_id', 'N/A')}")
        st.write(f"**Type:** {resource.get('type', 'Unknown')}")
        st.write(f"**Title:** {resource.get('resource_title', 'Unknown')}")

    with col2:
        st.subheader("Organization")
        st.write(f"**Manager:** {resource.get('manager', 'Unknown')}")
        st.write(f"**Director Org:** {resource.get('director_org', 'Unknown')}")
        st.write(f"**VP Org:** {resource.get('vp_org', 'Unknown')}")
        st.write(f"**L3 Org:** {resource.get('l3_org', 'Unknown')}")

    # Allocation information
    st.subheader("📊 Allocation Summary")
    total_pct = resource.get('total_allocation_pct', 0)
    st.write(f"**Total Allocation:** {total_pct:.1f}%")

    # Status flags
    status_indicators = []
    if resource.get('overallocated', False):
        status_indicators.append("🔴 Overallocated")
    if resource.get('underallocated', False):
        status_indicators.append("🟡 Underallocated")
    if resource.get('unassigned', False):
        status_indicators.append("⚪ Unassigned")
    if resource.get('allocation_mismatch', False):
        status_indicators.append("⚠️ Allocation Mismatch")

    if status_indicators:
        st.write("**Status:** " + " | ".join(status_indicators))

    # Workstream assignments
    st.subheader("🎯 Workstream Assignments")

    if assignments_df.empty:
        st.write("No workstream assignments found.")
    else:
        emp_id = resource.get('employee_id')
        if emp_id:
            person_assignments = assignments_df[assignments_df['employee_id'] == emp_id]

            if person_assignments.empty:
                st.write("No workstream assignments found.")
            else:
                # Display as table
                display_assignments = person_assignments[['workstream', 'allocation_pct']].copy()
                display_assignments['allocation_pct'] = display_assignments['allocation_pct'].round(1)
                display_assignments = display_assignments.rename(columns={
                    'workstream': 'Workstream',
                    'allocation_pct': 'Allocation %'
                })

                st.dataframe(display_assignments, use_container_width=True)

                # Workstream FTE summary
                total_ws_pct = display_assignments['Allocation %'].sum()
                st.write(f"**Total from assignments:** {total_ws_pct:.1f}%")
        else:
            st.write("Cannot show assignments - no employee ID available.")

    # Action buttons
    st.subheader("Actions")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📋 Copy Manager Chain"):
            org_chain = [
                resource.get('manager', 'Unknown'),
                resource.get('director_org', 'Unknown'),
                resource.get('vp_org', 'Unknown'),
                resource.get('l3_org', 'Unknown')
            ]
            chain_text = " → ".join(org_chain)
            st.code(chain_text, language="text")
            st.success("Manager chain copied to clipboard!")

    with col2:
        if st.button("📊 Export This Resource"):
            # Create CSV data for this resource
            resource_data = resource.to_frame().T
            csv_data = resource_data.to_csv(index=False)

            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"{resource_name.replace(' ', '_')}_details.csv",
                mime="text/csv"
            )

    with col3:
        if st.button("🔗 View in Assignments"):
            st.info("Switch to Workstream View to see all assignments for this resource.")
