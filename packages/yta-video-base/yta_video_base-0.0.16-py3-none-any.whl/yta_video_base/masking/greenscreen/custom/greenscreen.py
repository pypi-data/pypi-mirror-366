from yta_video_base.masking.greenscreen.custom.image_greenscreen import ImageGreenscreen
from yta_video_base.masking.greenscreen.custom.video_greenscreen import VideoGreenscreen
from yta_video_base.masking.greenscreen.consts import GREENSCREENS_FOLDER
from yta_multimedia.resources import Resource
from yta_general_utils.checker.url import url_is_ok
from yta_general_utils.checker.url import is_google_drive_url
from yta_file.handler import FileHandler
from yta_google_drive_downloader import GoogleDriveResource


class Greenscreen:
    """
    This class is an initializer of the ImageGreenscreen and 
    VideoGreenscreen classes so you provide the valid filename
    or Google Drive url of a greenscreen to the 'init' method
    and you get the corresponding ImageGreenscreen or 
    VideoGreenscreen initialized and ready to work.

    If you provide a Google Drive url the system will identify
    the resource and download it only if necessary, as it will
    create locally a unique identifier with the Google Drive ID
    so once it's been downloaded the first time it will be get
    from the local source the next time.

    This will not be possible if a local path is given as the
    system will not be able to identify the resource and the
    greenscreen processing time will be long in any execution.
    """

    @staticmethod
    def init(
        filename_or_google_drive_url: str
    ):
        """
        Parses the provided parameter 'filename_or_google_drive_url' and
        checks if it is a valid filename or a valid Google Drive url. If
        valid, it dowloads the resource (if necessary) and checks if the
        file is an image or a video and returns the corresponding
        ImageGreenscreen or VideoGreenscreen.

        This method will raise an Exception if something goes wrong.
        """
        filename = Greenscreen.process_file(filename_or_google_drive_url)

        # We have a valid filename, lets check if video or image
        if FileHandler.is_image_file(filename):
            return ImageGreenscreen(filename)
        elif FileHandler.is_video_file(filename):
            return VideoGreenscreen(filename)
        else:
            raise Exception(f'The greenscreen file "{filename}" is not a valid image or video file.')
    
    # TODO: This method below is exactly the same as the one in 
    # 'greenscreen.py' file. Only the folder name changes
    @staticmethod
    def process_file(
        filename_or_google_drive_url: str
    ):
        """
        Parses the provided parameter 'filename_or_google_drive_url' and
        checks if it is a valid filename or a valid Google Drive url. If
        valid, it dowloads the resource (if necessary) and checks if the
        file is an image or a video and returns the corresponding
        filename.

        This method will raise an Exception if something goes wrong.
        """
        is_a_file = FileHandler.file_exists(filename_or_google_drive_url)
        is_url = False
        filename = filename_or_google_drive_url

        if not is_a_file:
            is_url = url_is_ok(filename_or_google_drive_url)

            if not is_url:
                raise Exception(f'The provided greenscreen "{filename_or_google_drive_url}" parameter is not a file nor a valid url.')
            
            if not is_google_drive_url(filename_or_google_drive_url):
                raise Exception(f'The provided greenscreen "url" parameter "{filename_or_google_drive_url}" is not a valid Google Drive url.')
            
            google_drive_id = GoogleDriveResource(filename_or_google_drive_url).id
            folder = f'{GREENSCREENS_FOLDER}{google_drive_id}/'
            # Extension will be replaced with real one
            filename = Resource.get(filename_or_google_drive_url, folder + 'alphaorgreenscreen.png')

        return filename