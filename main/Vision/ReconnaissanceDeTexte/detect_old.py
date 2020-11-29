from __future__ import print_function

from argparse import Namespace

import httplib2
import io, os
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
from D4 import settings

# try:
#     import argparse
#     flags =  argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
#
# except ImportError:
#     flags = None
# print("FALGS =", flags)
# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credential_path = os.path.join("./", 'drive-python-quickstart.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(settings.CLIENT_SECRET_FILE, settings.SCOPES)
        flow.user_agent = settings.APPLICATION_NAME
        client.fr
        # if flags:
            # credentials = tools.run_flow(flow, store, flags)
        credentials = tools.run_flow(flow, store, flags=Namespace(auth_host_name='127.0.0.1', auth_host_port=[8080, 8090], logging_level='ERROR', noauth_local_webserver=False))
        # else:  # Needed only for compatibility with Python 2.6
        #     credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def process(img_address=None):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    # imgfile = '../../../media/images/produit02.jpg'  # Image with texts (png, jpg, bmp, gif, pdf)
    txtfile = 'output.txt'  # Text file outputted by OCR

    mime = 'application/vnd.google-apps.document'
    res = service.files().create(
        body={
            'name': img_address,
            'mimeType': mime
        },
        media_body=MediaFileUpload(img_address, mimetype=mime, resumable=True)
    ).execute()

    downloader = MediaIoBaseDownload(
        io.FileIO(txtfile, 'wb'),
        service.files().export_media(fileId=res['id'], mimeType="text/pla"
                                                                "in")
    )
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    service.files().delete(fileId=res['id']).execute()
    print("Done.")