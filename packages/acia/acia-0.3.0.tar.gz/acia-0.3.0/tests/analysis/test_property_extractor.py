""" Testcases for single-cell property extractors """

import unittest
from itertools import product

import numpy as np

from acia import ureg
from acia.analysis import (
    AreaEx,
    CircularityEx,
    DynamicTimeEx,
    ExtractorExecutor,
    FluorescenceEx,
    FrameEx,
    LengthEx,
    LengthWidthEx,
    PerimeterEx,
    PositionEx,
    PropertyExtractor,
    TimeEx,
    WidthEx,
)
from acia.base import Contour, Overlay
from acia.segm.local import InMemorySequenceSource, LocalImageSource, THWCSequenceSource


class TestPropertyExtractors(unittest.TestCase):
    """Test cases for single-cell property extractors"""

    def test_unit_conversion(self):
        # test basic conversion patterns

        self.assertAlmostEqual(
            PropertyExtractor("test", "meter", "millimeter").convert(1), 1000
        )
        self.assertAlmostEqual(
            PropertyExtractor("test", "micrometer", "millimeter").convert(1), 1e-3
        )
        self.assertAlmostEqual(
            PropertyExtractor("test", "liter", "milliliter").convert(1), 1000
        )
        self.assertAlmostEqual(
            PropertyExtractor("test", "micrometer", "micrometer").convert(1), 1
        )
        self.assertAlmostEqual(
            PropertyExtractor("test", "meter", "micrometer").convert(1), 1e6
        )

    def test_extractors(self):
        # in x,y coordinates
        contours = [Contour([[0, 0], [2, 0], [2, 3], [0, 3]], -1, frame=0, id=23)]
        overlay = Overlay(contours)

        image = np.zeros((200, 200))
        image[0, 0] = 2
        image[0, 1] = 5
        image[1, 0] = 6
        image[1, 1] = 10
        image[2, 0:3] = 4
        image[0:2, 2] = 4
        image_source = LocalImageSource.from_array(image)

        # pixel size
        ps = 0.07

        # test basic extractors
        df = ExtractorExecutor().execute(
            overlay=overlay,
            images=image_source,
            extractors=[
                FrameEx(),
                AreaEx(input_unit=(ps * ureg.micrometer) ** 2),
                LengthEx(input_unit=ps * ureg.micrometer),
                WidthEx(input_unit=ps * ureg.micrometer),
                LengthWidthEx("a_", input_unit=ps * ureg.micrometer),
                TimeEx(input_unit="15 * minute"),  # one frame every 15 minutes
                PositionEx(input_unit=ps * ureg.micrometer),
                FluorescenceEx(channels=[0], channel_names=["gfp"], parallel=1),
                FluorescenceEx(
                    channels=[0],
                    channel_names=["gfp_mean"],
                    summarize_operator=np.mean,
                    parallel=1,
                ),
                PerimeterEx(input_unit=(ps * ureg.micrometer)),
                CircularityEx(),
            ],
        )

        self.assertEqual(df["area"].iloc[0], (2 * 3) * ps**2)
        self.assertEqual(df["length"].iloc[0], 3 * ps)
        self.assertEqual(df["a_length"].iloc[0], 3 * ps)
        self.assertEqual(df["width"].iloc[0], 2 * ps)
        self.assertEqual(df["a_width"].iloc[0], 2 * ps)
        self.assertEqual(df.index[0], 23)
        self.assertEqual(df["frame"].iloc[0], 0)
        self.assertEqual(df["time"].iloc[0], 0 * 15 / 60)
        np.testing.assert_almost_equal(df["position_x"].iloc[0], 2 / 2 * ps)
        np.testing.assert_almost_equal(df["position_y"].iloc[0], 3 / 2 * ps)
        self.assertEqual(df["gfp"].iloc[0], np.median(image[:3, :2]))
        self.assertEqual(df["gfp_mean"].iloc[0], np.mean(image[:3, :2]))
        self.assertEqual(df["perimeter"].iloc[0], 10 * ps)
        np.testing.assert_almost_equal(df["circularity"].iloc[0], 0.7539822368615503)

    def test_dynamic_time_extractor(self):
        # in x,y coordinates
        contours = [
            Contour([[0, 0], [2, 0], [2, 3], [0, 3]], -1, frame=0, id=23),
            Contour([[0, 0], [2, 0], [2, 3], [0, 3]], -1, frame=1, id=24),
            Contour([[0, 0], [2, 0], [2, 3], [0, 3]], -1, frame=2, id=25),
        ]
        overlay = Overlay(contours)

        timepoints = [1710326746.8015938, 1710326987.554663, 1710327228.3607492]
        rel_timepoints = np.array(timepoints) - timepoints[0]

        df = ExtractorExecutor().execute(
            overlay=overlay,
            images=THWCSequenceSource(np.zeros((3, 100, 100, 1), dtype=np.uint8)),
            extractors=[FrameEx(), DynamicTimeEx(timepoints, relative=True)],
        )

        self.assertEqual(df["time"].iloc[0], 0)
        self.assertEqual(df["time"].iloc[1], rel_timepoints[1] / 3600)
        self.assertEqual(df["time"].iloc[2], rel_timepoints[2] / 3600)

    def test_dynamic_time_extractor_failures(self):
        contours = [
            Contour([[0, 0], [2, 0], [2, 3], [0, 3]], -1, frame=0, id=23),
            Contour([[0, 0], [2, 0], [2, 3], [0, 3]], -1, frame=1, id=24),
            Contour([[0, 0], [2, 0], [2, 3], [0, 3]], -1, frame=2, id=25),
        ]
        overlay = Overlay(contours)

        with self.assertRaises(ValueError) as _:
            DynamicTimeEx([])

        with self.assertRaises(ValueError) as _:
            _ = ExtractorExecutor().execute(
                overlay=overlay,
                images=THWCSequenceSource(np.zeros((3, 100, 100, 1), dtype=np.uint8)),
                extractors=[
                    FrameEx(),
                    DynamicTimeEx(timepoints=[1, 2], relative=True),
                ],
            )

    def test_fluorescence_extractor_float(self):
        """Testing that the fluorescence exporter can work with float values"""

        contours = [Contour([[0, 0], [2, 0], [2, 3], [0, 3]], -1, frame=0, id=23)]
        overlay = Overlay(contours)

        image = np.zeros((200, 200), dtype=np.float32)
        image[0, 0] = 2.5
        image[0, 1] = 5.5
        image[1, 0] = 6
        image[1, 1] = 10.1
        image[2, 0:3] = 4
        image[0:2, 2] = -4.3
        image_source = LocalImageSource.from_array(image)

        # test basic extractors
        df = ExtractorExecutor().execute(
            overlay=overlay,
            images=image_source,
            extractors=[
                FluorescenceEx(channels=[0], channel_names=["gfp"], parallel=1),
                FluorescenceEx(
                    channels=[0],
                    channel_names=["gfp_mean"],
                    summarize_operator=np.mean,
                    parallel=1,
                ),
            ],
        )

        self.assertEqual(df["gfp"].iloc[0], np.median(image[:3, :2]))
        self.assertEqual(df["gfp_mean"].iloc[0], np.mean(image[:3, :2]))

    def test_parallel_fluorescence_extraction(self):
        squared_num = 30
        contours = [
            Contour([[0, 0], [2, 0], [2, 2], [0, 2]], -1, frame=frame, id=id)
            for id, frame in product(list(range(squared_num)), list(range(squared_num)))
        ]
        overlay = Overlay(contours)

        image = np.zeros((200, 200))
        image[0, 0] = 2
        image[0, 1] = 5
        image[1, 0] = 6
        image[1, 1] = 10
        image_sources = InMemorySequenceSource(np.stack([image] * squared_num))

        self.assertTrue(image_sources is not None)

        # test basic extractors
        df = ExtractorExecutor().execute(
            overlay=overlay,
            images=image_sources,
            extractors=[
                FluorescenceEx(channels=[0], channel_names=["fl1"], parallel=3),
                FluorescenceEx(
                    channels=[0],
                    channel_names=["fl1_mean"],
                    summarize_operator=np.mean,
                    parallel=3,
                ),
            ],
        )

        np.testing.assert_array_equal(df["fl1"], [5.5] * len(df))
        np.testing.assert_array_equal(
            df["fl1_mean"], [np.mean([2, 5, 6, 10])] * len(df)
        )


if __name__ == "__main__":
    unittest.main()
