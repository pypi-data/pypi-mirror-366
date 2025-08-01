"""
Created on 2022/09

Test suite validating that all role and types of the annotation are consistent with the model they refer to.

@author: laurentmichel
"""

import os
import unittest
from mivot_validator.utils.session import Session
from mivot_validator.dmtypes_and_role_checker import DmTypesAndRolesChecker

mapping_sample = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")


class Test(unittest.TestCase):

    def testOK(self):
        """
        Check that all sample files tagged as OK are actually valid
        """
        session = Session()
        types_and_role_checker = DmTypesAndRolesChecker(session)
        file_path = os.path.join(mapping_sample, "test_dmtypes_and_roles_ok.xml")
        self.assertTrue(types_and_role_checker.validate(file_path))
        session.close()

    def testKO(self):
        """
        Check that all sample files tagged as OK are actually valid
        """
        session = Session()
        types_and_role_checker = DmTypesAndRolesChecker(session)
        file_path = os.path.join(mapping_sample, "test_dmtypes_and_roles_ko.xml")
        self.assertFalse(types_and_role_checker.validate(file_path))
        self.assertListEqual(
            types_and_role_checker.messages, ["unknown dmrole meas:Measure.coord"]
        )
        session.close()


if __name__ == "__main__":
    unittest.main()
