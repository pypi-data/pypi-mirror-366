# NetDes

#### <ins>Net</ins>work inference and optimization using <ins>D</ins>ynamical <ins>e</ins>quation <ins>s</ins>imulations

NetDes is a computational method for optimizing gene regulatory networks (GRNs) of core transcription factor (TF) based on gene expression time trajectories. NetDes was specifically designed for analyzing time-series scRNA-seq data. The NetDes pipeline contains the following steps. 

* (1) NetDes calculates smoothed gene expression trajectories along inferred pseudotime.

* (2) Genes are then clustered according to the trajectories.

* (3) Core TFs are inferred for each gene cluster using gene set analysis and TF-target gene relationship. 

* (4) An initial GRN of core TFs is constructed according to TF-target gene relationship, where target genes also belong to the core TFs.

* (5) Network optimization that refines the GRN and constructs a dynamical model using ordinary differential equations (ODEs).

* (6) Dynamical systems modeling, such as gene perturbation simulations, signal driving simulations, network coarse-graining.

## Installation
Python version 3.9 or greater is required.

#### Install from PyPi (recommended)
To install the most recent release, run

`pip install NetDes`

#### Install with github
* Git clone the [NetDes repository](https://github.com/lusystemsbio/NetDes), cd to the `NetDes` directory, and run

`pip install .`

## Tutorials

[Processing gene expression time trajectories using scRNA-seq data]: This script illustrates the steps to process input scRNA-seq data, obtain smoothed gene expression time trajectories, and cluster genes based on the trajectories. (Steps 1 and 2)

[Inferring core TFs]: This script shows the inference of core transcription factors using Fisher's exact test. (Step 3)

[Initial GRN construction]: This script illustrates how to build an initial GRN using TF-target gene databases like Rcistarge, TRRUST, and NetAct. (Step 4)

[GRN optimization and simulation]: This tutorial page shows the NetDes' usage for network optimization and simulation. The user input includes pseudotime, smoothed gene expression trajectories, and an initial GRN.

[Benchmarking]: This script explains the steps for GRN evaluation by comparing RACIPE simulations with the scRNA-seq data. (Step 5)

[Network coarse-graining]: This script shows the process of coarse-graining the optimized GRN into a small gene circuit using [SacroGraci](https://github.com/lusystemsbio/SacoGraci). (Step 6)
