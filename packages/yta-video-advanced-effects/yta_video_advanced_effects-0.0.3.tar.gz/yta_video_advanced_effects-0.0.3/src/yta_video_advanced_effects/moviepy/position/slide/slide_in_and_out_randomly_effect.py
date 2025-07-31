from yta_video_advanced_effects.m_effect import MEffect as Effect
from yta_video_advanced_effects.moviepy.position.move.move_linear_position_effect import MoveLinearPositionEffect
from yta_video_advanced_effects.moviepy.position.objects.coordinate import Coordinate
from yta_video_advanced_effects.moviepy.position.objects.moviepy_slide import MoviepySlide
from yta_positioning.position import Position
from yta_video_moviepy.generator import MoviepyNormalClipGenerator
from moviepy.Clip import Clip
from moviepy import concatenate_videoclips
from typing import Union


class SlideInAndOutRandomlyEffect(Effect):
    """
    Slides from outside the screen to the specified position
    (which is the center by default), stays there and goes
    away through the opposite side.
    """
    def apply(
        self,
        video: Clip,
        position: Union[Position, Coordinate, tuple] = Position.CENTER
    ) -> Clip:
        # TODO: This is not working properly yet
        #PythonValidator.validate_method_params(BlurEffect.apply, locals(), ['video'])
        background_video = MoviepyNormalClipGenerator.get_static_default_color_background(duration = video.duration, fps = video.fps)

        return self.apply_over_video(video, background_video, position)
    
    def apply_over_video(
        self,
        video: Clip,
        background_video: Clip,
        position: Union[Position, Coordinate] = Position.CENTER
    ) -> Clip:
        random_position = MoviepySlide.get_in_and_out_positions_as_list()

        # TODO: Is this ok (?)
        # video_handler = MPVideo(video)
        # background_video = video_handler.prepare_background_clip(background_video)

        movement_time = background_video.duration / 6
        stay_time = background_video.duration / 6 * 4

        return concatenate_videoclips([   
            MoveLinearPositionEffect().apply_over_video(
                video.with_subclip(0, movement_time),
                background_video.with_subclip(0, movement_time),
                random_position[0],
                position
            ),
            # TODO: This can be replaced by a StayAtPositionEffect
            # but the result is the same actually
            MoveLinearPositionEffect().apply_over_video(
                video.with_subclip(movement_time, movement_time + stay_time),
                background_video.with_subclip(movement_time, movement_time + stay_time),
                position,
                position
            ),
            MoveLinearPositionEffect().apply_over_video(
                video.with_subclip(movement_time + stay_time, video.duration),
                background_video.with_subclip(movement_time + stay_time, video.duration),
                position,
                random_position[1]
            )
        ])