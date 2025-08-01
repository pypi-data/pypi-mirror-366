"""
Created on 22 Feb 2023

Test suite validating that the object instances resulting from the annotation parsing 
are compliant with their VODML class definitions

@author: laurentmichel
"""

import os
import unittest
from mivot_validator.utils.session import Session
from mivot_validator.utils.xml_utils import XmlUtils
from mivot_validator.utils.dict_utils import DictUtils
from mivot_validator.instance_checking.snippet_builder import Builder

if __name__ == "__main__":

           
    session = Session()
    session.install_local_vodml("mango")
    vodml_filename = session.get_vodml("mango")
    builder = Builder(
        "mango",
        "EpochPosition",
                # "Property",
        session,
    )
            # build the XML snippet and store it on disk
    builder.build()
    print(builder.outputname)
    XmlUtils.pretty_print(XmlUtils.xmltree_from_file(builder.outputname))
