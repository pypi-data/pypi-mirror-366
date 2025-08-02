""" Test acia base functionality"""

import unittest

import numpy as np

import time

from acia.segm.output import fast_mask_rendering


class TestMaskRendering(unittest.TestCase):
    """Test contour functionality"""

    def test_fast_mask(self):
        mask = np.array([
            [0, 0, 0, 0, 0],
            [0, 0, 3, 3, 0],
            [0, 3, 3, 3, 3],
            [0, 2, 2, 0, 0],
        ], dtype=np.uint8)

        im = np.zeros((*mask.shape, 3), dtype=np.uint8)

        colors = [(255, 0, 0), ]

        rendered_image = fast_mask_rendering((mask==3)[None], np.copy(im), colors)
        np.testing.assert_equal(rendered_image[...,0] == 127, mask==3)

        colors = [(255, 0, 0), (0, 0, 255)]
        rendered_image = fast_mask_rendering(np.stack([(mask==3), mask==2]), np.copy(im), colors)

        np.testing.assert_equal(rendered_image[...,0] == 127, mask==3)
        np.testing.assert_equal(rendered_image[...,2] == 127, mask==2)

        #print(rendered_image)
        #print(rendered_image.shape)


if __name__ == "__main__":
    unittest.main()
