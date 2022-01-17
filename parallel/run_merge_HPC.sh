#!/bin/sh

#SBATCH --partition=shared-cpu,private-lehmann-cpu
#SBATCH --time=10:00:00
#SBATCH --mem=62G

#load modules

module load GCC/8.2.0-2.31.1 OpenMPI/3.1.3 Python/3.7.2 SciPy-bundle/2019.03 GDAL/3.0.0-Python-3.7.2 xarray/0.13.0-Python-3.7.2

#launch execution
srun python3 merge_HPC.py
