from django.conf import settings
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.auth import ServiceAccountCredentials

class DriveStorage:

    def __init__(self):
        gauth = GoogleAuth()
        scope = ['https://www.googleapis.com/auth/drive']
        gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(settings.CLIENT_SECRET_FILE_SERVICEACCOUNT, scope)
        self.drive = GoogleDrive(gauth)

    def list_files(self):
        file_list = self.drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        for file1 in file_list:
            print(file1)

    def delete_file(self, file_url, folder='root'):
        file_list = self.drive.ListFile({'q': "'{}' in parents and trashed=false".format(folder)}).GetList()
        for file1 in file_list:
            try:
                if file1['webContentLink'] == file_url:
                    file1.Delete()
            except KeyError:
                pass

    def upload_file(self, file_content):

        uploaded_file = self.drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": "root"}]})
        uploaded_file.content = file_content
        uploaded_file['mimeType'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        uploaded_file['title'] = "name" #file_content.name
        uploaded_file.Upload(param={'convert': True})
        uploaded_file.InsertPermission({
            'type': 'anyone',
            'value': 'anyone',
            'role': 'reader'})
        # return uploaded_file['webContentLink']
        # return uploaded_file['exportLinks']['application/rtf']
        return uploaded_file['exportLinks']['text/plain']






