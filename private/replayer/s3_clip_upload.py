from clip_upload_service import ClipUploadService
from database.clip_store_service import ClipStoreService
from s3_upload import S3Upload
from clip import Clip



from datetime import timedelta
from time import sleep
from pathlib import PurePath
from os import path
from shutil import rmtree

class S3ClipUpload(ClipUploadService):
    _RESOLUTION_HEIGHTS = [480, 720, 1080]

    def __init__(self, store_service: ClipStoreService):
        self._upload_service = S3Upload()
        self._store_service = store_service

    def upload(self, clip: Clip):
        video = clip.video
        for required_height in self._RESOLUTION_HEIGHTS:
            resolution_video_name = '{}_{}_{}_{}p.mp4'.format(
                clip.event.platform_id,
                clip.event.game_id,
                clip.ingame_clip_num,
                required_height
            )
            if required_height == video.resolution_height:
                clip_res_path = video.path
            else:
                clip_res_path = path.join(path.dirname(video.path),
                    resolution_video_name)
                video.resize(required_height, clip_res_path)
            if required_height is self._RESOLUTION_HEIGHTS[-1]:
                clip.clip_uri = ('https://s3.amazonaws.com/lolvvvclips/'
                    + resolution_video_name)
                callback_func = self._upload_finished
                callback_arg = clip
            else:
                callback_func = None
                callback_arg = None
            self._upload_service.upload(
                clip_res_path
                , resolution_video_name
                , callback_func
                , callback_arg
            )

    def _upload_finished(self, clip: Clip):
        self._store_service.store(clip)
        rmtree(path.dirname(clip.clip_path))
        # ToDo: remove game_id dir if empty