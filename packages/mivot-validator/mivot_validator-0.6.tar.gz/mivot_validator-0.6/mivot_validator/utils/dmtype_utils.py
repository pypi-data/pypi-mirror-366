"""
Created on 20 Jun 2024

@author: laurentmichel
"""


class DmtypeUtils(object):
    """
    classdocs
    """

    @staticmethod
    def split_dmtype(dmtype):
        """
        return the model, type tuples extracted from dmtype
        """
        elements = dmtype.split(":")
        if len(elements) == 2:
            return elements[0], elements[1]
        else:
            return None, elements[0]

    @staticmethod
    def get_snippet_name(dmtype):
        """
        return a standard name for the dmtype snipper
        """
        return f"{dmtype.replace(':', '.')}.xml"
