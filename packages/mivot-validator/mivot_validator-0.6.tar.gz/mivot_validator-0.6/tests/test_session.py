"""
Created on 2024/05


@author: laurentmichel
"""

import os
import unittest
from mivot_validator.utils.session import Session

mapping_sample = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")


class TestSession(unittest.TestCase):

    def testLocal(self):
        session = Session()

        self.assertTrue(session.install_local_vodml("Meas"))

        fpath = session.get_vodml("Meas")
        self.assertTrue(fpath.endswith("Meas.vo-dml.xml"))
        self.assertIsNone(session.get_vodml("XXX"))
        session.close()

    def testRemote(self):
        session = Session()
        self.assertFalse(session.install_vodml("Model", None))

        self.assertTrue(session.install_vodml("ModelURL", "https://www.google.com"))
        fpath = session.get_vodml("ModelURL")
        self.assertTrue(fpath.endswith("ModelURL.vo-dml.xml"))

        with self.assertRaises(Exception): 
            session.install_vodml("ModelNOURL", "https://,,,,,,.com")
            
        self.assertIsNone(session.get_vodml("ModelNOURL"))

        self.assertTrue(
            session.install_vodml(
                "Provenance",
                "https://ivoa.net/xml/VODML/20191125/Provenance-v1.vo-dml.xml",
            )
        )
        fpath = session.get_vodml("Provenance")
        self.assertTrue(fpath.endswith("Provenance.vo-dml.xml"))


if __name__ == "__main__":
    unittest.main()
