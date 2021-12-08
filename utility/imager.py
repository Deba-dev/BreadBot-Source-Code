import io
import typing
from PIL import Image, ImageEnhance, ImageOps
from .imaging import save_image, sort_size, discord
from io import BytesIO
import cv2 as opencv
import numpy as np

file = discord.File
MAX_FRAMES = 30

def exceeded_frames(self, image: Image, ignore: str):
    if getattr(image, 'is_animated', False) and ignore.lower() in [
        '--true', '--ignore-frames', '--reduce',
        '--filter'
    ]:
        if ignore.lower() in ['--reduce', '--filter']:
            pass
        else:
            return image.n_frames > 30
    return False

def IMAGEOPS(effect, stream: io.BytesIO, animate: str, *size) -> Image:
    image: Image = Image.open(stream)

    try:
        if type(size[-1]) == dict:
            kwargs = size[-1]
            size = size[:-1]
        else:
            kwargs = {}
    except IndexError:
        kwargs = {}

    if not size and not getattr(stream, 'discord', False):
        size = image.size
    else:
        size = sort_size(*size)

    if getattr(image, 'is_animated', False) and animate.lower() == '--true':
        duration = image.info.get('duration')
        loops = image.info.get('loop')

        frames = []
        frames_ = image.n_frames if image.n_frames <= MAX_FRAMES else MAX_FRAMES
        for _ in range(frames_):
            frames.append(effect.__call__(image=image.convert('RGB').resize(size), **kwargs))
            image.seek(_)
        return save_image(image=frames, filename='{}.gif'.format(effect.__class__.__name__), duration=duration, loop=loops)

    else:
        inverted: Image = effect.__call__(image=image.convert('RGB').resize(size))
        return save_image(image=inverted, filename='{}.png'.format(effect.__class__.__name__))

def COLOUR_MAP(func, stream: io.BytesIO, animate: str, *size) -> Image:
    try:
        if type(size[-1]) == dict:
            kwargs = size[-1]
            size = size[:-1]
        else:
            kwargs = {}
    except IndexError:
        kwargs = {}

    try:
        if type(size[-1]) == list:
            args = size[-1]
            size = size[:-1]
        else:
            args = []
    except KeyError:
        args = []

    file_bytes = np.asarray(bytearray(stream.read()), dtype=np.uint8)
    image = opencv.imdecode(file_bytes, opencv.IMREAD_COLOR)
    opencv.waitKey(1)