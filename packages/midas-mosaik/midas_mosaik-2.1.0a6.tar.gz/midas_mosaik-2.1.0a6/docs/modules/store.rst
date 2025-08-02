Midas Store Module
==================

The *store* module, provided by the `midas-store` package, contains a simple database simulator.
It will store simulation results of other simulators in a *comma-separated values* (csv) file.
The store alternatively supports to use a *Hierarchical Document Format* (HDF) database to store the data.
In that case, *pandas* and *pytables* are used to allow pandas dataframes to be saved directly to the HDF file.
This makes it convenient to use inside of python code or a Jupyter notebook but on the otherside it gets more complicated to read the HDF file with a common HDF viewer application.

Installation
------------

This package will usually installed automatically together with `midas-mosaik` if you opt-in any of the extras, e.g., `base` or `bh`.
It is available on pypi, so you can install it manually with

.. code-block:: bash

    pip install midas-store

or if you want to have HDF support you have to install it manually with

.. code-block:: bash

    pip install midas-store[hdf]

Usage
-----

The intended use-case for the store is to be used inside of Midas, but it can be used in any mosaik simulation scenario.

Inside of Midas
~~~~~~~~~~~~~~~

To use the store inside of Midas, add `store` to your modules

.. code-block:: yaml

    my_scenario:
      modules:
        - store
        # - ...

and configure it with:

.. code-block:: yaml
    
    my_scenario:
      # ...
      store_params:
        filename: my_results.csv

All of the core simulators that have something to store will then automatically connect to the *store* simulator.
Since only one instance of the store is allowed, the store does not support scopes.
Implicitly, the scope *database* will be created and used.  
If you want to use HDF and you have installed the required extras, rename your filename to `my_results.hdf5` (something that ends with `.hdf5`).

Any Mosaik Scenario
~~~~~~~~~~~~~~~~~~~

If you don't use Midas, you can add the `store` manually to your mosaik scenario file. 
First, the entry in the `sim_config`:

.. code-block:: python

    sim_config = {
        "MidasCSVStore": {"python": "midas_store.simulator:MidasCSVStore"},
        # ...
    }


Next, you need to start the simulator (assuming a `step_size` of 900):

.. code-block:: python
    
    store_sim = world.start("MidasCSVStore", step_size=900)


Finally, the model needs to be started:

.. code-block:: python
    
    store = store_sim.Database(filename="my_results.csv", keep_old_files=False, unique_filename=False)


Afterwards, you can define `world.connect(other_entity, store, attrs)` as you like.

The Keys of the Store
---------------------

This section gives a short description for all of the keys of the *store* module. 
Keys that are part of every upgrade module will only be mentioned if the actual behavior might be unexpected.

step_size
  While the *step_size* works as expected, the implications might not be directly clear.
  When *step_size* is set to 1, the store will step in every step.
  In each step, mosaik passes all the outputs from all simulators connected to the store as inputs.
  When other simulators did not perform a step between two store steps, the store will receive the same data from those simulators until they stepped again.
  Therefore, it does not make sense to step the store every second.
  On the other hand, if the step size of the store is larger than those of the simulators, only the latest step results will be passed to the store.
  A good rule-of-thumb would be to set the step size to be the same as the simulator with smallest step size that passes relevant data to the store.
  Since the default step size of Midas is 900, this step size works as well for the store.

filename
  This key defines the name of the database file.
  A database file with that name will be created inside of the *_outputs* directory defined in the *midas-runtime-conf.yml*.
  The value is of type string.

path
  With this, the output directory, where the database file will be created, can be specified.
  By default, it will use the outputs directory defined in the *midas-runtime-conf.yml*, which defaults to *_outputs* in the current working directory. 
  The value is of type string.

unique_filename
  This key controls the behavior of the store when the filename is already present in the directory specified by *path*.
  The value is of type bool.

  Otherwise, the store will create a unique filename using `uuid4`, e.g., *existing_db-<uuid4>.csv*.
  This works for both csv and HDF and he default value is *false*.

keep_old_files
  This key controls the behavior of the store when the filename is already present in the directory specified by *path*.
  The value if of type bool.
  If it is set to *false*, the existing file *existing_db.csv* will be moved to *existing_db.csv.old* and the store will use the filename *existing_db.csv* (or whatever was defined as *filename*).
  If will not check if *existing_db.csv.old* already exists and will overwrite that file.
  Otherwise, the store will create a new filename by adding an increment, e.g. *existing_db-002.csv*.
  This key will (by definition) not work when *unique_filename* is used. 
  The default value is *false*

buffer_size
  This key is only used by the HDF store and can be used to control how the store will save the data into the database.
  The value is if of type integer and defaults to 1000, i.e., the store will collect data from the simulation for 1000 step function calls and will then save the collected data to disk.
  Reducing this value should reduce memory usage but may slow down the simulation at the end since appending to existing data is rather costly.
  Setting the value too high will lead to an increase of memory usage and possibly data loss if the simulation terminates prematurly.
  
threaded
  This key can be used to control if the store writer is started as separate process or in-process, i.e., as thread.
  The value is of type bool and defaults to *false*.

timeout
  This key controls the timeout of the store writer.
  It is of type integer and can be interpreted as seconds. 
  If during shutdown the writer does not send data for *timeout* seconds, it will be forced shut down.
  The default value is 300.