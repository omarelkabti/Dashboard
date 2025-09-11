#!/usr/bin/env python3
"""
PET Resource Allocation Dashboard - Deployment Script
Helps deploy the dashboard to various cloud platforms
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, cwd=None, shell=False):
    """Run a command and return success status"""
    try:
        result = subprocess.run(
            cmd if shell else cmd.split(),
            cwd=cwd,
            shell=shell,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

class PETDeployer:
    """Handles deployment of PET Dashboard to various platforms"""

    def __init__(self, project_dir="."):
        self.project_dir = Path(project_dir).absolute()
        self.requirements_file = self.project_dir / "requirements.txt"

    def check_requirements(self):
        """Check if all required files exist"""
        required_files = [
            "app.py",
            "src/etl.py",
            "src/store.py",
            "src/schema.py",
            "requirements.txt"
        ]

        missing = []
        for file in required_files:
            if not (self.project_dir / file).exists():
                missing.append(file)

        if missing:
            print("❌ Missing required files:")
            for file in missing:
                print(f"   - {file}")
            return False

        print("✅ All required files found")
        return True

    def deploy_colab(self):
        """Generate Google Colab deployment files"""
        print("🚀 Setting up Google Colab deployment...")

        # Create Colab notebook if it doesn't exist
        colab_file = self.project_dir / "PET_Dashboard_Colab.ipynb"
        if not colab_file.exists():
            print("❌ Colab notebook not found. Please run the Colab setup first.")
            return False

        print("✅ Colab deployment files ready")
        print("📝 Instructions:")
        print("   1. Open Google Colab: https://colab.research.google.com")
        print("   2. Upload PET_Dashboard_Colab.ipynb")
        print("   3. Run all cells in order")
        print("   4. Share the generated public URL")
        return True

    def deploy_streamlit_cloud(self):
        """Prepare for Streamlit Cloud deployment"""
        print("🚀 Preparing for Streamlit Cloud deployment...")

        # Create streamlit config
        config_dir = self.project_dir / ".streamlit"
        config_dir.mkdir(exist_ok=True)

        config_content = """[server]
headless = true
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 200
maxMessageSize = 200
enableWebsocketCompression = true

[browser]
gatherUsageStats = false
"""

        config_file = config_dir / "config.toml"
        with open(config_file, 'w') as f:
            f.write(config_content)

        # Create packages.txt for system dependencies
        packages_file = self.project_dir / "packages.txt"
        with open(packages_file, 'w') as f:
            f.write("# System dependencies for Streamlit Cloud\n")

        print("✅ Streamlit Cloud deployment ready")
        print("📝 Instructions:")
        print("   1. Push code to GitHub repository")
        print("   2. Go to: https://share.streamlit.io")
        print("   3. Connect your GitHub repo")
        print("   4. Select main branch and app.py")
        print("   5. Deploy!")
        return True

    def deploy_heroku(self):
        """Prepare for Heroku deployment"""
        print("🚀 Preparing for Heroku deployment...")

        # Create Procfile
        procfile_content = "web: streamlit run app.py --server.port $PORT --server.headless true --server.address 0.0.0.0"
        procfile = self.project_dir / "Procfile"
        with open(procfile, 'w') as f:
            f.write(procfile_content)

        # Create setup script
        setup_content = """#!/bin/bash
mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = $PORT
enableCORS = false
enableXsrfProtection = false
" > ~/.streamlit/config.toml
"""
        setup_file = self.project_dir / "setup.sh"
        with open(setup_file, 'w') as f:
            f.write(setup_content)

        # Make setup script executable
        os.chmod(setup_file, 0o755)

        # Update requirements.txt to include gunicorn
        with open(self.requirements_file, 'a') as f:
            f.write("\ngunicorn==20.1.0\n")

        print("✅ Heroku deployment ready")
        print("📝 Instructions:")
        print("   1. Install Heroku CLI")
        print("   2. heroku create your-pet-dashboard")
        print("   3. git push heroku main")
        print("   4. Access at: https://your-pet-dashboard.herokuapp.com")
        return True

    def deploy_gcp(self):
        """Prepare for Google Cloud Platform deployment"""
        print("🚀 Preparing for Google Cloud Platform deployment...")

        # Create Dockerfile
        dockerfile_content = """FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["streamlit", "run", "app.py", "--server.port", "8080", "--server.headless", "true", "--server.address", "0.0.0.0"]
