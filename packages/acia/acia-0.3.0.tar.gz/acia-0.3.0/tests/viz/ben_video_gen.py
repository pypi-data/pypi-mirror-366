import timeit
import numpy as np
from acia.viz import VideoExporter2, VideoExporter

def run_encoder(encoder):
    images = np.random.randint(0, 255, size=(100, 1024, 1024, 3), dtype=np.uint8)

    with encoder as ve:
        for image in images:
            ve.write(image)


def func():
    run_encoder(VideoExporter2.default_h265("test.mp4", 3))

def func_old():
    run_encoder(VideoExporter("test.mp4", 3, codec="vp09"))

run_encoder(VideoExporter2.default_av1("test.mkv", 3))

#print(timeit.repeat(func, number=1, repeat=1))
#print(timeit.repeat(func_old, number=1, repeat=1))