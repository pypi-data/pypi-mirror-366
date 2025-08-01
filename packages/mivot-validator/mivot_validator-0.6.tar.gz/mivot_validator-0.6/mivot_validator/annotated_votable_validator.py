"""
Created on 2022/07/01

@author: laurentmichel
"""

import os
import ssl
from lxml import etree
from mivot_validator.xml_validator import XMLValidator
from mivot_validator import logger

ssl._create_default_https_context = ssl._create_unverified_context


class AnnotatedVOTableValidator:
    """
    Validate tool for annotated VOTable
    Operate 2 separate validations
    - One for the VOTable
    - One for the MIVOT annotations

    See the mivot_launcher to get how to use it
    """

    # VOtable schema
    # MIVOT schema
    votable_validator = None
    defaut_votable_schema = "http://www.ivoa.net/xml/VOTable/v1.3"
    vodml_validator = XMLValidator("https://ivoa.net/xml/MIVOT/mivot-v1.xsd")

    def validate(self, data_path):
        """
        Validate the content of data_path.
        If data_path is a directory, all its direct content is evaluated and
        the method returns false at the first XML file not validating
        :param data_path: file or directory path to be evaluated
        :type data_path: string
        :return: true all files validate
        :rtype: boolean
        """

        # Check that the path exist
        if os.path.exists(data_path) is False:
            logger.error(f"Path {data_path} does not exist")
            return False

        # Process the whole directory content
        if os.path.isdir(data_path):
            files = os.listdir(data_path)
            for sample_file in files:
                file_path = os.path.join(data_path, sample_file)
                if os.path.isdir(file_path):
                    continue
                if self.__is_xml(file_path) is True:
                    if self.__validate_file(file_path) is False:
                        return False
            return True

        # Process one single
        return self.__validate_file(data_path)

    def _set_votable_validator(self, data_path):
        """
        Look for the schema URL within the XML header.
        If not found take the 1.3 XSD (default)
        Build the validator instance from the schema
        """
        XMLSchemaNamespace = "{http://www.w3.org/2001/XMLSchema-instance}"
        document = etree.parse(data_path).getroot()
        schemaLink = document.get(XMLSchemaNamespace + "schemaLocation")
        if schemaLink is None:
            schemaLink = document.get(XMLSchemaNamespace + "noNamespaceSchemaLocation")
        if schemaLink:
            self.defaut_votable_schema = schemaLink.split(" ")[-1]
            logger.info(f"Validate against {schemaLink.split(' ')[-1]}")
        else:
            logger.info(f"Validate against {self.defaut_votable_schema}")

        AnnotatedVOTableValidator.votable_validator = XMLValidator(
            self.defaut_votable_schema
        )

    def __validate_file(self, file_path):
        """
        Validate one XML file.
        2 step validation : VOTable first and then MIVOT
        :param file_path: file to be evaluated
        :type file_path: string
        :return: true all files validate
        :rtype: boolean
        """

        # non XML files are considered as non valid
        if self.__is_xml(file_path) is False:
            logger.error(f"File {file_path} does not look like XML")
            return False

        # Get the filename for the log messages
        file_name = os.path.basename(file_path)
        logger.info(f"Validate file {file_name}")
        self._set_votable_validator(file_path)
        # Validate the VOTable
        if (
            AnnotatedVOTableValidator.votable_validator.validate_file(
                file_path, verbose=False
            )
            is False
        ):
            AnnotatedVOTableValidator.votable_validator.validate_file(
                file_path, verbose=True
            )
            logger.error("Not a valid VOTable")
            return False
        logger.info("- passed")
        # and then validate the annotations
        logger.info("- Validate against MIVOT")
        retour = self.validate_mivot(file_path)
        if retour is True:
            logger.info("- passed")
            logger.info(f"{file_name} is a valid annotated VOTable")
        return retour

    def validate_mivot(self, file_path):
        """
        Validate MIVOT block in one XML file.
        :param file_path: file to be evaluated
        :type file_path: string
        :return: true all files validate
        :rtype: boolean
        """
        # non XML files are considered as non valid
        if self.__is_xml(file_path) is False:
            logger.error(f"File {file_path} does not look like XML")
            return False
        if (
            AnnotatedVOTableValidator.vodml_validator.validate_file(
                file_path, verbose=False
            )
            is False
        ):
            AnnotatedVOTableValidator.vodml_validator.validate_file(
                file_path, verbose=True
            )
            logger.error("MIVOT annotations are not valid")
            return False
        return True

    def __is_xml(self, file_path):
        """
        :param file_path: file path ot be evaluated
        :type file_path: string
        :return: true if file_path is an XML file (test based on the prolog)
        :rtype: boolean
        """
        try:
            with open(file_path) as unknown_file:
                prolog = unknown_file.read(45)
                return prolog.startswith("<?xml") is True
        except Exception:
            pass
        return False
