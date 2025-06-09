"""
Test runner script for Clinic Voice AI

This script runs the automated test scenarios and generates a test report.
"""

import os
import logging
from src.test_scenarios import run_all_tests, generate_test_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Running Clinic Voice AI tests")
    
    # Run tests
    results = run_all_tests()
    
    # Generate report
    report = generate_test_report(results)
    
    # Save report
    with open("test_report.md", "w") as f:
        f.write(report)
    
    logger.info("Test report saved to test_report.md")
