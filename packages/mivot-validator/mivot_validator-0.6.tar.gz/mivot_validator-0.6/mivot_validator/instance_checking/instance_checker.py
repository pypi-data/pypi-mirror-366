"""
Created on 21 Feb 2023

@author: laurentmichel
"""

import os

from mivot_validator.utils.xml_utils import XmlUtils
from mivot_validator.utils.dmtype_utils import DmtypeUtils
from mivot_validator.instance_checking.inheritance_checker import InheritanceChecker
from mivot_validator.instance_checking.snippet_builder import Builder

# types to be ignored for now
inheritence_tree = {}
ivoa_types = ["ivoa:RealQuantity", "ivoa:IntQuantity"]


class CheckFailedException(Exception):
    pass

def raise_check_failed_exception(message, tree_element):
    """
    Parameters
    ----------
    message: string
        Exception message
    tree_element: Element (XML)
        XML element where the error occured
    """
    if tree_element is not None:
        XmlUtils.pretty_print(tree_element)
    raise CheckFailedException(message)

class InstanceChecker:
    """
    API operating the validation of mapped instances against the VODML definition

    - all ATTRIBUTE/COLLECTION/INSTANCE children of the mapped instance must be
      referenced in the VODML with the same dmrole and the same dmtype.
    - The dmtype checking takes into account the inheritance
    - The mapped instances must not necessary host all the components declared in the VODML
    - All the components hosted by the mapped instances must be compliant with the VODML

    The VODML files are stored locally for the moment
    """

    inheritence_tree = {}

    @staticmethod
    def _get_vodml_class_tree(model, dmtype, session):
        """
        Extract from the VODML file the object to be checked
        Store first on disk a VODML representation of the searched object type
        and then works with that XML snippet

        parameters
        ----------
        model: string
            model short name as defined by the VODML
        dmtype: string
            type of the model component to be checked

        return
        ------
        The etree serialisation of the XML snippet
        """
        filepath = os.path.join(session.tmp_data_path, f"{model}:{dmtype}")
        filepath = filepath.replace(":", ".") + ".xml"

        if os.path.exists(filepath) is False:
            print(f"-> build snippet for class {model}:{dmtype}")

            vodml_filename = session.get_vodml(model)
            builder = Builder(
                model,
                dmtype,
                # "Property",
                session,
            )
            # build the XML snippet and store it on disk
            builder.build()
            InstanceChecker._build_inheritence_graph(vodml_filename)
        else:
            print(f"-> snippet for class {dmtype} already in the cache")

        return XmlUtils.xmltree_from_file(filepath)

    @staticmethod
    def _get_vodmlid(vodmlid, model_name):
        if ":" in vodmlid:
            return f"{vodmlid}"
        return f"{model_name}:{vodmlid}"

    @staticmethod
    def _build_inheritence_graph(vodml_filepath):
        """
        Build a map of the inheritance links.
        This is necessary to resolve cases where the model refer to abstract types
        and the annotation uses concrete types (sub-types)
        """
        vodml_tree = XmlUtils.xmltree_from_file(vodml_filepath)
        graph = {}
        for ele in vodml_tree.xpath("./name"):
            model_name = ele.text
        print(f"   Build inheritence tree for model {model_name}")

        # Build a map superclass : [sublcasses]
        # No distinctions between objecttypeand datatypes
        # MIVOT does not make any difference
        # the vodml)id are unique within the scope of the whole model
        for ele in vodml_tree.xpath(".//primitiveType"):
            for tags in ele.getchildren():
                if tags.tag == "vodml-id":
                    sub_class = model_name + ":" + tags.text
                for ext in ele.xpath("./extends/vodml-ref"):
                    super_class = ext.text
                    if super_class not in graph:
                        graph[super_class] = []
                    if sub_class not in graph[super_class]:
                        graph[super_class].append(sub_class)
        print(graph)
        for ele in vodml_tree.xpath(".//dataType"):
            for tags in ele.getchildren():
                if tags.tag == "vodml-id":
                    sub_class = model_name + ":" + tags.text
                for ext in ele.xpath("./extends/vodml-ref"):
                    super_class = ext.text
                    if super_class not in graph:
                        graph[super_class] = []
                    if sub_class not in graph[super_class]:
                        graph[super_class].append(sub_class)

        for ele in vodml_tree.xpath(".//objectType"):
            for tags in ele.getchildren():
                if tags.tag == "vodml-id":
                    sub_class = model_name + ":" + tags.text
                for ext in ele.xpath("./extends/vodml-ref"):
                    super_class = ext.text
                    if super_class not in graph:
                        graph[super_class] = []
                    if sub_class not in graph[super_class]:
                        graph[super_class].append(sub_class)
        #
        # We have inheritance with multiple levels (A->B->C)
        # In such a case we must consider (in term of validation) that C extends A as well
        # This the purpose of the code below.
        # {A: [B, C, D]  C:[X, Y]} --> {A: [B, C, D, X, Y],  C:[X, Y]}
        deep_tree = {}
        for superclass, subclasses in graph.items():
            for subclass in subclasses:
                if subclass in graph:
                    if superclass not in deep_tree:
                        deep_tree[superclass] = []
                    for sc in graph[subclass]:
                        if sc not in deep_tree[superclass]:
                            deep_tree[superclass].append(sc)

        for key in deep_tree:
            for val in deep_tree[key]:
                if val not in graph[key]:
                    graph[key].append(val)
        for key in graph:
            if key not in InstanceChecker.inheritence_tree:
                InstanceChecker.inheritence_tree[key] = graph[key]
            else:
                InstanceChecker.inheritence_tree[key] = (
                    InstanceChecker.inheritence_tree[key] + graph[key]
                )
        # ivoa model is not parsed yet....
        if "ivoa:Quantity" not in InstanceChecker.inheritence_tree:
            InstanceChecker.inheritence_tree["ivoa:Quantity"] = ivoa_types
        # Cross model inheritance not supported yet
        if "meas:Measure" in InstanceChecker.inheritence_tree:
            InstanceChecker.inheritence_tree["meas:Measure"].append(
                "mango:extmeas.PhotometricMeasure"
            )

        return graph

    @staticmethod
    def _check_attribute(attribute_etree, vodml_instance):
        """
        checks that the MIVOT representation of the attribute matches the model definition

        parameters
        ----------
        attribute_etree: etree
            MIVOT representation of the attribute
        vodml_instance: etree
            VODML serialization of that attribute
        return
        ------
            boolean
        """
        for child in vodml_instance.xpath("./ATTRIBUTE"):
            print("### " +  child.get("dmrole"), " ",  child.get("dmtype"))
            
                        
            checker = InheritanceChecker(InstanceChecker.inheritence_tree)
                        
            if child.get("dmrole") == attribute_etree.get("dmrole") and checker.inherits_from(
                attribute_etree.get("dmtype"), child.get("dmtype")):
                return True
            model1, class1 = DmtypeUtils.split_dmtype(
                child.get("dmtype")
                )
            model2, class2 = DmtypeUtils.split_dmtype(
                attribute_etree.get("dmtype")
                )
            if model1 != model2 and class1 == class2:
                return True
        return False

    @staticmethod
    def _check_collection(collection_etree, vodml_instance, session):
        """
        checks that the MIVOT representation of the collection matches the model definition

        parameters
        ----------
        collection_etree: etree
            MIVOT representation of the collection
        vodml_instance: etree
            VODML serialization of that collection
        return
        ------
            a documented  exception in case of failure
        """

        collection_role = collection_etree.get("dmrole")

        # Checks that collection items have all the same type
        item_type = ""
        for item in collection_etree.xpath("./*"):
            mivot_item_type = item.get("dmtype")
            checker = InheritanceChecker(InstanceChecker.inheritence_tree)
            if item_type != "" and not checker.check_inheritance(
                mivot_item_type, item_type
            ):
                raise_check_failed_exception(
                    f"Collection with dmrole={collection_role} has items with different dmtypes {mivot_item_type} {item_type}",
                    collection_etree
                )
            item_type = mivot_item_type

        # check that the mapped collection item have the type defined in the model
        role_found = False

        for vodml_child in vodml_instance.xpath("./COLLECTION"):
            print(f'{vodml_child.get("dmrole")} {collection_role}')
            if vodml_child.get("dmrole") == collection_role:
                role_found = True
                # Get the item type as defined by vodml
                vodml_type = None
                for vodml_item in vodml_child.xpath("./*"):
                    vodml_type = vodml_item.get("dmtype")
                    break
                # This occurs when the collection is empty or filled with ATTRIBUTE
                # The latest is a bug in the snippet generator
                # TODO: fix it
                if not vodml_type:
                    print(f"collection {collection_role} looks empty: no further checking")

                    return
                # Get the item type as used by mivot
                for item in collection_etree.xpath("./*"):
                    mivot_item_type = item.get("dmtype")
                    if (
                        mivot_item_type not in ivoa_types
                        and mivot_item_type != vodml_type
                        and (
                            vodml_type not in InstanceChecker.inheritence_tree
                            or mivot_item_type
                            not in InstanceChecker.inheritence_tree[vodml_type]
                        )
                    ):
                        raise_check_failed_exception(
                            f"Collection with dmrole={collection_role} "
                            f"has items with prohibited types ({mivot_item_type}) "
                            f"instead of expected {vodml_type} ",
                            item
                        )
                    for item in collection_etree.xpath("./*"):
                        if item.tag == "INSTANCE":
                            InstanceChecker.check_instance_validity(item, session)
                    return

        if role_found is False:
            raise_check_failed_exception(
                f"No collection with dmrole {collection_role} "
                f"in object type {vodml_instance.getroot().get('dmtype')}",
                collection_etree
            )

    @staticmethod
    def _check_membership(actual_instance, enclosing_vodml_instance):
        """
        Checks that the MIVOT component is a component of the VODML class

        parameters
        ----------
        actual_instance: etree
            MIVOT instance
        enclosing_vodml_instance: etree
            VODML class supposed to enclose the actual instance
        return
        -------
            a documented exception ins case of failure
        """
        actual_role = actual_instance.get("dmrole")
        for vodml_instance in enclosing_vodml_instance.getroot().xpath("./*"):
            #print(vodml_instance.get("dmrole") + " " + actual_role)
            if vodml_instance.get("dmrole") == actual_role:
                actual_type = actual_instance.get("dmtype")
                vodml_type = vodml_instance.get("dmtype")
                if actual_type == vodml_type:
                    return
                # Sort of ad_hoc patch meanwhile ivoa DM is properly supported
                if actual_type == "ivoa:RealQuantity" and vodml_type == "ivoa:Quantity":
                    return
                if vodml_type == "ivoa:datetime" and actual_type in ["mango:year", "mango:jd", "mango:mjd", "mango:iso"]:
                    return
                if (
                    vodml_type in InstanceChecker.inheritence_tree
                    and actual_type in InstanceChecker.inheritence_tree[vodml_type]
                ):
                    print(f"-> found that {actual_type} inherits from {vodml_type}")
                    return
                raise_check_failed_exception(
                    f"Object type {enclosing_vodml_instance.getroot().get('dmtype')} "
                    f"has no component with dmrole={actual_role} and dmtype={actual_type} "
                    f"type should be {vodml_type}",
                    vodml_instance
                )
        raise_check_failed_exception(
            f"dmrole {actual_role} not found in "
            f"object type {enclosing_vodml_instance.getroot().get('dmtype')}",
            actual_instance
        )

    @staticmethod
    def check_instance_validity(instance_etree, session):
        """
        Public method. The only one meant to be used from from outside
        Checks that instance_etree is compliant with the model it refers to

        parameters
        ----------
        instance_etree: etree
            MIVOT instance to be checked
        return
        -------
            a documented exception ins case of failure
        """
        checked_roles = []
        dmtype = instance_etree.get("dmtype")
        if dmtype is None:
            raise_check_failed_exception(f"Mising dmtype in \n {XmlUtils.pretty_string(instance_etree)}",
                                         instance_etree)

        eles = dmtype.split(":")
        print(f"-> check class {eles[0]}:{eles[1]}")
        if eles[0] == "ivoa":
            print("-> IVOA/ see later")
            return True

        vodml_instance = InstanceChecker._get_vodml_class_tree(
            eles[0], eles[1], session
        )

        for child in instance_etree.xpath("./*"):
            if child.tag == "ATTRIBUTE":
                InstanceChecker._check_membership(child, vodml_instance)

                dmrole = child.get("dmrole")
                if dmrole in checked_roles:
                    raise_check_failed_exception(f"Duplicated dmrole {dmrole}",
                                                 child)
                checked_roles.append(child.get("dmrole"))

                # ivao:Quantity are complex types that can be serialized as ATTRIBUTE.
                # This is an exception
                if (
                    child.get("dmtype") not in ivoa_types
                    and InstanceChecker._check_attribute(child, vodml_instance) is False
                ):
                    message = (
                        f"cannot find attribute with dmrole={dmrole} "
                        f'dmtype={child.get("dmtype")} in complex type {dmtype}'
                    )
                    raise_check_failed_exception(message,
                                                 child)
                print(
                    f'VALID: attribute with dmrole={child.get("dmrole")} '
                    f'dmtype={child.get("dmtype")} in complex type {dmtype}'
                )
            elif child.tag == "INSTANCE":
                dmrole = child.get("dmrole")
                if dmrole in checked_roles:
                    raise_check_failed_exception(f"Duplicated dmrole {dmrole} (dmtype {child.get('dmtype')})",
                                                 child)
                checked_roles.append(child.get("dmrole"))

                if InstanceChecker.check_instance_validity(child, session) is False:
                    message = (
                        f"cannot find instance with dmrole={dmrole} "
                        f'dmtype={child.get("dmtype")} in complex type {dmtype}'
                    )
                    raise_check_failed_exception(message,
                                                 child)
                InstanceChecker._check_membership(child, vodml_instance)
                print(
                    f"VALID: instance with dmrole={dmrole} "
                    f'dmtype={child.get("dmtype")} in complex type {dmtype}'
                )

            elif child.tag == "COLLECTION":
                dmrole = child.get("dmrole")
                if dmrole in checked_roles:
                    raise_check_failed_exception(f"Duplicated dmrole {dmrole}",
                                                 child)
                checked_roles.append(child.get("dmrole"))

                if (
                    InstanceChecker._check_collection(child, vodml_instance, session)
                    is False
                ):
                    message = (
                        f"cannot find collection with dmrole={dmrole} "
                        f"in complex type {dmtype}"
                    )
                    raise_check_failed_exception(message,
                                                 instance_etree)
                print(
                    f"VALID: collection with dmrole={dmrole} "
                    f"in complex type {dmtype}"
                )
            elif child.tag == "REFERENCE":
                dmrole = child.get("dmrole")
                if dmrole in checked_roles:
                    raise_check_failed_exception(f"Duplicated dmrole {dmrole}",
                                                 child)
                print(f"SKIPPED: Reference to instance with dmrole={dmrole}")

            else:
                raise_check_failed_exception(f"unsupported tag {child.tag}",
                                            child)
        return True
