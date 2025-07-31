The DeltaTwin® run module handles the execution and monitoring of the DeltaTwin® components.
The run can be done remotely or locally when possible.
Run results can be saved as artifacts in the user's DeltaTwin® drive space.

______________________________________________

.. click:: delta.cli.run.start:start
   :prog: deltatwin run start
   :nested: full


**Examples**:

If your DeltaTwin® component requires two inputs:

   - "product": of type Data that points to a url with or without an authentication method
   - "angle": of type integer

Your input section in the JSON file would look like this:

.. code-block:: console

   {
      "product": {
            "type": "Data",
            "url": "https://api.sesameo.destine.eu/odata/....",
            "auth": {
               "type": "SesamEO",
               "api_key": "xxxx_Your_SesamEO_API_KEY"
            }
      },
      "angle": {
            "type": "integer",
            "value": 45
      }
   }

Currently, 2 authentication methods are supported: "No auth" and "SesamEO".

Then, to start your run execute the following command:

.. code-block:: console

    deltatwin run start <DELTATWIN_NAME> -i name_of_your_inputs_file.json




______________________________________________

.. click:: delta.cli.run.local:run_local
   :prog: deltatwin run start_local
   :nested: full

.. warning::
   | When running DeltaTwin® components locally, some input types are not supported:
   | * **DriveData**: Resources stored in DeltaTwin® Drive cannot be accessed remotely for local execution.  You must download these files manually and update the manifest to reference the local path.
   | * **Secret**: Sensitive or secure data management mechanism cannot be used locally, you may use the ```string``` type.
   | * **URL with SesamEO API Key**: only URL with no authentication can be used.

.. code-block:: console

    deltatwin run start_local -i name_of_your_inputs_file.json

______________________________________________

.. click:: delta.cli.run.list:list_deltatwin_executions
   :prog: deltatwin run list
   :nested: full

**Example:**

The following command  lists all the runs with the status "error" for the
DeltaTwin® named "my_deltatwin"

.. code-block:: console

    deltatwin run list -s error -t my_deltatwin

If you don't specify the DeltaTwin® name, the command will list all the runs that
ended with an error.

.. code-block:: console

    deltatwin run list -s error

______________________________________________

.. click:: delta.cli.run.get:get_deltatwin_execution
   :prog: deltatwin run get
   :nested: full


.. code-block:: console

    deltatwin run get <RUN_ID>




______________________________________________

.. click:: delta.cli.run.delete:delete_deltatwin_execution
   :prog: deltatwin run delete
   :nested: full

.. code-block:: console

    deltatwin run delete <RUN_ID>


______________________________________________

.. click:: delta.cli.run.download:download_deltatwin_execution
   :prog: deltatwin run download
   :nested: full

.. code-block:: console

    deltatwin run download RUN_ID OUTPUT_NAME


______________________________________________

.. click:: delta.cli.run.monitor.status:get_deltatwin_execution_status
   :prog: deltatwin run monitor status
   :nested: full

.. code-block:: console

    deltatwin run monitor status RUN_ID


______________________________________________

.. click:: delta.cli.run.monitor.logs:get_deltatwin_execution_logs
   :prog: deltatwin run monitor logs
   :nested: full

.. code-block:: console

    deltatwin run monitor logs RUN_ID NODE_ID