"""
        dockerfile = self.project_dir / "Dockerfile"
        with open(dockerfile, 'w') as f:
            f.write(dockerfile_content)

        # Create .dockerignore
        dockerignore_content = """__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
node_modules
.streamlit
"""
        dockerignore = self.project_dir / ".dockerignore"
        with open(dockerignore, 'w') as f:
            f.write(dockerignore_content)

        print("✅ Google Cloud Platform deployment ready")
        print("📝 Instructions:")
        print("   1. Install Google Cloud SDK")
        print("   2. gcloud builds submit --tag gcr.io/PROJECT-ID/pet-dashboard")
        print("   3. gcloud run deploy --image gcr.io/PROJECT-ID/pet-dashboard --platform managed")
        return True

    def local_development(self):
        """Setup for local development"""
        print("🚀 Setting up local development environment...")

        # Create virtual environment if it doesn't exist
        venv_dir = self.project_dir / "venv"
        if not venv_dir.exists():
            print("📦 Creating virtual environment...")
            success, stdout, stderr = run_command("python -m venv venv", cwd=self.project_dir)
            if not success:
                print(f"❌ Failed to create virtual environment: {stderr}")
                return False

        # Install dependencies
        print("📦 Installing dependencies...")
        if os.name == 'nt':  # Windows
            pip_cmd = "venv\\Scripts\\pip install -r requirements.txt"
        else:  # Unix/Linux/Mac
            pip_cmd = "venv/bin/pip install -r requirements.txt"

        success, stdout, stderr = run_command(pip_cmd, cwd=self.project_dir, shell=True)
        if not success:
            print(f"❌ Failed to install dependencies: {stderr}")
            return False

        print("✅ Local development environment ready")
        print("📝 To start the dashboard:")
        if os.name == 'nt':  # Windows
            print("   venv\\Scripts\\streamlit run app.py")
        else:  # Unix/Linux/Mac
            print("   source venv/bin/activate")
            print("   streamlit run app.py")
        print("   # Access at: http://localhost:8501")
        return True

    def create_ngrok_tunnel(self):
        """Setup ngrok tunnel for local development"""
        print("🚀 Setting up ngrok tunnel...")

        try:
            # Check if ngrok is installed
            success, stdout, stderr = run_command("ngrok version")
            if not success:
                print("❌ ngrok not found. Please install ngrok:")
                print("   1. Download from: https://ngrok.com/download")
                print("   2. Sign up for free account")
                print("   3. Run: ngrok authtoken YOUR_TOKEN")
                return False

            print("✅ ngrok is installed")
            print("📝 To create public tunnel:")
            print("   1. Start dashboard: streamlit run app.py")
            print("   2. In new terminal: ngrok http 8501")
            print("   3. Share the https://xxxxx.ngrok.io URL")
            return True

        except Exception as e:
            print(f"❌ Error setting up ngrok: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Deploy PET Resource Allocation Dashboard")
    parser.add_argument(
        "platform",
        choices=["colab", "streamlit", "heroku", "gcp", "local", "ngrok"],
        help="Deployment platform"
    )
    parser.add_argument(
        "--project-dir",
        default=".",
        help="Project directory (default: current directory)"
    )

    args = parser.parse_args()

    deployer = PETDeployer(args.project_dir)

    # Check requirements
    if not deployer.check_requirements():
        print("❌ Please ensure all required files are present")
        sys.exit(1)

    # Deploy based on platform
    platform_map = {
        "colab": deployer.deploy_colab,
        "streamlit": deployer.deploy_streamlit_cloud,
        "heroku": deployer.deploy_heroku,
        "gcp": deployer.deploy_gcp,
        "local": deployer.local_development,
        "ngrok": deployer.create_ngrok_tunnel
    }

    success = platform_map[args.platform]()

    if success:
        print("\n🎉 Deployment preparation successful!")
        print("📖 Check DEPLOYMENT_GUIDE.md for detailed instructions")
    else:
        print("\n❌ Deployment preparation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
