"""
A video has only one frame per each 't' time
moment provided, but if that video has an
audio associated, and considering that the
video 'fps' and the audio 'fps' are different,
we need to consider something. Both, video and
audio will have only one frame per a single
and specific 't' time moment. But, when we 
consider both, video clip and audio clip, as
attached clips, we need to know that when one
video frame is being shown, a lot of different
audio frames will be played in the background
and not only one.

If the video has fps=30 but the audio has 
fps=44_100, the video will have 1 frame from
frame 0 (0/30 = 0.0s) to frame 1
(1/30 = 0.033s). The audio will have also 1
frame from frame 0 (0/44_100 = 0.0s) to
frame 1 (1/44_100 = 0.00000227s). But the 
audio frame 2 (2/44_100 = 0.00000454s) is also
in the video frame 1 time lapse, so it must be
attached to that video frame. And also the
audio frame 1000 (1000/44_100 = 0.0227s) is
inside that timelapse. And, if you use the 
numbers, 44_100 / 30 = 1470, which means that
each video frame has 1470 audio frames
associated for the same video 't' time moment.
Thats why the audio frame that acts, the audio
frame 1470 (1_470/44_100 = 0.033s) has the 
same result as the first video frame.
"""
from yta_video_base.parser import VideoParser
from yta_video_base.video.setting import VideoSetting
from yta_video_base.video.attribute_modifier import VideoAttributeModifier
from yta_video_base.video.validation import _validate_attribute_modifier, _validate_is_video_attribute_modifier_instance, _validate_zoom, _validate_x_movement, _validate_y_movement, _validate_rotation
from yta_video_moviepy.utils import wrap_video_with_transparent_background, calculate_real_video_duration
from yta_video_moviepy.frame.extractor import MoviepyVideoFrameExtractor
from yta_video_moviepy.t import T, get_frame_duration, get_number_of_frames
from yta_video_moviepy.frame import MoviepyVideoFrame
from yta_programming.decorators.requires_dependency import requires_dependency
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from yta_constants.video import COLOR_TEMPERATURE_LIMIT, BRIGHTNESS_LIMIT, CONTRAST_LIMIT, SHARPNESS_LIMIT, WHITE_BALANCE_LIMIT, SPEED_FACTOR_LIMIT, VOLUME_LIMIT
from yta_constants.multimedia import DEFAULT_SCENE_SIZE
from yta_general_utils.math.rate_functions.rate_function_argument import RateFunctionArgument
from moviepy.Clip import Clip
from moviepy import VideoClip, AudioClip
from typing import Union

import numpy as np


# TODO: Move this decorator below to another place (?)
def unset_video_processed(
    func
):
    """
    Decorator function that sets the '_video_processed'
    attribute to None to indicate that it has been
    modified and it must be processed again.
    """
    def wrapper(
        self,
        value
    ):
        value = func(self, value)
        self._video_processed = None
        
        return value
    
    return wrapper

"""
The effects have to be applied first, and once
the values have been calculated, we need to
check the rotation, zoom, x_movement, etc. and
apply the difference to those values that have
been calculated when the effects were applied.
"""

