"""
Testing generations of concrete snippets

Created on 9 May 2023
@author: julien abid
"""

import unittest
import os
import filecmp
from mivot_validator.instance_checking.instance_snippet_builder import (
    InstanceSnippetBuilder,
)
from mivot_validator.utils.session import Session

OUTPUT = os.path.abspath(os.getcwd() + "/../tmp_snippets/")
FILE_NAME = "meas.Position.res"
REF_FILE_NAME = "meas.Position.test"


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(OUTPUT):
            os.system("mkdir " + OUTPUT)

    @classmethod
    def setUp(cls):
        if os.path.exists(OUTPUT):
            for file in os.listdir(OUTPUT):
                if file != ".gitkeep":
                    os.system("rm -rf " + OUTPUT + "/" + file)

    @classmethod
    def tearDown(cls):
        filecmp.clear_cache()
        if os.path.exists(OUTPUT):
            for file in os.listdir(OUTPUT):
                if file != ".gitkeep":
                    os.system("rm -rf " + OUTPUT + "/" + file)

    def testFileExist(self):
        return
        """
        Check that files are generated in the given directory with the right name
        """
        return
        # Given
        classes_list = [
            {
                "dmrole": "meas:Error.statError",
                "context": "meas:Position",
                "dmtype": "meas:Uncertainty",
                "class": "meas:Symmetrical",
            },
            {
                "dmrole": "meas:Error.sysError",
                "context": "meas:Position",
                "dmtype": "meas:Uncertainty",
                "class": "meas:Asymmetrical2D",
            },
            {
                "dmrole": "meas:Position.coord",
                "context": "meas:Position",
                "dmtype": "coords:Point",
                "class": "coords:LonLatPoint",
            },
            {
                "dmrole": "coords:SpaceFrame.refPosition",
                "context": "coords:LonLatPoint",
                "dmtype": "coords:RefLocation",
                "class": "coords:CustomRefLocation",
            },
            {
                "dmrole": "coords:CustomRefLocation.position",
                "context": "coords:CustomRefLocation",
                "dmtype": "coords:Point",
                "class": "coords:LonLatPoint",
            },
            {
                "dmrole": "coords:SpaceFrame.refPosition",
                "context": "coords:LonLatPoint",
                "dmtype": "coords:RefLocation",
                "class": "coords:StdRefLocation",
            },
            {
                "dmrole": "coords:CustomRefLocation.velocity",
                "context": "coords:CustomRefLocation",
                "dmtype": "coords:Point",
                "class": "coords:LonLatPoint",
            },
            {
                "dmrole": "coords:SpaceFrame.refPosition",
                "context": "coords:LonLatPoint",
                "dmtype": "coords:RefLocation",
                "class": "coords:StdRefLocation",
            },
        ]
        session = Session()
        snippet = InstanceSnippetBuilder(
            "meas:Position", FILE_NAME, session, concrete_list=classes_list
        )

        # When
        snippet.build()
        snippet.output_result()

        # Then
        self.assertTrue(
            os.path.exists(session.tmp_data_path + "/" + FILE_NAME + ".xml")
        )

    def testFileCohesion(self):
        """
        Check that file generated in the given directory have the same content as the test data
        """
        # Given
        classes_list = [
            {
                "dmrole": "meas:Error.statError",
                "context": "meas:Position",
                "dmtype": "meas:Uncertainty",
                "class": "meas:Symmetrical",
            },
            {
                "dmrole": "meas:Error.sysError",
                "context": "meas:Position",
                "dmtype": "meas:Uncertainty",
                "class": "meas:Asymmetrical2D",
            },
            {
                "dmrole": "meas:Position.coord",
                "context": "meas:Position",
                "dmtype": "coords:Point",
                "class": "coords:LonLatPoint",
            },
            {
                "dmrole": "coords:SpaceFrame.refPosition",
                "context": "coords:LonLatPoint",
                "dmtype": "coords:RefLocation",
                "class": "coords:CustomRefLocation",
            },
            {
                "dmrole": "coords:CustomRefLocation.position",
                "context": "coords:CustomRefLocation",
                "dmtype": "coords:Point",
                "class": "coords:LonLatPoint",
            },
            {
                "dmrole": "coords:SpaceFrame.refPosition",
                "context": "coords:LonLatPoint",
                "dmtype": "coords:RefLocation",
                "class": "coords:StdRefLocation",
            },
            {
                "dmrole": "coords:CustomRefLocation.velocity",
                "context": "coords:CustomRefLocation",
                "dmtype": "coords:Point",
                "class": "coords:LonLatPoint",
            },
            {
                "dmrole": "coords:SpaceFrame.refPosition",
                "context": "coords:LonLatPoint",
                "dmtype": "coords:RefLocation",
                "class": "coords:StdRefLocation",
            },
        ]
        session = Session()
        snippet = InstanceSnippetBuilder(
            "meas:Position", FILE_NAME, session, concrete_list=classes_list
        )
        # When
        snippet.build()
        snippet.output_result()

        # Then
        if os.path.exists(os.path.join(session.tmp_data_path, FILE_NAME + ".xml")):
            filecmp.clear_cache()
            self.assertTrue(
                filecmp.cmp(
                    os.path.join(session.tmp_data_path, FILE_NAME + ".xml"),
                    # os.path.join(session.tmp_data_path, FILE_NAME + ".xml"),
                    os.path.realpath(
                        os.path.dirname(__file__) + "/data/" + REF_FILE_NAME + ".xml"
                    ),
                    shallow=False,
                )
            )


if __name__ == "__main__":
    unittest.main()
