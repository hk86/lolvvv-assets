from clip_upload_service import ClipUploadService
from database.clip_store_service import ClipStoreService
from s3_upload import S3Upload
from clip import Clip

# pip install ez_setup (optional)
# pip install moviepy
from moviepy import editor as mp

from datetime import timedelta
from time import sleep
from pathlib import PurePath
from os import path
from shutil import rmtree

class S3ClipUpload(ClipUploadService):
    _RESOLUTION_HEIGHTS = [720, 480]

    def __init__(self, store_service: ClipStoreService):
        self._upload_service = S3Upload()
        self._store_service = store_service

    def upload(self, clip: Clip):
        clip_video_path = PurePath(clip.clip_path)
        MAX_TRIES = 3
        for tries in range(MAX_TRIES):
            try:
                clip_video = mp.VideoFileClip(clip.clip_path)
                break
            except OSError:
                print('couldn\'t access file {}'.format(clip.clip_path))
                if tries == MAX_TRIES-1:
                    raise
            sleep(1)
        clip.length = timedelta(seconds=clip_video.duration)
        for new_height in self._RESOLUTION_HEIGHTS:
            resized_video_name = '{}_{}_{}_{}p.mp4'.format(
                clip.event.platform_id,
                clip.event.game_id,
                clip.ingame_clip_num,
                new_height
            )
            resized_video_path = path.join(
                *clip_video_path.parts[:-1],
                resized_video_name
            )
            for tries in range(MAX_TRIES):
                try:
                    resized_video = clip_video.resize(height=new_height)
                    resized_video.write_videofile(resized_video_path)
                    break
                except OSError:
                    if tries == MAX_TRIES-1:
                        raise
                sleep(1)
            self._upload_service.upload(
                resized_video_path,
                None,
                None,
                None
            )
        clip_s3_name = '{}_{}_{}_1080p.mp4'.format(
                clip.event.platform_id
                , clip.event.game_id
                , clip.ingame_clip_num
                )
        clip.clip_uri = ('https://s3.amazonaws.com/lolvvvclips/'
            + clip_s3_name
        )
        self._upload_service.upload(
            clip.clip_path
            , clip_s3_name
            , self._upload_finished
            , clip
        )

    def _upload_finished(self, clip: Clip):
        self._store_service.store(clip)
        rmtree(path.dirname(clip.clip_path))
        # ToDo: remove game_id dir if empty