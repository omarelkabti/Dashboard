"""
PET Resource Allocation Dashboard
Local dashboard for analyzing resource allocation and Workstream 1 completion
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import logging
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.etl import process_pet_csv, process_workstream_goals_csv
from src.views.goal_view import create_goal_overview, create_goal_drilldown, create_integrated_view

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="PET Resource Allocation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .completion-rate {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .drilldown-header {
        background: linear-gradient(90deg, #1f77b4, #17becf);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    """Load and cache data from CSV files"""
    data_dir = Path("data")
    looker_data_dir = Path("looker_data")
    
    # Load resource allocation data
    csv_files = list(data_dir.glob("*.csv"))
    people_df, hierarchy_df = None, None
    
    if csv_files:
        # Use the most recent file by default
        latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
        
        try:
            people_df, hierarchy_df = process_pet_csv(str(latest_file))
        except Exception as e:
            st.error(f"Error loading resource allocation data: {str(e)}")
    
    # Load workstream-goals data
    goals_files = list(looker_data_dir.glob("*Goals*.csv"))
    goals_df = None
    
    if goals_files:
        # Use the most recent goals file
        latest_goals_file = max(goals_files, key=lambda x: x.stat().st_mtime)
        
        try:
            goals_df = process_workstream_goals_csv(str(latest_goals_file))
        except Exception as e:
            st.error(f"Error loading workstream goals data: {str(e)}")
            goals_df = pd.DataFrame()
    else:
        goals_df = pd.DataFrame()
    
    return people_df, hierarchy_df, goals_df

def create_summary_metrics(df):
    """Create summary metrics for the dashboard focused on Business Platform Services"""
    if df is None or df.empty:
        return
    
    # Filter for Business Platform Services
    bps_df = df[df['l3_org'] == 'Business Platform Services (Kashi Kakarla)'].copy()
    
    if bps_df.empty:
        st.warning("No Business Platform Services data found")
        return
    
    total_resources = len(bps_df)
    ws1_completed = bps_df['workstream1_completed'].sum()
    completion_rate = (ws1_completed / total_resources * 100) if total_resources > 0 else 0
    
    overallocated = bps_df['overallocated'].sum()
    underallocated = bps_df['underallocated'].sum()
    unassigned = bps_df['unassigned'].sum()
    
    # Also show overall org stats for context
    total_org_resources = len(df)
    org_ws1_completed = df['workstream1_completed'].sum()
    org_completion_rate = (org_ws1_completed / total_org_resources * 100) if total_org_resources > 0 else 0
    
    st.markdown("### Business Platform Services Focus")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="BPS Resources",
            value=total_resources,
            delta=f"of {total_org_resources} total org"
        )
    
    with col2:
        st.metric(
            label="BPS Workstream 1 Completed",
            value=f"{ws1_completed}/{total_resources}",
            delta=f"{completion_rate:.1f}% vs {org_completion_rate:.1f}% org avg"
        )
    
    with col3:
        st.metric(
            label="BPS Allocation Issues",
            value=overallocated + underallocated + unassigned,
            delta=f"Over: {overallocated}, Under: {underallocated}, Unassigned: {unassigned}"
        )
    
    with col4:
        avg_allocation = bps_df['total_allocation_pct'].mean()
        st.metric(
            label="BPS Average Allocation",
            value=f"{avg_allocation:.1f}%",
            delta=None
        )

def create_workstream1_overview(df):
    """Create Workstream 1 completion overview focused on Business Platform Services"""
    st.markdown('<div class="drilldown-header"><h2>🎯 Workstream 1 Completion Overview - Business Platform Services</h2></div>', unsafe_allow_html=True)
    
    if df is None or df.empty:
        st.warning("No data available")
        return
    
    # Filter for Business Platform Services only
    bps_df = df[df['l3_org'] == 'Business Platform Services (Kashi Kakarla)'].copy()
    
    if bps_df.empty:
        st.warning("No Business Platform Services data found")
        return
    
    # Show BPS summary first
    total_bps = len(bps_df)
    completed_bps = bps_df['workstream1_completed'].sum()
    completion_rate_bps = (completed_bps / total_bps * 100) if total_bps > 0 else 0
    
    st.metric(
        label="Business Platform Services Overall",
        value=f"{completed_bps}/{total_bps}",
        delta=f"{completion_rate_bps:.1f}% completion rate"
    )
    
    # Completion by VP Org within Business Platform Services
    vp_completion = bps_df.groupby('vp_org').agg({
        'workstream1_completed': ['sum', 'count']
    }).round(2)
    vp_completion.columns = ['completed', 'total']
    vp_completion['completion_rate'] = (vp_completion['completed'] / vp_completion['total'] * 100).round(1)
    vp_completion = vp_completion.reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Completion by VP Organization")
        fig = px.bar(
            vp_completion,
            x='vp_org',
            y='completion_rate',
            title="Workstream 1 Completion Rate by VP Org (Business Platform Services)",
            labels={'completion_rate': 'Completion Rate (%)', 'vp_org': 'VP Organization'},
            color='completion_rate',
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.subheader("VP Completion Details")
        vp_completion_display = vp_completion.copy()
        vp_completion_display['completion_rate'] = vp_completion_display['completion_rate'].astype(str) + '%'
        st.dataframe(
            vp_completion_display,
            column_config={
                'vp_org': 'VP Organization',
                'completed': 'Completed',
                'total': 'Total Resources',
                'completion_rate': 'Completion Rate'
            },
            hide_index=True,
            width='stretch'
        )

def create_hierarchical_drilldown(df):
    """Create hierarchical drilldown view focused on Business Platform Services"""
    st.markdown('<div class="drilldown-header"><h2>🔍 Business Platform Services - Hierarchical Analysis</h2></div>', unsafe_allow_html=True)
    
    if df is None or df.empty:
        st.warning("No data available")
        return
    
    # Filter for Business Platform Services only
    bps_df = df[df['l3_org'] == 'Business Platform Services (Kashi Kakarla)'].copy()
    
    if bps_df.empty:
        st.warning("No Business Platform Services data found")
        return
    
    # Level selection for BPS with grouping mechanism
    col1, col2 = st.columns([2, 1])
    
    with col1:
        level_options = ['VP Org', 'Director Org', 'Supervisor', 'Individual Resources']
        selected_level = st.selectbox("Select organizational level within BPS:", level_options, index=0)
    
    with col2:
        if selected_level != 'VP Org':
            # Add grouping filter based on selected level
            if selected_level == 'Director Org':
                group_options = ['All VP Orgs'] + sorted(bps_df['vp_org'].dropna().unique().tolist())
                selected_group = st.selectbox("Filter by VP Org:", group_options, index=0)
                if selected_group != 'All VP Orgs':
                    bps_df = bps_df[bps_df['vp_org'] == selected_group]
            elif selected_level == 'Supervisor':
                group_options = ['All Director Orgs'] + sorted(bps_df['director_org'].dropna().unique().tolist())
                selected_group = st.selectbox("Filter by Director Org:", group_options, index=0)
                if selected_group != 'All Director Orgs':
                    bps_df = bps_df[bps_df['director_org'] == selected_group]
            elif selected_level == 'Individual Resources':
                group_options = ['All Supervisors'] + sorted(bps_df['supervisor'].dropna().unique().tolist())
                selected_group = st.selectbox("Filter by Supervisor:", group_options, index=0)
                if selected_group != 'All Supervisors':
                    bps_df = bps_df[bps_df['supervisor'] == selected_group]
    
    # Create summary based on selected level
    if selected_level == 'VP Org':
        level_data = bps_df.groupby('vp_org').agg({
            'workstream1_completed': ['sum', 'count'],
            'total_allocation_pct': 'mean',
            'overallocated': 'sum',
            'underallocated': 'sum',
            'unassigned': 'sum'
        }).round(2)
        level_data.columns = ['ws1_completed', 'resource_count', 'avg_allocation', 'overallocated', 'underallocated', 'unassigned']
        level_data['ws1_completion_rate'] = (level_data['ws1_completed'] / level_data['resource_count'] * 100).round(1)
        level_data = level_data.reset_index()
        
    elif selected_level == 'Director Org':
        level_data = bps_df.groupby(['vp_org', 'director_org']).agg({
            'workstream1_completed': ['sum', 'count'],
            'total_allocation_pct': 'mean',
            'overallocated': 'sum',
            'underallocated': 'sum',
            'unassigned': 'sum'
        }).round(2)
        level_data.columns = ['ws1_completed', 'resource_count', 'avg_allocation', 'overallocated', 'underallocated', 'unassigned']
        level_data['ws1_completion_rate'] = (level_data['ws1_completed'] / level_data['resource_count'] * 100).round(1)
        level_data = level_data.reset_index()
        
    elif selected_level == 'Supervisor':
        level_data = bps_df.groupby(['vp_org', 'director_org', 'supervisor']).agg({
            'workstream1_completed': ['sum', 'count'],
            'total_allocation_pct': 'mean',
            'overallocated': 'sum',
            'underallocated': 'sum',
            'unassigned': 'sum'
        }).round(2)
        level_data.columns = ['ws1_completed', 'resource_count', 'avg_allocation', 'overallocated', 'underallocated', 'unassigned']
        level_data['ws1_completion_rate'] = (level_data['ws1_completed'] / level_data['resource_count'] * 100).round(1)
        level_data = level_data.reset_index()
        
    else:  # Individual Resources
        level_data = bps_df[['vp_org', 'director_org', 'supervisor', 'resource_name', 'workstream1_completed', 'total_allocation_pct', 'type']].copy()
        level_data['workstream1_completed'] = level_data['workstream1_completed'].astype(int)
    
    # Display metrics for selected level
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if selected_level == 'Individual Resources':
            total_resources = len(level_data)
        else:
            total_resources = level_data['resource_count'].sum()
        st.metric(f"Total BPS Resources ({selected_level})", total_resources)
    
    with col2:
        if selected_level == 'Individual Resources':
            total_completed = level_data['workstream1_completed'].sum()
        else:
            total_completed = level_data['ws1_completed'].sum()
        completion_rate = (total_completed / total_resources * 100) if total_resources > 0 else 0
        st.metric("WS1 Completed", f"{total_completed}/{total_resources}", f"{completion_rate:.1f}%")
    
    with col3:
        if selected_level == 'Individual Resources':
            total_issues = 0  # Will calculate from individual records if needed
        else:
            total_issues = level_data['overallocated'].sum() + level_data['underallocated'].sum() + level_data['unassigned'].sum()
        st.metric("Allocation Issues", total_issues)
    
    # Detailed table
    st.subheader(f"BPS {selected_level} Details")
    
    # Format the display dataframe
    display_df = level_data.copy()
    
    if selected_level == 'Individual Resources':
        display_df['workstream1_completed'] = display_df['workstream1_completed'].map({1: '✅ Yes', 0: '❌ No'})
        display_df = display_df.sort_values(['supervisor', 'resource_name'])
        
        st.dataframe(
            display_df,
            column_config={
                'vp_org': 'VP Org',
                'director_org': 'Director Org', 
                'supervisor': 'Supervisor',
                'resource_name': 'Resource Name',
                'workstream1_completed': 'WS1 Status',
                'total_allocation_pct': st.column_config.NumberColumn('Total Allocation (%)', format="%.1f%%"),
                'type': 'Type'
            },
            hide_index=True,
            width='stretch'
        )
    else:
        display_df = display_df.sort_values('ws1_completion_rate', ascending=False)
        
        # Show relevant columns based on level
        if selected_level == 'VP Org':
            cols_to_show = ['vp_org', 'resource_count', 'ws1_completed', 'ws1_completion_rate', 'avg_allocation']
            column_config = {
                'vp_org': 'VP Organization',
                'resource_count': 'Resources',
                'ws1_completed': 'WS1 Completed',
                'ws1_completion_rate': st.column_config.NumberColumn('Completion Rate (%)', format="%.1f%%"),
                'avg_allocation': st.column_config.NumberColumn('Avg Allocation (%)', format="%.1f%%")
            }
        elif selected_level == 'Director Org':
            cols_to_show = ['vp_org', 'director_org', 'resource_count', 'ws1_completed', 'ws1_completion_rate']
            column_config = {
                'vp_org': 'VP Org',
                'director_org': 'Director Organization',
                'resource_count': 'Resources',
                'ws1_completed': 'WS1 Completed',
                'ws1_completion_rate': st.column_config.NumberColumn('Completion Rate (%)', format="%.1f%%")
            }
        else:  # Supervisor
            cols_to_show = ['vp_org', 'director_org', 'supervisor', 'resource_count', 'ws1_completed', 'ws1_completion_rate']
            column_config = {
                'vp_org': 'VP Org',
                'director_org': 'Director Org',
                'supervisor': 'Supervisor',
                'resource_count': 'Resources',
                'ws1_completed': 'WS1 Completed',
                'ws1_completion_rate': st.column_config.NumberColumn('Completion Rate (%)', format="%.1f%%")
            }
        
        st.dataframe(
            display_df[cols_to_show],
            column_config=column_config,
            hide_index=True,
            width='stretch'
        )

def create_detailed_pivot_table(df):
    """Create detailed pivot table view focused on Business Platform Services"""
    st.markdown('<div class="drilldown-header"><h2>📋 Business Platform Services - Detailed Resource Analysis</h2></div>', unsafe_allow_html=True)
    
    if df is None or df.empty:
        st.warning("No data available")
        return
    
    # Filter for Business Platform Services only
    bps_df = df[df['l3_org'] == 'Business Platform Services (Kashi Kakarla)'].copy()
    
    if bps_df.empty:
        st.warning("No Business Platform Services data found")
        return
    
    # Filters specific to BPS
    col1, col2, col3 = st.columns(3)
    
    with col1:
        vp_filter = st.multiselect(
            "Filter by VP Org:",
            options=sorted(bps_df['vp_org'].unique()),
            default=sorted(bps_df['vp_org'].unique())
        )
    
    with col2:
        completion_filter = st.selectbox(
            "Workstream 1 Status:",
            options=['All', 'Completed', 'Not Completed'],
            index=0
        )
    
    with col3:
        allocation_filter = st.selectbox(
            "Allocation Status:",
            options=['All', 'Overallocated', 'Underallocated', 'Unassigned', 'Properly Allocated'],
            index=0
        )
    
    # Apply filters
    filtered_df = bps_df[bps_df['vp_org'].isin(vp_filter)].copy()
    
    if completion_filter == 'Completed':
        filtered_df = filtered_df[filtered_df['workstream1_completed'] == True]
    elif completion_filter == 'Not Completed':
        filtered_df = filtered_df[filtered_df['workstream1_completed'] == False]
    
    if allocation_filter == 'Overallocated':
        filtered_df = filtered_df[filtered_df['overallocated'] == True]
    elif allocation_filter == 'Underallocated':
        filtered_df = filtered_df[filtered_df['underallocated'] == True]
    elif allocation_filter == 'Unassigned':
        filtered_df = filtered_df[filtered_df['unassigned'] == True]
    elif allocation_filter == 'Properly Allocated':
        filtered_df = filtered_df[
            (filtered_df['overallocated'] == False) & 
            (filtered_df['underallocated'] == False) & 
            (filtered_df['unassigned'] == False)
        ]
    
    # Display filtered results
    st.subheader(f"BPS Filtered Results ({len(filtered_df)} resources)")
    
    # Select columns to display
    display_columns = [
        'resource_name', 'supervisor', 'director_org', 'vp_org',
        'total_allocation_pct', 'workstream1_completed', 'type'
    ]
    
    display_df = filtered_df[display_columns].copy()
    display_df['workstream1_completed'] = display_df['workstream1_completed'].map({True: '✅ Yes', False: '❌ No'})
    
    st.dataframe(
        display_df,
        column_config={
            'resource_name': 'Resource Name',
            'supervisor': 'Supervisor',
            'director_org': 'Director Org',
            'vp_org': 'VP Org',
            'total_allocation_pct': st.column_config.NumberColumn(
                'Total Allocation (%)',
                format="%.1f%%"
            ),
            'workstream1_completed': 'Workstream 1 Status',
            'type': 'Type'
        },
        hide_index=True,
        width='stretch'
    )

def apply_search_filter(df, search_term):
    """Apply search filter across all text columns"""
    if not search_term:
        return df
    
    search_term = search_term.lower()
    
    # Define searchable columns
    text_columns = ['resource_name', 'supervisor', 'director_org', 'vp_org', 'l3_org', 'type', 'resource_raw']
    
    # Create a mask for rows that match the search term in any column
    mask = False
    for col in text_columns:
        if col in df.columns:
            mask = mask | df[col].astype(str).str.lower().str.contains(search_term, na=False, regex=False)
    
    return df[mask]

def create_search_results_view(df, search_term):
    """Create dedicated search results view"""
    st.markdown(f'<div class="drilldown-header"><h2>🔍 Search Results for "{search_term}"</h2></div>', unsafe_allow_html=True)
    
    if df is None or df.empty:
        st.warning("No search results found")
        return
    
    # Summary of search results
    total_results = len(df)
    ws1_completed = df['workstream1_completed'].sum()
    completion_rate = (ws1_completed / total_results * 100) if total_results > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Search Results", total_results)
    
    with col2:
        st.metric("WS1 Completed", f"{ws1_completed}/{total_results}", f"{completion_rate:.1f}%")
    
    with col3:
        unique_orgs = df['vp_org'].nunique()
        st.metric("VP Organizations", unique_orgs)
    
    # Breakdown by organization
    st.subheader("Results by VP Organization")
    org_breakdown = df.groupby('vp_org').agg({
        'workstream1_completed': ['sum', 'count'],
        'total_allocation_pct': 'mean'
    }).round(2)
    org_breakdown.columns = ['ws1_completed', 'total_count', 'avg_allocation']
    org_breakdown['completion_rate'] = (org_breakdown['ws1_completed'] / org_breakdown['total_count'] * 100).round(1)
    org_breakdown = org_breakdown.reset_index()
    
    st.dataframe(
        org_breakdown,
        column_config={
            'vp_org': 'VP Organization',
            'total_count': 'Resources Found',
            'ws1_completed': 'WS1 Completed',
            'completion_rate': st.column_config.NumberColumn('Completion Rate (%)', format="%.1f%%"),
            'avg_allocation': st.column_config.NumberColumn('Avg Allocation (%)', format="%.1f%%")
        },
        hide_index=True,
        width='stretch'
    )
    
    # Detailed results
    st.subheader("Individual Search Results")
    
    # Select columns to display
    display_columns = [
        'resource_name', 'supervisor', 'director_org', 'vp_org', 'l3_org',
        'total_allocation_pct', 'workstream1_completed', 'type'
    ]
    
    display_df = df[display_columns].copy()
    display_df['workstream1_completed'] = display_df['workstream1_completed'].map({True: '✅ Yes', False: '❌ No'})
    display_df = display_df.sort_values(['vp_org', 'director_org', 'supervisor', 'resource_name'])
    
    st.dataframe(
        display_df,
        column_config={
            'resource_name': 'Resource Name',
            'supervisor': 'Supervisor',
            'director_org': 'Director Org',
            'vp_org': 'VP Org',
            'l3_org': 'L3 Org',
            'total_allocation_pct': st.column_config.NumberColumn(
                'Total Allocation (%)',
                format="%.1f%%"
            ),
            'workstream1_completed': 'Workstream 1 Status',
            'type': 'Type'
        },
        hide_index=True,
        width='stretch'
    )

def main():
    """Main dashboard application"""
    st.title("📊 PET Resource Allocation Dashboard")
    st.markdown("### Business Platform Services - Workstream 1 Completion Tracking")
    
    # Load data
    with st.spinner("Loading data..."):
        people_df, hierarchy_df, goals_df = load_data()
    
    if people_df is None and goals_df.empty:
        st.error("No data available. Please ensure CSV files are in the data/ and looker_data/ directories.")
        st.stop()
    
    # Search bar at the top
    st.markdown("---")
    search_col1, search_col2 = st.columns([3, 1])
    
    with search_col1:
        search_term = st.text_input(
            "🔍 Search across all data (name, supervisor, organization, type, etc.):",
            placeholder="Enter search term...",
            key="global_search"
        )
    
    with search_col2:
        if st.button("Clear Search", key="clear_search"):
            st.session_state.global_search = ""
            st.rerun()
    
    # Apply search filter if search term is provided (only if people_df exists)
    original_count = len(people_df) if people_df is not None else 0
    if search_term and people_df is not None:
        people_df = apply_search_filter(people_df, search_term)
        filtered_count = len(people_df)
        
        if filtered_count == 0:
            st.warning(f"No results found for '{search_term}'. Showing all data.")
            people_df, hierarchy_df, goals_df = load_data()  # Reload original data
        else:
            st.info(f"Found {filtered_count} resources matching '{search_term}' (filtered from {original_count} total)")
    
    st.markdown("---")
    
    # Summary metrics (only show if people_df exists)
    if people_df is not None:
        create_summary_metrics(people_df)
    
    st.divider()
    
    # Create tabs based on available data
    available_tabs = []
    tab_functions = []
    
    if people_df is not None and not goals_df.empty:
        # Both datasets available
        if search_term:
            available_tabs = ["🔍 Search Results", "📈 Workstream 1 Overview", "🔍 Hierarchical Analysis", "📋 Detailed View", "🎯 Goal Overview", "🔍 Goal Analysis", "🔗 Integrated View"]
            tab_functions = [
                lambda: create_search_results_view(people_df, search_term),
                lambda: create_workstream1_overview(people_df),
                lambda: create_hierarchical_drilldown(people_df),
                lambda: create_detailed_pivot_table(people_df),
                lambda: create_goal_overview(goals_df),
                lambda: create_goal_drilldown(goals_df),
                lambda: create_integrated_view(goals_df, people_df)
            ]
        else:
            available_tabs = ["📈 Workstream 1 Overview", "🔍 Hierarchical Analysis", "📋 Detailed View", "🎯 Goal Overview", "🔍 Goal Analysis", "🔗 Integrated View"]
            tab_functions = [
                lambda: create_workstream1_overview(people_df),
                lambda: create_hierarchical_drilldown(people_df),
                lambda: create_detailed_pivot_table(people_df),
                lambda: create_goal_overview(goals_df),
                lambda: create_goal_drilldown(goals_df),
                lambda: create_integrated_view(goals_df, people_df)
            ]
    elif people_df is not None:
        # Only resource allocation data
        if search_term:
            available_tabs = ["🔍 Search Results", "📈 Workstream 1 Overview", "🔍 Hierarchical Analysis", "📋 Detailed View"]
            tab_functions = [
                lambda: create_search_results_view(people_df, search_term),
                lambda: create_workstream1_overview(people_df),
                lambda: create_hierarchical_drilldown(people_df),
                lambda: create_detailed_pivot_table(people_df)
            ]
        else:
            available_tabs = ["📈 Workstream 1 Overview", "🔍 Hierarchical Analysis", "📋 Detailed View"]
            tab_functions = [
                lambda: create_workstream1_overview(people_df),
                lambda: create_hierarchical_drilldown(people_df),
                lambda: create_detailed_pivot_table(people_df)
            ]
    elif not goals_df.empty:
        # Only goal data
        available_tabs = ["🎯 Goal Overview", "🔍 Goal Analysis"]
        tab_functions = [
            lambda: create_goal_overview(goals_df),
            lambda: create_goal_drilldown(goals_df)
        ]
    
    # Create tabs and execute functions
    if available_tabs:
        tabs = st.tabs(available_tabs)
        for tab, func in zip(tabs, tab_functions):
            with tab:
                func()
    
    # Footer
    st.divider()
    st.markdown("*Dashboard built with Streamlit • Data refreshed on page load*")

if __name__ == "__main__":
    main()