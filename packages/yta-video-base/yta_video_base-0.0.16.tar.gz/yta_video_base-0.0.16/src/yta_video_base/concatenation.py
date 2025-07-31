"""
Module dedicated to concatenation of
videos.
"""
from yta_video_moviepy.utils import wrap_video_with_transparent_background
from yta_validation import PythonValidator
from moviepy import VideoClip, concatenate_videoclips as concatenate_videoclips_moviepy
from typing import Union


@staticmethod
def concatenate_videos(
    videos: Union[VideoClip, list[VideoClip]]
):
    """
    Concatenate the provided 'videos' but fixing the
    videos dimensions. It will wrap any video that
    doesn't fit the 1920x1080 scene size with a full
    transparent background to fit those dimensions.
    """
    videos = (
        [videos]
        if not PythonValidator.is_list(videos) else
        videos
    )

    videos = [
        wrap_video_with_transparent_background(video) 
        for video in videos
    ]
    
    return concatenate_videoclips_moviepy(videos)