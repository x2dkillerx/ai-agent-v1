"""
Run script for Clinic Voice AI web demo
"""

import os
import logging
from app import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting Clinic Voice AI web demo")
    app.run(host='0.0.0.0', port=5000, debug=True)
