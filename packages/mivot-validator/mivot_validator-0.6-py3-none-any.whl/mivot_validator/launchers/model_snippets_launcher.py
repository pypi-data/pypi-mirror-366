"""
Created on 19 Apr 2023

generate for a given model all  non-abstract object
and data types (one per snippet)
.
@author: julien abid
"""

import os
import sys

from urllib.parse import urlparse
from urllib.request import urlretrieve

from mivot_validator.instance_checking.model_snippets_builder import (
    ModelBuilder
    )
from mivot_validator.utils.session import Session


def main():
    """
    Package launcher (script)
    """
    if len(sys.argv) < 2:
        print("USAGE: mivot-snippet-model [url] <output_dir>")
        print("   Create MIVOT snippets from VODML files")
        print("   url: url of any VODML-Model (must be prefixed with file:// in case of local file)")
        print(
            "   output_dir: path to the chosen output directory"
            "(session working directory by default)"
        )
        print("   exit status: 0 in case of success, 1 otherwise")
        sys.exit(1)

    session = Session()

    # if output is not absolute use the default session work dir
    if len(sys.argv) >= 2 and os.path.isdir(sys.argv[2]):            
        output_dir = os.path.abspath(sys.argv[2])
        session.tmp_data_path = output_dir

    vodml_path = check_args(sys.argv[1])
    try:
        snippet = ModelBuilder(vodml_path, session)
    except Exception:
        sys.exit(1)
        
    if snippet.build():
        folder = os.path.basename(
            sys.argv[1]
            ).split('.')[0].split('_')[0].split('-')[0].lower()
        print("\n===============================================")
        print(
            f"Snippets generated in "
            f"{session.tmp_data_path} \n in the folder : "
            f"{folder}"
        )
        print("===============================================\n")

        if os.path.isdir("tmp_vodml"):
            os.system("rm -rf tmp_vodml")

        sys.exit(0)


def check_args(args):
    """
    Check if the path is a file or an url and download the file if needed
    :args: path or link
    :return: local path
    """
    local_vodml_path = args
    if not urlparse(args).scheme:
        temp_dir = "tmp_vodml"
        os.makedirs(temp_dir, exist_ok=True)
        local_vodml_path = os.path.join(temp_dir, os.path.basename(args))
        urlretrieve(args, local_vodml_path)

    return local_vodml_path


if __name__ == "__main__":
    main()
