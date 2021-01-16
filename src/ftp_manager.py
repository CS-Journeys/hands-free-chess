from os import path
import shutil
import yaml
import ftplib
import random
import re
import time
import logging
import tkinter as tk
from tkinter import simpledialog

simple_gui = tk.Tk()
simple_gui.withdraw()
simple_gui.geometry("500x500")

BASE_CONF_FILE = 'config/base_ftp_config.yaml'
FTP_CONF_FILE = 'config/user_ftp_config.yaml'
random.seed(time.time())

class FTPManager:
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.cfg = None
        self.session = None
        self.load_config()

        self.hostname = self.cfg['host']['hostname']
        self.global_upload_path = self.cfg['host']['upload_path']
        self.credentials = self.cfg['host']['key'].split(':')
        self.user_name = self.cfg['user']['name']
        self.user_id = self.cfg['user']['id']

        if self.user_name == 'None':
            self.init_user()

    def init_user(self):
        # Set user's name and ID
        user_input = simpledialog.askstring(title=" ",
                                            prompt="Welcome to Hands-Free Chess!\n"
                                                   "Thank you for participating in the beta-testing.\n\n"
                                                   "For logging purposes, please enter your name: ")
        if user_input is None:
            return

        self.log.debug('user input: ' + user_input)
        self.set_user_name(re.sub('[^a-zA-Z]+', '_', user_input))
        self.set_user_id(random.randint(100000, 999999))
        self.update_config_file()

        # Create a folder on the TCP server for the new user
        try:
            self.start_session()
            ftp_response = self.session.cwd(self.global_upload_path)
            self.log.debug(ftp_response)
            ftp_response = self.session.mkd(self.get_user_directory_name())
            self.log.debug(ftp_response)
            self.log.info("Remote user directory created")
            self.quit_session()
        except:
            self.log.error('Unable to create the directory ' + self.get_user_directory_name(), exc_info=True)

    def set_user_id(self, user_id):
        self.user_id = user_id
        self.cfg['user']['id'] = user_id

    def set_user_name(self, user_name):
        self.user_name = user_name
        self.cfg['user']['name'] = user_name

    def get_user_upload_path(self):
        return self.global_upload_path + self.get_user_directory_name() + '/'

    def get_user_directory_name(self):
        return self.user_name + '-' + str(self.user_id)

    def start_session(self):
        self.session = ftplib.FTP(self.hostname)
        ftp_response = self.session.login(self.credentials[0], self.credentials[1])
        self.log.info('FTP session started')
        self.log.debug(ftp_response)

    def upload_file(self, filename, local_path):
        # Error checking
        if self.user_id == "None":
            raise ValueError('User ID not set. Check ftp_config.yaml')
        if self.user_name == "None":
            raise ValueError('User name not set. Check ftp_config.yaml')
        if self.session is None:
            raise ValueError('FTP session not yet started. Run start_session() first.')

        # Set local and remote filename (including path)
        local_filename = local_path + filename
        remote_filename = self.get_user_upload_path() + filename
        if remote_filename[-4:] == '.log':
            remote_filename = remote_filename[:-4] + time.strftime('_%Y-%m-%d_%H.%M.%S.log', time.localtime())

        # Actually upload the file
        self.session.storbinary('STOR ' + remote_filename, open(local_filename, 'rb'))
        self.log.debug(local_filename + ' uploaded to ' + remote_filename)

    def quit_session(self):
        self.session.quit()
        self.session = None
        self.log.info('FTP session closed')

    def load_config(self):
        if not path.exists(FTP_CONF_FILE):
            self.log.warning("Could not find user's ftp config file. Generating a new config.")
            shutil.copy(BASE_CONF_FILE, FTP_CONF_FILE)
        with open(FTP_CONF_FILE, 'r') as conf_file:
            self.cfg = yaml.safe_load(conf_file.read())

    def update_config_file(self):
        with open(FTP_CONF_FILE, 'w') as conf_file:
            yaml.dump(self.cfg, conf_file)
