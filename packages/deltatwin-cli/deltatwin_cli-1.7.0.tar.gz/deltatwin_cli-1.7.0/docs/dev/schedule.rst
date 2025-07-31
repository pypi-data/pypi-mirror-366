The ``schedule`` section enables to manage your planned runs.
You can schedule a run on a specific date or schedule a recurring run.
You can also manage the list of your planned runs. You can pause and resume them or delete them.

_____________________________________________________

.. click:: delta.cli.schedule.list:list_deltatwin_schedule
   :prog: deltatwin schedule list
   :nested: full

**Example**

.. code-block:: console

    deltatwin schedule list -f json

This command will list the schedule run and returns:

.. code-block:: console

    {
    "schedule_id": "my-deltatwin_my_schedule_name_xxxx",
    "schedule_name": "my-deltatwin_my_schedule_name",
    "schedule": "2024-10-30 15:00:00",
    "schedule_name": "my_next_schedule1",
    "type": "date",
    "deltatwin_name": "my-deltatwin",
    "deltatwin_version": "1.0.0",
    "inputs": {
        "image" : {
            "type": "Data",
            "url": "https://example/$value",
        "angle": {
            "value": "30",
            "type": "integer"
        }
    },
    "next_schedule": "2024-10-30 15:00:00+00:00",
    "owner": "John Doe"
    }




______________________________________________


.. click:: delta.cli.schedule.get:get_deltatwin_schedule
   :prog: deltatwin schedule get
   :nested: full



______________________________________________


.. click:: delta.cli.schedule.add:add_deltatwin_schedule
   :prog: deltatwin schedule add
   :nested: full


**Example**

.. code-block:: console

    deltatwin schedule add DELTATWIN_NAME -n my_schedule_name -i inputs.json  -C date -s "2024-10-30 15:00:00" -f json

This command will add a new schedule run and returns:

.. code-block:: console

    {
    "schedule_id": "my-deltatwin_my_schedule_name_xxxxx",
    "schedule_name": "my-deltatwin_my_schedule_name",
    "schedule": "2024-10-30 15:00:00",
    "type": "date",
    "deltatwin_name": "my-deltatwin",
    "deltatwin_version": "1.0.0",
    "inputs": {
        "image": {
            "type": "Data",
            "url": "https://example/\$value",
            "auth": {
                "type": "SesamEO",
                "api_key": "MY_Sesame_EO_Key_xxxx"
            }
        },
        "angle": {
            "type": "integer",
            "value": 12
        }
    },
    "next_schedule": "2024-10-30 15:00:00+00:00",
    "owner": "John Doe"
    }



______________________________________________


.. click:: delta.cli.schedule.pause:pause_deltatwin_schedule
   :prog: deltatwin schedule pause
   :nested: full



______________________________________________


.. click:: delta.cli.schedule.resume:resume_deltatwin_schedule
   :prog: deltatwin schedule resume
   :nested: full


______________________________________________


.. click:: delta.cli.schedule.delete:delete_deltatwin_schedule
   :prog: deltatwin schedule delete
   :nested: full


