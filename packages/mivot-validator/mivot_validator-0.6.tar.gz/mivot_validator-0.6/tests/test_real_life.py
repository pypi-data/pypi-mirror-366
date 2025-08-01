"""
Created on 2023/03

Test suite validating the whole votables against both schema (VOTable MIVOT)
and the model compliance

@author: laurentmichel
"""

import os, sys
import unittest
import pytest
from astropy.io.votable import parse
from mivot_validator.utils.session import Session
from mivot_validator.annotated_votable_validator import AnnotatedVOTableValidator
from mivot_validator.instance_checking.xml_interpreter.model_viewer import ModelViewer
from mivot_validator.instance_checking.instance_checker import InstanceChecker

mapping_sample = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")


class Test(unittest.TestCase):
    @pytest.mark.skip(reason="Need Mango to be stable")    
    def test6paramOK(self):
        """
        Check that all sample files tagged as OK are actually valid
        """
        votables = ["gaia_with_mivot.xml", "xtapdb.xml"]
        annotated_votable_validator = AnnotatedVOTableValidator()
        for votable in votables:
            file_path = os.path.join(mapping_sample, votable)
            self.assertTrue(annotated_votable_validator.validate(file_path))
            votable = parse(file_path)

            mviewer = None
            for resource in votable.resources:
                session = Session()
                if len(votable.resources) != 1:
                    print(
                        "VOTable with more than one resource are not supported yet"
                    )
                    sys.exit(1)

                mviewer = ModelViewer(resource, votable_path=file_path)
                for key, value in mviewer.get_declared_models().items():
                    session.install_vodml(key, value)

                mviewer.connect_table(None)
                # Seek the first data row
                mviewer.get_next_row()
                # and get its model view
                # The references are resolved in order to be able to check their counterparts
                model_view = mviewer.get_model_view(resolve_ref=True)
                # empty the snippet cache

                # Validate all instances  on which the table data are mapped
                for instance in model_view.xpath(".//INSTANCE"):
                    print(f'CHECKING: instance {instance.get("dmtype")}')
                    InstanceChecker.check_instance_validity(instance, session)

 
if __name__ == "__main__":
    unittest.main()
