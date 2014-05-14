#!/bin/sh

sudo apt-get update
sudo apt-get install zlib1g-dev libbz2-dev
sudo apt-get install build-essential
sudo apt-get install libboost-all-dev

sudo apt-get install git htop cmake pigz

git clone https://github.com/graphlab-code/graphlab
cd graphlab
./configure --no_mpi

echo "Stuff configured. Go to CF directory and make -jX"
