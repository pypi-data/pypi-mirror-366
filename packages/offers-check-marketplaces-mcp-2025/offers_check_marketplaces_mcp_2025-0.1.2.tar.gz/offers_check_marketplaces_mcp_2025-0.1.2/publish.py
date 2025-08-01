#!/usr/bin/env python3
"""
Script for building and publishing the offers-check-marketplaces package to PyPI
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    print(f"Running: {' '.join(command)}")
    
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error {description}:")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        sys.exit(1)
    else:
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    required_packages = ['build', 'twine']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is not installed")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        run_command([sys.executable, "-m", "pip", "install"] + missing_packages, 
                   "Installing missing packages")

def clean_build():
    """Clean previous build artifacts"""
    print("\n🧹 Cleaning previous build artifacts...")
    
    dirs_to_clean = ['build', 'dist', 'offers_check_marketplaces.egg-info']
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            import shutil
            shutil.rmtree(dir_path)
            print(f"✅ Removed {dir_name}")
        else:
            print(f"ℹ️  {dir_name} doesn't exist")

def build_package():
    """Build the package"""
    run_command([sys.executable, "-m", "build"], "Building package")

def check_package():
    """Check the built package"""
    run_command([sys.executable, "-m", "twine", "check", "dist/*"], "Checking package")

def upload_to_test_pypi():
    """Upload to Test PyPI"""
    print("\n🚀 Uploading to Test PyPI...")
    print("You will need to enter your Test PyPI credentials")
    
    result = subprocess.run([
        sys.executable, "-m", "twine", "upload", 
        "--repository", "testpypi", 
        "dist/*"
    ])
    
    if result.returncode == 0:
        print("✅ Successfully uploaded to Test PyPI")
        print("🔗 Check your package at: https://test.pypi.org/project/offers-check-marketplaces/")
    else:
        print("❌ Failed to upload to Test PyPI")
        return False
    
    return True

def upload_to_pypi():
    """Upload to PyPI"""
    print("\n🚀 Uploading to PyPI...")
    print("You will need to enter your PyPI credentials")
    
    result = subprocess.run([
        sys.executable, "-m", "twine", "upload", 
        "dist/*"
    ])
    
    if result.returncode == 0:
        print("✅ Successfully uploaded to PyPI")
        print("🔗 Check your package at: https://pypi.org/project/offers-check-marketplaces/")
    else:
        print("❌ Failed to upload to PyPI")
        return False
    
    return True

def main():
    """Main function"""
    print("=" * 60)
    print("📦 OFFERS-CHECK-MARKETPLACES PACKAGE PUBLISHER")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ pyproject.toml not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Check requirements
    check_requirements()
    
    # Clean previous builds
    clean_build()
    
    # Build package
    build_package()
    
    # Check package
    check_package()
    
    # Ask user what to do
    print("\n" + "=" * 60)
    print("📋 PUBLISHING OPTIONS")
    print("=" * 60)
    print("1. Upload to Test PyPI (recommended for testing)")
    print("2. Upload to PyPI (production)")
    print("3. Exit without uploading")
    
    while True:
        choice = input("\nEnter your choice (1/2/3): ").strip()
        
        if choice == "1":
            upload_to_test_pypi()
            break
        elif choice == "2":
            confirm = input("⚠️  Are you sure you want to upload to production PyPI? (yes/no): ").strip().lower()
            if confirm == "yes":
                upload_to_pypi()
            else:
                print("❌ Upload cancelled")
            break
        elif choice == "3":
            print("👋 Exiting without uploading")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")
    
    print("\n" + "=" * 60)
    print("✅ PUBLISHING PROCESS COMPLETED")
    print("=" * 60)
    
    # Show installation instructions
    print("\n📋 INSTALLATION INSTRUCTIONS:")
    print("For Test PyPI:")
    print("  pip install -i https://test.pypi.org/simple/ offers-check-marketplaces")
    print("\nFor PyPI:")
    print("  pip install offers-check-marketplaces")

if __name__ == "__main__":
    main()