#!/usr/bin/env python
### Non-google customizations
import json
import logging
import sys
import argparse
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client import tools
from oauth2client.tools import run_flow, argparser
from oauth2client.client import OAuth2WebServerFlow

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

OAUTH2_STORAGE = 'oauth2.dat'
OAUTH2_CLIENT_ID = INSERT_CLIENT_ID_HERE
OAUTH2_CLIENT_SECRET = INSERT_CLLIENT_SECRET_HERE


class GoogleDriveHandler:
	def __init__(self, argv):
		""" A constructor which creates a google drive instance. This involves two steps. The first is authorizing access using the oauth 2.0 protocol. The second is to actually build the drive."""
		print 'begin authorization stuff\n'
		self.drive_service = self.build_drive_service()
		self.drive_file_list = self.drive_service.files().list(q='trashed=false').execute()["items"]
		print 'Contents of your drive are: ' + str(self.drive_file_list)

	def get_list_of_drives_files(self):
		return self.drive_file_list

	def build_drive_service(self):
		print 'begin authentication\n'
		flow = OAuth2WebServerFlow(client_id=OAUTH2_CLIENT_ID, client_secret=OAUTH2_CLIENT_SECRET,
scope='https://www.googleapis.com/auth/drive', user_agent='MyApplication/0.1')
		
		print 'flow completed\n'
		storage = Storage(OAUTH2_STORAGE)
		credentials = storage.get()
		print 'credentials parsing\n'

		import os
		print 'Current directory path: ' + os.getcwd()

		if credentials is None or credentials.invalid:
		    parser = argparse.ArgumentParser(parents=[argparser])
		    flags = parser.parse_args()
		    print 'try running the flow\n'
		    credentials = run_flow(flow, storage, flags)
		    print 'flow can run\n'
		print 'Drive object will be built\n'
		http = httplib2.Http(disable_ssl_certificate_validation=True)
		print 'http stuff done\n'
		http = credentials.authorize(http)
		print 'credentials are authorized with \n' + str(http.__dict__)

		service = build(serviceName='drive', version='v2', http=http)
		return service

	def get_drive(self):
		return self.drive_service

