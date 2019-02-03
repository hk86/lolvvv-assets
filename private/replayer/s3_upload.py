from json import load as json_load
from os import path

from tinys3 import Pool  # pip install tinys3

from Interval import Interval


class S3UploadNode:
    request = None
    callback_func = None
    callback_arg = None


class S3Upload:
    def __init__(self):
        access_data = json_load(open(r'../json/s3_access.json'))
        self._connection = Pool(access_data['s3_access_key']
                                , access_data['s3_secret_key']
                                , tls=True
                                , default_bucket='lolvvvclips'
                                , size=21)
        self._upload_nodes = []
        self._interval = Interval(60, self._cleanup_requests)
        self._interval.start()

    def upload(self
               , src_file_path
               , dst_bucket_path
               , callback_func
               , callback_arg):
        if dst_bucket_path is None:
            dst_bucket_path = path.basename(src_file_path)
        file = open(src_file_path, 'rb')
        node = S3UploadNode()
        node.request = self._connection.upload(
            dst_bucket_path
            , file
            , public=True
        )
        node.callback_func = callback_func
        node.callback_arg = callback_arg
        self._upload_nodes.append(node)

    def _cleanup_requests(self):
        for idx, node in enumerate(self._upload_nodes):
            if node.request.done():
                print('s3 cleanup state: {}'.format(node.request.result()))
                callback = node.callback_func
                callback_arg = node.callback_arg
                # delete request to close file handle
                del node.request
                self._upload_nodes.pop(idx)
                if callback:
                    callback(callback_arg)

    def __del__(self):
        self._interval.stop()