class Video:
    """
    The base class of our video management
    system.
    
    Class to wrap a moviepy video, simplify
    the way we work with them and also fix
    some issues with bugs.

    This class has a lot of properties to 
    simplify the way we access to the 
    information, but nothing to change the
    instance or modify properties.
    """

    @property
    def video_processed(
        self
    ) -> VideoClip:
        """
        The video once it's been processed with all the
        attributes that are set in this instance.
        """
        self._video_processed = (
            self._process()
            if not hasattr(self, '_video_processed') else
            self._video_processed
        )

        return self._video_processed

    @property
    def duration(
        self
    ) -> float:
        """
        Real duration of the video, that has been
        checked according to the available frames.
        """
        return self.video.duration
    
    @property
    def fps(
        self
    ) -> float:
        """
        Frames per second of the original video.
        """
        return self.video.fps
    
    @property
    def audio_fps(
        self
    ) -> Union[float, None]:
        """
        Frames per second of the audio clip attached
        to this video clip, that can be None if no
        audio attached.
        """
        return (
            None
            if not self.has_audio else
            self.audio.fps
        )

    @property
    def original_size(
        self
    ):
        """
        The size of the original video clip.
        """
        return self.video.size

    @property
    def original_width(
        self
    ):
        """
        The width of the original video clip.
        """
        return self.original_size[0]
    
    @property
    def original_height(
        self
    ):
        """
        The height of the original video clip.
        """
        return self.original_size[1]
    
    @property
    def number_of_frames(
        self
    ) -> int:
        """
        Number of frames of the moviepy
        video.
        """
        return get_number_of_frames(self.duration, self.fps)
    
    @property
    def frame_duration(
        self
    ) -> float:
        """
        Frame duration, based on the video
        frames per second (fps).
        """
        return get_frame_duration(self.fps)

    @property
    def audio_frame_duration(
        self
    ) -> Union[float, None]:
        """
        Frame duration of the audio clip attached
        to this video clip, if attached, or None
        if not.
        """
        return (
            None
            if not self.has_audio else
            1 / self.audio_fps
        )
    
    @property
    def audio(
        self
    ) -> Union[AudioClip, None]:
        """
        Get the audio of the video, if an AudioClip is
        attached, or None if not.
        """
        return self.video.audio
    
    @property
    def has_audio(
        self
    ) -> bool:
        """
        Indicate if the video has an audio clip attached
        or not.
        """
        return self.audio is not None
    
    @property
    def without_audio(
        self
    ) -> 'Clip':
        """
        Get the video clip but without any audio clip 
        attached to it.
        
        This method doesn't affect to the original
        video, it is just a copy.
        """
        return self.video.without_audio()

    # TODO: Should I keep this here? I think this is
    # an additional functionality that is not about
    # wrapping the class but adding functionality, and
    # that must be done in another library related
    # to video editing
    # @property
    # def with_audio(
    #     self
    # ) -> 'Clip':
    #     """
    #     Get the video clip with an audio clip attached
    #     to it. If there is not an audio clip attached,
    #     a new silent audio clip will be created and
    #     attached to it.

    #     This method doesn't affect to the original
    #     video, it is just a copy.
    #     """
    #     # TODO: Create a silent audio clip with the
    #     # same duration and return a copy with it
    #     # attached to
    #     return self.video.copy()

    @property
    def mask(
        self
    ) -> Union['Clip', None]:
        """
        Get the mask video clip attached to this video,
        if existing, or None if not.
        """
        return self.video.mask
    
    @property
    def is_mask(
        self
    ) -> bool:
        """
        Indicate if the video is set as a mask video. A
        video that is a mask cannot has another video
        attached as a mask.
        """
        return self.video.is_mask

    @property
    def has_mask(
        self
    ) -> bool:
        """
        Indicate if the video has another video attached
        as a mask.
        """
        return self.mask is not None
    
    @property
    def has_transparent_mask(
        self
    ) -> bool:
        """
        Check if the first frame of the mask of this
        video has, at least, one transparent pixel,
        which means that the mask is actually a
        transparent mask.
        """
        # TODO: I would like to check all the frames not
        # only the first one, but that takes time...
        # TODO: While 1 means that the mask is fully
        # transparent, it could have partial transparency
        # which is a value greater than 0.0, and we are
        # not considering that here...
        return (
            self.has_mask and
            #np.any(self.mask.get_frame(t = 0) == 1) # Full transparent pixel only
            np.any(self.mask.get_frame(t = 0) > 0) # Partial transparent pixel
        )

    @property
    def frames(
        self
    ):
        """
        All the frames of this video clip.
        """
        # TODO: Maybe map in an internal variable (?)
        return MoviepyVideoFrameExtractor.get_all_frames(self.video)

    @property
    def audio_frames(
        self
    ) -> Union[list[any], None]:
        """
        All the frames of the audio clip that is
        attached to this video, if attached, or None
        if not.
        """
        # TODO: Maybe map in an internal variable (?)
        return (
            None
            if not self.has_audio else
            MoviepyVideoFrameExtractor.get_all_frames(self.audio)
        )

    @property
    def number_of_frames(
        self
    ) -> int:
        """
        Get the number of video frames that exist in
        the video, using the duration of this instance
        that can be the one checked if it was requested
        in the '__init__' method.
        """
        return get_number_of_frames(self.duration, self.fps)
    
    @property
    def number_of_audio_frames(
        self
    ) -> Union[int, None]:
        """
        Get the number of audio frames that exist in
        the audio clip that is attached to the video,
        if attached, or None if not audio.
        """
        return (
            None
            if not self.has_audio else
            get_number_of_frames(self.duration, self.audio_fps)
        )
    
    @property
    def frame_indexes(
        self
        # TODO: Please, type
    ) -> list[int]:
        """
        Array containing all the indexes of video frames,
        that can be used to obtain its corresponding
        frame time moment, or to make things simpler.
        """
        self._frames_indexes = (
            T.get_frame_indexes(self.duration, self.fps)
            if not hasattr(self, '_frames_indexes') else
            self._frames_indexes
        )
        
        return self._frames_indexes
        # TODO: Maybe map in an internal variable (?)
        return T.get_frame_indexes(self.duration, self.fps)
    
    @property
    def audio_frame_indexes(
        self
        # TODO: Please, type
    ) -> Union[list[int], None]:
        """
        The indexes of all the audio frames if there is
        an audio clip attached to this video clip, or 
        None if not.
        """
        return (
            None
            if not self.has_audio else
            T.get_frame_indexes(self.duration, self.audio_fps)
        )
    
    @property
    def frame_time_moments(
        self
    ) -> list[float]:
        """
        Array containing all the time moments of video
        frames, that can be used to obtain each frame
        individually with the 'video.get_frame(t = t)'
        method.

        Each frame time moment has been increased by 
        a small amount to ensure it is greater than 
        the base frame time value (due to decimals
        issue).
        """
        # self._frames_time_moments = (
        #     get_frame_time_moments(self.duration, self.fps)
        #     if not hasattr(self, '_frames_time_moments') else
        #     self._frames_time_moments
        # )

        # return self._frames_time_moments
        # TODO: Maybe map in an internal variable (?)
        return T.get_frame_time_moments(self.duration, self.fps)
    
    @property
    def audio_frame_time_moments(
        self
    ) -> Union[list[float], None]:
        """
        All the frame time moments of the audio clip
        that is attached to this video clip, if
        attached, or None if not.
        """
        return (
            None
            if not self.has_audio else
            T.get_frame_time_moments(self.duration, self.audio_fps)
        )
    
    @property
    def inverted(
        self
    ):
        """
        The video but inverted, a process in which the numpy
        array values of each frame are inverted by
        substracting the highest value. If the frame is an
        RGB frame with values between 0 and 255, it will be
        inverted by doing 255 - X on each frame pixel value.
        If it is normalized and values are between 0 and 1
        (it is a mask clip frame), by doing 1 - X on each
        mask frame pixel value.
        """
        mask_frames = [
            MoviepyVideoFrame(frame).inverted
            for frame in self.video.iter_frames()
        ]

        # TODO: Which calculation is better, t * fps or t // frame_duration (?)
        # TODO: What if we have fps like 29,97 (?) I proposed forcing
        # the videos to be 60fps always so we avoid this problem
        return VideoClip(
            make_frame = lambda t: mask_frames[int(t * self.video.fps)],
            is_mask = self.is_mask
        ).with_fps(self.fps)

    @property
    def wrapped_with_transparent_video(
        self
    ) -> 'Clip':
        """
        Place a full transparent background
        behind the video if its size its not
        our default 1920x1080 scene and also
        places this video on the center of
        the background.

        This method generates a copy of the
        original video so it remains
        unchanged.
        """
        return wrap_video_with_transparent_background(self.video)

    def __init__(
        self,
        video: Union[str, Clip],
        is_mask: Union[bool, None] = None,
        do_include_mask: Union[bool, None] = None,
        do_force_60_fps: bool = False,
        do_fix_duration: bool = False
    ):
        """
        If 'is_mask' or 'do_include_mask' is None is 
        because we don't know and/or it must be handled
        automatically
        """
        ParameterValidator.validate_mandatory_instance_of('video', video, [str, VideoClip])
        ParameterValidator.validate_bool('is_mask', is_mask)
        ParameterValidator.validate_bool('do_include_mask', do_include_mask)
        ParameterValidator.validate_mandatory_bool('do_force_60_fps', do_force_60_fps)
        ParameterValidator.validate_mandatory_bool('do_fix_duration', do_fix_duration)

        # A moviepy video can be a 'normal'
        # video or a 'mask' video. Remember,
        # a 'normal' video can have another
        # 'mask' video attached, but a 'mask'
        # video cannot ('normal' nor 'mask')
        is_mask = (
            is_mask
            if is_mask is not None else
            # TODO: Maybe auto-check? How (?)
            False
        )

        # If a 'normal' video, we need to
        # include the mask if requested
        # (and if existing)
        do_include_mask = (
            do_include_mask
            if do_include_mask is not None else
            False
        )

        # Force to read the video with or
        # without mask and recalculating
        # the duration if needed
        # TODO: Cyclic import issue solved here (?)
        video = VideoParser.to_moviepy(
            video,
            do_include_mask = do_include_mask,
            # TODO: By now I'm not calculating the real
            # duration until I solve the way I want to
            # strcture the different video classes...
            # do_calculate_real_duration =  do_fix_duration
        )

        # Forcing the fps to be 60 solves a
        # problem with some strange fps values
        # like 29.97 and also makes easier
        # handling the videos
        video = (
            video.with_fps(60)
            if do_force_60_fps else
            video
        )

        # Solve the moviepy bug about some
        # unreadable frames at the end that
        # make the video having not the
        # expected duration
        video = (
            video.subclipped(0, calculate_real_video_duration(video))
            if do_fix_duration else
            video
        )

        self.video: VideoClip = video
        """
        The moviepy original clip.
        """

    def get_frame(
        self,
        t: float
    ) -> Union[np.ndarray, None]:
        """
        Get the video frame that should be visible at
        the 't' time moment provided.
        """
        return self.video.get_frame(t)
    
    def get_audio_frame(
        self,
        t: float
    ) -> Union[np.ndarray, None]:
        """
        Get the audio frame associated with the 't'
        time moment provided. This is only one 
        audio frame, associated with that audio
        't' time moment. If you need all the audio
        frames associated with a video 't' time 
        moment use the 'get_audio_frames(t)' method.
        """
        return (
            self.audio.get_frame(t)
            if self.has_audio else
            None
        )

    def get_audio_frames(
        self,
        t: float
    ) -> Union[list[np.ndarray], None]:
        """
        Get the audio frames associated with the
        't' video time moment provided. These are
        all the audio frames associated with the
        video frame of the 't' time moment.
        Remember that the amount of audio frames
        attached to a video frame is defined by 
        the `audio_fps/video_fps` division.
        
        If a video has `fps=30` and the audio
        `fps=44_100`, the number of audio frames
        associated to each video frame will be
        `44_100/30=1_470`.
        """
        return (
            [
                self.get_audio_frame(audio_t)
                for audio_t in T.get_audio_frame_time_moments_from_frame_time(
                    video_t = t,
                    video_fps = self.fps,
                    audio_fps = self.audio_fps
                )
            ]
            if self.has_audio else
            None
        ) 

    def _process(
        self
    ) -> VideoClip:
        """
        Process the video. This must be implemented
        in any child class.
        """
        return wrap_video_with_transparent_background(self.video)

    def save(
        self,
        output_filename: str
    ):
        """
        Save the video locally with the 'output_filename'
        name provided.
        """
        ParameterValidator.validate_mandatory_string('output_filename', output_filename, do_accept_empty = False)
        # TODO: Format with 'Output' class (?)

        self.video_processed.write_videofile(output_filename)

