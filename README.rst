#######
BasicDB
#######

When BasicDB grows up, it wants to be a higly available, flexible,
non-relational data store.

It offers an API that is somewhat compatible with AWS SimpleDB, so if you know
how to deal with SimpleDB, you should know how to deal with BasicDB.

The following API calls work (sufficiently to make the positive tests pass):

 * CreateDomain
 * DeleteAttributes
 * DeleteDomain
 * DomainMetadata
 * GetAttributes
 * ListDomains
 * PutAttributes
 * Select
 * BatchPutAttributes
 * BatchDeleteAttributes

Things BasicDB doesn't do:
 * Authentication
 * Index data (so query performance will probably be horrible compared to SimpleDB)


Basic operations
----------------

Install dependencies.

.. code-block:: sh

    virtualenv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    pip install boto
    pip install -e git+https://github.com/sorenh/basicdb#egg=basicdb

Start server locally, say with port 8000.

.. code-block:: sh

    export REMOTE_USER=fake
    python /path/to/basicdb/basicdb/__init__.py 8000

This will start the 'fake' backend, that is, all the data will be in memory. If you want to use filesystem as a backend, also export ``BASICDB_BACKEND_DRIVER=filesystem`` into environment before starting the server as above.

From python shell, use boto to access SimpleDB

.. code-block:: python

    import boto
    local_region = boto.regioninfo.RegionInfo(name='local',
                       endpoint='localhost')
    conn = boto.connect_sdb('', '',
               region=local_region,
               is_secure=False, port=8000)

And now you can use the ``conn`` object for making API calls. See http://boto.readthedocs.org/en/latest/simpledb_tut.html for more info on how to use ``boto`` to access BasicDB.
