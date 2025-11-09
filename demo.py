#!/usr/bin/env python3
"""
Demo script for running Selenium tests and displaying results.

This script will:
1. Run all Selenium tests
2. Generate an HTML report
3. Open the report in the default web browser
"""

import os
import sys
import subprocess
import platform
import webbrowser
from pathlib import Path

def print_banner():
    """Print a nice banner for the demo."""
    banner = """
    #######################################################
    #  Selenium Login Automation - Test Runner            #
    #  Running automated tests for login functionality    #
    #######################################################
    """
    print(banner)

def run_tests():
    """Run pytest and generate HTML report."""
    print("🚀 Starting test execution...")
    
    # Create reports directory if it doesn't exist
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Run pytest with HTML reporting and keep browser open
    cmd = [
        "pytest",
        "src/tests/test_login_logout.py",
        "-v",
        "--html=reports/report.html",
        "--self-contained-html",
        "--no-quit"  # Keep browser open after tests
    ]
    
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
        return False

def open_report():
    """Open the HTML report in the default web browser."""
    report_path = Path("reports/report.html")
    
    if not report_path.exists():
        print("❌ Error: Test report not found!")
        return False
    
    print("🌐 Opening test report in browser...")
    try:
        report_url = f"file://{report_path.absolute()}"
        webbrowser.open(report_url)
        return True
    except Exception as e:
        print(f"❌ Failed to open report: {str(e)}")
        return False

def main():
    """Main function to run the demo."""
    print_banner()
    
    # Run tests
    success = run_tests()
    
    # Open report if tests completed (regardless of pass/fail)
    if success or True:  # Always try to open report if it exists
        open_report()
    
    # Print completion message
    if success:
        print("✅ Test execution completed successfully!")
    else:
        print("❌ Some tests failed. Please check the report for details.")
    
    print("\n💡 Tips:")
    print("  - The HTML report has been opened in your default browser")
    print("  - The browser was kept open due to the --no-quit flag")
    print("  - To close the browser, simply close the browser window")
    print("  - To run tests normally (with auto-close), use: pytest src/tests/")
    print("  - To run with browser kept open, use: pytest src/tests/ --no-quit")

if __name__ == "__main__":
    main()