class VideoExtended(Video):
    """
    TODO: Write
    """

    @property
    def volume(
        self
    ):
        """
        The volume we want on the video. 

        The range of values we accept as parameters:
        - `0` as the minimum (silence)
        - `300` as the maximum (x3 audio)

        The range of values we store and process
        internally:
        - `0` as the minimum (silence)
        - `3` as the maximum (x3 audio)

        We make it simple for the input using bigger
        numbers than we store divided by 100 to 
        simplify the factor.
        """
        return self._volume
    
    @volume.setter
    def volume(
        self,
        value: VideoAttributeModifier
    ):
        """
        Set the video audio volume values by providing
        a SubClipAtrributeModifier that will set those
        values for this SubClip instance.

        The range of values we accept as parameters:
        - `0` as the minimum (silence)
        - `300` as the maximum (x3 audio)
        """
        _validate_is_video_attribute_modifier_instance(value)
        _validate_attribute_modifier(value, 'volume', VOLUME_LIMIT, self.number_of_frames)

        # Values from 0 to 100 are for humans, but this
        # is a factor so we normalize it
        self._volume = (
            value.modifier / 100
            if value.is_single_value else
            [
                value / 100
                for value in value.get_values(self.number_of_frames)
            ]
        )

    @property
    def zoom(
        self
    ):
        """
        The zoom we want on the video. 

        The range of values we accept as parameters:
        - `1` as the minimum (x0.01)
        - `500` as the maximum (x5.00)

        The range of values we store and process
        internally:
        - `0.01` as the minimum (x0.01)
        - `5.0` as the maximum (x5.00)

        We consider the `100` (`1.0` internally) as the
        no-zoom value.
        """
        return self._zoom
    
    @zoom.setter
    @unset_video_processed
    def zoom(
        self,
        value: int
    ):
        _validate_zoom(value)

        self._zoom = value / 100

    @property
    def x_movement(
        self
    ):
        return self._x_movement
    
    @x_movement.setter
    def x_movement(
        self,
        value: int
    ):
        _validate_x_movement(value)
        
        self._x_movement = int(value)

    @property
    def y_movement(
        self
    ):
        return self._y_movement
    
    @y_movement.setter
    def y_movement(
        self,
        value: int
    ):
        _validate_y_movement(value)
        
        self._y_movement = int(value)

    @property
    def rotation(
        self
    ):
        return self._rotation
    
    @rotation.setter
    def rotation(
        self,
        value: int
    ):
        _validate_rotation(value)
        
        self._rotation = int(value)

    def __init__(
        self,
        video: Union[str, Clip],
        is_mask: Union[bool, None] = None,
        do_include_mask: Union[bool, None] = None,
        do_force_60_fps: bool = False,
        do_fix_duration: bool = False
    ):
        super().__init__(
            video = video,
            is_mask = is_mask,
            do_include_mask = do_include_mask,
            do_force_60_fps = do_force_60_fps,
            do_fix_duration = do_fix_duration
        )

        self._volume: int = 1
        """
        The volume we want on the video. 

        The range of values we accept as parameters:
        - `0` as the minimum (silence)
        - `300` as the maximum (x3 audio)

        The range of values we store and process
        internally:
        - `0` as the minimum (silence)
        - `3` as the maximum (x3 audio)

        We make it simple for the input using bigger
        numbers than we store divided by 100 to 
        simplify the factor.
        """
        self._zoom: int = 1
        """
        The zoom we want on the video. 

        The range of values we accept as parameters:
        - `1` as the minimum (x0.01)
        - `500` as the maximum (x5.00)

        The range of values we store and process
        internally:
        - `1` as the minimum (x0.01)
        - `500` as the maximum (x5.00)

        We consider the `100` as the no-zoom value,
        just as the video originally is.
        """
        self._x_movement: int = 0
        """
        A single value indicating the movement in the X axis,
        where a positive value means right and a negative one 
        left, from the origin.

        TODO: Improve the description and say limits
        """
        self._y_movement: int = 0
        """
        A single value indicating the movement in the Y axis,
        where a positive value means up and a negative one
        bottom, from the origin.

        TODO: Improve the description and say limits
        """
        self._rotation: int = 0
        """
        A single value indicating the rotation of the video
        we want. A positive value will rotate it clockwise,
        and a negative value, anti-clockwise.

        TODO: Improve the description and say limits
        """
        # These 3 values below are used internally to
        # calculate what we need for some effects
        self._resized: tuple[int, int] = [(1, 1)] * self.number_of_frames
        """
        TODO: Improve the description and say limits
        """
        self._rotated: int = [0] * self.number_of_frames
        """
        TODO: Improve the description and say limits
        """
        self._with_position: tuple[int, int] = [(DEFAULT_SCENE_SIZE[0] / 2, DEFAULT_SCENE_SIZE[1] / 2)] * self.number_of_frames
        """
        TODO: Improve the description and say limits
        """

    def set_volume(
        self,
        start: float,
        end: Union[float, None] = None,
        rate_function: RateFunctionArgument = RateFunctionArgument.default()
    ):
        """
        Set a new volume for the video that will be modified frame by
        frame.

        This method allows 2 ways of setting the value:
        - Provide only `start`, so it will be the value for
        all the video frames.
        - Provide `start` and `end`, so the `rate_function`
        will be used to calculate the values in between those
        limits and will be applied for the corresponding frames.
        """
        self._set_attribute('volume', start, end, rate_function)

    def set_zoom(
        self,
        value: int
    ):
        """
        Set a new zoom value.
        """
        self.zoom = value

    def set_x_movement(
        self,
        value: int
    ):
        """
        Set a new x movement value.
        """
        self.x_movement = value

    def set_y_movement(
        self,
        value: int
    ):
        """
        Set a new y movement value.
        """
        self.y_movement = value

    def set_rotation(
        self,
        value: int
    ):
        """
        Set a new rotation value.
        """
        self.rotation = value

    def _set_attribute(
        self,
        attribute: str,
        start: int,
        end: Union[int, None] = None,
        rate_function: RateFunctionArgument = RateFunctionArgument.default()
    ):
        """
        Set the attribute with the VideoAttributeModifier
        class we have created with this purpose, that is
        able to identify the method we want to use to
        generate the values to be set.
        """
        setattr(
            self,
            attribute,
            VideoAttributeModifier(
                VideoSetting(
                    initial_value = start,
                    final_value = (
                        start
                        if end is None else
                        end
                    ),
                    rate_function = rate_function
                )
            )
        )

    @requires_dependency('yta_audio_base', 'yta_video_base', 'yta_audio_base')
    def _process(
        self
    ) -> VideoClip:
        """
        Process the video clip with the attributes set and 
        obtain a copy of the original video clip with those
        attributes and effects applied on it. This method
        uses a black (but transparent) background with the
        same video size to make sure everything works 
        properly.

        This method doesn't change the original clip, it
        applies the changes on a copy of the original one
        and returns that copy modified.
        """
        video = self.video.copy()

        # We do not modify each frame by now in
        # this basic version of the class

        # Process audio frames one by one
        def modify_audio_frame_by_frame(
            get_frame,
            t
        ):
            # The 't' time moment is here a numpy array
            # of a lot of consecutive time moments (maybe
            # 1960). That ishow it works internally
            frame = get_frame(t)
            # Before it was: 'video.fps' and 'video.audio.fps'
            frame_index = T.get_frame_index_from_audio_frame_time(t[500], self.fps, self.audio_fps)

            # Volume value 1 means no change
            if (
                self._volume is not None and
                self._volume != 1
            ):
                from yta_audio_base.volume import AudioVolume
                
                frame = AudioVolume.set_volume(
                    frame,
                    (
                        self._volume * 100
                        if PythonValidator.is_number(self._volume) else
                        self._volume[frame_index] * 100
                    )
                )
                # TODO: The result with this below is the same
                #frame *= self._volume if PythonValidator.is_number(self._volume) else self._volume[frame_index]

            return frame
        
        if self.has_audio:
            audio = self.audio.copy()
            audio = audio.transform(lambda get_frame, t: modify_audio_frame_by_frame(get_frame, t))
            video = video.with_audio(audio)

        # The '_apply_speed_factor' updates these arrays
        resizes = self._resized.copy()
        positions = self._with_position.copy()
        rotations = self._rotated.copy()

        # Modifications below affect to other important
        # attributes.
        # TODO: I don't know if I will accept these
        # modifications below in any case or if I will
        # block them if there are some effects or things
        # that can make conflicts or malfunctioning. If
        # I have a very specific effect, changing these
        # important attributes (resizes, positions and
        # rotations) could be a big headache.
        if (
            self.zoom is not None and
            self.zoom != 1
        ):
            resizes = [
                (resize[0] * self.zoom, resize[1] * self.zoom)
                for resize in resizes
            ]
        if (
            self.x_movement is not None and
            self.x_movement != 0
        ):
            positions = [
                (position[0] + self.x_movement, position[1])
                for position in positions
            ]
        if (
            self.y_movement is not None and
            self.y_movement != 0
        ):
            positions = [
                (position[0], position[1] + self.y_movement)
                for position in positions
            ]
        if (
            self.rotation is not None and
            self.rotation != 0
        ):
            rotations = [
                rotation + self.rotation
                for rotation in rotations
            ]

        """
        The rotation process makes a redimension of the
        frame image setting the pixels out of the rotation
        as alpha to actually build this effect. Thats why
        we need to know the new frame size to be able to
        position it correctly in the position we want
        """
        # Apply the video rotation, frame by frame
        def rotated(
            t
        ):
            """
            Rotate the video by applying the rotation
            values we have and return it to be applied.
            """
            current_frame_index = T.frame_time_to_frame_index(t, video.fps)

            return rotations[current_frame_index]
        
        # Apply the rotation
        video = video.rotated(
            lambda t: rotated(t),
            expand = True
        )

        # As the rotation changes the frame size, we need
        # to recalculate the resize factors
        # TODO: Move this method to a helper or something
        def get_rotated_image_size(
            size: tuple[int, int],
            angle: int
        ):
            """
            Get the size of an image of the given 'size' when it
            is rotated the also given 'angle'.

            This method is based on the moviepy Rotate effect to
            pre-calculate the frame rotation new size so we are
            able to apply that resize factor to the other 
            attributes.

            This method returns the new size and also the width
            size change factor and the height size change factor.
            """
            from PIL import Image

            new_size = Image.new('RGB', size, (0, 0, 0)).rotate(
                angle,
                expand = True,
                resample = Image.Resampling.BILINEAR
            ).size

            width_factor = new_size[0] / size[0]
            height_factor = new_size[1] / size[1]

            return new_size, width_factor, height_factor
        
        for index, resize in enumerate(resizes):
            current_rotation = rotations[index]
            if current_rotation != 0:
                # Recalculate the resize according to the resize
                # factor that took place when rotating the image
                _, width_factor, height_factor = get_rotated_image_size(
                    (
                        int(self.original_width * resize[0]),
                        int(self.original_height * resize[1])
                    ),
                    current_rotation
                )
                
                # Fix the resizes with the calculated values
                resizes[index] = (
                    resize[0] * width_factor,
                    resize[1] * height_factor
                )

        """
        The video 'resized' method doesn't accept double
        factors so I have to manually calculate the new
        size according to the video size and pass that
        exact new size to be actually resized as I need.
        """
        # Resize the video dynamically frame by frame
        def resized(
            t
        ):
            """
            Resize the video by applying the resize factors
            to the original size and return the new size to
            be applied.
            """
            current_frame_index = T.frame_time_to_frame_index(t, self.fps)

            return (
                resizes[current_frame_index][0] * self.original_width,
                resizes[current_frame_index][1] * self.original_height
            )

        # Apply the resize
        video = video.resized(
            lambda t: resized(t)
        )

        """
        The position is very special because it depends on
        the size of each frame, that can change dynamically
        because of resizes, rotations, etc. The 'positions'
        array is pointing the center coordinate of the 
        position, so we need to recalculate the upper left
        corner according to that position.
        """

        def with_position(
            t
        ):
            # This is very slow but I know the exact frame
            # size so I'm sure the positioning will be ok
            #frame = video.get_frame(t)
            #frame_size = frame.shape[1], frame.shape[0]
            current_frame_index = T.frame_time_to_frame_index(t, video.fps)
            
            # Adjust position to its upper left corner
            upper_left_corner_position = [
                # Here before was 'self.width' not 'self.original_width'
                positions[current_frame_index][0] - self.original_width * resizes[current_frame_index][0] / 2,
                positions[current_frame_index][1] - self.original_height * resizes[current_frame_index][1] / 2
            ]

            return upper_left_corner_position[0], upper_left_corner_position[1]
        
        # Apply the position
        video = video.with_position(
            lambda t: with_position(t)
        )

        # TODO: This below is repeated in VideoEditor class as
        # '._overlay_video()'
        return wrap_video_with_transparent_background(video)
        return CompositeVideoClip([
            ClipGenerator.get_default_background_video(duration = video.duration, fps = video.fps),
            video
        ])#.with_audio(VideoAudioCombinator(audio_mode).process_audio(background_video, video))


