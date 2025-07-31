[![Documentation Status](https://readthedocs.org/projects/drive-ibd/badge/?version=latest)](https://drive-ibd.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI version](https://badge.fury.io/py/drive-ibd.svg)](https://badge.fury.io/py/drive-ibd)
[![DRIVE python package](https://github.com/belowlab/drive/actions/workflows/python-app.yml/badge.svg)](https://github.com/belowlab/drive/actions/workflows/python-app.yml)

# DRIVE:

This repository contains the source code for the tool DRIVE (Distant Relatedness for Identification and Variant Evaluation) is a novel approach to IBD-based genotype inference used to identify shared chromosomal segments in dense genetic arrays. DRIVE implements a random walk algorithm that identifies clusters of individuals who pairwise share an IBD segment overlapping a locus of interest. This tool was developed in python by the Below Lab at Vanderbilt University. The documentation for how to use this tool can be found here [DRIVE documentation](https://drive-ibd.readthedocs.io/en/latest/)

## Installing DRIVE:
DRIVE is available on PYPI and can easily be installed using the following command:

```bash
pip install drive-ibd
```
It is recommended to install DRIVE within a virtual environment such as venv, or conda. More information about this process can be found within the documentation.

If the user wishes to develop DRIVE or install the program from source then they can clone the repository. This process is described under the section called "Github Installation" in the documentation.

DRIVE is also available on Docker. The docker image can be found here "jtb114/drive".

If you are working on an HPC cluster it may be better to use a singularity image. Singularity can pull the docker container and build a singularity image with the following command:

```bash
singularity pull singularity-image-name.sif docker://jtb114/drive:latest
```

### Reporting issues:
If you wish to report a bug or propose a feature you can find templates under the .github/ISSUE_TEMPLATE directory.

