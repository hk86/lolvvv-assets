from json import load as json_load
from os import path

from tinys3 import Pool #pip install tinys3

from Interval import Interval

class S3UploadNode:
    request = None
    callback_func = None
    callback_arg = None

class S3Upload:
    def __init__(self):
        access_data = json_load(open(r'../json/s3_access.json'))
        S3_ACCESS_KEY = access_data['s3_access_key']
        S3_SECRET_KEY = access_data['s3_secret_key']
        self._connection = Pool(S3_ACCESS_KEY
                                      ,S3_SECRET_KEY
                                      ,tls=True
                                      ,default_bucket='lolvvvclips')
        self._upload_nodes = []
        self._interval = Interval(60, self._cleanup_requests)
        self._interval.start()
    
    def upload(self
                , src_file_path
                , dst_bucket_path
                , callback_func
                , callback_arg):
        if dst_bucket_path == None:
            dst_bucket_path = path.basename(src_file_path)
        file = open(src_file_path, 'rb')
        node = S3UploadNode()
        node.request = self._connection.upload(
                dst_bucket_path
                ,file
                ,public=True
            )
        node.callback_func = callback_func
        node.callback_arg = callback_arg
        self._upload_nodes.append(node)

    def _cleanup_requests(self):
        for idx, node in enumerate(self._upload_nodes):
            if node.request.done():
                if node.callback_func:
                    node.callback_func(node.callback_arg)
                self._upload_nodes.pop(idx)