"""
TODO: I comment this class below because I
am working with the VideoExtended first and
I don't want problems with the imports I
didn't refactor yet...
"""
# class VideoExtendedAdvanced(Video):
#     """
#     Temporary and test class to implement a
#     way of making some easy changes in the
#     frames and render a new video with all
#     those changes.

#     TODO: This class is too advanced, it 
#     must be in a advanced library.
#     """

#     # Special complex attributes below
#     @property
#     def volume(
#         self
#     ):
#         return self._volume
    
#     @volume.setter
#     def volume(
#         self,
#         value: VideoAttributeModifier
#     ):
#         """
#         Set the video audio volume values by providing
#         a SubClipAtrributeModifier that will set those
#         values for this SubClip instance.

#         TODO: Say the limit values and explain more.
#         """
#         _validate_is_video_attribute_modifier_instance(value)
#         _validate_attribute_modifier(value, 'volume', VOLUME_LIMIT, self.number_of_frames)

#         # Values from 0 to 100 are for humans, but this
#         # is a factor so we normalize it
#         self._volume = value.modifier / 100 if value.is_single_value else [value / 100 for value in value.get_values(self.number_of_frames)]

#     @property
#     def color_temperature(
#         self
#     ):
#         """
#         A list of values for the color temperature modification
#         in which each position is the modifier for each video
#         frame.
#         """
#         return self._color_temperature
    
#     @color_temperature.setter
#     def color_temperature(
#         self,
#         value: VideoAttributeModifier
#     ):
#         """
#         Set the color temperature values by providing a 
#         VideoAttributeModifier that will set the values
#         for the current SubClip.
#         """
#         _validate_is_video_attribute_modifier_instance(value)
#         # TODO: Which one to validate (?)
#         # This first one was the original in SubClip
#         _validate_attribute_modifier(value, 'color_temperature', COLOR_TEMPERATURE_LIMIT, self.number_of_frames)

#         self._color_temperature = value.get_values(self.number_of_frames)

#     @property
#     def brightness(
#         self
#     ):
#         """
#         A list of values for the brightness modification in
#         which each position is the modifier for each video
#         frame.
#         """
#         return self._brightness
    
#     @brightness.setter
#     def brightness(
#         self,
#         value: VideoAttributeModifier
#     ):
#         _validate_is_video_attribute_modifier_instance(value)
#         _validate_attribute_modifier(value, 'brightness', BRIGHTNESS_LIMIT, self.number_of_frames)

#         self._brightness = value.get_values(self.number_of_frames)

#     @property
#     def contrast(
#         self
#     ):
#         """
#         A list of values for the contrast modification in which
#         each position is the modifier for each video frame.
#         """
#         return self._contrast
    
#     @contrast.setter
#     def contrast(
#         self,
#         value: VideoAttributeModifier
#     ):
#         _validate_is_video_attribute_modifier_instance(value)
#         _validate_attribute_modifier(value, 'contrast', CONTRAST_LIMIT, self.number_of_frames)

#         self._contrast = value.get_values(self.number_of_frames)

#     @property
#     def sharpness(
#         self
#     ):
#         """
#         A list of values for the sharpness modification in which
#         each position is the modifier for each video frame.
#         """
#         return self._sharpness

#     @sharpness.setter
#     def sharpness(
#         self,
#         value: VideoAttributeModifier
#     ):
#         _validate_is_video_attribute_modifier_instance(value)
#         _validate_attribute_modifier(value, 'sharpness', SHARPNESS_LIMIT, self.number_of_frames)

#         self._sharpness = value.get_values(self.number_of_frames)

#     @property
#     def white_balance(
#         self
#     ):
#         """
#         A list of values for the white balance modification in
#         which each position is the modifier for each video frame.
#         """
#         return self._white_balance
    
#     @white_balance.setter
#     def white_balance(
#         self,
#         value: VideoAttributeModifier
#     ):
#         _validate_is_video_attribute_modifier_instance(value)
#         _validate_attribute_modifier(value, 'white_balance', WHITE_BALANCE_LIMIT, self.number_of_frames)

