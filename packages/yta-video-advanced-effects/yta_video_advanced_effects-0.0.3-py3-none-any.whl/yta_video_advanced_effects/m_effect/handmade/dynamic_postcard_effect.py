from yta_video_advanced_effects.m_effect import MEffect as Effect
from yta_video_base.parser import VideoParser
from yta_video_moviepy.generator import MoviepyNormalClipGenerator
from yta_constants.multimedia import DEFAULT_SCENE_SIZE
from yta_random import Random
from moviepy import concatenate_videoclips, CompositeVideoClip, ColorClip, ImageClip
from moviepy.Clip import Clip


class DynamicPostcardEffect(Effect):
    """
    Makes the provided clip being displayed as a dynamic 
    postcard whose frames are rotated and resized to make
    an effect similar to the one in this reel:

    https://www.instagram.com/reel/C-ZzozroX_1/?igsh=MTVrcmtsYWFuMnowZw%3D%3D

    This effect is recommended to be used with a pure 
    white background.
    """
    def apply(
        self,
        video: Clip
    ) -> Clip:
        # TODO: duration = 1 / video.fps (?)
        background_video = MoviepyNormalClipGenerator.get_static_default_color_background(duration = 1 / video.fps, fps = video.fps)

        return self.apply_over_video(video, background_video)
    
    def apply_over_video(
        self,
        video: Clip,
        background_video: Clip
    ):
        # TODO: This is not working properly yet
        #PythonValidator.validate_method_params(BlinkEffect.apply, locals(), ['video'])
        video = VideoParser.to_moviepy(video)

        # TODO: We can use images as backgrounds if we have them
        # but we will have, for sure, dynamic white backgrounds
        # we create by ourselves
        #backgrounds_abspath = 'C:/Users/dania/Desktop/tmp_greenscreens/test_effect/'
        #files = FileHandler.get_list(backgrounds_abspath, FileSearchOption.FILES_ONLY)

        # I could obtain images from somewhere and resize all of them
        # to 1920x1080 keeping the aspect ratio

        # We need to have images enough for each video frame
        #images = files * (video.n_frames // len(files))

        frames = []
        for _, frame in enumerate(video.iter_frames()):
            # TODO: We can apply a stop-motion effect but that makes
            # the video last more than the original video
            frames.append(CompositeVideoClip([
                # TODO: What if 1920x1080 is not the original video size (?)
                ColorClip(DEFAULT_SCENE_SIZE, color = [255, 255, 255], duration = 1 / video.fps),
                # TODO: We can use the images as background instead of
                # these white backgrounds
                # ImageClip(images[index], duration = 5 / 60).with_fps(60),
                ImageClip(frame, duration = 1 / video.fps).with_fps(video.fps).with_position(('center', 'center'))
            ]))

        clips = []
        for frame in frames:
            #image_frame = ImageClip(frame, duration = 1 / 60).with_fps(60)
            resize = 1 + Random.float_between(0, 0.1, step = 0.005)
            rotation = 2 * Random.float_between(0, 1, step = 0.1)
            if Random.bool():
                rotation = -abs(rotation)

            clips.append(CompositeVideoClip([
                MoviepyNormalClipGenerator.get_static_default_color_background(duration = 1 / video.fps, fps = video.fps),
                #image_frame.with_position(('center', 'center')).resized(1 + randrangefloat(0, 0.1, step = 0.005)).rotated(rotation)
                frame.with_position(('center', 'center')).resized(resize).rotated(rotation)
            ]))

        # TODO: I think I am creating more clips than needed but,
        # as it seems to be working, I don't touch anything by now
        # TODO: Use our custom 'concatenate_videos'
        video = concatenate_videoclips(clips)
        # TODO: Do this as EaseIn or similar, not linear
        #white_background = ClipGenerator.generate_color_background((1920, 1080), [255, 255, 255], video.duration, video.fps)
        video = CompositeVideoClip([
            background_video,
            #MoviepyNormalClipGenerator.get_static_default_color_background(duration = video.duration),
            video.resized(lambda t: 1.5 - 0.5 * t / video.duration).with_position(('center', 'center'))
        ])

        return video