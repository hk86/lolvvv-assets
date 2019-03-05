from os import path

from clip import Clip
from clip_upload_service import ClipUploadService
from s3_upload import S3Upload


class S3ClipUpload(ClipUploadService):
    _RESOLUTION_HEIGHTS = [480, 720, 1080]

    def __init__(self):
        self._upload_service = S3Upload()

    def upload(self, clip: Clip, callback_func):
        video = clip.video
        for required_height in self._RESOLUTION_HEIGHTS:
            resolution_video_name = '{}_{}p.mp4'.format(
                clip.id,
                required_height
            )
            if required_height == video.resolution_height:
                clip_res_path = video.path
            else:
                clip_res_path = path.join(path.dirname(video.path),
                                          resolution_video_name)
                video.resize(required_height, clip_res_path)
            if required_height is self._RESOLUTION_HEIGHTS[-1]:
                clip.clip_uri = ('https://d1jo2ofi91zpb5.cloudfront.net/'
                                 + resolution_video_name)
                callback = callback_func
                callback_arg = clip
            else:
                callback = None
                callback_arg = None
            self._upload_service.upload(
                clip_res_path
                , resolution_video_name
                , callback
                , callback_arg
            )
