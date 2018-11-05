from clip_upload_service import ClipUploadService
from s3_upload import S3Upload

from clip import Clip

class S3ClipUpload(ClipUploadService):
    def __init__(self, meteor_db):
        self._upload_service = S3Upload()
        self._meteor_db = meteor_db

    def upload(self, clip: Clip):
        clip_s3_name = '{}_{}_{}_1080p.mp4'.format(
                clip.platform_id
                , clip.game_id
                , clip.ingame_clip_number)
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
        self._meteor_db.store_clip(clip)