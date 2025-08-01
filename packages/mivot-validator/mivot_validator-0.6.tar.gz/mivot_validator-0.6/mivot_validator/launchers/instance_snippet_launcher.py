"""
Created on 21 Apr 2023

launcher script for the instance snippet generator package
Concrete classes can be given as parameters of by interactive user input

@author: julien abid
"""

import os.path
import sys
import argparse
from mivot_validator.utils.session import Session
from mivot_validator.instance_checking.instance_snippet_builder import (
    InstanceSnippetBuilder,
)

CONSTRAINTS = None


def check_concrete_classes(args, parser=None):
    """
    Check the validity of the concrete class list
    """
    if args is None:
        return None

    for my_dict in args:
        if not all(
            x in my_dict.keys() for x in [
                "dmtype",
                "dmrole",
                "context",
                "class"
                ]
        ):
            print("Invalid format for class name")
            if parser is not None:
                parser.print_help()
            sys.exit(1)
    return args


def main():
    """
    Package launcher (script)
    """

    parser = argparse.ArgumentParser(
        description="Create MIVOT snippet for a model instance "
    )
    parser.add_argument(
        "vodml_id",
        metavar="vodml_id",
        type=str,
        nargs="?",
        help="Vodml_id of the class for which we want a snippet.",
    )
    parser.add_argument(
        "output",
        metavar="output",
        type=str,
        nargs="?",
        help="output file: absolute path or simple file name",
    )

    parser.add_argument(
        "-cc",
        "--concrete-class",
        metavar="classes_list",
        type=lambda x: dict((i.split("=") for i in x.split(","))),
        nargs="?",
        action="append",
        help="[OPTIONAL] list of classes to be included in the snippet, "
        "it will prevent the script to ask for the user input if given.\n"
        "Syntax is : dmrole=model:Type.role,"
        "context=model:ParentType,dmtype=model:Type,context:"
        "model:hostClass,class=model:Type",
    )

    args = vars(parser.parse_args())
    session = Session()

    if args["output"] is None or args["class_name"] is None:
        parser.print_help()
        sys.exit(1)

    # id output is not absolute use the default session work dir
    if os.path.isabs(args["output"]):
        output_dir = os.path.dirname(args["output"])
        session.tmp_data_path = output_dir
    output_file = os.path.basename(args["output"])

    vodml_id = args["vodml_id"]

    classes_list = check_concrete_classes(args["concrete_class"], parser)

    snippet = InstanceSnippetBuilder(
        vodml_id, output_file, session, concrete_list=classes_list
    )
    snippet.build()
    snippet.output_result()


if __name__ == "__main__":
    main()
