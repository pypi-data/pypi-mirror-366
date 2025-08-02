""" Utils for segmentation testing """

import unittest

import numpy as np
from shapely.geometry import Polygon

import cv2

from acia.segm.processor.offline import FlexibleModel, ModelDescriptor
from acia.segm.local import LocalImageSource, LocalImage, LocalSequenceSource

import os

os.environ["CACHE_FOLDER"] = "/tmp"

class TestIndexing(unittest.TestCase):
    """Test the linearization of z and t stacks"""

    def test_both(self):

        model_desc = ModelDescriptor(
            repo="https://gitlab+deploy-token-281:TZYmjRQZzLZsBfWsd2XS@jugit.fz-juelich.de/mlflow-executors/omnipose-executor.git",
            parameters={
                # default omnipose model
                "model": "https://fz-juelich.sciebo.de/s/3J8Z7MrADMtw9fz/download"
            },
            entry_point="main",
            version="main"
        )

        fm = FlexibleModel(
            modelDesc=model_desc,
        )

        lis = LocalImageSource.from_file("lut_image.png") #LocalImageSource(LocalImage(cv2.imread("lut_image.png")))

        res = fm.predict(lis)

        print(len(res))
        


if __name__ == "__main__":
    unittest.main()
