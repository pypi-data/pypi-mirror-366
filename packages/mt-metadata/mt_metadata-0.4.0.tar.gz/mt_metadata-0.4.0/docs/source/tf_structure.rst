========================
Transfer Functions
========================

The `transfer_functions` module deals with various formats that transfer functions are stored in.  This includes reading and writing for most formats.      

Supported Formats
------------------

.. list-table:: 
    :widths: 25 50 20 20
    :header-rows: 1
    
    * - Format
      - Description
      - Read
      - Write
    * - **EDI**
      - Common `SEG format <https://library.seg.org/doi/abs/10.1190/1.1892244>`_ (including spectra) 
      - Yes
      - Yes
    * - **EMTFXML**
      - Anna Kelbert's `XML format <https://library.seg.org/doi/10.1190/geo2018-0679.1>`_, archive format at `IRIS <https://eos.org/science-updates/taking-magnetotelluric-data-out-of-the-drawer>`_  
      - Yes
      - Yes
    * - **ZFiles**
      - Output from Gary Egbert's EMFT processing code [.zmm, .zrr, .zss]
      - Yes
      - Yes
    * - **JFiles**
      - Jones' format, also output of Alan Chave's BIRRP code [.j]
      - Yes
      - No
    * - **Zonge AVG**
      - Zonge International .avg format out put by their MTEdit code [.avg]
      - Yes
      - No
      
Purpose
----------------

Modules exists for each supported format, but should only be used under the hood.  Instead, the `transfer_functions` module was set up to have a common container for any transfer function.  This is the :class:`mt_metadata.transfer_functions.core.TF` object.  It can read any supported format and write those that have write methods.  

The :class:`mt_metadata.transfer_functions.core.TF` object contains standard metadata and the data are stored in an :class:`xarray.DataSet` for generalization and easy access to elements.

Module Structure
------------------

The module structure for :mod:`mt_metadata.transfer_functions` is setup to be plug-in like.  Each transfer function file format has its own module in :mod:`mt_metadata.transfer_functions.io`.  For example EDI files are in the module :mod:`mt_metadata.transfer_functions.io.edi`.  Under each module there is a `metadata` folder and a `metadata/standards` folder to accommodate format specific metadata and standardize data types for those metadata.

.. code-block:: python

    mt_metadata.transfer_functions.io
    -----------------------------------
        |- edi
          |- metadata
            |- standards
              |- .json standard files           
        |- zfiles
          |- metadata
            |- standards
              |- .json standard files
        |- jfiles
          |- metadata
            |- standards
              |- .json standard files
        |- zonge
          |- metadata
             |- standards
               |- .json standard files
        |- emtfxml
          |- metadata
              |- standards
                |- .json standard files
               
Each of these modules are imported into `mt_metadata.transfer_functions.io.readwrite` for generic readers and writers.  The :class:`mt_metadata.transfer_functions.core.TF` class uses the :func:`mt_metadata.transfer_functions.io.readwrite.read` and :func:`mt_metadata.transfer_functions.io.readwrite.write` functions to read and write through :func:`mt_metadata.transfer_functions.core.TF.read_tf_file` and :func:`mt_metadata.transfer_functions.core.TF.write_tf_file` methods   


===============================   
Supported Formats
===============================

.. toctree::
    :maxdepth: 1
    :caption: Examples

    notebooks/tf_example.ipynb
    notebooks/tf_edi_example.ipynb
    notebooks/tf_emtfxml_example.ipynb
    notebooks/tf_zfile_example.ipynb
    notebooks/tf_jfile_example.ipynb    
    notebooks/tf_avg_example.ipynb
    
=======================================
Archiving Transfer Functions at IRIS
=======================================

.. toctree::
    :maxdepth: 3
    :caption: Example of Archiving Transfer Functions at IRIS
    
    notebooks/tf_iris_archive_example.ipynb

========================
Metadata Definitions
========================

.. toctree::
    :maxdepth: 1
    
    tf_index
    tf_emtfxml_index
    tf_edi_index
    tf_zmm_index
    tf_jfile_index
    tf_zonge_index