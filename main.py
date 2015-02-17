import kivy
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.app import App


import sys
sys.path.append('GoogleNetworking')
from googleapiclient.http import MediaFileUpload
from googleapiclient import errors

import logging

import os

Builder.load_string('''
<MakeFolderScreen>:
	orientation: "vertical"
	cols: 1
	Button: 
		text: 'Authenticate'
		font_size: 50
		on_press: root.authenticate()
	Button: 
		text: 'Upload'
		font_size: 50
		on_press: root.upload('Test_File.txt')
	Button:
		text: 'Download and display'
		font_size: 50
		on_press: root.download('Test_File.txt')
''')

# Some util functions to parse the content in google drive:

def get_file_download_url(file_name, drive_service_object):
	files = drive_service_object.files().list(q="trashed=false").execute()
	file_id = None
	for file_temp in files["items"]:
		if file_temp["title"]==file_name:
			file_id = file_temp["downloadUrl"]
			#file_id = drive_service_object.files().get(fileId=file_id, fields='downloadUrl').execute()
	if file_id is None:
		print "The folder "+file_name+" needs to be created."
	return file_id			

class MakeFolderScreen(GridLayout):
    def authenticate(self):
	from google_drive_handler import GoogleDriveHandler
	print 'current working directory: ' + os.getcwd() 
	self.drive_handler = GoogleDriveHandler(sys.argv)
	print 'authentication successful and drive object is created. \n'
	
    def upload(self, FILENAME):
	print 'Try to upload\n'
	media_body = MediaFileUpload(FILENAME, mimetype='text/plain', resumable=True)
	body = {'title': FILENAME, 'description': 'A test document', 'mimeType': 'text/plain'}
	try:
		self.new_file = self.drive_handler.drive_service.files().insert(body=body, media_body=media_body).execute()
		import pprint
		pprint.pprint(self.new_file)
	except errors.HttpError, error:
		print 'An error has occured: %s' % error

    def download(self, FILENAME):
	# Verify the file is absent locally by removing the local copy
        print 'download the file'
	import os
	os.remove(FILENAME)
	print 'local files are: ' + str(os.listdir(os.curdir))
	download_url = get_file_download_url(FILENAME, self.drive_handler.drive_service)
	print 'download_url is ' + str(download_url)
	if download_url is not None:
		# request the download URL 
		resp, content = self.drive_handler.drive_service._http.request(download_url)
		if resp.status == 200:
			print "Response status: %s" % resp
			f = open(FILENAME,"wb") 
			f.write(content)
			f.close()
			print 'local files are: ' +  str(os.listdir(os.curdir))

			# Display the modified content in a popup:
			f = open(FILENAME,"rb")
			s = f.read()
			popup = Popup(title='Content of file from google drive', content=Label(text=str(s),font_size=50), size_hint=(None, None), size=(500, 500))
			popup.open()
		else:
			print "An error occurred: %s" % resp
			return None
	else:
		print 'The file does not exist in your drive\n'
		popup = Popup(title='FILE NOT AVAILABLE', content=Label(text='File does not exist\n in your google drive',font_size=50), size_hint=(None, None), size=(500, 500))
		popup.open()

class DriveTest(App):
	def build(self):
		return MakeFolderScreen()

	def on_pause(self):
		# Save data?
		return True

	def on_resume(self):
		# Here you can check if any data needs replacing (usually nothing)
		return True

if __name__ == '__main__':
    DriveTest().run()

