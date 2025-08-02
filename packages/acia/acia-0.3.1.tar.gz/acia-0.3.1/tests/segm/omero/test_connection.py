import unittest

from acia.segm.omero.storer import OmeroSequenceSource
import time

class TestIndexing(unittest.TestCase):
    """Test the linearization of z and t stacks"""

    def test_conn_loss(self):
        iss = OmeroSequenceSource(978, username="jseiffarth", password="jseiffarth", serverUrl="localhost")

        image = next(iter(iss))

        time.sleep(15*60)
        #iss.conn.close()

        other_image = next(iter(iss))

if __name__ == "__main__":
    unittest.main()
