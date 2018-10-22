from json import load as json_load
from os import path

from tinys3 import Connection

class S3Upload:
    def __init__(self):
        access_data = json_load(open(r'../json/s3_access.json'))
        S3_ACCESS_KEY = access_data['s3_access_key']
        S3_SECRET_KEY = access_data['s3_secret_key']
        self._connection = Connection(S3_ACCESS_KEY
                                      ,S3_SECRET_KEY
                                      ,tls=True
                                      ,default_bucket='lolvvvclips')
    
    def upload(self, file_path):
        file = open(file_path, 'rb')
        filename = path.basename(file_path)
        self._connection.upload(
                            filename
                            ,file
                            ,public=True
                            )
