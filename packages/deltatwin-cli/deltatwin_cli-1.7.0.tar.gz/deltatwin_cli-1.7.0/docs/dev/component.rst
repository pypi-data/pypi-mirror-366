The ``deltatwin component`` section gathers the commands dedicated to handle DeltaTwin® projects.
It lists all the DeltaTwin® projects the user has access to. User can initialize, publish or delete their DeltaTwin® components.

A DeltaTwin® component is managed by 2 files : the ``manifest`` and ``workflow`` files.

These commands allow to store the ``manifest`` and ``workflow`` files as well as all the models and source code that enable to build your DeltaTwin® component.

The DeltaTwin® component anatomy can be described with the following empty local representation:
::

    my_project
    ├─── manifest.json
    ├─── workflow.yml
    ├─── models/

______________________________________________


.. click:: delta.cli.components.list:list_deltatwins
   :prog: deltatwin component list
   :nested: full

.. code-block:: console

    deltatwin component list

This command will list the DeltaTwin® components visible to the user,
it includes, the user's DeltaTwin® components, all the DeltaTwin® components of the
Starter Kit and all the published DeltaTwins
with public visibility.
By default the information's will be displayed as an array, these information can also
be retrieved as a json.

.. code-block:: console

    deltatwin component list --format-output json

This command will list the DeltaTwin® components of the user.
Before using this command the user must be logged in,
using the *deltatwin* *login* command. For example, it returns:

.. code-block:: console

    [
        {
            "name": "Deltatwin1",
            "short_description": "Description of the Deltatwin1",
            "publication_date": "2024-02-21T13:16:47.548Z",
            "license": "LGPLv3",
            "topics": [
                "starter-kit",
                "sentinel-2",
                "optical",
                "color-composition"
            ],
            "owner": "delta-user"
            "visibility": "public"
        },
        {
            "name": "Deltatwin2",
            "short_description": "Description of the Deltatwin2",
            "publication_date": "2024-02-21T13:16:47.548Z",
            "license": "LGPLv3",
            "topics": [
                "starter-kit",
                "sentinel-2",
                "optical",
                "color-composition"
            ],
            "owner": "delta-user"
            "visibility": "public"
        }
    ]

______________________________________________


.. click:: delta.cli.components.get:get_deltatwin_info
   :prog: deltatwin component get
   :nested: full

.. code-block:: console

    deltatwin component get dt_name -f json

This command will show the information of a DeltaTwin® component,
before using this command the user must be logged in,
using the *deltatwin* *login* command. As example, it returns:

.. code-block:: console

    {
        "name": "Deltatwin2",
        "description": "Description of the Deltatwin2",
        "publication_date": "2024-03-07T12:50:55.055721Z",
        "topics": [
            "starter-kit",
            "sentinel-2",
            "optical",
            "color-composition"
        ],
        "version": "1.1.0",
        "available_version": [
            "1.1.0",
            "1.0.1",
            "1.0.0"
        ],
        "owner": "delta-user",
        "inputs": [
            {
                "name": "angle",
                "type": "integer",
                "default_value": null,
                "description": "Rotation angle in degree"
            },
            {
                "name": "image",
                "type": "Data",
                "default_value": null,
                "description": "URL of the image to rotate"
            }
        ],
        "outputs": []
    }


.. note::
    The input structure, returned by the get command, can be used to create the JSON input
    file required for running a DeltaTwin® component.
    However, the format requires modification.
    For instance, following the above example, the resulting input file
    for runing this DeltaTwin® component will be:

        {
            "angle":{
                "type": "integer",
                "value": 90
            },

            "image":{
                "type": "Data",
                "value": "https://url_to_image"
            }
        }



______________________________________________

.. click:: delta.cli.components.init:init
   :prog: deltatwin component init
   :nested: full

**Examples**:
For example, you can create a new DeltaTwin® called *ndvi* with the following command:

.. code-block:: console

    deltatwin component init /home/user/desktop/ndvi

This command will create the basic files of a DeltaTwin® component, in a folder called *ndvi* and returns the following data

.. code-block:: console

    INFO: DeltaTwin® ndvi created

______________________________________________


.. click:: delta.cli.components.build:build
   :prog: deltatwin component build
   :nested: full

**Examples:**

.. code-block:: console

    delta component build -t <tag name>

This command will build a (Docker) image of your DeltaTwin® component.

______________________________________________


.. click:: delta.cli.components.publish:publish_dt
   :prog: deltatwin component publish
   :nested: full

**Examples:**


**Example 1:**
To publish a new DeltaTwin® component to the DeltaTwin® platform, execute:

.. code-block:: console

    deltatwin component publish 1.0.0 --change-log "First version"


**Example 2:**

If you have already pushed your DeltaTwin®, please use the second command to
publish a new version of your DeltaTwin® component.

.. code-block:: console

    deltatwin component publish 1.1.0 --change-log "New version of my DeltaTwin"


.. warning::
    | * DeltaTwin® components are only visible to the individual user and cannot be shared with other users. To make a component publicly accessible, please contact DestinE Platform Support.
    | * DeltaTwin® names must be unique. A DeltaTwin cannot be published if its name is already in use.
    | * The characters allowed for naming a DeltaTwin® are letters (a-z),digits (0-9) and special (-). Upper case letter are not supported.

______________________________________________


.. click:: delta.cli.components.delete:delete_deltatwin_info
   :prog: deltatwin component delete
   :nested: full


**Examples:**

.. code-block:: console

    deltatwin component delete -v 1.2.0 MyDeltaTwin

This command will remove the version 1.2.0 of the Deltatwin component named
MyDeltaTwin.

.. warning::
    When deleting a Delta Twin component, all generated artifacts are transformed into resources
    because the service will no longer be able to relate them to the version of the DeltaTwin that was used to generate them.

______________________________________________

.. click:: delta.cli.components.update:update
   :prog: deltatwin component update
   :nested: full

This command allows users to modify the topics and the visibility of his published DeltaTwin components.

**Examples**:
To update the visibility of a DeltaTwin component, execute:

.. code-block:: console

    deltatwin component update --visibility private MyDeltaTwin_ID

Note that only administrators user can toggle the visibility status from private to public.


To change the topics list, execute:

.. code-block:: console

    deltatwin component update --topics <topic1> ... --topics <topicN> COMPONENT_ID

The previous topic list will be deleted and replaced by the new one.
