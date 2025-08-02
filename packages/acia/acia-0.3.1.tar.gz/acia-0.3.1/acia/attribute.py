"""Attribute usage"""

import logging
import os
from datetime import datetime, timezone

import networkx as nx
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from acia.base import Overlay

logger = logging.getLogger(__name__)

TOKEN = "58M8R17lQgh-U17snMPjya139MFD9_de2KqseKmJihcAZ6mkohozd-9-rvz71SZLI7GI1Qz8Nii2QxI1QjcVkw=="
URL = "https://worldofmicrobes.ddnss.org:8086"
ORG = "com.microbes"

#### Attribute functionality
def attribute_segmentation(overlay: Overlay, segmentation_processor=None):
    # pylint: disable=broad-except
    try:
        user = os.environ.get(
            "JUPYTERHUB_USER", os.environ.get("USER", os.environ.get("USERNAME"))
        )
        bucket = "segmentation"

        # initialize client from environment properties
        with InfluxDBClient(url=URL, token=TOKEN) as client:
            # setup write api
            write_api = client.write_api(write_options=SYNCHRONOUS)

            # get current time
            now = datetime.now(timezone.utc)

            point = Point("segmentation")

            point.tag("user", user)
            if segmentation_processor is not None:
                point.tag("method", segmentation_processor.__class__)

            # add the count field
            point.field("num_cells", len(overlay))
            point.field("num_images", len(overlay.frames()))

            # set the time
            point.time(now, WritePrecision.S)

            # write (will already be batched)
            write_api.write(bucket=bucket, record=point, org=ORG)
    except Exception as e:
        logger.exception(e)


def attribute_tracking(
    tracking_ov: Overlay,
    tracklet_graph: nx.DiGraph,
    tracking_graph: nx.DiGraph,
    tracker=None,
):
    # pylint: disable=broad-except
    try:
        user = os.environ.get(
            "JUPYTERHUB_USER", os.environ.get("USER", os.environ.get("USERNAME"))
        )
        bucket = "tracking"

        # initialize client from environment properties
        with InfluxDBClient(url=URL, token=TOKEN) as client:
            # setup write api
            write_api = client.write_api(write_options=SYNCHRONOUS)

            # get current time
            now = datetime.now(timezone.utc)

            point = Point("tracking")

            point.tag("user", user)
            if tracker is not None:
                point.tag("method", tracker.__class__)

            # add the count field
            point.field("num_cells", len(tracking_ov))
            point.field("tracking_nodes", tracking_graph.number_of_nodes())
            point.field("tracking_edges", tracking_graph.number_of_edges())
            if tracklet_graph is not None:
                point.field("tracklets_nodes", tracklet_graph.number_of_nodes())
                point.field("tracklets_edges", tracklet_graph.number_of_edges())
            point.field("num_images", len(tracking_ov.frames()))

            # set the time
            point.time(now, WritePrecision.S)

            # write (will already be batched)
            write_api.write(bucket=bucket, record=point, org=ORG)
    except Exception as e:
        logger.exception(e)
