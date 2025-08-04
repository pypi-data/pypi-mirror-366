
.. image:: https://esamultimedia.esa.int/docs/corporate/ESA_logo_2020_Deep.png
   :width: 400
   :alt: [Image not found]


EOPF CPM: Earth Observation Platform framework for python developers
====================================================================

|pipeline|
|coverage|
|docstr-coverage|




Introduction
=============

The **EOPF Core Python Modules (EOPF-CPM)** is python package gathering the best-in-class open-source python modules in
a harmonized framework intended for the development of image processors. Particularly the re-engineering of the
operational Level-0, Level-1 and Level-2 processors for the instruments on-board of the Copernicus Sentinel-1, Sentinel-2, Sentinel-3 (Land) missions.
It is providing features such as:

   * A generic product representation EOProduct compatible with the UNIDATA CDM model with utilities library allowing:
            * Writing an EOProduct to different external representations, formats and file systems.
            * Reading an EOProduct from different external representations including the legacy file format (mostly SAFE).
   * Distributed and parallel computing based on Dask.
   * Logging and tracing tools.
   * Processors triggering and workflows definition.


Installation
=============

See https://cpm.pages.eopf.copernicus.eu/eopf-cpm/main/quickstart/installation.html for installation documentation

Contributing
============

See https://cpm.pages.eopf.copernicus.eu/eopf-cpm/main/contributing.html for contributing documentation


API Reference
=============

See https://cpm.pages.eopf.copernicus.eu/eopf-cpm/main/api/eopf.html for the latest release API


License
========

EOPF CPM is licensed under the Apache License, Version 2.0. See LICENSE.txt for the full license text.


Copyright
=========

Copyright (C)  2021-2025 ESA



.. |pipeline| image:: https://gitlab.eopf.copernicus.eu/cpm/eopf-cpm/badges/main/pipeline.svg
   :target: https://github.com/CSC-DPR/eopf-cpm/tree/main

.. |coverage| image:: https://gitlab.eopf.copernicus.eu/cpm/eopf-cpm/badges/main/coverage.svg
   :target: https://github.com/CSC-DPR/eopf-cpm/tree/main

.. |docstr-coverage| image:: https://gitlab.eopf.copernicus.eu/cpm/eopf-cpm/-/jobs/artifacts/main/raw/docstrcov.svg?job=docs-cov
   :target: https://github.com/CSC-DPR/eopf-cpm/tree/main

.. _dask: https://www.dask.org/
