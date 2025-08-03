Usage Guide
===========

Welcome to the Dashing Turtle Quick Start Tutorial! This guide will help you get started with setting up sequences, loading data, running predictions, and generating landscapes.

Overview: Visual Workflow
-------------------------

.. code-block:: none

    [Add Sequences]
          │
          ▼
    [List Sequences & Get LIDs (Visible in Graphical Interface)]
          │
          ▼
    [Load Basecall Data]
    [Load Signal Data]
          │
          ▼
    [Run Predictions]
          │
          ▼
    [Create Landscape]

Step 1: Add Your Sequences
--------------------------

Before running predictions, add at least two sequences:

- One **unmodified** (control)
- One **modified**

Example command:

.. code-block:: bash

    seq -add -s GGAUCGAUCG -sec .......... -e EXP001 -n Testgoose -t 37 -t1 TypeA -t2 TypeB -r 1

**Options:**

- ``-s``: RNA sequence (A, C, G, U)
- ``-sec``: Secondary structure in dot-bracket notation (must match sequence length)
- ``-e``: Experiment name (required with ``-sec``)
- ``-n``: Sequence name
- ``-t``: Temperature in °C (default: 37)
- ``-t1``, ``-t2``: Type labels (e.g. modified vs unmodified)
- ``-r``: Run ID (default: 1)

Step 2: List Sequences & Get LIDs
---------------------------------

Once added, list your sequences to obtain Library IDs (LIDs):

.. code-block:: bash

    seq -list

Example output:

.. code-block:: text

    52 Unmodified Example Sequence
    53 Modified Example Sequence

You'll use these LIDs in subsequent steps.

Step 3: Load Basecall and Signal Data
-------------------------------------

**Load basecall data:**

.. code-block:: bash

    load -basecall -l 52 -p Sample/DMSO/Alignment

- ``-l``: LID of the sequence
- ``-p``: Path to basecall alignment directory

**Load signal data:**

.. code-block:: bash

    load -signal -l 52 -p Sample/DMSO/DMSO_fmn.txt

- ``-l``: LID of the sequence
- ``-p``: Path to signal file

Repeat for both modified and unmodified sequences.

Step 4: Run Predictions
-----------------------

Once data is loaded, run predictions:

.. code-block:: bash

    predict -u 52 -l 53 -v

- ``-u``: LID of unmodified sequence
- ``-l``: LID of modified sequence
- ``-v``: (Optional) Include ViennaRNA base-pairing probabilities

Step 5: Create Landscape
------------------------

Generate a landscape visualization using:

.. code-block:: bash

    create_landscape -u 52 -l 53 -o

- ``-u``: LID of unmodified sequence
- ``-l``: LID of modified sequence
- ``-o``: Optimize clusters and output dendrograms

Cheat Sheet
-----------

+--------------------+---------------------------------------------------------+
| Step               | Example Command                                         |
+====================+=========================================================+
| Add (unmodified)   | seq -add -s AGCUAGCUA -n Test -t1 TypeA -t2 TypeA       |
+--------------------+---------------------------------------------------------+
| Add (modified)     | seq -add -s AGCUAGCUA -n Test -t1 TypeA -t2 TypeB       |
+--------------------+---------------------------------------------------------+
| List sequences     | seq -list                                               |
+--------------------+---------------------------------------------------------+
| Load basecall      | load -basecall -l 52 -p Sample/DMSO/Alignment          |
+--------------------+---------------------------------------------------------+
| Load signal        | load -signal -l 52 -p Sample/DMSO/DMSO_fmn.txt         |
+--------------------+---------------------------------------------------------+
| Predict            | predict -u 52 -l 53 -v                                  |
+--------------------+---------------------------------------------------------+
| Create landscape   | create_landscape -u 52 -l 53 -o                         |
+--------------------+---------------------------------------------------------+

Summary
-------

1. **Add sequences** (at least one unmodified and one modified)
2. **List sequences** to find LIDs
3. **Load basecall and signal data**
4. **Run predictions**
5. **Generate a landscape** visualization

You're now ready to begin your Dashing Turtle data analysis workflow!