#         self._white_balance = value.get_values(self.number_of_frames)
#     # Special complex attributes above

#     # Other complex attributes below
#     @property
#     def speed_factor(
#         self
#     ):
#         """
#         A list of values that will modify the video duration
#         making it shorter or longer.
#         """
#         return self._speed_factor
    
#     @speed_factor.setter
#     def speed_factor(
#         self,
#         value: VideoAttributeModifier
#     ):
#         _validate_is_video_attribute_modifier_instance(value)
#         _validate_attribute_modifier(value, 'speed_factor', SPEED_FACTOR_LIMIT, self.number_of_frames)

#         self._speed_factor = (
#             value.modifier
#             if value.is_single_value else
#             value.get_values(self.number_of_frames)
#         )

#     @property
#     def zoom(
#         self
#     ):
#         return self._zoom
    
#     @zoom.setter
#     @unset_video_processed
#     def zoom(
#         self,
#         value: int
#     ):
#         """
#         The zoom must be an integer number between [1, 500]. A
#         zoom value of 100 means no zoom.
        
#         - Zoom=100 means no zoom
#         - Zoom=50 means zoom out until the clip size is the half.
#         - Zoom=200 means zoom in until the clip size is the doubel
#         """
#         _validate_zoom(value)

#         self._zoom = value / 100

#     @property
#     def x_movement(
#         self
#     ):
#         return self._x_movement
    
#     @x_movement.setter
#     def x_movement(
#         self,
#         value: int
#     ):
#         """
#         The movement in X axis must be a value between
#         [-1920*4, 1920*4]. A positive number means moving
#         the clip to the right side.
#         """
#         _validate_x_movement(value)
        
#         self._x_movement = int(value)

#     @property
#     def y_movement(
#         self
#     ):
#         return self._y_movement
    
#     @y_movement.setter
#     def y_movement(
#         self,
#         value: int
#     ):
#         """
#         The movement in Y axis must be a value between
#         [-1920*4, 1920*4]. A positive number means moving
#         the clip to the bottom.
#         """
#         _validate_y_movement(value)
        
#         self._y_movement = int(value)

#     @property
#     def rotation(
#         self
#     ):
#         return self._rotation
    
#     @rotation.setter
#     def rotation(
#         self,
#         value: int
#     ):
#         """
#         Rotation must be an integer value between -360
#         and 360. A positive number means rotating the
#         clip clockwise.
#         """
#         _validate_rotation(value)
        
#         self._rotation = int(value)
#     # Other complex attributes above

#     @property
#     def effects(
#         self
#     ):
#         return self._effects

#     def __init__(
#         self,
#         video: Union[str, Clip],
#         is_mask: Union[bool, None] = None,
#         do_include_mask: Union[bool, None] = None,
#         do_force_60_fps: bool = False,
#         do_fix_duration: bool = False
#     ):
#         super().__init__(
#             video = video,
#             is_mask = is_mask,
#             do_include_mask = do_include_mask,
#             do_force_60_fps = do_force_60_fps,
#             do_fix_duration = do_fix_duration
#         )

#         self._volume = 1
#         """
#         A list of values for the volume we want in the video.
#         """
#         self._color_temperature: Union[float, list[float]] = None # 0
#         """
#         A list of values for the color temperature modification
#         in which each position is the modifier for each video
#         frame.
#         """
#         self._brightness: list[float] = None # 1
#         """
#         A list of values for the brightness modification in
#         which each position is the modifier for each video
#         frame.
#         """
#         self._contrast: list[float] = None
#         """
#         A list of values for the contrast modification in which
#         each position is the modifier for each video frame.
#         """
#         self._sharpness: list[float] = None
#         """
#         A list of values for the sharpness modification in which
#         each position is the modifier for each video frame.
#         """
#         self._white_balance: list[float] = None
#         """
#         A list of values for the white balance modification in
#         which each position is the modifier for each video frame.
#         """

#         # TODO: Are these modifications being applied before
#         # or after the effects and the other things (?)
#         self._speed_factor = 1
#         """
#         A list of values that will modify the video duration
#         making it shorter or longer.
#         """
#         self._zoom = 1
#         """
#         A single value to make the video be zoomed in or out
#         according to it.
#         """
#         self._x_movement = 0
#         """
#         A single value indicating the movement in the X axis,
#         where a positive value means right and a negative one 
#         left, from the origin.
#         """
#         self._y_movement = 0
#         """
#         A single value indicating the movement in the Y axis,
#         where a positive value means up and a negative one
#         bottom, from the origin.
#         """
#         self._rotation = 0
#         """
#         A single value indicating the rotation of the video
#         we want. A positive value will rotate it clockwise,
#         and a negative value, anti-clockwise.
#         """
#         # These 3 values below are used internally to
#         # calculate what we need for some effects
#         self._resized = [(1, 1)] * self.number_of_frames
#         self._rotated = [0] * self.number_of_frames
#         self._with_position = [(DEFAULT_SCENE_SIZE[0] / 2, DEFAULT_SCENE_SIZE[1] / 2)] * self.number_of_frames

#         # TODO: Maybe this should go in the advanced
#         # version of the class as it is there where
#         # we will be able to apply the effects
#         self._effects = []

#     # Easy setters below, that are another way of setting
#     # attributes values but just passing arguments. This
#     # is interesting if you just need to apply a simple
#     # and single value or an easy range
#     def set_volume(
#         self,
#         start: float,
#         end: Union[float, None] = None,
#         rate_function: RateFunctionArgument = RateFunctionArgument.default()
#     ):
#         """
#         Set a new volume for the video that will be modified frame by
#         frame.

#         If only 'start' is provided, the change will be the same in all
#         frames, but if a different 'end' value is provided, the also given
#         'rate_function' will be used to calculate the values in between
#         those 'start' and 'end' limits to be applied in the corresponding
#         frames.
#         """
#         self._set_attribute('volume', start, end, rate_function)

#     def set_color_temperature(
#         self,
#         start: int,
#         end: Union[int, None] = None,
#         rate_function: RateFunctionArgument = RateFunctionArgument.default()
#     ):
#         """
#         Set a new color temperature that will be modified frame by frame.

#         If only 'start' is provided, the change will be the same in all
#         frames, but if a different 'end' value is provided, the also given
#         'rate_function' will be used to calculate the values in between
#         those 'start' and 'end' limits to be applied in the corresponding
#         frames.
#         """
#         self._set_attribute('color_temperature', start, end, rate_function)

#     def set_brightness(
#         self,
#         start: int,
#         end: Union[int, None] = None,
#         rate_function: RateFunctionArgument = RateFunctionArgument.default()
#     ):
#         """
#         Set a new brightness that will be modified frame by frame.
        
#         If only 'start' is provided, the change will be the same in all
#         frames, but if a different 'end' value is provided, the also given
#         'rate_function' will be used to calculate the values in between
#         those 'start' and 'end' limits to be applied in the corresponding
#         frames.
#         """
#         self._set_attribute('brightness', start, end, rate_function)

#     def set_contrast(
#         self,
#         start: int,
#         end: Union[int, None] = None,
#         rate_function: RateFunctionArgument = RateFunctionArgument.default()
#     ):
#         """
#         Set a new contrast that will be modified frame by frame.
        
#         If only 'start' is provided, the change will be the same in all
#         frames, but if a different 'end' value is provided, the also given
#         'rate_function' will be used to calculate the values in between
#         those 'start' and 'end' limits to be applied in the corresponding
#         frames.
#         """
#         self._set_attribute('contrast', start, end, rate_function)

#     def set_sharpness(
#         self,
#         start: int,
#         end: Union[int, None] = None,
#         rate_function: RateFunctionArgument = RateFunctionArgument.default()
#     ):
#         """
#         Set a new sharpness that will be modified frame by frame.
        
#         If only 'start' is provided, the change will be the same in all
#         frames, but if a different 'end' value is provided, the also given
#         'rate_function' will be used to calculate the values in between
#         those 'start' and 'end' limits to be applied in the corresponding
#         frames.
#         """
#         self._set_attribute('sharpness', start, end, rate_function)

#     def set_white_balance(
#         self,
#         start: int,
#         end: Union[int, None] = None,
#         rate_function: RateFunctionArgument = RateFunctionArgument.default()
#     ):
#         """
#         Set a new white balance that will be modified frame by frame.
        
