# 🚀 PET Resource Allocation Dashboard - Deployment Guide

This guide shows you how to deploy the PET Resource Allocation Dashboard and make it accessible via various cloud platforms, including Google Drive integration.

## 📋 Table of Contents

1. [Quick Start - Google Colab](#google-colab-quick-start)
2. [Google Drive Integration](#google-drive-integration)
3. [Streamlit Cloud Deployment](#streamlit-cloud)
4. [Google Cloud Platform](#google-cloud-platform)
5. [Heroku Deployment](#heroku-deployment)
6. [Local Development](#local-development)

---

## 🌐 Google Colab Quick Start

The fastest way to get your dashboard running with public access.

### Step 1: Upload Files to Google Colab

1. Go to [Google Colab](https://colab.research.google.com)
2. Create a new notebook
3. Upload the `PET_Dashboard_Colab.ipynb` file
4. Or copy the code from the notebook manually

### Step 2: Run the Setup

Execute each cell in order:

```python
# Cell 1: Install dependencies
!pip install -q streamlit pandas plotly openpyxl pyngrok

# Cell 2: Create directory structure
!mkdir -p src/components src/views data
```

### Step 3: Upload Your Data

```python
# Upload your PET CSV files to the data/ folder
# Or use the sample data generator in Cell 3
```

### Step 4: Launch Dashboard

Run the final cell to start the dashboard with public access:

```python
# This will create a public URL using ngrok
# The dashboard will be accessible from anywhere
```

### ✅ Result
- **Public URL**: `https://xxxxx.ngrok.io`
- **Features**: Full dashboard with public access
- **Cost**: Free (with ngrok limitations)
- **Persistence**: Runs while Colab session is active

---

## 📁 Google Drive Integration

### Method 1: Colab + Google Drive

1. **Mount Google Drive in Colab**:
```python
from google.colab import drive
drive.mount('/content/drive')

# Copy dashboard files
!cp -r /content/drive/MyDrive/PET_Dashboard/* ./
```

2. **Store data in Google Drive**:
```python
# Your CSV files will be accessible from Google Drive
data_path = '/content/drive/MyDrive/PET_Data/'
```

### Method 2: Google Apps Script Web App

1. **Create Google Apps Script**:
```javascript
function doGet() {
  return HtmlService
    .createHtmlOutputFromFile('index')
    .setTitle('PET Dashboard');
}
```

2. **Deploy as Web App**:
   - Go to Deploy > New deployment
   - Select "Web app"
   - Execute as "Me", Access as "Anyone"
   - Get the public URL

### Method 3: Google Sites Integration

1. **Create Google Site**
2. **Embed Colab iframe**:
```html
<iframe src="YOUR_COLAB_URL" width="100%" height="600"></iframe>
```

---

## ☁️ Streamlit Cloud Deployment

### Step 1: Prepare Repository

1. **Create GitHub Repository**:
```bash
# Initialize git repo
git init
git add .
git commit -m "Initial PET Dashboard"

# Push to GitHub
git remote add origin https://github.com/yourusername/pet-dashboard.git
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud

1. Go to [Streamlit Cloud](https://share.streamlit.io)
2. Connect your GitHub repository
3. Select main branch and app.py
4. Deploy!

### Step 3: Configure Secrets

Add environment variables for sensitive data:
- Database connections
- API keys
- File paths

### ✅ Streamlit Cloud Benefits
- **Free tier**: 100 hours/month
- **Custom domains**: your-app.streamlit.app
- **Automatic HTTPS**
- **GitHub integration**

---

## 🏢 Google Cloud Platform (GCP)

### Option 1: Google Cloud Run

1. **Create Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["streamlit", "run", "app.py", "--server.port", "8080", "--server.headless", "true"]
```

2. **Deploy to Cloud Run**:
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/pet-dashboard
gcloud run deploy --image gcr.io/PROJECT-ID/pet-dashboard --platform managed
```

### Option 2: Google App Engine

1. **Create app.yaml**:
```yaml
runtime: python39
entrypoint: streamlit run app.py --server.port $PORT --server.headless true

env_variables:
  PORT: "8080"
```

2. **Deploy**:
```bash
gcloud app deploy
```

### ✅ GCP Benefits
- **Scalable**: Auto-scaling based on traffic
- **Secure**: Google Cloud security
- **Integrated**: Works with other Google services
- **Cost-effective**: Pay only for what you use

---

## 🟣 Heroku Deployment

### Step 1: Prepare Files

1. **Create requirements.txt** (already exists)
2. **Create Procfile**:
```
web: streamlit run app.py --server.port $PORT --server.headless true
```

3. **Create setup.sh**:
```bash
mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
```

### Step 2: Deploy

```bash
# Install Heroku CLI
# Create Heroku app
heroku create your-pet-dashboard

# Deploy
git push heroku main
```

### ✅ Heroku Benefits
- **Free tier**: 550-1000 hours/month
- **Custom domains**
- **Add-ons ecosystem**
- **Easy scaling**

---

## 💻 Local Development

### Quick Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run app.py

# Access at http://localhost:8501
```

### Advanced Local Setup

```bash
# Create virtual environment
python -m venv pet_env
source pet_env/bin/activate  # Linux/Mac
# or
pet_env\\Scripts\\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run with custom settings
streamlit run app.py --server.port 8501 --server.headless false
```

---

## 🔧 Configuration Options

### Environment Variables

Create a `.env` file for configuration:

```bash
# Data settings
DATA_DIR=./data
CSV_PATTERN=PET Resource Allocation*.csv

# Server settings
PORT=8501
HOST=0.0.0.0

# Feature flags
ENABLE_AUTO_REFRESH=true
REFRESH_INTERVAL=300
```

### Custom Configuration

Modify `src/schema.py` for your specific needs:

```python
# Custom column mappings
HEADER_MAP = {
    'Your Manager Column': 'manager',
    'Your Resource Column': 'resource_raw',
    # ... add your mappings
}

# Custom workstream pairs
WORKSTREAM_PAIRS = [
    ('Your WS 1', 'Your % 1'),
    ('Your WS 2', 'Your % 2'),
    # ... add your pairs
]
```

---

## 🌟 Recommended Deployment Strategy

### For Teams (Recommended)
1. **Primary**: Streamlit Cloud (easy, free tier)
2. **Backup**: Google Colab (quick setup, public access)
3. **Production**: Google Cloud Run (scalable, enterprise-ready)

### For Individuals
1. **Primary**: Google Colab + ngrok (free, immediate access)
2. **Backup**: Local development with ngrok tunneling

### For Enterprises
1. **Primary**: Google Cloud Platform (security, scalability)
2. **Backup**: Streamlit Cloud (quick prototyping)

---

## 🚨 Troubleshooting

### Common Issues

1. **Memory Errors**:
   - Reduce data size
   - Use pagination in dataframes
   - Implement data caching

2. **File Upload Issues**:
   - Check file size limits
   - Verify CSV format
   - Clear browser cache

3. **Performance Issues**:
   - Optimize data processing
   - Use Streamlit caching
   - Implement lazy loading

4. **Access Issues**:
   - Check firewall settings
   - Verify ngrok authentication
   - Confirm port availability

---

## 📞 Support

### Getting Help

1. **Documentation**: Check this guide first
2. **Logs**: Check Streamlit logs for errors
3. **Browser Console**: Look for JavaScript errors
4. **Network Issues**: Verify internet connectivity

### Performance Monitoring

```python
# Add to your app.py for monitoring
import logging
logging.basicConfig(level=logging.INFO)

# Monitor resource usage
import psutil
st.write(f"Memory usage: {psutil.virtual_memory().percent}%")
```

---

## 🎯 Next Steps

1. **Choose your deployment method** based on your needs
2. **Set up your data pipeline** for regular CSV updates
3. **Configure user access** and permissions
4. **Monitor performance** and optimize as needed
5. **Add custom features** specific to your workflow

**🚀 Your PET Resource Allocation Dashboard is ready for deployment!**
