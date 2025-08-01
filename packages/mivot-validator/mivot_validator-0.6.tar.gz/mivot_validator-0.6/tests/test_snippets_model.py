"""
Testing generations of generic snippets from a VODML-Model file

Created on 9 May 2023
@author: julien abid
"""

import unittest
import os

from mivot_validator.utils.xml_utils import XmlUtils
from mivot_validator.instance_checking.model_snippets_builder import ModelBuilder
from mivot_validator.utils.session import Session

MODELS = ["coords", "meas", "Phot"]
MAPPING_SAMPLE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")

def get_model_path(model):
    mod_dir = os.path.dirname(__file__)
    vodml_dir = os.path.realpath(
        os.path.join(mod_dir, "..", "mivot_validator", "instance_checking", "vodml"))
    if model == "coords":
        return "file://" + os.path.join(vodml_dir, "Coords-v1.0.vo-dml.xml")
    elif model == "meas":
        return "file://" + os.path.join(vodml_dir, "Meas-v1.vo-dml.xml")
    elif model == "Phot":
        return "file://" +  os.path.join(vodml_dir, "Phot-v1.1.vodml.xml")
    
def getObjectTypes(model):
    """
    Get the object types of the given model which are not abstract
    """
    res = []

    for ele in model.xpath(f".//objectType"):
        if ele.get("abstract") == "true":
            continue
        for tags in ele.getchildren():
            if tags.tag == "vodml-id":
                res.append(tags.text)
    return res


def getDataTypes(model):
    """
    Get the data types of the given model which are not abstract
    """
    res = []

    for ele in model.xpath(f".//dataType"):
        if ele.get("abstract") == "true":
            continue
        for tags in ele.getchildren():
            if tags.tag == "vodml-id":
                res.append(tags.text)
    return res


class Test(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        if os.path.exists("../xml_interpreter/tmp_vodml"):
            os.system("rm -rf " + "../xml_interpreter/tmp_vodml")

    def testFilesExists(self):
        """
        Check that files are generated in the given directory
        """

        for model_name in MODELS:
            session = Session()
            # Given
            snippets = ModelBuilder(get_model_path(model_name), session)

            # When
            snippets.build()

            # Then
            self.assertTrue(
                len(os.listdir(session.tmp_data_path + "/" + model_name)) > 0,
                f"Snippets for model {model_name} should be generated",
            )

    def testFilesCohesion(self):
        """
        Check that files generated in the given directory
        are the object types and data types of the model
        """
        return
        for model_name in MODELS:
            # Given
            session = Session()

            snippets = ModelBuilder(model_name, session)
            object_types = getObjectTypes(
                XmlUtils.xmltree_from_file(session.get_vodml(model_name))
            )
            data_types = getDataTypes(
                XmlUtils.xmltree_from_file(session.get_vodml(model_name))
            )

            # When
            snippets.build()

            # Then
            for obj in object_types:
                print(
                    session.tmp_data_path
                    + "/"
                    + model_name
                    + "/"
                    + model_name
                    + "."
                    + obj
                    + ".xml"
                )
                self.assertTrue(
                    os.path.exists(
                        session.tmp_data_path
                        + "/"
                        + model_name
                        + "/"
                        + model_name
                        + "."
                        + obj
                        + ".xml"
                    )
                )
            for data in data_types:
                self.assertTrue(
                    os.path.exists(
                        session.tmp_data_path
                        + "/"
                        + model_name
                        + "/"
                        + model_name
                        + "."
                        + data
                        + ".xml"
                    )
                )


if __name__ == "__main__":
    unittest.main()
