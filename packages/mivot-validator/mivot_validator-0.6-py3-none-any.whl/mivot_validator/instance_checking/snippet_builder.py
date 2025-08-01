"""
Created on 22 Dec 2022

@author: laurentmichel
"""

import os
from mivot_validator.utils.xml_utils import XmlUtils
from mivot_validator.instance_checking.xml_interpreter.exceptions import (
    MappingException,
)

# no longer used
DEFAULT_CONCRETE_CLASSES = {}


class Constraints:
    """
    Place holder for the constraints detected in the model
    Contraints consist in forcing a certain sub-type for a certain role
    There are stored in a dict {role: type}
    """

    def __init__(self, model_name, verbose=False):
        self.datatype = None
        self.role = None
        self.model_name = model_name
        self.constraints = {}
        self.verbose = verbose

    def _print_(self, message):
        if self.verbose:
            self._print_(message)

    def add_constraint(self, ele):
        refs = ele.xpath(".//datatype/vodml-ref")
        if len(refs) == 0:
            return
        self.datatype = refs[0].text
        self.role = ele.xpath(".//role/vodml-ref")[0].text.replace(
            self.model_name + ":", ""
        )
        self.constraints[self.role] = self.datatype
        self._print_(f"add constraint on role {self.role}: type={self.datatype} ")

    def get_contraint(self, const_key):
        self._print_(
            f"look for the constrains {const_key} in {self.constraints.keys()}"
        )
        for key in self.constraints.keys():
            if const_key.endswith(key):
                self._print_(f"  found as {self.constraints[key]}")
                return self.constraints[key]
        self._print_("  not found")
        return None

    def get_superclass_contraint(self, const_key):
        self._print_(f"look for const {const_key} in {self.constraints.keys()}")
        stripped_key = const_key.replace(self.model_name + ":", "")
        for key in self.constraints.keys():
            if key.startswith(stripped_key) is True:
                self._print_(f"  found SC as {self.constraints[key]}")
                return self.constraints[key]
        self._print_("  not found")
        return None


