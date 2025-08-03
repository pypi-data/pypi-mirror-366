
.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.8370310.svg
   :target: https://doi.org/10.5281/zenodo.8370310
   :align: right

==========
pymetacode
==========

*A Python package helping to write and maintain Python packages.*

**Code that writes code** -- yes, that's correct. Automating the boring stuff, one could say, or helping to focus on the creative part of programming. In any case, the idea for this package stems from experience with a couple of Python projects, and as such it is pretty *opinionated*, focussing on personal needs regarding structure and layout. Nevertheless, it tries to be as user-friendly as possible, coming with an intuitive command-line interface (CLI).

What is the difference to CookieCutter and alike? It does not only create a project structure for you once, but **it helps you to maintain your projects**, *i.e.*, adding modules, classes, functions together with documentation stubs and tests -- **following good practices of software development**.

Want to get an idea? Here you go. **Creating a new package** would be a two-step process:

1) Write a configuration file for your new package (and afterwards fill it with sensible content)

.. code-block:: bash

    pymeta write config to mypackage_config.yaml

2) Create the basic Python package structure for your package.

.. code-block:: bash

    pymeta create package from mypackage_config.yaml

Once you have your package structure, you can **add modules, classes, and functions** to your package from *within the package's root directory* at any time:

.. code-block:: bash

    pymeta add module mymodule
    pymeta add class MyClass to mymodule
    pymeta add function my_function to mymodule

If you ever want to add a **graphical user interface (GUI)** to your project, this is (now) possible as well:

.. code-block:: bash

    pymeta add gui
    pymeta add window mysubwindow

And now - happy coding!


Features
========

A list of features:

* Create initial package structure (directory layout, files)

* Add module, class, and function scaffolds to an existing project, including tests and API documentation

* Add initial (Qt) GUI subpackage structure (directory layout, files)

* Add (Qt) GUI window scaffolds to existing project, including tests and API documentation

* Intuitive command-line interface (CLI)

* Initialise git repository; automatically incrementing version number with each commit


And to make it even more convenient for users and future-proof:

* Open source project written in Python (>= 3.7)

* Developed fully test-driven

* Extensive user and API documentation


Installation
============

To install the pymetacode package on your computer (sensibly within a Python virtual environment), open a terminal (activate your virtual environment), and type in the following:

.. code-block:: bash

    pip install pymetacode


License
=======

This program is free software: you can redistribute it and/or modify it under the terms of the **BSD License**.

