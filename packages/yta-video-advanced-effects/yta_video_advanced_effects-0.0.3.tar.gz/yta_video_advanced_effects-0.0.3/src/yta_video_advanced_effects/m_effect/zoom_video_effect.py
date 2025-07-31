from yta_video_advanced_effects.m_effect import MEffect as Effect
from yta_video_base.video import VVideo
from yta_video_advanced_effects.moviepy.objects import MoviepyArgument, MoviepyWith
from yta_multimedia.video.edition.effect.moviepy.t_function import TFunctionResize
from yta_video_moviepy.generator import MoviepyNormalClipGenerator
from yta_general_utils.math.rate_functions.rate_function_argument import RateFunctionArgument
from moviepy.Clip import Clip


# TODO: The use of this method must be by using the
# new MoviepyWith, not VideoEffect that will be
# removed in a near future version.
# TODO: Rename it, as it is making zoom but in an
# specific an static position, so it should be
# something like ZoomInPlaceEffect
class ZoomVideoEffect(Effect):
    """
    Creates a Zoom effect in the provided video.
    """

    def apply(
        self,
        video: Clip,
        zoom_start: float,
        zoom_end: float,
        rate_function: RateFunctionArgument = RateFunctionArgument.default()
    ):
        """
        Apply the effect on the provided 'video'.

        :param float zoom_start: The zoom at the start of the video, where a 1 is no zoom, a 0.8 is a zoom out of 20% and 1.1 is a zoom in of a 10%.

        :param float zoom_end: The zoom at the end of the video, where a 1 is no zoom, a 0.8 is a zoom out of 20% and 1.1 is a zoom in of a 10%.

        :param type rate_func: The rate function to apply in the animation effect. Must be one of the methods available in the RateFunction class.
        """
        # TODO: I have 2 ways of making a zoom. One is placing the clip
        # over a black (transparent) background and resizing in in the
        # center. The other one is resizing it and recalculating the
        # position for each frame to be at the same position but still
        # being resized

        # 1st. Use black background
        arg = MoviepyArgument(zoom_start, zoom_end, TFunctionResize.resize_from_to, rate_function)
        background_video = MoviepyNormalClipGenerator.get_static_default_color_background(duration = video.duration, fps = video.fps)

        return MoviepyWith.apply_over_video(video, background_video, resized = arg)
    
        vvideo = VVideo(video)

        # 2nd. Resize but keeping the position
        resizes = [
            TFunctionResize.resize_from_to(t, video.duration, zoom_start, zoom_end, rate_function)
            for t in vvideo.frame_time_moments
        ]

    # TODO: I don't need this
    def apply_over_video(
        self,
        video,
        background_video
    ):
        return super().apply_over_video(video, background_video)