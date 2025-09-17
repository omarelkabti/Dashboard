"""
Goal-focused dashboard views for workstream-goal mapping analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, List, Dict, Any

def create_goal_overview(goals_df: pd.DataFrame) -> None:
    """Create overview dashboard for workstream-goal mappings"""
    if goals_df.empty:
        st.warning("No goal data available")
        return
    
    st.header("🎯 Workstream-Goal Mapping Overview")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_workstreams = goals_df['Workstream Name'].nunique()
        st.metric("Total Workstreams", total_workstreams)
    
    with col2:
        total_goals = goals_df['Goal Name'].nunique()
        st.metric("Total Goals", total_goals)
    
    with col3:
        avg_allocation = goals_df['Allocation %'].mean()
        st.metric("Avg Goal Allocation", f"{avg_allocation:.1f}%")
    
    with col4:
        # Calculate unique FTE by workstream to avoid double counting
        unique_fte_by_workstream = goals_df.groupby('Workstream Name')['Target FTE Headcount'].first().sum()
        st.metric("Total Target FTE (Unique)", f"{unique_fte_by_workstream:.0f}")
    
    st.divider()
    
    # Allocation by workstream and goal (with proper FTE counting)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("FTE and Goal Count by Workstream")
        # Group by workstream - show FTE and goal count, not allocation sum
        workstream_summary = []
        for workstream in goals_df['Workstream Name'].unique():
            ws_data = goals_df[goals_df['Workstream Name'] == workstream]
            unique_fte = ws_data['Target FTE Headcount'].iloc[0] if len(ws_data) > 0 else 0
            goal_count = len(ws_data)
            max_allocation = ws_data['Allocation %'].max() if len(ws_data) > 0 else 0
            workstream_summary.append({
                'Workstream Name': workstream,
                'Target FTE': unique_fte,
                'Goal Count': goal_count,
                'Max Goal Allocation %': max_allocation
            })
        
        workstream_allocation = pd.DataFrame(workstream_summary)
        workstream_allocation = workstream_allocation.sort_values('Target FTE', ascending=True)
        
        fig = px.bar(
            workstream_allocation,
            x='Target FTE',
            y='Workstream Name',
            orientation='h',
            title="Target FTE by Workstream",
            labels={'Target FTE': 'Target FTE', 'Workstream Name': 'Workstream'},
            hover_data=['Goal Count', 'Max Goal Allocation %']
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.subheader("Allocation by Benefit Type")
        benefit_allocation = goals_df.groupby('Benefit L2')['Allocation %'].sum().reset_index()
        benefit_allocation = benefit_allocation.sort_values('Allocation %', ascending=False)
        
        fig = px.pie(
            benefit_allocation,
            values='Allocation %',
            names='Benefit L2',
            title="Allocation Distribution by Benefit Type"
        )
        st.plotly_chart(fig, width='stretch')
    
    # Goal details table
    st.subheader("Goal Details")
    
    # Add filters - now with 5 columns
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        selected_l4_leaders = st.multiselect(
            "Filter by L4 Leaders",
            options=sorted(goals_df['L4 Leaders'].dropna().unique()),
            key="goal_l4_filter"
        )
    
    with col2:
        selected_benefit = st.multiselect(
            "Filter by Benefit Type",
            options=sorted(goals_df['Benefit L2'].dropna().unique()),
            key="goal_benefit_filter"
        )
    
    with col3:
        selected_workstreams = st.multiselect(
            "Filter by Workstream",
            options=sorted(goals_df['Workstream Name'].dropna().unique()),
            key="goal_workstream_filter"
        )
    
    with col4:
        # Allocation range filter
        allocation_range = st.slider(
            "Allocation % Range",
            min_value=0,
            max_value=100,
            value=(0, 100),
            key="goal_allocation_filter"
        )
    
    with col5:
        active_only = st.checkbox("Active Goals Only", value=True, key="goal_active_filter")
    
    # Apply filters
    filtered_df = goals_df.copy()
    
    if selected_l4_leaders:
        filtered_df = filtered_df[filtered_df['L4 Leaders'].isin(selected_l4_leaders)]
    
    if selected_benefit:
        filtered_df = filtered_df[filtered_df['Benefit L2'].isin(selected_benefit)]
    
    if selected_workstreams:
        filtered_df = filtered_df[filtered_df['Workstream Name'].isin(selected_workstreams)]
    
    if allocation_range != (0, 100):
        filtered_df = filtered_df[
            (filtered_df['Allocation %'] >= allocation_range[0]) & 
            (filtered_df['Allocation %'] <= allocation_range[1])
        ]
    
    if active_only:
        filtered_df = filtered_df[filtered_df['Active'] == True]
    
    # Create TRUE pivot table - matrix view of workstreams vs goals
    st.subheader("Workstream-Goal Matrix (True Pivot Table)")
    
    if not filtered_df.empty:
        # Option to choose what to display in the pivot cells
        col1, col2 = st.columns(2)
        
        with col1:
            pivot_value = st.selectbox(
                "Show in cells:",
                options=["Allocation %", "Active Status", "Benefit L2"],
                key="pivot_value_selector"
            )
        
        with col2:
            max_goals = st.slider(
                "Max goals to show",
                min_value=5,
                max_value=min(20, len(filtered_df['Goal Name'].unique())),
                value=10,
                key="max_goals_slider"
            )
        
        # Get top goals by frequency across workstreams
        top_goals = filtered_df['Goal Name'].value_counts().head(max_goals).index.tolist()
        pivot_filtered = filtered_df[filtered_df['Goal Name'].isin(top_goals)]
        
        if not pivot_filtered.empty:
            # Create the actual pivot table
            if pivot_value == "Allocation %":
                pivot_table = pivot_filtered.pivot_table(
                    index='Workstream Name',
                    columns='Goal Name', 
                    values='Allocation %',
                    aggfunc='first',  # Use first since there should be one value per workstream-goal pair
                    fill_value=0
                )
                # Format as percentages
                pivot_display = pivot_table.round(1)
                
            elif pivot_value == "Active Status":
                pivot_table = pivot_filtered.pivot_table(
                    index='Workstream Name',
                    columns='Goal Name',
                    values='Active',
                    aggfunc='first',
                    fill_value=False
                )
                # Convert to readable format
                pivot_display = pivot_table.replace({True: "✅", False: "❌", 0: ""})
                
            else:  # Benefit L2
                pivot_table = pivot_filtered.pivot_table(
                    index='Workstream Name',
                    columns='Goal Name',
                    values='Benefit L2',
                    aggfunc='first',
                    fill_value=""
                )
                pivot_display = pivot_table
            
            # Add workstream summary columns
            ws_summary = []
            for ws in pivot_table.index:
                ws_data = filtered_df[filtered_df['Workstream Name'] == ws]
                fte = ws_data['Target FTE Headcount'].iloc[0] if len(ws_data) > 0 else 0
                goal_count = len(ws_data)
                leader = ws_data['L4 Leaders'].iloc[0] if len(ws_data) > 0 else ''
                
                ws_summary.append({
                    'FTE': fte,
                    'Goals': goal_count,
                    'L4 Leader': leader
                })
            
            summary_df = pd.DataFrame(ws_summary, index=pivot_table.index)
            
            # Combine pivot table with summary
            combined_table = pd.concat([summary_df, pivot_display], axis=1)
            
            st.write(f"**Showing {pivot_value} for workstreams vs top {len(top_goals)} goals**")
            st.dataframe(combined_table, width='stretch')
            
            # Show legend for the pivot table
            if pivot_value == "Allocation %":
                st.info("💡 **Reading the table**: Each cell shows what % of the workstream's resources are allocated to that goal. 0 means no allocation.")
            elif pivot_value == "Active Status":
                st.info("💡 **Reading the table**: ✅ = Active goal for this workstream, ❌ = Inactive, blank = No allocation")
            else:
                st.info("💡 **Reading the table**: Shows the benefit type for each workstream-goal combination")
        
        else:
            st.warning("No data available for the selected filters")
            
        # Summary statistics
        st.subheader("Pivot Summary Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_combinations = len(filtered_df)
            st.metric("Total Workstream-Goal Combinations", total_combinations)
        
        with col2:
            avg_goals_per_ws = filtered_df.groupby('Workstream Name').size().mean()
            st.metric("Avg Goals per Workstream", f"{avg_goals_per_ws:.1f}")
        
        with col3:
            avg_ws_per_goal = filtered_df.groupby('Goal Name').size().mean()
            st.metric("Avg Workstreams per Goal", f"{avg_ws_per_goal:.1f}")
        
        # Additional summary metrics for filtered data
        st.subheader("Filtered Data Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            unique_workstreams = filtered_df['Workstream Name'].nunique()
            st.metric("Filtered Workstreams", unique_workstreams)
        with col2:
            total_goals = filtered_df['Goal Name'].nunique()
            st.metric("Unique Goals", total_goals)
        with col3:
            # Show average allocation instead of sum (since allocation % should not be summed)
            avg_allocation = filtered_df['Allocation %'].mean()
            st.metric("Avg Goal Allocation %", f"{avg_allocation:.1f}%")
        with col4:
            # Calculate unique FTE across all workstreams (no double counting)
            unique_total_fte = filtered_df.groupby('Workstream Name')['Target FTE Headcount'].first().sum()
            st.metric("Total Target FTE", f"{unique_total_fte:.0f}")
    
    else:
        st.warning("No data matches the selected filters")
    
    # Detailed view (expandable)
    with st.expander("Detailed Goal View (All Goals)"):
        display_cols = [
            'Workstream Name', 'L4 Leaders', 'Goal Name', 'Benefit L2', 
            'Allocation %', 'Target FTE Headcount', 'Active'
        ]
        
        st.dataframe(
            filtered_df[display_cols],
            width='stretch',
            hide_index=True
        )

def create_goal_drilldown(goals_df: pd.DataFrame) -> None:
    """Create interactive drilldown view for goal analysis"""
    if goals_df.empty:
        st.warning("No goal data available")
        return
    
    st.header("🔍 Goal Analysis Drilldown")
    
    # Level selection
    drill_level = st.selectbox(
        "Select Analysis Level",
        options=["L4 Leaders", "Workstream", "Goal", "Benefit Type"],
        key="goal_drill_level"
    )
    
    # Create aggregation based on selected level
    if drill_level == "L4 Leaders":
        group_col = 'L4 Leaders'
        title_suffix = "by L4 Leaders"
    elif drill_level == "Workstream":
        group_col = 'Workstream Name'
        title_suffix = "by Workstream"
    elif drill_level == "Goal":
        group_col = 'Goal Name'
        title_suffix = "by Goal"
    else:  # Benefit Type
        group_col = 'Benefit L2'
        title_suffix = "by Benefit Type"
    
    # Calculate metrics by selected level
    if drill_level == "L4 Leaders":
        # For L4 Leaders, calculate average allocation percentage (not sum)
        # and sum unique FTE from workstreams to avoid double counting
        # For L4 Leaders, calculate metrics differently to avoid double counting
        leader_metrics = []
        for leader in goals_df[group_col].unique():
            leader_data = goals_df[goals_df[group_col] == leader]
            # Get unique FTE per workstream to avoid double counting
            unique_fte = leader_data.groupby('Workstream Name')['Target FTE Headcount'].first().sum()
            avg_allocation = leader_data['Allocation %'].mean()
            unique_goals = leader_data['Goal Name'].nunique()
            unique_workstreams = leader_data['Workstream Name'].nunique()
            
            leader_metrics.append({
                group_col: leader,
                'Avg Allocation %': avg_allocation,
                'Total FTE': unique_fte,
                'Unique Goals': unique_goals,
                'Unique Workstreams': unique_workstreams
            })
        
        agg_df = pd.DataFrame(leader_metrics)
    else:
        # For other levels, sum makes more sense
        agg_df = goals_df.groupby(group_col).agg({
            'Allocation %': 'sum',
            'Target FTE Headcount': 'sum',
            'Goal Name': 'nunique',
            'Workstream Name': 'nunique'
        }).reset_index()
        agg_df.columns = [group_col, 'Total Allocation %', 'Total FTE', 'Unique Goals', 'Unique Workstreams']
    # Sort by the appropriate allocation column
    sort_col = 'Avg Allocation %' if drill_level == "L4 Leaders" else 'Total Allocation %'
    agg_df = agg_df.sort_values(sort_col, ascending=False)
    
    # Create visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"Allocation Distribution {title_suffix}")
        # Use appropriate allocation column for chart
        x_col = 'Avg Allocation %' if drill_level == "L4 Leaders" else 'Total Allocation %'
        chart_title = f"Top 10 {title_suffix} - {'Average' if drill_level == 'L4 Leaders' else 'Total'} Allocation"
        
        fig = px.bar(
            agg_df.head(10),  # Show top 10
            x=x_col,
            y=group_col,
            orientation='h',
            title=chart_title
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.subheader(f"FTE Distribution {title_suffix}")
        fig = px.bar(
            agg_df.head(10),
            x='Total FTE',
            y=group_col,
            orientation='h',
            title=f"Top 10 FTE {title_suffix}"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, width='stretch')
    
    # Detailed breakdown table
    st.subheader(f"Detailed Breakdown {title_suffix}")
    
    # Add selection for detailed view
    selected_item = st.selectbox(
        f"Select {drill_level} for detailed view",
        options=agg_df[group_col].tolist(),
        key="goal_detail_selection"
    )
    
    if selected_item:
        detailed_df = goals_df[goals_df[group_col] == selected_item]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Calculate appropriate allocation metric based on drill level
            if drill_level == "L4 Leaders":
                # For L4 Leaders, show average allocation across goals
                avg_allocation = detailed_df['Allocation %'].mean()
                st.metric("Average Allocation %", f"{avg_allocation:.1f}%")
            else:
                # For other levels, sum makes sense
                total_allocation = detailed_df['Allocation %'].sum()
                st.metric("Total Allocation %", f"{total_allocation:.1f}%")
            st.metric("Number of Goals", detailed_df['Goal Name'].nunique())
        
        with col2:
            # Calculate appropriate FTE metric based on drill level
            if drill_level == "L4 Leaders":
                # For L4 Leaders, get unique FTE per workstream to avoid double counting
                unique_fte = detailed_df.groupby('Workstream Name')['Target FTE Headcount'].first().sum()
                st.metric("Total Target FTE (Unique)", f"{unique_fte:.0f}")
            else:
                # For other levels, sum makes sense
                total_fte = detailed_df['Target FTE Headcount'].sum()
                st.metric("Total Target FTE", f"{total_fte:.0f}")
            st.metric("Number of Workstreams", detailed_df['Workstream Name'].nunique())
        
        # Show detailed records
        detail_cols = [
            'Workstream Name', 'Goal Name', 'Benefit L2', 'Allocation %', 
            'Target FTE Headcount', 'Active'
        ]
        
        st.dataframe(
            detailed_df[detail_cols],
            width='stretch',
            hide_index=True
        )

def normalize_workstream_name(name: str) -> str:
    """Normalize workstream name by removing common prefixes and cleaning"""
    if not name or not isinstance(name, str):
        return ""
    
    # Remove common prefixes
    prefixes_to_remove = [
        "SBG PD | ",
        "SBG | ",
        "GBSG ",
        "PDX | ",
        "Mailchimp | "
    ]
    
    normalized = name.strip()
    for prefix in prefixes_to_remove:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):].strip()
            break
    
    # Additional cleanup
    normalized = normalized.replace("  ", " ").strip()
    return normalized

def fuzzy_match_workstreams(people_workstreams: set, goal_workstreams: set) -> dict:
    """
    Create fuzzy matches between people and goal workstreams.
    Returns a dictionary mapping people workstream names to goal workstream names.
    """
    try:
        from difflib import SequenceMatcher
    except ImportError:
        # Fallback to simple string matching if difflib not available
        return {}
    
    matches = {}
    
    # First pass: exact matches after normalization
    people_normalized = {ws: normalize_workstream_name(ws) for ws in people_workstreams}
    goal_normalized = {ws: normalize_workstream_name(ws) for ws in goal_workstreams}
    
    # Create reverse lookup for goal workstreams
    goal_norm_to_original = {norm: orig for orig, norm in goal_normalized.items()}
    
    for people_ws, people_norm in people_normalized.items():
        if people_norm in goal_norm_to_original:
            matches[people_ws] = goal_norm_to_original[people_norm]
    
    # Second pass: fuzzy matching for unmatched workstreams
    unmatched_people = set(people_workstreams) - set(matches.keys())
    unmatched_goals = set(goal_workstreams) - set(matches.values())
    
    for people_ws in unmatched_people:
        people_norm = people_normalized[people_ws]
        best_match = None
        best_score = 0.0
        
        for goal_ws in unmatched_goals:
            goal_norm = goal_normalized[goal_ws]
            
            # Use sequence matcher for similarity
            score = SequenceMatcher(None, people_norm.lower(), goal_norm.lower()).ratio()
            
            # Boost score if one contains the other
            if people_norm.lower() in goal_norm.lower() or goal_norm.lower() in people_norm.lower():
                score = max(score, 0.8)
            
            if score > best_score and score >= 0.7:  # Minimum threshold for fuzzy match
                best_score = score
                best_match = goal_ws
        
        if best_match:
            matches[people_ws] = best_match
            unmatched_goals.remove(best_match)
    
    return matches

def create_integrated_view(goals_df: pd.DataFrame, people_df: Optional[pd.DataFrame] = None) -> None:
    """Create integrated view combining goal data with resource allocation data"""
    if goals_df.empty:
        st.warning("No goal data available")
        return
    
    st.header("🔗 Integrated Workstream Analysis")
    st.write("Combined view of goal mappings and detailed resource allocation")
    
    # If people_df is provided, try to match workstreams
    if people_df is not None and not people_df.empty:
        st.subheader("Workstream Matching Analysis")
        st.info("🔗 Using fuzzy matching to bridge workstream name differences between datasets")
        
        # Extract workstream names from people_df (from workstream columns)
        people_workstreams = set()
        for col_idx, col in enumerate(people_df.columns):
            if 'Workstream Display Name' in str(col):
                # Use iloc to access by position to avoid duplicate column name issues
                series = people_df.iloc[:, col_idx].dropna()
                ws_names = series.unique()
                # Filter out empty strings and null values
                ws_names = [name for name in ws_names if name and str(name).strip() != '']
                people_workstreams.update(ws_names)
        
        # Extract workstream names from goals_df
        goal_workstreams = set(goals_df['Workstream Name'].dropna().unique())
        
        # Create fuzzy matches
        fuzzy_matches = fuzzy_match_workstreams(people_workstreams, goal_workstreams)
        
        # Find exact matches (for backward compatibility)
        exact_matches = people_workstreams.intersection(goal_workstreams)
        
        # All matched workstreams (exact + fuzzy)
        matched_people_workstreams = set(fuzzy_matches.keys()) | exact_matches
        matched_goal_workstreams = set(fuzzy_matches.values()) | exact_matches
        
        goals_only = goal_workstreams - matched_goal_workstreams
        people_only = people_workstreams - matched_people_workstreams
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Matched Workstreams", len(matched_people_workstreams))
            if matched_people_workstreams:
                with st.expander("View Matched Workstreams"):
                    # Show exact matches
                    if exact_matches:
                        st.write("**Exact Matches:**")
                        for ws in sorted(exact_matches):
                            st.write(f"✅ {ws}")
                    
                    # Show fuzzy matches
                    if fuzzy_matches:
                        st.write("**Fuzzy Matches:**")
                        for people_ws, goal_ws in sorted(fuzzy_matches.items()):
                            st.write(f"🔗 {people_ws} ➜ {goal_ws}")
        
        with col2:
            st.metric("Goals Data Only", len(goals_only))
            if goals_only:
                with st.expander("View Goals-Only Workstreams"):
                    for ws in sorted(goals_only):
                        st.write(f"🎯 {ws}")
        
        with col3:
            st.metric("People Data Only", len(people_only))
            if people_only:
                with st.expander("View People-Only Workstreams"):
                    for ws in sorted(people_only):
                        st.write(f"👥 {ws}")
        
        st.divider()
        
        # Combined analysis for matched workstreams
        if matched_people_workstreams:
            st.subheader("Combined Analysis - Matched Workstreams")
            
            selected_workstream = st.selectbox(
                "Select Workstream for Detailed Analysis",
                options=sorted(matched_people_workstreams),
                key="integrated_workstream_selection"
            )
            
            if selected_workstream:
                # Determine the corresponding goal workstream name
                if selected_workstream in fuzzy_matches:
                    goal_workstream_name = fuzzy_matches[selected_workstream]
                else:
                    goal_workstream_name = selected_workstream  # Exact match
                
                # Goal information
                goal_info = goals_df[goals_df['Workstream Name'] == goal_workstream_name]
                
                st.write("**Goal Mapping Information:**")
                goal_summary_cols = ['Goal Name', 'Benefit L2', 'Allocation %', 'Target FTE Headcount']
                st.dataframe(goal_info[goal_summary_cols], width='stretch', hide_index=True)
                
                # Resource allocation information
                st.write("**Resource Allocation Information:**")
                
                # Find people assigned to this workstream
                workstream_people = people_df[
                    people_df.apply(lambda row: selected_workstream in str(row.values), axis=1)
                ]
                
                if not workstream_people.empty:
                    # Use the correct column names after ETL processing
                    people_summary_cols = ['resource_name', 'l3_org', 'type', 'total_allocation_pct']
                    
                    # Create a display-friendly copy with better column names
                    display_df = workstream_people[people_summary_cols].copy()
                    display_df.columns = ['Resource Name', 'L3 Org', 'Type', 'Total Allocation %']
                    st.dataframe(display_df, width='stretch', hide_index=True)
                    
                    # Summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Assigned Resources", len(workstream_people))
                    with col2:
                        avg_allocation = workstream_people['total_allocation_pct'].mean()
                        st.metric("Avg Resource Allocation", f"{avg_allocation:.1f}%")
                    with col3:
                        goal_target_fte = goal_info['Target FTE Headcount'].sum()
                        st.metric("Goal Target FTE", f"{goal_target_fte:.0f}")
                else:
                    st.info("No detailed resource allocation found for this workstream")
    
    # Standalone goal analysis
    st.subheader("Goal Summary by L4 Leaders")
    
    # Calculate proper metrics without summing allocation percentages
    leader_summary = []
    for leader in goals_df['L4 Leaders'].unique():
        leader_data = goals_df[goals_df['L4 Leaders'] == leader]
        unique_workstreams = leader_data['Workstream Name'].nunique()
        total_goals = leader_data['Goal Name'].nunique()
        # Calculate unique FTE by summing unique FTE per workstream
        unique_fte_per_ws = leader_data.groupby('Workstream Name')['Target FTE Headcount'].first().sum()
        avg_allocation = leader_data['Allocation %'].mean()
        
        leader_summary.append({
            'L4 Leaders': leader,
            'Workstreams': unique_workstreams,
            'Goals': total_goals,
            'Avg Allocation %': avg_allocation,
            'Total FTE (Unique)': unique_fte_per_ws
        })
    
    leader_summary = pd.DataFrame(leader_summary)
    leader_summary = leader_summary.sort_values('Total FTE (Unique)', ascending=False)
    
    st.dataframe(leader_summary, width='stretch', hide_index=True)
    
    # Goal Hierarchy Visualization - Using reliable chart types
    st.subheader("Goal Hierarchy Visualization")
    
    # Create a properly aggregated dataframe for visualization
    viz_df = goals_df[['L4 Leaders', 'Workstream Name', 'Goal Name', 'Allocation %', 'Target FTE Headcount']].copy()
    viz_df = viz_df.dropna(subset=['L4 Leaders', 'Workstream Name'])
    
    if not viz_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Workstream Distribution by L4 Leaders")
            # Aggregate by L4 Leaders and Workstream
            ws_by_leader = viz_df.groupby(['L4 Leaders', 'Workstream Name']).agg({
                'Target FTE Headcount': 'first',
                'Allocation %': 'mean',
                'Goal Name': 'nunique'
            }).reset_index()
            
            # Create stacked bar chart
            fig = px.bar(
                ws_by_leader,
                x='L4 Leaders',
                y='Target FTE Headcount',
                color='Workstream Name',
                title="FTE Distribution by L4 Leaders and Workstreams",
                hover_data=['Allocation %', 'Goal Name']
            )
            fig.update_layout(height=500, xaxis_tickangle=-45)
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            st.subheader("Goal Allocation Overview")
            # Create scatter plot showing FTE vs Allocation
            goal_scatter = viz_df.groupby(['L4 Leaders', 'Goal Name']).agg({
                'Target FTE Headcount': 'first',
                'Allocation %': 'first',
                'Workstream Name': 'first'
            }).reset_index()
            
            fig = px.scatter(
                goal_scatter,
                x='Target FTE Headcount',
                y='Allocation %',
                color='L4 Leaders',
                size='Target FTE Headcount',
                hover_data=['Goal Name', 'Workstream Name'],
                title="Goal Allocation vs Target FTE"
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, width='stretch')
    else:
        st.info("No data available for visualization")
    
    # L4 Leaders Summary Bar Chart
    st.subheader("L4 Leaders Summary")
    if not leader_summary.empty:
        summary_chart = px.bar(
            leader_summary.head(10),
            x='Total FTE (Unique)',
            y='L4 Leaders',
            orientation='h',
            title="Top 10 L4 Leaders by Target FTE",
            hover_data=['Workstreams', 'Goals', 'Avg Allocation %']
        )
        summary_chart.update_layout(height=500)
        st.plotly_chart(summary_chart, width='stretch')
