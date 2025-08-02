#!/bin/bash

VENV=esi_utils_colors

cwd=$(pwd)
echo "Installing ${VENV}...${cwd}"

unamestr=`uname`
env_file=environment.yml
if [ "$unamestr" == 'Linux' ]; then
    prof=~/.bashrc
elif [ "$unamestr" == 'FreeBSD' ] || [ "$unamestr" == 'Darwin' ]; then
    prof=~/.bash_profile
else
    echo "Unsupported environment. Exiting."
    exit
fi

source $prof

# Start in conda base environment
echo "Activate base virtual environment"
conda activate base

# Create a conda virtual environment
echo "Creating the $VENV virtual environment:"
conda create -y -n $VENV -c conda-forge python>=3.9


# Bail out at this point if the conda create command fails.
# Clean up zip files we've downloaded
if [ $? -ne 0 ]; then
    echo "Failed to create conda environment.  Resolve any conflicts, then try again."
    exit
fi

# Activate the new environment
echo "Activating the $VENV virtual environment"
conda activate $VENV

# This package
cd "${cwd}"
echo "Installing ${VENV}...${cwd}"
pip install -e .[dev,test]

# Tell the user they have to activate this environment
echo "Type 'conda activate $VENV' to use this new virtual environment."
