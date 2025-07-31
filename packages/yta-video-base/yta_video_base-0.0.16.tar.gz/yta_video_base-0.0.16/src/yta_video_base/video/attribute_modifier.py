from yta_validation import PythonValidator
from yta_general_utils.math.progression import Progression
from typing import Union


class VideoAttributeModifier:
    """
    Class to encapsulate the possible ways to modify a 
    video attribute.

    This will be passed as an instance to a Video to 
    calculate the modification values array for each 
    frame and set those modifying values in the video
    instance to be lately applied to the video when
    processing it.

    This is a wrapper to simplify the way we interact
    with different object types valid to generate
    values.

    The only accepted values by now are:
    - Single value
    - VideoSetting
    - Graphic
    """

    modifier: Union[any, 'VideoSetting', 'Graphic'] = None

    @property
    def is_single_value(
        self
    ) -> bool:
        """
        Return True if the modifier is just a single value.
        """
        return PythonValidator.is_number(self.modifier)

    def __init__(
        self,
        modifier: Union[any, 'SubClipSetting', 'Graphic']
    ):
        # TODO: Change SubClipSetting name as its purpose is
        # now different and not to appropiate for this
        if (
            # TODO: Maybe we accept some non-numeric modifier
            # single values (?)
            not PythonValidator.is_number(modifier) and
            not PythonValidator.is_instance_of(modifier, 'SubClipSetting') and
            not PythonValidator.is_instance_of(modifier, 'Graphic')
        ):
            raise Exception('The provided "modifier" parameter is not a valid modifier.')
        
        self.modifier = modifier

    def get_values(
        self,
        n: float
    ):
        """
        Obtain an array of 'n' values that will modify the
        attribute this instance is designed for. The 'n'
        value must be the number of frames.
        """
        # I don't like float 'fps' but it is possible, and I
        # should force any clip to be 30 or 60fps always
        return (
            [self.modifier] * n
            if PythonValidator.is_number(self.modifier) else
            self.modifier.get_values(n)
            if PythonValidator.is_instance_of(self.modifier, 'SubClipSetting') else
            [
                self.modifier.get_xy_from_normalized_d(d)[1]
                for d in Progression(0, 1, n).values
            ]
            if PythonValidator.is_instance_of(self.modifier, 'Graphic') else
            1 # TODO: What about this option (?)
        )
        # if PythonValidator.is_number(self.modifier): return [self.modifier] * n
        # if PythonValidator.is_instance_of(self.modifier, 'SubClipSetting'): return self.modifier.get_values(n)
        # if PythonValidator.is_instance_of(self.modifier, 'Graphic'): return [self.modifier.get_xy_from_normalized_d(d)[1] for d in Progression(0, 1, n).values]

    def validate_values(
        self,
        n: float,
        limit: list[float, float]
    ):
        """
        Validate that any of those 'values' is between the
        limit range. The 'n' parameter must be the number of
        frames in the video, and 'limit' a tuple of the lower
        and upper limit.

        This method must be called when a VideoAttributeModifier
        instance is set in a SubClip because we know the number
        of frames and the limit for that specific attribute (it
        is being added to that attribute modifier) in that 
        moment.
        """
        if any(
            (
                value < limit[0] or
                value > limit[1]
            )
            for value in self.get_values(n)
        ):
            raise Exception(f'One of the generated "values" is out of the limit [{limit[0]}, {limit[1]}]')

    def copy(
        self
    ):
        """
        Make a copy of the instance.
        """
        return VideoAttributeModifier(self.modifier.copy())