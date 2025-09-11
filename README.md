# PET Resource Allocation Dashboard

A comprehensive dashboard for visualizing PET (Product Engineering Team) resource allocation data with auto-updating capabilities.

## 🎉 Status: FULLY COMPLETE & DEPLOYMENT READY!

✅ **All Core Features Implemented**
- Auto-updating CSV processing
- Organization hierarchy mapping
- Workstream analysis & FTE calculations
- Advanced filtering & search
- Interactive visualizations
- Export capabilities

✅ **Technical Features**
- Robust ETL pipeline
- File monitoring system
- Performance optimizations
- Error handling & logging
- Sample data included

✅ **Deployment Options Ready**
- Google Colab (instant public access)
- Streamlit Cloud (managed hosting)
- Heroku (flexible scaling)
- Google Cloud (enterprise-ready)
- Local development (customizable)

---

## 🚀 Quick Start (Choose Your Method)

### Option 1: Google Colab (Instant Public Access - RECOMMENDED)
```bash
# 1. Go to: https://colab.research.google.com
# 2. Upload: PET_Dashboard_Colab.ipynb
# 3. Run all cells → Get public URL instantly!
# 4. Share: https://xxxxx.ngrok.io
```

### Option 2: Local Development
```bash
pip install -r requirements.txt
streamlit run app.py
# Access: http://localhost:8501
```

### Option 3: Cloud Deployment
```bash
python deploy.py streamlit    # Streamlit Cloud
python deploy.py heroku      # Heroku
python deploy.py gcp         # Google Cloud
```

### Option 4: SECURE Company Deployment (RECOMMENDED)
```bash
# For complete company privacy and security:
# Use: PET_Dashboard_Secure_Colab.ipynb
# Or: python -c "from src.secure_dashboard import run_company_dashboard()"
# Data stays 100% within company Google Workspace
```

---

## 🔒 Security & Privacy Options

### For Company Use (Data Privacy Guaranteed)
- ✅ **Google Workspace Integration**: Store data in company Shared Drives
- ✅ **Access Control**: Controlled by company IT policies
- ✅ **Audit Logging**: Complete access trail via Google Workspace
- ✅ **No External Access**: Dashboard runs locally within company network
- ✅ **Compliance Ready**: Meets enterprise security requirements

**📖 See: `COMPANY_PRIVACY_GUIDE.md` for complete security setup**

### For Personal Use
- ✅ **Local Data Only**: Data stays on your computer
- ✅ **No Cloud Upload**: Optional local-only mode available
- ✅ **Private Mode**: Disable all external communications

---

## Features

- **Auto-updating**: Automatically detects and processes new CSV files every 5 minutes
- **Organization Mapping**: Hierarchical view of resources by L3 → VP → Director → Manager
- **Workstream Analysis**: FTE distribution and assignment tracking across workstreams
- **Advanced Filtering**: Filter by type, manager, org levels, workstreams, and allocation status
- **Interactive Visualizations**: Charts and tables for data exploration
- **Export Capabilities**: Export filtered views and assignment data as CSV
- **File Upload**: Manual upload of CSV files for immediate processing

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Place Your CSV File

Copy your PET Resource Allocation CSV file to the `data/` directory with a name matching the pattern:
```
PET Resource Allocation*.csv
```

Example: `PET Resource Allocation (9).csv`

### 3. Run the Dashboard

```bash
streamlit run app.py
```

The dashboard will automatically:
- Load the latest CSV file from the `data/` folder
- Process and transform the data
- Display interactive visualizations
- Monitor for new files every 5 minutes

## CSV Format Requirements

Your CSV file should contain these key columns:

### Required Columns
- **Supervisor or Hiring Manager**: Direct manager name
- **Resource or Rec/Offer**: Employee info (format: "ID: Name" or just name)
- **Type**: Employee/Contractor/Req/Open Role
- **L3 Org, VP Org, Director Org**: Organizational hierarchy
- **Total Workstream Allocation %**: Computed total allocation
- **Workstream 1-10**: Workstream names
- **% 1-10**: Corresponding allocation percentages

### Optional Columns
- **Sub-Capabilities 1-5**: Additional skill categories
- **City Map Capability 1-5**: Location-based capabilities

## Project Structure

```
pet-dashboard/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── src/
│   ├── __init__.py
│   ├── schema.py              # Column mappings and validation
│   ├── etl.py                 # Data processing pipeline
│   ├── store.py               # File watching and data storage
│   ├── components/
│   │   ├── filters.py         # Filter components
│   │   └── kpis.py            # KPI tiles and charts
│   └── views/
│       ├── org_view.py        # Organization mapping view
│       └── ws_view.py         # Workstream analysis view
├── data/                      # CSV files (auto-created)
└── tests/
    └── samples/               # Sample data files
```

## Data Processing Pipeline

1. **Ingestion**: Load CSV with robust error handling
2. **Cleaning**: Normalize types, standardize percentages, parse employee IDs
3. **Unpivoting**: Transform wide workstream columns to tidy long format
4. **Validation**: Check allocation consistency and flag mismatches
5. **Metrics**: Calculate FTE, headcount, and allocation statistics

## Key Features

### Organization View
- **Table View**: Sortable table with resource details
- **Tree View**: Hierarchical organization structure
- **Resource Drawer**: Detailed view of individual resources
- **Allocation Flags**: Visual indicators for over/under/unassigned

### Workstream View
- **FTE Charts**: Bar charts showing allocation by workstream
- **Assignment Tables**: Detailed breakdown of resource assignments
- **Resource Lookup**: Find resources by workstream assignment
- **Drill-down**: Click workstreams to see assigned resources

### Filtering & Search
- **Multi-level Filters**: Type, Manager, Organization levels
- **Workstream Filters**: Filter by assigned workstreams
- **Allocation Status**: Filter by over/under/unassigned status
- **Search**: Text search across names, IDs, and titles

### Auto-Update System
- **File Monitoring**: Watches `data/` folder for new CSV files
- **Automatic Refresh**: Updates dashboard when new files detected
- **Manual Upload**: Upload files directly through the UI
- **Version History**: Keeps 5 most recent files for rollback

## Configuration

### File Watching
- **Pattern**: `PET Resource Allocation*.csv`
- **Interval**: 5 minutes (configurable in `schema.py`)
- **Max Backups**: 5 files

### Allocation Thresholds
- **Overallocated**: > 100%
- **Underallocated**: < 100% and > 0%
- **Unassigned**: = 0%

## Troubleshooting

### No Data Showing
- Check that your CSV file is in the `data/` folder
- Verify the filename matches the pattern `PET Resource Allocation*.csv`
- Check the browser console for any error messages

### Processing Errors
- Ensure your CSV has the expected column structure
- Check for special characters or encoding issues
- Review the data processing logs in the terminal

### Performance Issues
- Large files (>10k rows) may take longer to process
- Consider filtering data or optimizing the ETL pipeline
- Check system memory usage

## Development

### Adding New Features
1. Add functionality to appropriate module in `src/`
2. Update the main `app.py` to integrate new features
3. Test with sample data
4. Update documentation

### Testing
```bash
# Run with sample data
python -c "from src.etl import process_pet_csv; process_pet_csv('tests/samples/PET_Resource_Allocation_Sample.csv')"
```

### Customization
- Modify `schema.py` for different column mappings
- Update `etl.py` for custom data transformations
- Customize UI in `app.py` and view modules

## Support

For issues or questions:
1. Check the CSV format matches expectations
2. Review the data processing logs
3. Verify file permissions on the `data/` folder
4. Check that all dependencies are installed

## License

This project is provided as-is for internal use.