class Builder:
    """
    Build a MIVOT view of the class model_name:class_name of the model
    serialized in the provided VOMDL file
    """
    CACHE={}
    RECORD=""
    RECORD_ON=True

    def __init__(self, model_name, class_name, session, verbose=False):
        """
        :model_name: name of the model to be processed (could be retrieved
                     in the vodml
        :class_name: name of the class (VOMDLID)  to be mapped
        """
        self.model_name = model_name
        if not session.get_vodml(model_name):
            raise NotImplementedError(f"model {model_name} not supported")
        self.vodml = XmlUtils.xmltree_from_file(session.get_vodml(model_name))
        self.output_dir = session.tmp_data_path
        self.output = None
        self.outputname = None
        self.constraints = Constraints(model_name)
        self.class_name = class_name
        self.resolved_references = []
        self.verbose = verbose

    def _print_(self, message):
        if self.verbose:
            self._print_(message)

    def build(self):
        """
        Build one snippet for the dataType/objectType found in the VODML block
        and matching the searched class
        """
        for ele in self.vodml.xpath(".//dataType"):
            for tags in ele.getchildren():
                if tags.tag == "vodml-id" and tags.text == self.class_name:
                    self._print_(f"build datatype {tags.text}")
                    self.build_object(ele, "", True, True)
                    return

        for ele in self.vodml.xpath(".//objectType"):
            for tags in ele.getchildren():
                if tags.tag == "vodml-id" and tags.text == self.class_name:
                    self.build_object(ele, "", True, True)
                    return

        raise MappingException(f"Complex type {self.class_name} (model {self.model_name}) not found")

    def build_object(self, ele, role, root, aggregate):
        """
        Build a MIVOT instance from a VOMDL element

        :ele: VODML representation of the class to be mapped
        :role: VODML role to be affected to the built instance
        :root: If true the INSTANCE is not a component of an enclosing object.
               The snippet file must be initialized
        :aggregate: If False, all components found out in the
                    VODML element are added
                    to the enclosing instance (in that case of
                    inheritance reconstruction).
                    Otherwise, those components are
                    enclosed in an INSTANCE (composition case)
        """
        self._print_(
            f"build object with role={role} within the class {self.class_name}"
        )
        for tags in list(ele):
            if tags.tag == "constraint":
                self.constraints.add_constraint(tags)
                break
        for tags in list(ele):
            self._print_(f"   TAG {tags.tag}")
            if tags.tag == "vodml-id":
                self._print_(f"== build {tags.text}")
                if root is True:
                    self.outputname = os.path.join(
                        self.output_dir, self.model_name + "." + tags.text + ".xml"
                    )
                    self._print_(f"opening {self.model_name}.{tags.text}.xml")
                    self.output = open(self.outputname, "w")
                if aggregate is True:
                    dmid = ""
                    if role == "coords:Coordinate.coordSys":
                        self.write_out(
                            f"<!-- The Coordinate system can be pushed up to the "
                            f"GLOBALS and replaced here with "
                            f'<REFERENCE dmref="SOME_REF" dmrole="{role}" />">-->'
                        )
                        dmid = 'dmid="PUT_AN_ID_HERE"'
                    self.write_out(
                        f'<INSTANCE {dmid} dmrole="{role}" dmtype="{self.model_name}:{tags.text}">'
                    )
            elif tags.tag == "extends":
                self.addExtend(tags)
            elif tags.tag == "reference":
                self.addReference(tags)
            elif tags.tag == "composition":
                self.addComposition(tags)
            elif tags.tag == "attribute":
                self.addAttribute(tags)
            elif tags.tag == "description":
                if aggregate is True:
                    self.write_out(f'<!-- {tags.text}" -->')
            # elif tags.tag == "multiplicity":
            #    max_occurs = int(tags.xpath(".//maxOccurs")[0].text)

        if aggregate is True:
            self.write_out("</INSTANCE>")
        if root is True:
            self.output.close()
            XmlUtils.xmltree_to_file(
                XmlUtils.xmltree_from_file(self.outputname), self.outputname
            )

    def addReference(self, ele):
        """
        insert in the current snippet the VOMDL element matching the VODML reference element
        :ele: VODML  element of the reference
        """
        self._print_("== Add reference")
        vodmlid = None
        for tags in ele.getchildren():
            if tags.tag == "vodml-id":
                vodmlid = tags.text
            elif tags.tag == "multiplicity":
                max_occurs = tags.xpath(".//maxOccurs")[0].text
            elif tags.tag == "datatype":
                for dttag in list(tags):
                    if dttag.tag == "vodml-ref":
                        reftype = dttag.text.replace(self.model_name + ":", "")
                        break
        vokey = self.model_name + ":" + vodmlid
        const_type = self.constraints.get_contraint(vokey)

        if const_type is not None:
            reftype = const_type
        already_here = False
        if vodmlid in self.resolved_references:
            self._print_(
                f"   Reference {vodmlid} skipped to break a model loop (already processed)"
            )
            already_here = True

            #return
        self._print_(f"   Reference {vodmlid} processed for the fist time")
        self.resolved_references.append(vodmlid)

        Builder.RECORD_ON = True
        if max_occurs != "1":
            self.write_out(
                f'<COLLECTION dmrole="{(self.model_name + ":" + vodmlid)}" >'
            )
            # if object type type has already be used, we populate the COLLECTION
            # with an empty instance to avoid recursive forever  loops
            if already_here:
                self.write_out(
                f'<INSTANCE dmtype="{(self.model_name + ":" + reftype)}" />'
                )
            else:
                self.get_object_by_ref(
                reftype.replace(self.model_name + ":", ""),
                self.model_name + ":" + vodmlid,
                True,
            )
            self.write_out("</COLLECTION>")
        else:
            self.get_object_by_ref(
                reftype.replace(self.model_name + ":", ""),
                self.model_name + ":" + vodmlid,
                True,
            )

    def addComposition(self, ele):
        """
        insert in the current snippet the VOMDL element matching the VODML composition element
        :ele: VODML  element of the composition
        """
        self._print_("== Add composition")
        vodmlid = None
        for tags in ele.getchildren():
            if tags.tag == "vodml-id":
                vodmlid = tags.text
            elif tags.tag == "multiplicity":
                max_occurs = tags.xpath(".//maxOccurs")[0].text
            elif tags.tag == "datatype":
                for dttag in list(tags):
                    if dttag.tag == "vodml-ref":
                        reftype = dttag.text.replace(self.model_name + ":", "")
                        break
        vokey = self.model_name + ":" + vodmlid
        const_type = self.constraints.get_contraint(vokey)
        if const_type is not None:
            reftype = const_type

        # MIVOT counterparts of compositions are INSTANCE when cardinality = 1
        # and COLLECTIONS otherwise
        if max_occurs != "1":
            self.write_out(
                f'<COLLECTION dmrole="{(self.model_name + ":" + vodmlid)}" >'
            )
            self.get_object_by_ref(reftype.replace(self.model_name + ":", ""), "", True)
            self.write_out("</COLLECTION>")
            return
        self.get_object_by_ref(
            reftype.replace(self.model_name + ":", ""),
            self.model_name + ":" + vodmlid,
            True,
        )

    def addExtend(self, ele):
        """
        add to the current snippet the super class components
        :ele: EXTEND VODML element
        """
        self._print_("== add extend")
        for tags in ele.getchildren():
            if tags.tag == "vodml-ref":
                reftype = tags.text
                break

        const_type = self.constraints.get_contraint(reftype)
        if const_type is not None in self.constraints.constraints:
            reftype = const_type
        self._print_(f"ref type {reftype}")

        #
        # Not very nice path , but as long as we do not handle cros-model inheritance links
        # we need it
        if self.model_name != "meas" and reftype == "meas:Measure":
            self.write_out(
                "<ATTRIBUTE dmrole='meas:Measure.ucd' "
                "dmtype='ivoa:string' value='phot.mag;em.opt;stat.mean' />"
            )
        else:
            self.get_object_by_ref(
                reftype.replace(self.model_name + ":", ""), reftype, False, extend=True
            )

    def addAttribute(self, ele):
        """
        add one attribute to the current snippet (can a complex data type or not)
        if the multiplicity is one:one attribute is added, a COLLECTION otherwise
        :ele: ATTRIBUTE VODML element
        """
        dmtype = None
        for tags in ele.getchildren():
            if tags.tag == "vodml-id":
                vodml_id = tags.text
                dmrole = f"{self.model_name}:{vodml_id}"
            elif tags.tag == "datatype":
                for ref in tags.getchildren():
                    vodmlref = ref.text
                    dmtype = self.get_vodmlid(vodmlref)
                    if vodmlref.startswith("ivoa:") is False :
                        self.get_object_by_ref(
                            vodmlref.replace(self.model_name + ":", ""), dmrole, True
                        )
                        return
                    break
            elif tags.tag == "multiplicity":
                max_occurs = int(tags.xpath(".//maxOccurs")[0].text)

        if not dmtype:
            return

        if dmtype.lower().endswith("string"):
            unit_att = ""
        else:
            unit_att = 'unit=""'

        if max_occurs == 1:
            if dmtype.endswith("Quantity"):
                self.write_out(
                    f'<ATTRIBUTE dmrole="{dmrole}" dmtype="{dmtype}"'
                    f' {unit_att} ref="@@@@@" value="" />'
                )
            else:
                self.write_out(
                    f'<ATTRIBUTE dmrole="{dmrole}" dmtype="{dmtype}"'
                    f' {unit_att} ref="@@@@@" value="" />'
                )
        else:
            self.write_out(f'<COLLECTION dmrole="{dmrole}">')
            for _ in range(max_occurs):
                if dmtype.endswith("Quantity"):
                    self.write_out(
                        f'<ATTRIBUTE dmtype="{dmtype}" '
                        f'{unit_att} ref="@@@@@" value="" />'
                    )
                else:
                    self.write_out(
                        f'<ATTRIBUTE dmtype="{dmtype}" '
                        f'{unit_att} ref="@@@@@" value="" />'
                    )
            self.write_out("</COLLECTION>")

    def get_object_by_ref(self, vodmlid, role, aggregate, extend=False):
        """ """
                    
        self._print_(f"search object with vodmlid={vodmlid}")
        for ele in self.vodml.xpath(".//objectType"):
            abstract_att = ele.get("abstract")
            for tags in list(ele):
                if tags.tag == "vodml-id" and tags.text == vodmlid:
                    self._print_("  found in objecttype")

                    if (
                        extend is False
                        and abstract_att is not None
                        and abstract_att.lower() == "true"
                    ):
                        self.get_concrete_type_by_ref(vodmlid, role, aggregate, extend)
                    else:
                        self.build_object(ele, role, False, aggregate)
                    return

        for ele in self.vodml.xpath(".//dataType"):
            abstract_att = ele.get("abstract")

            for tags in list(ele):  # root is the ElementTree object
                if tags.tag == "vodml-id" and tags.text == vodmlid:
                    self._print_("  found in datatype")
                    self._print_(extend)
                    if (
                        extend is False
                        and abstract_att is not None
                        and abstract_att.lower() == "true"
                    ):
                        self.get_concrete_type_by_ref(vodmlid, role, aggregate, extend)
                    else:
                        self.build_object(ele, role, False, aggregate)
                    return

        for ele in self.vodml.xpath(".//primitiveType"):
            found = False
            description = ""
            for tags in list(ele):  # root is the ElementTree object
                if tags.tag == "vodml-id" and tags.text == vodmlid:
                    found = True
                if tags.tag == "description":
                    description = f"<!-- {tags.text} -->"
            if found is True:
                if description:
                    self.write_out(description)
                dmtype = self.get_vodmlid(vodmlid)
                self.write_out(
                    f'<ATTRIBUTE dmrole="{role}" dmtype="{dmtype}" ref="@@@@@" value=""/>'
                )
                return

        for ele in self.vodml.xpath(".//enumeration"):
            found = False
            description = ""
            for tags in list(ele):  # root is the ElementTree object
                if tags.tag == "vodml-id" and tags.text == vodmlid:
                    found = True
                if tags.tag == "description":
                    description = f"<!-- {tags.text} -->"
            if found is True:
                values = ele.xpath(".//literal/name")
                val_str = ""
                for value in values:
                    val_str += value.text + " "
                if description:
                    self.write_out(description)
                self.write_out(
                    f"<!-- Enumeration datatype: supported values are {val_str} -->"
                )
                dmtype = self.get_vodmlid(vodmlid)
                self.write_out(
                    f'<ATTRIBUTE dmrole="{role}" dmtype="{dmtype}" value="OneOf {val_str}"/>'
                )
                return
         
        # "coords:Epoch" is a primitive type, and right now, there is no way see it at this level
        # we hardcode this specific case
        if vodmlid == "coords:Epoch":
            self.write_out(f'<ATTRIBUTE dmrole="{role}" dmtype="{vodmlid}"/>')
        else:
            self.write_out(f'<INSTANCE dmrole="{role}" dmtype="{vodmlid}"/>')

    def get_concrete_type_by_ref(self, abstract_vodmlid, role, aggregate, extend):
        """ """
        self._print_(f"search concrete object of vodmlid={abstract_vodmlid}")
        if role.endswith("coordSpace"):
            self.write_out(
                "<!-- the axis representation (coords:PhysicalCoordSys.coordSpace)"
                " is not serialized here -->"
            )
        elif abstract_vodmlid in DEFAULT_CONCRETE_CLASSES:
            concrete_type = DEFAULT_CONCRETE_CLASSES[abstract_vodmlid]
            self._print_(
                f"    Take {concrete_type} as concrete type for {abstract_vodmlid}"
            )
            self.write_out(
                f"<!-- {concrete_type} taken as concrete type for {abstract_vodmlid} -->"
            )

            self.get_object_by_ref(concrete_type, role, aggregate, extend)
            return
        else:
            self.write_out(
                f"<!-- Replace by an INSTANCE of a derived classes of {abstract_vodmlid} if applicable. -->"
            )
            self.write_out(
                f"<INSTANCE dmrole='{role}' dmtype='{self.model_name}:{abstract_vodmlid}'/>"
            )

    def is_abstract(self, ele):
        """
        Tells whether the datatype ele is abstract or not
        """
        self._print_(f' is that abstract {ele.get("abstract")} ?')
        return ele.get("abstract") is not None

    def get_vodmlid(self, vodmlid):
        """
        returns the full qualified VODMLid
        """
        if ":" in vodmlid:
            return f"{vodmlid}"
        return f"{self.model_name}:{vodmlid}"

    def write_out(self, string, record=False):
        """
        Write out the element given as string into the current snippet
        """
        if record is True:
            Builder.RECORD_ON = True
            Builder.RECORD = ""
        if Builder.RECORD_ON is True:
            Builder.RECORD += string + "\n"
        if self.output is None:
            self._print_(string)
        else:
            self.output.write(string)
            self.output.write("\n")
        if record is False:
            Builder.RECORD_ON = False
        

    def include_file(self, filename):
        """
        Snippet aggregation: no longer used
        """
        if os.path.exists(filename):
            self._print_(f"include file {filename}")
            lines = []
            with open(filename) as include_file:
                lines = include_file.readlines()
            for line in lines:
                self.write_out(line)
            return True

        self._print_(f"Cannot find file {filename}")
        return False
