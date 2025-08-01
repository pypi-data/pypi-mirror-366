"""
Manage a temporary working area

Must be used as a singleton : On session per process

my_session = Session.session()

Created on 23 May 2024

@author: laurentmichel
"""

import os
import tempfile
import urllib.request
import shutil
from mivot_validator import logger


class Session(object):
    """
    classdocs
    """

    SNIPPET = "tmp_snippets"
    VODML = "vodml"

    def __init__(self):
        """
        Constructor
        """
        self.tmp_data_path = None
        self.vodml_default_path = None
        self.vodml_path = None

        self.tmp_dirname = tempfile.mkdtemp()
        self.tmp_data_path = os.path.join(self.tmp_dirname, Session.SNIPPET)
        os.mkdir(self.tmp_data_path)

        self.vodml_path = os.path.join(self.tmp_dirname, Session.VODML)
        os.mkdir(self.vodml_path)

        self.vodml_default_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "..",
            "instance_checking",
            Session.VODML,
        )

        self.install_vodml(
            "coords",
            "https://ivoa.net/xml/VODML/Coords-v1.0.vo-dml.xml"
        )
        self.install_vodml("meas",
                           "https://ivoa.net/xml/VODML/Meas-v1.vo-dml.xml")
        self.install_vodml(
            "ivoa",
            "https://ivoa.net/xml/VODML/20180519/IVOA-v1.0.vo-dml.xml"
        )
        self.install_vodml(
            "Phot",
            "https://ivoa.net/xml/VODML/Phot-v1.vodml.xml"
            )

        logger.info(
            f"setup session in {self.tmp_dirname} ({os.getpid()})"
            )

    def _is_model_here(self, model_name):
        """
        return True if model_name is already installed
        """
        return os.path.isfile(self._get_model_path(model_name))

    def _get_model_path(self, model_name):
        """
        return the full path of the vodml file of the model model_name
        """
        return os.path.join(self.vodml_path, f"{model_name}.vo-dml.xml")

    def install_vodml(self, model_name, url, force=False):
        """
        Install the model model_name from the give, url or
        from the vodml files located in the package in case of failure
        """

        if self._is_model_here(model_name) and not force:
            logger.info(f"{model_name} already here")
            return True

        if not url:
            logger.info(f"no url given install local {model_name}")
            return self.install_local_vodml(model_name)
        try:
            logger.info(f"fetching {model_name} at {url}")

            urllib.request.urlretrieve(url, self._get_model_path(model_name))
            return True
        except Exception as exception:
            logger.error(f"error fetching URL {url}")
            logger.error(f"{exception}")
            raise FileNotFoundError from exception
            return False

    def install_local_vodml(self, model_name):
        """
        Install the model model_name from the vodml files
        located in the package
        """
        if self._is_model_here(model_name):
            logger.info(f"{model_name} already here")
            return True

        local_models = os.listdir(self.vodml_default_path)
        for model in local_models:
            if model.startswith(model_name) and model.endswith("vo-dml.xml"):
                logger.info(f"use local {model} for model {model_name}")
                shutil.copyfile(
                    os.path.join(self.vodml_default_path, model),
                    self._get_model_path(model_name),
                )

                return True
        logger.info(f"no local model found for {model_name}")
        return False

    def get_vodml(self, model_name):
        """
        Return the full path of the requested model
        or None in case of failure
        """
        if self._is_model_here(model_name):
            return self._get_model_path(model_name)
        return None

    def clean_tmp_data_dir(self):
        """
        Remove all xml files from the tempo directory
        """
        for filename in os.listdir(self.tmp_data_path):
            file_path = os.path.join(self.tmp_data_path, filename)
            if filename.endswith(".xml") and os.path.isfile(file_path):
                os.unlink(file_path)

    def close(self):
        """
        remove all session stuff
        """
        logger.info(f"Clear session {self.tmp_dirname} ({os.getpid()})")
        shutil.rmtree(self.tmp_dirname)
