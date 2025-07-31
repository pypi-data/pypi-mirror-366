*****************************
DeltaTwin Service
*****************************

Version v\ |version|

-------------------

GAEL Systems is developing a dedicated service, named "DeltaTwin® Service" to
facilitate modelling activities of digital twins.

It aims to offer a collaborative environment for building and running
multi-scale and composable workflows, leveraging the numerous
available data sources, sharing results, and easing interoperability
with other digital twin standards and system dynamics models.

The DeltaTwin® Component, also name hereafter Delta Component, is the central
element for the management of workflows, resources and their results.
They follow a precise structure folder to ensure they are handled
by the DeltaTwin® service.

The service includes the “component“ element in charge of handling DeltaTwin
storage, their configuration and versionning.
The “drive“ module enable to handle data resources and the artifacts produced.
The “run“ element is in charge of the models executions and their monitoring.
The "schedule" part offer the possibility to plan a run at a specific date
or to plan a periodic run.

The DeltaTwin® command line allows user to control the management of the
later modules. It allows user to either work online and perform all actions
in a cloud environment or locally using your computer's resources.

DeltaTwin® service also provides a web application to graphically manages your
DeltaTwins and their execution.

User Guide
==========

.. toctree::
   :maxdepth: 2

   user/install

-------------------

.. toctree::

   dev/api

-------------------

.. toctree::

   change_log/tata

-------------------

.. toctree::

   change_log/change_log
