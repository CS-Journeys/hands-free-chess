from src.ftp_manager import FTPManager
import os
import logging
import logging.config
import yaml
import ftplib
import sys
from threading import Thread

LOG_CONF_FILE = 'config/log_config.yaml'
MAX_LOG_SIZE = 50 # MB


class LogManager:
    def __init__(self):
        # Global logging setup
        _delete_giant_text_log_files()
        _configure_logging()

        # LogManager logging setup
        self.log = logging.getLogger(__name__)

        # Upload and delete log files when log/ gets too big
        self.log_uploader = FTPManager()
        if self._get_directory_size('log', 'MB') > MAX_LOG_SIZE:
            thread = Thread(target=self._upload_logs, daemon=True)
            thread.start()

    def _upload_logs(self):
        success = False
        try:
            self.log_uploader.start_session()
            self.log.info('Uploading logs...')
            for root, dirs, files in os.walk('log/'):
                for fname in files:
                    self.log_uploader.upload_file(fname, root)
            self.log.info('Logs successfully uploaded')
            self.log_uploader.quit_session()
            success = True
        except ftplib.error_perm:
            self.log.error('Unable to upload logs. FTP permission error. ', exc_info=True)
        except:
            self.log.error('Unable to upload logs. ', exc_info=True)

        if success:
            self._delete_img_logs()

    def _delete_img_logs(self):
        for root, dirs, files in os.walk('log/'):
            for fname in files:
                if fname.endswith('.png'):
                    full_fname = os.path.join(root, fname)
                    os.remove(full_fname)
        self.log.info('PNG logs deleted')

    def _get_directory_size(self, directory, unit):
        total_bytes = 0
        for path, dirs, files in os.walk(directory):
            for f in files:
                fp = os.path.join(path, f)
                total_bytes += os.path.getsize(fp)
        result = round(total_bytes / _calculate_bytes_per_unit(unit), 1)
        self.log.debug(str(result) + unit + " in log/")
        return result


def _configure_logging():
    # Load logging configuration from file
    if not os.path.exists('log'):
        os.makedirs('log')
    with open(LOG_CONF_FILE, 'r') as conf_file:
        log_cfg = yaml.safe_load(conf_file.read())
    try:
        logging.config.dictConfig(log_cfg)
    except ValueError as e:
        print("Unable to load log configuration\n==> " + str(e))
        sys.exit(1)

def _calculate_bytes_per_unit(unit):
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

def _get_file_size(full_fname, unit):
    size_in_bytes = os.path.getsize(full_fname)
    result = round(size_in_bytes / _calculate_bytes_per_unit(unit), 1)
    return result

def _delete_giant_text_log_files():
    for root, dirs, files in os.walk('log/'):
        for fname in files:
            if fname.endswith('.log'):
                full_fname = os.path.join(root, fname)
                if _get_file_size(full_fname, 'MB') > 3 * MAX_LOG_SIZE:
                    os.remove(full_fname)
