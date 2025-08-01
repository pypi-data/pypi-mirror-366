Installation
============

Installation via PIP
--------------------


A typical way to install a package is to use the python package installer (`PIP`).
To install the package using the PIP personal token (github or other tool depending on
the artifactory server) with the `read_api` scope is required. Next, user needs to
create a `pip config file <https://pip.pypa.io/en/stable/topics/configuration/>`_
to access artifactory server with the package.

.. code-block:: console

   (.venv) $ pip install hwc


Editable install
----------------


For development, the package is usually installed as an `editable install`. To do this, 
in the root directory of the package the following command should be executed:

.. code-block:: console

   (.venv) $ pip install -e .
 

Development version
-------------------

Sometimes a development package may be needed (e.g. so that it can be tested in a
CI environment as a dependency).

To release a dev package, add the suffix `.dev[xx]` to `version.txt`, where `xx` is the
consecutive package number, and run the `deploy_dev` pipeline to build and deploy the
package.

