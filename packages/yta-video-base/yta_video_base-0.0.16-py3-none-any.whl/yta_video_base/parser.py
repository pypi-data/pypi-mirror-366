from yta_file.handler import FileHandler
from yta_validation import PythonValidator
from yta_validation.parameter import ParameterValidator
from moviepy import VideoFileClip, VideoClip
from typing import Union


class VideoParser:
    """
    Class to simplify the way we parse video
    parameters.
    """

    @staticmethod
    def to_moviepy(
        video: Union[str, VideoClip],
        do_include_mask: bool = False
    ) -> VideoClip:
        """
        Parse the provided 'video' and transform
        into a moviepy video instance, including
        the video mask if 'do_include_mask' is
        True.
        """
        ParameterValidator.validate_mandatory_instance_of('video', video, [str, 'VideoClip', 'VideoFileClip'])
        ParameterValidator.validate_mandatory_bool('do_include_mask', do_include_mask)
        
        if PythonValidator.is_string(video):
            if not FileHandler.is_video_file(video):
                # By now I validate by extension
                raise Exception('The "video" parameter provided is not a valid video filename.')
            
            video = VideoFileClip(video, has_mask = do_include_mask)

            # TODO: This below just adds a mask attribute but
            # without fps and empty, so it doesn't make sense
            # if do_include_mask and not video.mask:
            #     video = video.add_mask()

        return video
        
    """
    TODO: This method below is causing a cyclic import
    because I'm using it in the Video class '__init__'
    method...
    """
    # @staticmethod
    # def to_video(
    #     video: Union[str, VideoClip],
    #     is_mask: bool = False,
    #     do_include_mask: bool = False,
    #     do_calculate_real_duration: bool = False
    # ) -> Video:
    #     """
    #     Parse the provided 'video' and transform
    #     into a Video instance, including the
    #     video mask if 'do_include_mask' is True,
    #     and recalculating the real video duration
    #     (slow process, because of a bug) if the
    #     'do_calculate_real_duration' is True.

    #     TODO: Is the bug still present? Doing the
    #     check costs a lot of time and should be
    #     avoided if possible.
    #     """
    #     ParameterValidator.validate_mandatory_instance_of('video', video, [str, 'VideoClip', 'VideoFileClip'])
    #     ParameterValidator.validate_mandatory_bool('is_mask', is_mask)
    #     ParameterValidator.validate_mandatory_bool('do_include_mask', do_include_mask)
    #     ParameterValidator.validate_mandatory_bool('do_calculate_real_duration', do_calculate_real_duration)

    #     from yta_video_base.video import Video
    
    #     return Video(
    #         video = VideoParser.to_moviepy(
    #             video = video,
    #             do_include_mask = do_include_mask
    #         ),
    #         is_mask = is_mask,
    #         do_include_mask = do_include_mask,
    #         do_force_60_fps = True,
    #         # Due to problems with decimal values I'm forcing
    #         # to obtain the real duration again, making the
    #         # system slower but avoiding fatal errors
    #         # TODO: I hope one day I don't need this below
    #         do_fix_duration = do_calculate_real_duration
    #     )