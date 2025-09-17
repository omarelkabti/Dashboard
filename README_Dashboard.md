# PET Resource Allocation Dashboard

A local Streamlit dashboard for analyzing PET resource allocation data with a focus on Workstream 1 completion tracking.

## Features

### 🎯 Workstream 1 Completion Tracking
- **Primary Focus**: Identifies which teams have mapped their resources to Workstream 1
- **Completion Detection**: Resources are marked as "completed" when they have any content in the Workstream 1 column
- **Visual Analytics**: Bar charts showing completion rates by L3 organization

### 📊 Hierarchical Drilldown Analysis
- **Multi-level Views**: Analyze data by Resource, Supervisor, Director, VP, and L3 levels
- **Pivot Table Functionality**: Interactive drilldown through organizational hierarchy
- **Key Metrics**: Resource counts, completion rates, allocation statistics

### 📋 Detailed Resource Analysis
- **Advanced Filtering**: Filter by L3 org, completion status, and allocation status
- **Resource-level Details**: Individual resource allocation and completion status
- **Export-ready Views**: Clean tabular format for further analysis

## Data Structure

The dashboard handles CSV files with a **two-header-row format**:
1. **Row 1**: Technical headers (`Workstream 1`, `% 1`, `Workstream 2`, `% 2`, etc.)
2. **Row 2**: Business headers (`Supervisor or Hiring Manager`, `Resource or Rec/Offer`, etc.)
3. **Row 3+**: Actual data

### Key Data Points
- **Workstream 1 Completion**: Detected when there's content in the "Workstream 1" column
- **Resource Allocation**: Percentage allocation across multiple workstreams
- **Organizational Hierarchy**: L3 → VP → Director → Manager → Resource

## Installation & Setup

### Prerequisites
```bash
pip install -r requirements.txt
```

### Required Dependencies
- `streamlit>=1.28.0`
- `pandas>=2.0.0`
- `plotly>=5.15.0`
- `numpy>=1.24.0`

### Data Setup
1. **Resource Allocation Data**: Place your PET Resource Allocation CSV files in the `data/` directory
2. **Workstream-Goals Mapping Data**: Place your PET Workstream Goals Data Grid CSV files in the `looker_data/` directory
3. The dashboard will automatically use the most recently modified CSV file from each directory

### Goal Mapping Data Format
For files in `looker_data/` (files with "Goals" in filename):
- **Columns A-M**: Base workstream information (Name, Description, L4 Leaders, Target FTE, etc.)
- **Columns N+**: Goal columns in groups of 6 (Priority, Goal Name, Goal Description, Benefit L2, Allocation %, Active)
- **Two-header format**: Goal numbers in row 1, detailed column names in row 2

### Running the Dashboard
```bash
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

## Dashboard Sections

### 1. Summary Metrics
- Total resources count
- Workstream 1 completion rate
- Allocation issues summary
- Average allocation percentage

### 2. Workstream 1 Overview Tab
- **Completion by L3 Organization**: Visual bar chart showing completion rates
- **Detailed Completion Table**: Exact counts and percentages

### 3. Hierarchical Analysis Tab
- **Level Selection**: Choose from L3 Org, VP Org, Director Org, Manager
- **Interactive Drilldown**: Click through organizational levels
- **Metrics per Level**: Resources, completion rates, allocation issues

### 4. Detailed View Tab
- **Multi-dimensional Filtering**: 
  - L3 Organization
  - Workstream 1 completion status
  - Allocation status (Over/Under/Unassigned/Proper)
- **Resource-level Details**: Individual allocation and status information

### 5. Goal Overview Tab (NEW)
- **Goal Mapping Summary**: Total workstreams, goals, and FTE allocation
- **Allocation Visualizations**: 
  - Allocation by workstream (horizontal bar chart)
  - Allocation by benefit type (pie chart)
- **Goal Details Table**: Filterable table with:
  - L4 Leaders filter
  - Benefit type filter
  - Active goals only toggle

### 6. Goal Analysis Tab (NEW)
- **Interactive Drilldown**: Analysis by L4 Leaders, Workstream, Goal, or Benefit Type
- **Dual Visualizations**: Allocation and FTE distribution charts
- **Detailed Breakdown**: Selection-based detailed view with metrics

### 7. Integrated View Tab (NEW)
- **Workstream Matching**: Shows which workstreams appear in both datasets
- **Combined Analysis**: Detailed view for matched workstreams showing:
  - Goal mapping information (allocation %, benefit type, target FTE)
  - Resource allocation details (assigned people, allocation percentages)
- **L4 Leader Summary**: Aggregated view by leadership
- **Hierarchy Visualization**: Treemap showing goal allocation hierarchy

## Key Metrics Explained

### Workstream 1 Completion
- ✅ **Completed**: Resource has content in Workstream 1 column
- ❌ **Not Completed**: Workstream 1 column is empty

### Allocation Status
- **Overallocated**: Total allocation > 100%
- **Underallocated**: Total allocation < 100%
- **Unassigned**: Total allocation = 0%
- **Properly Allocated**: Total allocation = 100%

### Completion Rate
- Percentage of resources within an organizational unit that have completed Workstream 1 mapping

## File Structure

```
Dashboard/
├── app.py                 # Main Streamlit dashboard
├── src/
│   ├── etl.py            # ETL pipeline with header detection
│   └── __init__.py
├── data/                 # CSV data files
├── requirements.txt      # Python dependencies
└── README_Dashboard.md   # This file
```

## ETL Pipeline Features

### Embedded Header Detection
- Automatically detects the two-header-row format
- Combines technical and business headers appropriately
- Handles dynamic workstream detection

### Data Processing
- **Employee Parsing**: Extracts ID, name, and title from resource strings
- **Allocation Computation**: Automatically calculates total allocation percentages
- **Workstream Detection**: Dynamically finds all workstream/percentage pairs
- **Hierarchical Summarization**: Creates rollup views for organizational analysis

### Error Handling
- Robust data type conversion
- Graceful handling of missing or malformed data
- Validation of allocation consistency

## Usage Tips

1. **Data Refresh**: Reload the browser page to pick up new CSV files
2. **Performance**: The dashboard is optimized for datasets with hundreds to thousands of resources
3. **Filtering**: Use the combination of filters in the Detailed View tab for targeted analysis
4. **Export**: Copy data from tables for use in other tools (Excel, etc.)

## Troubleshooting

### Common Issues

**Dashboard won't start**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're in the correct directory when running `streamlit run app.py`

**No data showing**
- Verify CSV files are in the `data/` directory
- Check that CSV files follow the expected two-header format
- Look for error messages in the Streamlit interface

**Incorrect completion rates**
- Verify that Workstream 1 data is in the expected column
- Check for extra spaces or formatting issues in the CSV

**Memory issues with large files**
- The dashboard is designed for typical organizational datasets
- For very large files (>10k resources), consider splitting the data

## Support

For issues or questions about the dashboard:
1. Check the error messages in the Streamlit interface
2. Verify your CSV file format matches the expected structure
3. Review the console output for detailed error information
