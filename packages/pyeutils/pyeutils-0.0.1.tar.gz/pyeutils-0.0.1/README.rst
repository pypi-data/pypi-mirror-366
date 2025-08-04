pyeutils
========

**pyeutils** is a lightweight Python wrapper for the NCBI E-utilities (Entrez Programming Utilities) API. It simplifies
programmatic access to the vast array of biomedical data available from NCBI, including PubMed, Gene,
Protein, Nucleotide, and more.

NCBI’s E-utilities are a powerful but low-level REST interface. `pyeutils` abstracts the complexity and
provides a more Pythonic way to interact with the API.

Features
--------

- Convenient interface to NCBI’s Entrez databases
- Supports key E-utilities: `esearch`, `efetch`, `esummary`
- `epost`, `elink`, `egquery`, and `espell` not yet implemented
- Handles request throttling and query parameters
- Returns structured Python objects (e.g., dicts, lists, or parsed XML/JSON)
- Compatible with Python 3.9+

Installation
------------

Install via pip:

.. code-block:: bash

   pip install pyeutils

Quick Start
-----------

.. code-block:: python

   import pyeutils
   client = pyeutils.NcbiEutils(API_TOKEN)

   result = client.esearch('assembly', 'GCF_000005845.2')
   print(result.id_list)

Documentation
-------------

none yet

License
-------

MIT License. See `LICENSE` file for details.

Support
-------

For questions, bugs, or feature requests, open an issue at:
https://github.com/Fxe/pyeutils/issues