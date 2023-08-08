.. raw:: html

   <h1 align="center">

layout2svg

.. raw:: html

   </h1>

.. container::

   .. raw:: html

      <p>

   This is a simple tool to convert an integrated circuit layout saved
   in OASIS / GDSII file format to a .SVG image file. The tool supports
   direct export of the SVG file into the Inkscape desktop app. This
   tool was written with the goal of rendering any layout in a desktop
   or web application.

   .. raw:: html

      </p>

.. raw:: html

   <h2 align="center">

Installation

.. raw:: html

   </h2>

.. raw:: html

   <h3 align="center">

MacOS, Linux, Windows

.. raw:: html

   </h3>

.. code:: bash

   pip install layout2svg

.. raw:: html

   <h2 align="center">

Usage - Command Line Interface

.. raw:: html

   </h2>

.. code:: bash

   layout2svg -i <input_file_path [.gds/.oas]> -o <output_file_path [.svg]>

.. raw:: html

   <h2 align="center">

Examples

.. raw:: html

   </h2>

.. raw:: html

   <p>

Running the example with the mock layerstack file and layout provided in
the examples directory, by running the following command:

.. raw:: html

   </p>

.. code:: bash

   layout2svg -i examples/crossed_metal.gds -t examples/mock_layers.lys.yml -o examples/crossed_metal.svg

.. raw:: html

   <p>

can generate the following SVG image:

.. raw:: html

   </p>

.. raw:: html

   <p align="center">

.. raw:: html

   </p>
