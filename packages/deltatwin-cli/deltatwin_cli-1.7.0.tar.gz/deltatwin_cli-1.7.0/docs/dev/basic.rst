.. click:: delta.cli:delta_login
   :prog: deltatwin login
   :nested: full

The DestinE DeltaTwin® API URL is https://api.deltatwin.destine.eu/

.. code-block:: console

    deltatwin login username password -a https://api.deltatwin.destine.eu/

This command will log in to the service with the api given in argument.
To set the service you want to query, you can either use *--api*,
or set the path to your configuration file *--conf*.

.. code-block:: console

    INFO: Login to the service token saved in /home/jiloop/.deltatwin/conf.ini

When log, all the connection information will be stored into a configuration file (conf.ini),
it will contain the token, and the api url, all the information mandatory to interact with,
the deltatwin services.

Once this file is created, you can simply log again using this command.

.. code-block:: console

    deltatwin login

It will find all the connection information into the configuration file.

---------------------------------

.. click:: delta.cli:version
   :prog: deltatwin version
   :nested: full

.. code-block:: console

    deltatwin version

Prints the DeltaTwin® command line version currently used.

.. code-block:: console

    DeltaTwin® CLI version : 1.2.0

.. code-block:: console

    deltatwin version --all

Prints the DeltaTwin® command line version and the core version installed.

.. code-block:: console

    DeltaTwin® CLI version : 1.3.0
    DeltaTwin® CORE version : 1.1.0


---------------------------------

.. click:: delta.cli.metrics:metrics_deltatwins
   :prog: deltatwin metrics
   :nested: full

.. code-block:: console

    deltatwin metrics

It shows the user the current status of his quotas : number of daily runs available,
number of scheduled tasks and the amount of disk space (in bytes) used on the user's drive.

.. code-block:: console

    INFO: Here are the available metric type to be shown: Drive, DeltaTwin Component, Schedules, Runs
    {
        "type": "drive",
        "storage_used": 36306993,
        "max_size": 21474836480,
        "total_objects": 1,
        "last_metric_update": "2025-06-06T08:20:30Z"
    }
    {
        "type": "runs",
        "number_of_runs": 0,
        "number_of_runs_parallel": 0,
        "execution_time": 0.0,
        "max_run": 10,
        "max_run_parallel": 2
    }
    {
        "type": "schedules",
        "cron_number": 0,
        "max_cron": 5,
        "metric_date": "2025-06-12T12:49:50Z"
    }
    {
        "total_size": 176867025.0,
        "type": "deltatwin component",
        "details": [
            {
                "deltatwin_name": "my_deltatwin",
                "size": 176867025.0,
                "last_metric_update": "Jun 10, 2025, 03:05:46 PM"
            }
        ]
    }

