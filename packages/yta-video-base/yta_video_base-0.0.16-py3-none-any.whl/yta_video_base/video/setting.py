from yta_general_utils.math.rate_functions.rate_function_argument import RateFunctionArgument
from yta_general_utils.math.progression import Progression


# TODO: Think again about this because now we have the
# VideoAttributeModifier to be passed as the modifier
# and it accepts this VideoSetting, that must be renamed
# for its new purpose
class VideoSetting:
    """
    Class to represent a video setting to be able to handle
    dynamic setting values and not only simple values. This
    means we can make a video go from 0 contrast to 10 
    contrast increasing it smoothly (for example: 0, 2, 4,
    6, 8 and 10) and not only abruptly (from 0 in one frame
    to 10 in the next frame).
    """

    initial_value: float = None
    final_value: float = None
    rate_function: RateFunctionArgument = None
    _values: list[float] = None
    """
    The list of values calculated in a previous method call
    to avoid recalculating them. The amount of elements is
    the amount of steps used in the previous calculation.
    """

    def __init__(
        self,
        initial_value: float,
        final_value: float,
        rate_function: RateFunctionArgument = RateFunctionArgument.default()
    ):
        # TODO: Maybe validate something? I don't know the
        # limits because each setting is different, but by
        # now I'm verifying the 'initial_value' and the
        # 'final_value' when using them on a SubClip
        self.initial_value = initial_value
        self.final_value = final_value
        self.rate_function = rate_function

    def get_values(
        self,
        steps: int
    ):
        """
        Obtain an array with the values between the 'initial_value'
        and the 'final_value' according to the 'rate_function'.

        The 'steps' parameter must be the amount of frames in which
        we are planning to apply this setting so we are able to read
        the value for each frame according to its index.
        """
        # Same limits cannot be handled by the Progression class as
        # it is just an array of the same value repeated 'steps' 
        # times
        # TODO: What about a rate function that allows us generating
        # different values even when the 'initial_value' and the
        # 'final_value' are the same (?)
        if self.initial_value == self.final_value:
            return [self.initial_value] * steps
        
        if (
            self._values is None or
            len(self._values) != steps
        ):
            # We recalculate only if needed
            self._values = Progression(self.initial_value, self.final_value, steps, self.rate_function).values
            
        return self._values
    
    def copy(
        self
    ):
        """
        Make a copy of the instance.
        """
        return VideoSetting(
            self.initial_value,
            self.final_value,
            self.rate_function
        )