import os
import sys
from pathlib import Path
import logging
import platform

# Database setup
def get_data_dir():
    try:
        if os.name == 'nt':  # Windows
            path = Path(os.getenv('LOCALAPPDATA')) / 'CineLog'
        elif os.name == 'posix':
            if sys.platform == 'darwin':  # macOS
                path = Path.home() / 'Library' / 'Application Support' / 'CineLog'
            else:  # Linux
                path = Path.home() / '.local' / 'share' / 'CineLog'
        else:
            logging.warning("Unsupported OS type.")
            return None

        print(f"os.name: {os.name}")
        print(f"sys.platform: {sys.platform}")
        print(f"Path.home(): {Path.home()}")
        logging.info(f"Path.home(): {Path.home()}")
        logging.info(f"sys.platform: {sys.platform}")
        logging.info(f"os.name: {os.name}")
        logging.info(f"platform: {platform.uname()}")

        path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Using data directory: {path}")
        return path

    except Exception as e:
        logging.error(f"Failed to create or access data directory: {e}", exc_info=True)
        return None