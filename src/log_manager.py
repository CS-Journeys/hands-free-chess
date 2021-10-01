import os
import logging
import logging.config
import yaml
import sys

LOG_CONF_FILE = 'config/log_config.yaml'
MAX_LOG_SIZE = 20 # MB
HFC_DOCS_DIR = os.path.expanduser('./')
LOG_DIR = HFC_DOCS_DIR + 'log/'

class LogManager:
    """
    When initialized, the LogManager:
        (a) configures the logger(s)
        (b) deletes the log files if the log directory is too big
    """
    def __init__(self):
        # Global logging setup
        if _get_directory_size(LOG_DIR, 'MB') > MAX_LOG_SIZE:
            _delete_log_files()
        _configure_logging()

        # LogManager logging setup
        self.log = logging.getLogger(__name__)

def _get_directory_size(directory, unit):
    """
    Returns the total size (in 'unit' units) of a directory's contents.
    Parameters:
        - directory: a string representation of the directory
        - unit: a string representation of a unit ('KB', 'MB', 'GB', etc.)
    """
    total_bytes = 0
    for path, dirs, files in os.walk(directory):
        for f in files:
            fp = os.path.join(path, f)
            total_bytes += os.path.getsize(fp)
    result = round(total_bytes / _calculate_bytes_per_unit(unit), 1)
    return result

def _configure_logging():
    """
    Loads logging configuration from configuration file.
    Creates log file/directory if it doesn't exist.
    """
    if not os.path.exists('log'):
        os.makedirs('log')
    with open(LOG_CONF_FILE, 'r') as conf_file:
        log_cfg = yaml.safe_load(conf_file.read())
    filename = log_cfg['handlers']['default_file_handler']['filename']
    log_cfg['handlers']['default_file_handler']['filename'] = LOG_DIR + filename
    try:
        logging.config.dictConfig(log_cfg)
    except ValueError as e:
        try:
            if 'Errno 2' in str(e):
                try:
                    os.mkdir(HFC_DOCS_DIR)
                except FileExistsError:
                    print(f"{HFC_DOCS_DIR} already exists")
                try:
                    os.mkdir(LOG_DIR)
                    print(f"Created {LOG_DIR}")
                except FileExistsError:
                    print(f"{LOG_DIR} already exists")
                f = open(filename, "x")
                logging.config.dictConfig(log_cfg)
            else:
                raise e
        except ValueError as e:
            print("Unable to load log configuration\n==> " + str(e))
            sys.exit(1)

def _calculate_bytes_per_unit(unit):
    """
    Returns the number of bytes in the specified unit.
    Parameters:
        - unit: a string representation of a unit ('KB', 'MB', 'GB', etc.)
    """
    bytes_per_unit = 1
    if unit == 'KB':
        bytes_per_unit = 1024
    elif unit == 'MB':
        bytes_per_unit = 1024 ** 2
    elif unit == 'GB':
        bytes_per_unit = 1024 ** 2
    elif unit == 'TB':
        bytes_per_unit = 1024 ** 3
    return bytes_per_unit

def _delete_log_files():
    """
    Deletes all log files from the log directory.
    """
    for root, dirs, files in os.walk(LOG_DIR):
        for fname in files:
            if fname.endswith('.log') or fname.endswith('.png'):
                full_fname = os.path.join(root, fname)
                os.remove(full_fname)

