.. mivot-validator documentation master file, created by
   sphinx-quickstart on Fri Dec  1 13:07:28 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Mivot Validator Tools
================================

This package has 2 purposes:

- Validation of VOTables with `MIVOT <https://ivoa.net/documents/MIVOT/20230620/index.html>`__ annotations
- MIVOT serialization of model components (snippets) that can be used to build annotations

Python scripts for validating annotated VOTables
------------------------------------------------

There are 2 validation levels:

- against the XML schemas (VOTable and MIVOT)
- against the model itself as it is defined in VODML

XML Schema Validation
~~~~~~~~~~~~~~~~~~~~~

Validation of an annotated VOTable against both VOTable and MIVOT schemas:

.. code:: bash

   $ mivot-validate  PROJECT_DIR/tests/data/gaia_3mags_ok_1.xml 
     
   USAGE: mivot-validate [path]
          Validate against both VOTable and MIVOT schemas
          path: either a simple file or a directory
                all directory XML files are validated
                exit status: 0 in case of success, 1 otherwise

Validation of an annotated VOTable against the MIVOT schema:
    
.. code:: bash
 
   $ mivot-mapping-validate  PROJECT_DIR/tests/data/gaia_3mags_ok_1.xml 
     
   USAGE: mivot-mapping-validate [path]
          Validate XML files against  MIVOT schema
          path: either a simple file or a directory
                all directory XML files are validated
                exit status: 0 in case of success, 1 otherwise


Model Validation
~~~~~~~~~~~~~~~~

This tool checks that mapped classes match the model they refer to. 

- Requires an annotated VOTable as input. 
- This VOTable is parsed with a model viewer issuing a model view of the first data row.
- Each instance of that view is compared with the VODML class definition. 
- This feature works with *PhotDM*, *Meas*, *Coords* and the *MANGO* draft. 
  Any other model, but *ivoa* which is skipped, makes the process failing.

.. code:: bash

    $ mivot-instance-validate <VOTABLE path>
    
    USAGE: mivot-instance-validate [path]
           Validate the mapped instances against the VODML definitions
           path: path to the mapped VOTable to be checked
           exit status: 0 in case of success, 1 otherwise
    

The detail of the validation process follows these steps: 

- INPUT: a VOTable annotated with the supported models. 
- The annotation must have at least one valid TEMPLATES 
- The current implementation works only with VOTables having one table. 
- Build a model view of the first data row (``mivot_validator/instance_checking/xml_interpreter/model_viewer.py``). 
- All top level INSTANCE of that model view are checked one by one. 
- The XML blocks corresponding to these instances are extracted as *etree* objects 
- Get the ``dmtype`` on the instance to be validated 
- Build an XML snippets for that class from the VODML file (``mivot_validator/instance_checking/snippet_builder.py``) 
- The validator checks all component of the mapped instance against the snippet. 
- If the component is an ATTRIBUTE, both ``dmtypes`` and ``roles`` are checked 
- If the component is a COLLECTION, ``dmrole`` as well as items ``dmtypes`` are checked 
- If the component is a REFERENCE, ``dmrole`` is checked 
- If the component is an INSTANCE, both ``dmtypes`` and roles are checked and the validation loop is run on its components

The validator only checks the model elements that are mapped. It does not care about missing attributes or any other missing class components. 
MIVOT does not have requirements on the model elements that must be mapped.


Types and Roles Checking
~~~~~~~~~~~~~~~~~~~~~~~~

The validation tool below checks that all ``dmtype`` and ``dmrole`` referenced in the mapping block 
are known by mapped models; it does not care of the class structures. 
This checking only works with the *PhotDM/MANGO/Meas/Coord/ivoa* models, other models are ignored.

.. code:: bash

    $ types-and-roles-validate <VOTABLE path>
    
    USAGE: types-and-roles-validate [path]
           Validate all dmtypes and dmroles
           exit status: 0 in case of success, 1 otherwise
    


Snippet Generation
------------------

To facilitate the MIVOT annotation of VODML files, it can be convenient to work with 
pre-computed snippets that can be stacked to build full annotation blocks.

- A snippet is a MIVOT fragment, where values and references are not set, that represents a component of a model.
- Snippets can easily be derived from the VODML representation of the model as long as there is no class polymorphism.
  If there is some, we provide a tool helping users to resolve abstract components.

There are two snippet generators available in this package:
 
- ``mivot-snippet-model`` which allows, for a given model, to generate all 
   non-abstract object and data types as MIVOT components.
-  The ``mivot-snippet-instance`` which generate, for a given concrete class name, a 
   usable snippet including the concrete classes given either as user input or as command line parameters. 

Build all MIVOT snippets for a model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash
   
   $ mivot-snippet-model [VODML path or url]
    
   USAGE: mivot-snippet-model [url] [output_dir]
           Create MIVOT snippets from VODML files
           url: url of any VODML-Model (must be prefixed with file:// in case of local file)
           output_dir: path to the chosen output directory(session working directory by default)
           exit status: 0 in case of success, 1 otherwise

Build the MIVOT snippet for one model class with resolving abstract types:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash
 
   $ mivot-snippet-instance coords:TimeSys `pwd`/coords.TimeSys.example \
   -cc dmrole=coords:TimeFrame.refPosition,context=coords:TimeSys,dmtype=coords:RefLocation,class=coords:StdRefLocation\
   -cc dmrole=coords:TimeFrame.refDirection,context=coords:TimeSys,dmtype=coords:RefLocation,class=coords:StdRefLocation
    
In this example the tool will generate one snippet for the object type `coords:TimeSys`.

- The produced file will be located in ``CURRENT_FOLDER/coords.TimeSys.example.xml``.
  If the output is not an absolute path, it will be located in the session working directory.
- All MIVOT instances of (abstract) type ``coords:RefLocation`` playing the role ``coords:TimeFrame.refPosition``
  and hosted by a class playing the role ``coords:TimeSys``, will be replaced by instances of type ``coords:StdRefLocation``
- All MIVOT instances of (abstract) type ``coords:RefLocation`` playing the role ``coords:TimeFrame.refDirection``
  and hosted by a class playing the role ``coords:TimeSys``, will be replaced by instances of type ``coords:StdRefLocation``


Change Log
~~~~~~~~~~

- 0.3: Support multiple instances of the same object in the snippet building


.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :glob:
   
   source/*
   
Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`
