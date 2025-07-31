from yta_video_base.parser import VideoParser
from yta_video_base.duration import set_video_duration
from yta_video_base.resize import resize_video
from yta_constants.video import ExtendVideoMode, EnshortVideoMode
from yta_image_base.parser import ImageParser
from yta_validation.parameter import ParameterValidator
from yta_positioning.region import Region
from moviepy import ImageClip, CompositeVideoClip
from moviepy.Clip import Clip


# TODO: It would be interesting that the ImageGreenscreen,
# VideoGreenscreen, ImageAlphascreen and VideoAlphascreen
# inherit from this one instead of having an instance and
# using it, but I decided to start like this because of
# the inheritance problems I've experienced in the past 
# that delayed me too much.
class MaskedClipCreator:
    """
    Class created to encapsulate the way we handle regions with
    transparency in moviepy clips and to add other multimedia
    elements behind those regions to be seen through a new 
    CompositedVideoClip.

    This class is intended to be used by the Alphascreen and
    Greenscreen classes that are generating this kind of videos
    with alpha or green regions on the source files.
    """

    regions: list[Region] = []
    """
    The regions existing in the masked_clip
    """
    masked_clip: Clip = None
    """
    The masked clip we want to use to put some multimedia elements
    behind it with the transparency applied to let them be seen
    through the existing regions.
    """

    def __init__(self, regions, masked_clip):
        self.regions = regions
        self.masked_clip = masked_clip

    def from_image_to_image(
        self,
        image,
        output_filename: str = None
    ):
        """
        This method returns a numpy representation of the image
        built by inserting the provided 'image' in this alphascreen.

        This method will write the result as a local file if the
        'output_filename' parameter is provided.

        This method will work if the amount of images to insert is
        the same of the amount of transparent regions existing in 
        this alphascreen.
        """
        # TODO: This is not returning RGBA only RGB. You can use
        # the 'rgba' method from VideoFrameExtractor
        return self.from_images_to_image([image], output_filename)

    def from_images_to_image(
        self,
        images,
        output_filename: str = None
    ):
        """
        This method returns a numpy representation of the image
        built by inserting the provided 'images' in this
        alphascreen.

        This method will write the result as a local file if the
        'output_filename' parameter is provided.

        This method will work if the amount of images to insert is
        the same of the amount of transparent regions existing in 
        this alphascreen.
        """
        video = self.from_images_to_video(images, duration = 1 / 60)

        # TODO: Use VideoFrameExtractor
        if output_filename:
            video.save_frame(output_filename, t = 0)

        # TODO: This is not returning RGBA only RGB. You can use
        # the 'rgba' method from VideoFrameExtractor
        return video.get_frame(t = 0)

    def from_image_to_video(
        self,
        image,
        duration: float,
        output_filename: str = None
    ):
        """
        This method returns a CompositeVideoClip with the provided
        'image' fitting the first alphascreen area and centered on
        those areas by applying a mask that let them be seen
        through that mask.

        This method will write the result as a local file if the
        'output_filename' parameter is provided.

        This method will work if the amount of images to insert is
        the same of the amount of transparent regions existing in 
        this alphascreen.
        """
        return self.from_images_to_video([image], duration, output_filename)
    
    def from_images_to_video(
        self,
        images,
        duration: float,
        output_filename: str = None
    ):
        """
        This method returns a CompositeVideoClip with the provided
        'images' fitting the different alphascreen areas and
        centered on those areas by applying a mask that let them be
        seen through that mask.

        This method will write the result as a local file if the
        'output_filename' parameter is provided.

        This method will work if the amount of images to insert is
        the same of the amount of transparent regions existing in 
        this alphascreen.
        """
        self._validate_enough_elements_for_regions(images)

        ParameterValidator.validate_mandatory_positive_number('duration', duration, do_include_zero = False)

        # TODO: Use the 'transparent' parameter (?)
        videos = [
            ImageClip(ImageParser.to_numpy(image), duration = duration).with_fps(60)
            for image in images
        ]

        return self.from_videos_to_video(videos, output_filename)
    
    def from_video_to_video(
        self,
        video,
        output_filename: str = None
    ):
        """
        This method returns a CompositeVideoClip with the provided
        'video' fitting in the alphascreen area and centered on it
        by applying a mask that let it be seen through that mask.

        This method will write the result as a local file if the
        'output_filename' parameter is provided.

        This method will work if the amount of images to insert is
        the same of the amount of transparent regions existing in 
        this alphascreen.
        """
        return self.from_videos_to_video([video], output_filename)

    def from_videos_to_video(
        self,
        videos,
        output_filename: str = None
    ):
        """
        This method is pretend to be used by the Alphascreen or
        Greenscreen classes to simplify the process and code.

        This method returns a CompositeVideoClip with the provided
        'videos' fitting the different alphascreen areas and
        centered on those areas by applying a mask that let them be
        seen through that mask.

        This method will write the result as a local file if the
        'output_filename' parameter is provided.

        This method will work if the amount of images to insert is
        the same of the amount of transparent regions existing in 
        this alphascreen.
        """
        self._validate_enough_elements_for_regions(videos)

        longest_duration = 0
        for video in videos:
            video = VideoParser.to_moviepy(video)
            if video.duration > longest_duration:
                longest_duration = video.duration

        for index, video in enumerate(videos):
            videos[index] = place_video_inside_region(video, self.regions[index])

        # TODO: What if video is not as longer as 'longest_duration' (?)
        masked_clip = self.masked_clip.with_duration(longest_duration)

        return self._build_composite_clip(videos, masked_clip, output_filename)


    def _validate_enough_elements_for_regions(
        self,
        elements
    ):
        """
        Raises an exception if the provided amount of 'elements' is 
        greater or less than the amount of alpha regions.
        """
        if len(elements) != len(self.regions):
            raise Exception(f'There are more or less elements provided ({str(len(elements))}) than available masked regions ({str(len(self.regions))}).')

    def _build_composite_clip(
        self,
        videos,
        masked_clip,
        output_filename: str = None
    ):
        """
        Builds the CompositeVideoClip that includes the provided 'videos'
        and the also provided 'alpha_clip' to build the desired video with
        alpha regions filled with the videos.
        """
        # TODO: Please private method
        # As this is for internal use I consider that 'videos' and
        # 'alpha_clip' are valid ones and ready to be used at this point

        # TODO: Provided videos can be shorther than the alphascreen
        # or the alphascreen can be shorter than the videos, so we
        # need an strategy to follow. By now I'm forcing all the 
        # videos to fit the alphascreen duration by shortening or
        # enlarging them.
        for index, _ in enumerate(videos):
            videos[index] = set_video_duration(videos[index], masked_clip.duration, ExtendVideoMode.FREEZE_LAST_FRAME, EnshortVideoMode.CROP)

        composite_clip = CompositeVideoClip([
            *videos,
            masked_clip
        ], size = masked_clip.size)

        composite_clip = composite_clip.with_fps(60) if not composite_clip.fps else composite_clip

        if output_filename:
            composite_clip.write_videofile(output_filename)

        return composite_clip

def place_video_inside_region(
    video: Clip,
    region: Region
):
    """
    Resize and place the provided 'video' in the
    position that fits the given 'region'.
    """
    video = VideoParser.to_moviepy(video)

    # Resize
    video = resize_video(video, region.size_to_fit)
    # Position
    x = region.center[0] - video.w / 2
    y = region.center[1] - video.h / 2

    # TODO: What about upper limits (out of bottom left bounds) (?)
    x = (
        0
        if x < 0 else
        x
    )
    y = (
        0
        if y < 0 else
        y
    )

    return video.with_position((x, y))