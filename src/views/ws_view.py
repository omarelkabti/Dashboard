"""
Workstream view for PET Resource Allocation Dashboard
Displays workstream assignments, FTE distribution, and drill-down capabilities
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Optional

def create_workstream_view(people_df: pd.DataFrame, assignments_df: pd.DataFrame) -> None:
    """
    Create the workstream analysis view

    Args:
        people_df: People DataFrame
        assignments_df: Assignments DataFrame
    """

    st.header("🎯 Workstream Analysis")

    if assignments_df.empty:
        st.info("No workstream assignment data available.")
        return

    # Create tabs for different workstream views
    tab1, tab2, tab3 = st.tabs(["📊 FTE Distribution", "📋 Assignments Table", "🔍 Resource Lookup"])

    with tab1:
        create_fte_distribution_chart(assignments_df, people_df)

    with tab2:
        create_assignments_table(assignments_df, people_df)

    with tab3:
        create_resource_lookup(assignments_df, people_df)

def create_fte_distribution_chart(assignments_df: pd.DataFrame, people_df: pd.DataFrame) -> None:
    """
    Create FTE distribution chart by workstream

    Args:
        assignments_df: Assignments DataFrame
        people_df: People DataFrame
    """

    # Calculate FTE by workstream
    ws_fte = assignments_df.groupby('workstream')['allocation_pct'].sum() / 100.0
    ws_fte = ws_fte.sort_values(ascending=False)

    if ws_fte.empty:
        st.warning("No FTE data available for visualization.")
        return

    # Create bar chart
    fig = px.bar(
        ws_fte.reset_index(),
        x='workstream',
        y='allocation_pct',
        title='Workstream FTE Distribution',
        labels={'allocation_pct': 'FTE', 'workstream': 'Workstream'},
        color='allocation_pct',
        color_continuous_scale='Blues'
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Workstreams", f"{len(ws_fte):,}")

    with col2:
        st.metric("Total FTE", f"{ws_fte.sum():.1f}")

    with col3:
        st.metric("Largest Workstream", f"{ws_fte.max():.1f} FTE")

    with col4:
        st.metric("Avg FTE per Workstream", f"{ws_fte.mean():.1f}")

    # Top workstreams table
    st.subheader("🏆 Top Workstreams by FTE")

    top_ws_df = ws_fte.head(10).reset_index()
    top_ws_df['allocation_pct'] = top_ws_df['allocation_pct'].round(2)
    top_ws_df.columns = ['Workstream', 'FTE']

    st.dataframe(
        top_ws_df,
        column_config={
            "FTE": st.column_config.NumberColumn("FTE", format="%.2f")
        },
        use_container_width=True,
        hide_index=True
    )

def create_assignments_table(assignments_df: pd.DataFrame, people_df: pd.DataFrame) -> None:
    """
    Create detailed assignments table with drill-down

    Args:
        assignments_df: Assignments DataFrame
        people_df: Assignments DataFrame
    """

    # Merge assignments with people data for richer display
    if not people_df.empty and 'employee_id' in assignments_df.columns:
        merged_df = assignments_df.merge(
            people_df[['employee_id', 'resource_name', 'type', 'manager', 'total_allocation_pct']],
            on='employee_id',
            how='left'
        )
    else:
        merged_df = assignments_df.copy()
        merged_df['resource_name'] = 'Unknown'
        merged_df['type'] = 'Unknown'
        merged_df['manager'] = 'Unknown'
        merged_df['total_allocation_pct'] = 0.0

    # Select and rename columns for display
    display_cols = [
        'workstream', 'resource_name', 'type', 'manager',
        'allocation_pct', 'total_allocation_pct'
    ]

    available_cols = [col for col in display_cols if col in merged_df.columns]
    display_df = merged_df[available_cols].copy()

    # Format percentages
    pct_cols = ['allocation_pct', 'total_allocation_pct']
    for col in pct_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].round(1)

    # Rename columns
    column_names = {
        'workstream': 'Workstream',
        'resource_name': 'Resource',
        'type': 'Type',
        'manager': 'Manager',
        'allocation_pct': 'Workstream %',
        'total_allocation_pct': 'Total Allocation %'
    }
    display_df = display_df.rename(columns=column_names)

    # Sort by workstream and allocation percentage
    display_df = display_df.sort_values(['Workstream', 'Workstream %'], ascending=[True, False])

    # Display table
    st.dataframe(
        display_df,
        column_config={
            "Workstream %": st.column_config.NumberColumn("Workstream %", format="%.1f%%"),
            "Total Allocation %": st.column_config.NumberColumn("Total Allocation %", format="%.1f%%")
        },
        use_container_width=True,
        hide_index=True
    )

    # Workstream selector for drill-down
    st.subheader("🔍 Drill-down by Workstream")

    workstreams = sorted(display_df['Workstream'].unique())
    selected_workstream = st.selectbox(
        "Select a workstream to view detailed assignments:",
        options=[""] + workstreams,
        format_func=lambda x: "Choose a workstream..." if x == "" else x
    )

    if selected_workstream:
        show_workstream_details(selected_workstream, display_df, people_df)

def show_workstream_details(workstream: str, assignments_df: pd.DataFrame, people_df: pd.DataFrame) -> None:
    """
    Show detailed view for a specific workstream

    Args:
        workstream: Selected workstream name
        assignments_df: Assignments DataFrame
        people_df: People DataFrame
    """

    ws_assignments = assignments_df[assignments_df['Workstream'] == workstream]

    if ws_assignments.empty:
        st.warning(f"No assignments found for workstream: {workstream}")
        return

    # Calculate workstream metrics
    total_fte = ws_assignments['Workstream %'].sum() / 100.0
    resource_count = len(ws_assignments)
    avg_allocation = ws_assignments['Workstream %'].mean()

    # Display metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(f"Resources in {workstream}", f"{resource_count:,}")

    with col2:
        st.metric("Total FTE", f"{total_fte:.1f}")

    with col3:
        st.metric("Avg Allocation", f"{avg_allocation:.1f}%")

    # Show assignments table
    st.subheader(f"📋 Resources Assigned to {workstream}")

    # Sort by allocation percentage
    ws_assignments_sorted = ws_assignments.sort_values('Workstream %', ascending=False)

    st.dataframe(
        ws_assignments_sorted,
        column_config={
            "Workstream %": st.column_config.NumberColumn("Workstream %", format="%.1f%%"),
            "Total Allocation %": st.column_config.NumberColumn("Total Allocation %", format="%.1f%%")
        },
        use_container_width=True,
        hide_index=True
    )

def create_resource_lookup(assignments_df: pd.DataFrame, people_df: pd.DataFrame) -> None:
    """
    Create resource lookup interface

    Args:
        assignments_df: Assignments DataFrame
        people_df: People DataFrame
    """

    st.subheader("🔍 Find Resources by Workstream")

    # Multi-select workstreams
    workstreams = sorted(assignments_df['workstream'].unique())
    selected_workstreams = st.multiselect(
        "Select workstreams to find assigned resources:",
        options=workstreams,
        default=[],
        help="Choose one or more workstreams to see all assigned resources"
    )

    if not selected_workstreams:
        st.info("Select one or more workstreams above to see assigned resources.")
        return

    # Filter assignments by selected workstreams
    filtered_assignments = assignments_df[assignments_df['workstream'].isin(selected_workstreams)]

    if filtered_assignments.empty:
        st.warning("No assignments found for selected workstreams.")
        return

    # Get unique resources
    unique_resources = filtered_assignments['employee_id'].unique()

    # Merge with people data
    if not people_df.empty and len(unique_resources) > 0:
        resource_details = people_df[people_df['employee_id'].isin(unique_resources)].copy()
    else:
        # Fallback if no people data or no employee IDs
        resource_details = pd.DataFrame()

    st.subheader(f"👥 Resources Assigned to Selected Workstreams ({len(unique_resources)})")

    # Show resource summary
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Resources Found", f"{len(unique_resources):,}")

    with col2:
        total_fte = filtered_assignments['allocation_pct'].sum() / 100.0
        st.metric("Combined FTE", f"{total_fte:.1f}")

    with col3:
        avg_resources_per_ws = len(unique_resources) / len(selected_workstreams)
        st.metric("Avg Resources per Workstream", f"{avg_resources_per_ws:.1f}")

    # Show detailed breakdown
    st.subheader("📊 Assignment Breakdown")

    # Create summary by workstream
    ws_summary = []
    for ws in selected_workstreams:
        ws_data = filtered_assignments[filtered_assignments['workstream'] == ws]
        ws_summary.append({
            'Workstream': ws,
            'Resources': len(ws_data),
            'FTE': ws_data['allocation_pct'].sum() / 100.0,
            'Avg Allocation': ws_data['allocation_pct'].mean()
        })

    summary_df = pd.DataFrame(ws_summary)
    summary_df = summary_df.round({'FTE': 2, 'Avg Allocation': 1})

    st.dataframe(
        summary_df,
        column_config={
            "FTE": st.column_config.NumberColumn("FTE", format="%.2f"),
            "Avg Allocation": st.column_config.NumberColumn("Avg Allocation", format="%.1f%%")
        },
        use_container_width=True,
        hide_index=True
    )

    # Option to show detailed resource list
    if st.checkbox("Show detailed resource assignments"):
        st.subheader("📋 Detailed Resource Assignments")

        # Merge assignments with resource details
        detailed_view = filtered_assignments.copy()

        if not resource_details.empty:
            detailed_view = detailed_view.merge(
                resource_details[['employee_id', 'resource_name', 'type', 'manager']],
                on='employee_id',
                how='left'
            )
        else:
            detailed_view['resource_name'] = 'Unknown'
            detailed_view['type'] = 'Unknown'
            detailed_view['manager'] = 'Unknown'

        # Select and format columns
        display_cols = ['workstream', 'resource_name', 'type', 'manager', 'allocation_pct']
        available_cols = [col for col in display_cols if col in detailed_view.columns]
        display_df = detailed_view[available_cols].copy()

        display_df['allocation_pct'] = display_df['allocation_pct'].round(1)

        display_df = display_df.rename(columns={
            'workstream': 'Workstream',
            'resource_name': 'Resource',
            'type': 'Type',
            'manager': 'Manager',
            'allocation_pct': 'Allocation %'
        })

        # Sort by workstream and resource
        display_df = display_df.sort_values(['Workstream', 'Resource'])

        st.dataframe(
            display_df,
            column_config={
                "Allocation %": st.column_config.NumberColumn("Allocation %", format="%.1f%%")
            },
            use_container_width=True,
            hide_index=True
        )
