Change log of DeltaTwin® CLI
#############################



.. list-table:: Change summary
   :widths: 30, 70
   :header-rows: 1

   * - Version
     - Change notice
   * -  1.7.0
     - :ref:`Version 1.7.0`
   * -  1.6.1
     - :ref:`Version 1.6.1`
   * -  1.6.0
     - :ref:`Version 1.6.0`
   * - 1.5.0
     - :ref:`Version 1.5.0`
   * - 1.4.0
     - :ref:`Version 1.4.0`
   * - 1.3.3
     - :ref:`Version 1.3.3`
   * - 1.3.2
     - :ref:`Version 1.3.2`
   * - 1.3.0
     - :ref:`Version 1.3.0`
   * - 1.2.0
     - :ref:`Version 1.2.0`
   * - 1.1.0
     - :ref:`Version 1.1.0`
   * - 1.0.1
     - :ref:`Version 1.0.1`
   * - 1.0.0
     - :ref:`Version 1.0.0`


Version 1.7.0
==================
.. _Version 1.7.0:

* The CLI is now compatible with Python 3.12.
* A new set of commands, gathered under the section "deltatwin run monitor", allow to get the details of a run execution and access to the log available for each node of type model.

Version 1.6.1
==================
.. _Version 1.6.1:


* The command "deltatwin drive artifact create" is now asynchronous, meaning it informs that the command has been successfully sent and the artifact will be available soon.

Version 1.6.0
==================
.. _Version 1.6.0:


* A new set commands, gathered under the section "deltatwin drive resource", enable to handle your resources data in your DeltaTwin personal storage.
* Improve error handling and code error messages.
* The command "deltatwin run list" lists now, all your current runs without having to specify a DeltaTwin name.
* It is now possible to provide as input of your run an URL from DESP SesamEO service, the authentication method by API key is now supported.
* New commands enable to modify the visibility status and topic list of the DeltaTwin components and Drive data.
* A dedicated command enables to download an artifact or a resource.

Version 1.5.0
==================
.. _Version 1.5.0:


* The metric command for the artifacts has been moved to a generic command named "deltatwin metrics"
* the commands for managing DeltaTwin components have been grouped under the "deltatwin component" section
* Add a new group of commands to schedule runs and manage these scheduling
* Add a command to delete a DeltaTwin component or only a specific version of a DeltaTwin component


Version 1.4.0
==================
.. _Version 1.4.0:


* Add metric feature for artifact
* Fix author name when displaying the list of DeltaTwin®


Version 1.3.3
==================
.. _Version 1.3.3:


* Correct command run_local to start_local


Version 1.3.2
==================
.. _Version 1.3.2:


* Update Readme
* Publish on PyPi


Version 1.3.0
==================
.. _Version 1.3.0:


* Remove all commands marked as deprecated
* Get deltatwin® component description and versioning
* Improve management of DeltaTwin® resources (add/delete/list)
* Improve management of DeltaTwin® dependencies (add/delete/list)
* Add return code, and documentation.


Version 1.2.0
==================
.. _Version 1.2.0:


* Mark git wrapping command as deprecated
* Add artifact generation and listing
* Improve token management when log
* Start remote run execution
* Get information on run execution


Version 1.1.0
==================
.. _Version 1.1.0:


* Improve documentation and its pdf generation
* Add deltatwin login option to list DeltaTwin®
* Remove pull, fetch, push command


Version 1.0.1
==================
.. _Version 1.0.1:


* Add release notes in documentation
* Improve CLI documentation
* No more Error raise when the command is not implemented
* Fix documentation.
* Add the deltatwin list command, to list open access DeltaTwins or to list them by group.

Version 1.0.0
================
.. _Version 1.0.0:


* Add version command.
* Raise NotImplementedError for all not implemented commands.
* Organize, and clean the doc generation to PDF
* Remove all click.echo() from run commands.

