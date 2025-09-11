"""
KPI tiles component for PET Resource Allocation Dashboard
Displays key metrics and statistics
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any

def create_kpi_tiles(metrics: Dict[str, Any], filtered_people: pd.DataFrame, filtered_assignments: pd.DataFrame) -> None:
    """
    Create and display KPI tiles

    Args:
        metrics: Global metrics dictionary
        filtered_people: Filtered people DataFrame
        filtered_assignments: Filtered assignments DataFrame
    """

    # Calculate filtered metrics
    filtered_metrics = calculate_filtered_metrics(filtered_people, filtered_assignments)

    st.subheader("📊 Key Metrics")

    # Create KPI tiles in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Resources",
            f"{filtered_metrics['total_resources']:,}",
            help="Number of resources matching current filters"
        )

    with col2:
        open_roles = filtered_metrics['open_roles']
        total_resources = filtered_metrics['total_resources']
        open_roles_pct = (open_roles / total_resources * 100) if total_resources > 0 else 0

        st.metric(
            "Open Roles",
            f"{open_roles:,}",
            f"{open_roles_pct:.1f}%",
            help="Number and percentage of open requisitions"
        )

    with col3:
        total_fte = filtered_metrics['total_fte']
        st.metric(
            "Total FTE",
            f"{total_fte:.1f}",
            help="Full-time equivalent based on allocation percentages"
        )

    with col4:
        overallocated = filtered_metrics['overallocated_count']
        overallocated_pct = (overallocated / filtered_metrics['total_resources'] * 100) if filtered_metrics['total_resources'] > 0 else 0

        st.metric(
            "Overallocated",
            f"{overallocated:,}",
            f"{overallocated_pct:.1f}%",
            help="Resources with total allocation > 100%"
        )

    # Second row of KPIs
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        unassigned = filtered_metrics['unassigned_count']
        unassigned_pct = (unassigned / filtered_metrics['total_resources'] * 100) if filtered_metrics['total_resources'] > 0 else 0

        st.metric(
            "Unassigned",
            f"{unassigned:,}",
            f"{unassigned_pct:.1f}%",
            help="Resources with 0% allocation"
        )

    with col6:
        unique_workstreams = filtered_metrics['unique_workstreams']
        st.metric(
            "Workstreams",
            f"{unique_workstreams:,}",
            help="Number of unique workstreams with assignments"
        )

    with col7:
        avg_allocation = filtered_metrics['avg_allocation']
        st.metric(
            "Avg Allocation",
            f"{avg_allocation:.1f}%",
            help="Average allocation percentage across all resources"
        )

    with col8:
        # Show allocation distribution
        allocated_100 = filtered_metrics['allocated_at_100']
        allocated_100_pct = (allocated_100 / filtered_metrics['total_resources'] * 100) if filtered_metrics['total_resources'] > 0 else 0

        st.metric(
            "At 100%",
            f"{allocated_100:,}",
            f"{allocated_100_pct:.1f}%",
            help="Resources allocated exactly at 100%"
        )

def calculate_filtered_metrics(people_df: pd.DataFrame, assignments_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate metrics for filtered data

    Args:
        people_df: Filtered people DataFrame
        assignments_df: Filtered assignments DataFrame

    Returns:
        Dictionary of calculated metrics
    """
    metrics = {}

    # Basic counts
    metrics['total_resources'] = len(people_df)

    if people_df.empty:
        metrics.update({
            'open_roles': 0,
            'total_fte': 0.0,
            'overallocated_count': 0,
            'unassigned_count': 0,
            'unique_workstreams': 0,
            'avg_allocation': 0.0,
            'allocated_at_100': 0
        })
        return metrics

    # Open roles count
    open_roles_mask = people_df['type'].isin(['Req', 'Open Role'])
    metrics['open_roles'] = open_roles_mask.sum()

    # FTE calculation
    total_allocation_pct = people_df['total_allocation_pct'].fillna(0).sum()
    metrics['total_fte'] = total_allocation_pct / 100.0

    # Allocation status counts
    metrics['overallocated_count'] = people_df['overallocated'].fillna(False).sum()
    metrics['unassigned_count'] = people_df['unassigned'].fillna(False).sum()

    # Workstream count
    if not assignments_df.empty:
        metrics['unique_workstreams'] = assignments_df['workstream'].nunique()
    else:
        metrics['unique_workstreams'] = 0

    # Average allocation
    valid_allocations = people_df['total_allocation_pct'].dropna()
    metrics['avg_allocation'] = valid_allocations.mean() if not valid_allocations.empty else 0.0

    # Resources allocated exactly at 100%
    at_100_mask = (people_df['total_allocation_pct'].fillna(0) == 100.0)
    metrics['allocated_at_100'] = at_100_mask.sum()

    return metrics

def create_allocation_status_chart(people_df: pd.DataFrame) -> None:
    """
    Create a simple allocation status distribution chart

    Args:
        people_df: People DataFrame
    """
    if people_df.empty:
        return

    # Count allocation statuses
    status_counts = {
        'Overallocated': people_df['overallocated'].fillna(False).sum(),
        'Underallocated': people_df['underallocated'].fillna(False).sum(),
        'Unassigned': people_df['unassigned'].fillna(False).sum(),
        'At 100%': ((people_df['total_allocation_pct'].fillna(0) == 100.0) &
                   ~people_df['overallocated'].fillna(False) &
                   ~people_df['underallocated'].fillna(False) &
                   ~people_df['unassigned'].fillna(False)).sum()
    }

    # Filter out zero values
    status_counts = {k: v for k, v in status_counts.items() if v > 0}

    if status_counts:
        st.subheader("📈 Allocation Status Distribution")

        # Simple bar chart using st.bar_chart
        chart_data = pd.DataFrame({
            'Status': list(status_counts.keys()),
            'Count': list(status_counts.values())
        })

        st.bar_chart(chart_data.set_index('Status'))

def create_workstream_fte_chart(assignments_df: pd.DataFrame) -> None:
    """
    Create workstream FTE distribution chart

    Args:
        assignments_df: Assignments DataFrame
    """
    if assignments_df.empty:
        return

    st.subheader("📊 Workstream FTE Distribution")

    # Calculate FTE by workstream
    ws_fte = assignments_df.groupby('workstream')['allocation_pct'].sum() / 100.0
    ws_fte = ws_fte.sort_values(ascending=False)

    # Show top 10 workstreams
    if len(ws_fte) > 10:
        top_ws = ws_fte.head(10)
        other_fte = ws_fte.tail(len(ws_fte) - 10).sum()
        chart_data = pd.concat([top_ws, pd.Series({'Other': other_fte})])
    else:
        chart_data = ws_fte

    # Create horizontal bar chart
    chart_df = pd.DataFrame({
        'Workstream': chart_data.index,
        'FTE': chart_data.values
    })

    st.bar_chart(chart_df.set_index('Workstream'), horizontal=True)
