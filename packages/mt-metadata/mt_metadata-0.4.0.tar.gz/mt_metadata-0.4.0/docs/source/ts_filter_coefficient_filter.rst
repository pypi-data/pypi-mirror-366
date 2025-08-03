.. role:: red
.. role:: blue
.. role:: navy

CoefficientFilter
=================


:navy:`name`
~~~~~~~~~~~~

.. container::

   .. table::
       :class: tight-table
       :widths: 45 45 15

       +----------------------------------------------+-----------------------------------------------+----------------+
       | **name**                                     | **Description**                               | **Example**    |
       +==============================================+===============================================+================+
       | **Required**: :red:`True`                    | Name of filter applied or to be applied. If   | "lowpass_magnet|
       |                                              | more than one filter input as a comma         | ic"            |
       | **Units**: None                              | separated list.                               |                |
       |                                              |                                               |                |
       | **Type**: string                             |                                               |                |
       |                                              |                                               |                |
       | **Style**: name                              |                                               |                |
       |                                              |                                               |                |
       | **Default**: None                            |                                               |                |
       |                                              |                                               |                |
       |                                              |                                               |                |
       +----------------------------------------------+-----------------------------------------------+----------------+

:navy:`comments`
~~~~~~~~~~~~~~~~

.. container::

   .. table::
       :class: tight-table
       :widths: 45 45 15

       +----------------------------------------------+-----------------------------------------------+----------------+
       | **comments**                                 | **Description**                               | **Example**    |
       +==============================================+===============================================+================+
       | **Required**: :blue:`False`                  | Any comments about the filter.                | ambient air    |
       |                                              |                                               | temperature    |
       | **Units**: None                              |                                               |                |
       |                                              |                                               |                |
       | **Type**: string                             |                                               |                |
       |                                              |                                               |                |
       | **Style**: free form                         |                                               |                |
       |                                              |                                               |                |
       | **Default**: None                            |                                               |                |
       |                                              |                                               |                |
       |                                              |                                               |                |
       +----------------------------------------------+-----------------------------------------------+----------------+

:navy:`type`
~~~~~~~~~~~~

.. container::

   .. table::
       :class: tight-table
       :widths: 45 45 15

       +----------------------------------------------+-----------------------------------------------+----------------+
       | **type**                                     | **Description**                               | **Example**    |
       +==============================================+===============================================+================+
       | **Required**: :red:`True`                    | Type of filter, must be one of the available  | fap_table      |
       |                                              | filters.                                      |                |
       | **Units**: None                              |                                               |                |
       |                                              |                                               |                |
       | **Type**: string                             |                                               |                |
       |                                              |                                               |                |
       | **Style**: controlled vocabulary             |                                               |                |
       |                                              |                                               |                |
       | **Default**: None                            |                                               |                |
       |                                              |                                               |                |
       |                                              |                                               |                |
       +----------------------------------------------+-----------------------------------------------+----------------+

:navy:`units_in`
~~~~~~~~~~~~~~~~

.. container::

   .. table::
       :class: tight-table
       :widths: 45 45 15

       +----------------------------------------------+-----------------------------------------------+----------------+
       | **units_in**                                 | **Description**                               | **Example**    |
       +==============================================+===============================================+================+
       | **Required**: :red:`True`                    | Name of the input units to the filter. Should | count          |
       |                                              | be all lowercase and separated with an        |                |
       | **Units**: None                              | underscore, use 'per' if units are divided    |                |
       |                                              | and '-' if units are multiplied.              |                |
       | **Type**: string                             |                                               |                |
       |                                              |                                               |                |
       | **Style**: alpha numeric                     |                                               |                |
       |                                              |                                               |                |
       | **Default**: None                            |                                               |                |
       |                                              |                                               |                |
       |                                              |                                               |                |
       +----------------------------------------------+-----------------------------------------------+----------------+

:navy:`units_out`
~~~~~~~~~~~~~~~~~

.. container::

   .. table::
       :class: tight-table
       :widths: 45 45 15

       +----------------------------------------------+-----------------------------------------------+----------------+
       | **units_out**                                | **Description**                               | **Example**    |
       +==============================================+===============================================+================+
       | **Required**: :red:`True`                    | Name of the output units.  Should be all      | millivolt      |
       |                                              | lowercase and separated with an underscore,   |                |
       | **Units**: None                              | use 'per' if units are divided and '-' if     |                |
       |                                              | units are multiplied.                         |                |
       | **Type**: string                             |                                               |                |
       |                                              |                                               |                |
       | **Style**: alpha numeric                     |                                               |                |
       |                                              |                                               |                |
       | **Default**: None                            |                                               |                |
       |                                              |                                               |                |
       |                                              |                                               |                |
       +----------------------------------------------+-----------------------------------------------+----------------+

:navy:`calibration_date`
~~~~~~~~~~~~~~~~~~~~~~~~

.. container::

   .. table::
       :class: tight-table
       :widths: 45 45 15

       +----------------------------------------------+-----------------------------------------------+----------------+
       | **calibration_date**                         | **Description**                               | **Example**    |
       +==============================================+===============================================+================+
       | **Required**: :blue:`False`                  | Most recent date of filter calibration in ISO | 2020-01-01     |
       |                                              | format of YYY-MM-DD.                          |                |
       | **Units**: None                              |                                               |                |
       |                                              |                                               |                |
       | **Type**: string                             |                                               |                |
       |                                              |                                               |                |
       | **Style**: date                              |                                               |                |
       |                                              |                                               |                |
       | **Default**: 1980-01-01T00:00:00+00:00       |                                               |                |
       |                                              |                                               |                |
       |                                              |                                               |                |
       +----------------------------------------------+-----------------------------------------------+----------------+

:navy:`gain`
~~~~~~~~~~~~

.. container::

   .. table::
       :class: tight-table
       :widths: 45 45 15

       +----------------------------------------------+-----------------------------------------------+----------------+
       | **gain**                                     | **Description**                               | **Example**    |
       +==============================================+===============================================+================+
       | **Required**: :red:`True`                    | Scale factor for a simple coefficient filter. | 100            |
       |                                              |                                               |                |
       | **Units**: None                              |                                               |                |
       |                                              |                                               |                |
       | **Type**: float                              |                                               |                |
       |                                              |                                               |                |
       | **Style**: number                            |                                               |                |
       |                                              |                                               |                |
       | **Default**: 1.0                             |                                               |                |
       |                                              |                                               |                |
       |                                              |                                               |                |
       +----------------------------------------------+-----------------------------------------------+----------------+