#         If only 'start' is provided, the change will be the same in all
#         frames, but if a different 'end' value is provided, the also given
#         'rate_function' will be used to calculate the values in between
#         those 'start' and 'end' limits to be applied in the corresponding
#         frames.
#         """
#         self._set_attribute('white_balance', start, end, rate_function)

#     def set_speed_factor(
#         self,
#         start: int,
#         end: Union[int, None] = None,
#         rate_function: RateFunctionArgument = RateFunctionArgument.default()
#     ):
#         """
#         Set a new speed factor that will be modifier frame by frame.

#         If only 'start' is provided, the change will be the same in all
#         frames, but if a different 'end' value is provided, the also given
#         'rate_function' will be used to calculate the values in between
#         those 'start' and 'end' limits to be applied in the corresponding
#         frames.
#         """
#         self._set_attribute('speed_factor', start, end, rate_function)

#     def _set_attribute(
#         self,
#         attribute: str,
#         start: int,
#         end: Union[int, None] = None,
#         rate_function: RateFunctionArgument = RateFunctionArgument.default()
#     ):
#         setattr(
#             self,
#             attribute,
#             VideoAttributeModifier(
#                 VideoSetting(
#                     start,
#                     start if end is None else end,
#                     rate_function
#                 )
#             )
#         )

#     # Other easy setters
#     def set_zoom(
#         self,
#         value: int
#     ):
#         """
#         Set a new zoom value.
#         """
#         self.zoom = value

#     def set_x_movement(
#         self,
#         value: int
#     ):
#         """
#         Set a new x movement value.
#         """
#         self.x_movement = value

#     def set_y_movement(
#         self,
#         value: int
#     ):
#         """
#         Set a new y movement value.
#         """
#         self.y_movement = value

#     def set_rotation(
#         self,
#         value: int
#     ):
#         """
#         Set a new rotation value.
#         """
#         self.rotation = value

#     # Complex methods below
#     def copy(
#         self
#     ):
#         # TODO: Complete this method to manually copy the instance
#         # because 'deepcopy' is not working properly
#         copy = VideoExtendedAdvanced(self.video.copy())

#         # The only thing we need to preserve is the values that
#         # modify each attribute. The modifier instance is only
#         # passed to generate these values, so that generator is
#         # only necessary once to generate those values
#         copy._color_temperature = (
#             self._color_temperature.copy()
#             if self._color_temperature is not None else
#             None
#         )
#         copy._brightness = (
#             self._brightness.copy()
#             if self._brightness is not None else
#             None
#         )
#         copy._contrast = (
#             self._contrast.copy()
#             if self._contrast is not None else
#             None
#         )
#         copy._sharpness = (
#             self._sharpness.copy()
#             if self._sharpness is not None else
#             None
#         )
#         copy._white_balance = (
#             self._white_balance.copy()
#             if self._white_balance is not None else
#             None
#         )
#         copy._speed_factor = (
#             self._speed_factor.copy()
#             if self._speed_factor is not None else
#             None
#         )

#         copy._zoom = (
#             self._zoom
#             if self._zoom is not None else
#             None
#         )
#         copy._x_movement = (
#             self._x_movement
#             if self._x_movement is not None else
#             None
#         )
#         copy._y_movement = (
#             self._y_movement
#             if self._y_movement is not None else
#             None
#         )
#         copy._rotation = (
#             self._rotation
#             if self._rotation is not None else
#             None
#         )

#         # TODO: Maybe I need to apply the basic values here (?)
#         copy._resized = (
#             self._resized.copy()
#             if self._resized is not None else
#             None
#         )
#         copy._rotated = (
#             self._rotated.copy()
#             if self._rotated is not None else
#             None
#         )
#         copy._with_position = (
#             self._with_position.copy()
#             if self._with_position is not None else
#             None
#         )

#         return copy

#     @requires_dependency('yta_audio_base', 'yta_video_base', 'yta_audio_base')
#     def _process(self):
#         """
#         Process the video clip with the attributes set and 
#         obtain a copy of the original video clip with those
#         attributes and effects applied on it. This method
#         uses a black (but transparent) background with the
#         same video size to make sure everything works 
#         properly.

#         This method doesn't change the original clip, it
#         applies the changes on a copy of the original one
#         and returns that copy modified.
#         """
#         from yta_audio_base.volume import AudioVolume

#         video = self.video.copy()

#         # Process video frames one by one
#         def modify_video_frame_by_frame(get_frame, t):
#             """
#             Modificate anything related to frame image: pixel
#             colors, distortion, etc.
#             """
#             frame = get_frame(t)
#             frame_index = VideoFrameTHelper.get_frame_index_from_frame_t(t, video.fps)

#             frame = ImageEditor.modify_color_temperature(frame, self._color_temperature[frame_index]) if self._color_temperature is not None else frame
#             frame = ImageEditor.modify_brightness(frame, self._brightness[frame_index]) if self._brightness is not None else frame
#             frame = ImageEditor.modify_contrast(frame, self._contrast[frame_index]) if self._contrast is not None else frame
#             frame = ImageEditor.modify_sharpness(frame, self._sharpness[frame_index]) if self._sharpness is not None else frame
#             frame = ImageEditor.modify_white_balance(frame, self._white_balance[frame_index]) if self._white_balance is not None else frame

#             return frame
        
#         # Apply frame by frame video modifications
#         video = video.transform(lambda get_frame, t: modify_video_frame_by_frame(get_frame, t))

#         # Process audio frames one by one
#         def modify_audio_frame_by_frame(get_frame, t):
#             # The 't' time moment is here a numpy array
#             # of a lot of consecutive time moments (maybe
#             # 1960). That ishow it works internally
#             frame = get_frame(t)
#             frame_index = VideoFrameTHelper.get_video_frame_index_from_video_audio_frame_t(t[500], video.fps, video.audio.fps)

#             # Volume value 1 means no change
#             if self._volume is not None and self._volume != 1:
#                 frame = AudioFrameEditor.modify_volume(
#                     frame,
#                     self._volume if PythonValidator.is_number(self._volume) else self._volume[frame_index]
#                 )
#                 # TODO: The result with this below is the same
#                 #frame *= self._volume if PythonValidator.is_number(self._volume) else self._volume[frame_index]

#             return frame
        
#         if video.audio is not None:
#             audio = video.audio.copy()
#             audio = audio.transform(lambda get_frame, t: modify_audio_frame_by_frame(get_frame, t))
#             video = video.with_audio(audio)

#         # Edit speed with speed factors (carefully)
#         if PythonValidator.is_number(self.speed_factor) and self.speed_factor != 1:
#             from yta_multimedia.video.edition.effect.fit_duration_effect import FitDurationEffect
#             video = FitDurationEffect().apply(video, self.duration / self.speed_factor)
#         elif PythonValidator.is_list(self.speed_factor):
#             # TODO: 'resizes', 'positions' and 'rotations' must be
#             # refactored also according to the new fps
#             video = self._apply_speed_factor(video)

#         # The '_apply_speed_factor' updates these arrays
#         resizes = self._resized.copy()
#         positions = self._with_position.copy()
#         rotations = self._rotated.copy()

#         # Modifications below affect to other important
#         # attributes.
#         # TODO: I don't know if I will accept these
#         # modifications below in any case or if I will
#         # block them if there are some effects or things
#         # that can make conflicts or malfunctioning. If
#         # I have a very specific effect, changing these
#         # important attributes (resizes, positions and
#         # rotations) could be a big headache.
#         if self.zoom is not None and self.zoom != 1:
#             resizes = [(resize[0] * self.zoom, resize[1] * self.zoom) for resize in resizes]
#         if self.x_movement is not None and self.x_movement != 0:
#             positions = [(position[0] + self.x_movement, position[1]) for position in positions]
#         if self.y_movement is not None and self.y_movement != 0:
#             positions = [(position[0], position[1] + self.y_movement) for position in positions]
#         if self.rotation is not None and self.rotation != 0:
#             rotations = [rotation + self.rotation for rotation in rotations]

#         # TODO: Should we apply effects here after the
#         # general basic attributes modifications and after
#         # speed factor is applied, or before? That's a 
#         # a good question that only testing can answer
#         if len(self.effects) > 0:
#             self._apply_effects()

