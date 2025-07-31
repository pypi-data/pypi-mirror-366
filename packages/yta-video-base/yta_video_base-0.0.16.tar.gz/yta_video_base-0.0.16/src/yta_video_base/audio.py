from yta_video_base.parser import VideoParser
from yta_file.handler import FileHandler
from yta_programming.output import Output
from yta_programming.decorators.requires_dependency import requires_dependency
from yta_constants.file import FileExtension
from moviepy import AudioClip
from moviepy.Clip import Clip
from typing import Union

# TODO: Why 'ffmpeg' here (?)
import ffmpeg


@requires_dependency('yta_audio_base', 'yta_video_base', 'yta_audio_base')
def set_audio_in_video(
    video: Union[Clip, str],
    audio: Union[AudioClip, str]
):
    """
    This method returns a VideoFileClip that
    is the provided 'video_input' with the
    also provided 'audio_input' as the unique 
    audio (if valid parameters are provided).
    """
    from yta_audio_base.parser import AudioParser

    video = VideoParser.to_moviepy(video)
    audio = AudioParser.to_audioclip(audio)

    return video.with_audio(audio)

def set_audio_in_video_ffmpeg(
    video_filename: str,
    audio_filename: str,
    output_filename: Union[str, None] = None
):
    """
    Sets the provided 'audio_filename' in the also provided 'video_filename'
    with the ffmpeg library and creates a new video 'output_filename' that
    is that video with the provided audio.

    TODO: This method need more checkings about extensions, durations, etc.
    """
    if (
        not audio_filename or
        not FileHandler.is_audio_file(audio_filename) or
        not video_filename or
        not FileHandler.is_video_file(video_filename)
    ):
        raise Exception('The provided "audio_filename" and/or "video_filename" are not valid filenames.')
    
    output_filename = Output.get_filename(output_filename, FileExtension.MP4)
    
    # TODO: What about longer audio than video (?)
    # TODO: Refactor this below with the FfmpegHandler
    input_video = ffmpeg.input(video_filename)
    input_audio = ffmpeg.input(audio_filename)

    ffmpeg.concat(input_video, input_audio, v = 1, a = 1).output(output_filename).run(overwrite_output = True)