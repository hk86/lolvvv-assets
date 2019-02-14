# pip install ez_setup (optional)
# pip install moviepy
from moviepy.editor import VideoFileClip

from time import sleep
from datetime import timedelta


class Video:

    def __init__(self, video_path: str):
        self._path = video_path

    def resize(self, resolution_h: int, resized_vid_path: str):
        src_video = self._open_video()
        dst_video = src_video.resize(height=resolution_h)
        new_width = dst_video.w
        if new_width % 2 != 0:
            new_width -= 1
            dst_video = src_video.resize((new_width, resolution_h))
        dst_video.write_videofile(resized_vid_path,
                                  audio_codec='aac', codec='libx264',
                                  ffmpeg_params=['-pix_fmt', 'yuv420p'])
        self._close_video(src_video)

    @property
    def path(self):
        return self._path

    @property
    def duration(self):
        vid = self._open_video()
        duration = vid.duration
        self._close_video(vid)
        return timedelta(seconds=duration)

    @property
    def resolution_height(self):
        vid = self._open_video()
        height = vid.h
        self._close_video(vid)
        return height

    def _open_video(self):
        max_tries = 5
        for tries in range(max_tries):
            try:
                clip_video = VideoFileClip(self._path)
                break
            except (OSError, KeyError):
                if tries == max_tries - 1:
                    print('couldn\'t access file {}'.format(self._path))
                    raise
            sleep(2)
        return clip_video

    @staticmethod
    def _close_video(video):
        video.reader.close()
        video.audio.reader.close_proc()
        video.close()
        del video