#         """
#         The rotation process makes a redimension of the
#         frame image setting the pixels out of the rotation
#         as alpha to actually build this effect. Thats why
#         we need to know the new frame size to be able to
#         position it correctly in the position we want
#         """
#         # Apply the video rotation, frame by frame
#         video = video.rotated(lambda t: rotations[VideoFrameTHelper.get_frame_index_from_frame_t(t, video.fps)], expand = True)

#         # As the rotation changes the frame size, we need
#         # to recalculate the resize factors
#         # TODO: Move this method to a helper or something
#         def get_rotated_image_size(size: tuple[int, int], angle: int):
#             """
#             Get the size of an image of the given 'size' when it
#             is rotated the also given 'angle'.

#             This method is based on the moviepy Rotate effect to
#             pre-calculate the frame rotation new size so we are
#             able to apply that resize factor to the other 
#             attributes.

#             This method returns the new size and also the width
#             size change factor and the height size change factor.
#             """
#             from PIL import Image

#             new_size = Image.new('RGB', size, (0, 0, 0)).rotate(
#                 angle,
#                 expand = True,
#                 resample = Image.Resampling.BILINEAR
#             ).size

#             width_factor = new_size[0] / size[0]
#             height_factor = new_size[1] / size[1]

#             return new_size, width_factor, height_factor
        
#         for index, resize in enumerate(resizes):
#             current_rotation = rotations[index]
#             if current_rotation != 0:
#                 # Recalculate the resize according to the resize
#                 # factor that took place when rotating the image
#                 _, width_factor, height_factor = get_rotated_image_size(
#                     (
#                         int(self.original_width * resize[0]),
#                         int(self.original_height * resize[1])
#                     ),
#                     current_rotation
#                 )
                
#                 resizes[index] = (
#                     resize[0] * width_factor,
#                     resize[1] * height_factor
#                 )

#         """
#         The video 'resized' method doesn't accept double
#         factors so I have to manually calculate the new
#         size according to the video size and pass that
#         exact new size to be actually resized as I need.
#         """
#         # Resize the video dynamically frame by frame
#         def resized(t):
#             """
#             Resizes the video by applying the resize factors to
#             the original size and returns the new size to be
#             applied.
#             """
#             current_frame_index = VideoFrameTHelper.get_frame_index_from_frame_t(t, video.fps)

#             return (
#                 resizes[current_frame_index][0] * self.original_width,
#                 resizes[current_frame_index][1] * self.original_height
#             )

#         video = video.resized(lambda t: resized(t))

#         """
#         The position is very special because it depends on
#         the size of each frame, that can change dynamically
#         because of resizes, rotations, etc. The 'positions'
#         array is pointing the center coordinate of the 
#         position, so we need to recalculate the upper left
#         corner according to that position.
#         """

#         def with_position(t):
#             # This is very slow but I know the exact frame
#             # size so I'm sure the positioning will be ok
#             #frame = video.get_frame(t)
#             #frame_size = frame.shape[1], frame.shape[0]
#             current_frame_index = VideoFrameTHelper.get_frame_index_from_frame_t(t, video.fps)
            
#             # Adjust position to its upper left corner
#             upper_left_corner_position = [
#                 positions[current_frame_index][0] - self.width * resizes[current_frame_index][0] / 2,
#                 positions[current_frame_index][1] - self.height * resizes[current_frame_index][1] / 2
#             ]

#             return upper_left_corner_position[0], upper_left_corner_position[1]
        
#         video = video.with_position(lambda t: with_position(t))

#         # TODO: This below is repeated in VideoEditor class as
#         # '._overlay_video()'
#         return CompositeVideoClip([
#             ClipGenerator.get_default_background_video(duration = video.duration, fps = video.fps),
#             video
#         ])#.with_audio(VideoAudioCombinator(audio_mode).process_audio(background_video, video))

#     # TODO: What about a method that only receives
#     # 1 time moment and splits the video in two 
#     # using that time moment provided as the half (?)
#     def split(
#         self,
#         start: float,
#         end: float
#     ):
#         """
#         Split the current video instance into 3 different
#         new instances that will be created according to 
#         the 'start' and 'end' times provided, using a copy
#         of the current instance. All settings will be
#         preserved as they were in the original instance
#         for all the new copies. Since this moment, any 
#         new instance will be handled as a new instance,
#         so all the calculations and settings will be
#         applied according to that.

#         This method will return 3 values: left part of the
#         VideoExtender, center part and right part. Left and
#         right part can be None depending on the 'start' and
#         'end' parameters provided. If 'start' is None, the
#         left instance will be None. If 'end' is None, the
#         right instance will be None.
#         """
#         # TODO: We should accept 'start' or 'end' as None
#         # to allow splitting the video in 2
#         ParameterValidator.validate_positive_number('start', start, do_include_zero = True)
#         ParameterValidator.validate_positive_number('end', end, do_include_zero = True)

#         if (
#             start is None and
#             end is None
#         ):
#             # You don't want to split actually...
#             return self
        
#         # We handle 'start' or 'end' as None when
#         # we don't want to split in 3
#         start = (
#             None
#             if start == 0 else
#             start
#         )

#         end = (
#             None
#             if end >= self.duration else
#             end
#         )

#         if (
#             start is not None and
#             end is not None and
#             start >= end
#         ):
#             raise Exception('The "start" parameter provided is greater or equal than the "end" parameter provided.')

#         # TODO: I need to calculate the frame index in which I'm
#         # splitting the subclip to also subclip the arrays that
#         # are inside the instance
#         left = (
#             self.copy()
#             if start is not None else
#             None
#         )
#         center = self.copy()
#         right = (
#             self.copy()
#             if end is not None else
#             None
#         )

#         def replace_attribute_values(
#             instance: VideoExtendedAdvanced,
#             start_index: Union[float, None],
#             end_index: Union[float, None]
#         ):
#             """
#             Replace the attribute values of the given 'instance' 
#             considering the left, center and right videos that will
#             be returned as result so each video keeps only their
#             values.
#             """
#             # TODO: Append here any new array of values per frame
#             instance._color_temperature = (
#                 instance._color_temperature[start_index: end_index]
#                 if instance._color_temperature is not None else
#                 instance._color_temperature # None
#             )
#             instance._brightness = (
#                 instance._brightness[start_index: end_index]
#                 if instance._brightness is not None else
#                 instance._brightness # None
#             )
#             instance._contrast = (
#                 instance._contrast[start_index: end_index]
#                 if instance._contrast is not None else
#                 instance._contrast # None
#             )
#             instance._sharpness = (
#                 instance._sharpness[start_index: end_index]
#                 if instance._sharpness is not None else
#                 instance._sharpness # None
#             )
#             instance._white_balance = (
#                 instance._white_balance[start_index: end_index]
#                 if instance._white_balance is not None else
#                 instance._white_balance # None
#             )

#             # The '_speed_factor' is special and can be both:
#             # a single value or a list (or None)
#             instance._speed_factor = (
#                 instance._speed_factor[start_index: end_index]
#                 if PythonValidator.is_list(instance._speed_factor) else
#                 instance._speed_factor # None or single value
#             )

#             # TODO: Any other attribute missing (?)
            
#             return instance

#         # Make the copies fit the expected part of
#         # the main video, preserving the values that
#         # are attached with those parts
#         last_index = 0
#         # Left
#         if left is not None:
#             left.video = left.video.with_subclip(0, start)
#             last_index = left.number_of_frames
#             left = replace_attribute_values(left, 0, last_index)

#         # Center
#         center.video = center.video.with_subclip(start, end)
#         center = replace_attribute_values(center, last_index, last_index + center.number_of_frames)
#         last_index = last_index + center.number_of_frames

#         # Right
#         if right is not None:
#             right.video = right.video.with_subclip(start_time = end)
#             right = replace_attribute_values(right, last_index, None)

#         return left, center, right

#     def _apply_speed_factor(self, video):
#         """
#         Apply the speed factor to the video. This method 
#         will use the 'time_transform' method and also will
#         set a new duration with the 'with_duration' method.

#         This method returns the new video modified.
#         """
#         # TODO: What is this condition below? We can do
#         # [self.speed_factor] * self.number_of_frames
#         if PythonValidator.is_number(self.speed_factor) or self.speed_factor is None:
#             raise Exception(f'The "speed_factor" parameter is not valid for this method. It must be an array of {self.number_of_frames} elements.')
        
