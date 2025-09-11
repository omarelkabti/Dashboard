# 🚀 PET Dashboard - Databricks Deployment Guide

## 📋 Overview

This guide helps you deploy your PET Resource Allocation Dashboard in Databricks for enterprise-scale data processing and collaborative analytics.

## ✨ Why Databricks?

- **🔥 Apache Spark** - Distributed processing for large datasets
- **🤝 Collaborative** - Share notebooks with your team
- **📊 Interactive** - Real-time widgets and visualizations  
- **🔄 Scalable** - Auto-scaling compute clusters
- **🔐 Secure** - Enterprise-grade security and governance
- **📈 Integrated** - Built-in ML, SQL, and BI capabilities

## 🚀 Quick Start

### Step 1: Upload the Notebook
1. In your Databricks workspace, go to **Workspace** → **Import**
2. Upload `PET_Dashboard_Databricks.py`
3. The notebook will appear in your workspace

### Step 2: Upload Your Data
1. Go to **Data** → **Create Table**
2. Upload your PET Resource Allocation CSV file
3. Note the file path (e.g., `/FileStore/shared_uploads/your_file.csv`)

### Step 3: Configure and Run
1. Open the imported notebook
2. Update the `file_path` widget with your CSV path
3. Choose the appropriate `file_format` (auto-detect recommended)
4. **Run All Cells** (Cmd/Ctrl + Shift + Enter)

## 📊 Features

### Smart Data Processing
- **Auto-header detection** - Handles both embedded and standard CSV formats
- **Dynamic workstream discovery** - Automatically finds workstream columns
- **Robust parsing** - Handles various data formats and edge cases
- **Type normalization** - Standardizes employee types and allocations

### Interactive Dashboard
- **Real-time filtering** - Use widgets to filter by Manager, Type, Organization
- **Live visualizations** - Pie charts, bar charts, and data tables
- **Key metrics** - Total resources, FTE, allocation status
- **Workstream analysis** - Detailed breakdown by workstream

### Data Export
- **CSV export** - Processed data saved to DBFS
- **Timestamped files** - Automatic versioning
- **Shareable results** - Easy download and sharing

## 🎛️ Widget Controls

The dashboard includes interactive widgets for dynamic filtering:

| Widget | Purpose | Options |
|--------|---------|---------|
| `file_path` | CSV file location | Text input |
| `file_format` | Format detection | auto, legacy, new |
| `filter_manager` | Manager filter | Dropdown list |
| `filter_type` | Resource type filter | Employee, Contractor, etc. |
| `filter_l3_org` | Organization filter | L3 organization list |

## 📈 Visualizations

### 1. Allocation Status Distribution
- **Pie Chart** showing overallocated, underallocated, and unassigned resources
- **Color-coded** for easy identification
- **Interactive** - click to filter

### 2. Workstream FTE Analysis  
- **Bar Chart** of FTE allocation by workstream
- **Sorted** by allocation amount
- **Responsive** to filters

### 3. Data Tables
- **Resource Overview** - Main resource data
- **Workstream Assignments** - Detailed workstream breakdown
- **Sortable and filterable**

## 🔧 Advanced Usage

### Scheduling Regular Updates
```python
# Create a Databricks Job to run this notebook daily
# Go to Jobs → Create Job → Select this notebook
# Set schedule: Daily at 9 AM
```

### Connecting to Databricks SQL
```sql
-- Create a table from processed data
CREATE TABLE pet_resources 
USING CSV
OPTIONS (path '/FileStore/shared_uploads/pet_processed_main_*.csv', header 'true')
```

### Integration with MLflow
```python
# Track model performance and data quality metrics
import mlflow
with mlflow.start_run():
    mlflow.log_metric("total_resources", len(df))
    mlflow.log_metric("data_quality_score", quality_score)
```

## 🔐 Security and Governance

### Data Access Control
- Use **Databricks Unity Catalog** for centralized governance
- Apply **row-level security** for sensitive data
- Enable **audit logging** for compliance

### Best Practices
1. **Store sensitive data** in Delta Lake with encryption
2. **Use service principals** for automated workflows  
3. **Implement data classification** tags
4. **Regular access reviews** and permissions audit

## 🛠️ Troubleshooting

### Common Issues

**❌ "File not found" error**
- Check the file path in the widget
- Ensure the CSV is uploaded to FileStore
- Verify file permissions

**❌ "No workstream assignments" found**
- Check your CSV format - ensure workstream columns are properly named
- Try different `file_format` settings (auto, legacy, new)
- Verify percentage values are numeric

**❌ Memory errors with large files**
- Use a larger cluster configuration
- Consider partitioning your data
- Use Spark DataFrame operations for very large datasets

### Performance Optimization

```python
# For large datasets, use Spark DataFrames
spark_df = spark.read.csv(file_path, header=True, inferSchema=True)
spark_df.cache()  # Cache for repeated operations
```

## 📚 Additional Resources

- [Databricks Documentation](https://docs.databricks.com/)
- [Spark SQL Guide](https://spark.apache.org/docs/latest/sql-programming-guide.html)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Delta Lake Guide](https://docs.delta.io/latest/index.html)

## 🤝 Support

Need help? Here are your options:

1. **Internal Team** - Share this notebook with colleagues
2. **Databricks Community** - Active forums and documentation
3. **Professional Services** - Databricks consulting available

---

## ✅ Checklist

- [ ] Databricks workspace access
- [ ] CSV file uploaded to FileStore  
- [ ] Notebook imported and configured
- [ ] Widgets configured with correct file path
- [ ] Dashboard running successfully
- [ ] Team members granted access
- [ ] Regular refresh schedule configured (optional)

**🎉 You're ready to analyze your PET resource allocation data at scale!**
