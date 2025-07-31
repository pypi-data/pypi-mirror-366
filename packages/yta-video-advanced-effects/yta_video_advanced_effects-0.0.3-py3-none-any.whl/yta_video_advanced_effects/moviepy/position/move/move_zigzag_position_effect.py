from yta_video_advanced_effects.m_effect import MEffect as Effect
from yta_video_advanced_effects.moviepy.position.objects.coordinate import Coordinate
from yta_video_advanced_effects.moviepy.t_function import TFunctionSetPosition
from yta_video_advanced_effects.moviepy.objects import MoviepyArgument, MoviepyWith
from yta_positioning.position import Position
from yta_video_base.parser import VideoParser
from yta_general_utils.math.rate_functions.rate_function_argument import RateFunctionArgument
from moviepy.Clip import Clip
from typing import Union


class MoveZigzagPositionEffect(Effect):
    """
    Move from A to B doing a wave effect
    while moving.
    """

    # TODO: Is this working (?)
    result_must_replace = True

    def apply(
        cls,
        video: Union[Clip, str],
        initial_position: Union[Coordinate, Position],
        final_position: Union[Coordinate, Position]
    ):
        video = VideoParser.to_moviepy(video)

        # TODO: Validate and parse 'initial_position' and 
        # 'final_position'. These positions must be coordinates
        # on a 1920x1080 scene.
        arg = MoviepyArgument(initial_position, final_position, TFunctionSetPosition.zigzag, RateFunctionArgument.default())

        return MoviepyWith.apply(video, with_position = arg)
    
    def apply_over_video(
        cls,
        video: Union[Clip, str],
        background_video: Union[Clip, str],
        initial_position: Union[Coordinate, Position],
        final_position: Union[Coordinate, Position]
    ):
        arg = MoviepyArgument(initial_position, final_position, TFunctionSetPosition.zigzag, RateFunctionArgument.default())

        return MoviepyWith.apply_over_video(video, background_video, with_position = arg)