#         def _get_frame_ts_applying_speed_factors(
#             self: VideoExtendedAdvanced
#         ):
#             """
#             Returns a tuple with the video and audio arrays
#             affected by the speed factors.
#             """
#             if self.number_of_frames != len(self.speed_factor):
#                 raise Exception(f'The number of video frames {self.number_of_frames} and speed factors array {len(self.speed_factor)} must be the same.')

#             # We only work with speed factors for video frames
#             # as we know what is the audio associated to each
#             # frame and can modify it according to it
#             final_video_frame_ts = []
#             final_audio_frame_ts = []
#             # TODO: I need to have any array that has to be
#             # recalculated according to the repeated or the
#             # skipped indexes
#             positions = []
#             resizes = []
#             rotations = []

#             rest = 0
#             current_frame_index = 0
#             while current_frame_index < self.number_of_frames:
#                 current_speed_factor = self.speed_factor[current_frame_index]
#                 current_video_frame_t = T.frame_index_to_frame_time(current_frame_index, self.video.fps)

#                 # We know current video frame 't', so we can obtain
#                 # the associated audio frame tts
#                 # TODO: What if no sound attached to the video (?)
#                 current_audio_frame_ts = T.get_audio_frame_time_moments_from_frame_time(current_video_frame_t, self.fps, self.audio_fps)

#                 if current_speed_factor < 1:
#                     # If needed, repeat frames to slow down
#                     times_to_append = 1
#                     current_rest = (1 / current_speed_factor) - 1
#                     rest -= current_rest

#                     if rest <= -1:
#                         times_to_append += int(abs(rest))
#                         rest += int(abs(rest))
                    
#                     final_video_frame_ts.extend([current_video_frame_t] * times_to_append)
#                     """
#                     We have two different ways of handling the audio
#                     duplication.
                    
#                     - One is duplicating block by block, so:
#                     from [1, 2] to [1, 2, 1, 2, 1, 2]

#                     - The other one duplicates value by value, so:
#                     from [1, 2] to [1, 1, 1, 2, 2, 2]

#                     TODO: What about from [1, 2] to [1, 1.33, 1.66,
#                     2] (?)
#                     TODO: Please, read: https://www.notion.so/Ralentizar-audio-asociado-a-v-deo-235f5a32d4628003a87de6ff330af416?source=copy_link
#                     """
#                     # Block by block
#                     #final_audio_frame_ts.extend([current_audio_frame_ts] * times_to_append)
#                     # Value by value
#                     # TODO: Using numpy is better in performance
#                     final_audio_frame_ts.extend([
#                         caft
#                         for caft in current_audio_frame_ts
#                         for _ in range(times_to_append)
#                     ])

#                     # Any other array that also has to be recalculated
#                     resizes.extend([self._resized[current_frame_index]] * times_to_append)
#                     positions.extend([self._with_position[current_frame_index]] * times_to_append)
#                     rotations.extend([self._rotated[current_frame_index]] * times_to_append)

#                 else:
#                     # Extend the video and the audio just once
#                     final_video_frame_ts.append(current_video_frame_t)
#                     final_audio_frame_ts.extend(current_audio_frame_ts)

#                     # Any other array that also has to be recalculated
#                     resizes.append(self._resized[current_frame_index])
#                     positions.append(self._with_position[current_frame_index])
#                     rotations.append(self._rotated[current_frame_index])

#                     if current_speed_factor > 1:
#                         # If needed, we skip frames to speed it up
#                         current_rest = current_speed_factor - 1
#                         rest += current_rest

#                         if rest >= 1:
#                             current_frame_index += int(rest)
#                             rest -= int(rest)

#                 current_frame_index += 1

#             return final_video_frame_ts, final_audio_frame_ts, resizes, positions, rotations

#         final_video_frame_ts, final_audio_frame_ts, resizes, positions, rotations = _get_frame_ts_applying_speed_factors(self)

#         # TODO: Remove this
#         print(f'Total of {len(final_video_frame_ts)} ({len(final_video_frame_ts) / self.video.fps}) video frame ts and {len(final_audio_frame_ts)} ({len(final_audio_frame_ts) / self.video.audio.fps}) audio frame ts.')

#         def transform_t_with_both_frames(t, video_fps: float, audio_fps: float):
#             """
#             Transform the time moment 't' we are processing
#             to render in the new file according to the time
#             moments of the original video/audio. We have
#             pre-calculated them so we know what frame of the
#             original video/audio has to be placed for each
#             rendering time moment 't' we handle here.
#             """
#             if not PythonValidator.is_numpy_array(t):
#                 # Video frame. The 't' is just a time moment
#                 return final_video_frame_ts[
#                     T.frame_time_to_frame_index(t, video_fps)
#                 ]
#             else:
#                 # Audio frame. The 't' is an array of time
#                 # moments. The amount of 't' is unespecific.
#                 # I think it's just a chunk. Mine was 1960
#                 t_indexes = [
#                     T.frame_time_to_frame_index(t_, audio_fps)
#                     for t_ in t
#                 ]

#                 # I have to return an array that replaces
#                 # the original tts
#                 return np.array([
#                     final_audio_frame_ts[t_index]
#                     for t_index in t_indexes
#                 ])

#         # TODO: What if video has no audio (?)
#         video = video.time_transform(
#             lambda t: transform_t_with_both_frames(
#                 t,
#                 self.video.fps,
#                 self.video.audio.fps
#             ),
#             apply_to = ['mask', 'audio']
#         )
#         video = video.with_duration(len(final_video_frame_ts) * get_frame_duration(video.fps))

#         # TODO: I don't want this to be done here, please
#         # return it and do in another place in this class
#         self._resized = resizes
#         # TODO: Positions must be the center of the 
#         # position we want, and then calculate the upper
#         # left corner when actually positioning it
#         self._with_position = positions
#         self._rotated = rotations

#         return video

    # TODO: This method 'add_effect' is for the
    # advanced version of this class, not this one
    # def add_effect(
    #     self,
    #     effect: 'SEffect'
    # ):
    #     """
    #     Add the provided 'effect' instance to be applied on the clip.
    #     """
    #     # TODO: I think this is equivalent
    #     #ParameterValidator.validate_mandatory_subclass_of('effect', effect, 'SEffect')
    #     if (
    #         not PythonValidator.is_an_instance(effect) or
    #         not PythonValidator.is_subclass(effect, 'SEffect')
    #     ):
    #         raise Exception('The provided "effect" parameter is not an instance of a SEffect subclass.')
        
    #     # TODO: Check that effect is valid (times are valid,
    #     # there is not another effect that makes it
    #     # incompatible, etc.)
    #     # We force the correct 'number_of_frames' attribute
    #     effect.number_of_frames = self.number_of_frames

    #     self._effects.append(effect)

    # TODO: This method '_apply_effects' has to go
    # to the advanced version of the instance,
    # through the 'yta_video_advanced' library
    # def _apply_effects(self):
    #     """
    #     Apply the effects.
    #     """
    #     if len(self._effects) > 0:
    #         # TODO: Apply effects
    #         for effect in self._effects:
    #             if effect.do_affect_frames:
    #                 frames = effect.values[0]
    #                 # TODO: Handle 'frames' array, by now I'm just
    #                 # replacing the values
    #                 # TODO: Add or replace (?)
    #                 pass

    #             if effect.do_affect_with_position:
    #                 with_position = effect.values[1]
    #                 # TODO: Handle 'with_position' array, by now I'm just
    #                 # replacing the values
    #                 self._with_position = with_position
    #                 # TODO: Add or replace (?)

    #             if effect.do_affect_resized:
    #                 resized = effect.values[2]
    #                 # TODO: Handle 'resized' array, by now I'm just
    #                 # replacing the values
    #                 self._resized = resized
    #                 # TODO: Multiply or replace (?)

    #             if effect.do_affect_rotated:
    #                 rotated = effect.values[3]
    #                 # TODO: Handle 'rotated' array, by now I'm just
    #                 # replacing the values
    #                 self._rotated = rotated
    #                 # TODO: Add or replace (?)

    # TODO: We still have more things to add from
    # the old SubClip class...


