# Dymachandran Documentation
Dymachandran is a Python tool that uses MDAnalysis functions to create a dynamic and interactive Ramachandran plot for analyzing and validating protein structures from molecular dynamics simulations.
# Installation

`pip install dymachandran` 

# Requirements

-Python 3.9 or higher

-numpy

-pandas

-plotly.express

-argparse

-PIL

-MDAnalysis

-multiprocessing

-progressbar2

-requests

# Usage

Dymachandran takes topology and trajectory files from a molecular dynamics simulation as input and generates an HTML file as output.

usage:  
`dymachandran.py [-h] "topology_file.gro" "trajectory_file.xtc" "num_processes" "output_file.html"`

positional arguments:

topology                             	: path to the topology file

trajectory                               	: path to the trajectory file

num_processes                    	: number of processes

output_file                             	: name of output file 

optional arguments:
  -h, --help                          :show this help message and exit


